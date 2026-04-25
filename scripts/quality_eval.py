from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from low_context import compile_style_contract, load_brief
from title_browser_qa import analyze_title_composition_path


NUMERIC_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:\$)?(?:\d{4}|\d+\.\d+|\d{2,})(?:%|\+|万|亿|座|辆|美元|亿美元|MWh|k|K)?"
)
CHART_NUMBER_SELECTOR = ",".join(
    [
        "svg text",
        ".chart-val",
        ".ds-kpi",
        ".ent-kpi-number",
        ".ent-timeline-date",
        ".swiss-stat",
        "[class*='kpi-number']",
        "[class*='metric-value']",
        "[class*='chart-value']",
    ]
)
COMPONENT_KIND_SELECTORS: dict[str, str] = {
    "heading": "h1,h2,h3",
    "paragraph": "p",
    "list": "ul li,ol li",
    "table": "table",
    "svg_chart": "svg",
    "quote": "blockquote,[class*='quote'],[class*='pull']",
    "metric_card": "[class*='kpi'],[class*='metric'],[class*='stat']",
    "timeline": "[class*='timeline']",
    "matrix": "[class*='matrix'],[class*='comparison']",
    "diagram": "[class*='diagram'],[class*='workflow'],[class*='arch']",
    "code": "pre,code",
    "image": "img,picture,figure",
}


def _read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _load_optional_brief(path: str | Path | None) -> dict[str, Any] | None:
    if not path:
        return None
    return load_brief(path)


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _extract_css_text(html_text: str) -> str:
    return "\n\n".join(match.group(1) for match in re.finditer(r"<style[^>]*>(.*?)</style>", html_text, re.DOTALL))


def _extract_rule_blocks(css_text: str, selector: str) -> list[str]:
    pattern = re.compile(rf"{re.escape(selector)}\s*\{{(.*?)\}}", re.DOTALL)
    return [match.group(1) for match in pattern.finditer(css_text)]


def _selector_hidden_by_default(css_text: str, selector: str) -> bool:
    blocks = _extract_rule_blocks(css_text, selector)
    if not blocks:
        return False
    combined = " ".join(blocks).replace(" ", "").lower()
    hide_markers = (
        "display:none",
        "visibility:hidden",
        "opacity:0",
        "transform:translatex(110%)",
        "transform:translatex(100%)",
        "transform:translatey(110%)",
        "transform:translatey(100%)",
    )
    return any(marker in combined for marker in hide_markers)


def _selector_default_width_risky(css_text: str, selector: str) -> bool:
    combined = " ".join(_extract_rule_blocks(css_text, selector)).lower()
    if not combined:
        return False
    compact = combined.replace(" ", "")
    if "width:min(380px,36vw)" in compact or "width:min(360px,32vw)" in compact:
        return True
    px_matches = [int(value) for value in re.findall(r"width\s*:\s*(\d{3,})px", combined)]
    vw_matches = [int(value) for value in re.findall(r"width\s*:\s*(\d{2,})vw", combined)]
    return any(value >= 280 for value in px_matches) or any(value >= 24 for value in vw_matches)


def _has_hidden_overflow(css_text: str, selector: str) -> bool:
    combined = " ".join(_extract_rule_blocks(css_text, selector)).replace(" ", "").lower()
    return any(token in combined for token in ("overflow:hidden", "overflow-x:hidden", "overflow-y:hidden"))


def _meaningful_numeric_tokens(text: str) -> list[str]:
    normalized = text.replace(",", "").replace(" ", "")
    tokens: list[str] = []
    for match in NUMERIC_TOKEN_RE.finditer(normalized):
        token = match.group(0).lstrip("$")
        if token not in tokens:
            tokens.append(token)
    return tokens


