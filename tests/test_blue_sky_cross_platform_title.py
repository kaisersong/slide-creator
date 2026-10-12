from __future__ import annotations

import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


def test_mixed_cjk_workflow_title_does_not_force_one_line():
    from low_context import _blue_sky_title_tag

    title = "精修路径多的是更强 planning，不是更多文件工厂"
    rendered = _blue_sky_title_tag("h2", title, layout_id="workflow")
    node = BeautifulSoup(rendered, "html.parser").h2
    assert "title-nowrap" not in node.get("class", [])
    assert node.get_text().replace("\n", "").replace(" ", "") == title.replace(" ", "")
    assert "planning" in node.get_text()
