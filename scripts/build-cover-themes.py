#!/usr/bin/env python3
"""Embed the shared cover controller and shader sources in offline custom starters."""
from __future__ import annotations

import argparse
import base64
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEMES = {
    "molten-flow": {
        "name": "Molten Flow", "title": "熔金流体", "label": "MOLTEN", "period": 30, "focalX": 76,
        "resolutionScale": 1, "night": "#160C0A", "paper": "#F9F2E5", "ink": "#321D17",
        "muted": "#70544A", "teal": "#A3421E", "light": "#FFE5B9", "amber": "#FFCA70", "rule": "#DDCFC1",
        "headline": "让想法<br>释放<em>锋芒</em>", "lede": "金色流体翻涌，让开场自带气场。",
    },
    "stellar-vortex": {
        "name": "Stellar Vortex", "title": "星核跃迁", "label": "STELLAR", "period": 144, "focalX": 74.5,
        "resolutionScale": 1, "night": "#080A20", "paper": "#F2F3FB", "ink": "#20233F",
        "muted": "#565B78", "teal": "#4F48B5", "light": "#CED5FF", "amber": "#80E4FF", "rule": "#CDD0E4",
        "headline": "向未知出发<br>向<em>未来跃迁</em>", "lede": "穿过粒子光场，看见新的可能。",
    },
}


def build(name: str) -> Path:
    settings = THEMES[name]
    directory = ROOT / "themes" / name
    source = (ROOT / "themes/shader-hero/starter.html").read_text()
    css = re.search(r"<style>(.*?)</style>", source, re.S).group(1)
    for token in ("night", "paper", "ink", "muted", "teal", "light", "amber", "rule"):
        css = re.sub(rf"(--sh-{token}:)#[0-9A-Fa-f]+", lambda m: m[1] + settings[token], css)
    css = css.replace("#shader-hero-canvas", "#cover-effect-canvas")
    css = css.replace("body { background-color: #081B23; }", f"body {{ background-color: {settings['night']}; }}")
    css = css.replace('data-shader-ready="true"', 'data-cover-effect-ready="true"')
    poster = directory / "cover.webp"
    background = settings["night"]
    if poster.exists():
        background = f'url("data:image/webp;base64,{base64.b64encode(poster.read_bytes()).decode()}")'
    css = re.sub(r"\.sh-cover-field \{[^}]+\}",
        '.sh-cover-field { position:absolute; inset:0; z-index:-2; background:' + background
        + f'; background-size:cover; background-position:{settings["focalX"]}% center; }}', css, count=1)
    css = css.replace("rgba(8,27,35,", "rgba(16,12,20,")
    css = re.sub(r"\.sh-scene--cover::before \{[^}]+\}",
        '.sh-scene--cover::before { content:""; position:absolute; inset:0; z-index:-1; '
        'background:linear-gradient(90deg,rgba(16,12,20,.96),rgba(16,12,20,.8) 42%,rgba(16,12,20,.38) 58%,rgba(16,12,20,0) 74%); }', css, count=1)
    css += "\n.sh-scene--cover .sh-headline { max-width:1000px; }\n.sh-scene--cover .sh-details { max-width:740px; }\n"
    fragment = (directory / "effect.frag").read_text()
    definition = {k: settings[k] for k in ("name", "period", "resolutionScale")}
    definition["fragment"] = fragment
    runtime = (ROOT / "references/cover-effects-runtime.js").read_text()
    html = f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{settings['title']}</title><style>{css}</style></head>
<body>
<template id="theme-decor"><canvas id="cover-effect-canvas" aria-hidden="true" hidden></canvas><nav class="nav-dots" aria-label="Slide navigation"></nav><div class="progress-bar" aria-hidden="true"></div></template>
<section class="slide sh-scene sh-scene--cover visible" id="slide-1"><div class="sh-cover-field" aria-hidden="true"></div><div class="sh-copy"><span class="sh-label">{settings['label']} / OPENING</span><h1 class="sh-headline">{settings['headline']}</h1><p class="sh-lede">{settings['lede']}</p></div></section>
<script>document.querySelector('#theme-decor').after(document.querySelector('#theme-decor').content.cloneNode(true));</script>
<script data-theme-runtime>
window.__coverEffectDefinition = {json.dumps(definition, ensure_ascii=False, indent=2)};
// BEGIN SHARED COVER RUNTIME
{runtime}// END SHARED COVER RUNTIME
</script></body></html>
'''
    target = directory / "starter.html"
    target.write_text(html)
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("themes", nargs="*", help="Theme names (defaults to both new themes)")
    args = parser.parse_args()
    if any(name not in THEMES for name in args.themes):
        parser.error("Available themes: " + ", ".join(THEMES))
    for name in args.themes or THEMES:
        print(build(name).relative_to(ROOT))
