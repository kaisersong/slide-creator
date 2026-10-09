from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from low_context import render_from_brief
from preset_capabilities import get_preset_render_capability
from validate_html import validate

THEMES = (("molten-flow", "熔金流体"), ("stellar-vortex", "星核跃迁"))


def brief(name):
    return json.loads((ROOT / "demos" / name / "BRIEF.json").read_text())


@pytest.mark.parametrize("name,label", THEMES)
def test_friendly_name_and_canonical_preset_select_the_same_theme(name, label):
    friendly = get_preset_render_capability(label)
    canonical = get_preset_render_capability("custom:" + name)
    assert friendly.can_render
    assert friendly.reference_path == canonical.reference_path
    assert friendly.renderer_strategy == "custom_theme"


@pytest.mark.parametrize("name,label", THEMES)
@pytest.mark.parametrize("intent", ["none", "pptx", "png"])
def test_render_and_static_export_preserve_caller_content(name, label, intent, tmp_path):
    data = brief(name)
    data["runtime"]["export_intent"] = intent
    data["narrative"]["slides"][1]["supporting_facts"] = ["客户增长 18%", "成本下降 12%", "三个月内完成迁移"]
    html, _, _ = render_from_brief(data)
    soup = BeautifulSoup(html, "html.parser")
    assert len(soup.select(".sh-scene--cover")) == 1
    assert len(soup.select("canvas")) == (1 if intent == "none" else 0)
    assert ("CoverEffectController" in html) == (intent == "none")
    assert "data:image/webp;base64," in html
    assert "客户增长 18%" in soup.select(".slide")[1].get_text()
    assert "成本下降 12%" in soup.select(".slide")[1].get_text()
    assert "三个月内完成迁移" in soup.select(".slide")[1].get_text()
    assert not soup.select(".sh-scene--content canvas, .sh-scene--closing canvas")
    target = tmp_path / (name + ".html")
    target.write_text(html)
    assert validate(target, strict=True)


@pytest.mark.parametrize("name,label", THEMES)
def test_shared_runtime_and_shader_sources_are_embedded_without_drift(name, label):
    starter = (ROOT / "themes" / name / "starter.html").read_text()
    shared = re.search(r"// BEGIN SHARED COVER RUNTIME\n(.*?)// END SHARED COVER RUNTIME", starter, re.S).group(1)
    assert shared == (ROOT / "references/cover-effects-runtime.js").read_text()
    config_text = starter.split("window.__coverEffectDefinition = ", 1)[1].split(";\n// BEGIN", 1)[0]
    config = json.loads(config_text)
    assert config["fragment"] == (ROOT / "themes" / name / "effect.frag").read_text()


