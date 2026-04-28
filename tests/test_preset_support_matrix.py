from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
SUPPORT_MATRIX = ROOT / "references" / "preset-support-tiers.json"
STYLE_INDEX = ROOT / "references" / "style-index.md"
WORKFLOW_MD = ROOT / "references" / "workflow.md"
sys.path.insert(0, str(SCRIPTS))

from low_context import PRESET_REFERENCE_MAP  # noqa: E402
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


def test_paper_ink_outranks_notebook_tabs_in_current_tiering():
    assert preset_support_tier("Paper & Ink") == "supported"
    assert preset_support_tier("Notebook Tabs") == "experimental"


def test_explicit_selection_policy_keeps_non_default_presets_selectable():
    assert explicit_selection_is_allowed("Neon Cyber") is True
    assert explicit_selection_is_allowed("Paper & Ink") is True
    assert explicit_selection_is_allowed("Blue Sky") is True


def test_docs_explain_core_four_defaults_and_explicit_selection_override():
    style_index = read_text(STYLE_INDEX)
    workflow = read_text(WORKFLOW_MD)

    assert "Core Recommendation Surface (Phase 1)" in style_index
    assert "This is a recommendation surface, not a hard capability boundary." in style_index
    assert "If the user explicitly names any current preset, honor that selection." in style_index
    assert "Support tier only affects default recommendation priority." in workflow
    assert "with \"Other\" option for all current presets" in workflow
