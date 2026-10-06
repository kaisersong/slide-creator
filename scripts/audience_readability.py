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
        seen = {copy_key(n.get_text(" ", strip=True)) for n in slide.select("h1,h2,h3,li,td,strong,.ds-kpi-label,.ent-kpi-label,.hero-stat-label,.sc-metric-label")}
        for paragraph in list(slide.select("p")):
            if paragraph.find_parent(["svg", "foreignobject"]):
                continue
            key = copy_key(paragraph.get_text(" ", strip=True))
            if key and key in seen:
                paragraph.decompose()
            elif key:
                seen.add(key)
        for node in slide.select("p,li,td,h3,.ds-insight,.hero-stat-label,.ent-kpi-label,.ent-cover-metric-title,.ds-kpi-label,.sc-metric-label,.sc-thing-body,.iri-fracture-item,.iri-field span:last-child,.iri-contract-layer p,.iri-fact strong,.pain-title,.pain-desc,.disc-step-title,.disc-step-desc"):
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
@media (max-width:600px) { body:not(.presenting) .slide .audience-copy { font-size:18px !important; } }
body .slide .iri-field code { font-size:20px; line-height:1.35; overflow-wrap:anywhere; }
body[data-preset="Data Story"] .ds-close .ds-kpi { font-size:clamp(38px,4vw,58px); line-height:1.1; }
body[data-preset="Data Story"] .ds-stage-grid--evidence { display:flex; flex-direction:column; gap:0; }
body[data-preset="Data Story"] .ds-stage-grid--evidence .ds-stage-card { display:grid; grid-template-columns:100px minmax(0,1fr); border:0; border-bottom:1px solid var(--axis-line,#c8d1dc); background:transparent; padding:14px 0; }
body[data-preset="Data Story"] .ds-stage-grid--evidence .ds-stage-copy { grid-column:2; }
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
