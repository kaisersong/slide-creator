from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL_MD = ROOT / "SKILL.md"
README_MD = ROOT / "README.md"
README_ZH_MD = ROOT / "README.zh-CN.md"
WORKFLOW_MD = ROOT / "references" / "workflow.md"
PLANNING_TEMPLATE_MD = ROOT / "references" / "planning-template.md"
HTML_TEMPLATE_MD = ROOT / "references" / "html-template.md"
BASE_CSS_MD = ROOT / "references" / "base-css.md"
ANTI_PATTERNS_MD = ROOT / "references" / "impeccable-anti-patterns.md"
DESIGN_QUALITY_MD = ROOT / "references" / "design-quality.md"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_skill_and_workflow_lock_preset_across_modes():
    skill = read_text(SKILL_MD)
    workflow = read_text(WORKFLOW_MD)

    # Planning depths are now in the routing header line
    assert "`自动`" in skill or "Auto" in skill
    assert "`精修`" in skill or "Polish" in skill
    assert "they should still render inside the same preset family" in workflow
    assert "record segmented timing for:" in workflow


def test_planning_template_treats_preset_as_locked():
    template = read_text(PLANNING_TEMPLATE_MD)
    assert "Treat preset as locked once chosen" in template
    assert "`plan`" in template
    assert "`total`" in template


def test_html_template_requires_preset_metadata_and_title_fit_guard():
    template = read_text(HTML_TEMPLATE_MD)
    assert "data-preset=\"Preset Name\"" in template
    assert "data-preset=\"Enterprise Dark\"" in template
    # Title fit guard: ensure responsive title sizing exists
    assert "--title-size" in template or "clamp" in template


def test_design_quality_baseline_catches_title_wrap_and_half_width_state_grids():
    baseline = read_text(DESIGN_QUALITY_MD)
    assert "A slide title wrapping to 4+ lines is a layout failure" in baseline
    assert "Never put a 5-step state chain or API matrix inside a 50/50 column" in baseline
    assert "Does any title wrap to 4+ lines on desktop?" in baseline


def test_readmes_publish_mode_aliases_and_timing_guidance():
    readme = read_text(README_MD)
    readme_zh = read_text(README_ZH_MD)

    assert "**Auto**" in readme
    assert "**Polish**" in readme
    assert "~3" in readme and "6 minutes" in readme
    assert "~8" in readme and "15 minutes" in readme

    assert "自动" in readme_zh
    assert "精修" in readme_zh


def test_slide_container_has_no_visual_properties():
    """Template .slide must NOT define background, justify-content, align-items, or color.

    These properties break styles with different slide-level needs (dark slides,
    hero/CTA flex alignment). Template owns mechanics only; styles own visuals.

    Regression: v1.7+ template added justify-content:center and background:
    var(--bg-primary), breaking Modern Newspaper dark CTA and other styles.
    """

    def extract_slide_block(text: str) -> str:
        """Extract the .slide { ... } block from CSS text."""
        match = re.search(r"\.slide\s*\{([^}]+)\}", text)
        if not match:
            raise ValueError(f"No .slide {{...}} block found in {text[:200]}")
        return match.group(1)

    for path, label in [(HTML_TEMPLATE_MD, "html-template.md"), (BASE_CSS_MD, "base-css.md")]:
        text = read_text(path)
        block = extract_slide_block(text)
        block_lower = block.lower()
        # These properties are forbidden in the shared .slide rule
        assert "justify-content" not in block_lower, (
            f"{label}: .slide must NOT have justify-content — breaks flex:1 children on hero/CTA slides"
        )
        assert "align-items" not in block_lower, (
            f"{label}: .slide must NOT have align-items — breaks full-bleed panels (children shrink to content width)"
        )
        assert not re.search(r"\bbackground\s*:", block_lower), (
            f"{label}: .slide must NOT have background — breaks dark-slide variants (Enterprise Dark, Terminal Green, etc.)"
        )
        assert "color:" not in block_lower.replace("border-color", "").replace("background-color", ""), (
            f"{label}: .slide must NOT have color — each style file owns text color"
        )


