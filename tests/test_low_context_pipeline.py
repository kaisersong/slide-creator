from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from low_context import (  # noqa: E402
    _chart_metric_values_from_spec,
    _balance_title_lines,
    _compact_display_token,
    _has_collapsed_middle_line,
    _is_orphan_title_line,
    _skill_version,
    _title_visual_units,
    BriefExtractionError,
    build_render_packet,
    build_slide_spec,
    compile_style_contract,
    extract_brief_from_context,
    extract_brief_from_source_text,
    load_brief,
    render_from_brief,
    RenderError,
)
from quality_eval import analyze_html_quality  # noqa: E402


VALIDATE_BRIEF = SCRIPTS / "validate-brief.py"
RENDER_FROM_BRIEF = SCRIPTS / "render-from-brief.py"
STRICT_VALIDATE = ROOT / "tests" / "validate.py"
AUTO_DEMO = ROOT / "demos" / "mode-paths" / "auto-BRIEF.json"
POLISH_DEMO = ROOT / "demos" / "mode-paths" / "polish-BRIEF.json"
DATA_STORY_CASE = ROOT / "evals" / "preset-surface-phase1" / "cases" / "core-data-story-brief.json"
WORK_HUB_SWISS = ROOT / "plans" / "ai-native-work-hub-v2-swiss-modern-BRIEF.json"
WORK_HUB_ENTERPRISE = ROOT / "plans" / "ai-native-work-hub-v2-enterprise-dark-BRIEF.json"
WORK_HUB_DATA_STORY = ROOT / "plans" / "ai-native-work-hub-v2-data-story-BRIEF.json"
ORG_PHASE_CHANGE_SWISS = ROOT / "plans" / "org-phase-change-ai-native-org-swiss-modern-BRIEF.json"
BLUE_SKY_DEMO = ROOT / "demos" / "blue-sky-zh.html"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def test_validate_brief_cli_rejects_polish_without_polish_controls(tmp_path: Path):
    brief = read_json(POLISH_DEMO)
    brief.pop("polish_controls")
    path = tmp_path / "invalid-polish.json"
    write_json(path, brief)

    result = subprocess.run(
        [sys.executable, str(VALIDATE_BRIEF), str(path)],
        capture_output=True,
        text=True,
        timeout=15,
    )

    assert result.returncode == 1
    assert "polish_controls is required" in result.stdout


def test_extract_brief_from_noisy_context_preserves_render_packet():
    brief_text = POLISH_DEMO.read_text(encoding="utf-8")

    clean = f"```json\n{brief_text}\n```"
    noisy = (
        "Earlier we discussed unrelated rollout details, budget noise, and style debate.\n\n"
        "Keep the render boundary hard. Only this artifact should drive the deck.\n\n"
        f"```json\n{brief_text}\n```\n\n"
        "Ignore everything else."
    )

    direct_brief = extract_brief_from_context(clean)
    noisy_brief = extract_brief_from_context(noisy)

    assert direct_brief == noisy_brief

    direct_packet = build_render_packet(direct_brief)
    noisy_packet = build_render_packet(noisy_brief)

    assert direct_packet == noisy_packet
    assert direct_packet["runtime_path"] == "shared-js-engine"
    assert direct_packet["composition_source"] == "references/composition-guide.md"


def test_extract_brief_from_conflicting_context_fails_closed():
    auto_text = AUTO_DEMO.read_text(encoding="utf-8")
    polish_text = POLISH_DEMO.read_text(encoding="utf-8")
    context = (
        "These two artifacts conflict. Do not guess.\n\n"
        f"```json\n{auto_text}\n```\n\n"
        f"```json\n{polish_text}\n```"
    )

    try:
        extract_brief_from_context(context)
    except BriefExtractionError as exc:
        assert "Multiple conflicting BRIEF artifacts" in str(exc)
    else:
        raise AssertionError("expected conflicting BRIEF extraction to fail closed")


def test_extract_brief_from_messages_json_source():
    brief_text = POLISH_DEMO.read_text(encoding="utf-8")
    source = json.dumps(
        {
            "messages": [
                {"role": "user", "content": "Ignore the noise."},
                {"role": "user", "content": f"```json\n{brief_text}\n```"},
            ]
        },
        ensure_ascii=False,
    )

    extracted = extract_brief_from_source_text(source)
    assert extracted == read_json(POLISH_DEMO)


