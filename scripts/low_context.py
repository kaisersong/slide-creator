from __future__ import annotations

import hashlib
import html
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from preset_support import preset_support_tier
from title_profiles import profile_allows_explicit_line_control, resolve_title_profile


ROOT = Path(__file__).resolve().parent.parent
REFERENCES_DIR = ROOT / "references"
BRIEF_SCHEMA_PATH = ROOT / "schemas" / "generation-brief.schema.json"
PRESET_USAGE_RULES_PATH = ROOT / "references" / "preset-usage-rules.json"

DEFAULT_SHELL_MARKERS = [
    "body[data-preset]",
    "#brand-mark",
    ".progress-bar",
    ".nav-dots",
    ".edit-hotzone",
    "#editToggle",
    "#notes-panel",
]

PRESET_REFERENCE_MAP = {
    "aurora mesh": "aurora-mesh.md",
    "blue sky": "blue-sky-starter.html",
    "bold signal": "bold-signal.md",
    "chinese chan": "chinese-chan.md",
    "creative voltage": "creative-voltage.md",
    "dark botanical": "dark-botanical.md",
    "data story": "data-story.md",
    "electric studio": "electric-studio.md",
    "enterprise dark": "enterprise-dark.md",
    "glassmorphism": "glassmorphism.md",
    "modern newspaper": "modern-newspaper.md",
    "neo-brutalism": "neo-brutalism.md",
    "neo-retro dev deck": "neo-retro-dev.md",
    "neon cyber": "neon-cyber.md",
    "notebook tabs": "notebook-tabs.md",
    "paper & ink": "paper-ink.md",
    "pastel geometry": "pastel-geometry.md",
    "split pastel": "split-pastel.md",
    "swiss modern": "swiss-modern.md",
    "terminal green": "terminal-green.md",
    "vintage editorial": "vintage-editorial.md",
}

DEFAULT_LAYOUTS = {
    "blue sky": ["cover", "chapter", "comparison", "workflow", "table", "bento", "closing"],
    "swiss modern": [
        "title_grid",
        "column_content",
        "stat_block",
        "data_table",
        "geometric_diagram",
        "pull_quote",
        "contents_index",
    ],
    "chinese chan": [
        "zen_center",
        "zen_split",
        "zen_stat",
        "zen_vertical",
    ],
}

SWISS_ROLE_LAYOUTS = {
    "cover": "title_grid",
    "hook": "title_grid",
    "problem": "column_content",
    "risk": "column_content",
    "two-depths": "column_content",
    "definition": "column_content",
    "boundary": "column_content",
    "baseline": "stat_block",
    "principles": "contents_index",
    "workflow": "geometric_diagram",
    "style-discovery": "contents_index",
    "driver": "contents_index",
    "solution": "stat_block",
    "signals": "contents_index",
    "feature": "data_table",
    "features": "data_table",
    "data-proof": "data_table",
    "proof": "data_table",
    "evidence": "data_table",
    "reliability": "geometric_diagram",
    "state-machines": "geometric_diagram",
    "architecture": "geometric_diagram",
    "verification": "data_table",
    "best-fit": "contents_index",
    "decision": "contents_index",
    "tradeoff": "column_content",
    "closing": "pull_quote",
    "cta": "pull_quote",
}

ENTERPRISE_ROLE_LAYOUTS = {
    "cover": "kpi_dashboard",
    "hook": "kpi_dashboard",
    "problem": "consulting_split",
    "baseline": "insight_pull",
    "risk": "consulting_split",
    "definition": "consulting_split",
    "workflow": "consulting_split",
    "discovery": "architecture_map",
    "core-concepts": "architecture_map",
    "architecture": "architecture_map",
    "solution": "insight_pull",
    "principles": "insight_pull",
    "tradeoff": "comparison_matrix",
    "feature": "comparison_matrix",
    "features": "comparison_matrix",
    "evidence": "data_table",
    "proof": "data_table",
    "metrics": "kpi_dashboard",
    "timeline": "timeline",
    "state-machines": "timeline",
    "comparison": "comparison_matrix",
    "checkpoint": "data_table",
    "best-fit": "comparison_matrix",
    "decision": "cta_close",
    "closing": "cta_close",
    "cta": "cta_close",
}

DATA_STORY_ROLE_LAYOUTS = {
    "cover": "hero_number",
    "hook": "hero_number",
    "problem": "kpi_chart",
    "baseline": "kpi_grid",
    "definition": "kpi_chart",
    "workflow": "workflow_chart",
    "driver": "workflow_chart",
    "discovery": "chart_insight",
    "solution": "comparison_matrix",
    "feature": "kpi_grid",
    "features": "kpi_grid",
    "evidence": "chart_insight",
    "proof": "chart_insight",
    "metrics": "kpi_chart",
    "timeline": "workflow_chart",
    "comparison": "comparison_matrix",
    "risk": "chart_insight",
    "decision": "cta_close",
    "checkpoint": "workflow_chart",
    "best-fit": "comparison_matrix",
    "closing": "cta_close",
    "cta": "cta_close",
}

CHINESE_CHAN_ROLE_LAYOUTS = {
    "cover": "zen_center",
    "hook": "zen_center",
    "problem": "zen_split",
    "definition": "zen_split",
    "discovery": "zen_split",
    "workflow": "zen_split",
    "translation": "zen_split",
    "evidence": "zen_split",
    "proof": "zen_split",
    "comparison": "zen_split",
    "checkpoint": "zen_split",
    "best-fit": "zen_split",
    "summary": "zen_split",
    "noise-filter": "zen_split",
    "driver": "zen_stat",
    "metrics": "zen_stat",
    "signals": "zen_stat",
    "solution": "zen_center",
    "reflection": "zen_center",
    "statement": "zen_center",
    "decision": "zen_vertical",
    "closing": "zen_vertical",
    "cta": "zen_vertical",
}

ENTERPRISE_ROLE_BADGES_ZH = {
    "cover": "总览",
    "hook": "总览",
    "problem": "为何现在",
    "definition": "问题定义",
    "workflow": "工作方式",
    "discovery": "方向判断",
    "solution": "核心判断",
    "feature": "关键动作",
    "features": "角色迁移",
    "evidence": "首批闭环",
    "proof": "验证依据",
    "metrics": "治理门禁",
    "timeline": "推进节奏",
    "comparison": "对比判断",
    "checkpoint": "管理节奏",
    "best-fit": "适配场景",
    "closing": "最终目标",
    "cta": "行动建议",
}

ENTERPRISE_ROLE_BADGES_EN = {
    "cover": "overview",
    "hook": "overview",
    "problem": "why now",
    "definition": "definition",
    "workflow": "workflow",
    "discovery": "direction",
    "solution": "core thesis",
    "feature": "key move",
    "features": "role shift",
    "evidence": "pilot loop",
    "proof": "evidence",
    "metrics": "guardrails",
    "timeline": "timeline",
    "comparison": "comparison",
    "checkpoint": "cadence",
    "best-fit": "fit",
    "closing": "goal",
    "cta": "action",
}


class BriefValidationError(ValueError):
    """Raised when a BRIEF artifact violates the contract."""


class BriefExtractionError(ValueError):
    """Raised when context contains zero or multiple valid BRIEF artifacts."""


class StyleContractError(ValueError):
    """Raised when a style reference cannot be compiled into a contract."""


class RenderError(RuntimeError):
    """Raised when deterministic rendering cannot proceed safely."""


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _load_preset_usage_rules() -> dict[str, Any]:
    return json.loads(_read_text(PRESET_USAGE_RULES_PATH))


def _preset_usage_rules(preset: str) -> dict[str, Any]:
    matrix = _load_preset_usage_rules()
    presets = matrix.get("presets", {})
    normalized = _normalize_preset_name(preset)
    for candidate, rules in presets.items():
        if _normalize_preset_name(candidate) == normalized:
            return rules
    return {}


def _canonical_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower())
    return re.sub(r"_+", "_", cleaned).strip("_")


def _normalize_preset_name(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).lower()


def _ensure_string(value: Any, path: str, errors: list[str], *, min_length: int = 1) -> None:
    if not isinstance(value, str) or len(value.strip()) < min_length:
        errors.append(f"{path} must be a string with length >= {min_length}")


def _ensure_boolean(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, bool):
        errors.append(f"{path} must be a boolean")


def _ensure_integer(
    value: Any,
    path: str,
    errors: list[str],
    *,
    minimum: int | None = None,
    maximum: int | None = None,
) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        errors.append(f"{path} must be an integer")
        return
    if minimum is not None and value < minimum:
        errors.append(f"{path} must be >= {minimum}")
    if maximum is not None and value > maximum:
        errors.append(f"{path} must be <= {maximum}")


def _ensure_enum(value: Any, path: str, errors: list[str], allowed: set[str]) -> None:
    if value not in allowed:
        formatted = ", ".join(sorted(allowed))
        errors.append(f"{path} must be one of: {formatted}")


def _ensure_no_extra_keys(obj: dict[str, Any], path: str, errors: list[str], allowed: set[str]) -> None:
    extras = sorted(set(obj) - allowed)
    if extras:
        errors.append(f"{path} has unexpected fields: {', '.join(extras)}")


def _ensure_required_keys(obj: dict[str, Any], path: str, errors: list[str], required: set[str]) -> None:
    missing = sorted(required - set(obj))
    if missing:
        errors.append(f"{path} missing required fields: {', '.join(missing)}")


def _validate_timing_block(block: Any, path: str, errors: list[str]) -> None:
    if not isinstance(block, dict):
        errors.append(f"{path} must be an object")
        return
    required = {"plan", "generate", "validate", "polish", "total"}
    _ensure_required_keys(block, path, errors, required)
    _ensure_no_extra_keys(block, path, errors, required)
    for key in required:
        if key in block:
            _ensure_string(block[key], f"{path}.{key}", errors)


