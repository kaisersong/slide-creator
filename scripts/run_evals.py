#!/usr/bin/env python3

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import math
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Any

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = ROOT / "tests"
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from low_context import (  # noqa: E402
    BriefValidationError,
    build_render_packet,
    compile_style_contract,
    load_brief,
    render_from_brief,
    validate_brief_path,
)
from preset_support import preset_support_tier  # noqa: E402
from ai_advised_eval import analyze_ai_advised_path  # noqa: E402
from browser_geometry_qa import (  # noqa: E402
    DEFAULT_VIEWPORTS,
    LAPTOP_WINDOW_VIEWPORT,
    MEASUREMENT_MODES,
    analyze_browser_geometry_path,
)
from compare_demo_parity import run_demo_parity as run_demo_parity_gate  # noqa: E402
from export_smoke import run_export_smoke  # noqa: E402
from pptx_export_smoke import run_pptx_export_smoke  # noqa: E402
from preset_contracts import (  # noqa: E402
    check_preset_contract_path,
    load_preset_contract,
    requirement_for_preset,
)
from preset_runtime_qa import analyze_preset_runtime_path  # noqa: E402
from promotion_gate import run_promotion_gate  # noqa: E402
from quality_eval import analyze_html_quality  # noqa: E402
from style_signature_eval import collect_signature_presence  # noqa: E402
from title_browser_qa import analyze_title_composition_path  # noqa: E402


