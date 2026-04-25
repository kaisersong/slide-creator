from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from title_profiles import (
    COMMON_TITLE_LINE_CLASSES,
    collect_title_candidate_nodes,
    detect_slide_layout_id,
    is_horizontal_title_profile,
    registry_version,
    resolve_title_profile,
)

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - import availability depends on environment
    sync_playwright = None


VISIBLE_CHROME_SELECTORS = [
    "#notes-panel",
    "#editToggle",
    ".edit-toggle",
    ".progress-bar",
    ".nav-dots",
]


def _read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _body_preset(soup: BeautifulSoup) -> str | None:
    body = soup.find("body")
    if not body:
        return None
    preset = body.get("data-preset")
    return str(preset).strip() if preset else None


def _annotate_title_targets(html_text: str, preset: str | None = None) -> tuple[str, list[dict[str, Any]]]:
    soup = BeautifulSoup(html_text, "html.parser")
    inferred_preset = preset or _body_preset(soup)
    targets: list[dict[str, Any]] = []
    target_index = 0

    for slide_index, slide in enumerate(soup.select(".slide"), start=1):
        layout_id = detect_slide_layout_id(slide)
        for node in collect_title_candidate_nodes(slide, inferred_preset):
            profile = resolve_title_profile(inferred_preset, layout_id=layout_id, node=node, slide=slide)
            qa_id = f"slide-{slide_index}-title-{target_index + 1}"
            node["data-title-qa-id"] = qa_id
            targets.append(
                {
                    "qa_id": qa_id,
                    "slide_index": slide_index,
                    "layout_id": layout_id,
                    "profile": profile["profile"],
                    "node_type": profile["node_type"],
                    "max_lines": int(profile.get("max_lines", 3)),
                    "required_companion_selectors": profile.get("required_companion_selectors", []),
                    "required_attributes": profile.get("required_attributes", []),
                    "text": node.get_text(" ", strip=True),
                    "tag_name": getattr(node, "name", ""),
                }
            )
            target_index += 1

    return str(soup), targets


def collect_title_browser_targets(html_text: str, preset: str | None = None) -> dict[str, Any]:
    inferred_preset = preset or _body_preset(BeautifulSoup(html_text, "html.parser"))
    annotated_html, targets = _annotate_title_targets(html_text, preset=inferred_preset)
    return {
        "registry_version": registry_version(),
        "preset": inferred_preset,
        "annotated_html": annotated_html,
        "targets": targets,
    }


def _launch_browser():
    if sync_playwright is None:
        raise RuntimeError("Playwright is not installed; cannot run browser title QA")

    playwright = sync_playwright().start()
    try:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
    except Exception:
        browser = playwright.chromium.launch(headless=True)
    return playwright, browser