def validate_brief_data(brief: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(brief, dict):
        return ["brief must be a JSON object"]

    required_top = {
        "schema_version",
        "brief_id",
        "mode",
        "language",
        "title",
        "audience",
        "desired_action",
        "deck",
        "style",
        "content",
        "narrative",
        "runtime",
        "plan_view",
        "timing",
    }
    allowed_top = required_top | {"polish_controls", "notes"}
    _ensure_required_keys(brief, "brief", errors, required_top)
    _ensure_no_extra_keys(brief, "brief", errors, allowed_top)

    if brief.get("schema_version") != 1:
        errors.append("schema_version must equal 1")
    if "brief_id" in brief:
        _ensure_string(brief["brief_id"], "brief.brief_id", errors)
    if "mode" in brief:
        _ensure_enum(brief["mode"], "brief.mode", errors, {"auto", "polish"})
    if "language" in brief:
        _ensure_string(brief["language"], "brief.language", errors, min_length=2)
    if "title" in brief:
        _ensure_string(brief["title"], "brief.title", errors)
    if "audience" in brief:
        _ensure_string(brief["audience"], "brief.audience", errors)
    if "desired_action" in brief:
        _ensure_string(brief["desired_action"], "brief.desired_action", errors)

    deck = brief.get("deck")
    if not isinstance(deck, dict):
        errors.append("brief.deck must be an object")
    else:
        required = {"deck_type", "page_count", "output_format"}
        _ensure_required_keys(deck, "brief.deck", errors, required)
        _ensure_no_extra_keys(deck, "brief.deck", errors, required)
        if "deck_type" in deck:
            _ensure_enum(deck["deck_type"], "brief.deck.deck_type", errors, {"product-demo", "user-content"})
        if "page_count" in deck:
            _ensure_integer(deck["page_count"], "brief.deck.page_count", errors, minimum=5, maximum=20)
        if deck.get("output_format") != "html-slides":
            errors.append("brief.deck.output_format must equal html-slides")

    style = brief.get("style")
    if not isinstance(style, dict):
        errors.append("brief.style must be an object")
    else:
        required = {"preset", "tone", "visual_density"}
        _ensure_required_keys(style, "brief.style", errors, required)
        _ensure_no_extra_keys(style, "brief.style", errors, required)
        if "preset" in style:
            _ensure_string(style["preset"], "brief.style.preset", errors)
        if "tone" in style:
            _ensure_string(style["tone"], "brief.style.tone", errors)
        if "visual_density" in style:
            _ensure_enum(style["visual_density"], "brief.style.visual_density", errors, {"low", "medium", "high"})

    content = brief.get("content")
    if not isinstance(content, dict):
        errors.append("brief.content must be an object")
    else:
        required = {"source_policy", "must_include", "must_avoid"}
        optional = {"global_facts", "optional_support"}
        _ensure_required_keys(content, "brief.content", errors, required)
        _ensure_no_extra_keys(content, "brief.content", errors, required | optional)
        if content.get("source_policy") != "distill-only":
            errors.append("brief.content.source_policy must equal distill-only")
        for key in ("must_include", "must_avoid", "global_facts", "optional_support"):
            if key not in content:
                continue
            value = content.get(key)
            if not isinstance(value, list) or (key in required and not value):
                errors.append(f"brief.content.{key} must be a non-empty array")
                continue
            for index, item in enumerate(value, start=1):
                _ensure_string(item, f"brief.content.{key}[{index}]", errors)

    narrative = brief.get("narrative")
    slides: list[dict[str, Any]] = []
    page_roles: list[str] = []
    if not isinstance(narrative, dict):
        errors.append("brief.narrative must be an object")
    else:
        required = {"thesis", "page_roles", "slides"}
        _ensure_required_keys(narrative, "brief.narrative", errors, required)
        _ensure_no_extra_keys(narrative, "brief.narrative", errors, required)
        if "thesis" in narrative:
            _ensure_string(narrative["thesis"], "brief.narrative.thesis", errors)
        page_roles = narrative.get("page_roles") if isinstance(narrative.get("page_roles"), list) else []
        if not isinstance(narrative.get("page_roles"), list) or len(page_roles) < 5:
            errors.append("brief.narrative.page_roles must be an array with at least 5 items")
        else:
            for index, item in enumerate(page_roles, start=1):
                _ensure_string(item, f"brief.narrative.page_roles[{index}]", errors)
        slides = narrative.get("slides") if isinstance(narrative.get("slides"), list) else []
        if not isinstance(narrative.get("slides"), list) or len(slides) < 5:
            errors.append("brief.narrative.slides must be an array with at least 5 items")
        else:
            slide_required = {"slide_number", "role", "title", "key_point", "visual"}
            slide_optional = {
                "claim",
                "explanation",
                "visual_intent",
                "preferred_layout_family",
                "chart_policy",
                "supporting_facts",
                "numeric_facts",
            }
            for index, slide in enumerate(slides, start=1):
                path = f"brief.narrative.slides[{index}]"
                if not isinstance(slide, dict):
                    errors.append(f"{path} must be an object")
                    continue
                _ensure_required_keys(slide, path, errors, slide_required)
                _ensure_no_extra_keys(slide, path, errors, slide_required | slide_optional)
                if "slide_number" in slide:
                    _ensure_integer(slide["slide_number"], f"{path}.slide_number", errors, minimum=1)
                for key in ("role", "title", "key_point", "visual"):
                    if key in slide:
                        _ensure_string(slide[key], f"{path}.{key}", errors)
                for key in ("claim", "explanation", "visual_intent", "preferred_layout_family"):
                    if key in slide and slide[key] is not None:
                        _ensure_string(slide[key], f"{path}.{key}", errors)
                if "chart_policy" in slide:
                    _ensure_enum(slide["chart_policy"], f"{path}.chart_policy", errors, {"auto", "required", "avoid"})
                for key in ("supporting_facts", "numeric_facts"):
                    if key not in slide:
                        continue
                    value = slide.get(key)
                    if not isinstance(value, list) or not value:
                        errors.append(f"{path}.{key} must be a non-empty array")
                        continue
                    for fact_index, item in enumerate(value, start=1):
                        _ensure_string(item, f"{path}.{key}[{fact_index}]", errors)

    runtime = brief.get("runtime")
    if not isinstance(runtime, dict):
        errors.append("brief.runtime must be an object")
    else:
        required = {"editing_mode", "presenter_mode", "watermark_mode", "export_intent"}
        _ensure_required_keys(runtime, "brief.runtime", errors, required)
        _ensure_no_extra_keys(runtime, "brief.runtime", errors, required)
        if "editing_mode" in runtime:
            _ensure_boolean(runtime["editing_mode"], "brief.runtime.editing_mode", errors)
        if "presenter_mode" in runtime:
            _ensure_boolean(runtime["presenter_mode"], "brief.runtime.presenter_mode", errors)
        if runtime.get("watermark_mode") != "injected-last-slide":
            errors.append("brief.runtime.watermark_mode must equal injected-last-slide")
        if "export_intent" in runtime:
            _ensure_enum(runtime["export_intent"], "brief.runtime.export_intent", errors, {"none", "pptx", "png"})

    plan_view = brief.get("plan_view")
    if not isinstance(plan_view, dict):
        errors.append("brief.plan_view must be an object")
    else:
        required = {"emit_planning_view", "planning_view_path"}
        _ensure_required_keys(plan_view, "brief.plan_view", errors, required)
        _ensure_no_extra_keys(plan_view, "brief.plan_view", errors, required)
        if "emit_planning_view" in plan_view:
            _ensure_boolean(plan_view["emit_planning_view"], "brief.plan_view.emit_planning_view", errors)
        if plan_view.get("planning_view_path") != "PLANNING.md":
            errors.append("brief.plan_view.planning_view_path must equal PLANNING.md")

    timing = brief.get("timing")
    if not isinstance(timing, dict):
        errors.append("brief.timing must be an object")
    else:
        required = {"estimate", "actual"}
        _ensure_required_keys(timing, "brief.timing", errors, required)
        _ensure_no_extra_keys(timing, "brief.timing", errors, required)
        if "estimate" in timing:
            _validate_timing_block(timing["estimate"], "brief.timing.estimate", errors)
        if "actual" in timing:
            _validate_timing_block(timing["actual"], "brief.timing.actual", errors)

    if "polish_controls" in brief:
        polish = brief["polish_controls"]
        if not isinstance(polish, dict):
            errors.append("brief.polish_controls must be an object")
        else:
            required = {"style_constraints", "image_plan", "reference_branch"}
            _ensure_required_keys(polish, "brief.polish_controls", errors, required)
            _ensure_no_extra_keys(polish, "brief.polish_controls", errors, required)
            constraints = polish.get("style_constraints")
            if not isinstance(constraints, list) or not constraints:
                errors.append("brief.polish_controls.style_constraints must be a non-empty array")
            else:
                for index, item in enumerate(constraints, start=1):
                    _ensure_string(item, f"brief.polish_controls.style_constraints[{index}]", errors)

            image_plan = polish.get("image_plan")
            if not isinstance(image_plan, list) or not image_plan:
                errors.append("brief.polish_controls.image_plan must be a non-empty array")
            else:
                item_required = {"slide_number", "intent"}
                item_allowed = item_required | {"reference_direction"}
                for index, item in enumerate(image_plan, start=1):
                    path = f"brief.polish_controls.image_plan[{index}]"
                    if not isinstance(item, dict):
                        errors.append(f"{path} must be an object")
                        continue
                    _ensure_required_keys(item, path, errors, item_required)
                    _ensure_no_extra_keys(item, path, errors, item_allowed)
                    if "slide_number" in item:
                        _ensure_integer(item["slide_number"], f"{path}.slide_number", errors, minimum=1)
                    if "intent" in item:
                        _ensure_string(item["intent"], f"{path}.intent", errors)
                    if "reference_direction" in item and item["reference_direction"] is not None:
                        _ensure_string(item["reference_direction"], f"{path}.reference_direction", errors)
            if polish.get("reference_branch") != "参考驱动":
                errors.append("brief.polish_controls.reference_branch must equal 参考驱动")
    elif brief.get("mode") == "polish":
        errors.append("brief.polish_controls is required when mode is polish")

    if "notes" in brief:
        notes = brief["notes"]
        if not isinstance(notes, str):
            errors.append("brief.notes must be a string")
        elif len(notes) > 400:
            errors.append("brief.notes must be <= 400 characters")

    if not errors and isinstance(deck, dict) and page_roles and slides:
        page_count = deck["page_count"]
        if len(page_roles) != page_count:
            errors.append("brief.narrative.page_roles length must equal deck.page_count")
        if len(slides) != page_count:
            errors.append("brief.narrative.slides length must equal deck.page_count")

        expected_numbers = list(range(1, len(slides) + 1))
        actual_numbers = [slide["slide_number"] for slide in slides]
        if actual_numbers != expected_numbers:
            errors.append("brief.narrative.slides slide_number values must be sequential starting at 1")

        valid_roles = set(page_roles)
        invalid_roles = [slide["role"] for slide in slides if slide["role"] not in valid_roles]
        if invalid_roles:
            errors.append("brief.narrative.slides roles must appear in narrative.page_roles")

    return errors


def load_brief(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    data = json.loads(_read_text(source))
    errors = validate_brief_data(data)
    if errors:
        raise BriefValidationError("\n".join(errors))
    return data


def validate_brief_path(path: str | Path) -> tuple[bool, list[str], dict[str, Any] | None]:
    source = Path(path)
    try:
        data = json.loads(_read_text(source))
    except FileNotFoundError:
        return False, [f"file not found: {source}"], None
    except json.JSONDecodeError as exc:
        return False, [f"invalid JSON: {exc}"], None

    errors = validate_brief_data(data)
    return not errors, errors, data if not errors else None


def _extract_fenced_blocks(text: str) -> list[tuple[str, str]]:
    pattern = re.compile(r"```([A-Za-z0-9_-]*)\n(.*?)```", re.DOTALL)
    return [(language.strip().lower(), block.strip()) for language, block in pattern.findall(text)]


def _extract_raw_json_objects(text: str) -> list[Any]:
    decoder = json.JSONDecoder()
    candidates: list[Any] = []
    index = 0
    while True:
        start = text.find("{", index)
        if start == -1:
            break
        try:
            obj, length = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            index = start + 1
            continue
        candidates.append(obj)
        index = start + length
    return candidates


def extract_brief_from_context(text: str) -> dict[str, Any]:
    raw_candidates: list[Any] = []
    for language, block in _extract_fenced_blocks(text):
        if language and language != "json":
            continue
        try:
            raw_candidates.append(json.loads(block))
        except json.JSONDecodeError:
            continue

    raw_candidates.extend(_extract_raw_json_objects(text))

    valid: dict[str, dict[str, Any]] = {}
    for candidate in raw_candidates:
        if not isinstance(candidate, dict):
            continue
        errors = validate_brief_data(candidate)
        if errors:
            continue
        valid[_canonical_json(candidate)] = candidate

    if not valid:
        raise BriefExtractionError("No valid BRIEF artifact found in context")
    if len(valid) > 1:
        raise BriefExtractionError("Multiple conflicting BRIEF artifacts found in context")
    return next(iter(valid.values()))


def extract_brief_from_messages(messages: list[dict[str, Any]]) -> dict[str, Any]:
    merged = "\n\n".join(str(message.get("content", "")) for message in messages)
    return extract_brief_from_context(merged)


def extract_brief_from_source_text(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if not stripped:
        raise BriefExtractionError("Empty context source")

    try:
        loaded = json.loads(stripped)
    except json.JSONDecodeError:
        loaded = None

    if isinstance(loaded, dict):
        if "messages" in loaded and isinstance(loaded["messages"], list):
            return extract_brief_from_messages(loaded["messages"])
        errors = validate_brief_data(loaded)
        if not errors:
            return loaded

    return extract_brief_from_context(stripped)


def extract_brief_from_source_path(path: str | Path) -> dict[str, Any]:
    return extract_brief_from_source_text(_read_text(Path(path)))


def resolve_style_reference(preset_or_path: str | Path) -> Path:
    candidate = Path(preset_or_path)
    if candidate.exists():
        return candidate.resolve()
    key = _normalize_preset_name(str(preset_or_path))
    if key not in PRESET_REFERENCE_MAP:
        raise StyleContractError(f"Unknown preset or reference path: {preset_or_path}")
    return (REFERENCES_DIR / PRESET_REFERENCE_MAP[key]).resolve()


def _relative_to_root(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def _parse_markdown_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current = "__preamble__"
    buffer: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            sections.setdefault(current, []).append("\n".join(buffer).strip())
            current = match.group(1).strip()
            buffer = []
            continue
        buffer.append(line)
    sections.setdefault(current, []).append("\n".join(buffer).strip())
    return sections


def _extract_backticked_values(text: str) -> list[str]:
    return re.findall(r"`([^`]+)`", text)


def _extract_css_vars(css_text: str) -> dict[str, str]:
    tokens: dict[str, str] = {}
    for match in re.finditer(r"(?<![a-zA-Z0-9_-])(--[a-zA-Z0-9_-]+)\s*:\s*([^;]+);", css_text):
        tokens[match.group(1)] = match.group(2).strip()
    return tokens


def _extract_font_urls(text: str) -> list[str]:
    urls = re.findall(r"https://fonts\.googleapis\.com[^'\"\s)]+", text)
    return sorted(dict.fromkeys(urls))


def _extract_font_families(css_text: str) -> list[str]:
    families: list[str] = []
    for match in re.finditer(r"font-family\s*:\s*([^;]+);", css_text):
        for family in match.group(1).split(","):
            cleaned = family.strip().strip("\"'")
            if cleaned and cleaned not in families:
                families.append(cleaned)
    return families


def _extract_layout_ids(text: str) -> list[str]:
    layout_ids: list[str] = []

    for line in text.splitlines():
        if "Use canonical layout roles:" in line:
            for value in _extract_backticked_values(line):
                if value not in layout_ids:
                    layout_ids.append(value)

    for line in text.splitlines():
        if "->" in line:
            for value in _extract_backticked_values(line):
                if value not in layout_ids:
                    layout_ids.append(value)

    in_named_layouts = False
    for line in text.splitlines():
        if re.match(r"^##\s+Named Layout Variations\b", line):
            in_named_layouts = True
            continue
        if in_named_layouts and re.match(r"^##\s+", line):
            break
        if not in_named_layouts:
            continue
        match = re.match(r"^###\s+\d+\.\s+(.+?)\s*$", line)
        if match:
            slug = _slugify(match.group(1))
            if slug and slug not in layout_ids:
                layout_ids.append(slug)

    return layout_ids


def _extract_heading_block(text: str, heading: str) -> str:
    heading_pattern = rf"(?:\d+\.\s+)?{re.escape(heading)}"
    pattern = re.compile(
        rf"^#{{2,3}}\s+{heading_pattern}\s*$\n(.*?)(?=^#{{2,3}}\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def _extract_forbidden_aliases(lines: list[str]) -> list[str]:
    forbidden: list[str] = []
    for line in lines:
        lowered = line.lower()
        if "must not be emitted" not in lowered and "input-only" not in lowered and "must not" not in lowered:
            continue
        for token in _extract_backticked_values(line):
            if token == "--generate":
                continue
            if not token.startswith((".", "--")):
                continue
            if token not in forbidden:
                forbidden.append(token)
    return forbidden


IGNORED_SIGNATURE_TOKENS = {
    ".slide",
    ".reveal",
    ".visible",
    ".js",
    ".pos",
    ".neg",
    ".neu",
    ".up",
    ".down",
    ".positive",
    ".negative",
    ".neutral",
    ".green",
    ".red",
    ".blue",
    ".muted",
    ".secondary",
    ".tertiary",
    ".card",
    ".badge",
    ".code",
    ".sep",
    ".label-tag",
    ".status-dot",
    ".kpi",
    ".kpi-value",
    ".kpi-label",
    ".kpi-number",
    ".kpi-grid",
    ".kpi-card",
    ".kpi-trend",
    ".chart-layout",
    ".chart-bar",
    ".chart-line",
    ".chart-area",
    ".divider",
    ".eyebrow",
}


def _keep_signature_token(token: str) -> bool:
    if not token:
        return False
    if token in IGNORED_SIGNATURE_TOKENS:
        return False
    if token.endswith("-"):
        return False
    if token.startswith("#") and re.fullmatch(r"#[0-9a-fA-F]{3,8}", token):
        return False
    return True


def _extract_signature_classes(text: str) -> list[str]:
    classes: list[str] = []
    for match in re.finditer(r"(?<![a-zA-Z0-9_-])(\.[A-Za-z][A-Za-z0-9_-]*)", text):
        class_name = match.group(1)
        if not _keep_signature_token(class_name):
            continue
        if class_name not in classes:
            classes.append(class_name)
    return classes


def _extract_background_layers(text: str) -> list[str]:
    layers: list[str] = []
    for pattern in (
        r"(body::before|body::after)",
        r"(\.[A-Za-z][A-Za-z0-9_-]*::before|\.[A-Za-z][A-Za-z0-9_-]*::after)",
        r"(#[A-Za-z][A-Za-z0-9_-]*)",
        r"(\.[A-Za-z][A-Za-z0-9_-]*)",
    ):
        for match in re.finditer(pattern, text):
            value = match.group(1)
            if not _keep_signature_token(value):
                continue
            if value not in layers:
                layers.append(value)
    return layers


def _compile_blue_sky_contract(path: Path) -> dict[str, Any]:
    content = _read_text(path)
    style_match = re.search(r"<style>\s*(.*?)\s*</style>", content, re.DOTALL)
    css_text = style_match.group(1) if style_match else ""
    tokens = _extract_css_vars(css_text)
    font_families = _extract_font_families(css_text)
    background_layers = [
        "body::before",
        "body::after",
        "#orb1",
        "#orb2",
        "#orb3",
        ".cloud-layer",
        ".cloud-strip",
        ".cloud-group",
        ".cloud-puff",
    ]
    required_classes = [
        ".orb",
        ".g",
        ".gt",
        ".pill",
        ".stat",
        ".cols2",
        ".cols3",
        ".cols4",
        ".bento",
        ".layer",
        ".ctable",
        ".info",
        ".co",
    ]
    contract = {
        "preset": "Blue Sky",
        "source_path": _relative_to_root(path),
        "tokens": tokens,
        "font_urls": [],
        "font_families": font_families,
        "required_signature_classes": required_classes,
        "required_background_layers": background_layers,
        "allowed_layout_ids": DEFAULT_LAYOUTS["blue sky"],
        "export_contract_rules": [
            "Blue Sky uses the starter template as the shell owner",
            "Keep REQUIRED BLOCK CSS intact",
            "Keep go() boolean wheel boundary semantics intact",
        ],
        "forbidden_aliases": [],
        "css_blocks": [css_text],
        "style_reminders": [
            "Use the starter template as the source of truth",
            "Keep the airy SaaS look and built-in cloud/orb background",
        ],
    }
    contract["digest"] = _sha256_text(_canonical_json(contract))
    return contract


def compile_style_contract(preset_or_path: str | Path) -> dict[str, Any]:
    path = resolve_style_reference(preset_or_path)
    if path.suffix.lower() == ".html":
        return _compile_blue_sky_contract(path)

    content = _read_text(path)
    sections = _parse_markdown_sections(content)
    css_blocks = [
        block
        for language, block in _extract_fenced_blocks(content)
        if language in {"", "css"}
    ]
    css_text = "\n\n".join(css_blocks)

    signature_text = "\n\n".join(
        entry
        for section, entries in sections.items()
        if section in {
            "Signature Elements",
            "Background",
            "Background Options",
            "Background Rule",
            "Allowed Components",
            "Required CSS Classes",
            "Style Preview Checklist",
            "Style-Specific Rules",
            "Canonical Export Contract",
            "User-Content 12-Page Route",
        }
        for entry in entries
    )

    export_block = _extract_heading_block(content, "Canonical Export Contract")
    export_lines = [
        line.strip()
        for line in export_block.splitlines()
        if line.strip().startswith("- ")
    ]

    preview_lines = []
    for entry in sections.get("Style Preview Checklist", []):
        preview_lines.extend(line.strip() for line in entry.splitlines() if line.strip().startswith("- "))

    contract = {
        "preset": path.stem.replace("-", " ").title().replace("Neo Retro", "Neo-Retro").replace("Dev", "Dev"),
        "source_path": _relative_to_root(path),
        "tokens": _extract_css_vars(css_text),
        "font_urls": _extract_font_urls(css_text),
        "font_families": _extract_font_families(css_text),
        "required_signature_classes": _extract_signature_classes(signature_text),
        "required_background_layers": _extract_background_layers(signature_text),
        "allowed_layout_ids": _extract_layout_ids(content),
        "export_contract_rules": export_lines,
        "forbidden_aliases": _extract_forbidden_aliases(export_lines),
        "css_blocks": css_blocks,
        "style_reminders": preview_lines[:8],
    }

    normalized = _normalize_preset_name(contract["preset"])
    if normalized in PRESET_REFERENCE_MAP:
        friendly = {
            key: key.title().replace("Neo Retro", "Neo-Retro").replace("Paper & Ink", "Paper & Ink")
            for key in PRESET_REFERENCE_MAP
        }
        contract["preset"] = friendly.get(normalized, contract["preset"])

    if contract["forbidden_aliases"]:
        forbidden = set(contract["forbidden_aliases"])
        contract["required_signature_classes"] = [
            token for token in contract["required_signature_classes"]
            if token not in forbidden
        ]
        contract["required_background_layers"] = [
            token for token in contract["required_background_layers"]
            if token not in forbidden
        ]

    if not contract["allowed_layout_ids"]:
        contract["allowed_layout_ids"] = DEFAULT_LAYOUTS.get(normalized, [])
    if not contract["tokens"]:
        raise StyleContractError(f"No CSS tokens found in style reference: {path.name}")

    contract["digest"] = _sha256_text(
        _canonical_json(
            {
                "preset": contract["preset"],
                "source_path": contract["source_path"],
                "tokens": contract["tokens"],
                "required_signature_classes": contract["required_signature_classes"],
                "required_background_layers": contract["required_background_layers"],
                "allowed_layout_ids": contract["allowed_layout_ids"],
                "export_contract_rules": contract["export_contract_rules"],
                "forbidden_aliases": contract["forbidden_aliases"],
            }
        )
    )
    return contract


def assess_quality_tier(brief: dict[str, Any]) -> str:
    errors = validate_brief_data(brief)
    if errors:
        raise BriefValidationError("\n".join(errors))

    score = 0
    if len(brief["content"]["must_include"]) >= 3:
        score += 1
    if len(brief["content"]["must_avoid"]) >= 3:
        score += 1
    if len(brief["narrative"]["page_roles"]) == brief["deck"]["page_count"]:
        score += 1
    if len(brief["narrative"]["slides"]) == brief["deck"]["page_count"]:
        score += 1
    if len(brief["narrative"]["thesis"]) >= 40:
        score += 1
    if all(len(slide["key_point"]) >= 12 and len(slide["visual"]) >= 4 for slide in brief["narrative"]["slides"]):
        score += 1
    if brief["mode"] == "polish":
        score += 1

    if score >= 6:
        return "tier0"
    if score >= 4:
        return "tier1"
    return "tier2"


def _canonical_layout_for_role(role: str, allowed_layouts: list[str], preset: str | None = None) -> str:
    role_map = _layout_map_for_preset(preset or "Swiss Modern")
    role_specific = role_map.get(role)
    if role_specific in allowed_layouts:
        return role_specific
    if allowed_layouts:
        return allowed_layouts[0]
    return "default"


def _layout_map_for_preset(preset: str) -> dict[str, str]:
    normalized = _normalize_preset_name(preset)
    if normalized == "swiss modern":
        return SWISS_ROLE_LAYOUTS
    if normalized == "enterprise dark":
        return ENTERPRISE_ROLE_LAYOUTS
    if normalized == "data story":
        return DATA_STORY_ROLE_LAYOUTS
    if normalized == "chinese chan":
        return CHINESE_CHAN_ROLE_LAYOUTS
    return SWISS_ROLE_LAYOUTS


def _avoid_long_layout_runs(layout_id: str, previous_layouts: list[str], layout_cycle: list[str]) -> str:
    if len(previous_layouts) < 2 or previous_layouts[-1] != previous_layouts[-2] or previous_layouts[-1] != layout_id:
        return layout_id
    for candidate in layout_cycle:
        if candidate != layout_id:
            return candidate
    return layout_id


def _slide_claim(slide: dict[str, Any]) -> str:
    return str(slide.get("claim") or slide.get("title") or "").strip()


def _slide_explanation(slide: dict[str, Any]) -> str:
    return str(slide.get("explanation") or slide.get("key_point") or "").strip()


def _slide_visual_intent(slide: dict[str, Any]) -> str:
    return str(slide.get("visual_intent") or slide.get("visual") or "").strip()


def _slide_supporting_facts(slide: dict[str, Any]) -> list[str]:
    values = slide.get("supporting_facts")
    if not isinstance(values, list):
        return []
    return [str(value).strip() for value in values if str(value).strip()]


def _slide_numeric_facts(slide: dict[str, Any]) -> list[str]:
    values = slide.get("numeric_facts")
    if not isinstance(values, list):
        return []
    return [str(value).strip() for value in values if str(value).strip()]


def _preferred_layout_from_family(
    family: str | None,
    usage_rules: dict[str, Any],
    allowed_layouts: list[str],
) -> str | None:
    if not family:
        return None
    family_map = usage_rules.get("layout_family_map", {})
    layout_id = family_map.get(str(family).strip().lower())
    if layout_id in allowed_layouts:
        return layout_id
    return None


def _title_component_for_layout(
    preset: str,
    layout_id: str,
    *,
    default: str = "title",
) -> str:
    rules = _preset_usage_rules(preset)
    mapping = rules.get("title_component_by_layout", {})
    value = mapping.get(layout_id)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def _slide_global_facts(brief: dict[str, Any]) -> list[str]:
    content = brief.get("content") if isinstance(brief.get("content"), dict) else {}
    facts = content.get("global_facts")
    if isinstance(facts, list) and facts:
        return [str(value).strip() for value in facts if str(value).strip()]
    return [str(value).strip() for value in content.get("must_include", []) if str(value).strip()]


def _slide_optional_support(brief: dict[str, Any]) -> list[str]:
    content = brief.get("content") if isinstance(brief.get("content"), dict) else {}
    values = content.get("optional_support")
    if not isinstance(values, list):
        return []
    return [str(value).strip() for value in values if str(value).strip()]


def _semantic_blob(*values: str) -> str:
    return " ".join(str(value or "").strip() for value in values if str(value or "").strip())


def _has_comparison_signal(*values: str) -> bool:
    blob = _semantic_blob(*values)
    patterns = [
        r"\bvs\b",
        r"versus",
        r"A/B",
        r"二选一",
        r"不是.+而是",
        r"对比",
        r"边界",
        r"分工",
        r"更适合",
        r"承担",
        r"负责",
    ]
    return any(re.search(pattern, blob, re.IGNORECASE) for pattern in patterns)


def _has_progression_signal(*values: str) -> bool:
    blob = _semantic_blob(*values)
    patterns = [
        r"先.+再",
        r"最后",
        r"阶段",
        r"里程碑",
        r"路径",
        r"个月",
        r"周期",
        r"逐步",
        r"today|tomorrow|next",
    ]
    return any(re.search(pattern, blob, re.IGNORECASE) for pattern in patterns)


def _has_compact_anchor(text: str) -> bool:
    compact = _compact_display_token(text, fallback="")
    return bool(compact) and len(compact) <= 6


def build_render_packet(
    brief: dict[str, Any],
    *,
    style_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    errors = validate_brief_data(brief)
    if errors:
        raise BriefValidationError("\n".join(errors))

    style_contract = style_contract or compile_style_contract(brief["style"]["preset"])
    preset = brief["style"]["preset"]
    deck_type = brief["deck"]["deck_type"]
    page_count = brief["deck"]["page_count"]
    normalized = _normalize_preset_name(preset)
    quality_tier = assess_quality_tier(brief)

    composition_source = (
        "references/composition-8.md"
        if deck_type == "product-demo"
        else "references/composition-guide.md"
    )
    if normalized == "blue sky":
        runtime_path = "blue-sky-starter"
        required_refs = [
            "references/blue-sky-starter.html",
            composition_source,
        ]
        required_contracts = ["preset-metadata", "blue-sky-architecture", "shell-ui-markers"]
    else:
        runtime_path = "shared-js-engine"
        required_refs = [
            composition_source,
            "references/html-template.md",
            "references/js-engine.md",
            "references/base-css.md",
            style_contract["source_path"],
        ]
        required_contracts = [
            "preset-metadata",
            "shared-runtime",
            "style-signature",
            "shell-ui-markers",
        ]

    fallback_policy = {
        "tier0": "full-preset-contract",
        "tier1": "canonical-layouts-before-fail",
        "tier2": "deterministic-scaffolds-before-fail",
    }[quality_tier]

    packet = {
        "brief_hash": _sha256_text(_canonical_json(brief)),
        "preset": preset,
        "preset_support_tier": preset_support_tier(preset),
        "deck_type": deck_type,
        "page_count": page_count,
        "composition_source": composition_source,
        "runtime_path": runtime_path,
        "required_refs": required_refs,
        "required_contracts": required_contracts,
        "required_shell_markers": DEFAULT_SHELL_MARKERS,
        "style_contract_digest": style_contract["digest"],
        "allowed_layouts": style_contract["allowed_layout_ids"] or DEFAULT_LAYOUTS.get(normalized, []),
        "quality_tier": quality_tier,
        "fallback_policy": fallback_policy,
    }
    return packet


def _split_supporting_phrases(value: str, *, minimum: int = 3) -> list[str]:
    parts = re.split(r"[，。；、,;:]| and | with | / ", value)
    cleaned: list[str] = []
    for part in parts:
        normalized = re.sub(r"\s+", " ", part).strip()
        if normalized and normalized not in cleaned:
            cleaned.append(normalized)
    if len(cleaned) >= minimum:
        return cleaned[:minimum]
    base = cleaned or [value.strip()]
    while len(base) < minimum:
        base.append(base[-1])
    return base[:minimum]


def _normalize_match_text(value: str) -> str:
    return re.sub(r"\s+", "", value or "").lower()


def _content_tokens(value: str) -> list[str]:
    chunks = re.split(r"[，。；、,;:：/+\-\s（）()【】\[\]“”\"']+", value or "")
    tokens: list[str] = []
    for chunk in chunks:
        cleaned = chunk.strip()
        if not cleaned:
            continue
        if re.fullmatch(r"\d+(?:\.\d+)?(?:\+|%|万|亿|年|个月)?", cleaned):
            tokens.append(cleaned)
            continue
        if len(cleaned) >= 2 and cleaned not in tokens:
            tokens.append(cleaned)
    return tokens


def _select_relevant_evidence_items(
    slide: dict[str, Any],
    must_include: list[str],
    *,
    limit: int,
    usage: dict[str, int] | None = None,
) -> list[str]:
    usage = usage or {}
    blob = " ".join([slide.get("title", ""), slide.get("key_point", ""), slide.get("visual", "")])
    normalized_blob = _normalize_match_text(blob)
    blob_numbers = set(_extract_numbers(blob))
    ranked: list[tuple[float, int, str]] = []

    for index, item in enumerate(must_include):
        cleaned = item.strip()
        if not cleaned:
            continue
        normalized_item = _normalize_match_text(cleaned)
        score = 0.0
        if normalized_item and normalized_item in normalized_blob:
            score += 10.0

        item_numbers = set(_extract_numbers(cleaned))
        if item_numbers and blob_numbers:
            score += 4.0 * len(item_numbers & blob_numbers)

        for token in _content_tokens(cleaned):
            if _normalize_match_text(token) in normalized_blob:
                score += 1.5 if len(token) <= 6 else 1.0

        score -= usage.get(cleaned, 0) * 1.2
        ranked.append((score, index, cleaned))

    ranked.sort(key=lambda entry: (-entry[0], entry[1]))
    selected = [item for _, _, item in ranked[:limit]]
    for item in selected:
        usage[item] = usage.get(item, 0) + 1
    return selected


def _build_supporting_items(slide: dict[str, Any], evidence: list[str], *, minimum: int) -> list[str]:
    candidates: list[str] = []
    for source in (slide.get("key_point", ""), slide.get("title", "")):
        for item in _split_supporting_phrases(source, minimum=1):
            cleaned = item.strip()
            if cleaned and cleaned not in candidates and cleaned != slide.get("title", "").strip():
                candidates.append(cleaned)
    for item in evidence:
        if item not in candidates:
            candidates.append(item)
    if not candidates:
        candidates = [slide.get("key_point", "").strip() or slide.get("title", "").strip()]
    while len(candidates) < minimum:
        candidates.append(candidates[-1])
    return candidates[:minimum]


def _has_numeric_signal(*values: str) -> bool:
    blob = " ".join(value for value in values if value).strip()
    return bool(_extract_numbers(blob))


def _enterprise_role_badge(role: str, language: str) -> str:
    is_zh = language.lower().startswith("zh")
    mapping = ENTERPRISE_ROLE_BADGES_ZH if is_zh else ENTERPRISE_ROLE_BADGES_EN
    return mapping.get(role, role)


def _should_use_enterprise_story_dashboard(
    spec: dict[str, Any],
    *,
    preset: str,
    language: str,
) -> bool:
    if _normalize_preset_name(preset) != "enterprise dark":
        return False
    if spec["layout_id"] != "kpi_dashboard":
        return False
    if _has_numeric_signal(
        spec["title"],
        spec["key_point"],
        spec["visual"],
        *spec["supporting_items"],
        *spec["evidence_items"],
    ):
        return False

    dense_title = len(_normalize_text_for_story(spec["title"])) >= (18 if language.lower().startswith("zh") else 28)
    dense_copy = len(_normalize_text_for_story(spec["key_point"])) >= (20 if language.lower().startswith("zh") else 36)
    return dense_title or dense_copy


def _normalize_text_for_story(value: str) -> str:
    return re.sub(r"\s+", "", value or "")


def _skill_version() -> str:
    skill_text = _read_text(ROOT / "SKILL.md")
    match = re.search(r"^version:\s*([^\s]+)\s*$", skill_text, re.MULTILINE)
    return match.group(1) if match else "unknown"


def _brand_mark_text(title: str, preset: str) -> str:
    normalized_title = re.sub(r"\s+", " ", title or "").strip()
    if not normalized_title:
        return preset
    compact = re.sub(r"\s+", "", normalized_title)
    limit = 18 if re.search(r"[\u3400-\u9fff]", compact) else 28
    if len(compact) <= limit:
        return normalized_title
    if re.search(r"[\u3400-\u9fff]", compact):
        return compact[:limit] + "…"
    return normalized_title[:limit].rstrip() + "…"


def _build_enterprise_story_items(
    specs: list[dict[str, Any]],
    index: int,
    *,
    language: str,
) -> list[dict[str, str]]:
    spec = specs[index]
    items: list[dict[str, str]] = []

    if spec["role"] in {"cover", "hook"}:
        for offset, preview in enumerate(specs[index + 1:index + 4], start=1):
            items.append(
                {
                    "index": f"{offset:02d}",
                    "badge": _enterprise_role_badge(preview["role"], language),
                    "title": preview["title"],
                    "body": preview["key_point"],
                }
            )
        if items:
            return items

    labels: list[str] = []
    for label in spec["supporting_items"] + spec["evidence_items"]:
        cleaned = label.strip()
        if cleaned and cleaned not in labels:
            labels.append(cleaned)
        if len(labels) == 3:
            break

    if not labels:
        labels = [spec["title"], spec["key_point"], spec["visual"]]

    body = spec["visual"].strip() or spec["key_point"]
    for offset, label in enumerate(labels[:3], start=1):
        if label == body:
            card_body = spec["key_point"]
        else:
            card_body = body
        items.append(
            {
                "index": f"{offset:02d}",
                "badge": _enterprise_role_badge(spec["role"], language),
                "title": label,
                "body": card_body,
            }
        )
    return items


def _build_candidate_fact_pool(
    slide: dict[str, Any],
    brief: dict[str, Any],
) -> list[str]:
    return _dedupe_preserve(
        [
            *_slide_supporting_facts(slide),
            *_slide_numeric_facts(slide),
            *_slide_global_facts(brief),
            *_slide_optional_support(brief),
        ]
    )


def _layout_requirement_failure(
    spec: dict[str, Any],
    layout_id: str,
    usage_rules: dict[str, Any],
) -> str | None:
    layout_rules = usage_rules.get("layout_requirements", {}).get(layout_id, {})
    if not layout_rules:
        return None

    if layout_rules.get("disallow_chart_policy_avoid") and spec.get("chart_policy") == "avoid":
        return "chart-policy-avoid"

    minimum_numeric_count = int(layout_rules.get("minimum_numeric_count", 3))
    if layout_rules.get("require_local_numeric_signal"):
        if not _chart_metric_values_from_spec(spec, ["0"] * minimum_numeric_count):
            return "missing-local-numeric-signal"

    if layout_rules.get("require_comparison_signal"):
        comparison_exempt_roles = {"feature", "features", "best-fit"}
        if spec["role"] not in comparison_exempt_roles and not _has_comparison_signal(
            spec["claim"],
            spec["key_point"],
            spec["visual_intent"],
            *spec["supporting_facts"],
            *spec["supporting_items"],
        ):
            return "missing-comparison-signal"

    if layout_rules.get("require_progression_signal") and not _has_progression_signal(
        spec["claim"],
        spec["key_point"],
        spec["visual_intent"],
        *spec["supporting_facts"],
        *spec["supporting_items"],
    ):
        return "missing-progression-signal"

    if layout_rules.get("require_supporting_facts"):
        if not spec.get("supporting_facts") and not spec.get("evidence_items"):
            return "missing-supporting-facts"

    if layout_rules.get("require_compact_anchor"):
        claim = spec["claim"].strip() or spec["title"]
        if not (_has_compact_anchor(claim) or _has_numeric_signal(claim, spec["key_point"])):
            return "missing-compact-anchor"

    return None


def _resolve_layout_with_usage_rules(
    spec: dict[str, Any],
    layout_id: str,
    *,
    usage_rules: dict[str, Any],
    allowed_layouts: list[str],
) -> str:
    current = layout_id
    visited: set[str] = set()
    role_forbidden = usage_rules.get("role_forbidden_layouts", {}).get(spec["role"], [])

    while current not in visited:
        visited.add(current)

        if current in role_forbidden:
            fallback = usage_rules.get("layout_fallbacks", {}).get(current)
            if fallback in allowed_layouts:
                current = fallback
                continue
            break

        failure = _layout_requirement_failure(spec, current, usage_rules)
        if not failure:
            return current

        if spec.get("chart_policy") == "required" and failure == "missing-local-numeric-signal":
            raise RenderError(
                f"Slide {spec['slide_number']} requires chart-driven rendering but lacks slide-local numeric facts"
            )

        fallback = usage_rules.get("layout_requirements", {}).get(current, {}).get("fallback")
        if fallback in allowed_layouts:
            current = fallback
            continue
        break

    return current if current in allowed_layouts else allowed_layouts[0]


def build_slide_spec(brief: dict[str, Any], packet: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    packet = packet or build_render_packet(brief)
    quality_tier = packet["quality_tier"]
    preset = brief["style"]["preset"]
    role_layouts = _layout_map_for_preset(preset)
    usage_rules = _preset_usage_rules(preset)
    allowed_layouts = packet["allowed_layouts"] or DEFAULT_LAYOUTS.get(_normalize_preset_name(preset), [])
    layout_cycle = allowed_layouts or ["default"]
    if quality_tier == "tier1":
        layout_cycle = allowed_layouts[:4] or layout_cycle
    elif quality_tier == "tier2":
        preferred = [layout for layout in ("title_grid", "column_content", "contents_index", "pull_quote") if layout in allowed_layouts]
        layout_cycle = preferred or (allowed_layouts[:3] or layout_cycle)

    specs: list[dict[str, Any]] = []
    previous_layouts: list[str] = []
    evidence_usage: dict[str, int] = {}
    for index, slide in enumerate(brief["narrative"]["slides"], start=1):
        role = slide["role"]
        claim = _slide_claim(slide)
        explanation = _slide_explanation(slide)
        visual_intent = _slide_visual_intent(slide)
        preferred_layout_family = str(slide.get("preferred_layout_family") or "").strip().lower() or None
        chart_policy = str(slide.get("chart_policy") or "auto").strip().lower()
        supporting_facts = _slide_supporting_facts(slide)
        numeric_facts = _slide_numeric_facts(slide)

        preferred_layout = _preferred_layout_from_family(preferred_layout_family, usage_rules, layout_cycle)
        layout_id = preferred_layout or role_layouts.get(role)
        if layout_id not in layout_cycle:
            layout_id = _canonical_layout_for_role(role, layout_cycle, preset)
        if quality_tier == "tier0" and layout_id not in layout_cycle:
            layout_id = layout_cycle[(index - 1) % len(layout_cycle)]
        elif quality_tier == "tier2":
            layout_id = preferred_layout or role_layouts.get(role)
            if layout_id not in layout_cycle:
                layout_id = _canonical_layout_for_role(role, layout_cycle, preset)

        evidence_limit = 3 if quality_tier == "tier0" else 2
        candidate_fact_pool = _build_candidate_fact_pool(slide, brief)
        evidence = _select_relevant_evidence_items(
            {
                **slide,
                "title": claim,
                "key_point": explanation,
                "visual": visual_intent,
            },
            candidate_fact_pool,
            limit=evidence_limit,
            usage=evidence_usage,
        )
        supporting = _build_supporting_items(
            {
                **slide,
                "title": claim,
                "key_point": explanation,
            },
            evidence,
            minimum=3 if quality_tier == "tier0" else 2,
        )

        if quality_tier == "tier1":
            supporting = supporting[:2]
            evidence = evidence[:2]
        elif quality_tier == "tier2":
            supporting = supporting[:1]
            evidence = evidence[:1]

        spec = {
            "slide_number": slide["slide_number"],
            "role": role,
            "layout_id": layout_id,
            "title": slide["title"],
            "claim": claim,
            "key_point": explanation,
            "explanation": explanation,
            "supporting_items": supporting,
            "evidence_items": evidence,
            "supporting_facts": supporting_facts,
            "numeric_facts": numeric_facts,
            "speaker_note": f"{role}: {explanation}",
            "visual": visual_intent,
            "visual_intent": visual_intent,
            "preferred_layout_family": preferred_layout_family,
            "chart_policy": chart_policy,
            "quality_tier": quality_tier,
        }
        spec["layout_id"] = _resolve_layout_with_usage_rules(
            spec,
            spec["layout_id"],
            usage_rules=usage_rules,
            allowed_layouts=layout_cycle,
        )
        spec["layout_id"] = _avoid_long_layout_runs(spec["layout_id"], previous_layouts, layout_cycle)
        spec["layout_id"] = _resolve_layout_with_usage_rules(
            spec,
            spec["layout_id"],
            usage_rules=usage_rules,
            allowed_layouts=layout_cycle,
        )
        specs.append(spec)
        previous_layouts.append(spec["layout_id"])

    if _normalize_preset_name(brief["style"]["preset"]) == "enterprise dark":
        language = brief["language"]
        for index, spec in enumerate(specs):
            if _should_use_enterprise_story_dashboard(spec, preset=brief["style"]["preset"], language=language):
                spec["dashboard_mode"] = "story"
                spec["dashboard_label"] = _enterprise_role_badge(spec["role"], language)
                spec["dashboard_items"] = _build_enterprise_story_items(specs, index, language=language)
    return specs


def _extract_js_engine_blocks(*, preset: str, version: str) -> str:
    content = _read_text(REFERENCES_DIR / "js-engine.md")
    blocks = [
        block
        for language, block in _extract_fenced_blocks(content)
        if language == "javascript"
    ]
    script = "\n\n".join(blocks)
    return (
        script
        .replace("[version]", version)
        .replace("[preset-name]", preset)
    )


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _normalize_title_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _title_visual_units(text: str) -> float:
    units = 0.0
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9%&+/#._:-]*|[\u3400-\u9fff]|[^\w\s]", text)
    for token in tokens:
        if re.fullmatch(r"[\u3400-\u9fff]", token):
            units += 1.0
        elif re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9%&+/#._:-]*", token):
            units += min(max(len(token) * 0.56, 1.0), 4.2)
        else:
            units += 0.25
    return round(units, 2)


def _tokenize_title(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9%&+/#._:-]*|[\u3400-\u9fff]|[^\w\s]", text)


def _join_title_tokens(tokens: list[str]) -> str:
    closing = ".,!?;:%，。！？；：、）》〉】」』"
    opening = "([<{（《〈【「『"
    result = ""
    previous = ""
    word_pattern = r"[A-Za-z0-9][A-Za-z0-9%&+/#._:-]*"
    cjk_pattern = r"[\u3400-\u9fff]"
    for token in tokens:
        if not result:
            result = token
        elif token in closing:
            result += token
        elif previous in opening:
            result += token
        elif re.fullmatch(word_pattern, token) and re.fullmatch(word_pattern, previous):
            result += " " + token
        elif re.fullmatch(word_pattern, token) and re.fullmatch(cjk_pattern, previous):
            result += " " + token
        elif re.fullmatch(cjk_pattern, token) and re.fullmatch(word_pattern, previous):
            result += " " + token
        else:
            result += token
        previous = token
    return result.strip()


def _is_orphan_title_line(text: str) -> bool:
    compact = re.sub(r"\s+", "", text)
    if not compact:
        return True
    if re.fullmatch(r"[\u3400-\u9fff]", compact):
        return True
    if re.fullmatch(r"[A-Za-z0-9%&+/#._:-]{1,3}", compact):
        return True
    return _title_visual_units(text) < 1.25 and len(compact) <= 3


def _has_collapsed_middle_line(units: list[float]) -> bool:
    if len(units) < 3:
        return False
    for index in range(1, len(units) - 1):
        longest_adjacent = max(units[index - 1], units[index + 1])
        shortest_adjacent = min(units[index - 1], units[index + 1])
        if units[index] <= longest_adjacent * 0.58 and units[index] + 1.8 <= shortest_adjacent:
            return True
    return False


def _is_globally_unbalanced_title(units: list[float]) -> bool:
    if len(units) < 2:
        return False
    longest = max(units)
    shortest = min(units)
    if longest <= 0:
        return False
    if len(units) == 2:
        return shortest <= longest * 0.48 and (longest - shortest) >= 3.0
    return shortest <= longest * 0.42 and (longest - shortest) >= 3.2


def _title_partition_cost(lines: list[str]) -> float:
    units = [_title_visual_units(line) for line in lines]
    if not units:
        return float("inf")
    target = sum(units) / len(units)
    cost = sum((unit - target) ** 2 for unit in units)
    if any(_is_orphan_title_line(line) for line in lines):
        cost += 100.0
    if _has_collapsed_middle_line(units):
        cost += 80.0
    if _is_globally_unbalanced_title(units):
        cost += 45.0

    total_units = sum(units)
    if len(lines) == 1 and total_units > 14.5:
        cost += (total_units - 14.5) * 3.2
    if len(lines) == 2 and total_units > 23:
        cost += 10.0
    if len(lines) == 3 and total_units < 11:
        cost += 18.0

    cost += (len(lines) - 1) * 0.35
    return cost


def _balance_title_lines(text: str, max_lines: int = 3, force_balance: bool = False) -> list[str]:
    normalized = _normalize_title_text(text)
    if not normalized:
        return []
    total_units = _title_visual_units(normalized)
    if not force_balance and total_units <= 12.5:
        return [normalized]

    tokens = _tokenize_title(normalized)
    if len(tokens) <= 1:
        return [normalized]

    best_lines = [normalized]
    best_cost = _title_partition_cost(best_lines)
    if force_balance and total_units >= 12.0:
        best_cost += 25.0
    token_count = len(tokens)
    max_lines = max(1, min(max_lines, 3, token_count))

    for line_count in range(2, max_lines + 1):
        if line_count == 2:
            cut_pairs = ((index, None) for index in range(1, token_count))
        else:
            cut_pairs = (
                (first, second)
                for first in range(1, token_count - 1)
                for second in range(first + 1, token_count)
            )

        for first_cut, second_cut in cut_pairs:
            segments = [tokens[:first_cut], tokens[first_cut:]]
            if second_cut is not None:
                segments = [
                    tokens[:first_cut],
                    tokens[first_cut:second_cut],
                    tokens[second_cut:],
                ]
            lines = [_join_title_tokens(segment) for segment in segments if segment]
            cost = _title_partition_cost(lines)
            if cost < best_cost:
                best_lines = lines
                best_cost = cost

    return best_lines


def _render_title_markup(
    text: str,
    *,
    preset: str | None = None,
    layout_id: str | None = None,
    line_class: str = "title-line",
    accent_class: str | None = None,
    force_balance: bool = False,
) -> tuple[str, bool]:
    profile = resolve_title_profile(preset, layout_id=layout_id) if preset else None
    if profile and not profile_allows_explicit_line_control(profile):
        inner = _escape(_normalize_title_text(text))
        if accent_class:
            return f'<span class="{accent_class}">{inner}</span>', False
        return inner, False

    max_lines = int(profile.get("max_lines", 3)) if profile else 3
    lines = _balance_title_lines(text, max_lines=max_lines, force_balance=force_balance)
    if len(lines) <= 1:
        inner = _escape(lines[0] if lines else text)
        if accent_class:
            return f'<span class="{accent_class}">{inner}</span>', False
        return inner, False

    parts = []
    for line in lines:
        classes = [line_class]
        if accent_class:
            classes.append(accent_class)
        parts.append(f'<span class="{" ".join(classes)}">{_escape(line)}</span>')
    return "".join(parts), True


def _title_tag(
    tag: str,
    base_class: str,
    text: str,
    *,
    preset: str | None = None,
    layout_id: str | None = None,
    accent_class: str | None = None,
    force_balance: bool = False,
    extra_classes: str = "",
    extra_attrs: str = "",
) -> str:
    markup, multiline = _render_title_markup(
        text,
        preset=preset,
        layout_id=layout_id,
        accent_class=accent_class,
        force_balance=force_balance,
    )
    classes = [base_class, "reveal"]
    if extra_classes:
        classes.extend(extra_classes.split())
    if multiline:
        classes.append("title-balance")
    attrs = f'class="{" ".join(classes)}"'
    if extra_attrs:
        attrs += f" {extra_attrs}"
    return f"<{tag} {attrs}>{markup}</{tag}>"


def _assemble_shell_html(
    title: str,
    language: str,
    preset: str,
    css: str,
    slides_html: str,
    total: int,
) -> str:
    js_engine = _extract_js_engine_blocks(preset=preset, version=_skill_version())
    brand_mark = _brand_mark_text(title, preset)
    return f"""<!DOCTYPE html>
<html lang="{_escape(language)}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_escape(title)} - {_escape(preset)}</title>
<style>
{css}
</style>
</head>
<body data-export-progress="true" data-preset="{_escape(preset)}">
<span id="brand-mark">{_escape(brand_mark)}</span>
<div class="progress-bar"></div>
<nav class="nav-dots" aria-label="Slide navigation"></nav>
<div class="edit-hotzone"></div>
<button class="edit-toggle" id="editToggle" title="Edit mode (E)">Edit</button>
<div id="notes-panel">
    <div id="notes-panel-header">
        <div id="notes-panel-label">SPEAKER NOTES - SLIDE 1 / {total}</div>
        <div id="notes-drag-hint"></div>
        <button id="notes-collapse-btn" title="Collapse / expand">▾</button>
    </div>
    <div id="notes-body">
        <textarea id="notes-textarea" placeholder="Add speaker notes..."></textarea>
    </div>
</div>
{slides_html}
<script>
{js_engine}
</script>
</body>
</html>
"""


def _build_non_swiss_shell_css(style_contract: dict[str, Any], preset: str) -> str:
    contract_css = "\n\n".join(style_contract["css_blocks"])
    slide_background = "transparent" if preset == "Enterprise Dark" else "var(--bg-primary, var(--bg, #0f1117))"
    nav_dot_idle = "rgba(255,255,255,0.28)"
    nav_dot_active = "var(--accent-blue, var(--chart-primary, #3b82f6))"
    if preset == "Data Story":
        nav_dot_idle = "rgba(15, 23, 42, 0.22)"
        nav_dot_active = "var(--chart-primary, #2563eb)"
        slide_overlay = """
.slide::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(var(--grid-line) 1px, transparent 1px),
        linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
    background-size: clamp(40px, 6vw, 80px) clamp(40px, 6vw, 80px);
    opacity: 0.3;
    pointer-events: none;
    z-index: 0;
}
"""
    elif preset == "Enterprise Dark":
        slide_overlay = """
.slide::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(48,54,61,0.5) 1px, transparent 1px),
        linear-gradient(90deg, rgba(48,54,61,0.5) 1px, transparent 1px);
    background-size: 24px 24px;
    opacity: 0.03;
    pointer-events: none;
    z-index: 0;
}
"""
    else:
        slide_overlay = ""

    return f"""
{contract_css}

html {{
    height: 100%;
    overflow-x: hidden;
    overflow-y: auto;
    scroll-snap-type: y mandatory;
    overscroll-behavior-y: contain;
}}

body {{
    margin: 0;
    min-height: 100%;
    overflow-x: hidden;
    overflow-y: auto;
    overscroll-behavior-y: contain;
    color: var(--text-primary, var(--text, #f3f4f6));
    background: var(--bg-primary, var(--bg, #0f1117));
    --nav-dot-idle: {nav_dot_idle};
    --nav-dot-active: {nav_dot_active};
}}

*, *::before, *::after {{ box-sizing: border-box; }}

.slide {{
    width: 100vw;
    height: 100vh;
    height: 100dvh;
    overflow: hidden;
    scroll-snap-align: start;
    scroll-snap-stop: always;
    display: flex;
    flex-direction: column;
    position: relative;
    background: {slide_background};
}}

{slide_overlay}

.slide-content {{
    position: relative;
    z-index: 1;
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: clamp(10px, 1.5vw, 18px);
    padding: clamp(24px, 4vw, 52px);
    max-height: 100%;
    overflow: hidden;
}}

.title-balance {{
    display: flex;
    flex-direction: column;
    gap: 0.02em;
    text-wrap: balance;
}}

.title-line {{
    display: block;
    white-space: nowrap;
}}

#brand-mark {{
    position: fixed;
    top: 20px;
    left: 28px;
    font-weight: 800;
    font-size: 15px;
    z-index: 1000;
    color: var(--text-primary, var(--text, #f3f4f6));
    letter-spacing: 0.06em;
}}

.progress-bar {{
    position: fixed;
    top: 0;
    left: 0;
    width: 0;
    height: 4px;
    background: var(--accent-blue, var(--chart-primary, #3b82f6));
    z-index: 1000;
    transition: width 0.3s ease;
}}

.nav-dots {{ position: fixed; right: 20px; top: 50%; transform: translateY(-50%); z-index: 1000; }}

.nav-dots button {{
    width: 8px;
    height: 8px;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    background: var(--nav-dot-idle);
    transition: background 0.3s ease, transform 0.3s ease;
}}

.nav-dots button.active {{
    background: var(--nav-dot-active);
    transform: scale(1.3);
}}

.edit-hotzone {{
    position: fixed;
    top: 0;
    left: 0;
    width: 84px;
    height: 84px;
    z-index: 9998;
}}

.edit-toggle {{
    position: fixed;
    top: 18px;
    left: 18px;
    z-index: 9999;
    border: none;
    background: rgba(0, 0, 0, 0.86);
    color: #fff;
    padding: 8px 12px;
    border-radius: 999px;
    font-size: 12px;
    cursor: pointer;
    opacity: 0;
    transform: translateY(-6px);
    transition: opacity 0.2s ease, transform 0.2s ease;
}}

.edit-toggle.show,
.edit-toggle.active {{
    opacity: 1;
    transform: translateY(0);
}}

#notes-panel {{
    display: none;
    position: fixed;
    right: 18px;
    bottom: 18px;
    width: min(380px, 36vw);
    background: rgba(15, 23, 42, 0.94);
    color: #f8fafc;
    border: 1px solid rgba(148, 163, 184, 0.25);
    z-index: 9996;
    box-shadow: 0 14px 40px rgba(0, 0, 0, 0.3);
}}

#notes-panel.active {{ display: block; }}
#notes-panel.collapsed #notes-body {{ display: none; }}

#notes-panel-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 12px 14px;
    cursor: pointer;
    border-bottom: 1px solid rgba(148, 163, 184, 0.16);
}}

#notes-panel-label {{
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(226, 232, 240, 0.7);
}}

#notes-body {{ padding: 12px 14px 14px; }}

#notes-textarea {{
    width: 100%;
    min-height: 160px;
    resize: vertical;
    border: none;
    background: transparent;
    color: inherit;
    font: inherit;
    outline: none;
}}

#notes-collapse-btn {{
    border: none;
    background: transparent;
    color: inherit;
    font-size: 16px;
    cursor: pointer;
}}

#present-btn {{
    position: fixed;
    right: 18px;
    bottom: 18px;
    z-index: 9997;
    width: 42px;
    height: 42px;
    border-radius: 999px;
    border: none;
    background: rgba(0, 0, 0, 0.86);
    color: #fff;
    cursor: pointer;
}}

#present-counter {{
    display: none;
    position: fixed;
    bottom: 18px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9997;
    font-size: 11px;
    letter-spacing: 0.12em;
    color: rgba(226, 232, 240, 0.38);
}}

body.presenting {{
    background: #000 !important;
    overflow: hidden !important;
}}

body.presenting .slide {{
    position: fixed !important;
    inset: 0;
    width: 100vw !important;
    height: 100vh !important;
    transform-origin: center center;
    scroll-snap-align: none !important;
    display: none !important;
}}

body.presenting .slide.p-on {{ display: flex !important; }}
body.presenting #present-btn {{ display: none !important; }}
body.presenting #present-counter {{ display: block; }}
body.presenting.presenting-black .slide {{ visibility: hidden !important; }}
body.presenting.presenting-black::after {{
    content: '';
    position: fixed;
    inset: 0;
    background: #000;
    z-index: 99999;
}}

.slide-num-label {{
    position: absolute;
    right: 28px;
    bottom: 24px;
    font-size: 11px;
    letter-spacing: 0.12em;
    color: rgba(148, 163, 184, 0.55);
    z-index: 2;
}}

.slide-credit {{
    position: absolute;
    bottom: 8px;
    right: 14px;
    font-size: 9px;
    color: rgba(148, 163, 184, 0.35);
    pointer-events: none;
    z-index: 1;
    font-family: system-ui, sans-serif;
}}

body.presenting .slide-credit {{ display: none !important; }}
""".strip()


def _extract_numbers(text: str) -> list[str]:
    return re.findall(r"\d+(?:\.\d+)?(?:\+|%|万|亿|座|年)?", text)


def _dedupe_preserve(values: list[str]) -> list[str]:
    deduped: list[str] = []
    for value in values:
        cleaned = re.sub(r"\s+", " ", value or "").strip()
        if cleaned and cleaned not in deduped:
            deduped.append(cleaned)
    return deduped


def _spec_explicit_numbers(spec: dict[str, Any]) -> list[str]:
    return _dedupe_preserve(
        _extract_numbers(
            " ".join(
                [
                    spec["title"],
                    spec.get("claim", ""),
                    spec["key_point"],
                    spec.get("visual_intent", spec.get("visual", "")),
                    *spec.get("supporting_facts", []),
                    *spec["supporting_items"],
                    *spec.get("numeric_facts", []),
                ]
            )
        )
    )


def _metric_values_from_spec(spec: dict[str, Any], fallback: list[str]) -> list[str]:
    values = _spec_explicit_numbers(spec)
    if not values:
        values = _dedupe_preserve(_extract_numbers(" ".join(spec["evidence_items"])))
    deduped: list[str] = []
    for value in values:
        if value not in deduped:
            deduped.append(value)
    if deduped:
        while len(deduped) < len(fallback):
            deduped.append(deduped[-1])
    else:
        while len(deduped) < len(fallback):
            deduped.append(fallback[len(deduped)])
    return deduped[: len(fallback)]


def _chart_metric_values_from_spec(
    spec: dict[str, Any],
    fallback: list[str],
    *,
    allow_evidence_fill: bool = False,
) -> list[str]:
    values = _dedupe_preserve(
        [
            *_extract_numbers(" ".join(spec.get("numeric_facts", []))),
            *_extract_numbers(
                " ".join(
                    [
                        spec["title"],
                        spec.get("claim", ""),
                        spec["key_point"],
                        spec.get("visual_intent", spec.get("visual", "")),
                        *spec.get("supporting_facts", []),
                        *spec["supporting_items"],
                    ]
                )
            ),
        ]
    )
    if allow_evidence_fill and len(values) < len(fallback):
        for value in _dedupe_preserve(_extract_numbers(" ".join(spec["evidence_items"]))):
            if value not in values:
                values.append(value)

    if len(values) < len(fallback):
        return []

    trimmed = values[: len(fallback)]
    distinct_numeric = {
        _numeric_value(value)
        for value in trimmed
        if _numeric_value(value) > 0
    }
    if len(trimmed) > 1 and len(distinct_numeric) < 2:
        return []
    return trimmed

def _numeric_value(value: str) -> float:
    match = re.search(r"\d+(?:\.\d+)?", value or "")
    return float(match.group(0)) if match else 0.0


GENERIC_DISPLAY_TOKENS = {
    "AI",
    "组织",
    "企业",
    "公司",
    "系统",
    "平台",
    "能力",
    "工作",
    "管理",
    "团队",
    "客户",
    "节点",
}

BAD_DISPLAY_SUFFIX_CHARS = set("不的了和与及会将在中里上下")

DISPLAY_KEYWORDS: list[tuple[str, str]] = [
    ("90/9/1", "90/9/1"),
    ("TOIS", "TOIS"),
    ("L1-L4", "L1-L4"),
    ("ERP", "ERP"),
    ("IM", "IM"),
    ("Workspace", "Workspace"),
    ("小K", "小K"),
    ("流体化", "流体化"),
    ("相变", "相变"),
    ("科层制", "科层制"),
    ("核心竞争力", "竞争力"),
    ("认知力", "认知力"),
    ("敏捷力", "敏捷力"),
    ("乘法关系", "乘法"),
    ("活化能", "活化能"),
    ("摩擦力", "摩擦"),
    ("中层", "中层"),
    ("质量", "质量"),
    ("信任", "信任"),
    ("边界", "边界"),
    ("骨架", "骨架"),
    ("循环系统", "循环"),
    ("上下文", "上下文"),
    ("能力库", "能力库"),
    ("价值信号", "价值"),
]


def _cleanup_display_candidate(text: str) -> str:
    candidate = re.sub(r"\s+", "", text or "").strip("，。；、,;:：/+-（）()【】[]“”\"' ")
    if not candidate:
        return ""

    cleanup_patterns = [
        r"^(?:AI原生组织的|AI原生企业的|AI原生组织|AI原生企业|AI原生|AI)",
        r"^(?:组织的|企业的|公司的|团队的|客户的|管理的|工作的|文章的)",
        r"^(?:真正的|新的|现有的|过去的|当前的|历史性的|这种|这个|这次|一次|一个)",
    ]
    changed = True
    while changed and candidate:
        changed = False
        for pattern in cleanup_patterns:
            updated = re.sub(pattern, "", candidate)
            if updated != candidate and len(updated) >= 2:
                candidate = updated
                changed = True
        candidate = candidate.lstrip("的")

    if len(candidate) > 8 and re.search(r"[\u4e00-\u9fff]", candidate):
        for phrase, token in DISPLAY_KEYWORDS:
            if phrase in candidate:
                return token

    if len(candidate) > 6 and re.search(r"[\u4e00-\u9fff]", candidate):
        shortened = candidate[:4]
        if shortened and shortened[-1] not in BAD_DISPLAY_SUFFIX_CHARS:
            return shortened
        return ""
    return candidate


def _is_bad_display_token(token: str, source_text: str) -> bool:
    if not token:
        return True
    if token in GENERIC_DISPLAY_TOKENS and len(re.sub(r"\s+", "", source_text or "")) > len(token) + 2:
        return True
    if "而是" in (source_text or "") and any(verb in token for verb in ("改变", "优化", "升级", "重写", "重构", "新增")):
        return True
    if len(token) >= 2 and token[-1] in BAD_DISPLAY_SUFFIX_CHARS:
        return True
    if token.upper() == "AI" and len(re.sub(r"\s+", "", source_text or "")) > 4:
        return True
    return False


def _compact_display_candidates(text: str, *, fallback: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    if not cleaned:
        return [fallback]

    candidates: list[str] = []

    def _add(raw: str | None) -> None:
        token = _cleanup_display_candidate(raw or "")
        if token and token not in candidates:
            candidates.append(token)

    if "90/9/1" in cleaned:
        _add("90/9/1")

    semantic_pairs = [
        (r"\bTOIS\b", "TOIS"),
        (r"L1-L4", "L1-L4"),
        (r"\bERP\b", "ERP"),
        (r"\bIM\b", "IM"),
        (r"Workspace", "Workspace"),
        (r"小\s*K|小K", "小K"),
    ]
    for pattern, token in semantic_pairs:
        if re.search(pattern, cleaned, re.IGNORECASE):
            _add(token)

    lhs_match = re.match(r"^\s*([^，。；、,;:：]{1,8}?)\s*不是", cleaned)
    if lhs_match:
        _add(lhs_match.group(1))

    rhs_match = re.search(r"(?:而是|转向|变成|成为)([^，。；、,;:：]{1,10})", cleaned)
    if rhs_match:
        _add(rhs_match.group(1))

    phrase_pairs = [
        ("唯一入口", "入口"),
        ("优先动作", "3项"),
        ("三项", "3项"),
        ("18 个月", "18月"),
        ("18个月", "18月"),
        ("容器", "容器"),
        ("发起器", "任务"),
        ("发起任务", "任务"),
        ("自动执行", "执行"),
        ("上下文", "上下文"),
        ("归位", "归位"),
        ("连通", "连通"),
        ("终局", "终局"),
    ]
    for phrase, token in phrase_pairs:
        if phrase in cleaned:
            _add(token)

    for phrase, token in DISPLAY_KEYWORDS:
        if phrase in cleaned:
            _add(token)

    direct_numbers = _extract_numbers(cleaned)
    if direct_numbers:
        _add(direct_numbers[0])

    segments = re.split(r"[，。；、,;:：/]|不是|而是|以及|并且|同时|因为|所以|如果|那么", cleaned)
    for segment in segments:
        _add(segment)

    split_candidates = re.split(r"[，。；、,;:：/+\-\s（）()【】\[\]]+", cleaned)
    filtered = [item for item in split_candidates if len(item) >= 2]
    if filtered:
        for candidate in filtered:
            _add(candidate)

    fallback_token = cleaned[:4] if re.search(r"[\u4e00-\u9fff]", cleaned) else cleaned[:8]
    _add(fallback_token)
    _add(fallback)
    return candidates


def _compact_display_token(
    text: str,
    *,
    fallback: str = "关键",
    used_tokens: set[str] | None = None,
) -> str:
    candidates = _compact_display_candidates(text, fallback=fallback)
    if not candidates:
        return fallback

    first_unique = next((token for token in candidates if not used_tokens or token not in used_tokens), candidates[0])
    for token in candidates:
        if used_tokens and token in used_tokens:
            continue
        if _is_bad_display_token(token, text):
            continue
        return token
    return first_unique


def _spec_display_items(spec: dict[str, Any], *, limit: int = 4) -> list[str]:
    items = _dedupe_preserve(
        [
            *spec["supporting_items"],
            *spec["evidence_items"],
            *_split_supporting_phrases(spec["title"], minimum=1),
        ]
    )
    if not items:
        items = [spec["key_point"]]
    while len(items) < limit:
        items.append(items[-1])
    return items[:limit]


def _spec_detail_pairs(spec: dict[str, Any], *, count: int = 4) -> list[tuple[str, str]]:
    titles = _spec_display_items(spec, limit=count)
    detail_pool = _dedupe_preserve(
        [
            *_split_supporting_phrases(spec["key_point"], minimum=1),
            spec["key_point"],
            *spec["supporting_items"],
            *spec["evidence_items"],
        ]
    )
    pairs: list[tuple[str, str]] = []
    used_bodies: set[str] = set()
    for title in titles:
        body = next(
            (
                candidate
                for candidate in detail_pool
                if candidate != title and candidate not in used_bodies
                and candidate not in titles
            ),
            next(
                (
                    candidate
                    for candidate in detail_pool
                    if candidate != title and candidate not in used_bodies
                ),
                spec["key_point"],
            ),
        )
        used_bodies.add(body)
        pairs.append((title, body))
    return pairs


def _metric_value_for_item(
    item: str,
    spec: dict[str, Any],
    *,
    index: int = 0,
    used_tokens: set[str] | None = None,
) -> str:
    direct_numbers = _extract_numbers(item)
    if direct_numbers:
        if "90/9/1" in item:
            return "90/9/1"
        return direct_numbers[0]

    compact = _compact_display_token(item, fallback=str(index + 1), used_tokens=used_tokens)
    explicit_numbers = _spec_explicit_numbers(spec)
    if compact not in {"关键", str(index + 1)}:
        return compact
    if explicit_numbers:
        return explicit_numbers[min(index, len(explicit_numbers) - 1)]
    evidence_numbers = _dedupe_preserve(_extract_numbers(" ".join(spec["evidence_items"])))
    if evidence_numbers:
        return evidence_numbers[min(index, len(evidence_numbers) - 1)]
    return compact


def _chart_labels_from_spec(spec: dict[str, Any], *, count: int = 4, family: str = "alpha") -> list[str]:
    labels = [_compact_display_token(item, fallback=f"Step{index + 1}") for index, item in enumerate(_spec_display_items(spec, limit=count))]
    if len(labels) >= count:
        return labels[:count]
    defaults = _sequence_labels(count, family=family)
    for label in defaults:
        if len(labels) == count:
            break
        if label not in labels:
            labels.append(label)
    return labels[:count]


def _has_chart_ready_numbers(spec: dict[str, Any], *, minimum: int = 3) -> bool:
    return bool(_chart_metric_values_from_spec(spec, ["0"] * minimum))


def _sequence_labels(count: int, *, family: str = "alpha") -> list[str]:
    if family == "workflow":
        base = ["Input", "Build", "Check", "Ship", "Learn", "Scale"]
    else:
        base = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta"]
    labels = base[:count]
    while len(labels) < count:
        labels.append(f"Step{len(labels) + 1}")
    return labels


def _svg_bar_chart(labels: list[str], values: list[str], *, color_class: str = "chart-bar") -> str:
    magnitudes = [_numeric_value(value) for value in values]
    max_value = max(magnitudes) if any(magnitudes) else 1
    bars = []
    for index, (label, value, magnitude) in enumerate(zip(labels, values, magnitudes), start=0):
        x = 60 + index * 70
        height = max(24, int((magnitude / max_value) * 110)) if magnitude > 0 else 24
        y = 140 - height
        bars.append(
            f'<rect x="{x}" y="{y}" width="42" height="{height}" rx="4" class="{color_class}{" secondary" if index == 1 else (" tertiary" if index == 2 else "")}"></rect>'
            f'<text x="{x + 21}" y="158" text-anchor="middle" class="chart-label">{_escape(label)}</text>'
            f'<text x="{x + 21}" y="{y - 8}" text-anchor="middle" class="chart-val">{value}</text>'
        )
    return (
        '<svg viewBox="0 0 320 170" class="ds-chart-svg" role="img" aria-label="bar chart">'
        '<line x1="40" y1="20" x2="40" y2="140" class="chart-axis"></line>'
        '<line x1="40" y1="140" x2="300" y2="140" class="chart-axis"></line>'
        '<line x1="40" y1="40" x2="300" y2="40" class="chart-grid"></line>'
        '<line x1="40" y1="90" x2="300" y2="90" class="chart-grid"></line>'
        + "".join(bars)
        + "</svg>"
    )


def _svg_line_chart(labels: list[str], values: list[str]) -> str:
    magnitudes = [_numeric_value(value) for value in values]
    max_value = max(magnitudes) if any(magnitudes) else 1
    points = []
    labels_html = []
    for index, (label, value, magnitude) in enumerate(zip(labels, values, magnitudes), start=0):
        x = 50 + index * 60
        y = 135 - int((magnitude / max_value) * 90) if magnitude > 0 else 135
        points.append(f"{x},{y}")
        labels_html.append(
            f'<circle cx="{x}" cy="{y}" r="4" class="ds-dot"></circle>'
            f'<text x="{x}" y="156" text-anchor="middle" class="chart-label">{_escape(label)}</text>'
            f'<text x="{x}" y="{y - 10}" text-anchor="middle" class="chart-val">{value}</text>'
        )
    point_string = " ".join(points)
    return (
        '<svg viewBox="0 0 320 170" class="ds-chart-svg" role="img" aria-label="line chart">'
        '<line x1="36" y1="18" x2="36" y2="140" class="chart-axis"></line>'
        '<line x1="36" y1="140" x2="294" y2="140" class="chart-axis"></line>'
        '<line x1="36" y1="50" x2="294" y2="50" class="chart-grid"></line>'
        '<line x1="36" y1="95" x2="294" y2="95" class="chart-grid"></line>'
        f'<polyline points="{point_string}" class="chart-line"></polyline>'
        + "".join(labels_html)
        + "</svg>"
    )


def _render_swiss_title_grid(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("h1", "swiss-title", spec["title"], preset="Swiss Modern", layout_id=spec["layout_id"])
    hero_stats = ""
    stat_items = spec["evidence_items"][:3] or spec["supporting_items"][:3]
    if stat_items:
        stat_blocks = []
        used_tokens: set[str] = set()
        for index, item in enumerate(stat_items, start=1):
            stat_value = _metric_value_for_item(item, spec, index=index - 1, used_tokens=used_tokens)
            used_tokens.add(stat_value)
            stat_blocks.append(
                f"""
                <div class="hero-stat reveal">
                    <div class="hero-stat-num">{_escape(stat_value)}</div>
                    <div class="hero-stat-label">{_escape(item)}</div>
                </div>
                """
            )
        hero_stats = f'<div class="hero-stats">{"".join(stat_blocks)}</div>'
    return f"""
    <section class="slide title_grid" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="title_grid">
        <div class="bg-num reveal">{slide_number:02d}</div>
        <div class="slide-content content">
            <div class="eyebrow swiss-label reveal">{_escape(spec['role'])}</div>
            <div class="hero-rule reveal"></div>
            {title_tag}
            <p class="swiss-body hero-sub reveal">{_escape(spec['key_point'])}</p>
            {hero_stats}
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_swiss_column_content(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("h2", "swiss-title", spec["title"], preset="Swiss Modern", layout_id=spec["layout_id"])
    pairs = _spec_detail_pairs(spec, count=3)
    items = "".join(
        f"""
        <div class="pain-item{' accent-border' if index == 0 else ''} reveal">
            <div class="pain-num">{slide_number}.{index + 1}</div>
            <div class="pain-title">{_escape(title)}</div>
            <div class="pain-desc">{_escape(body)}</div>
        </div>
        """
        for index, (title, body) in enumerate(pairs[:3])
    )
    return f"""
    <section class="slide column_content" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="column_content">
        <div class="bg-num reveal">{slide_number:02d}</div>
        <div class="left-panel">
            <div class="red-bar"></div>
            <div class="slide-content content">
                <div class="eyebrow swiss-label reveal">{_escape(spec['role'])}</div>
                {title_tag}
                <div class="left-rule reveal"></div>
                <p class="swiss-body reveal" style="color:var(--text-light);max-width:26ch;">{_escape(spec['key_point'])}</p>
            </div>
        </div>
        <div class="right-panel">
            <div class="slide-content content">
                {items}
            </div>
        </div>
        <span class="slide-num-label light">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_swiss_stat_block(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    emphasis = re.search(r"\d+(?:\.\d+)?", spec["key_point"])
    value = emphasis.group(0) if emphasis else _compact_display_token(spec["title"], fallback="入口")
    return f"""
    <section class="slide stat_block" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="stat_block">
        <div class="bg-num reveal">{slide_number:02d}</div>
        <div class="slide-content content">
            <div class="eyebrow swiss-label reveal">{_escape(spec['role'])}</div>
            <div class="stat-row reveal">
                <div>
                    <div class="swiss-stat accent">{_escape(value)}</div>
                    <div class="swiss-rule red"></div>
                </div>
                <div class="stat-divider"></div>
                <div class="stat-copy">
                    <div class="stat-label">{_escape(spec['title'])}</div>
                    <div class="stat-value">{_escape(spec['key_point'])}</div>
                </div>
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_swiss_geometric_diagram(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("h2", "swiss-title", spec["title"], preset="Swiss Modern", layout_id=spec["layout_id"])
    pairs = _spec_detail_pairs(spec, count=3)
    steps = "".join(
        f"""
        <div class="disc-step reveal">
            <div class="disc-step-num">{index + 1}</div>
            <div>
                <div class="disc-step-title">{_escape(title)}</div>
                <div class="disc-step-desc">{_escape(body)}</div>
            </div>
        </div>
        """
        for index, (title, body) in enumerate(pairs[:3])
    )
    diagram_labels = _chart_labels_from_spec(spec, count=3)
    return f"""
    <section class="slide geometric_diagram" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="geometric_diagram">
        <div class="bg-num reveal">{slide_number:02d}</div>
        <div class="slide-content content disc-header">
            <div class="eyebrow swiss-label reveal">{_escape(spec['role'])}</div>
            {title_tag}
            <div class="disc-body">
                <div class="disc-steps">
                    {steps}
                </div>
                <div class="disc-diagram reveal">
                    <svg class="diagram-svg" viewBox="0 0 320 220" role="img" aria-label="{_escape(spec['visual'])}">
                        <rect x="20" y="20" width="110" height="46" fill="none" stroke="#0a0a0a" stroke-width="1.5"></rect>
                        <rect x="190" y="20" width="110" height="46" fill="#ff3300" stroke="#0a0a0a" stroke-width="1.5"></rect>
                        <rect x="105" y="144" width="110" height="46" fill="none" stroke="#0a0a0a" stroke-width="1.5"></rect>
                        <line x1="130" y1="43" x2="190" y2="43" stroke="#0a0a0a" stroke-width="1.5"></line>
                        <line x1="245" y1="66" x2="160" y2="144" stroke="#0a0a0a" stroke-width="1.5"></line>
                        <line x1="75" y1="66" x2="160" y2="144" stroke="#0a0a0a" stroke-width="1.5"></line>
                        <text x="34" y="47" font-size="12" fill="#0a0a0a">{_escape(diagram_labels[0])}</text>
                        <text x="204" y="47" font-size="12" fill="#ffffff">{_escape(diagram_labels[1])}</text>
                        <text x="124" y="171" font-size="12" fill="#0a0a0a">{_escape(diagram_labels[2])}</text>
                    </svg>
                </div>
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_swiss_data_table(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("h2", "swiss-title", spec["title"], preset="Swiss Modern", layout_id=spec["layout_id"])
    pairs = _spec_detail_pairs(spec, count=3)
    rows = []
    for index, (item, body) in enumerate(pairs[:3]):
        highlight = " class=\"highlight\"" if index == 0 else ""
        rows.append(
            f"<tr{highlight}><td>{_escape(item)}</td><td>{_escape(body)}</td><td>{_escape(_compact_display_token(item, fallback=spec['role']))}</td></tr>"
        )
    rows_html = "\n".join(rows)
    return f"""
    <section class="slide data_table" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="data_table">
        <div class="bg-num reveal">{slide_number:02d}</div>
        <div class="slide-content content">
            <div class="eyebrow swiss-label reveal">{_escape(spec['role'])}</div>
            {title_tag}
            <table class="data-table reveal">
                <thead>
                    <tr><th>Signal</th><th>Meaning</th><th>Focus</th></tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_swiss_pull_quote(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    quote = spec["key_point"]
    if len(quote) > 88:
        quote = quote[:85].rstrip() + "..."
    quote_tag = _title_tag(
        "h2",
        "swiss-title",
        quote,
        preset="Swiss Modern",
        layout_id=spec["layout_id"],
        extra_attrs='style="max-width:18ch;"',
    )
    return f"""
    <section class="slide pull_quote" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="pull_quote">
        <div class="bg-num reveal">{slide_number:02d}</div>
        <div class="slide-content content" style="align-items:flex-start;justify-content:flex-start;padding-top:18vh;">
            <div class="eyebrow swiss-label reveal">{_escape(spec['role'])}</div>
            {quote_tag}
            <div class="swiss-rule red reveal" style="width:120px;margin:18px 0 10px;"></div>
            <p class="swiss-body reveal">{_escape(spec['title'])}</p>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_swiss_contents_index(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("h2", "swiss-title", spec["title"], preset="Swiss Modern", layout_id=spec["layout_id"])
    pairs = _spec_detail_pairs(spec, count=3)
    items = "".join(
        f"""
        <li class="index-item reveal">
            <div class="index-num">{index + 1}</div>
            <div>
                <div class="index-title">{_escape(title)}</div>
                <div class="index-desc">{_escape(body)}</div>
            </div>
        </li>
        """
        for index, (title, body) in enumerate(pairs[:3])
    )
    return f"""
    <section class="slide contents_index" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="contents_index">
        <div class="bg-num reveal">{slide_number:02d}</div>
        <div class="slide-content content">
            <div class="eyebrow swiss-label reveal">{_escape(spec['role'])}</div>
            {title_tag}
            <ul style="list-style:none;display:grid;gap:14px;padding:0;margin:0;">{items}</ul>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_swiss_slide(spec: dict[str, Any], total: int) -> str:
    layout_id = spec["layout_id"]
    if layout_id == "title_grid":
        return _render_swiss_title_grid(spec, total)
    if layout_id == "column_content":
        return _render_swiss_column_content(spec, total)
    if layout_id == "stat_block":
        return _render_swiss_stat_block(spec, total)
    if layout_id == "geometric_diagram":
        return _render_swiss_geometric_diagram(spec, total)
    if layout_id == "data_table":
        return _render_swiss_data_table(spec, total)
    if layout_id == "pull_quote":
        return _render_swiss_pull_quote(spec, total)
    return _render_swiss_contents_index(spec, total)


def _build_swiss_shell_css(style_contract: dict[str, Any]) -> str:
    contract_css = "\n\n".join(style_contract["css_blocks"])
    return f"""
{contract_css}

.swiss-body {{
    font-size: clamp(14px, 1.75vw, 18px);
    line-height: 1.62;
}}

.pain-desc,
.stat-value,
.disc-step-desc,
.index-desc {{
    font-size: clamp(14px, 1.7vw, 18px);
    line-height: 1.62;
}}

.pain-title,
.disc-step-title,
.index-title,
.stat-label,
.data-table td,
.data-table th {{
    font-size: clamp(14px, 1.6vw, 17px);
}}

.pain-item {{
    padding-left: clamp(14px, 2.2vw, 24px);
}}

html {{
    height: 100%;
    overflow-x: hidden;
    scroll-snap-type: y mandatory;
}}

body {{
    margin: 0;
    min-height: 100%;
    overflow-x: hidden;
    background: var(--bg);
    color: var(--text);
    --nav-dot-idle: rgba(10, 10, 10, 0.18);
    --nav-dot-active: var(--red);
}}

*, *::before, *::after {{ box-sizing: border-box; }}

body::before {{
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(0,0,0,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,0,0,0.03) 1px, transparent 1px);
    background-size: calc(100vw / 12) 100vh;
    pointer-events: none;
    z-index: 0;
}}

.slide {{
    width: 100vw;
    height: 100vh;
    height: 100dvh;
    overflow: hidden;
    scroll-snap-align: start;
    display: flex;
    position: relative;
    background: #ffffff;
}}

.slide-content {{
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: clamp(10px, 1.5vw, 18px);
    max-height: 100%;
    overflow: hidden;
    padding: var(--slide-padding, clamp(1rem, 4vw, 4rem));
}}

.title-balance {{
    display: flex;
    flex-direction: column;
    gap: 0.02em;
    text-wrap: balance;
}}

.title-line {{
    display: block;
    white-space: nowrap;
}}

#brand-mark {{
    position: fixed;
    top: 20px;
    left: 28px;
    font-family: "Archivo Black", sans-serif;
    font-size: 15px;
    font-weight: 900;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--text);
    z-index: 1000;
}}

.progress-bar {{
    position: fixed;
    top: 0;
    left: 0;
    width: 0;
    height: 4px;
    background: var(--red);
    z-index: 1000;
    transition: width 0.3s ease;
}}

.nav-dots {{ position: fixed; right: 22px; top: 50%; transform: translateY(-50%); z-index: 1000; }}

.nav-dots button {{
    width: 8px;
    height: 8px;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    background: var(--nav-dot-idle);
    transition: background 0.3s ease, transform 0.3s ease;
}}

.nav-dots button.active {{
    background: var(--nav-dot-active);
    transform: scale(1.3);
}}

.bg-num {{
    position: absolute;
    right: clamp(2rem, 5vw, 5rem);
    top: 0;
    font-family: "Archivo Black", sans-serif;
    font-weight: 900;
    font-size: clamp(8rem, 25vw, 18rem);
    color: #f0f0f0;
    line-height: 0.85;
    pointer-events: none;
    user-select: none;
    z-index: 0;
}}

.slide-num-label {{
    position: absolute;
    top: 28px;
    right: 28px;
    font-family: "Archivo Black", sans-serif;
    font-size: 11px;
    font-weight: 900;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(0, 0, 0, 0.18);
    z-index: 2;
}}

.slide-num-label.light {{
    color: rgba(255, 255, 255, 0.28);
}}

.edit-hotzone {{
    position: fixed;
    top: 0;
    left: 0;
    width: 84px;
    height: 84px;
    z-index: 9998;
}}

.edit-toggle {{
    position: fixed;
    top: 18px;
    left: 18px;
    z-index: 9999;
    border: none;
    background: rgba(0, 0, 0, 0.86);
    color: #fff;
    padding: 8px 12px;
    border-radius: 999px;
    font-size: 12px;
    cursor: pointer;
    opacity: 0;
    transform: translateY(-6px);
    transition: opacity 0.2s ease, transform 0.2s ease;
}}

.edit-toggle.show,
.edit-toggle.active {{
    opacity: 1;
    transform: translateY(0);
}}

#notes-panel {{
    display: none;
    position: fixed;
    right: 18px;
    bottom: 18px;
    width: min(380px, 36vw);
    background: rgba(255, 255, 255, 0.96);
    border: 1px solid rgba(0, 0, 0, 0.12);
    z-index: 9996;
    box-shadow: 0 14px 40px rgba(0, 0, 0, 0.12);
}}

#notes-panel.active {{ display: block; }}
#notes-panel.collapsed #notes-body {{ display: none; }}

#notes-panel-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 12px 14px;
    cursor: pointer;
    border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}}

#notes-panel-label {{
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #555;
}}

#notes-body {{
    padding: 12px 14px 14px;
}}

#notes-textarea {{
    width: 100%;
    min-height: 160px;
    resize: vertical;
    border: none;
    background: transparent;
    font: inherit;
    color: #111;
    outline: none;
}}

