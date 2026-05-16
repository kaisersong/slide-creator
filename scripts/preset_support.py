from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PRESET_SUPPORT_PATH = ROOT / "references" / "preset-support-tiers.json"
THEMES_DIR = ROOT / "themes"


def _normalize_preset_name(value: str | None) -> str:
    return (value or "").strip().lower()


def load_preset_support_matrix() -> dict:
    return json.loads(PRESET_SUPPORT_PATH.read_text(encoding="utf-8"))


def _is_custom_theme(preset: str) -> bool:
    key = _normalize_preset_name(preset).removeprefix("custom:").strip()
    theme_dir = THEMES_DIR / key
    return theme_dir.is_dir() and (theme_dir / "reference.md").exists()


def canonical_preset_name(preset: str) -> str:
    normalized = _normalize_preset_name(preset)
    matrix = load_preset_support_matrix()
    for tier_presets in matrix["tiers"].values():
        for candidate in tier_presets:
            if _normalize_preset_name(candidate) == normalized:
                return candidate
    if _is_custom_theme(preset):
        key = _normalize_preset_name(preset).removeprefix("custom:").strip()
        return (THEMES_DIR / key).name.title()
    raise KeyError(f"Unknown preset in support matrix: {preset}")


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
    matrix = load_preset_support_matrix()
    return list(matrix["policy"]["default_recommendation_presets"])


def explicit_selection_is_allowed(preset: str) -> bool:
    normalized = _normalize_preset_name(preset)
    matrix = load_preset_support_matrix()
    for tier_presets in matrix["tiers"].values():
        if any(_normalize_preset_name(candidate) == normalized for candidate in tier_presets):
            return True
    return _is_custom_theme(preset)