def _measure_title_targets_in_browser(annotated_html: str, targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="title-browser-qa-") as temp_dir:
        html_path = Path(temp_dir) / "deck.html"
        html_path.write_text(annotated_html, encoding="utf-8")
        playwright, browser = _launch_browser()
        try:
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(html_path.as_uri(), wait_until="load", timeout=20000)
            page.wait_for_timeout(800)

            results: list[dict[str, Any]] = []
            for target in targets:
                result = page.evaluate(
                    """
                    ({ qaId, lineClasses, visibleChromeSelectors, companionSelectors, requiredAttributes }) => {
                        const el = document.querySelector(`[data-title-qa-id="${qaId}"]`);
                        if (!el) {
                            return { missing: true };
                        }

                        const isVisible = (node) => {
                            const style = window.getComputedStyle(node);
                            if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity || '1') === 0) {
                                return false;
                            }
                            const rect = node.getBoundingClientRect();
                            return rect.width > 1 && rect.height > 1;
                        };

                        const mergeLineRects = (rectList) => {
                            const sorted = rectList
                                .filter((rect) => rect.width > 1 && rect.height > 1)
                                .map((rect) => ({
                                    left: rect.left,
                                    top: rect.top,
                                    width: rect.width,
                                    height: rect.height,
                                }))
                                .sort((a, b) => a.top - b.top || a.left - b.left);

                            const lines = [];
                            for (const rect of sorted) {
                                const existing = lines.find((line) => Math.abs(line.top - rect.top) <= 2);
                                if (existing) {
                                    existing.width = Math.max(existing.width, rect.width);
                                    existing.left = Math.min(existing.left, rect.left);
                                } else {
                                    lines.push({ ...rect });
                                }
                            }
                            return lines;
                        };

                        const explicitChildren = Array.from(el.children).filter((child) =>
                            Array.from(child.classList || []).some((token) => lineClasses.includes(token))
                        );

                        let lineRects = [];
                        if (explicitChildren.length) {
                            lineRects = explicitChildren
                                .filter(isVisible)
                                .map((child) => child.getBoundingClientRect())
                                .map((rect) => ({ left: rect.left, top: rect.top, width: rect.width, height: rect.height }));
                        } else {
                            const range = document.createRange();
                            range.selectNodeContents(el);
                            lineRects = mergeLineRects(Array.from(range.getClientRects()));
                        }

                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);

                        const nodeSelfClips = (node) => {
                            const nodeStyle = window.getComputedStyle(node);
                            const clipsX = ['hidden', 'clip'].includes(nodeStyle.overflowX);
                            const clipsY = ['hidden', 'clip'].includes(nodeStyle.overflowY);
                            return (clipsX && node.scrollWidth > node.clientWidth + 2) ||
                                (clipsY && node.scrollHeight > node.clientHeight + 2);
                        };

                        const lineBoxes = (lineRects.length ? lineRects : [{ left: rect.left, top: rect.top, width: rect.width, height: rect.height }])
                            .map((item) => ({
                                left: item.left,
                                top: item.top,
                                right: item.left + item.width,
                                bottom: item.top + item.height,
                            }));

                        const clippingAncestors = [];
                        let current = el.parentElement;
                        while (current) {
                            const currentStyle = window.getComputedStyle(current);
                            if (['hidden', 'clip'].includes(currentStyle.overflowX) || ['hidden', 'clip'].includes(currentStyle.overflowY)) {
                                clippingAncestors.push(current.getBoundingClientRect());
                            }
                            current = current.parentElement;
                        }

                        const clippedByAncestor = clippingAncestors.some((ancestorRect) =>
                            lineBoxes.some((box) =>
                                box.left < ancestorRect.left - 2 ||
                                box.right > ancestorRect.right + 2 ||
                                box.top < ancestorRect.top - 2 ||
                                box.bottom > ancestorRect.bottom + 2
                            )
                        );
                        const clipped = nodeSelfClips(el) || clippedByAncestor;

                        const visibleChrome = visibleChromeSelectors
                            .flatMap((selector) => Array.from(document.querySelectorAll(selector)))
                            .filter((node) => node && node !== el && isVisible(node))
                            .map((node) => ({
                                selector: node.id ? `#${node.id}` : `.${Array.from(node.classList || [])[0] || node.tagName.toLowerCase()}`,
                                rect: node.getBoundingClientRect(),
                            }));

                        const intersects = (a, b) =>
                            a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;
                        const occludedBy = visibleChrome
                            .filter((entry) => intersects(rect, entry.rect))
                            .map((entry) => entry.selector);

                        const slide = el.closest('.slide');
                        const companionsPresent = companionSelectors.every((selector) => slide && slide.querySelector(selector));
                        const attrsPresent = requiredAttributes.every((attr) => el.getAttribute(attr));

                        return {
                            missing: false,
                            line_count: lineRects.length,
                            line_widths: lineRects.map((item) => Math.round(item.width * 100) / 100),
                            clipped,
                            occluded: occludedBy.length > 0,
                            occluded_by: occludedBy,
                            writing_mode: style.writingMode || '',
                            tag_name: el.tagName.toLowerCase(),
                            classes: Array.from(el.classList || []),
                            attrs_present: attrsPresent,
                            companions_present: companionsPresent,
                        };
                    }
                    """,
                    {
                        "qaId": target["qa_id"],
                        "lineClasses": sorted(COMMON_TITLE_LINE_CLASSES),
                        "visibleChromeSelectors": VISIBLE_CHROME_SELECTORS,
                        "companionSelectors": target.get("required_companion_selectors", []),
                        "requiredAttributes": target.get("required_attributes", []),
                    },
                )
                results.append({"qa_id": target["qa_id"], **result})

            return results
        finally:
            browser.close()
            playwright.stop()


def _orphan_after_render(widths: list[float]) -> bool:
    if len(widths) < 2:
        return False
    longest = max(widths)
    shortest = min(widths)
    return shortest <= max(56.0, longest * 0.26) and shortest <= longest * 0.38


def _collapsed_middle_after_render(widths: list[float]) -> bool:
    if len(widths) < 3:
        return False
    for index in range(1, len(widths) - 1):
        longest_adjacent = max(widths[index - 1], widths[index + 1])
        shortest_adjacent = min(widths[index - 1], widths[index + 1])
        if widths[index] <= longest_adjacent * 0.58 and widths[index] + 72 <= shortest_adjacent:
            return True
    return False