def test_compile_style_contract_swiss_modern_collects_canonical_export_contract():
    contract = compile_style_contract("Swiss Modern")

    assert contract["preset"] == "Swiss Modern"
    assert contract["source_path"] == "references/swiss-modern.md"
    assert "--bg" in contract["tokens"]
    assert "--red" in contract["tokens"]
    assert "title_grid" in contract["allowed_layout_ids"]
    assert "geometric_diagram" in contract["allowed_layout_ids"]
    assert ".bg-num" in contract["required_signature_classes"]
    assert ".left-panel" in contract["required_signature_classes"]
    assert "--bg-primary" in contract["forbidden_aliases"]


def test_compile_style_contract_glassmorphism_collects_orb_background_layers():
    contract = compile_style_contract("Glassmorphism")

    assert contract["preset"] == "Glassmorphism"
    assert contract["source_path"] == "references/glassmorphism.md"
    assert "--glass-bg" in contract["tokens"]
    assert "glass_hero" in contract["allowed_layout_ids"]
    assert ".glass-card" in contract["required_signature_classes"]
    assert ".orb-1" in contract["required_signature_classes"]
    assert ".glass-orb" in contract["required_background_layers"]


def test_compile_style_contract_chinese_chan_collects_layout_roles_and_h2_component():
    contract = compile_style_contract("Chinese Chan")

    assert contract["preset"] == "Chinese Chan"
    assert contract["source_path"] == "references/chinese-chan.md"
    assert "zen_center" in contract["allowed_layout_ids"]
    assert "zen_stat" in contract["allowed_layout_ids"]
    assert ".zen-h2" in contract["required_signature_classes"]


def test_build_render_packet_blue_sky_uses_starter_path():
    brief = load_brief(AUTO_DEMO)
    packet = build_render_packet(brief)

    assert packet["preset"] == "Blue Sky"
    assert packet["preset_support_tier"] == "production"
    assert packet["runtime_path"] == "blue-sky-starter"
    assert "references/blue-sky-starter.html" in packet["required_refs"]
    assert "blue-sky-architecture" in packet["required_contracts"]


def test_render_chinese_chan_from_brief_uses_canonical_roles_and_content_headlines():
    brief = read_json(AUTO_DEMO)
    brief["title"] = "人生的意义"
    brief["language"] = "zh-CN"
    brief["style"]["preset"] = "Chinese Chan"
    brief["style"]["tone"] = "Still"
    brief["style"]["visual_density"] = "low"
    brief["deck"]["page_count"] = 8
    roles = ["cover", "problem", "discovery", "solution", "evidence", "driver", "checkpoint", "closing"]
    titles = [
        "人生的意义",
        "我们为何会追问意义",
        "意义不会从外界自动掉下来",
        "真正的答案来自向内寻找",
        "不同的人会在不同关系里找到意义",
        "意义感通常来自三个锚点",
        "如果只想不做，意义感会继续流失",
        "人生的意义，是你活出来的答案",
    ]
    points = [
        "在有限生命里，找到值得投入、值得珍惜、值得承担的方向。",
        "当外部标准失效时，人会开始追问自己真正想成为什么样的人。",
        "意义不是统一模板，而是由选择、体验和责任一点点塑造出来。",
        "向内看的过程，不是逃离现实，而是重新校准行动与价值的关系。",
        "有人在亲密关系里找到意义，有人在创造、照顾和探索里找到意义。",
        "热爱、联结、利他，通常是意义感最稳定的三个来源。",
        "哪怕从一件小事开始实践，意义也会比抽象思辨更快变得具体。",
        "没有标准答案，但每一步认真活过的路都会留下答案。",
    ]
    facts = [
        ["向内", "觉察", "诚实"],
        ["外部标准", "存在感", "价值感"],
        ["选择", "体验", "责任"],
        ["校准行动", "对齐价值", "承认本心"],
        ["亲密关系", "创造", "照顾他人"],
        ["热爱", "联结", "利他"],
        ["小步实践", "日常行动", "持续记录"],
        ["活出来", "每一步", "答案"],
    ]
    slides = []
    for index, role in enumerate(roles, start=1):
        slides.append(
            {
                "slide_number": index,
                "role": role,
                "title": titles[index - 1],
                "key_point": points[index - 1],
                "visual": "narrow contemplative column",
                "claim": titles[index - 1],
                "explanation": points[index - 1],
                "preferred_layout_family": "stat" if role == "driver" else ("close" if role == "closing" else ("hero" if role in {"cover", "solution"} else "evidence")),
                "chart_policy": "avoid",
                "supporting_facts": facts[index - 1],
            }
        )
    brief["narrative"]["page_roles"] = roles
    brief["narrative"]["slides"] = slides

    html, packet, _ = render_from_brief(brief)
    soup = BeautifulSoup(html, "html.parser")

    assert packet["preset"] == "Chinese Chan"
    assert packet["runtime_path"] == "shared-js-engine"
    assert [slide.get("data-export-role") for slide in soup.select("section.slide")] == [
        "zen_center", "zen_split", "zen_split", "zen_center",
        "zen_split", "zen_stat", "zen_split", "zen_vertical",
    ]
    split_slide = soup.select('section.slide[data-export-role="zen_split"]')[0]
    stat_slide = soup.select_one('section.slide[data-export-role="zen_stat"]')
    vertical_slide = soup.select_one('section.slide[data-export-role="zen_vertical"]')
    assert split_slide.select_one(".zen-h2") is not None
    assert split_slide.select_one(".zen-title") is None
    assert stat_slide.select_one(".zen-h2") is not None
    assert vertical_slide.select_one(".zen-vertical-title") is not None


