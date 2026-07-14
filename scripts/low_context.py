from __future__ import annotations

import hashlib
import html
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from preset_capabilities import (
    PRESET_REFERENCE_MAP,
    canonical_preset_name as canonical_preset_display_name,
    discover_custom_themes,
    get_preset_render_capability,
    resolve_style_reference_path,
)
from preset_profile_renderer import build_preset_profile_payload, profile_auto_contrast_script
from preset_support import preset_support_tier
from title_profiles import profile_allows_explicit_line_control, resolve_title_profile


def _discover_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "references").is_dir() and (candidate / "schemas").is_dir():
            return candidate
    return here.parent


ROOT = _discover_root()
REFERENCES_DIR = ROOT / "references"
THEMES_DIR = ROOT / "themes"
BRIEF_SCHEMA_PATH = ROOT / "schemas" / "generation-brief.schema.json"
PRESET_USAGE_RULES_PATH = ROOT / "references" / "preset-usage-rules.json"

PICTORIAL_EMOJI_RE = re.compile(
    "[\U0001F300-\U0001F6FF\U0001F900-\U0001FAFF\U0001F1E0-\U0001F1FF\ufe0f]+",
    flags=re.UNICODE,
)


def _sanitize_pictorial_text(value: str) -> str:
    return PICTORIAL_EMOJI_RE.sub("", value)


def _is_custom_theme(preset: str) -> bool:
    capability = get_preset_render_capability(preset)
    return capability.renderer_strategy == "custom_theme"

DEFAULT_SHELL_MARKERS = [
    "body[data-preset]",
    "#brand-mark",
    ".progress-bar",
    ".nav-dots",
    ".edit-hotzone",
    "#editToggle",
    "#notes-panel",
]

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
    "strategy consulting": [
        "cover",
        "exec_summary",
        "scr_narrative",
        "framework_matrix",
        "waterfall_chart",
        "comparison_table",
        "pillars_mece",
        "process_timeline",
        "before_after",
        "three_things",
        "funnel",
        "quote_evidence",
        "driver_breakdown",
        "closing",
    ],
}

BLUE_SKY_ROLE_LOCKED_LAYOUTS = {
    "presets": "bento",
    "interaction": "bento",
    "use-cases": "bento",
}

SWISS_ROLE_LOCKED_LAYOUTS = {
    "baseline": "stat_block",
    "solution": "stat_block",
    "presets": "contents_index",
    "features": "data_table",
    "content-routing": "contents_index",
    "validation": "data_table",
    "proof": "data_table",
    "evidence": "data_table",
    "interaction": "data_table",
    "use-cases": "column_content",
}

BLUE_SKY_ROLE_LAYOUTS = {
    "cover": "cover",
    "hook": "cover",
    "problem": "comparison",
    "risk": "comparison",
    "baseline": "comparison",
    "definition": "comparison",
    "solution": "chapter",
    "discovery": "chapter",
    "workflow": "workflow",
    "process": "workflow",
    "checkpoint": "workflow",
    "timeline": "workflow",
    "style-discovery": "bento",
    "features": "bento",
    "feature": "bento",
    "design-philosophy": "bento",
    "presets": "bento",
    "interaction": "bento",
    "use-cases": "bento",
    "recommendation": "bento",
    "best-fit": "bento",
    "decision": "bento",
    "comparison": "comparison",
    "dual": "comparison",
    "pain-solution": "comparison",
    "output-contract": "table",
    "content-routing": "table",
    "validation": "workflow",
    "evidence": "table",
    "proof": "table",
    "metrics": "table",
    "data-proof": "table",
    "closing": "closing",
    "cta": "closing",
    "cta_close": "closing",
    "getting-started": "closing",
}

