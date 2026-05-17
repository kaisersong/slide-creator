#!/usr/bin/env python3
"""Compare two captured-run skill eval JSON files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


CATEGORIES = ["outcome", "process", "style", "efficiency"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def numeric_delta(new_value: Any, old_value: Any) -> int | float:
    return round(float(new_value or 0) - float(old_value or 0), 2)


def cases_by_id(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(case["case_id"]): case for case in payload.get("cases", [])}


def summary_delta(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    old_summary = old.get("summary", {})
    new_summary = new.get("summary", {})
    old_categories = old_summary.get("average_category_scores", {})
    new_categories = new_summary.get("average_category_scores", {})
    return {
        "total": numeric_delta(new_summary.get("total"), old_summary.get("total")),
        "passed": numeric_delta(new_summary.get("passed"), old_summary.get("passed")),
        "failed": numeric_delta(new_summary.get("failed"), old_summary.get("failed")),
        "incomplete": numeric_delta(new_summary.get("incomplete"), old_summary.get("incomplete")),
        "average_score": numeric_delta(new_summary.get("average_score"), old_summary.get("average_score")),
        "average_category_scores": {
            category: numeric_delta(new_categories.get(category), old_categories.get(category))
            for category in CATEGORIES
        },
    }


def compare_cases(old: dict[str, Any], new: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    old_cases = cases_by_id(old)
    new_cases = cases_by_id(new)
    case_deltas: list[dict[str, Any]] = []
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
            category: numeric_delta(new_scores.get(category), old_scores.get(category))
            for category in CATEGORIES
        }
        total_delta = numeric_delta(new_case.get("total_score"), old_case.get("total_score"))
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

    return case_deltas, regressions


def build_payload(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    case_deltas, regressions = compare_cases(old, new)
    return {
        "summary_delta": summary_delta(old, new),
        "case_deltas": case_deltas,
        "regressions": regressions,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old", required=True, help="Baseline JSON path.")
    parser.add_argument("--new", required=True, help="New eval JSON path.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(load_json(Path(args.old)), load_json(Path(args.new)))
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Average score delta: {payload['summary_delta']['average_score']:+}")
        for case in payload["case_deltas"]:
            if case["status"] != "compared":
                print(f"{case['status'].upper()} {case['case_id']}")
                continue
            print(
                f"{case['case_id']}: "
                f"score {case['total_score']:+}, "
                f"pass {case['passed']:+}, "
                f"complete {case['eval_complete']:+}"
            )
        if payload["regressions"]:
            print("Regressions:")
            for regression in payload["regressions"]:
                print(f"  - {regression}")
    return 1 if payload["regressions"] else 0


if __name__ == "__main__":
    sys.exit(main())
