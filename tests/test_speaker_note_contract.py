import copy
import json
import sys
from pathlib import Path
import pytest
from bs4 import BeautifulSoup

ROOT=Path(__file__).parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from low_context import render_from_brief, validate_brief_data, build_slide_spec


def source():
    return json.loads((ROOT/"references/brief-template.json").read_text())


@pytest.mark.parametrize("preset",["Blue Sky","Swiss Modern","Enterprise Dark","Data Story","Chinese Chan","Strategy Consulting","fantasy-rainbow"])
def test_speaker_guidance_stays_out_of_audience_body(preset):
    brief=source();brief["style"]["preset"]=preset
    brief["narrative"]["slides"][0]["speaker_note"]="SPEAKER_ONLY_7F3: Ask the audience to pause before this decision."
    assert not validate_brief_data(brief)
    html,_,_=render_from_brief(brief)
    soup=BeautifulSoup(html,"html.parser")
    assert "SPEAKER_ONLY_7F3" in soup.select_one(".slide")["data-notes"]
    assert "SPEAKER_ONLY_7F3" not in " ".join(s.get_text(" ") for s in soup.select(".slide"))


def test_old_brief_keeps_explanation_fallback():
    brief=source();spec=build_slide_spec(brief)[0]
    assert spec["speaker_note"] == f"{spec['role']}: {spec['explanation']}"


@pytest.mark.parametrize("value",[None,123,""," ","x"*1201])
def test_invalid_note_fails_closed(value):
    brief=source();brief["narrative"]["slides"][0]["speaker_note"]=value
    assert any("speaker_note" in e for e in validate_brief_data(brief))
