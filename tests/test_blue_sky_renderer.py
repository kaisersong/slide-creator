from __future__ import annotations

import copy
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from low_context import build_render_packet, build_slide_spec, render_from_brief
from validate_html import validate


AUTO_BRIEF = ROOT / "demos" / "mode-paths" / "auto-BRIEF.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _strict_validate_html(html: str) -> bool:
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as handle:
        handle.write(html)
        path = Path(handle.name)
    try:
        return validate(path, strict=True)
    finally:
        path.unlink(missing_ok=True)


def _openai_like_blue_sky_brief() -> dict:
    brief = copy.deepcopy(_load_json(AUTO_BRIEF))
    brief["brief_id"] = "test-openai-like-blue-sky"
    brief["title"] = "从模型到生态"
    brief["deck"]["deck_type"] = "user-content"
    brief["deck"]["page_count"] = 12
    brief["narrative"]["page_roles"] = [
        "cover",
        "problem",
        "discovery",
        "solution",
        "features",
        "comparison",
        "dual",
        "process",
        "checkpoint",
        "recommendation",
        "evidence",
        "closing",
    ]
    slides = []
    for index, role in enumerate(brief["narrative"]["page_roles"], start=1):
        slides.append(
            {
                "slide_number": index,
                "role": role,
                "title": {
                    "cover": "从模型到生态",
                    "problem": "2024的瓶颈",
                    "discovery": "四线突破",
                    "solution": "推理模型",
                    "features": "代码：1M上下文 + 终端Agent",
                    "comparison": "代码能力",
                    "dual": "互补路径",
                    "process": "Agent双引擎",
                    "checkpoint": "多模态",
                    "recommendation": "产品时间线",
                    "evidence": "开发者影响",
                    "closing": "关键指标",
                }[role],
                "key_point": f"{role} 页面推进同一条叙事，不依赖模板重复。",
                "visual": {
                    "cover": "hero statement with stat row",
                    "problem": "comparison cards",
                    "discovery": "4 quadrant grid",
                    "solution": "chapter divider",
                    "features": "bento cards",
                    "comparison": "two column comparison",
                    "dual": "two column comparison",
                    "process": "workflow layers",
                    "checkpoint": "timeline",
                    "recommendation": "grid recommendation cards",
                    "evidence": "data table",
                    "closing": "closing CTA",
                }[role],
                "supporting_facts": [
                    f"{role} fact 1",
                    f"{role} fact 2",
                    f"{role} fact 3",
                    f"{role} fact 4",
                ],
            }
        )
    brief["narrative"]["slides"] = slides
    return brief


def test_blue_sky_auto_demo_resolves_varied_layouts():
    brief = _load_json(AUTO_BRIEF)
    packet = build_render_packet(brief)
    specs = build_slide_spec(brief, packet=packet)
    layouts_by_role = {spec["role"]: spec["layout_id"] for spec in specs}
    layouts = list(layouts_by_role.values())

    assert layouts_by_role["workflow"] == "workflow"
    assert layouts_by_role["style-discovery"] == "bento"
    assert layouts_by_role["output-contract"] == "table"
    assert layouts_by_role["best-fit"] == "bento"
    assert layouts_by_role["closing"] == "closing"
    assert len(set(layouts)) >= 5
    assert max(Counter(layouts).values()) <= 2


def test_blue_sky_auto_demo_strict_validates():
    brief = _load_json(AUTO_BRIEF)
    html = render_from_brief(brief)[0]

    assert _strict_validate_html(html)


def test_blue_sky_generated_html_injects_current_watermark():
    brief = _load_json(AUTO_BRIEF)
    html = render_from_brief(brief)[0]

    assert "slides[slides.length - 1]" in html
    assert "slide-credit" in html
    assert "By kai-slide-creator v" in html
    assert "· Blue Sky" in html


def test_blue_sky_canonical_twelve_role_brief_strict_validates():
    brief = _openai_like_blue_sky_brief()
    html = render_from_brief(brief)[0]

    assert _strict_validate_html(html)
