"""Exercise the shipped WebGPU/WebGL2 controller in a real Chrome session."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from low_context import render_from_brief


@pytest.fixture(scope="module")
def browser():
    api = pytest.importorskip("playwright.sync_api")
    with api.sync_playwright() as p:
        try:
            instance = p.chromium.launch(channel="chrome", headless=True)
        except api.Error:
            pytest.skip("Chrome is required for WebGPU runtime checks")
        yield instance
        instance.close()


@pytest.fixture
def page(browser, tmp_path):
    brief = json.loads((ROOT / "demos/shader-hero/BRIEF.json").read_text())
    output, _, _ = render_from_brief(brief)
    path = tmp_path / "deck.html"
    path.write_text(output)
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    tab = context.new_page()
    tab.local_deck_url = path.as_uri()
    tab.deck_url = "https://slide-preview.test/"
    tab.deck_html = output
    tab.route("https://slide-preview.test/**", lambda route: route.fulfill(
        status=200, content_type="text/html", body=output
    ))
    yield tab
    context.close()


def state(page):
    return page.evaluate("window.__shaderHeroQA.state()")


def start_gpu(page, backend="webgpu"):
    if backend == "webgl2":
        page.add_init_script("Object.defineProperty(navigator,'gpu',{value:undefined})")
    page.goto(page.deck_url)
    page.wait_for_function("window.__shaderHeroQA && !window.__shaderHeroQA.state().pending")
    if not state(page)["ready"]:
        pytest.skip(f"WebGPU unavailable: {state(page)['reason']}")
    if state(page)["backend"] != backend:
        pytest.skip(f"{backend} unavailable; using {state(page)['backend']}")
    page.wait_for_function("window.__shaderHeroQA.state().drawCount > 2")


def assert_stopped(page):
    page.wait_for_function("!window.__shaderHeroQA.state().rafActive && window.__shaderHeroQA.state().canvasHidden")
    before = state(page)
    assert not before["rafActive"]
    assert before["canvasHidden"]
    page.wait_for_timeout(160)
    assert state(page)["drawCount"] == before["drawCount"]


@pytest.mark.parametrize("backend", ["webgpu", "webgl2"])
def test_navigation_presentation_black_screen_and_print_stop_gpu(page, backend):
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    start_gpu(page, backend)
    for _ in range(3):
        page.keyboard.press("ArrowRight")
        page.wait_for_function("!window.__shaderHeroQA.state().active")
        assert_stopped(page)
        page.keyboard.press("ArrowLeft")
        page.wait_for_function("window.__shaderHeroQA.state().rafActive")
    page.keyboard.press("F5")
    page.wait_for_function("document.body.classList.contains('presenting')")
    page.keyboard.press("ArrowRight")
    page.wait_for_function("!window.__shaderHeroQA.state().active")
    assert_stopped(page)
    page.keyboard.press("ArrowLeft")
    page.wait_for_function("window.__shaderHeroQA.state().rafActive")
    page.keyboard.press("b")
    page.wait_for_function("document.body.classList.contains('presenting-black')")
    assert_stopped(page)
    page.keyboard.press("b")
    page.wait_for_function("window.__shaderHeroQA.state().rafActive")
    page.evaluate("dispatchEvent(new Event('beforeprint'))")
    assert_stopped(page)
    page.evaluate("dispatchEvent(new Event('afterprint'))")
    page.wait_for_function("window.__shaderHeroQA.state().rafActive")
    page.evaluate("dispatchEvent(new Event('pagehide'))")
    assert_stopped(page)
    page.evaluate("dispatchEvent(new Event('pageshow'))")
    page.wait_for_function("window.__shaderHeroQA.state().rafActive")
    assert not errors


@pytest.mark.parametrize("backend", ["webgpu", "webgl2"])
def test_reduced_motion_is_static_and_resumes_when_disabled(page, backend):
    if backend == "webgl2":
        page.add_init_script("Object.defineProperty(navigator,'gpu',{value:undefined})")
    page.emulate_media(reduced_motion="reduce")
    page.goto(page.deck_url)
    assert_stopped(page)
    assert state(page)["drawCount"] == 0
    page.emulate_media(reduced_motion="no-preference")
    page.wait_for_function("!window.__shaderHeroQA.state().reducedMotion && (window.__shaderHeroQA.state().ready || window.__shaderHeroQA.state().reason)")
    if not state(page)["ready"]:
        pytest.skip("WebGPU unavailable")
    page.wait_for_function("window.__shaderHeroQA.state().rafActive")
    page.emulate_media(reduced_motion="reduce")
    page.wait_for_function("window.__shaderHeroQA.state().reducedMotion")
    assert_stopped(page)


def test_missing_webgpu_uses_webgl_animation(page):
    page.add_init_script("Object.defineProperty(navigator,'gpu',{value:undefined})")
    page.goto(page.deck_url)
    page.wait_for_function("window.__shaderHeroQA.state().drawCount > 2")
    before = state(page)
    assert before["backend"] == "webgl2"
    assert before["rafActive"]
    page.wait_for_function(f"window.__shaderHeroQA.state().drawCount > {before['drawCount'] + 2}")


def test_plain_http_origin_animates_without_secure_context(page):
    page.route("http://slide-preview.test/**", lambda route: route.fulfill(
        status=200, content_type="text/html", body=page.deck_html
    ))
    page.goto("http://slide-preview.test/")
    assert page.evaluate("!window.isSecureContext && !navigator.gpu")
    page.wait_for_function("window.__shaderHeroQA.state().drawCount > 2")
    before = state(page)
    assert before["backend"] == "webgl2"
    page.wait_for_function(f"window.__shaderHeroQA.state().drawCount > {before['drawCount'] + 2}")
    page.keyboard.press("ArrowRight")
    page.wait_for_function("!window.__shaderHeroQA.state().active")
    assert_stopped(page)


def test_offline_single_html_defaults_to_webgl_and_stops_on_content(page):
    # No server and no network: this is the user's actual double-click path.
    page.context.set_offline(True)
    external_requests = []
    page.on("request", lambda request: external_requests.append(request.url)
            if request.url.startswith(("https://", "http://")) else None)
    page.goto(page.local_deck_url)
    page.wait_for_function("window.__shaderHeroQA.state().drawCount > 2")
    before = state(page)
    assert before["backend"] == "webgl2"
    assert before["rafActive"]
    page.wait_for_function(f"window.__shaderHeroQA.state().drawCount > {before['drawCount'] + 2}")
    page.keyboard.press("ArrowRight")
    page.wait_for_function("!window.__shaderHeroQA.state().active")
    assert_stopped(page)
    page.keyboard.press("ArrowLeft")
    page.wait_for_function("window.__shaderHeroQA.state().rafActive")
    assert not external_requests


def test_missing_both_gpu_backends_uses_visible_static_background(page):
    page.add_init_script("""
      Object.defineProperty(navigator,'gpu',{value:undefined});
      const getContext = HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext = function(type, ...args) {
        return type === 'webgl2' ? null : getContext.call(this, type, ...args);
      };
    """)
    page.goto(page.deck_url)
    assert state(page)["reason"] == "webgl2-unavailable"
    assert_stopped(page)
    assert page.locator(".sh-cover-field").evaluate("e => getComputedStyle(e).opacity") == "1"


def test_device_loss_reveals_static_background(page):
    start_gpu(page)
    page.evaluate("window.__shaderHeroQA.loseDevice()")
    page.wait_for_function("window.__shaderHeroQA.state().reason === 'device-lost'")
    assert_stopped(page)
    assert page.locator(".sh-cover-field").evaluate("e => getComputedStyle(e).opacity") == "1"


def test_initialization_timeout_and_late_results_cannot_start_gpu(page):
    page.add_init_script("""
      Object.defineProperty(navigator, 'gpu', {value:{requestAdapter: () => new Promise(resolve => {
        window.resolveLateAdapter = resolve;
      })}});
    """)
    page.goto(page.deck_url)
    page.wait_for_function("window.__shaderHeroQA.state().reason === 'adapter-timeout'", timeout=5000)
    page.evaluate("window.resolveLateAdapter({requestDevice: () => { throw new Error('Late adapter was used'); }})")
    assert_stopped(page)
    assert state(page)["drawCount"] == 0


def test_initialization_completing_after_navigation_keeps_gpu_stopped(page):
    page.add_init_script("""
      if (navigator.gpu) {
        const request = navigator.gpu.requestAdapter.bind(navigator.gpu);
        navigator.gpu.requestAdapter = options => request(options).then(adapter => new Promise(resolve => {
          window.resolvePendingAdapter = () => resolve(adapter);
        }));
      }
    """)
    page.goto(page.deck_url)
    if page.evaluate("!navigator.gpu"):
        pytest.skip("WebGPU unavailable")
    page.wait_for_function("Boolean(window.resolvePendingAdapter)")
    page.keyboard.press("ArrowRight")
    page.wait_for_function("!window.__shaderHeroQA.state().active")
    page.evaluate("window.resolvePendingAdapter()")
    page.wait_for_function("!window.__shaderHeroQA.state().pending")
    assert_stopped(page)
    assert state(page)["drawCount"] == 0
    page.keyboard.press("ArrowLeft")
    page.wait_for_function("window.__shaderHeroQA.state().rafActive")


@pytest.mark.parametrize("backend", ["webgpu", "webgl2"])
def test_document_visibility_suspends_and_resumes(page, backend):
    start_gpu(page, backend)
    page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,value:true}); document.dispatchEvent(new Event('visibilitychange'))")
    assert_stopped(page)
    page.evaluate("delete document.hidden; document.dispatchEvent(new Event('visibilitychange'))")
    page.wait_for_function("window.__shaderHeroQA.state().rafActive")


def test_webgl_context_restoration_waits_for_visible_cover(page):
    start_gpu(page, "webgl2")
    assert page.evaluate("window.__shaderHeroQA.loseContext()")
    page.wait_for_function("window.__shaderHeroQA.state().reason === 'webgl-context-lost'")
    assert_stopped(page)
    page.keyboard.press("ArrowRight")
    page.wait_for_function("!window.__shaderHeroQA.state().active")
    page.evaluate("window.__shaderHeroQA.restoreContext()")
    page.wait_for_function("window.__shaderHeroQA.state().reason === null")
    assert_stopped(page)
    page.keyboard.press("ArrowLeft")
    page.wait_for_function("window.__shaderHeroQA.state().rafActive")