#notes-collapse-btn {{
    border: none;
    background: transparent;
    font-size: 16px;
    cursor: pointer;
}}

#present-btn {{
    position: fixed;
    right: 18px;
    bottom: 18px;
    z-index: 9997;
    width: 42px;
    height: 42px;
    border-radius: 999px;
    border: none;
    background: rgba(0, 0, 0, 0.86);
    color: #fff;
    cursor: pointer;
}}

#present-counter {{
    display: none;
    position: fixed;
    bottom: 18px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9997;
    font-size: 11px;
    letter-spacing: 0.12em;
    color: rgba(0, 0, 0, 0.35);
}}

body.presenting {{
    background: #000 !important;
    overflow: hidden !important;
}}

body.presenting .slide {{
    position: fixed !important;
    inset: 0;
    width: 100vw !important;
    height: 100vh !important;
    transform-origin: center center;
    scroll-snap-align: none !important;
    display: none !important;
}}

body.presenting .slide.p-on {{ display: flex !important; }}
body.presenting #present-btn {{ display: none !important; }}
body.presenting #present-counter {{ display: block; }}
body.presenting.presenting-black .slide {{ visibility: hidden !important; }}
body.presenting.presenting-black::after {{
    content: '';
    position: fixed;
    inset: 0;
    background: #000;
    z-index: 99999;
}}

