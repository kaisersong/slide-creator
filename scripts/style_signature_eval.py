from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag


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

SEMANTIC_VISUALS = {"img", "picture", "svg", "canvas", "table", "pre", "code"}
SVG_GRAPHICS = {"path", "rect", "circle", "ellipse", "line", "polyline", "polygon", "text", "image", "use"}


@dataclass(frozen=True)
class SelectorGroupRequirement:
    name: str
    selectors: tuple[str, ...]
    match: str = "any"
    scope: str = "document"
    page_buckets: tuple[str, ...] = ()
    weight: float = 1.0
    minimum_group_score: float = 1.0
    minimum_bucket_count: int | None = None
    content_required: bool = True


@dataclass(frozen=True)
class SignatureRequirement:
    groups: tuple[SelectorGroupRequirement, ...]

    @property
    def classes(self) -> tuple[str, ...]:
        return _simple_selectors(self.groups, prefix=".")

    @property
    def ids(self) -> tuple[str, ...]:
        return _simple_selectors(self.groups, prefix="#")

    @property
    def backgrounds(self) -> tuple[str, ...]:
        return ()


@dataclass(frozen=True)
class GroupPresence:
    name: str
    score: float | None
    integrity: float | None
    applicable_page_count: int | None
    matched_page_count: int | None
    selector_hits: tuple[str, ...]
    invalid_selectors: tuple[str, ...]


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
    groups: tuple[GroupPresence, ...]


def _simple_selectors(groups: tuple[SelectorGroupRequirement, ...], *, prefix: str) -> tuple[str, ...]:
    values: list[str] = []
    pattern = r"\.[A-Za-z][A-Za-z0-9_-]*" if prefix == "." else r"#[A-Za-z][A-Za-z0-9_-]*"
    for group in groups:
        for selector in group.selectors:
            if re.fullmatch(pattern, selector) and selector not in values:
                values.append(selector)
    return tuple(values)


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


def _numeric_size(value: str) -> float | None:
    if value.strip() == "0":
        return 0.0
    match = re.search(r"(-?\d+(?:\.\d+)?)(?:px|rem|em|%|vw|vh)?\b", value)
    return float(match.group(1)) if match else None


def _style_hides_node(style: dict[str, str]) -> bool:
    if style.get("display") == "none" or style.get("visibility") in {"hidden", "collapse"}:
        return True
    try:
        if "opacity" in style and float(style["opacity"]) <= 0.05:
            return True
    except ValueError:
        pass
    width = _numeric_size(style.get("width", ""))
    height = _numeric_size(style.get("height", ""))
    if width is not None and height is not None and width <= 1 and height <= 1:
        return True
    left = _numeric_size(style.get("left", ""))
    if left is not None and left <= -9000:
        return True
    font_size = _numeric_size(style.get("font-size", ""))
    if font_size is not None and font_size <= 0:
        return True
    compact_clip = style.get("clip-path", "").replace(" ", "")
    return "inset(50%)" in compact_clip or "rect(" in style.get("clip", "")


def _is_marker_node(node: Tag) -> bool:
    classes = set(node.get("class", []))
    return "profile-signature-markers" in classes or any(
        str(item).startswith("preset-signature-") for item in classes
    )


def _is_runtime_chrome(node: Tag) -> bool:
    classes = set(node.get("class", []))
    if classes and classes <= RUNTIME_CLASS_STOPWORDS:
        return True
    return node.get("id") in {"notes-panel", "notes-textarea", "editToggle", "slide-counter"}


def _invalid_visibility_reason(node: Tag) -> str | None:
    current: Tag | None = node
    while current is not None and isinstance(current, Tag):
        if _is_marker_node(current):
            return "marker"
        if current.has_attr("hidden") or str(current.get("aria-hidden", "")).lower() == "true":
            return "hidden"
        if _style_hides_node(_style_map(current)):
            return "hidden"
        parent = current.parent
        current = parent if isinstance(parent, Tag) else None
    return None


