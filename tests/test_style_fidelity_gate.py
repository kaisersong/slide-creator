from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from low_context import render_from_brief  # noqa: E402
from preset_contracts import validate_preset_fidelity  # noqa: E402


spec = importlib.util.spec_from_file_location("slide_validate", ROOT / "scripts" / "validate_html.py")
validate = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validate)


def _brief(preset: str) -> dict:
    brief = json.loads((ROOT / "demos" / "mode-paths" / "auto-BRIEF.json").read_text(encoding="utf-8"))
    brief = copy.deepcopy(brief)
    brief["brief_id"] = "style-fidelity-gate"
    brief["style"]["preset"] = preset
    return brief


def test_strict_adapter_serializes_the_canonical_preset_fidelity_verdict():
    html = render_from_brief(_brief("Blue Sky"))[0]
    canonical = validate_preset_fidelity(html, "Blue Sky")
    passed, message = validate.check_preset_fidelity(BeautifulSoup(html, "html.parser"), html, [])

    assert passed == canonical["pass"]
    assert f"coverage {canonical['style']['metrics']['coverage']:.2f}" in message
    assert f"integrity {canonical['style']['metrics']['integrity']:.2f}" in message


def test_strict_adapter_returns_the_same_failure_codes_for_shell_injection():
    html = (ROOT / "tests" / "fixtures" / "existing-deck" / "blue-sky-shell-injection.html").read_text(encoding="utf-8")
    canonical = validate_preset_fidelity(html, "Blue Sky")
    passed, message = validate.check_preset_fidelity(BeautifulSoup(html, "html.parser"), html, [])

    assert passed is False
    for code in canonical["hard_failures"]:
        assert code in message


def test_strict_adapter_cannot_downgrade_to_reference_by_omitting_renderer_metadata():
    soup = BeautifulSoup(render_from_brief(_brief("Blue Sky"))[0], "html.parser")
    body = soup.find("body")
    assert body is not None
    body.attrs.pop("data-render-path", None)
    body.attrs.pop("data-renderer-strategy", None)
    for slide in soup.select("section.slide"):
        slide.attrs.pop("data-notes", None)
    html = str(soup)

    assert validate_preset_fidelity(html, "Blue Sky", mode="reference")["pass"] is True
    assert validate_preset_fidelity(html, "Blue Sky", mode="product")["pass"] is False
    passed, message = validate.check_preset_fidelity(soup, html, [])

    assert passed is False
    assert "contract-export-slot-missing" in message


def test_strict_check_list_has_one_style_score_owner():
    names = [item.__name__ for item in validate.STRICT_CHECKS]
    assert names.count("check_preset_fidelity") == 1
    assert names.count("check_glassmorphism_layout_semantics") == 1
    assert "check_blue_sky_signature_contract" not in names
    assert "check_glassmorphism_contract" not in names
