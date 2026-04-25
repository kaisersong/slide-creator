#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from low_context import (
    BriefExtractionError,
    BriefValidationError,
    RenderError,
    load_brief,
    render_from_brief,
    render_from_context_path,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a deterministic low-context deck from BRIEF.json.")
    parser.add_argument("brief", nargs="?", help="Path to BRIEF.json")
    parser.add_argument("--context-file", help="Path to a context artifact that must contain exactly one valid BRIEF")
    parser.add_argument("--extract-brief-out", help="Optional path to write the extracted BRIEF as JSON")
    parser.add_argument("--output", required=True, help="Output HTML path")
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

    output_path = Path(args.output)
    output_path.write_text(html_text, encoding="utf-8")

    if args.packet_out:
        packet_path = Path(args.packet_out)
        packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.extract_brief_out:
        brief_path = Path(args.extract_brief_out)
        brief_path.write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"RENDERED: {output_path}")
    print(f"PRESET: {packet['preset']}")
    print(f"QUALITY TIER: {packet['quality_tier']}")
    print(f"RUNTIME PATH: {packet['runtime_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