def _explicitly_zero_sized(node: Tag) -> bool:
    style = _style_map(node)
    width = _numeric_size(style.get("width", ""))
    height = _numeric_size(style.get("height", ""))
    return width is not None and height is not None and width <= 0 and height <= 0


def _svg_has_graphics(node: Tag) -> bool:
    return node.name == "svg" and any(node.find(name) is not None for name in SVG_GRAPHICS)


def _has_meaningful_content(node: Tag) -> bool:
    if len(re.sub(r"\s+", "", node.get_text("", strip=True))) >= 2:
        return True
    candidates: list[Tag] = []
    if node.name in SEMANTIC_VISUALS:
        candidates.append(node)
    candidates.extend(item for item in node.find_all(SEMANTIC_VISUALS) if isinstance(item, Tag))
    for candidate in candidates:
        if _invalid_visibility_reason(candidate) or _explicitly_zero_sized(candidate):
            continue
        if candidate.name == "svg" and not _svg_has_graphics(candidate):
            continue
        return True
    return False


def _select(root: BeautifulSoup | Tag, selector: str) -> list[Tag]:
    try:
        return [item for item in root.select(selector) if isinstance(item, Tag)]
    except Exception:
        return []


def _page_bucket(slide: Tag, index: int, total: int) -> str:
    explicit = str(slide.get("data-page-bucket", "")).strip().lower()
    if explicit in {"cover", "content", "closing"}:
        return explicit
    if total <= 1 or index == 0:
        return "cover"
    if index == total - 1:
        return "closing"
    return "content"


def _occurrence_state(node: Tag, *, content_required: bool, selector: str | None = None) -> str:
    if (
        selector
        and selector.startswith(".")
        and selector != ".profile-slide"
        and node.name == "section"
        and "slide" in set(node.get("class", []))
    ):
        return "marker"
    visibility_reason = _invalid_visibility_reason(node)
    if visibility_reason:
        return visibility_reason
    if content_required and not _has_meaningful_content(node):
        return "empty"
    return "valid"


def _selector_integrity(
    nodes: list[Tag],
    *,
    content_required: bool,
    selector: str,
) -> tuple[float | None, set[str]]:
    if not nodes:
        return None, set()
    states = {
        _occurrence_state(node, content_required=content_required, selector=selector)
        for node in nodes
    }
    return (1.0 if states == {"valid"} else 0.0), states


