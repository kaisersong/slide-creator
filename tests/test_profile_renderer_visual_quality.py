from __future__ import annotations

import copy
import re
import sys
from pathlib import Path

import pytest
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from low_context import render_from_brief  # noqa: E402
from compare_demo_parity import PRESETS, analyze_html  # noqa: E402
from preset_profile_renderer import _title_lines  # noqa: E402
from preset_profile_specs import PROFILE_SPECS  # noqa: E402


DEMO_SLUGS_BY_PRESET = {preset: demo_slug for preset, demo_slug, _output_slug in PRESETS}
DEMO_ANCHOR_SELECTORS = {
    "Bold Signal": (".bold-hero-card", ".bold-title", ".bold-ghost-number"),
    "Electric Studio": (".pill", ".stats", ".stat-value"),
    "Neo-Brutalism": (".brute-title", ".brute-tag", ".code-block"),
    "Neo-Retro Dev Deck": (".pill", ".stats", ".stat-value"),
    "Notebook Tabs": (".pill", ".stats", ".stat-value"),
}

DEMO_CLASS_STOPWORDS = {
    "slide",
    "content",
    "reveal",
    "visible",
    "active",
    "nav-dots",
    "progress-bar",
    "edit-hotzone",
    "edit-toggle",
    "slide-credit",
    "slide-num-label",
}


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _minimal_brief_for_preset(preset: str) -> dict:
    slides = [
        {
            "slide_number": index,
            "role": role,
            "title": title,
            "claim": title,
            "key_point": key_point,
            "explanation": key_point,
            "visual": visual,
            "visual_intent": visual,
            "preferred_layout_family": visual,
            "chart_policy": "auto",
            "supporting_facts": facts,
        }
        for index, (role, title, key_point, visual, facts) in enumerate(
            [
                (
                    "cover",
                    "kai-slide-creator ships a single HTML deck",
                    "A browser-native deck keeps planning, presenting, editing, and export in one file.",
                    "hero",
                    ["single HTML output", "present mode", "edit mode"],
                ),
                (
                    "problem",
                    "Slide tooling still creates avoidable friction",
                    "Teams lose time to template hunting, build systems, and fragile export steps.",
                    "comparison",
                    ["template drift", "build friction", "export mismatch"],
                ),
                (
                    "solution",
                    "The generator turns a brief into a styled deck",
                    "A structured BRIEF selects the preset, layout intent, runtime shell, and validation path.",
                    "workflow",
                    ["BRIEF.json", "style contract", "strict validate"],
                ),
                (
                    "evidence",
                    "Quality must be visible, not only syntactic",
                    "A valid deck still fails if its preset-specific components and first viewport are unrecognizable.",
                    "evidence",
                    ["visible components", "style parity", "first viewport"],
                ),
                (
                    "cta_close",
                    "Make every explicit preset usable",
                    "All profile presets should render honestly without pretending they are deterministic core.",
                    "close",
                    ["explicit preset", "profile renderer", "honest eval"],
                ),
            ],
            start=1,
        )
    ]
    return {
        "schema_version": 1,
        "brief_id": f"profile-quality-{_slugify(preset)}",
        "mode": "auto",
        "language": "en",
        "title": f"{preset} Visual Quality",
        "audience": "slide-creator maintainers",
        "desired_action": "verify profile renderer visual quality",
        "deck": {
            "deck_type": "user-content",
            "page_count": len(slides),
            "output_format": "html-slides",
        },
        "style": {
            "preset": preset,
            "tone": "clear and concrete",
            "visual_density": "medium",
        },
        "content": {
            "source_policy": "distill-only",
            "must_include": ["single HTML output", "explicit preset", "strict validate"],
            "must_avoid": ["preset substitution", "marker-only style", "hidden class injection"],
            "global_facts": ["zero dependency HTML", "present mode", "edit mode"],
        },
        "narrative": {
            "thesis": "Profile presets must generate visible preset-specific decks.",
            "page_roles": [slide["role"] for slide in slides],
            "slides": slides,
        },
        "runtime": {
            "editing_mode": True,
            "presenter_mode": True,
            "watermark_mode": "injected-last-slide",
            "export_intent": "none",
        },
        "plan_view": {
            "emit_planning_view": False,
            "planning_view_path": "PLANNING.md",
        },
        "timing": {
            "estimate": {"plan": "1m", "generate": "1m", "validate": "1m", "polish": "0m", "total": "3m"},
            "actual": {"plan": "0m", "generate": "0m", "validate": "0m", "polish": "0m", "total": "0m"},
        },
    }


def _render_profile(preset: str) -> tuple[str, dict]:
    html_text, packet, _contract = render_from_brief(_minimal_brief_for_preset(preset))
    assert packet["renderer_strategy"] == "unified_profile"
    return html_text, packet


