#!/usr/bin/env python3
"""Run every unchanged release-gate case in independent worker processes."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from preset_release_gate import _build_summary_markdown, _collect_gate_failures, _suite_requires_browser_titles
from run_evals import _summarize_cases


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=3)
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    source = args.suite.resolve()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(source.read_text(encoding="utf-8"))
    original_ids = [case["case_id"] for case in manifest["cases"]]
    if not original_ids or len(set(original_ids)) != len(original_ids):
        raise ValueError("Release cases must have unique, non-empty IDs")
    jobs = min(args.jobs, len(original_ids))
    shards = []
    for worker in range(jobs):
        shard = copy.deepcopy(manifest)
        shard["cases"] = shard["cases"][worker::jobs]
        for case in shard["cases"]:
            for key in ("brief_path", "html_path", "source_path", "title_browser_report_path", "baseline_html_path"):
                if case.get(key):
                    case[key] = str((source.parent / case[key]).resolve())
        path = output / f"manifest-{worker}.json"
        path.write_text(json.dumps(shard, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        shards.append(path)

    def run(worker: int) -> int:
        with (output / f"worker-{worker}.log").open("w", encoding="utf-8") as log:
            result = subprocess.run([
                sys.executable, str(Path(__file__).with_name("preset_release_gate.py")),
                "--suite", str(shards[worker]), "--output-dir", str(output / f"worker-{worker}"),
                "--browser-geometry", "--mobile-geometry", "--export-smoke",
            ], stdout=log, stderr=subprocess.STDOUT)
        print(f"Release worker {worker + 1}/{jobs} completed: exit {result.returncode}", flush=True)
        return result.returncode

    with ThreadPoolExecutor(max_workers=jobs) as executor:
        codes = list(executor.map(run, range(jobs)))
    reports = [json.loads((output / f"worker-{worker}/release-gate-report.json").read_text())
               for worker in range(jobs)]
    cases = [case for report in reports for case in report["cases"]]
    by_id = {case["case_id"]: case for case in cases}
    if len(cases) != len(original_ids) or set(by_id) != set(original_ids):
        raise ValueError("Release workers did not produce exactly the original case set")
    report = {**reports[0], "manifest_path": str(source),
              "manifest_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "output_dir": str(output), "cases": [by_id[case_id] for case_id in original_ids]}
    report["summary"] = _summarize_cases(report["cases"], baseline_dir=None)
    failures = _collect_gate_failures(report, require_baseline=False)
    if any(codes) and not failures:
        failures.append("Release worker returned nonzero status")
    report["gate"] = {"passed": not failures, "require_baseline": False, "failures": failures}
    (output / "release-gate-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    (output / "release-gate-summary.md").write_text(_build_summary_markdown(
        report, failures, require_baseline=False, browser_titles_enabled=_suite_requires_browser_titles(source)))
    print(json.dumps(report["summary"], ensure_ascii=False), flush=True)
    if failures:
        print(json.dumps({"gate_failures": failures}, ensure_ascii=False), flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
