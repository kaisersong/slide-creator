import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from model_context import build_model_context
from low_context import compile_style_contract, StyleContractError


@pytest.mark.parametrize("preset", ["Data Story","Swiss Modern","Enterprise Dark","Blue Sky","Chinese Chan","Strategy Consulting","fantasy-rainbow"])
def test_compact_contract_keeps_style_owner_and_rich_content(preset):
    context = build_model_context(preset)
    owner = compile_style_contract(preset)
    assert context["style_digest"] == owner["digest"]
    assert context["visual_contract"]["allowed_layout_ids"] == owner["allowed_layout_ids"]
    assert {"claim","explanation","visual_intent","numeric_facts","supporting_facts"} <= context["slide_optional"].keys()
    text = json.dumps(context, ensure_ascii=False)
    assert len(text.encode()) < 12000
    assert "css_blocks" not in text and "class SlidePresentation" not in text
    assert context["brief_skeleton"]["style"]["preset"] == preset


def test_context_query_does_not_mutate_template_or_render_artifact(tmp_path):
    path = ROOT / "references/brief-template.json"
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    result = subprocess.run([sys.executable,str(ROOT/"main.py"),"--model-context","--preset","Blue Sky"],cwd=tmp_path,capture_output=True,text=True)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["renderer_strategy"] == "native"
    assert not list(tmp_path.iterdir())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before


def test_unknown_preset_fails_closed():
    with pytest.raises(StyleContractError):
        build_model_context("not-a-real-theme")


def test_context_requires_preset():
    result = subprocess.run([sys.executable,str(ROOT/"main.py"),"--model-context"],capture_output=True,text=True)
    assert result.returncode != 0
    assert "--preset is required" in result.stderr


def test_preset_argument_does_not_silently_override_generation():
    result = subprocess.run([sys.executable,str(ROOT/"main.py"),"--generate","--preset","Data Story","--output","unused.html"],capture_output=True,text=True)
    assert result.returncode == 2
    assert "generation style comes from BRIEF" in result.stderr
