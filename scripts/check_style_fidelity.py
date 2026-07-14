#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from bs4 import BeautifulSoup

from preset_capabilities import canonical_preset_name
from preset_contracts import builtin_preset_names, slug_for_preset, validate_preset_fidelity


def _preset_from_html_or_path(html_text: str, path: Path) -> str:
    soup = BeautifulSoup(html_text, "html.parser")
    body = soup.find("body")
    if body and str(body.get("data-preset", "")).strip():
        try:
            return canonical_preset_name(str(body["data-preset"]).strip())
        except KeyError:
            pass
    stem = path.stem.rsplit("-", 1)[0] if path.stem.endswith(("-en", "-zh")) else path.stem
    for preset in builtin_preset_names():
        canonical_slug = slug_for_preset(preset)
        if canonical_slug == stem or canonical_slug.removesuffix("-deck") == stem:
            return preset
    raise ValueError(f"Cannot infer preset for {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run canonical preset style fidelity validation")
    parser.add_argument("html")
    parser.add_argument("--preset")
    parser.add_argument("--mode", choices=("product", "reference"), default="reference")
    args = parser.parse_args()
    path = Path(args.html)
    html_text = path.read_text(encoding="utf-8")
    preset = args.preset or _preset_from_html_or_path(html_text, path)
    report = validate_preset_fidelity(html_text, preset, mode=args.mode)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
