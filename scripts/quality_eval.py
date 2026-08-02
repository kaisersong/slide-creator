from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from low_context import _preset_usage_rules, compile_style_contract, load_brief
from preset_contracts import requirement_for_preset
from style_signature_eval import collect_signature_presence
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
    "heading": "h1,h2,h3,h4",
    "paragraph": "p",
    "list": "ul li,ol li",
    "table": "table",
    "svg_chart": "svg",
    "quote": "blockquote,[class*='quote'],[class*='pull']",
    "card": ".feat-card,.inst-block,.cta-block,.index-item,.disc-step,.pain-item,.hero-stat,.g,.bl,.step,.info,.co,.ds-kpi-card,.ds-matrix-cell,.ent-kpi-card,.ent-feature-card,.ent-feature-row,.ent-arch-card,.ent-contrast-block,.ent-timeline-item,[class*='card']",
    "metric_card": "[class*='kpi'],[class*='metric'],[class*='stat']",
    "timeline": "[class*='timeline']",
    "matrix": "[class*='matrix'],[class*='comparison'],.cols2,.cols3,.cols4,.bento,.ent-contrast-split,.ent-feature-grid",
    "diagram": "[class*='diagram'],[class*='workflow'],[class*='arch'],.layer,.ent-arch-grid",
    "code": "pre,code,.ent-code",
    "image": "img,picture,figure",
    "fact": ".iri-fact,.iri-fracture-item,.iri-spectrum-item",
    "field": ".iri-field,.iri-contract-layer",
    "process": ".iri-pipeline-step,.iri-gate",
    "control": ".iri-key,.iri-command",
    "mode": ".iri-mode,.iri-quadrant",
}


def _project_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "scripts").is_dir() and (candidate / "references").is_dir():
            return candidate
    return Path(__file__).resolve().parent.parent


COPY_RESIDUAL_BLOCKLIST_PATH = _project_root() / "references" / "copy-residual-blocklist.json"


def _read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _load_optional_brief(path: str | Path | None) -> dict[str, Any] | None:
    if not path:
        return None
    return load_brief(path)


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _residual_text_contains(haystack: str, needle: str) -> bool:
    normalized_haystack = _normalize_text(haystack).casefold()
    normalized_needle = _normalize_text(needle).casefold()
    return bool(normalized_needle and normalized_needle in normalized_haystack)


def _copy_residual_source_label(path: Path) -> str:
    try:
        return path.relative_to(_project_root()).as_posix()
    except ValueError:
        return path.as_posix()


