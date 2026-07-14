#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from run_evals import run_suite  # noqa: E402
from preset_contracts import load_preset_contract  # noqa: E402


DEFAULT_SUITE = ROOT / "evals" / "preset-surface-all" / "manifest.json"
SKILL_EVAL_CATEGORIES = ["outcome", "process", "style", "efficiency"]


def _suite_requires_browser_titles(suite_path: Path) -> bool:
    manifest = json.loads(suite_path.read_text(encoding="utf-8"))
    return any(case.get("expectations", {}).get("required_title_gates") for case in manifest.get("cases", []))


def _group_cases(report: dict) -> tuple[list[dict], list[dict]]:
    render_cases = [case for case in report["cases"] if case.get("mode") == "render"]
    fixture_cases = [case for case in report["cases"] if case.get("mode") == "html-fixture"]
    return render_cases, fixture_cases


def _collect_gate_failures(report: dict, *, require_baseline: bool) -> list[str]:
    failures: list[str] = []
    for case in report["cases"]:
        if not case["pass"]:
            failures.append(f"{case['case_id']}: eval case failed")
        browser_geometry = case.get("validations", {}).get("browser_geometry")
        if browser_geometry and not browser_geometry.get("pass", False):
            hard_failures = browser_geometry.get("hard_failures") or ["browser-geometry-failed"]
            for code in hard_failures:
                failures.append(f"{case['case_id']}: browser geometry failed {code}")
        validations = case.get("validations", {})
        preset_fidelity = validations.get("preset_fidelity")
        if validations.get("preset_contract") is not None and preset_fidelity is None:
            failures.append(f"{case['case_id']}: preset fidelity missing (legacy writer key rejected)")
        if preset_fidelity and not preset_fidelity.get("pass", False):
            hard_failures = preset_fidelity.get("hard_failures") or ["preset-fidelity-failed"]
            for code in hard_failures:
                failures.append(f"{case['case_id']}: preset fidelity failed {code}")
        try:
            runtime_required = bool(load_preset_contract(case.get("preset", "")).get("runtime_fidelity"))
        except (FileNotFoundError, ValueError, KeyError):
            runtime_required = False
        if runtime_required:
            runtime_fidelity = validations.get("runtime_fidelity")
            if not runtime_fidelity:
                failures.append(f"{case['case_id']}: runtime fidelity evidence missing")
            elif not runtime_fidelity.get("pass", False):
                hard_failures = runtime_fidelity.get("hard_failures") or ["runtime-fidelity-failed"]
                for code in hard_failures:
                    failures.append(f"{case['case_id']}: runtime fidelity failed {code}")
        export_smoke = case.get("validations", {}).get("export_smoke")
        if export_smoke and not export_smoke.get("pass", False):
            hard_failures = export_smoke.get("hard_failures") or ["export-smoke-failed"]
            for code in hard_failures:
                failures.append(f"{case['case_id']}: export smoke failed {code}")
        mobile_geometry = case.get("validations", {}).get("mobile_geometry")
        if mobile_geometry and not mobile_geometry.get("pass", False):
            hard_failures = mobile_geometry.get("hard_failures") or ["mobile-geometry-failed"]
            for code in hard_failures:
                failures.append(f"{case['case_id']}: mobile geometry failed {code}")
        ai_advised = case.get("validations", {}).get("ai_advised")
        if ai_advised and not ai_advised.get("pass", False):
            hard_failures = ai_advised.get("hard_failures") or ["ai-advised-failed"]
            for code in hard_failures:
                failures.append(f"{case['case_id']}: ai-advised eval failed {code}")
        pptx_export = case.get("validations", {}).get("pptx_export")
        if pptx_export and not pptx_export.get("pass", False):
            hard_failures = pptx_export.get("hard_failures") or ["pptx-export-failed"]
            for code in hard_failures:
                failures.append(f"{case['case_id']}: PPTX export failed {code}")

    promotion_gate = report.get("promotion_gate")
    if promotion_gate and not promotion_gate.get("pass", False):
        hard_failures = promotion_gate.get("hard_failures") or ["promotion-gate-failed"]
        for code in hard_failures:
            failures.append(f"promotion-gate: {code}")

    demo_parity = report.get("demo_parity")
    if demo_parity and not demo_parity.get("pass", False):
        for item in demo_parity.get("results") or []:
            if item.get("verdict") == "PASS":
                continue
            failures.append(
                f"demo-parity: {item.get('preset', 'unknown preset')} "
                f"{item.get('verdict', 'FAIL')} - {item.get('main_issue', 'parity failed')}"
            )
            visual_gate = item.get("visual_gate") or {}
            for code in visual_gate.get("failures") or []:
                failures.append(f"demo-parity: {item.get('preset', 'unknown preset')} visual failed {code}")
            for code in item.get("required_instance_failures") or []:
                failures.append(f"demo-parity: {item.get('preset', 'unknown preset')} instance failed {code}")
        for code in demo_parity.get("hard_failures") or []:
            failures.append(f"demo-parity: {code}")

    if require_baseline:
        for case in report["cases"]:
            if case.get("mode") == "invalid-brief":
                continue
            if not case.get("baseline_html_path"):
                failures.append(f"{case['case_id']}: missing baseline compare artifact")

    skill_evals = report.get("skill_evals")
    if skill_evals:
        if skill_evals.get("returncode") != 0:
            failures.append("skill-evals: captured-run eval command failed")
        summary = skill_evals.get("summary") or {}
        if summary.get("failed"):
            failures.append(f"skill-evals: {summary['failed']} captured-run case(s) failed")
        if summary.get("incomplete"):
            failures.append(f"skill-evals: {summary['incomplete']} captured-run case(s) incomplete")
        baseline_compare = skill_evals.get("baseline_compare") or {}
        for regression in baseline_compare.get("regressions") or []:
            failures.append(f"skill-evals: baseline regression {regression}")

    return failures


