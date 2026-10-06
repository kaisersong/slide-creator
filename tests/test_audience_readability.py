import sys
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from audience_readability import apply_audience_readability, unique_facts, non_repeating_copy


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
    assert table and len(table.select('tbody tr'))==2
    assert sections[4].select_one('.sc-close-facts').get_text(strip=True)=="当前没有试点结果。"
    first=table.select('tbody tr')[0]
    assert [c.get_text() for c in first.select('td')]==['若服务成本增加且满意度未改善','停止扩展。']


def test_consulting_close_does_not_label_plain_facts_as_condition_action():
    from preset_profile_renderer import _render_strategy_consulting_body
    from preset_profile_specs import PROFILE_SPECS
    value={'title':'先评估再扩展','key_point':'当前没有试点结果','supporting_facts':['当前没有试点结果。','访谈是小样本，不能推断全体比例。']}
    soup=BeautifulSoup(_render_strategy_consulting_body(value,layout='consulting_close',canonical_preset='Strategy Consulting',profile_spec=PROFILE_SPECS['Strategy Consulting']),'html.parser')
    assert not soup.select('.sc-rule-table,th')
    assert [n.get_text() for n in soup.select('.sc-close-facts li')]==value['supporting_facts']


def test_complete_sentence_filter_keeps_new_scope_negations_and_decimal_values():
    text="Activation is 52.5%. If a token leaks, revoke it first. No, retry. No retry."
    result=non_repeating_copy(text,["Activation is 52.5%.","No retry."])
    assert result=="If a token leaks, revoke it first. No, retry."


def test_blue_action_fact_is_not_copied_into_pill_and_body():
    from low_context import _render_blue_sky_action_cards
    fact="下一阶段邀请两个团队试点。"
    html=_render_blue_sky_action_cards({},[fact])
    assert BeautifulSoup(html,'html.parser').get_text(' ',strip=True)==fact
    command="clawhub install kai-slide-creator"
    html=_render_blue_sky_action_cards({},[command])
    soup=BeautifulSoup(html,'html.parser')
    assert soup.select_one('.cmd').get_text(strip=True)==command
    assert not soup.select('.pill')


def test_long_fact_pill_and_heading_participate_in_dedup_and_audience_font():
    html='<html><head></head><body><section class="slide"><span class="pill" data-audience-fact="true">下一阶段邀请两个团队试点。</span><p>下一阶段邀请两个团队试点。 新条件仍需确认。</p><h4>Known risk remains</h4><p>Known risk remains.</p></section></body></html>'
    soup=BeautifulSoup(apply_audience_readability(html),'html.parser')
    assert soup.select_one('p').get_text()=="新条件仍需确认。"
    assert len(soup.select('p'))==1
    assert 'audience-copy' in soup.select_one('.pill')['class']
    assert 'audience-copy' in soup.select_one('h4')['class']


def test_metric_keeps_its_adjacent_source_label_when_summary_repeats_it():
    html='<html><head></head><body><section class="slide"><h2>45名产品经理参与试点</h2><div class="g"><div class="stat">45</div><p class="blue-metric-label">45名产品经理参与试点</p></div></section></body></html>'
    soup=BeautifulSoup(apply_audience_readability(html),'html.parser')
    assert soup.select_one('.g .blue-metric-label').get_text()=="45名产品经理参与试点"


def test_custom_theme_fields_remove_only_repeated_lead_sentences():
    html='<html><head></head><body><section class="slide"><p>导出的图片不能保留文字编辑能力。 需要继续改字时选择 HTML。</p><div class="iri-field"><span>01</span><span>导出的图片不能保留文字编辑能力。</span></div></section></body></html>'
    soup=BeautifulSoup(apply_audience_readability(html),'html.parser')
    assert soup.select_one('p').get_text()=="需要继续改字时选择 HTML。"
    assert soup.select_one('.iri-field span:last-child').get_text()=="导出的图片不能保留文字编辑能力。"


def test_dedup_never_uses_own_ancestor_or_child_as_a_duplicate():
    html='<html><head></head><body><section class="slide"><table><tr><td><p>Disable debug dumps before production use.</p></td></tr></table><li><p><strong>Revoke the old token first.</strong></p></li></section></body></html>'
    soup=BeautifulSoup(apply_audience_readability(html),'html.parser')
    assert soup.select_one('td p').get_text()=="Disable debug dumps before production use."
    assert soup.select_one('li p').get_text()=="Revoke the old token first."


def test_enterprise_action_binding_survives_matching_headline_without_fake_bars():
    from low_context import _render_enterprise_consulting_split
    spec={'slide_number':3,'title':'Disable Debug Dumps','layout_id':'consulting_split','key_point':'The service does not encrypt local debug dumps.','role':'condition','speaker_note':'Before production use, disable debug dumps.','supporting_facts':['Condition: before production use.','Action: Disable Debug Dumps']}
    h=_render_enterprise_consulting_split(spec,5)
    soup=BeautifulSoup(apply_audience_readability('<html><head></head><body>'+h+'</body></html>'),'html.parser')
    assert [p.get_text() for p in soup.select('.ent-split-item-copy')]==['before production use.','Disable Debug Dumps']
    assert not soup.select('.ent-prog-bar')
