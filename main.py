#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from low_context import (  # noqa: E402
    BriefExtractionError,
    BriefValidationError,
    RenderError,
    load_brief,
    render_from_brief,
    render_from_context_path,
    validate_brief_path,
)


PLAN_HELP = """\
PLAN STEP REQUIRES SKILL INVOCATION

`/slide-creator --plan` is a Claude/OpenClaw slash-skill step, not a raw bash/python command.

In a bare sandbox:
1. Read `references/brief-template.json`
2. Write `BRIEF.json` yourself (or extract one valid BRIEF from context)
3. Run `python3 main.py --validate-brief --brief BRIEF.json`
4. Run `python3 main.py --generate --brief BRIEF.json --output presentation.html`
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sandbox-friendly CLI for slide-creator BRIEF validation and deterministic rendering."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--plan",
        nargs="*",
        metavar="PROMPT",
        help="Explain the planning-step fallback in a raw sandbox",
    )
    mode.add_argument(
        "--generate",
        action="store_true",
        help="Render HTML from BRIEF.json or a context artifact",
    )
    mode.add_argument(
        "--validate-brief",
        action="store_true",
        help="Validate a BRIEF.json artifact",
    )
    parser.add_argument("--brief", help="Path to BRIEF.json (defaults to ./BRIEF.json)")
    parser.add_argument("--context-file", help="Path to a context artifact containing exactly one valid BRIEF")
    parser.add_argument("--output", help="Output HTML path for --generate")
    parser.add_argument("--packet-out", help="Optional path to write the render packet as JSON")
    parser.add_argument("--extract-brief-out", help="Optional path to write the extracted BRIEF as JSON")
    return parser


def _default_brief_path(value: str | None) -> Path:
    return Path(value) if value else Path("BRIEF.json")


def run_plan(prompt_parts: list[str] | None) -> int:
    print(PLAN_HELP)
    if prompt_parts:
        print("PROMPT:")
        print(" ".join(prompt_parts))
    return 2


def run_validate_brief(brief_path: Path) -> int:
    is_valid, errors, _brief = validate_brief_path(brief_path)
    if is_valid:
        print(f"VALID: {brief_path.name}")
        return 0

    print(f"INVALID: {brief_path.name}")
    for error in errors:
        print(f"- {error}")
    return 1


def run_generate(
    *,
    brief_path: Path | None,
    context_file: str | None,
    output: Path,
    packet_out: str | None,
    extract_brief_out: str | None,
) -> int:
    try:
        if context_file:
            brief, html_text, packet, _style_contract = render_from_context_path(context_file)
        else:
            if brief_path is None:
                raise BriefValidationError("A BRIEF path or --context-file is required")
            brief = load_brief(brief_path)
            html_text, packet, _style_contract = render_from_brief(brief)
    except (BriefExtractionError, BriefValidationError) as exc:
        print(f"BRIEF ERROR: {exc}")
        return 1
    except RenderError as exc:
        print(f"RENDER ERROR: {exc}")
        return 1

    output.write_text(html_text, encoding="utf-8")

    if packet_out:
        Path(packet_out).write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")

    if extract_brief_out:
        Path(extract_brief_out).write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"RENDERED: {output}")
    print(f"PRESET: {packet['preset']}")
    print(f"QUALITY TIER: {packet['quality_tier']}")
    print(f"RUNTIME PATH: {packet['runtime_path']}")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.plan is not None:
        return run_plan(args.plan)

    brief_path = _default_brief_path(args.brief)

    if args.validate_brief:
        return run_validate_brief(brief_path)

    if args.generate:
        if not args.output:
            parser.error("--output is required with --generate")
        return run_generate(
            brief_path=None if args.context_file else brief_path,
            context_file=args.context_file,
            output=Path(args.output),
            packet_out=args.packet_out,
            extract_brief_out=args.extract_brief_out,
        )

    parser.error("One of --plan / --generate / --validate-brief is required")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