def _extract_html_numeric_tokens(soup: BeautifulSoup) -> list[str]:
    tokens: list[str] = []
    for node in soup.select(CHART_NUMBER_SELECTOR):
        text = _normalize_text(node.get_text(" ", strip=True))
        if not text:
            continue
        if node.find_parent(id="notes-panel") is not None:
            continue
        classes = " ".join(node.get("class", []))
        if any(marker in classes for marker in ("slide-num-label", "bg-num")):
            continue
        for token in _meaningful_numeric_tokens(text):
            if token not in tokens:
                tokens.append(token)
    return tokens


def _collect_source_numeric_tokens(brief: dict[str, Any] | None, source_text: str | None) -> set[str]:
    corpus: list[str] = []
    if brief:
        corpus.append(json.dumps(brief, ensure_ascii=False))
    if source_text:
        corpus.append(source_text)
    tokens: set[str] = set()
    for chunk in corpus:
        tokens.update(_meaningful_numeric_tokens(chunk))
    return tokens


def _extract_phrase_tokens(value: str) -> list[str]:
    tokens: list[str] = []
    for token in re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z0-9][A-Za-z0-9+\-]{2,}", value):
        cleaned = token.lower()
        if cleaned not in tokens:
            tokens.append(cleaned)
    return tokens


def _phrase_present(item: str, html_text: str) -> bool:
    normalized_html = _normalize_text(html_text).lower()
    normalized_item = _normalize_text(item).lower()
    if normalized_item and normalized_item in normalized_html:
        return True
    tokens = _extract_phrase_tokens(item)
    if not tokens:
        return False
    matches = sum(1 for token in tokens if token in normalized_html)
    threshold = 2 if len(tokens) >= 2 else 1
    return matches >= threshold


def _must_include_coverage(brief: dict[str, Any] | None, html_text: str) -> float | None:
    if not brief:
        return None
    must_include = [item.strip() for item in brief["content"]["must_include"] if item.strip()]
    if not must_include:
        return None
    matched = sum(1 for item in must_include if _phrase_present(item, html_text))
    return round(matched / len(must_include), 4)


def _narrative_role_coverage(brief: dict[str, Any] | None, soup: BeautifulSoup) -> tuple[float | None, bool | None]:
    if not brief:
        return None, None
    expected = [slide["role"] for slide in brief["narrative"]["slides"]]
    actual = [
        _normalize_text(slide.get("aria-label") or "")
        for slide in soup.select(".slide")
        if slide.get("aria-label")
    ]
    if not expected:
        return None, None
    matches = sum(1 for expected_role, actual_role in zip(expected, actual) if expected_role == actual_role)
    exact = len(expected) == len(actual) and matches == len(expected)
    return round(matches / len(expected), 4), exact


def _component_kinds(slide: Any) -> set[str]:
    kinds: set[str] = set()
    for kind, selector in COMPONENT_KIND_SELECTORS.items():
        if slide.select_one(selector):
            kinds.add(kind)
    return kinds


def _minimal_slide_ratio(slides: list[Any]) -> tuple[float, int]:
    minimal_flags: list[bool] = []
    for slide in slides:
        kinds = _component_kinds(slide)
        paragraph_count = len(slide.select("p"))
        minimal = kinds <= {"heading", "paragraph"} and paragraph_count <= 1
        minimal_flags.append(minimal)

    if not minimal_flags:
        return 0.0, 0

    max_run = 0
    current_run = 0
    for flag in minimal_flags:
        if flag:
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 0
    ratio = sum(1 for flag in minimal_flags if flag) / len(minimal_flags)
    return round(ratio, 4), max_run


def _avg_component_kinds_per_slide(slides: list[Any]) -> float:
    if not slides:
        return 0.0
    total = sum(len(_component_kinds(slide)) for slide in slides)
    return round(total / len(slides), 4)


def _layout_variety(slides: list[Any]) -> float:
    if not slides:
        return 0.0
    roles = {slide.get("data-export-role") for slide in slides if slide.get("data-export-role")}
    return round(len(roles) / len(slides), 4)


