#!/usr/bin/env python3
"""
check-doc-sync.py — lightweight doc contract checker for slide-creator.

Purpose:
    Catch drift between the three user-facing docs that define the skill:
    - SKILL.md
    - README.md
    - references/workflow.md

This script is intentionally zero-dependency and read-only. `--dry-run` is
accepted for explicit check-only usage and future compatibility, but it does
not modify files in any mode.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuleResult:
    name: str
    ok: bool
    detail: str


def read_required(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    return path.read_text(encoding="utf-8")


def contains_all(text: str, snippets: list[str]) -> tuple[bool, str]:
    missing = [snippet for snippet in snippets if snippet not in text]
    if missing:
        return False, "missing: " + ", ".join(repr(item) for item in missing)
    return True, "all expected markers present"


def contains_none(text: str, snippets: list[str]) -> tuple[bool, str]:
    present = [snippet for snippet in snippets if snippet in text]
    if present:
        return False, "forbidden markers present: " + ", ".join(repr(item) for item in present)
    return True, "no forbidden markers present"


def evaluate(root: Path) -> list[RuleResult]:
    skill = read_required(root / "SKILL.md")
    readme = read_required(root / "README.md")
    workflow = read_required(root / "references" / "workflow.md")

    results: list[RuleResult] = []

    ok, detail = contains_all(
        skill,
        [
            "Edit Mode (default-on, optional)",
            "--plan",
            "--generate",
            "themes/<name>/reference.md",
        ],
    )
    if ok:
        ok, detail = contains_none(skill, ["Every generated HTML file MUST include both of these", "shareable URL"])
    results.append(RuleResult("skill-contract", ok, detail))

    ok, detail = contains_all(
        readme,
        [
            "Two-stage workflow",
            "--plan",
            "--generate",
            "Default-on, optional",
            "themes/your-theme/",
            "reference.md",
        ],
    )
    if ok:
        ok, detail = contains_none(readme, ["Vercel", "shareable URL", "Share to URL"])
    results.append(RuleResult("readme-contract", ok, detail))

    ok, detail = contains_all(
        workflow,
        [
            "Enhancement Mode (existing HTML)",
            "single AskUserQuestion call with all 5 questions at once",
            "1280x720",
        ],
    )
    results.append(RuleResult("workflow-contract", ok, detail))

    share_violations = []
    for label, text, forbidden in [
        ("SKILL.md", skill, ["shareable URL"]),
        ("README.md", readme, ["Vercel", "shareable URL", "Share to URL"]),
        ("references/workflow.md", workflow, ["Phase 6: Share"]),
    ]:
        present = [item for item in forbidden if item in text]
        if present:
            share_violations.append(f"{label}: {', '.join(repr(item) for item in present)}")
    results.append(
        RuleResult(
            "no-share-language",
            not share_violations,
            "ok" if not share_violations else "; ".join(share_violations),
        )
    )

    edit_mode_ok = (
        "Edit Mode (default-on, optional)" in skill
        and "Default-on, optional" in readme
        and "Every generated HTML file MUST include both of these" not in skill
    )
    results.append(
        RuleResult(
            "edit-mode-default",
            edit_mode_ok,
            "skill + readme agree that edit mode is default-on and optional"
            if edit_mode_ok
            else "skill/readme disagree on optional edit mode language",
        )
    )

    return results


def print_results(results: list[RuleResult], dry_run: bool) -> int:
    if dry_run:
        print("DRY RUN: checking document contracts only, no files will be changed.")

    failures = 0
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"{status} {result.name}: {result.detail}")
        if not result.ok:
            failures += 1

    if failures:
        print(f"\nSummary: {failures} rule(s) failed.")
        return 1

    print(f"\nSummary: {len(results)} rule(s) passed.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root to inspect. Defaults to current directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Explicit check-only mode. This script is read-only in all modes.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    try:
        results = evaluate(root)
    except FileNotFoundError as exc:
        print(f"FAIL missing-file: {exc}")
        return 1
    return print_results(results, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
