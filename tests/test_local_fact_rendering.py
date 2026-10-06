import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from low_context import (
    _build_candidate_fact_pool, _spec_detail_pairs, _enterprise_table_items,
    _render_enterprise_contrast_split, _render_data_story_kpi_chart,
    render_from_brief,
)


def spec(facts):
    return dict(slide_number=1, role="requirements", layout_id="contrast_split",
                title="Revoke before replacement", key_point="If a token leaks, revoke it first.",
                claim="Revocation comes first", speaker_note="Explain the order.",
                supporting_facts=facts, supporting_items=facts, evidence_items=facts,
                numeric_facts=[], visual="neutral requirements", chart_policy="avoid")


def test_explicit_page_facts_do_not_receive_global_filler():
    slide = {"supporting_facts": ["Worker persists the task."], "numeric_facts": []}
    brief = {"content": {"global_facts": ["Legacy peak: 120 requests per second."]}}
    assert _build_candidate_fact_pool(slide, brief) == slide["supporting_facts"]
    # Legacy briefs without local facts retain the existing fallback.
    assert _build_candidate_fact_pool({}, brief) == brief["content"]["global_facts"]


def test_sparse_fact_is_not_padded_or_cross_paired():
    value = spec(["Audit records remain for 7 days."])
    assert _enterprise_table_items(value) == value["supporting_facts"]
    assert _spec_detail_pairs(value) == [("Audit records remain for 7 days.", "")]


def test_operator_requirements_do_not_become_incorrect_before_state():
    facts = ["Access tokens expire after 24 hours.",
             "If a token leaks, revoke the old token before issuing a replacement."]
    soup = BeautifulSoup(_render_enterprise_contrast_split(spec(facts), 5), "html.parser")
    text = soup.get_text(" ", strip=True)
    assert all(fact in text for fact in facts)
    assert "Before" not in text and "After" not in text and "对比" not in text
    assert "✗" not in text and "✓" not in text
    assert not soup.select(".ent-contrast-block--negative")


def test_kpi_avoid_does_not_plot_unlike_units_or_infer_trend():
    value = spec(["Activation: 42%", "Latency: 310 ms", "Change: 8 percentage points"])
    value.update(layout_id="kpi_chart", numeric_facts=value["supporting_facts"])
    soup = BeautifulSoup(_render_data_story_kpi_chart(value, 5), "html.parser")
    assert not soup.select("svg")
    assert "▲" not in soup.get_text() and "▼" not in soup.get_text()


def test_consulting_explicit_facts_clear_demo_copy_and_preserve_four_steps():
    brief = json.loads((ROOT / "references/brief-template.json").read_text())
    brief["style"]["preset"] = "Strategy Consulting"
    facts = ["Retain the original process as a control.", "Start the delivery dashboard.",
             "Escalate delays and record the owner.", "Compare cost and satisfaction."]
    for slide in brief["narrative"]["slides"]:
        slide.update(title="Test before wider rollout", claim="Test before wider rollout",
                     key_point="The pilot has no results yet.", explanation="The pilot has no results yet.",
                     supporting_facts=facts, chart_policy="avoid")
        slide.pop("numeric_facts", None)
    html, _, _ = render_from_brief(brief)
    slides = BeautifulSoup(html, "html.parser").select("section.slide")
    for slide in slides:
        text = slide.get_text(" ", strip=True)
        assert all(fact in text for fact in facts)
        assert "demo-derived" not in text
        assert "PowerPoint" not in text and "60秒" not in text and "2.24.3" not in text
