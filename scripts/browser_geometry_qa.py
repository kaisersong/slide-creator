from __future__ import annotations

import argparse
import hashlib
import io
import json
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - import availability depends on environment
    sync_playwright = None


REPORT_VERSION = 1
DEFAULT_VIEWPORTS = [{"width": 1600, "height": 900}, {"width": 1280, "height": 720}]
# Real laptop browser windows (menu bar + tab strip + dock) land near 730-860px of
# usable height. Dense slides clip there while passing at 900px, so keep an explicit
# short-window viewport available for gates that want laptop coverage.
LAPTOP_WINDOW_VIEWPORT = {"width": 1440, "height": 733}
# Play mode pins every slide to a fixed 1440x900 box and scales it (see
# references/html-template.md). Window-mode geometry therefore never observes what the
# audience sees on a projector, which is why measurement modes are explicit.
MEASUREMENT_MODES = ("window", "present")
PRESENT_BOX = {"width": 1440, "height": 900}
CLIPPING_TOLERANCE_PX = 4.0
DEVICE_PIXEL_RATIO = 1
QA_FREEZE_CSS = """
*, *::before, *::after {
  animation: none !important;
  transition: none !important;
  caret-color: transparent !important;
  scroll-behavior: auto !important;
  scroll-snap-type: none !important;
}
"""

HARD_FAILURE_CODES = {
    "title_clipped": "browser-geometry-title-clipped",
    "content_clipped": "browser-geometry-content-clipped",
    "text_overflow": "browser-geometry-text-overflow",
    "empty_component": "browser-geometry-empty-component",
    "character_overlap": "browser-geometry-character-overlap",
    "low_contrast": "browser-geometry-low-contrast",
    "invisible_target": "browser-geometry-invisible-target",
}


def _read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _launch_browser():
    if sync_playwright is None:
        raise RuntimeError("Playwright is not installed; cannot run browser geometry QA")

    playwright = sync_playwright().start()
    try:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
    except Exception:
        browser = playwright.chromium.launch(headless=True)
    return playwright, browser


def _round_rect(rect: dict[str, Any]) -> dict[str, float]:
    return {
        "x": round(float(rect.get("x", 0)), 2),
        "y": round(float(rect.get("y", 0)), 2),
        "width": round(float(rect.get("width", 0)), 2),
        "height": round(float(rect.get("height", 0)), 2),
    }


def _parse_rgb(value: str | None) -> tuple[int, int, int, float] | None:
    if not value:
        return None
    text = value.strip().lower()
    if not text.startswith("rgb"):
        return None
    start = text.find("(")
    end = text.rfind(")")
    if start < 0 or end < start:
        return None
    parts = [part.strip() for part in text[start + 1 : end].split(",")]
    if len(parts) < 3:
        return None
    try:
        r, g, b = (int(float(parts[index])) for index in range(3))
        alpha = float(parts[3]) if len(parts) >= 4 else 1.0
    except ValueError:
        return None
    return r, g, b, alpha


