from __future__ import annotations

import copy
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
import preset_capabilities  # noqa: E402
from preset_capabilities import (  # noqa: E402
    CANONICAL_PRESET_NAMES,
    get_preset_render_capability,
    renderable_recommendation_presets,
)
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


def test_support_states_cover_every_builtin_and_match_capabilities():
    matrix = read_json(SUPPORT_MATRIX)
    support_states = matrix["policy"]["support_states"]
    generation_states = ("native_deterministic_core", "unified_profile_renderer", "unsupported_archive")
    flattened = [
        preset
        for state in generation_states
        for preset in support_states[state]
    ]

    normalized_flat = [preset.lower() for preset in flattened]
    assert len(normalized_flat) == len(set(normalized_flat))
    assert set(normalized_flat) == set(PRESET_REFERENCE_MAP.keys())
    assert not set(support_states["native_deterministic_core"]) & set(support_states["unified_profile_renderer"])

    for normalized, reference in PRESET_REFERENCE_MAP.items():
        preset = CANONICAL_PRESET_NAMES[normalized]
        capability = get_preset_render_capability(preset)
        assert capability.canonical_preset == preset
        assert capability.reference_path.endswith(reference)
        if preset in support_states["native_deterministic_core"]:
            assert capability.generation_status == "ready"
            assert capability.renderer_strategy == "native"
        elif preset in support_states["unified_profile_renderer"]:
            assert capability.generation_status == "profile"
            assert capability.renderer_strategy == "unified_profile"
        else:
            raise AssertionError(f"{preset} is not assigned to a renderable support state")


def test_every_builtin_preset_can_render_on_explicit_request():
    for normalized, reference in PRESET_REFERENCE_MAP.items():
        preset = CANONICAL_PRESET_NAMES[normalized]
        capability = get_preset_render_capability(preset)

        assert capability.canonical_preset == preset
        assert capability.can_render is True
        assert capability.explicit_request_behavior == "render"
        assert capability.reference_path.endswith(reference)
        assert capability.generation_status in {"ready", "profile"}
        assert capability.renderer_strategy in {"native", "unified_profile"}


def test_no_builtin_preset_uses_reference_driven_as_primary_renderer_strategy():
    for normalized in PRESET_REFERENCE_MAP:
        preset = CANONICAL_PRESET_NAMES[normalized]
        capability = get_preset_render_capability(preset)

        assert capability.renderer_strategy != "reference_driven"
        assert capability.generation_status != "reference_driven"
        assert capability.explicit_request_behavior == "render"


def test_custom_prefixed_builtin_name_never_falls_through_to_builtin():
    capability = get_preset_render_capability("custom:terminal green")

    assert capability.can_render is False
    assert capability.generation_status == "unsupported"
    assert capability.renderer_strategy == "unsupported"


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


def test_capability_matrix_separates_recommendation_from_native_stability():
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
    profile_rendered = {
        capability.canonical_preset
        for capability in capabilities.values()
        if capability.generation_status == "profile"
    }

    assert deterministic_ready == {"Swiss Modern", "Enterprise Dark", "Data Story", "Blue Sky", "Chinese Chan"}
    assert default_recommended == {"Swiss Modern", "Enterprise Dark", "Data Story", "Blue Sky"}
    assert contextual == {"Chinese Chan"}
    assert "Paper & Ink" in profile_rendered
    assert "Terminal Green" in profile_rendered
    assert all(capability.renderer_strategy != "unsupported" for capability in capabilities.values())


def test_non_core_builtins_share_supported_reporting_tier():
    assert preset_support_tier("Paper & Ink") == "supported"
    assert preset_support_tier("Notebook Tabs") == "supported"
    assert preset_support_tier("Terminal Green") == "supported"


def test_explicit_selection_policy_keeps_non_default_presets_selectable():
    assert explicit_selection_is_allowed("Neon Cyber") is True
    assert explicit_selection_is_allowed("Paper & Ink") is True
    assert explicit_selection_is_allowed("Blue Sky") is True
    assert explicit_selection_is_allowed("Chinese Chan") is True


def test_profile_preset_builds_unified_profile_render_packet_without_claiming_native_renderer():
    brief = read_json(AUTO_DEMO)
    brief["style"]["preset"] = "Paper & Ink"

    contract = compile_style_contract("Paper & Ink")
    assert contract["preset"] == "Paper & Ink"

    validation_errors = validate_generation_brief_data(brief)
    assert validation_errors == []

    packet = build_render_packet(brief)
    assert packet["canonical_preset"] == "Paper & Ink"
    assert packet["reference_path"] == "references/paper-ink.md"
    assert packet["preset_generation_status"] == "profile"
    assert packet["renderer_strategy"] == "unified_profile"
    assert packet["render_path"] == "profile:paper-ink"
    assert packet["can_render"] is True
    assert "references/paper-ink.md" in packet["required_refs"]
    assert "references/html-template.md" in packet["required_refs"]
    assert "unified-profile-renderer" in packet["required_contracts"]


def test_support_states_are_the_only_generation_source(monkeypatch):
    matrix = read_json(SUPPORT_MATRIX)
    stale_matrix = copy.deepcopy(matrix)
    assert set(stale_matrix["tiers"]) == {"production", "supported", "experimental", "archive_candidate"}
    stale_matrix["tiers"]["archive_candidate"] = ["Terminal Green"]
    stale_matrix["tiers"]["production"] = stale_matrix["tiers"]["production"] + ["Terminal Green"]
    stale_matrix["tiers"]["supported"] = [
        preset for preset in stale_matrix["tiers"]["supported"] if preset != "Terminal Green"
    ]
    monkeypatch.setattr(preset_capabilities, "load_preset_support_matrix", lambda: stale_matrix)

    capability = get_preset_render_capability("Terminal Green")

    assert capability.can_render is True
    assert capability.generation_status == "profile"
    assert capability.renderer_strategy == "unified_profile"


def test_docs_explain_core_four_defaults_and_explicit_selection_override():
    style_index = read_text(STYLE_INDEX)
    workflow = read_text(WORKFLOW_MD)
    skill = read_text(SKILL_MD)
    readme = read_text(README_MD)
    readme_zh = read_text(README_ZH)
    support_policy = read_json(SUPPORT_MATRIX)["policy"]["explicit_user_selection"]

    assert "Generator-Ready Recommendation Surface" in style_index
    assert "All built-in presets are explicitly renderable" in style_index
    assert "All built-in presets render on explicit user selection" in support_policy
    assert "deterministic renderer or unified profile renderer" in workflow
    assert "当前稳定生成器覆盖" in skill
    assert "Profile-rendered presets are renderable" in readme
    assert "非核心 profile 可生成" in readme_zh

    outdated_claims = [
        "honor that selection",
        "任意当前 preset",
        "Still selectable directly",
        "Support tier only affects default recommendation priority",
        "Blud Sky",
        "Reference-driven presets are design references with an agent generation path",
        "Reference-driven presets remain opt-in generation paths",
        "参考驱动型 preset 仍保留为显式选择的生成路径",
        "reference_driven_generation_required",
    ]
    for text in (style_index, workflow, skill, readme, readme_zh, support_policy):
        for claim in outdated_claims:
            assert claim not in text