.slide-credit {{
    position: absolute;
    bottom: 8px;
    right: 14px;
    font-size: 9px;
    color: rgba(0, 0, 0, 0.35);
    pointer-events: none;
    z-index: 1;
    font-family: system-ui, sans-serif;
}}

body.presenting .slide-credit {{ display: none !important; }}
""".strip()


def render_swiss_modern_html(
    brief: dict[str, Any],
    *,
    packet: dict[str, Any] | None = None,
    style_contract: dict[str, Any] | None = None,
) -> str:
    packet = packet or build_render_packet(brief)
    style_contract = style_contract or compile_style_contract("Swiss Modern")
    if brief["style"]["preset"] != "Swiss Modern":
        raise RenderError("Swiss renderer only accepts Swiss Modern briefs")

    specs = build_slide_spec(brief, packet=packet)
    total = len(specs)
    slides_html = "\n\n".join(_render_swiss_slide(spec, total) for spec in specs)
    css = _build_swiss_shell_css(style_contract)
    js_engine = _extract_js_engine_blocks(preset="Swiss Modern", version=_skill_version())
    language = brief["language"]
    brand_mark = _brand_mark_text(brief["title"], "Swiss Modern")

    return f"""<!DOCTYPE html>
<html lang="{_escape(language)}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_escape(brief['title'])} - Swiss Modern</title>
<style>
{css}
</style>
</head>
<body data-export-progress="true" data-preset="Swiss Modern">
<span id="brand-mark">{_escape(brand_mark)}</span>
<div class="progress-bar"></div>
<nav class="nav-dots" aria-label="Slide navigation"></nav>
<div class="edit-hotzone"></div>
<button class="edit-toggle" id="editToggle" title="Edit mode (E)">Edit</button>
<div id="notes-panel">
    <div id="notes-panel-header">
        <div id="notes-panel-label">SPEAKER NOTES - SLIDE 1 / {total}</div>
        <div id="notes-drag-hint"></div>
        <button id="notes-collapse-btn" title="Collapse / expand">▾</button>
    </div>
    <div id="notes-body">
        <textarea id="notes-textarea" placeholder="Add speaker notes..."></textarea>
    </div>
