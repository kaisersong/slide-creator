#!/usr/bin/env python3
"""Extract the CSS and content templates required by installed profile renderers."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup
from preset_profile_renderer import DEMO_SLUG_BY_PRESET

ROOT = Path(__file__).resolve().parent.parent


def extract(source: Path) -> str:
    soup = BeautifulSoup(source.read_text(encoding="utf-8"), "html.parser")
    sections = soup.select("section.slide")
    if not sections:
        raise ValueError(f"No slide templates in {source}")
    imports = [str(link) for link in soup.find_all("link")
               if "fonts.googleapis.com" in str(link.get("href", ""))]
    styles = [str(style) for style in soup.find_all("style")]
    return "\n".join([
        "<!DOCTYPE html>",
        '<!-- Program-owned profile template. Regenerate with scripts/build-profile-templates.py. -->',
        "<html><head>", *imports, *styles, "</head><body>",
        *[str(section) for section in sections], "</body></html>", "",
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check tracked assets without writing")
    args = parser.parse_args()
    target_dir = ROOT / "references" / "profile-templates"
    if not args.check:
        target_dir.mkdir(parents=True, exist_ok=True)
    failures = []
    manifest = {"version": 1, "presets": {}}
    for preset, slug in DEMO_SLUG_BY_PRESET.items():
        manifest["presets"][preset] = {}
        for language in ("en", "zh"):
            name = f"{slug}-{language}.html"
            if preset == "Strategy Consulting":
                reference = (ROOT / "references/strategy-consulting.md").read_text(encoding="utf-8")
                canvas_css = re.search(r"```css\n(/\* Strategy Consulting canvas contract \*/.*?)```", reference, re.S).group(1)
                demo = ROOT / "demos" / name
                original = demo.read_text(encoding="utf-8")
                updated = re.sub(r'\n<style id="consulting-canvas">.*?</style>\n', '\n', original, flags=re.S)
                updated = re.sub(r'<div class="reveal" style="display:grid;grid-template-columns:repeat\(3,1fr\);[^"]*">',
                                 '<div class="reveal sc-evidence-row">', updated)
                updated = updated.replace("</head>", '<style id="consulting-canvas">\n' + canvas_css + '</style>\n</head>', 1)
                if args.check:
                    if original != updated:
                        failures.append("demos/" + name)
                else:
                    demo.write_text(updated, encoding="utf-8")
            rendered = extract(ROOT / "demos" / name)
            target = target_dir / name
            manifest["presets"][preset][language] = {
                "path": str(target.relative_to(ROOT)),
                "sha256": hashlib.sha256(rendered.encode("utf-8")).hexdigest(),
            }
            if args.check:
                if not target.exists() or target.read_text(encoding="utf-8") != rendered:
                    failures.append(name)
            else:
                target.write_text(rendered, encoding="utf-8")
    manifest_path = target_dir / "manifest.json"
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not manifest_path.exists() or manifest_path.read_text(encoding="utf-8") != manifest_text:
            failures.append("manifest.json")
    else:
        manifest_path.write_text(manifest_text, encoding="utf-8")
    if failures:
        print("Profile templates differ: " + ", ".join(failures))
        return 1
    print(f"{'Verified' if args.check else 'Built'} {len(DEMO_SLUG_BY_PRESET) * 2} runtime profile templates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