def summarize_title_browser_report(
    targets: list[dict[str, Any]],
    measurements: list[dict[str, Any]],
    *,
    preset: str | None = None,
) -> dict[str, Any]:
    merged: list[dict[str, Any]] = []
    hard_failure_codes: list[str] = []

    measurement_map = {item["qa_id"]: item for item in measurements}
    orphan_count = 0
    collapsed_count = 0
    mismatch_count = 0
    structural_break_count = 0
    clipping_count = 0
    occlusion_count = 0

    for target in targets:
        measurement = measurement_map.get(target["qa_id"], {"missing": True})
        profile = target["profile"]
        failures: list[str] = []
        profile_mismatch = False

        if measurement.get("missing"):
            failures.append("browser-title-missing")
            profile_mismatch = True
        elif is_horizontal_title_profile(profile):
            widths = measurement.get("line_widths", [])
            if measurement.get("line_count", 0) >= 4:
                failures.append("browser-title-too-many-lines")
            if _orphan_after_render(widths):
                failures.append("browser-title-orphan-line")
                orphan_count += 1
            if _collapsed_middle_after_render(widths):
                failures.append("browser-title-collapsed-middle-line")
                collapsed_count += 1
            if measurement.get("clipped"):
                failures.append("browser-title-clipped")
                clipping_count += 1
            if measurement.get("occluded"):
                failures.append("browser-title-occluded")
                occlusion_count += 1
        else:
            if profile == "vertical_title" and "vertical" not in str(measurement.get("writing_mode", "")).lower():
                failures.append("browser-title-profile-mismatch")
                profile_mismatch = True
            if profile == "glitch_lockup" and not measurement.get("attrs_present"):
                failures.append("browser-title-profile-mismatch")
                profile_mismatch = True
            if profile == "split_lockup" and not measurement.get("companions_present"):
                failures.append("browser-title-profile-mismatch")
                profile_mismatch = True
            if measurement.get("clipped"):
                failures.append("browser-title-clipped")
                clipping_count += 1
            if measurement.get("occluded"):
                failures.append("browser-title-occluded")
                occlusion_count += 1
            if profile_mismatch:
                structural_break_count += 1

        if profile_mismatch:
            mismatch_count += 1

        for code in failures:
            if code not in hard_failure_codes:
                hard_failure_codes.append(code)

        merged.append(
            {
                **target,
                **measurement,
                "profile_mismatch": profile_mismatch,
                "hard_failures": failures,
            }
        )

    target_count = len(targets)
    hard_fail_targets = sum(1 for target in merged if target["hard_failures"])
    diagnostics = {
        "browser_title_target_count": target_count,
        "title_hard_fail_rate": round(hard_fail_targets / target_count, 4) if target_count else 0.0,
        "orphan_line_rate": round(orphan_count / target_count, 4) if target_count else 0.0,
        "collapsed_middle_line_rate": round(collapsed_count / target_count, 4) if target_count else 0.0,
        "profile_mismatch_rate": round(mismatch_count / target_count, 4) if target_count else 0.0,
        "structural_preset_break_rate": round(structural_break_count / target_count, 4) if target_count else 0.0,
        "title_clipping_rate": round(clipping_count / target_count, 4) if target_count else 0.0,
        "title_occlusion_rate": round(occlusion_count / target_count, 4) if target_count else 0.0,
    }
    return {
        "preset": preset,
        "registry_version": registry_version(),
        "pass": not hard_failure_codes,
        "hard_failures": hard_failure_codes,
        "diagnostics": diagnostics,
        "targets": merged,
    }


def analyze_title_composition_html(html_text: str, *, preset: str | None = None) -> dict[str, Any]:
    target_data = collect_title_browser_targets(html_text, preset=preset)
    measurements = _measure_title_targets_in_browser(target_data["annotated_html"], target_data["targets"])
    report = summarize_title_browser_report(target_data["targets"], measurements, preset=preset)
    if not report["preset"]:
        report["preset"] = preset or BeautifulSoup(html_text, "html.parser").body.get("data-preset")
    return report


def analyze_title_composition_path(path: str | Path, *, preset: str | None = None) -> dict[str, Any]:
    report = analyze_title_composition_html(_read_text(path), preset=preset)
    report["html_path"] = str(path)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Browser-level QA for slide title composition.")
    parser.add_argument("html_path", help="Path to the generated HTML deck")
    parser.add_argument("--preset", help="Optional preset override")
    parser.add_argument("--output", help="Optional output path for the JSON report")
    parser.add_argument("--strict", action="store_true", help="Return exit code 1 when hard failures exist")
    args = parser.parse_args()

    report = analyze_title_composition_path(args.html_path, preset=args.preset)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    if args.strict and not report["pass"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
