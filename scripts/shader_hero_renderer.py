"""Content rendering for the opt-in Shader Hero theme; animation is cover-only."""

from __future__ import annotations

import html
import re
from typing import Any


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _title(spec: dict[str, Any]) -> str:
    text = str(spec.get("title", ""))
    emphasis = str(spec.get("title_emphasis") or "")
    lines = []
    for line in text.splitlines() or [text]:
        rendered = _escape(line)
        if emphasis and emphasis in line:
            before, after = line.split(emphasis, 1)
            rendered = f"{_escape(before)}<em>{_escape(emphasis)}</em>{_escape(after)}"
        lines.append(f'<span class="title-line sh-title-line">{rendered}</span>')
    return "".join(lines)


def render_shader_hero_slide(spec: dict[str, Any], total: int, *, role_index: int, theme: str = "shader-hero") -> str:
    number = spec["slide_number"]
    role = str(spec["role"])
    layout = re.sub(r"[^a-zA-Z0-9_-]", "-", str(spec["layout_id"]))
    cover = role_index == 0
    closing = not cover and (role in {"cta", "closing"} or layout == "cta_close")
    family = str(spec.get("preferred_layout_family") or "").lower()
    if cover:
        layout = "title_grid"
    elif closing:
        layout = "cta_close"
    else:
        # Custom themes own their compositions, as Fantasy Rainbow does. Interpret
        # caller intent here rather than inheriting the generic custom-theme route.
        families = {
            "comparison": "column_content", "split": "column_content",
            "diagram": "geometric_diagram", "workflow": "geometric_diagram", "flow": "geometric_diagram",
            "index": "contents_index", "list": "contents_index",
            "quote": "pull_quote", "statement": "pull_quote",
        }
        cycle = ("column_content", "geometric_diagram", "contents_index", "pull_quote")
        layout = families.get(family, cycle[(role_index - 1) % len(cycle)])
    scene = "cover" if cover else "closing" if closing else "content"
    items = list(spec.get("supporting_facts") or spec.get("supporting_items") or [])
    # Keep all local facts, including ones with numeric evidence, in editable DOM.
    facts = "".join(
        f'<li class="sh-fact"><span class="sh-index" aria-hidden="true">{i:02d}</span>'
        f'<span>{_escape(item)}</span></li>'
        for i, item in enumerate(items, 1)
    )
    evidence = "".join(
        f'<p class="sh-evidence">{_escape(item)}</p>'
        for item in spec.get("evidence_items", [])
        if not any(str(item) in str(fact) for fact in items)
    )
    tag = "h1" if cover else "h2"
    title = f'<{tag} class="sh-headline">{_title(spec)}</{tag}>'
    name = {"shader-hero": "AURORA", "molten-flow": "MOLTEN", "stellar-vortex": "STELLAR"}[theme]
    label = f"{name} / OPENING" if cover else f"{name} / FINISH" if closing else f"{name} / IDEAS"
    lede = f'<p class="sh-lede">{_escape(spec.get("key_point", ""))}</p>'
    background = '<div class="sh-cover-field" aria-hidden="true"></div>' if cover else ""
    if layout == "pull_quote" and not cover and not closing:
        title = f'<blockquote class="sh-quote">{title}</blockquote>'
    return (
        f'<section class="slide sh-scene sh-scene--{scene} layout-{layout}" '
        f'id="slide-{number}" data-notes="{_escape(spec["speaker_note"])}" '
        f'aria-label="{_escape(spec["title"])}" data-export-role="{layout}">'
        f'{background}<div class="sh-copy"><span class="sh-label">{label}</span>'
        f'{title}{lede}</div><div class="sh-details"><ul class="sh-facts">{facts}</ul>{evidence}</div>'
        f'<span class="slide-num-label">{number:02d} / {total:02d}</span></section>'
    )
