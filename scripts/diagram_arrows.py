"""Keep diagram connectors subordinate to content in the two airy presets."""
from __future__ import annotations

import re
from bs4 import BeautifulSoup


def refine_diagram_arrows(html: str, preset: str) -> str:
    if preset not in {"Blue Sky", "Fantasy Rainbow"}:
        return html

    def refine(match: re.Match[str]) -> str:
        if not match.group(0).lower().startswith("<section"):
            return match.group(0)
        soup = BeautifulSoup(match.group(0), "html.parser")
        for marker in soup.select("svg marker"):
            # Default strokeWidth units multiply the head by the line width.
            # User-space units keep a small head even on emphasized edges.
            marker["markerunits"] = "userSpaceOnUse"
            marker["markerwidth"] = "6"
            marker["markerheight"] = "6"
        for node in soup.select("div, span, b, strong, i, p, text"):
            if node.find(True) or node.find_parent(["button", "kbd", "pre", "code"]):
                continue
            if node.name != "text" and node.find_parent("svg"):
                continue
            if re.fullmatch(r"[→←↑↓↔↕⇒⇐⇑⇓➜➔➝➞➟➠➤▶▷▼▽]+", node.get_text(strip=True)):
                node["class"] = list(dict.fromkeys([*node.get("class", []), "diagram-arrow"]))
        return str(soup)

    # Only slide fragments are parsed; scripts, styles and keyboard chrome
    # outside the slides retain their exact source.
    return re.sub(r"<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>|<section\b[^>]*>.*?</section>",
                  refine, html, flags=re.S | re.I)