def _zh_mixed_brief_for_preset(preset: str) -> dict:
    brief = copy.deepcopy(_minimal_brief_for_preset(preset))
    brief["language"] = "zh-CN"
    brief["title"] = f"{preset} 中文混排视觉质量"
    mixed_slides = [
        (
            "cover",
            "交付提速来自链路重排，不只是多一个 agent",
            "把澄清、实现、验收和复盘压到同一条工作流里，收益才会稳定出现。",
            ["agent 协作", "验收门禁", "HTML 单文件"],
        ),
        (
            "problem",
            "如果任务边界不清，agent 只会把返工提得更快",
            "模板和验收门禁要比生成速度更早进入链路，否则只是更快制造返工。",
            ["需求含混", "风格漂移", "人工补救"],
        ),
        (
            "solution",
            "把 kai-slide-creator 放进真实验收链路",
            "生成器必须同时处理风格、版式、文字长度和浏览器截图级 QA。",
            ["kai-slide-creator", "Playwright 截图", "视觉审计"],
        ),
        (
            "evidence",
            "质量证据来自页面，而不是类名相似度",
            "相似度只能说明风格来源，不能证明内容没有越界、重叠或断词。",
            ["布局边界", "组件重叠", "英文断词"],
        ),
        (
            "cta_close",
            "让每个显式预设都能直接交付",
            "预设渲染器要对真实内容负责，不能只复刻 demo 骨架。",
            ["显式预设", "稳定节奏", "可用成品"],
        ),
    ]
    for slide, (role, title, key_point, facts) in zip(brief["narrative"]["slides"], mixed_slides, strict=False):
        slide["role"] = role
        slide["title"] = title
        slide["claim"] = title
        slide["key_point"] = key_point
        slide["explanation"] = key_point
        slide["supporting_facts"] = facts
    brief["narrative"]["page_roles"] = [slide["role"] for slide in brief["narrative"]["slides"]]
    return brief


def _agent_delivery_review_brief_for_preset(preset: str) -> dict:
    brief = copy.deepcopy(_minimal_brief_for_preset(preset))
    brief["language"] = "zh-CN"
    brief["title"] = "Agent Delivery Review"
    brief["deck"]["page_count"] = 8
    rows = [
        (
            "cover",
            "交付提速来自链路重排，不只是多一个 agent",
            "把澄清、实现、验收和复盘压到同一条工作流里，收益才会稳定出现。",
            "hero",
            ["agent 协作", "验收门禁", "HTML 单文件"],
        ),
        (
            "problem",
            "如果任务边界不清，agent 只会把返工提得更快",
            "需求含混、验收缺位和上下文断裂，会把自动化放大成更多噪声。",
            "comparison",
            ["需求含混", "风格漂移", "人工补救"],
        ),
        (
            "baseline",
            "当前最好用的路径，是先把输入和门禁固定下来",
            "模板、参考实现和验收标准比额外抽象层更直接决定结果稳定性。",
            "grid",
            ["Bold Signal", "Aurora Mesh", "Neon Cyber", "Swiss Modern", "Modern Newspaper", "Notebook Tabs"],
        ),
        (
            "workflow",
            "澄清输入、执行产出、校验结果、记录复盘必须在同一轮内闭合",
            "稳定场景先做深，比同时铺开多个实验更有效。",
            "workflow",
            ["澄清输入", "执行产出", "校验结果", "记录复盘"],
        ),
        (
            "evidence",
            "稳定场景先做深，比同时铺开多个实验更有效",
            "高频、低耦合、可验证的任务更适合作为第一批标准化路径。",
            "evidence",
            ["F5 播放", "P 演讲", "E 编辑"],
        ),
        (
            "tradeoff",
            "速度提升必须换来更强的验收，而不是更弱的判断",
            "把 reviewer 从重复执行中解放出来，不等于把质量判断整体省掉。",
            "workflow",
            ["/slide-creator --plan", "/slide-creator --generate", "/slide-creator --review"],
        ),
        (
            "decision",
            "下一阶段应优先复制高频稳定场景",
            "先把已经跑通的工作流扩展到相邻任务，再处理边缘场景。",
            "decision",
            ["零依赖", "21 种设计预设", "浏览器即环境"],
        ),
        (
            "closing",
            "更短的交付链路，才是 agent 团队真正的复利",
            "团队应该把复利押在可复用工作流和门禁，而不是押在更多即兴自动化。",
            "close",
            ["/slide-creator \"你的主题\"", "clawhub install kai-slide-creator"],
        ),
    ]
    brief["narrative"]["slides"] = [
        {
            "slide_number": index,
            "role": role,
            "title": title,
            "claim": title,
            "key_point": key_point,
            "explanation": key_point,
            "visual": visual,
            "visual_intent": visual,
            "preferred_layout_family": visual,
            "chart_policy": "auto",
            "supporting_facts": facts,
        }
        for index, (role, title, key_point, visual, facts) in enumerate(rows, start=1)
    ]
    brief["narrative"]["page_roles"] = [slide["role"] for slide in brief["narrative"]["slides"]]
    return brief