def _relative_luminance(rgb: tuple[int, int, int]) -> float:
    channels = []
    for value in rgb:
        channel = value / 255
        if channel <= 0.03928:
            channels.append(channel / 12.92)
        else:
            channels.append(((channel + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def _contrast_ratio(foreground: tuple[int, int, int], background: tuple[int, int, int]) -> float:
    fg = _relative_luminance(foreground)
    bg = _relative_luminance(background)
    lighter = max(fg, bg)
    darker = min(fg, bg)
    return (lighter + 0.05) / (darker + 0.05)


def _rgb_distance(first: tuple[int, int, int], second: tuple[int, int, int]) -> float:
    return sum((first[index] - second[index]) ** 2 for index in range(3)) ** 0.5


def _composite_foreground(
    foreground: tuple[int, int, int, float],
    background: tuple[int, int, int],
) -> tuple[int, int, int]:
    alpha = max(0.0, min(1.0, foreground[3]))
    return tuple(
        int(round(foreground[index] * alpha + background[index] * (1 - alpha)))
        for index in range(3)
    )


def _dominant_background_samples(
    samples: list[tuple[int, int, int]],
    foreground: tuple[int, int, int, float] | None = None,
) -> list[tuple[int, int, int]]:
    if not samples:
        return []

    candidate_samples = samples
    if foreground and foreground[3] >= 0.98:
        foreground_rgb = (foreground[0], foreground[1], foreground[2])
        filtered = [sample for sample in samples if _rgb_distance(sample, foreground_rgb) >= 72]
        if len(filtered) >= max(5, int(len(samples) * 0.25)):
            candidate_samples = filtered

    clusters: list[list[tuple[int, int, int]]] = []
    for sample in candidate_samples:
        matched = False
        for cluster in clusters:
            centroid = tuple(round(sum(item[index] for item in cluster) / len(cluster)) for index in range(3))
            if _rgb_distance(sample, centroid) <= 18:
                cluster.append(sample)
                matched = True
                break
        if not matched:
            clusters.append([sample])

    dominant = max(clusters, key=len)
    if len(dominant) >= max(5, int(len(candidate_samples) * 0.45)):
        return dominant
    return candidate_samples


def _representative_contrast_ratio(
    foreground: tuple[int, int, int, float],
    samples: list[tuple[int, int, int]],
) -> float:
    if not samples:
        return 21.0
    samples = _dominant_background_samples(samples, foreground)
    rendered_pairs = [(_composite_foreground(foreground, sample), sample) for sample in samples]
    ratios = [_contrast_ratio(rendered_foreground, sample) for rendered_foreground, sample in rendered_pairs]
    background_ratios = [
        ratio
        for ratio, (rendered_foreground, sample) in zip(ratios, rendered_pairs, strict=False)
        if _rgb_distance(rendered_foreground, sample) >= 36 and ratio >= 1.18
    ]
    if background_ratios:
        ordered = sorted(background_ratios)
        percentile_index = min(len(ordered) - 1, max(0, int(len(ordered) * 0.2)))
        return ordered[percentile_index]
    return max(ratios)


def _sample_points(rect: dict[str, Any], image: Image.Image) -> list[tuple[int, int]]:
    left = float(rect["x"])
    top = float(rect["y"])
    width = float(rect["width"])
    height = float(rect["height"])
    right = left + width
    bottom = top + height
    raw_points: list[tuple[float, float]] = [
        (left + width / 2, top + height / 2),
        (left + 2, top + 2),
        (right - 2, top + 2),
        (left + 2, bottom - 2),
        (right - 2, bottom - 2),
        (left - 2, top - 2),
        (right + 2, top - 2),
        (left - 2, bottom + 2),
        (right + 2, bottom + 2),
    ]
    for x_index in range(5):
        for y_index in range(3):
            raw_points.append((left + width * (x_index + 0.5) / 5, top + height * (y_index + 0.5) / 3))

    points: list[tuple[int, int]] = []
    max_x = image.width - 1
    max_y = image.height - 1
    for x, y in raw_points:
        clamped = (max(0, min(max_x, int(round(x)))), max(0, min(max_y, int(round(y)))))
        if clamped not in points:
            points.append(clamped)
    return points


def _background_variance(samples: list[tuple[int, int, int]]) -> float:
    if not samples:
        return 0.0
    luminances = [_relative_luminance(sample) for sample in samples]
    average = sum(luminances) / len(luminances)
    return sum((item - average) ** 2 for item in luminances) / len(luminances)


def _artifact_reference(
    screenshot_bytes: bytes,
    *,
    artifact_dir: str | Path | None,
    label: str,
) -> str:
    digest = hashlib.sha256(screenshot_bytes).hexdigest()[:12]
    if artifact_dir:
        directory = Path(artifact_dir)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{label}-{digest}.png"
        path.write_bytes(screenshot_bytes)
        return str(path)
    return f"screenshot-sha256:{digest}"


def _measurement_signature(measurements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    signature: list[dict[str, Any]] = []
    for item in measurements:
        signature.append(
            {
                "qa_id": item.get("qa_id"),
                "rect": _round_rect(item.get("rect", {})),
                "flags": {
                    key: bool(item.get(key))
                    for key in [
                        "title_clipped",
                        "text_overflow",
                        "empty_component",
                        "character_overlap",
                        "compressed_letter_spacing",
                        "invisible_target",
                    ]
                },
            }
        )
    return signature


def _slide_count(page) -> int:
    return int(page.evaluate("() => Math.max(1, document.querySelectorAll('.slide').length)"))


def _enter_present_mode(page) -> bool:
    """Activate the deck's own play mode (F5 / round play control).

    Play mode pins slides to a fixed 1440x900 box and scales them, so its geometry is
    independent from window-mode geometry. Headless Chromium rejects the fullscreen
    request; the deck keeps `body.presenting` regardless, which is what we measure.
    """
    return bool(
        page.evaluate(
            """
            () => {
              const btn = document.getElementById('present-btn');
              if (btn) btn.click();
              if (!document.body.classList.contains('presenting')) {
                document.dispatchEvent(new KeyboardEvent('keydown', { key: 'F5', bubbles: true }));
              }
              return document.body.classList.contains('presenting');
            }
            """
        )
    )


def _activate_slide(page, slide_index: int, *, mode: str = "window") -> bool:
    if mode == "present":
        return bool(
            page.evaluate(
                """
                ({ slideIndex }) => {
                  const slides = Array.from(document.querySelectorAll('.slide'));
                  if (!slides.length) return true;
                  const idx = Math.max(0, Math.min((slideIndex || 1) - 1, slides.length - 1));
                  try {
                    if (typeof ctrl !== 'undefined' && ctrl && typeof ctrl.goTo === 'function') ctrl.goTo(idx);
                  } catch (_err) {}
                  slides.forEach((slide, slideIdx) => slide.classList.toggle('p-on', slideIdx === idx));
                  return slides[idx].classList.contains('p-on');
                }
                """,
                {"slideIndex": slide_index},
            )
        )
    return bool(
        page.evaluate(
            """
            ({ slideIndex }) => {
              const slides = Array.from(document.querySelectorAll('.slide'));
              if (!slides.length) return true;
              const idx = Math.max(0, Math.min((slideIndex || 1) - 1, slides.length - 1));
              const targetSlide = slides[idx];
              if (!targetSlide) return false;

              const activateViaController = () => {
                try {
                  if (typeof ctrl !== 'undefined' && ctrl && typeof ctrl.goTo === 'function') {
                    ctrl.goTo(idx);
                    return true;
                  }
                } catch (_err) {}
                try {
                  if (typeof goTo !== 'undefined' && typeof goTo === 'function') {
                    goTo(idx);
                    return true;
                  }
                } catch (_err) {}
                return false;
              };

              const activateViaDots = () => {
                const nav = document.querySelector('#nav-dots, .nav-dots');
                if (!nav) return false;
                const dots = Array.from(nav.querySelectorAll('button, .dot'));
                if (dots.length < slides.length || !dots[idx]) return false;
                dots[idx].dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                return true;
              };

              const activateViaTrack = () => {
                const track = document.getElementById('track');
                if (!track || !slides.every((slide) => track.contains(slide))) {
                  return false;
                }
                slides.forEach((slide, slideIdx) => slide.classList.toggle('active', slideIdx === idx));
                const previousTransition = track.style.transition;
                track.style.transition = 'none';
                track.style.transform = `translateX(-${idx * 100}vw)`;
                track.getBoundingClientRect();
                track.style.transition = previousTransition;
                return true;
              };

              if (!activateViaController() && !activateViaDots() && !activateViaTrack()) {
                slides.forEach((slide, slideIdx) => slide.classList.toggle('active', slideIdx === idx));
              }
              targetSlide.scrollIntoView({ behavior: 'instant', block: 'start', inline: 'nearest' });
              return true;
            }
            """,
            {"slideIndex": slide_index},
        )
    )


def _measure_targets_script() -> str:
    return """
    ({ viewport, slideIndex }) => {
      const rolePattern = /(title|headline|hero|copy|body|text|pill|badge|card|chip|tag|command|cmd|terminal|code|cli|shell|prompt)/i;
      const componentPattern = /(pill|badge|card|chip|tag|command|cmd|terminal|code|cli|shell|prompt)/i;
      const decorativePattern = /(orb|decor|ornament|shape|rule|divider|ghost|mesh|gradient|blob|bg)/i;
      const slides = Array.from(document.querySelectorAll('.slide'));
      const targetSlide = slides.length ? slides[Math.max(0, Math.min((slideIndex || 1) - 1, slides.length - 1))] : null;

      const rectOf = (node) => {
        const rect = node.getBoundingClientRect();
        return { x: rect.left, y: rect.top, width: rect.width, height: rect.height };
      };

      const isVisible = (node) => {
        const style = window.getComputedStyle(node);
        const rect = node.getBoundingClientRect();
        return style.display !== 'none' &&
          style.visibility !== 'hidden' &&
          Number(style.opacity || '1') > 0.01 &&
          rect.width > 1 &&
          rect.height > 1;
      };

      const textOf = (node) => (node.innerText || node.textContent || '').replace(/\\s+/g, ' ').trim();
      const roleOf = (node) => {
        const explicit = node.getAttribute('data-geometry-role');
        if (explicit) return explicit;
        const tag = node.tagName.toLowerCase();
        const classes = Array.from(node.classList || []).join(' ');
        if (/^h[1-6]$/.test(tag) || /title|headline|hero/.test(classes)) return 'title';
        if (tag === 'code' || tag === 'pre' || /command|cmd|terminal|code|cli|shell|prompt/.test(classes)) return 'command';
        if (/pill/.test(classes)) return 'pill';
        if (/badge|chip|tag/.test(classes)) return 'badge';
        if (/card/.test(classes)) return 'card';
        return 'text';
      };

      const selectorOf = (node) => {
        if (node.id) return `#${node.id}`;
        const explicit = node.getAttribute('data-geometry-target');
        if (explicit && explicit !== '') return `[data-geometry-target="${explicit}"]`;
        const classes = Array.from(node.classList || []);
        if (classes.length) return `${node.tagName.toLowerCase()}.${classes[0]}`;
        return node.tagName.toLowerCase();
      };

      const slideFor = (node) => node.closest('.slide') || document.body;
      const slideIndexFor = (node) => {
        const slide = slideFor(node);
        const slides = Array.from(document.querySelectorAll('.slide'));
        const index = slides.indexOf(slide);
        return index >= 0 ? index + 1 : 1;
      };

      const allCandidates = Array.from(document.querySelectorAll(
        '[data-geometry-target], h1, h2, h3, p, li, blockquote, code, pre, .title, .headline, .copy, .body, .text, .pill, .badge, .chip, .tag, .card, .command, .cmd, .terminal, .code-block, .command-block, .command-line, .terminal-line, .install-command, .cli, .shell, .prompt, .np-cmd, .bold-cmd'
      ));
      const seen = new Set();
      const targets = allCandidates.filter((node) => {
        if (seen.has(node)) return false;
        seen.add(node);
        if (targetSlide && slideFor(node) !== targetSlide) return false;
        const hasExplicit = node.hasAttribute('data-geometry-target');
        const text = textOf(node);
        const signature = `${node.tagName.toLowerCase()} ${Array.from(node.classList || []).join(' ')}`;
        return hasExplicit || text || rolePattern.test(signature);
      });

      const clipsBySlide = (rect, slideRect) =>
        rect.x < slideRect.x - 1 ||
        rect.y < slideRect.y - 1 ||
        rect.x + rect.width > slideRect.x + slideRect.width + 1 ||
        rect.y + rect.height > slideRect.y + slideRect.height + 1;

      const hasOverflow = (node) => {
        const style = window.getComputedStyle(node);
        const overflowX = style.overflowX;
        const overflowY = style.overflowY;
        const clipsX = ['hidden', 'clip'].includes(overflowX);
        const clipsY = ['hidden', 'clip'].includes(overflowY);
        const exceedsX = node.scrollWidth > node.clientWidth + 2;
        const exceedsY = node.scrollHeight > node.clientHeight + 2;
        return (clipsX && exceedsX) || (clipsY && exceedsY) || (exceedsX && overflowX === 'visible' && node.clientWidth > 0);
      };

      const textNodesOf = (node) => {
        const walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT);
        const nodes = [];
        while (walker.nextNode()) nodes.push(walker.currentNode);
        return nodes;
      };

      const charBoxes = (node) => {
        const boxes = [];
        for (const textNode of textNodesOf(node)) {
          const text = textNode.textContent || '';
          for (let index = 0; index < text.length; index += 1) {
            const ch = text[index];
            if (!ch || /\\s/.test(ch)) continue;
            const range = document.createRange();
            range.setStart(textNode, index);
            range.setEnd(textNode, index + 1);
            const rects = Array.from(range.getClientRects());
            range.detach();
            for (const rect of rects) {
              if (rect.width > 0 && rect.height > 0) {
                boxes.push({ char: ch, x: rect.left, y: rect.top, width: rect.width, height: rect.height });
              }
            }
          }
        }
        return boxes;
      };

      const hasCharacterOverlap = (node, text) => {
        if (!/(https?:\\/\\/|npm |pnpm |yarn |git |[A-Za-z0-9_/-]{12,})/.test(text)) return false;
        const boxes = charBoxes(node);
        for (let index = 1; index < boxes.length; index += 1) {
          const prev = boxes[index - 1];
          const curr = boxes[index];
          const verticalOverlap = Math.min(prev.y + prev.height, curr.y + curr.height) - Math.max(prev.y, curr.y);
          const horizontalOverlap = Math.min(prev.x + prev.width, curr.x + curr.width) - Math.max(prev.x, curr.x);
          if (verticalOverlap > Math.min(prev.height, curr.height) * 0.45 && horizontalOverlap > Math.min(prev.width, curr.width) * 0.20) {
            return true;
          }
        }

        const lines = [];
        for (const box of boxes) {
          let line = lines.find((candidate) => Math.abs(candidate.y - box.y) <= 2);
          if (!line) {
            line = { y: box.y, count: 0 };
            lines.push(line);
          }
          line.count += 1;
        }
        if (lines.length >= 6 && lines.filter((line) => line.count <= 2).length / lines.length >= 0.7) {
          return true;
        }
        return false;
      };

      const cssNumber = (value) => {
        const parsed = parseFloat(value);
        return Number.isFinite(parsed) ? parsed : 0;
      };

      const hasCompressedLetterSpacing = (text, role, style) => {
        if (role !== 'command') return false;
        if (!/(https?:\\/\\/|npm |pnpm |yarn |git |clawhub|slide-creator|[A-Za-z0-9_/-]{12,})/.test(text)) return false;
        const fontSize = cssNumber(style.fontSize) || 16;
        const letterSpacing = cssNumber(style.letterSpacing);
        return letterSpacing < 0 && Math.abs(letterSpacing) / fontSize >= 0.08;
      };

      const isDecorative = (node) => {
        if (node.getAttribute('aria-hidden') === 'true') return true;
        if ((node.getAttribute('role') || '').toLowerCase() === 'presentation') return true;
        const classes = Array.from(node.classList || []).join(' ');
        return decorativePattern.test(classes);
      };

      const hasComplexBackground = (node) => {
        let current = node;
        while (current && current.nodeType === Node.ELEMENT_NODE) {
          const style = window.getComputedStyle(current);
          const filterValue = `${style.backdropFilter || ''} ${style.webkitBackdropFilter || ''}`.trim();
          if (filterValue && filterValue !== 'none') return true;
          if ((current.getAttribute('data-geometry-complex-background') || '').toLowerCase() === 'true') return true;
          current = current.parentElement;
        }
        return false;
      };

      return targets.map((node, index) => {
        const role = roleOf(node);
        const text = textOf(node);
        const rect = rectOf(node);
        const slide = slideFor(node);
        const slideRect = rectOf(slide);
        const style = window.getComputedStyle(node);
        const visible = isVisible(node);
        const componentLike = componentPattern.test(`${role} ${Array.from(node.classList || []).join(' ')}`) || ['pill', 'badge', 'card', 'command'].includes(role);
        const emptyComponent = visible && componentLike && !isDecorative(node) && text.length === 0;
        const titleClipped = role === 'title' && visible && clipsBySlide(rect, slideRect);
        const textOverflow = visible && Boolean(text) && hasOverflow(node);
        const compressedLetterSpacing = hasCompressedLetterSpacing(text, role, style);
        return {
          qa_id: node.getAttribute('data-geometry-target') || `geometry-${index + 1}`,
          selector: selectorOf(node),
          role,
          slide_index: targetSlide ? slideIndex : slideIndexFor(node),
          text,
          rect,
          slide_rect: slideRect,
          tag_name: node.tagName.toLowerCase(),
          classes: Array.from(node.classList || []),
          font_size: parseFloat(style.fontSize || '16') || 16,
          letter_spacing: cssNumber(style.letterSpacing),
          color: style.color,
          visible,
          zero_area: rect.width <= 1 || rect.height <= 1,
          invisible_target: node.hasAttribute('data-geometry-target') && !visible,
          title_clipped: titleClipped,
          text_overflow: textOverflow,
          empty_component: emptyComponent,
          compressed_letter_spacing: compressedLetterSpacing,
          character_overlap: hasCharacterOverlap(node, text) || compressedLetterSpacing,
          complex_background: hasComplexBackground(node),
          decorative: isDecorative(node),
          viewport,
        };
      });
    }
    """


def _measure_clipping_script() -> str:
    """Scan one slide for text that the slide box clips vertically.

    `.slide` is `overflow: hidden` by contract, so any text whose box crosses the slide's
    top or bottom edge is invisible to the audience. Titles are already covered by
    `title_clipped`; this scan covers body copy, list rows, table cells and footers, which
    is where dense decks actually lose lines on short windows and in play mode.
    """
    return """
    ({ slideIndex, tolerance, mode }) => {
      const decorativePattern = /(orb|deco|decor|ornament|shape|rule|divider|ghost|mesh|gradient|blob|bg|cloud|noise|grid|watermark|template-source)/i;
      const chromeSelector = '[aria-hidden="true"], .notes-panel, #notes-panel, .slide-credit, #present-counter, .edit-hotzone, #present-btn, .nav-dots, #nav-dots';
      const slides = Array.from(document.querySelectorAll('.slide'));
      if (!slides.length) return [];
      const idx = Math.max(0, Math.min((slideIndex || 1) - 1, slides.length - 1));
      const slide = slides[idx];
      const slideRect = slide.getBoundingClientRect();
      if (slideRect.width < 2 || slideRect.height < 2) return [];

      const isScreenReaderOnly = (node) => {
        const style = window.getComputedStyle(node);
        if (style.clipPath && style.clipPath !== 'none') return true;
        if (style.clip && style.clip !== 'auto') return true;
        return false;
      };

      const out = [];
      const candidates = Array.from(slide.querySelectorAll(
        'h1, h2, h3, h4, h5, h6, p, li, td, th, dd, dt, blockquote, figcaption, code, pre, span, small, strong, em, div, label'
      ));
      for (const node of candidates) {
        const text = (node.innerText || node.textContent || '').replace(/\\s+/g, ' ').trim();
        if (!text) continue;
        // Only leaf-ish text holders, so one clipped line is reported once.
        if (Array.from(node.children).some((child) => (child.textContent || '').trim())) continue;
        const style = window.getComputedStyle(node);
        if (style.display === 'none' || style.visibility === 'hidden') continue;
        if (Number(style.opacity || '1') < 0.05) continue;
        if (node.closest(chromeSelector)) continue;
        if (decorativePattern.test(Array.from(node.classList || []).join(' '))) continue;
        if (isScreenReaderOnly(node)) continue;
        const rect = node.getBoundingClientRect();
        if (rect.width < 1 || rect.height < 1) continue;
        // Require horizontal intersection so off-canvas metadata markers
        // (left: -9999px) are not reported as clipped content.
        if (rect.right < slideRect.left + 1 || rect.left > slideRect.right - 1) continue;
        const below = rect.bottom - slideRect.bottom;
        const above = slideRect.top - rect.top;
        const overflow = Math.max(below, above);
        if (overflow <= tolerance) continue;
        out.push({
          slide_index: slideIndex,
          mode,
          selector: node.id
            ? `#${node.id}`
            : `${node.tagName.toLowerCase()}${Array.from(node.classList || []).slice(0, 1).map((cls) => `.${cls}`).join('')}`,
          text: text.slice(0, 120),
          rect: { x: rect.left, y: rect.top, width: rect.width, height: rect.height },
          slide_rect: { x: slideRect.left, y: slideRect.top, width: slideRect.width, height: slideRect.height },
          clipped_px: Math.round(overflow * 10) / 10,
          edge: below >= above ? 'bottom' : 'top',
        });
      }
      return out;
    }
    """


def _wait_for_deterministic_layout(page) -> bool:
    return bool(
        page.evaluate(
            """
            async () => {
              if (document.fonts && document.fonts.ready) {
                await document.fonts.ready;
              }
              const tracked = () => Array.from(document.querySelectorAll('[data-geometry-target], h1, h2, h3, code, pre, .code-block, .command, .cmd, .terminal'))
                .map((node) => {
                  const rect = node.getBoundingClientRect();
                  return [Math.round(rect.left * 10) / 10, Math.round(rect.top * 10) / 10, Math.round(rect.width * 10) / 10, Math.round(rect.height * 10) / 10].join(',');
                })
                .join('|');
              const before = tracked();
              await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
              const after = tracked();
              return before === after;
            }
            """
        )
    )


def _capture_screenshot(page, *, attempts: int = 2) -> bytes:
    for attempt in range(max(1, attempts)):
        try:
            return page.screenshot(full_page=False, timeout=30000)
        except Exception:
            if attempt + 1 >= max(1, attempts):
                raise
            page.wait_for_timeout(100)
    raise AssertionError("screenshot retry loop exited without a result")


def _measure_viewport(
    page,
    viewport: dict[str, int],
    stable_runs: int,
    *,
    mode: str = "window",
) -> tuple[list[dict[str, Any]], bool]:
    slide_records: list[dict[str, Any]] = []
    overall_stable = True
    for slide_index in range(1, _slide_count(page) + 1):
        _activate_slide(page, slide_index, mode=mode)
        _wait_for_deterministic_layout(page)
        signatures: list[list[dict[str, Any]]] = []
        measurements: list[dict[str, Any]] = []
        for _run_index in range(max(1, stable_runs)):
            run_measurements = page.evaluate(
                _measure_targets_script(),
                {"viewport": viewport, "slideIndex": slide_index},
            )
            signatures.append(_measurement_signature(run_measurements))
            measurements = run_measurements
        for item in measurements:
            item["mode"] = mode
        clipped = page.evaluate(
            _measure_clipping_script(),
            {"slideIndex": slide_index, "tolerance": CLIPPING_TOLERANCE_PX, "mode": mode},
        )
        stable = all(signature == signatures[0] for signature in signatures[1:])
        overall_stable = overall_stable and stable
        slide_records.append(
            {
                "slide_index": slide_index,
                "mode": mode,
                "measurements": measurements,
                "clipped": clipped,
                "screenshot_bytes": _capture_screenshot(page),
            }
        )
    return slide_records, overall_stable


def _contrast_violations(
    measurements: list[dict[str, Any]],
    screenshot_bytes: bytes,
    *,
    evidence_image: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    image = Image.open(io.BytesIO(screenshot_bytes)).convert("RGB")
    violations: list[dict[str, Any]] = []
    telemetry: list[dict[str, Any]] = []
    for item in measurements:
        if not item.get("text") or not item.get("visible"):
            continue
        color = _parse_rgb(item.get("color"))
        if color is None:
            continue
        role = str(item.get("role", ""))
        if role not in {"title", "text", "command"}:
            continue
        rect = item["rect"]
        points = _sample_points(rect, image)
        samples = [image.getpixel(point) for point in points]
        background_samples = _dominant_background_samples(samples, color)
        variance = _background_variance(background_samples)
        if item.get("complex_background") or variance > 0.035:
            telemetry.append(
                {
                    "type": "needs_contract_policy",
                    "reason": "complex_background_contrast",
                    "slide_index": item.get("slide_index"),
                    "selector": item.get("selector"),
                    "text": item.get("text"),
                    "rect": _round_rect(rect),
                }
            )
            continue

        observed = _representative_contrast_ratio(color, background_samples)
        threshold = 3.0 if float(item.get("font_size") or 16) >= 24 else 4.5
        if observed < threshold:
            violations.append(
                {
                    "type": "low_contrast",
                    "code": HARD_FAILURE_CODES["low_contrast"],
                    "severity": "hard",
                    "slide_index": item.get("slide_index"),
                    "selector": item.get("selector"),
                    "text": item.get("text"),
                    "rect": _round_rect(rect),
                    "contrast_ratio": round(observed, 3),
                    "threshold": threshold,
                    "evidence_image": evidence_image,
                }
            )
    return violations, telemetry


def _geometry_violations(measurements: list[dict[str, Any]], *, evidence_image: str) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    checks = [
        ("invisible_target", "invisible_target"),
        ("title_clipped", "title_clipped"),
        ("text_overflow", "text_overflow"),
        ("empty_component", "empty_component"),
        ("character_overlap", "character_overlap"),
    ]
    for item in measurements:
        for flag, violation_type in checks:
            if not item.get(flag):
                continue
            violations.append(
                {
                    "type": violation_type,
                    "code": HARD_FAILURE_CODES[violation_type],
                    "severity": "hard",
                    "slide_index": item.get("slide_index"),
                    "selector": item.get("selector"),
                    "role": item.get("role"),
                    "text": item.get("text"),
                    "rect": _round_rect(item.get("rect", {})),
                    "evidence_image": evidence_image,
                }
            )
    return violations


def _clipping_violations(
    clipped: list[dict[str, Any]],
    *,
    viewport: dict[str, int],
    mode: str,
    evidence_image: str,
) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    for item in clipped:
        violations.append(
            {
                "type": "content_clipped",
                "code": HARD_FAILURE_CODES["content_clipped"],
                "severity": "hard",
                "mode": mode,
                "viewport": dict(viewport),
                "slide_index": item.get("slide_index"),
                "selector": item.get("selector"),
                "role": "text",
                "text": item.get("text"),
                "rect": _round_rect(item.get("rect", {})),
                "slide_rect": _round_rect(item.get("slide_rect", {})),
                "clipped_px": item.get("clipped_px"),
                "edge": item.get("edge"),
                "evidence_image": evidence_image,
            }
        )
    return violations


def analyze_browser_geometry_html(
    html_text: str,
    *,
    preset: str | None = None,
    viewports: list[dict[str, int]] | None = None,
    stable_runs: int = 3,
    artifact_dir: str | Path | None = None,
    modes: tuple[str, ...] | list[str] | None = None,
) -> dict[str, Any]:
    viewports = viewports or DEFAULT_VIEWPORTS
    modes = tuple(modes) if modes else ("window",)
    unknown_modes = [mode for mode in modes if mode not in MEASUREMENT_MODES]
    if unknown_modes:
        raise ValueError(f"unsupported measurement modes: {unknown_modes}")
    all_measurements: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []
    telemetry: list[dict[str, Any]] = []
    layout_settled = True
    stable = True
    screenshot_refs: list[str] = []
    present_mode_entered: dict[str, bool] = {}

    with tempfile.TemporaryDirectory(prefix="browser-geometry-qa-") as temp_dir:
        html_path = Path(temp_dir) / "deck.html"
        html_path.write_text(html_text, encoding="utf-8")
        playwright, browser = _launch_browser()
        try:
            for viewport in viewports:
                for mode in modes:
                    context = browser.new_context(
                        viewport={"width": int(viewport["width"]), "height": int(viewport["height"])},
                        device_scale_factor=DEVICE_PIXEL_RATIO,
                    )
                    page = context.new_page()
                    try:
                        page.goto(html_path.as_uri(), wait_until="load", timeout=20000)
                        page.add_style_tag(content=QA_FREEZE_CSS)
                        layout_settled = _wait_for_deterministic_layout(page) and layout_settled
                        if mode == "present":
                            entered = _enter_present_mode(page)
                            present_mode_entered[f"{viewport['width']}x{viewport['height']}"] = entered
                            if not entered:
                                telemetry.append(
                                    {
                                        "type": "needs_contract_policy",
                                        "reason": "present_mode_not_entered",
                                        "viewport": dict(viewport),
                                    }
                                )
                                continue
                            _wait_for_deterministic_layout(page)
                        slide_records, viewport_stable = _measure_viewport(
                            page, viewport, stable_runs, mode=mode
                        )
                        stable = stable and viewport_stable
                        for record in slide_records:
                            measurements = record["measurements"]
                            screenshot_bytes = record["screenshot_bytes"]
                            evidence_image = _artifact_reference(
                                screenshot_bytes,
                                artifact_dir=artifact_dir,
                                label=(
                                    f"browser-geometry-{mode}-slide-{record['slide_index']}-"
                                    f"{viewport['width']}x{viewport['height']}"
                                ),
                            )
                            screenshot_refs.append(evidence_image)
                            all_measurements.extend(measurements)
                            violations.extend(_geometry_violations(measurements, evidence_image=evidence_image))
                            violations.extend(
                                _clipping_violations(
                                    record.get("clipped", []),
                                    viewport=viewport,
                                    mode=mode,
                                    evidence_image=evidence_image,
                                )
                            )
                            if mode == "window":
                                contrast_violations, contrast_telemetry = _contrast_violations(
                                    measurements, screenshot_bytes, evidence_image=evidence_image
                                )
                                violations.extend(contrast_violations)
                                telemetry.extend(contrast_telemetry)
                    finally:
                        context.close()
        finally:
            browser.close()
            playwright.stop()

    hard_failures: list[str] = []
    for violation in violations:
        code = str(violation["code"])
        if code not in hard_failures:
            hard_failures.append(code)

    diagnostics = {
        "target_count": len(all_measurements),
        "hard_violation_count": len(violations),
        "telemetry_count": len(telemetry),
        "viewport_count": len(viewports),
        "mode_count": len(modes),
        "clipped_violation_count": len([v for v in violations if v.get("type") == "content_clipped"]),
        "stable_measurement": stable,
    }
    return {
        "version": REPORT_VERSION,
        "status": "pass" if not violations else "fail",
        "pass": not violations,
        "preset": preset,
        "hard_failures": hard_failures,
        "violations": violations,
        "telemetry": telemetry,
        "measurements": all_measurements,
        "diagnostics": diagnostics,
        "runner": {
            "viewports": viewports,
            "modes": list(modes),
            "present_mode_entered": present_mode_entered,
            "clipping_tolerance_px": CLIPPING_TOLERANCE_PX,
            "device_pixel_ratio": DEVICE_PIXEL_RATIO,
            "stable_runs": stable_runs,
            "fonts_ready": True,
            "animation_frozen": True,
            "layout_settled": layout_settled,
            "stable_measurement": stable,
            "qa_css_sha256": hashlib.sha256(QA_FREEZE_CSS.encode("utf-8")).hexdigest(),
            "screenshots": screenshot_refs,
        },
        "phase": "0.5-contract-independent",
    }


def analyze_browser_geometry_path(
    path: str | Path,
    *,
    preset: str | None = None,
    viewports: list[dict[str, int]] | None = None,
    stable_runs: int = 3,
    artifact_dir: str | Path | None = None,
    modes: tuple[str, ...] | list[str] | None = None,
) -> dict[str, Any]:
    report = analyze_browser_geometry_html(
        _read_text(path),
        preset=preset,
        viewports=viewports,
        stable_runs=stable_runs,
        artifact_dir=artifact_dir,
        modes=modes,
    )
    report["html_path"] = str(path)
    return report


def _parse_viewport(value: str) -> dict[str, int]:
    parts = value.lower().split("x")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("viewport must be WIDTHxHEIGHT")
    try:
        width, height = int(parts[0]), int(parts[1])
    except ValueError as exc:
        raise argparse.ArgumentTypeError("viewport must contain integer dimensions") from exc
    return {"width": width, "height": height}


def main() -> int:
    parser = argparse.ArgumentParser(description="Browser Geometry QA Phase 0.5 gate.")
    parser.add_argument("html_path", help="Path to the generated HTML deck")
    parser.add_argument("--preset", help="Optional preset override")
    parser.add_argument("--output", help="Optional output path for the JSON report")
    parser.add_argument("--artifact-dir", help="Directory for evidence screenshots")
    parser.add_argument("--viewport", action="append", type=_parse_viewport, help="Viewport as WIDTHxHEIGHT")
    parser.add_argument(
        "--laptop-window",
        action="store_true",
        help=f"Add the short laptop window viewport ({LAPTOP_WINDOW_VIEWPORT['width']}x{LAPTOP_WINDOW_VIEWPORT['height']})",
    )
    parser.add_argument(
        "--mode",
        choices=("window", "present", "both"),
        default="window",
        help="Measure window scrolling geometry, play-mode geometry (fixed 1440x900 box), or both",
    )
    parser.add_argument("--stable-runs", type=int, default=3, help="Repeated measurements per viewport")
    parser.add_argument("--strict", action="store_true", help="Return exit code 1 when hard failures exist")
    args = parser.parse_args()

    viewports = list(args.viewport or DEFAULT_VIEWPORTS)
    if args.laptop_window and LAPTOP_WINDOW_VIEWPORT not in viewports:
        viewports.append(dict(LAPTOP_WINDOW_VIEWPORT))
    modes = MEASUREMENT_MODES if args.mode == "both" else (args.mode,)

    report = analyze_browser_geometry_path(
        args.html_path,
        preset=args.preset,
        viewports=viewports,
        stable_runs=args.stable_runs,
        artifact_dir=args.artifact_dir,
        modes=modes,
    )
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    if args.strict and not report["pass"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