def test_render_chinese_chan_stat_slide_uses_numeric_fact_units_and_action_labels():
    brief = read_json(AUTO_DEMO)
    brief["title"] = "意义行动"
    brief["language"] = "zh-CN"
    brief["style"]["preset"] = "Chinese Chan"
    brief["style"]["tone"] = "Still"
    brief["style"]["visual_density"] = "low"
    brief["deck"]["page_count"] = 5
    brief["narrative"]["page_roles"] = ["cover", "problem", "driver", "summary", "closing"]
    brief["narrative"]["slides"] = [
        {
            "slide_number": 1,
            "role": "cover",
            "title": "意义行动",
            "key_point": "从一件小事开始。",
            "visual": "centered contemplative title",
        },
        {
            "slide_number": 2,
            "role": "problem",
            "title": "为什么总觉得还没开始",
            "key_point": "意义感最怕被一直推迟。",
            "visual": "quiet split layout",
        },
        {
            "slide_number": 3,
            "role": "driver",
            "title": "现在，你可以从这三件小事开始",
            "key_point": "意义感最怕被无限推迟，真正有效的起点通常都很小。",
            "visual": "restrained stat row",
            "claim": "把意义落地的最好方法，是立刻开始一件足够小、但足够真实的行动。",
            "explanation": "今晚写下让你开心的小事，这周完成一件拖延的小事，给重要的人发一句问候。",
            "visual_intent": "three-action stat anchor",
            "preferred_layout_family": "stat",
            "chart_policy": "avoid",
            "supporting_facts": [
                "10分钟：写下最近让你开心的小事",
                "1件：完成一直想做但没做的小事",
                "1句：给重要的人发出一句问候",
            ],
            "numeric_facts": ["10分钟", "1件", "1句"],
        },
        {
            "slide_number": 4,
            "role": "summary",
            "title": "小事会把抽象意义拉回现实",
            "key_point": "行动比空想更快生成意义。",
            "visual": "quiet split layout",
        },
        {
            "slide_number": 5,
            "role": "closing",
            "title": "意义，是你活出来的答案",
            "key_point": "探索本身，就是意义的一部分。",
            "visual": "vertical title close",
        },
    ]

    html, _, _ = render_from_brief(brief)
    soup = BeautifulSoup(html, "html.parser")
    stat_slide = soup.select_one('section.slide[data-export-role="zen_stat"]')
    assert stat_slide is not None
    nums = [node.get_text(strip=True) for node in stat_slide.select(".zen-stat .num")]
    labels = [node.get_text(strip=True) for node in stat_slide.select(".zen-stat .label")]
    assert nums == ["10分钟", "1件", "1句"]
    assert labels == [
        "写下最近让你开心的小事",
        "完成一直想做但没做的小事",
        "给重要的人发出一句问候",
    ]