def _render_profile_from_brief(preset: str, brief: dict) -> tuple[str, dict]:
    html_text, packet, _contract = render_from_brief(brief)
    assert packet["renderer_strategy"] == "unified_profile"
    assert packet["canonical_preset"] == preset
    return html_text, packet


def _line_pair_splits_token(lines: list[str], token: str) -> bool:
    token_key = token.lower().replace(" ", "")
    for first, second in zip(lines, lines[1:], strict=False):
        first_key = first.lower().replace(" ", "")
        second_key = second.lower().replace(" ", "")
        joined_key = first_key + second_key
        if token_key in joined_key and token_key not in first_key and token_key not in second_key:
            return True
    return False


def _style_text(html_text: str) -> str:
    soup = BeautifulSoup(html_text, "html.parser")
    return "\n".join(style.get_text("\n") for style in soup.find_all("style"))


def _browser_layout_issues(html_text: str, tmp_path: Path, stem: str) -> list[str]:
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    html_path = tmp_path / f"{stem}.html"
    html_path.write_text(html_text, encoding="utf-8")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
        page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        issues = page.evaluate(
            """
            () => {
                const isVisible = (el) => {
                    const style = getComputedStyle(el);
                    const rect = el.getBoundingClientRect();
                    return style.display !== 'none' && style.visibility !== 'hidden' &&
                        Number(style.opacity || 1) > 0.001 && rect.width > 0 && rect.height > 0;
                };
                const rect = (el) => {
                    const r = el.getBoundingClientRect();
                    return { left: r.left, right: r.right, top: r.top, bottom: r.bottom, width: r.width, height: r.height };
                };
                const intersects = (a, b) => !(a.right <= b.left || b.right <= a.left || a.bottom <= b.top || b.bottom <= a.top);
                const issues = [];
                for (const slide of document.querySelectorAll('section.slide')) {
                    slide.scrollIntoView();
                    const slideRect = rect(slide);
                    const slideId = slide.id || '(missing slide id)';
                    const visibleGhosts = [...slide.querySelectorAll('.bold-ghost,.slide-num')].filter(isVisible);
                    if (document.body.dataset.profileSpec === 'bold-signal' && visibleGhosts.length > 1) {
                        issues.push(`${slideId}: duplicate visible ghost markers: ${visibleGhosts.map((el) => el.textContent.trim()).join(',')}`);
                    }
                    const headings = [...slide.querySelectorAll('h1,h2,h3,.signal-block,.bold-hero-card')].filter(isVisible);
                    for (const ghost of visibleGhosts) {
                        const ghostRect = rect(ghost);
                        for (const target of headings) {
                            if (intersects(ghostRect, rect(target))) {
                                issues.push(`${slideId}: ${ghost.className} overlaps ${target.tagName}.${target.className}`);
                            }
                        }
                    }
                    const contentTargets = [
                        ...slide.querySelectorAll('.slide-content > *, .bold-callout, .bold-cmd, .aurora-card, .code-block, .cta-pill')
                    ].filter(isVisible);
                    for (const target of contentTargets) {
                        const targetRect = rect(target);
                        if (
                            targetRect.left < slideRect.left - 1 ||
                            targetRect.right > slideRect.right + 1 ||
                            targetRect.top < slideRect.top - 1 ||
                            targetRect.bottom > slideRect.bottom + 1
                        ) {
                            issues.push(`${slideId}: ${target.tagName}.${target.className} overflows slide bounds`);
                        }
                    }
                }
                return issues;
            }
            """
        )
        browser.close()
    return list(issues)


def _demo_feature_path(preset: str) -> Path:
    slug = DEMO_SLUGS_BY_PRESET[preset]
    en_path = ROOT / "demos" / f"{slug}-en.html"
    zh_path = ROOT / "demos" / f"{slug}-zh.html"
    return en_path if en_path.exists() else zh_path


def _rendered_features(tmp_path: Path, preset: str):
    html_text, _packet = _render_profile(preset)
    candidate_path = tmp_path / f"{_slugify(preset)}.html"
    candidate_path.write_text(html_text, encoding="utf-8")
    return analyze_html(candidate_path), html_text


def _assert_demo_derived(packet: dict, preset: str) -> None:
    source = packet["body_data_attrs"].get("data-profile-renderer-source", "")
    assert source.startswith("demo-derived:"), f"{preset} did not use demo-derived renderer: {source}"


def _key_component_classes(features) -> set[str]:
    return {
        class_name
        for class_name in features.classes
        if class_name not in DEMO_CLASS_STOPWORDS
        and not class_name.startswith("profile-")
        and not class_name.startswith("preset-")
        and not re.fullmatch(r"slide-?\d+", class_name)
    }


def test_profile_renderer_reuses_demo_structure_anchors_for_worst_gap_presets():
    for preset, selectors in DEMO_ANCHOR_SELECTORS.items():
        html_text, _packet = _render_profile(preset)
        soup = BeautifulSoup(html_text, "html.parser")

        missing = [selector for selector in selectors if soup.select_one(selector) is None]
        assert not missing, f"{preset} missing demo structure anchors: {missing}"


