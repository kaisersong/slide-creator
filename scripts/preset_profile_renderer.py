from __future__ import annotations

import hashlib
import html
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from preset_profile_specs import PROFILE_SPECS, PresetProfileSpec


PROFILE_FAMILY_REGISTRY = {preset: spec.family for preset, spec in PROFILE_SPECS.items()}

PROFILE_LAYOUTS = {
    "editorial_static": ("profile_masthead", "profile_columns", "profile_pullquote", "profile_index", "profile_close"),
    "signal_pitch": ("profile_hero", "profile_signal_grid", "profile_split", "profile_timeline", "profile_close"),
    "technical_terminal": ("profile_terminal", "profile_code_split", "profile_cards", "profile_timeline", "profile_close"),
    "glass_material": ("glass_hero", "glass_card", "glass_split", "glass_trio", "glass_stat"),
    "consulting_structured": ("profile_exec", "profile_matrix", "profile_split", "profile_timeline", "profile_close"),
    "brutalist_graphic": ("profile_poster", "profile_blocks", "profile_split", "profile_manifesto", "profile_close"),
}

FAMILY_LABELS = {
    "editorial_static": "Editorial",
    "signal_pitch": "Signal",
    "technical_terminal": "Terminal",
    "glass_material": "Glass",
    "consulting_structured": "Advisory",
    "brutalist_graphic": "Brutalist",
    "geometric_soft": "Geometry",
    "split_editorial": "Split",
}

ROLE_LABELS_ZH = {
    "cover": "封面",
    "problem": "问题",
    "solution": "方案",
    "workflow": "流程",
    "evidence": "证据",
    "comparison": "对比",
    "cta_close": "行动",
    "close": "收束",
}

ROLE_LABELS_EN = {
    "cover": "COVER",
    "problem": "PROBLEM",
    "solution": "SOLUTION",
    "workflow": "FLOW",
    "evidence": "EVIDENCE",
    "comparison": "COMPARE",
    "cta_close": "ACTION",
    "close": "CLOSE",
}

FORBIDDEN_MARKER_CLASSES = {
    "bg-cool",
    "bg-warm",
    "bg-mint",
    "dark-text",
    "light-text",
    "glass-grid",
    "glass-slide-center",
}

DEMO_SLUG_BY_PRESET = {
    "Aurora Mesh": "aurora-mesh",
    "Bold Signal": "bold-signal",
    "Creative Voltage": "creative-voltage",
    "Dark Botanical": "dark-botanical",
    "Electric Studio": "electric-studio",
    "Glassmorphism": "glassmorphism",
    "Modern Newspaper": "modern-newspaper",
    "Neo-Brutalism": "neo-brutalism",
    "Neo-Retro Dev Deck": "neo-retro-dev",
    "Neon Cyber": "neon-cyber",
    "Notebook Tabs": "notebook-tabs",
    "Paper & Ink": "paper-ink",
    "Pastel Geometry": "pastel-geometry",
    "Split Pastel": "split-pastel",
    "Strategy Consulting": "strategy-consulting",
    "Terminal Green": "terminal-green",
    "Vintage Editorial": "vintage-editorial",
}

TITLE_SELECTORS = (
    ".hero-title",
    ".main-title",
    ".display-title",
    ".elec-title",
    ".bold-title",
    ".brute-title",
    ".nb-title",
    ".headline",
    ".manifesto-headline",
    ".pull-quote",
    ".cta-title",
    ".sc-action-title",
    ".profile-title",
    ".glass-title",
    ".t-title",
    ".t-h2",
    ".a-title",
    ".a-h2",
    ".aurora-subtitle.stat-sub",
    "h1",
    "h2",
)

BODY_SELECTORS = (
    ".hero-sub",
    ".elec-body",
    ".bold-body",
    ".nb-body",
    ".body-text",
    ".body-muted",
    ".cta-sub",
    ".cta-body",
    ".comment",
    "p",
)

LABEL_SELECTORS = (
    ".elec-label",
    ".bold-label",
    ".nb-label",
    ".label",
    ".eyebrow",
    ".hero-brand",
    ".brute-tag",
    ".badge",
)

ITEM_TITLE_SELECTORS = (
    ".feat-card-title",
    ".feature-name",
    ".feature-title",
    ".arch-layer-title",
    ".layer-label",
    ".install-label",
    ".badge-pill",
    ".nb-card-title",
    ".stat-label",
    ".metric-label",
    ".cmd-name",
    "h3",
)

ITEM_BODY_SELECTORS = (
    ".feat-card-desc",
    ".feature-desc",
    ".arch-layer-desc",
    ".install-command",
    ".install-copy",
    ".badge-desc",
    ".nb-card-body",
    ".stat-sub",
    ".metric-body",
    ".cmd-desc",
)

NUMBER_SELECTORS = (
    ".elec-stat-number",
    ".nb-stat",
    ".bold-stat",
    ".stat-num",
    ".stat-value",
    ".metric-num-pink",
    ".num",
)

READABLE_PROFILE_INK = {
    "Bold Signal": "#ffffff",
    "Electric Studio": "#ffffff",
    "Paper & Ink": "#1a1a1a",
    "Modern Newspaper": "#111111",
}

PICTORIAL_EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA70-\U0001FAFF"
    "\ufe0f"
    "]+",
    flags=re.UNICODE,
)

LATIN_TITLE_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*")
TITLE_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*|[\u4e00-\u9fff]|[^\sA-Za-z0-9\u4e00-\u9fff]")

SIGNATURE_TARGET_SKIP_CLASSES = {
    "profile-content",
    "slide-content",
    "title-line",
    "title-balance",
    "profile-fit-title",
    "profile-fit-title-long",
    "profile-fit-title-xlong",
    "profile-fit-title-xxlong",
    "paper",
    "paper-content",
    "tabs",
    "binder-holes",
    "bottom-panel",
    "cover-inner",
    "cta-inner",
    "elec-quote-block",
    "left-panel",
    "panel-content",
    "right-panel",
    "badges",
    "stat-group",
    "top-panel",
    "cards-grid",
    "feat-grid",
    "feature-grid",
    "grid",
    "pills",
    "glass-orb",
    "geo-accent",
    "install-blocks",
    "install-item",
    "install-label",
    "install-row",
    "aurora-slide",
    "aurora-content",
    "aurora-badge",
    "aurora-divider",
    "cta-pill",
    "code-block",
    "style-name",
    "style-desc",
    "slide-num",
    "breadcrumb",
    "bold-ghost",
    "bold-label",
    "bold-stat",
    "bold-cmd",
    "np-ghost",
    "np-stamp",
    "deco-num",
    "deco-circle",
    "metric-num",
    "cyber-label",
    "ba-list",
    "ba-panel",
    "badge-row",
    "fade-in",
    "metrics-grid",
    "preset-grid",
    "rule",
    "rule-thick",
    "section-id",
    "slide-content-anim",
    "step-editorial",
    "voltage-grid",
}


@dataclass(frozen=True)
class PresetProfilePayload:
    canonical_preset: str
    generation_status: str
    renderer_strategy: str
    render_path: str
    css: str
    sections_html: str
    body_classes: tuple[str, ...]
    body_data_attrs: dict[str, str]
    slide_count: int
    style_signature: dict[str, Any]


def profile_auto_contrast_script() -> str:
    return """
<script>
(function () {
  const TARGET_SELECTOR = 'body[data-renderer-strategy="unified_profile"] .profile-content :is(h1,h2,h3,p,li,blockquote,code,pre,.reveal,.body-text,.body-muted,.aurora-subtitle,.feat-card-desc,.feat-name,.elec-title,.elec-body,.code-block,.bold-cmd,.np-cmd,.neon-body,.hero-title,.hero-sub,.hero-subtitle,.display-title,.headline,.np-body,.cta-sub,.comment,.glass-body,.profile-lede,.cmd,.cmd-name,.cmd-desc,.install-label,.install-copy,.pullquote,.pain-body,.step-ed-body,.link-text)';

  function parseRgb(value) {
    const match = String(value || '').match(/rgba?\\(([^)]+)\\)/i);
    if (!match) return null;
    const parts = match[1].split(',').map((part) => Number.parseFloat(part.trim()));
    if (parts.length < 3 || parts.slice(0, 3).some((part) => !Number.isFinite(part))) return null;
    return {
      r: Math.max(0, Math.min(255, parts[0])),
      g: Math.max(0, Math.min(255, parts[1])),
      b: Math.max(0, Math.min(255, parts[2])),
      a: Number.isFinite(parts[3]) ? Math.max(0, Math.min(1, parts[3])) : 1
    };
  }

  function blend(fg, bg) {
    return {
      r: fg.r * fg.a + bg.r * (1 - fg.a),
      g: fg.g * fg.a + bg.g * (1 - fg.a),
      b: fg.b * fg.a + bg.b * (1 - fg.a),
      a: 1
    };
  }

  function luminance(color) {
    const channels = [color.r, color.g, color.b].map((value) => {
      const normalized = value / 255;
      return normalized <= 0.03928 ? normalized / 12.92 : Math.pow((normalized + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
  }

  function contrast(a, b) {
    const first = luminance(a);
    const second = luminance(b);
    const lighter = Math.max(first, second);
    const darker = Math.min(first, second);
    return (lighter + 0.05) / (darker + 0.05);
  }

  function renderedForeground(foreground, background) {
    return blend(foreground, background);
  }

  function effectiveBackground(node) {
    const stack = [];
    let current = node;
    while (current && current.nodeType === Node.ELEMENT_NODE) {
      stack.unshift(current);
      current = current.parentElement;
    }
    let bg = { r: 255, g: 255, b: 255, a: 1 };
    for (const element of stack) {
      const parsed = parseRgb(window.getComputedStyle(element).backgroundColor);
      if (parsed && parsed.a > 0.01) {
        bg = blend(parsed, bg);
      }
    }
    return bg;
  }

  function applyProfileAutoContrast() {
    for (const node of document.querySelectorAll(TARGET_SELECTOR)) {
      const text = (node.innerText || node.textContent || '').replace(/\\s+/g, ' ').trim();
      if (!text) continue;
      const style = window.getComputedStyle(node);
      const current = parseRgb(style.color);
      if (!current) continue;
      const background = effectiveBackground(node);
      const fontSize = Number.parseFloat(style.fontSize || '16') || 16;
      const threshold = fontSize >= 24 ? 3 : 4.5;
      const dark = { r: 17, g: 17, b: 17, a: 1 };
      const light = { r: 255, g: 255, b: 255, a: 1 };
      const currentRatio = contrast(renderedForeground(current, background), background);
      const darkRatio = contrast(dark, background);
      const lightRatio = contrast(light, background);
      if (currentRatio >= threshold) {
        continue;
      }
      if (darkRatio >= lightRatio) {
        node.style.color = '#111111';
      } else {
        node.style.color = '#ffffff';
      }
      node.setAttribute('data-profile-contrast-adjusted', 'true');
    }
  }

  window.applyProfileAutoContrast = applyProfileAutoContrast;
  const schedule = () => requestAnimationFrame(() => requestAnimationFrame(applyProfileAutoContrast));
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', schedule, { once: true });
  } else {
    schedule();
  }
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(schedule).catch(function () {});
  }
})();
</script>
""".strip()


def _discover_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "demos").is_dir() and (candidate / "references").is_dir() and (candidate / "schemas").is_dir():
            return candidate
    return here.parent


ROOT = _discover_root()


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _is_zh_language(language: str) -> bool:
    return (language or "").lower().startswith("zh")


def _section_role_label(role: str, language: str) -> str:
    role_key = (role or "slide").strip().lower()
    if _is_zh_language(language):
        return ROLE_LABELS_ZH.get(role_key, "页面")
    return ROLE_LABELS_EN.get(role_key, role_key.replace("_", " ").upper()[:12] or "SLIDE")


def _compact(value: str, *, limit: int = 86) -> str:
    cleaned = re.sub(r"\s+", " ", value or "").strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip(" ,;:-") + "..."


def _is_latin_title_token(value: str) -> bool:
    return bool(LATIN_TITLE_TOKEN_RE.fullmatch(value or ""))


def _title_token_width(token: str) -> float:
    if _is_latin_title_token(token):
        return max(1.4, len(token) * 0.58)
    if re.fullmatch(r"[\u4e00-\u9fff]", token or ""):
        return 1.0
    if token in {"，", "。", "、", "；", "：", "！", "？", ",", ".", ";", ":", "!", "?", ")", "]", "）"}:
        return 0.35
    return 0.7


def _title_visual_width(value: str) -> float:
    return sum(_title_token_width(token) for token in TITLE_TOKEN_RE.findall(value or ""))


def _punctuation_title_lines(cleaned: str, line_count: int) -> list[str]:
    if line_count != 2:
        return []
    candidates: list[tuple[float, list[str]]] = []
    for match in re.finditer(r"[，,、；;：:]", cleaned):
        left = cleaned[: match.end()].strip()
        right = cleaned[match.end() :].strip()
        if not left or not right:
            continue
        left_width = _title_visual_width(left)
        right_width = _title_visual_width(right)
        if min(left_width, right_width) < 4:
            continue
        candidates.append((abs(left_width - right_width), [left, right]))
    if not candidates:
        return []
    return sorted(candidates, key=lambda item: item[0])[0][1]


def _join_title_tokens(tokens: list[str]) -> str:
    result = ""
    previous = ""
    for token in tokens:
        if not result:
            result = token
        elif _is_latin_title_token(previous) and _is_latin_title_token(token):
            result += " " + token
        elif _is_latin_title_token(previous) and re.fullmatch(r"[\u4e00-\u9fff]", token):
            result += " " + token
        elif re.fullmatch(r"[\u4e00-\u9fff]", previous) and _is_latin_title_token(token):
            result += " " + token
        else:
            result += token
        previous = token
    return result.strip()


