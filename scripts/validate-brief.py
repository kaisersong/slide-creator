#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from low_context import validate_brief_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a slide-creator BRIEF.json artifact.")
    parser.add_argument("brief", help="Path to the BRIEF.json file")
    args = parser.parse_args()

    source = Path(args.brief)
    is_valid, errors, _ = validate_brief_path(source)
    if is_valid:
        print(f"VALID: {source.name}")
        return 0

    print(f"INVALID: {source.name}")
    for error in errors:
        print(f"- {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
