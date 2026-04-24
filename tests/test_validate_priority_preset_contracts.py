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


def test_enterprise_dark_contract_accepts_canonical_ent_classes():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          :root {
            --bg-primary:#0d1117; --bg-secondary:#161b22; --bg-header:#21262d; --border:#30363d;
            --text-primary:#e6edf3; --text-body:#c9d1d9; --text-muted:#8b949e;
            --accent-blue:#388bfd; --accent-green:#3fb950; --accent-red:#f85149; --accent-amber:#d29922;
          }
          .slide { display:flex; position:relative; }
          .ent-split { display:grid; }
        </style>
      </head>
      <body data-preset="Enterprise Dark">
        <section class="slide" data-export-role="consulting_split">
          <div class="ent-split"></div>
          <span class="slide-num-label">01 / 12</span>
        </section>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    ok, message = validate.check_enterprise_dark_contract(soup, html, [])
    assert ok, message


def test_enterprise_dark_contract_rejects_generic_aliases():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          :root {
            --bg-primary:#0d1117; --bg-secondary:#161b22; --bg-header:#21262d; --border:#30363d;
            --text-primary:#e6edf3; --text-body:#c9d1d9; --text-muted:#8b949e;
            --accent-blue:#388bfd; --accent-green:#3fb950; --accent-red:#f85149; --accent-amber:#d29922;
          }
        </style>
      </head>
      <body data-preset="Enterprise Dark">
        <section class="slide">
          <div class="kpi"></div>
        </section>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    ok, message = validate.check_enterprise_dark_contract(soup, html, [])
    assert not ok
    assert "generic alias classes" in message


def test_data_story_contract_requires_svg_css_path_not_chart_library():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          :root {
            --bg:#0f1117; --bg-card:#1a1f2e; --border:#2d3748; --text:#e2e8f0; --text-muted:#64748b;
            --positive:#00d4aa; --negative:#ff6b6b; --neutral:#e2e8f0;
            --chart-primary:#3b82f6; --chart-secondary:#8b5cf6; --chart-tertiary:#10b981;
            --grid-line:#1e293b; --axis-line:#334155;
          }
          .slide::before { content:''; }
          body { font-variant-numeric: tabular-nums; }
        </style>
      </head>
      <body data-preset="Data Story">
        <script src="https://cdn.example.com/chart.js"></script>
        <section class="slide" data-export-role="chart_insight">
          <div class="ds-kpi-card"></div>
        </section>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    ok, message = validate.check_data_story_contract(soup, html, [])
    assert not ok
    assert "external chart libs" in message


def test_glassmorphism_contract_requires_orbs_and_glass_cards():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          :root {
            --bg-gradient-1:#667eea; --bg-gradient-2:#764ba2; --bg-gradient-3:#f093fb;
            --glass-bg:rgba(255,255,255,0.15); --glass-border:rgba(255,255,255,0.30);
            --glass-text-dark:#1a1a2e; --glass-text-light:rgba(255,255,255,0.92);
            --orb-purple:rgba(102,126,234,0.5); --orb-pink:rgba(240,147,251,0.4); --orb-mint:rgba(168,237,234,0.4);
          }
          .slide-0 { background: linear-gradient(135deg, #667eea, #764ba2, #f093fb); }
          .glass-card { backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); }
        </style>
      </head>
      <body data-preset="Glassmorphism">
        <section class="slide slide-0" data-export-role="glass_hero">
          <div class="orb orb1"></div>
          <div class="slide-content"><div class="glass-card"></div></div>
        </section>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    ok, message = validate.check_glassmorphism_contract(soup, html, [])
    assert ok, message


def test_glassmorphism_contract_rejects_missing_orbs():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          :root {
            --bg-gradient-1:#667eea; --bg-gradient-2:#764ba2; --bg-gradient-3:#f093fb;
            --glass-bg:rgba(255,255,255,0.15); --glass-border:rgba(255,255,255,0.30);
            --glass-text-dark:#1a1a2e; --glass-text-light:rgba(255,255,255,0.92);
            --orb-purple:rgba(102,126,234,0.5); --orb-pink:rgba(240,147,251,0.4); --orb-mint:rgba(168,237,234,0.4);
          }
          .slide-0 { background: linear-gradient(135deg, #667eea, #764ba2, #f093fb); }
          .glass-card { backdrop-filter: blur(20px); }
        </style>
      </head>
      <body data-preset="Glassmorphism">
        <section class="slide slide-0"></section>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    ok, message = validate.check_glassmorphism_contract(soup, html, [])
    assert not ok
    assert "blurred orb layers missing" in message


def test_chinese_chan_contract_rejects_alias_or_centered_ghost():
    validate = load_validate_module()
    alias_html = """
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          :root { --bg:#FAFAF8; --text:#1a1a18; --text-muted:#6b6b68; --accent:#C41E3A; --accent-alt:#1B3A6B; --rule:rgba(26,26,24,0.15); }
        </style>
      </head>
      <body data-preset="Chinese Chan">
        <section class="slide"><div class="ghost-kanji"></div></section>
      </body>
    </html>
    """
    alias_soup = BeautifulSoup(alias_html, "html.parser")
    ok, message = validate.check_chinese_chan_contract(alias_soup, alias_html, [])
    assert not ok
    assert "input-only aliases emitted" in message

    centered_html = """
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          :root { --bg:#FAFAF8; --text:#1a1a18; --text-muted:#6b6b68; --accent:#C41E3A; --accent-alt:#1B3A6B; --rule:rgba(26,26,24,0.15); }
        </style>
      </head>
      <body data-preset="Chinese Chan">
        <section class="slide" data-export-role="zen_center">
          <div class="zen-ghost-kanji" style="left: 50%; transform: translateX(-50%);"></div>
        </section>
      </body>
    </html>
    """
    centered_soup = BeautifulSoup(centered_html, "html.parser")
    ok, message = validate.check_chinese_chan_contract(centered_soup, centered_html, [])
    assert not ok
    assert "off-center" in message