def _balanced_title_lines(cleaned: str, line_count: int) -> list[str]:
    tokens = TITLE_TOKEN_RE.findall(cleaned)
    if not tokens:
        return [cleaned]
    total_width = sum(_title_token_width(token) for token in tokens)
    target = max(1.0, total_width / line_count)
    lines: list[list[str]] = []
    current: list[str] = []
    current_width = 0.0

    for token in tokens:
        token_width = _title_token_width(token)
        can_break = token not in {"，", "。", "、", "；", "：", "！", "？", ",", ".", ";", ":", "!", "?", ")", "]", "）"}
        if current and can_break and len(lines) < line_count - 1 and current_width >= target * 0.72 and current_width + token_width > target:
            lines.append(current)
            current = [token]
            current_width = token_width
        else:
            current.append(token)
            current_width += token_width

    if current:
        lines.append(current)
    return [_join_title_tokens(line) for line in lines if _join_title_tokens(line)]


def _title_fit_classes(value: str) -> list[str]:
    width = _title_visual_width(value)
    classes = ["profile-fit-title"]
    if width > 38:
        classes.append("profile-fit-title-xxlong")
    elif width > 28:
        classes.append("profile-fit-title-xlong")
    elif width > 18:
        classes.append("profile-fit-title-long")
    return classes


