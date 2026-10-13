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


def test_relation_types_remain_metadata_and_explicit_labels_remain_visible():
    from bs4 import BeautifulSoup
    brief = json.loads((ROOT / "evals/fantasy-structured/BRIEF.json").read_text())
    slide = brief["narrative"]["slides"][8]
    html, _, _ = render_from_brief(brief)
    edges = BeautifulSoup(html, "html.parser").select("#slide-9 .iri-interaction-edge")
    assert [edge.get_text(strip=True) for edge in edges] == ["→", "→"]
    assert all(edge["data-relation"] == "ordered-before" for edge in edges)
    assert all(edge["data-geometry-target"] == "flow-edge" for edge in edges)
    slide["structured_content"]["edges"][0]["label"] = "确认输入后执行下一步"
    html, _, _ = render_from_brief(brief)
    edge = BeautifulSoup(html, "html.parser").select_one("#slide-9 .iri-interaction-edge")
    assert edge.get_text(strip=True) == "确认输入后执行下一步"
    assert "has-edge-label" in edge["class"]


def test_profile_fixture_is_explicitly_fictional():
    brief = json.loads((ROOT / "evals/fantasy-structured/BRIEF.json").read_text())
    identity, credentials = brief["narrative"]["slides"][0]["structured_content"]["groups"]
    assert identity["label"] == "示例讲者"
    assert identity["description"] == "Demo Speaker"
    assert all("虚构" in value for value in identity["items"])
    assert all("虚构" in node["label"] for node in credentials["nodes"])


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