def test_profile_renderer_does_not_split_latin_tokens_inside_cjk_titles():
    for preset in ("Notebook Tabs", "Electric Studio", "Pastel Geometry"):
        html_text, _packet = _render_profile_from_brief(preset, _zh_mixed_brief_for_preset(preset))
        soup = BeautifulSoup(html_text, "html.parser")
        title_lines = [node.get_text(" ", strip=True) for node in soup.select(".title-line")]

        assert title_lines, f"{preset} did not render balanced title lines"
        assert not _line_pair_splits_token(title_lines, "agent"), f"{preset} split agent across title lines"
        assert not _line_pair_splits_token(
            title_lines, "kai-slide-creator"
        ), f"{preset} split kai-slide-creator across title lines"
        assert not _line_pair_splits_token(title_lines, "链路重排"), f"{preset} split 链路重排 across title lines"


def test_profile_renderer_does_not_force_moderate_cjk_titles_to_wrap_early():
    title = "用同一把尺子比较速度、质量与返工"

    assert _title_lines(title) == [title]


def test_profile_renderer_title_line_class_is_not_split_or_signature_polluted():
    polluted = []
    for preset in PROFILE_SPECS:
        html_text, _packet = _render_profile_from_brief(preset, _zh_mixed_brief_for_preset(preset))
        soup = BeautifulSoup(html_text, "html.parser")
        signature_classes = set(PROFILE_SPECS[preset].visible_signature_classes)
        title_lines = soup.select(".title-line")

        for node in title_lines:
            classes = set(node.get("class", []))
            character_split = {"t", "i", "l", "e"} <= classes
            extra_signature = classes & signature_classes
            if character_split or extra_signature:
                polluted.append((preset, sorted(classes), node.get_text(" ", strip=True)))

    assert not polluted


def test_profile_renderer_uses_short_localized_labels_for_zh_demo_slots():
    html_text, _packet = _render_profile_from_brief("Notebook Tabs", _zh_mixed_brief_for_preset("Notebook Tabs"))
    soup = BeautifulSoup(html_text, "html.parser")
    labels = [
        node.get_text(" ", strip=True)
        for node in soup.select(".nb-label, .elec-label, .label, .eyebrow, .hero-brand, .brute-tag, .badge")
        if node.get_text(" ", strip=True)
    ]
    micro_labels = [
        node.get_text(" ", strip=True)
        for node in soup.select(".nb-label, .elec-label, .label, .eyebrow, .brute-tag, .badge")
        if node.get_text(" ", strip=True)
    ]

    assert labels
    assert all("Notebook Tabs /" not in label for label in labels)
    assert all(len(label) <= 12 for label in micro_labels if "/" not in label)


def test_profile_renderer_marks_decorative_empty_pills_as_presentational():
    html_text, _packet = _render_profile_from_brief("Pastel Geometry", _zh_mixed_brief_for_preset("Pastel Geometry"))
    soup = BeautifulSoup(html_text, "html.parser")
    empty_pills = [
        node
        for node in soup.select(".pills, .pill-bar")
        if not node.get_text(" ", strip=True)
    ]

    assert empty_pills
    for node in empty_pills:
        assert node.get("aria-hidden") == "true"
        assert node.get("role") == "presentation"


def test_profile_renderer_emits_visual_safety_css_for_demo_derived_content():
    html_text, _packet = _render_profile_from_brief("Electric Studio", _zh_mixed_brief_for_preset("Electric Studio"))
    css_text = _style_text(html_text)

    assert ".profile-fit-title" in css_text
    assert "word-break: keep-all" in css_text
    assert "min-width: 0" in css_text
    assert re.search(
        r'\.profile-fit-title\s+\.title-line\s*\{[^}]*white-space:\s*normal\s*!important',
        css_text,
        re.DOTALL,
    )


def test_profile_renderer_emits_readability_hardening_css_for_text_and_command_pills():
    html_text, _packet = _render_profile_from_brief(
        "Aurora Mesh", _agent_delivery_review_brief_for_preset("Aurora Mesh")
    )
    css_text = _style_text(html_text)

    command_rule_start = css_text.find('body[data-renderer-strategy="unified_profile"] .code-block')
    assert command_rule_start != -1
    command_rule_end = css_text.find("}", command_rule_start)
    command_rule = css_text[command_rule_start:command_rule_end]
    assert "letter-spacing: 0 !important" in command_rule
    for selector in (".code-block", ".bold-cmd", ".np-cmd"):
        assert selector in command_rule
    assert re.search(
        r'body\[data-renderer-strategy="unified_profile"\]\s+:is\(p,\s*li,\s*\.body-text,[^)]*'
        r"\)\s*\{[^}]*opacity:\s*1\s*!important",
        css_text,
        re.DOTALL,
    )
    assert "body[data-renderer-strategy=\"unified_profile\"][data-profile-spec=\"aurora-mesh\"]" in css_text
    assert "--profile-muted: #f7fbff;" in css_text