def test_sparse_brief_degrades_to_tier2_and_uses_canonical_slide_spec():
    brief = read_json(AUTO_DEMO)
    brief["style"]["preset"] = "Swiss Modern"
    brief["style"]["tone"] = "Minimal"
    brief["style"]["visual_density"] = "low"
    brief["title"] = "Sparse deck"
    brief["content"]["must_include"] = ["agent control"]
    brief["content"]["must_avoid"] = ["noise"]
    brief["narrative"]["thesis"] = "Agent control matters."
    for slide in brief["narrative"]["slides"]:
        slide["key_point"] = "Control first"
        slide["visual"] = "grid"

    packet = build_render_packet(brief)
    specs = build_slide_spec(brief, packet)

    assert packet["quality_tier"] == "tier2"
    assert packet["fallback_policy"] == "deterministic-scaffolds-before-fail"
    assert all(spec["quality_tier"] == "tier2" for spec in specs)
    assert all(len(spec["supporting_items"]) == 1 for spec in specs)
    assert all(spec["layout_id"] in {"title_grid", "column_content", "contents_index", "pull_quote"} for spec in specs)


def test_balance_title_lines_produces_no_orphans_or_collapsed_middle_line():
    lines = _balance_title_lines("越早把 AI 做成内核, 越早锁定下一轮壁垒")

    assert 2 <= len(lines) <= 3
    assert not any(_is_orphan_title_line(line) for line in lines)
    assert not _has_collapsed_middle_line([_title_visual_units(line) for line in lines])


def test_balance_title_lines_force_balance_rescues_cjk_statement_orphan():
    lines = _balance_title_lines("这轮数据已经足够支持谨慎扩面", force_balance=True)

    assert len(lines) == 2
    assert not any(_is_orphan_title_line(line) for line in lines)
    assert abs(_title_visual_units(lines[0]) - _title_visual_units(lines[1])) <= 1.0


def test_compact_display_token_avoids_dangling_negation_and_generic_ai_prefix():
    assert _compact_display_token("流体化不是新的组织架构图，而是组织新增的特性") == "流体化"
    assert _compact_display_token("AI 改变组织不是渐进优化，而是相变") == "相变"


def test_render_data_story_cta_close_uses_balanced_title_markup():
    brief = read_json(DATA_STORY_CASE)

    html, packet, _ = render_from_brief(brief)

    assert packet["preset"] == "Data Story"
    assert 'class="ds-heading reveal title-balance"' in html
    assert "这轮数据已经足" in html
    assert "够支持谨慎扩面" in html