def _style_signature_coverage(soup: BeautifulSoup, preset: str | None) -> float | None:
    if not preset:
        return None
    try:
        contract = compile_style_contract(preset)
    except Exception:
        return None

    required = set(contract["required_signature_classes"]) | set(contract["required_background_layers"])
    if not required:
        return None

    classes_present = {
        f".{class_name}"
        for tag in soup.select("[class]")
        for class_name in tag.get("class", [])
    }
    ids_present = {
        f"#{tag.get('id')}"
        for tag in soup.select("[id]")
        if tag.get("id")
    }
    pseudo_present: set[str] = set()
    css_text = _extract_css_text(str(soup))
    for pseudo in ("body::before", "body::after"):
        if pseudo in css_text:
            pseudo_present.add(pseudo)

    present = classes_present | ids_present | pseudo_present
    matched = len(required & present)
    return round(matched / len(required), 4)


def _compare_non_regression(current: dict[str, Any], baseline: dict[str, Any] | None) -> dict[str, Any] | None:
    if not baseline:
        return None

    layout_delta = round(current["layout_variety"] - baseline["layout_variety"], 4)
    component_delta = round(
        current["avg_component_kinds_per_slide"] - baseline["avg_component_kinds_per_slide"], 4
    )
    style_current = current.get("style_signature_coverage")
    style_baseline = baseline.get("style_signature_coverage")
    style_delta = None
    if style_current is not None and style_baseline is not None:
        style_delta = round(style_current - style_baseline, 4)
    minimal_delta = round(current["minimal_slide_ratio"] - baseline["minimal_slide_ratio"], 4)

    style_ok = style_delta is None or style_delta >= -0.05
    passed = (
        layout_delta >= -0.05
        and component_delta >= -0.05
        and style_ok
        and minimal_delta <= 0.1
    )
    return {
        "layout_variety_delta": layout_delta,
        "component_diversity_delta": component_delta,
        "style_signature_coverage_delta": style_delta,
        "minimal_slide_ratio_delta": minimal_delta,
        "pass": passed,
    }