def _resolve_root_path(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else ROOT / path


def _numeric_delta(new_value: object, old_value: object) -> int | float:
    return round(float(new_value or 0) - float(old_value or 0), 2)


def _cases_by_id(payload: dict) -> dict[str, dict]:
    return {str(case["case_id"]): case for case in payload.get("cases", [])}


def _compare_skill_eval_payloads(old: dict, new: dict) -> dict:
    old_summary = old.get("summary", {})
    new_summary = new.get("summary", {})
    old_categories = old_summary.get("average_category_scores", {})
    new_categories = new_summary.get("average_category_scores", {})
    summary_delta = {
        "total": _numeric_delta(new_summary.get("total"), old_summary.get("total")),
        "passed": _numeric_delta(new_summary.get("passed"), old_summary.get("passed")),
        "failed": _numeric_delta(new_summary.get("failed"), old_summary.get("failed")),
        "incomplete": _numeric_delta(new_summary.get("incomplete"), old_summary.get("incomplete")),
        "average_score": _numeric_delta(new_summary.get("average_score"), old_summary.get("average_score")),
        "average_category_scores": {
            category: _numeric_delta(new_categories.get(category), old_categories.get(category))
            for category in SKILL_EVAL_CATEGORIES
        },
    }

    old_cases = _cases_by_id(old)
    new_cases = _cases_by_id(new)
    case_deltas: list[dict] = []
    regressions: list[str] = []
    for case_id in sorted(set(old_cases) | set(new_cases)):
        old_case = old_cases.get(case_id)
        new_case = new_cases.get(case_id)
        if old_case is None:
            case_deltas.append({"case_id": case_id, "status": "added"})
            continue
        if new_case is None:
            case_deltas.append({"case_id": case_id, "status": "removed"})
            regressions.append(f"case.{case_id}.removed")
            continue

        old_scores = old_case.get("scores", {})
        new_scores = new_case.get("scores", {})
        category_deltas = {
            category: _numeric_delta(new_scores.get(category), old_scores.get(category))
            for category in SKILL_EVAL_CATEGORIES
        }
        total_delta = _numeric_delta(new_case.get("total_score"), old_case.get("total_score"))
        pass_delta = int(bool(new_case.get("passed"))) - int(bool(old_case.get("passed")))
        complete_delta = int(bool(new_case.get("eval_complete", True))) - int(bool(old_case.get("eval_complete", True)))
        case_deltas.append(
            {
                "case_id": case_id,
                "status": "compared",
                "total_score": total_delta,
                "passed": pass_delta,
                "eval_complete": complete_delta,
                "scores": category_deltas,
                "old_failures": old_case.get("failures", []),
                "new_failures": new_case.get("failures", []),
            }
        )

        if old_case.get("passed") and not new_case.get("passed"):
            regressions.append(f"case.{case_id}.pass_regressed")
        if old_case.get("eval_complete", True) and not new_case.get("eval_complete", True):
            regressions.append(f"case.{case_id}.completeness_regressed")
        if total_delta < 0:
            regressions.append(f"case.{case_id}.score_regressed")
        for category, delta in category_deltas.items():
            if delta < 0:
                regressions.append(f"case.{case_id}.{category}_regressed")

    return {
        "summary_delta": summary_delta,
        "case_deltas": case_deltas,
        "regressions": regressions,
    }


def _skill_eval_baseline_path(args: argparse.Namespace, baseline_dir: Path | None) -> Path | None:
    if args.skill_evals_baseline_json:
        return _resolve_root_path(args.skill_evals_baseline_json)
    if baseline_dir:
        candidate = baseline_dir / "skill-evals.json"
        if candidate.exists():
            return candidate
    return None


def _run_skill_evals(args: argparse.Namespace, output_dir: Path, baseline_dir: Path | None) -> dict:
    json_out = _resolve_root_path(args.skill_evals_json_out) if args.skill_evals_json_out else output_dir / "skill-evals.json"
    command = [
        sys.executable,
        str(ROOT / "scripts" / "run-skill-evals.py"),
        "--root",
        str(ROOT),
        "--runner",
        args.skill_evals_runner,
        "--format",
        "json",
        "--artifact-dir",
        str(output_dir / "skill-runs"),
        "--json-out",
        str(json_out),
    ]
    if args.skill_evals_case_id:
        command.extend(["--case-id", args.skill_evals_case_id])
    if args.skill_evals_normalized_trace:
        command.extend(["--normalized-trace", str(_resolve_root_path(args.skill_evals_normalized_trace))])
    elif args.skill_evals_runner != "fixture":
        command.append("--run-live")

    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=900)
    payload: dict = {}
    if json_out.exists():
        payload = json.loads(json_out.read_text(encoding="utf-8"))
    result = {
        "command": subprocess.list2cmdline(command),
        "json_out": str(json_out),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        **payload,
    }
    baseline_path = _skill_eval_baseline_path(args, baseline_dir)
    if baseline_path and baseline_path.exists() and payload:
        result["baseline_compare"] = _compare_skill_eval_payloads(
            json.loads(baseline_path.read_text(encoding="utf-8")),
            payload,
        )
        result["baseline_json"] = str(baseline_path)
    return result


