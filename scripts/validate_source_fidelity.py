#!/usr/bin/env python3
"""Validate generated slide HTML against a deterministic source-coverage map.

This gate performs normalized exact text matching and explicit DOM relation checks.
It does not attempt semantic or NLP-based equivalence.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Iterable

from bs4 import BeautifulSoup, Comment, NavigableString, Tag


MIN_RETENTION = 0.90
ORDER_RELATIONS = {
    "before",
    "dom_order",
    "order",
    "ordered",
    "precedes",
    "sequence",
    "sequence_before",
}
CONTAINMENT_RELATIONS = {
    "contains",
    "containment",
    "includes",
    "parent_child",
    "parent_to_child",
}
NOTE_CLASS_TOKENS = {
    "notes",
    "notes-content",
    "notes-panel",
    "presenter-note",
    "presenter-notes",
    "speaker-note",
    "speaker-notes",
}
NON_CONTENT_TAGS = {"script", "style", "template", "noscript"}
HIDDEN_DECLARATION_RE = re.compile(
    r"(?:^|;)\s*(display|visibility)\s*:\s*(none|hidden)\s*(?:!important\s*)?(?:;|$)",
    re.IGNORECASE,
)
CSS_RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
RELATION_TOKEN_RE = re.compile(r"[\s,;]+")


class CoverageError(ValueError):
    """Raised when the coverage contract is invalid."""


def _matches_simple_compound(tag: Tag, compound: str) -> bool:
    """Match a small CSS subset when an older bs4 lacks soupsieve."""
    position = 0
    tag_match = re.match(r"(?:\*|[a-zA-Z][\w-]*)", compound)
    if tag_match:
        expected_tag = tag_match.group(0)
        if expected_tag != "*" and tag.name.casefold() != expected_tag.casefold():
            return False
        position = tag_match.end()
    while position < len(compound):
        marker = compound[position]
        if marker in ".#":
            match = re.match(r"[.#]([\w-]+)", compound[position:])
            if not match:
                raise ValueError(f"unsupported selector: {compound}")
            value = match.group(1)
            if marker == "." and value not in tag.get("class", []):
                return False
            if marker == "#" and tag.get("id") != value:
                return False
            position += len(match.group(0))
            continue
        if marker == "[":
            end = compound.find("]", position + 1)
            if end < 0:
                raise ValueError(f"unsupported selector: {compound}")
            expression = compound[position + 1 : end].strip()
            if "=" in expression:
                attribute, expected = expression.split("=", 1)
                attribute = attribute.strip()
                expected = expected.strip().strip("\"'")
                if str(tag.get(attribute, "")) != expected:
                    return False
            elif not expression or not tag.has_attr(expression):
                return False
            position = end + 1
            continue
        raise ValueError(f"unsupported selector: {compound}")
    return True


def _fallback_select(root: Tag, selector: str) -> list[Tag]:
    result: list[Tag] = []
    seen: set[int] = set()
    for group in selector.split(","):
        compounds = group.strip().split()
        if not compounds or any(any(symbol in item for symbol in (">", "+", "~", ":")) for item in compounds):
            raise ValueError(f"unsupported selector: {selector}")
        for candidate in root.find_all(True):
            if not _matches_simple_compound(candidate, compounds[-1]):
                continue
            ancestor = candidate.parent
            valid = True
            for compound in reversed(compounds[:-1]):
                while isinstance(ancestor, Tag) and ancestor is not root.parent:
                    if _matches_simple_compound(ancestor, compound):
                        ancestor = ancestor.parent
                        break
                    ancestor = ancestor.parent
                else:
                    valid = False
                    break
            if valid and id(candidate) not in seen:
                seen.add(id(candidate))
                result.append(candidate)
    return result


def _select(root: Tag, selector: str) -> list[Tag]:
    try:
        return list(root.select(selector))
    except NotImplementedError:
        return _fallback_select(root, selector)


def _normalise_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return "".join(value.split())


def _relation_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")


def _number(value: Any, label: str, *, minimum: float = 0.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CoverageError(f"{label} must be a number")
    result = float(value)
    if not math.isfinite(result) or result < minimum:
        raise CoverageError(f"{label} must be finite and >= {minimum}")
    return result


def _non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CoverageError(f"{label} must be a non-empty string")
    return value.strip()


def _read_threshold(coverage: dict[str, Any], name: str) -> float:
    thresholds = coverage.get("thresholds", {})
    if thresholds is None:
        thresholds = {}
    if not isinstance(thresholds, dict):
        raise CoverageError("thresholds must be an object")
    value = coverage.get(f"{name}_threshold", thresholds.get(name, MIN_RETENTION))
    result = _number(value, f"thresholds.{name}")
    if not MIN_RETENTION <= result <= 1.0:
        raise CoverageError(
            f"thresholds.{name} must be between {MIN_RETENTION:.2f} and 1.0"
        )
    return result


def _validate_coverage(raw: Any) -> tuple[dict[str, Any], float, float]:
    if not isinstance(raw, dict):
        raise CoverageError("coverage JSON root must be an object")
    text_threshold = _read_threshold(raw, "text_retention")
    relation_threshold = _read_threshold(raw, "relation_retention")
    slides = raw.get("slides")
    if not isinstance(slides, list) or not slides:
        raise CoverageError("slides must be a non-empty array")

    seen_slide_numbers: set[int] = set()
    for slide_index, slide in enumerate(slides):
        prefix = f"slides[{slide_index}]"
        if not isinstance(slide, dict):
            raise CoverageError(f"{prefix} must be an object")
        slide_number = slide.get("slide_number")
        if isinstance(slide_number, bool) or not isinstance(slide_number, int) or slide_number < 1:
            raise CoverageError(f"{prefix}.slide_number must be a positive integer")
        if slide_number in seen_slide_numbers:
            raise CoverageError(f"duplicate slide_number: {slide_number}")
        seen_slide_numbers.add(slide_number)

        units = slide.get("units")
        if not isinstance(units, list) or not units:
            raise CoverageError(f"{prefix}.units must be a non-empty array")
        unit_ids: set[str] = set()
        for unit_index, unit in enumerate(units):
            unit_prefix = f"{prefix}.units[{unit_index}]"
            if not isinstance(unit, dict):
                raise CoverageError(f"{unit_prefix} must be an object")
            unit_id = _non_empty_string(unit.get("id"), f"{unit_prefix}.id")
            if unit_id in unit_ids:
                raise CoverageError(f"duplicate unit id on slide {slide_number}: {unit_id}")
            unit_ids.add(unit_id)
            _non_empty_string(unit.get("text"), f"{unit_prefix}.text")
            _number(unit.get("weight"), f"{unit_prefix}.weight", minimum=0.0)
            if not isinstance(unit.get("protected"), bool):
                raise CoverageError(f"{unit_prefix}.protected must be a boolean")
            for optional in ("selector", "source_ref"):
                if optional in unit:
                    _non_empty_string(unit[optional], f"{unit_prefix}.{optional}")
            if "selector" in unit:
                try:
                    _select(BeautifulSoup("<div></div>", "html.parser"), unit["selector"])
                except Exception as exc:
                    raise CoverageError(f"{unit_prefix}.selector is invalid: {exc}") from exc
        if sum(float(unit["weight"]) for unit in units) <= 0:
            raise CoverageError(f"{prefix}.units must have positive total weight")

        relations = slide.get("relations")
        if not isinstance(relations, list):
            raise CoverageError(f"{prefix}.relations must be an array")
        relation_ids: set[str] = set()
        for relation_index, relation in enumerate(relations):
            relation_prefix = f"{prefix}.relations[{relation_index}]"
            if not isinstance(relation, dict):
                raise CoverageError(f"{relation_prefix} must be an object")
            relation_id = _non_empty_string(relation.get("id"), f"{relation_prefix}.id")
            if relation_id in relation_ids:
                raise CoverageError(
                    f"duplicate relation id on slide {slide_number}: {relation_id}"
                )
            relation_ids.add(relation_id)
            _non_empty_string(relation.get("type"), f"{relation_prefix}.type")
            source = _non_empty_string(relation.get("from"), f"{relation_prefix}.from")
            target = _non_empty_string(relation.get("to"), f"{relation_prefix}.to")
            if source == target:
                raise CoverageError(f"{relation_prefix}.from and .to must differ")
            _number(relation.get("weight"), f"{relation_prefix}.weight", minimum=0.0)
            if not isinstance(relation.get("protected"), bool):
                raise CoverageError(f"{relation_prefix}.protected must be a boolean")
        if relations and sum(float(relation["weight"]) for relation in relations) <= 0:
            raise CoverageError(f"{prefix}.relations must have positive total weight")

    expected_numbers = list(range(1, len(slides) + 1))
    actual_numbers = sorted(seen_slide_numbers)
    if actual_numbers != expected_numbers:
        raise CoverageError(
            f"slide_number values must be consecutive from 1: expected {expected_numbers}, "
            f"got {actual_numbers}"
        )
    return raw, text_threshold, relation_threshold


def _inline_hidden(tag: Tag) -> bool:
    if tag.has_attr("hidden"):
        return True
    if str(tag.get("aria-hidden", "")).strip().casefold() == "true":
        return True
    return bool(HIDDEN_DECLARATION_RE.search(str(tag.get("style", ""))))


def _css_hidden_tags(soup: BeautifulSoup) -> set[int]:
    hidden: set[int] = set()
    for style in soup.find_all("style"):
        css = CSS_COMMENT_RE.sub("", style.get_text(" "))
        for selector_group, declarations in CSS_RULE_RE.findall(css):
            if not HIDDEN_DECLARATION_RE.search(declarations):
                continue
            if selector_group.lstrip().startswith("@"):
                continue
            for selector in selector_group.split(","):
                selector = selector.strip()
                if not selector:
                    continue
                try:
                    hidden.update(id(tag) for tag in _select(soup, selector))
                except Exception:
                    # Generated CSS can contain browser-only or malformed selectors. Inline
                    # visibility and valid selectors remain enforceable without aborting.
                    continue
    return hidden


def _is_note_element(tag: Tag, slide: Tag) -> bool:
    if tag is not slide and tag.has_attr("data-notes"):
        return True
    if tag.has_attr("data-speaker-note") or tag.has_attr("data-speaker-notes"):
        return True
    tokens = {str(token).casefold() for token in tag.get("class", [])}
    if tokens & NOTE_CLASS_TOKENS:
        return True
    element_id = str(tag.get("id", "")).casefold()
    return element_id in NOTE_CLASS_TOKENS


def _is_visible(tag: Tag, slide: Tag, css_hidden: set[int]) -> bool:
    current: Tag | None = tag
    while current is not None:
        if current.name in NON_CONTENT_TAGS:
            return False
        if id(current) in css_hidden or _inline_hidden(current):
            return False
        if _is_note_element(current, slide):
            return False
        if current is slide:
            return True
        parent = current.parent
        current = parent if isinstance(parent, Tag) else None
    return False


def _visible_text(root: Tag, slide: Tag, css_hidden: set[int]) -> str:
    if not _is_visible(root, slide, css_hidden):
        return ""
    fragments: list[str] = []
    for descendant in root.descendants:
        if not isinstance(descendant, NavigableString) or isinstance(descendant, Comment):
            continue
        parent = descendant.parent
        if isinstance(parent, Tag) and _is_visible(parent, slide, css_hidden):
            fragments.append(str(descendant))
    return _normalise_text(" ".join(fragments))


def _top_level_slides(soup: BeautifulSoup) -> list[Tag]:
    slides = [
        tag
        for tag in soup.find_all(True)
        if "slide" in tag.get("class", [])
    ]
    if not slides:
        slides = list(soup.find_all("section", attrs={"data-slide-number": True}))
    result: list[Tag] = []
    slide_ids = {id(slide) for slide in slides}
    for slide in slides:
        ancestor = slide.parent
        nested = False
        while isinstance(ancestor, Tag):
            if id(ancestor) in slide_ids:
                nested = True
                break
            ancestor = ancestor.parent
        if not nested:
            result.append(slide)
    return result


def _describe_node(tag: Tag) -> str:
    description = tag.name
    if tag.get("id"):
        description += f"#{tag['id']}"
    classes = tag.get("class", [])
    if classes:
        description += "".join(f".{name}" for name in classes[:3])
    if tag.get("data-source-ref"):
        description += f"[data-source-ref={tag['data-source-ref']!r}]"
    return description


def _unit_candidates(
    slide: Tag,
    unit: dict[str, Any],
    css_hidden: set[int],
) -> list[Tag]:
    source_ref = unit.get("source_ref")
    selector = unit.get("selector")
    if source_ref is not None:
        candidates = [
            tag
            for tag in slide.find_all(attrs={"data-source-ref": True})
            if isinstance(tag, Tag)
            and source_ref in str(tag.get("data-source-ref", "")).split()
        ]
        if source_ref in str(slide.get("data-source-ref", "")).split():
            candidates.insert(0, slide)
        if selector:
            selected = {id(tag) for tag in _select(slide, selector)}
            candidates = [tag for tag in candidates if id(tag) in selected]
    elif selector:
        candidates = _select(slide, selector)
    else:
        candidates = [slide]
    return [tag for tag in candidates if _is_visible(tag, slide, css_hidden)]


def _evaluate_units(
    slide: Tag,
    units: list[dict[str, Any]],
    css_hidden: set[int],
    threshold: float,
) -> dict[str, Any]:
    results: list[dict[str, Any] | None] = [None] * len(units)
    consumed_source_nodes: set[int] = set()
    evaluation_order = sorted(
        range(len(units)),
        key=lambda index: (
            not bool(units[index]["protected"]),
            -float(units[index]["weight"]),
            index,
        ),
    )

    for index in evaluation_order:
        unit = units[index]
        expected = _normalise_text(unit["text"])
        candidates = _unit_candidates(slide, unit, css_hidden)
        matching = [
            candidate
            for candidate in candidates
            if expected and expected in _visible_text(candidate, slide, css_hidden)
        ]
        enforce_single_use = unit.get("source_ref") is not None
        available = [
            candidate
            for candidate in matching
            if not enforce_single_use or id(candidate) not in consumed_source_nodes
        ]
        matched = bool(available)
        evidence = available[0] if matched else None
        if matched and enforce_single_use and evidence is not None:
            consumed_source_nodes.add(id(evidence))
        if matched:
            reason = "matched_normalized_visible_text"
        elif matching and enforce_single_use:
            reason = "source_ref_evidence_already_used"
        elif not candidates and unit.get("source_ref") is not None:
            reason = "visible_source_ref_not_found"
        elif not candidates and unit.get("selector") is not None:
            reason = "visible_selector_match_not_found"
        else:
            reason = "normalized_visible_text_not_found"
        results[index] = {
            "id": unit["id"],
            "matched": matched,
            "protected": unit["protected"],
            "weight": float(unit["weight"]),
            "source_ref": unit.get("source_ref"),
            "selector": unit.get("selector"),
            "evidence": _describe_node(evidence) if evidence is not None else None,
            "reason": reason,
        }

    final_results = [result for result in results if result is not None]
    total_weight = sum(float(unit["weight"]) for unit in units)
    matched_weight = sum(
        float(unit["weight"])
        for unit, result in zip(units, final_results)
        if result["matched"]
    )
    score = matched_weight / total_weight
    missing_protected = [
        result["id"]
        for result in final_results
        if result["protected"] and not result["matched"]
    ]
    passed = score + 1e-12 >= threshold and not missing_protected
    return {
        "pass": passed,
        "score": round(score, 6),
        "threshold": threshold,
        "matched_weight": matched_weight,
        "total_weight": total_weight,
        "protected_pass": not missing_protected,
        "missing_protected": missing_protected,
        "units": final_results,
    }


def _relation_marker_matches(tag: Tag, relation: dict[str, Any]) -> bool:
    raw = str(tag.get("data-relation", "")).strip().casefold()
    if not raw:
        return False
    accepted = {relation["id"].casefold(), relation["type"].casefold()}
    return raw in accepted or bool(accepted & set(RELATION_TOKEN_RE.split(raw)))


def _is_descendant_or_self(child: Tag, parent: Tag) -> bool:
    if child is parent:
        return True
    return any(ancestor is parent for ancestor in child.parents)


def _evaluate_relation(
    slide: Tag,
    relation: dict[str, Any],
    css_hidden: set[int],
    dom_order: dict[int, int],
) -> tuple[bool, str, str | None]:
    visible_tags = [
        tag
        for tag in slide.find_all(True)
        if isinstance(tag, Tag) and _is_visible(tag, slide, css_hidden)
    ]
    sources = [
        tag
        for tag in visible_tags
        if relation["from"] in {tag.get("data-node-id"), tag.get("data-group-id")}
    ]
    targets = [
        tag
        for tag in visible_tags
        if relation["to"] in {tag.get("data-node-id"), tag.get("data-group-id")}
    ]
    edges = [tag for tag in visible_tags if tag.has_attr("data-edge-from") or tag.has_attr("data-edge-to")]

    correct_edges = [
        tag
        for tag in edges
        if tag.get("data-edge-from") == relation["from"]
        and tag.get("data-edge-to") == relation["to"]
        and (not tag.has_attr("data-relation") or _relation_marker_matches(tag, relation))
    ]
    if correct_edges and sources and targets:
        return True, "directed_edge", _describe_node(correct_edges[0])

    reversed_edges = [
        tag
        for tag in edges
        if tag.get("data-edge-from") == relation["to"]
        and tag.get("data-edge-to") == relation["from"]
        and (not tag.has_attr("data-relation") or _relation_marker_matches(tag, relation))
    ]
    if reversed_edges:
        return False, "directed_edge_reversed", _describe_node(reversed_edges[0])

    relation_key = _relation_key(relation["type"])
    if relation_key in CONTAINMENT_RELATIONS:
        for source in sources:
            for target in targets:
                if source is not target and _is_descendant_or_self(target, source):
                    return True, "dom_containment", _describe_node(source)
        return False, "required_dom_containment_not_found", None

    if relation_key in ORDER_RELATIONS:
        for source in sources:
            for target in targets:
                if dom_order.get(id(source), math.inf) < dom_order.get(id(target), math.inf):
                    return True, "dom_order", f"{_describe_node(source)} -> {_describe_node(target)}"
        return False, "required_dom_order_not_found", None

    containers = [tag for tag in visible_tags if _relation_marker_matches(tag, relation)]
    for container in containers:
        has_source = any(_is_descendant_or_self(source, container) for source in sources)
        has_target = any(_is_descendant_or_self(target, container) for target in targets)
        if has_source and has_target:
            return True, "relation_container", _describe_node(container)
    if not sources or not targets:
        return False, "visible_relation_endpoint_not_found", None
    return False, "explicit_relation_binding_not_found", None


def _evaluate_relations(
    slide: Tag,
    relations: list[dict[str, Any]],
    css_hidden: set[int],
    threshold: float,
) -> dict[str, Any]:
    if not relations:
        return {
            "pass": True,
            "applicable": False,
            "score": None,
            "threshold": threshold,
            "matched_weight": 0.0,
            "total_weight": 0.0,
            "protected_pass": True,
            "missing_protected": [],
            "relations": [],
        }

    ordered_tags = [slide, *slide.find_all(True)]
    dom_order = {id(tag): index for index, tag in enumerate(ordered_tags)}
    results: list[dict[str, Any]] = []
    for relation in relations:
        matched, method, evidence = _evaluate_relation(
            slide, relation, css_hidden, dom_order
        )
        results.append(
            {
                "id": relation["id"],
                "type": relation["type"],
                "from": relation["from"],
                "to": relation["to"],
                "matched": matched,
                "protected": relation["protected"],
                "weight": float(relation["weight"]),
                "method": method,
                "evidence": evidence,
            }
        )

    total_weight = sum(float(relation["weight"]) for relation in relations)
    matched_weight = sum(
        float(relation["weight"])
        for relation, result in zip(relations, results)
        if result["matched"]
    )
    score = matched_weight / total_weight
    missing_protected = [
        result["id"]
        for result in results
        if result["protected"] and not result["matched"]
    ]
    passed = score + 1e-12 >= threshold and not missing_protected
    return {
        "pass": passed,
        "applicable": True,
        "score": round(score, 6),
        "threshold": threshold,
        "matched_weight": matched_weight,
        "total_weight": total_weight,
        "protected_pass": not missing_protected,
        "missing_protected": missing_protected,
        "relations": results,
    }


def _average(values: Iterable[float]) -> float | None:
    values = list(values)
    if not values:
        return None
    return round(sum(values) / len(values), 6)


def validate_source_fidelity(
    html_text: str,
    coverage_data: Any,
    *,
    html_path: str | None = None,
    coverage_path: str | None = None,
) -> dict[str, Any]:
    coverage, text_threshold, relation_threshold = _validate_coverage(coverage_data)
    soup = BeautifulSoup(html_text, "html.parser")
    css_hidden = _css_hidden_tags(soup)
    slides = _top_level_slides(soup)
    coverage_slides = sorted(coverage["slides"], key=lambda item: item["slide_number"])
    if len(slides) != len(coverage_slides):
        raise CoverageError(
            f"HTML slide count ({len(slides)}) does not match coverage slide count "
            f"({len(coverage_slides)})"
        )

    slide_reports: list[dict[str, Any]] = []
    for slide, slide_coverage in zip(slides, coverage_slides):
        text_report = _evaluate_units(
            slide, slide_coverage["units"], css_hidden, text_threshold
        )
        relation_report = _evaluate_relations(
            slide, slide_coverage["relations"], css_hidden, relation_threshold
        )
        slide_reports.append(
            {
                "slide_number": slide_coverage["slide_number"],
                "pass": text_report["pass"] and relation_report["pass"],
                "text": text_report,
                "relations": relation_report,
            }
        )

    text_matched = sum(report["text"]["matched_weight"] for report in slide_reports)
    text_total = sum(report["text"]["total_weight"] for report in slide_reports)
    relation_reports = [
        report["relations"] for report in slide_reports if report["relations"]["applicable"]
    ]
    relation_matched = sum(report["matched_weight"] for report in relation_reports)
    relation_total = sum(report["total_weight"] for report in relation_reports)
    failed_slides = [report["slide_number"] for report in slide_reports if not report["pass"]]

    return {
        "pass": not failed_slides,
        "matching_mode": "normalized_exact_visible_text_and_explicit_dom_relations",
        "semantic_matching": False,
        "html": html_path,
        "coverage": coverage_path,
        "thresholds": {
            "text_retention": text_threshold,
            "relation_retention": relation_threshold,
        },
        "slides": slide_reports,
        "summary": {
            "slide_count": len(slide_reports),
            "passed_slides": len(slide_reports) - len(failed_slides),
            "failed_slides": failed_slides,
            "macro_average": {
                "text_retention": _average(
                    report["text"]["score"] for report in slide_reports
                ),
                "relation_retention": _average(
                    report["score"] for report in relation_reports
                ),
            },
            "weighted_average": {
                "text_retention": round(text_matched / text_total, 6),
                "relation_retention": (
                    round(relation_matched / relation_total, 6)
                    if relation_total
                    else None
                ),
            },
        },
        "errors": [],
    }


def _error_report(message: str, html_path: Path, coverage_path: Path) -> dict[str, Any]:
    return {
        "pass": False,
        "matching_mode": "normalized_exact_visible_text_and_explicit_dom_relations",
        "semantic_matching": False,
        "html": str(html_path),
        "coverage": str(coverage_path),
        "slides": [],
        "summary": None,
        "errors": [message],
    }


def _write_report(report: dict[str, Any], report_path: Path | None) -> None:
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if report_path is not None:
        report_path.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate exact visible source retention and DOM relations"
    )
    parser.add_argument("html", type=Path, help="generated HTML deck")
    parser.add_argument("coverage", type=Path, help="source coverage JSON")
    parser.add_argument("--report", type=Path, help="also write the JSON report to this path")
    args = parser.parse_args(argv)

    try:
        html_text = args.html.read_text(encoding="utf-8")
        coverage_data = json.loads(args.coverage.read_text(encoding="utf-8"))
        report = validate_source_fidelity(
            html_text,
            coverage_data,
            html_path=str(args.html),
            coverage_path=str(args.coverage),
        )
        exit_code = 0 if report["pass"] else 1
    except (OSError, json.JSONDecodeError, CoverageError) as exc:
        report = _error_report(str(exc), args.html, args.coverage)
        exit_code = 2

    try:
        _write_report(report, args.report)
    except OSError as exc:
        fallback = _error_report(f"cannot write report: {exc}", args.html, args.coverage)
        print(json.dumps(fallback, ensure_ascii=False, indent=2))
        return 2
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
