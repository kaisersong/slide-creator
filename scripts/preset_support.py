from __future__ import annotations

import json
from pathlib import Path

from preset_capabilities import (
    PRESET_SUPPORT_PATH,
    canonical_preset_name as capability_canonical_preset_name,
    default_recommendation_presets as capability_default_recommendation_presets,
    get_preset_render_capability,
    is_custom_theme,
    normalize_preset_name,
)

def _discover_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "references" / "preset-support-tiers.json").exists():
            return candidate
    return here.parent


def _normalize_preset_name(value: str | None) -> str:
    return normalize_preset_name(value)


def load_preset_support_matrix() -> dict:
    return json.loads(PRESET_SUPPORT_PATH.read_text(encoding="utf-8"))


def _is_custom_theme(preset: str) -> bool:
    return is_custom_theme(preset)


def canonical_preset_name(preset: str) -> str:
    return capability_canonical_preset_name(preset)


def preset_support_tier(preset: str) -> str:
    normalized = _normalize_preset_name(preset)
    matrix = load_preset_support_matrix()
    for tier, tier_presets in matrix["tiers"].items():
        if any(_normalize_preset_name(candidate) == normalized for candidate in tier_presets):
            return tier
    if _is_custom_theme(preset):
        return "custom"
    raise KeyError(f"Unknown preset in support matrix: {preset}")


def list_tier_presets(tier: str) -> list[str]:
    matrix = load_preset_support_matrix()
    if tier not in matrix["tiers"]:
        raise KeyError(f"Unknown support tier: {tier}")
    return list(matrix["tiers"][tier])


def default_recommendation_presets() -> list[str]:
    return capability_default_recommendation_presets()


def explicit_selection_is_allowed(preset: str) -> bool:
    return get_preset_render_capability(preset).can_render