def _build_summary_markdown(
    report: dict,
    gate_failures: list[str],
    *,
    require_baseline: bool,
    browser_titles_enabled: bool,
) -> str:
    summary = report["summary"]
    render_cases, fixture_cases = _group_cases(report)

    lines = [
        "# Preset Surface Release Gate",
        "",
        f"- Generated: `{datetime.now().isoformat(timespec='seconds')}`",
        f"- Suite: `{report['suite_id']}`",
        f"- Output: `{report['output_dir']}`",
        f"- Baseline dir: `{report['baseline_dir'] or 'none'}`",
        f"- Require baseline: `{str(require_baseline).lower()}`",
        f"- Browser titles: `{str(browser_titles_enabled).lower()}`",
        "",
        "## Summary",
        "",
        f"- Pass count: `{summary['pass_count']}`",
        f"- Fail count: `{summary['fail_count']}`",
        f"- Best case: `{summary['best_case']}`",
        f"- Baseline enabled: `{str(summary['baseline_comparison_enabled']).lower()}`",
        f"- Non-regression ready cases: `{summary['non_regression_ready_cases']}`",
        "",
        "## Deterministic Core",
        "",
    ]

    for case in render_cases:
        diagnostics = case["diagnostics"]["low_context"]
        lines.append(
            "- "
            f"`{case['case_id']}` "
            f"`{'PASS' if case['pass'] else 'FAIL'}` "
            f"preset=`{case['preset']}` "
            f"tier=`{diagnostics.get('quality_tier')}` "
            f"style=`{diagnostics.get('style_signature_coverage')}` "
            f"minimal-run=`{diagnostics.get('max_minimal_slide_run')}`"
        )

    lines.extend([
        "",
        "## Support Surface",
        "",
    ])

    for case in fixture_cases:
        diagnostics = case["diagnostics"]["low_context"]
        lines.append(
            "- "
            f"`{case['case_id']}` "
            f"`{'PASS' if case['pass'] else 'FAIL'}` "
            f"preset=`{case['preset']}` "
            f"support-tier=`{case['support_tier']}` "
            f"style=`{diagnostics.get('style_signature_coverage')}`"
        )

    demo_parity = report.get("demo_parity")
    if demo_parity:
        parity_summary = demo_parity.get("summary") or {}
        verdicts = parity_summary.get("verdicts") or {}
        lines.extend(
            [
                "",
                "## Demo Parity",
                "",
                f"- Pass: `{str(demo_parity.get('pass', False)).lower()}`",
                f"- Presets: `{parity_summary.get('preset_count', 0)}`",
                f"- Verdicts: `{json.dumps(verdicts, ensure_ascii=False)}`",
                f"- Report: `{report.get('demo_parity_report_path')}`",
            ]
        )

    lines.extend([
        "",
        "## Gate Result",
        "",
    ])

    if gate_failures:
        for failure in gate_failures:
            lines.append(f"- `{failure}`")
    else:
        lines.append("- `PASS`")

    skill_evals = report.get("skill_evals")
    if skill_evals:
        summary = skill_evals.get("summary") or {}
        lines.extend(
            [
                "",
                "## Captured-Run Skill Evals",
                "",
                f"- Command: `{skill_evals.get('command')}`",
                f"- Return code: `{skill_evals.get('returncode')}`",
                f"- Total: `{summary.get('total', 0)}`",
                f"- Passed: `{summary.get('passed', 0)}`",
                f"- Failed: `{summary.get('failed', 0)}`",
                f"- Incomplete: `{summary.get('incomplete', 0)}`",
            ]
        )
        baseline_compare = skill_evals.get("baseline_compare")
        if baseline_compare:
            lines.extend(
                [
                    f"- Baseline JSON: `{skill_evals.get('baseline_json')}`",
                    f"- Baseline regressions: `{len(baseline_compare.get('regressions') or [])}`",
                ]
            )

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the preset-surface release gate for core presets plus support-surface fixtures."
    )
    parser.add_argument("--suite", default=str(DEFAULT_SUITE), help="Eval suite manifest to run")
    parser.add_argument("--output-dir", required=True, help="Directory for eval artifacts")
    parser.add_argument("--baseline-dir", help="Optional baseline eval output directory")
    parser.add_argument("--browser-titles", action="store_true", help="Run browser title QA while evaluating")
    parser.add_argument("--browser-geometry", action="store_true", help="Run browser geometry QA while evaluating")
    parser.add_argument("--contract", action="store_true", help="Run preset contract QA while evaluating")
    parser.add_argument("--export-smoke", action="store_true", help="Run export DOM smoke QA while evaluating")
    parser.add_argument("--mobile-geometry", action="store_true", help="Run mobile browser geometry QA while evaluating")
    parser.add_argument("--ai-advised", action="store_true", help="Run AI-advised content/rhythm eval while evaluating")
    parser.add_argument("--pptx-export", action="store_true", help="Run real HTML-to-PPTX export smoke while evaluating")
    parser.add_argument("--promotion-gate", action="store_true", help="Run style-native promotion precondition gate")
    parser.add_argument("--demo-parity", action="store_true", help="Run historical demo parity gate for the 17 profile presets")
    parser.add_argument("--demo-parity-require-visual", action="store_true", help="Fail demo parity when screenshots cannot be captured")
    parser.add_argument("--demo-parity-viewport", choices=("desktop", "mobile"), action="append", default=None)
    parser.add_argument("--require-baseline", action="store_true", help="Fail if render cases have no baseline artifact")
    parser.add_argument("--report-path", help="Optional explicit JSON report path")
    parser.add_argument("--summary-md", help="Optional markdown summary output path")
    parser.add_argument("--include-skill-evals", action="store_true", help="Run optional captured-run skill evals.")
    parser.add_argument("--skill-evals-runner", default="codex", choices=["fixture", "codex"], help="Skill eval runner.")
    parser.add_argument("--skill-evals-normalized-trace", help="Use one normalized trace fixture for selected skill eval case.")
    parser.add_argument("--skill-evals-case-id", help="Run one captured-run skill eval case.")
    parser.add_argument("--skill-evals-json-out", help="Output path for captured-run skill eval JSON.")
    parser.add_argument(
        "--skill-evals-baseline-json",
        help="Optional captured-run baseline JSON. Defaults to <baseline-dir>/skill-evals.json when present.",
    )
    args = parser.parse_args()

    suite_path = Path(args.suite).resolve()
    output_dir = Path(args.output_dir).resolve()
    baseline_dir = Path(args.baseline_dir).resolve() if args.baseline_dir else None
    browser_titles_enabled = args.browser_titles or _suite_requires_browser_titles(suite_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    run_suite_kwargs = {
        "output_dir": output_dir,
        "baseline_dir": baseline_dir,
        "run_browser_titles": browser_titles_enabled,
        "run_contract": True,
    }
    if args.browser_geometry:
        run_suite_kwargs["run_browser_geometry"] = True
    if args.export_smoke:
        run_suite_kwargs["run_export_smoke"] = True
    if args.mobile_geometry:
        run_suite_kwargs["run_mobile_geometry"] = True
    if args.ai_advised:
        run_suite_kwargs["run_ai_advised"] = True
    if args.pptx_export:
        run_suite_kwargs["run_pptx_export"] = True
    if args.promotion_gate:
        run_suite_kwargs["run_promotion_gate"] = True
    if args.demo_parity:
        run_suite_kwargs["run_demo_parity"] = True
        run_suite_kwargs["demo_parity_require_visual"] = bool(args.demo_parity_require_visual)
        run_suite_kwargs["demo_parity_viewports"] = args.demo_parity_viewport
    report = run_suite(suite_path, **run_suite_kwargs)

    if args.include_skill_evals:
        report["skill_evals"] = _run_skill_evals(args, output_dir, baseline_dir)

    gate_failures = _collect_gate_failures(report, require_baseline=args.require_baseline)
    report["gate"] = {
        "passed": not gate_failures,
        "require_baseline": bool(args.require_baseline),
        "failures": gate_failures,
    }

    report_path = Path(args.report_path).resolve() if args.report_path else output_dir / "release-gate-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    summary_md_path = Path(args.summary_md).resolve() if args.summary_md else output_dir / "release-gate-summary.md"
    summary_md_path.write_text(
        _build_summary_markdown(
            report,
            gate_failures,
            require_baseline=args.require_baseline,
            browser_titles_enabled=browser_titles_enabled,
        ),
        encoding="utf-8",
    )

    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    if gate_failures:
        print(json.dumps({"gate_failures": gate_failures}, ensure_ascii=False, indent=2))
    print(f"REPORT: {report_path}")
    print(f"SUMMARY_MD: {summary_md_path}")
    return 0 if not gate_failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