def test_render_from_brief_cli_outputs_strict_valid_swiss_html(tmp_path: Path):
    brief = read_json(POLISH_DEMO)
    brief["style"]["preset"] = "Swiss Modern"
    brief["style"]["tone"] = "Precise, assertive, structured"
    brief["title"] = "Visible Control Wins"
    brief["language"] = "en"
    brief["audience"] = "Engineering and product leaders"
    brief["desired_action"] = "Adopt visible-control collaboration patterns"
    brief["narrative"]["thesis"] = "Visible control makes team-grade agent collaboration trustworthy."
    for slide in brief["narrative"]["slides"]:
        slide["visual"] = "structured swiss modern evidence layout"

    brief_path = tmp_path / "swiss-brief.json"
    output_path = tmp_path / "swiss-output.html"
    packet_path = tmp_path / "packet.json"
    write_json(brief_path, brief)

    render = subprocess.run(
        [
            sys.executable,
            str(RENDER_FROM_BRIEF),
            str(brief_path),
            "--output",
            str(output_path),
            "--packet-out",
            str(packet_path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert render.returncode == 0, render.stdout + render.stderr
    assert output_path.exists()
    packet = read_json(packet_path)
    assert packet["preset"] == "Swiss Modern"
    assert packet["preset_support_tier"] == "production"
    assert packet["runtime_path"] == "shared-js-engine"
    assert packet["quality_tier"] == "tier0"

    validate = subprocess.run(
        [sys.executable, str(STRICT_VALIDATE), str(output_path), "--strict"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert validate.returncode == 0, validate.stdout + validate.stderr
    assert "All strict checks passed" in validate.stdout


def test_render_cli_keeps_file_backed_and_context_extracted_outputs_identical(tmp_path: Path):
    brief = read_json(POLISH_DEMO)
    brief["style"]["preset"] = "Swiss Modern"
    brief["style"]["tone"] = "Precise, assertive, structured"
    brief["title"] = "Visible Control Wins"
    brief["language"] = "en"
    brief["audience"] = "Engineering and product leaders"
    brief["desired_action"] = "Adopt visible-control collaboration patterns"
    brief["narrative"]["thesis"] = "Visible control makes team-grade agent collaboration trustworthy."
    for slide in brief["narrative"]["slides"]:
        slide["visual"] = "structured swiss modern evidence layout"

    brief_path = tmp_path / "source-brief.json"
    direct_html = tmp_path / "direct.html"
    context_html = tmp_path / "context.html"
    direct_packet = tmp_path / "direct-packet.json"
    context_packet = tmp_path / "context-packet.json"
    extracted_brief = tmp_path / "extracted-brief.json"
    context_file = tmp_path / "context.json"
    write_json(brief_path, brief)
    context_file.write_text(
        json.dumps(
            {
                "messages": [
                    {"role": "user", "content": "We discussed many noisy org details first."},
                    {"role": "user", "content": f"```json\n{json.dumps(brief, ensure_ascii=False, indent=2)}\n```"},
                ]
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    direct = subprocess.run(
        [
            sys.executable,
            str(RENDER_FROM_BRIEF),
            str(brief_path),
            "--output",
            str(direct_html),
            "--packet-out",
            str(direct_packet),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    extracted = subprocess.run(
        [
            sys.executable,
            str(RENDER_FROM_BRIEF),
            "--context-file",
            str(context_file),
            "--extract-brief-out",
            str(extracted_brief),
            "--output",
            str(context_html),
            "--packet-out",
            str(context_packet),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert direct.returncode == 0, direct.stdout + direct.stderr
    assert extracted.returncode == 0, extracted.stdout + extracted.stderr
    assert direct_html.read_text(encoding="utf-8") == context_html.read_text(encoding="utf-8")
    assert read_json(direct_packet) == read_json(context_packet)
    assert read_json(extracted_brief) == brief


def test_render_cli_context_without_valid_brief_fails_closed(tmp_path: Path):
    context_file = tmp_path / "bad-context.txt"
    context_file.write_text("This is noisy context with no parseable BRIEF artifact.", encoding="utf-8")
    output_path = tmp_path / "bad.html"

    result = subprocess.run(
        [
            sys.executable,
            str(RENDER_FROM_BRIEF),
            "--context-file",
            str(context_file),
            "--output",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 1
    assert "BRIEF ERROR" in result.stdout
    assert not output_path.exists()


def test_enterprise_dark_render_hides_editing_chrome_by_default():
    brief = read_json(POLISH_DEMO)
    brief["style"]["preset"] = "Enterprise Dark"
    brief["style"]["tone"] = "Strategic"
    brief["title"] = "AI Native Operating System"
    brief["language"] = "zh-CN"
    brief["audience"] = "内部管理与产研团队"
    brief["desired_action"] = "对齐 AI 原生产研转型路径"
    brief["narrative"]["thesis"] = "AI 原生组织要先重写工作系统，而不是只给每个人多一个工具。"

    html_text, _packet, _style_contract = render_from_brief(brief)
    report = analyze_html_quality(html_text, brief=brief, preset="Enterprise Dark")

    assert "#notes-panel {" in html_text
    assert "display: none;" in html_text.split("#notes-panel {", 1)[1].split("}", 1)[0]
    assert "#notes-panel.active { display: block; }" in html_text
    assert "setActiveSlide(index)" in html_text
    assert "querySelectorAll('.reveal').forEach(function(r) { r.classList.toggle('visible', active); });" in html_text
    assert report["diagnostics"]["chrome_leak"] is False
    assert report["quality_gates"]["chrome-hidden-by-default"] is True


def test_enterprise_dark_narrative_cover_uses_story_cards_instead_of_fake_kpi_trends():
    brief = read_json(POLISH_DEMO)
    brief["style"]["preset"] = "Enterprise Dark"
    brief["style"]["tone"] = "Strategic"
    brief["title"] = "AI Native Operating System"
    brief["language"] = "zh-CN"
    brief["audience"] = "内部管理与产研团队"
    brief["desired_action"] = "对齐 AI 原生产研转型路径"
    brief["narrative"]["thesis"] = "AI 原生组织要先重写工作系统，而不是只给每个人多一个工具。"

    brief["narrative"]["slides"][0]["title"] = "AI 原生组织不是工具升级，而是工作系统重写"
    brief["narrative"]["slides"][0]["key_point"] = "把需求、设计、研发、测试和发布改成人与智能体协作默认流"
    brief["narrative"]["slides"][0]["visual"] = "operating model overview"

    brief["narrative"]["slides"][1]["title"] = "深度使用决定组织差距"
    brief["narrative"]["slides"][1]["key_point"] = "试点心态会把团队锁在效率下游"
    brief["narrative"]["slides"][1]["visual"] = "gap framing"

    brief["narrative"]["slides"][2]["title"] = "集团方向必须翻译成产研动作"
    brief["narrative"]["slides"][2]["key_point"] = "战略要求只有落到日常流程才会变成真实能力"
    brief["narrative"]["slides"][2]["visual"] = "strategy map"

    brief["narrative"]["slides"][3]["title"] = "工作流要先重写再谈提效"
    brief["narrative"]["slides"][3]["key_point"] = "先探索、再规划、后执行、最后验证才能形成闭环"
    brief["narrative"]["slides"][3]["visual"] = "workflow loop"

    html_text, _packet, _style_contract = render_from_brief(brief)
    first_slide = html_text.split('<section class="slide enterprise-dashboard', 1)[1].split("</section>", 1)[0]

    assert "ent-dashboard-story" in html_text
    assert "ent-kpi-card-story" in first_slide
    assert "深度使用决定组织差距" in first_slide
    assert "集团方向必须翻译成产研动作" in first_slide
    assert "工作流要先重写再谈提效" in first_slide
    assert "▲" not in first_slide
    assert "▼" not in first_slide


def test_enterprise_dark_runtime_replaces_watermark_placeholders_and_hides_brand_mark():
    brief = read_json(POLISH_DEMO)
    brief["style"]["preset"] = "Enterprise Dark"
    brief["title"] = "AI原生组织转型指南"
    brief["language"] = "zh-CN"

    html_text, _packet, _style_contract = render_from_brief(brief)

    assert f"By kai-slide-creator v{_skill_version()} · Enterprise Dark" in html_text
    assert "[version]" not in html_text
    assert "[preset-name]" not in html_text
    assert "#brand-mark {" in html_text
    assert "display: none;" in html_text.split("#brand-mark {")[-1].split("}", 1)[0]
    assert "scroll-snap-stop: always;" in html_text
    assert "overscroll-behavior-y: contain;" in html_text
    assert "addEventListener('wheel'" in html_text
    assert "addEventListener('scroll'" in html_text
    assert "wState = 'animating'" in html_text
    assert "wLastTime" in html_text


def test_enterprise_dark_split_structure_and_layout_rhythm_match_preset_better():
    brief = read_json(ROOT / "plans" / "ai-native-org-transformation-guide-brief.json")

    html_text, _packet, _style_contract = render_from_brief(brief)

    assert 'class="ent-split-labels slide-content"' not in html_text
    assert 'class="ent-split-panel"' in html_text
    assert 'grid-template-columns: clamp(380px, 38%, 470px) minmax(0, 1fr);' in html_text
    assert 'font-size: clamp(19px, 2.1vw, 28px);' in html_text
    assert 'body[data-preset="Enterprise Dark"]::before {' in html_text
    assert 'opacity: 0.09;' in html_text
    assert 'opacity: 0.05;' in html_text
    assert 'enterprise-feature-grid-slide' in html_text
    assert 'class="ent-feature-grid"' in html_text
    assert 'id="slide-11"' in html_text
    slide_10 = html_text.split('<section class="slide enterprise-timeline" id="slide-10"', 1)[1].split("</section>", 1)[0]
    slide_11 = html_text.split('<section class="slide enterprise-table" id="slide-11"', 1)[1].split("</section>", 1)[0]
    assert 'data-export-role="timeline"' in slide_10
    assert 'data-export-role="data_table"' in slide_11


def _max_run(values: list[str]) -> int:
    longest = 0
    current = 0
    previous = None
    for value in values:
        if value == previous:
            current += 1
        else:
            previous = value
            current = 1
        longest = max(longest, current)
    return longest


def test_work_hub_production_presets_keep_style_signal_without_placeholder_leaks():
    cases = [
        ("Swiss Modern", WORK_HUB_SWISS, 0.70),
        ("Enterprise Dark", WORK_HUB_ENTERPRISE, 0.60),
        ("Data Story", WORK_HUB_DATA_STORY, 0.45),
    ]
    generic_needles = [
        "Alpha",
        "Beta",
        "Input",
        "Freeze",
        "Output",
        "before after comparison",
        "risk ladder",
        "validated archetypes",
        "reference archetypes",
        "shared trajectory",
    ]

    for preset, brief_path, min_signature in cases:
        brief = read_json(brief_path)
        html_text, _packet, _style_contract = render_from_brief(brief)
        report = analyze_html_quality(html_text, brief=brief, preset=preset)
        soup = BeautifulSoup(html_text, "html.parser")
        visible_text = soup.get_text(" ", strip=True)
        export_roles = [section.get("data-export-role") for section in soup.select("section.slide[data-export-role]")]

        assert report["hard_failures"] == []
        assert all(report["quality_gates"].values())
        assert report["diagnostics"]["style_signature_coverage"] >= min_signature
        assert _max_run(export_roles) == 1
        for needle in generic_needles:
            assert needle not in visible_text


def test_production_presets_do_not_leak_chinese_chan_signatures():
    cases = [
        ("Swiss Modern", WORK_HUB_SWISS),
        ("Enterprise Dark", WORK_HUB_ENTERPRISE),
        ("Data Story", WORK_HUB_DATA_STORY),
        ("Blue Sky", BLUE_SKY_DEMO),
    ]

    for preset, brief_path in cases:
        if brief_path.suffix == ".json":
            brief = read_json(brief_path)
            if brief["style"]["preset"] != preset:
                brief["style"]["preset"] = preset
            html_text, _packet, _style_contract = render_from_brief(brief)
        else:
            html_text = brief_path.read_text(encoding="utf-8")

        assert f'data-preset="{preset}"' in html_text
        assert "zen-ghost-kanji" not in html_text
        assert 'data-export-role="zen_' not in html_text
        assert '"Noto Serif SC"' not in html_text


def test_org_phase_change_production_presets_avoid_generic_or_truncated_anchor_tokens():
    source_brief = read_json(ORG_PHASE_CHANGE_SWISS)
    cases = [
        ("Swiss Modern", ".hero-stat-num", 3),
        ("Enterprise Dark", ".ent-kpi-number", 0),
        ("Data Story", ".ds-kpi", 1),
    ]

    for preset, selector, expected_count in cases:
        brief = json.loads(json.dumps(source_brief, ensure_ascii=False))
        brief["style"]["preset"] = preset
        html_text, _packet, _style_contract = render_from_brief(brief)
        soup = BeautifulSoup(html_text, "html.parser")
        values = [node.get_text(" ", strip=True) for node in soup.select(selector)]
        visible_text = soup.get_text(" ", strip=True)

        assert 'class="swiss-stat accent">流体化不<' not in html_text
        assert 'class="hero-stat-num">AI<' not in html_text
        assert 'class="ent-kpi-number positive">AI<' not in html_text
        assert 'class="ent-kpi-number neutral">AI<' not in html_text
        assert 'class="ds-kpi positive reveal">AI<' not in html_text
        if preset == "Swiss Modern":
            assert 'class="swiss-stat accent">流体化<' in html_text
        if expected_count:
            assert len(values) >= expected_count
        if expected_count > 1:
            assert len(set(values[:expected_count])) == expected_count, (preset, values)
        assert all(value != "AI" for value in values[: max(expected_count, len(values))]), (preset, values)


def test_shared_shell_nav_dots_are_preset_driven_and_swiss_chrome_is_positioned():
    swiss_brief = read_json(ORG_PHASE_CHANGE_SWISS)
    swiss_html, _packet, _style_contract = render_from_brief(swiss_brief)

    assert ".nav-dots button.active {" in swiss_html
    assert "--nav-dot-idle: rgba(10, 10, 10, 0.18);" in swiss_html
    assert "--nav-dot-active: var(--red);" in swiss_html
    assert ".bg-num {" in swiss_html
    assert ".slide-num-label {" in swiss_html
    assert "dot.classList.toggle('active', active);" in swiss_html
    assert "rgba(255,255,255,0.3)" not in swiss_html
    assert "dot.style.background = i === this.currentSlide ? 'var(--accent)'" not in swiss_html

    data_story_brief = read_json(WORK_HUB_DATA_STORY)
    data_story_html, _packet, _style_contract = render_from_brief(data_story_brief)

    assert "--nav-dot-idle: rgba(15, 23, 42, 0.22);" in data_story_html
    assert "--nav-dot-active: var(--chart-primary, #2563eb);" in data_story_html


def test_data_story_work_hub_falls_back_to_stage_grids_when_numbers_are_not_slide_local():
    brief = read_json(WORK_HUB_DATA_STORY)
    packet = build_render_packet(brief)
    specs = build_slide_spec(brief, packet)
    by_role = {spec["role"]: spec for spec in specs}

    assert _chart_metric_values_from_spec(by_role["driver"], ["1", "2", "3", "4"]) == []
    assert _chart_metric_values_from_spec(by_role["metrics"], ["1", "2", "3"]) == []
    assert by_role["risk"]["layout_id"] == "chart_insight"

    html_text, _packet, _style_contract = render_from_brief(brief)
    soup = BeautifulSoup(html_text, "html.parser")
    driver_slide = soup.select_one('section.slide[aria-label="driver"]')
    risk_slide = soup.select_one('section.slide[aria-label="risk"]')
    metrics_slide = soup.select_one('section.slide[aria-label="metrics"]')

    assert driver_slide is not None
    assert risk_slide is not None
    assert metrics_slide is not None
    assert 'aria-label="line chart"' not in str(driver_slide)
    assert 'class="ds-stage-grid"' in str(driver_slide)
    assert 'data-export-role="chart_insight"' in str(risk_slide)
    assert 'class="ds-stage-grid"' in str(risk_slide)
    assert 'aria-label="bar chart"' not in str(metrics_slide)
    assert 'class="ds-stage-grid"' in str(metrics_slide)


def test_validate_brief_accepts_richer_low_context_v2_fields():
    brief = read_json(BRIEF_TEMPLATE_JSON := ROOT / "references" / "brief-template.json")
    first_slide = brief["narrative"]["slides"][0]

    assert first_slide["claim"]
    assert first_slide["explanation"]
    assert first_slide["visual_intent"]
    assert first_slide["preferred_layout_family"]
    assert "global_facts" in brief["content"]
    assert "optional_support" in brief["content"]

    errors = load_brief(BRIEF_TEMPLATE_JSON)
    assert errors["schema_version"] == 1


def test_data_story_chart_policy_required_fails_closed_without_slide_local_numeric_facts():
    brief = read_json(WORK_HUB_DATA_STORY)
    slide = brief["narrative"]["slides"][8]
    slide["chart_policy"] = "required"
    slide["preferred_layout_family"] = "chart"
    slide.pop("numeric_facts", None)
    slide.pop("supporting_facts", None)
    slide["claim"] = "三个今天必须完成的动作，比更多新功能更关键"
    slide["explanation"] = "统一入口协议、建设 Workspace 底层、推动模块归位，是当前最该先做的动作。"
    slide["visual_intent"] = "bar chart with three action blocks"

    try:
        render_from_brief(brief)
    except RenderError as exc:
        assert "lacks slide-local numeric facts" in str(exc)
    else:
        raise AssertionError("expected chart_policy required to fail closed without local numeric facts")