def test_profile_renderer_injects_runtime_auto_contrast_for_mixed_demo_backgrounds():
    html_text, packet = _render_profile_from_brief(
        "Electric Studio", _agent_delivery_review_brief_for_preset("Electric Studio")
    )

    assert packet["body_data_attrs"]["data-profile-auto-contrast"] == "true"
    assert "function applyProfileAutoContrast" in html_text
    assert "data-profile-contrast-adjusted" in html_text


def test_glassmorphism_cover_subtitle_uses_readable_text_surface():
    html_text, _packet = _render_profile_from_brief(
        "Glassmorphism", _agent_delivery_review_brief_for_preset("Glassmorphism")
    )

    assert 'body[data-renderer-strategy="unified_profile"][data-profile-spec="glassmorphism"] #slide-1 > .profile-content > p.glass-body' in html_text
    assert "color: #101828 !important;" in html_text
    assert "background: rgba(255, 255, 255, 0.78) !important;" in html_text


def test_electric_studio_cover_mixed_cjk_title_uses_long_fit_class():
    html_text, _packet = _render_profile_from_brief("Electric Studio", _zh_mixed_brief_for_preset("Electric Studio"))
    soup = BeautifulSoup(html_text, "html.parser")
    title = soup.select_one("#slide-1 h1, #slide-1 h2, #slide-1 .elec-title")
    assert title is not None

    classes = set(title.get("class", []))
    assert "profile-fit-title" in classes
    assert classes & {"profile-fit-title-long", "profile-fit-title-xlong", "profile-fit-title-xxlong"}


def test_creative_voltage_cover_keeps_demo_blue_canvas_and_unpolluted_cover_container():
    html_text, _packet = _render_profile_from_brief(
        "Creative Voltage", _agent_delivery_review_brief_for_preset("Creative Voltage")
    )
    soup = BeautifulSoup(html_text, "html.parser")
    css_text = _style_text(html_text)
    cover_inner = soup.select_one("#slide-1 .cover-inner")
    title_accent = soup.select_one("#slide-1 .title-accent")

    assert cover_inner is not None
    assert "pill" not in cover_inner.get("class", [])
    assert title_accent is not None
    assert "body[data-renderer-strategy=\"unified_profile\"][data-profile-spec=\"creative-voltage\"] #slide-1 .title-accent" in css_text
    assert "color: #d4ff00 !important;" in css_text
    assert "display: none !important;" not in css_text.split('body[data-renderer-strategy="unified_profile"][data-profile-spec="creative-voltage"] #slide-1 .title-accent', 1)[-1][:120]


def test_electric_studio_cover_preserves_demo_metric_anchors():
    html_text, _packet = _render_profile_from_brief(
        "Electric Studio", _agent_delivery_review_brief_for_preset("Electric Studio")
    )
    soup = BeautifulSoup(html_text, "html.parser")
    css_text = _style_text(html_text)

    label = soup.select_one("#slide-1 .elec-label")
    numbers = [node.get_text(strip=True) for node in soup.select("#slide-1 .elec-stat-number")]

    assert label is not None
    assert label.get_text(strip=True).lower().startswith("slide-creator")
    assert "bottom-panel" not in label.get("class", [])
    assert "elec-quote-block" not in label.get("class", [])
    assert numbers[:3] == ["21", "0", "∞"]
    electric_mobile_css = css_text.split(
        'body[data-renderer-strategy="unified_profile"][data-profile-spec="electric-studio"] #slide-1 .elec-body',
        1,
    )[-1][:360]
    assert "-webkit-line-clamp: 2" in electric_mobile_css
    assert "overflow-wrap: anywhere !important;" in electric_mobile_css


def test_demo_derived_profile_preserves_demo_brand_mark():
    html_text, _packet = _render_profile_from_brief(
        "Electric Studio", _agent_delivery_review_brief_for_preset("Electric Studio")
    )
    soup = BeautifulSoup(html_text, "html.parser")

    brand_mark = soup.select_one("#brand-mark")

    assert brand_mark is not None
    assert brand_mark.get_text(strip=True) == "slide-creator"


def test_terminal_green_demo_derived_output_includes_scanlines_instance():
    html_text, _packet = _render_profile_from_brief(
        "Terminal Green", _agent_delivery_review_brief_for_preset("Terminal Green")
    )
    soup = BeautifulSoup(html_text, "html.parser")

    scanlines = soup.select_one("body > .terminal-scanlines")
    assert scanlines is not None
    assert scanlines.get("aria-hidden") == "true"


def test_split_pastel_cover_subtitle_has_gate_safe_contrast():
    html_text, _packet = _render_profile_from_brief(
        "Split Pastel", _agent_delivery_review_brief_for_preset("Split Pastel")
    )
    css_text = _style_text(html_text)

    selector = 'body[data-renderer-strategy="unified_profile"][data-profile-spec="split-pastel"] #slide-1 .hero-sub'
    assert selector in css_text
    assert "color: #555555 !important;" in css_text.split(selector, 1)[-1][:160]


