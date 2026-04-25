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


def build_html(script: str, *, preset: str | None = "Aurora Mesh") -> str:
    body_attrs = f' data-preset="{preset}"' if preset is not None else ""
    return f"""
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          .slide {{ height: 100vh; overflow: hidden; }}
          body.presenting {{ background: #111; }}
        </style>
      </head>
      <body{body_attrs}>
        <section class="slide" data-notes="slide 1"></section>
        <section class="slide" data-notes="slide 2"></section>
        <section class="slide" data-notes="slide 3"></section>
        <div class="edit-hotzone"></div>
        <script>
        {script}
        </script>
      </body>
    </html>
    """


VALID_RUNTIME = """
class SlidePresentation {
  constructor() {
    this.slides = document.querySelectorAll('.slide');
    this.channel = new BroadcastChannel('slide-creator-presenter');
    this.slides[0]?.classList.add('visible');
    this.slides[0]?.querySelectorAll('.reveal').forEach(r => r.classList.add('visible'));
    this.setupObserver();
    this.setupPresenter();
    this.setupEditor();
  }
  setupObserver() {
    return new IntersectionObserver(() => {}, { threshold: 0.5 });
  }
  setupPresenter() {
    this.channel.postMessage({ type: 'state' });
  }
  setupEditor() {
    return document.querySelector('.edit-hotzone');
  }
}

if (new URLSearchParams(location.search).has('presenter')) {
  const ch = new BroadcastChannel('slide-creator-presenter');
  ch.postMessage({ type: 'request-state' });
} else {
  class PresentMode {}
  new PresentMode(new SlidePresentation());
}

(function() {
  var slides = document.querySelectorAll('.slide');
  var last = slides[slides.length - 1];
  var credit = document.createElement('div');
  credit.className = 'slide-credit';
  last.appendChild(credit);
})();
"""


def test_preset_metadata_passes_with_real_value():
    validate = load_validate_module()
    html = build_html(VALID_RUNTIME)
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_preset_metadata(soup, html, [])

    assert ok
    assert "Aurora Mesh" in message


def test_preset_metadata_fails_when_missing():
    validate = load_validate_module()
    html = build_html(VALID_RUNTIME, preset=None)
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_preset_metadata(soup, html, [])

    assert not ok
    assert "data-preset" in message


def test_shared_js_engine_contract_accepts_non_blue_sky_runtime():
    validate = load_validate_module()
    html = build_html(VALID_RUNTIME)
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_shared_js_engine_contract(soup, html, [])

    assert ok
    assert "Shared js-engine runtime present" in message


def test_shared_js_engine_contract_flags_missing_first_slide_visible_fix():
    validate = load_validate_module()
    html = build_html(
        VALID_RUNTIME.replace(
            "    this.slides[0]?.classList.add('visible');\n"
            "    this.slides[0]?.querySelectorAll('.reveal').forEach(r => r.classList.add('visible'));\n",
            "",
        )
    )
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_shared_js_engine_contract(soup, html, [])

    assert not ok
    assert "first-slide visible fix" in message


def test_shared_js_engine_contract_rejects_comment_spoof():
    validate = load_validate_module()
    spoof = """
class SlidePresentation {}
/* new BroadcastChannel('slide-creator-presenter') */
/* new URLSearchParams(location.search).has('presenter') */
/* slides[0]?.classList.add('visible') */
/* slides[0]?.querySelectorAll('.reveal').forEach(r => r.classList.add('visible')) */
/* class PresentMode {} */
/* new PresentMode(new SlidePresentation()) */
/* var last = slides[slides.length - 1]; credit.className = 'slide-credit'; last.appendChild(credit); */
"""
    html = build_html(spoof)
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_shared_js_engine_contract(soup, html, [])

    assert not ok
    assert "BroadcastChannel sync" in message or "first-slide visible fix" in message


def test_shared_js_engine_contract_rejects_string_spoof():
    validate = load_validate_module()
    spoof = """
class SlidePresentation {
  constructor() {
    this.slides = document.querySelectorAll('.slide');
    const fake = "new BroadcastChannel('slide-creator-presenter'); "
      + "new URLSearchParams(location.search).has('presenter'); "
      + "slides[0]?.classList.add('visible'); "
      + "slides[0]?.querySelectorAll('.reveal').forEach(r => r.classList.add('visible')); "
      + "credit.className = 'slide-credit'; "
      + "slides[slides.length - 1].appendChild(credit);";
  }
}
class PresentMode {}
new PresentMode(new SlidePresentation());
"""
    html = build_html(spoof)
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_shared_js_engine_contract(soup, html, [])

    assert not ok
    assert "BroadcastChannel sync" in message or "?presenter branch" in message


def test_shared_js_engine_contract_skips_blue_sky_runtime():
    validate = load_validate_module()
    html = build_html("class SlidePresentation {}", preset="Blue Sky")
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_shared_js_engine_contract(soup, html, [])

    assert ok
    assert "Blue Sky" in message
