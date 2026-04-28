#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from run_evals import run_suite  # noqa: E402


DEFAULT_SUITE = ROOT / "evals" / "preset-surface-phase1" / "manifest.json"


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

    if require_baseline:
        for case in report["cases"]:
            if case.get("mode") == "invalid-brief":
                continue
            if not case.get("baseline_html_path"):
                failures.append(f"{case['case_id']}: missing baseline compare artifact")

    return failures


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

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the preset-surface release gate for core presets plus support-surface fixtures."
    )
    parser.add_argument("--suite", default=str(DEFAULT_SUITE), help="Eval suite manifest to run")
    parser.add_argument("--output-dir", required=True, help="Directory for eval artifacts")
    parser.add_argument("--baseline-dir", help="Optional baseline eval output directory")
    parser.add_argument("--browser-titles", action="store_true", help="Run browser title QA while evaluating")
    parser.add_argument("--require-baseline", action="store_true", help="Fail if render cases have no baseline artifact")
    parser.add_argument("--report-path", help="Optional explicit JSON report path")
    parser.add_argument("--summary-md", help="Optional markdown summary output path")
    args = parser.parse_args()

    suite_path = Path(args.suite).resolve()
    output_dir = Path(args.output_dir).resolve()
    baseline_dir = Path(args.baseline_dir).resolve() if args.baseline_dir else None
    browser_titles_enabled = args.browser_titles or _suite_requires_browser_titles(suite_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    report = run_suite(
        suite_path,
        output_dir=output_dir,
        baseline_dir=baseline_dir,
        run_browser_titles=browser_titles_enabled,
    )

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
