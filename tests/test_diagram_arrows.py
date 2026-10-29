import sys
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from diagram_arrows import refine_diagram_arrows


@pytest.mark.parametrize("preset", ["Blue Sky", "Fantasy Rainbow"])
def test_arrows_do_not_scale_with_body_text_or_line_width(preset):
    script = '<script>const example = \'<section><span>→</span></section>\';</script>'
    source = '''<section class="slide" data-notes="Keep direction">
      <div style="font-size:80px">→</div><p>A → B</p><kbd><span>→</span></kbd>
      <svg><defs><marker id="end" markerWidth="20" markerHeight="20"><path d="M0 0 L8 4 L0 8z"/></marker></defs>
      <path data-edge-from="A" data-edge-to="B" d="M0 0 L100 0" marker-end="url(#end)"/>
      <text font-size="60">↓</text></svg></section>'''
    result = refine_diagram_arrows(source + script, preset)
    assert script in result
    soup = BeautifulSoup(result, "html.parser")
    marker = soup.select_one("marker")
    assert marker["markerunits"] == "userSpaceOnUse"
    assert marker["markerwidth"] == marker["markerheight"] == "6"
    assert len(soup.select(".diagram-arrow")) == 2
    assert soup.select_one("p").get_text() == "A → B"
    assert not soup.select_one("kbd .diagram-arrow")
    path = soup.select_one("path[data-edge-from]")
    assert path["data-edge-to"] == "B" and path["d"] == "M0 0 L100 0"
    assert path["marker-end"] == "url(#end)"


def test_unrelated_presets_retain_their_connector_style():
    source = '<section class="slide"><span>→</span></section>'
    assert refine_diagram_arrows(source, "Strategy Consulting") == source
