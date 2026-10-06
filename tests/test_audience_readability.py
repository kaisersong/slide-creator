import sys
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from audience_readability import apply_audience_readability, unique_facts


def test_dedup_preserves_negation_conditions_and_internal_punctuation():
    facts=["No, retry.","No retry.","If A happens, revoke B.","If B happens, revoke A.","反馈整理时间减少30%。","反馈整理时间减少：30%"]
    assert unique_facts(facts) == facts[:5]


def test_runtime_scripts_and_speaker_notes_survive_readability_pass():
    script='<script>const sample = \'<section class="slide"><p>runtime</p></section>\';</script>'
    opening='<section class="slide" id="slide-1" data-notes="Preserve &quot;24 hours&quot; in notes">'
    html='<html><head></head><body>'+opening+'<h2>Known boundary</h2><p>Known boundary.</p><p>Tokens expire after 24 hours.</p><p>Tokens expire after 24 hours.</p></section>'+script+'</body></html>'
    rendered=apply_audience_readability(html)
    assert script in rendered
    assert opening in rendered
    soup=BeautifulSoup(rendered,'html.parser')
    assert len(soup.select('section.slide p')) == 1
    assert soup.select_one('section.slide p').get_text() == "Tokens expire after 24 hours."


def test_consulting_uses_distinct_exhibits_and_source_condition_action_pairs():
    from preset_profile_renderer import _render_strategy_consulting_body
    from preset_profile_specs import PROFILE_SPECS
    value={'title':'达标再申请扩大','claim':'按结果决定','key_point':'当前没有试点结果','role':'decision','supporting_facts':['若服务成本增加且满意度未改善，停止扩展。','若延迟下降且客户满意度改善，再申请扩大。','当前没有试点结果。']}
    sections=[]
    for layout in ['consulting_exec','consulting_matrix','consulting_split','consulting_quote','consulting_close']:
        sections.append(BeautifulSoup(_render_strategy_consulting_body(value,layout=layout,canonical_preset='Strategy Consulting',profile_spec=PROFILE_SPECS['Strategy Consulting']),'html.parser'))
    assert sections[0].select_one('.sc-evidence-row')
    assert sections[1].select_one('.sc-fact-table')
    assert sections[2].select_one('.sc-before-after')
    assert sections[3].select_one('.sc-quote-block')
    table=sections[4].select_one('.sc-rule-table')
    assert table and len(table.select('tbody tr'))==3
    first=table.select('tbody tr')[0]
    assert [c.get_text() for c in first.select('td')]==['若服务成本增加且满意度未改善','停止扩展。']
