"""Readable audience text and conservative, within-slide copy deduplication."""
from __future__ import annotations

import re
from bs4 import BeautifulSoup


def copy_key(text: str) -> str:
    text = re.sub(r"[:：](?=\s*\d+(?:\.\d+)?(?:%|名|个|ms|hours?|days?)?\s*[。.!！]?\s*$)", "", text, flags=re.I)
    return re.sub(r"\s+", "", text).strip("。.!！？?").casefold()


def unique_facts(values: list[str]) -> list[str]:
    result, seen = [], set()
    for value in values:
        text = str(value).strip()
        key = copy_key(text)
        if key and key not in seen:
            result.append(text)
            seen.add(key)
    return result


def non_repeating_copy(text: str, visible_facts: list[str]) -> str:
    """Remove only complete, verbatim sentences already visibly stated."""
    facts = {copy_key(fact) for fact in visible_facts if fact.strip()}
    sentences = re.findall(r".*?(?:[。!?！？]|(?<!\d)\.(?=\s|$)|$)", text, re.S)
    return " ".join(sentence.strip() for sentence in sentences
                    if sentence.strip() and copy_key(sentence) not in facts)


def apply_audience_readability(html: str) -> str:
    scripts = []
    def protect_script(match):
        scripts.append(match.group(0))
        return f"<!--AUDIENCE_SCRIPT_{len(scripts)-1}-->"
    html = re.sub(r"<script\b[^>]*>.*?</script>", protect_script, html, flags=re.S|re.I)
    def transform(match):
        fragment = match.group(0)
        soup = BeautifulSoup(fragment, "html.parser")
        slide = soup.select_one("section.slide")
        if slide is None:
            return fragment
        # Keep source statement labels, numbers and conditions. Remove a
        # repeated paragraph only when the entire normalized text is already
        # present elsewhere; do not merge similar but distinct propositions.
        fact_nodes = [n for n in slide.select("h1,h2,h3,h4,h5,h6,li,td,strong,.pill,.ds-action-title,.ds-kpi-label,.ent-kpi-label,.hero-stat-label,.sc-metric-label,.iri-field span:last-child,.iri-fracture-item,.pain-title,.pain-desc,.disc-step-title,.disc-step-desc,.sc-thing-body") if not n.find_parent(["svg","foreignobject"])]
        fact_records = [(n, n.get_text(" ",strip=True)) for n in fact_nodes]
        seen = set()
        for paragraph in list(slide.select("p")):
            if paragraph.find_parent(["svg", "foreignobject"]):
                continue
            # A metric must retain its adjacent source label, even when the
            # same fact is used in a headline or summary elsewhere.
            if "blue-metric-label" in paragraph.get("class", []) or paragraph.get("data-copy-binding") == "true":
                continue
            # A table/list cell or bold child cannot be evidence that its own
            # paragraph is duplicated; compare separate visible statements.
            fact_text = [text for n,text in fact_records if n not in paragraph.parents and paragraph not in n.parents]
            key = copy_key(paragraph.get_text(" ", strip=True))
            if key and (key in seen or key in {copy_key(text) for text in fact_text}):
                paragraph.decompose()
            elif key:
                if not paragraph.find(True):
                    compact = non_repeating_copy(paragraph.get_text(" ",strip=True), fact_text)
                    if not compact:
                        paragraph.decompose()
                        continue
                    paragraph.string = compact
                    key = copy_key(compact)
                seen.add(key)
        # Data Story stores explanatory copy in a div with a bold UI prefix.
        # Compare its body, rather than allowing "Insight:" to hide a repeat.
        for block in list(slide.select(".ds-insight:not(.ds-stage-card):not(.ds-kpi-card)")):
            label = block.find("strong", recursive=False)
            if not label or len(block.find_all(True, recursive=False)) != 1:
                continue
            prefix = label.get_text(" ",strip=True)
            if not re.fullmatch(r"(?:Insight|Flow|Decision|Question|Readout)[:：]", prefix, re.I):
                continue
            body = block.get_text(" ",strip=True)[len(prefix):].strip()
            visible = [text for n,text in fact_records if n not in block.parents and block not in n.parents]
            compact = non_repeating_copy(body, visible)
            if compact == body:
                continue
            if compact:
                label.extract()
                block.clear()
                block.append(label)
                block.append(" " + compact)
            else:
                # Keep the real insight visual, using the existing source card
                # once rather than adding a second copy or an empty shell.
                card = next((card for card in slide.select(".ds-stage-card,.ds-kpi-card")
                             if any(copy_key(text) in copy_key(card.get_text(" ",strip=True))
                                    for text in visible if text and copy_key(text) in copy_key(body))), None)
                if card is not None:
                    card["class"] = [*card.get("class", []), "ds-insight"]
                    block.decompose()
        for card in list(slide.select(".g,.ent-kpi-card,.ds-stage-card,.sc-evidence-card")):
            if not card.get_text(" ",strip=True) and not card.select("img,svg,canvas,video"):
                card.decompose()
        for node in slide.select("p,li,td,h3,h4,h5,h6,pre,code,span[data-audience-fact],.ds-action-title,.ds-insight,.hero-stat-label,.ent-kpi-label,.ent-cover-metric-title,.ds-kpi-label,.sc-metric-label,.sc-thing-body,.iri-fracture-item,.iri-field span:last-child,.iri-contract-layer p,.iri-fact strong,.pain-title,.pain-desc,.disc-step-title,.disc-step-desc"):
            if node.find_parent(["svg", "foreignobject"]):
                continue
            if not node.get_text(" ", strip=True):
                continue
            classes = node.get("class", [])
            if any(re.search(r"caption|eyebrow|label-tag|slide-num|source|index", cls) for cls in classes):
                continue
            node["class"] = [*classes, "audience-copy"]
        rendered = str(soup)
        opening = re.match(r"<section\b[^>]*>", fragment).group(0)
        return re.sub(r"^<section\b[^>]*>", lambda _: opening, rendered, count=1)
    html = re.sub(r"<section\b[^>]*>.*?</section>", transform, html, flags=re.S)
    for index, script in enumerate(scripts):
        html = html.replace(f"<!--AUDIENCE_SCRIPT_{index}-->", script)
    css = """
body .slide .audience-copy { font-size:22px !important; line-height:1.45 !important; letter-spacing:normal; }
body .slide .pill.audience-copy { white-space:normal; max-width:100%; }
@media (max-width:600px) { body:not(.presenting) .slide .audience-copy { font-size:18px !important; } }
body .slide .iri-field code { font-size:20px; line-height:1.35; overflow-wrap:anywhere; }
body .slide .iri-brief-code pre { font-size:20px !important; line-height:1.45 !important; white-space:pre-wrap; overflow-wrap:anywhere; }
body[data-preset="Data Story"] .ds-close .ds-kpi { font-size:clamp(38px,4vw,58px); line-height:1.1; }
body[data-preset="Data Story"] .ds-stage-grid--evidence { display:flex; flex-direction:column; gap:0; }
body[data-preset="Data Story"] .ds-stage-grid--evidence .ds-stage-card { display:grid; grid-template-columns:100px minmax(0,1fr); border:0; border-bottom:1px solid var(--axis-line,#c8d1dc); background:transparent; padding:14px 0; }
body[data-preset="Data Story"] .ds-stage-grid--evidence .ds-stage-copy { grid-column:2; }
body[data-preset="Data Story"] .ds-stage-card.ds-insight { border-left:3px solid var(--chart-primary,#3b82f6) !important; background:rgba(59,130,246,0.08) !important; }
body[data-preset="Strategy Consulting"] .sc-fact-table { border-collapse:collapse; width:100%; }
body[data-preset="Strategy Consulting"] .sc-fact-table td { border-bottom:1px solid var(--border,#c8d1dc); padding:16px; vertical-align:top; }
body[data-preset="Strategy Consulting"] .sc-fact-table td:first-child { width:55px; color:#1b3a6b; }
body[data-preset="Strategy Consulting"] .sc-rule-table { table-layout:fixed; }
body[data-preset="Strategy Consulting"] .sc-rule-table td:first-child { width:58%; }
body[data-preset="Strategy Consulting"] .sc-rule-table th { text-align:left; padding:12px 16px; color:#1b3a6b; }
body[data-preset="Strategy Consulting"] .sc-quote-block { font-size:28px; line-height:1.5; }
body[data-preset="Strategy Consulting"] .sc-evidence-card .sc-metric { font-size:20px; margin-bottom:12px; }
"""
    return html.replace("</head>", '<style id="audience-readability">' + css + "</style></head>", 1)