SWISS_ROLE_LAYOUTS = {
    "cover": "title_grid",
    "hook": "title_grid",
    "problem": "column_content",
    "risk": "column_content",
    "two-depths": "column_content",
    "definition": "column_content",
    "boundary": "column_content",
    "pain-solution": "column_content",
    "baseline": "stat_block",
    "principles": "contents_index",
    "workflow": "geometric_diagram",
    "design-philosophy": "contents_index",
    "style-discovery": "contents_index",
    "driver": "contents_index",
    "solution": "stat_block",
    "signals": "contents_index",
    "presets": "contents_index",
    "interaction": "data_table",
    "use-cases": "column_content",
    "feature": "data_table",
    "features": "data_table",
    "data-proof": "data_table",
    "proof": "data_table",
    "evidence": "data_table",
    "content-routing": "contents_index",
    "validation": "data_table",
    "reliability": "geometric_diagram",
    "state-machines": "geometric_diagram",
    "architecture": "geometric_diagram",
    "verification": "data_table",
    "best-fit": "contents_index",
    "decision": "contents_index",
    "tradeoff": "column_content",
    "closing": "pull_quote",
    "cta": "pull_quote",
    "cta_close": "pull_quote",
    "getting-started": "pull_quote",
    # Fix 1 v2: fill unmapped canonical roles
    "discovery": "contents_index",
    "comparison": "column_content",
    "dual": "column_content",
    "process": "geometric_diagram",
    "checkpoint": "geometric_diagram",
    "recommendation": "contents_index",
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
    "solution": "kpi_dashboard",
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
    # Fix 1 v2: fill unmapped canonical roles
    "dual": "consulting_split",
    "process": "consulting_split",
    "recommendation": "comparison_matrix",
    # Contrast split role mappings
    "before-after": "contrast_split",
    "pain-solution": "contrast_split",
    # Fix B: additional role mappings for BRIEF AI-generated roles
    "design-philosophy": "architecture_map",
    "presets": "data_table",
    "content-routing": "consulting_split",
    "validation": "data_table",
    "interaction": "comparison_matrix",
    "use-cases": "consulting_split",
    "cta_close": "cta_close",
    "getting-started": "cta_close",
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
    "feature": "kpi_chart",
    "features": "kpi_chart",
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
    # Fix 1 v2: fill unmapped canonical roles
    "dual": "kpi_grid",
    "process": "workflow_chart",
    "recommendation": "kpi_grid",
    "pain-solution": "chart_insight",
    "design-philosophy": "chart_insight",
    "presets": "comparison_matrix",
    "content-routing": "workflow_chart",
    "validation": "kpi_chart",
    "interaction": "chart_insight",
    "use-cases": "workflow_chart",
    "cta_close": "cta_close",
    "getting-started": "cta_close",
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
    # Fix 1 v2: fill unmapped canonical roles
    "features": "zen_split",
    "dual": "zen_stat",
    "process": "zen_split",
    "recommendation": "zen_split",
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

    def __init__(self, message: str, *, payload: dict[str, Any] | None = None):
        super().__init__(message)
        self.payload = payload or {}


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


def _render_capability_validation_errors(brief: Any) -> list[str]:
    if not isinstance(brief, dict):
        return []
    style = brief.get("style")
    if not isinstance(style, dict):
        return []
    preset = style.get("preset")
    if not isinstance(preset, str):
        return []

    capability = get_preset_render_capability(preset)
    if capability.can_render:
        return []

    payload = capability.render_error_payload()
    alternatives = ", ".join(payload["alternatives"])
    return [
        "brief.style.preset is not generator-ready: "
        f"code={payload['code']}; "
        f"preset={payload['preset']}; "
        f"generation_status={payload['generation_status']}; "
        f"renderer_strategy={payload['renderer_strategy']}; "
        f"reason={payload['reason']}; "
        f"alternatives={alternatives}; "
        "do_not_retry=true"
    ]


def validate_generation_brief_data(brief: Any) -> list[str]:
    """Validate BRIEF schema plus generation capability for HTML output."""
    errors = validate_brief_data(brief)
    if errors:
        return errors
    return _render_capability_validation_errors(brief)


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

    errors = validate_generation_brief_data(data)
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
    try:
        return resolve_style_reference_path(preset_or_path)
    except (FileNotFoundError, KeyError) as exc:
        raise StyleContractError(f"Unknown preset or reference path: {preset_or_path}") from exc


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

    builtin_preset = next(
        (
            key
            for key, relative_path in PRESET_REFERENCE_MAP.items()
            if (REFERENCES_DIR / relative_path).resolve() == path.resolve()
        ),
        None,
    )
    if builtin_preset:
        contract_preset = canonical_preset_display_name(builtin_preset)
    elif THEMES_DIR in path.parents:
        contract_preset = path.parent.name.replace("-", " ").title()
    else:
        contract_preset = path.stem.replace("-", " ").title().replace("Neo Retro", "Neo-Retro").replace("Dev", "Dev")

    contract = {
        "preset": contract_preset,
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
    if normalized == "blue sky":
        return BLUE_SKY_ROLE_LAYOUTS
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


def _avoid_data_story_long_layout_runs(
    spec: dict[str, Any],
    layout_id: str,
    previous_layouts: list[str],
    layout_cycle: list[str],
) -> str:
    adjusted = _avoid_long_layout_runs(layout_id, previous_layouts, layout_cycle)
    if adjusted != "hero_number" or spec["role"] in {"cover", "hook"}:
        return adjusted

    # hero_number treats the anchor as a KPI; keep text-heavy generated roles in
    # card/chart layouts when diversity rotation would otherwise promote them.
    for candidate in ("workflow_chart", "chart_insight"):
        if candidate in layout_cycle and candidate != layout_id:
            return candidate
    return layout_id


def _avoid_data_story_component_runs(
    spec: dict[str, Any],
    layout_id: str,
    previous_families: list[str],
    layout_cycle: list[str],
    previous_signatures: list[str] | None = None,
) -> str:
    family = _layout_component_family("Data Story", spec["role"], layout_id)
    repeated_pair = (
        len(previous_families) >= 2
        and previous_families[-1] == previous_families[-2]
        and previous_families[-1] == family
    )
    over_global_cap = family == "workflow" and previous_families.count(family) >= 2
    if not repeated_pair and not over_global_cap:
        return layout_id

    for candidate in ("chart_insight", "comparison_matrix", "kpi_chart", "workflow_chart", "cta_close"):
        if candidate not in layout_cycle or candidate == layout_id:
            continue
        if candidate in {"kpi_chart", "kpi_grid", "hero_number"} and not _spec_explicit_numbers(spec):
            continue
        candidate_family = _layout_component_family("Data Story", spec["role"], candidate)
        if previous_signatures is not None and len(previous_signatures) >= 2:
            candidate_signature = _data_story_visual_signature(spec, candidate)
            creates_triplet = (
                previous_signatures[-1] == previous_signatures[-2]
                and previous_signatures[-1] == candidate_signature
            )
        else:
            creates_triplet = (
                len(previous_families) >= 2
                and previous_families[-1] == previous_families[-2]
                and previous_families[-1] == candidate_family
            )
        if creates_triplet:
            continue
        if candidate_family != family:
            return candidate
    return layout_id


def _swiss_component_family(role: str, layout_id: str) -> str:
    if layout_id == "contents_index":
        if role in {"presets", "features", "feature", "recommendation", "best-fit"}:
            return "feature-grid"
        return "index"
    if layout_id == "data_table":
        if role in {"validation", "evidence", "proof"}:
            return "evidence"
        return "table"
    return {
        "title_grid": "hero",
        "column_content": "split",
        "stat_block": "stat",
        "geometric_diagram": "diagram",
        "pull_quote": "cta" if role in {"closing", "cta", "cta_close", "getting-started"} else "quote",
    }.get(layout_id, layout_id)


def _avoid_swiss_component_runs(
    spec: dict[str, Any],
    layout_id: str,
    previous_families: list[str],
    layout_cycle: list[str],
) -> str:
    family = _swiss_component_family(spec["role"], layout_id)
    if len(previous_families) < 2 or previous_families[-1] != previous_families[-2] or previous_families[-1] != family:
        return layout_id

    valid_layouts = set(DEFAULT_LAYOUTS["swiss modern"])
    for candidate in layout_cycle:
        if candidate not in valid_layouts or candidate == layout_id:
            continue
        if _swiss_component_family(spec["role"], candidate) != family:
            return candidate
    return layout_id


def _enterprise_component_family(role: str, layout_id: str) -> str:
    if layout_id == "kpi_dashboard":
        if role in {"cover", "hook"}:
            return "cover-dashboard"
        return "story-dashboard"
    if layout_id == "comparison_matrix" and role in {"feature", "features", "interaction"}:
        return "feature-grid"
    return {
        "consulting_split": "split",
        "contrast_split": "contrast",
        "data_table": "table",
        "architecture_map": "architecture",
        "comparison_matrix": "matrix",
        "insight_pull": "insight",
        "timeline": "timeline",
        "cta_close": "cta",
    }.get(layout_id, layout_id)


def _layout_component_family(preset: str, role: str, layout_id: str) -> str:
    normalized = _normalize_preset_name(preset)
    if normalized == "swiss modern":
        return _swiss_component_family(role, layout_id)
    if normalized == "enterprise dark":
        return _enterprise_component_family(role, layout_id)
    if normalized == "data story":
        if layout_id in {"kpi_chart", "kpi_grid", "hero_number"}:
            return "stat"
        if layout_id == "workflow_chart":
            return "workflow"
        if layout_id == "chart_insight":
            return "chart"
        if layout_id == "comparison_matrix":
            return "matrix"
        if layout_id == "cta_close":
            return "cta"
    if normalized == "blue sky":
        return {
            "cover": "hero",
            "chapter": "chapter",
            "comparison": "comparison",
            "workflow": "workflow",
            "table": "table",
            "bento": "bento",
            "closing": "cta",
        }.get(layout_id, layout_id)
    return layout_id


def _data_story_visual_signature(spec: dict[str, Any], layout_id: str) -> str:
    role = str(spec.get("role") or "").strip()
    family = str(spec.get("preferred_layout_family") or spec.get("visual_intent") or spec.get("visual") or "").strip().lower()
    if layout_id in {"hero_number", "kpi_chart", "kpi_grid"}:
        return "stat"
    if layout_id == "comparison_matrix":
        return "matrix"
    if layout_id == "cta_close":
        return "cta"
    if layout_id == "workflow_chart":
        if role == "workflow" or family == "timeline":
            return "workflow-timeline"
        return "workflow-flow"
    if layout_id == "chart_insight":
        if role == "interaction":
            return "interaction-panel"
        if role in {"validation", "evidence", "proof"}:
            return "evidence-ladder"
        if role == "use-cases":
            return "phase-timeline"
        if role in {"content-routing", "solution"} or family in {"three-things", "flow"}:
            return "flow-map"
        if role in {"design-philosophy", "architecture"} or family in {"architecture-map"}:
            return "signal-map"
        if role in {"pain-solution", "problem", "risk"} or family in {"comparison"}:
            return "signal-bars"
        return "signal-bars"
    return layout_id


def _avoid_component_runs(
    spec: dict[str, Any],
    layout_id: str,
    previous_families: list[str],
    layout_cycle: list[str],
    *,
    preset: str,
) -> str:
    family = _layout_component_family(preset, spec["role"], layout_id)
    if not previous_families or previous_families[-1] != family:
        return layout_id

    valid_layouts = set(layout_cycle)
    for candidate in layout_cycle:
        if candidate not in valid_layouts or candidate == layout_id:
            continue
        if _layout_component_family(preset, spec["role"], candidate) != family:
            return candidate
    return layout_id


def _semantic_layout_candidates(
    spec: dict[str, Any],
    *,
    usage_rules: dict[str, Any],
    layout_cycle: list[str],
) -> list[str]:
    family_map = usage_rules.get("layout_family_map", {})
    preferred_family = str(spec.get("preferred_layout_family") or "").strip().lower()
    visual_family = str(spec.get("visual_intent") or spec.get("visual") or "").strip().lower()
    role = str(spec.get("role") or "").strip().lower()
    facts = [str(item).strip() for item in spec.get("supporting_facts", []) if str(item).strip()]
    blob_values = [
        role,
        str(spec.get("title") or ""),
        str(spec.get("claim") or ""),
        str(spec.get("key_point") or ""),
        visual_family,
        *facts,
    ]
    blob = _semantic_blob(*blob_values)
    header_blob = _semantic_blob(
        role,
        str(spec.get("title") or ""),
        str(spec.get("claim") or ""),
        str(spec.get("key_point") or ""),
        preferred_family,
        visual_family,
    )
    identity_blob = _semantic_blob(
        role,
        str(spec.get("title") or ""),
        preferred_family,
        visual_family,
    )
    hero_signal = role in {"cover", "hook", "hero"} or preferred_family in {"hero", "cover"} or visual_family in {"hero", "cover"}
    family_key = lambda value: re.sub(r"[\s_]+", "-", str(value).strip().lower())
    has_mapped_explicit_family = any(
        family_map.get(family_key(value)) in layout_cycle
        for value in (preferred_family, visual_family)
        if value
    )
    feature_grid_signal = (
        preferred_family in {"feature-grid", "grid"}
        or visual_family in {"feature-grid", "feature grid", "grid"}
        or re.search(r"feature grid|capabilities|功能|特性", header_blob, re.IGNORECASE)
    )

    keys: list[str] = []
    if preferred_family:
        keys.append(preferred_family)
    if visual_family and visual_family != preferred_family:
        keys.append(visual_family)

    if hero_signal:
        keys.insert(0, "hero")
    if any(token in f"{role} {preferred_family} {visual_family}" for token in ("close", "closing", "cta", "getting-started")):
        keys.insert(0, "close")
    if _has_before_after_signal(*blob_values):
        keys.insert(0, "before-after")
    if _has_progression_signal(*blob_values):
        keys.append("timeline")
    if re.search(r"architecture|system|map|架构|系统|地图", blob, re.IGNORECASE):
        keys.append("architecture-map")

    structured_facts = [item for item in facts if any(sep in item for sep in (" — ", " – ", " - ", "：", ":"))]
    catalog_signal = bool(
        re.search(r"catalog|inventory|preset|matrix|目录|清单|预设|矩阵", header_blob, re.IGNORECASE)
        or (len(facts) >= 5 and not re.search(r"feature|capabilit|功能|特性", header_blob, re.IGNORECASE))
    )
    explicit_evidence_signal = (
        preferred_family in {"evidence", "table", "data", "proof"}
        or visual_family in {"evidence", "table", "data", "proof"}
        or bool(re.search(r"validation|evidence|proof|验证|校验|证据", identity_blob, re.IGNORECASE))
    )
    strong_evidence_signal = (
        explicit_evidence_signal
        or (catalog_signal and not hero_signal and not feature_grid_signal and not has_mapped_explicit_family)
    )
    evidence_signal = (
        strong_evidence_signal
        or catalog_signal
        or re.search(r"validation|validate|evidence|proof|验证|校验|证据", blob, re.IGNORECASE)
        or len(structured_facts) >= 3
    )
    if strong_evidence_signal:
        if "before-after" in keys or "close" in keys or "hero" in keys:
            keys.append("evidence")
        else:
            keys.insert(0, "evidence")
    elif evidence_signal:
        keys.append("evidence")
    if feature_grid_signal:
        keys.append("feature-grid")
    flow_signal = (
        preferred_family in {"flow", "workflow"}
        or visual_family in {"flow", "workflow"}
        or role in {"content-routing", "use-cases"}
        or re.search(r"workflow|routing|use case|流程|路由", blob, re.IGNORECASE)
    )
    if flow_signal:
        if (
            not has_mapped_explicit_family
            or preferred_family in {"three-things", "flow", "workflow"}
            or visual_family in {"three-things", "three anchors", "flow", "workflow"}
        ) and (role in {"content-routing", "use-cases"} or preferred_family in {"flow", "workflow"} or visual_family in {"flow", "workflow"}):
            keys.insert(0, "flow")
        else:
            keys.append("flow")

    candidates: list[str] = []
    for key in keys:
        normalized_key = family_key(key)
        layout = family_map.get(normalized_key)
        if layout in layout_cycle and layout not in candidates:
            candidates.append(layout)
    return candidates


def _spec_for_candidate_layout(
    spec: dict[str, Any],
    layout_id: str,
    *,
    preset: str,
    usage_rules: dict[str, Any],
    language: str,
) -> dict[str, Any]:
    candidate = {**spec, "layout_id": layout_id}
    visual_family = str(candidate.get("visual_intent") or candidate.get("visual") or "").strip().lower()
    preferred_family = str(candidate.get("preferred_layout_family") or "").strip().lower()
    if _normalize_preset_name(preset) == "enterprise dark":
        if layout_id == "kpi_dashboard" and _should_use_enterprise_story_dashboard(candidate, preset=preset, language=language):
            candidate["_skip_numeric_signal_check"] = True
        if (
            layout_id == "comparison_matrix"
            and (
                preferred_family in {"feature-grid", "grid"}
                or visual_family in {"feature-grid", "feature grid", "grid"}
                or re.search(r"feature grid|capabilities|功能|特性", _semantic_blob(candidate["role"], candidate["title"], candidate["key_point"], visual_family), re.IGNORECASE)
            )
        ):
            candidate["_skip_comparison_signal_check"] = True
    return candidate


def _choose_rhythm_layout(
    spec: dict[str, Any],
    initial_layout: str,
    *,
    preset: str,
    usage_rules: dict[str, Any],
    layout_cycle: list[str],
    previous_families: list[str],
    language: str,
) -> str:
    semantic_candidates = _semantic_layout_candidates(spec, usage_rules=usage_rules, layout_cycle=layout_cycle)
    candidates = list(semantic_candidates)
    role_specific_layout = _layout_map_for_preset(preset).get(spec["role"])
    if role_specific_layout in layout_cycle:
        candidates.append(role_specific_layout)
    if initial_layout in layout_cycle:
        candidates.append(initial_layout)
    candidates = _dedupe_preserve(candidates)
    if not candidates:
        candidates = [initial_layout]

    family_key = lambda value: re.sub(r"[\s_]+", "-", str(value).strip().lower())
    preferred_family = str(spec.get("preferred_layout_family") or "").strip().lower()
    visual_family = str(spec.get("visual_intent") or spec.get("visual") or "").strip().lower()
    has_mapped_explicit_family = any(
        usage_rules.get("layout_family_map", {}).get(family_key(value)) in layout_cycle
        for value in (preferred_family, visual_family)
        if value
    )
    initial_is_role_specific = role_specific_layout == initial_layout
    if (
        _normalize_preset_name(preset) == "blue sky"
        and role_specific_layout in layout_cycle
        and not has_mapped_explicit_family
    ):
        candidates = _dedupe_preserve([role_specific_layout, *semantic_candidates, initial_layout])
    if _normalize_preset_name(preset) == "blue sky":
        locked_layout = BLUE_SKY_ROLE_LOCKED_LAYOUTS.get(spec["role"])
        if locked_layout in layout_cycle:
            return locked_layout
    if _normalize_preset_name(preset) == "swiss modern":
        locked_layout = SWISS_ROLE_LOCKED_LAYOUTS.get(spec["role"])
        if locked_layout in layout_cycle:
            return locked_layout

    best_layout = initial_layout
    best_spec = spec
    best_score = -10_000
    for rank, candidate_layout in enumerate(candidates):
        candidate_spec = _spec_for_candidate_layout(
            spec,
            candidate_layout,
            preset=preset,
            usage_rules=usage_rules,
            language=language,
        )
        resolved = _resolve_layout_with_usage_rules(
            candidate_spec,
            candidate_layout,
            usage_rules=usage_rules,
            allowed_layouts=layout_cycle,
        )
        resolved_spec = _spec_for_candidate_layout(
            candidate_spec,
            resolved,
            preset=preset,
            usage_rules=usage_rules,
            language=language,
        )
        family = _layout_component_family(preset, spec["role"], resolved)
        score = 40 - rank * 5
        if resolved != candidate_layout:
            score -= 10
        if resolved == initial_layout and not semantic_candidates:
            score += 2
        elif candidate_layout == initial_layout and semantic_candidates and initial_layout not in semantic_candidates:
            score -= 4
        if resolved == initial_layout and initial_is_role_specific and not has_mapped_explicit_family:
            score += 10
        if previous_families and family == previous_families[-1]:
            score -= 12
        if family in previous_families[-2:]:
            score -= 3
        if score > best_score:
            best_score = score
            best_layout = resolved
            best_spec = resolved_spec

    for key in ("_skip_numeric_signal_check", "_skip_comparison_signal_check"):
        if best_spec.get(key):
            spec[key] = best_spec[key]
        else:
            spec.pop(key, None)
    return best_layout


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


def _has_before_after_signal(*values: str) -> bool:
    """Detect before/after or pain/solution contrast signals in slide content."""
    blob = _semantic_blob(*values)
    patterns = [
        r"before.*after",
        r"之前.*之后",
        r"痛点.*方案",
        r"pain.*solution",
        r"现状.*改变",
        r"before.*comparison",
        r"after.*comparison",
    ]
    return any(re.search(pattern, blob, re.IGNORECASE) for pattern in patterns)


def _has_progression_signal(*values: str) -> bool:
    blob = _semantic_blob(*values)
    patterns = [
        r"先.+再",
        r"最后",
        r"阶段",
        r"里程碑",
        r"个月",
        r"周期",
        r"逐步",
        r"today|tomorrow|next",
    ]
    return any(re.search(pattern, blob, re.IGNORECASE) for pattern in patterns)


def _has_compact_anchor(text: str) -> bool:
    compact = _compact_display_token(text, fallback="")
    return bool(compact) and len(compact) <= 6


def _safe_preset_tier(preset: str) -> str:
    try:
        return preset_support_tier(preset)
    except KeyError:
        return "custom"


def _render_capability_or_raise(preset: str):
    capability = get_preset_render_capability(preset)
    if capability.can_render:
        return capability
    payload = capability.render_error_payload()
    raise RenderError(capability.user_message, payload=payload)


def build_render_packet(
    brief: dict[str, Any],
    *,
    style_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    errors = validate_brief_data(brief)
    if errors:
        raise BriefValidationError("\n".join(errors))

    preset = brief["style"]["preset"]
    capability = _render_capability_or_raise(preset)
    style_contract = style_contract or compile_style_contract(preset)
    canonical_preset = capability.canonical_preset or style_contract["preset"]
    deck_type = brief["deck"]["deck_type"]
    page_count = brief["deck"]["page_count"]
    normalized = _normalize_preset_name(canonical_preset)
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
            capability.reference_path or style_contract["source_path"],
        ]
        required_contracts = [
            "preset-metadata",
            "shared-runtime",
            "style-signature",
            "shell-ui-markers",
        ]
        if capability.renderer_strategy == "unified_profile":
            required_contracts.append("unified-profile-renderer")

    fallback_policy = {
        "tier0": "full-preset-contract",
        "tier1": "canonical-layouts-before-fail",
        "tier2": "deterministic-scaffolds-before-fail",
    }[quality_tier]

    packet = {
        "brief_hash": _sha256_text(_canonical_json(brief)),
        "generator": "kai-slide-creator",
        "generator_version": _skill_version(),
        "render_path": _canonical_render_path(canonical_preset, capability.renderer_strategy),
        "preset": canonical_preset,
        "canonical_preset": canonical_preset,
        "reference_path": capability.reference_path or style_contract["source_path"],
        "preset_support_tier": _safe_preset_tier(preset),
        "preset_generation_status": capability.generation_status,
        "preset_recommendation_status": capability.recommendation_status,
        "renderer_strategy": capability.renderer_strategy,
        "can_render": capability.can_render,
        "can_recommend": capability.can_recommend,
        "deck_type": deck_type,
        "page_count": page_count,
        "composition_source": composition_source,
        "runtime_path": runtime_path,
        "validate_strict": "pending",
        "required_refs": required_refs,
        "required_contracts": required_contracts,
        "required_shell_markers": DEFAULT_SHELL_MARKERS,
        "style_contract_digest": style_contract["digest"],
        "allowed_layouts": style_contract["allowed_layout_ids"] or DEFAULT_LAYOUTS.get(normalized, []),
        "quality_tier": quality_tier,
        "fallback_policy": fallback_policy,
        "repair_rounds": 0,
        "repair_status": "not_needed",
        "original_failures": [],
        "final_failures": [],
        "style_signature_hash": style_contract["digest"],
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


def _canonical_render_path(preset: str, renderer_strategy: str = "native") -> str:
    normalized = _normalize_preset_name(preset)
    if renderer_strategy == "unified_profile":
        return "profile:" + re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return "blue-sky-starter-canonical" if normalized == "blue sky" else "brief-canonical"


def _html_body_provenance_attrs(packet: dict[str, Any]) -> str:
    attrs = {
        "data-generator": packet.get("generator", "kai-slide-creator"),
        "data-generator-version": packet.get("generator_version", _skill_version()),
        "data-render-path": packet.get("render_path", "brief-canonical"),
        "data-brief-hash": packet.get("brief_hash", ""),
        "data-runtime-path": packet.get("runtime_path", ""),
        "data-validate-strict": packet.get("validate_strict", "pending"),
        "data-preset-generation-status": packet.get("preset_generation_status", ""),
        "data-renderer-strategy": packet.get("renderer_strategy", ""),
    }
    attrs.update(packet.get("body_data_attrs", {}))
    return " ".join(f'{key}="{_escape(str(value))}"' for key, value in attrs.items() if value)


def stamp_validation_status(html_text: str, *, status: str) -> str:
    if not re.search(r"<body\b", html_text):
        return html_text
    if re.search(r'data-validate-strict=\"[^\"]*\"', html_text):
        return re.sub(r'data-validate-strict=\"[^\"]*\"', f'data-validate-strict="{status}"', html_text, count=1)
    return re.sub(r"<body\b", f'<body data-validate-strict="{status}"', html_text, count=1)


def _brand_mark_text(title: str, preset: str) -> str:
    normalized_title = re.sub(r"\s+", " ", title or "").strip()
    if not normalized_title:
        return preset
    prefix = re.split(r"[:：]", normalized_title, maxsplit=1)[0].strip()
    if prefix and prefix != normalized_title:
        compact_prefix = re.sub(r"\s+", "", prefix)
        prefix_limit = 18 if re.search(r"[\u3400-\u9fff]", compact_prefix) else 28
        if len(compact_prefix) <= prefix_limit:
            return prefix
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

    # Fix C: check numeric signal for kpi_dashboard
    if layout_rules.get("require_numeric_signal"):
        # Skip check if story dashboard already determined this slide should use story cards
        if not spec.get("_skip_numeric_signal_check"):
            # Check if spec has any numbers, not using _metric_values_from_spec(fallback=[])
            # which incorrectly returns empty when fallback=[]
            if not _spec_explicit_numbers(spec):
                return "missing-numeric-signal"

    minimum_numeric_count = int(layout_rules.get("minimum_numeric_count", 3))
    if layout_rules.get("require_local_numeric_signal"):
        if not _chart_metric_values_from_spec(spec, ["0"] * minimum_numeric_count):
            return "missing-local-numeric-signal"

    if layout_rules.get("require_comparison_signal"):
        comparison_exempt_roles = {
            "feature",
            "features",
            "best-fit",
            *usage_rules.get("comparison_signal_exempt_roles", []),
        }
        comparison_exempt_families = set(usage_rules.get("comparison_signal_exempt_preferred_families", []))
        preferred_family = str(spec.get("preferred_layout_family") or "").strip().lower()
        if (
            not spec.get("_skip_comparison_signal_check")
            and
            spec["role"] not in comparison_exempt_roles
            and preferred_family not in comparison_exempt_families
            and not _has_comparison_signal(
                spec["claim"],
                spec["key_point"],
                spec["visual_intent"],
                *spec["supporting_facts"],
                *spec["supporting_items"],
            )
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

    if layout_rules.get("require_before_after_signal") and not _has_before_after_signal(
        spec["role"],
        spec["claim"],
        spec["key_point"],
        spec["visual_intent"],
        *spec["supporting_facts"],
        *spec["supporting_items"],
    ):
        return "missing-before-after-signal"

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
    normalized_preset = _normalize_preset_name(preset)
    role_layouts = _layout_map_for_preset(preset)
    usage_rules = _preset_usage_rules(preset)
    allowed_layouts = packet["allowed_layouts"] or DEFAULT_LAYOUTS.get(normalized_preset, [])
    layout_cycle = allowed_layouts or ["default"]
    rhythm_scheduler_enabled = bool(usage_rules.get("layout_family_map")) and normalized_preset in {
        "blue sky",
        "swiss modern",
        "enterprise dark",
        "data story",
    }
    if normalized_preset == "blue sky":
        layout_cycle = allowed_layouts or layout_cycle
    elif quality_tier == "tier1":
        # Production presets get full layout cycle; experimental presets stay conservative
        support_tier = packet.get("preset_support_tier", "experimental")
        if support_tier == "production":
            layout_cycle = allowed_layouts or layout_cycle
        else:
            layout_cycle = allowed_layouts[:4] or layout_cycle
    elif quality_tier == "tier2":
        preferred = [layout for layout in ("title_grid", "column_content", "contents_index", "pull_quote") if layout in allowed_layouts]
        layout_cycle = preferred or (allowed_layouts[:3] or layout_cycle)

    specs: list[dict[str, Any]] = []
    previous_layouts: list[str] = []
    previous_rhythm_families: list[str] = []
    previous_data_story_signatures: list[str] = []
    previous_swiss_families: list[str] = []
    evidence_usage: dict[str, int] = {}
    for index, slide in enumerate(brief["narrative"]["slides"], start=1):
        role = slide["role"]
        claim = _sanitize_pictorial_text(_slide_claim(slide))
        explanation = _sanitize_pictorial_text(_slide_explanation(slide))
        visual_intent = _sanitize_pictorial_text(_slide_visual_intent(slide))
        preferred_layout_family = str(slide.get("preferred_layout_family") or "").strip().lower() or None
        chart_policy = str(slide.get("chart_policy") or "auto").strip().lower()
        supporting_facts = _slide_supporting_facts(slide)
        numeric_facts = _slide_numeric_facts(slide)

        preferred_layout = _preferred_layout_from_family(preferred_layout_family, usage_rules, layout_cycle)
        if normalized_preset == "data story" and role == "solution":
            preferred_layout = None
        layout_id = preferred_layout or role_layouts.get(role)
        if layout_id not in layout_cycle:
            layout_id = _canonical_layout_for_role(role, layout_cycle, preset)
        if quality_tier == "tier0" and layout_id not in layout_cycle:
            layout_id = layout_cycle[(index - 1) % len(layout_cycle)]
        elif quality_tier == "tier2":
            layout_id = preferred_layout or role_layouts.get(role)
            if layout_id not in layout_cycle:
                # For Enterprise Dark: allow role-mapped layouts from allowed_layouts
                if preset == "Enterprise Dark" and layout_id in allowed_layouts:
                    pass  # keep role-mapped layout
                else:
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
            "title": _sanitize_pictorial_text(slide["title"]),
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
        if rhythm_scheduler_enabled:
            spec["layout_id"] = _choose_rhythm_layout(
                spec,
                spec["layout_id"],
                preset=preset,
                usage_rules=usage_rules,
                layout_cycle=layout_cycle,
                previous_families=previous_rhythm_families,
                language=brief["language"],
            )
            layout_id = spec["layout_id"]
        # Fix C prerequisite: check story dashboard BEFORE layout requirement failure
        # If story dashboard triggers, skip numeric signal requirement for kpi_dashboard
        if normalized_preset == "enterprise dark" and spec["layout_id"] == "kpi_dashboard":
            if _should_use_enterprise_story_dashboard(spec, preset=preset, language=brief["language"]):
                spec["dashboard_mode"] = "story"
                spec["_skip_numeric_signal_check"] = True  # marker for _layout_requirement_failure
        if (
            normalized_preset == "enterprise dark"
            and spec["layout_id"] == "comparison_matrix"
            and role in {"feature", "features", "interaction"}
            and preferred_layout_family == "feature-grid"
        ):
            spec["_skip_comparison_signal_check"] = True

        # Detect before/after contrast signal and route to contrast_split
        if spec["layout_id"] in ("comparison_matrix", "consulting_split"):
            if _has_before_after_signal(spec["role"], spec["title"], claim, explanation, visual_intent):
                if "contrast_split" in layout_cycle:
                    spec["layout_id"] = "contrast_split"
        spec["layout_id"] = _resolve_layout_with_usage_rules(
            spec,
            spec["layout_id"],
            usage_rules=usage_rules,
            allowed_layouts=layout_cycle,
        )
        if normalized_preset == "swiss modern":
            spec["layout_id"] = _avoid_swiss_component_runs(
                spec,
                spec["layout_id"],
                previous_swiss_families,
                layout_cycle,
            )
        elif normalized_preset == "enterprise dark":
            pass
        elif normalized_preset == "data story":
            spec["layout_id"] = _avoid_data_story_long_layout_runs(spec, spec["layout_id"], previous_layouts, layout_cycle)
            spec["layout_id"] = _avoid_data_story_component_runs(
                spec,
                spec["layout_id"],
                previous_rhythm_families,
                layout_cycle,
                previous_signatures=previous_data_story_signatures,
            )
        else:
            spec["layout_id"] = _avoid_long_layout_runs(spec["layout_id"], previous_layouts, layout_cycle)
        if normalized_preset == "enterprise dark":
            spec.pop("_skip_comparison_signal_check", None)
        # Removed second _resolve_layout_with_usage_rules call to prevent overriding diversity adjustment
        # The first resolve + avoid_long_layout_runs already handles all constraints
        specs.append(spec)
        previous_layouts.append(spec["layout_id"])
        if rhythm_scheduler_enabled:
            previous_rhythm_families.append(_layout_component_family(preset, spec["role"], spec["layout_id"]))
        if normalized_preset == "data story":
            previous_data_story_signatures.append(_data_story_visual_signature(spec, spec["layout_id"]))
        if normalized_preset == "swiss modern":
            previous_swiss_families.append(_swiss_component_family(spec["role"], spec["layout_id"]))

    if _normalize_preset_name(brief["style"]["preset"]) == "enterprise dark":
        language = brief["language"]
        for index, spec in enumerate(specs):
            # Skip if already determined in the main loop
            if spec.get("dashboard_mode") == "story":
                # Clean up internal marker
                spec.pop("_skip_numeric_signal_check", None)
                # Set remaining story dashboard fields
                if "dashboard_label" not in spec:
                    spec["dashboard_label"] = _enterprise_role_badge(spec["role"], language)
                if "dashboard_items" not in spec:
                    spec["dashboard_items"] = _build_enterprise_story_items(specs, index, language=language)
            elif _should_use_enterprise_story_dashboard(spec, preset=brief["style"]["preset"], language=language):
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


_TITLE_OPENING_PUNCTUATION = "([<{（《〈【「『"
_TITLE_CLOSING_PUNCTUATION = ".,!?;:%，。！？；：、）》〉】」』"
_TITLE_DANGLING_CONNECTORS = frozenset("把以从向与和及为对在将让被给不")
_PROTECTED_CJK_TITLE_BIGRAMS = frozenset(
    """
    文化 转型 时代 哲学 升级 智能 共生 邪道 辩证 客户 产品 销售 交付 服务
    市场 生态 领导 能力 战略 全景 产研 中心 实践 干部 企业 伙伴 模型 安全
    数据 长期 价值 系统 组织 技术 投入 重构 成败 员工 管理 基础 答卷 原生
    操作 愿景 夯实 塑造 践行 素养 认知 伦理 治理 引领 趋势 机会 模式
    谨慎 扩面 足够 支持 内核 壁垒 不清 状态 风险 地图 五个 真实 场景
    开始 追求 输出 宣传 等级 自治 必须 同时 过线 锚点 授权
    """.split()
)


def _compact_title_text(value: str) -> str:
    return re.sub(r"\s+", "", value or "")


def _semantic_title_boundary_penalty(left: str, right: str) -> float:
    left_compact = _compact_title_text(left)
    right_compact = _compact_title_text(right)
    if not left_compact or not right_compact:
        return 0.0

    left_last = left_compact[-1]
    right_first = right_compact[0]
    if left_last in _TITLE_OPENING_PUNCTUATION:
        return 120.0
    if right_first in _TITLE_CLOSING_PUNCTUATION:
        return 120.0
    if left_last in _TITLE_DANGLING_CONNECTORS:
        return 35.0

    if re.fullmatch(r"[\u3400-\u9fff]", left_last) and re.fullmatch(r"[\u3400-\u9fff]", right_first):
        if f"{left_last}{right_first}" in _PROTECTED_CJK_TITLE_BIGRAMS:
            return 90.0
        return 1.25

    if left_last in "，。！？；：:":
        return -0.35
    return 0.0


def _semantic_title_boundary_issue(lines: list[str]) -> str | None:
    for left, right in zip(lines, lines[1:]):
        left_compact = _compact_title_text(left)
        right_compact = _compact_title_text(right)
        if not left_compact or not right_compact:
            continue
        left_last = left_compact[-1]
        right_first = right_compact[0]
        if left_last in _TITLE_OPENING_PUNCTUATION:
            return f"dangling opening punctuation '{left_last}'"
        if right_first in _TITLE_CLOSING_PUNCTUATION:
            return f"line starts with closing punctuation '{right_first}'"
        if left_last in _TITLE_DANGLING_CONNECTORS:
            return f"dangling connector '{left_last}'"
        if (
            re.fullmatch(r"[\u3400-\u9fff]", left_last)
            and re.fullmatch(r"[\u3400-\u9fff]", right_first)
            and f"{left_last}{right_first}" in _PROTECTED_CJK_TITLE_BIGRAMS
        ):
            return f"bad CJK word split '{left_last}{right_first}'"
    return None


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
    cost += sum(_semantic_title_boundary_penalty(left, right) for left, right in zip(lines, lines[1:]))
    if any(_is_orphan_title_line(line) for line in lines):
        cost += 100.0
    if _has_collapsed_middle_line(units):
        cost += 80.0
    if _is_globally_unbalanced_title(units):
        cost += 45.0

    total_units = sum(units)
    if len(lines) == 1 and total_units > 14.5:
        cost += (total_units - 14.5) * 3.2
    if len(lines) > 1:
        cost += sum(max(0.0, unit - 10.0) ** 2 * 2.0 for unit in units)
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
    packet: dict[str, Any],
) -> str:
    js_engine = _extract_js_engine_blocks(preset=preset, version=_skill_version())
    brand_mark = str(packet.get("brand_mark") or _brand_mark_text(title, preset))
    provenance_attrs = _html_body_provenance_attrs(packet)
    body_classes = " ".join(str(item) for item in packet.get("body_classes", []) if item)
    class_attr = f' class="{_escape(body_classes)}"' if body_classes else ""
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
<body data-export-progress="true" data-preset="{_escape(preset)}"{class_attr} {provenance_attrs}>
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
    tokens = style_contract.get("tokens", {})
    # Detect light vs dark theme from CSS vars
    bg_token = tokens.get("--bg") or tokens.get("--bg-primary") or tokens.get("--bg-white")
    is_dark = bg_token and not bg_token.strip().startswith(("#f", "#F", "#e", "#E", "#d", "#D", "#c", "#C", "#b", "#B", "white", "rgb(255", "rgba(255"))

    if preset == "Enterprise Dark":
        slide_background = "transparent"
        nav_dot_idle = "rgba(255,255,255,0.28)"
        nav_dot_active = "var(--accent-blue, var(--chart-primary, #3b82f6))"
    elif is_dark:
        slide_background = f"var(--bg-primary, var(--bg, {bg_token}))"
        nav_dot_idle = "rgba(255,255,255,0.28)"
        nav_dot_active = "var(--accent-blue, var(--chart-primary, #3b82f6))"
    else:
        # Light theme (including custom themes like Kingdee)
        slide_background = f"var(--bg-white, var(--bg-primary, var(--bg, #FFFFFF)))"
        nav_dot_idle = "rgba(0,0,0,0.18)"
        nav_dot_active = "var(--kd-blue, var(--accent, #2971EB))"

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

    body_text = "var(--text-primary, var(--text, #f3f4f6))" if is_dark else "var(--text-primary, var(--text, #1A1A1A))"
    body_bg = "var(--bg-primary, var(--bg, #0f1117))" if is_dark else "var(--bg-white, var(--bg-primary, var(--bg, #FFFFFF)))"

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
    color: {body_text};
    background: {body_bg};
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
    top: 0;
    left: 0;
    width: 1440px !important;
    height: 900px !important;
    transform-origin: top left;
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
    right: 84px;
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


def _primary_numbers_from_numeric_facts(spec: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for fact in spec.get("numeric_facts", []):
        numbers = _extract_numbers(str(fact))
        if numbers:
            values.append(numbers[0])
    return _dedupe_preserve(values)


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

    meaningful = [
        value for value in values
        if any(marker in value for marker in (".", "%", "+", "万", "亿", "座", "美元", "年"))
        or _numeric_value(value) >= 10
    ]
    if len(meaningful) < len(fallback):
        return []
    values = meaningful

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

    if re.search(r"[A-Za-z]", candidate) and re.search(r"[\u4e00-\u9fff]", candidate):
        short_latin = re.search(r"(?:(?<=^)|(?<=[\u4e00-\u9fff]))([A-Za-z][A-Za-z0-9%&+/#._:-]{1,7})(?=[\u4e00-\u9fff]|$)", candidate)
        if short_latin:
            token = short_latin.group(1)
            if token.upper() != "AI":
                return token
        long_latin_prefix = re.match(r"^[A-Za-z][A-Za-z0-9%&+/#._:-]{8,}的?(.*)$", candidate)
        if long_latin_prefix:
            remainder = long_latin_prefix.group(1).lstrip("的")
            if len(remainder) >= 2 and re.search(r"[\u4e00-\u9fff]", remainder):
                candidate = remainder

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
        cjk_match = re.search(r"[\u4e00-\u9fffA-Za-z0-9]{2,6}", candidate)
        shortened = cjk_match.group(0)[:4] if cjk_match else candidate[:4]
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
        (r"\bBRIEF\.json\b", "BRIEF"),
        (r"\bHTML\b", "HTML"),
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
            *spec.get("supporting_facts", []),
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
            *spec.get("supporting_facts", []),
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


def _swiss_table_cell(value: str, *, max_chars: int = 72) -> str:
    cleaned = re.sub(r"\s+", " ", value or "").strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[: max_chars - 3].rstrip(" ,，、;；:：-—") + "..."


def _metric_value_for_item(
    item: str,
    spec: dict[str, Any],
    *,
    index: int = 0,
    used_tokens: set[str] | None = None,
    numeric_only: bool = False,
) -> str:
    numeric_fact_numbers = _primary_numbers_from_numeric_facts(spec)
    if numeric_only and numeric_fact_numbers:
        return numeric_fact_numbers[min(index, len(numeric_fact_numbers) - 1)]

    explicit_numbers = _spec_explicit_numbers(spec)
    if numeric_only and explicit_numbers:
        return explicit_numbers[min(index, len(explicit_numbers) - 1)]

    direct_numbers = _extract_numbers(item)
    if direct_numbers:
        if "90/9/1" in item:
            return "90/9/1"
        return direct_numbers[0]

    evidence_numbers = _dedupe_preserve(_extract_numbers(" ".join(spec["evidence_items"])))
    if numeric_only:
        if evidence_numbers:
            return evidence_numbers[min(index, len(evidence_numbers) - 1)]
        return str(index + 1)

    compact = _compact_display_token(item, fallback=str(index + 1), used_tokens=used_tokens)
    if compact not in {"关键", str(index + 1)}:
        return compact
    if explicit_numbers:
        return explicit_numbers[min(index, len(explicit_numbers) - 1)]
    if evidence_numbers:
        return evidence_numbers[min(index, len(evidence_numbers) - 1)]
    return compact


def _strip_chart_label_prefix(text: str) -> str:
    cleaned = str(text).strip()
    patterns = [
        r"^\s*\d+(?:\.\d+)?(?:[-–—]\d+(?:\.\d+)?)?(?:\+|%|万|亿|座|年)?\s*[：:、，,;；\-—–]*\s*",
        r"^\s*阶段\s*\d+\s*[：:、，,;；\-—–]*\s*",
        r"^\s*phase\s*\d+\s*[:：,\-—–]?\s*",
    ]
    for pattern in patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def _is_weak_chart_label(label: str) -> bool:
    cleaned = re.sub(r"\s+", "", str(label or ""))
    if not cleaned:
        return True
    if re.fullmatch(r"[\d\.\-%+/年月万亿座]+", cleaned):
        return True
    semantic_chars = re.sub(r"[^A-Za-z\u3400-\u9fff]", "", cleaned)
    return len(semantic_chars) < 2


def _compact_chart_axis_label(item: str, candidate: str, *, fallback: str) -> str:
    if _title_visual_units(candidate) <= 12 and not re.search(r"[→—–]", candidate):
        return candidate

    segments = re.split(r"\s*(?:→|—|–|->|:|：)\s*", item)
    for segment in segments:
        token = _compact_display_token(segment, fallback=fallback)
        if not _is_weak_chart_label(token) and _title_visual_units(token) <= 12 and not re.search(r"[→—–]", token):
            return token

    token = _compact_display_token(candidate, fallback=fallback)
    if not _is_weak_chart_label(token) and _title_visual_units(token) <= 12 and not re.search(r"[→—–]", token):
        return token
    return fallback


def _chart_labels_from_spec(spec: dict[str, Any], *, count: int = 4, family: str = "alpha") -> list[str]:
    defaults = _sequence_labels(count, family=family)
    labels: list[str] = []
    for index, item in enumerate(_spec_display_items(spec, limit=count)):
        fallback = defaults[index] if index < len(defaults) else f"Step{index + 1}"
        candidate = _compact_display_token(item, fallback=fallback)
        if _is_weak_chart_label(candidate):
            candidate = _compact_display_token(_strip_chart_label_prefix(item), fallback=fallback)
        if _is_weak_chart_label(candidate):
            candidate = fallback
        candidate = _compact_chart_axis_label(item, candidate, fallback=fallback)
        labels.append(candidate)
    if len(labels) >= count:
        return labels[:count]
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
        base = [f"Phase {index:02d}" for index in range(1, 7)]
    else:
        base = [f"Signal {index:02d}" for index in range(1, 7)]
    labels = base[:count]
    while len(labels) < count:
        labels.append(f"Step{len(labels) + 1}")
    return labels


def _svg_bar_chart(labels: list[str], values: list[str], *, color_class: str = "chart-bar") -> str:
    magnitudes = [_numeric_value(value) for value in values]
    max_value = max(magnitudes) if any(magnitudes) else 1
    chart_bottom = 150
    chart_top = 18
    plot_height = chart_bottom - chart_top
    bars = []
    for index, (label, value, magnitude) in enumerate(zip(labels, values, magnitudes), start=0):
        x = 38 + index * 68
        height = max(34, int((magnitude / max_value) * plot_height)) if magnitude > 0 else 34
        y = chart_bottom - height
        bars.append(
            f'<rect x="{x}" y="{y}" width="54" height="{height}" rx="4" class="{color_class}{" secondary" if index == 1 else (" tertiary" if index == 2 else "")}"></rect>'
            f'<text x="{x + 27}" y="174" text-anchor="middle" class="chart-label">{_escape(label)}</text>'
            f'<text x="{x + 24}" y="{y - 8}" text-anchor="middle" class="chart-val">{value}</text>'
        )
    return (
        '<svg viewBox="0 0 320 188" class="ds-chart-svg" role="img" aria-label="bar chart">'
        '<line x1="24" y1="16" x2="24" y2="150" class="chart-axis"></line>'
        '<line x1="24" y1="150" x2="308" y2="150" class="chart-axis"></line>'
        '<line x1="24" y1="42" x2="308" y2="42" class="chart-grid"></line>'
        '<line x1="24" y1="96" x2="308" y2="96" class="chart-grid"></line>'
        + "".join(bars)
        + "</svg>"
    )


def _svg_line_chart(labels: list[str], values: list[str]) -> str:
    magnitudes = [_numeric_value(value) for value in values]
    max_value = max(magnitudes) if any(magnitudes) else 1
    chart_left = 28
    chart_right = 296
    chart_top = 18
    chart_bottom = 150
    plot_width = chart_right - chart_left
    plot_height = chart_bottom - chart_top
    points = []
    labels_html = []
    for index, (label, value, magnitude) in enumerate(zip(labels, values, magnitudes), start=0):
        ratio = 0 if len(labels) == 1 else index / (len(labels) - 1)
        x = int(chart_left + ratio * plot_width)
        y = chart_bottom - int((magnitude / max_value) * plot_height) if magnitude > 0 else chart_bottom
        points.append(f"{x},{y}")
        labels_html.append(
            f'<circle cx="{x}" cy="{y}" r="5.5" class="ds-dot"></circle>'
            f'<text x="{x}" y="174" text-anchor="middle" class="chart-label">{_escape(label)}</text>'
            f'<text x="{x}" y="{y - 10}" text-anchor="middle" class="chart-val">{value}</text>'
        )
    point_string = " ".join(points)
    return (
        '<svg viewBox="0 0 320 188" class="ds-chart-svg" role="img" aria-label="line chart">'
        '<line x1="22" y1="16" x2="22" y2="150" class="chart-axis"></line>'
        '<line x1="22" y1="150" x2="302" y2="150" class="chart-axis"></line>'
        '<line x1="22" y1="44" x2="302" y2="44" class="chart-grid"></line>'
        '<line x1="22" y1="98" x2="302" y2="98" class="chart-grid"></line>'
        f'<polyline points="{point_string}" class="chart-line"></polyline>'
        + "".join(labels_html)
        + "</svg>"
    )


def _svg_signal_map(spec: dict[str, Any], *, count: int = 4, family: str = "signal") -> str:
    labels = _chart_labels_from_spec(spec, count=count, family=family)
    positions = [(48, 112), (120, 58), (200, 58), (272, 112)]
    positions = positions[:count]
    if len(positions) < len(labels):
        labels = labels[: len(positions)]
    path = " ".join(f"{'M' if index == 0 else 'L'} {x} {y}" for index, (x, y) in enumerate(positions))
    nodes = []
    tone_classes = ["", "secondary", "tertiary", "secondary"]
    for index, ((x, y), label) in enumerate(zip(positions, labels)):
        tone = tone_classes[index] if index < len(tone_classes) else ""
        nodes.append(
            f'<circle cx="{x}" cy="{y}" r="28" class="ds-signal-node {tone}"></circle>'
            f'<text x="{x}" y="{y}" class="ds-signal-label">{_escape(label)}</text>'
        )
    return (
        '<svg viewBox="0 0 320 188" class="ds-chart-svg ds-signal-map" role="img" aria-label="signal map">'
        '<line x1="24" y1="150" x2="296" y2="150" class="chart-axis"></line>'
        '<line x1="24" y1="42" x2="296" y2="42" class="chart-grid"></line>'
        '<line x1="24" y1="96" x2="296" y2="96" class="chart-grid"></line>'
        f'<path d="{path}" class="ds-signal-link"></path>'
        + "".join(nodes)
        + "</svg>"
    )


def _svg_signal_bars(spec: dict[str, Any], *, count: int = 4) -> str:
    labels = _chart_labels_from_spec(spec, count=count)
    widths = [158, 134, 110, 88]
    rows = []
    for index, label in enumerate(labels):
        y = 34 + index * 34
        tone = "" if index == 0 else ("secondary" if index == 1 else ("tertiary" if index == 2 else ""))
        rows.append(
            f'<text x="32" y="{y + 8}" class="ds-svg-label">{_escape(label)}</text>'
            f'<rect x="128" y="{y}" width="158" height="16" rx="8" class="ds-bar-track"></rect>'
            f'<rect x="128" y="{y}" width="{widths[index]}" height="16" rx="8" class="ds-bar-fill {tone}"></rect>'
        )
    return (
        '<svg viewBox="0 0 320 188" class="ds-chart-svg ds-signal-bars" role="img" aria-label="signal bars">'
        '<line x1="118" y1="24" x2="118" y2="164" class="chart-axis"></line>'
        '<line x1="128" y1="164" x2="288" y2="164" class="chart-axis"></line>'
        + "".join(rows)
        + "</svg>"
    )


def _svg_flow_map(spec: dict[str, Any], *, count: int = 4) -> str:
    labels = _chart_labels_from_spec(spec, count=count, family="workflow")
    positions = [(42, 104), (118, 62), (202, 104), (278, 62)]
    positions = positions[: len(labels)]
    path = " ".join(f"{'M' if index == 0 else 'L'} {x} {y}" for index, (x, y) in enumerate(positions))
    nodes = []
    tone_classes = ["", "secondary", "tertiary", ""]
    for index, ((x, y), label) in enumerate(zip(positions, labels), start=1):
        tone = tone_classes[index - 1] if index - 1 < len(tone_classes) else ""
        nodes.append(
            f'<circle cx="{x}" cy="{y}" r="24" class="ds-flow-node {tone}"></circle>'
            f'<text x="{x}" y="{y}" class="ds-svg-label" text-anchor="middle">{index}</text>'
            f'<text x="{x}" y="{y + 42}" class="ds-svg-muted" text-anchor="middle">{_escape(label)}</text>'
        )
    return (
        '<svg viewBox="0 0 320 188" class="ds-chart-svg ds-flow-map" role="img" aria-label="flow map">'
        '<line x1="24" y1="150" x2="296" y2="150" class="chart-axis"></line>'
        '<line x1="24" y1="42" x2="296" y2="42" class="chart-grid"></line>'
        f'<path d="{path}" class="ds-flow-path"></path>'
        + "".join(nodes)
        + "</svg>"
    )


def _svg_phase_timeline(spec: dict[str, Any], *, count: int = 4, aria_label: str = "phase timeline") -> str:
    labels = _chart_labels_from_spec(spec, count=count, family="workflow")
    positions = [(42, 98), (118, 98), (202, 98), (278, 98)]
    positions = positions[: len(labels)]
    nodes = []
    tone_classes = ["", "secondary", "tertiary", ""]
    for index, ((x, y), node_label) in enumerate(zip(positions, labels), start=1):
        tone = tone_classes[index - 1] if index - 1 < len(tone_classes) else ""
        nodes.append(
            f'<line x1="{x}" y1="56" x2="{x}" y2="142" class="chart-grid"></line>'
            f'<circle cx="{x}" cy="{y}" r="22" class="ds-flow-node {tone}"></circle>'
            f'<text x="{x}" y="{y}" class="ds-svg-label" text-anchor="middle">{index}</text>'
            f'<text x="{x}" y="154" class="ds-svg-muted" text-anchor="middle">{_escape(node_label)}</text>'
        )
    return (
        f'<svg viewBox="0 0 320 188" class="ds-chart-svg ds-phase-timeline" role="img" aria-label="{_escape(aria_label)}">'
        '<line x1="24" y1="98" x2="296" y2="98" class="chart-axis"></line>'
        '<line x1="24" y1="42" x2="296" y2="42" class="chart-grid"></line>'
        + "".join(nodes)
        + "</svg>"
    )


def _svg_evidence_ladder(spec: dict[str, Any], *, count: int = 4) -> str:
    labels = _chart_labels_from_spec(spec, count=count)
    rows = []
    rail_x = 44
    label_x = 292
    widths = [110, 96, 82, 68]
    for index, label in enumerate(labels):
        y = 40 + index * 32
        tone = "" if index == 0 else ("secondary" if index == 1 else ("tertiary" if index == 2 else ""))
        rows.append(
            f'<line x1="{rail_x}" y1="{y}" x2="{rail_x + widths[index]}" y2="{y}" class="ds-ladder-rung {tone}"></line>'
            f'<circle cx="{rail_x}" cy="{y}" r="6" class="ds-dot"></circle>'
            f'<text x="{label_x}" y="{y}" class="ds-svg-label" text-anchor="end">{_escape(label)}</text>'
        )
    return (
        '<svg viewBox="0 0 320 188" class="ds-chart-svg ds-evidence-ladder" role="img" aria-label="evidence ladder">'
        f'<line x1="{rail_x}" y1="28" x2="{rail_x}" y2="150" class="ds-ladder-rail"></line>'
        '<line x1="28" y1="150" x2="292" y2="150" class="chart-axis"></line>'
        + "".join(rows)
        + "</svg>"
    )


def _svg_state_grid(spec: dict[str, Any], *, count: int = 4) -> str:
    labels = _chart_labels_from_spec(spec, count=count)
    positions = [(52, 42), (174, 42), (52, 104), (174, 104)]
    cells = []
    for index, ((x, y), label) in enumerate(zip(positions, labels)):
        cells.append(
            f'<rect x="{x}" y="{y}" width="94" height="44" rx="8" class="ds-state-cell {"hot" if index in (0, 3) else ""}"></rect>'
            f'<text x="{x + 47}" y="{y + 22}" class="ds-svg-label" text-anchor="middle">{_escape(label)}</text>'
        )
    return (
        '<svg viewBox="0 0 320 188" class="ds-chart-svg ds-state-grid-svg" role="img" aria-label="state grid">'
        '<line x1="24" y1="94" x2="296" y2="94" class="chart-grid"></line>'
        '<line x1="160" y1="24" x2="160" y2="156" class="chart-grid"></line>'
        + "".join(cells)
        + "</svg>"
    )


def _data_story_non_numeric_svg(spec: dict[str, Any]) -> str:
    role = spec["role"]
    family = str(spec.get("preferred_layout_family") or spec.get("visual_intent") or "").strip().lower()
    if role == "workflow":
        return _svg_phase_timeline(spec, count=4, aria_label="workflow timeline")
    if family == "timeline":
        return _svg_phase_timeline(spec, count=4)
    if role == "use-cases":
        return _svg_phase_timeline(spec, count=4)
    if spec.get("layout_id") == "workflow_chart" or role in {"content-routing", "solution"} or family in {"three-things", "flow"}:
        return _svg_flow_map(spec, count=4)
    if role in {"validation", "evidence", "proof"}:
        return _svg_evidence_ladder(spec, count=4)
    if role in {"interaction"}:
        return _svg_state_grid(spec, count=4)
    if role in {"pain-solution", "problem", "risk"} or family in {"comparison"}:
        return _svg_signal_bars(spec, count=4)
    if role in {"design-philosophy", "architecture"} or family in {"architecture-map"}:
        return _svg_signal_map(spec, count=4)
    return _svg_signal_bars(spec, count=4)


SWISS_BG_NUM_ROLES = {"cover", "pain-solution", "presets", "content-routing", "use-cases", "cta_close", "closing", "cta", "getting-started"}


def _swiss_bg_num(spec: dict[str, Any]) -> str:
    if spec["role"] not in SWISS_BG_NUM_ROLES:
        return ""
    return f'<div class="bg-num reveal">{int(spec["slide_number"]):02d}</div>'


def _swiss_left_title_lines(text: str) -> list[str]:
    normalized = _normalize_title_text(text)
    if not normalized:
        return []

    tokens = _tokenize_title(normalized)
    first_cjk = next((index for index, token in enumerate(tokens) if re.fullmatch(r"[\u3400-\u9fff]", token)), None)
    if first_cjk is not None and first_cjk >= 2:
        latin_tokens = tokens[:first_cjk]
        cjk_tail = _join_title_tokens(tokens[first_cjk:])
        word_tokens = [token for token in latin_tokens if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9%&+/#._:-]*", token)]
        if len(word_tokens) >= 2 and cjk_tail:
            return [
                _join_title_tokens(word_tokens[:-1]),
                word_tokens[-1],
                cjk_tail,
            ]

    return _balance_title_lines(normalized, max_lines=3, force_balance=True)


def _swiss_left_title_tag(tag: str, text: str, *, layout_id: str) -> str:
    lines = _swiss_left_title_lines(text)
    if len(lines) <= 1:
        return _title_tag(tag, "swiss-title", text, preset="Swiss Modern", layout_id=layout_id)

    markup = "".join(f'<span class="title-line">{_escape(line)}</span>' for line in lines)
    return f'<{tag} class="swiss-title reveal title-balance">{markup}</{tag}>'


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
        {_swiss_bg_num(spec)}
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
    title_tag = _swiss_left_title_tag("h2", spec["title"], layout_id=spec["layout_id"])
    pairs = _spec_detail_pairs(spec, count=3)
    items = "".join(
        f"""
        <div class="pain-item{' accent-border' if index == 0 else ''} reveal">
            <div class="pain-num">{index + 1:02d}</div>
            <div class="pain-title">{_escape(title)}</div>
            <div class="pain-desc">{_escape(body)}</div>
        </div>
        """
        for index, (title, body) in enumerate(pairs[:3])
    )
    return f"""
    <section class="slide column_content" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="column_content">
        {_swiss_bg_num(spec)}
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
        {_swiss_bg_num(spec)}
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
        {_swiss_bg_num(spec)}
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
    if spec["role"] in {"content-routing", "validation", "proof", "evidence"}:
        blocks = []
        for index, (label, body) in enumerate(pairs[:3], start=1):
            blocks.append(
                f"""
                <div class="inst-block reveal">
                    <div class="inst-label">{index:02d} / {_escape(label)}</div>
                    <div class="inst-link">{_escape(spec['role'])}</div>
                    <div class="swiss-body">{_escape(body)}</div>
                </div>
                """
            )
        return f"""
    <section class="slide data_table" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="data_table">
        {_swiss_bg_num(spec)}
        <div class="slide-content content">
            <div class="eyebrow swiss-label reveal">{_escape(spec['role'])}</div>
            {title_tag}
            <div class="inst-blocks">
                {"".join(blocks)}
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()

    rows = []
    for index, (item, body) in enumerate(pairs[:3]):
        highlight = " class=\"highlight\"" if index == 0 else ""
        signal = _swiss_table_cell(item, max_chars=58)
        meaning = _swiss_table_cell(body, max_chars=72)
        focus = _swiss_table_cell(_compact_display_token(item, fallback=spec["role"]), max_chars=24)
        rows.append(
            f"<tr{highlight}><td>{_escape(signal)}</td><td>{_escape(meaning)}</td><td>{_escape(focus)}</td></tr>"
        )
    rows_html = "\n".join(rows)
    return f"""
    <section class="slide data_table" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="data_table">
        {_swiss_bg_num(spec)}
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
    is_closing_role = spec["role"] in {"closing", "cta", "cta_close", "getting-started"}
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
    cta_html = ""
    if is_closing_role:
        cta_lines = _balance_title_lines(spec["title"], max_lines=2, force_balance=True) or [spec["title"]]
        cta_line_html = "".join(f'<span class="cta-line">{_escape(line)}</span>' for line in cta_lines[:2])
        echo_items = _spec_display_items(spec, limit=2)
        echo_html = "".join(
            f"""
            <div class="cta-echo">
                <div class="cta-echo-num">{index:02d}</div>
                <div class="cta-echo-label">{_escape(item)}</div>
            </div>
            """
            for index, item in enumerate(echo_items[:2], start=1)
        )
        cta_html = f"""
            <div class="cta-block reveal">
                <div class="cta-title">{cta_line_html}</div>
                {echo_html}
            </div>
        """
    tail_html = ""
    if not is_closing_role:
        tail_html = f"""
            <div class="swiss-rule red reveal" style="width:120px;margin:18px 0 10px;"></div>
            <p class="swiss-body reveal">{_escape(spec['title'])}</p>
        """
    section_class = "slide pull_quote swiss-cta-close" if is_closing_role else "slide pull_quote"
    return f"""
    <section class="{section_class}" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="pull_quote">
        {_swiss_bg_num(spec)}
        <div class="slide-content content" style="align-items:flex-start;justify-content:flex-start;padding-top:18vh;">
            <div class="eyebrow swiss-label reveal">{_escape(spec['role'])}</div>
            {quote_tag}
            {cta_html}
            {tail_html}
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_swiss_contents_index(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("h2", "swiss-title", spec["title"], preset="Swiss Modern", layout_id=spec["layout_id"])
    pairs = _spec_detail_pairs(spec, count=3)
    if spec["role"] in {"presets", "interaction", "use-cases", "features", "recommendation", "best-fit"}:
        items = "".join(
            f"""
            <div class="feat-card reveal">
                <div class="feat-key">{index + 1:02d}</div>
                <div class="feat-name">{_escape(_swiss_table_cell(title, max_chars=36))}</div>
                <div class="feat-desc">{_escape(_swiss_table_cell(body, max_chars=52))}</div>
            </div>
            """
            for index, (title, body) in enumerate(pairs[:3])
        )
        body_html = f'<div class="feat-grid">{items}</div>'
    else:
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
        body_html = f'<ul style="list-style:none;display:grid;gap:14px;padding:0;margin:0;">{items}</ul>'
    return f"""
    <section class="slide contents_index" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="contents_index">
        {_swiss_bg_num(spec)}
        <div class="slide-content content">
            <div class="eyebrow swiss-label reveal">{_escape(spec['role'])}</div>
            {title_tag}
            {body_html}
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
    font-size: clamp(17px, 1.9vw, 22px);
    line-height: 1.62;
}}

.pain-desc,
.stat-value,
.disc-step-desc,
.index-desc {{
    font-size: clamp(16px, 1.8vw, 21px);
    line-height: 1.62;
}}

.pain-title,
.disc-step-title,
.index-title,
.stat-label,
.data-table td,
.data-table th {{
    font-size: clamp(16px, 1.7vw, 20px);
}}

.pain-item {{
    padding-left: clamp(14px, 2.2vw, 24px);
}}

.left-panel .swiss-title {{
    color: var(--text-light);
    font-size: clamp(1.5rem, 1.9vw, 2.4rem);
    line-height: 1.02;
    overflow-wrap: normal;
    word-break: normal;
    hyphens: none;
}}

.left-panel .swiss-label {{
    color: rgba(255, 255, 255, 0.34);
}}

.left-panel .title-line {{
    white-space: nowrap;
    overflow-wrap: normal;
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

.slide-content, .left-panel, .right-panel {{
    position: relative;
    z-index: 2;
}}

.contents_index .feat-grid {{
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: clamp(8px, 1.2vw, 14px);
}}

.contents_index .feat-card {{
    padding: clamp(10px, 1.4vw, 18px);
    min-height: 0;
}}

.contents_index .feat-key {{
    font-size: clamp(18px, 2.4vw, 32px);
}}

.contents_index .feat-desc {{
    line-height: 1.36;
}}

.swiss-cta-close .slide-content {{
    gap: clamp(10px, 1.5vw, 16px);
    padding-top: clamp(42px, 8vh, 80px) !important;
}}

.swiss-cta-close .swiss-title {{
    font-size: clamp(2.4rem, 4.48vw, 4.28rem);
    line-height: 0.98;
    max-width: min(18ch, 800px) !important;
}}

.swiss-cta-close .swiss-title .title-line {{
    white-space: normal;
}}

.swiss-cta-close .cta-block {{
    width: min(680px, 88vw);
    max-width: 100%;
}}

.cta-echo-label {{
    color: rgba(255, 255, 255, 0.74);
}}

@media (max-width: 900px) {{
    .contents_index .feat-grid {{
        grid-template-columns: 1fr;
    }}
}}

@media (max-width: 520px) {{
    .slide {{
        padding-left: clamp(16px, 6vw, 28px) !important;
        padding-right: clamp(16px, 6vw, 28px) !important;
    }}
    .slide-content,
    .content,
    .left-panel,
    .right-panel {{
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
        position: relative !important;
        left: auto !important;
        right: auto !important;
    }}
    .column_content,
    .pull_quote {{
        flex-direction: column !important;
    }}
    .swiss-title,
    .swiss-body,
    .left-panel .swiss-title,
    .swiss-cta-close .swiss-title {{
        width: auto !important;
        max-width: 100% !important;
        min-width: 0 !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
        overflow-wrap: anywhere !important;
        word-break: normal !important;
        letter-spacing: 0 !important;
    }}
    .title-balance {{
        display: block !important;
        max-width: 100% !important;
    }}
    .title-line,
    .left-panel .title-line {{
        display: inline !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
        word-break: normal !important;
    }}
    .geometric_diagram .slide-content.disc-header {{
        justify-content: flex-start;
        padding-top: clamp(52px, 7vh, 64px) !important;
        padding-bottom: 18px !important;
        gap: 8px;
    }}
    .geometric_diagram .disc-body {{
        flex-direction: column;
        align-items: stretch;
        gap: 10px;
        min-height: 0;
    }}
    .geometric_diagram .disc-steps {{
        gap: 8px;
    }}
    .geometric_diagram .disc-step {{
        gap: 8px;
    }}
    .geometric_diagram .disc-step-title {{
        font-size: 13px;
        line-height: 1.2;
    }}
    .geometric_diagram .disc-step-desc {{
        font-size: 12.5px;
        line-height: 1.35;
    }}
    .geometric_diagram .disc-diagram {{
        align-self: center;
        width: min(230px, 100%);
        max-height: 170px;
    }}
    .geometric_diagram .diagram-svg {{
        max-height: 170px;
    }}
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
    right: clamp(-3rem, -2vw, -1rem);
    top: 0;
    font-family: "Archivo Black", sans-serif;
    font-weight: 900;
    font-size: clamp(10rem, 30vw, 30rem);
    color: #f4f4f4;
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
    top: 0;
    left: 0;
    width: 1440px !important;
    height: 900px !important;
    transform-origin: top left;
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
    provenance_attrs = _html_body_provenance_attrs(packet)

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
<body data-export-progress="true" data-preset="Swiss Modern" {provenance_attrs}>
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

/* Center content on slide — matches demo golden standard */
.slide {
    align-items: center;
    justify-content: center;
    padding: var(--slide-padding, clamp(24px, 4vw, 52px));
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
    font-size: clamp(13px, 1.3vw, 15px);
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

.ent-cover-metric-row {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: clamp(12px, 2vw, 20px);
    margin-top: clamp(22px, 3vw, 34px);
}

.ent-kpi-card.ent-cover-metric-card {
    min-height: clamp(110px, 15vw, 148px);
    padding: clamp(16px, 2vw, 22px);
    justify-content: space-between;
    gap: 16px;
    background: linear-gradient(180deg, rgba(56, 139, 253, 0.07), rgba(15, 23, 42, 0.42)), var(--bg-secondary);
}

.ent-cover-metric-index {
    font-size: clamp(11px, 1.05vw, 13px);
    line-height: 1;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
}

.ent-cover-metric-title {
    font-size: clamp(18px, 2vw, 24px);
    line-height: 1.18;
    font-weight: 650;
    color: var(--text-primary);
    letter-spacing: 0;
}

.ent-cover-metric-title .ent-kpi-number.ent-cover-inline-number {
    display: inline;
    font-size: inherit;
    line-height: inherit;
    font-weight: inherit;
    color: inherit;
    letter-spacing: inherit;
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
    font-size: clamp(11px, 1.1vw, 13px);
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
    font-size: clamp(20px, 2.2vw, 30px);
    line-height: 1.14;
    max-width: min(100%, 20ch);
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
    font-size: clamp(12px, 1.2vw, 14px);
    letter-spacing: 0.08em;
    color: var(--text-muted);
    text-transform: uppercase;
}

.ent-timeline-copy {
    font-size: clamp(14px, 1.4vw, 16px);
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
    font-size: clamp(14px, 1.4vw, 16px);
    line-height: 1.55;
    color: var(--text-body);
}

@media (max-width: 900px) {
    .enterprise-split .ent-split,
    .ent-feature-grid,
    .ent-matrix,
    .ent-arch-grid,
    .ent-timeline,
    .ent-contrast-split {
        grid-template-columns: 1fr;
    }
}

/* === Consulting split inline replacements === */
.ent-split-item-title {
    margin: 0 0 6px;
    color: var(--text-primary);
    font-size: clamp(14px, 1.4vw, 16px);
}
.ent-split-item-copy {
    margin: 0;
    color: var(--text-primary);
    font-size: clamp(13px, 1.2vw, 15px);
    line-height: 1.5;
}

/* === Semantic accent variants === */
.ent-accent-cyan { color: var(--accent-cyan, #18b5b5); }
.ent-accent-violet { color: var(--accent-violet, #a371f7); }

/* === Contrast Split (before/after comparison) === */
.ent-contrast-split {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: clamp(14px, 2vw, 24px);
    width: 100%;
}
.ent-contrast-block {
    border-radius: 8px;
    padding: clamp(18px, 2.4vw, 28px);
    display: flex;
    flex-direction: column;
    gap: 12px;
}
.ent-contrast-block--negative {
    background: rgba(248, 81, 73, 0.06);
    border: 1px solid rgba(248, 81, 73, 0.3);
}
.ent-contrast-block--positive {
    background: rgba(63, 185, 80, 0.06);
    border: 1px solid rgba(63, 185, 80, 0.4);
}
.ent-contrast-block h4 {
    font-size: clamp(18px, 2vw, 22px);
    font-weight: 700;
    line-height: 1.3;
}
.ent-contrast-block--negative h4 { color: var(--accent-red); }
.ent-contrast-block--positive h4 { color: var(--accent-green); }
.ent-contrast-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 6px 0;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    font-size: clamp(14px, 1.4vw, 16px);
    color: var(--text-body);
    line-height: 1.5;
}
.ent-contrast-item:last-child { border-bottom: none; }
.ent-contrast-marker {
    flex-shrink: 0;
    width: 18px;
    height: 18px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    font-family: var(--font-mono, monospace);
}
.ent-contrast-block--negative .ent-contrast-marker {
    background: rgba(248,81,73,0.2);
    color: var(--accent-red);
}
.ent-contrast-block--positive .ent-contrast-marker {
    background: rgba(63,185,80,0.2);
    color: var(--accent-green);
}
""".strip()


def _enterprise_metric_value_for_label(
    label: str,
    metric_values: list[str],
    used_values: set[str],
    index: int,
) -> str | None:
    candidates = _extract_numbers(label)
    if index < len(metric_values):
        candidates.append(metric_values[index])
    candidates.extend(metric_values)
    for value in candidates:
        if value not in used_values:
            used_values.add(value)
            return value
    return None


def _enterprise_table_items(spec: dict[str, Any], *, minimum: int = 3, limit: int = 4) -> list[str]:
    pools = [
        spec.get("supporting_facts") or [],
        spec.get("evidence_items") or [],
        spec.get("supporting_items") or [],
    ]
    items: list[str] = []
    for pool in pools:
        for value in pool:
            item = str(value).strip()
            if item and item not in items:
                items.append(item)
            if len(items) >= limit:
                return items[:limit]

    fallback = str(spec.get("key_point") or spec.get("visual") or "").strip()
    while fallback and len(items) < minimum:
        items.append(fallback)
    return items[:limit]


def _enterprise_table_cells(item: str, fallback_meaning: str) -> tuple[str, str]:
    for separator in (" — ", " – ", " - ", "：", ":"):
        if separator in item:
            signal, meaning = item.split(separator, 1)
            signal = signal.strip()
            meaning = meaning.strip()
            if signal and meaning:
                return signal, meaning
    return item, fallback_meaning


def _render_enterprise_cover_metric_title(label: str) -> str:
    numbers = _extract_numbers(label)
    if not numbers:
        return _escape(label)
    value = numbers[0]
    prefix, _separator, suffix = label.partition(value)
    return (
        f"{_escape(prefix)}"
        f'<span class="ent-kpi-number ent-cover-inline-number">{_escape(value)}</span>'
        f"{_escape(suffix)}"
    )


def _render_enterprise_kpi_dashboard(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    is_cover = spec["role"] in ("cover", "hook")
    title_tag = _title_tag(
        "h1" if is_cover else "h2",
        "ent-hero-title" if is_cover else "ent-title",
        spec["title"],
        preset="Enterprise Dark",
        layout_id=spec["layout_id"],
        accent_class="ent-accent-blue",
    )
    # Extract real numbers from spec — use _spec_explicit_numbers to avoid fallback=[] bug
    real_numbers = _spec_explicit_numbers(spec)[:3]  # Limit to 3 KPI cards
    has_numbers = bool(real_numbers)

    if is_cover:
        labels = _spec_display_items(spec, limit=3)
        cards = []
        for index, label in enumerate(labels[:3], start=1):
            cards.append(
                f"""
                <div class="ent-kpi-card ent-cover-metric-card reveal">
                    <div class="ent-cover-metric-index">Signal {index:02d}</div>
                    <div class="ent-cover-metric-title">{_render_enterprise_cover_metric_title(label)}</div>
                </div>
                """
            )
        kpi_row = f'<div class="ent-cover-metric-row">{"".join(cards)}</div>'
    elif has_numbers:
        labels = _spec_display_items(spec, limit=3)
        used_metric_values: set[str] = set()
        # Content area: card-based KPI row
        cards = []
        for index, label in enumerate(labels[:3]):
            trend_class = "positive" if index == 0 else ("neutral" if index == 1 else "negative")
            metric_value = _enterprise_metric_value_for_label(label, real_numbers, used_metric_values, index)
            if metric_value is None:
                cards.append(
                    f"""
                    <div class="ent-kpi-card reveal">
                        <div class="ent-kpi-label" style="text-transform:none;font-size:clamp(13px,1.3vw,16px);letter-spacing:0;max-width:260px">{_escape(label)}</div>
                    </div>
                    """
                )
                continue
            cards.append(
                f"""
                    <div class="ent-kpi-card reveal">
                        <div class="ent-kpi-number {trend_class}">{_escape(metric_value)}</div>
                        <div class="ent-kpi-label">{_escape(label)}</div>
                    </div>
                    """
            )
        kpi_row = f'<div class="ent-kpi-row">{"".join(cards)}</div>'
    else:
        # No real numbers: render as text cards instead of big-number KPIs
        labels = _spec_display_items(spec, limit=3)
        cards = []
        for item in labels[:3]:
            cards.append(
                f"""
                <div class="ent-kpi-card reveal">
                    <div class="ent-kpi-label" style="text-transform:none;font-size:clamp(13px,1.3vw,16px);letter-spacing:0;max-width:260px">{_escape(item)}</div>
                </div>"""
            )
        kpi_row = f'<div class="ent-kpi-row">{"".join(cards)}</div>'

    subtitle_html = f'<p class="ent-kpi-meta reveal">{_escape(spec["key_point"])}</p>' if not is_cover else f'<p style="font-size:clamp(16px,2vw,22px);color:var(--text-muted);margin-top:clamp(8px,1.5vw,16px);margin-bottom:clamp(24px,3vw,40px);line-height:1.5;" class="reveal">{_escape(spec["key_point"])}</p>'
    section_class = "enterprise-dashboard" if not is_cover else "enterprise-dashboard"

    return f"""
    <section class="slide {section_class}" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="kpi_dashboard">
        <div class="slide-content">
            <div class="ent-shell">
                <span class="ent-label-tag reveal">AI landscape</span>
                {title_tag}
                <div class="ent-sep reveal"></div>
                {subtitle_html}
{kpi_row}
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
    title_tag = _title_tag(
        "h2",
        "ent-title",
        spec["title"],
        preset="Enterprise Dark",
        layout_id=spec["layout_id"],
        force_balance=True,
    )
    labels = "".join(f'<div class="ent-split-label">{_escape(item)}</div>' for item in _spec_display_items(spec, limit=3))
    pairs = _spec_detail_pairs(spec, count=3)
    accent_colors = ["ent-accent-cyan", "ent-accent-blue", "ent-accent-violet"]
    rows = "".join(
        f"""
        <div class="ent-feature-row reveal">
            <div class="ent-feature-icon {accent_colors[index % len(accent_colors)]}">{index + 1}</div>
            <div style="flex:1;">
                <h3 class="ent-split-item-title">{_escape(title)}</h3>
                <p class="ent-split-item-copy">{_escape(body)}</p>
                <div class="ent-prog-bar" style="margin-top:10px;"><div class="ent-prog-fill" style="width:{70 - index * 15}%"></div></div>
            </div>
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
        row_items = _enterprise_table_items(spec, minimum=4, limit=4)
        while len(row_items) < 4:
            row_items.append(spec["visual"])
        for index, item in enumerate(row_items[:4]):
            badge = "weekly" if index < 2 else "monthly"
            dot = "ent-dot-blue" if index < 2 else "ent-dot-green"
            signal, meaning = _enterprise_table_cells(
                item,
                "把 AI 使用率、模板复用率、评测通过率和场景 ROI 纳入固定治理节奏",
            )
            rows.append(
                f"<tr><td><span class=\"ent-status-dot {dot}\"></span>{_escape(signal)}</td><td>{_escape(meaning)}</td><td><span class=\"ent-badge {'ent-badge-green' if index >= 2 else 'ent-badge-blue'}\">{badge}</span></td></tr>"
            )
        headers = "<thead><tr><th>Ritual</th><th>Decision focus</th><th>Cadence</th></tr></thead>"
        label = "governance"
    else:
        for index, item in enumerate(_enterprise_table_items(spec, minimum=3, limit=4)[:4]):
            dot = "ent-dot-green" if index == 0 else ("ent-dot-blue" if index == 1 else "ent-dot-red")
            signal, meaning = _enterprise_table_cells(item, spec["key_point"])
            rows.append(
                f"<tr><td><span class=\"ent-status-dot {dot}\"></span>{_escape(signal)}</td><td>{_escape(meaning)}</td><td><span class=\"ent-badge {'ent-badge-green' if index == 0 else 'ent-badge-blue'}\">{_escape(spec['role'])}</span></td></tr>"
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
    arch_accents = ["var(--accent-cyan)", "var(--accent-blue)", "var(--accent-violet)"]
    cards = "".join(
        f'<div class="ent-arch-card reveal"><div class="ent-label" style="color:{arch_accents[index % len(arch_accents)]};">{index + 1:02d}</div><h3 style="margin:6px 0;color:var(--text-primary);">{_escape(title)}</h3><p style="margin:0;color:var(--text-body);line-height:1.5;">{_escape(body)}</p></div>'
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
    badge_classes = ["ent-badge-blue", "ent-badge-blue", "ent-badge-blue", "ent-badge-blue"]
    cards = []
    for index, (item, body) in enumerate(pairs[:4]):
        cards.append(
            f"""
            <div class="ent-feature-card reveal">
                <div class="ent-feature-card-head">
                    <div>
                        <div class="ent-label" style="color:var(--accent-cyan);">{_escape(item)}</div>
                        <h3 style="margin:8px 0 0;color:var(--text-primary);">{_escape(item)}</h3>
                    </div>
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
    matrix_accents = ["var(--accent-blue)", "var(--accent-cyan)", "var(--accent-amber)", "var(--accent-violet)"]
    cells = "".join(
        f"""
        <div class="ent-kpi-card reveal">
            <div class="ent-label" style="color:{matrix_accents[index % len(matrix_accents)]};">{_escape(title)}</div>
            <h3 style="margin:8px 0;color:var(--text-primary);">{_escape(title)}</h3>
            <p style="margin:0;color:var(--text-body);line-height:1.5;">{_escape(body)}</p>
        </div>
        """
        for index, (title, body) in enumerate(pairs[:4])
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


def _render_enterprise_contrast_split(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("h2", "ent-title", spec["title"], preset="Enterprise Dark", layout_id=spec["layout_id"])
    items = _spec_display_items(spec, limit=4)
    if len(items) >= 4:
        neg_items = items[:len(items) // 2]
        pos_items = items[len(items) // 2:]
    else:
        neg_items = items[:1] + [spec["key_point"]]
        pos_items = items[1:] + [spec["key_point"]]
    neg_rows = "".join(
        f'<div class="ent-contrast-item"><span class="ent-contrast-marker">&#x2717;</span>{_escape(item)}</div>'
        for item in neg_items
    )
    pos_rows = "".join(
        f'<div class="ent-contrast-item"><span class="ent-contrast-marker">&#x2713;</span>{_escape(item)}</div>'
        for item in pos_items
    )
    return f"""
    <section class="slide enterprise-contrast" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="contrast_split">
        <div class="slide-content">
            <div class="ent-shell">
                <span class="ent-label-tag reveal">对比</span>
                {title_tag}
                <div class="ent-sep reveal"></div>
                <div class="ent-contrast-split reveal">
                    <div class="ent-contrast-block ent-contrast-block--negative">
                        <h4>Before</h4>
                        {neg_rows}
                    </div>
                    <div class="ent-contrast-block ent-contrast-block--positive">
                        <h4>After</h4>
                        {pos_rows}
                    </div>
                </div>
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
    dot_accents = ["var(--accent-blue)", "var(--accent-cyan)", "var(--accent-amber)", "var(--accent-green)"]
    for idx in range(4):
        items.append(
            f"""
            <div class="ent-timeline-item reveal">
                <div class="ent-timeline-dot" style="background:{dot_accents[idx]};"></div>
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
    metric_values = _spec_explicit_numbers(spec)[:3]
    used_metric_values: set[str] = set()
    card_html = []
    for index, item in enumerate(items[:3]):
        metric_value = _enterprise_metric_value_for_label(item, metric_values, used_metric_values, index)
        trend_class = "positive" if index == 2 else "neutral"
        if metric_value is None:
            card_html.append(
                f'<div class="ent-kpi-card reveal"><div class="ent-kpi-label" style="text-transform:none;font-size:clamp(13px,1.3vw,16px);letter-spacing:0;max-width:260px">{_escape(item)}</div></div>'
            )
        else:
            card_html.append(
                f'<div class="ent-kpi-card reveal"><div class="ent-kpi-number {trend_class}">{_escape(metric_value)}</div><div class="ent-kpi-label">{_escape(item)}</div></div>'
            )
    return f"""
    <section class="slide enterprise-close" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="cta_close">
        <div class="slide-content">
            <div class="ent-shell">
                <span class="ent-label-tag reveal">close</span>
                {title_tag}
                <div class="ent-sep reveal"></div>
                <div class="ent-code reveal"><span class="green">thesis</span> = {_escape(spec['key_point'])}</div>
                <div class="ent-kpi-row" style="margin-top:18px;">
                    {''.join(card_html)}
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
    if spec["layout_id"] == "contrast_split":
        return _render_enterprise_contrast_split(spec, total)
    if spec["layout_id"] == "data_table":
        return _render_enterprise_data_table(spec, total)
    if spec["layout_id"] == "architecture_map":
        return _render_enterprise_architecture_map(spec, total)
    if spec["layout_id"] == "comparison_matrix":
        if spec["role"] in {"feature", "features", "interaction"}:
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
    return _assemble_shell_html(brief["title"], brief["language"], "Enterprise Dark", css, slides_html, total, packet)


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
.chart-line { stroke: var(--chart-primary); stroke-width: 3.2; fill: none; stroke-linecap: round; stroke-linejoin: round; }
.chart-label, .chart-val { fill: var(--text-muted); font-size: 10px; font-family: inherit; font-variant-numeric: tabular-nums; }
.chart-val { fill: var(--text); }
.ds-signal-map { width: 100%; height: auto; max-height: 240px; }
.ds-signal-link { stroke: var(--chart-primary); stroke-width: 2.4; fill: none; stroke-linecap: round; stroke-dasharray: 6 8; opacity: 0.72; }
.ds-signal-node { fill: var(--bg-card); stroke: var(--chart-primary); stroke-width: 2.2; }
.ds-signal-node.secondary { stroke: var(--chart-secondary); }
.ds-signal-node.tertiary { stroke: var(--chart-tertiary); }
.ds-signal-label { fill: var(--text); font-size: 12px; font-weight: 800; text-anchor: middle; dominant-baseline: middle; }
.ds-signal-bars,
.ds-flow-map,
.ds-phase-timeline,
.ds-evidence-ladder,
.ds-state-grid-svg { width: 100%; height: auto; max-height: 240px; }
.ds-bar-track { fill: rgba(148, 163, 184, 0.12); }
.ds-bar-fill { fill: var(--chart-primary); }
.ds-bar-fill.secondary { fill: var(--chart-secondary); }
.ds-bar-fill.tertiary { fill: var(--chart-tertiary); }
.ds-svg-label { fill: var(--text); font-size: 11px; font-weight: 800; dominant-baseline: middle; }
.ds-svg-muted { fill: var(--text-muted); font-size: 10px; font-weight: 700; dominant-baseline: middle; }
.ds-flow-path { stroke: var(--chart-primary); stroke-width: 2.8; fill: none; stroke-linecap: round; stroke-linejoin: round; }
.ds-flow-node { fill: var(--bg-card); stroke: var(--chart-primary); stroke-width: 2.2; }
.ds-flow-node.secondary { stroke: var(--chart-secondary); }
.ds-flow-node.tertiary { stroke: var(--chart-tertiary); }
.ds-ladder-rail { stroke: var(--axis-line); stroke-width: 2; }
.ds-ladder-rung { stroke: var(--chart-primary); stroke-width: 3; stroke-linecap: round; }
.ds-ladder-rung.secondary { stroke: var(--chart-secondary); }
.ds-ladder-rung.tertiary { stroke: var(--chart-tertiary); }
.ds-state-cell { fill: rgba(59, 130, 246, 0.09); stroke: var(--border); stroke-width: 1; }
.ds-state-cell.hot { fill: rgba(59, 130, 246, 0.18); stroke: var(--chart-primary); }

.ds-chart-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 18px;
}

.ds-chart-visual {
    min-height: min(44vh, 380px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: clamp(4px, 1vw, 12px);
    overflow: visible;
}

.ds-chart-visual .ds-chart-svg {
    display: block;
    width: auto;
    height: min(44vh, 380px);
    max-width: 100%;
    max-height: none;
    margin: 0 auto;
}

body[data-preset="Data Story"] .ds-kpi-chart .slide-content {
    justify-content: flex-start;
}

body[data-preset="Data Story"] .ds-kpi-chart .ds-shell,
body[data-preset="Data Story"] .ds-grid .ds-shell {
    min-height: 0;
    max-height: calc(100vh - clamp(48px, 8vw, 104px));
    display: flex;
    flex-direction: column;
}

body[data-preset="Data Story"] .ds-kpi-chart .ds-split-layout {
    flex: 1 1 auto;
    min-height: 0;
    height: auto;
    padding: clamp(12px, 2vw, 28px);
    align-items: stretch;
}

body[data-preset="Data Story"] .ds-kpi-chart .ds-kpi-grid,
body[data-preset="Data Story"] .ds-grid .ds-kpi-grid {
    min-height: 0;
}

body[data-preset="Data Story"] .ds-kpi-chart .ds-kpi-card,
body[data-preset="Data Story"] .ds-grid .ds-kpi-card {
    min-height: 0;
    padding: clamp(12px, 1.6vw, 18px);
}

body[data-preset="Data Story"] .ds-kpi-chart .ds-kpi,
body[data-preset="Data Story"] .ds-grid .ds-kpi {
    font-size: clamp(2.1rem, 5vw, 4.6rem);
    overflow-wrap: normal;
}

body[data-preset="Data Story"] .ds-kpi-chart .ds-kpi-label,
body[data-preset="Data Story"] .ds-grid .ds-kpi-label {
    line-height: 1.42;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

body[data-preset="Data Story"] .ds-kpi-chart .ds-chart-card {
    min-width: 0;
    min-height: 0;
    display: flex;
    align-items: center;
    justify-content: center;
}

body[data-preset="Data Story"] .ds-kpi-chart .ds-chart-svg {
    max-height: min(42vh, 360px);
}

.ds-chart-insight .ds-heading,
.ds-workflow .ds-heading,
.ds-grid .ds-heading,
.ds-kpi-chart .ds-heading {
    max-width: min(1040px, 94%);
}

.ds-chart-insight .ds-chart-card {
    padding: 12px 14px;
}

.ds-chart-insight .ds-chart-visual {
    min-height: min(42vh, 350px);
}

.ds-chart-insight .ds-chart-visual .ds-chart-svg {
    height: min(42vh, 350px);
    max-height: none;
}

.ds-chart-insight .ds-chart-svg {
    display: block;
    max-height: 188px;
    min-height: 176px;
    margin: 0 auto;
}

.ds-chart-insight .ds-insight {
    margin-top: 16px;
}

.ds-interaction-layout {
    display: grid;
    grid-template-columns: minmax(0, 1.08fr) minmax(260px, 0.92fr);
    gap: clamp(14px, 2vw, 24px);
    align-items: stretch;
    min-height: 0;
}

.ds-key-strip {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: clamp(10px, 1.4vw, 16px);
}

.ds-key-card,
.ds-mini-console {
    min-width: 0;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: clamp(14px, 1.6vw, 20px);
}

.ds-key-card {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.ds-keycap {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: fit-content;
    min-width: 44px;
    height: 34px;
    padding: 0 12px;
    border: 1px solid var(--axis-line);
    border-radius: 6px;
    color: var(--text);
    background: rgba(15, 17, 23, 0.58);
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0;
}

.ds-key-title {
    margin: 0;
    color: var(--text);
    font-size: clamp(0.96rem, 1.45vw, 1.15rem);
    line-height: 1.28;
}

.ds-key-copy {
    margin: 0;
    color: var(--text-muted);
    font-size: clamp(0.82rem, 1.1vw, 0.94rem);
    line-height: 1.45;
    overflow-wrap: anywhere;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.ds-mini-console {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 12px;
}

.ds-console-row {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
}

.ds-console-row:last-child {
    border-bottom: 0;
    padding-bottom: 0;
}

.ds-console-row span {
    color: var(--text-muted);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.ds-console-row strong {
    min-width: 0;
    color: var(--text);
    font-size: clamp(0.92rem, 1.35vw, 1.08rem);
    line-height: 1.3;
    text-align: right;
    overflow-wrap: anywhere;
}

body[data-preset="Data Story"] .ds-comparison .ds-matrix {
    flex: 1 1 auto;
    gap: 0;
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
    background: rgba(26, 31, 46, 0.72);
    height: min(52vh, 360px);
    min-height: 0;
}

body[data-preset="Data Story"] .ds-comparison .ds-matrix-cell {
    border: 0;
    border-radius: 0;
    background: transparent;
    padding: clamp(16px, 2vw, 24px);
    justify-content: flex-start;
    gap: 12px;
}

body[data-preset="Data Story"] .ds-comparison .ds-matrix-cell:nth-child(odd) {
    border-right: 1px solid var(--border);
}

body[data-preset="Data Story"] .ds-comparison .ds-matrix-cell:nth-child(-n+2) {
    border-bottom: 1px solid var(--border);
}

body[data-preset="Data Story"] .ds-comparison .ds-matrix-index {
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
}

body[data-preset="Data Story"] .ds-comparison .ds-matrix-title {
    margin: 0;
    font-size: clamp(1.05rem, 1.65vw, 1.35rem);
    line-height: 1.28;
    color: var(--text);
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

body[data-preset="Data Story"] .ds-comparison .ds-matrix-copy {
    margin: 0;
    color: var(--text);
    line-height: 1.5;
    font-size: clamp(0.84rem, 1.25vw, 0.96rem);
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.ds-cover-hero .ds-heading {
    font-size: clamp(3rem, 7.4vw, 6rem);
    letter-spacing: 0;
}

.ds-cover-metric {
    display: inline-flex;
    align-items: baseline;
    justify-content: center;
    gap: 12px;
    margin: 4px auto 0;
}

.ds-cover-metric .ds-kpi {
    font-size: clamp(1.65rem, 4vw, 3.25rem);
}

.ds-cover-metric .ds-kpi-label {
    margin-top: 0;
    font-size: clamp(13px, 1.4vw, 16px);
    line-height: 1.35;
    letter-spacing: 0.02em;
    text-transform: none;
}

body[data-preset="Data Story"] .ds-workflow .ds-shell {
    min-height: 0;
    max-height: calc(100vh - clamp(48px, 8vw, 104px));
    display: flex;
    flex-direction: column;
}

body[data-preset="Data Story"] .ds-workflow .ds-split-layout {
    flex: 1 1 auto;
    min-height: 0;
    height: auto;
    max-height: min(58vh, 456px);
    padding: clamp(12px, 2vw, 24px);
    align-items: stretch;
}

body[data-preset="Data Story"] .ds-workflow .ds-chart-card {
    min-width: 0;
    min-height: 0;
    overflow: hidden;
}

body[data-preset="Data Story"] .ds-workflow .ds-workflow-layout {
    flex: 1 1 auto;
    min-height: 0;
    display: grid;
    grid-template-rows: minmax(0, 1fr) auto;
    gap: clamp(10px, 1.8vw, 18px);
    padding: clamp(6px, 1.2vw, 14px) clamp(8px, 2vw, 24px) 0;
}

body[data-preset="Data Story"] .ds-workflow .ds-workflow-visual {
    min-height: min(46vh, 380px);
}

body[data-preset="Data Story"] .ds-workflow .ds-workflow-visual .ds-chart-svg {
    height: min(46vh, 380px);
}

body[data-preset="Data Story"] .ds-workflow .ds-flow-note {
    margin: 0;
    max-width: none;
}

body[data-preset="Data Story"] .ds-workflow .ds-stage-grid {
    height: 100%;
    min-height: 0;
    gap: clamp(10px, 1.5vw, 16px);
}

body[data-preset="Data Story"] .ds-workflow .ds-stage-card {
    min-height: 0;
    padding: clamp(12px, 1.4vw, 16px);
    gap: 8px;
}

body[data-preset="Data Story"] .ds-workflow .ds-stage-title {
    font-size: clamp(0.92rem, 1.45vw, 1.05rem);
}

body[data-preset="Data Story"] .ds-workflow .ds-stage-copy {
    font-size: clamp(0.82rem, 1.25vw, 0.96rem);
    line-height: 1.42;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
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

.ds-action-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: clamp(10px, 1.4vw, 16px);
}

.ds-action-card {
    min-width: 0;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: clamp(16px, 2vw, 24px);
}

.ds-action-label {
    color: var(--text-muted);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.ds-action-title {
    margin-top: 10px;
    color: var(--text);
    font-size: clamp(1.25rem, 2.4vw, 2rem);
    font-weight: 800;
    line-height: 1.12;
    letter-spacing: 0;
    overflow-wrap: anywhere;
}

.ds-action-copy {
    margin: 10px 0 0;
    color: var(--text);
    font-size: clamp(0.86rem, 1.18vw, 0.98rem);
    line-height: 1.46;
    overflow-wrap: anywhere;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.ds-cta-block {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 20px;
    align-items: end;
}

@media (max-width: 900px) {
    .ds-stage-grid,
    .ds-cta-block,
    .ds-interaction-layout {
        grid-template-columns: 1fr;
    }

    .ds-key-strip,
    .ds-action-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 520px) {
    body[data-preset="Data Story"] .slide {
        padding-left: clamp(16px, 6vw, 28px) !important;
        padding-right: clamp(16px, 6vw, 28px) !important;
    }
    body[data-preset="Data Story"] :is(.slide-content, .content, .ds-shell, .ds-cover-hero) {
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
    }
    body[data-preset="Data Story"] :is(.ds-heading, .title-balance) {
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
    }
    body[data-preset="Data Story"] .title-line {
        display: inline !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
        word-break: normal !important;
    }
    body[data-preset="Data Story"] .ds-comparison .ds-matrix {
        height: min(48vh, 400px);
    }
    body[data-preset="Data Story"] .ds-comparison .ds-matrix-cell {
        padding: 10px;
        gap: 6px;
    }
    body[data-preset="Data Story"] .ds-comparison :is(.ds-matrix-title, .ds-matrix-copy) {
        display: block;
        -webkit-line-clamp: unset;
        overflow: visible;
    }
    body[data-preset="Data Story"] .ds-comparison .ds-matrix-title { font-size: 13px; }
    body[data-preset="Data Story"] .ds-comparison .ds-matrix-copy { font-size: 11.5px; line-height: 1.35; }
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


def _data_story_interaction_keycap(title: str, body: str, index: int) -> str:
    title_blob = str(title or "").lower()
    body_blob = str(body or "").lower()

    if any(token in title_blob for token in ("present", "presenter", "演讲")):
        return "P"
    if any(token in title_blob for token in ("note", "notes", "speaker note", "笔记", "备注")):
        return "Notes"
    if re.search(r"\bf5\b", title_blob):
        return "F5"
    if any(token in title_blob for token in ("edit", "editing", "inline", "编辑")):
        return "E"
    if "play" in title_blob:
        return "F5" if re.search(r"\bf5\b", body_blob) else "P"

    blob = f"{title_blob} {body_blob}"
    if any(token in blob for token in ("note", "notes", "speaker note", "笔记", "备注")):
        return "Notes"
    if re.search(r"\bf5\b", blob):
        return "F5"
    if any(token in blob for token in ("present", "presenter", "play", "演讲", "播放")):
        return "P"
    if any(token in blob for token in ("edit", "editing", "inline", "编辑")):
        return "E"
    return f"K{index}"


def _render_data_story_interaction_panel(spec: dict[str, Any]) -> str:
    pairs = _spec_detail_pairs(spec, count=4)
    cards = []
    for index, (title, body) in enumerate(pairs[:4], start=1):
        keycap = _data_story_interaction_keycap(title, body, index)
        cards.append(
            f"""
            <div class="ds-key-card reveal">
                <div class="ds-keycap">{_escape(keycap)}</div>
                <h3 class="ds-key-title">{_escape(title)}</h3>
                <p class="ds-key-copy">{_escape(body)}</p>
            </div>
            """
        )

    mode = " / ".join(_dedupe_preserve([pairs[0][0], pairs[1][0]])[:2])
    edit = " / ".join(_dedupe_preserve([pairs[2][0], pairs[3][0]])[:2])
    loop = _compact_display_token(spec["key_point"], fallback="Live deck")
    return f"""
    <div class="ds-interaction-layout">
        <div class="ds-key-strip">{"".join(cards)}</div>
        <div class="ds-mini-console reveal">
            <div class="ds-console-row"><span>Mode</span><strong>{_escape(mode)}</strong></div>
            <div class="ds-console-row"><span>Edit</span><strong>{_escape(edit)}</strong></div>
            <div class="ds-console-row"><span>Loop</span><strong>{_escape(loop)}</strong></div>
        </div>
    </div>
    """.strip()


def _data_story_has_numeric_cta_signal(spec: dict[str, Any], items: list[str]) -> bool:
    return bool(
        _primary_numbers_from_numeric_facts(spec)
        or _spec_explicit_numbers(spec)
        or _extract_numbers(" ".join(items))
    )


def _split_data_story_action_text(title: str, body: str) -> tuple[str, str]:
    cleaned_title = re.sub(r"\s+", " ", str(title or "")).strip()
    cleaned_body = re.sub(r"\s+", " ", str(body or "")).strip()
    match = re.match(r"^([^:：]{1,36})[:：]\s*(.+)$", cleaned_title)
    if match:
        action_title = match.group(1).strip()
        action_body = match.group(2).strip()
        return action_title, action_body
    return cleaned_title, cleaned_body


def _render_data_story_action_grid(spec: dict[str, Any]) -> str:
    cards = []
    for index, (title, body) in enumerate(_spec_detail_pairs(spec, count=2)[:2], start=1):
        action_title, action_body = _split_data_story_action_text(title, body)
        cards.append(
            f"""
            <div class="ds-action-card reveal">
                <div class="ds-action-label">action {index:02d}</div>
                <div class="ds-action-title">{_escape(action_title)}</div>
                <p class="ds-action-copy">{_escape(action_body)}</p>
            </div>
            """
        )
    return f'<div class="ds-action-grid">{"".join(cards)}</div>'


def _cover_summary_without_metric_label(summary: str, label: str) -> str:
    summary = re.sub(r"\s+", " ", summary or "").strip()
    label = re.sub(r"\s+", " ", label or "").strip()
    if not summary or not label:
        return summary
    if summary.startswith(label):
        remainder = summary[len(label):]
        remainder = re.sub(r"^[\s，。、；;,:：]+", "", remainder).strip()
        return remainder or summary
    return summary


def _render_data_story_hero_number(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("h1", "ds-heading", spec["title"], preset="Data Story", layout_id=spec["layout_id"])
    value = _metric_values_from_spec(spec, [_compact_display_token(spec["title"], fallback="关键")])[0]
    label = _split_supporting_phrases(spec["key_point"], minimum=1)[0]
    if spec["role"] == "cover":
        summary = _cover_summary_without_metric_label(spec["key_point"], label)
        return f"""
    <section class="slide ds-hero-number ds-cover-hero" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="hero_number">
        <div class="slide-content ds-hero-slide">
            <div class="ds-shell">
                <div class="ds-subhead reveal">AI industry landscape</div>
                {title_tag}
                <div class="ds-cover-metric reveal">
                    <div class="ds-kpi positive">{_escape(value)}</div>
                    <div class="ds-kpi-label">{_escape(label)}</div>
                </div>
                <p style="max-width:42rem;margin:0 auto;color:var(--text);line-height:1.6;" class="ds-cover-summary reveal">{_escape(summary)}</p>
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()
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
        value = _metric_value_for_item(item, spec, index=index, used_tokens=used_tokens, numeric_only=True)
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


def _render_data_story_visual_container(content: str, *, extra_class: str = "") -> str:
    if "<svg" not in content:
        return f'<div class="ds-chart-card reveal">{content}</div>'
    classes = " ".join(part for part in ("ds-chart-visual", extra_class, "reveal") if part)
    return f'<div class="{classes}">{content}</div>'


def _render_data_story_chart_insight(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    title_tag = _title_tag("h2", "ds-heading", spec["title"], preset="Data Story", layout_id=spec["layout_id"])
    chart_values = _chart_metric_values_from_spec(spec, ["1", "2", "3", "4"])
    if spec["role"] == "interaction" and not chart_values:
        chart_container = _render_data_story_interaction_panel(spec)
    elif chart_values and spec.get("chart_policy") != "avoid":
        insight_body = _svg_line_chart(_chart_labels_from_spec(spec, count=4), chart_values)
        chart_container = _render_data_story_visual_container(insight_body)
    elif spec.get("chart_policy") == "avoid":
        insight_body = _render_data_story_stage_grid(spec, count=4, prefix="evidence")
        chart_container = _render_data_story_visual_container(insight_body)
    else:
        insight_body = _data_story_non_numeric_svg(spec)
        chart_container = _render_data_story_visual_container(insight_body)
    return f"""
    <section class="slide ds-chart-insight" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="chart_insight">
        <div class="slide-content">
            <div class="ds-shell">
                <div class="ds-subhead reveal">trend</div>
                {title_tag}
                <div class="ds-divider reveal"></div>
                {chart_container}
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
            <div class="ds-matrix-index">Quadrant {index + 1:02d}</div>
            <h3 class="ds-matrix-title">{_escape(title)}</h3>
            <p class="ds-matrix-copy">{_escape(body)}</p>
        </div>
        """
        for index, (title, body) in enumerate(pairs[:4])
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
    numeric_fact_count = len(_primary_numbers_from_numeric_facts(spec))
    card_count = numeric_fact_count if 3 <= numeric_fact_count < 4 else 4
    items = _spec_display_items(spec, limit=card_count)
    cards = []
    for index, item in enumerate(items[:card_count]):
        tone = "positive" if index == 0 else ("negative" if index == 2 else "neutral")
        value = _metric_value_for_item(item, spec, index=index, numeric_only=True)
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
    if chart_values and spec.get("chart_policy") != "avoid":
        chart = _svg_line_chart(_chart_labels_from_spec(spec, count=4, family="workflow"), chart_values)
    elif spec.get("chart_policy") == "avoid":
        chart = _render_data_story_stage_grid(spec, count=4, prefix="phase")
    else:
        chart = _data_story_non_numeric_svg(spec)
    chart_container = _render_data_story_visual_container(chart, extra_class="ds-workflow-visual")
    return f"""
    <section class="slide ds-workflow" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="workflow_chart">
        <div class="slide-content">
            <div class="ds-shell">
                <div class="ds-subhead reveal">workflow</div>
                {title_tag}
                <div class="ds-divider reveal"></div>
                <div class="ds-workflow-layout">
                    {chart_container}
                    <div class="ds-flow-note ds-insight reveal"><strong>Flow:</strong> {_escape(spec['key_point'])}</div>
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
    if not _data_story_has_numeric_cta_signal(spec, items):
        action_grid = _render_data_story_action_grid(spec)
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
                {action_grid}
            </div>
        </div>
        <span class="slide-num-label">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()

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
    return _assemble_shell_html(brief["title"], brief["language"], "Data Story", css, slides_html, total, packet)


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


def _compact_vertical_title(text: str) -> str:
    normalized = re.sub(r"\s+", "", text or "")
    if not normalized:
        return "答案"

    semantic_pairs = [
        (("先问", "自己"), "先问自己"),
        (("意义",), "意义"),
        (("方向",), "方向"),
        (("判断",), "判断"),
        (("连接",), "连接"),
        (("创造",), "创造"),
        (("责任",), "责任"),
        (("承担",), "承担"),
    ]
    for needles, label in semantic_pairs:
        if all(needle in normalized for needle in needles):
            return label

    segments = [segment.strip() for segment in re.split(r"[，。；、,:：]", text) if segment.strip()]
    prefix_patterns = (
        r"^(?:而在于|不在于|在于|终究不在于|终究|与其问|不如先问|我愿意把自己训练成|我愿意把自己|我愿意)",
    )
    for segment in reversed(segments):
        compact = segment
        for pattern in prefix_patterns:
            updated = re.sub(pattern, "", compact).strip()
            if updated:
                compact = updated
        compact = re.sub(r"^(?:你|我)", "", compact).strip()
        normalized_compact = re.sub(r"\s+", "", compact)
        if 2 <= len(normalized_compact) <= 6:
            return compact

    if len(normalized) <= 6:
        return text
    return _compact_display_token(text, fallback="答案")


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
    # Fix 2 v2: alternate ornament per slide (rule ↔ ghost ↔ vline)
    _ornament_cycle = ("rule", "ghost", "vline")
    _orn_type = _ornament_cycle[(slide_number - 1) % len(_ornament_cycle)]
    if _orn_type == "ghost":
        _ornament = f'\n        {_chinese_chan_ghost(spec)}'
        _rule = ""
    elif _orn_type == "vline":
        _ornament = '<div class="reveal" style="margin-top:26px;"><div class="zen-vline"></div></div>'
        _rule = ""
    else:
        _ornament = ""
        _rule = '<div class="zen-rule reveal"><span class="zen-rule-line"></span></div>'
    return f"""
    <section class="slide" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="zen_split">
        <div class="zen-content">
            <span class="zen-caption reveal">{_escape(_chinese_chan_caption(spec, language))}</span>
            {title_tag}
            {_rule}
            <div class="zen-paragraph-stack">
                <p class="zen-body zen-cn reveal">{_escape(spec['key_point'])}</p>
                <ul class="zen-list zen-body zen-cn reveal">{list_html}</ul>
            </div>
        </div>
        {_ornament}
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
    # Fix 2 v2: alternate ornament per slide (rule ↔ ghost ↔ vline)
    _ornament_cycle = ("rule", "ghost", "vline")
    _orn_type = _ornament_cycle[(slide_number - 1) % len(_ornament_cycle)]
    if _orn_type == "ghost":
        _ornament = f'\n        {_chinese_chan_ghost(spec)}'
        _rule = ""
    elif _orn_type == "vline":
        _ornament = '<div class="reveal" style="margin-top:26px;"><div class="zen-vline"></div></div>'
        _rule = ""
    else:
        _ornament = ""
        _rule = '<div class="zen-rule reveal"><span class="zen-rule-line"></span></div>'
    return f"""
    <section class="slide" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(spec['role'])}" data-export-role="zen_stat">
        <div class="zen-content">
            <span class="zen-caption reveal">{_escape(_chinese_chan_caption(spec, language))}</span>
            {title_tag}
            {_rule}
            <div class="zen-stat-row">
                {''.join(cards)}
            </div>
            <p class="zen-body zen-cn reveal" style="text-align:center;">{_escape(spec['key_point'])}</p>
        </div>
        {_ornament}
        <span class="slide-num-label zen-caption">{slide_number:02d} / {total:02d}</span>
    </section>
    """.strip()


def _render_chinese_chan_vertical(spec: dict[str, Any], total: int) -> str:
    slide_number = spec["slide_number"]
    raw_title = re.sub(r"\s+", "", spec["title"])
    title_text = _compact_vertical_title(spec["title"]) if len(raw_title) > 8 else spec["title"]
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


def _extract_blue_sky_js(starter_path: Path, total: int) -> str:
    """Extract the <script> block from blue-sky-starter.html, updating TOTAL."""
    content = _read_text(starter_path)
    match = re.search(r"<script>(.*?)</script>", content, re.DOTALL)
    if not match:
        return ""
    js = match.group(1).strip()
    # Update TOTAL to match actual slide count
    js = re.sub(r'const TOTAL\s*=\s*\d+', f'const TOTAL = {total}', js)
    return js


def _blue_sky_watermark_script(*, preset: str, version: str) -> str:
    watermark_text = json.dumps(
        f"By kai-slide-creator v{version} · {preset}",
        ensure_ascii=False,
    )
    return f"""
(function() {{
    var slides = document.querySelectorAll('#track .slide');
    if (!slides.length) return;
    var last = slides[slides.length - 1];
    var credit = document.createElement('div');
    credit.className = 'slide-credit';
    credit.textContent = {watermark_text};
    last.appendChild(credit);
}})();
""".strip()


def _blue_sky_title_tag(tag: str, text: str, *, layout_id: str, extra_attrs: str = "") -> str:
    normalized = _normalize_title_text(text)
    nowrap_limit = 18.5 if tag.lower() == "h1" else 22.5
    if _title_visual_units(normalized) <= nowrap_limit:
        attrs = 'class="gt reveal title-nowrap"'
        if extra_attrs:
            attrs += f" {extra_attrs}"
        return f"<{tag} {attrs}>{_escape(normalized)}</{tag}>"

    return _title_tag(
        tag,
        "gt",
        text,
        preset="Blue Sky",
        layout_id=layout_id,
        force_balance=False,
        extra_attrs=extra_attrs,
    )


def _blue_sky_display_items(spec: dict[str, Any], *, limit: int | None = None) -> list[str]:
    items = _dedupe_preserve(
        [
            *[str(item) for item in spec.get("supporting_facts", [])],
            *[str(item) for item in spec.get("supporting_items", [])],
            *[str(item) for item in spec.get("evidence_items", [])],
        ]
    )
    if not items:
        items = _split_supporting_phrases(spec.get("key_point", ""), minimum=1)
    if not items:
        items = [str(spec.get("key_point") or spec.get("title") or "")]
    return items[:limit] if limit is not None else items


def _blue_sky_item_parts(item: str) -> tuple[str, str]:
    cleaned = re.sub(r"\s+", " ", str(item or "")).strip()
    match = re.match(r"^(.{1,48}?)(?:\s+[—–-]\s+|[:：]\s*)(.+)$", cleaned)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return cleaned, ""


def _blue_sky_keycap(title: str, body: str, index: int) -> str:
    blob = f"{title} {body}".lower()
    if re.search(r"\bf5\b", blob):
        return "F5"
    if re.search(r"\bp\b", blob) or any(token in blob for token in ("presenter", "present", "演讲")):
        return "P"
    if re.search(r"\be\b", blob) or any(token in blob for token in ("edit", "inline", "编辑")):
        return "E"
    if any(token in blob for token in ("note", "notes", "笔记", "备注")):
        return "Notes"
    return f"{index}"


def _blue_sky_metric_label(item: str, value: str) -> str:
    label = _strip_chart_label_prefix(str(item or "")).strip()
    if value:
        label = re.sub(rf"^\s*{re.escape(value)}\s*[%％]?\s*", "", label).strip()
    label = re.sub(r"^[种个项层类]\s*", "", label).strip()
    return label or "指标"


def _blue_sky_add_metric(metrics: list[tuple[str, str]], value: str, label: str) -> None:
    pair = (value.strip(), label.strip())
    if not pair[0] or not pair[1] or pair in metrics:
        return
    metrics.append(pair)


def _blue_sky_cover_metrics(spec: dict[str, Any], items: list[str]) -> list[tuple[str, str]]:
    metrics: list[tuple[str, str]] = []
    for item in items:
        numbers = _extract_numbers(str(item))
        if numbers:
            value = numbers[0]
            _blue_sky_add_metric(metrics, value, _blue_sky_metric_label(str(item), value))

    blob = " ".join([str(spec.get("title", "")), str(spec.get("key_point", "")), *items])
    has_cjk = bool(re.search(r"[\u3400-\u9fff]", blob))
    has_zero_dependency = bool(
        re.search(r"零依赖|zero[- ]?dependency|zero dependencies|no dependencies", blob, re.IGNORECASE)
    )
    if has_zero_dependency:
        _blue_sky_add_metric(metrics, "0", "依赖" if has_cjk else "Dependencies")
    if has_zero_dependency or re.search(r"浏览器|browser|html", blob, re.IGNORECASE):
        _blue_sky_add_metric(metrics, "100%", "浏览器运行" if has_cjk else "Browser-native")
    if len(metrics) < 3 and re.search(r"单\s*HTML|single\s+html|html\s+file", blob, re.IGNORECASE):
        _blue_sky_add_metric(metrics, "1", "HTML 文件" if has_cjk else "HTML file")

    return metrics[:3]


def _blue_sky_cover_pill_text(spec: dict[str, Any], items: list[str], metrics: list[tuple[str, str]]) -> str:
    subtitle = str(spec.get("subtitle") or "").strip()
    if subtitle:
        return subtitle
    for item in items:
        if _extract_numbers(str(item)):
            return str(item).strip()
    if metrics:
        value, label = metrics[0]
        return f"{value} {label}".strip()
    return "Blue Sky"


def _blue_sky_bento_variant(spec: dict[str, Any]) -> int:
    role = str(spec.get("role") or "").strip().lower()
    role_variants = {
        "features": 0,
        "feature": 0,
        "design-philosophy": 1,
        "style-discovery": 1,
        "recommendation": 1,
        "best-fit": 1,
    }
    if role in role_variants:
        return role_variants[role]
    try:
        return int(spec.get("slide_number") or 0)
    except (TypeError, ValueError):
        return 0


def _blue_sky_bento_card_placement(index: int, total: int, *, variant: int = 0) -> tuple[str, str]:
    if total >= 6:
        placement_variants = [
            [
                ("g span2", "grid-column:1 / span 2;grid-row:1;"),
                ("g span2", "grid-column:3 / span 2;grid-row:1;"),
                ("g span2 row2", "grid-column:1 / span 2;grid-row:2 / span 2;"),
                ("g", "grid-column:3;grid-row:2;"),
                ("g", "grid-column:4;grid-row:2;"),
                ("g span2", "grid-column:3 / span 2;grid-row:3;"),
            ],
            [
                ("g span2 row2", "grid-column:3 / span 2;grid-row:1 / span 2;"),
                ("g", "grid-column:1;grid-row:1;"),
                ("g", "grid-column:2;grid-row:1;"),
                ("g span2", "grid-column:1 / span 2;grid-row:2;"),
                ("g span2", "grid-column:1 / span 2;grid-row:3;"),
                ("g span2", "grid-column:3 / span 2;grid-row:3;"),
            ],
        ]
    elif total == 5:
        placement_variants = [
            [
                ("g span2", "grid-column:1 / span 2;grid-row:1;"),
                ("g span2", "grid-column:3 / span 2;grid-row:1;"),
                ("g span2", "grid-column:1 / span 2;grid-row:2;"),
                ("g span2", "grid-column:3 / span 2;grid-row:2;"),
                ("g", "grid-column:1 / span 4;grid-row:3;"),
            ],
            [
                ("g span2 row2", "grid-column:1 / span 2;grid-row:1 / span 2;"),
                ("g span2", "grid-column:3 / span 2;grid-row:1;"),
                ("g", "grid-column:3;grid-row:2;"),
                ("g", "grid-column:4;grid-row:2;"),
                ("g", "grid-column:1 / span 4;grid-row:3;"),
            ],
        ]
    else:
        placement_variants = [
            [
                ("g span2", "grid-column:1 / span 2;grid-row:1;"),
                ("g span2", "grid-column:3 / span 2;grid-row:1;"),
                ("g span2", "grid-column:1 / span 2;grid-row:2;"),
                ("g span2", "grid-column:3 / span 2;grid-row:2;"),
            ],
            [
                ("g span2 row2", "grid-column:1 / span 2;grid-row:1 / span 2;"),
                ("g span2", "grid-column:3 / span 2;grid-row:1;"),
                ("g", "grid-column:3;grid-row:2;"),
                ("g", "grid-column:4;grid-row:2;"),
            ],
        ]
    placements = placement_variants[variant % len(placement_variants)]
    return placements[index % len(placements)]


def _render_blue_sky_bento_cards(spec: dict[str, Any], items: list[str]) -> str:
    visible_items = items[:6]
    placement_variant = _blue_sky_bento_variant(spec)
    cards = []
    for index, item in enumerate(visible_items):
        title, body = _blue_sky_item_parts(item)
        card_class, card_style = _blue_sky_bento_card_placement(index, len(visible_items), variant=placement_variant)
        numbers = _extract_numbers(item)
        stat_html = ""
        display_title = title
        if numbers and index < 3:
            stat_html = f'<div class="stat" style="font-size:2.2rem;margin-bottom:6px;">{_escape(numbers[0])}</div>'
            display_title = _blue_sky_metric_label(title, numbers[0])
        body_html = f'<p style="font-size:0.82rem;margin-top:6px;">{_escape(body)}</p>' if body else ""
        cards.append(
            f"""
            <div class="{card_class}" style="{card_style}">
              {stat_html}
              <h4 style="margin-bottom:6px;">{_escape(display_title)}</h4>
              {body_html}
            </div>
            """
        )
    return "".join(cards)


def _render_blue_sky_interaction_body(spec: dict[str, Any], items: list[str]) -> str:
    key_cards = []
    for index, item in enumerate(items[:4], start=1):
        title, body = _blue_sky_item_parts(item)
        key = _blue_sky_keycap(title, body, index)
        copy = body or spec.get("key_point", "")
        key_cards.append(
            f"""
            <div class="g" style="padding:15px 18px;">
              <kbd>{_escape(key)}</kbd>
              <h4 style="margin:9px 0 5px;font-size:1.02rem;line-height:1.18;">{_escape(title)}</h4>
              <p style="font-size:0.78rem;line-height:1.45;">{_escape(copy)}</p>
            </div>
            """
        )
    return f"""
      <div class="cols2" style="align-items:stretch;">
        <div class="bento" style="grid-template-columns:repeat(2,1fr);grid-auto-rows:164px;">{"".join(key_cards)}</div>
        <div style="display:flex;flex-direction:column;gap:12px;">
          <div class="info"><strong>Live deck:</strong> {_escape(spec.get("key_point", ""))}</div>
          <div class="cmd">F5 · P · E · Ctrl+S</div>
          <div class="co"><strong>Browser-native</strong><br>Presenter Mode、Inline Editing、Notes Panel 都在单 HTML 内运行。</div>
        </div>
      </div>
    """.strip()


def _render_blue_sky_use_case_body(spec: dict[str, Any], items: list[str]) -> str:
    layers = []
    for index, item in enumerate(items[:4], start=1):
        title, body = _blue_sky_item_parts(item)
        layers.append(
            f"""
            <div class="layer">
              <div class="step">{index}</div>
              <div>
                <h4 style="margin-bottom:4px;">{_escape(title)}</h4>
                <p style="font-size:0.82rem;">{_escape(body or spec.get("key_point", ""))}</p>
              </div>
            </div>
            """
        )
    return f'<div style="display:flex;flex-direction:column;gap:11px;">{"".join(layers)}</div>'


def _render_blue_sky_preset_body(items: list[str]) -> str:
    cards = []
    for item in items[:6]:
        title, body = _blue_sky_item_parts(item)
        cards.append(
            f"""
            <div class="g" style="padding:18px 20px;">
              <span class="pill green" style="margin-bottom:10px;">{_escape(title)}</span>
              <p style="font-size:0.82rem;">{_escape(body or item)}</p>
            </div>
            """
        )
    return f'<div class="cols3">{"".join(cards)}</div>'


def _render_blue_sky_action_cards(spec: dict[str, Any], items: list[str]) -> str:
    cards = []
    accent_classes = [" info", " co", "", ""]
    for index, item in enumerate(items[:4]):
        title, body = _blue_sky_item_parts(item)
        body = body or item
        is_command = bool(re.search(r"install|clawhub|https?://|/slide-creator", body, flags=re.IGNORECASE))
        body_html = f'<div class="cmd" style="margin-top:10px;">{_escape(body)}</div>' if is_command else f'<p style="margin-top:8px;">{_escape(body)}</p>'
        card_class = f"g{accent_classes[index]}"
        cards.append(
            f"""
            <div class="{card_class}" style="padding:18px 20px;text-align:left;">
              <span class="pill green">{_escape(title)}</span>
              {body_html}
            </div>
            """
        )
    return "".join(cards)


def render_blue_sky_html(
    brief: dict[str, Any],
    *,
    packet: dict[str, Any] | None = None,
    style_contract: dict[str, Any] | None = None,
) -> str:
    """Renderer for Blue Sky preset.

    Blue Sky uses its own #stage/#track architecture (not shared js-engine shell).
    Extracts starter CSS + JS from blue-sky-starter.html and assembles with generated slides.
    """
    packet = packet or build_render_packet(brief)
    preset = "Blue Sky"
    style_contract = style_contract or compile_style_contract(preset)
    starter_path = ROOT / "references" / "blue-sky-starter.html"

    # Extract starter CSS
    if starter_path.exists():
        starter_css = _extract_starter_css(starter_path)
    else:
        starter_css = "\n\n".join(style_contract["css_blocks"])

    # Build slides
    specs = build_slide_spec(brief, packet=packet)
    total = len(specs)
    slides_html = "\n\n".join(
        _render_blue_sky_slide(spec, total, language=brief["language"], role_index=i)
        for i, spec in enumerate(specs)
    )

    brand_mark = _brand_mark_text(brief["title"], preset)
    provenance_attrs = _html_body_provenance_attrs(packet)

    # Pre-generate nav-dots
    dots_html = "".join(f'<button class="dot" aria-label="Slide {i + 1}"></button>' for i in range(total))

    # Extract Blue Sky presentation JS (includes PresentMode, keyboard nav, go())
    blue_sky_js = _extract_blue_sky_js(starter_path, total) if starter_path.exists() else ""
    watermark_js = _blue_sky_watermark_script(preset=preset, version=_skill_version())

    return f"""<!DOCTYPE html>
<html lang="{_escape(brief['language'])}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_escape(brief['title'])} - {preset}</title>
<style>
{starter_css}
.title-balance {{
  display: flex;
  flex-direction: column;
  gap: 0.02em;
}}
.title-line {{
  display: block;
}}
.title-nowrap {{
  white-space: nowrap;
}}
h2.title-nowrap {{
  font-size: clamp(1.12rem, 2.6vw, 2.25rem);
}}
@media (max-width: 720px) {{
  .title-nowrap {{
    white-space: normal;
  }}
}}
.slide-credit {{
  position: absolute;
  right: 28px;
  bottom: 18px;
  z-index: 20;
  font-size: 11px;
  letter-spacing: 0.04em;
  color: rgba(100, 116, 139, 0.72);
  pointer-events: none;
}}
body.presenting .slide-credit {{ display: none !important; }}
</style>
</head>
<body data-export-progress="true" data-preset="{preset}" {provenance_attrs}>

<div class="orb" id="orb1"></div>
<div class="orb" id="orb2"></div>
<div class="orb" id="orb3"></div>
<div id="slide-counter">01 / {total:02d}</div>
<div id="nav-dots"></div>

<div class="edit-hotzone"></div>
<button class="edit-toggle" id="editToggle" title="Edit mode (E)">✏ Edit</button>

<div id="notes-panel">
  <div id="notes-panel-header">
    <div id="notes-panel-label">SPEAKER NOTES — SLIDE 1 / {total}</div>
    <div id="notes-drag-hint"></div>
    <button id="notes-collapse-btn" title="Collapse / expand">▾</button>
  </div>
  <div id="notes-body">
    <textarea id="notes-textarea" placeholder="Add speaker notes for this slide…"></textarea>
  </div>
</div>

<span id="brand-mark">{_escape(brand_mark)}</span>

<div id="stage">
<div id="track">
{slides_html}
</div>
</div>

<script>
{blue_sky_js}
{watermark_js}
</script>
</body>
</html>"""


def _render_blue_sky_slide(
    spec: dict[str, Any],
    total: int,
    *,
    language: str,
    role_index: int,
) -> str:
    """Render a single Blue Sky slide using starter.html component classes."""
    slide_number = spec["slide_number"]
    role = str(spec["role"])
    role_attr = _escape(role)
    layout_id = str(spec.get("layout_id") or "bento")
    title_text = str(spec["title"])
    key_point = _escape(spec.get("key_point", ""))
    speaker_note = _escape(spec.get("speaker_note", ""))
    cover_title = _blue_sky_title_tag(
        "h1",
        title_text,
        layout_id=layout_id,
        extra_attrs='style="margin-bottom:14px;"',
    )
    section_title = _blue_sky_title_tag("h2", title_text, layout_id=layout_id)

    items = spec.get("supporting_items", [])
    evidence = spec.get("evidence_items", [])
    facts = spec.get("supporting_facts", [])
    all_items = _blue_sky_display_items(spec)

    # Cover slide
    if layout_id == "cover" or role_index == 0:
        cover_items = facts or all_items
        cover_metrics = _blue_sky_cover_metrics(spec, cover_items)
        cover_pill = _blue_sky_cover_pill_text(spec, cover_items, cover_metrics)
        stat_items = []
        for stat_val, stat_label in cover_metrics:
            label_html = f'<p style="font-size:0.78rem;margin-top:2px;">{_escape(stat_label)}</p>' if stat_label else ""
            stat_items.append(
                f'<div class="g" style="padding:16px 28px;text-align:center;">'
                f'<div class="stat" style="font-size:2.8rem;">{_escape(stat_val)}</div>'
                f'{label_html}</div>'
            )
        if not stat_items:
            for item in cover_items[:3]:
                stat_items.append(
                    f'<div class="g" style="padding:16px 22px;text-align:center;">'
                    f'<h4 style="margin:0;font-size:0.98rem;line-height:1.3;">{_escape(str(item))}</h4>'
                    f'</div>'
                )
        stats_html = f'<div style="display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin-top:28px;">{"".join(stat_items)}</div>' if stat_items else ""
        return f"""
    <!-- slide {slide_number}: {role} -->
    <section class="slide cover" style="overflow:hidden;" id="slide-{slide_number}" data-notes="{speaker_note}" aria-label="{role_attr}" data-export-role="cover">

      <svg width="0" height="0" style="position:absolute;pointer-events:none;">
        <defs>
          <filter id="cloud-filter">
            <feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="4" seed="5" result="noise"/>
            <feDisplacementMap in="SourceGraphic" in2="noise" scale="60" xChannelSelector="R" yChannelSelector="G"/>
          </filter>
        </defs>
      </svg>

      <!-- Ambient orbs -->
      <div style="position:absolute;width:50%;height:60%;top:5%;left:-10%;border-radius:50%;background:rgba(96,165,250,0.28);filter:blur(90px);pointer-events:none;z-index:1;"></div>
      <div style="position:absolute;width:55%;height:65%;top:8%;right:-12%;border-radius:50%;background:rgba(14,165,233,0.22);filter:blur(100px);pointer-events:none;z-index:1;"></div>
      <div style="position:absolute;width:35%;height:40%;bottom:32%;left:30%;border-radius:50%;background:rgba(99,102,241,0.18);filter:blur(80px);pointer-events:none;z-index:1;"></div>

      <!-- Scrolling cloud bank -->
      <div class="cloud-layer" style="filter:url(#cloud-filter);">
        <div class="cloud-strip">
          <div style="position:relative;width:1920px;height:100%;flex-shrink:0;">
            <div class="cloud-group" style="left:192px;bottom:-54px;width:576px;height:216px;opacity:0.65;">
              <div class="cloud-puff" style="bottom:0;left:10%;width:288px;height:288px;filter:blur(18px);"></div>
              <div class="cloud-puff" style="bottom:22px;left:30%;width:384px;height:384px;filter:blur(22px);"></div>
              <div class="cloud-puff" style="bottom:-22px;left:60%;width:346px;height:346px;filter:blur(18px);"></div>
            </div>
            <div class="cloud-group" style="left:1100px;bottom:-86px;width:480px;height:194px;opacity:0.5;">
              <div class="cloud-puff" style="bottom:0;left:0%;width:230px;height:230px;filter:blur(14px);"></div>
              <div class="cloud-puff" style="bottom:32px;left:40%;width:346px;height:346px;filter:blur(20px);"></div>
              <div class="cloud-puff" style="bottom:11px;left:70%;width:288px;height:288px;filter:blur(16px);"></div>
            </div>
          </div>
          <div style="position:relative;width:1920px;height:100%;flex-shrink:0;">
            <div class="cloud-group" style="left:192px;bottom:-54px;width:576px;height:216px;opacity:0.65;">
              <div class="cloud-puff" style="bottom:0;left:10%;width:288px;height:288px;filter:blur(18px);"></div>
              <div class="cloud-puff" style="bottom:22px;left:30%;width:384px;height:384px;filter:blur(22px);"></div>
              <div class="cloud-puff" style="bottom:-22px;left:60%;width:346px;height:346px;filter:blur(18px);"></div>
            </div>
            <div class="cloud-group" style="left:1100px;bottom:-86px;width:480px;height:194px;opacity:0.5;">
              <div class="cloud-puff" style="bottom:0;left:0%;width:230px;height:230px;filter:blur(14px);"></div>
              <div class="cloud-puff" style="bottom:32px;left:40%;width:346px;height:346px;filter:blur(20px);"></div>
              <div class="cloud-puff" style="bottom:11px;left:70%;width:288px;height:288px;filter:blur(16px);"></div>
            </div>
          </div>
        </div>
        <div class="cloud-strip fast" style="z-index:2;">
          <div style="position:relative;width:1920px;height:100%;flex-shrink:0;">
            <div class="cloud-group" style="left:580px;bottom:-70px;width:420px;height:170px;opacity:0.42;">
              <div class="cloud-puff" style="bottom:0;left:5%;width:200px;height:200px;filter:blur(12px);"></div>
              <div class="cloud-puff" style="bottom:20px;left:35%;width:300px;height:300px;filter:blur(16px);"></div>
              <div class="cloud-puff" style="bottom:-15px;left:65%;width:250px;height:250px;filter:blur(13px);"></div>
            </div>
          </div>
          <div style="position:relative;width:1920px;height:100%;flex-shrink:0;">
            <div class="cloud-group" style="left:580px;bottom:-70px;width:420px;height:170px;opacity:0.42;">
              <div class="cloud-puff" style="bottom:0;left:5%;width:200px;height:200px;filter:blur(12px);"></div>
              <div class="cloud-puff" style="bottom:20px;left:35%;width:300px;height:300px;filter:blur(16px);"></div>
              <div class="cloud-puff" style="bottom:-15px;left:65%;width:250px;height:250px;filter:blur(13px);"></div>
            </div>
          </div>
        </div>
      </div>

      <div style="text-align:center;position:relative;z-index:10;">
        <span class="pill" style="margin-bottom:20px;display:inline-block;">{_escape(cover_pill)}</span>
        {cover_title}
        <p style="font-size:1.1rem;max-width:560px;margin:0 auto 28px;">{key_point}</p>
        {stats_html}
      </div>
    </section>""".strip()

    # Closing slide
    if layout_id == "closing":
        action_cards = _render_blue_sky_action_cards(spec, all_items)
        return f"""
    <!-- slide {slide_number}: {role} -->
    <section class="slide" id="slide-{slide_number}" data-notes="{speaker_note}" aria-label="{role_attr}" data-export-role="{role_attr}">
      <div style="text-align:center;max-width:900px;width:100%;">
        <span class="pill" style="margin-bottom:14px;display:inline-block;">Start</span>
        {section_title}
        <p style="font-size:1rem;color:var(--text-secondary);margin:14px auto 22px;max-width:620px;">{key_point}</p>
        <div class="cols2">{action_cards}</div>
      </div>
    </section>""".strip()

    # Chapter / section slide
    if layout_id == "chapter":
        return f"""
    <!-- slide {slide_number}: {role} -->
    <section class="slide chapter" id="slide-{slide_number}" data-notes="{speaker_note}" aria-label="{role_attr}" data-export-role="{role_attr}">
      <div style="text-align:center;">
        <span class="pill" style="margin-bottom:14px;display:inline-block;">Chapter {role_index:02d}</span>
        {section_title}
        <div class="divider" style="margin:8px auto 14px;"></div>
        <p style="max-width:600px;margin:0 auto;color:var(--text-secondary);">{key_point}</p>
      </div>
    </section>""".strip()

    # Default content slide
    items_html = ""
    if all_items:
        item_list = "".join(f"<li>{_escape(item)}</li>" for item in all_items)
        items_html = f'<ul class="bl">{item_list}</ul>'

    # Two-column comparison
    if layout_id == "comparison":
        left_items = all_items[:len(all_items)//2]
        right_items = all_items[len(all_items)//2:]
        left_html = "".join(f"<li>{_escape(i)}</li>" for i in left_items)
        right_html = "".join(f"<li>{_escape(i)}</li>" for i in right_items)
        return f"""
    <!-- slide {slide_number}: {role} -->
    <section class="slide" id="slide-{slide_number}" data-notes="{speaker_note}" aria-label="{role_attr}" data-export-role="{role_attr}">
      <div style="max-width:860px;width:100%;">
        <span class="pill" style="margin-bottom:14px;display:inline-block;">Chapter {role_index:02d}</span>
        {section_title}
        <div class="divider"></div>
        <div class="cols2">
          <div class="g" style="padding:22px 24px;"><ul class="bl">{left_html}</ul></div>
          <div class="g" style="padding:22px 24px;"><ul class="bl">{right_html}</ul></div>
        </div>
        <p style="margin-top:14px;color:var(--text-secondary);font-size:0.9rem;">{key_point}</p>
      </div>
    </section>""".strip()

    # Process / workflow slide
    if layout_id == "workflow":
        steps_html = ""
        for idx, item in enumerate(all_items[:6], 1):
            steps_html += f"""
        <div class="layer">
          <div class="step">{idx}</div>
          <div><h4 style="margin-bottom:4px;">{_escape(item)}</h4></div>
        </div>"""
        return f"""
    <!-- slide {slide_number}: {role} -->
    <section class="slide" id="slide-{slide_number}" data-notes="{speaker_note}" aria-label="{role_attr}" data-export-role="{role_attr}">
      <div style="max-width:820px;width:100%;">
        <span class="pill" style="margin-bottom:14px;display:inline-block;">Chapter {role_index:02d}</span>
        {section_title}
        <div class="divider"></div>
        <div style="display:flex;flex-direction:column;gap:11px;">{steps_html}
        </div>
        <p style="margin-top:14px;color:var(--text-secondary);font-size:0.9rem;">{key_point}</p>
      </div>
    </section>""".strip()

    # Bento / grid slide
    if layout_id == "bento":
        if role == "interaction":
            body_html = _render_blue_sky_interaction_body(spec, all_items)
        elif role == "use-cases":
            body_html = _render_blue_sky_use_case_body(spec, all_items)
        elif role == "presets":
            body_html = _render_blue_sky_preset_body(all_items)
        else:
            cards_html = _render_blue_sky_bento_cards(spec, all_items)
            body_html = f'<div class="bento" style="grid-auto-rows:132px;">{cards_html}</div>'
        return f"""
    <!-- slide {slide_number}: {role} -->
    <section class="slide" id="slide-{slide_number}" data-notes="{speaker_note}" aria-label="{role_attr}" data-export-role="{role_attr}">
      <div style="max-width:940px;width:100%;">
        <span class="pill" style="margin-bottom:14px;display:inline-block;">Chapter {role_index:02d}</span>
        {section_title}
        <div class="divider"></div>
        {body_html}
      </div>
    </section>""".strip()

    # Evidence / data slide
    if layout_id == "table":
        table_rows = ""
        table_items = all_items or [spec["key_point"]]
        for idx, item in enumerate(table_items[:8], 1):
            table_rows += f'<tr><td>{idx}</td><td>{_escape(item)}</td></tr>'
        return f"""
    <!-- slide {slide_number}: {role} -->
    <section class="slide" id="slide-{slide_number}" data-notes="{speaker_note}" aria-label="{role_attr}" data-export-role="{role_attr}">
      <div style="max-width:860px;width:100%;">
        <span class="pill" style="margin-bottom:14px;display:inline-block;">Chapter {role_index:02d}</span>
        {section_title}
        <div class="divider"></div>
        <div class="g" style="padding:0;overflow:hidden;"><table class="ctable"><thead><tr><th>#</th><th>证据</th></tr></thead><tbody>{table_rows}</tbody></table></div>
        <p style="margin-top:14px;color:var(--text-secondary);font-size:0.9rem;">{key_point}</p>
      </div>
    </section>""".strip()

    # Default: generic content slide
    return f"""
    <!-- slide {slide_number}: {role} -->
    <section class="slide" id="slide-{slide_number}" data-notes="{speaker_note}" aria-label="{role_attr}" data-export-role="{role_attr}">
      <div style="max-width:860px;width:100%;">
        <span class="pill" style="margin-bottom:14px;display:inline-block;">Chapter {role_index:02d}</span>
        {section_title}
        <div class="divider"></div>
        <p style="color:var(--text-secondary);">{key_point}</p>
        {items_html}
      </div>
    </section>""".strip()


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
    return _assemble_shell_html(brief["title"], brief["language"], "Chinese Chan", css, slides_html, total, packet)


def render_unified_profile_html(
    brief: dict[str, Any],
    *,
    packet: dict[str, Any],
    style_contract: dict[str, Any],
) -> str:
    capability = get_preset_render_capability(brief["style"]["preset"])
    specs = build_slide_spec(brief, packet)
    payload = build_preset_profile_payload(
        brief=brief,
        packet=packet,
        style_contract=style_contract,
        capability=capability,
        specs=specs,
    )
    packet["body_classes"] = list(payload.body_classes)
    packet["body_data_attrs"] = payload.body_data_attrs
    packet["style_family"] = payload.style_signature["family"]
    packet["style_signature"] = payload.style_signature
    packet["style_signature_hash"] = payload.style_signature["hash"]
    packet["render_path"] = payload.render_path
    packet["preset_generation_status"] = payload.generation_status
    packet["renderer_strategy"] = payload.renderer_strategy
    if payload.body_data_attrs.get("data-profile-renderer-source", "").startswith("demo-derived:"):
        packet["brand_mark"] = "slide-creator"
    css = _build_non_swiss_shell_css(style_contract, payload.canonical_preset) + "\n\n" + payload.css
    sections_html = payload.sections_html + "\n\n" + profile_auto_contrast_script()
    return _assemble_shell_html(
        brief["title"],
        brief["language"],
        payload.canonical_preset,
        css,
        sections_html,
        payload.slide_count,
        packet,
    )


def _extract_starter_css(starter_path: Path) -> str:
    """Extract <style> block content from a starter.html."""
    content = _read_text(starter_path)
    match = re.search(r"<style>(.*?)</style>", content, re.DOTALL)
    return match.group(1).strip() if match else ""


def _extract_starter_image_urls(starter_path: Path) -> dict[str, str]:
    """Extract all image URLs (logos + backgrounds) from starter.html img tags."""
    content = _read_text(starter_path)
    images: dict[str, str] = {}
    for match in re.finditer(r'<img[^>]+class="([^"]+)"[^>]+src="([^"]+)"', content):
        cls = match.group(1)
        url = match.group(2)
        if "logo" in cls:
            if "blue" in cls.lower() or "blue" in url.lower():
                images["logo_blue"] = url
            elif "white" in cls.lower() or "white" in url.lower():
                images["logo_white"] = url
            elif "logo" not in images:
                images["logo_default"] = url
        elif "hero" in cls:
            images["hero"] = url
        elif "section-image" in cls or "chapter" in cls:
            images["chapter_bg"] = url
        elif "toc-image" in cls or "catalogue" in cls:
            images["catalogue_bg"] = url
        elif "closing-image-left" in cls or "thanks" in cls:
            images["closing_left"] = url
        elif "closing-image" in cls or "endpage" in cls:
            images["closing_right"] = url
    return images


def _render_custom_theme_slide(
    spec: dict[str, Any],
    total: int,
    *,
    style_contract: dict[str, Any],
    images: dict[str, str],
    role_index: int,
) -> str:
    """Render a slide using theme-specific component classes from the style contract."""
    slide_number = spec["slide_number"]
    role = spec["role"]
    layout_id = spec["layout_id"]
    items = spec.get("supporting_items", [])
    evidence = spec.get("evidence_items", [])

    logo_blue = images.get("logo_blue") or images.get("logo_default") or ""
    logo_white = images.get("logo_white") or logo_blue
    logo_url = logo_blue

    # Title slide
    if role == "title" or role_index == 0:
        title_lines = spec["title"].split("\n", 1)
        main_title = _escape(title_lines[0])
        sub_title = _escape(title_lines[1]) if len(title_lines) > 1 else _escape(spec.get("key_point", ""))
        title_logo = f'<img class="kd-logo-left" src="{logo_url}" alt="Logo">' if logo_url else ""
        hero_img = f'<img class="kd-hero-image" src="{images["hero"]}" alt="首页右侧装饰">' if images.get("hero") else ""
        return f"""
    <section class="slide slide-title" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="title" data-export-role="title">
        {title_logo}
        {hero_img}
        <div class="title-content">
            <h1 class="title-main kd-reveal">{main_title}</h1>
            <p class="title-sub kd-reveal">{sub_title}</p>
        </div>
    </section>""".strip()

    # CTA / closing slide
    if role == "cta" or layout_id == "cta_close":
        cta_logo = f'<img class="kd-logo-left" src="{logo_url}" alt="Logo">' if logo_url else ""
        closing_left = f'<img class="kd-closing-image-left" src="{images["closing_left"]}" alt="感谢页面">' if images.get("closing_left") else ""
        closing_right = f'<img class="kd-closing-image" src="{images["closing_right"]}" alt="尾页右侧装饰">' if images.get("closing_right") else ""
        return f"""
    <section class="slide slide-closing" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="cta" data-export-role="cta_close">
        {cta_logo}
        {closing_left}
        {closing_right}
        <div class="section-content" style="left:80px;top:50%;transform:translateY(-50%);">
            <h2 class="section-title kd-reveal" style="font-size:clamp(28pt,4vw,42pt);color:var(--kd-blue);">{_escape(spec["title"])}</h2>
            <div class="section-divider kd-reveal" style="background:var(--kd-blue);"></div>
            <p style="font-size:14pt;color:var(--text-secondary);line-height:1.6;">{_escape(spec.get("key_point", ""))}</p>
        </div>
    </section>""".strip()

    # Section slide (blue background) — use for problem, solution, evidence roles
    is_section_role = role in ("problem", "solution", "evidence", "core")
    if is_section_role:
        section_logo = f'<img class="kd-logo-right-section" src="{logo_white}" alt="Logo">' if logo_white else ""
        section_bg = f'<img class="kd-section-image" src="{images["chapter_bg"]}" alt="章节背景">' if images.get("chapter_bg") else ""
        section_num = f"{role_index:02d}"
        return f"""
    <section class="slide slide-section" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(role)}" data-export-role="{_escape(layout_id)}">
        {section_bg}
        {section_logo}
        <div class="section-content">
            <div class="section-number kd-reveal">{section_num}</div>
            <div class="section-divider kd-reveal"></div>
            <h2 class="section-title kd-reveal">{_escape(spec["title"])}</h2>
            <p class="section-title kd-reveal" style="font-size:clamp(12pt,1.6vw,16pt);font-weight:400;margin-top:16px;line-height:1.6;">{_escape(spec.get("key_point", ""))}</p>
        </div>
    </section>""".strip()

    # TOC slide
    if role == "toc" or layout_id == "toc":
        toc_logo = f'<img class="kd-logo-right-toc" src="{logo_blue}" alt="Logo">' if logo_blue else ""
        toc_bg = f'<img class="kd-toc-image" src="{images["catalogue_bg"]}" alt="目录背景">' if images.get("catalogue_bg") else ""
        toc_items_html = ""
        for i, item in enumerate(items[:12], 1):
            compact_cls = " compact" if len(items) > 5 else ""
            num_compact = ""
            if len(items) > 9:
                num_compact = " ultra-compact"
            elif len(items) > 5:
                num_compact = " compact"
            toc_items_html += f'<div class="toc-item{compact_cls}"><span class="toc-number{num_compact}">{i:02d}</span><span class="toc-text">{_escape(item)}</span><span class="toc-page">P {i + 1:02d}</span></div>\n'
        return f"""
    <section class="slide slide-toc" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="toc" data-export-role="toc">
        {toc_bg}
        {toc_logo}
        <h2 class="toc-title">目 录</h2>
        <div class="toc-content">
            {toc_items_html}
        </div>
    </section>""".strip()

    # Content slide (default)
    items_html = ""
    for item in items[:5]:
        items_html += f'<li class="kd-reveal">{_escape(item)}</li>\n'

    cards_html = ""
    for ev in evidence[:3]:
        cards_html += f'<div class="kd-card kd-reveal"><p class="kd-card-body">{_escape(ev)}</p></div>\n'

    cards_section = ""
    if cards_html:
        cards_section = f'<div class="cols-2">{cards_html}</div>'

    logo_img = f'<img class="kd-logo-right" src="{logo_url}" alt="Logo">' if logo_url else ""

    return f"""
    <section class="slide slide-content" id="slide-{slide_number}" data-notes="{_escape(spec['speaker_note'])}" aria-label="{_escape(role)}" data-export-role="{_escape(layout_id)}">
        {logo_img}
        <div class="content-header">
            <h2 class="content-title kd-reveal">{_escape(spec["title"])}</h2>
            <p class="content-subtitle kd-reveal">{_escape(spec.get("key_point", ""))}</p>
        </div>
        <div class="content-body">
            <ul>
                {items_html}
            </ul>
            {cards_section}
        </div>
    </section>""".strip()


def render_custom_theme_html(
    brief: dict[str, Any],
    *,
    packet: dict[str, Any] | None = None,
    style_contract: dict[str, Any] | None = None,
) -> str:
    """Renderer for custom themes. Uses starter.html CSS + theme component classes."""
    packet = packet or build_render_packet(brief)
    preset = brief["style"]["preset"]
    capability = get_preset_render_capability(preset)
    if capability.renderer_strategy != "custom_theme" or not capability.reference_path:
        raise RenderError(f"Custom theme not found: {preset}")
    style_contract = style_contract or compile_style_contract(preset)
    display_preset = capability.canonical_preset or style_contract["preset"]

    reference_path = Path(capability.reference_path)
    if not reference_path.is_absolute():
        reference_path = ROOT / reference_path
    theme_dir = reference_path.resolve().parent
    display_preset = display_preset or theme_dir.name.title()

    # Extract starter.html CSS if available
    starter_path = theme_dir / "starter.html"
    if starter_path.exists():
        starter_css = _extract_starter_css(starter_path)
        images = _extract_starter_image_urls(starter_path)
    else:
        starter_css = "\n\n".join(style_contract["css_blocks"])
        images = {}

    specs = build_slide_spec(brief, packet=packet)
    total = len(specs)
    slides_html = "\n\n".join(
        _render_custom_theme_slide(spec, total, style_contract=style_contract, images=images, role_index=i)
        for i, spec in enumerate(specs)
    )

    # Use starter.html CSS directly, skip the generic shell CSS
    js_engine = _extract_js_engine_blocks(preset=display_preset, version=_skill_version())
    brand_mark = _brand_mark_text(brief["title"], display_preset)
    provenance_attrs = _html_body_provenance_attrs(packet)

    return f"""<!DOCTYPE html>
<html lang="{_escape(brief['language'])}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_escape(brief['title'])} - {_escape(display_preset)}</title>
<style>
{starter_css}

/* Present mode */
body.presenting {{
    margin: 0; padding: 0;
    background: #000;
    overflow: hidden;
    scroll-snap-type: none;
}}
body.presenting .slide {{
    position: fixed; top: 0; left: 0;
    width: 1440px; height: 900px;
    transform-origin: top left;
    scroll-snap-align: none;
    visibility: hidden;
    pointer-events: none;
}}
body.presenting .slide.p-on {{
    visibility: visible;
    pointer-events: auto;
    display: flex !important;
}}
body.presenting #present-btn {{ display: none !important; }}
body.presenting #present-counter {{ display: block; }}
body.presenting.presenting-black .slide {{ visibility: hidden !important; }}
body.presenting .slide-credit {{ display: none !important; }}

/* Edit hotzone */
.edit-hotzone {{
    position: fixed;
    top: 0; left: 0;
    width: 120px; height: 120px;
    z-index: 9999;
}}
#editToggle, .edit-toggle {{
    position: fixed;
    top: 12px; left: 12px;
    z-index: 10000;
    padding: 6px 16px;
    border-radius: 6px;
    border: 1px solid #ddd;
    background: #fff;
    cursor: pointer;
    font-size: 13px;
    display: none;
}}
#editToggle.show, .edit-toggle.show {{ display: block; }}
#editToggle.active, .edit-toggle.active {{ background: var(--kd-blue, #2971EB); color: #fff; border-color: var(--kd-blue, #2971EB); }}
</style>
</head>
<body data-export-progress="true" data-preset="{_escape(display_preset)}" {provenance_attrs}>
<span id="brand-mark">{_escape(brand_mark)}</span>
{slides_html}
<div class="edit-hotzone"></div>
<button id="editToggle" class="edit-toggle" type="button">Edit</button>
<script>
{js_engine}
</script>
</body>
</html>"""


NATIVE_RENDERER_REGISTRY = {
    "Swiss Modern": render_swiss_modern_html,
    "Enterprise Dark": render_enterprise_dark_html,
    "Data Story": render_data_story_html,
    "Chinese Chan": render_chinese_chan_html,
    "Blue Sky": render_blue_sky_html,
}


def _annotate_page_buckets(html_text: str) -> str:
    pattern = re.compile(r'<section\b[^>]*class="[^"]*\bslide\b[^"]*"[^>]*>')
    matches = list(pattern.finditer(html_text))
    if not matches:
        return html_text
    total = len(matches)
    pieces: list[str] = []
    cursor = 0
    for index, match in enumerate(matches):
        opening = match.group(0)
        if "data-page-bucket=" not in opening:
            bucket = "cover" if total == 1 or index == 0 else "closing" if index == total - 1 else "content"
            opening = opening[:-1] + f' data-page-bucket="{bucket}">'
        pieces.extend((html_text[cursor:match.start()], opening))
        cursor = match.end()
    pieces.append(html_text[cursor:])
    return "".join(pieces)


def _annotate_preset_content_scope(html_text: str, preset: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", preset.lower()).strip("-")
    marker = f"preset-{slug}-content"

    def add_scope(match: re.Match[str]) -> str:
        classes = match.group(1).split()
        if set(classes) & {"slide-content", "content"} and marker not in classes:
            classes.append(marker)
        return f'class="{" ".join(classes)}"'

    return re.sub(r'class="([^"]*)"', add_scope, html_text)


def render_from_brief(brief: dict[str, Any]) -> tuple[str, dict[str, Any], dict[str, Any]]:
    packet = build_render_packet(brief)
    style_contract = compile_style_contract(brief["style"]["preset"])
    preset = packet["canonical_preset"]
    renderer_strategy = packet.get("renderer_strategy")
    renderer = NATIVE_RENDERER_REGISTRY.get(preset)
    if renderer_strategy == "native" and renderer:
        html_text = renderer(brief, packet=packet, style_contract=style_contract)
    elif renderer_strategy == "unified_profile":
        html_text = render_unified_profile_html(brief, packet=packet, style_contract=style_contract)
    elif _is_custom_theme(brief["style"]["preset"]):
        html_text = render_custom_theme_html(brief, packet=packet, style_contract=style_contract)
    else:
        raise RenderError(
            f"Low-context render does not have a valid strategy for {preset}; got {renderer_strategy}"
        )
    html_text = _annotate_preset_content_scope(html_text, preset)
    return _annotate_page_buckets(html_text), packet, style_contract


def render_from_context_text(text: str) -> tuple[dict[str, Any], str, dict[str, Any], dict[str, Any]]:
    brief = extract_brief_from_source_text(text)
    html_text, packet, style_contract = render_from_brief(brief)
    return brief, html_text, packet, style_contract


def render_from_context_path(path: str | Path) -> tuple[dict[str, Any], str, dict[str, Any], dict[str, Any]]:
    brief = extract_brief_from_source_path(path)
    html_text, packet, style_contract = render_from_brief(brief)
    return brief, html_text, packet, style_contract
