from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_MD = ROOT / "SKILL.md"
WORKFLOW_MD = ROOT / "references" / "workflow.md"
BRIEF_TEMPLATE_JSON = ROOT / "references" / "brief-template.json"
AUTO_DEMO = ROOT / "demos" / "mode-paths" / "auto-BRIEF.json"
POLISH_DEMO = ROOT / "demos" / "mode-paths" / "polish-BRIEF.json"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def test_skill_exposes_only_two_user_facing_planning_depths():
    skill = read_text(SKILL_MD)
    assert "`自动`" in skill
    assert "`精修`" in skill
    assert "(Auto)" in skill
    assert "(Polish)" in skill
    assert "快速出稿" in skill
    assert "深度规划" in skill


def test_workflow_routes_to_polish_and_hides_reference_as_top_level_mode():
    workflow = read_text(WORKFLOW_MD)
    assert "Default: if the user does not specify a mode, route to `自动` (`Auto` in English UI)." in workflow
    assert "Route to `精修` (`Polish`) when" in workflow
    assert "`参考驱动` is only an internal branch inside `精修` / `Polish`." in workflow
    assert "Image intent exists only in `精修` / `Polish`." in workflow
    assert "English requests: show `Auto` / `Polish`" in workflow
    assert "Save as `BRIEF.json` in the working directory." in workflow
    assert "Only create `PLANNING.md` if the user explicitly asks to review a human-readable plan." in workflow


def test_brief_template_supports_auto_and_polish_depths():
    template = read_json(BRIEF_TEMPLATE_JSON)
    assert template["schema_version"] == 1
    assert template["mode"] == "auto"
    assert template["deck"]["deck_type"] == "user-content"
    assert "page_roles" in template["narrative"]
    assert "must_include" in template["content"]
    assert "timing" in template
    assert "plan_view" in template
    assert template["plan_view"]["emit_planning_view"] is False


def test_demo_auto_path_stays_lightweight():
    auto_demo = read_json(AUTO_DEMO)
    assert auto_demo["mode"] == "auto"
    assert "polish_controls" not in auto_demo
    assert auto_demo["plan_view"]["emit_planning_view"] is False


def test_demo_polish_path_embeds_deeper_ir_sections():
    polish_demo = read_json(POLISH_DEMO)
    assert polish_demo["mode"] == "polish"
    assert polish_demo["narrative"]["thesis"]
    assert polish_demo["narrative"]["page_roles"]
    assert polish_demo["polish_controls"]["style_constraints"]
    assert polish_demo["polish_controls"]["image_plan"]
    assert polish_demo["polish_controls"]["reference_branch"] == "参考驱动"