</div>
{slides_html}
<script>
{js_engine}
</script>
</body>
</html>
"""


def _enterprise_extra_css() -> str:
    return """
#brand-mark {
    display: none;
}

.ent-shell {
    width: 100%;
    max-width: 1120px;
    margin: 0 auto;
}

.ent-hero-title {
    font-size: clamp(28px, 4.8vw, 56px);
    line-height: 1.04;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.03em;
    margin: 0;
}

.ent-kpi-meta {
    font-size: 12px;
    color: var(--text-muted);
}

.ent-dashboard-story .ent-kpi-meta {
    font-size: 14px;
    line-height: 1.6;
    color: var(--text-body);
    max-width: 62rem;
}

.ent-kpi-row.ent-kpi-row-story {
    align-items: stretch;
}

.ent-kpi-card.ent-kpi-card-story {
    gap: 14px;
    min-height: 208px;
    justify-content: flex-start;
}

.ent-kpi-story-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}

.ent-kpi-story-index {
    font-size: clamp(24px, 3vw, 36px);
    font-weight: 700;
    color: var(--accent-blue);
    line-height: 1;
    letter-spacing: -0.04em;
}

.ent-kpi-story-badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    border: 1px solid var(--border);
    border-radius: 999px;
    font-size: 11px;
    line-height: 1;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
    background: rgba(56, 139, 253, 0.08);
}

