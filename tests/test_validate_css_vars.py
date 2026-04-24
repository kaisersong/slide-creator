from __future__ import annotations

import importlib.util
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
VALIDATE_PY = ROOT / "tests" / "validate.py"


def load_validate_module():
    spec = importlib.util.spec_from_file_location("validate_module", VALIDATE_PY)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_validate_flags_undefined_css_vars_without_fallback():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          :root { --accent: #ff3300; }
          .rule { color: var(--text); background: var(--accent); }
        </style>
      </head>
      <body></body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    ok, message = validate.check_css_vars_defined(soup, html, [])

    assert not ok
    assert "--text" in message


def test_validate_allows_defined_or_fallback_css_vars():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          :root {
            --text: #111111;
            --accent: #ff3300;
          }
          .rule {
            color: var(--text);
            border-color: var(--missing, #cccccc);
            background: var(--accent);
          }
        </style>
      </head>
      <body></body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    ok, message = validate.check_css_vars_defined(soup, html, [])

    assert ok
    assert "All CSS variables resolved" in message
