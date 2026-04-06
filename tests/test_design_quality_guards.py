from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL_MD = ROOT / "SKILL.md"
README_MD = ROOT / "README.md"
README_ZH_MD = ROOT / "README.zh-CN.md"
WORKFLOW_MD = ROOT / "references" / "workflow.md"
PLANNING_TEMPLATE_MD = ROOT / "references" / "planning-template.md"
HTML_TEMPLATE_MD = ROOT / "references" / "html-template.md"
DESIGN_QUALITY_MD = ROOT / "references" / "design-quality.md"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_skill_and_workflow_lock_preset_across_modes():
    skill = read_text(SKILL_MD)
    workflow = read_text(WORKFLOW_MD)

    assert "keep the same preset across `自动` and `精修`" in skill
    assert "English requests should show `Auto` / `Polish`" in skill
    assert "`Auto`: usually ~3-6 minutes end-to-end" in skill
    assert "`Polish`: usually ~8-15 minutes end-to-end" in skill
    assert "do not silently switch presets" in workflow
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
    assert "do not globally cap CJK or technical titles to tiny measures" in template


def test_design_quality_baseline_catches_title_wrap_and_half_width_state_grids():
    baseline = read_text(DESIGN_QUALITY_MD)
    assert "A slide title wrapping to 4+ lines is a layout failure" in baseline
    assert "Never put a 5-step state chain or API matrix inside a 50/50 column" in baseline
    assert "Does any title wrap to 4+ lines on desktop?" in baseline


def test_readmes_publish_mode_aliases_and_timing_guidance():
    readme = read_text(README_MD)
    readme_zh = read_text(README_ZH_MD)

    assert "`Auto` — fast draft path" in readme
    assert "`Polish` — deeper planning path" in readme
    assert "`Auto`: usually ~3-6 minutes" in readme
    assert "`Polish`: usually ~8-15 minutes" in readme
    assert "Intent Broker rerun timings" in readme

    assert "`自动（Auto）`" in readme_zh
    assert "`精修（Polish）`" in readme_zh
    assert "端到端预计耗时" in readme_zh
    assert "Intent Broker 重跑实测" in readme_zh
