#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from quality_eval import analyze_html_quality_paths


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate whether a generated deck actually improved user-visible quality."
    )
    parser.add_argument("html_path", help="Generated HTML deck to evaluate")
    parser.add_argument("--brief", dest="brief_path", help="BRIEF.json used for rendering")
    parser.add_argument("--source", dest="source_path", help="Original source document path")
    parser.add_argument("--preset", dest="preset", help="Override preset name")
    parser.add_argument("--baseline-html", dest="baseline_html_path", help="Baseline/control HTML for non-regression comparison")
    parser.add_argument("--title-browser-report", dest="title_browser_report_path", help="Precomputed browser title QA JSON report")
    parser.add_argument("--browser-titles", dest="run_browser_titles", action="store_true", help="Run browser-level title QA and merge the result")
    parser.add_argument("--output", dest="output_path", help="Optional output path for JSON report")
    args = parser.parse_args()

    report = analyze_html_quality_paths(
        args.html_path,
        brief_path=args.brief_path,
        source_path=args.source_path,
        preset=args.preset,
        baseline_html_path=args.baseline_html_path,
        title_browser_report_path=args.title_browser_report_path,
        run_browser_titles=args.run_browser_titles,
    )

    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output_path:
        with open(args.output_path, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
