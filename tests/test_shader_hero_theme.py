from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from low_context import render_from_brief
from preset_capabilities import get_preset_render_capability
from validate_html import validate


def brief():
    return json.loads((ROOT / "demos/shader-hero/BRIEF.json").read_text())


@pytest.mark.parametrize("preset", ["custom:shader-hero", "shader-hero", "Shader Hero", "极光封面"])
def test_theme_can_be_selected_without_animation_instructions(preset):
    b = brief()
    b["style"]["preset"] = preset
    capability = get_preset_render_capability(preset)
    assert capability.can_render and capability.renderer_strategy == "custom_theme"
    output, _, _ = render_from_brief(b)
    soup = BeautifulSoup(output, "html.parser")
    assert len(soup.select("canvas")) == 1
    assert len(soup.select(".sh-scene--cover")) == 1
    assert not soup.select(".sh-scene--content canvas, .sh-scene--closing canvas")
    assert {s["data-export-role"] for s in soup.select(".slide")} == {
        "title_grid", "column_content", "geometric_diagram", "contents_index", "pull_quote", "cta_close"
    }


@pytest.mark.parametrize("intent", ["none", "pptx", "png"])
def test_generation_and_static_export_pass_strict(intent, tmp_path):
    b = brief()
    b["runtime"]["export_intent"] = intent
    output, _, _ = render_from_brief(b)
    soup = BeautifulSoup(output, "html.parser")
    assert len(soup.select("canvas")) == (1 if intent == "none" else 0)
    assert ("navigator.gpu" in output) == (intent == "none")
    assert ("WebGLAurora" in output) == (intent == "none")
    assert soup.select_one(".sh-cover-field")
    artifact = tmp_path / "deck.html"
    artifact.write_text(output)
    assert validate(artifact, strict=True)


def test_caller_content_and_numeric_facts_survive_without_sample_branding():
    b = copy.deepcopy(brief())
    b["title"] = "客户稿"
    for index, slide in enumerate(b["narrative"]["slides"]):
        slide["title"] = f"客户判断 {index} <安全>"
        slide["supporting_facts"] = [f"客户事实 {index} & 证据", f"年度增长 {index + 10}%"]
        slide["numeric_facts"] = [f"{index + 10}%"]
        slide["title_emphasis"] = "<安全>"
    output, _, _ = render_from_brief(b)
    soup = BeautifulSoup(output, "html.parser")
    for index, slide in enumerate(soup.select(".slide")):
        assert f"客户判断 {index} <安全>" in slide.get_text()
        assert f"客户事实 {index} & 证据" in slide.get_text()
        assert f"年度增长 {index + 10}%" in slide.get_text()
        assert not any(node.get_text(strip=True) == f"{index + 10}%" for node in slide.select(".sh-evidence"))
        assert slide.select_one("em").get_text() == "<安全>"
        assert slide.select_one("safe") is None
    assert "金蝶" not in soup.get_text()
    assert "让第一眼" not in soup.get_text()


def test_existing_fantasy_rainbow_export_behavior_is_unchanged():
    b = brief()
    b["style"]["preset"] = "custom:fantasy-rainbow"
    b["runtime"]["export_intent"] = "pptx"
    output, _, _ = render_from_brief(b)
    assert 'id="iridescence-canvas"' in output
    assert "IridescenceController" in output
