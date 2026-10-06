import argparse,json,statistics,sys,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from browser_geometry_qa import _launch_browser,_enter_present_mode,_activate_slide,_wait_for_deterministic_layout
p=argparse.ArgumentParser();p.add_argument('--target',default='candidate10');p.add_argument('--run-dir',type=Path,required=True);a=p.parse_args()
base=a.run_dir.resolve();manifest=json.loads((base/'manifest.json').read_text())
selector='h1,h2,h3,h4,h5,h6,p,li,td,pre,code,.pill,.ds-action-title,.ent-kpi-label,.ent-cover-metric-title,.ds-kpi-label,.hero-stat-label,.sc-metric-label,.iri-fracture-item,.iri-field span:last-child,.sc-thing-body'
js=r'''({selector})=>{
 const slide=document.querySelector('.slide.p-on')||[...document.querySelectorAll('.slide')].find(s=>s.getBoundingClientRect().top>=-1&&s.getBoundingClientRect().top<innerHeight/2);
 if(!slide)return [];
 const scale=slide.getBoundingClientRect().width/slide.offsetWidth;
 const nodes=[...slide.querySelectorAll(selector)];
 return nodes.filter(n=>!n.closest('svg,footer,[aria-hidden="true"]')&&!nodes.some(a=>a!==n&&a.contains(n))).map(n=>{
  const r=n.getBoundingClientRect(),s=getComputedStyle(n),text=n.innerText.trim();
  return {text,tag:n.tagName,classes:n.className,font:parseFloat(s.fontSize)*scale,visible:r.width>0&&r.height>0&&s.visibility!=='hidden'&&parseFloat(s.opacity)>0,metric_label:n.classList.contains('blue-metric-label')};
 }).filter(n=>n.visible&&n.text.length>=12&&!/caption|eyebrow|source|slide-num|label-tag|index/.test(n.classes));
}'''
rows=[];pw,browser=_launch_browser()
try:
 for case in manifest['cases']:
  if case.get('negative'):continue
  for rep in range(1,4):
   measurements=[]
   for arm in ['candidate5',a.target]:
    deck=base/arm/case['id']/f'rep-{rep}/workspace/output/deck.html'; node_rows=[];dupes=[]
    for vp in [{'width':1600,'height':900},{'width':1280,'height':720}]:
     for mode in ['window','present']:
      page=browser.new_page(viewport=vp);page.goto(deck.as_uri());_wait_for_deterministic_layout(page)
      if mode=='present':assert _enter_present_mode(page)
      for i in range(1,page.locator('.slide').count()+1):
       assert _activate_slide(page,i,mode=mode);_wait_for_deterministic_layout(page)
       values=page.evaluate(js,{'selector':selector});node_rows.extend({**v,'mode':mode,'width':vp['width'],'slide':i} for v in values)
       seen=set()
       for v in values:
        if v['metric_label']:continue
        sentences=[x.strip() for x in re.findall(r'.*?(?:[。!?！？]|(?<!\d)\.(?=\s|$)|$)',v['text'],re.S) if x.strip()]
        for sent in sentences:
         if len(sent)<12:continue
         key=re.sub(r'\s+','',sent).strip('。.!！？?').casefold()
         if key in seen:dupes.append({'mode':mode,'width':vp['width'],'slide':i,'text':sent})
         else:seen.add(key)
      page.close()
    fonts=[v['font'] for v in node_rows if v['tag'] not in ['H1','H2']]
    measurements.append({'arm':arm,'audience_effective_font_median':round(statistics.median(fonts),2),'audience_font_below16':sum(f<16 for f in fonts),'font_nodes':len(fonts),'duplicate_statement_observations':len(dupes),'duplicates':dupes,'nodes':node_rows})
   rows.append({'case_id':case['id'],'rep':rep,'measures':measurements});print(case['id'],rep,[{k:m[k] for k in ['arm','audience_effective_font_median','audience_font_below16','duplicate_statement_observations']} for m in measurements],flush=True)
finally:browser.close();pw.stop()
(base/a.target/'readability-diagnostics-v3.json').write_text(json.dumps({'version':3,'definition':'Audience nodes >=12 chars, leaf selected nodes, footer/metadata excluded; full sentence duplicates per slide, adjacent metric source captions retained; four real browser contexts, scale=slide bounding width/offsetWidth. Not semantic similarity or STE certification.','selector':selector,'runs':rows},ensure_ascii=False,indent=2))
