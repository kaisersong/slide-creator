from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from preset_capabilities import (  # noqa: E402
    PRESET_REFERENCE_MAP,
    get_preset_render_capability,
    load_preset_support_matrix,
    normalize_preset_name,
)
from preset_contracts import load_preset_contract, load_preset_manifest  # noqa: E402


NATIVE_STATE = "native_deterministic_core"
PROFILE_STATE = "unified_profile_renderer"
PROMOTION_NATIVE_STATES = {NATIVE_STATE, "production_native", "contextual_native"}
PROMOTION_PROFILE_STATES = {PROFILE_STATE, "production_contract_enforced"}


def _violation(code: str, message: str, **extra: Any) -> dict[str, Any]:
    return {"code": code, "type": code.removeprefix("promotion-"), "severity": "hard", "message": message, **extra}


def _support_state_sets() -> dict[str, set[str]]:
    matrix = load_preset_support_matrix()
    states = matrix.get("policy", {}).get("support_states", {})
    return {
        state: {normalize_preset_name(preset) for preset in presets}
        for state, presets in states.items()
    }


def _state_for_preset(preset: str, states: dict[str, set[str]]) -> str | None:
    normalized = normalize_preset_name(preset)
    matches = [state for state, presets in states.items() if normalized in presets]
    if len(matches) == 1:
        return matches[0]
    return None


def _all_builtin_presets() -> list[str]:
    return sorted(PRESET_REFERENCE_MAP.keys())


def validate_contract_and_manifest_states() -> dict[str, Any]:
    states = _support_state_sets()
    violations: list[dict[str, Any]] = []
    native_count = 0
    profile_count = 0

    assigned: dict[str, list[str]] = {}
    for state, presets in states.items():
        for preset in presets:
            assigned.setdefault(preset, []).append(state)
    for preset, matched_states in sorted(assigned.items()):
        if len(matched_states) > 1:
            violations.append(
                _violation(
                    "promotion-support-state-overlap",
                    "preset appears in multiple support states",
                    preset=preset,
                    states=matched_states,
                )
            )

    for normalized in _all_builtin_presets():
        state = _state_for_preset(normalized, states)
        if state is None:
            violations.append(
                _violation(
                    "promotion-support-state-missing",
                    "preset is not assigned to exactly one support state",
                    preset=normalized,
                )
            )
            continue

        capability = get_preset_render_capability(normalized)
        contract = load_preset_contract(normalized)
        manifest = load_preset_manifest(normalized)
        expected_strategy = "native" if state in PROMOTION_NATIVE_STATES else "unified_profile"
        expected_generation = "ready" if expected_strategy == "native" else "profile"

        if state in PROMOTION_NATIVE_STATES:
            native_count += 1
        elif state in PROMOTION_PROFILE_STATES:
            profile_count += 1

        for source_name, source in (("contract", contract), ("manifest", manifest)):
            if source.get("support_state") != state:
                violations.append(
                    _violation(
                        "promotion-support-state-drift",
                        "contract or manifest support state does not match support matrix",
                        preset=normalized,
                        source=source_name,
                        expected=state,
                        actual=source.get("support_state"),
                    )
                )
            if source.get("renderer_strategy") != expected_strategy:
                violations.append(
                    _violation(
                        "promotion-renderer-strategy-drift",
                        "contract or manifest renderer strategy does not match support state",
                        preset=normalized,
                        source=source_name,
                        expected=expected_strategy,
                        actual=source.get("renderer_strategy"),
                    )
                )

        if capability.renderer_strategy != expected_strategy:
            violations.append(
                _violation(
                    "promotion-capability-drift",
                    "runtime capability renderer strategy does not match support matrix",
                    preset=capability.preset,
                    expected=expected_strategy,
                    actual=capability.renderer_strategy,
                )
            )
        if expected_generation == "ready" and capability.generation_status != "ready":
            violations.append(
                _violation(
                    "promotion-native-not-ready",
                    "native support state must expose ready generation status",
                    preset=capability.preset,
                    actual=capability.generation_status,
                )
            )
        if expected_generation == "profile" and capability.generation_status != "profile":
            violations.append(
                _violation(
                    "promotion-profile-not-profile",
                    "profile support state must expose profile generation status",
                    preset=capability.preset,
                    actual=capability.generation_status,
                )
            )

    return _finish_report(
        phase="1.0-style-native-promotion-precondition",
        violations=violations,
        diagnostics={
            "native_count": native_count,
            "profile_count": profile_count,
            "support_states": {state: len(presets) for state, presets in states.items()},
        },
    )


