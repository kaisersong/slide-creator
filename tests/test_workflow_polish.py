from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_MD = ROOT / "SKILL.md"
README_MD = ROOT / "README.md"
WORKFLOW_MD = ROOT / "references" / "workflow.md"
DEPLOY_SCRIPT = ROOT / "scripts" / "deploy-vercel.py"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_skill_contract_says_edit_mode_is_default_not_mandatory():
    skill = read_text(SKILL_MD)
    assert "Edit Mode (default-on, optional)" in skill
    assert "Every generated HTML file MUST include both of these" not in skill


def test_workflow_has_explicit_existing_html_guardrails():
    workflow = read_text(WORKFLOW_MD)
    assert "Enhancement Mode (existing HTML)" in workflow
    assert "Count existing content before adding new text or images." in workflow
    assert "If a change would exceed density limits, split the slide proactively." in workflow


def test_slide_creator_docs_do_not_mention_share_or_vercel():
    workflow = read_text(WORKFLOW_MD)
    readme = read_text(README_MD)
    skill = read_text(SKILL_MD)
    assert "Phase 6: Share" not in workflow
    assert "deploy-vercel.py" not in workflow
    assert "Share to URL" not in readme
    assert "Vercel" not in readme
    assert "shareable URL" not in readme
    assert "shareable URL" not in skill


def test_slide_creator_does_not_ship_deploy_helper():
    assert not DEPLOY_SCRIPT.exists(), f"Deploy helper should live outside slide-creator: {DEPLOY_SCRIPT}"
