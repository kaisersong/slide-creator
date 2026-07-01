from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterator

from bs4 import BeautifulSoup
from bs4.element import Tag

from low_context import _preset_usage_rules, compile_style_contract
from preset_profile_specs import PROFILE_SPECS


VISIBLE_CSS_PROPERTIES = {
    "background",
    "background-color",
    "border",
    "border-bottom",
    "border-color",
    "border-left",
    "border-right",
    "border-top",
    "box-shadow",
    "color",
    "content",
    "display",
    "fill",
    "grid-template-columns",
    "height",
    "outline",
    "padding",
    "stroke",
    "transform",
    "width",
}

RUNTIME_CLASS_STOPWORDS = {
    "content",
    "edit-hotzone",
    "edit-toggle",
    "keyboard-hint",
    "nav-dots",
    "p-on",
    "progress-bar",
    "profile-content",
    "profile-slide",
    "reveal",
    "slide",
    "slide-content",
    "slide-credit",
    "slide-num-label",
    "title-balance",
    "title-line",
    "visible",
}


@dataclass(frozen=True)
class SignatureRequirement:
    classes: tuple[str, ...]
    ids: tuple[str, ...] = ()
    backgrounds: tuple[str, ...] = ()


@dataclass(frozen=True)
class SignaturePresence:
    visible_class_hits: tuple[str, ...]
    visible_id_hits: tuple[str, ...]
    background_hits: tuple[str, ...]
    ignored_marker_hits: tuple[str, ...]
    invisible_hits: tuple[str, ...]
    empty_shell_hits: tuple[str, ...]
    coverage: float | None
    integrity: float


def _selector_to_class(selector: str) -> str | None:
    if not selector.startswith(".") or "::" in selector:
        return None
    class_name = selector[1:]
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", class_name):
        return class_name
    return None


def _selector_to_id(selector: str) -> str | None:
    if not selector.startswith("#") or "::" in selector:
        return None
    value = selector[1:]
    if value and value != "slide-N":
        return value
    return None


def _dedupe(values: list[str]) -> tuple[str, ...]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return tuple(result)


def requirement_for_preset(preset: str) -> SignatureRequirement:
    if preset in PROFILE_SPECS:
        spec = PROFILE_SPECS[preset]
        classes = tuple(f".{class_name}" for class_name in spec.visible_signature_classes)
        ids = tuple(f"#{value}" for value in spec.visible_signature_ids)
        return SignatureRequirement(
            classes=classes,
            ids=ids,
            backgrounds=spec.background_signature_selectors,
        )

    usage_rules = _preset_usage_rules(preset)
    coverage_signature = usage_rules.get("coverage_signature", {}) if isinstance(usage_rules, dict) else {}
    if coverage_signature:
        return SignatureRequirement(
            classes=tuple(coverage_signature.get("required_classes", ())),
            backgrounds=tuple(coverage_signature.get("required_backgrounds", ())),
        )

    contract = compile_style_contract(preset)
    classes: list[str] = []
    ids: list[str] = []
    backgrounds: list[str] = []
    for selector in contract["required_signature_classes"]:
        class_name = _selector_to_class(selector)
        id_value = _selector_to_id(selector)
        if class_name:
            classes.append(f".{class_name}")
        elif id_value:
            ids.append(f"#{id_value}")
    for selector in contract["required_background_layers"]:
        class_name = _selector_to_class(selector)
        id_value = _selector_to_id(selector)
        if class_name:
            classes.append(f".{class_name}")
        elif id_value:
            ids.append(f"#{id_value}")
        else:
            backgrounds.append(selector)
    return SignatureRequirement(
        classes=_dedupe(classes),
        ids=_dedupe(ids),
        backgrounds=_dedupe(backgrounds),
    )


def _style_map(node: Tag) -> dict[str, str]:
    value = node.get("style")
    if not isinstance(value, str):
        return {}
    result: dict[str, str] = {}
    for declaration in value.split(";"):
        if ":" not in declaration:
            continue
        name, raw_value = declaration.split(":", 1)
        result[name.strip().lower()] = raw_value.strip().lower()
    return result


def _numeric_px(value: str) -> float | None:
    if value.strip() == "0":
        return 0.0
    match = re.search(r"(-?\d+(?:\.\d+)?)px\b", value)
    if not match:
        return None
    return float(match.group(1))


def _style_hides_node(style: dict[str, str]) -> bool:
    if style.get("display") == "none" or style.get("visibility") == "hidden":
        return True
    opacity = style.get("opacity")
    if opacity is not None:
        try:
            if float(opacity) < 0.1:
                return True
        except ValueError:
            pass
    width = _numeric_px(style.get("width", ""))
    height = _numeric_px(style.get("height", ""))
    if width is not None and height is not None and width <= 1 and height <= 1:
        return True
    left = _numeric_px(style.get("left", ""))
    if left is not None and left <= -9000:
        return True
    font_size = _numeric_px(style.get("font-size", ""))
    if font_size is not None and font_size <= 0:
        return True
    clip_path = style.get("clip-path", "")
    if "inset(50%)" in clip_path.replace(" ", ""):
        return True
    clip = style.get("clip", "")
    return "rect(" in clip


def _is_runtime_chrome(node: Tag) -> bool:
    classes = set(node.get("class", []))
    if classes and classes <= RUNTIME_CLASS_STOPWORDS:
        return True
    if node.get("id") in {"notes-panel", "notes-textarea", "editToggle", "slide-counter"}:
        return True
    return False


