from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Literal

from bs4 import BeautifulSoup


def _discover_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "references" / "preset-contracts").is_dir() and (candidate / "schemas").is_dir():
            return candidate
    return here.parent


ROOT = _discover_root()
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from preset_capabilities import (  # noqa: E402
    CANONICAL_PRESET_NAMES,
    PRESET_REFERENCE_MAP,
    canonical_preset_name,
)
from style_signature_eval import (  # noqa: E402
    SelectorGroupRequirement,
    SignatureRequirement,
    collect_signature_presence,
)


CONTRACT_DIR = ROOT / "references" / "preset-contracts"
MANIFEST_DIR = ROOT / "references" / "preset-manifests"
REQUIRED_EXPORT_SLOTS = ("slide", "title", "body", "speaker_notes")
MANIFEST_PROJECTION_FIELDS = (
    "preset",
    "support_state",
    "renderer_strategy",
    "source_reference",
    "fonts",
    "tokens",
    "layout_families",
    "signature_components",
    "required_visible_components",
    "decorative_selectors",
    "non_critical_selectors",
    "forbidden_substitutions",
    "style_fidelity",
    "runtime_fidelity",
)


def slug_for_preset(preset: str) -> str:
    canonical = canonical_preset_name(preset)
    text = canonical.lower().replace("&", " ")
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _contract_path(preset: str) -> Path:
    return CONTRACT_DIR / f"{slug_for_preset(preset)}.json"


def _manifest_path(preset: str) -> Path:
    return MANIFEST_DIR / f"{slug_for_preset(preset)}.json"


def load_preset_contract(preset: str) -> dict[str, Any]:
    path = _contract_path(preset)
    if not path.exists():
        raise FileNotFoundError(f"Missing preset contract for {preset}: {path}")
    return _read_json(path)


def load_preset_manifest(preset: str) -> dict[str, Any]:
    path = _manifest_path(preset)
    if not path.exists():
        raise FileNotFoundError(f"Missing preset manifest for {preset}: {path}")
    return _read_json(path)


def builtin_preset_names() -> list[str]:
    return [
        CANONICAL_PRESET_NAMES[normalized]
        for normalized in sorted(PRESET_REFERENCE_MAP)
    ]


def manifest_projection(contract: dict[str, Any]) -> dict[str, Any]:
    projection: dict[str, Any] = {"version": int(contract["contract_version"])}
    for field in MANIFEST_PROJECTION_FIELDS:
        if field in contract:
            projection[field] = contract[field]
    return projection


def requirement_for_preset(preset: str) -> SignatureRequirement:
    contract = load_preset_contract(preset)
    style = contract.get("style_fidelity")
    if not isinstance(style, dict):
        raise ValueError(f"Preset contract has no style_fidelity section: {preset}")
    groups = []
    for item in style.get("required_selector_groups", []):
        groups.append(
            SelectorGroupRequirement(
                name=str(item["name"]),
                selectors=tuple(str(selector) for selector in item["selectors"]),
                match=str(item.get("match", "any")),
                scope=str(item.get("scope", "document")),
                page_buckets=tuple(str(bucket) for bucket in item.get("page_buckets", [])),
                weight=float(item.get("weight", 1.0)),
                minimum_group_score=float(item.get("minimum_group_score", 1.0)),
                minimum_bucket_count=(
                    int(item["minimum_bucket_count"])
                    if item.get("minimum_bucket_count") is not None
                    else None
                ),
                content_required=bool(item.get("content_required", True)),
            )
        )
    return SignatureRequirement(groups=tuple(groups))


def _style_hidden(style: str) -> bool:
    compact = re.sub(r"\s+", "", style.lower())
    if "display:none" in compact:
        return True
    if "visibility:hidden" in compact or "visibility:collapse" in compact:
        return True
    opacity_match = re.search(r"opacity:([0-9.]+)", compact)
    return bool(opacity_match and float(opacity_match.group(1)) <= 0.05)