@pytest.mark.parametrize("name,label", THEMES)
def test_static_poster_contains_visible_effect_detail(name, label):
    image_api = pytest.importorskip("PIL.Image")
    with image_api.open(ROOT / "themes" / name / "cover.webp") as image:
        assert image.width >= 1280 and image.height >= 720
        extrema = image.convert("RGB").crop((image.width // 2, 0, image.width, image.height)).getextrema()
        assert any(high - low > 120 for low, high in extrema)
        assert max(high for _, high in extrema) > 200


@pytest.fixture(scope="module")
def browser():
    api = pytest.importorskip("playwright.sync_api")
    with api.sync_playwright() as p:
        try:
            instance = p.chromium.launch(channel="chrome", headless=True)
        except api.Error:
            pytest.skip("Chrome is required for cover rendering checks")
        yield instance
        instance.close()


@pytest.fixture(params=[theme[0] for theme in THEMES])
def page(request, browser, tmp_path):
    html, _, _ = render_from_brief(brief(request.param))
    target = tmp_path / (request.param + ".html")
    target.write_text(html)
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    tab = context.new_page()
    tab.local_url = target.as_uri()
    tab.deck_html = html
    yield tab
    context.close()


def state(page):
    return page.evaluate("window.__coverEffectQA.state()")


def stopped(page):
    page.wait_for_function("!window.__coverEffectQA.state().rafActive && window.__coverEffectQA.state().canvasHidden")
    before = state(page)["drawCount"]
    page.wait_for_timeout(150)
    assert state(page)["drawCount"] == before


def start(page):
    page.goto(page.local_url)
    page.wait_for_function("window.__coverEffectQA.state().drawCount > 2")


def test_offline_file_playback_navigation_and_suspend_states(page):
    page.context.set_offline(True)
    errors = []
    external_requests = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("request", lambda request: external_requests.append(request.url)
            if request.url.startswith(("http://", "https://")) else None)
    start(page)
    before = state(page)["drawCount"]
    page.wait_for_function(f"window.__coverEffectQA.state().drawCount > {before + 2}")
    for _ in range(3):
        page.keyboard.press("ArrowRight")
        page.wait_for_function("!window.__coverEffectQA.state().active")
        stopped(page)
        page.keyboard.press("ArrowLeft")
        page.wait_for_function("window.__coverEffectQA.state().rafActive")
    page.keyboard.press("F5")
    page.wait_for_function("document.body.classList.contains('presenting')")
    page.keyboard.press("ArrowRight")
    page.wait_for_function("!window.__coverEffectQA.state().active")
    stopped(page)
    page.keyboard.press("ArrowLeft")
    page.wait_for_function("window.__coverEffectQA.state().rafActive")
    page.keyboard.press("b")
    page.wait_for_function("document.body.classList.contains('presenting-black')")
    stopped(page)
    page.keyboard.press("b")
    page.wait_for_function("window.__coverEffectQA.state().rafActive")
    for event, resume in [("beforeprint", "afterprint"), ("pagehide", "pageshow")]:
        page.evaluate("event => dispatchEvent(new Event(event))", event)
        stopped(page)
        page.evaluate("event => dispatchEvent(new Event(event))", resume)
        page.wait_for_function("window.__coverEffectQA.state().rafActive")
    page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,value:true}); document.dispatchEvent(new Event('visibilitychange'))")
    stopped(page)
    page.evaluate("delete document.hidden;document.dispatchEvent(new Event('visibilitychange'))")
    page.wait_for_function("window.__coverEffectQA.state().rafActive")
    assert not errors
    assert not external_requests


def test_plain_http_origin_automatically_animates(page):
    page.route("http://covers.test/**", lambda route: route.fulfill(status=200, content_type="text/html", body=page.deck_html))
    page.goto("http://covers.test/")
    assert page.evaluate("!window.isSecureContext")
    page.wait_for_function("window.__coverEffectQA.state().drawCount > 2")
    assert state(page)["backend"] == "webgl2"


def test_reduced_motion_and_context_restoration_preserve_cover_lifecycle(page):
    page.emulate_media(reduced_motion="reduce")
    page.goto(page.local_url)
    stopped(page)
    assert state(page)["drawCount"] == 0
    page.emulate_media(reduced_motion="no-preference")
    page.wait_for_function("window.__coverEffectQA.state().rafActive")
    assert page.evaluate("window.__coverEffectQA.loseContext()")
    page.wait_for_function("window.__coverEffectQA.state().contextLost")
    stopped(page)
    page.keyboard.press("ArrowRight")
    page.wait_for_function("!window.__coverEffectQA.state().active")
    page.evaluate("window.__coverEffectQA.restoreContext()")
    page.wait_for_function("!window.__coverEffectQA.state().contextLost")
    stopped(page)
    page.keyboard.press("ArrowLeft")
    page.wait_for_function("window.__coverEffectQA.state().rafActive")
    page.emulate_media(reduced_motion="reduce")
    stopped(page)


def test_unavailable_gpu_shows_detailed_poster(page):
    page.add_init_script("""
      const original=HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext=function(type,...args) {
        return type==='webgl2' ? null : original.call(this,type,...args);
      };
    """)
    page.goto(page.local_url)
    stopped(page)
    assert state(page)["reason"] == "webgl2-unavailable"
    assert page.locator(".sh-cover-field").evaluate("e => getComputedStyle(e).opacity") == "1"


def test_compile_failure_and_forced_fallback_stop_rendering(page):
    bad = page.deck_html.replace("#version 300 es\\nprecision highp float;", "INVALID_SHADER\\nprecision highp float;", 1)
    page.route("http://invalid-cover.test/**", lambda route: route.fulfill(status=200, content_type="text/html", body=bad))
    page.goto("http://invalid-cover.test/")
    stopped(page)
    assert state(page)["reason"] == "shader-compilation-failed"
    start(page)
    page.evaluate("window.__coverEffectQA.forceFallback()")
    stopped(page)
