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


def test_visual_variety_uses_descendant_layout_signatures():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <body>
        <section class="slide" id="slide-1"><div class="slide-content"><div class="hero-rule"></div><div class="hero-sub"></div></div></section>
        <section class="slide" id="slide-2"><div class="slide-content"><div class="left-panel"></div><div class="right-panel"></div></div></section>
        <section class="slide" id="slide-3"><div class="slide-content"><div class="disc-step"></div><div class="diagram-svg"></div></div></section>
        <section class="slide" id="slide-4"><div class="slide-content"><div class="data-table"></div><div class="terminal-line"></div></div></section>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_visual_variety(soup, html, [])

    assert ok
    assert "Visual variety OK" in message


def test_visual_variety_fails_on_three_repeated_component_patterns():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <body>
        <section class="slide" id="slide-1"><div class="slide-content"><div class="hero-rule"></div></div></section>
        <section class="slide" id="slide-2"><div class="slide-content"><div class="callout"></div><div class="callout-title"></div></div></section>
        <section class="slide" id="slide-3"><div class="slide-content"><div class="callout"></div><div class="callout-title"></div></div></section>
        <section class="slide" id="slide-4"><div class="slide-content"><div class="callout"></div><div class="callout-title"></div></div></section>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_visual_variety(soup, html, [])

    assert not ok
    assert "3 consecutive slides" in message


def test_swiss_modern_contract_accepts_canonical_direct_child_layouts():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          :root { --bg:#fff; --bg-dark:#0a0a0a; --text:#0a0a0a; --text-light:#fff; --text-muted:#666; --red:#ff3300; --grid-line:#e6e6e6; }
          .slide { position: relative; display: flex; }
          .slide-content { display: flex; flex-direction: column; }
        </style>
      </head>
      <body data-preset="Swiss Modern">
        <section class="slide" id="slide-1" data-export-role="title_grid">
          <div class="bg-num"></div>
          <div class="slide-content"></div>
          <span class="slide-num-label">01 / 04</span>
        </section>
        <section class="slide" id="slide-2" data-export-role="column_content">
          <div class="left-panel"><div class="slide-content"></div></div>
          <div class="right-panel"><div class="slide-content"></div></div>
          <span class="slide-num-label">02 / 04</span>
        </section>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_swiss_modern_contract(soup, html, [])

    assert ok
    assert "Swiss Modern contract OK" in message


def test_swiss_modern_contract_rejects_compatible_alias_wrappers():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          :root { --bg-primary:#fff; --text-primary:#0a0a0a; --accent:#ff3300; }
          .slide { position: relative; display: flex; }
          .slide-content { display: flex; }
        </style>
      </head>
      <body data-preset="Swiss Modern">
        <section class="slide" id="slide-2">
          <div class="slide-content">
            <div class="left-col"></div>
            <div class="right-col"></div>
          </div>
          <span class="slide-num-label">02 / 04</span>
        </section>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_swiss_modern_contract(soup, html, [])

    assert not ok
    assert "compatible aliases" in message or "legacy token aliases" in message
