from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
VALIDATE_HTML = ROOT / "scripts" / "validate_html.py"
AUDITED_DEMOS = [
    "notebook-tabs-zh.html",
    "modern-newspaper-zh.html",
    "vintage-editorial-zh.html",
    "glassmorphism-zh.html",
    "aurora-mesh-zh.html",
    "bold-signal-zh.html",
    "terminal-green-zh.html",
    "neon-cyber-zh.html",
    "neo-retro-dev-zh.html",
]


def load_validate_module():
    spec = importlib.util.spec_from_file_location("validate_html_module", VALIDATE_HTML)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("demo_name", AUDITED_DEMOS)
def test_audited_family_demos_pass_strict_validate(demo_name: str):
    validate_html = load_validate_module()
    demo_path = ROOT / "demos" / demo_name

    assert validate_html.validate(demo_path, strict=True), f"{demo_name} failed strict validate"
