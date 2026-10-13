from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from low_context import render_from_brief, validate_brief_data
from validate_source_fidelity import validate_source_fidelity


def test_all_structured_kinds_preserve_frozen_source_and_relations():
    fixture = ROOT / "evals/fantasy-structured"
    brief = json.loads((fixture / "BRIEF.json").read_text())
    assert len({s["structured_content"]["kind"] for s in brief["narrative"]["slides"]}) == 15
    assert validate_brief_data(brief) == []
    jsonschema.validate(brief, json.loads((ROOT / "schemas/generation-brief.schema.json").read_text()))
    html, _, _ = render_from_brief(brief)
    report = validate_source_fidelity(html, json.loads((fixture / "coverage.json").read_text()))
    assert report["pass"], report


@pytest.mark.parametrize("kind", ["card-sequence", "card-grid", "paired-panels", "parallel-flows"])
def test_generic_scene_root_nodes_keep_overridden_title_and_source_ref(kind):
    from bs4 import BeautifulSoup
    fixture = ROOT / "evals/fantasy-structured"
    brief = json.loads((fixture / "BRIEF.json").read_text())
    scene = brief["narrative"]["slides"][-1]
    scene["structured_content"] = {
        "kind": kind, "title": "独立结构标题 <safe>", "badge": "SOURCE",
        "nodes": [{"id": "root-a", "label": "完整事实", "source_refs": ["original-source"]}],
        "items": ["权限与范围必须保留"],
    }
    assert validate_brief_data(brief) == []
    html, _, _ = render_from_brief(brief)
    slide = BeautifulSoup(html, "html.parser").select_one("#slide-15")
    assert slide.select_one("h2").get_text("", strip=True) == "独立结构标题 <safe>"
    assert slide.select_one('[data-node-id="root-a"][data-source-ref="original-source"]')
    assert "权限与范围必须保留" in slide.get_text()
    duplicate = copy.deepcopy(brief)
    duplicate["narrative"]["slides"][-1]["structured_content"]["groups"] = [{"id": "root-a"}]
    assert any("reuses structured id" in error for error in validate_brief_data(duplicate))