def test_notebook_tabs_signature_classes_do_not_pollute_structural_paper_container():
    html_text, _packet = _render_profile_from_brief("Notebook Tabs", _zh_mixed_brief_for_preset("Notebook Tabs"))
    soup = BeautifulSoup(html_text, "html.parser")
    feature_slide = soup.select_one("#slide-3")
    assert feature_slide is not None
    outer_paper = feature_slide.select_one(":scope > .profile-content > .paper")
    if outer_paper is None:
        outer_paper = feature_slide.select_one(":scope > .paper")

    assert outer_paper is not None
    assert "paper" in outer_paper.get("class", [])
    assert "feat-grid" not in outer_paper.get("class", [])
    assert outer_paper.select_one(".paper-content .feat-grid") is not None


def test_aurora_mesh_signature_classes_do_not_pollute_structural_layout_nodes():
    html_text, _packet = _render_profile_from_brief(
        "Aurora Mesh", _agent_delivery_review_brief_for_preset("Aurora Mesh")
    )
    soup = BeautifulSoup(html_text, "html.parser")
    visible = set(PROFILE_SPECS["Aurora Mesh"].visible_signature_classes)
    allowed = {
        "aurora-slide": {"aurora-slide"},
        "aurora-content": {"aurora-content"},
        "aurora-badge": {"aurora-badge"},
        "aurora-divider": {"aurora-divider"},
        "install-row": {"install-row"},
        "install-item": {"install-item"},
        "install-label": {"install-label"},
    }

    polluted = []
    for structural_class, allowed_visible in allowed.items():
        for node in soup.select(f".{structural_class}"):
            extra = (set(node.get("class", [])) & visible) - allowed_visible
            if extra:
                polluted.append((structural_class, sorted(extra), node.get_text(" ", strip=True)[:40]))

    assert not polluted


def test_demo_signature_classes_do_not_pollute_editorial_or_retro_text_nodes():
    cases = {
        "Creative Voltage": {
            ".feat-grid": {"voltage-neon-badge", "voltage-card", "voltage-dark-panel"},
        },
        "Vintage Editorial": {
            ".section-id": {"rule", "rule-thick", "step-editorial", "preset-grid"},
        },
        "Neo-Retro Dev Deck": {
            ".badge-row .badge": {"metrics-grid", "cmd-table", "cards-grid"},
            ".ba-list": {"cmd-table", "metrics-grid", "cards-grid"},
        },
    }

    polluted = []
    for preset, selector_map in cases.items():
        html_text, _packet = _render_profile_from_brief(preset, _agent_delivery_review_brief_for_preset(preset))
        soup = BeautifulSoup(html_text, "html.parser")
        for selector, forbidden in selector_map.items():
            for node in soup.select(selector):
                extra = set(node.get("class", [])) & forbidden
                if extra:
                    polluted.append((preset, selector, sorted(extra), node.get_text(" ", strip=True)[:40]))

    assert not polluted


def test_aurora_mesh_command_blocks_can_wrap_instead_of_single_line_pills():
    html_text, _packet = _render_profile_from_brief(
        "Aurora Mesh", _agent_delivery_review_brief_for_preset("Aurora Mesh")
    )
    css_text = _style_text(html_text)

    assert re.search(
        r'body\[data-renderer-strategy="unified_profile"\]\[data-profile-spec="aurora-mesh"\]\s+\.code-block\s*\{[^}]*white-space:\s*normal',
        css_text,
        re.DOTALL,
    )
    assert re.search(
        r'body\[data-renderer-strategy="unified_profile"\]\[data-profile-spec="aurora-mesh"\]\s+\.code-block\s*\{[^}]*overflow-wrap:\s*anywhere',
        css_text,
        re.DOTALL,
    )


def test_bold_signal_browser_layout_has_no_duplicate_ghost_or_content_overflow(tmp_path: Path):
    html_text, _packet = _render_profile_from_brief(
        "Bold Signal", _agent_delivery_review_brief_for_preset("Bold Signal")
    )
    issues = _browser_layout_issues(html_text, tmp_path, "bold-signal-layout")

    assert issues == []


def test_profile_renderer_covers_demo_component_vocabulary_for_worst_gap_presets(tmp_path: Path):
    for preset in DEMO_ANCHOR_SELECTORS:
        demo_features = analyze_html(_demo_feature_path(preset))
        candidate_features, _html_text = _rendered_features(tmp_path, preset)
        expected = _key_component_classes(demo_features)
        actual = _key_component_classes(candidate_features)
        coverage = len(expected & actual) / max(1, len(expected))

        assert coverage >= 0.55, f"{preset} demo component coverage too low: {coverage:.3f}"