def _load_validate_module():
    validate_path = ROOT / "scripts" / "validate_html.py"
    spec = importlib.util.spec_from_file_location("slide_validate", validate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


VALIDATE = _load_validate_module()

HTML_CHECK_ALIASES = {
    "preset-metadata": "preset_metadata",
    "present-mode": "present_mode",
    "edit-mode": "edit_mode",
    "watermark-injected": "watermark_injection",
}

NON_REGRESSION_KEYS = {
    "layout-variety": "layout_variety_delta",
    "component-diversity": "component_diversity_delta",
    "style-signature-coverage": "style_signature_coverage_delta",
    "minimal-slide-ratio": "minimal_slide_ratio_delta",
}

KNOWN_EXPECTATION_KEYS = {
    "artifact_status",
    "should_fail_closed",
    "expected_mode",
    "expected_preset",
    "expected_canonical_preset",
    "expected_support_tier",
    "expected_generation_status",
    "expected_renderer_strategy",
    "expected_render_path",
    "expected_reference_path",
    "required_brief_fields",
    "expected_quality_tier",
    "allowed_quality_tiers",
    "required_html_checks",
    "forbidden_html_checks",
    "required_quality_gates",
    "required_title_gates",
    "quality_thresholds",
    "non_regression_metrics",
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _git_head() -> str | None:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def _git_dirty() -> bool | None:
    try:
        completed = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return None
    if completed.returncode != 0:
        return None
    return bool(completed.stdout.strip())


def _resolve_path(base: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    return (base / path).resolve()


def _slugify_check_name(function_name: str) -> str:
    return function_name.replace("check_", "")


def _run_validate_checks(
    html_text: str,
    *,
    strict: bool,
    preset_fidelity_mode: str = "product",
) -> dict[str, Any]:
    soup = BeautifulSoup(html_text, "html.parser")
    warnings: list[str] = []
    checks = list(VALIDATE.REQUIRED_CHECKS)
    if strict:
        checks.extend(VALIDATE.STRICT_CHECKS)

    results: dict[str, dict[str, Any]] = {}
    for check_fn in checks:
        try:
            if check_fn is VALIDATE.check_preset_fidelity:
                passed, message = check_fn(soup, html_text, warnings, mode=preset_fidelity_mode)
            else:
                passed, message = check_fn(soup, html_text, warnings)
        except Exception as exc:  # pragma: no cover - defensive path
            passed, message = False, f"Check error: {exc}"
        results[_slugify_check_name(check_fn.__name__)] = {
            "passed": bool(passed),
            "message": message,
        }

    failed = sorted(name for name, result in results.items() if not result["passed"])
    return {
        "strict": strict,
        "preset_fidelity_mode": preset_fidelity_mode,
        "passed": not failed,
        "failed_checks": failed,
        "warnings": warnings,
        "checks": results,
    }


def _run_single_validate_check(function_name: str, html_text: str) -> tuple[bool, str]:
    check_fn = getattr(VALIDATE, function_name, None)
    if check_fn is None:
        return False, f"validate function '{function_name}' not found"
    soup = BeautifulSoup(html_text, "html.parser")
    warnings: list[str] = []
    try:
        return check_fn(soup, html_text, warnings)
    except Exception as exc:  # pragma: no cover - defensive path
        return False, f"Check error: {exc}"


def _collect_css_text(html_text: str) -> str:
    soup = BeautifulSoup(html_text, "html.parser")
    css_sources = [tag.string or "" for tag in soup.find_all("style")]
    css_sources.extend(tag.get("style", "") for tag in soup.find_all(style=True))
    return "\n".join(css_sources)


def _compute_style_signature_metrics(html_text: str, preset: str) -> dict[str, Any]:
    requirement = requirement_for_preset(preset)
    presence = collect_signature_presence(html_text, requirement)

    signature_required = set(requirement.classes) | set(requirement.ids) | set(requirement.backgrounds)
    background_required = set(requirement.backgrounds)
    background_hits = len(background_required & set(presence.background_hits))
    background_total = len(background_required)
    background_coverage = round(background_hits / background_total, 4) if background_total else None

    return {
        "signature_required": sorted(signature_required),
        "signature_coverage": presence.coverage,
        "background_required": sorted(background_required),
        "background_coverage": background_coverage,
        "visible_signature_hits": sorted(set(presence.visible_class_hits) | set(presence.visible_id_hits)),
        "background_hits": list(presence.background_hits),
        "ignored_marker_class_count": len(presence.ignored_marker_hits),
        "marker_only_signature_hits": list(presence.ignored_marker_hits),
        "invisible_signature_hits": list(presence.invisible_hits),
        "empty_shell_signature_hits": list(presence.empty_shell_hits),
        "style_signature_integrity": presence.integrity,
    }


def _resolve_html_check(
    check_name: str,
    *,
    brief: dict[str, Any] | None,
    packet: dict[str, Any] | None,
    validate_report: dict[str, Any],
    quality_report: dict[str, Any],
    html_text: str,
    preset: str,
) -> tuple[bool, str]:
    checks = validate_report["checks"]
    if check_name in HTML_CHECK_ALIASES:
        alias = HTML_CHECK_ALIASES[check_name]
        result = checks.get(alias)
        if result:
            return bool(result["passed"]), result["message"]
        validate_name = f"check_{alias}"
        return _run_single_validate_check(validate_name, html_text)

    if check_name == "shared-runtime":
        runtime_ok = True
        if packet and packet.get("runtime_path") is not None:
            runtime_ok = packet.get("runtime_path") == "shared-js-engine"
        contract = checks.get("shared_js_engine_contract", {})
        passed = runtime_ok and bool(contract.get("passed"))
        message = contract.get("message", "shared_js_engine_contract check missing")
        return passed, message

    if check_name == "shared-runtime-required":
        runtime_ok = True
        if packet and packet.get("runtime_path") is not None:
            runtime_ok = packet.get("runtime_path") == "shared-js-engine"
        contract = checks.get("shared_js_engine_contract", {})
        passed = runtime_ok and bool(contract.get("passed"))
        message = contract.get("message", "shared_js_engine_contract check missing")
        return passed, message

    if check_name == "blue-sky-architecture":
        has_stage = 'id="stage"' in html_text
        has_track = 'id="track"' in html_text
        runtime_marker = packet.get("runtime_path") if packet else None
        runtime_ok = runtime_marker == "blue-sky-starter" if runtime_marker is not None else True
        passed = runtime_ok and has_stage and has_track
        return passed, "Blue Sky starter markers present" if passed else "Blue Sky starter markers missing"

    if check_name == "style-signature":
        coverage = quality_report["diagnostics"].get("style_signature_coverage")
        passed = coverage is not None and coverage > 0.0
        return passed, f"style signature coverage={coverage}"

    if check_name == "background-signature":
        metrics = _compute_style_signature_metrics(html_text, preset)
        coverage = metrics["background_coverage"]
        required = metrics["background_required"]
        if coverage is None:
            return True, "background signature not required for this preset"
        passed = bool(required) and coverage > 0.0
        return passed, f"background signature coverage={coverage}"

    return False, f"Unknown html check '{check_name}'"


def _dot_get(data: dict[str, Any] | None, path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _is_present_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) > 0
    return True


def _evaluate_thresholds(
    thresholds: dict[str, Any],
    *,
    diagnostics: dict[str, Any],
    quality_report: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    failures: list[str] = []

    comparison = quality_report.get("comparison", {}).get("non_regression", {})
    for key, expected in thresholds.items():
        status = True
        actual = None
        message = ""

        if key.endswith("_min"):
            metric = key[:-4]
            actual = diagnostics.get(metric)
            status = actual is not None and actual >= expected
            message = f"{metric} >= {expected}"
        elif key.endswith("_max_delta"):
            metric = key[: -len("_max_delta")]
            comparison_key = f"{metric}_delta"
            actual = comparison.get(comparison_key)
            status = actual is not None and actual <= expected
            message = f"{comparison_key} <= {expected}"
        elif key.endswith("_max"):
            metric = key[:-4]
            actual = diagnostics.get(metric)
            status = actual is not None and actual <= expected
            message = f"{metric} <= {expected}"
        elif key == "max_minimal_slide_run":
            actual = diagnostics.get(key)
            status = actual is not None and actual <= expected
            message = f"{key} <= {expected}"
        else:
            actual = diagnostics.get(key)
            status = actual == expected
            message = f"{key} == {expected}"

        entry = {
            "name": key,
            "passed": bool(status),
            "expected": expected,
            "actual": actual,
            "message": message,
        }
        results.append(entry)
        if not status:
            failures.append(key)

    return results, failures


def _evaluate_case(
    expectations: dict[str, Any],
    *,
    brief: dict[str, Any] | None,
    packet: dict[str, Any] | None,
    quality_report: dict[str, Any] | None,
    validate_report: dict[str, Any] | None,
    preset: str | None,
    html_text: str | None,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    failures: list[str] = []

    unknown_expectations = sorted(set(expectations) - KNOWN_EXPECTATION_KEYS)
    for key in unknown_expectations:
        checks.append({
            "name": f"unknown_expectation:{key}",
            "passed": False,
            "message": f"unknown expectation key '{key}'",
        })
        failures.append(f"unknown_expectation:{key}")

    if expectations.get("expected_mode"):
        actual_mode = brief.get("mode") if brief else None
        passed = actual_mode == expectations["expected_mode"]
        checks.append({
            "name": "expected_mode",
            "passed": passed,
            "expected": expectations["expected_mode"],
            "actual": actual_mode,
        })
        if not passed:
            failures.append("expected_mode")

    if expectations.get("expected_preset"):
        actual_preset = packet.get("preset") if packet else preset
        passed = actual_preset == expectations["expected_preset"]
        checks.append({
            "name": "expected_preset",
            "passed": passed,
            "expected": expectations["expected_preset"],
            "actual": actual_preset,
        })
        if not passed:
            failures.append("expected_preset")

    packet_expectations = [
        ("expected_canonical_preset", "canonical_preset"),
        ("expected_generation_status", "preset_generation_status"),
        ("expected_renderer_strategy", "renderer_strategy"),
        ("expected_render_path", "render_path"),
        ("expected_reference_path", "reference_path"),
    ]
    for expectation_key, packet_key in packet_expectations:
        if expectation_key not in expectations:
            continue
        actual = packet.get(packet_key) if packet else None
        passed = actual == expectations[expectation_key]
        checks.append({
            "name": expectation_key,
            "passed": passed,
            "expected": expectations[expectation_key],
            "actual": actual,
        })
        if not passed:
            failures.append(expectation_key)

    if expectations.get("expected_support_tier"):
        actual_tier = packet.get("preset_support_tier") if packet else preset_support_tier(preset or "")
        passed = actual_tier == expectations["expected_support_tier"]
        checks.append({
            "name": "expected_support_tier",
            "passed": passed,
            "expected": expectations["expected_support_tier"],
            "actual": actual_tier,
        })
        if not passed:
            failures.append("expected_support_tier")

    for field in expectations.get("required_brief_fields", []):
        actual = _dot_get(brief, field)
        passed = _is_present_value(actual)
        checks.append({
            "name": f"required_brief_field:{field}",
            "passed": passed,
            "actual": actual,
        })
        if not passed:
            failures.append(f"required_brief_field:{field}")

    if expectations.get("expected_quality_tier"):
        actual_quality = packet.get("quality_tier") if packet else None
        passed = actual_quality == expectations["expected_quality_tier"]
        checks.append({
            "name": "expected_quality_tier",
            "passed": passed,
            "expected": expectations["expected_quality_tier"],
            "actual": actual_quality,
        })
        if not passed:
            failures.append("expected_quality_tier")

    if expectations.get("allowed_quality_tiers"):
        actual_quality = packet.get("quality_tier") if packet else None
        passed = actual_quality in set(expectations["allowed_quality_tiers"])
        checks.append({
            "name": "allowed_quality_tiers",
            "passed": passed,
            "expected": expectations["allowed_quality_tiers"],
            "actual": actual_quality,
        })
        if not passed:
            failures.append("allowed_quality_tiers")

    if validate_report and quality_report and html_text and preset:
        for check_name in expectations.get("required_html_checks", []):
            passed, message = _resolve_html_check(
                check_name,
                brief=brief,
                packet=packet,
                validate_report=validate_report,
                quality_report=quality_report,
                html_text=html_text,
                preset=preset,
            )
            checks.append({"name": f"required_html_check:{check_name}", "passed": passed, "message": message})
            if not passed:
                failures.append(f"required_html_check:{check_name}")

        for check_name in expectations.get("forbidden_html_checks", []):
            passed, message = _resolve_html_check(
                check_name,
                brief=brief,
                packet=packet,
                validate_report=validate_report,
                quality_report=quality_report,
                html_text=html_text,
                preset=preset,
            )
            status = not passed
            checks.append({"name": f"forbidden_html_check:{check_name}", "passed": status, "message": message})
            if not status:
                failures.append(f"forbidden_html_check:{check_name}")

        for gate_name in expectations.get("required_quality_gates", []):
            actual = quality_report["quality_gates"].get(gate_name)
            passed = actual is True
            checks.append({"name": f"required_quality_gate:{gate_name}", "passed": passed, "actual": actual})
            if not passed:
                failures.append(f"required_quality_gate:{gate_name}")

        for gate_name in expectations.get("required_title_gates", []):
            actual = quality_report["quality_gates"].get(gate_name)
            passed = actual is True
            checks.append({"name": f"required_title_gate:{gate_name}", "passed": passed, "actual": actual})
            if not passed:
                failures.append(f"required_title_gate:{gate_name}")

        threshold_results, threshold_failures = _evaluate_thresholds(
            expectations.get("quality_thresholds", {}),
            diagnostics=quality_report["diagnostics"],
            quality_report=quality_report,
        )
        checks.extend(threshold_results)
        failures.extend(f"quality_threshold:{name}" for name in threshold_failures)

        comparison = quality_report.get("comparison", {}).get("non_regression", {})
        for metric in expectations.get("non_regression_metrics", []):
            comparison_key = NON_REGRESSION_KEYS.get(metric)
            actual = comparison.get(comparison_key) if comparison_key else None
            if comparison_key and comparison:
                if metric == "minimal-slide-ratio":
                    passed = actual is not None and actual <= 0.1
                else:
                    passed = actual is not None and actual >= -0.05
                checks.append({
                    "name": f"non_regression:{metric}",
                    "passed": passed,
                    "actual": actual,
                })
                if not passed:
                    failures.append(f"non_regression:{metric}")
            else:
                checks.append({
                    "name": f"non_regression:{metric}",
                    "passed": True,
                    "actual": None,
                    "message": "baseline not provided; skipped",
                })

    return {
        "checks": checks,
        "failures": failures,
        "passed": not failures,
    }


def _compute_scores(
    *,
    brief_valid: bool,
    expectations_report: dict[str, Any],
    quality_report: dict[str, Any] | None,
    validate_report: dict[str, Any] | None,
    weights: dict[str, float],
) -> tuple[dict[str, Any], float]:
    diagnostics = quality_report["diagnostics"] if quality_report else {}
    hard_failures = quality_report["hard_failures"] if quality_report else []

    route_checks = [brief_valid]
    compression_checks = [brief_valid]
    render_checks = []
    efficiency_checks = []

    for check in expectations_report["checks"]:
        name = check["name"]
        if name.startswith("expected_mode") or name.startswith("expected_preset") or name.startswith("expected_support_tier"):
            route_checks.append(bool(check["passed"]))
        elif name.startswith("required_brief_field") or name.startswith("expected_quality_tier") or name.startswith("allowed_quality_tiers"):
            compression_checks.append(bool(check["passed"]))
        elif name.startswith("required_html_check") or name.startswith("required_quality_gate") or name.startswith("required_title_gate") or name.startswith("quality_threshold") or name.startswith("non_regression"):
            render_checks.append(bool(check["passed"]))

    if quality_report:
        render_checks.append(validate_report["passed"] if validate_report else False)
        render_checks.append(not hard_failures)
        route_checks.append(diagnostics.get("route_drift") is False)
        compression_checks.append((diagnostics.get("narrative_role_coverage") or 0) >= 1.0 if diagnostics.get("narrative_role_coverage") is not None else True)
        efficiency_checks.append((diagnostics.get("latency_ms", {}).get("validate") or 0) >= 0)
        efficiency_checks.append(diagnostics.get("repair_rounds", 0) == 0)
        efficiency_checks.append(diagnostics.get("strict_pass_first_try") is not False)

    def score(flags: list[bool]) -> float:
        if not flags:
            return 1.0
        return round(sum(1 for flag in flags if flag) / len(flags), 4)

    score_map = {
        "route": score(route_checks),
        "compression": score(compression_checks),
        "render": score(render_checks),
        "efficiency": score(efficiency_checks),
    }
    overall = 0.0
    scored_layers: dict[str, Any] = {}
    for layer, layer_score in score_map.items():
        weight = float(weights.get(layer, 0.0))
        overall += layer_score * weight
        scored_layers[layer] = {
            "weight": weight,
            "score": layer_score,
        }

    return scored_layers, round(overall, 4)


def _render_case_from_brief(brief: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    packet_started = perf_counter()
    packet = build_render_packet(brief)
    packet_ms = round((perf_counter() - packet_started) * 1000, 2)

    render_started = perf_counter()
    html_text, rendered_packet, _style_contract = render_from_brief(brief)
    render_ms = round((perf_counter() - render_started) * 1000, 2)

    rendered_packet["latency_ms"] = {
        "packet": packet_ms,
        "render": render_ms,
        "assemble": 0.0,
    }
    return html_text, rendered_packet


def _evaluate_rendered_case(
    *,
    case: dict[str, Any],
    suite_dir: Path,
    output_dir: Path,
    baseline_dir: Path | None,
    run_browser_titles: bool,
    run_browser_geometry: bool,
    run_contract: bool,
    run_export_smoke: bool,
    run_mobile_geometry: bool,
    run_ai_advised: bool,
    run_pptx_export: bool,
    weights: dict[str, float],
) -> dict[str, Any]:
    case_id = case["case_id"]
    case_dir = output_dir / case_id
    case_dir.mkdir(parents=True, exist_ok=True)

    brief_path = _resolve_path(suite_dir, case.get("brief_path"))
    fixture_html_path = _resolve_path(suite_dir, case.get("html_path"))
    source_path = _resolve_path(suite_dir, case.get("source_path"))
    title_report_path = _resolve_path(suite_dir, case.get("title_browser_report_path"))
    expectations = case.get("expectations", {})
    validation_profile = case.get("validation_profile", "strict")
    strict_validate = validation_profile == "strict"
    preset_fidelity_mode = str(case.get("preset_fidelity_mode", "product"))
    quality_eval_use_brief = case.get("quality_eval_use_brief", True)

    brief = None
    brief_valid = False
    brief_errors: list[str] = []
    packet: dict[str, Any] | None = None
    html_text: str | None = None
    rendered_html_path = case_dir / "deck.html"
    preset = case.get("preset")

    if brief_path:
        brief_valid, brief_errors, _loaded = validate_brief_path(brief_path)
        if brief_valid:
            brief = load_brief(brief_path)
            if case.get("preset"):
                brief = copy.deepcopy(brief)
                brief["style"]["preset"] = str(case["preset"])
                brief["brief_id"] = f"{brief.get('brief_id', case_id)}-{_slugify_check_name(str(case['preset']).lower().replace(' ', '-'))}"
            preset = brief["style"]["preset"]

    artifact_status = expectations.get("artifact_status")
    should_fail_closed = bool(expectations.get("should_fail_closed"))
    if not brief_valid and artifact_status == "invalid" and should_fail_closed:
        expectations_report = {
            "checks": [
                {
                    "name": "invalid_brief_fail_closed",
                    "passed": True,
                    "actual": brief_errors,
                }
            ],
            "failures": [],
            "passed": True,
        }
        scores, overall = _compute_scores(
            brief_valid=False,
            expectations_report=expectations_report,
            quality_report=None,
            validate_report=None,
            weights=weights,
        )
        return {
            "case_id": case_id,
            "mode": "invalid-brief",
            "pass": True,
            "preset": preset,
            "support_tier": preset_support_tier(preset) if preset else None,
            "brief_path": str(brief_path) if brief_path else None,
            "hard_failures": [],
            "validations": {
                "brief": {
                    "passed": False,
                    "errors": brief_errors,
                }
            },
            "expectations": expectations_report,
            "scores": scores,
            "overall": overall,
            "notes": ["Invalid brief correctly failed closed before rendering."],
        }

    if not brief_valid and brief_path:
        return {
            "case_id": case_id,
            "mode": "invalid-brief",
            "pass": False,
            "preset": preset,
            "support_tier": preset_support_tier(preset) if preset else None,
            "brief_path": str(brief_path),
            "hard_failures": ["invalid-brief"],
            "validations": {
                "brief": {
                    "passed": False,
                    "errors": brief_errors,
                }
            },
            "expectations": {
                "checks": [],
                "failures": ["invalid-brief"],
                "passed": False,
            },
            "scores": {
                "route": {"weight": weights["route"], "score": 0.0},
                "compression": {"weight": weights["compression"], "score": 0.0},
                "render": {"weight": weights["render"], "score": 0.0},
                "efficiency": {"weight": weights["efficiency"], "score": 0.0},
            },
            "overall": 0.0,
            "notes": ["BRIEF validation failed before rendering."],
        }

    mode = "html-fixture" if fixture_html_path else "render"
    if fixture_html_path:
        html_text = _read_text(fixture_html_path)
        rendered_html_path.write_text(html_text, encoding="utf-8")
        packet_started = perf_counter()
        packet = build_render_packet(brief) if brief else None
        packet_ms = round((perf_counter() - packet_started) * 1000, 2)
        if packet:
            packet["latency_ms"] = {
                "packet": packet_ms,
                "render": 0.0,
                "assemble": 0.0,
            }
    else:
        if brief is None:
            raise BriefValidationError(f"{case_id} requires either brief_path or html_path")
        html_text, packet = _render_case_from_brief(brief)
        rendered_html_path.write_text(html_text, encoding="utf-8")

    if packet is None:
        packet = {
            "preset": preset,
            "preset_support_tier": preset_support_tier(preset or ""),
            "quality_tier": None,
            "latency_ms": {"packet": 0.0, "render": 0.0, "assemble": 0.0},
        }

    packet_path = case_dir / "packet.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")

    validate_started = perf_counter()
    validate_report = _run_validate_checks(
        html_text,
        strict=strict_validate,
        preset_fidelity_mode=preset_fidelity_mode,
    )
    validate_ms = round((perf_counter() - validate_started) * 1000, 2)

    baseline_html_text = None
    baseline_html_path = _resolve_path(suite_dir, case.get("baseline_html_path"))
    if baseline_dir:
        candidate = baseline_dir / case_id / "deck.html"
        if candidate.exists():
            baseline_html_path = candidate
    if baseline_html_path and baseline_html_path.exists():
        baseline_html_text = _read_text(baseline_html_path)

    title_browser_report = None
    if title_report_path and title_report_path.exists():
        title_browser_report = _read_json(title_report_path)
    elif run_browser_titles or case.get("run_browser_titles"):
        try:
            title_browser_report = analyze_title_composition_path(rendered_html_path, preset=packet["preset"])
        except Exception as exc:  # pragma: no cover - depends on local browser sandboxing
            title_browser_report = {
                "pass": False,
                "unavailable": True,
                "error": f"browser title QA unavailable: {exc}",
            }
        generated_title_report_path = case_dir / "title-browser-report.json"
        generated_title_report_path.write_text(
            json.dumps(title_browser_report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        title_report_path = generated_title_report_path

    browser_geometry_report = None
    browser_geometry_report_path = None
    if run_browser_geometry or case.get("run_browser_geometry"):
        try:
            # Desktop geometry covers three window shapes and both playback modes:
            # 1600x900 and 1280x720 are the historical defaults, 1440x733 is the real
            # laptop browser window where dense slides clip, and play mode pins slides
            # to a fixed 1440x900 box whose geometry window mode never observes.
            browser_geometry_report = analyze_browser_geometry_path(
                rendered_html_path,
                preset=packet["preset"],
                viewports=[*DEFAULT_VIEWPORTS, dict(LAPTOP_WINDOW_VIEWPORT)],
                modes=MEASUREMENT_MODES,
                stable_runs=1,
                artifact_dir=case_dir / "browser-geometry-evidence",
            )
        except Exception as exc:  # pragma: no cover - depends on local browser sandboxing
            browser_geometry_report = {
                "pass": False,
                "unavailable": True,
                "error": f"browser geometry QA unavailable: {exc}",
                "hard_failures": ["browser-geometry-unavailable"],
                "violations": [],
                "diagnostics": {},
            }
        generated_geometry_report_path = case_dir / "browser-geometry-report.json"
        generated_geometry_report_path.write_text(
            json.dumps(browser_geometry_report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        browser_geometry_report_path = generated_geometry_report_path

    preset_fidelity_report = None
    preset_fidelity_report_path = None
    runtime_fidelity_report = None
    runtime_fidelity_report_path = None
    if run_contract or case.get("run_contract"):
        try:
            preset_fidelity_report = check_preset_contract_path(
                rendered_html_path,
                preset=packet["preset"],
            )
        except Exception as exc:  # pragma: no cover - defensive local file path
            preset_fidelity_report = {
                "pass": False,
                "unavailable": True,
                "error": f"preset fidelity check unavailable: {exc}",
                "hard_failures": ["preset-fidelity-unavailable"],
                "violations": [],
                "diagnostics": {},
            }
        generated_fidelity_report_path = case_dir / "preset-fidelity-report.json"
        generated_fidelity_report_path.write_text(
            json.dumps(preset_fidelity_report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        preset_fidelity_report_path = generated_fidelity_report_path

        try:
            contract = load_preset_contract(packet["preset"])
            if contract.get("runtime_fidelity"):
                runtime_fidelity_report = analyze_preset_runtime_path(
                    rendered_html_path,
                    preset=packet["preset"],
                )
        except Exception as exc:  # pragma: no cover - browser/runtime availability
            runtime_fidelity_report = {
                "pass": False,
                "unavailable": True,
                "error": f"runtime fidelity check unavailable: {exc}",
                "hard_failures": ["runtime-qa-unavailable"],
                "violations": [],
            }
        if runtime_fidelity_report is not None:
            generated_runtime_report_path = case_dir / "runtime-fidelity-report.json"
            generated_runtime_report_path.write_text(
                json.dumps(runtime_fidelity_report, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            runtime_fidelity_report_path = generated_runtime_report_path

    export_smoke_report = None
    export_smoke_report_path = None
    if run_export_smoke or case.get("run_export_smoke"):
        try:
            export_smoke_report = globals()["run_export_smoke"](
                rendered_html_path,
                preset=packet["preset"],
                output_dir=case_dir / "export-smoke-evidence",
            )
        except Exception as exc:  # pragma: no cover - defensive local file path
            export_smoke_report = {
                "pass": False,
                "unavailable": True,
                "error": f"export smoke unavailable: {exc}",
                "hard_failures": ["export-smoke-unavailable"],
                "violations": [],
                "diagnostics": {},
            }
        generated_export_smoke_path = case_dir / "export-smoke-report.json"
        generated_export_smoke_path.write_text(
            json.dumps(export_smoke_report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        export_smoke_report_path = generated_export_smoke_path

    mobile_geometry_report = None
    mobile_geometry_report_path = None
    if run_mobile_geometry or case.get("run_mobile_geometry"):
        try:
            mobile_geometry_report = analyze_browser_geometry_path(
                rendered_html_path,
                preset=packet["preset"],
                viewports=[{"width": 390, "height": 844}],
                stable_runs=1,
                artifact_dir=case_dir / "mobile-geometry-evidence",
            )
            mobile_geometry_report["phase"] = "1.0-mobile-browser-geometry"
        except Exception as exc:  # pragma: no cover - depends on local browser sandboxing
            mobile_geometry_report = {
                "pass": False,
                "unavailable": True,
                "error": f"mobile browser geometry QA unavailable: {exc}",
                "hard_failures": ["mobile-browser-geometry-unavailable"],
                "violations": [],
                "diagnostics": {},
            }
        generated_mobile_geometry_path = case_dir / "mobile-geometry-report.json"
        generated_mobile_geometry_path.write_text(
            json.dumps(mobile_geometry_report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        mobile_geometry_report_path = generated_mobile_geometry_path

    ai_advised_report = None
    ai_advised_report_path = None
    if run_ai_advised or case.get("run_ai_advised"):
        try:
            ai_advised_report = analyze_ai_advised_path(
                rendered_html_path,
                preset=packet["preset"],
            )
        except Exception as exc:  # pragma: no cover - defensive local file path
            ai_advised_report = {
                "pass": False,
                "unavailable": True,
                "error": f"AI-advised eval unavailable: {exc}",
                "hard_failures": ["ai-advised-unavailable"],
                "violations": [],
                "diagnostics": {},
            }
        generated_ai_path = case_dir / "ai-advised-report.json"
        generated_ai_path.write_text(
            json.dumps(ai_advised_report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        ai_advised_report_path = generated_ai_path

    pptx_export_report = None
    pptx_export_report_path = None
    if run_pptx_export or case.get("run_pptx_export"):
        try:
            pptx_export_report = globals()["run_pptx_export_smoke"](
                rendered_html_path,
                preset=packet["preset"],
                output_dir=case_dir / "pptx-export-evidence",
            )
        except Exception as exc:  # pragma: no cover - depends on local browser/export environment
            pptx_export_report = {
                "pass": False,
                "unavailable": True,
                "error": f"PPTX export smoke unavailable: {exc}",
                "hard_failures": ["pptx-export-unavailable"],
                "violations": [],
                "diagnostics": {},
            }
        generated_pptx_path = case_dir / "pptx-export-report.json"
        generated_pptx_path.write_text(
            json.dumps(pptx_export_report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        pptx_export_report_path = generated_pptx_path

    quality_report = analyze_html_quality(
        html_text,
        brief=brief if quality_eval_use_brief else None,
        source_text=_read_text(source_path) if source_path and source_path.exists() else None,
        preset=packet["preset"],
        baseline_html=baseline_html_text,
        title_browser_report=title_browser_report,
    )
    diagnostics = quality_report["diagnostics"]
    diagnostics["quality_tier"] = packet.get("quality_tier")
    diagnostics["strict_pass_first_try"] = validate_report["passed"] if strict_validate else validate_report["passed"]
    diagnostics["repair_rounds"] = 0
    diagnostics["route_drift"] = packet.get("preset") != preset if preset else False
    diagnostics["latency_ms"] = {
        "packet": packet["latency_ms"]["packet"],
        "render": packet["latency_ms"]["render"],
        "assemble": packet["latency_ms"]["assemble"],
        "validate": validate_ms,
    }

    expectations_report = _evaluate_case(
        expectations,
        brief=brief,
        packet=packet,
        quality_report=quality_report,
        validate_report=validate_report,
        preset=packet["preset"],
        html_text=html_text,
    )
    scores, overall = _compute_scores(
        brief_valid=brief_valid or brief is None,
        expectations_report=expectations_report,
        quality_report=quality_report,
        validate_report=validate_report,
        weights=weights,
    )

    hard_failures = list(quality_report["hard_failures"])
    if strict_validate and not validate_report["passed"]:
        hard_failures.append("strict-validate-failed")
    if browser_geometry_report and not browser_geometry_report.get("pass", False):
        hard_failures.extend(str(code) for code in browser_geometry_report.get("hard_failures", []))
    if preset_fidelity_report and not preset_fidelity_report.get("pass", False):
        hard_failures.extend(str(code) for code in preset_fidelity_report.get("hard_failures", []))
    if runtime_fidelity_report and not runtime_fidelity_report.get("pass", False):
        hard_failures.extend(str(code) for code in runtime_fidelity_report.get("hard_failures", []))
    if export_smoke_report and not export_smoke_report.get("pass", False):
        hard_failures.extend(str(code) for code in export_smoke_report.get("hard_failures", []))
    if mobile_geometry_report and not mobile_geometry_report.get("pass", False):
        hard_failures.extend(str(code) for code in mobile_geometry_report.get("hard_failures", []))
    if ai_advised_report and not ai_advised_report.get("pass", False):
        hard_failures.extend(str(code) for code in ai_advised_report.get("hard_failures", []))
    if pptx_export_report and not pptx_export_report.get("pass", False):
        hard_failures.extend(str(code) for code in pptx_export_report.get("hard_failures", []))
    pass_status = (
        expectations_report["passed"]
        and (validate_report["passed"] if strict_validate else True)
        and (browser_geometry_report.get("pass", False) if browser_geometry_report else True)
        and (preset_fidelity_report.get("pass", False) if preset_fidelity_report else True)
        and (runtime_fidelity_report.get("pass", False) if runtime_fidelity_report else True)
        and (export_smoke_report.get("pass", False) if export_smoke_report else True)
        and (mobile_geometry_report.get("pass", False) if mobile_geometry_report else True)
        and (ai_advised_report.get("pass", False) if ai_advised_report else True)
        and (pptx_export_report.get("pass", False) if pptx_export_report else True)
    )

    quality_report_path = case_dir / "quality-report.json"
    quality_report_path.write_text(json.dumps(quality_report, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "case_id": case_id,
        "mode": mode,
        "validation_profile": validation_profile,
        "pass": pass_status,
        "preset": packet["preset"],
        "support_tier": packet.get("preset_support_tier"),
        "brief_path": str(brief_path) if brief_path else None,
        "source_path": str(source_path) if source_path else None,
        "html_path": str(rendered_html_path),
        "fixture_html_path": str(fixture_html_path) if fixture_html_path else None,
        "packet_path": str(packet_path),
        "packet": packet,
        "quality_report_path": str(quality_report_path),
        "baseline_html_path": str(baseline_html_path) if baseline_html_path else None,
        "hard_failures": hard_failures,
        "validations": {
            "brief": {
                "passed": brief_valid if brief_path else None,
                "errors": brief_errors,
            },
            "html_validate": validate_report,
            "title_browser": title_browser_report,
            "browser_geometry": browser_geometry_report,
            "browser_geometry_report_path": str(browser_geometry_report_path) if browser_geometry_report_path else None,
            "preset_fidelity": preset_fidelity_report,
            "preset_fidelity_report_path": str(preset_fidelity_report_path) if preset_fidelity_report_path else None,
            "runtime_fidelity": runtime_fidelity_report,
            "runtime_fidelity_report_path": str(runtime_fidelity_report_path) if runtime_fidelity_report_path else None,
            "export_smoke": export_smoke_report,
            "export_smoke_report_path": str(export_smoke_report_path) if export_smoke_report_path else None,
            "mobile_geometry": mobile_geometry_report,
            "mobile_geometry_report_path": str(mobile_geometry_report_path) if mobile_geometry_report_path else None,
            "ai_advised": ai_advised_report,
            "ai_advised_report_path": str(ai_advised_report_path) if ai_advised_report_path else None,
            "pptx_export": pptx_export_report,
            "pptx_export_report_path": str(pptx_export_report_path) if pptx_export_report_path else None,
        },
        "expectations": expectations_report,
        "scores": scores,
        "diagnostics": {"low_context": diagnostics},
        "overall": overall,
        "notes": case.get("notes", []),
    }


def _summarize_cases(cases: list[dict[str, Any]], *, baseline_dir: Path | None) -> dict[str, Any]:
    pass_count = sum(1 for case in cases if case["pass"])
    fail_count = len(cases) - pass_count
    by_bucket: dict[str, dict[str, int]] = {}
    non_regression_ready = 0
    for case in cases:
        bucket = case.get("mode", "unknown")
        bucket_summary = by_bucket.setdefault(bucket, {"pass": 0, "fail": 0})
        if case["pass"]:
            bucket_summary["pass"] += 1
        else:
            bucket_summary["fail"] += 1

        if case.get("baseline_html_path"):
            non_regression_ready += 1

    best_case = None
    best_score = -math.inf
    for case in cases:
        if case["overall"] > best_score:
            best_case = case["case_id"]
            best_score = case["overall"]

    return {
        "pass_count": pass_count,
        "fail_count": fail_count,
        "best_case": best_case,
        "best_overall": round(best_score, 4) if cases else None,
        "baseline_comparison_enabled": bool(baseline_dir),
        "non_regression_ready_cases": non_regression_ready,
        "buckets": by_bucket,
    }


def run_suite(
    manifest_path: Path,
    *,
    output_dir: Path,
    baseline_dir: Path | None = None,
    run_browser_titles: bool = False,
    run_browser_geometry: bool = False,
    run_contract: bool = False,
    run_export_smoke: bool = False,
    run_mobile_geometry: bool = False,
    run_ai_advised: bool = False,
    run_pptx_export: bool = False,
    run_promotion_gate: bool = False,
    run_demo_parity: bool = False,
    demo_parity_require_visual: bool = False,
    demo_parity_viewports: list[str] | None = None,
) -> dict[str, Any]:
    manifest = _read_json(manifest_path)
    suite_dir = manifest_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    weights = manifest.get(
        "weights",
        {
            "route": 0.15,
            "compression": 0.25,
            "render": 0.45,
            "efficiency": 0.15,
        },
    )

    results = []
    for case in manifest["cases"]:
        results.append(
            _evaluate_rendered_case(
                case=case,
                suite_dir=suite_dir,
                output_dir=output_dir,
                baseline_dir=baseline_dir,
                run_browser_titles=run_browser_titles,
                run_browser_geometry=run_browser_geometry,
                run_contract=run_contract,
                run_export_smoke=run_export_smoke,
                run_mobile_geometry=run_mobile_geometry,
                run_ai_advised=run_ai_advised,
                run_pptx_export=run_pptx_export,
                weights=weights,
            )
        )

    report = {
        "suite_id": manifest["suite_id"],
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "manifest_path": str(manifest_path),
        "git_head": _git_head(),
        "git_dirty": _git_dirty(),
        "output_dir": str(output_dir),
        "baseline_dir": str(baseline_dir) if baseline_dir else None,
        "workflow": manifest.get("workflow", ["BRIEF.json", "HTML", "validate", "eval"]),
        "weights": weights,
        "cases": results,
        "summary": _summarize_cases(results, baseline_dir=baseline_dir),
    }
    if run_promotion_gate:
        try:
            promotion_report = globals()["run_promotion_gate"](release_report=report)
        except Exception as exc:  # pragma: no cover - defensive local file path
            promotion_report = {
                "pass": False,
                "unavailable": True,
                "error": f"promotion gate unavailable: {exc}",
                "hard_failures": ["promotion-gate-unavailable"],
                "violations": [],
                "diagnostics": {},
            }
        promotion_report_path = output_dir / "promotion-gate-report.json"
        promotion_report_path.write_text(
            json.dumps(promotion_report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        report["promotion_gate"] = promotion_report
        report["promotion_gate_report_path"] = str(promotion_report_path)
    if run_demo_parity:
        demo_parity_output_dir = output_dir / "demo-parity"
        try:
            demo_parity_report = globals()["run_demo_parity_gate"](
                candidate_dir=output_dir,
                demo_dir=ROOT / "demos",
                output_dir=demo_parity_output_dir,
                viewports=demo_parity_viewports or ["desktop", "mobile"],
                require_visual=demo_parity_require_visual,
            )
        except Exception as exc:  # pragma: no cover - defensive local file path
            demo_parity_output_dir.mkdir(parents=True, exist_ok=True)
            demo_parity_report = {
                "pass": False,
                "unavailable": True,
                "error": f"demo parity gate unavailable: {exc}",
                "hard_failures": ["demo-parity-unavailable"],
                "summary": {"preset_count": 0, "verdicts": {"FAIL": 1}, "average_score": 0.0},
                "results": [],
            }
            (demo_parity_output_dir / "demo-parity-report.json").write_text(
                json.dumps(demo_parity_report, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        report["demo_parity"] = demo_parity_report
        report["demo_parity_report_path"] = str(demo_parity_output_dir / "demo-parity-report.json")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run benchmark eval suites for slide-creator quality verification."
    )
    parser.add_argument("manifest", help="Path to eval suite manifest JSON")
    parser.add_argument("--output-dir", required=True, help="Directory for generated artifacts and report")
    parser.add_argument("--baseline-dir", help="Optional directory from a prior eval run for non-regression comparison")
    parser.add_argument("--browser-titles", action="store_true", help="Run browser title QA for each case")
    parser.add_argument("--browser-geometry", action="store_true", help="Run browser geometry QA for each case")
    parser.add_argument("--contract", action="store_true", help="Run preset contract QA for each case")
    parser.add_argument("--export-smoke", action="store_true", help="Run export DOM smoke QA for each case")
    parser.add_argument("--mobile-geometry", action="store_true", help="Run mobile browser geometry QA for each case")
    parser.add_argument("--ai-advised", action="store_true", help="Run AI-advised content/rhythm eval for each case")
    parser.add_argument("--pptx-export", action="store_true", help="Run real HTML-to-PPTX export smoke for each case")
    parser.add_argument("--promotion-gate", action="store_true", help="Run style-native promotion precondition gate")
    parser.add_argument("--demo-parity", action="store_true", help="Run historical demo parity gate for the 17 profile presets")
    parser.add_argument("--demo-parity-require-visual", action="store_true", help="Fail demo parity when screenshots cannot be captured")
    parser.add_argument("--demo-parity-viewport", choices=("desktop", "mobile"), action="append", default=None)
    parser.add_argument("--report-path", help="Optional explicit path for the JSON report")
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    output_dir = Path(args.output_dir).resolve()
    baseline_dir = Path(args.baseline_dir).resolve() if args.baseline_dir else None

    report = run_suite(
        manifest_path,
        output_dir=output_dir,
        baseline_dir=baseline_dir,
        run_browser_titles=args.browser_titles,
        run_browser_geometry=args.browser_geometry,
        run_contract=args.contract,
        run_export_smoke=args.export_smoke,
        run_mobile_geometry=args.mobile_geometry,
        run_ai_advised=args.ai_advised,
        run_pptx_export=args.pptx_export,
        run_promotion_gate=args.promotion_gate,
        run_demo_parity=args.demo_parity,
        demo_parity_require_visual=args.demo_parity_require_visual,
        demo_parity_viewports=args.demo_parity_viewport,
    )

    report_path = Path(args.report_path).resolve() if args.report_path else output_dir / "eval-results.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    print(f"REPORT: {report_path}")
    promotion_ok = report.get("promotion_gate", {}).get("pass", True)
    demo_parity_ok = report.get("demo_parity", {}).get("pass", True)
    return 0 if report["summary"]["fail_count"] == 0 and promotion_ok and demo_parity_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
