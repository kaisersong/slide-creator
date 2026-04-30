#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from low_context import (
    BriefExtractionError,
    BriefValidationError,
    RenderError,
    load_brief,
    render_from_brief,
    render_from_context_path,
    stamp_validation_status,
)
from generation_eval import (
    build_generation_eval_report,
    default_eval_output_path,
    write_generation_eval_report,
)
from validate_html import validate


def _strict_validate_rendered_html(html_text: str) -> bool:
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as handle:
        handle.write(html_text)
        tmp_path = Path(handle.name)

    try:
        return validate(tmp_path, strict=True)
    finally:
        tmp_path.unlink(missing_ok=True)


def _has_canonical_provenance(html_text: str) -> bool:
    required_markers = (
        'data-generator="kai-slide-creator"',
        'data-generator-version="',
        'data-render-path="',
        'data-brief-hash="',
        'data-runtime-path="',
        'data-validate-strict="pending"',
    )
    return all(marker in html_text for marker in required_markers)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a deterministic low-context deck from BRIEF.json.")
    parser.add_argument("brief", nargs="?", help="Path to BRIEF.json")
    parser.add_argument("--context-file", help="Path to a context artifact that must contain exactly one valid BRIEF")
    parser.add_argument("--extract-brief-out", help="Optional path to write the extracted BRIEF as JSON")
    parser.add_argument("--output", required=True, help="Output HTML path")
    parser.add_argument("--eval", action="store_true", help="Write a single-deck eval JSON next to the output HTML")
    parser.add_argument("--eval-out", help="Optional path for the single-deck eval JSON report")
    parser.add_argument("--packet-out", help="Optional path to write the render packet as JSON")
    args = parser.parse_args()

    try:
        if args.context_file:
            brief, html_text, packet, _style_contract = render_from_context_path(args.context_file)
        else:
            if not args.brief:
                parser.error("Either a BRIEF path or --context-file is required")
            brief = load_brief(args.brief)
            html_text, packet, _style_contract = render_from_brief(brief)
    except (BriefExtractionError, BriefValidationError) as exc:
        print(f"BRIEF ERROR: {exc}")
        return 1
    except RenderError as exc:
        print(f"RENDER ERROR: {exc}")
        return 1

    if not _has_canonical_provenance(html_text):
        print("PROVENANCE ERROR: canonical render markers missing; refusing to write output")
        return 1

    if not _strict_validate_rendered_html(html_text):
        print("VALIDATE ERROR: strict pre-write gate failed; refusing to write output")
        return 1

    output_path = Path(args.output)
    final_html = stamp_validation_status(html_text, status="pass")
    output_path.write_text(final_html, encoding="utf-8")

    if args.packet_out:
        packet_path = Path(args.packet_out)
        packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.extract_brief_out:
        brief_path = Path(args.extract_brief_out)
        brief_path.write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")

    eval_path = None
    if args.eval or args.eval_out:
        eval_path = Path(args.eval_out) if args.eval_out else default_eval_output_path(output_path)
        report = build_generation_eval_report(
            html_text=final_html,
            brief=brief,
            packet=packet,
            html_path=output_path,
        )
        write_generation_eval_report(eval_path, report)

    print(f"RENDERED: {output_path}")
    print(f"PRESET: {packet['preset']}")
    print(f"QUALITY TIER: {packet['quality_tier']}")
    print(f"RUNTIME PATH: {packet['runtime_path']}")
    if eval_path is not None:
        print(f"EVAL: {eval_path}")
        print(f"STYLE SCORE: {report['summary']['style_score']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
