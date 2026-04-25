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


def test_default_hidden_chrome_flags_visible_notes_panel():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          #notes-panel { position: fixed; right: 18px; bottom: 18px; width: min(380px, 36vw); }
          .edit-toggle { opacity: 0; }
        </style>
      </head>
      <body>
        <button id="editToggle" class="edit-toggle">Edit</button>
        <div id="notes-panel">Notes</div>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_default_hidden_chrome(soup, html, [])

    assert not ok
    assert "notes-panel" in message


def test_default_hidden_chrome_accepts_hidden_notes_panel():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          #notes-panel { display: none; position: fixed; right: 18px; bottom: 18px; }
          #notes-panel.active { display: block; }
          .edit-toggle { opacity: 0; }
        </style>
      </head>
      <body>
        <button id="editToggle" class="edit-toggle">Edit</button>
        <div id="notes-panel">Notes</div>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_default_hidden_chrome(soup, html, [])

    assert ok
    assert "hidden by default" in message