def _load_copy_residual_blocklist(path: Path = COPY_RESIDUAL_BLOCKLIST_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items", []) if isinstance(data, dict) else []
    normalized_items: list[dict[str, Any]] = []
    source = _copy_residual_source_label(path)
    for item in items:
        if not isinstance(item, dict):
            continue
        term = str(item.get("term") or "").strip()
        if not term:
            continue
        category = str(item.get("category") or "copy").strip() or "copy"
        normalized_items.append(
            {
                "term": term,
                "code": str(item.get("code") or f"{category}-residual").strip(),
                "category": category,
                "severity": str(item.get("severity") or "warning").strip().lower(),
                "allow_if_authorized": bool(item.get("allow_if_authorized", True)),
                "evidence": str(item.get("evidence") or "").strip(),
                "source": source,
            }
        )
    return normalized_items


def _copy_residual_authorized(term: str, brief: dict[str, Any] | None, source_text: str | None) -> bool:
    corpus: list[str] = []
    if brief:
        corpus.append(json.dumps(brief, ensure_ascii=False))
    if source_text:
        corpus.append(source_text)
    return any(_residual_text_contains(chunk, term) for chunk in corpus)


def _copy_residual_diagnostics(
    visible_text: str,
    brief: dict[str, Any] | None,
    source_text: str | None,
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[str]]:
    hard_hits: list[dict[str, str]] = []
    hard_failures: list[str] = []
    for item in _load_copy_residual_blocklist():
        if not _residual_text_contains(visible_text, item["term"]):
            continue
        if item["allow_if_authorized"] and _copy_residual_authorized(item["term"], brief, source_text):
            continue
        hit = {
            "code": item["code"],
            "term": item["term"],
            "category": item["category"],
            "severity": item["severity"],
            "source": item["source"],
            "evidence": item["evidence"],
        }
        hard_hits.append(hit)
        if item["severity"] == "hard" and item["code"] not in hard_failures:
            hard_failures.append(item["code"])

    must_avoid_hits: list[dict[str, str]] = []
    content = brief.get("content", {}) if brief else {}
    for item in content.get("must_avoid", []) or []:
        term = str(item).strip()
        if term and _residual_text_contains(visible_text, term):
            must_avoid_hits.append(
                {
                    "term": term,
                    "severity": "warning",
                    "source": "brief.content.must_avoid",
                }
            )

    return hard_hits, must_avoid_hits, hard_failures


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
    normalized = text.replace(",", "")
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
            if re.fullmatch(r"0[1-9]", token) and (
                re.fullmatch(r"0[1-9]", text)
                or re.fullmatch(r"(?:signal|step|stage|phase|item|point)\s+0[1-9]", text, flags=re.IGNORECASE)
            ):
                continue
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


def _slide_local_numeric_tokens(slide: dict[str, Any]) -> set[str]:
    corpus = [
        slide.get("title", ""),
        slide.get("key_point", ""),
        slide.get("claim", ""),
        slide.get("explanation", ""),
        slide.get("visual_intent", ""),
        " ".join(str(value) for value in slide.get("supporting_facts", []) if str(value).strip()),
        " ".join(str(value) for value in slide.get("numeric_facts", []) if str(value).strip()),
    ]
    tokens: set[str] = set()
    for chunk in corpus:
        tokens.update(_meaningful_numeric_tokens(str(chunk)))
    return tokens


def _chart_signal_mismatch(brief: dict[str, Any] | None, slides: list[Any]) -> tuple[int | None, float | None]:
    if not brief:
        return None, None
    mismatch = 0
    chart_slide_count = 0
    brief_slides = brief.get("narrative", {}).get("slides", [])
    for slide_meta, slide_dom in zip(brief_slides, slides):
        has_chart = bool(slide_dom.select_one('svg[aria-label="bar chart"], svg[aria-label="line chart"]'))
        if not has_chart:
            continue
        chart_slide_count += 1
        chart_policy = str(slide_meta.get("chart_policy") or "auto").strip().lower()
        if chart_policy == "required":
            continue
        local_numeric = _slide_local_numeric_tokens(slide_meta)
        if len(local_numeric) < 2:
            mismatch += 1
    if chart_slide_count == 0:
        return 0, 0.0
    return mismatch, round(mismatch / chart_slide_count, 4)


def _global_fact_overuse(brief: dict[str, Any] | None, slides: list[Any]) -> int | None:
    if not brief:
        return None
    content = brief.get("content", {})
    facts = content.get("global_facts") or content.get("must_include") or []
    normalized_facts = [str(item).strip() for item in facts if str(item).strip()]
    if not normalized_facts:
        return 0

    threshold = max(3, len(slides) // 2)
    overused = 0
    for fact in normalized_facts:
        count = 0
        for slide in slides:
            text = slide.get_text(" ", strip=True)
            if _phrase_present(fact, text):
                count += 1
        if count > threshold:
            overused += 1
    return overused


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


def _max_sequence_run(values: list[str]) -> int:
    longest = 0
    current = 0
    previous = None
    for value in values:
        if value == previous:
            current += 1
        else:
            previous = value
            current = 1
        longest = max(longest, current)
    return longest


def _unique_ratio(values: list[str]) -> float:
    if not values:
        return 0.0
    return round(len(set(values)) / len(values), 4)


def _slide_visual_family(slide: Any) -> str:
    role = str(slide.get("data-export-role") or "").strip()
    classes = set(slide.get("class", []))

    if slide.select_one(".ent-dashboard-story"):
        return "story-dashboard"
    if slide.select_one(".ent-cover-metric-row"):
        return "cover-dashboard"
    if slide.select_one(".ent-contrast-split"):
        return "contrast"
    if slide.select_one(".ent-feature-grid"):
        return "feature-grid"
    if slide.select_one(".ent-table"):
        return "table"
    if slide.select_one(".ent-timeline"):
        return "timeline"
    if slide.select_one(".ent-arch-grid"):
        return "architecture"
    if slide.select_one(".ent-split"):
        return "split"
    if slide.select_one(".ent-matrix"):
        return "matrix"
    if slide.select_one(".ent-code") or "enterprise-close" in classes:
        return "cta"

    if "cover" in classes or role == "cover":
        return "hero"

    if slide.select_one(".ds-action-grid"):
        return "action-grid"
    if slide.select_one(".ds-interaction-layout,.ds-key-strip,.ds-mini-console"):
        return "interaction"
    if slide.select_one(".ds-workflow-layout,.ds-workflow-visual,.ds-phase-timeline,.ds-flow-map"):
        return "workflow"
    if slide.select_one(".ds-matrix"):
        return "matrix"
    if slide.select_one(".ds-kpi-grid,.ds-kpi-card,.ds-cover-metric"):
        return "stat"
    if slide.select_one(".ds-signal-bars"):
        return "bar-chart"
    if slide.select_one(".ds-signal-map"):
        return "signal-map"
    if slide.select_one(".ds-evidence-ladder"):
        return "evidence-ladder"
    if slide.select_one(".ds-state-grid-svg"):
        return "state-grid"
    if slide.select_one(".ds-chart-visual,.ds-chart-svg"):
        return "chart"

    if "chapter" in classes or role == "chapter":
        return "chapter"
    if slide.select_one(".cloud-layer,.cloud-strip"):
        return "hero"
    if slide.select_one(".bento"):
        if slide.select_one(".stat"):
            return "bento-stat"
        if slide.select_one(".cmd,.co,.info"):
            return "bento-control"
        return "bento"
    if slide.select_one(".layer"):
        return "layer-flow"
    if slide.select_one(".cols2,.cols3,.cols4"):
        if slide.select_one(".cmd,.co,.info"):
            return "control-split"
        if slide.select_one(".bl"):
            return "list-split"
        return "split"
    if slide.select_one(".cmd"):
        return "command"

    if slide.select_one(".left-panel,.right-panel"):
        if role in {"title_grid", "cover"}:
            return "hero"
        return "split"
    if slide.select_one(".stat-row,.hero-stat"):
        return "stat"
    if slide.select_one(".feat-grid,.feat-card"):
        return "feature-grid"
    if slide.select_one(".inst-blocks,.inst-block"):
        return "evidence"
    if slide.select_one(".cta-block"):
        return "cta"

    role_map = {
        "title_grid": "hero",
        "cover": "hero",
        "chapter": "chapter",
        "kpi_dashboard": "dashboard",
        "kpi_chart": "stat-chart",
        "kpi_grid": "stat",
        "hero_number": "stat",
        "contrast_split": "contrast",
        "consulting_split": "split",
        "column_content": "split",
        "comparison_matrix": "matrix",
        "workflow_chart": "workflow",
        "timeline": "timeline",
        "architecture_map": "architecture",
        "data_table": "table",
        "contents_index": "index",
        "bento": "bento",
        "pull_quote": "quote",
        "insight_pull": "insight",
        "cta_close": "cta",
        "closing": "cta",
    }
    return role_map.get(role, role or "unknown")


def _density_bucket(kind_count: int) -> str:
    if kind_count <= 1:
        return "bare"
    if kind_count <= 3:
        return "standard"
    return "rich"


def _slide_visual_signature(slide: Any) -> str:
    family = _slide_visual_family(slide)
    role = str(slide.get("data-export-role") or "").strip() or "unknown"
    kinds = sorted(kind for kind in _component_kinds(slide) if kind not in {"heading", "paragraph"})
    kind_key = ",".join(kinds) if kinds else "text"
    return f"{family}|{role}|{_density_bucket(len(kinds))}|{kind_key}"


def _layout_rhythm_diagnostics(slides: list[Any]) -> dict[str, Any]:
    if not slides:
        return {
            "layout_variety": 0.0,
            "layout_role_variety": 0.0,
            "visual_family_variety": 0.0,
            "visual_signature_variety": 0.0,
            "max_layout_role_run": 0,
            "max_visual_family_run": 0,
            "max_visual_signature_run": 0,
            "visual_families": [],
        }

    roles = [str(slide.get("data-export-role") or "unknown").strip() or "unknown" for slide in slides]
    families = [_slide_visual_family(slide) for slide in slides]
    signatures = [_slide_visual_signature(slide) for slide in slides]

    role_variety = _unique_ratio(roles)
    family_variety = _unique_ratio(families)
    signature_variety = _unique_ratio(signatures)
    max_role_run = _max_sequence_run(roles)
    max_family_run = _max_sequence_run(families)
    max_signature_run = _max_sequence_run(signatures)

    raw_score = 0.30 * role_variety + 0.35 * family_variety + 0.35 * signature_variety
    run_penalty = min(
        0.35,
        0.06 * max(0, max_role_run - 2)
        + 0.12 * max(0, max_family_run - 1)
        + 0.10 * max(0, max_signature_run - 1),
    )
    visual_rhythm_score = round(max(0.0, min(1.0, raw_score - run_penalty)), 4)
    return {
        "layout_variety": visual_rhythm_score,
        "layout_role_variety": role_variety,
        "visual_family_variety": family_variety,
        "visual_signature_variety": signature_variety,
        "max_layout_role_run": max_role_run,
        "max_visual_family_run": max_family_run,
        "max_visual_signature_run": max_signature_run,
        "visual_families": families,
    }


def _style_signature_coverage(soup: BeautifulSoup, preset: str | None) -> float | None:
    if not preset:
        return None
    try:
        return collect_signature_presence(str(soup), requirement_for_preset(preset)).coverage
    except Exception:
        return None


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
    comparison = {
        "layout_variety_delta": layout_delta,
        "component_diversity_delta": component_delta,
        "style_signature_coverage_delta": style_delta,
        "minimal_slide_ratio_delta": minimal_delta,
        "pass": passed,
    }
    for key in (
        "layout_role_variety",
        "visual_family_variety",
        "visual_signature_variety",
        "max_layout_role_run",
        "max_visual_family_run",
        "max_visual_signature_run",
    ):
        current_value = current.get(key)
        baseline_value = baseline.get(key)
        if isinstance(current_value, (int, float)) and isinstance(baseline_value, (int, float)):
            comparison[f"{key}_delta"] = round(current_value - baseline_value, 4)
    return comparison


def analyze_html_quality(
    html_text: str,
    *,
    brief: dict[str, Any] | None = None,
    source_text: str | None = None,
    preset: str | None = None,
    baseline_html: str | None = None,
    baseline_report: dict[str, Any] | None = None,
    title_browser_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    soup = BeautifulSoup(html_text, "html.parser")
    css_text = _extract_css_text(html_text)
    slides = list(soup.select(".slide"))
    inferred_preset = preset or (soup.body.get("data-preset") if soup.body else None)
    visible_text = soup.get_text(" ", strip=True)

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

    rhythm_diagnostics = _layout_rhythm_diagnostics(slides)
    layout_variety = rhythm_diagnostics["layout_variety"]
    avg_components = _avg_component_kinds_per_slide(slides)
    minimal_slide_ratio, max_minimal_run = _minimal_slide_ratio(slides)
    role_coverage, role_sequence_match = _narrative_role_coverage(brief, soup)
    must_include_coverage = _must_include_coverage(brief, visible_text)
    chart_signal_mismatch_count, chart_signal_mismatch_rate = _chart_signal_mismatch(brief, slides)
    global_fact_overuse_count = _global_fact_overuse(brief, slides)
    style_presence = None
    if inferred_preset:
        try:
            style_presence = collect_signature_presence(
                html_text,
                requirement_for_preset(inferred_preset),
            )
        except (FileNotFoundError, KeyError):
            # Custom themes compile their contract from themes/<name>/reference.md
            # and do not require a built-in preset-contract JSON.
            style_presence = None
    style_signature_coverage = style_presence.coverage if style_presence else None
    copy_residual_hits, must_avoid_hits, copy_residual_failures = _copy_residual_diagnostics(
        visible_text,
        brief,
        source_text,
    )

    diagnostics = {
        "quality_tier": None,
        "chrome_leak": chrome_leak,
        "default_visible_chrome": default_visible_chrome,
        "content_occlusion_risk": content_occlusion_risk,
        "layout_variety": layout_variety,
        "layout_role_variety": rhythm_diagnostics["layout_role_variety"],
        "visual_family_variety": rhythm_diagnostics["visual_family_variety"],
        "visual_signature_variety": rhythm_diagnostics["visual_signature_variety"],
        "max_layout_role_run": rhythm_diagnostics["max_layout_role_run"],
        "max_visual_family_run": rhythm_diagnostics["max_visual_family_run"],
        "max_visual_signature_run": rhythm_diagnostics["max_visual_signature_run"],
        "visual_families": rhythm_diagnostics["visual_families"],
        "avg_component_kinds_per_slide": avg_components,
        "style_signature_coverage": style_signature_coverage,
        "style_signature_integrity": style_presence.integrity if style_presence else None,
        "visible_signature_hits": list(style_presence.visible_class_hits + style_presence.visible_id_hits) if style_presence else [],
        "background_signature_hits": list(style_presence.background_hits) if style_presence else [],
        "ignored_marker_class_count": len(style_presence.ignored_marker_hits) if style_presence else 0,
        "marker_only_signature_hits": list(style_presence.ignored_marker_hits) if style_presence else [],
        "invisible_signature_hits": list(style_presence.invisible_hits) if style_presence else [],
        "empty_shell_signature_hits": list(style_presence.empty_shell_hits) if style_presence else [],
        "numeric_faithfulness": numeric_faithfulness,
        "hallucinated_numeric_tokens": hallucinated_numeric_tokens,
        "source_fact_coverage": must_include_coverage,
        "chart_signal_mismatch_count": chart_signal_mismatch_count,
        "chart_signal_mismatch_rate": chart_signal_mismatch_rate,
        "global_fact_overuse_count": global_fact_overuse_count,
        "copy_residual_hit_count": len(copy_residual_hits),
        "copy_residual_hits": copy_residual_hits,
        "must_avoid_residual_hits": must_avoid_hits,
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
        "chart-local-signal": chart_signal_mismatch_count in (None, 0),
        "no-copy-residual-hard-failures": not copy_residual_failures,
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
    if chart_signal_mismatch_count:
        hard_failures.append("chart-without-local-numeric-signal")
    for code in copy_residual_failures:
        if code not in hard_failures:
            hard_failures.append(code)
    if role_coverage is not None and role_coverage < 1.0:
        hard_failures.append("narrative-role-mismatch")
    if title_browser_report:
        for code in title_browser_report.get("hard_failures", []):
            if code not in hard_failures:
                hard_failures.append(code)

    computed_baseline_report = baseline_report
    if baseline_html:
        computed_baseline_report = analyze_html_quality(
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
    comparison = _compare_non_regression(
        diagnostics,
        computed_baseline_report["diagnostics"] if computed_baseline_report else None,
    )
    if comparison is not None:
        report["comparison"] = {"non_regression": comparison}
        gates["baseline-non-regression"] = bool(comparison["pass"])
        if not comparison["pass"]:
            hard_failures.append("baseline-regression")
    return report


def analyze_html_quality_paths(
    html_path: str | Path,
    *,
    brief_path: str | Path | None = None,
    source_path: str | Path | None = None,
    preset: str | None = None,
    baseline_html_path: str | Path | None = None,
    baseline_report_path: str | Path | None = None,
    title_browser_report_path: str | Path | None = None,
    run_browser_titles: bool = False,
) -> dict[str, Any]:
    html_text = _read_text(html_path)
    brief = _load_optional_brief(brief_path)
    source_text = _read_text(source_path) if source_path else None
    baseline_html = _read_text(baseline_html_path) if baseline_html_path else None
    baseline_report = json.loads(_read_text(baseline_report_path)) if baseline_report_path else None
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
        baseline_report=baseline_report,
        title_browser_report=title_browser_report,
    )
    report["html_path"] = str(html_path)
    if brief_path:
        report["brief_path"] = str(brief_path)
    if source_path:
        report["source_path"] = str(source_path)
    if baseline_html_path:
        report["baseline_html_path"] = str(baseline_html_path)
    if baseline_report_path:
        report["baseline_report_path"] = str(baseline_report_path)
    if title_browser_report_path:
        report["title_browser_report_path"] = str(title_browser_report_path)
    return report
