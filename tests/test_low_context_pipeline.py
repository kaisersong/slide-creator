from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import low_context as low_context_module  # noqa: E402
from low_context import (  # noqa: E402
    _chart_labels_from_spec,
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
from browser_geometry_qa import analyze_browser_geometry_html  # noqa: E402
from quality_eval import analyze_html_quality  # noqa: E402


VALIDATE_BRIEF = SCRIPTS / "validate-brief.py"
RENDER_FROM_BRIEF = SCRIPTS / "render-from-brief.py"
STRICT_VALIDATE = ROOT / "tests" / "validate.py"
AUTO_DEMO = ROOT / "demos" / "mode-paths" / "auto-BRIEF.json"
POLISH_DEMO = ROOT / "demos" / "mode-paths" / "polish-BRIEF.json"
DATA_STORY_CASE = ROOT / "evals" / "preset-surface-phase1" / "cases" / "core-data-story-brief.json"
CORE_SWISS_BRIEF = ROOT / "evals" / "preset-surface-phase1" / "cases" / "core-swiss-modern-brief.json"
CORE_DATA_STORY_BRIEF = ROOT / "evals" / "preset-surface-phase1" / "cases" / "core-data-story-brief.json"
ENTERPRISE_INTENT_BRIEF = ROOT / "demos" / "mode-paths" / "intent-broker-auto-BRIEF.json"
BLUE_SKY_DEMO = ROOT / "demos" / "blue-sky-zh.html"
CORE_GEOMETRY_VIEWPORTS = [{"width": 1600, "height": 900}, {"width": 1280, "height": 720}]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_skill_version_supports_source_and_packaged_layouts(tmp_path: Path, monkeypatch):
    plugin_root = tmp_path / "plugin-layout"
    plugin_root.mkdir()
    (plugin_root / "plugin.json").write_text(
        json.dumps({"version": " 3.2.1 "}),
        encoding="utf-8",
    )

    nested_root = tmp_path / "nested-skill-layout"
    nested_skill = nested_root / "skills" / "slide-planner" / "SKILL.md"
    nested_skill.parent.mkdir(parents=True)
    nested_skill.write_text("---\nversion: 3.2.0\n---\n", encoding="utf-8")

    root_skill_root = tmp_path / "root-skill-layout"
    root_skill_root.mkdir()
    (root_skill_root / "SKILL.md").write_text(
        "---\nversion: 3.1.9\n---\n",
        encoding="utf-8",
    )

    invalid_plugin_root = tmp_path / "invalid-plugin-layout"
    invalid_plugin_nested_skill = invalid_plugin_root / "skills" / "slide-planner" / "SKILL.md"
    invalid_plugin_nested_skill.parent.mkdir(parents=True)
    (invalid_plugin_root / "plugin.json").write_text("{not-json", encoding="utf-8")
    invalid_plugin_nested_skill.write_text("---\nversion: 3.1.8\n---\n", encoding="utf-8")

    for candidate_root, expected in (
        (plugin_root, "3.2.1"),
        (nested_root, "3.2.0"),
        (root_skill_root, "3.1.9"),
        (invalid_plugin_root, "3.1.8"),
    ):
        monkeypatch.setattr(low_context_module, "ROOT", candidate_root)
        assert _skill_version() == expected


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _clone_json(data: dict) -> dict:
    return json.loads(json.dumps(data, ensure_ascii=False))


def _load_core_swiss_brief() -> dict:
    return _clone_json(read_json(CORE_SWISS_BRIEF))


def _load_core_data_story_brief() -> dict:
    return _clone_json(read_json(CORE_DATA_STORY_BRIEF))


def _make_enterprise_dark_rhythm_brief() -> dict:
    brief = _load_core_swiss_brief()
    brief["style"]["preset"] = "Enterprise Dark"
    brief["style"]["tone"] = "Strategic, deliberate, board-ready"
    brief["style"]["visual_density"] = "medium"
    brief["title"] = "AI Native Org Transformation"
    brief["language"] = "zh-CN"
    brief["audience"] = "管理层与产研负责人"
    brief["desired_action"] = "确认推进路径和首批动作"
    roles = [
        "cover",
        "problem",
        "baseline",
        "workflow",
        "discovery",
        "tradeoff",
        "feature",
        "evidence",
        "decision",
        "timeline",
        "checkpoint",
    ]
    titles = [
        "市场已经进入深度使用决定收益的阶段",
        "试点如果停在浅层试用，团队只会被锁死在效率补丁里",
        "公开趋势与组织差距需要被同时看到",
        "集团方向要求把 AI 变成企业管理入口",
        "组织底座必须补齐数据治理、评测和 champions",
        "转型不是多上工具，而是重排工作方式与控制点",
        "首批模块要围绕 Workspace、Agent 和治理闭环推进",
        "证据链要证明收益来自流程重构，而不是单点自动化",
        "这轮决策的关键是先压实首批试点，再复制稳定链路",
        "30-60-90 天推进节奏必须提前明确",
        "周会、月会和指标口径要同步纳入治理表",
    ]
    points = [
        "试错会把团队锁死在效率补丁里，深度复用才会带来组织收益。",
        "只会偶尔写提示词，不会形成可复用闭环。",
        "公开案例显示收益来自使用深度，而不是偶尔试一下。",
        "集团方向要求把 AI 做成企业管理入口，而不是外挂工具。",
        "没有数据治理、评测和 champions，执行会停在口号层。",
        "真正变化发生在工作流、治理节奏和责任归位。",
        "先做清晰模块，再拉通跨团队协同能力。",
        "收益要能被管理层看见，也能被产研团队复现。",
        "先复制高频稳定场景，再扩大覆盖范围。",
        "先压实 30 天动作，再完成 60 天协同，最后在 90 天固化机制。",
        "治理表是让推进从热情回到机制的关键。",
    ]
    facts = [
        ["公开趋势", "组织差距", "收益结构"],
        ["浅层试用", "效率补丁", "闭环缺失"],
        ["外部趋势", "组织差距", "基线判断"],
        ["管理入口", "企业级 AI", "统一工作台"],
        ["数据治理", "评测机制", "AI champions"],
        ["工作方式", "控制点", "角色迁移"],
        ["Workspace", "Agent", "治理闭环"],
        ["收益证据", "流程重构", "可复现"],
        ["首批试点", "复制链路", "避免稀释"],
        ["30 天", "60 天", "90 天"],
        ["周节奏", "月治理", "指标口径"],
    ]
    visuals = [
        "kpi dashboard",
        "consulting split",
        "insight pull",
        "consulting split",
        "architecture map",
        "comparison matrix",
        "feature grid",
        "evidence table",
        "closing signal",
        "timeline",
        "governance table",
    ]
    slides = []
    for index, role in enumerate(roles, start=1):
        slides.append(
            {
                "slide_number": index,
                "role": role,
                "title": titles[index - 1],
                "key_point": points[index - 1],
                "visual": visuals[index - 1],
                "claim": titles[index - 1],
                "explanation": points[index - 1],
                "supporting_facts": facts[index - 1],
            }
        )
    brief["deck"]["page_count"] = len(slides)
    brief["narrative"]["page_roles"] = roles
    brief["narrative"]["slides"] = slides
    return brief


def _make_slide_creator_intro_brief(*, preset: str) -> dict:
    brief = _make_enterprise_dark_rhythm_brief()
    brief["brief_id"] = f"slide-creator-intro-12p-{preset.lower().replace(' ', '-')}-regression"
    brief["style"]["preset"] = preset
    brief["style"]["tone"] = "清爽、产品化、可信"
    brief["title"] = "slide-creator: Stable AI Slide Generation"
    brief["audience"] = "评估 slide-creator 的产品经理、开发者、内容创作者"
    brief["desired_action"] = "理解 slide-creator 的核心价值并试跑第一个 deck"
    brief["content"]["must_include"] = [
        "IR-first workflow（BRIEF.json → HTML）",
        "零依赖 runtime（浏览器原生）",
        "22 design presets 与内容型路由",
        "Validate before trust（严格验证）",
        "Presenter Mode、Inline Editing、Play Mode",
    ]
    slide_data = [
        ("cover", "slide-creator", "AI 能生成幻灯片但质量不稳定，slide-creator 给你稳定、精致的输出", "22 种设计预设、零依赖运行、IR-first 工作流、内容型路由", "hero", ["22 种设计预设", "零依赖运行", "IR-first 工作流", "内容型路由"]),
        ("pain-solution", "AI Slide Generation 的痛点", "同一提示词每次结果都不同，反复重试让人疲惫", "质量不稳定、风格混乱、Context 压力、依赖外部工具、无验证、视觉密度失控", "comparison", ["质量不稳定", "风格混乱", "Context 压力", "无验证"]),
        ("solution", "slide-creator 解决方案", "通过 IR-first workflow、零依赖 runtime 和严格验证体系，解决 AI slide generation 的不稳定性问题", "BRIEF.json 作为硬真相源、单 HTML 文件浏览器原生、生成前严格验证", "three-things", ["IR-first Workflow", "零依赖 Runtime", "Validate Before Trust"]),
        ("features", "核心功能", "六个核心功能覆盖从规划、渲染、验证到交互和自定义", "prompt → BRIEF.json → HTML → validate → eval、22 design presets 每预设 8-12 种布局变体、Content-type routing、Zero-dependency runtime、16 checkpoints review、Custom themes", "feature-grid", ["IR-first Workflow — prompt → BRIEF.json → HTML → validate → eval", "22 Design Presets — 每预设 8-12 种布局变体", "Content-type Routing — 数据报告 → Data Story / Enterprise Dark，VC pitch → Bold Signal / Aurora Mesh，Dev tool → Terminal Green / Neon Cyber", "Zero-dependency — Viewport-fitted slides、Presenter Mode、Inline Editing、自包含 runtime", "Content Review — 16 checkpoints: 6 auto-detect + 10 AI-advised", "Custom Themes — themes/your-theme/reference.md + starter.html"]),
        ("workflow", "工作流", "五个阶段的确定性路径，从内容到 HTML deck 的稳定交付", "Phase 1 内容收集、Phase 2 BRIEF.json 生成、Phase 3 确定性渲染、Phase 3.5 Content Review、Phase 4 浏览器打开导出", "timeline", ["Phase 1 内容收集", "Phase 2 BRIEF.json", "Phase 3 渲染验证", "Phase 4 打开导出"]),
        ("design-philosophy", "设计哲学", "四个设计哲学保护最后一步，减轻 context 压力，避免视觉 slop", "Progressive Disclosure、Show Don't Tell、Against Slide Slop、Contract Alignment", "architecture-map", ["Progressive Disclosure", "Show Don't Tell", "Against Slide Slop", "Contract Alignment"]),
        ("presets", "设计预设", "22 design presets 按内容型分类，覆盖从 pitch deck 到数据报告到 dev tool 的所有场景", "企业级、创意类、开发者、数据/咨询、文艺/品牌、设计探索", "comparison-matrix", ["企业级", "创意类", "开发者", "数据/咨询", "文艺/品牌", "设计探索"]),
        ("content-routing", "内容型路由", "Content-type routing 自动推荐最佳风格，减少返工", "数据报告 → Data Story / Enterprise Dark / Swiss Modern、Business Pitch / VC Deck → Bold Signal / Aurora Mesh / Enterprise Dark、Developer Tool / API Docs → Terminal Green / Neon Cyber", "three-things", ["数据报告", "Business Pitch", "Developer Tool"]),
        ("validation", "验证体系", "四层验证体系确保从 IR 到运行时的契约一致性", "validate-brief.py 检查 BRIEF.json 契约、validate_html.py --strict 检查运行时契约、preset-usage-rules.json 定义路由规则、Captured-run Skill Evals 回归基线对比", "feature-grid", ["validate-brief.py", "validate_html.py --strict", "preset-usage-rules.json", "Captured-run Skill Evals"]),
        ("interaction", "交互特性", "四个交互特性让 HTML deck 成为真正的演示工具，而非一次性截图", "F5 全屏、P 键演讲窗口、默认浏览器编辑、E 键笔记栏", "feature-grid", ["F5 全屏", "P 键演讲窗口", "默认浏览器编辑", "E 键笔记栏"]),
        ("use-cases", "使用场景", "三种典型使用场景覆盖从零开始、复杂内容、PPT 转换", "Interactive Creation 从交互开始、IR-first Workflow 从 BRIEF 开始、PPT Conversion 从 .pptx 开始", "three-things", ["Interactive Creation", "IR-first Workflow", "PPT Conversion"]),
        ("cta_close", "开始使用", "两个平台一句话安装，文档和 demo 在线可访问", "Claude Code: Install、OpenClaw: clawhub install、文档链接、Demo 链接", "close", ['Claude Code: "Install https://github.com/kaisersong/slide-creator"', "OpenClaw: clawhub install kai-slide-creator", "文档: https://kaisersong.github.io/slide-creator/", "Demo: https://kaisersong.github.io/slide-creator/demos/blue-sky-zh.html"]),
    ]
    brief["deck"]["page_count"] = len(slide_data)
    brief["narrative"]["page_roles"] = [role for role, *_rest in slide_data]
    brief["narrative"]["slides"] = []
    for index, values in enumerate(slide_data, start=1):
        role, title, claim, explanation, family, facts = values
        brief["narrative"]["slides"].append(
            {
                "slide_number": index,
                "role": role,
                "title": title,
                "claim": claim,
                "key_point": explanation,
                "explanation": explanation,
                "visual": family,
                "visual_intent": family,
                "preferred_layout_family": family,
                "chart_policy": "auto",
                "supporting_facts": facts,
            }
        )
    return brief


def _make_anchor_regression_brief() -> dict:
    brief = _load_core_swiss_brief()
    brief["language"] = "zh-CN"
    brief["title"] = "组织的相变"
    brief["audience"] = "关注 AI 原生组织变革的管理者"
    brief["desired_action"] = "判断组织约束已经发生何种变化"
    brief["content"]["must_include"] = [
        "AI 同时改写信息处理成本",
        "AI 同时改写协同与控制成本",
        "AI 把竞争优势推向认知力与文化",
    ]
    roles = ["cover", "problem", "baseline", "workflow", "evidence", "tradeoff", "decision", "closing"]
    titles = [
        "组织竞争正在从资源规模转向认知力与文化",
        "当信息处理和协同成本同时下降，旧组织约束会被重写",
        "流体化不是新的组织架构图，而是组织新增的特性",
        "管理正在从结构设计转向维护高质量的认知场",
        "案例并不稀缺，真正稀缺的是把经验变成机制",
        "如果只把 AI 当工具，组织只会得到更快的旧流程",
        "下一阶段竞争力来自更高密度的判断与协同闭环",
        "先重写组织约束，再谈规模化复制",
    ]
    points = [
        "真正变化不是替代多少岗位，而是组织如何更快处理信息、协同判断并持续学习。",
        "过去依赖层级和流程兜住的事情，正在被新的判断密度取代。",
        "流体化意味着组织可以围绕任务快速重组，而不是彻底抛弃结构。",
        "结构仍然存在，但管理重点已经转向场的质量和节奏维护。",
        "公开案例说明变化已发生，但可复制能力仍然稀缺。",
        "把 AI 贴在旧流程上，只会得到更快的旧约束。",
        "新的复利点来自认知力、文化与闭环速度的叠加。",
        "组织必须先承认约束变化，才谈得上稳定复制。",
    ]
    slide_facts = [
        ["AI 改写信息处理成本", "AI 改写协同与控制成本", "AI 推动认知力成为核心竞争优势"],
        ["信息处理", "协同成本", "控制边界"],
        ["流体化", "任务重组", "新增特性"],
        ["结构设计", "认知场", "维护节奏"],
        ["公开案例", "机制化", "可复制"],
        ["更快旧流程", "局部提效", "组织锁死"],
        ["认知力", "文化", "闭环速度"],
        ["承认变化", "重写约束", "稳定复制"],
    ]
    slides = []
    for index, role in enumerate(roles, start=1):
        slides.append(
            {
                "slide_number": index,
                "role": role,
                "title": titles[index - 1],
                "key_point": points[index - 1],
                "visual": "structured evidence layout",
                "claim": titles[index - 1],
                "explanation": points[index - 1],
                "supporting_facts": slide_facts[index - 1],
            }
        )
    brief["deck"]["page_count"] = len(slides)
    brief["narrative"]["page_roles"] = roles
    brief["narrative"]["slides"] = slides
    return brief


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


def test_validate_brief_cli_accepts_reference_driven_preset(tmp_path: Path):
    brief = read_json(AUTO_DEMO)
    brief["style"]["preset"] = "Paper & Ink"
    path = tmp_path / "paper-ink-brief.json"
    write_json(path, brief)

    result = subprocess.run(
        [sys.executable, str(VALIDATE_BRIEF), str(path)],
        capture_output=True,
        text=True,
        timeout=15,
    )

    assert result.returncode == 0
    assert "VALID: paper-ink-brief.json" in result.stdout


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
    direct_brief["style"]["preset"] = "Data Story"
    noisy_brief["style"]["preset"] = "Data Story"

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


def test_balance_title_lines_preserves_cjk_words_and_quote_boundaries():
    assert _balance_title_lines("我们正站在一个『背水一战』的时刻", force_balance=True) == [
        "我们正站在一个",
        "『背水一战』的时刻",
    ]

    philosophy_lines = _balance_title_lines(
        "哲学 7.0 的升级：把『辩证性』写进客户哲学",
        force_balance=True,
    )
    philosophy_joined = "|".join(philosophy_lines)
    assert "升|级" not in philosophy_joined
    assert "『|" not in philosophy_joined
    assert not any(line.endswith("把") for line in philosophy_lines)

    ecology_lines = _balance_title_lines("生态哲学升级:智能共生，不走邪道", force_balance=True)
    ecology_joined = "|".join(ecology_lines)
    assert "智|能" not in ecology_joined
    assert "升级:|" in ecology_joined or "升级：|" in ecology_joined


def test_balance_title_lines_preserves_common_cjk_title_words():
    cases = {
        "AERAM 五级描述的是授权状态，不是企业优劣排名": ("状|态",),
        "落地路线从低风险真实场景开始，而不是先追求 L5": ("风|险",),
        "最终输出是一张授权地图，而不是一个宣传等级": ("地|图",),
        "SCOPE 把自治能力拆成五个必须同时过线的锚点": ("五|个",),
    }

    for title, forbidden_breaks in cases.items():
        joined = "|".join(_balance_title_lines(title, force_balance=True))

        for forbidden in forbidden_breaks:
            assert forbidden not in joined


def test_balance_title_lines_force_balance_rescues_cjk_statement_orphan():
    lines = _balance_title_lines("这轮数据已经足够支持谨慎扩面", force_balance=True)

    assert len(lines) == 2
    assert not any(_is_orphan_title_line(line) for line in lines)
    assert "足|够" not in "|".join(lines)
    assert abs(_title_visual_units(lines[0]) - _title_visual_units(lines[1])) <= 2.0


def test_compact_display_token_avoids_dangling_negation_and_generic_ai_prefix():
    assert _compact_display_token("流体化不是新的组织架构图，而是组织新增的特性") == "流体化"
    assert _compact_display_token("AI 改变组织不是渐进优化，而是相变") == "相变"


def test_render_data_story_cta_close_uses_balanced_title_markup():
    brief = read_json(DATA_STORY_CASE)

    html, packet, _ = render_from_brief(brief)

    assert packet["preset"] == "Data Story"
    assert 'class="ds-heading reveal title-balance"' in html
    assert '<span class="title-line">这轮数据已经足</span><span class="title-line">够支持谨慎扩面</span>' not in html


def test_enterprise_dark_split_titles_balance_before_browser_wrap_orphans():
    brief = read_json(ENTERPRISE_INTENT_BRIEF)

    html, packet, _ = render_from_brief(brief)
    soup = BeautifulSoup(html, "html.parser")
    split_titles = {
        title.get_text("", strip=True): title
        for title in soup.select(".enterprise-split .ent-title")
    }

    assert packet["preset"] == "Enterprise Dark"
    for text in ("现有协作方式缺少稳定任务语义", "Broker 只负责协议与可靠投递"):
        title = split_titles[text]
        assert "title-balance" in title.get("class", [])
        lines = [line.get_text("", strip=True) for line in title.select(".title-line")]
        assert len(lines) == 2
        assert not any(_is_orphan_title_line(line) for line in lines)
        assert not _has_collapsed_middle_line([_title_visual_units(line) for line in lines])


def test_data_story_cover_uses_title_as_primary_hero_not_metric():
    brief = _load_core_data_story_brief()
    brief["title"] = "slide-creator: Stable AI Slide Generation"
    cover = brief["narrative"]["slides"][0]
    cover.update(
        {
            "role": "cover",
            "title": "slide-creator",
            "key_point": "22 种设计预设、零依赖运行、IR-first 工作流、内容型路由",
            "claim": "slide-creator",
            "supporting_facts": ["22 种设计预设", "零依赖运行", "IR-first 工作流"],
            "numeric_facts": ["22 种设计预设"],
        }
    )

    html_text, _packet, _style_contract = render_from_brief(brief)
    soup = BeautifulSoup(html_text, "html.parser")
    cover_slide = soup.find(id="slide-1")
    heading = cover_slide.select_one(".ds-heading")
    kpi = cover_slide.select_one(".ds-kpi")
    label = cover_slide.select_one(".ds-kpi-label")
    summary = cover_slide.select_one(".ds-cover-summary")

    assert cover_slide.get("data-export-role") == "hero_number"
    assert heading is not None
    assert heading.get_text(" ", strip=True) == "slide-creator"
    assert heading.find_previous(class_="ds-kpi") is None
    assert kpi is not None
    assert kpi.get_text(" ", strip=True) == "22"
    assert label is not None
    assert label.get_text(" ", strip=True) == "22 种设计预设"
    assert summary is not None
    assert summary.get_text(" ", strip=True) == "零依赖运行、IR-first 工作流、内容型路由"
    assert ".ds-cover-metric" in html_text


def test_brand_mark_uses_complete_short_product_name_before_colon():
    from low_context import _brand_mark_text

    assert _brand_mark_text("slide-creator: Stable AI Slide Generation", "Data Story") == "slide-creator"


def test_data_story_kpi_grid_alias_resolves_to_compact_numeric_kpis():
    brief = _load_core_data_story_brief()
    slide = brief["narrative"]["slides"][2]
    brief["narrative"]["page_roles"][2] = "consumer-model"
    slide.update(
        {
            "role": "consumer-model",
            "title": "GPT-5.5 Instant 把默认体验推向更可靠的日常助手",
            "key_point": "OpenAI 将 ChatGPT 默认模型升级到 GPT-5.5 Instant，并强化个性化与 memory sources。",
            "claim": "默认模型升级的意义，是让更高可靠性直接进入每个普通 ChatGPT 会话。",
            "explanation": "官方称 GPT-5.5 Instant 面向所有 ChatGPT 用户滚动发布，并在 API 中以 chat-latest 提供。",
            "visual_intent": "three KPI cards with compact evidence",
            "preferred_layout_family": "kpi-grid",
            "chart_policy": "required",
            "supporting_facts": [
                "默认模型从 GPT-5.3 Instant 迁移到 GPT-5.5 Instant",
                "面向所有 ChatGPT 用户滚动发布",
                "Memory sources 帮助用户查看个性化响应使用了哪些上下文",
            ],
            "numeric_facts": [
                "52.5% fewer hallucinated claims on high-stakes prompts vs GPT-5.3 Instant",
                "37.3% fewer inaccurate claims on especially challenging flagged conversations",
                "3 months paid-user access window for GPT-5.3 Instant",
            ],
        }
    )

    specs = build_slide_spec(brief, packet=build_render_packet(brief))
    assert specs[2]["layout_id"] == "kpi_grid"

    html, packet, _ = render_from_brief(brief)
    soup = BeautifulSoup(html, "html.parser")
    rendered_slide = soup.find(id="slide-3")
    kpi_values = [node.get_text(" ", strip=True) for node in rendered_slide.select(".ds-kpi-card .ds-kpi")]

    assert packet["preset"] == "Data Story"
    assert kpi_values[:3] == ["52.5%", "37.3%", "3"]
    assert "默认模型</div>" not in str(rendered_slide)
    assert 'body[data-preset="Data Story"] .ds-kpi-chart .ds-split-layout' in html


def test_data_story_numeric_only_metric_never_returns_text_tokens():
    from low_context import _metric_value_for_item

    spec = {
        "title": "内容路由必须先让结构清晰",
        "claim": "数据报告不能被当成 KPI 数字",
        "key_point": "这页没有任何真实数字，视觉 KPI 只能降级为占位序号。",
        "visual_intent": "kpi grid",
        "supporting_items": ["数据报告", "模板选择", "字段路由"],
        "supporting_facts": ["数据报告", "模板选择", "字段路由"],
        "evidence_items": [],
        "numeric_facts": [],
    }

    value = _metric_value_for_item("数据报告", spec, index=0, numeric_only=True)

    assert value == "1"
    assert any(char.isdigit() for char in value)


def test_shared_runtime_keeps_slide_number_clear_of_present_button():
    brief = _load_core_data_story_brief()
    html, _packet, _ = render_from_brief(brief)

    present_block = re.search(r"#present-btn\s*\{(?P<body>.*?)\}", html, re.DOTALL)
    label_block = re.search(r"\.slide-num-label\s*\{(?P<body>.*?)\}", html, re.DOTALL)

    assert present_block is not None
    assert label_block is not None

    present_right = int(re.search(r"right:\s*(\d+)px", present_block.group("body")).group(1))
    present_width = int(re.search(r"width:\s*(\d+)px", present_block.group("body")).group(1))
    label_right = int(re.search(r"right:\s*(\d+)px", label_block.group("body")).group(1))

    assert label_right >= present_right + present_width + 12


def test_data_story_generated_text_role_falls_back_from_kpi_grid_without_numbers(tmp_path: Path):
    from validate_html import validate

    brief = _load_core_data_story_brief()
    brief["narrative"]["page_roles"][1] = "content-routing"
    slide = brief["narrative"]["slides"][1]
    slide.update(
        {
            "role": "content-routing",
            "title": "内容路由先保证信息结构清晰",
            "key_point": "这页只解释数据报告、模板选择和字段路由之间的关系，不提供数字证据。",
            "claim": "没有数字证据的内容路由页不应被强行渲染成 KPI 网格。",
            "explanation": "如果视觉上需要强调结构，应使用洞察卡片，而不是伪造数字感。",
            "visual_intent": "kpi grid",
            "preferred_layout_family": "kpi-grid",
            "chart_policy": "auto",
            "supporting_facts": ["数据报告", "模板选择", "字段路由"],
        }
    )
    slide.pop("numeric_facts", None)

    specs = build_slide_spec(brief, packet=build_render_packet(brief))
    assert specs[1]["layout_id"] == "chart_insight"

    html_text, _packet, _style_contract = render_from_brief(brief)
    output_path = tmp_path / "data-story-content-routing.html"
    output_path.write_text(html_text, encoding="utf-8")

    assert validate(output_path, strict=True)


def test_data_story_layout_run_avoidance_keeps_text_roles_out_of_hero_number():
    def build_brief_for_target_role(target_role: str) -> dict:
        brief = _load_core_data_story_brief()
        roles = [
            "cover",
            "design-philosophy",
            "validation",
            target_role,
            "interaction",
            "decision",
            "closing",
            "cta_close",
        ]
        titles = [
            "数据故事需要先建立上下文",
            "设计原则让模板选择更稳定",
            "校验链路保证输出可复查",
            "内容型路由",
            "交互状态让演示可被操作",
            "下一步聚焦四类核心场景",
            "输出已经可以进入复测",
            "开始生成第一版演示文稿",
        ]
        points = [
            "先说明目标用户和判断口径，再进入结构化演示。",
            "用信息密度、视觉语气和内容类型共同决定风格。",
            "生成前校验 brief，生成后检查版式合同和质量门禁。",
            "数据报告、商业路演、开发者文档会进入不同推荐路径。",
            "播放、导出、复测和修订状态需要保持一致。",
            "先覆盖数据报告、路演、开发者文档和展厅说明四类入口。",
            "复测结果显示关键版式已经具备稳定输出能力。",
            "按用户流程重新生成并记录产物路径。",
        ]
        facts = [
            ["目标用户", "判断口径", "结构化演示"],
            ["信息密度", "视觉语气", "内容类型"],
            ["brief 校验", "版式合同", "质量门禁"],
            ["数据报告", "商业路演", "开发者文档"],
            ["播放状态", "导出状态", "复测状态"],
            ["数据报告", "路演", "开发者文档"],
            ["版式稳定", "复测通过", "路径可追踪"],
            ["用户流程", "产物路径", "评分记录"],
        ]
        brief["narrative"]["page_roles"] = roles
        for slide, role, title, point, supporting_facts in zip(
            brief["narrative"]["slides"],
            roles,
            titles,
            points,
            facts,
            strict=True,
        ):
            slide.update(
                {
                    "role": role,
                    "title": title,
                    "claim": title,
                    "key_point": point,
                    "explanation": point,
                    "visual_intent": "structured content cards",
                    "chart_policy": "auto",
                    "supporting_facts": supporting_facts,
                }
            )
            slide.pop("preferred_layout_family", None)
            slide.pop("numeric_facts", None)
        return brief

    for target_role in ("content-routing", "use-cases"):
        brief = build_brief_for_target_role(target_role)
        specs = build_slide_spec(brief, packet=build_render_packet(brief))
        target_spec = next(spec for spec in specs if spec["role"] == target_role)

        assert target_spec["layout_id"] != "hero_number", (target_role, [spec["layout_id"] for spec in specs])

        html_text, _packet, _style_contract = render_from_brief(brief)
        soup = BeautifulSoup(html_text, "html.parser")
        rendered_slide = soup.find("section", attrs={"aria-label": target_role})

        assert rendered_slide is not None
        assert rendered_slide.get("data-export-role") != "hero_number"


def test_data_story_chart_policy_avoid_keeps_url_sources_as_evidence_cards():
    brief = _load_core_data_story_brief()
    slide = brief["narrative"]["slides"][-1]
    slide.update(
        {
            "role": "source-boundary",
            "title": "这份简报只使用 OpenAI 官方信息",
            "key_point": "事实边界截至 2026-05-17；后续发布需要重新核对官方页面。",
            "claim": "快速变化的产品线必须保留来源、日期和可用性边界。",
            "explanation": "本 deck 的判断来自 OpenAI product release pages 与 Help Center release notes。",
            "visual_intent": "source ledger grouped by product line",
            "preferred_layout_family": "evidence",
            "chart_policy": "avoid",
            "supporting_facts": [
                "Product releases: https://openai.com/news/product-releases/",
                "GPT-5.5 Instant: https://openai.com/index/gpt-5-5-instant/",
                "ChatGPT release notes: https://help.openai.com/en/articles/6825453-release-notes",
                "Enterprise release notes: https://help.openai.com/en/articles/10128477-chatgpt-enterprise-edu-release-notes",
            ],
            "numeric_facts": ["Checked on 2026-05-17"],
        }
    )
    brief["narrative"]["page_roles"][-1] = "source-boundary"

    specs = build_slide_spec(brief, packet=build_render_packet(brief))
    assert specs[-1]["layout_id"] == "chart_insight"
    assert specs[-1]["chart_policy"] == "avoid"

    html, _packet, _ = render_from_brief(brief)
    soup = BeautifulSoup(html, "html.parser")
    rendered_slide = soup.find(id=f"slide-{slide['slide_number']}")

    assert rendered_slide.find(class_="ds-stage-grid") is not None
    assert rendered_slide.find(class_="ds-chart-svg") is None
    assert "https://openai.com/news/product-releases/" in rendered_slide.get_text(" ")


def test_render_from_brief_emits_pending_canonical_provenance_markers():
    brief = read_json(POLISH_DEMO)
    brief["style"]["preset"] = "Enterprise Dark"
    brief["title"] = "Canonical Provenance"

    html, packet, _ = render_from_brief(brief)

    assert packet["render_path"] == "brief-canonical"
    assert packet["generator"] == "kai-slide-creator"
    assert 'data-generator="kai-slide-creator"' in html
    assert f'data-generator-version="{_skill_version()}"' in html
    assert 'data-render-path="brief-canonical"' in html
    assert f'data-brief-hash="{packet["brief_hash"]}"' in html
    assert f'data-runtime-path="{packet["runtime_path"]}"' in html
    assert 'data-validate-strict="pending"' in html


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
    rendered = output_path.read_text(encoding="utf-8")
    assert 'data-generator="kai-slide-creator"' in rendered
    assert 'data-render-path="brief-canonical"' in rendered
    assert 'data-validate-strict="pass"' in rendered

    validate = subprocess.run(
        [sys.executable, str(STRICT_VALIDATE), str(output_path), "--strict"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert validate.returncode == 0, validate.stdout + validate.stderr
    assert "All strict checks passed" in validate.stdout


def test_render_from_brief_cli_can_emit_single_deck_eval_report(tmp_path: Path):
    brief = read_json(POLISH_DEMO)
    brief["style"]["preset"] = "Enterprise Dark"
    brief["title"] = "Eval Report Contract"
    brief["audience"] = "Internal stakeholders"
    brief["desired_action"] = "Verify render-from-brief eval output"

    brief_path = tmp_path / "brief.json"
    output_path = tmp_path / "deck.html"
    write_json(brief_path, brief)

    render = subprocess.run(
        [
            sys.executable,
            str(RENDER_FROM_BRIEF),
            str(brief_path),
            "--output",
            str(output_path),
            "--eval",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    eval_path = tmp_path / "deck.eval.json"
    assert render.returncode == 0, render.stdout + render.stderr
    assert eval_path.exists()
    report = read_json(eval_path)
    assert report["preset"] == "Enterprise Dark"
    assert report["render_packet"]["runtime_path"] == "shared-js-engine"
    assert report["summary"]["style_score"] is not None
    assert "STYLE SCORE:" in render.stdout


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


def test_enterprise_dark_cover_uses_uniform_signal_cards_for_mixed_facts():
    from low_context import _render_enterprise_kpi_dashboard

    spec = {
        "slide_number": 1,
        "role": "cover",
        "layout_id": "kpi_dashboard",
        "title": "Slide Creator 展厅覆盖 22 种设计预设",
        "claim": "22 种设计预设",
        "key_point": "零依赖运行和 IR-first 工作流是能力说明，不是额外数字。",
        "visual": "kpi dashboard",
        "visual_intent": "kpi dashboard",
        "supporting_items": ["22 种设计预设", "零依赖运行", "IR-first 工作流"],
        "evidence_items": [],
        "supporting_facts": ["22 种设计预设", "零依赖运行", "IR-first 工作流"],
        "numeric_facts": [],
        "speaker_note": "cover",
    }

    html_text = _render_enterprise_kpi_dashboard(spec, total=3)
    soup = BeautifulSoup(html_text, "html.parser")
    cards = soup.select(".ent-cover-metric-row .ent-cover-metric-card")
    titles = [node.get_text(" ", strip=True) for node in soup.select(".ent-cover-metric-title")]
    inline_numbers = soup.select(".ent-cover-metric-title .ent-kpi-number")

    assert len(cards) == 3
    assert all("ent-kpi-card" in card.get("class", []) for card in cards)
    assert titles == ["22 种设计预设", "零依赖运行", "IR-first 工作流"]
    assert [node.get_text(" ", strip=True) for node in inline_numbers] == ["22"]
    assert all("ent-cover-inline-number" in node.get("class", []) for node in inline_numbers)


def test_enterprise_dark_cta_close_uses_text_cards_when_no_numeric_values_exist():
    from low_context import _render_enterprise_cta_close

    spec = {
        "slide_number": 12,
        "role": "cta_close",
        "layout_id": "cta_close",
        "title": "下一步先开放展厅样例",
        "claim": "开放展厅样例",
        "key_point": "让 ClaudeCode、OpenClaw 和文档共同进入验证闭环。",
        "visual": "cta",
        "visual_intent": "cta",
        "supporting_items": ["ClaudeCode", "OpenClaw", "文档"],
        "evidence_items": [],
        "supporting_facts": ["ClaudeCode", "OpenClaw", "文档"],
        "numeric_facts": [],
        "speaker_note": "close",
    }

    html_text = _render_enterprise_cta_close(spec, total=12)
    soup = BeautifulSoup(html_text, "html.parser")

    assert soup.select(".ent-kpi-number") == []
    assert "ClaudeCode" in soup.get_text(" ", strip=True)
    assert "OpenClaw" in soup.get_text(" ", strip=True)
    assert "文档" in soup.get_text(" ", strip=True)


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
    brief = _make_enterprise_dark_rhythm_brief()

    html_text, _packet, _style_contract = render_from_brief(brief)

    assert 'class="ent-split-labels slide-content"' not in html_text
    assert 'class="ent-split-panel"' in html_text
    assert 'grid-template-columns: clamp(380px, 38%, 470px) minmax(0, 1fr);' in html_text
    assert 'font-size: clamp(20px, 2.2vw, 30px);' in html_text
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


def _enterprise_rendered_component_families(slides) -> list[str]:
    families = []
    for slide in slides:
        if "ent-dashboard-story" in slide.get("class", []):
            families.append("story-dashboard")
        elif slide.select_one(".ent-cover-metric-row"):
            families.append("cover-dashboard")
        elif slide.select_one(".ent-contrast-split"):
            families.append("contrast")
        elif slide.select_one(".ent-feature-grid"):
            families.append("feature-grid")
        elif slide.select_one(".ent-table"):
            families.append("table")
        elif slide.select_one(".ent-timeline"):
            families.append("timeline")
        elif slide.select_one(".ent-arch-grid"):
            families.append("architecture")
        elif slide.select_one(".ent-split"):
            families.append("split")
        elif slide.select_one(".ent-matrix"):
            families.append("matrix")
        elif "enterprise-matrix" in slide.get("class", []):
            families.append("matrix")
        elif slide.select_one(".ent-code"):
            families.append("cta")
        elif "enterprise-close" in slide.get("class", []):
            families.append("cta")
    return families


def test_enterprise_dark_rhythm_uses_semantics_not_exact_role_names():
    brief = _make_slide_creator_intro_brief(preset="Enterprise Dark")
    replacements = {
        "pain-solution": ("instability-contrast", "before after comparison"),
        "solution": ("stability-pillars", "three anchors"),
        "presets": ("style-catalog", "structured evidence catalog"),
        "validation": ("quality-evidence", "validation evidence table"),
        "interaction": ("runtime-capabilities", "feature grid capabilities"),
        "use-cases": ("scenario-flow", "workflow scenarios"),
        "cta_close": ("action-close", "close action"),
    }
    for slide in brief["narrative"]["slides"]:
        replacement = replacements.get(slide["role"])
        if replacement:
            role, visual = replacement
            slide["role"] = role
            slide["visual"] = visual
            slide["visual_intent"] = visual
            slide.pop("preferred_layout_family", None)
    brief["narrative"]["page_roles"] = [slide["role"] for slide in brief["narrative"]["slides"]]

    html_text, _packet, _style_contract = render_from_brief(brief)
    soup = BeautifulSoup(html_text, "html.parser")
    slides = soup.select("section.slide")
    families = _enterprise_rendered_component_families(slides)
    roles = [slide.get("data-export-role") for slide in slides]

    assert len(slides) == 12
    assert _max_run(families) <= 1
    assert len(set(roles)) >= 6
    assert {"contrast", "feature-grid", "table", "timeline", "architecture", "split", "cta"}.issubset(set(families))

    contrast_slide = soup.select_one('section.slide[aria-label="instability-contrast"]')
    assert contrast_slide is not None
    assert contrast_slide.get("data-export-role") == "contrast_split"
    assert contrast_slide.select_one(".ent-contrast-split") is not None

    evidence_slide = soup.select_one('section.slide[aria-label="quality-evidence"]')
    assert evidence_slide is not None
    assert evidence_slide.get("data-export-role") == "data_table"
    assert len(evidence_slide.select(".ent-table tbody tr")) >= 3

    cta_slide = soup.select_one('section.slide[aria-label="action-close"]')
    assert cta_slide is not None
    assert cta_slide.get("data-export-role") == "cta_close"
    assert cta_slide.select_one(".ent-code") is not None


def test_enterprise_dark_scheduler_prioritizes_semantics_over_fallbacks():
    from low_context import build_slide_spec, _preset_usage_rules, _semantic_layout_candidates

    brief = _make_slide_creator_intro_brief(preset="Enterprise Dark")
    packet = build_render_packet(brief)
    usage_rules = _preset_usage_rules("Enterprise Dark")
    specs = {spec["role"]: spec for spec in build_slide_spec(brief, packet)}
    allowed_layouts = packet["allowed_layouts"]

    assert specs["cover"]["layout_id"] == "kpi_dashboard"
    assert specs["pain-solution"]["layout_id"] == "contrast_split"
    assert specs["features"]["layout_id"] == "comparison_matrix"
    assert specs["presets"]["layout_id"] == "data_table"
    assert specs["validation"]["layout_id"] == "data_table"

    assert _semantic_layout_candidates(
        specs["pain-solution"],
        usage_rules=usage_rules,
        layout_cycle=allowed_layouts,
    )[0] == "contrast_split"
    assert _semantic_layout_candidates(
        specs["validation"],
        usage_rules=usage_rules,
        layout_cycle=allowed_layouts,
    )[0] == "data_table"


def test_work_hub_production_presets_keep_style_signal_without_placeholder_leaks():
    cases = [
        ("Swiss Modern", _load_core_swiss_brief(), 0.70),
        ("Enterprise Dark", _make_enterprise_dark_rhythm_brief(), 0.60),
        ("Data Story", _load_core_data_story_brief(), 0.45),
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

    for preset, brief, min_signature in cases:
        html_text, _packet, _style_contract = render_from_brief(brief)
        report = analyze_html_quality(html_text, brief=brief, preset=preset)
        soup = BeautifulSoup(html_text, "html.parser")
        visible_text = soup.get_text(" ", strip=True)
        export_roles = [section.get("data-export-role") for section in soup.select("section.slide[data-export-role]")]
        gates = {key: value for key, value in report["quality_gates"].items() if key != "source-fact-coverage"}

        assert report["hard_failures"] == []
        assert all(gates.values())
        assert report["diagnostics"]["style_signature_coverage"] >= min_signature
        assert _max_run(export_roles) <= 2
        for needle in generic_needles:
            assert needle not in visible_text


def test_native_core_eval_briefs_pass_browser_geometry_gate():
    failing: dict[str, list[str]] = {}
    for preset in ["Swiss Modern", "Enterprise Dark", "Data Story"]:
        brief = _load_core_swiss_brief()
        brief["style"]["preset"] = preset
        html_text, _packet, _style_contract = render_from_brief(brief)
        report = analyze_browser_geometry_html(html_text, viewports=CORE_GEOMETRY_VIEWPORTS, stable_runs=1)
        if report["hard_failures"]:
            failing[preset] = report["hard_failures"]

    assert failing == {}


def test_swiss_representative_brief_passes_desktop_and_mobile_browser_geometry():
    brief = json.loads(
        (ROOT / "evals" / "preset-surface-all" / "cases" / "representative-12-role-brief.json").read_text(
            encoding="utf-8"
        )
    )
    brief["style"]["preset"] = "Swiss Modern"

    html_text, _packet, _style_contract = render_from_brief(brief)
    report = analyze_browser_geometry_html(
        html_text,
        viewports=[{"width": 1600, "height": 900}, {"width": 390, "height": 844}],
        stable_runs=1,
    )

    assert report["hard_failures"] == []


def test_production_presets_do_not_leak_chinese_chan_signatures():
    cases = [
        ("Swiss Modern", _load_core_swiss_brief()),
        ("Enterprise Dark", {**_load_core_swiss_brief(), "style": {**_load_core_swiss_brief()["style"], "preset": "Enterprise Dark"}}),
        ("Data Story", _load_core_data_story_brief()),
        ("Blue Sky", BLUE_SKY_DEMO),
    ]

    for preset, brief_or_path in cases:
        if isinstance(brief_or_path, dict):
            brief = _clone_json(brief_or_path)
            if brief["style"]["preset"] != preset:
                brief["style"]["preset"] = preset
            html_text, _packet, _style_contract = render_from_brief(brief)
        else:
            html_text = brief_or_path.read_text(encoding="utf-8")

        assert f'data-preset="{preset}"' in html_text
        assert "zen-ghost-kanji" not in html_text
        assert 'data-export-role="zen_' not in html_text
        assert '"Noto Serif SC"' not in html_text


def test_org_phase_change_production_presets_avoid_generic_or_truncated_anchor_tokens():
    source_brief = _make_anchor_regression_brief()
    cases = [
        ("Swiss Modern", ".hero-stat-num", 3),
        ("Enterprise Dark", ".ent-kpi-number", 0),
        ("Data Story", ".ds-kpi", 1),
    ]

    for preset, selector, expected_count in cases:
        brief = _clone_json(source_brief)
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
    swiss_brief = _load_core_swiss_brief()
    swiss_html, _packet, _style_contract = render_from_brief(swiss_brief)

    assert ".nav-dots button.active {" in swiss_html
    assert "--nav-dot-idle: rgba(10, 10, 10, 0.18);" in swiss_html
    assert "--nav-dot-active: var(--red);" in swiss_html
    assert ".bg-num {" in swiss_html
    assert ".slide-num-label {" in swiss_html
    assert "dot.classList.toggle('active', active);" in swiss_html
    assert "rgba(255,255,255,0.3)" not in swiss_html
    assert "dot.style.background = i === this.currentSlide ? 'var(--accent)'" not in swiss_html

    data_story_brief = _load_core_data_story_brief()
    data_story_html, _packet, _style_contract = render_from_brief(data_story_brief)

    assert "--nav-dot-idle: rgba(15, 23, 42, 0.22);" in data_story_html
    assert "--nav-dot-active: var(--chart-primary, #2563eb);" in data_story_html


def test_data_story_work_hub_uses_non_numeric_svgs_when_numbers_are_not_slide_local():
    brief = _load_core_data_story_brief()
    packet = build_render_packet(brief)
    specs = build_slide_spec(brief, packet)
    by_role = {spec["role"]: spec for spec in specs}

    assert _chart_metric_values_from_spec(by_role["driver"], ["1", "2", "3", "4"]) == []
    if "metrics" in by_role:
        assert _chart_metric_values_from_spec(by_role["metrics"], ["1", "2", "3"]) == []
    assert by_role["risk"]["layout_id"] == "chart_insight"

    html_text, _packet, _style_contract = render_from_brief(brief)
    soup = BeautifulSoup(html_text, "html.parser")
    driver_slide = soup.select_one('section.slide[aria-label="driver"]')
    risk_slide = soup.select_one('section.slide[aria-label="risk"]')
    assert driver_slide is not None
    assert risk_slide is not None
    assert 'aria-label="line chart"' not in str(driver_slide)
    assert 'aria-label="flow map"' in str(driver_slide)
    assert 'data-export-role="chart_insight"' in str(risk_slide)
    assert 'aria-label="signal bars"' in str(risk_slide)
    metrics_slide = soup.select_one('section.slide[aria-label="metrics"]')
    if metrics_slide is not None:
        assert 'aria-label="bar chart"' not in str(metrics_slide)
        assert metrics_slide.select_one(".ds-chart-svg") is not None


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
    brief = _load_core_data_story_brief()
    slide = next(item for item in brief["narrative"]["slides"] if item["role"] == "risk")
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


def test_data_story_standard_headings_prefer_two_lines_outside_cta_close():
    brief = _load_core_data_story_brief()
    html_text, _packet, _style_contract = render_from_brief(brief)
    soup = BeautifulSoup(html_text, "html.parser")

    for slide in soup.select("section.slide[data-export-role]"):
        role = slide.get("data-export-role")
        heading = slide.select_one(".ds-heading")
        assert heading is not None
        line_count = len(heading.select(".title-line"))
        if role == "cta_close":
            assert line_count <= 3
        else:
            assert line_count <= 2, (role, heading.get_text(" ", strip=True), line_count)


def test_data_story_workflow_layout_has_bounded_split_css():
    brief = _load_core_data_story_brief()
    html_text, _packet, _style_contract = render_from_brief(brief)

    assert 'body[data-preset="Data Story"] .ds-workflow .ds-split-layout' in html_text
    assert "max-height: min(58vh, 456px)" in html_text
    assert "-webkit-line-clamp: 3" in html_text


def test_data_story_text_heavy_generated_families_preserve_layout_variety():
    brief = _load_core_data_story_brief()
    roles = [
        "cover",
        "design-philosophy",
        "content-routing",
        "presets",
        "validation",
        "use-cases",
        "interaction",
        "cta_close",
    ]
    families = [
        "hero",
        "architecture-map",
        "three-things",
        "comparison-matrix",
        "feature-grid",
        "three-things",
        "feature-grid",
        "close",
    ]
    titles = [
        "Data Story text deck",
        "设计哲学",
        "内容型路由",
        "设计预设",
        "验证体系",
        "使用场景",
        "交互特性",
        "开始使用",
    ]
    facts = [
        ["22 种设计预设", "零依赖运行", "内容型路由"],
        ["Progressive Disclosure", "Show Don't Tell", "Against Slide Slop", "Contract Alignment"],
        ["数据报告", "商业路演", "开发者文档"],
        ["企业级", "创意类", "开发者", "数据/咨询"],
        ["validate-brief.py", "validate_html.py --strict", "preset-usage-rules.json", "Captured-run Skill Evals"],
        ["Interactive Creation", "IR-first Workflow", "PPT Conversion"],
        ["Play Mode", "Presenter Mode", "Inline Editing", "Notes Editing Panel"],
        ["Claude Code", "OpenClaw", "文档", "Demo"],
    ]
    brief["narrative"]["page_roles"] = roles
    for slide, role, family, title, supporting_facts in zip(
        brief["narrative"]["slides"],
        roles,
        families,
        titles,
        facts,
        strict=True,
    ):
        slide.update(
            {
                "role": role,
                "title": title,
                "claim": title,
                "key_point": "、".join(supporting_facts),
                "explanation": "、".join(supporting_facts),
                "visual_intent": family,
                "preferred_layout_family": family,
                "chart_policy": "auto",
                "supporting_facts": supporting_facts,
            }
        )
        slide.pop("numeric_facts", None)

    specs = build_slide_spec(brief, packet=build_render_packet(brief))
    by_role = {spec["role"]: spec["layout_id"] for spec in specs}

    assert by_role["design-philosophy"] == "chart_insight"
    assert by_role["presets"] == "comparison_matrix"
    assert by_role["validation"] == "chart_insight"
    assert by_role["interaction"] == "chart_insight"
    assert by_role["content-routing"] == "workflow_chart"
    assert by_role["use-cases"] == "workflow_chart"

    html_text, _packet, _style_contract = render_from_brief(brief)
    soup = BeautifulSoup(html_text, "html.parser")
    svg_labels_by_role = {
        slide.get("aria-label"): slide.select_one(".ds-chart-svg").get("aria-label")
        for slide in soup.select("section.slide")
        if slide.select_one(".ds-chart-svg")
    }

    assert 'body[data-preset="Data Story"] .ds-comparison .ds-matrix' in html_text
    assert 'body[data-preset="Data Story"] .ds-comparison .ds-matrix-cell' in html_text
    assert ".ds-signal-map" in html_text
    assert ".ds-flow-map" in html_text
    assert ".ds-evidence-ladder" in html_text
    assert ".ds-state-grid-svg" in html_text
    assert "height: min(52vh, 360px)" in html_text
    assert "-webkit-line-clamp: 3" in html_text
    assert svg_labels_by_role["design-philosophy"] == "signal map"
    assert svg_labels_by_role["content-routing"] == "flow map"
    assert svg_labels_by_role["validation"] == "evidence ladder"
    assert svg_labels_by_role["use-cases"] == "phase timeline"
    interaction_slide = soup.select_one('section.slide[aria-label="interaction"]')
    assert interaction_slide is not None
    assert interaction_slide.select_one(".ds-key-strip") is not None
    assert interaction_slide.select_one(".ds-state-grid-svg") is None
    assert html_text.count('aria-label="state grid"') <= 1


def test_data_story_workflow_global_cap_does_not_create_chart_family_triplet():
    from low_context import _data_story_visual_signature

    brief = read_json(POLISH_DEMO)
    brief["style"]["preset"] = "Data Story"
    brief["title"] = "Single Deck Eval"
    brief["audience"] = "Operators"
    brief["desired_action"] = "Verify eval wiring"

    specs = build_slide_spec(brief, packet=build_render_packet(brief))
    signatures = [
        _data_story_visual_signature(spec, spec["layout_id"])
        for spec in specs
    ]

    assert not any(
        first == second == third
        for first, second, third in zip(signatures, signatures[1:], signatures[2:])
    )


def test_data_story_slide_creator_intro_stays_chart_first():
    brief = _make_enterprise_dark_rhythm_brief()
    brief["brief_id"] = "slide-creator-intro-12p-data-story-regression"
    brief["style"]["preset"] = "Data Story"
    brief["style"]["tone"] = "分析、数据驱动、清晰"
    brief["title"] = "slide-creator: Stable AI Slide Generation"
    brief["audience"] = "评估 slide-creator 的产品经理、开发者、内容创作者"
    brief["desired_action"] = "理解 slide-creator 的核心价值并试跑第一个 deck"
    brief["content"]["must_include"] = [
        "IR-first workflow（BRIEF.json → HTML）",
        "零依赖 runtime（浏览器原生）",
        "22 design presets 与内容型路由",
        "Validate before trust（严格验证）",
        "Presenter Mode、Inline Editing、Play Mode",
    ]
    brief["narrative"]["page_roles"] = [
        "cover",
        "pain-solution",
        "solution",
        "features",
        "workflow",
        "design-philosophy",
        "presets",
        "content-routing",
        "validation",
        "interaction",
        "use-cases",
        "cta_close",
    ]
    slide_data = [
        (
            "cover",
            "slide-creator",
            "AI 能生成幻灯片但质量不稳定，slide-creator 给你稳定、精致的输出",
            "22 种设计预设、零依赖运行、IR-first 工作流、内容型路由",
            "hero",
            ["22 种设计预设", "零依赖运行", "IR-first 工作流", "内容型路由"],
        ),
        (
            "pain-solution",
            "AI Slide Generation 的痛点",
            "同一提示词每次结果都不同，反复重试让人疲惫",
            "质量不稳定、风格混乱、Context 压力、依赖外部工具、无验证、视觉密度失控",
            "comparison",
            ["质量不稳定", "风格混乱", "Context 压力", "无验证"],
        ),
        (
            "solution",
            "slide-creator 解决方案",
            "通过 IR-first workflow、零依赖 runtime 和严格验证体系，解决 AI slide generation 的不稳定性问题",
            "BRIEF.json 作为硬真相源、单 HTML 文件浏览器原生、生成前严格验证",
            "three-things",
            ["IR-first Workflow", "零依赖 Runtime", "Validate Before Trust"],
        ),
        (
            "features",
            "核心功能",
            "六个核心功能覆盖从规划、渲染、验证到交互和自定义",
            "prompt → BRIEF.json → HTML → validate → eval、22 design presets 每预设 8-12 种布局变体、Content-type routing、Zero-dependency runtime、16 checkpoints review、Custom themes",
            "feature-grid",
            ["22 Design Presets", "8-12 种布局变体", "16 checkpoints", "6 auto-detect + 10 AI-advised"],
        ),
        (
            "workflow",
            "工作流",
            "五个阶段的确定性路径，从内容到 HTML deck 的稳定交付",
            "Phase 1 内容收集、Phase 2 BRIEF.json 生成、Phase 3 确定性渲染、Phase 3.5 Content Review、Phase 4 浏览器打开导出",
            "timeline",
            ["Phase 1 内容收集", "Phase 2 BRIEF.json", "Phase 3 渲染验证", "Phase 4 打开导出"],
        ),
        (
            "design-philosophy",
            "设计哲学",
            "四个设计哲学保护最后一步，减轻 context 压力，避免视觉 slop",
            "Progressive Disclosure、Show Don't Tell、Against Slide Slop、Contract Alignment",
            "architecture-map",
            ["Progressive Disclosure", "Show Don't Tell", "Against Slide Slop", "Contract Alignment"],
        ),
        (
            "presets",
            "设计预设",
            "22 design presets 按内容型分类，覆盖从 pitch deck 到数据报告到 dev tool 的所有场景",
            "企业级、创意类、开发者、数据/咨询、文艺/品牌、设计探索",
            "comparison-matrix",
            ["企业级", "创意类", "开发者", "数据/咨询", "文艺/品牌", "设计探索"],
        ),
        (
            "content-routing",
            "内容型路由",
            "Content-type routing 自动推荐最佳风格，减少返工",
            "数据报告 → Data Story / Enterprise Dark / Swiss Modern、Business Pitch / VC Deck → Bold Signal / Aurora Mesh / Enterprise Dark、Developer Tool / API Docs → Terminal Green / Neon Cyber",
            "three-things",
            ["数据报告", "Business Pitch", "Developer Tool"],
        ),
        (
            "validation",
            "验证体系",
            "四层验证体系确保从 IR 到运行时的契约一致性",
            "validate-brief.py 检查 BRIEF.json 契约、validate_html.py --strict 检查运行时契约、preset-usage-rules.json 定义路由规则、Captured-run Skill Evals 回归基线对比",
            "feature-grid",
            ["validate-brief.py", "validate_html.py --strict", "preset-usage-rules.json", "Captured-run Skill Evals"],
        ),
        (
            "interaction",
            "交互特性",
            "四个交互特性让 HTML deck 成为真正的演示工具，而非一次性截图",
            "F5 全屏、P 键演讲窗口、默认浏览器编辑、E 键笔记栏",
            "feature-grid",
            ["F5 全屏", "P 键演讲窗口", "默认浏览器编辑", "E 键笔记栏"],
        ),
        (
            "use-cases",
            "使用场景",
            "三种典型使用场景覆盖从零开始、复杂内容、PPT 转换",
            "Interactive Creation 从交互开始、IR-first Workflow 从 BRIEF 开始、PPT Conversion 从 .pptx 开始",
            "three-things",
            ["Interactive Creation", "IR-first Workflow", "PPT Conversion"],
        ),
        (
            "cta_close",
            "开始使用",
            "两个平台一句话安装，文档和 demo 在线可访问",
            "Claude Code: Install、OpenClaw: clawhub install、文档链接、Demo 链接",
            "close",
            [
                'Claude Code: "Install https://github.com/kaisersong/slide-creator"',
                "OpenClaw: clawhub install kai-slide-creator",
                "文档: https://kaisersong.github.io/slide-creator/",
                "Demo: https://kaisersong.github.io/slide-creator/demos/enterprise-dark-en.html",
            ],
        ),
    ]
    brief["deck"]["page_count"] = len(slide_data)
    brief["narrative"]["slides"] = [{} for _ in slide_data]
    for index, (slide, values) in enumerate(zip(brief["narrative"]["slides"], slide_data, strict=True), start=1):
        role, title, claim, explanation, family, facts = values
        slide.update(
            {
                "slide_number": index,
                "role": role,
                "title": title,
                "claim": claim,
                "key_point": explanation,
                "explanation": explanation,
                "visual": family,
                "visual_intent": family,
                "preferred_layout_family": family,
                "chart_policy": "auto",
                "supporting_facts": facts,
            }
        )
        slide.pop("numeric_facts", None)

    html_text, _packet, _style_contract = render_from_brief(brief)
    soup = BeautifulSoup(html_text, "html.parser")
    export_roles = [slide.get("data-export-role") for slide in soup.select("section.slide")]
    chart_slides = [
        slide
        for slide in soup.select("section.slide")
        if slide.select_one(".ds-chart-svg")
    ]
    svg_labels = [
        svg.get("aria-label")
        for svg in soup.select("section.slide .ds-chart-svg")
        if svg.get("aria-label")
    ]
    p2_slide = soup.select_one('section.slide[aria-label="pain-solution"]')

    assert export_roles.count("comparison_matrix") <= 2
    assert len(set(export_roles)) >= 6
    assert len(chart_slides) >= 6
    assert len(set(svg_labels)) >= 4
    assert svg_labels.count("signal map") <= 3
    assert p2_slide is not None
    assert p2_slide.select_one('svg[aria-label="signal map"]') is None

    solution_slide = soup.select_one('section.slide[aria-label="solution"]')
    assert solution_slide is not None
    assert solution_slide.get("data-export-role") == "comparison_matrix"
    assert solution_slide.select_one(".ds-matrix") is not None

    workflow_slides = [
        soup.select_one(f'section.slide[aria-label="{role}"]')
        for role in ("workflow", "content-routing", "use-cases")
    ]
    workflow_roles = {slide.get("aria-label"): slide.get("data-export-role") for slide in workflow_slides if slide}
    assert workflow_roles["workflow"] == "workflow_chart"
    assert workflow_roles["content-routing"] == "workflow_chart"
    assert workflow_roles["use-cases"] == "chart_insight"
    assert export_roles.count("workflow_chart") <= 2

    for slide in workflow_slides[:2]:
        assert slide is not None
        assert slide.get("data-export-role") == "workflow_chart"
        visual_svg = slide.select_one(".ds-chart-svg")
        assert visual_svg is not None
        assert "ds-chart-card" not in (visual_svg.parent.get("class") or [])
        assert len(slide.select(".ds-chart-card")) <= 1
        assert slide.select_one(".ds-workflow-visual") is not None

    workflow_svg_labels = [
        slide.select_one(".ds-chart-svg").get("aria-label")
        for slide in workflow_slides
        if slide and slide.select_one(".ds-chart-svg")
    ]
    assert len(set(workflow_svg_labels)) >= 3
    assert workflow_svg_labels.count("flow map") <= 2
    assert soup.select_one('section.slide[aria-label="workflow"] .ds-phase-timeline') is not None
    assert soup.select_one('section.slide[aria-label="use-cases"] .ds-phase-timeline') is not None

    cta_slide = soup.select_one('section.slide[aria-label="cta_close"]')
    assert cta_slide is not None
    assert cta_slide.select_one(".ds-action-grid") is not None
    assert cta_slide.select_one(".ds-action-title") is not None
    interaction_slide = soup.select_one('section.slide[aria-label="interaction"]')
    assert interaction_slide is not None
    keycaps = {node.get_text(" ", strip=True) for node in interaction_slide.select(".ds-keycap")}
    assert {"F5", "P", "E", "Notes"}.issubset(keycaps)
    action_titles = [node.get_text(" ", strip=True) for node in cta_slide.select(".ds-action-title")]
    assert action_titles[:2] == ["Claude Code", "OpenClaw"]
    assert "clawhub install kai-slide-creator" in cta_slide.get_text(" ", strip=True)
    assert ".ds-action-copy" in html_text
    assert "overflow-wrap: anywhere" in html_text
    assert all(
        not re.search(r"Claude|OpenClaw", kpi.get_text(" ", strip=True), flags=re.IGNORECASE)
        for kpi in cta_slide.select(".ds-kpi")
    )
    from low_context import _compact_display_token

    assert _compact_display_token("IR-first Workflow — BRIEF.json 作为硬真相源", fallback="Step") == "BRIEF"

    validation_slide = soup.select_one('section.slide[aria-label="validation"]')
    assert validation_slide is not None
    ladder_svg = validation_slide.select_one(".ds-evidence-ladder")
    assert ladder_svg is not None
    assert "ds-chart-card" not in (ladder_svg.parent.get("class") or [])
    assert validation_slide.select_one(".ds-chart-visual") is not None
    ladder_labels = ladder_svg.select("text.ds-svg-label")
    assert ladder_labels
    assert all(label.get("text-anchor") == "end" for label in ladder_labels)
    assert all(float(label.get("x")) <= 300 for label in ladder_labels)
    ladder_rungs = ladder_svg.select("line.ds-ladder-rung")
    assert ladder_rungs
    assert all(float(rung.get("x2")) <= 160 for rung in ladder_rungs)


def test_data_story_ai_generated_roles_have_explicit_safe_layouts():
    from low_context import DATA_STORY_ROLE_LAYOUTS

    expected = {
        "pain-solution": "chart_insight",
        "design-philosophy": "chart_insight",
        "presets": "comparison_matrix",
        "content-routing": "workflow_chart",
        "validation": "kpi_chart",
        "interaction": "chart_insight",
        "use-cases": "workflow_chart",
        "cta_close": "cta_close",
        "getting-started": "cta_close",
    }

    for role, layout in expected.items():
        assert DATA_STORY_ROLE_LAYOUTS.get(role) == layout


def test_swiss_ai_generated_roles_have_explicit_reference_layouts():
    from low_context import SWISS_ROLE_LAYOUTS

    expected = {
        "pain-solution": "column_content",
        "design-philosophy": "contents_index",
        "presets": "contents_index",
        "content-routing": "contents_index",
        "validation": "data_table",
        "interaction": "data_table",
        "use-cases": "column_content",
        "cta_close": "pull_quote",
        "getting-started": "pull_quote",
    }

    for role, layout in expected.items():
        assert SWISS_ROLE_LAYOUTS.get(role) == layout


def test_enterprise_dark_slide_creator_intro_uses_demo_level_component_rhythm():
    brief = _make_slide_creator_intro_brief(preset="Enterprise Dark")

    html_text, _packet, _style_contract = render_from_brief(brief)
    soup = BeautifulSoup(html_text, "html.parser")
    slides = soup.select("section.slide")
    assert len(slides) == 12

    roles = [slide.get("data-export-role") for slide in slides]
    component_families = _enterprise_rendered_component_families(slides)
    assert len(component_families) == len(slides)
    assert _max_run(component_families) <= 1
    assert len(set(roles)) >= 7
    assert roles.count("data_table") >= 2
    assert {
        "cover-dashboard",
        "contrast",
        "split",
        "feature-grid",
        "timeline",
        "architecture",
        "table",
        "cta",
    }.issubset(set(component_families))

    cover_slide = soup.select_one('section.slide[aria-label="cover"]')
    assert cover_slide is not None
    assert cover_slide.get("data-export-role") == "kpi_dashboard"
    assert len(cover_slide.select(".ent-cover-metric-card")) == 3
    assert cover_slide.select(".ent-kpi-number.ent-cover-inline-number")

    pain_slide = soup.select_one('section.slide[aria-label="pain-solution"]')
    assert pain_slide is not None
    assert pain_slide.get("data-export-role") == "contrast_split"
    assert pain_slide.select_one(".ent-contrast-split") is not None
    assert len(pain_slide.select(".ent-contrast-block")) == 2

    solution_slide = soup.select_one('section.slide[aria-label="solution"]')
    assert solution_slide is not None
    assert solution_slide.get("data-export-role") in {"kpi_dashboard", "consulting_split"}
    if solution_slide.get("data-export-role") == "kpi_dashboard":
        assert "ent-dashboard-story" in solution_slide.get("class", [])
        assert len(solution_slide.select(".ent-kpi-card-story")) == 3
        assert solution_slide.select(".ent-kpi-story-index")
    else:
        assert solution_slide.select_one(".ent-split") is not None
        assert len(solution_slide.select(".ent-feature-row")) == 3
    assert not solution_slide.select(".ent-kpi-number")

    features_slide = soup.select_one('section.slide[aria-label="features"]')
    assert features_slide is not None
    assert features_slide.get("data-export-role") == "comparison_matrix"
    assert "enterprise-feature-grid-slide" in features_slide.get("class", [])
    assert len(features_slide.select(".ent-feature-card")) == 4
    assert len(features_slide.select(".ent-prog-bar")) == 4

    workflow_slide = soup.select_one('section.slide[aria-label="workflow"]')
    assert workflow_slide is not None
    assert workflow_slide.get("data-export-role") == "timeline"
    assert len(workflow_slide.select(".ent-timeline-item")) == 4

    design_slide = soup.select_one('section.slide[aria-label="design-philosophy"]')
    assert design_slide is not None
    assert design_slide.get("data-export-role") == "architecture_map"
    assert len(design_slide.select(".ent-arch-card")) == 3

    presets_slide = soup.select_one('section.slide[aria-label="presets"]')
    assert presets_slide is not None
    assert presets_slide.get("data-export-role") == "data_table"
    assert presets_slide.select_one(".ent-table") is not None
    assert len(presets_slide.select(".ent-status-dot")) >= 3
    assert len(presets_slide.select(".ent-badge")) >= 3

    routing_slide = soup.select_one('section.slide[aria-label="content-routing"]')
    assert routing_slide is not None
    assert routing_slide.get("data-export-role") == "consulting_split"
    assert routing_slide.select_one(".ent-split") is not None
    assert len(routing_slide.select(".ent-feature-row")) == 3

    validation_slide = soup.select_one('section.slide[aria-label="validation"]')
    assert validation_slide is not None
    assert validation_slide.get("data-export-role") == "data_table"
    assert validation_slide.select_one(".ent-table") is not None
    assert len(validation_slide.select(".ent-status-dot")) >= 3
    assert len(validation_slide.select(".ent-badge")) >= 3

    interaction_slide = soup.select_one('section.slide[aria-label="interaction"]')
    assert interaction_slide is not None
    assert interaction_slide.get("data-export-role") == "comparison_matrix"
    assert "enterprise-feature-grid-slide" in interaction_slide.get("class", [])
    assert len(interaction_slide.select(".ent-feature-card")) == 4

    use_cases_slide = soup.select_one('section.slide[aria-label="use-cases"]')
    assert use_cases_slide is not None
    assert use_cases_slide.get("data-export-role") == "consulting_split"
    assert len(use_cases_slide.select(".ent-feature-row")) == 3

    cta_slide = soup.select_one('section.slide[aria-label="cta_close"]')
    assert cta_slide is not None
    assert cta_slide.get("data-export-role") == "cta_close"
    assert cta_slide.select_one(".ent-code") is not None
    assert not cta_slide.select(".ent-kpi-number")

    assert component_families == _enterprise_rendered_component_families(slides)


def test_enterprise_dark_tier1_tables_keep_minimum_board_density():
    brief = _make_slide_creator_intro_brief(preset="Enterprise Dark")
    brief["content"]["must_avoid"] = ["不要生成浅色背景"]
    brief["narrative"]["thesis"] = "AI slide generation needs a deterministic render path."
    assert build_render_packet(brief)["quality_tier"] == "tier1"

    html_text, _packet, _style_contract = render_from_brief(brief)
    soup = BeautifulSoup(html_text, "html.parser")

    for role in ("presets", "validation"):
        slide = soup.select_one(f'section.slide[aria-label="{role}"]')
        assert slide is not None
        assert slide.get("data-export-role") == "data_table"
        assert len(slide.select(".ent-table tbody tr")) >= 3
        assert len(slide.select(".ent-status-dot")) >= 3
        assert len(slide.select(".ent-badge")) >= 3


def test_swiss_slide_creator_intro_uses_demo_level_component_rhythm():
    brief = _make_slide_creator_intro_brief(preset="Swiss Modern")

    html_text, _packet, _style_contract = render_from_brief(brief)
    soup = BeautifulSoup(html_text, "html.parser")
    slides = soup.select("section.slide")
    assert len(slides) == 12

    roles = [slide.get("data-export-role") for slide in slides]
    assert roles[0] == "title_grid"
    assert roles[-1] == "pull_quote"
    assert len(set(roles)) >= 5
    ghost_roles = [slide.get("aria-label") for slide in slides if slide.select_one(":scope > .bg-num")]
    assert ghost_roles == ["cover", "pain-solution", "presets", "content-routing", "use-cases", "cta_close"]
    assert len(ghost_roles) < len(slides)
    assert ".slide-content, .left-panel, .right-panel" in html_text
    assert "z-index: 2;" in html_text

    cover_slide = soup.select_one('section.slide[aria-label="cover"]')
    assert cover_slide is not None
    assert len(cover_slide.select(".hero-stat")) >= 3

    pain_slide = soup.select_one('section.slide[aria-label="pain-solution"]')
    assert pain_slide is not None
    left_title = pain_slide.select_one(".left-panel .swiss-title")
    assert left_title is not None
    assert left_title.get_text(" ", strip=True) == "AI Slide Generation 的痛点"
    left_title_lines = [node.get_text(" ", strip=True) for node in left_title.select(".title-line")]
    assert left_title_lines == ["AI Slide", "Generation", "的痛点"]
    assert ".left-panel .swiss-title" in html_text
    assert ".left-panel .swiss-label" in html_text
    assert ".left-panel .title-line" in html_text
    assert "overflow-wrap: normal;" in html_text
    assert "word-break: normal;" in html_text
    assert "hyphens: none;" in html_text
    assert "white-space: nowrap;" in html_text
    assert "font-size: clamp(1.5rem, 1.9vw, 2.4rem);" in html_text
    assert "font-size: clamp(10rem, 30vw, 30rem);" in html_text
    assert "right: clamp(-3rem, -2vw, -1rem);" in html_text
    assert "font-size: clamp(17px, 1.9vw, 22px);" in html_text
    assert "font-size: clamp(16px, 1.8vw, 21px);" in html_text
    assert "font-size: clamp(16px, 1.7vw, 20px);" in html_text
    assert [node.get_text(" ", strip=True) for node in pain_slide.select(".pain-num")] == ["01", "02", "03"]
    assert not any("." in node.get_text(" ", strip=True) for node in pain_slide.select(".pain-num"))

    features_slide = soup.select_one('section.slide[aria-label="features"]')
    assert features_slide is not None
    assert features_slide.select_one(".feat-grid, .data-table") is not None
    feature_text_units = [
        node.get_text(" ", strip=True)
        for node in features_slide.select(".feat-card, .data-table td")
    ]
    assert feature_text_units
    assert all(len(cell) <= 100 for cell in feature_text_units)
    assert "IR-first Workflow — IR-first Workflow" not in features_slide.get_text(" ", strip=True)

    design_slide = soup.select_one('section.slide[aria-label="design-philosophy"]')
    assert design_slide is not None
    assert design_slide.get("data-export-role") == "contents_index"
    assert design_slide.select_one(".index-item") is not None
    assert design_slide.select_one(".disc-diagram") is None

    routing_slide = soup.select_one('section.slide[aria-label="content-routing"]')
    assert routing_slide is not None
    assert routing_slide.get("data-export-role") in {"contents_index", "geometric_diagram"}
    assert routing_slide.select_one(".index-item, .disc-diagram") is not None
    assert routing_slide.select_one(".inst-blocks") is None

    validation_slide = soup.select_one('section.slide[aria-label="validation"]')
    assert validation_slide is not None
    assert validation_slide.get("data-export-role") == "data_table"
    assert validation_slide.select_one(".inst-blocks") is not None
    assert len(validation_slide.select(".inst-block")) >= 3

    interaction_slide = soup.select_one('section.slide[aria-label="interaction"]')
    assert interaction_slide is not None
    assert interaction_slide.get("data-export-role") in {"contents_index", "data_table"}
    assert interaction_slide.select_one(".feat-grid, .data-table") is not None

    use_cases_slide = soup.select_one('section.slide[aria-label="use-cases"]')
    assert use_cases_slide is not None
    assert use_cases_slide.get("data-export-role") in {"column_content", "geometric_diagram"}
    assert use_cases_slide.select_one(".left-panel, .disc-diagram") is not None

    cta_slide = soup.select_one('section.slide[aria-label="cta_close"]')
    assert cta_slide is not None
    assert cta_slide.select_one(".cta-block") is not None
    assert cta_slide.select_one(".cta-title") is not None
    assert cta_slide.select_one(".cta-line") is not None
    assert cta_slide.select_one(".cta-echo") is not None

    component_families = []
    for slide in slides:
        if slide.select_one(".left-panel"):
            component_families.append("split")
        elif slide.select_one(".data-table"):
            component_families.append("table")
        elif slide.select_one(".disc-diagram"):
            component_families.append("diagram")
        elif slide.select_one(".inst-blocks"):
            component_families.append("evidence")
        elif slide.select_one(".feat-grid"):
            component_families.append("feature-grid")
        elif slide.select_one(".index-item"):
            component_families.append("index")
        elif slide.select_one(".stat-row"):
            component_families.append("stat")
        elif slide.select_one(".cta-block"):
            component_families.append("cta")
        else:
            component_families.append("hero")

    assert all(left != right for left, right in zip(component_families, component_families[1:]))
    assert {"split", "stat", "diagram", "index", "evidence", "feature-grid", "cta"}.issubset(set(component_families))


def test_swiss_generated_roles_emit_reference_signature_components():
    brief = _load_core_swiss_brief()
    brief["narrative"]["page_roles"][2] = "presets"
    brief["narrative"]["page_roles"][4] = "validation"
    brief["narrative"]["page_roles"][-1] = "cta_close"
    presets_slide = brief["narrative"]["slides"][2]
    validation_slide = brief["narrative"]["slides"][4]
    cta_slide = brief["narrative"]["slides"][-1]
    presets_slide.update(
        {
            "role": "presets",
            "title": "预设选择必须成为可比较的能力面",
            "key_point": "展厅里最关键的是让风格差异、适用场景和风险边界可以被横向比较。",
            "claim": "预设不是皮肤，而是内容组织方式。",
            "explanation": "Swiss Modern 应以功能卡片展示选择维度，而不是普通列表。",
            "supporting_facts": ["风格差异", "适用场景", "风险边界"],
            "visual": "feature cards",
        }
    )
    validation_slide.update(
        {
            "role": "validation",
            "title": "验证页需要显示证据块而不是泛列表",
            "key_point": "严格校验、来源覆盖和组件签名共同决定这套展厅是否可信。",
            "claim": "验证结果必须能被快速扫描。",
            "explanation": "Swiss Modern 应输出 inst-block 证据块，保留参考组件签名。",
            "supporting_facts": ["严格校验", "来源覆盖", "组件签名"],
            "visual": "evidence blocks",
        }
    )
    cta_slide.update(
        {
            "role": "cta_close",
            "title": "先收敛关键风格，再扩大模板覆盖",
            "key_point": "下一步应该围绕 Swiss、Data Story、Blue Sky 和 Enterprise Dark 建立稳定评测集。",
            "claim": "先收敛关键风格。",
            "explanation": "CTA 页需要输出 Swiss 原生 cta-block。",
            "supporting_facts": ["稳定评测集", "关键风格", "模板覆盖"],
            "visual": "cta block",
        }
    )

    html_text, _packet, _style_contract = render_from_brief(brief)
    soup = BeautifulSoup(html_text, "html.parser")
    presets_rendered = soup.select_one('section[aria-label="presets"]')
    validation_rendered = soup.select_one('section[aria-label="validation"]')
    cta_rendered = soup.select_one('section[aria-label="cta_close"]')

    assert presets_rendered is not None
    assert validation_rendered is not None
    assert cta_rendered is not None
    assert presets_rendered.select_one(".feat-grid") is not None
    assert len(presets_rendered.select(".feat-card")) >= 3
    assert validation_rendered.select_one(".inst-blocks") is not None
    assert len(validation_rendered.select(".inst-block")) >= 3
    assert cta_rendered.select_one(".cta-block") is not None
    assert cta_rendered.select_one(".cta-title") is not None
    assert cta_rendered.select_one(".cta-line") is not None
    assert cta_rendered.select_one(".cta-echo") is not None


def test_blue_sky_ai_generated_roles_have_explicit_non_cover_layouts():
    from low_context import BLUE_SKY_ROLE_LAYOUTS

    expected = {
        "pain-solution": "comparison",
        "design-philosophy": "bento",
        "presets": "bento",
        "content-routing": "table",
        "validation": "workflow",
        "interaction": "bento",
        "use-cases": "bento",
        "cta_close": "closing",
        "getting-started": "closing",
    }

    for role, layout in expected.items():
        assert BLUE_SKY_ROLE_LAYOUTS.get(role) == layout
        assert layout != "cover"


def test_blue_sky_slide_creator_intro_uses_demo_level_component_rhythm():
    brief = _make_slide_creator_intro_brief(preset="Blue Sky")

    html_text, _packet, _style_contract = render_from_brief(brief)
    soup = BeautifulSoup(html_text, "html.parser")
    slides = soup.select("section.slide")
    assert len(slides) == 12

    cover_slide = soup.select_one('section.slide[aria-label="cover"]')
    assert cover_slide is not None
    cover_pill = cover_slide.select_one(".pill")
    assert cover_pill is not None
    assert cover_pill.get_text(" ", strip=True)
    assert "22" in cover_pill.get_text(" ", strip=True)
    cover_cards = cover_slide.select(".g")
    cover_stats = cover_slide.select(".g .stat")
    assert len(cover_cards) == len(cover_stats)
    assert len(cover_stats) >= 3
    assert not cover_slide.select(".g h4")
    assert all(re.search(r"\d", node.get_text(" ", strip=True)) for node in cover_stats)

    features_slide = soup.select_one('section.slide[aria-label="features"]')
    assert features_slide is not None
    feature_cards = features_slide.select(".bento > .g")
    assert len(feature_cards) >= 4
    assert features_slide.select_one(".bento .span2, .bento .span3, .bento .row2") is not None
    assert all("grid-column" in card.get("style", "") for card in feature_cards[:6])
    assert all("grid-row" in card.get("style", "") for card in feature_cards[:6])
    feature_grid_style = features_slide.select_one(".bento").get("style", "")
    assert "grid-auto-rows:132px" in feature_grid_style
    assert features_slide.select_one(".bento + p") is None
    assert "Content-type Routing" in features_slide.get_text(" ", strip=True)
    assert "22 22 Design Presets" not in features_slide.get_text(" ", strip=True)

    design_slide = soup.select_one('section.slide[aria-label="design-philosophy"]')
    assert design_slide is not None
    design_cards = design_slide.select(".bento > .g")
    assert len(design_cards) >= 4
    feature_card_styles = [card.get("style", "") for card in feature_cards[:6]]
    design_card_styles = [card.get("style", "") for card in design_cards[:6]]
    assert design_card_styles != feature_card_styles
    assert any("grid-row:1 / span 2;" in style for style in design_card_styles)

    interaction_slide = soup.select_one('section.slide[aria-label="interaction"]')
    assert interaction_slide is not None
    key_labels = {node.get_text(" ", strip=True) for node in interaction_slide.select("kbd")}
    assert {"F5", "P", "E"}.issubset(key_labels)
    assert interaction_slide.select_one(".info") is not None
    assert interaction_slide.select_one(".co") is not None
    interaction_grid_styles = " ".join(
        node.get("style", "") for node in interaction_slide.select(".bento")
    )
    assert "grid-auto-rows:164px" in interaction_grid_styles

    presets_slide = soup.select_one('section.slide[aria-label="presets"]')
    assert presets_slide is not None
    assert presets_slide.select_one(".cols3") is not None

    use_cases_slide = soup.select_one('section.slide[aria-label="use-cases"]')
    assert use_cases_slide is not None
    assert len(use_cases_slide.select(".layer, .g")) >= 3

    cta_slide = soup.select_one('section.slide[aria-label="cta_close"]')
    assert cta_slide is not None
    assert cta_slide.select_one(".cmd") is not None
    assert cta_slide.select_one(".g") is not None
    assert "clawhub install kai-slide-creator" in cta_slide.get_text(" ", strip=True)

    component_classes = {
        class_name
        for node in soup.select(".g,.pill,.stat,.layer,.ctable,.info,.co,.cmd,kbd,.bento,.cols2,.cols3,.cols4")
        for class_name in (node.get("class") or [node.name])
    }
    assert {"g", "pill", "stat", "layer", "ctable", "info", "cmd", "bento"}.issubset(component_classes)
    assert {"co", "cols3"}.issubset(component_classes)


def test_blue_sky_cover_does_not_render_text_facts_as_stat_values():
    from low_context import _render_blue_sky_slide

    spec = {
        "slide_number": 1,
        "role": "cover",
        "layout_id": "cover",
        "title": "展厅风格验证",
        "key_point": "文本证据可以保留，但不能被放进大号统计数字槽。",
        "speaker_note": "cover",
        "subtitle": "Blue Sky",
        "supporting_items": ["validate-brief.py", "数据报告", "模板选择"],
        "evidence_items": [],
        "supporting_facts": ["validate-brief.py", "数据报告", "模板选择"],
    }

    html_text = _render_blue_sky_slide(spec, total=1, language="zh-CN", role_index=0)
    soup = BeautifulSoup(html_text, "html.parser")
    stat_values = [node.get_text(" ", strip=True) for node in soup.select(".stat")]

    assert "validate-brief.py" in soup.get_text(" ", strip=True)
    assert "validate-brief.py" not in stat_values
    assert "数据报告" not in stat_values
    assert all(any(char.isdigit() for char in value) for value in stat_values)


def test_compact_display_token_preserves_complete_mixed_language_terms():
    assert _compact_display_token("对国内 SaaS 最稳的路径仍然是分阶段落地") == "SaaS"
    assert _compact_display_token("国内 SaaS 应采用分阶段落地策略") == "SaaS"
    assert _compact_display_token("Salesforce 的四次 AI 演进，基本写出了软件行业的确定性路径") == "四次AI演进"


def test_chart_labels_skip_numeric_prefixes_and_version_tokens():
    spec = {
        "supporting_items": [
            "2016：Einstein 1.0，规则加机器学习做业务预测",
            "2023：Einstein GPT，接入大模型增强生成能力",
            "2024：Einstein Copilot，嵌入 CRM 全流程",
            "2025 路线图：Einstein Agents，自主执行业务闭环",
        ],
        "evidence_items": [],
        "title": "Salesforce 的产品里程碑几乎逐点映射了行业分水岭",
        "key_point": "龙头路径可以用来校准行业节奏。",
    }

    labels = _chart_labels_from_spec(spec, count=4)

    assert labels[0] != "1.0"
    assert all(label not in {"1.0", "2016", "2023", "2024", "2025"} for label in labels)


def test_chart_labels_compact_long_arrow_workflow_items():
    spec = {
        "supporting_items": [
            "IR-first Workflow — prompt → BRIEF.json → HTML → validate → eval",
            "22 Design Presets — 每预设 8-12 种命名布局变体",
            "Content-type Routing — 数据报告 → Data Story / Enterprise Dark",
        ],
        "evidence_items": [],
        "title": "核心功能",
        "key_point": "六个核心功能覆盖从规划、渲染、验证到交互和自定义",
    }

    labels = _chart_labels_from_spec(spec, count=3)

    assert all(_title_visual_units(label) <= 12 for label in labels)
    assert not any("→" in label or "—" in label for label in labels)


def test_chart_metric_values_ignore_ordinal_stage_numbers_without_real_numeric_signal():
    spec = {
        "numeric_facts": [],
        "supporting_items": [],
        "title": "阶段 1 和阶段 2 解决的是提效，阶段 3 和阶段 4 开始重写产品形态",
        "claim": "阶段 1 和阶段 2 解决的是提效，阶段 3 和阶段 4 开始重写产品形态",
        "key_point": "前两阶段主要减少重复劳动，后两阶段开始改写入口、协作方式和人机分工边界。",
        "visual_intent": "evidence contrast between efficiency and product-shape change",
        "supporting_facts": [
            "规则自动化只处理确定性流程",
            "大模型增强仍要求用户主动触发",
            "Copilot 开始主动跟随业务上下文",
            "Agent 开始承担端到端闭环执行",
        ],
        "evidence_items": [],
    }

    assert _chart_metric_values_from_spec(spec, ["1", "2", "3", "4"]) == []


def test_chinese_chan_vertical_titles_compact_to_safe_semantic_anchors():
    brief = {
        "schema_version": 1,
        "brief_id": "chan-vertical-anchor-test",
        "mode": "auto",
        "language": "zh-CN",
        "title": "AI时代工作的意义",
        "audience": "测试",
        "desired_action": "测试",
        "deck": {"deck_type": "user-content", "page_count": 5, "output_format": "html-slides"},
        "style": {"preset": "Chinese Chan", "tone": "克制", "visual_density": "low"},
        "content": {"source_policy": "distill-only", "must_include": ["意义", "判断", "承担"], "must_avoid": ["鸡汤", "口号", "替代论"]},
        "narrative": {
            "thesis": "AI 时代工作的意义来自判断与承担。",
            "page_roles": ["cover", "problem", "driver", "decision", "closing"],
            "slides": [
                {
                    "slide_number": 1,
                    "role": "cover",
                    "title": "AI时代，工作失去的不是意义，而是旧的意义",
                    "key_point": "当重复执行被机器接管，真正留下来的，是判断、责任与创造。",
                    "visual": "contemplative hero",
                    "claim": "AI时代，工作失去的不是意义，而是旧的意义",
                    "explanation": "当重复执行被机器接管，真正留下来的，是判断、责任与创造。",
                    "supporting_facts": ["重复执行先被压缩", "判断与责任更难外包", "创造会重新被看见"],
                    "visual_intent": "still centered statement"
                },
                {
                    "slide_number": 2,
                    "role": "problem",
                    "title": "很多人的焦虑，不是怕没有工作，而是怕自己只剩可替代的部分",
                    "key_point": "如果一个人的价值只等于执行效率，那么意义感会先于岗位一起被侵蚀。",
                    "visual": "quiet split reflection",
                    "claim": "很多人的焦虑，不是怕没有工作，而是怕自己只剩可替代的部分",
                    "explanation": "如果一个人的价值只等于执行效率，那么意义感会先于岗位一起被侵蚀。",
                    "supporting_facts": ["重复劳动最先被接管", "纯执行型价值缩水", "意义感来自不可替代之处"],
                    "visual_intent": "split reflection on anxiety and substitution"
                },
                {
                    "slide_number": 3,
                    "role": "driver",
                    "title": "未来更有意义的工作，通常会围绕三件事重新定价",
                    "key_point": "判断、连接与创造，共同构成 AI 难以完全替代的工作核心。",
                    "visual": "stat meditation",
                    "claim": "未来更有意义的工作，通常会围绕三件事重新定价",
                    "explanation": "判断、连接与创造，共同构成 AI 难以完全替代的工作核心。",
                    "supporting_facts": ["判断", "连接", "创造"],
                    "visual_intent": "three-anchor stat composition"
                },
                {
                    "slide_number": 4,
                    "role": "decision",
                    "title": "与其问AI会不会抢走工作，不如先问：我愿意把自己训练成什么样的人",
                    "key_point": "比起守住旧任务，更重要的是把自己推向更会判断、更能合作、更敢创造的位置。",
                    "visual": "vertical decision",
                    "claim": "与其问AI会不会抢走工作，不如先问：我愿意把自己训练成什么样的人",
                    "explanation": "比起守住旧任务，更重要的是把自己推向更会判断、更能合作、更敢创造的位置。",
                    "supporting_facts": ["训练判断力", "训练协作力", "训练创造力"],
                    "visual_intent": "vertical question as decision point",
                },
                {
                    "slide_number": 5,
                    "role": "closing",
                    "title": "工作的意义，终究不在于你替代了多少动作，而在于你承担了多少方向",
                    "key_point": "AI 可以帮助人做得更快，但只有人能决定什么值得做、为何而做、以及做完以后愿意为谁负责。",
                    "visual": "vertical close",
                    "claim": "工作的意义，终究不在于你替代了多少动作，而在于你承担了多少方向",
                    "explanation": "AI 可以帮助人做得更快，但只有人能决定什么值得做、为何而做、以及做完以后愿意为谁负责。",
                    "supporting_facts": ["值得做什么", "为何而做", "愿意为谁负责"],
                    "visual_intent": "vertical closing seal",
                },
            ],
        },
        "runtime": {"editing_mode": True, "presenter_mode": True, "watermark_mode": "injected-last-slide", "export_intent": "none"},
        "plan_view": {"emit_planning_view": False, "planning_view_path": "PLANNING.md"},
        "timing": {"estimate": {"plan": "1m", "generate": "1m", "validate": "1m", "polish": "1m", "total": "4m"}, "actual": {"plan": "0m", "generate": "0m", "validate": "0m", "polish": "0m", "total": "0m"}},
        "notes": "",
    }
    html_text, _packet, _style_contract = render_from_brief(brief)

    assert 'zen-vertical-title' in html_text
    assert '>先问自己<' in html_text


# ── Custom theme tests ──────────────────────────────────────────────────


def test_resolve_custom_theme():
    """Kingdee / kingdee / Custom: kingdee all resolve to themes/kingdee/reference.md."""
    from low_context import resolve_style_reference, discover_custom_themes

    themes = discover_custom_themes()
    assert "kingdee" in themes, f"Expected 'kingdee' in custom themes, got {list(themes.keys())}"

    ref = resolve_style_reference("Kingdee")
    assert ref.exists()
    assert ref.name == "reference.md"
    assert ref.parent.name == "kingdee"

    ref_lower = resolve_style_reference("kingdee")
    assert ref_lower == ref

    ref_prefix = resolve_style_reference("Custom: kingdee")
    assert ref_prefix == ref


def test_compile_custom_contract():
    """compile_style_contract('Kingdee') produces contract with preset='Kingdee', not 'Reference'."""
    from low_context import compile_style_contract

    contract = compile_style_contract("Kingdee")
    assert contract["preset"] == "Kingdee", f"Expected 'Kingdee', got '{contract['preset']}'"
    assert "themes/kingdee/reference.md" in contract["source_path"]
    assert len(contract.get("tokens", {})) > 0
    assert len(contract.get("css_blocks", [])) > 0
    assert contract["allowed_layout_ids"] == [
        "title_grid",
        "contents_index",
        "column_content",
        "stat_block",
        "geometric_diagram",
        "data_table",
        "pull_quote",
        "toc",
        "cta_close",
    ]


def test_render_custom_theme():
    """render_from_brief with Kingdee preset produces valid HTML without RenderError."""
    from low_context import render_from_brief, StyleContractError

    brief = read_json(AUTO_DEMO)
    brief["style"]["preset"] = "Kingdee"
    brief["title"] = "Kingdee Test Deck"

    html_text, packet, contract = render_from_brief(brief)

    assert len(html_text) > 1000
    assert 'data-preset="Kingdee"' in html_text
    assert packet["preset_support_tier"] == "custom"
    assert contract["preset"] == "Kingdee"

    soup = BeautifulSoup(html_text, "html.parser")
    slides = soup.select("section.slide")
    layout_classes = {
        class_name
        for slide in slides
        for class_name in slide.get("class", [])
        if class_name.startswith("layout-")
    }
    assert layout_classes == {
        "layout-title_grid",
        "layout-contents_index",
        "layout-column_content",
        "layout-stat_block",
        "layout-geometric_diagram",
        "layout-pull_quote",
    }
    for slide in slides:
        export_role = slide["data-export-role"]
        layout_id = "title_grid" if export_role == "title" else export_role
        assert f"layout-{layout_id}" in slide.get("class", [])


def test_preset_support_custom():
    """preset_support_tier('Kingdee') returns 'custom', explicit_selection_is_allowed returns True."""
    from preset_support import preset_support_tier, canonical_preset_name, explicit_selection_is_allowed

    assert preset_support_tier("Kingdee") == "custom"
    assert canonical_preset_name("Kingdee") == "Kingdee"
    assert explicit_selection_is_allowed("Kingdee") is True
    assert explicit_selection_is_allowed("kingdee") is True


def test_title_profile_custom():
    """resolve_title_profile('Kingdee') returns default profile without KeyError."""
    from title_profiles import resolve_title_profile

    profile = resolve_title_profile("Kingdee")
    assert profile["profile"] == "horizontal_balanced_left_anchor"
    assert profile["preset"] == "Kingdee"


def test_custom_theme_render_has_shared_shell():
    """Rendered custom theme HTML contains the shared shell markers (scroll-snap, SlidePresentation, data-notes)."""
    from low_context import render_from_brief

    brief = read_json(AUTO_DEMO)
    brief["style"]["preset"] = "Kingdee"
    brief["title"] = "Kingdee Shell Test"

    html_text, _, _ = render_from_brief(brief)

    assert "scroll-snap-type" in html_text
    assert "SlidePresentation" in html_text
    assert "data-notes" in html_text


def test_custom_theme_render_slide_count():
    """Rendered custom theme HTML has the correct number of slides."""
    from low_context import render_from_brief

    brief = read_json(AUTO_DEMO)
    brief["style"]["preset"] = "Kingdee"
    brief["title"] = "Kingdee Slide Count"
    expected_pages = brief["deck"]["page_count"]

    html_text, _, _ = render_from_brief(brief)

    soup = BeautifulSoup(html_text, "html.parser")
    slides = soup.find_all(class_="slide")
    assert len(slides) == expected_pages, f"Expected {expected_pages} slides, got {len(slides)}"


def test_custom_theme_resolve_strips_custom_prefix():
    """'Custom: <name>' and 'custom: <name>' both resolve correctly."""
    from low_context import resolve_style_reference

    ref1 = resolve_style_reference("Custom: kingdee")
    ref2 = resolve_style_reference("custom: kingdee")
    ref3 = resolve_style_reference("kingdee")

    assert ref1 == ref2 == ref3
    assert ref1.name == "reference.md"


def test_custom_theme_direct_reference_path_renders_with_canonical_theme_name():
    from low_context import render_from_brief, resolve_style_reference

    brief = read_json(AUTO_DEMO)
    brief["style"]["preset"] = str(resolve_style_reference("Kingdee"))
    brief["title"] = "Kingdee Direct Path"

    html_text, packet, contract = render_from_brief(brief)

    assert 'data-preset="Kingdee"' in html_text
    assert packet["renderer_strategy"] == "custom_theme"
    assert packet["preset_support_tier"] == "custom"
    assert contract["preset"] == "Kingdee"


def test_custom_theme_built_in_presets_unaffected():
    """Built-in presets still resolve and render correctly after custom theme changes."""
    from low_context import resolve_style_reference, compile_style_contract

    for preset in ["Swiss Modern", "Enterprise Dark", "Data Story", "Chinese Chan"]:
        ref = resolve_style_reference(preset)
        assert ref.exists(), f"Built-in preset {preset} not found at {ref}"
        assert "themes/" not in str(ref), f"Built-in {preset} incorrectly resolved to themes/"

        contract = compile_style_contract(preset)
        assert contract["preset"] == preset


def test_custom_theme_e2e_render_and_validate(tmp_path):
    """End-to-end: render a Kingdee deck, write to file, run validate_html --strict."""
    from low_context import render_from_brief

    sys.path.insert(0, str(SCRIPTS))
    from validate_html import validate

    brief = read_json(AUTO_DEMO)
    brief["style"]["preset"] = "Kingdee"
    brief["title"] = "Kingdee E2E Test Deck"

    html_text, packet, contract = render_from_brief(brief)

    output_path = tmp_path / "kingdee-e2e.html"
    output_path.write_text(html_text, encoding="utf-8")

    assert output_path.exists()
    assert len(html_text) > 5000

    # Run required (non-strict) validation
    passed = validate(output_path, strict=False)
    assert passed, f"Required validation failed for Kingdee deck at {output_path}"


def test_custom_theme_provenance_attrs():
    """Custom theme HTML has correct provenance attributes on body."""
    from low_context import render_from_brief

    brief = read_json(AUTO_DEMO)
    brief["style"]["preset"] = "Kingdee"
    brief["title"] = "Kingdee Provenance"

    html_text, packet, _ = render_from_brief(brief)

    soup = BeautifulSoup(html_text, "html.parser")
    body = soup.find("body")
    assert body is not None
    assert body.get("data-preset") == "Kingdee"
    assert body.get("data-generator") == "kai-slide-creator"
    assert body.get("data-render-path") is not None


def test_custom_theme_no_preset_collision():
    """A folder name that happens to match a built-in preset should still resolve to built-in."""
    from low_context import resolve_style_reference

    # "swiss modern" is a built-in, should resolve to references/ not themes/
    ref = resolve_style_reference("Swiss Modern")
    assert "references/" in str(ref)
    assert "themes/" not in str(ref)


def test_enterprise_dark_insight_pull_exports_semantic_title_slot():
    from low_context import render_from_brief

    brief = read_json(ROOT / "evals" / "preset-surface-all" / "cases" / "image-heavy-restyle-brief.json")
    brief["style"]["preset"] = "Enterprise Dark"

    html_text, _, _ = render_from_brief(brief)
    soup = BeautifulSoup(html_text, "html.parser")
    insight_slides = soup.select('.slide[data-export-role="insight_pull"]')

    assert insight_slides
    for slide in insight_slides:
        title = slide.select_one('[data-export-slot="title"]')
        assert title is not None
        assert title.get_text(" ", strip=True)


def test_enterprise_dark_contrast_split_signal_detection():
    from low_context import _has_before_after_signal

    # Strong signals should match
    assert _has_before_after_signal("before and after comparison")
    assert _has_before_after_signal("之前之后")
    assert _has_before_after_signal("痛点与方案")
    assert _has_before_after_signal("pain and solution")
    assert _has_before_after_signal("before after comparison")

    # Weak signals should NOT match
    assert not _has_before_after_signal("Validate Before Trust")
    assert not _has_before_after_signal("before the change")
    assert not _has_before_after_signal("升级计划")
    assert not _has_before_after_signal("改变策略")
    assert not _has_before_after_signal("transform")
    assert not _has_before_after_signal("从 POC 走到生产")  # common phrase, not contrast


def test_enterprise_dark_contrast_split_render():
    from low_context import _render_enterprise_contrast_split

    spec = {
        "slide_number": 1,
        "role": "before-after",
        "layout_id": "contrast_split",
        "title": "Before vs After",
        "claim": "对比",
        "key_point": "关键点",
        "supporting_items": ["工具调用错误率上升", "记忆失效", "统一翻译层解耦", "Harness 持久化"],
        "evidence_items": [],
        "supporting_facts": [],
        "speaker_note": "note",
        "visual": "before after comparison",
        "visual_intent": "contrast",
        "chart_policy": "auto",
        "quality_tier": "tier0",
    }
    html = _render_enterprise_contrast_split(spec, 9)

    assert 'data-export-role="contrast_split"' in html
    assert "ent-contrast-split" in html
    assert "ent-contrast-block--negative" in html
    assert "ent-contrast-block--positive" in html
    assert "Before" in html
    assert "After" in html
    assert "&#x2717;" in html  # ✗ mark
    assert "&#x2713;" in html  # ✓ mark
    assert 'class="ent-contrast-item"' in html


def test_enterprise_dark_signal_detection_in_routing():
    """Test that contrast_split signal detection triggers before resolver runs."""
    from low_context import (
        build_slide_spec, build_render_packet, _has_before_after_signal,
        ENTERPRISE_ROLE_LAYOUTS, _resolve_layout_with_usage_rules, _preset_usage_rules,
    )

    # Verify role mapping exists
    assert ENTERPRISE_ROLE_LAYOUTS.get("comparison") == "comparison_matrix"
    assert ENTERPRISE_ROLE_LAYOUTS.get("before-after") == "contrast_split"
    assert ENTERPRISE_ROLE_LAYOUTS.get("pain-solution") == "contrast_split"

    # Verify signal detection works with realistic content
    assert _has_before_after_signal("Before vs After", "痛点与方案对比", "之前之后的对比", "before after comparison")
    assert _has_before_after_signal("痛点与方案")
    assert _has_before_after_signal("之前之后")
    assert _has_before_after_signal("before after comparison")
    assert not _has_before_after_signal("从旧系统到新系统")  # "从...到" is no longer a signal
    assert not _has_before_after_signal("升级计划")
    assert not _has_before_after_signal("改变策略")
