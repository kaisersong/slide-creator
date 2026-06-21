from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
SUPPORT_MATRIX = ROOT / "references" / "preset-support-tiers.json"
STYLE_INDEX = ROOT / "references" / "style-index.md"
WORKFLOW_MD = ROOT / "references" / "workflow.md"
SKILL_MD = ROOT / "SKILL.md"
README_MD = ROOT / "README.md"
README_ZH = ROOT / "README.zh-CN.md"
AUTO_DEMO = ROOT / "demos" / "mode-paths" / "auto-BRIEF.json"
sys.path.insert(0, str(SCRIPTS))

from low_context import (  # noqa: E402
    PRESET_REFERENCE_MAP,
    build_render_packet,
    compile_style_contract,
    validate_generation_brief_data,
)
from preset_capabilities import get_preset_render_capability, renderable_recommendation_presets  # noqa: E402
from preset_support import (  # noqa: E402
    default_recommendation_presets,
    explicit_selection_is_allowed,
    preset_support_tier,
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def test_support_matrix_covers_all_supported_presets_exactly_once():
    matrix = read_json(SUPPORT_MATRIX)
    flattened = []
    for presets in matrix["tiers"].values():
        flattened.extend(presets)

    normalized_flat = [preset.lower() for preset in flattened]
    assert len(normalized_flat) == len(set(normalized_flat)), "preset-support-tiers.json has duplicate presets"
    assert set(normalized_flat) == set(PRESET_REFERENCE_MAP.keys())


def test_default_recommendation_surface_is_core_four():
    matrix = read_json(SUPPORT_MATRIX)
    assert matrix["policy"]["default_recommendation_presets"] == [
        "Swiss Modern",
        "Enterprise Dark",
        "Data Story",
        "Blue Sky",
    ]
    assert default_recommendation_presets() == matrix["policy"]["default_recommendation_presets"]
    assert renderable_recommendation_presets(include_contextual=False) == [
        "Blue Sky",
        "Data Story",
        "Enterprise Dark",
        "Swiss Modern",
    ]


def test_capability_matrix_separates_recommendation_from_generation_readiness():
    capabilities = {
        preset: get_preset_render_capability(preset)
        for preset in PRESET_REFERENCE_MAP
    }

    deterministic_ready = {
        capability.canonical_preset
        for capability in capabilities.values()
        if capability.renderer_strategy == "native"
    }
    default_recommended = {
        capability.canonical_preset
        for capability in capabilities.values()
        if capability.recommendation_status == "default"
    }
    contextual = {
        capability.canonical_preset
        for capability in capabilities.values()
        if capability.recommendation_status == "contextual"
    }
    reference_driven = {
        capability.canonical_preset
        for capability in capabilities.values()
        if capability.generation_status == "reference_driven"
    }

    assert deterministic_ready == {"Swiss Modern", "Enterprise Dark", "Data Story", "Blue Sky", "Chinese Chan"}
    assert default_recommended == {"Swiss Modern", "Enterprise Dark", "Data Story", "Blue Sky"}
    assert contextual == {"Chinese Chan"}
    assert "Paper & Ink" in reference_driven
    assert "Terminal Green" in reference_driven
    assert all(capability.renderer_strategy != "unsupported" for capability in capabilities.values())


def test_paper_ink_outranks_notebook_tabs_in_current_tiering():
    assert preset_support_tier("Paper & Ink") == "supported"
    assert preset_support_tier("Notebook Tabs") == "experimental"


def test_explicit_selection_policy_keeps_non_default_presets_selectable():
    assert explicit_selection_is_allowed("Neon Cyber") is True
    assert explicit_selection_is_allowed("Paper & Ink") is True
    assert explicit_selection_is_allowed("Blue Sky") is True
    assert explicit_selection_is_allowed("Chinese Chan") is True


def test_reference_driven_preset_builds_agent_render_packet_without_claiming_native_renderer():
    brief = read_json(AUTO_DEMO)
    brief["style"]["preset"] = "Paper & Ink"

    contract = compile_style_contract("Paper & Ink")
    assert contract["preset"] == "Paper & Ink"

    validation_errors = validate_generation_brief_data(brief)
    assert validation_errors == []

    packet = build_render_packet(brief)
    assert packet["preset_generation_status"] == "reference_driven"
    assert packet["renderer_strategy"] == "reference_driven"
    assert packet["can_render"] is True
    assert "references/paper-ink.md" in packet["required_refs"]
    assert "references/html-template.md" in packet["required_refs"]
    assert "reference-driven-generation" in packet["required_contracts"]


def test_docs_explain_core_four_defaults_and_explicit_selection_override():
    style_index = read_text(STYLE_INDEX)
    workflow = read_text(WORKFLOW_MD)
    skill = read_text(SKILL_MD)
    readme = read_text(README_MD)
    readme_zh = read_text(README_ZH)
    support_policy = read_json(SUPPORT_MATRIX)["policy"]["explicit_user_selection"]

    assert "Generator-Ready Recommendation Surface" in style_index
    assert "Reference-driven presets are design references with an agent generation path" in style_index
    assert "Use deterministic renderers when available; otherwise route reference-backed presets through reference-driven generation" in support_policy
    assert "deterministic renderer or reference-driven preset" in workflow
    assert "当前稳定生成器覆盖" in skill
    assert "Reference-driven presets remain opt-in generation paths" in readme
    assert "参考驱动型 preset 仍保留为显式选择的生成路径" in readme_zh

    outdated_claims = [
        "honor that selection",
        "任意当前 preset",
        "Still selectable directly",
        "Support tier only affects default recommendation priority",
        "Blud Sky",
    ]
    for text in (style_index, workflow, skill, readme, readme_zh, support_policy):
        for claim in outdated_claims:
            assert claim not in text