.ent-kpi-story-title {
    font-size: clamp(18px, 1.8vw, 25px);
    line-height: 1.28;
    color: var(--text-primary);
    font-weight: 620;
}

.ent-kpi-story-copy {
    margin: 0;
    font-size: clamp(13px, 1.12vw, 15px);
    line-height: 1.6;
    color: var(--text-body);
}

.ent-pull {
    max-width: 16ch;
    font-size: clamp(28px, 4vw, 52px);
    line-height: 1.08;
    color: var(--text-primary);
    letter-spacing: -0.03em;
    font-weight: 650;
}

.enterprise-split .ent-split {
    flex: 1;
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: clamp(32px, 5.4vh, 58px) clamp(34px, 3.8vw, 48px) clamp(26px, 3.8vh, 36px);
    grid-template-columns: clamp(380px, 38%, 470px) minmax(0, 1fr);
    gap: clamp(20px, 2.2vw, 30px);
    align-items: center;
}

.enterprise-split .ent-title {
    font-size: clamp(19px, 2.1vw, 28px);
    line-height: 1.14;
    max-width: 13ch;
}

.ent-split-labels {
    display: flex;
    flex-direction: column;
    gap: clamp(10px, 1.5vw, 14px);
    min-width: 0;
    justify-content: center;
}

.ent-split-panel {
    min-width: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

body[data-preset="Enterprise Dark"]::before {
    background-image:
        linear-gradient(rgba(71,85,105,0.58) 1px, transparent 1px),
        linear-gradient(90deg, rgba(71,85,105,0.58) 1px, transparent 1px);
    opacity: 0.09;
    background-size: 30px 30px;
}

body[data-preset="Enterprise Dark"] .slide::before {
    background-image:
        linear-gradient(rgba(56,139,253,0.18) 1px, transparent 1px),
        linear-gradient(90deg, rgba(56,139,253,0.10) 1px, transparent 1px);
    background-size: 30px 30px;
    opacity: 0.05;
}

.ent-arch-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 18px;
    width: 100%;
}

.ent-arch-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 18px;
}

.ent-timeline {
    position: relative;
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 20px;
    margin-top: 24px;
}

.ent-timeline::before {
    content: '';
    position: absolute;
    left: 0;
    right: 0;
    top: 15px;
    height: 1px;
    background: var(--border);
}

.ent-timeline-item {
    position: relative;
    padding-top: 28px;
}

.ent-timeline-dot {
    position: absolute;
    top: 8px;
    left: 0;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: var(--accent-blue);
    box-shadow: 0 0 0 4px rgba(56,139,253,0.14);
}

.ent-timeline-date {
    font-size: 11px;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    text-transform: uppercase;
}

.ent-timeline-copy {
    font-size: 14px;
    color: var(--text-body);
    line-height: 1.5;
}

.ent-matrix {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
}

.ent-feature-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
}

.ent-feature-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 18px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.ent-feature-card-head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
}

.ent-feature-card-copy {
    margin: 0;
    font-size: 14px;
    line-height: 1.55;
    color: var(--text-body);
}