def _title_lines(value: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", value or "").strip()
    if not cleaned:
        return []
    visual_width = _title_visual_width(cleaned)
    if re.search(r"[\u4e00-\u9fff]", cleaned) and visual_width > 28:
        line_count = 2 if visual_width <= 54 else 3
        punctuated = _punctuation_title_lines(cleaned, line_count)
        if punctuated:
            return punctuated
        return _balanced_title_lines(cleaned, line_count)
    if len(cleaned) <= 30:
        return [cleaned]
    parts = cleaned.split()
    if len(parts) <= 1:
        return [cleaned]
    if len(parts) == 2:
        return parts
    midpoint = max(1, len(parts) // 2)
    return [" ".join(parts[:midpoint]), " ".join(parts[midpoint:])]


def _title_markup(tag: str, class_name: str, title: str) -> str:
    lines = _title_lines(title)
    if not lines:
        lines = [title]
    inner = "".join(f'<span class="title-line">{_escape(line)}</span>' for line in lines)
    fit_classes = " ".join(_title_fit_classes(title))
    return f'<{tag} class="{class_name} reveal title-balance {fit_classes}">{inner}</{tag}>'


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        cleaned = re.sub(r"\s+", " ", value or "").strip()
        if cleaned and cleaned not in result:
            result.append(cleaned)
    return result


def _items_for_spec(spec: dict[str, Any], *, minimum: int = 3) -> list[str]:
    values = _dedupe(
        [
            *[str(item) for item in spec.get("supporting_items", [])],
            *[str(item) for item in spec.get("supporting_facts", [])],
            *[str(item) for item in spec.get("evidence_items", [])],
            str(spec.get("key_point", "")),
        ]
    )
    if not values:
        values = [str(spec.get("title") or "Key point")]
    while len(values) < minimum:
        values.append(values[-1])
    return values[: max(minimum, 4)]


def _profile_demo_path(profile_spec: PresetProfileSpec, language: str) -> Path | None:
    demo_slug = DEMO_SLUG_BY_PRESET.get(profile_spec.preset)
    if not demo_slug:
        return None
    preferred = "zh" if language.lower().startswith("zh") else "en"
    candidates = [
        ROOT / "demos" / f"{demo_slug}-{preferred}.html",
        ROOT / "demos" / f"{demo_slug}-zh.html",
        ROOT / "demos" / f"{demo_slug}-en.html",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


@lru_cache(maxsize=None)
def _demo_soup(path_text: str) -> BeautifulSoup:
    return BeautifulSoup(Path(path_text).read_text(encoding="utf-8"), "html.parser")


def _demo_font_imports(soup: BeautifulSoup) -> str:
    imports: list[str] = []
    for link in soup.find_all("link"):
        href = str(link.get("href", ""))
        if "fonts.googleapis.com" not in href:
            continue
        if href not in imports:
            imports.append(href)
    return "\n".join(f'@import url("{href.replace(chr(34), "%22")}");' for href in imports)


def _extract_demo_css(demo_path: Path, profile_spec: PresetProfileSpec) -> str:
    soup = _demo_soup(str(demo_path))
    imports = _demo_font_imports(soup)
    css_blocks = [style.get_text("\n") for style in soup.find_all("style")]
    profile_ink = READABLE_PROFILE_INK.get(profile_spec.preset, "var(--text-primary, var(--text, #111111))")
    compatibility = f"""
body[data-renderer-strategy="unified_profile"][data-profile-spec="{_slugify(profile_spec.preset)}"] {{
    --profile-ink: {profile_ink};
    --profile-muted: var(--text-secondary, var(--text-muted, rgba(17, 17, 17, 0.68)));
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="aurora-mesh"],
body[data-renderer-strategy="unified_profile"][data-profile-spec="bold-signal"],
body[data-renderer-strategy="unified_profile"][data-profile-spec="creative-voltage"],
body[data-renderer-strategy="unified_profile"][data-profile-spec="dark-botanical"],
body[data-renderer-strategy="unified_profile"][data-profile-spec="electric-studio"],
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"],
body[data-renderer-strategy="unified_profile"][data-profile-spec="neon-cyber"],
body[data-renderer-strategy="unified_profile"][data-profile-spec="terminal-green"] {{
    --profile-ink: #ffffff;
    --profile-muted: #f7fbff;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="modern-newspaper"],
body[data-renderer-strategy="unified_profile"][data-profile-spec="neo-brutalism"],
body[data-renderer-strategy="unified_profile"][data-profile-spec="neo-retro-dev-deck"],
body[data-renderer-strategy="unified_profile"][data-profile-spec="notebook-tabs"],
body[data-renderer-strategy="unified_profile"][data-profile-spec="paper-ink"],
body[data-renderer-strategy="unified_profile"][data-profile-spec="pastel-geometry"],
body[data-renderer-strategy="unified_profile"][data-profile-spec="split-pastel"],
body[data-renderer-strategy="unified_profile"][data-profile-spec="strategy-consulting"],
body[data-renderer-strategy="unified_profile"][data-profile-spec="vintage-editorial"] {{
    --profile-ink: #111111;
    --profile-muted: #2d2d2d;
}}
body[data-renderer-strategy="unified_profile"] *,
body[data-renderer-strategy="unified_profile"] *::before,
body[data-renderer-strategy="unified_profile"] *::after {{
    box-sizing: border-box;
}}
body[data-renderer-strategy="unified_profile"] :is(p, li, .body-text, .body-muted, .feat-card-desc, .feature-desc, .stat-label, .metric-label, .cmd-name, .cmd-desc, .install-label, .install-copy, .profile-lede, .glass-body, .profile-card-label) {{
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"] :is(.profile-eyebrow, .profile-kicker, .profile-card-label, .profile-lede, .glass-body, .profile-card p, .profile-matrix-cell p, .profile-signature-component p, .sc-evidence-card p) {{
    color: var(--profile-muted) !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="bold-signal"] .bold-hero-card {{
    background: #c43a16 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="bold-signal"] .bold-bullet-list li,
body[data-renderer-strategy="unified_profile"][data-profile-spec="bold-signal"] .bold-callout,
body[data-renderer-strategy="unified_profile"][data-profile-spec="bold-signal"] .bold-cmd {{
    color: #ffffff !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="dark-botanical"] .cta-sub,
body[data-renderer-strategy="unified_profile"][data-profile-spec="neon-cyber"] .neon-body {{
    color: #ffffff !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] .profile-content :is(h1, h2, h3, p.reveal) {{
    color: #101828 !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="notebook-tabs"] #slide-5 .paper-content li,
body[data-renderer-strategy="unified_profile"][data-profile-spec="notebook-tabs"] .cta-sub {{
    color: #ffffff !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="notebook-tabs"] #slide-4 .paper-content li {{
    color: #1a1a1a !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="split-pastel"] .cta-sub {{
    color: #111111 !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="split-pastel"] #slide-1 .hero-sub {{
    color: #555555 !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="creative-voltage"] h2.reveal,
body[data-renderer-strategy="unified_profile"][data-profile-spec="pastel-geometry"] h2.reveal,
body[data-renderer-strategy="unified_profile"][data-profile-spec="split-pastel"] h2.reveal {{
    max-width: min(90vw, 1040px) !important;
    font-size: clamp(1.25rem, 2.8vw, 2.35rem) !important;
    line-height: 1.14 !important;
    overflow-wrap: normal !important;
    word-break: normal !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="modern-newspaper"] .np-headline,
body[data-renderer-strategy="unified_profile"][data-profile-spec="neo-brutalism"] .brute-h2,
body[data-renderer-strategy="unified_profile"][data-profile-spec="vintage-editorial"] .headline {{
    max-width: min(90vw, 980px) !important;
    font-size: clamp(1.25rem, 2.8vw, 2.35rem) !important;
    line-height: 1.12 !important;
    overflow-wrap: normal !important;
    word-break: normal !important;
}}
body[data-renderer-strategy="unified_profile"] .profile-fit-title .title-line {{
    white-space: normal !important;
    word-break: normal !important;
}}
body[data-renderer-strategy="unified_profile"] .profile-generated-title {{
    color: var(--profile-ink) !important;
    font-size: clamp(1.05rem, 2vw, 1.95rem) !important;
    line-height: 1.08 !important;
    margin: 0 0 clamp(0.45rem, 1.1vw, 0.9rem) 0 !important;
    width: min(88vw, 680px) !important;
    max-width: 100% !important;
    position: relative;
    z-index: 3;
    overflow-wrap: anywhere !important;
    word-break: normal !important;
    text-wrap: balance;
}}
body[data-renderer-strategy="unified_profile"] .profile-generated-title .title-line {{
    display: inline !important;
    overflow-wrap: anywhere !important;
    word-break: normal !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="aurora-mesh"] .profile-generated-title,
body[data-renderer-strategy="unified_profile"][data-profile-spec="bold-signal"] .profile-generated-title,
body[data-renderer-strategy="unified_profile"][data-profile-spec="creative-voltage"] .profile-generated-title,
body[data-renderer-strategy="unified_profile"][data-profile-spec="dark-botanical"] .profile-generated-title,
body[data-renderer-strategy="unified_profile"][data-profile-spec="electric-studio"] .profile-generated-title,
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] .profile-generated-title,
body[data-renderer-strategy="unified_profile"][data-profile-spec="neon-cyber"] .profile-generated-title,
body[data-renderer-strategy="unified_profile"][data-profile-spec="terminal-green"] .profile-generated-title {{
    color: #ffffff !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="modern-newspaper"] .np-cmd {{
    writing-mode: horizontal-tb !important;
    text-orientation: mixed !important;
    display: block !important;
    width: min(72vw, 560px) !important;
    min-width: 0 !important;
    height: auto !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    letter-spacing: 0 !important;
    line-height: 1.35 !important;
}}
body[data-renderer-strategy="unified_profile"] .slide-1 {{
    background: var(--bg, var(--bg-primary, inherit));
}}
body[data-renderer-strategy="unified_profile"] .profile-content,
body[data-renderer-strategy="unified_profile"] .left-panel,
body[data-renderer-strategy="unified_profile"] .right-panel,
body[data-renderer-strategy="unified_profile"] .top-panel,
body[data-renderer-strategy="unified_profile"] .bottom-panel {{
    min-width: 0;
    min-height: 0;
    max-width: 100%;
}}
body[data-renderer-strategy="unified_profile"] .profile-fit-title {{
    max-width: 100%;
    overflow-wrap: normal;
    word-break: keep-all;
    hyphens: manual;
    text-wrap: balance;
    line-height: 1.08;
}}
body[data-renderer-strategy="unified_profile"] .profile-fit-title .title-line {{
    display: block;
    max-width: 100%;
    overflow-wrap: normal;
    word-break: keep-all;
    hyphens: manual;
}}
body[data-renderer-strategy="unified_profile"] .profile-fit-title-long {{
    font-size: clamp(1.35rem, 3.4vw, 2.85rem) !important;
}}
body[data-renderer-strategy="unified_profile"] .profile-fit-title-xlong {{
    font-size: clamp(1.2rem, 3.2vw, 2.85rem) !important;
}}
body[data-renderer-strategy="unified_profile"] .profile-fit-title-xxlong {{
    font-size: clamp(1.05rem, 2.8vw, 2.35rem) !important;
}}
body[data-renderer-strategy="unified_profile"] .code-block,
body[data-renderer-strategy="unified_profile"] .install-command,
body[data-renderer-strategy="unified_profile"] .install-copy,
body[data-renderer-strategy="unified_profile"] .bold-cmd,
body[data-renderer-strategy="unified_profile"] .np-cmd,
body[data-renderer-strategy="unified_profile"] .cmd-table,
body[data-renderer-strategy="unified_profile"] pre,
body[data-renderer-strategy="unified_profile"] code {{
    max-width: 100%;
    overflow-wrap: normal;
    word-break: keep-all;
    hyphens: manual;
    letter-spacing: 0 !important;
}}
body[data-renderer-strategy="unified_profile"] .code-block,
body[data-renderer-strategy="unified_profile"] .install-command,
body[data-renderer-strategy="unified_profile"] .install-copy,
body[data-renderer-strategy="unified_profile"] .bold-cmd,
body[data-renderer-strategy="unified_profile"] .np-cmd {{
    white-space: normal;
    overflow: visible;
    text-overflow: clip;
    overflow-wrap: anywhere;
    font-size: clamp(0.72rem, 1vw, 0.9rem);
    line-height: 1.42;
}}
body[data-renderer-strategy="unified_profile"] .badge-pill,
body[data-renderer-strategy="unified_profile"] .pill,
body[data-renderer-strategy="unified_profile"] .label,
body[data-renderer-strategy="unified_profile"] .nb-label,
body[data-renderer-strategy="unified_profile"] .elec-label {{
    overflow-wrap: normal;
    word-break: keep-all;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="bold-signal"] .bold-ghost {{
    display: none !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="bold-signal"] .slide-content {{
    gap: clamp(0.55rem, 1.2vw, 0.9rem);
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="bold-signal"] .slide-content [style*="margin-bottom:1.5rem"] {{
    margin-bottom: clamp(0.55rem, 1.2vw, 0.85rem) !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="bold-signal"] .slide-content [style*="margin-top:1.5rem"] {{
    margin-top: clamp(0.55rem, 1.2vw, 0.85rem) !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="bold-signal"] .slide-content [style*="padding:1.25rem"] {{
    padding: clamp(0.7rem, 1.5vw, 0.95rem) !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="bold-signal"] .bold-callout {{
    margin-top: clamp(0.45rem, 1vw, 0.65rem) !important;
    padding: clamp(0.55rem, 1vw, 0.75rem) clamp(0.8rem, 1.4vw, 1rem) !important;
    font-size: clamp(0.72rem, 1vw, 0.82rem) !important;
    line-height: 1.35 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="bold-signal"] .bold-cmd {{
    min-width: 0;
    white-space: normal;
    overflow-wrap: anywhere;
    word-break: normal;
    line-height: 1.35;
    padding: clamp(0.55rem, 1.1vw, 0.75rem) clamp(0.7rem, 1.4vw, 0.9rem) !important;
    font-size: clamp(0.68rem, 0.9vw, 0.78rem) !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="bold-signal"] .bold-hero-card .bold-label,
body[data-renderer-strategy="unified_profile"][data-profile-spec="bold-signal"] .bold-hero-card p,
body[data-renderer-strategy="unified_profile"][data-profile-spec="bold-signal"] .bold-hero-card > div:first-child {{
    color: #ffffff !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="aurora-mesh"] .code-block {{
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    overflow-wrap: anywhere;
    word-break: normal;
    line-height: 1.42;
    min-width: 0;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="aurora-mesh"] .aurora-badge,
body[data-renderer-strategy="unified_profile"][data-profile-spec="aurora-mesh"] .cta-pill {{
    display: inline-flex !important;
    align-items: center;
    justify-content: center;
    text-align: center;
    min-height: 0;
    line-height: 1.18;
    white-space: normal;
    letter-spacing: 0.04em;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="aurora-mesh"] .cta-pill {{
    padding: clamp(0.8rem, 1.6vw, 1.1rem) clamp(1.4rem, 3vw, 2.4rem) !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="aurora-mesh"] .aurora-subtitle,
body[data-renderer-strategy="unified_profile"][data-profile-spec="aurora-mesh"] .feat-card-title,
body[data-renderer-strategy="unified_profile"][data-profile-spec="aurora-mesh"] .feat-card-desc {{
    letter-spacing: 0;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="aurora-mesh"] .aurora-subtitle.h2-title {{
    color: #ffffff !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="creative-voltage"] #slide-1 .cover-inner,
body[data-renderer-strategy="unified_profile"][data-profile-spec="creative-voltage"] #slide-1 .main-title,
body[data-renderer-strategy="unified_profile"][data-profile-spec="creative-voltage"] #slide-1 .cover-sub,
body[data-renderer-strategy="unified_profile"][data-profile-spec="creative-voltage"] #slide-1 .eyebrow {{
    color: #ffffff !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="creative-voltage"] #slide-1 .title-accent {{
    color: #d4ff00 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="creative-voltage"] #slide-1 .cover-sub {{
    max-width: min(72ch, 74vw);
    margin-top: clamp(0.7rem, 1.4vw, 1rem) !important;
    opacity: 0.86;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="creative-voltage"] #slide-1 .main-title {{
    line-height: 1.02 !important;
    margin-bottom: clamp(0.5rem, 1.2vw, 0.85rem) !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="creative-voltage"] #slide-1 .pill {{
    color: #1a1a2e !important;
    background: #d4ff00 !important;
    border-color: #d4ff00 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="creative-voltage"] .grid-wrap {{
    margin-top: clamp(0.8rem, 1.5vw, 1.2rem) !important;
    max-height: 48vh;
    overflow: visible;
    width: min(92vw, 980px) !important;
    max-width: min(92vw, 980px) !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="creative-voltage"] .voltage-grid {{
    transform: none !important;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)) !important;
    gap: clamp(5px, 0.8vw, 8px) !important;
    width: 100% !important;
    max-width: 100% !important;
    opacity: 1 !important;
    background: transparent !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="creative-voltage"] .voltage-diamond {{
    transform: none !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="creative-voltage"] .vg-cell {{
    min-width: 0;
    white-space: normal;
    overflow-wrap: anywhere;
    line-height: 1.12;
    font-size: clamp(0.58rem, 0.75vw, 0.72rem) !important;
    padding: clamp(0.34rem, 0.7vw, 0.52rem) !important;
    color: #ffffff !important;
    background: rgba(26, 26, 46, 0.72) !important;
    border-color: rgba(212, 255, 0, 0.35) !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="creative-voltage"] .vg-cell.hot {{
    color: #1a1a2e !important;
    background: #d4ff00 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="electric-studio"] .code-block {{
    box-sizing: border-box;
    display: block;
    width: min(100%, 520px);
    max-width: min(100%, 520px);
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="electric-studio"] #slide-7 .install-row {{
    margin-top: clamp(0.55rem, 1vw, 0.8rem) !important;
    transform: translateY(-18px);
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="electric-studio"] #slide-7 .elec-title {{
    font-size: clamp(2rem, 4vw, 3.3rem) !important;
    line-height: 1.04 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="electric-studio"] #slide-7 .install-label {{
    color: #1a1a1a !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] #slide-1 > .profile-content > p.glass-body {{
    color: #101828 !important;
    background: rgba(255, 255, 255, 0.78) !important;
    border: 1px solid rgba(255, 255, 255, 0.45) !important;
    border-radius: 999px !important;
    padding: 0.35rem 0.75rem !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] .pill {{
    background: rgba(10, 16, 32, 0.78) !important;
    color: #ffffff !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] .text-light-theme .pill {{
    background: rgba(255, 255, 255, 0.84) !important;
    color: #1a1a2e !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] #slide-1 .stat-label {{
    color: #101828 !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] #slide-4 .glass-item span,
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] #slide-4 .glass-card span {{
    color: #101828 !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] #slide-8 .glass-card span {{
    color: #ffffff !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] .glass-card {{
    max-width: 100%;
    min-width: 0;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] #slide-5 .glass-card,
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] #slide-6 .glass-card,
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] #slide-7 .glass-card {{
    padding: clamp(0.65rem, 1.2vw, 0.95rem) !important;
    line-height: 1.34;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] #slide-5 h3,
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] #slide-6 h3,
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] #slide-7 h3 {{
    font-size: clamp(0.9rem, 1.5vw, 1.15rem) !important;
    line-height: 1.22;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] #slide-5 .glass-body,
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] #slide-6 .glass-body,
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] #slide-7 .glass-body {{
    font-size: clamp(0.72rem, 1vw, 0.9rem) !important;
    line-height: 1.38 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="modern-newspaper"] .np-ghost {{
    display: none !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="modern-newspaper"] #slide-6 h2 {{
    max-width: min(82vw, 980px);
    font-size: clamp(1.45rem, 3vw, 2.05rem) !important;
    line-height: 1.02 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="modern-newspaper"] #slide-6 [style*="display:grid"] {{
    top: clamp(135px, 24vh, 190px) !important;
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    gap: clamp(6px, 1vw, 10px) !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="modern-newspaper"] #slide-6 .reveal {{
    min-width: 0;
    padding: clamp(0.45rem, 1vw, 0.7rem) !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="modern-newspaper"] #slide-6 .np-rule::before,
body[data-renderer-strategy="unified_profile"][data-profile-spec="modern-newspaper"] #slide-6 .np-rule::after {{
    display: none !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="modern-newspaper"] #slide-6 .np-rule {{
    width: auto !important;
    height: auto !important;
    background: transparent !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="modern-newspaper"] #slide-6 .np-body {{
    font-size: clamp(0.66rem, 0.9vw, 0.82rem) !important;
    line-height: 1.28 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="modern-newspaper"] #slide-7 .np-stamp {{
    color: #111111 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="modern-newspaper"] #slide-7 .profile-eval-card {{
    width: auto !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: clamp(0.65rem, 1.2vw, 0.9rem) clamp(0.8rem, 1.5vw, 1.05rem) !important;
    background: #111111 !important;
    color: #f7f5f0 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="modern-newspaper"] #slide-7 .profile-eval-card .np-stamp,
body[data-renderer-strategy="unified_profile"][data-profile-spec="modern-newspaper"] #slide-7 .profile-eval-card .np-cmd {{
    color: #f7f5f0 !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="neo-retro-dev-deck"] .metric-num {{
    line-height: 0.95;
    margin-bottom: clamp(0.3rem, 0.8vw, 0.6rem);
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="neo-retro-dev-deck"] .label,
body[data-renderer-strategy="unified_profile"][data-profile-spec="neo-retro-dev-deck"] .before-label,
body[data-renderer-strategy="unified_profile"][data-profile-spec="neo-retro-dev-deck"] .after-label,
body[data-renderer-strategy="unified_profile"][data-profile-spec="neo-retro-dev-deck"] .cmd-label,
body[data-renderer-strategy="unified_profile"][data-profile-spec="neo-retro-dev-deck"] .metric-label {{
    color: var(--ink, #111111) !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="neo-retro-dev-deck"] #slide-4 .ba-header.bad,
body[data-renderer-strategy="unified_profile"][data-profile-spec="neo-retro-dev-deck"] #slide-4 .ba-header.good {{
    color: #111111 !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="neo-retro-dev-deck"] #slide-6 .cmd-pink {{
    color: #97133f !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="neo-retro-dev-deck"] #slide-6 .cmd-cyan {{
    color: #006d7d !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="neo-retro-dev-deck"] #slide-6 .cmd-green {{
    color: #166022 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="neo-retro-dev-deck"] #slide-8 .close-block .badge {{
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="neo-retro-dev-deck"] #slide-7 .badge-row .badge {{
    background: #111111 !important;
    color: #ffffff !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="neo-retro-dev-deck"] #slide-8 .close-block .badge-pink {{
    background: #9a1747 !important;
    color: #ffffff !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="neo-retro-dev-deck"] #slide-8 .close-block .badge-cyan-bg {{
    background: #006d7d !important;
    color: #ffffff !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="neo-retro-dev-deck"] #slide-8 .close-block .badge-yellow-bg {{
    background: #ffe14d !important;
    color: #111111 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="neon-cyber"] .cyber-label {{
    display: inline-block;
    margin-bottom: clamp(0.85rem, 1.4vw, 1.15rem) !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="neon-cyber"] .cyber-heading {{
    margin-top: clamp(0.35rem, 0.8vw, 0.65rem) !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="notebook-tabs"] #slide-4 [class*="label"],
body[data-renderer-strategy="unified_profile"][data-profile-spec="notebook-tabs"] #slide-4 .ba-header,
body[data-renderer-strategy="unified_profile"][data-profile-spec="notebook-tabs"] #slide-6 .cmd-name,
body[data-renderer-strategy="unified_profile"][data-profile-spec="notebook-tabs"] #slide-6 .cmd-desc {{
    color: #1a1a1a !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="pastel-geometry"] .hero-brand,
body[data-renderer-strategy="unified_profile"][data-profile-spec="pastel-geometry"] .stat-value,
body[data-renderer-strategy="unified_profile"][data-profile-spec="pastel-geometry"] .stat-label,
body[data-renderer-strategy="unified_profile"][data-profile-spec="pastel-geometry"] .feature-badge {{
    color: #2d2d2d !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="pastel-geometry"] #slide-1 .hero-badge,
body[data-renderer-strategy="unified_profile"][data-profile-spec="pastel-geometry"] #slide-8 .cta-badge {{
    background: #8f3652 !important;
    color: #ffffff !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="pastel-geometry"] #slide-1 .hero-stat-num,
body[data-renderer-strategy="unified_profile"][data-profile-spec="pastel-geometry"] #slide-8 .cta-stat-num {{
    color: #5a3f86 !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="pastel-geometry"] #slide-6 .feat-icon {{
    color: #1a2530 !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="vintage-editorial"] .eyebrow,
body[data-renderer-strategy="unified_profile"][data-profile-spec="vintage-editorial"] .chapter-num,
body[data-renderer-strategy="unified_profile"][data-profile-spec="vintage-editorial"] .feature-badge,
body[data-renderer-strategy="unified_profile"][data-profile-spec="vintage-editorial"] .feature-name,
body[data-renderer-strategy="unified_profile"][data-profile-spec="vintage-editorial"] .feature-desc {{
    color: #4a2f22 !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="vintage-editorial"] .section-id,
body[data-renderer-strategy="unified_profile"][data-profile-spec="vintage-editorial"] .headline,
body[data-renderer-strategy="unified_profile"][data-profile-spec="vintage-editorial"] .pullquote,
body[data-renderer-strategy="unified_profile"][data-profile-spec="vintage-editorial"] .pain-title,
body[data-renderer-strategy="unified_profile"][data-profile-spec="vintage-editorial"] .step-ed-title {{
    color: #1a1a1a !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="vintage-editorial"] .pain-num,
body[data-renderer-strategy="unified_profile"][data-profile-spec="vintage-editorial"] .step-ed-num {{
    color: #5a2a1a !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="vintage-editorial"] .pain-body,
body[data-renderer-strategy="unified_profile"][data-profile-spec="vintage-editorial"] .step-ed-body {{
    color: #333333 !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="notebook-tabs"] .paper-content {{
    width: calc(100% - clamp(72px, 8vw, 96px));
    max-width: calc(100% - clamp(72px, 8vw, 96px));
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="notebook-tabs"] .tabs {{
    pointer-events: none;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] .glass-orb {{
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);
    pointer-events: none;
    z-index: 0;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] .orb-1 {{ width: 400px; height: 400px; background: var(--orb-purple, rgba(102,126,234,0.5)); top: -10%; left: -5%; }}
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] .orb-2 {{ width: 300px; height: 300px; background: var(--orb-pink, rgba(240,147,251,0.4)); bottom: -5%; right: -5%; }}
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] .orb-3 {{ width: 250px; height: 250px; background: var(--orb-mint, rgba(168,237,234,0.4)); top: 30%; right: 15%; }}
body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] .profile-content :is(h1, h2, h3, p.reveal) {{
    display: inline-block;
    width: fit-content;
    max-width: min(88vw, 980px);
    padding: 0.08em 0.22em;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.68) !important;
    color: #101828 !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="notebook-tabs"] #slide-5 .paper-content li {{
    color: #ffffff !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="notebook-tabs"] #slide-5 .manifesto-points li {{
    color: #ffffff !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="creative-voltage"] h2.reveal,
body[data-renderer-strategy="unified_profile"][data-profile-spec="pastel-geometry"] h2.reveal {{
    font-size: clamp(1.05rem, 2.35vw, 1.95rem) !important;
    line-height: 1.18 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="creative-voltage"] p {{
    color: #ffffff !important;
    opacity: 1 !important;
}}
body[data-renderer-strategy="unified_profile"][data-profile-spec="modern-newspaper"] .np-headline,
body[data-renderer-strategy="unified_profile"][data-profile-spec="neo-brutalism"] .brute-h2 {{
    font-size: clamp(1.05rem, 2.35vw, 1.95rem) !important;
    line-height: 1.16 !important;
    max-width: min(92vw, 760px) !important;
}}
@media (max-width: 1300px) {{
    body[data-renderer-strategy="unified_profile"][data-profile-spec="creative-voltage"] h2.reveal,
    body[data-renderer-strategy="unified_profile"][data-profile-spec="modern-newspaper"] .np-headline {{
        font-size: clamp(0.95rem, 2.1vw, 1.65rem) !important;
        line-height: 1.18 !important;
        max-width: min(92vw, 720px) !important;
    }}
    body[data-renderer-strategy="unified_profile"][data-profile-spec="creative-voltage"] #slide-2 h2.reveal {{
        color: #ffffff !important;
        opacity: 1 !important;
        font-size: clamp(0.9rem, 1.85vw, 1.4rem) !important;
        line-height: 1.2 !important;
        max-width: 360px !important;
    }}
}}
@media (max-width: 520px) {{
    body[data-renderer-strategy="unified_profile"] .slide {{
        padding-left: clamp(16px, 6vw, 28px) !important;
        padding-right: clamp(16px, 6vw, 28px) !important;
        overflow: hidden !important;
    }}
    body[data-renderer-strategy="unified_profile"] .profile-content,
    body[data-renderer-strategy="unified_profile"] .slide-content,
    body[data-renderer-strategy="unified_profile"] .content,
    body[data-renderer-strategy="unified_profile"] .left-panel,
    body[data-renderer-strategy="unified_profile"] .right-panel,
    body[data-renderer-strategy="unified_profile"] .top-panel,
    body[data-renderer-strategy="unified_profile"] .bottom-panel,
    body[data-renderer-strategy="unified_profile"] .paper-content,
    body[data-renderer-strategy="unified_profile"] .content-wrapper,
    body[data-renderer-strategy="unified_profile"] .grid-wrap {{
        min-width: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
    }}
    body[data-renderer-strategy="unified_profile"] :is(
        h1,
        h2,
        h3,
        .title-balance,
        .profile-fit-title,
        .profile-fit-title .title-line,
        .hero-title,
        .main-title,
        .display-title,
        .bold-signal-title,
        .aurora-title,
        .aurora-subtitle,
        .voltage-title,
        .glass-title,
        .np-headline,
        .brute-h2,
        .nb-title,
        .headline,
        .t-title,
        .t-h2,
        .a-title
    ) {{
        display: block !important;
        width: auto !important;
        max-width: 100% !important;
        min-width: 0 !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
        overflow-wrap: anywhere !important;
        word-break: normal !important;
        letter-spacing: 0 !important;
        writing-mode: horizontal-tb !important;
        text-orientation: mixed !important;
        transform: none !important;
    }}
    body[data-renderer-strategy="unified_profile"] .profile-fit-title .title-line {{
        display: inline !important;
    }}
    body[data-renderer-strategy="unified_profile"] :is(
        .pill,
        .badge-pill,
        .label,
        .nb-label,
        .elec-label,
        .glass-card,
        .glass-item,
        .bold-cmd,
        .np-cmd,
        .code-block,
        .install-command,
        .install-copy,
        .cmd,
        .cmd-table,
        .code-mono,
        pre,
        code
    ) {{
        min-width: 0 !important;
        max-width: 100% !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
        overflow-wrap: anywhere !important;
        word-break: normal !important;
        letter-spacing: 0 !important;
    }}
    body[data-renderer-strategy="unified_profile"] :is(
        .grid,
        .feature-grid,
        .preset-grid,
        .feat-grid,
        .cards-grid,
        .metrics-grid,
        .voltage-grid,
        .steps-grid,
        .glass-grid
    ) {{
        display: grid !important;
        grid-template-columns: 1fr !important;
        min-width: 0 !important;
        max-width: 100% !important;
    }}
    body[data-renderer-strategy="unified_profile"] :is(.left-panel, .right-panel) {{
        position: relative !important;
        left: auto !important;
        right: auto !important;
    }}
    body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] .profile-content :is(h1, h2, h3, p.reveal) {{
        width: auto !important;
        max-width: 100% !important;
        background: #ffffff !important;
        color: #0f172a !important;
    }}
    body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] .profile-content div.reveal {{
        width: auto !important;
        height: auto !important;
        min-height: 0 !important;
        border-radius: 16px !important;
        padding: 0.65rem 0.8rem !important;
        line-height: 1.28 !important;
    }}
    body[data-renderer-strategy="unified_profile"][data-profile-spec="electric-studio"] #slide-1 .left-panel {{
        box-sizing: border-box !important;
        flex: 0 0 132px !important;
        height: 132px !important;
        min-height: 132px !important;
        max-height: 132px !important;
        overflow: hidden !important;
        padding: 20px 24px 14px !important;
    }}
    body[data-renderer-strategy="unified_profile"][data-profile-spec="electric-studio"] #slide-1 .right-panel {{
        box-sizing: border-box !important;
        padding: 24px !important;
    }}
    body[data-renderer-strategy="unified_profile"][data-profile-spec="electric-studio"] #slide-1 .elec-label {{
        margin-bottom: 8px !important;
        font-size: 10px !important;
        line-height: 1.1 !important;
    }}
    body[data-renderer-strategy="unified_profile"][data-profile-spec="electric-studio"] #slide-1 .elec-title {{
        font-size: clamp(1.25rem, 5.4vw, 1.55rem) !important;
        line-height: 1.03 !important;
        margin: 0 0 4px !important;
    }}
    body[data-renderer-strategy="unified_profile"][data-profile-spec="electric-studio"] #slide-1 .elec-body {{
        font-size: 0.72rem !important;
        line-height: 1.24 !important;
        display: -webkit-box !important;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden !important;
        overflow-wrap: anywhere !important;
    }}
    body[data-renderer-strategy="unified_profile"][data-profile-spec="pastel-geometry"] #slide-4 h2.reveal {{
        position: relative !important;
        top: auto !important;
        margin-top: 0 !important;
    }}
    body[data-renderer-strategy="unified_profile"][data-profile-spec="dark-botanical"] #slide-4,
    body[data-renderer-strategy="unified_profile"][data-profile-spec="pastel-geometry"] #slide-4 {{
        justify-content: flex-start !important;
        padding-top: 28px !important;
    }}
    body[data-renderer-strategy="unified_profile"][data-profile-spec="dark-botanical"] #slide-4 h2,
    body[data-renderer-strategy="unified_profile"][data-profile-spec="pastel-geometry"] #slide-4 h2 {{
        position: relative !important;
        top: auto !important;
        margin-top: 0 !important;
        margin-bottom: 10px !important;
        font-size: clamp(1.1rem, 6vw, 1.55rem) !important;
        line-height: 1.12 !important;
    }}
    body[data-renderer-strategy="unified_profile"][data-profile-spec="dark-botanical"] #slide-4 .preset-grid,
    body[data-renderer-strategy="unified_profile"][data-profile-spec="pastel-geometry"] #slide-4 .preset-grid {{
        grid-template-columns: 1fr !important;
        gap: 6px !important;
        margin-top: 8px !important;
        max-height: calc(100vh - 155px) !important;
        overflow: hidden !important;
    }}
    body[data-renderer-strategy="unified_profile"][data-profile-spec="dark-botanical"] #slide-4 .preset-grid > *:nth-child(n+9),
    body[data-renderer-strategy="unified_profile"][data-profile-spec="pastel-geometry"] #slide-4 .preset-grid > *:nth-child(n+9) {{
        display: none !important;
    }}
    body[data-renderer-strategy="unified_profile"][data-profile-spec="dark-botanical"] #slide-4 .preset-grid > *,
    body[data-renderer-strategy="unified_profile"][data-profile-spec="pastel-geometry"] #slide-4 .preset-grid > * {{
        min-height: 0 !important;
        padding: 8px 10px !important;
    }}
    body[data-renderer-strategy="unified_profile"][data-profile-spec="notebook-tabs"] .paper {{
        width: 100% !important;
        max-width: 100% !important;
    }}
    body[data-renderer-strategy="unified_profile"][data-profile-spec="notebook-tabs"] .paper > .tabs {{
        display: none !important;
    }}
    body[data-renderer-strategy="unified_profile"][data-profile-spec="notebook-tabs"] .paper-content,
    body[data-renderer-strategy="unified_profile"][data-profile-spec="notebook-tabs"] .cta-content {{
        width: 100% !important;
        max-width: 100% !important;
    }}
    body[data-renderer-strategy="unified_profile"][data-profile-spec="notebook-tabs"] #slide-8 .cta-headline {{
        width: auto !important;
        max-width: 100% !important;
        font-size: clamp(1.15rem, 6vw, 1.55rem) !important;
    }}
}}
body[data-renderer-strategy="unified_profile"] .profile-template-source {{
    position: absolute;
    left: -9999px;
    top: auto;
    width: 1px;
    height: 1px;
    overflow: hidden;
}}
""".strip()
    return "\n\n".join(block for block in [imports, *css_blocks, compatibility] if block.strip())


def _demo_section_templates(demo_path: Path) -> list[str]:
    soup = _demo_soup(str(demo_path))
    return [str(section) for section in soup.select("section.slide")]


def _set_node_text(node: Any, value: str) -> None:
    node.clear()
    node.append(_sanitize_pictorial_text(value))


def _set_title_node_text(soup: BeautifulSoup, node: Any, title: str) -> None:
    cleaned_title = _sanitize_pictorial_text(title)
    if node.has_attr("data-text"):
        node["data-text"] = cleaned_title
    _append_class(node, "title-balance")
    for class_name in _title_fit_classes(cleaned_title):
        _append_class(node, class_name)
    node.clear()
    for line in _title_lines(cleaned_title):
        child = soup.new_tag("span")
        child["class"] = ["title-line"]
        child.string = line
        node.append(child)


def _sanitize_pictorial_text(value: str) -> str:
    return PICTORIAL_EMOJI_RE.sub("", value)


def _append_class(node: Any, class_name: str) -> None:
    raw_classes = node.get("class", [])
    classes = raw_classes.split() if isinstance(raw_classes, str) else list(raw_classes)
    if class_name not in classes:
        classes.append(class_name)
        node["class"] = classes


def _ensure_profile_content_scope(soup: BeautifulSoup, section: Any) -> Any | None:
    container = section.select_one(".slide-content, .profile-content, .content")
    if container is not None:
        _append_class(container, "profile-content")
        return container

    children = [child for child in list(section.children) if getattr(child, "name", None)]
    if not children:
        return None
    wrapper = soup.new_tag("div")
    wrapper["class"] = "profile-content"
    wrapper["style"] = "display: contents;"
    for child in children:
        wrapper.append(child.extract())
    section.insert(0, wrapper)
    return wrapper


def _mark_presentational_empty_decor(section: Any) -> None:
    for node in section.select(".pills, .pill-bar, .geo-accent, .binder-holes, .hole"):
        if node.get_text(" ", strip=True):
            continue
        node["aria-hidden"] = "true"
        node["role"] = "presentation"


def _has_meaningful_demo_content(node: Any) -> bool:
    text = re.sub(r"\s+", "", node.get_text("", strip=True))
    if len(text) >= 2:
        return True
    return bool(node.select_one("img,svg,canvas,table,code,pre,path,polygon,circle,rect,line"))


def _signature_target_nodes(scope: Any) -> list[Any]:
    selectors = "h1,h2,h3,p,li,td,code,pre,blockquote,.pill,.stat,.stats,[class]"
    result: list[Any] = []
    for node in scope.select(selectors):
        classes = set(node.get("class", []))
        if "profile-template-source" in classes or "slide-num-label" in classes:
            continue
        if classes & SIGNATURE_TARGET_SKIP_CLASSES:
            continue
        if not _has_meaningful_demo_content(node):
            continue
        if node not in result:
            result.append(node)
    return result


def _ensure_component_richness(section: Any) -> None:
    paragraphs = section.select("p")
    has_rich_component = section.select_one(
        "ul li,ol li,table,svg,pre,code,blockquote,"
        "[class*='card'],[class*='quote'],[class*='pull'],[class*='stat'],"
        "[class*='timeline'],[class*='matrix'],[class*='diagram'],[class*='workflow'],[class*='arch']"
    )
    if has_rich_component is not None or len(paragraphs) > 1:
        return
    scope = section.select_one(".profile-content, .slide-content")
    if scope is None:
        return
    targets = _signature_target_nodes(scope)
    if targets:
        _append_class(targets[0], "profile-eval-card")


def _sanitize_demo_section_text(section: Any) -> None:
    for text_node in list(section.find_all(string=True)):
        cleaned = _sanitize_pictorial_text(str(text_node))
        if cleaned != str(text_node):
            text_node.replace_with(cleaned)


def _ensure_glass_orbs(soup: BeautifulSoup, section: Any, profile_spec: PresetProfileSpec) -> None:
    if profile_spec.preset != "Glassmorphism" or section.select_one(".glass-orb"):
        return
    for class_value in ("glass-orb orb orb1 orb-1", "glass-orb orb orb2 orb-2", "glass-orb orb orb3 orb-3"):
        node = soup.new_tag("div")
        node["class"] = class_value
        node["aria-hidden"] = "true"
        section.insert(0, node)


def _first_text_node(section: Any, selectors: tuple[str, ...]) -> Any | None:
    for selector in selectors:
        node = section.select_one(selector)
        if node and "slide-num-label" not in node.get("class", []):
            return node
    return None


def _nodes(section: Any, selectors: tuple[str, ...]) -> list[Any]:
    result: list[Any] = []
    for selector in selectors:
        for node in section.select(selector):
            if node in result or "slide-num-label" in node.get("class", []):
                continue
            result.append(node)
    return result


def _trim_overloaded_lists(section: Any, *, max_items: int = 6) -> None:
    for list_node in section.select("ul"):
        direct_items = list_node.find_all("li", recursive=False)
        if len(direct_items) <= max_items:
            continue
        for item in direct_items[max_items:]:
            item.decompose()


def _insert_generated_title(soup: BeautifulSoup, section: Any, title: str) -> Any | None:
    container = section.select_one(".paper-content, .slide-content, .profile-content, .strategy-consulting-block") or section
    title_node = soup.new_tag("h2")
    title_node["class"] = "profile-generated-title reveal title-balance " + " ".join(_title_fit_classes(title))
    _set_title_node_text(soup, title_node, title)
    container.insert(0, title_node)
    return title_node


def _numbers_for_spec(spec: dict[str, Any], count: int) -> list[str]:
    blob = " ".join(
        [
            str(spec.get("title", "")),
            str(spec.get("key_point", "")),
            *[str(item) for item in spec.get("supporting_items", [])],
            *[str(item) for item in spec.get("supporting_facts", [])],
        ]
    )
    numbers = re.findall(r"\b\d+(?:[.,]\d+)?%?\b|∞", blob)
    while len(numbers) < count:
        numbers.append(str(len(numbers) + 1))
    return numbers[:count]


def _hydrate_demo_section(
    template_html: str,
    spec: dict[str, Any],
    *,
    total: int,
    layout: str,
    family: str,
    canonical_preset: str,
    slug: str,
    profile_spec: PresetProfileSpec,
    language: str,
) -> str:
    soup = BeautifulSoup(template_html, "html.parser")
    section = soup.select_one("section.slide")
    if section is None:
        return ""

    slide_number = int(spec.get("slide_number") or 1)
    role = str(spec.get("role", "slide"))
    template_role = str(section.get("aria-label") or section.get("data-export-role") or layout)
    export_role = layout if profile_spec.preset == "Glassmorphism" else template_role
    title = str(spec.get("title", ""))
    key_point = _compact(str(spec.get("key_point", "")), limit=150)
    items = _items_for_spec(spec, minimum=8)

    section["id"] = f"slide-{slide_number}"
    classes = list(section.get("class", []))
    for class_name in ("profile-slide", f"pf-{family}", f"preset-{slug}", layout, f"slide-{slide_number}"):
        if class_name not in classes:
            classes.append(class_name)
    section["class"] = classes
    section["data-notes"] = str(spec.get("speaker_note", ""))
    section["aria-label"] = role
    section["data-export-role"] = export_role
    section["data-visual-family"] = family
    section["data-visual-signature"] = f"{slug}-{layout}"
    section["data-template-source"] = "demo"

    title_node = _first_text_node(section, TITLE_SELECTORS)
    if title_node is not None and title:
        _set_title_node_text(soup, title_node, title)
    elif title:
        _insert_generated_title(soup, section, title)

    body_node = _first_text_node(section, BODY_SELECTORS)
    if body_node is not None and key_point:
        _set_node_text(body_node, key_point)

    preserve_cover_label = slide_number == 1 and canonical_preset in {"Creative Voltage", "Electric Studio"}
    if not preserve_cover_label:
        label = _section_role_label(role, language)
        label_limit = 12 if _is_zh_language(language) else 16
        for node in _nodes(section, LABEL_SELECTORS)[:3]:
            _set_node_text(node, _compact(label, limit=label_limit))

    item_title_nodes = _nodes(section, ITEM_TITLE_SELECTORS)
    for index, node in enumerate(item_title_nodes):
        _set_node_text(node, _compact(items[index % len(items)], limit=34))

    item_body_nodes = _nodes(section, ITEM_BODY_SELECTORS)
    for index, node in enumerate(item_body_nodes):
        label_text = item_title_nodes[index].get_text(" ", strip=True) if index < len(item_title_nodes) else ""
        _set_node_text(node, _paired_body_text(items, index, label_text, fallback=key_point, limit=82))

    number_nodes = _nodes(section, NUMBER_SELECTORS)
    numbers = _numbers_for_spec(spec, len(number_nodes))
    if canonical_preset == "Electric Studio" and slide_number == 1:
        numbers = ["21", "0", "∞"][: len(number_nodes)]
    for index, node in enumerate(number_nodes):
        _set_node_text(node, numbers[index])

    for index, node in enumerate(section.select("li")):
        if node.find(True):
            continue
        _set_node_text(node, _compact(items[index % len(items)], limit=76))
    _trim_overloaded_lists(section)

    for index, node in enumerate(section.select("td")):
        if node.find(True):
            continue
        _set_node_text(node, _compact(items[index % len(items)], limit=74))

    slide_label = section.select_one(".slide-num-label")
    if slide_label is not None:
        _set_node_text(slide_label, f"{slide_number:02d} / {total:02d}")

    content_scope = _ensure_profile_content_scope(soup, section)
    if content_scope is not None:
        _append_class(content_scope, f"preset-{slug}-content")
    _ensure_component_richness(section)
    _ensure_glass_orbs(soup, section, profile_spec)
    _mark_presentational_empty_decor(section)
    _sanitize_demo_section_text(section)

    marker = soup.new_tag("span")
    marker["class"] = "profile-template-source"
    marker.string = f"demo-derived:{canonical_preset}"
    section.append(marker)
    return str(section)


def _render_demo_derived_sections(
    specs: list[dict[str, Any]],
    *,
    demo_path: Path,
    layouts: tuple[str, ...],
    family: str,
    canonical_preset: str,
    slug: str,
    profile_spec: PresetProfileSpec,
    language: str,
) -> str:
    templates = _demo_section_templates(demo_path)
    if not templates:
        return ""
    total = len(specs)
    sections = []
    for index, spec in enumerate(specs):
        layout = layouts[index % len(layouts)]
        template_html = templates[index % len(templates)]
        sections.append(
            _hydrate_demo_section(
                template_html,
                spec,
                total=total,
                layout=layout,
                family=family,
                canonical_preset=canonical_preset,
                slug=slug,
                profile_spec=profile_spec,
                language=language,
            )
        )
    sections_html = "\n\n".join(section for section in sections if section)
    if canonical_preset == "Terminal Green":
        sections_html = '<div class="terminal-scanlines" aria-hidden="true"></div>\n\n' + sections_html
    return sections_html


def _text_key(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip().lower()


def _paired_body_text(items: list[str], index: int, label: str, *, fallback: str, limit: int) -> str:
    candidates: list[str] = []
    if items:
        candidates.extend(items[(index + offset) % len(items)] for offset in range(1, len(items)))
    candidates.append(fallback)

    label_key = _text_key(label)
    for candidate in candidates:
        body = _compact(candidate, limit=limit)
        if body and _text_key(body) != label_key:
            return body
    return _compact(fallback or label, limit=limit)


def _safe_marker_classes(style_contract: dict[str, Any], profile_spec: PresetProfileSpec) -> tuple[str, ...]:
    markers: list[str] = []
    for class_name in [*profile_spec.required_component_classes, *profile_spec.signature_classes]:
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", class_name) and class_name not in markers:
            markers.append(class_name)
    for token in style_contract.get("required_signature_classes", []):
        if not isinstance(token, str) or not token.startswith("."):
            continue
        class_name = token[1:]
        if class_name in FORBIDDEN_MARKER_CLASSES:
            continue
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", class_name) and class_name not in markers:
            markers.append(class_name)
        if len(markers) >= 24:
            break
    return tuple(markers)


def _style_signature_hash(canonical_preset: str, family: str, markers: tuple[str, ...]) -> str:
    payload = {
        "preset": canonical_preset,
        "family": family,
        "markers": list(markers),
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    return "sha256:" + digest


def _css_string(value: str) -> str:
    if value in {"inherit", "serif", "sans-serif", "monospace", "system-ui", "-apple-system"}:
        return value
    if re.fullmatch(r"[A-Za-z0-9 -]+", value):
        return '"' + value + '"'
    return value


def _font_stack(profile_spec: PresetProfileSpec) -> str:
    return ", ".join(_css_string(item) for item in profile_spec.fonts)


def _css_var_declarations(profile_spec: PresetProfileSpec) -> str:
    declarations = [f"    {name}: {value};" for name, value in profile_spec.css_vars.items()]
    for index, color in enumerate(profile_spec.colors, start=1):
        declarations.append(f"    --demo-color-{index:02d}: {color};")
    return "\n".join(declarations)


def _palette(profile_spec: PresetProfileSpec, count: int = 6) -> list[str]:
    values = [item for item in profile_spec.colors if item.startswith("#")]
    values.extend(item for item in profile_spec.colors if item.startswith("rgb"))
    if not values:
        values = ["#111111", "#f7f7f3", "#666666"]
    while len(values) < count:
        values.append(values[-1])
    return values[:count]


def _slide_background_css(profile_spec: PresetProfileSpec) -> str:
    palette = _palette(profile_spec, 8)
    preset = profile_spec.preset
    if preset == "Aurora Mesh":
        return """
.slide { background: #0a0a1a; }
.slide-1, .slide-2, .slide-3, .slide-4, .slide-5, .slide-6 { background: radial-gradient(circle at 18% 20%, rgba(0,245,196,0.18), transparent 34%), linear-gradient(135deg, #0a0a1a, #101033); }
""".strip()
    if preset == "Creative Voltage":
        return """
.slide { background: #1a1a2e; }
.slide-1, .slide-2, .slide-3, .slide-4, .slide-5, .slide-6 { background: linear-gradient(135deg, #1a1a2e, #0066ff); }
""".strip()
    if preset == "Dark Botanical":
        return """
.slide { background: #0f0f0f; }
.slide-1, .slide-2, .slide-3, .slide-4, .slide-5, .slide-6 { background: radial-gradient(circle at 72% 22%, rgba(201,184,150,0.16), transparent 30%), #0f0f0f; }
""".strip()
    if preset == "Neo-Brutalism":
        return """
.slide { background: #ffeb3b; }
.slide-1, .slide-2, .slide-3, .slide-4, .slide-5, .slide-6 { background: #ffeb3b; }
""".strip()
    if preset == "Notebook Tabs":
        return """
.slide { background: #f8f6f1; }
.slide-1, .slide-2, .slide-3, .slide-4, .slide-5, .slide-6 { background: linear-gradient(90deg, #2d2d2d 0 7%, #f8f6f1 7% 100%); }
""".strip()
    if preset == "Pastel Geometry":
        return """
.slide { background: #faf9f7; }
.slide-1, .slide-2, .slide-3, .slide-4, .slide-5, .slide-6 { background: linear-gradient(135deg, #faf9f7, #c8d9e6); }
""".strip()
    if preset == "Vintage Editorial":
        return """
.slide { background: #f5f3ee; }
.slide-1, .slide-2, .slide-3, .slide-4, .slide-5, .slide-6 { background: #f5f3ee; }
""".strip()
    if preset == "Paper & Ink":
        return """
.slide { background: #faf9f7; }
.slide-1, .slide-2, .slide-3, .slide-4, .slide-5, .slide-6 { background: #faf9f7; }
""".strip()
    if preset == "Strategy Consulting":
        return """
.slide { background: #ffffff; }
.slide-1, .slide-2, .slide-3, .slide-4, .slide-5, .slide-6 { background: #ffffff; }
""".strip()
    if preset == "Modern Newspaper":
        return """
.slide { background: #fafaf9; }
.slide-1, .slide-2, .slide-3, .slide-4, .slide-5, .slide-6 { background: #fafaf9; }
""".strip()
    if profile_spec.family in {"editorial_static", "consulting_structured", "split_editorial"}:
        return f"""
.slide-1 {{ background: linear-gradient(135deg, {palette[1]}, {palette[5]}); }}
.slide-2 {{ background: linear-gradient(135deg, {palette[5]}, {palette[2]}); }}
.slide-3 {{ background: linear-gradient(135deg, {palette[3]}, {palette[6]}); }}
.slide-4 {{ background: linear-gradient(135deg, {palette[4]}, {palette[7]}); }}
.slide-5 {{ background: linear-gradient(135deg, {palette[6]}, {palette[1]}); }}
.slide-6 {{ background: linear-gradient(135deg, {palette[7]}, {palette[2]}); }}
""".strip()
    if profile_spec.family in {"technical_terminal", "brutalist_graphic"}:
        return f"""
.slide-1 {{ background: linear-gradient(135deg, {palette[0]}, {palette[2]}); }}
.slide-2 {{ background: linear-gradient(135deg, {palette[1]}, {palette[3]}); }}
.slide-3 {{ background: linear-gradient(135deg, {palette[2]}, {palette[4]}); }}
.slide-4 {{ background: linear-gradient(135deg, {palette[3]}, {palette[5]}); }}
.slide-5 {{ background: linear-gradient(135deg, {palette[4]}, {palette[6]}); }}
.slide-6 {{ background: linear-gradient(135deg, {palette[5]}, {palette[7]}); }}
""".strip()
    return f"""
.slide-1 {{ background: linear-gradient(135deg, {palette[0]}, {palette[1]}, {palette[2]}); }}
.slide-2 {{ background: linear-gradient(135deg, {palette[2]}, {palette[3]}, {palette[4]}); }}
.slide-3 {{ background: linear-gradient(135deg, {palette[4]}, {palette[5]}, {palette[0]}); }}
.slide-4 {{ background: linear-gradient(135deg, {palette[1]}, {palette[3]}); }}
.slide-5 {{ background: linear-gradient(135deg, {palette[5]}, {palette[2]}); }}
.slide-6 {{ background: linear-gradient(135deg, {palette[0]}, {palette[4]}); }}
""".strip()


def _component_signature_css(profile_spec: PresetProfileSpec) -> str:
    slug = _slugify(profile_spec.preset)
    rules = [
        f'body[data-profile-spec="{slug}"] .profile-signature-component {{',
        "    position: relative;",
        "    overflow: hidden;",
        "}",
    ]
    for class_name in profile_spec.visible_signature_classes:
        rules.append(
            f'body[data-profile-spec="{slug}"] .profile-signature-component.{class_name} {{ '
            "box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--profile-rule) 35%, transparent); "
            "}"
        )

    preset = profile_spec.preset
    if preset == "Creative Voltage":
        rules.extend(
            [
                '.profile-signature-component.voltage-card, .profile-signature-component.voltage-blue-panel { background: #0066ff; color: #ffffff; border-color: #d4ff00; }',
                '.profile-signature-component.voltage-dark-panel { background: #1a1a2e; color: #ffffff; border-color: #0066ff; }',
                '.profile-signature-component.voltage-neon-badge, .profile-signature-component.pill, .profile-signature-component.stat { background: #d4ff00; color: #1a1a2e; border-radius: 999px; min-height: 0; }',
                '.profile-signature-component.voltage-diamond::before { content: ""; position: absolute; width: 72px; height: 72px; right: -24px; top: -24px; background: #d4ff00; transform: rotate(45deg); opacity: 0.9; }',
                '.profile-signature-component.voltage-halftone { background-image: radial-gradient(circle, rgba(212,255,0,0.34) 1px, transparent 1px); background-size: 10px 10px; }',
            ]
        )
    elif preset == "Aurora Mesh":
        rules.extend(
            [
                '.profile-signature-component.aurora-card, .profile-signature-component.aurora-stat { background: rgba(0,245,196,0.12); border-color: rgba(0,245,196,0.55); }',
                '.profile-signature-component.aurora-badge { border-radius: 999px; min-height: 0; background: #00f5c4; color: #0a0a1a; }',
                '.profile-signature-component.aurora-divider::after { content: ""; display: block; height: 2px; margin-top: 18px; background: linear-gradient(90deg, #00f5c4, #00b4ff); }',
            ]
        )
    elif preset == "Bold Signal":
        rules.extend(
            [
                '.profile-signature-component.bold-signal-card, .profile-signature-component.signal-block { background: #ff5722; color: #ffffff; border-color: #ffffff; box-shadow: 10px 10px 0 rgba(0,0,0,0.55); }',
                '.profile-signature-component.bold-signal-title { background: #ffffff; color: #1a1a1a; text-transform: uppercase; }',
            ]
        )
    elif preset == "Electric Studio":
        rules.extend(
            [
                '.profile-signature-component.left-panel, .profile-signature-component.right-panel, .profile-signature-component.top-panel, .profile-signature-component.bottom-panel { background: #ffffff; color: #0a0a0a; border-color: #4361ee; }',
                '.profile-signature-component.elec-quote-block { background: #0a0a0a; color: #ffffff; border-left: 6px solid #4361ee; }',
            ]
        )
    elif preset == "Dark Botanical":
        rules.extend(
            [
                '.profile-signature-component.orb, .profile-signature-component.orb-gold, .profile-signature-component.orb-pink, .profile-signature-component.orb-terra { border-radius: 999px 999px 44px 999px; background: rgba(201,184,150,0.16); }',
                '.profile-signature-component.feature-grid, .profile-signature-component.preset-grid { background: rgba(15,15,15,0.86); border-color: #c9b896; }',
            ]
        )
    elif preset == "Neon Cyber":
        rules.extend(
            [
                '.profile-signature-component.cyber-card, .profile-signature-component.grid { background: rgba(0,255,204,0.08); border-color: #00ffcc; box-shadow: 0 0 36px rgba(0,255,204,0.18); }',
                '.profile-signature-component.cyber-heading, .profile-signature-component.cyber-title { color: #00ffcc; text-transform: uppercase; }',
                '.profile-signature-component.neon-divider::after { content: ""; display: block; height: 2px; margin-top: 16px; background: linear-gradient(90deg, #00ffcc, #ff00aa); }',
            ]
        )
    elif preset == "Notebook Tabs":
        rules.extend(
            [
                '.profile-signature-component.tab, .profile-signature-component.tabs { border-right: 10px solid #98d4bb; background: #ffffff; color: #1a1a1a; }',
                '.profile-signature-component.cmd-table { font-family: "SFMono-Regular", Consolas, monospace; }',
            ]
        )
    elif preset == "Neo-Brutalism":
        rules.extend(
            [
                '.profile-signature-component.brutalist-block, .profile-signature-component.brutalist-poster { background: #ffffff; border: 4px solid #050505; box-shadow: 10px 10px 0 #050505; }',
                '.profile-signature-component.heavy-rule::after, .profile-signature-component.cta-rule::after { content: ""; display: block; height: 6px; margin-top: 18px; background: #050505; }',
            ]
        )
    elif preset in {"Pastel Geometry", "Split Pastel"}:
        rules.extend(
            [
                '.profile-signature-component.geo-shape, .profile-signature-component.soft-orb { border-radius: 32px; background: rgba(255,255,255,0.72); }',
                '.profile-signature-component.pill, .profile-signature-component.pastel-chip, .profile-signature-component.badge-pink { border-radius: 999px; min-height: 0; }',
            ]
        )
    elif preset in {"Modern Newspaper", "Vintage Editorial"}:
        rules.extend(
            [
                '.profile-signature-component.np-rule::after, .profile-signature-component.editorial-rule::after, .profile-signature-component.rule-thick::after { content: ""; display: block; height: 2px; margin-top: 18px; background: var(--profile-rule); }',
                '.profile-signature-component.vintage-masthead, .profile-signature-component.pullquote { font-family: Georgia, "Times New Roman", serif; font-size: clamp(18px, 2vw, 30px); }',
            ]
        )
    return "\n".join(rules)


def _glass_orbs() -> str:
    return (
        '<div class="glass-orb orb-1" aria-hidden="true"></div>'
        '<div class="glass-orb orb-2" aria-hidden="true"></div>'
        '<div class="glass-orb orb-3" aria-hidden="true"></div>'
    )


def _card_grid(spec: dict[str, Any], *, class_name: str = "profile-card-grid") -> str:
    cards = []
    items = _items_for_spec(spec, minimum=4)
    for index, item in enumerate(items[:4]):
        label = _compact(item, limit=28)
        body = _paired_body_text(items, index, label, fallback=str(spec.get("key_point", "")), limit=74)
        cards.append(
            '<article class="profile-card reveal">'
            f'<div class="profile-card-label">{_escape(label)}</div>'
            f'<p>{_escape(body)}</p>'
            '</article>'
        )
    return f'<div class="{class_name}">{"".join(cards)}</div>'


def _timeline(spec: dict[str, Any]) -> str:
    rows = []
    for item in _items_for_spec(spec, minimum=4)[:4]:
        rows.append(
            '<li class="profile-timeline-item reveal">'
            '<span class="profile-timeline-dot"></span>'
            f'<span>{_escape(_compact(item, limit=78))}</span>'
            '</li>'
        )
    return f'<ul class="profile-timeline">{"".join(rows)}</ul>'


def _matrix(spec: dict[str, Any]) -> str:
    cells = []
    items = _items_for_spec(spec, minimum=4)
    for index, item in enumerate(items[:4]):
        label = _compact(item, limit=26)
        body = _paired_body_text(items, index, label, fallback=str(spec.get("key_point", "")), limit=64)
        cells.append(
            '<div class="profile-matrix-cell reveal">'
            f'<strong>{_escape(label)}</strong>'
            f'<p>{_escape(body)}</p>'
            '</div>'
        )
    return f'<div class="profile-matrix">{"".join(cells)}</div>'


def _terminal(spec: dict[str, Any], canonical_preset: str) -> str:
    command = f"render --preset {_slugify(canonical_preset)} --strict"
    items = "".join(f"<li>{_escape(_compact(item, limit=58))}</li>" for item in _items_for_spec(spec)[:3])
    return (
        '<div class="profile-terminal-window reveal">'
        '<div class="profile-terminal-bar"><span></span><span></span><span></span></div>'
        f'<pre><code>$ {_escape(command)}\nstatus: profile renderer ready\nvalidate: strict pass</code></pre>'
        f'<ul class="profile-terminal-list">{items}</ul>'
        '</div>'
    )


def _signature_component_grid(spec: dict[str, Any], profile_spec: PresetProfileSpec, *, count: int = 4) -> str:
    items = _items_for_spec(spec, minimum=4)
    cards: list[str] = []
    classes = profile_spec.visible_signature_classes
    if not classes:
        return ""
    start = ((int(spec.get("slide_number") or 1) - 1) * count) % len(classes)
    selected = [classes[(start + offset) % len(classes)] for offset in range(min(count, len(classes)))]
    for index, class_name in enumerate(selected):
        item = items[index % len(items)]
        label = _escape(_compact(class_name.replace("-", " ").replace("_", " "), limit=30))
        if "title" in class_name or "heading" in class_name:
            cards.append(f'<article class="profile-signature-component {class_name} reveal"><span>{label}</span></article>')
        else:
            cards.append(
                f'<article class="profile-signature-component {class_name} reveal">'
                f'<strong>{label}</strong>'
                f'<p>{_escape(_compact(item, limit=72))}</p>'
                '</article>'
            )
    return f'<div class="profile-signature-grid">{"".join(cards)}</div>'


def _signature_classes_for_slide(spec: dict[str, Any], profile_spec: PresetProfileSpec, *, count: int = 4) -> list[str]:
    classes = list(profile_spec.visible_signature_classes)
    if not classes:
        return []
    start = ((int(spec.get("slide_number") or 1) - 1) * count) % len(classes)
    return [classes[(start + offset) % len(classes)] for offset in range(min(count, len(classes)))]


def _signature_cards(spec: dict[str, Any], profile_spec: PresetProfileSpec, *, class_name: str, count: int = 4) -> str:
    cards: list[str] = []
    items = _items_for_spec(spec, minimum=4)
    for index, signature_class in enumerate(_signature_classes_for_slide(spec, profile_spec, count=count)):
        item = items[index % len(items)]
        label = _escape(_compact(signature_class.replace("-", " ").replace("_", " "), limit=30))
        body = _paired_body_text(items, index, label, fallback=str(spec.get("key_point", "")), limit=74)
        cards.append(
            f'<article class="profile-signature-component {signature_class} reveal">'
            f'<strong>{label}</strong>'
            f'<p>{_escape(body)}</p>'
            '</article>'
        )
    return f'<div class="{class_name}">{"".join(cards)}</div>'


def _cover_signature_mark(profile_spec: PresetProfileSpec) -> str:
    classes = list(profile_spec.visible_signature_classes[:2])
    if not classes:
        return ""
    label = _escape(profile_spec.preset)
    class_attr = " ".join(["profile-cover-mark", *classes, "reveal"])
    return (
        f'<div class="{class_attr}">'
        f'<span>{label}</span>'
        '</div>'
    )


def _signature_timeline(spec: dict[str, Any], profile_spec: PresetProfileSpec) -> str:
    items = _items_for_spec(spec, minimum=4)
    rows: list[str] = []
    for index, signature_class in enumerate(_signature_classes_for_slide(spec, profile_spec, count=4)):
        item = items[index % len(items)]
        rows.append(
            f'<li class="profile-timeline-item profile-signature-component {signature_class} reveal">'
            '<span class="profile-timeline-dot"></span>'
            f'<span>{_escape(_compact(item, limit=78))}</span>'
            '</li>'
        )
    return f'<ul class="profile-timeline">{"".join(rows)}</ul>'


def _render_paper_and_ink_body(spec: dict[str, Any], *, layout: str, canonical_preset: str, profile_spec: PresetProfileSpec) -> str:
    title = str(spec.get("title", ""))
    key_point = _compact(str(spec.get("key_point", "")), limit=160)
    items = _items_for_spec(spec, minimum=4)
    steps = ""
    for index, item in enumerate(items[:3], start=1):
        label = _compact(item, limit=34)
        body = _paired_body_text(items, index - 1, label, fallback=key_point, limit=82)
        steps += (
            '<div class="step reveal">'
            f'<span class="step-num">{index:02d}</span>'
            f'<span class="step-text"><strong>{_escape(label)}</strong><br>{_escape(body)}</span>'
            '</div>'
        )
    stats = "".join(
        '<div class="stat">'
        f'<span class="stat-val">{index}</span>'
        f'<span class="stat-label">{_escape(_compact(item, limit=24))}</span>'
        '</div>'
        for index, item in enumerate(items[:3], start=1)
    )
    rule = '<div class="rule"><span class="rule-line"></span></div>'
    role = str(spec.get("role", ""))

    if layout == "paper_hero" or role == "cover":
        return (
            '<div class="profile-hero-block paper-ink-block reveal">'
            f'{rule}'
            f'<p class="profile-kicker pill">Paper & Ink</p>'
            f'{_title_markup("h1", "profile-title", title)}'
            f'<p class="body-text hero-body">{_escape(key_point)}</p>'
            f'<div class="stat-row stats">{stats}</div>'
            '</div>'
        )

    if layout in {"paper_columns", "paper_index"}:
        return (
            '<div class="profile-hero-block paper-ink-block reveal">'
            f'{_title_markup("h2", "profile-title", title)}'
            f'{rule}'
            f'<p class="body-text drop-cap">{_escape(key_point)}</p>'
            f'<div class="steps">{steps}</div>'
            '</div>'
        )

    if layout == "paper_pullquote":
        return (
            '<div class="profile-hero-block paper-ink-block reveal">'
            f'<blockquote class="pull-quote">{_escape(key_point)}</blockquote>'
            f'{rule}'
            f'{_title_markup("h2", "profile-title", title)}'
            '</div>'
        )

    return (
        '<div class="profile-hero-block paper-ink-block reveal">'
        f'<p class="profile-kicker pill">Paper & Ink</p>'
        f'<blockquote class="pull-quote">{_escape(_compact(items[0], limit=96))}</blockquote>'
        f'{rule}'
        f'<p class="body-text">{_escape(key_point)}</p>'
        '</div>'
    )


def _render_strategy_consulting_body(spec: dict[str, Any], *, layout: str, canonical_preset: str, profile_spec: PresetProfileSpec) -> str:
    title = str(spec.get("title", ""))
    key_point = _compact(str(spec.get("key_point", "")), limit=160)
    items = _items_for_spec(spec, minimum=4)
    cards = ""
    things = ""
    for index, item in enumerate(items[:3], start=1):
        label = _compact(item, limit=32)
        card_body = _paired_body_text(items, index - 1, label, fallback=key_point, limit=76)
        thing_body = _paired_body_text(items, index - 1, label, fallback=key_point, limit=90)
        cards += (
            '<article class="sc-evidence-card reveal">'
            f'<div class="sc-metric">{index}</div>'
            f'<div class="sc-metric-label">{_escape(label)}</div>'
            f'<p>{_escape(card_body)}</p>'
            '</article>'
        )
        things += (
            '<div class="sc-thing reveal">'
            f'<div class="sc-thing-icon">{index}</div>'
            f'<div class="sc-thing-title">{_escape(label)}</div>'
            f'<div class="sc-thing-body">{_escape(thing_body)}</div>'
            '</div>'
        )
    source = '<div class="sc-source">Source: BRIEF.json</div>'
    header = (
        '<div class="sc-section-header reveal">Analysis</div>'
        f'<h2 class="sc-action-title reveal">{_escape(title)}</h2>'
        f'<p class="sc-body reveal">{_escape(key_point)}</p>'
    )

    if layout == "consulting_exec" or spec.get("role") == "cover":
        return (
            '<div class="strategy-consulting-block">'
            f'{header}'
            f'<div class="sc-evidence-row">{cards}</div>'
            f'{source}'
            '</div>'
        )

    if layout == "consulting_matrix":
        return (
            '<div class="strategy-consulting-block">'
            f'{header}'
            f'<div class="sc-evidence-row">{cards}</div>'
            f'<div class="sc-reco-box reveal">{_escape(_compact(key_point, limit=120))}</div>'
            '</div>'
        )

    if layout == "consulting_split":
        return (
            '<div class="strategy-consulting-block">'
            f'{header}'
            f'<div class="sc-before-after reveal"><div class="sc-before-panel"><div class="sc-panel-label">Before</div><p>{_escape(_compact(items[0], limit=80))}</p></div><div class="sc-after-panel"><div class="sc-panel-label">After</div><p>{_escape(_compact(items[1], limit=80))}</p></div></div>'
            f'{source}'
            '</div>'
        )

    if layout == "consulting_quote":
        return (
            '<div class="strategy-consulting-block">'
            f'{header}'
            f'<div class="sc-quote-evidence reveal"><div class="sc-quote-block"><div class="sc-quote-text">{_escape(_compact(key_point, limit=110))}</div><div class="sc-quote-attribution">BRIEF evidence</div></div></div>'
            '</div>'
        )

    return (
        '<div class="strategy-consulting-block">'
        f'{header}'
        f'<div class="sc-three-things">{things}</div>'
        f'{source}'
        '</div>'
    )


def _render_generic_profile_body(spec: dict[str, Any], *, layout: str, family: str, canonical_preset: str, profile_spec: PresetProfileSpec) -> str:
    title = str(spec.get("title", ""))
    key_point = _compact(str(spec.get("key_point", "")), limit=150)
    hero = (
        '<div class="profile-hero-block reveal">'
        f'<p class="profile-kicker">{_escape(canonical_preset)}</p>'
        f'{_title_markup("h2", "profile-title", title)}'
        f'<p class="profile-lede">{_escape(key_point)}</p>'
        '</div>'
    )
    is_cover = spec.get("role") == "cover" or layout == profile_spec.layout_sequence[0]
    if is_cover:
        return hero + _cover_signature_mark(profile_spec)
    layout_words = layout.replace("-", "_")
    if any(word in layout_words for word in ("quote", "manifesto", "close")):
        return (
            '<blockquote class="profile-pullquote reveal">'
            f'{_escape(key_point)}'
            '</blockquote>'
            f'{_signature_cards(spec, profile_spec, class_name="profile-chip-row", count=3)}'
        )
    if any(word in layout_words for word in ("timeline", "steps")):
        return f'{_title_markup("h2", "profile-title", title)}{_signature_timeline(spec, profile_spec)}'
    if any(word in layout_words for word in ("terminal", "cmd", "code", "boot")):
        return (
            f'{_title_markup("h2", "profile-title", title)}'
            f'{_terminal(spec, canonical_preset)}'
            f'{_signature_cards(spec, profile_spec, class_name="profile-chip-row", count=2)}'
        )
    if any(word in layout_words for word in ("grid", "cards", "blocks", "trio", "index", "stat", "metrics")):
        return f'{_title_markup("h2", "profile-title", title)}{_signature_cards(spec, profile_spec, class_name="profile-card-grid", count=4)}'
    if any(word in layout_words for word in ("split", "panel", "statement", "columns")):
        return (
            '<div class="profile-split-layout">'
            f'{hero}'
            f'{_signature_cards(spec, profile_spec, class_name="profile-showcase", count=3)}'
            '</div>'
        )
    return f'{_title_markup("h2", "profile-title", title)}{_signature_cards(spec, profile_spec, class_name="profile-card-grid", count=4)}'


def _layout_body(
    spec: dict[str, Any],
    *,
    layout: str,
    family: str,
    canonical_preset: str,
    profile_spec: PresetProfileSpec,
) -> str:
    if profile_spec.adapter_key == "paper_and_ink":
        return _render_paper_and_ink_body(spec, layout=layout, canonical_preset=canonical_preset, profile_spec=profile_spec)
    if profile_spec.adapter_key == "strategy_consulting":
        return _render_strategy_consulting_body(spec, layout=layout, canonical_preset=canonical_preset, profile_spec=profile_spec)
    if profile_spec.visible_signature_classes:
        return _render_generic_profile_body(
            spec,
            layout=layout,
            family=family,
            canonical_preset=canonical_preset,
            profile_spec=profile_spec,
        )
    key_point = _compact(str(spec.get("key_point", "")), limit=150)
    title = str(spec.get("title", ""))
    layout_words = layout.replace("-", "_")
    if (
        layout in {"profile_hero", "profile_masthead", "profile_exec", "profile_poster", "glass_hero"}
        or any(word in layout_words for word in ("cover", "hero", "masthead", "exec", "poster"))
    ):
        return (
            '<div class="profile-hero-block reveal">'
            f'<p class="profile-kicker">{_escape(FAMILY_LABELS.get(family, "Profile"))} profile</p>'
            f'{_title_markup("h1", "profile-title", title)}'
            f'<p class="profile-lede">{_escape(key_point)}</p>'
            '</div>'
            + _card_grid(spec, class_name="profile-chip-row")
        )
    if layout in {"profile_columns", "profile_split", "profile_code_split", "glass_split"} or any(
        word in layout_words for word in ("columns", "split", "panel")
    ):
        return (
            '<div class="profile-split-layout">'
            '<div class="profile-split-main reveal">'
            f'{_title_markup("h2", "profile-title", title)}'
            f'<p class="profile-lede">{_escape(key_point)}</p>'
            '</div>'
            f'{_card_grid(spec)}'
            '</div>'
        )
    if layout in {"profile_pullquote", "profile_manifesto"} or any(word in layout_words for word in ("quote", "manifesto")):
        return (
            '<blockquote class="profile-pullquote reveal">'
            f'{_escape(key_point)}'
            '</blockquote>'
            f'{_title_markup("h2", "profile-title", title)}'
            + _timeline(spec)
        )
    if layout in {"profile_timeline"} or any(word in layout_words for word in ("timeline", "steps")):
        return f'{_title_markup("h2", "profile-title", title)}{_timeline(spec)}'
    if layout in {"profile_matrix", "profile_index", "profile_signal_grid", "profile_cards", "profile_blocks", "glass_trio"} or any(
        word in layout_words for word in ("grid", "cards", "blocks", "trio", "index", "stat", "metrics")
    ):
        return f'{_title_markup("h2", "profile-title", title)}{_matrix(spec)}'
    if layout == "profile_terminal" or any(word in layout_words for word in ("terminal", "cmd", "code", "boot")):
        return f'{_title_markup("h2", "profile-title", title)}{_terminal(spec, canonical_preset)}'
    if layout in {"glass_card", "glass_stat"}:
        return (
            '<div class="glass-card reveal">'
            f'{_title_markup("h2", "glass-title", title)}'
            f'<p class="glass-body">{_escape(key_point)}</p>'
            f'{_card_grid(spec)}'
            '</div>'
        )
    return f'{_title_markup("h2", "profile-title", title)}{_card_grid(spec)}'


def _render_section(
    spec: dict[str, Any],
    *,
    total: int,
    layout: str,
    family: str,
    canonical_preset: str,
    slug: str,
) -> str:
    slide_number = int(spec.get("slide_number") or 1)
    profile_spec = PROFILE_SPECS[canonical_preset]
    body = _layout_body(
        spec,
        layout=layout,
        family=family,
        canonical_preset=canonical_preset,
        profile_spec=profile_spec,
    )
    glass_layers = _glass_orbs() if family == "glass_material" else ""
    return f"""
    <section class="slide slide-{slide_number} profile-slide pf-{family} preset-{slug} {layout}" id="slide-{slide_number}" data-notes="{_escape(spec.get('speaker_note', ''))}" aria-label="{_escape(spec.get('role', 'slide'))}" data-export-role="{_escape(layout)}" data-visual-family="{_escape(family)}" data-visual-signature="{_escape(slug + '-' + layout)}">
        {glass_layers}
        <div class="slide-content content profile-content preset-{slug}-content">
            <div class="profile-eyebrow reveal">{_escape(canonical_preset)} / {_escape(str(spec.get('role', 'slide')))}</div>
            {body}
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _profile_css(canonical_preset: str, family: str, slug: str, profile_spec: PresetProfileSpec) -> str:
    vars_css = _css_var_declarations(profile_spec)
    font_stack = _font_stack(profile_spec)
    backgrounds = _slide_background_css(profile_spec)
    component_css = _component_signature_css(profile_spec)
    return f"""
body[data-renderer-strategy="unified_profile"] {{
{vars_css}
    --profile-ink: var(--text-primary, var(--text, #111827));
    --profile-muted: var(--text-secondary, var(--text-muted, rgba(17, 24, 39, 0.68)));
    --profile-panel: rgba(255, 255, 255, 0.78);
    --profile-rule: var(--accent, var(--accent-blue, #2563eb));
    font-family: {font_stack};
}}

body[data-style-family="technical_terminal"] {{
    --profile-ink: #d7ffe2;
    --profile-muted: rgba(215, 255, 226, 0.72);
    --profile-panel: rgba(1, 18, 11, 0.78);
    --profile-rule: #32ff7e;
    background: #04120b;
}}

body[data-style-family="brutalist_graphic"] {{
    --profile-ink: #050505;
    --profile-muted: rgba(5, 5, 5, 0.68);
    --profile-panel: #f8f100;
    --profile-rule: #050505;
}}

body[data-style-family="glass_material"] {{
    --profile-ink: var(--glass-text-dark, #1a1a2e);
    --profile-muted: rgba(26, 26, 46, 0.72);
    --profile-panel: var(--glass-bg, rgba(255, 255, 255, 0.16));
    --profile-rule: rgba(255, 255, 255, 0.72);
}}

body[data-style-family="geometric_soft"] {{
    --profile-ink: var(--text-primary, #1a2530);
    --profile-muted: var(--text-secondary, rgba(26, 37, 48, 0.68));
    --profile-panel: var(--card-bg, rgba(255, 255, 255, 0.86));
    --profile-rule: var(--accent, #7bb8d4);
}}

body[data-style-family="split_editorial"] {{
    --profile-ink: var(--text-dark, #1a1a1a);
    --profile-muted: var(--text-secondary, rgba(26, 26, 26, 0.68));
    --profile-panel: rgba(255, 255, 255, 0.70);
    --profile-rule: var(--accent, #b0e0c0);
}}

body[data-profile-spec="bold-signal"] {{
    --profile-ink: #ffffff;
    --profile-muted: rgba(255, 255, 255, 0.78);
    --profile-panel: rgba(255, 87, 34, 0.92);
    --profile-rule: #ff5722;
}}

body[data-profile-spec="electric-studio"] {{
    --profile-ink: #ffffff;
    --profile-muted: rgba(255, 255, 255, 0.78);
    --profile-panel: rgba(10, 10, 10, 0.82);
    --profile-rule: #4361ee;
}}

body[data-profile-spec="glassmorphism"] {{
    --profile-ink: #ffffff;
    --profile-muted: rgba(255, 255, 255, 0.78);
    --profile-panel: rgba(255, 255, 255, 0.18);
    --profile-rule: #a8edea;
}}

body[data-profile-spec="modern-newspaper"] {{
    --profile-ink: #111111;
    --profile-muted: rgba(17, 17, 17, 0.68);
    --profile-panel: rgba(255, 255, 255, 0.86);
    --profile-rule: #10b981;
}}

body[data-profile-spec="paper-ink"] {{
    --profile-ink: #1a1a1a;
    --profile-muted: #4a4a4a;
    --profile-panel: rgba(255, 255, 255, 0.72);
    --profile-rule: #c41e3a;
}}

body[data-profile-spec="aurora-mesh"] {{
    --profile-ink: #f7fbff;
    --profile-muted: rgba(247, 251, 255, 0.76);
    --profile-panel: rgba(10, 10, 26, 0.74);
    --profile-rule: #00f5c4;
}}

body[data-profile-spec="creative-voltage"] {{
    --profile-ink: #ffffff;
    --profile-muted: rgba(255, 255, 255, 0.76);
    --profile-panel: rgba(26, 26, 46, 0.74);
    --profile-rule: #d4ff00;
}}

body[data-profile-spec="dark-botanical"] {{
    --profile-ink: #e8e4df;
    --profile-muted: rgba(232, 228, 223, 0.66);
    --profile-panel: rgba(15, 15, 15, 0.76);
    --profile-rule: #c9b896;
}}

body[data-profile-spec="neo-brutalism"] {{
    --profile-ink: #050505;
    --profile-muted: rgba(5, 5, 5, 0.72);
    --profile-panel: #ffffff;
    --profile-rule: #050505;
}}

body[data-profile-spec="notebook-tabs"] {{
    --profile-ink: #1a1a1a;
    --profile-muted: rgba(26, 26, 26, 0.64);
    --profile-panel: rgba(255, 255, 255, 0.86);
    --profile-rule: #98d4bb;
}}

body[data-profile-spec="pastel-geometry"] {{
    --profile-ink: #1a2530;
    --profile-muted: rgba(26, 37, 48, 0.68);
    --profile-panel: rgba(255, 255, 255, 0.78);
    --profile-rule: #7bb8d4;
}}

body[data-profile-spec="vintage-editorial"] {{
    --profile-ink: #6a1c28;
    --profile-muted: rgba(90, 42, 26, 0.72);
    --profile-panel: rgba(255, 255, 255, 0.72);
    --profile-rule: #6a1c28;
}}

.profile-slide {{
    color: var(--profile-ink);
}}

.profile-slide::after {{
    content: "{_escape(canonical_preset)}";
    position: absolute;
    right: clamp(28px, 5vw, 72px);
    top: clamp(22px, 4vw, 52px);
    font-size: 11px;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--profile-muted);
    z-index: 1;
}}

.profile-content {{
    max-width: min(1180px, 92vw);
    width: 100%;
    margin: 0 auto;
    gap: clamp(18px, 2.6vw, 32px);
}}

.profile-eyebrow,
.profile-kicker,
.profile-card-label {{
    font-size: clamp(11px, 1vw, 14px);
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--profile-muted);
    font-weight: 800;
}}

.profile-title,
.glass-title {{
    margin: 0;
    max-width: 15ch;
    font-size: clamp(42px, 6.2vw, 86px);
    line-height: 0.96;
    letter-spacing: 0;
    color: var(--profile-ink);
}}

.profile-lede,
.glass-body {{
    margin: 0;
    max-width: 62ch;
    font-size: clamp(17px, 1.6vw, 25px);
    line-height: 1.45;
    color: var(--profile-muted);
}}

.profile-hero-block {{
    display: grid;
    gap: clamp(14px, 2vw, 26px);
    max-width: 980px;
}}

.profile-cover-mark {{
    width: min(340px, 52vw);
    min-height: 74px;
    display: grid;
    place-items: center;
    padding: 18px 24px;
    border: 1px solid color-mix(in srgb, var(--profile-rule) 58%, transparent);
    background: var(--profile-panel);
    color: var(--profile-ink);
    box-shadow: 0 22px 70px rgba(0, 0, 0, 0.18);
    font-size: clamp(12px, 1vw, 15px);
    letter-spacing: 0.18em;
    text-transform: uppercase;
    font-weight: 900;
}}

.pf-signal_pitch .profile-cover-mark {{
    width: min(420px, 62vw);
    min-height: 92px;
    justify-items: start;
    border-radius: 0;
    transform: skew(-2deg);
}}

.pf-editorial_static .profile-cover-mark {{
    border-width: 1px 0;
    box-shadow: none;
    background: transparent;
}}

.pf-technical_terminal .profile-cover-mark {{
    font-family: "SFMono-Regular", Consolas, monospace;
    border-color: var(--profile-rule);
    background: rgba(0, 12, 7, 0.74);
}}

.pf-brutalist_graphic .profile-cover-mark {{
    border: 4px solid #050505;
    box-shadow: 10px 10px 0 #050505;
    background: #ffffff;
}}

.pf-glass_material .profile-cover-mark {{
    border-radius: 18px;
    backdrop-filter: blur(20px) saturate(1.5);
    -webkit-backdrop-filter: blur(20px) saturate(1.5);
}}

.profile-cover-mark.voltage-title,
.profile-cover-mark.voltage-card,
.profile-cover-mark.voltage-blue-panel {{
    background: #d4ff00;
    color: #1a1a2e;
    border-color: #ffffff;
}}

.profile-cover-mark.left-panel,
.profile-cover-mark.right-panel,
.profile-cover-mark.top-panel {{
    background: #ffffff;
    color: #0a0a0a;
    border-left: 10px solid #4361ee;
}}

.profile-cover-mark.pill,
.profile-cover-mark.stat,
.profile-cover-mark.stats {{
    border-radius: 999px;
}}

.profile-card-grid,
.profile-chip-row,
.profile-matrix,
.profile-signature-grid,
.profile-showcase,
.sc-evidence-row,
.sc-three-things {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: clamp(14px, 1.8vw, 22px);
}}

.profile-chip-row {{
    grid-template-columns: repeat(4, minmax(0, 1fr));
}}

.profile-card,
.profile-matrix-cell,
.profile-signature-component,
.sc-evidence-card,
.sc-thing {{
    min-height: 118px;
    padding: clamp(18px, 2vw, 26px);
    border: 1px solid color-mix(in srgb, var(--profile-rule) 42%, transparent);
    background: var(--profile-panel);
    box-shadow: 0 20px 60px rgba(15, 23, 42, 0.10);
}}

.profile-showcase {{
    grid-template-columns: repeat(3, minmax(0, 1fr));
}}

.profile-card p,
.profile-matrix-cell p,
.profile-signature-component p,
.sc-evidence-card p {{
    margin: 10px 0 0;
    color: var(--profile-muted);
    line-height: 1.45;
}}

.profile-signature-component strong {{
    display: block;
    color: var(--profile-ink);
    font-size: clamp(14px, 1.2vw, 18px);
    line-height: 1.2;
}}

.paper-ink-block {{
    color: #1a1a1a;
}}

.rule {{
    display: flex;
    align-items: center;
    gap: 0.8rem;
    width: min(520px, 70vw);
}}

.rule::before,
.rule::after {{
    content: "\\25C6";
    color: #c41e3a;
    font-size: 0.45rem;
}}

.rule-line {{
    flex: 1;
    height: 1px;
    background: #c41e3a;
}}

.body-text {{
    max-width: 62ch;
    color: #1a1a1a;
    font-size: clamp(18px, 1.55vw, 24px);
    line-height: 1.75;
}}

.body-text.drop-cap::first-letter {{
    float: left;
    color: #c41e3a;
    font-size: 4em;
    line-height: 0.82;
    margin-right: 0.12em;
}}

.pull-quote {{
    margin: 0;
    max-width: 34ch;
    color: #c41e3a;
    font-style: italic;
    font-size: clamp(26px, 3vw, 46px);
    line-height: 1.18;
}}

.stat-row {{
    display: flex;
    gap: clamp(24px, 4vw, 56px);
}}

.stat-val {{
    display: block;
    color: #c41e3a;
    font-size: clamp(30px, 4vw, 56px);
    line-height: 1;
    font-weight: 800;
}}

.stat-label {{
    display: block;
    color: #4a4a4a;
    font-size: 12px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}}

.steps {{
    display: grid;
    gap: 12px;
    max-width: 760px;
}}

.step {{
    display: grid;
    grid-template-columns: 3rem 1fr;
    gap: 16px;
    border-top: 1px solid rgba(196, 30, 58, 0.25);
    padding: 14px 0;
}}

.step-num {{
    color: #c41e3a;
    font-weight: 800;
}}

.strategy-consulting-block {{
    display: grid;
    gap: clamp(14px, 1.8vw, 22px);
    width: 100%;
    color: #1a2b4a;
}}

.sc-action-title {{
    margin: 0;
    padding-bottom: 0.55rem;
    border-bottom: 2px solid #1b3a6b;
    color: #1a2b4a;
    font-size: clamp(25px, 2.5vw, 38px);
    line-height: 1.24;
}}

.sc-section-header,
.sc-metric-label,
.sc-panel-label {{
    color: #1b3a6b;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-size: clamp(11px, 1vw, 14px);
}}

.sc-body {{
    color: #1a2b4a;
    max-width: 760px;
    line-height: 1.55;
}}

.sc-reco-box {{
    background: #eef2f7;
    border-left: 4px solid #1b3a6b;
    padding: 16px 20px;
    border-radius: 0 6px 6px 0;
}}

.sc-before-after {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
}}

.sc-before-panel,
.sc-after-panel {{
    background: #f7f8fa;
    border: 1px solid #d8dfe8;
    border-top: 3px solid #1b3a6b;
    padding: 16px;
}}

.sc-source {{
    color: #6b7a90;
    font-size: 11px;
}}

.sc-quote-evidence {{
    display: grid;
    grid-template-columns: minmax(0, 1fr);
}}

.sc-quote-block {{
    border-left: 4px solid #1b3a6b;
    background: #f7f8fa;
    padding: 18px 20px;
}}

.sc-quote-text {{
    color: #1a2b4a;
    font-size: clamp(18px, 1.7vw, 26px);
    line-height: 1.35;
    font-weight: 700;
}}

.sc-quote-attribution {{
    color: #6b7a90;
    margin-top: 10px;
    font-size: 12px;
}}

.profile-split-layout {{
    display: grid;
    grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
    gap: clamp(20px, 4vw, 58px);
    align-items: center;
}}

.profile-pullquote {{
    margin: 0;
    max-width: 18ch;
    font-size: clamp(38px, 5.4vw, 74px);
    line-height: 1.02;
    color: var(--profile-ink);
}}

.profile-timeline {{
    list-style: none;
    margin: 0;
    padding: 0;
    display: grid;
    gap: 14px;
    max-width: 760px;
}}

.profile-timeline-item {{
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 18px;
    border-left: 4px solid var(--profile-rule);
    background: color-mix(in srgb, var(--profile-panel) 82%, transparent);
}}

.profile-timeline-dot {{
    width: 12px;
    height: 12px;
    border-radius: 999px;
    background: var(--profile-rule);
    flex: 0 0 auto;
}}

.profile-terminal-window {{
    border: 1px solid rgba(50, 255, 126, 0.42);
    background: rgba(0, 12, 7, 0.88);
    color: #d7ffe2;
    box-shadow: 0 24px 80px rgba(0, 0, 0, 0.38);
    padding: 18px;
    max-width: 820px;
}}

.profile-terminal-bar {{
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
}}

.profile-terminal-bar span {{
    width: 10px;
    height: 10px;
    border-radius: 999px;
    background: #32ff7e;
    opacity: 0.82;
}}

.profile-terminal-window pre {{
    margin: 0;
    white-space: pre-wrap;
    font: 700 clamp(15px, 1.3vw, 20px)/1.55 "SFMono-Regular", Consolas, monospace;
}}

.profile-terminal-list {{
    margin: 18px 0 0;
    display: grid;
    gap: 8px;
}}

.pf-editorial_static .profile-title,
.pf-editorial_static .profile-pullquote {{
    font-family: Georgia, "Times New Roman", serif;
    font-weight: 700;
}}

.pf-editorial_static .profile-card {{
    border-width: 0 0 1px 0;
    box-shadow: none;
    background: transparent;
}}

.pf-signal_pitch .profile-title {{
    text-transform: uppercase;
    max-width: 13ch;
}}

.pf-signal_pitch .profile-card,
.pf-signal_pitch .profile-matrix-cell {{
    border-radius: 0;
    transform: skew(-1deg);
}}

.pf-consulting_structured .profile-matrix-cell {{
    background: rgba(255, 255, 255, 0.94);
    border-color: rgba(15, 23, 42, 0.16);
}}

.pf-brutalist_graphic .profile-card,
.pf-brutalist_graphic .profile-matrix-cell,
.pf-brutalist_graphic .profile-terminal-window {{
    border: 3px solid #050505;
    box-shadow: 8px 8px 0 #050505;
    border-radius: 0;
}}

.pf-glass_material {{
    background: transparent;
}}

{backgrounds}

.glass-orb {{
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);
    pointer-events: none;
    z-index: 0;
}}

.orb-1 {{ width: 400px; height: 400px; background: var(--orb-purple, rgba(102,126,234,0.5)); top: -10%; left: -5%; }}
.orb-2 {{ width: 300px; height: 300px; background: var(--orb-pink, rgba(240,147,251,0.4)); bottom: -5%; right: -5%; }}
.orb-3 {{ width: 250px; height: 250px; background: var(--orb-mint, rgba(168,237,234,0.4)); top: 30%; right: 15%; }}

.glass-card,
.pf-glass_material .profile-card,
.pf-glass_material .profile-matrix-cell {{
    background: var(--glass-bg, rgba(255, 255, 255, 0.15));
    backdrop-filter: blur(20px) saturate(1.5);
    -webkit-backdrop-filter: blur(20px) saturate(1.5);
    border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.30));
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.10);
}}

body[data-preset="{_escape(canonical_preset)}"] .preset-{slug} .profile-card:first-child {{
    border-color: var(--profile-rule);
}}

{component_css}
""".strip()


def build_preset_profile_payload(
    *,
    brief: dict[str, Any],
    packet: dict[str, Any],
    style_contract: dict[str, Any],
    capability: Any,
    specs: list[dict[str, Any]],
) -> PresetProfilePayload:
    canonical_preset = str(capability.canonical_preset or packet.get("canonical_preset") or style_contract["preset"])
    profile_spec = PROFILE_SPECS[canonical_preset]
    family = profile_spec.family
    layouts = profile_spec.layout_sequence
    slug = _slugify(canonical_preset)
    markers = _safe_marker_classes(style_contract, profile_spec)
    total = len(specs)
    language = str(brief.get("language", ""))
    demo_path = _profile_demo_path(profile_spec, language)
    if demo_path is not None:
        css = _extract_demo_css(demo_path, profile_spec)
        sections_html = _render_demo_derived_sections(
            specs,
            demo_path=demo_path,
            layouts=layouts,
            family=family,
            canonical_preset=canonical_preset,
            slug=slug,
            profile_spec=profile_spec,
            language=language,
        )
        renderer_source = f"demo-derived:{demo_path.name}"
    else:
        sections = []
        for index, spec in enumerate(specs):
            layout = layouts[index % len(layouts)]
            sections.append(
                _render_section(
                    spec,
                    total=total,
                    layout=layout,
                    family=family,
                    canonical_preset=canonical_preset,
                    slug=slug,
                )
            )
        css = _profile_css(canonical_preset, family, slug, profile_spec)
        sections_html = "\n\n".join(sections)
        renderer_source = "generic-profile"
    signature_hash = _style_signature_hash(canonical_preset, family, markers)
    return PresetProfilePayload(
        canonical_preset=canonical_preset,
        generation_status="profile",
        renderer_strategy="unified_profile",
        render_path=str(packet.get("render_path") or f"profile:{slug}"),
        css=css,
        sections_html=sections_html,
        body_classes=("profile-rendered", "profile-renderer", f"pf-{family}", f"preset-{slug}", *profile_spec.body_classes),
        body_data_attrs={
            "data-style-family": family,
            "data-profile-family": family,
            "data-profile-spec": slug,
            "data-profile-renderer-source": renderer_source,
            "data-profile-auto-contrast": "true",
            "data-style-signature": signature_hash,
        },
        slide_count=total,
        style_signature={
            "family": family,
            "preset_slug": slug,
            "marker_classes": list(markers),
            "hash": signature_hash,
            "renderer_source": renderer_source,
        },
    )