def _is_marker_node(node: Tag) -> bool:
    classes = set(node.get("class", []))
    if "profile-signature-markers" in classes:
        return True
    return any(str(item).startswith("preset-signature-") for item in classes)


def _is_hidden_or_marker_node(node: Tag) -> bool:
    current: Tag | None = node
    while current is not None and isinstance(current, Tag):
        if current.get("hidden") is not None or current.get("aria-hidden") == "true":
            return True
        if _is_marker_node(current):
            return True
        if _style_hides_node(_style_map(current)):
            return True
        parent = current.parent
        current = parent if isinstance(parent, Tag) else None
    return False


def _has_meaningful_visual_content(node: Tag) -> bool:
    if len(re.sub(r"\s+", "", node.get_text("", strip=True))) >= 2:
        return True
    if node.name in {"img", "svg", "canvas", "table", "code", "pre"}:
        return True
    return node.select_one("img,svg,canvas,table,code,pre,path,polygon,circle,rect,line") is not None


def iter_visible_signature_nodes(soup: BeautifulSoup, *, profile_mode: bool) -> Iterator[Tag]:
    if not profile_mode:
        for node in soup.select("[class],[id]"):
            if isinstance(node, Tag) and not _is_hidden_or_marker_node(node) and not _is_runtime_chrome(node):
                yield node
        return

    selector = (
        "section.slide .slide-content [class],"
        "section.slide .profile-content [class],"
        "section.slide .slide-content [id],"
        "section.slide .profile-content [id]"
    )
    for node in soup.select(selector):
        if not isinstance(node, Tag):
            continue
        if _is_runtime_chrome(node) or _is_hidden_or_marker_node(node):
            yield from ()
            continue
        if not _has_meaningful_visual_content(node):
            continue
        yield node


def _collect_css_text(soup: BeautifulSoup) -> str:
    return "\n\n".join(style.get_text("\n") for style in soup.find_all("style"))


def _extract_rule_blocks(css_text: str, selector: str) -> list[str]:
    return [match.group(1) for match in re.finditer(rf"{re.escape(selector)}\s*\{{(.*?)\}}", css_text, re.DOTALL)]


def selector_has_visible_rule(css_text: str, selector: str) -> bool:
    if "profile-signature-markers" in selector or "preset-signature-" in selector:
        return False
    blocks = _extract_rule_blocks(css_text, selector)
    for block in blocks:
        declarations = {
            name.strip().lower(): value.strip()
            for name, value in (part.split(":", 1) for part in block.split(";") if ":" in part)
        }
        if not declarations:
            continue
        if set(declarations) <= {"--profile-component-present"}:
            continue
        if any(name in VISIBLE_CSS_PROPERTIES for name in declarations):
            return True
    return False


def collect_signature_presence(html_text: str, preset: str) -> SignaturePresence:
    soup = BeautifulSoup(html_text, "html.parser")
    requirement = requirement_for_preset(preset)
    profile_mode = preset in PROFILE_SPECS
    required_classes = set(requirement.classes)
    required_ids = set(requirement.ids)
    required_backgrounds = set(requirement.backgrounds)

    visible_classes: set[str] = set()
    visible_ids: set[str] = set()
    ignored_marker: set[str] = set()
    invisible: set[str] = set()
    empty_shell: set[str] = set()

    for node in soup.select("[class],[id]"):
        classes = {f".{class_name}" for class_name in node.get("class", [])}
        ids = {f"#{node.get('id')}"} if node.get("id") else set()
        matched = (classes & required_classes) | (ids & required_ids)
        if not matched:
            continue
        if _is_marker_node(node) or _is_runtime_chrome(node):
            ignored_marker.update(matched)
        elif _is_hidden_or_marker_node(node):
            invisible.update(matched)
        elif profile_mode and not _has_meaningful_visual_content(node):
            empty_shell.update(matched)

    for node in iter_visible_signature_nodes(soup, profile_mode=profile_mode):
        for class_name in node.get("class", []):
            selector = f".{class_name}"
            if selector in required_classes:
                visible_classes.add(selector)
        node_id = node.get("id")
        if node_id and f"#{node_id}" in required_ids:
            visible_ids.add(f"#{node_id}")

    css_text = _collect_css_text(soup)
    background_hits = {selector for selector in required_backgrounds if selector_has_visible_rule(css_text, selector)}
    total = len(required_classes | required_ids | required_backgrounds)
    hit_total = len(visible_classes | visible_ids | background_hits)
    coverage = round(hit_total / total, 4) if total else None
    # Demo-derived renderers can preserve decorative empty elements while also
    # attaching the same required class to real visible content. Penalize a
    # class only when it has no visible counterpart.
    visible_selectors = visible_classes | visible_ids | background_hits
    bad_total = len((ignored_marker | invisible | empty_shell) - visible_selectors)
    integrity = round(hit_total / (hit_total + bad_total), 4) if hit_total or bad_total else 1.0

    return SignaturePresence(
        visible_class_hits=tuple(sorted(visible_classes)),
        visible_id_hits=tuple(sorted(visible_ids)),
        background_hits=tuple(sorted(background_hits)),
        ignored_marker_hits=tuple(sorted(ignored_marker)),
        invisible_hits=tuple(sorted(invisible)),
        empty_shell_hits=tuple(sorted(empty_shell)),
        coverage=coverage,
        integrity=integrity,
    )