def _is_visible_node(node: Any) -> bool:
    current = node
    while current is not None and getattr(current, "name", None):
        if current.has_attr("hidden"):
            return False
        if str(current.get("aria-hidden", "")).lower() == "true":
            return False
        if _style_hidden(str(current.get("style", ""))):
            return False
        current = current.parent
    return True


def _has_meaningful_content(node: Any) -> bool:
    if (node.get_text(" ", strip=True) or "").strip():
        return True
    return bool(node.select_one("img,svg,canvas,video,picture"))


def _select_all(soup: BeautifulSoup, selectors: list[str]) -> list[Any]:
    matches: list[Any] = []
    seen: set[int] = set()
    for selector in selectors:
        try:
            selected = soup.select(selector)
        except Exception:
            selected = []
        for node in selected:
            marker = id(node)
            if marker not in seen:
                matches.append(node)
                seen.add(marker)
    return matches


def _visible_content_matches(soup: BeautifulSoup, selectors: list[str]) -> list[Any]:
    return [
        node
        for node in _select_all(soup, selectors)
        if _is_visible_node(node) and _has_meaningful_content(node)
    ]


def _component_violation(
    *,
    name: str,
    selectors: list[str],
    min_count: int,
    actual_count: int,
) -> dict[str, Any]:
    return {
        "code": "contract-required-visible-component-missing",
        "type": "required_visible_component",
        "name": name,
        "selectors": ", ".join(selectors),
        "expected_min_count": min_count,
        "actual_count": actual_count,
        "severity": "hard",
    }


def _validate_structural_html(
    html_text: str,
    contract: dict[str, Any],
    *,
    require_product_metadata: bool,
) -> dict[str, Any]:
    soup = BeautifulSoup(html_text, "html.parser")
    violations: list[dict[str, Any]] = []

    for item in contract.get("required_visible_components", []):
        selectors = [str(selector) for selector in item.get("selectors", []) if str(selector).strip()]
        if not selectors:
            violations.append(
                _component_violation(
                    name=str(item.get("name", "unnamed")),
                    selectors=[],
                    min_count=1,
                    actual_count=0,
                )
            )
            continue
        min_count = int(item.get("min_count", 1))
        matches = _visible_content_matches(soup, selectors)
        if len(matches) < min_count:
            violations.append(
                _component_violation(
                    name=str(item.get("name", selectors[0])),
                    selectors=selectors,
                    min_count=min_count,
                    actual_count=len(matches),
                )
            )

    if require_product_metadata:
        export_mapping = contract.get("export_dom_mapping", {})
        for slot in REQUIRED_EXPORT_SLOTS:
            selector_text = export_mapping.get(slot)
            selectors = [selector_text] if isinstance(selector_text, str) else list(selector_text or [])
            if not selectors or not _select_all(soup, selectors):
                violations.append(
                    {
                        "code": "contract-export-slot-missing",
                        "type": "export_dom_mapping",
                        "slot": slot,
                        "selectors": ", ".join(selectors),
                        "severity": "hard",
                    }
                )

    hard_failures: list[str] = []
    for violation in violations:
        code = str(violation["code"])
        if code not in hard_failures:
            hard_failures.append(code)

    return {
        "pass": not violations,
        "hard_failures": hard_failures,
        "violations": violations,
        "diagnostics": {
            "required_visible_component_count": len(contract.get("required_visible_components", [])),
            "violation_count": len(violations),
        },
    }


def _style_violation(code: str, **details: Any) -> dict[str, Any]:
    return {"code": code, "type": "style_fidelity", "severity": "hard", **details}