def test_profile_renderer_does_not_put_all_signature_classes_on_every_slide():
    for preset in ("Paper & Ink", "Strategy Consulting"):
        html_text, _packet = _render_profile(preset)
        soup = BeautifulSoup(html_text, "html.parser")
        required = set(PROFILE_SPECS[preset].required_component_classes)
        assert required

        overloaded = []
        for slide in soup.select("section.slide"):
            classes = set(slide.get("class", []))
            if required <= classes:
                overloaded.append(slide.get("id", "(missing id)"))

        assert not overloaded, f"{preset} marker classes are injected on slide sections: {overloaded}"


def test_profile_specs_define_visible_adapters_and_background_strategy_for_all_profile_presets():
    missing: list[str] = []
    for preset, spec in PROFILE_SPECS.items():
        adapters = getattr(spec, "component_adapters", ())
        visible_classes = getattr(spec, "visible_signature_classes", ())
        background_strategy = getattr(spec, "background_strategy", "")
        if len(adapters) < 4 or not visible_classes or not background_strategy:
            missing.append(preset)

    assert not missing, "profile presets missing visible adapter specs: " + ", ".join(missing)


def test_paper_ink_profile_uses_paper_canvas_and_visible_editorial_components():
    html_text, packet = _render_profile("Paper & Ink")
    soup = BeautifulSoup(html_text, "html.parser")
    css_text = _style_text(html_text)

    _assert_demo_derived(packet, "Paper & Ink")
    assert "--bg: #faf9f7" in css_text or "--paper" in css_text
    assert ".slide-1 { background: linear-gradient" not in css_text
    assert soup.select_one(".hero-layout") is not None
    assert soup.select_one(".stats, .stat-value") is not None



def test_paper_ink_cover_uses_single_editorial_route_without_component_pileup():
    html_text, packet = _render_profile("Paper & Ink")
    soup = BeautifulSoup(html_text, "html.parser")
    cover = soup.select_one("#slide-1")
    assert cover is not None

    _assert_demo_derived(packet, "Paper & Ink")
    assert cover.select_one(".hero-layout") is not None
    assert cover.select_one(".stats, .stat-value") is not None

    piled_components = [
        selector
        for selector in (".pull-quote", ".steps")
        if cover.select_one(selector) is not None
    ]
    assert not piled_components, "Paper & Ink cover should not stack every editorial component: " + ", ".join(piled_components)


def test_strategy_consulting_cover_uses_exec_route_without_component_pileup():
    html_text, packet = _render_profile("Strategy Consulting")
    soup = BeautifulSoup(html_text, "html.parser")
    cover = soup.select_one("#slide-1")
    assert cover is not None

    _assert_demo_derived(packet, "Strategy Consulting")
    assert soup.select_one(".sc-action-title") is not None
    assert soup.select_one(".sc-evidence-card") is not None

    piled_components = [
        selector
        for selector in (".sc-reco-box", ".sc-before-after", ".sc-quote-evidence", ".sc-three-things")
        if cover.select_one(selector) is not None
    ]
    assert not piled_components, "Strategy Consulting cover should not stack every consulting component: " + ", ".join(piled_components)


def test_generic_profile_cover_does_not_render_signature_component_grid():
    for preset in ("Creative Voltage", "Glassmorphism", "Terminal Green"):
        html_text, packet = _render_profile(preset)
        soup = BeautifulSoup(html_text, "html.parser")
        cover = soup.select_one("#slide-1")
        assert cover is not None

        _assert_demo_derived(packet, preset)
        assert cover.select_one("h1, h2, .hero-title, .main-title, .glass-title") is not None
        assert cover.select(".profile-signature-grid") == []
        assert cover.select(".profile-signature-component") == []


def test_generic_profile_cover_still_has_preset_specific_visual_signature():
    for preset in ("Creative Voltage", "Electric Studio", "Modern Newspaper"):
        html_text, packet = _render_profile(preset)
        soup = BeautifulSoup(html_text, "html.parser")
        cover = soup.select_one("#slide-1")
        assert cover is not None

        _assert_demo_derived(packet, preset)
        expected = _key_component_classes(analyze_html(_demo_feature_path(preset)))
        actual = {class_name for node in cover.find_all(True) for class_name in node.get("class", [])}
        assert expected & actual, f"{preset} cover has no demo-specific visible signature class"


