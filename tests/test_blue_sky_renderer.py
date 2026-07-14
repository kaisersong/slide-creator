from __future__ import annotations

import copy
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from low_context import build_render_packet, build_slide_spec, render_from_brief
from validate_html import check_blue_sky_signature_contract, validate


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


def test_blue_sky_starter_defines_mobile_grid_constraints():
    starter = (ROOT / "references" / "blue-sky-starter.html").read_text(encoding="utf-8")

    assert "@media (max-width: 720px)" in starter
    assert ".cols2, .cols3, .cols4" in starter
    assert "grid-template-columns: repeat(2, minmax(0, 1fr));" in starter
    assert ".cols2 > *, .cols3 > *, .cols4 > *, .bento > *" in starter
    assert "min-width: 0;" in starter


def test_blue_sky_signature_contract_accepts_native_renderer_output():
    brief = _load_json(AUTO_BRIEF)
    html = render_from_brief(brief)[0]
    soup = BeautifulSoup(html, "html.parser")

    passed, message = check_blue_sky_signature_contract(soup, html, [])

    assert passed, message


def test_blue_sky_signature_contract_rejects_static_shell_without_demo_motion():
    html = """
    <html>
    <head>
      <style>
        body::before { content: ""; background: #eaf6ff; }
        body::after { content: ""; background: #ffffff; }
        .slide { height: 100vh; overflow: hidden; }
        .orb { position: absolute; width: 200px; height: 200px; }
        .pill { display: inline-block; padding: 4px 12px; }
        .gt { font-size: 6rem; }
      </style>
    </head>
    <body data-preset="Blue Sky">
      <div class="orb" id="orb1"></div>
      <div class="orb" id="orb2"></div>
      <div class="orb" id="orb3"></div>
      <div id="stage">
        <div id="track">
          <section class="slide hero-clean" data-export-role="cover">
            <span class="pill">2026 MID-YEAR MEETING</span>
            <h1 class="gt">闭幕辞</h1>
          </section>
          <section class="slide thank-you-slide" data-export-role="closing">
            <h2 class="gt">谢谢</h2>
          </section>
        </div>
      </div>
    </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    passed, message = check_blue_sky_signature_contract(soup, html, [])

    assert not passed
    assert "style-selector-group-missing" in message
    assert "style-signature-coverage-low" in message


def test_blue_sky_signature_contract_rejects_sparse_cloud_only_shell():
    html = """
    <html>
    <head>
      <style>
        body::before { content: ""; background: #eaf6ff; }
        body::after { content: ""; background: #ffffff; }
        .slide { height: 100vh; overflow: hidden; }
        .orb { position: absolute; width: 200px; height: 200px; }
        .pill { display: inline-block; padding: 4px 12px; }
        .gt { font-size: 6rem; }
        .g { border: 1px solid rgba(255,255,255,.9); }
        .stat { font-size: 2.8rem; }
        .cloud-layer { position: absolute; bottom: 0; left: 0; width: 100%; height: 75%; }
        .cloud-strip { position: absolute; bottom: 0; left: 0; display: flex; height: 100%; }
        .cloud-group { position: absolute; bottom: 0; }
        .cloud-puff { position: absolute; background: white; border-radius: 50%; }
      </style>
    </head>
    <body data-preset="Blue Sky">
      <div class="orb" id="orb1"></div>
      <div class="orb" id="orb2"></div>
      <div class="orb" id="orb3"></div>
      <section class="slide cover" data-export-role="cover">
        <div class="cloud-layer"><div class="cloud-strip"><div class="cloud-group"><div class="cloud-puff"> </div></div></div></div>
        <span class="pill">Meeting</span>
        <h1 class="gt">Closing</h1>
        <div class="g"><div class="stat">2030</div></div>
      </section>
    </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    passed, message = check_blue_sky_signature_contract(soup, html, [])

    assert not passed
    assert "style-selector-group-missing" in message


def test_blue_sky_keeps_medium_cjk_titles_on_one_line():
    brief = _openai_like_blue_sky_brief()
    brief["narrative"]["slides"][1]["title"] = "我们正站在一个『背水一战』的时刻"
    brief["narrative"]["slides"][2]["title"] = "哲学 7.0 的升级：把『辩证性』写进客户哲学"
    brief["narrative"]["slides"][3]["title"] = "生态哲学升级:智能共生，不走邪道"
    brief["narrative"]["slides"][4]["title"] = "落地路线从低风险真实场景开始，而不是先追求 L5"

    html = render_from_brief(brief)[0]

    assert '<h2 class="gt reveal title-nowrap">我们正站在一个『背水一战』的时刻</h2>' in html
    assert '<h2 class="gt reveal title-nowrap">哲学 7.0 的升级：把『辩证性』写进客户哲学</h2>' in html
    assert '<h2 class="gt reveal title-nowrap">生态哲学升级:智能共生，不走邪道</h2>' in html
    assert '<h2 class="gt reveal title-nowrap">落地路线从低风险真实场景开始，而不是先追求 L5</h2>' in html


def test_blue_sky_canonical_twelve_role_brief_strict_validates():
    brief = _openai_like_blue_sky_brief()
    html = render_from_brief(brief)[0]

    assert _strict_validate_html(html)
