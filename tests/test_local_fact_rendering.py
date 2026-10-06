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
    _render_enterprise_consulting_split, visible_numeric_coverage_failures,
    _chart_metric_values_from_spec, _cleanup_display_candidate,
    _render_enterprise_kpi_dashboard, _render_data_story_kpi_grid, _render_data_story_hero_number,
    _render_data_story_chart_insight, _render_data_story_cta_close, _render_chinese_chan_center,
)
from preset_contracts import check_preset_contract_html


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
    assert check_preset_contract_html(html, "Strategy Consulting")["pass"]
    slides = BeautifulSoup(html, "html.parser").select("section.slide")
    for slide in slides:
        text = slide.get_text(" ", strip=True)
        assert all(fact in text for fact in facts)
        assert "demo-derived" not in text
        assert "PowerPoint" not in text and "60秒" not in text and "2.24.3" not in text


def test_enterprise_split_keeps_expiry_explanation_and_fourth_risk():
    facts = ["Condition: a token leaks.", "Action: revoke it before replacement.",
             "Operators must revoke the old token.", "Remaining risk: the leaked token is still valid."]
    value = spec(facts)
    value.update(layout_id="consulting_split", key_point="Access tokens expire after 24 hours.")
    html = _render_enterprise_consulting_split(value, 5)
    text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
    assert value["key_point"] in text
    assert all(fact.replace(":", "") in text.replace(":", "") for fact in facts)


def test_required_numeric_guard_ignores_notes_and_identifiers():
    brief = {"content":{"must_include":["Tokens expire after 24 hours.", "p95 latency is 310 ms."]}}
    html = '<section class="slide" data-notes="Expires after 24 hours."><p>p95 latency is 310 ms.</p></section>'
    failures=visible_numeric_coverage_failures(brief,html)
    assert len(failures) == 1
    assert failures[0]["missing_tokens"] == ["24"]
    numbered=html.replace('</section>','<span class="slide-num-label">24</span></section>')
    assert visible_numeric_coverage_failures(brief,numbered)[0]["missing_tokens"] == ["24"]
    html=html.replace('</section>','<p>Tokens expire after 24 hours.</p></section>')
    assert visible_numeric_coverage_failures(brief,html) == []


def test_numeric_guard_keeps_legacy_brief_without_required_numbers():
    assert visible_numeric_coverage_failures({"content":{"must_include":["Keep uncertainty clear."]}},'<section class="slide">Evidence</section>') == []


def test_cli_missing_required_number_preserves_existing_output(tmp_path):
    import subprocess
    brief=json.loads((ROOT/"references/brief-template.json").read_text())
    brief["content"]["must_include"]=["Access tokens expire after 987654 hours."]
    path=tmp_path/"BRIEF.json"
    path.write_text(json.dumps(brief))
    output=tmp_path/"deck.html"
    output.write_text("existing output")
    result=subprocess.run([sys.executable,str(ROOT/"main.py"),"--generate","--brief",str(path),"--output",str(output)],capture_output=True,text=True)
    assert result.returncode == 1
    assert "CONTENT ERROR" in result.stdout
    assert "987654" in result.stdout
    assert output.read_text() == "existing output"


def test_chart_values_reject_mixed_units_but_keep_same_unit_series():
    value=spec(["Activation: 52.5%", "Latency: 310 ms", "Change: 9 percentage points"])
    value.update(numeric_facts=value["supporting_facts"], chart_policy="auto")
    assert _chart_metric_values_from_spec(value,["0","0","0"]) == []
    value.update(numeric_facts=["North: 40%", "South: 50%", "West: 60%"],supporting_facts=[],supporting_items=[],evidence_items=[])
    assert _chart_metric_values_from_spec(value,["0","0","0"]) == ["40%","50%","60%"]


def test_english_display_words_keep_spaces():
    assert _cleanup_display_candidate("No source value gives the prior baseline") == "No source value gives the prior baseline"


def test_enterprise_kpis_do_not_shift_token_and_audit_values_to_tls():
    facts=["The gateway uses TLS for data in transit.", "Access tokens expire after 24 hours.", "Audit records remain for 7 days."]
    value=spec(facts)
    value.update(role="controls",layout_id="kpi_dashboard",numeric_facts=facts[1:])
    soup=BeautifulSoup(_render_enterprise_kpi_dashboard(value,5),'html.parser')
    cards=soup.select('.ent-kpi-card')
    assert len(cards) == 3
    assert cards[0].select_one('.ent-kpi-number') is None
    assert cards[1].select_one('.ent-kpi-number').get_text(strip=True) == "24"
    assert cards[2].select_one('.ent-kpi-number').get_text(strip=True) == "7"


def test_data_story_numbers_follow_items_even_if_numeric_facts_order_differs():
    facts=["Review is pending.", "Latency reached 310 ms.", "Activation reached 52.5%."]
    value=spec(facts)
    value.update(layout_id="kpi_grid",numeric_facts=[facts[2],facts[1]])
    soup=BeautifulSoup(_render_data_story_kpi_grid(value,5),'html.parser')
    cards=soup.select('.ds-kpi-card')
    by_label={card.select_one('.ds-kpi-label').get_text(strip=True):card for card in cards}
    assert by_label[facts[0]].select_one('.ds-kpi') is None
    assert by_label[facts[1]].select_one('.ds-kpi').get_text(strip=True) == "310"
    assert by_label[facts[2]].select_one('.ds-kpi').get_text(strip=True) == "52.5%"
    assert "▲" not in soup.get_text() and "▼" not in soup.get_text()


def test_hero_number_has_its_own_source_entity_label():
    value=spec(["Activation reached 52.5%.", "The team has not approved expansion."])
    value.update(role="cover",layout_id="hero_number",title="Expansion waits for review",key_point="The team has not approved expansion.",numeric_facts=["Activation reached 52.5%."])
    soup=BeautifulSoup(_render_data_story_hero_number(value,5),'html.parser')
    assert soup.select_one('.ds-kpi').get_text(strip=True) == "52.5%"
    assert soup.select_one('.ds-kpi-label').get_text(strip=True) == "Activation reached 52.5%."


def test_single_measurement_never_creates_placeholder_bars():
    value=spec(["Activation reached 52.5%.", "Prior baseline is not provided."])
    value.update(role="evidence",layout_id="chart_insight",chart_policy="auto",numeric_facts=["Activation reached 52.5%."])
    soup=BeautifulSoup(_render_data_story_chart_insight(value,5),'html.parser')
    assert not soup.select('svg')
    assert "Signal 01" not in soup.get_text()
    assert "Prior baseline is not provided." in soup.get_text()


def test_closing_scope_comes_from_audience_action():
    value=spec(["Activation reached 52.5%.", "Reviews remain open."])
    value.update(layout_id="cta_close",desired_action="Decide whether to expand to all enterprise tenants next week.")
    text=BeautifulSoup(_render_data_story_cta_close(value,5),'html.parser').get_text(' ',strip=True)
    assert value['desired_action'] in text


def test_chan_center_retains_observation_fact_when_explanation_paraphrases_it():
    value=spec(["团队先观察用户遇到的问题。", "观察之后再写假设。"])
    value.update(layout_id="zen_center",title="先看真实困处",key_point="先看用户在哪里受阻，再决定要检验什么。")
    text=BeautifulSoup(_render_chinese_chan_center(value,5,language="zh-CN"),'html.parser').get_text(' ',strip=True)
    assert all(fact in text for fact in value['supporting_facts'])