def validate_release_report_routes(release_report: dict[str, Any]) -> dict[str, Any]:
    states = _support_state_sets()
    violations: list[dict[str, Any]] = []
    checked = 0

    for case in release_report.get("cases", []):
        if case.get("mode") == "invalid-brief":
            continue
        preset = str(case.get("preset") or case.get("packet", {}).get("preset") or "")
        if not preset:
            continue
        checked += 1
        state = _state_for_preset(preset, states)
        packet = case.get("packet") or {}
        actual_strategy = packet.get("renderer_strategy")
        actual_generation = packet.get("preset_generation_status")
        actual_render_path = packet.get("render_path")

        if state in PROMOTION_NATIVE_STATES:
            if actual_strategy != "native" or actual_generation not in {"ready", "native"}:
                violations.append(
                    _violation(
                        "promotion-native-renderer-regressed",
                        "native support-state preset was not rendered by the native path",
                        case_id=case.get("case_id"),
                        preset=preset,
                        actual_strategy=actual_strategy,
                        actual_generation=actual_generation,
                        actual_render_path=actual_render_path,
                    )
                )
        elif state in PROMOTION_PROFILE_STATES:
            if actual_strategy != "unified_profile" or actual_generation != "profile":
                violations.append(
                    _violation(
                        "promotion-profile-renderer-claimed-native",
                        "profile preset is being claimed as native without promotion evidence",
                        case_id=case.get("case_id"),
                        preset=preset,
                        actual_strategy=actual_strategy,
                        actual_generation=actual_generation,
                        actual_render_path=actual_render_path,
                    )
                )

    return _finish_report(
        phase="1.0-release-report-route-check",
        violations=violations,
        diagnostics={"checked_case_count": checked},
    )


def _finish_report(*, phase: str, violations: list[dict[str, Any]], diagnostics: dict[str, Any]) -> dict[str, Any]:
    hard_failures: list[str] = []
    for violation in violations:
        code = str(violation["code"])
        if code not in hard_failures:
            hard_failures.append(code)
    return {
        "version": 1,
        "phase": phase,
        "pass": not violations,
        "hard_failures": hard_failures,
        "violations": violations,
        "diagnostics": diagnostics,
    }


def run_promotion_gate(
    *,
    release_report: dict[str, Any] | None = None,
    release_report_path: str | Path | None = None,
) -> dict[str, Any]:
    base_report = validate_contract_and_manifest_states()

    if release_report is None and release_report_path:
        release_report = json.loads(Path(release_report_path).read_text(encoding="utf-8"))

    route_report = validate_release_report_routes(release_report) if release_report else None
    violations = list(base_report["violations"])
    if route_report:
        violations.extend(route_report["violations"])

    diagnostics = dict(base_report["diagnostics"])
    if route_report:
        diagnostics["release_report"] = route_report["diagnostics"]

    report = _finish_report(
        phase="1.0-style-native-promotion-precondition",
        violations=violations,
        diagnostics=diagnostics,
    )
    report["checks"] = {
        "contract_and_manifest_states": base_report,
        "release_report_routes": route_report,
    }
    return report


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run style-native promotion precondition gate.")
    parser.add_argument("--release-report")
    parser.add_argument("--output")
    args = parser.parse_args()

    report = run_promotion_gate(release_report_path=args.release_report)
    if args.output:
        Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