@media (max-width: 900px) {
    .enterprise-split .ent-split,
    .ent-feature-grid,
    .ent-matrix,
    .ent-arch-grid,
    .ent-timeline {
        grid-template-columns: 1fr;
    }
}
""".strip()


def _render_enterprise_kpi_dashboard(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag(
        "h1",
        "ent-hero-title",
        spec["title"],
        preset="Enterprise Dark",
        layout_id=spec["layout_id"],
        accent_class="ent-accent-blue",
    )
    values = _metric_values_from_spec(spec, ["入口", "结构", "动作"])
    cards = []
    labels = _spec_display_items(spec, limit=3)
    used_tokens: set[str] = set()
    for index, label in enumerate(labels[:3]):
        trend_class = "positive" if index == 0 else ("neutral" if index == 1 else "negative")
        metric_value = _metric_value_for_item(label, spec, index=index, used_tokens=used_tokens) or values[index]
        used_tokens.add(metric_value)
        cards.append(
            f"""
            <div class="ent-kpi-card reveal">
                <div class="ent-kpi-number {trend_class}">{_escape(metric_value)}</div>
                <div class="ent-kpi-label">{_escape(label)}</div>
                <div class="ent-trend {'up' if index != 2 else 'down'}">{'▲' if index != 2 else '▼'} {_escape(spec['key_point'])}</div>
            </div>
            """
        )
    return f"""
    <section class="slide enterprise-dashboard" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="kpi_dashboard">
        <div class="slide-content">
            <div class="ent-shell">
                <span class="ent-label-tag reveal">AI landscape</span>
                {title_tag}
                <div class="ent-sep reveal"></div>
                <p class="ent-kpi-meta reveal">{_escape(spec['key_point'])}</p>
                <div class="ent-kpi-row">
                    {''.join(cards)}
                </div>
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_enterprise_story_dashboard(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag(
        "h1",
        "ent-hero-title",
        spec["title"],
        preset="Enterprise Dark",
        layout_id=spec["layout_id"],
        accent_class="ent-accent-blue",
    )
    story_items = spec.get("dashboard_items") or []
    cards = []
    for item in story_items[:3]:
        cards.append(
            f"""
            <div class="ent-kpi-card ent-kpi-card-story reveal">
                <div class="ent-kpi-story-top">
                    <div class="ent-kpi-story-index">{_escape(item['index'])}</div>
                    <span class="ent-kpi-story-badge">{_escape(item['badge'])}</span>
                </div>
                <div class="ent-kpi-story-title">{_escape(item['title'])}</div>
                <p class="ent-kpi-story-copy">{_escape(item['body'])}</p>
            </div>
            """
        )
    return f"""
    <section class="slide enterprise-dashboard ent-dashboard-story" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="kpi_dashboard">
        <div class="slide-content">
            <div class="ent-shell">
                <span class="ent-label-tag reveal">{_escape(spec.get('dashboard_label', spec['role']))}</span>
                {title_tag}
                <div class="ent-sep reveal"></div>
                <p class="ent-kpi-meta reveal">{_escape(spec['key_point'])}</p>
                <div class="ent-kpi-row ent-kpi-row-story">
                    {''.join(cards)}
                </div>
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_enterprise_consulting_split(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("h2", "ent-title", spec["title"], preset="Enterprise Dark", layout_id=spec["layout_id"])
    labels = "".join(f'<div class="ent-split-label">{_escape(item)}</div>' for item in _spec_display_items(spec, limit=3))
    pairs = _spec_detail_pairs(spec, count=3)
    rows = "".join(
        f"""
        <div class="ent-feature-row reveal">
            <div class="ent-feature-icon">{index + 1}</div>
            <div style="flex:1;">
                <h3 style="margin:0 0 6px;color:var(--text-primary);font-size:1rem;">{_escape(title)}</h3>
                <p style="margin:0;color:var(--text-body);font-size:0.92rem;line-height:1.5;">{_escape(body)}</p>
                <div class="ent-prog-bar" style="margin-top:10px;"><div class="ent-prog-fill" style="width:{70 - index * 15}%"></div></div>
            </div>
            <span class="ent-badge ent-badge-blue">Flow</span>
        </div>
        """
        for index, (title, body) in enumerate(pairs[:3])
    )
    return f"""
    <section class="slide enterprise-split" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="consulting_split">
        <div class="ent-split">
            <div class="ent-split-labels">
                <span class="ent-label-tag reveal">section</span>
                {title_tag}
                <div class="ent-sep reveal"></div>
                {labels}
            </div>
            <div class="ent-split-panel">
                <div class="ent-kpi-card">
                    {rows}
                </div>
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_enterprise_data_table(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("h2", "ent-title", spec["title"], preset="Enterprise Dark", layout_id=spec["layout_id"])
    rows = []
    if spec["role"] == "checkpoint":
        row_items = spec["supporting_items"][:4] or [spec["key_point"]]
        while len(row_items) < 4:
            row_items.append(spec["visual"])
        for index, item in enumerate(row_items[:4]):
            badge = "weekly" if index < 2 else "monthly"
            dot = "ent-dot-blue" if index < 2 else "ent-dot-green"
            meaning = "把 AI 使用率、模板复用率、评测通过率和场景 ROI 纳入固定治理节奏"
            rows.append(
                f"<tr><td><span class=\"ent-status-dot {dot}\"></span>{_escape(item)}</td><td>{_escape(meaning)}</td><td><span class=\"ent-badge {'ent-badge-green' if index >= 2 else 'ent-badge-blue'}\">{badge}</span></td></tr>"
            )
        headers = "<thead><tr><th>Ritual</th><th>Decision focus</th><th>Cadence</th></tr></thead>"
        label = "governance"
    else:
        for index, item in enumerate((spec["evidence_items"] or spec["supporting_items"])[:3]):
            dot = "ent-dot-green" if index == 0 else ("ent-dot-blue" if index == 1 else "ent-dot-red")
            rows.append(
                f"<tr><td><span class=\"ent-status-dot {dot}\"></span>{_escape(item)}</td><td>{_escape(spec['key_point'])}</td><td><span class=\"ent-badge {'ent-badge-green' if index == 0 else 'ent-badge-blue'}\">{_escape(spec['role'])}</span></td></tr>"
            )
        headers = "<thead><tr><th>Signal</th><th>Meaning</th><th>State</th></tr></thead>"
        label = "evidence"
    return f"""
    <section class="slide enterprise-table" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="data_table">
        <div class="slide-content">
            <div class="ent-shell">
                <span class="ent-label-tag reveal">{label}</span>
                {title_tag}
                <div class="ent-sep reveal"></div>
                <table class="ent-table reveal">
                    {headers}
                    <tbody>{''.join(rows)}</tbody>
                </table>
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_enterprise_architecture_map(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("h2", "ent-title", spec["title"], preset="Enterprise Dark", layout_id=spec["layout_id"])
    pairs = _spec_detail_pairs(spec, count=3)
    cards = "".join(
        f'<div class="ent-arch-card reveal"><div class="ent-label">{index + 1:02d}</div><h3 style="margin:6px 0;color:var(--text-primary);">{_escape(title)}</h3><p style="margin:0;color:var(--text-body);line-height:1.5;">{_escape(body)}</p></div>'
        for index, (title, body) in enumerate(pairs[:3])
    )
    return f"""
    <section class="slide enterprise-architecture" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="architecture_map">
        <div class="slide-content">
            <div class="ent-shell">
                <span class="ent-label-tag reveal">system map</span>
                {title_tag}
                <div class="ent-sep reveal"></div>
                <div class="ent-arch-grid">{cards}</div>
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_enterprise_feature_grid(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("h2", "ent-title", spec["title"], preset="Enterprise Dark", layout_id=spec["layout_id"])
    pairs = _spec_detail_pairs(spec, count=4)
    cards = []
    for index, (item, body) in enumerate(pairs[:4]):
        cards.append(
            f"""
            <div class="ent-feature-card reveal">
                <div class="ent-feature-card-head">
                    <div>
                        <div class="ent-label">{_escape(item)}</div>
                        <h3 style="margin:8px 0 0;color:var(--text-primary);">{_escape(item)}</h3>
                    </div>
                    <span class="ent-badge ent-badge-blue">AI default</span>
                </div>
                <p class="ent-feature-card-copy">{_escape(body)}</p>
                <div class="ent-prog-bar"><div class="ent-prog-fill" style="width:{78 - index * 14}%"></div></div>
            </div>
            """
        )
    return f"""
    <section class="slide enterprise-feature-grid-slide" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="comparison_matrix">
        <div class="slide-content">
            <div class="ent-shell">
                <span class="ent-label-tag reveal">translation</span>
                {title_tag}
                <div class="ent-sep reveal"></div>
                <div class="ent-feature-grid">{''.join(cards)}</div>
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_enterprise_comparison_matrix(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("h2", "ent-title", spec["title"], preset="Enterprise Dark", layout_id=spec["layout_id"])
    pairs = _spec_detail_pairs(spec, count=4)
    cells = "".join(
        f"""
        <div class="ent-kpi-card reveal">
            <div class="ent-label">{_escape(title)}</div>
            <h3 style="margin:8px 0;color:var(--text-primary);">{_escape(title)}</h3>
            <p style="margin:0;color:var(--text-body);line-height:1.5;">{_escape(body)}</p>
        </div>
        """
        for title, body in pairs[:4]
    )
    return f"""
    <section class="slide enterprise-matrix" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="comparison_matrix">
        <div class="slide-content">
            <div class="ent-shell">
                <span class="ent-label-tag reveal">comparison</span>
                {title_tag}
                <div class="ent-sep reveal"></div>
                <div class="ent-matrix">{cells}</div>
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_enterprise_insight_pull(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("div", "ent-pull", spec["title"], preset="Enterprise Dark", layout_id=spec["layout_id"])
    return f"""
    <section class="slide enterprise-pull" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="insight_pull">
        <div class="slide-content">
            <div class="ent-shell">
                <span class="ent-label-tag reveal">insight</span>
                {title_tag}
                <div class="ent-sep reveal" style="max-width:180px;"></div>
                <p style="max-width:34rem;color:var(--text-body);line-height:1.6;" class="reveal">{_escape(spec['key_point'])}</p>
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_enterprise_timeline(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("h2", "ent-title", spec["title"], preset="Enterprise Dark", layout_id=spec["layout_id"])
    explicit_numbers = _spec_explicit_numbers(spec)
    if len(explicit_numbers) >= 4:
        dates = explicit_numbers[:4]
    else:
        dates = ["现在", "样板", "协同", "切换"]
    items = []
    labels = _spec_display_items(spec, limit=4)
    while len(labels) < 4:
        labels.append(spec["key_point"])
    for idx in range(4):
        items.append(
            f"""
            <div class="ent-timeline-item reveal">
                <div class="ent-timeline-dot"></div>
                <div class="ent-timeline-date">{_escape(dates[idx])}</div>
                <div class="ent-timeline-copy">{_escape(labels[idx])}</div>
            </div>
            """
        )
    return f"""
    <section class="slide enterprise-timeline" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="timeline">
        <div class="slide-content">
            <div class="ent-shell">
                <span class="ent-label-tag reveal">timeline</span>
                {title_tag}
                <div class="ent-sep reveal"></div>
                <div class="ent-timeline">{''.join(items)}</div>
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_enterprise_cta_close(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag(
        "h2",
        "ent-hero-title",
        spec["title"],
        preset="Enterprise Dark",
        layout_id=spec["layout_id"],
        accent_class="ent-accent-blue",
    )
    items = _spec_display_items(spec, limit=3)
    used_tokens: set[str] = set()
    value0 = _metric_value_for_item(items[0], spec, index=0, used_tokens=used_tokens)
    used_tokens.add(value0)
    value1 = _metric_value_for_item(items[1], spec, index=1, used_tokens=used_tokens)
    used_tokens.add(value1)
    value2 = _metric_value_for_item(items[2], spec, index=2, used_tokens=used_tokens)
    return f"""
    <section class="slide enterprise-close" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="cta_close">
        <div class="slide-content">
            <div class="ent-shell">
                <span class="ent-label-tag reveal">close</span>
                {title_tag}
                <div class="ent-sep reveal"></div>
                <div class="ent-code reveal"><span class="green">thesis</span> = {_escape(spec['key_point'])}</div>
                <div class="ent-kpi-row" style="margin-top:18px;">
                    <div class="ent-kpi-card reveal"><div class="ent-kpi-number neutral">{_escape(value0)}</div><div class="ent-kpi-label">{_escape(items[0])}</div></div>
                    <div class="ent-kpi-card reveal"><div class="ent-kpi-number neutral">{_escape(value1)}</div><div class="ent-kpi-label">{_escape(items[1])}</div></div>
                    <div class="ent-kpi-card reveal"><div class="ent-kpi-number positive">{_escape(value2)}</div><div class="ent-kpi-label">{_escape(items[2])}</div></div>
                </div>
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_enterprise_slide(spec: dict[str, Any], total: int) -> str:
    if spec["layout_id"] == "kpi_dashboard":
        if spec.get("dashboard_mode") == "story":
            return _render_enterprise_story_dashboard(spec, total)
        return _render_enterprise_kpi_dashboard(spec, total)
    if spec["layout_id"] == "consulting_split":
        return _render_enterprise_consulting_split(spec, total)
    if spec["layout_id"] == "data_table":
        return _render_enterprise_data_table(spec, total)
    if spec["layout_id"] == "architecture_map":
        return _render_enterprise_architecture_map(spec, total)
    if spec["layout_id"] == "comparison_matrix":
        if spec["role"] == "feature":
            return _render_enterprise_feature_grid(spec, total)
        return _render_enterprise_comparison_matrix(spec, total)
    if spec["layout_id"] == "timeline":
        return _render_enterprise_timeline(spec, total)
    if spec["layout_id"] == "cta_close":
        return _render_enterprise_cta_close(spec, total)
    return _render_enterprise_insight_pull(spec, total)


def render_enterprise_dark_html(
    brief: dict[str, Any],
    *,
    packet: dict[str, Any] | None = None,
    style_contract: dict[str, Any] | None = None,
) -> str:
    packet = packet or build_render_packet(brief)
    style_contract = style_contract or compile_style_contract("Enterprise Dark")
    if brief["style"]["preset"] != "Enterprise Dark":
        raise RenderError("Enterprise renderer only accepts Enterprise Dark briefs")
    specs = build_slide_spec(brief, packet=packet)
    total = len(specs)
    slides_html = "\n\n".join(_render_enterprise_slide(spec, total) for spec in specs)
    css = _build_non_swiss_shell_css(style_contract, "Enterprise Dark") + "\n\n" + _enterprise_extra_css()
    return _assemble_shell_html(brief["title"], brief["language"], "Enterprise Dark", css, slides_html, total)


def _data_story_extra_css() -> str:
    return """
.ds-shell {
    width: 100%;
    max-width: 1120px;
    margin: 0 auto;
}

.ds-heading {
    font-size: clamp(24px, 4vw, 46px);
    line-height: 1.08;
    letter-spacing: -0.03em;
    color: var(--text);
    margin: 0;
}

.ds-subhead {
    font-size: 12px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
}

.ds-divider {
    height: 1px;
    background: var(--border);
    margin: 14px 0 18px;
}

.chart-axis { stroke: var(--axis-line); stroke-width: 1; fill: none; }
.chart-grid { stroke: var(--grid-line); stroke-width: 1; stroke-dasharray: 4 4; fill: none; }
.chart-bar { fill: var(--chart-primary); }
.chart-bar.secondary { fill: var(--chart-secondary); }
.chart-bar.tertiary { fill: var(--chart-tertiary); }
.chart-line { stroke: var(--chart-primary); stroke-width: 2.5; fill: none; stroke-linecap: round; stroke-linejoin: round; }
.chart-label, .chart-val { fill: var(--text-muted); font-size: 10px; font-family: inherit; font-variant-numeric: tabular-nums; }
.chart-val { fill: var(--text); }

.ds-chart-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 18px;
}

.ds-stage-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
}

.ds-stage-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 18px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.ds-stage-index {
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
}

.ds-stage-title {
    margin: 0;
    font-size: 1.05rem;
    line-height: 1.35;
    color: var(--text);
}

.ds-stage-copy {
    margin: 0;
    color: var(--text);
    line-height: 1.58;
}

.ds-cta-block {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 20px;
    align-items: end;
}

@media (max-width: 900px) {
    .ds-stage-grid,
    .ds-cta-block {
        grid-template-columns: 1fr;
    }
}
""".strip()


def _render_data_story_stage_grid(spec: dict[str, Any], *, count: int = 4, prefix: str = "stage") -> str:
    cards = []
    for index, (title, body) in enumerate(_spec_detail_pairs(spec, count=count), start=1):
        cards.append(
            f"""
            <div class="ds-stage-card reveal">
                <div class="ds-stage-index">{_escape(prefix)} {index:02d}</div>
                <h3 class="ds-stage-title">{_escape(title)}</h3>
                <p class="ds-stage-copy">{_escape(body)}</p>
            </div>
            """
        )
    return f'<div class="ds-stage-grid">{"".join(cards)}</div>'


def _render_data_story_hero_number(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("h1", "ds-heading", spec["title"], preset="Data Story", layout_id=spec["layout_id"])
    value = _metric_values_from_spec(spec, [_compact_display_token(spec["title"], fallback="关键")])[0]
    label = _split_supporting_phrases(spec["key_point"], minimum=1)[0]
    return f"""
    <section class="slide ds-hero-number" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="hero_number">
        <div class="slide-content ds-hero-slide">
            <div class="ds-shell">
                <div class="ds-subhead reveal">AI industry landscape</div>
                <div class="ds-kpi positive reveal">{_escape(value)}</div>
                <div class="ds-kpi-label reveal">{_escape(label)}</div>
                {title_tag}
                <p style="max-width:42rem;margin:0 auto;color:var(--text);line-height:1.6;" class="reveal">{_escape(spec['key_point'])}</p>
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_data_story_kpi_chart(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("h2", "ds-heading", spec["title"], preset="Data Story", layout_id=spec["layout_id"])
    labels = _spec_display_items(spec, limit=3)
    used_tokens: set[str] = set()
    metric_values = []
    for index, item in enumerate(labels):
        value = _metric_value_for_item(item, spec, index=index, used_tokens=used_tokens)
        used_tokens.add(value)
        metric_values.append(value)
    chart_values = _chart_metric_values_from_spec(spec, ["1", "2", "3"])
    chart = (
        _svg_bar_chart(_chart_labels_from_spec(spec, count=3), chart_values)
        if chart_values
        else _render_data_story_stage_grid(spec, count=3, prefix="metric")
    )
    cards = "".join(
        f"""
        <div class="ds-kpi-card reveal">
            <div class="ds-kpi">{_escape(metric_values[index])}</div>
            <div class="ds-kpi-label">{_escape(item)}</div>
            <div class="ds-trend {'up' if index < 2 else 'down'}">{'▲' if index < 2 else '▼'} {_escape(spec['role'])}</div>
        </div>
        """
        for index, item in enumerate(labels)
    )
    return f"""
    <section class="slide ds-kpi-chart" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="kpi_chart">
        <div class="slide-content">
            <div class="ds-shell">
                <div class="ds-subhead reveal">numbers first</div>
                {title_tag}
                <div class="ds-divider reveal"></div>
                <div class="ds-split-layout">
                    <div class="ds-kpi-grid">{cards}</div>
                    <div class="ds-chart-card reveal">{chart}</div>
                </div>
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_data_story_chart_insight(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("h2", "ds-heading", spec["title"], preset="Data Story", layout_id=spec["layout_id"])
    chart_values = _chart_metric_values_from_spec(spec, ["1", "2", "3", "4"])
    insight_body = (
        _svg_line_chart(_chart_labels_from_spec(spec, count=4), chart_values)
        if chart_values
        else _render_data_story_stage_grid(spec, count=4, prefix="evidence")
    )
    return f"""
    <section class="slide ds-chart-insight" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="chart_insight">
        <div class="slide-content">
            <div class="ds-shell">
                <div class="ds-subhead reveal">trend</div>
                {title_tag}
                <div class="ds-divider reveal"></div>
                <div class="ds-chart-card reveal">{insight_body}</div>
                <div class="ds-insight reveal"><strong>Insight:</strong> {_escape(spec['key_point'])}</div>
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_data_story_comparison_matrix(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("h2", "ds-heading", spec["title"], preset="Data Story", layout_id=spec["layout_id"])
    pairs = _spec_detail_pairs(spec, count=4)
    cells = "".join(
        f"""
        <div class="ds-matrix-cell reveal">
            <div class="ds-subhead">{_escape(title)}</div>
            <h3 style="margin:8px 0;color:var(--text);font-size:1.1rem;">{_escape(title)}</h3>
            <p style="margin:0;color:var(--text);line-height:1.5;">{_escape(body)}</p>
        </div>
        """
        for title, body in pairs[:4]
    )
    return f"""
    <section class="slide ds-comparison" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="comparison_matrix">
        <div class="slide-content">
            <div class="ds-shell">
                <div class="ds-subhead reveal">comparison</div>
                {title_tag}
                <div class="ds-divider reveal"></div>
                <div class="ds-matrix">{cells}</div>
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_data_story_kpi_grid(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("h2", "ds-heading", spec["title"], preset="Data Story", layout_id=spec["layout_id"])
    items = _spec_display_items(spec, limit=4)
    cards = []
    for index, item in enumerate(items[:4]):
        tone = "positive" if index == 0 else ("negative" if index == 2 else "neutral")
        value = _metric_value_for_item(item, spec, index=index)
        cards.append(
            f"""
            <div class="ds-kpi-card reveal">
                <div class="ds-kpi {tone}">{_escape(value)}</div>
                <div class="ds-kpi-label">{_escape(item)}</div>
                <div class="ds-trend {'up' if index != 2 else 'down'}">{'▲' if index != 2 else '▼'} {_escape(spec['role'])}</div>
            </div>
            """
        )
    return f"""
    <section class="slide ds-grid" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="kpi_grid">
        <div class="slide-content">
            <div class="ds-shell">
                <div class="ds-subhead reveal">kpi grid</div>
                {title_tag}
                <div class="ds-divider reveal"></div>
                <div class="ds-kpi-grid">{''.join(cards)}</div>
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_data_story_workflow_chart(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("h2", "ds-heading", spec["title"], preset="Data Story", layout_id=spec["layout_id"])
    chart_values = _chart_metric_values_from_spec(spec, ["1", "2", "3", "4"])
    chart = (
        _svg_line_chart(_chart_labels_from_spec(spec, count=4, family="workflow"), chart_values)
        if chart_values
        else _render_data_story_stage_grid(spec, count=4, prefix="phase")
    )
    return f"""
    <section class="slide ds-workflow" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="workflow_chart">
        <div class="slide-content">
            <div class="ds-shell">
                <div class="ds-subhead reveal">workflow</div>
                {title_tag}
                <div class="ds-divider reveal"></div>
                <div class="ds-split-layout">
                    <div class="ds-chart-card reveal">
                        <div class="ds-insight"><strong>Flow:</strong> {_escape(spec['key_point'])}</div>
                    </div>
                    <div class="ds-chart-card reveal">{chart}</div>
                </div>
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_data_story_cta_close(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag(
        "h2",
        "ds-heading",
        spec["title"],
        preset="Data Story",
        layout_id=spec["layout_id"],
        force_balance=True,
    )
    items = _spec_display_items(spec, limit=2)
    used_tokens: set[str] = set()
    value0 = _metric_value_for_item(items[0], spec, index=0, used_tokens=used_tokens)
    used_tokens.add(value0)
    value1 = _metric_value_for_item(items[1], spec, index=1, used_tokens=used_tokens)
    return f"""
    <section class="slide ds-close" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="cta_close">
        <div class="slide-content">
            <div class="ds-shell ds-cta-block">
                <div>
                    <div class="ds-subhead reveal">closing readout</div>
                    {title_tag}
                    <div class="ds-divider reveal"></div>
                    <div class="ds-insight reveal"><strong>Decision:</strong> {_escape(spec['key_point'])}</div>
                </div>
                <div class="ds-kpi-grid">
                    <div class="ds-kpi-card reveal"><div class="ds-kpi positive">{_escape(value0)}</div><div class="ds-kpi-label">{_escape(items[0])}</div></div>
                    <div class="ds-kpi-card reveal"><div class="ds-kpi neutral">{_escape(value1)}</div><div class="ds-kpi-label">{_escape(items[1])}</div></div>
                </div>
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_data_story_slide(spec: dict[str, Any], total: int) -> str:
    if spec["layout_id"] == "hero_number":
        return _render_data_story_hero_number(spec, total)
    if spec["layout_id"] == "kpi_chart":
        return _render_data_story_kpi_chart(spec, total)
    if spec["layout_id"] == "comparison_matrix":
        return _render_data_story_comparison_matrix(spec, total)
    if spec["layout_id"] == "kpi_grid":
        return _render_data_story_kpi_grid(spec, total)
    if spec["layout_id"] == "workflow_chart":
        return _render_data_story_workflow_chart(spec, total)
    if spec["layout_id"] == "cta_close":
        return _render_data_story_cta_close(spec, total)
    return _render_data_story_chart_insight(spec, total)


def render_data_story_html(
    brief: dict[str, Any],
    *,
    packet: dict[str, Any] | None = None,
    style_contract: dict[str, Any] | None = None,
) -> str:
    packet = packet or build_render_packet(brief)
    style_contract = style_contract or compile_style_contract("Data Story")
    if brief["style"]["preset"] != "Data Story":
        raise RenderError("Data Story renderer only accepts Data Story briefs")
    specs = build_slide_spec(brief, packet=packet)
    total = len(specs)
    slides_html = "\n\n".join(_render_data_story_slide(spec, total) for spec in specs)
    css = _build_non_swiss_shell_css(style_contract, "Data Story") + "\n\n" + _data_story_extra_css()
    return _assemble_shell_html(brief["title"], brief["language"], "Data Story", css, slides_html, total)


def _chinese_chan_extra_css() -> str:
    return """
#brand-mark {
    display: none;
}

body[data-preset="Chinese Chan"] {
    font-feature-settings: "palt";
}

body[data-preset="Chinese Chan"] .progress-bar {
    height: 2px;
    background: var(--accent);
}

body[data-preset="Chinese Chan"] .nav-dots button {
    width: 6px;
    height: 6px;
    border: none;
    border-radius: 50%;
    background: var(--rule);
    transition: transform 0.2s ease, background 0.2s ease;
}

body[data-preset="Chinese Chan"] .nav-dots button.active {
    background: var(--accent);
    transform: scale(1.4);
}

body[data-preset="Chinese Chan"] .slide {
    justify-content: center;
    align-items: center;
    padding: clamp(3rem, 8vw, 8rem) clamp(2rem, 6vw, 6rem);
}

body[data-preset="Chinese Chan"] .zen-content {
    width: min(100%, 600px);
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
}

body[data-preset="Chinese Chan"] .zen-center {
    align-items: center;
    text-align: center;
}

body[data-preset="Chinese Chan"] .zen-rule {
    margin: clamp(18px, 3vh, 28px) 0;
}

body[data-preset="Chinese Chan"] .zen-paragraph-stack {
    display: flex;
    flex-direction: column;
    gap: 18px;
}

body[data-preset="Chinese Chan"] .zen-list {
    margin: 0;
}

body[data-preset="Chinese Chan"] .zen-list li {
    font-size: clamp(0.9rem, 1.6vw, 1.05rem);
    font-weight: 300;
    line-height: 1.9;
    color: var(--text);
}

body[data-preset="Chinese Chan"] .zen-stat-row {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: clamp(18px, 3vw, 30px);
    margin: clamp(12px, 2vh, 18px) 0 clamp(18px, 3vh, 26px);
}

body[data-preset="Chinese Chan"] .zen-stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    text-align: center;
}

body[data-preset="Chinese Chan"] .zen-stat .num {
    font-family: "EB Garamond", "Noto Serif SC", "Noto Serif CJK SC", Georgia, serif;
    font-size: clamp(2rem, 4vw, 3.3rem);
    font-weight: 600;
    line-height: 1;
    letter-spacing: 0;
}

body[data-preset="Chinese Chan"] .zen-stat .label {
    max-width: 15ch;
    font-size: clamp(0.7rem, 1vw, 0.84rem);
    letter-spacing: 0.04em;
    line-height: 1.65;
    color: var(--text-muted);
}

body[data-preset="Chinese Chan"] .zen-vertical-shell {
    width: min(100%, 680px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: clamp(18px, 4vh, 36px);
    padding: clamp(12px, 2vh, 24px) 0;
    position: relative;
}

body[data-preset="Chinese Chan"] .zen-vertical-caption {
    position: static;
    text-align: center;
    max-width: 24rem;
}

body[data-preset="Chinese Chan"] .zen-seal {
    width: 12px;
    height: 12px;
    background: var(--accent);
    border-radius: 2px;
    position: static;
}

body[data-preset="Chinese Chan"] .slide-num-label {
    font-family: "EB Garamond", "Noto Serif SC", "Noto Serif CJK SC", Georgia, serif;
    font-size: clamp(0.65rem, 1vw, 0.8rem);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-muted);
    font-variant-numeric: proportional-nums;
}

body[data-preset="Chinese Chan"] #notes-panel {
    background: rgba(250,250,248,0.94);
    color: var(--text);
    border-color: var(--rule);
    box-shadow: none;
}

body[data-preset="Chinese Chan"] #notes-panel-label,
body[data-preset="Chinese Chan"] #notes-collapse-btn {
    color: var(--text-muted);
}

body[data-preset="Chinese Chan"] #notes-textarea {
    color: var(--text);
}

@media (max-width: 900px) {
    body[data-preset="Chinese Chan"] .zen-stat-row {
        grid-template-columns: 1fr;
    }
}
""".strip()


def _chinese_chan_caption(spec: dict[str, Any], language: str) -> str:
    if language.lower().startswith("zh"):
        return f"第 {spec['slide_number']:02d} 章"
    return f"Section {spec['slide_number']:02d}"


def _chinese_chan_copy_items(spec: dict[str, Any], *, count: int = 3) -> list[str]:
    items = _dedupe_preserve(
        [
            *spec.get("supporting_facts", []),
            *spec["supporting_items"],
            *spec["evidence_items"],
            *_split_supporting_phrases(spec["key_point"], minimum=1),
        ]
    )
    items = [item for item in items if item and item != spec["title"]]
    if not items:
        items = [spec["key_point"]]
    while len(items) < count:
        items.append(items[-1])
    return items[:count]


def _chinese_chan_metric_value(item: str, spec: dict[str, Any], *, index: int, used_tokens: set[str]) -> str:
    numeric_facts = [str(value).strip() for value in spec.get("numeric_facts", []) if str(value).strip()]
    if index < len(numeric_facts):
        return numeric_facts[index]

    value = _metric_value_for_item(item, spec, index=index, used_tokens=used_tokens)
    if not _extract_numbers(value) and re.search(r"[\u3400-\u9fff]", value):
        compact = _compact_display_token(value, fallback=value[:2], used_tokens=used_tokens)
        value = compact[:2] if len(compact) > 2 else compact
    return value


def _chinese_chan_stat_label(item: str, value: str) -> str:
    cleaned = re.sub(r"\s+", " ", item or "").strip()
    if not cleaned:
        return value

    for sep in ("：", ":"):
        if sep in cleaned:
            prefix, suffix = cleaned.split(sep, 1)
            prefix = prefix.strip()
            suffix = suffix.strip()
            if suffix and prefix == value:
                return suffix

    if value and cleaned.startswith(value):
        trimmed = cleaned[len(value) :].lstrip("：:，,；;。 ")
        if trimmed:
            return trimmed
    return cleaned


def _chinese_chan_ghost(spec: dict[str, Any]) -> str:
    anchor = _compact_display_token(spec["title"], fallback="空")
    glyph = next((char for char in anchor if re.fullmatch(r"[\u3400-\u9fff]", char)), "空")
    styles = [
        "right: -0.16em; bottom: -0.22em; opacity: 0.08;",
        "left: -0.12em; top: -0.08em; opacity: 0.08;",
    ]
    style = styles[(spec["slide_number"] - 1) % len(styles)]
    return f'<div class="zen-ghost-kanji reveal" style="{style}">{_escape(glyph)}</div>'


def _render_chinese_chan_center(spec: dict[str, Any], total: int, *, language: str) -> str:
    slide_number = spec["slide_number"]
    title_class = _title_component_for_layout("Chinese Chan", spec["layout_id"], default="zen-title")
    title_tag = _title_tag(
        "h1",
        title_class,
        spec["title"],
        preset="Chinese Chan",
        layout_id=spec["layout_id"],
        extra_classes="zen-cn",
        force_balance=True,
    )
    use_ghost = slide_number % 2 == 1
    ornament = _chinese_chan_ghost(spec) if use_ghost else ""
    separator = (
        '<div class="reveal" style="margin-top: 26px;"><div class="zen-vline"></div></div>'
        if not use_ghost else ""
    )
    return f"""
    <section class="slide" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="zen_center">
        {ornament}
        <div class="zen-content zen-center">
            <div class="zen-caption reveal">{_escape(_chinese_chan_caption(spec, language))}</div>
            {title_tag}
            <p class="zen-body zen-cn reveal" style="margin-top: 18px;">{_escape(spec['key_point'])}</p>
            {separator}
        </div>
        <span class="slide-num-label zen-caption">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_chinese_chan_split(spec: dict[str, Any], total: int, *, language: str) -> str:
    slide_number = spec["slide_number"]
    title_class = _title_component_for_layout("Chinese Chan", spec["layout_id"], default="zen-h2")
    title_tag = _title_tag(
        "h2",
        title_class,
        spec["title"],
        preset="Chinese Chan",
        layout_id=spec["layout_id"],
        extra_classes="zen-cn",
        force_balance=True,
    )
    items = _chinese_chan_copy_items(spec, count=3)
    list_html = "".join(f"<li>{_escape(item)}</li>" for item in items)
    return f"""
    <section class="slide" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="zen_split">
        <div class="zen-content">
            <span class="zen-caption reveal">{_escape(_chinese_chan_caption(spec, language))}</span>
            {title_tag}
            <div class="zen-rule reveal"><span class="zen-rule-line"></span></div>
            <div class="zen-paragraph-stack">
                <p class="zen-body zen-cn reveal">{_escape(spec['key_point'])}</p>
                <ul class="zen-list zen-body zen-cn reveal">{list_html}</ul>
            </div>
        </div>
        <span class="slide-num-label zen-caption">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_chinese_chan_stat(spec: dict[str, Any], total: int, *, language: str) -> str:
    slide_number = spec["slide_number"]
    title_class = _title_component_for_layout("Chinese Chan", spec["layout_id"], default="zen-h2")
    title_tag = _title_tag(
        "h2",
        title_class,
        spec["title"],
        preset="Chinese Chan",
        layout_id=spec["layout_id"],
        extra_classes="zen-cn",
        force_balance=True,
    )
    items = _chinese_chan_copy_items(spec, count=3)
    used_tokens: set[str] = set()
    cards = []
    for index, item in enumerate(items):
        value = _chinese_chan_metric_value(item, spec, index=index, used_tokens=used_tokens)
        used_tokens.add(value)
        label = _chinese_chan_stat_label(item, value)
        cards.append(
            f"""
            <div class="zen-stat reveal">
                <div class="num">{_escape(value)}</div>
                <div class="label">{_escape(label)}</div>
            </div>
            """
        )
    return f"""
    <section class="slide" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="zen_stat">
        <div class="zen-content">
            <span class="zen-caption reveal">{_escape(_chinese_chan_caption(spec, language))}</span>
            {title_tag}
            <div class="zen-rule reveal"><span class="zen-rule-line"></span></div>
            <div class="zen-stat-row">
                {''.join(cards)}
            </div>
            <p class="zen-body zen-cn reveal" style="text-align:center;">{_escape(spec['key_point'])}</p>
        </div>
        <span class="slide-num-label zen-caption">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_chinese_chan_vertical(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    raw_title = re.sub(r"\s+", "", spec["title"])
    title_text = spec["title"]
    if len(raw_title) > 12:
        segments = [segment.strip() for segment in re.split(r"[，。；、,:：]", spec["title"]) if segment.strip()]
        tail = next((segment for segment in reversed(segments) if 2 <= len(re.sub(r"\s+", "", segment)) <= 12), "")
        if tail:
            compact_tail = re.sub(r"^(?:是|让|把)", "", tail).strip()
            if compact_tail:
                title_text = compact_tail
    if len(re.sub(r"\s+", "", title_text)) > 12:
        title_text = _compact_display_token(title_text, fallback="答案")
    extra_attrs = ""
    if len(raw_title) > 14:
        extra_attrs = 'style="font-size: clamp(1.55rem, 4.4vw, 3.9rem); letter-spacing: 0.12em;"'
    elif len(raw_title) > 10:
        extra_attrs = 'style="font-size: clamp(1.75rem, 4.8vw, 4.4rem);"'
    title_class = _title_component_for_layout("Chinese Chan", spec["layout_id"], default="zen-vertical-title")
    title_tag = _title_tag(
        "div",
        title_class,
        title_text,
        preset="Chinese Chan",
        layout_id=spec["layout_id"],
        extra_classes="zen-cn",
        extra_attrs=extra_attrs,
    )
    return f"""
    <section class="slide" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="zen_vertical">
        <div class="zen-vertical-shell">
            {title_tag}
            <div class="zen-seal"></div>
            <div class="zen-vertical-caption">
                <p class="zen-body zen-cn reveal">{_escape(spec['key_point'])}</p>
            </div>
        </div>
        <span class="slide-num-label zen-caption">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_chinese_chan_slide(spec: dict[str, Any], total: int, *, language: str) -> str:
    if spec["layout_id"] == "zen_vertical":
        return _render_chinese_chan_vertical(spec, total)
    if spec["layout_id"] == "zen_stat":
        return _render_chinese_chan_stat(spec, total, language=language)
    if spec["layout_id"] == "zen_center":
        return _render_chinese_chan_center(spec, total, language=language)
    return _render_chinese_chan_split(spec, total, language=language)


def render_chinese_chan_html(
    brief: dict[str, Any],
    *,
    packet: dict[str, Any] | None = None,
    style_contract: dict[str, Any] | None = None,
) -> str:
    packet = packet or build_render_packet(brief)
    style_contract = style_contract or compile_style_contract("Chinese Chan")
    if brief["style"]["preset"] != "Chinese Chan":
        raise RenderError("Chinese Chan renderer only accepts Chinese Chan briefs")
    specs = build_slide_spec(brief, packet=packet)
    total = len(specs)
    slides_html = "\n\n".join(_render_chinese_chan_slide(spec, total, language=brief["language"]) for spec in specs)
    css = _build_non_swiss_shell_css(style_contract, "Chinese Chan") + "\n\n" + _chinese_chan_extra_css()
    return _assemble_shell_html(brief["title"], brief["language"], "Chinese Chan", css, slides_html, total)


def render_from_brief(brief: dict[str, Any]) -> tuple[str, dict[str, Any], dict[str, Any]]:
    packet = build_render_packet(brief)
    style_contract = compile_style_contract(brief["style"]["preset"])
    preset = brief["style"]["preset"]
    if preset == "Swiss Modern":
        html_text = render_swiss_modern_html(brief, packet=packet, style_contract=style_contract)
    elif preset == "Enterprise Dark":
        html_text = render_enterprise_dark_html(brief, packet=packet, style_contract=style_contract)
    elif preset == "Data Story":
        html_text = render_data_story_html(brief, packet=packet, style_contract=style_contract)
    elif preset == "Chinese Chan":
        html_text = render_chinese_chan_html(brief, packet=packet, style_contract=style_contract)
    else:
        raise RenderError(
            f"Deterministic low-context render is only implemented for Swiss Modern, Enterprise Dark, Data Story, and Chinese Chan right now; got {preset}"
        )
    return html_text, packet, style_contract


def render_from_context_text(text: str) -> tuple[dict[str, Any], str, dict[str, Any], dict[str, Any]]:
    brief = extract_brief_from_source_text(text)
    html_text, packet, style_contract = render_from_brief(brief)
    return brief, html_text, packet, style_contract


def render_from_context_path(path: str | Path) -> tuple[dict[str, Any], str, dict[str, Any], dict[str, Any]]:
    brief = extract_brief_from_source_path(path)
    html_text, packet, style_contract = render_from_brief(brief)
    return brief, html_text, packet, style_contract