def _validate_style_html(html_text: str, contract: dict[str, Any]) -> dict[str, Any]:
    style = contract.get("style_fidelity") or {}
    requirement = requirement_for_preset(str(contract["preset"]))
    presence = collect_signature_presence(html_text, requirement)
    violations: list[dict[str, Any]] = []
    groups_by_name = {group.name: group for group in requirement.groups}

    for result in presence.groups:
        required = groups_by_name[result.name]
        if required.minimum_bucket_count is not None and (
            result.applicable_page_count is None
            or result.applicable_page_count < required.minimum_bucket_count
        ):
            violations.append(
                _style_violation(
                    "style-selector-group-missing",
                    group=result.name,
                    expected_minimum_bucket_count=required.minimum_bucket_count,
                    actual_bucket_count=result.applicable_page_count or 0,
                )
            )
            continue
        if result.score is None or result.score < required.minimum_group_score:
            code = (
                "style-signature-slide-distribution-low"
                if required.scope == "slide"
                else "style-selector-group-missing"
            )
            violations.append(
                _style_violation(
                    code,
                    group=result.name,
                    expected_minimum_group_score=required.minimum_group_score,
                    actual_group_score=result.score,
                )
            )

    minimum_coverage = float(style.get("minimum_coverage", 1.0))
    if presence.coverage is None or presence.coverage < minimum_coverage:
        violations.append(
            _style_violation(
                "style-signature-coverage-low",
                expected_minimum_coverage=minimum_coverage,
                actual_coverage=presence.coverage,
            )
        )
    minimum_integrity = float(style.get("minimum_integrity", 1.0))
    if presence.integrity < minimum_integrity:
        violations.append(
            _style_violation(
                "style-signature-integrity-low",
                expected_minimum_integrity=minimum_integrity,
                actual_integrity=presence.integrity,
                invalid_selectors=sorted(
                    {selector for group in presence.groups for selector in group.invalid_selectors}
                ),
            )
        )

    hard_failures = list(dict.fromkeys(str(item["code"]) for item in violations))
    return {
        "pass": not violations,
        "hard_failures": hard_failures,
        "violations": violations,
        "metrics": {
            "coverage": presence.coverage,
            "integrity": presence.integrity,
            "minimum_coverage": minimum_coverage,
            "minimum_integrity": minimum_integrity,
            "groups": [
                {
                    "name": result.name,
                    "score": result.score,
                    "integrity": result.integrity,
                    "applicable_page_count": result.applicable_page_count,
                    "matched_page_count": result.matched_page_count,
                    "selector_hits": list(result.selector_hits),
                    "invalid_selectors": list(result.invalid_selectors),
                }
                for result in presence.groups
            ],
        },
    }


def validate_preset_fidelity(
    html_text: str,
    preset: str,
    mode: Literal["product", "reference"] = "product",
) -> dict[str, Any]:
    if mode not in {"product", "reference"}:
        raise ValueError(f"Unsupported preset fidelity mode: {mode}")
    contract = load_preset_contract(preset)
    structural = _validate_structural_html(
        html_text,
        contract,
        require_product_metadata=mode == "product",
    )
    if mode == "reference":
        structural = {"pass": True, "hard_failures": [], "violations": [], "diagnostics": {"skipped": True}}
    style = _validate_style_html(html_text, contract)
    violations = [*structural["violations"], *style["violations"]]
    hard_failures = list(dict.fromkeys([*structural["hard_failures"], *style["hard_failures"]]))
    return {
        "version": 2,
        "phase": "preset-fidelity",
        "preset": contract["preset"],
        "contract_path": str(_contract_path(preset)),
        "mode": mode,
        "pass": structural["pass"] and style["pass"],
        "structural": structural,
        "style": style,
        "hard_failures": hard_failures,
        "violations": violations,
        "diagnostics": {
            "structural_pass": structural["pass"],
            "style_pass": style["pass"],
            "violation_count": len(violations),
        },
    }


def check_preset_contract_html(html_text: str, preset: str) -> dict[str, Any]:
    """Deprecated compatibility alias for product fidelity validation."""
    return validate_preset_fidelity(html_text, preset, mode="product")


def check_preset_contract_path(path: str | Path, preset: str | None = None) -> dict[str, Any]:
    html_path = Path(path)
    if preset is None:
        raise ValueError("preset is required for contract checking")
    report = check_preset_contract_html(html_path.read_text(encoding="utf-8"), preset)
    report["html_path"] = str(html_path)
    return report