def test_generic_profile_non_cover_slides_use_distinct_layout_routes():
    for preset in ("Creative Voltage", "Electric Studio", "Modern Newspaper", "Neon Cyber", "Split Pastel"):
        html_text, packet = _render_profile(preset)
        soup = BeautifulSoup(html_text, "html.parser")
        _assert_demo_derived(packet, preset)

        repeated_grid_slides = [
            slide.get("id", "(missing id)")
            for slide in soup.select("section.slide:not(#slide-1)")
            if slide.select_one(".profile-hero-block") is not None
            and slide.select_one(".profile-signature-grid") is not None
        ]
        assert not repeated_grid_slides, f"{preset} repeats the same hero + signature grid route: {repeated_grid_slides}"

        route_selectors = (
            ".profile-split-layout",
            ".profile-matrix",
            ".profile-timeline",
            ".profile-terminal-window",
            ".profile-pullquote",
            ".profile-card-grid",
            ".profile-showcase",
        )
        used_routes = {
            slide.get("data-export-role", "")
            for slide in soup.select("section.slide:not(#slide-1)")
            if slide.get("data-export-role")
        }
        used_routes.update(
            selector
            for selector in route_selectors
            if soup.select_one(f"section.slide:not(#slide-1) {selector}") is not None
        )
        assert len(used_routes) >= 3, f"{preset} does not vary page rhythm enough: {sorted(used_routes)}"


def test_profile_renderer_does_not_attach_demo_css_classes_to_arbitrary_content_nodes():
    brief = _agent_delivery_review_brief_for_preset("Modern Newspaper")
    html_text, _packet = _render_profile_from_brief("Modern Newspaper", brief)
    soup = BeautifulSoup(html_text, "html.parser")

    assert soup.select(".np-rule .np-cmd") == []


def test_profile_renderer_styles_visible_signature_classes_in_css():
    html_text, _packet = _render_profile("Creative Voltage")
    css_text = _style_text(html_text)

    for selector in (".voltage-card", ".voltage-blue-panel", ".voltage-neon-badge", ".voltage-diamond"):
        assert selector in css_text


def test_profile_renderer_defines_readable_ink_for_known_low_contrast_presets():
    readable_tokens = {
        "Bold Signal": "--profile-ink: #ffffff",
        "Electric Studio": "--profile-ink: #ffffff",
        "Paper & Ink": "--profile-ink: #1a1a1a",
        "Modern Newspaper": "--profile-ink: #111111",
    }
    for preset, expected_token in readable_tokens.items():
        html_text, _packet = _render_profile(preset)
        assert expected_token in _style_text(html_text)


def test_profile_cover_canvas_uses_preset_specific_readable_surfaces(tmp_path: Path):
    for preset in (
        "Aurora Mesh",
        "Creative Voltage",
        "Dark Botanical",
        "Neo-Brutalism",
        "Notebook Tabs",
        "Pastel Geometry",
        "Vintage Editorial",
    ):
        _html_text, packet = _render_profile(preset)
        demo_features = analyze_html(_demo_feature_path(preset))
        candidate_features, _html_text = _rendered_features(tmp_path, preset)
        color_coverage = len(demo_features.colors & candidate_features.colors) / max(1, len(demo_features.colors))

        _assert_demo_derived(packet, preset)
        assert color_coverage >= 0.45, f"{preset} does not preserve enough demo canvas colors: {color_coverage:.3f}"


def test_profile_renderer_does_not_emit_hidden_signature_marker_nodes():
    for preset in ("Paper & Ink", "Strategy Consulting", "Creative Voltage"):
        html_text, _packet = _render_profile(preset)
        soup = BeautifulSoup(html_text, "html.parser")

        assert soup.select(".profile-signature-markers") == []
        assert soup.select("[class*='preset-signature-']") == []


def test_paper_ink_steps_do_not_repeat_label_as_body():
    html_text, _packet = _render_profile("Paper & Ink")
    soup = BeautifulSoup(html_text, "html.parser")

    for step in soup.select(".steps .step"):
        text = step.select_one(".step-text")
        assert text is not None
        label = text.select_one("strong")
        assert label is not None
        lines = text.get_text("\n", strip=True).split("\n")
        body = " ".join(lines[1:]).strip()

        assert body
        assert body != label.get_text(" ", strip=True)


def test_strategy_consulting_cards_do_not_repeat_label_as_body():
    html_text, _packet = _render_profile("Strategy Consulting")
    soup = BeautifulSoup(html_text, "html.parser")

    for card in soup.select(".sc-evidence-card"):
        label = card.select_one(".sc-metric-label")
        body = card.select_one("p")
        assert label is not None
        assert body is not None

        assert body.get_text(" ", strip=True) != label.get_text(" ", strip=True)


def test_strategy_consulting_profile_uses_white_canvas_and_visible_sc_components():
    html_text, packet = _render_profile("Strategy Consulting")
    soup = BeautifulSoup(html_text, "html.parser")
    css_text = _style_text(html_text)

    _assert_demo_derived(packet, "Strategy Consulting")
    assert re.search(r"--bg\s*:\s*#ffffff\b", css_text) or re.search(r"--bg-card\s*:\s*#f7f8fa\b", css_text)
    assert ".slide-1 { background: linear-gradient" not in css_text
    assert soup.select_one(".sc-action-title") is not None
    assert soup.select_one(".sc-evidence-card, .sc-reco-box, .sc-source") is not None


def test_component_signature_css_does_not_create_bare_presence_markers():
    html_text, _packet = _render_profile("Creative Voltage")
    css_text = _style_text(html_text)

    assert "--profile-component-present" not in css_text