def collect_signature_presence(html_text: str, requirement: SignatureRequirement) -> SignaturePresence:
    soup = BeautifulSoup(html_text, "html.parser")
    slides = [item for item in soup.select("section.slide, .slide") if isinstance(item, Tag)]
    deduped_slides: list[Tag] = []
    for slide in slides:
        if slide not in deduped_slides:
            deduped_slides.append(slide)
    buckets = [_page_bucket(slide, index, len(deduped_slides)) for index, slide in enumerate(deduped_slides)]

    group_results: list[GroupPresence] = []
    visible_hits: set[str] = set()
    marker_hits: set[str] = set()
    invisible_hits: set[str] = set()
    empty_hits: set[str] = set()
    weighted_scores: list[tuple[float, float]] = []
    weighted_integrities: list[tuple[float, float]] = []

    for group in requirement.groups:
        applicable: list[Tag] | None = None
        if group.scope == "slide":
            applicable = [
                slide for slide, bucket in zip(deduped_slides, buckets, strict=False)
                if not group.page_buckets or bucket in group.page_buckets
            ]
            if not applicable:
                group_results.append(GroupPresence(group.name, None, None, 0, 0, (), ()))
                continue

        selector_hits: set[str] = set()
        invalid_selectors: set[str] = set()
        selector_integrities: list[float] = []
        matched_page_count: int | None = None

        if group.scope == "document":
            selector_scores: list[float] = []
            for selector in group.selectors:
                nodes = _select(soup, selector)
                states = [
                    _occurrence_state(node, content_required=group.content_required, selector=selector)
                    for node in nodes
                ]
                valid_nodes = [node for node, state in zip(nodes, states, strict=False) if state == "valid"]
                hit = bool(valid_nodes)
                selector_scores.append(1.0 if hit else 0.0)
                if hit:
                    selector_hits.add(selector)
                    visible_hits.add(selector)
                integrity, state_set = _selector_integrity(
                    nodes,
                    content_required=group.content_required,
                    selector=selector,
                )
                if integrity is not None:
                    selector_integrities.append(integrity)
                    if integrity == 0:
                        invalid_selectors.add(selector)
                if "marker" in state_set:
                    marker_hits.add(selector)
                if "hidden" in state_set:
                    invisible_hits.add(selector)
                if "empty" in state_set:
                    empty_hits.add(selector)
            score = max(selector_scores, default=0.0) if group.match == "any" else sum(selector_scores) / max(1, len(selector_scores))
            applicable_page_count = None
        else:
            page_scores: list[float] = []
            matched_pages = 0
            all_nodes_by_selector: dict[str, list[Tag]] = {selector: [] for selector in group.selectors}
            for slide in applicable or []:
                selector_scores = []
                for selector in group.selectors:
                    nodes = _select(slide, selector)
                    all_nodes_by_selector[selector].extend(nodes)
                    hit = any(
                        _occurrence_state(node, content_required=group.content_required, selector=selector) == "valid"
                        for node in nodes
                    )
                    selector_scores.append(1.0 if hit else 0.0)
                    if hit:
                        selector_hits.add(selector)
                        visible_hits.add(selector)
                page_score = max(selector_scores, default=0.0) if group.match == "any" else sum(selector_scores) / max(1, len(selector_scores))
                page_scores.append(page_score)
                if page_score > 0:
                    matched_pages += 1
            score = sum(page_scores) / len(page_scores)
            applicable_page_count = len(applicable or [])
            matched_page_count = matched_pages
            for selector, nodes in all_nodes_by_selector.items():
                integrity, states = _selector_integrity(
                    nodes,
                    content_required=group.content_required,
                    selector=selector,
                )
                if integrity is not None:
                    selector_integrities.append(integrity)
                    if integrity == 0:
                        invalid_selectors.add(selector)
                if "marker" in states:
                    marker_hits.add(selector)
                if "hidden" in states:
                    invisible_hits.add(selector)
                if "empty" in states:
                    empty_hits.add(selector)

        group_integrity = sum(selector_integrities) / len(selector_integrities) if selector_integrities else None
        weighted_scores.append((score, group.weight))
        if group_integrity is not None:
            weighted_integrities.append((group_integrity, group.weight))
        group_results.append(
            GroupPresence(
                group.name,
                round(score, 4),
                round(group_integrity, 4) if group_integrity is not None else None,
                applicable_page_count,
                matched_page_count,
                tuple(sorted(selector_hits)),
                tuple(sorted(invalid_selectors)),
            )
        )

    total_weight = sum(weight for _score, weight in weighted_scores)
    coverage = sum(score * weight for score, weight in weighted_scores) / total_weight if total_weight else None
    integrity_weight = sum(weight for _score, weight in weighted_integrities)
    integrity = sum(score * weight for score, weight in weighted_integrities) / integrity_weight if integrity_weight else 1.0
    classes = tuple(sorted(item for item in visible_hits if item.startswith(".")))
    ids = tuple(sorted(item for item in visible_hits if item.startswith("#")))
    return SignaturePresence(
        visible_class_hits=classes,
        visible_id_hits=ids,
        background_hits=(),
        ignored_marker_hits=tuple(sorted(marker_hits)),
        invisible_hits=tuple(sorted(invisible_hits)),
        empty_shell_hits=tuple(sorted(empty_hits)),
        coverage=round(coverage, 4) if coverage is not None else None,
        integrity=round(integrity, 4),
        groups=tuple(group_results),
    )
