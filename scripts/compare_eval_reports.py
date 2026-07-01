#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from preset_capabilities import CANONICAL_PRESET_NAMES  # noqa: E402


def _read_json(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def _case_preset(case: dict[str, Any]) -> str | None:
    packet = case.get("packet") or {}
    return packet.get("canonical_preset") or case.get("preset") or packet.get("preset")


def _case_score(case: dict[str, Any] | None) -> float | None:
    if not case:
        return None
    if isinstance(case.get("overall"), (int, float)):
        return float(case["overall"])
    if "pass" in case:
        return 1.0 if case.get("pass") else 0.0
    return None


def _strict_pass(case: dict[str, Any] | None) -> bool | None:
    if not case:
        return None
    html_validate = (case.get("validations") or {}).get("html_validate") or {}
    if "passed" in html_validate:
        return bool(html_validate["passed"])
    return None


def _generation_status(case: dict[str, Any] | None) -> str | None:
    if not case:
        return None
    packet = case.get("packet") or {}
    return packet.get("preset_generation_status")


def _repair_rounds(case: dict[str, Any] | None) -> int | None:
    if not case:
        return None
    packet = case.get("packet") or {}
    value = packet.get("repair_rounds")
    return int(value) if isinstance(value, int) else None


def _style_signature(case: dict[str, Any] | None) -> float | None:
    if not case:
        return None
    diagnostics = ((case.get("diagnostics") or {}).get("low_context") or {})
    value = diagnostics.get("style_signature_coverage")
    return float(value) if isinstance(value, (int, float)) else None


def _cases_by_preset(report: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not report:
        return {}
    cases: dict[str, dict[str, Any]] = {}
    for case in report.get("cases", []):
        preset = _case_preset(case)
        if preset:
            cases[preset] = case
    return cases


def _score_delta(baseline: float | None, candidate: float | None) -> float | None:
    if baseline is None or candidate is None:
        return None
    return round(candidate - baseline, 4)


def _strict_delta(baseline: bool | None, candidate: bool | None) -> int | None:
    if baseline is None or candidate is None:
        return None
    return int(candidate) - int(baseline)


def _status_delta(baseline: dict[str, Any] | None, candidate: dict[str, Any] | None) -> str | None:
    if baseline is None or candidate is None:
        return None
    old_pass = bool(baseline.get("pass"))
    new_pass = bool(candidate.get("pass"))
    old_status = _generation_status(baseline) or "unknown"
    new_status = _generation_status(candidate) or "unknown"
    if not old_pass and new_pass:
        return f"{old_status}_fail_to_{new_status}_pass"
    if old_pass and not new_pass:
        return f"{old_status}_pass_to_{new_status}_fail"
    if old_status != new_status:
        return f"{old_status}_to_{new_status}"
    return "unchanged"


def compare_reports(
    *,
    baseline: dict[str, Any] | None,
    candidate: dict[str, Any],
    manifest: str | None,
) -> dict[str, Any]:
    baseline_cases = _cases_by_preset(baseline)
    candidate_cases = _cases_by_preset(candidate)
    presets = sorted(CANONICAL_PRESET_NAMES.values())
    baseline_found = baseline is not None
    comparable_presets = [
        preset for preset in presets if baseline_found and preset in baseline_cases and preset in candidate_cases
    ]

    by_preset: dict[str, Any] = {}
    new_failures: list[str] = []
    fixed_failures: list[str] = []
    new_coverage: list[str] = []
    non_comparable_metrics: set[str] = set()

    for preset in presets:
        old = baseline_cases.get(preset)
        new = candidate_cases.get(preset)
        baseline_score = _case_score(old)
        candidate_score = _case_score(new)
        strict_validation_delta = _strict_delta(_strict_pass(old), _strict_pass(new))
        style_baseline = _style_signature(old)
        style_candidate = _style_signature(new)
        repair_baseline = _repair_rounds(old)
        repair_candidate = _repair_rounds(new)
        non_comparable: list[str] = []

        if baseline_found and old is None:
            non_comparable.append("baseline missing preset case")
        if baseline_found and new is None:
            non_comparable.append("candidate missing preset case")
        if baseline_found and old is not None and baseline_score is None:
            non_comparable.append("baseline score missing")
        if baseline_found and old is not None and _strict_pass(old) is None:
            non_comparable.append("baseline strict validation field missing")
        if baseline_found and old is not None and style_baseline is None:
            non_comparable.append("baseline style signature score missing")
        if baseline_found and old is not None and repair_baseline is None:
            non_comparable.append("baseline repair round count missing")
        non_comparable_metrics.update(non_comparable)

        if old and new and old.get("pass") and not new.get("pass"):
            new_failures.append(f"{preset}: candidate eval case regressed to failure")
        if old and new and not old.get("pass") and new.get("pass"):
            fixed_failures.append(f"{preset}: eval case now passes")
        if old is None and new and new.get("pass") and baseline_found:
            new_coverage.append(f"{preset}: newly covered passing case")

        by_preset[preset] = {
            "baseline_score": baseline_score,
            "candidate_score": candidate_score,
            "delta": _score_delta(baseline_score, candidate_score),
            "strict_validation_delta": strict_validation_delta,
            "generation_status_delta": _status_delta(old, new),
            "repair_rounds_delta": (
                repair_candidate - repair_baseline
                if repair_candidate is not None and repair_baseline is not None
                else None
            ),
            "style_signature_delta": _score_delta(style_baseline, style_candidate),
            "baseline_pass": bool(old.get("pass")) if old else None,
            "candidate_pass": bool(new.get("pass")) if new else None,
            "non_comparable_fields": non_comparable,
        }

    baseline_scores = [_case_score(baseline_cases[preset]) for preset in comparable_presets]
    comparable_candidate_scores = [_case_score(candidate_cases[preset]) for preset in comparable_presets]
    candidate_scores = [_case_score(case) for case in candidate_cases.values()]
    baseline_overall = (
        round(sum(score for score in baseline_scores if score is not None) / len(baseline_scores), 4)
        if baseline_scores and all(score is not None for score in baseline_scores)
        else None
    )
    comparable_candidate_overall = (
        round(sum(score for score in comparable_candidate_scores if score is not None) / len(comparable_candidate_scores), 4)
        if comparable_candidate_scores and all(score is not None for score in comparable_candidate_scores)
        else None
    )
    candidate_full_score = (
        round(sum(score for score in candidate_scores if score is not None) / len(candidate_scores), 4)
        if candidate_scores and all(score is not None for score in candidate_scores)
        else None
    )
    candidate_overall = comparable_candidate_overall if baseline_found else candidate_full_score

    return {
        "baseline_status": "found" if baseline_found else "missing",
        "baseline_git_sha": baseline.get("git_head") if baseline else None,
        "baseline_git_dirty": baseline.get("git_dirty") if baseline else None,
        "candidate_git_sha": candidate.get("git_head") or _git_head(),
        "candidate_git_dirty": candidate.get("git_dirty"),
        "manifest": manifest or candidate.get("manifest_path"),
        "baseline_preset_count": len(baseline_cases),
        "candidate_preset_count": len(candidate_cases),
        "comparable_preset_count": len(comparable_presets),
        "baseline_missing_presets": [preset for preset in presets if baseline_found and preset not in baseline_cases],
        "candidate_missing_presets": [preset for preset in presets if baseline_found and preset not in candidate_cases],
        "overall": {
            "baseline_score": baseline_overall,
            "candidate_score": candidate_overall,
            "candidate_full_score": candidate_full_score,
            "delta": _score_delta(baseline_overall, candidate_overall),
        },
        "by_preset": by_preset,
        "new_failures": new_failures,
        "fixed_failures": fixed_failures,
        "new_coverage": new_coverage,
        "non_comparable_metrics": sorted(non_comparable_metrics),
    }


def _markdown_summary(delta: dict[str, Any]) -> str:
    status = delta["baseline_status"]
    overall = delta["overall"]
    lines = [
        "# EVA Delta",
        "",
        f"- Baseline status: `{status}`",
        f"- Manifest: `{delta.get('manifest')}`",
        f"- Baseline git SHA: `{delta.get('baseline_git_sha') or 'n/a'}`",
        f"- Baseline git dirty: `{delta.get('baseline_git_dirty')}`",
        f"- Candidate git SHA: `{delta.get('candidate_git_sha') or 'n/a'}`",
        f"- Candidate git dirty: `{delta.get('candidate_git_dirty')}`",
        f"- Baseline presets: `{delta.get('baseline_preset_count')}`",
        f"- Candidate presets: `{delta.get('candidate_preset_count')}`",
        f"- Comparable presets: `{delta.get('comparable_preset_count')}`",
        f"- Baseline score: `{overall.get('baseline_score')}`",
        f"- Candidate comparable score: `{overall.get('candidate_score')}`",
        f"- Candidate full score: `{overall.get('candidate_full_score')}`",
        f"- Delta: `{overall.get('delta')}`",
        "",
        "## Result",
        "",
    ]
    if status == "missing":
        lines.append("No comparable baseline was found, so this EVA report does not claim improvement or regression.")
    elif delta["new_failures"]:
        lines.append("Candidate regressed because new failures were introduced.")
    elif overall.get("delta") is not None and overall["delta"] > 0:
        lines.append("Candidate improved on comparable aggregate score.")
    elif overall.get("delta") is not None and overall["delta"] < 0:
        lines.append("Candidate regressed on comparable aggregate score.")
    else:
        lines.append("Candidate is score-neutral on comparable aggregate score.")

    lines.extend(["", "## New Failures", ""])
    lines.extend(f"- {item}" for item in delta["new_failures"] or ["None"])
    lines.extend(["", "## Fixed Failures", ""])
    lines.extend(f"- {item}" for item in delta["fixed_failures"] or ["None"])
    lines.extend(["", "## New Coverage", ""])
    lines.extend(f"- {item}" for item in delta["new_coverage"] or ["None"])
    lines.extend(["", "## Non-Comparable Metrics", ""])
    lines.extend(f"- {item}" for item in delta["non_comparable_metrics"] or ["None"])
    lines.extend(["", "## Missing Baseline Presets", ""])
    lines.extend(f"- `{item}`" for item in delta["baseline_missing_presets"] or ["None"])
    lines.extend(["", "## Missing Candidate Presets", ""])
    lines.extend(f"- `{item}`" for item in delta["candidate_missing_presets"] or ["None"])
    lines.extend(["", "## Per Preset", ""])
    for preset, entry in delta["by_preset"].items():
        lines.append(
            f"- `{preset}` baseline=`{entry['baseline_score']}` "
            f"candidate=`{entry['candidate_score']}` delta=`{entry['delta']}` "
            f"status=`{entry['generation_status_delta']}`"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare slide-creator eval reports and write EVA delta artifacts.")
    parser.add_argument("--baseline", help="Baseline eval report JSON. Missing path is reported as baseline_status=missing.")
    parser.add_argument("--candidate", required=True, help="Candidate eval report JSON")
    parser.add_argument("--manifest", help="Manifest path to record in the delta")
    parser.add_argument("--output-json", required=True, help="Output delta JSON path")
    parser.add_argument("--output-md", required=True, help="Output delta Markdown path")
    args = parser.parse_args()

    baseline_path = Path(args.baseline).resolve() if args.baseline else None
    candidate_path = Path(args.candidate).resolve()
    baseline = _read_json(baseline_path)
    candidate = _read_json(candidate_path)
    if candidate is None:
        print(f"Candidate report not found: {candidate_path}", file=sys.stderr)
        return 2

    delta = compare_reports(baseline=baseline, candidate=candidate, manifest=args.manifest)
    output_json = Path(args.output_json).resolve()
    output_md = Path(args.output_md).resolve()
    _write_json(output_json, delta)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(_markdown_summary(delta), encoding="utf-8")
    print(f"EVA_DELTA_JSON: {output_json}")
    print(f"EVA_DELTA_MD: {output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