def analyze_html_quality(
    html_text: str,
    *,
    brief: dict[str, Any] | None = None,
    source_text: str | None = None,
    preset: str | None = None,
    baseline_html: str | None = None,
    title_browser_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    soup = BeautifulSoup(html_text, "html.parser")
    css_text = _extract_css_text(html_text)
    slides = list(soup.select(".slide"))
    inferred_preset = preset or (soup.body.get("data-preset") if soup.body else None)

    default_visible_chrome: list[str] = []
    if soup.select_one("#notes-panel") and not _selector_hidden_by_default(css_text, "#notes-panel"):
        default_visible_chrome.append("notes-panel")
    if soup.select_one("#editToggle") and not _selector_hidden_by_default(css_text, ".edit-toggle"):
        default_visible_chrome.append("edit-toggle")

    chrome_leak = bool(default_visible_chrome)
    content_occlusion_risk = (
        "notes-panel" in default_visible_chrome
        and _selector_default_width_risky(css_text, "#notes-panel")
        and (_has_hidden_overflow(css_text, ".slide") or _has_hidden_overflow(css_text, ".slide-content"))
    )

    html_numeric_tokens = _extract_html_numeric_tokens(soup)
    source_numeric_tokens = _collect_source_numeric_tokens(brief, source_text)
    hallucinated_numeric_tokens = [
        token
        for token in html_numeric_tokens
        if token not in source_numeric_tokens
    ]
    if html_numeric_tokens:
        numeric_faithfulness = round(
            (len(html_numeric_tokens) - len(hallucinated_numeric_tokens)) / len(html_numeric_tokens),
            4,
        )
    else:
        numeric_faithfulness = 1.0

    layout_variety = _layout_variety(slides)
    avg_components = _avg_component_kinds_per_slide(slides)
    minimal_slide_ratio, max_minimal_run = _minimal_slide_ratio(slides)
    role_coverage, role_sequence_match = _narrative_role_coverage(brief, soup)
    must_include_coverage = _must_include_coverage(brief, soup.get_text(" ", strip=True))
    style_signature_coverage = _style_signature_coverage(soup, inferred_preset)

    diagnostics = {
        "quality_tier": None,
        "chrome_leak": chrome_leak,
        "default_visible_chrome": default_visible_chrome,
        "content_occlusion_risk": content_occlusion_risk,
        "layout_variety": layout_variety,
        "avg_component_kinds_per_slide": avg_components,
        "style_signature_coverage": style_signature_coverage,
        "numeric_faithfulness": numeric_faithfulness,
        "hallucinated_numeric_tokens": hallucinated_numeric_tokens,
        "source_fact_coverage": must_include_coverage,
        "narrative_role_coverage": role_coverage,
        "role_sequence_match": role_sequence_match,
        "minimal_slide_ratio": minimal_slide_ratio,
        "max_minimal_slide_run": max_minimal_run,
    }
    if title_browser_report:
        diagnostics.update(title_browser_report.get("diagnostics", {}))
    if brief and brief.get("style"):
        diagnostics["quality_tier"] = brief["style"].get("quality_tier")

    gates = {
        "chrome-hidden-by-default": not chrome_leak,
        "no-content-occlusion-risk": not content_occlusion_risk,
        "numeric-faithfulness": numeric_faithfulness >= 0.95,
        "source-fact-coverage": must_include_coverage is None or must_include_coverage >= 0.67,
        "narrative-role-coverage": role_coverage is None or role_coverage == 1.0,
        "minimal-slide-run": max_minimal_run < 3,
    }
    if title_browser_report:
        gates["browser-title-composition"] = bool(title_browser_report.get("pass"))

    hard_failures: list[str] = []
    if chrome_leak:
        hard_failures.append("chrome-visible-by-default")
    if content_occlusion_risk:
        hard_failures.append("content-occlusion-risk")
    if hallucinated_numeric_tokens:
        hard_failures.append("hallucinated-numeric-chart-values")
    if role_coverage is not None and role_coverage < 1.0:
        hard_failures.append("narrative-role-mismatch")
    if title_browser_report:
        for code in title_browser_report.get("hard_failures", []):
            if code not in hard_failures:
                hard_failures.append(code)

    baseline_report = None
    if baseline_html:
        baseline_report = analyze_html_quality(
            baseline_html,
            brief=brief,
            source_text=source_text,
            preset=inferred_preset,
        )

    report = {
        "preset": inferred_preset,
        "slide_count": len(slides),
        "hard_failures": hard_failures,
        "quality_gates": gates,
        "diagnostics": diagnostics,
    }
    comparison = _compare_non_regression(diagnostics, baseline_report["diagnostics"] if baseline_report else None)
    if comparison is not None:
        report["comparison"] = {"non_regression": comparison}
    return report


def analyze_html_quality_paths(
    html_path: str | Path,
    *,
    brief_path: str | Path | None = None,
    source_path: str | Path | None = None,
    preset: str | None = None,
    baseline_html_path: str | Path | None = None,
    title_browser_report_path: str | Path | None = None,
    run_browser_titles: bool = False,
) -> dict[str, Any]:
    html_text = _read_text(html_path)
    brief = _load_optional_brief(brief_path)
    source_text = _read_text(source_path) if source_path else None
    baseline_html = _read_text(baseline_html_path) if baseline_html_path else None
    title_browser_report = None
    if title_browser_report_path:
        title_browser_report = json.loads(_read_text(title_browser_report_path))
    elif run_browser_titles:
        title_browser_report = analyze_title_composition_path(html_path, preset=preset)

    report = analyze_html_quality(
        html_text,
        brief=brief,
        source_text=source_text,
        preset=preset,
        baseline_html=baseline_html,
        title_browser_report=title_browser_report,
    )
    report["html_path"] = str(html_path)
    if brief_path:
        report["brief_path"] = str(brief_path)
    if source_path:
        report["source_path"] = str(source_path)
    if baseline_html_path:
        report["baseline_html_path"] = str(baseline_html_path)
    if title_browser_report_path:
        report["title_browser_report_path"] = str(title_browser_report_path)
    return report
