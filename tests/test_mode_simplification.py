from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_MD = ROOT / "SKILL.md"
WORKFLOW_MD = ROOT / "references" / "workflow.md"
PLANNING_TEMPLATE_MD = ROOT / "references" / "planning-template.md"
AUTO_DEMO = ROOT / "demos" / "mode-paths" / "auto-PLANNING.md"
POLISH_DEMO = ROOT / "demos" / "mode-paths" / "polish-PLANNING.md"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_skill_exposes_only_two_user_facing_planning_depths():
    skill = read_text(SKILL_MD)
    assert "`自动`" in skill
    assert "`精修`" in skill
    assert "`Auto`" in skill
    assert "`Polish`" in skill
    assert "two user-facing planning depths" in skill
    assert "Do not add a third top-level mode." in skill
    assert "reference-driven" in skill


def test_workflow_routes_to_polish_and_hides_reference_as_top_level_mode():
    workflow = read_text(WORKFLOW_MD)
    assert "Default: if the user does not specify a mode, route to `自动` (`Auto` in English UI)." in workflow
    assert "Route to `精修` (`Polish`) when" in workflow
    assert "`参考驱动` is only an internal branch inside `精修` / `Polish`." in workflow
    assert "Image intent exists only in `精修` / `Polish`." in workflow
    assert "English requests: show `Auto` / `Polish`" in workflow


def test_planning_template_supports_auto_and_polish_depths():
    template = read_text(PLANNING_TEMPLATE_MD)
    assert "**Mode**: [自动 / 精修 / Auto / Polish]" in template
    assert "Only include this section when mode is `精修`." in template
    assert "## Deck Thesis" in template
    assert "## Narrative Arc" in template
    assert "## Page Roles" in template
    assert "## Style Constraints" in template
    assert "## Image Intent" in template
    assert "## Timing" in template


def test_demo_auto_path_stays_lightweight():
    auto_demo = read_text(AUTO_DEMO)
    assert "**Mode**: 自动" in auto_demo
    assert "## Deck Thesis" not in auto_demo
    assert "## Image Intent" not in auto_demo


def test_demo_polish_path_embeds_deeper_planning_sections():
    polish_demo = read_text(POLISH_DEMO)
    assert "**Mode**: 精修" in polish_demo
    assert "## Deck Thesis" in polish_demo
    assert "## Narrative Arc" in polish_demo
    assert "## Page Roles" in polish_demo
    assert "## Style Constraints" in polish_demo
    assert "## Image Intent" in polish_demo
    assert "参考驱动" in polish_demo
