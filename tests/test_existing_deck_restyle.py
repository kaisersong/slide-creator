from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from low_context import render_from_brief  # noqa: E402
from preset_contracts import validate_preset_fidelity  # noqa: E402


FIXTURE_DIR = ROOT / "tests" / "fixtures" / "existing-deck"


def test_shell_injection_is_rejected_but_brief_restyle_uses_native_renderer_and_passes():
    shell_html = (FIXTURE_DIR / "blue-sky-shell-injection.html").read_text(encoding="utf-8")
    rejected = validate_preset_fidelity(shell_html, "Blue Sky", mode="product")

    assert rejected["pass"] is False
    assert any(code.startswith("style-") for code in rejected["hard_failures"])

    brief = json.loads((FIXTURE_DIR / "blue-sky-restyle-BRIEF.json").read_text(encoding="utf-8"))
    html, packet, _style_contract = render_from_brief(brief)
    repaired = validate_preset_fidelity(html, "Blue Sky", mode="product")

    assert packet["renderer_strategy"] == "native"
    assert packet["render_path"] == "blue-sky-starter-canonical"
    assert repaired["pass"], repaired
    assert 'data-page-bucket="cover"' in html
    assert 'data-page-bucket="content"' in html
    assert 'data-page-bucket="closing"' in html
