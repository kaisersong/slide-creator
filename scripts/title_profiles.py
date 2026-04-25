from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "references" / "title-profile-registry.json"

STRUCTURAL_TITLE_PROFILES = {
    "vertical_title",
    "split_lockup",
    "glitch_lockup",
    "terminal_object",
}

COMMON_TITLE_LINE_CLASSES = {
    "title-line",
    "headline-line",
    "heading-line",
    "cta-line",
    "balance-line",
    "quote-line",
    "pull-line",
}

_REGISTRY_CACHE: dict[str, Any] | None = None


def _class_tokens(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(token) for token in value]
    return str(value).split()


def _normalize_preset_name(value: str | None) -> str:
    return (value or "").strip().lower()


def load_title_profile_registry() -> dict[str, Any]:
    global _REGISTRY_CACHE
    if _REGISTRY_CACHE is None:
        _REGISTRY_CACHE = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return _REGISTRY_CACHE


def registry_version() -> int:
    return int(load_title_profile_registry()["version"])


def list_registry_presets() -> list[str]:
    return list(load_title_profile_registry()["presets"].keys())


def detect_slide_layout_id(slide: Any) -> str | None:
    if slide is None:
        return None
    role = slide.get("data-export-role")
    if role:
        return str(role).strip()
    classes = [token for token in _class_tokens(slide.get("class", [])) if token != "slide"]
    return classes[0] if classes else None


def _resolve_preset_config(preset: str | None) -> tuple[str, dict[str, Any]]:
    registry = load_title_profile_registry()
    presets = registry["presets"]
    normalized = _normalize_preset_name(preset)
    for preset_name, config in presets.items():
        if _normalize_preset_name(preset_name) == normalized:
            return preset_name, config
    raise KeyError(f"Unknown title profile preset: {preset}")


def _node_has_any_class(node: Any, classes: list[str]) -> bool:
    node_classes = set(_class_tokens(node.get("class", [])))
    return any(cls in node_classes for cls in classes)


def _node_has_any_name(node: Any, names: list[str]) -> bool:
    return getattr(node, "name", "").lower() in {name.lower() for name in names}


def _node_has_all_attrs(node: Any, attrs: list[str]) -> bool:
    return all(node.get(attr) is not None for attr in attrs)


def _node_has_descendant_class(node: Any, classes: list[str]) -> bool:
    return any(node.find(class_=cls) is not None for cls in classes)


def _node_has_ancestor_class(node: Any, classes: list[str]) -> bool:
    current = node.parent
    allowed = set(classes)
    while current is not None:
        if any(cls in allowed for cls in _class_tokens(current.get("class", []))):
            return True
        current = current.parent
    return False


def _slide_has_any_class(slide: Any, classes: list[str]) -> bool:
    return any(cls in _class_tokens(slide.get("class", [])) for cls in classes)


def _profile_payload(profile_name: str, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    registry = load_title_profile_registry()
    payload = dict(registry["profiles"][profile_name])
    payload["profile"] = profile_name
    if overrides:
        for key in (
            "node_type",
            "measure_policy",
            "max_lines",
            "explicit_line_control_allowed",
            "auto_fix_policy",
            "required_companion_selectors",
            "required_attributes",
            "browser_selector",
        ):
            if key in overrides:
                payload[key] = overrides[key]
    return payload


def _matcher_matches(rule: dict[str, Any], node: Any, slide: Any, layout_id: str | None) -> bool:
    if rule.get("layout_ids") and layout_id not in rule["layout_ids"]:
        return False
    if rule.get("node_classes_any") and not _node_has_any_class(node, rule["node_classes_any"]):
        return False
    if rule.get("node_names_any") and not _node_has_any_name(node, rule["node_names_any"]):
        return False
    if rule.get("node_attrs_all") and not _node_has_all_attrs(node, rule["node_attrs_all"]):
        return False
    if rule.get("descendant_classes_any") and not _node_has_descendant_class(node, rule["descendant_classes_any"]):
        return False
    if rule.get("ancestor_classes_any") and not _node_has_ancestor_class(node, rule["ancestor_classes_any"]):
        return False
    if slide is not None and rule.get("slide_classes_any") and not _slide_has_any_class(slide, rule["slide_classes_any"]):
        return False
    return True


def resolve_title_profile(
    preset: str | None,
    *,
    layout_id: str | None = None,
    node: Any | None = None,
    slide: Any | None = None,
) -> dict[str, Any]:
    preset_name, config = _resolve_preset_config(preset)
    if node is not None and slide is None:
        slide = node.find_parent(class_="slide")
    layout_id = layout_id or detect_slide_layout_id(slide)

    base = _profile_payload(config["default_profile"])

    layout_overrides = config.get("layout_overrides", {})
    if layout_id and layout_id in layout_overrides:
        override = layout_overrides[layout_id]
        base.update(_profile_payload(override["profile"], override))

    if node is not None:
        for rule in config.get("matchers", []):
            if _matcher_matches(rule, node, slide, layout_id):
                base.update(_profile_payload(rule["profile"], rule))
                break

    base["preset"] = preset_name
    base["layout_id"] = layout_id
    return base


def is_horizontal_title_profile(profile: str) -> bool:
    return profile not in STRUCTURAL_TITLE_PROFILES


def is_structural_title_profile(profile: str) -> bool:
    return profile in STRUCTURAL_TITLE_PROFILES


def profile_allows_explicit_line_control(profile_data: dict[str, Any]) -> bool:
    return bool(profile_data.get("explicit_line_control_allowed", False))


def collect_title_candidate_nodes(slide: Any, preset: str | None) -> list[Any]:
    nodes: list[Any] = []
    seen: set[int] = set()

    for node in slide.find_all(["h1", "h2"]):
        if node.find_parent(["h1", "h2"]):
            continue
        marker = id(node)
        if marker not in seen:
            nodes.append(node)
            seen.add(marker)

    try:
        _preset_name, config = _resolve_preset_config(preset)
    except KeyError:
        return nodes

    for rule in config.get("matchers", []):
        selector = rule.get("browser_selector")
        if not selector:
            continue
        for node in slide.select(selector):
            marker = id(node)
            if marker not in seen:
                nodes.append(node)
                seen.add(marker)

    return nodes