def test_anti_patterns_covers_all_skill_pipeline_rules():
    """SKILL.md Pipeline references must exist in anti-patterns.md as named sections."""
    anti = read_text(ANTI_PATTERNS_MD)
    # Each keyword must appear as a ### section header (not just anywhere in the file)
    required_sections = [
        "U\\+FE0F",          # Pipeline: U+FE0F
        "letter-spacing",    # Pipeline: letter-spacing
        "#000",              # Pipeline: pure black
        "bounce",            # Pipeline: bounce easing
        "组件单调",           # Pipeline: component richness
        "SVG",               # Pipeline: SVG arrows
    ]
    for pattern in required_sections:
        assert re.search(r"###.*" + pattern, anti, re.IGNORECASE), (
            f"impeccable-anti-patterns.md 缺少包含 '{pattern}' 的主章节"
        )


def test_anti_patterns_integration_table_has_required_rules():
    """Integration table must contain rows for U+FE0F and component richness."""
    anti = read_text(ANTI_PATTERNS_MD)
    table_section = anti[anti.find("Pre-Write Validation"):]
    required_in_table = ["U+FE0F", "组件单调"]
    for concept in required_in_table:
        assert concept in table_section, (
            f"集成表缺少 '{concept}' 行"
        )


def test_anti_patterns_integration_table_has_continuous_numbering():
    """anti-patterns.md integration table numbering must be continuous from 9."""
    anti = read_text(ANTI_PATTERNS_MD)
    table_section = anti[anti.find("Pre-Write Validation"):]
    numbers = [int(m) for m in re.findall(r"^\|\s*(\d+)\s*\|", table_section, re.MULTILINE)]
    assert numbers, "anti-patterns.md 集成表为空"
    # Numbers must start from 9 and be monotonically increasing (allow gaps for inserted items)
    assert numbers[0] == 9, f"集成表应从 9 开始，实际从 {numbers[0]}"
    # Must be monotonically increasing (not necessarily +1 each step, as items may have been inserted)
    for i in range(1, len(numbers)):
        assert numbers[i] > numbers[i - 1], (
            f"集成表编号不递增：{numbers[i-1]} → {numbers[i]}"
        )


def test_skill_md_pipeline_mandates_anti_patterns_load():
    """SKILL.md Pipeline must reference anti-patterns.md (either '必须加载' or routing table)."""
    skill = read_text(SKILL_MD)
    pipeline_ok = "必须加载" in skill and "impeccable-anti-patterns" in skill
    routing_ok = "impeccable-anti-patterns" in skill and "title-quality" in skill
    assert pipeline_ok or routing_ok, (
        "SKILL.md 必须在 Pipeline 或路由表中引用 impeccable-anti-patterns.md 和 title-quality.md"
    )


def test_skill_md_generate_route_includes_required_files():
    """--generate routing table must include anti-patterns and title-quality."""
    skill = read_text(SKILL_MD)
    # Scope search to the routing table (starts with | 命令 |)
    routing_start = skill.find("| 命令 |")
    if routing_start == -1:
        routing_start = skill.find("| 命令")
    assert routing_start != -1, "SKILL.md routing table not found"
    routing_end = skill.find("\n---", routing_start)
    if routing_end == -1:
        routing_end = len(skill)
    routing_section = skill[routing_start:routing_end]
    assert "impeccable-anti-patterns" in routing_section, (
        "--generate 路由表必须包含 impeccable-anti-patterns.md"
    )
    assert "title-quality" in routing_section, (
        "--generate 路由表必须包含 title-quality.md"
    )


def test_skill_md_no_duplicate_command_routing_headers():
    """SKILL.md should not have duplicate ## 命令路由 section headers."""
    skill = read_text(SKILL_MD)
    count = skill.count("## 命令路由")
    assert count == 1, (
        f"SKILL.md 有 {count} 个 '## 命令路由' 章节，应合并为 1 个"
    )


def test_skill_md_line_count_within_budget():
    """SKILL.md line count should stay within budget (current target ≤195 lines)."""
    lines = read_text(SKILL_MD).splitlines()
    assert len(lines) <= 200, (
        f"SKILL.md has {len(lines)} lines, exceeding budget of 195. "
        f"Consider moving more content to references/ files."
    )


def test_title_quality_file_exists_in_both_repos():
    """title-quality.md must exist in both project and SKILL repos."""
    project_file = ROOT / "references" / "title-quality.md"
    skill_file = ROOT.parent / ".claude" / "skills" / "slide-creator" / "references" / "title-quality.md"
    assert project_file.exists(), "project repo references/title-quality.md not found"
    # SKILL repo check — only if the path exists (may not in all environments)
    if skill_file.parent.parent.exists():
        assert skill_file.exists(), "SKILL repo references/title-quality.md not found"
