"""Run the shipped cover controller against a deterministic browser lifecycle.

The DOM and WebGL boundaries are mocked, but the complete, unmodified theme
script runs in Node. Assertions count real scheduled callbacks and draw calls,
so a stopped-looking canvas cannot hide a background render loop.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
RUNTIMES = (
    "themes/fantasy-rainbow/starter.html",
    "demos/fantasy-rainbow-zh.html",
    "demos/fantasy-rainbow-en.html",
)

HARNESS = r"""
const assert = require('node:assert/strict');
const vm = require('node:vm');
const payload = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
let now = 100, sequence = 0, slideGeometryReads = 0, drawCalls = 0, contextRequests = 0;
const frames = new Map(), timers = new Map(), observers = [];
class Target {
  constructor() { this.listeners = new Map(); }
  addEventListener(type, callback) {
    if (!this.listeners.has(type)) this.listeners.set(type, new Set());
    this.listeners.get(type).add(callback);
  }
  removeEventListener(type, callback) { this.listeners.get(type)?.delete(callback); }
  dispatchEvent(event) {
    if (!event.preventDefault) event.preventDefault = () => { event.defaultPrevented = true; };
    event.target = this;
    for (const callback of [...(this.listeners.get(event.type) || [])]) callback(event);
    return !event.defaultPrevented;
  }
}
class Element extends Target {
  constructor(classes = '') {
    super();
    this.dataset = {}; this.style = {setProperty() {}, removeProperty() {}};
    this.hidden = false; this.width = 1280; this.height = 720;
    this.rect = {top: 0, bottom: 720, left: 0, right: 1280, width: 1280, height: 720};
    const names = new Set(classes.split(/\s+/).filter(Boolean));
    const change = (name, on) => {
      const before = names.has(name);
      on ? names.add(name) : names.delete(name);
      if (before !== on) {
        for (const observer of observers) {
          if (observer.targets.has(this)) observer.pending.push({type: 'attributes', attributeName: 'class', target: this});
        }
      }
      return on;
    };
    this.classList = {
      contains: name => names.has(name),
      add: (...values) => values.forEach(name => change(name, true)),
      remove: (...values) => values.forEach(name => change(name, false)),
      toggle: (name, force) => change(name, force === undefined ? !names.has(name) : Boolean(force))
    };
  }
  getBoundingClientRect() {
    if (this.classList.contains('slide')) slideGeometryReads += 1;
    return {...this.rect};
  }
  querySelectorAll() { return []; }
  querySelector() { return null; }
  setAttribute(name, value) { this[name] = String(value); }
  getAttribute(name) { return this[name] ?? null; }
}
global.MutationObserver = class {
  constructor(callback) { this.callback = callback; this.targets = new Set(); this.pending = []; observers.push(this); }
  observe(target) { this.targets.add(target); }
  disconnect() { this.targets.clear(); this.pending = []; }
};
const windowTarget = new Target();
global.window = global;
global.addEventListener = windowTarget.addEventListener.bind(windowTarget);
global.removeEventListener = windowTarget.removeEventListener.bind(windowTarget);
global.dispatchEvent = windowTarget.dispatchEvent.bind(windowTarget);
global.innerWidth = 1280; global.innerHeight = 720; global.devicePixelRatio = 1;
global.performance = {now: () => now};
global.requestAnimationFrame = callback => { const id = ++sequence; frames.set(id, callback); return id; };
global.cancelAnimationFrame = id => frames.delete(id);
global.setTimeout = (callback, delay = 0) => { const id = ++sequence; timers.set(id, {callback, at: now + delay}); return id; };
global.clearTimeout = id => timers.delete(id);
const motion = new Target();
motion.matches = Boolean(payload.reducedMotion);
motion.addListener = callback => motion.addEventListener('change', callback);
global.matchMedia = () => motion;
const body = new Element(), root = new Element(), canvas = new Element();
const slides = [new Element('slide iri-scene iri-scene--hero'), new Element('slide iri-scene slide-content'), new Element('slide iri-scene iri-scene--closing')];
function positionSlides(index) {
  slides.forEach((slide, i) => {
    slide.rect.top = (i - index) * 720;
    slide.rect.bottom = slide.rect.top + 720;
  });
}
positionSlides(payload.initialIndex || 0);
slides[payload.initialIndex || 0].classList.add('visible');
const glMethods = {
  createShader: () => ({}), getShaderParameter: () => true,
  createProgram: () => ({}), getProgramParameter: () => true,
  createBuffer: () => ({}), getAttribLocation: () => 1,
  getUniformLocation: () => ({}), getExtension: () => null,
  drawArrays: () => { drawCalls += 1; }
};
const gl = new Proxy(glMethods, {get: (object, key) => key in object ? object[key] : /^[A-Z_]+$/.test(key) ? 1 : () => {}});
canvas.getContext = () => { contextRequests += 1; return gl; };
global.document = new Target();
document.body = body; document.documentElement = root; document.hidden = Boolean(payload.hidden);
document.getElementById = id => id === 'iridescence-canvas' ? canvas : null;
document.querySelectorAll = selector => {
  if (selector === '.slide') return slides;
  if (selector.includes('.slide') || selector.includes('.iri-scene--hero')) {
    const names = [...selector.matchAll(/\.([\w-]+)/g)].map(match => match[1]);
    return slides.filter(slide => names.every(name => slide.classList.contains(name)));
  }
  return [];
};
document.querySelector = selector => selector === '#iridescence-canvas' ? canvas : document.querySelectorAll(selector)[0] || null;
function flushMutations() {
  for (let round = 0; round < 10; round++) {
    const pending = observers.filter(observer => observer.pending.length);
    if (!pending.length) return;
    for (const observer of pending) observer.callback(observer.pending.splice(0), observer);
  }
  throw new Error('Mutation observers did not settle');
}
function event(target, type) { target.dispatchEvent({type}); flushMutations(); }
function advance(milliseconds) {
  now += milliseconds;
  for (const [id, timer] of [...timers]) {
    if (timer.at <= now) { timers.delete(id); timer.callback(); }
  }
  flushMutations();
}
function tick(count = 1) {
  for (let i = 0; i < count; i++) {
    now += 16.67;
    for (const [id, callback] of [...frames]) {
      if (!frames.delete(id)) continue;
      callback(now);
    }
    flushMutations();
  }
}
function navigate(index, presenting = false) {
  body.classList.toggle('presenting', presenting);
  positionSlides(index);
  slides.forEach((slide, i) => {
    slide.classList.toggle('visible', i === index);
    slide.classList.toggle('p-on', presenting && i === index);
  });
  flushMutations();
  event(windowTarget, 'scroll');
  advance(50);
}
function setMotion(value) { motion.matches = value; event(motion, 'change'); }
function setHidden(value) { document.hidden = value; event(document, 'visibilitychange'); }
function assertStopped(message) {
  assert.equal(frames.size, 0, message + ': pending animation callbacks');
  const before = drawCalls;
  tick(120);
  assert.equal(drawCalls, before, message + ': WebGL kept drawing');
}
function assertRunning(message) {
  assert.equal(frames.size, 1, message + ': expected exactly one animation callback');
  const before = drawCalls;
  tick(3);
  assert.equal(drawCalls, before + 3, message + ': missing rendered frames');
  assert.equal(frames.size, 1, message + ': duplicate animation callback');
}
vm.runInThisContext(payload.runtime, {filename: payload.path});
flushMutations();
const qa = window.__iridescenceQA;
assert.ok(qa, 'theme QA interface is missing');
vm.runInThisContext(payload.scenario, {filename: payload.path + ':scenario'});
"""


@pytest.fixture(params=RUNTIMES, ids=("starter", "zh-demo", "en-demo"))
def runtime(request):
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required to exercise the shipped JavaScript runtime")
    html = (ROOT / request.param).read_text(encoding="utf-8")
    # Generated decks combine the shared presentation engine and theme IIFE
    # into a single script; select the same complete controller in both forms.
    script = re.search(
        r'(\(function \(\) \{\s*"use strict";\s*class IridescenceController\b.*?\n\}\)\(\);)',
        html,
        re.DOTALL,
    )
    assert script is not None

    def run(scenario: str, **options):
        payload = {"runtime": script.group(1), "scenario": scenario, "path": request.param, **options}
        result = subprocess.run(
            [node, "-e", HARNESS], input=json.dumps(payload), capture_output=True, text=True, timeout=15
        )
        assert result.returncode == 0, result.stderr or result.stdout

    return run


def test_cover_navigation_stops_rendering_and_resumes_one_loop(runtime):
    runtime(r"""
assertRunning('initial cover');
for (const presenting of [false, true]) {
  for (let i = 0; i < 50; i++) {
    navigate(1, presenting);
    assert.equal(canvas.hidden, true, 'content must hide cover canvas');
    assert.equal(body.dataset.coverAnimating, 'false', 'content must pause cover CSS animation');
    assertStopped('content slide');
    navigate(2, presenting);
    assertStopped('closing slide');
    navigate(0, presenting);
    assert.equal(canvas.hidden, false, 'cover must restore canvas');
    assert.equal(body.dataset.coverAnimating, 'true', 'cover must resume CSS animation');
    for (let repeat = 0; repeat < 5; repeat++) qa.sync();
    assertRunning('returned cover');
  }
}
""")


def test_navigation_stops_before_scroll_and_resumes_after_cover_is_visible(runtime):
    runtime(r"""
assertRunning('initial cover');
// The shared engine selects its target before smooth scrolling changes geometry.
slides[0].classList.remove('visible'); slides[1].classList.add('visible');
flushMutations();
assertStopped('navigation away before smooth scroll');
positionSlides(1); event(windowTarget, 'scroll');
slides[1].classList.remove('visible'); slides[0].classList.add('visible');
flushMutations();
assertStopped('cover selected but still outside viewport');
positionSlides(0); event(windowTarget, 'scroll');
assertRunning('cover back inside viewport');
// Native scrolling can leave the cover before its observed class updates.
positionSlides(1); event(windowTarget, 'scroll');
assertStopped('native scroll outside cover');
""")


def test_hidden_document_and_pagehide_cannot_be_restarted_by_resize(runtime):
    runtime(r"""
assertRunning('initial cover');
setHidden(true);
assertStopped('hidden document');
assert.equal(body.dataset.coverAnimating, 'false', 'hidden document must pause CSS animation');
let before = drawCalls;
event(windowTarget, 'resize'); qa.sync();
assert.equal(drawCalls, before, 'hidden resize must not draw');
assertStopped('hidden after resize');
setHidden(false);
assertRunning('visible document');
event(windowTarget, 'pagehide');
assertStopped('pagehide');
before = drawCalls;
event(windowTarget, 'resize'); qa.sync();
assert.equal(drawCalls, before, 'pagehide resize must not draw');
assertStopped('pagehide after resize');
event(windowTarget, 'pageshow');
assertRunning('pageshow');
""")


def test_reduced_motion_changes_cancel_existing_work_immediately(runtime):
    runtime(r"""
assertRunning('initial cover');
const before = drawCalls;
setMotion(true);
assertStopped('reduced motion');
assert.equal(body.dataset.coverAnimating, 'false', 'reduced motion must pause CSS animation');
event(windowTarget, 'resize'); qa.sync();
assert.equal(drawCalls, before, 'reduced motion must not upload a new frame');
setMotion(false);
assertRunning('motion restored');
navigate(1);
setMotion(true); setMotion(false);
assertStopped('motion restored off cover');
""")


def test_frame_detects_reduced_motion_before_the_media_change_event(runtime):
    runtime(r"""
assertRunning('initial cover');
const before = drawCalls;
// Some browsers expose the new match before delivering the MQL change event.
motion.matches = true;
tick();
assert.equal(drawCalls, before, 'the first reduced-motion frame must not draw');
assertStopped('reduced motion before change event');
assert.equal(body.dataset.coverAnimating, 'false', 'CSS animation must pause with WebGL');
""")


@pytest.mark.parametrize("options", [{"reducedMotion": True}, {"hidden": True}, {"initialIndex": 1}], ids=("reduced-motion", "hidden", "content"))
def test_initially_inactive_cover_does_not_allocate_webgl(runtime, options):
    runtime(r"""
assert.equal(contextRequests, 0, 'inactive cover must not create a WebGL context');
assert.equal(drawCalls, 0, 'inactive cover must not draw');
assertStopped('initially inactive cover');
""", **options)


def test_print_and_blackout_suspend_without_breaking_resume(runtime):
    runtime(r"""
assertRunning('initial cover');
event(windowTarget, 'beforeprint');
assertStopped('printing');
assert.equal(body.dataset.coverAnimating, 'false', 'printing must pause CSS animation');
let before = drawCalls;
event(windowTarget, 'resize'); qa.sync();
assert.equal(drawCalls, before, 'print resize must not draw');
event(windowTarget, 'afterprint');
assertRunning('after print');
navigate(0, true);
body.classList.add('presenting-black'); flushMutations();
assertStopped('presentation blackout');
assert.equal(body.dataset.coverAnimating, 'false', 'blackout must pause CSS animation');
before = drawCalls;
event(windowTarget, 'resize'); qa.sync();
assert.equal(drawCalls, before, 'blackout resize must not draw');
body.classList.remove('presenting-black'); flushMutations();
assertRunning('blackout dismissed');
navigate(1, true);
event(windowTarget, 'beforeprint'); event(windowTarget, 'afterprint');
assertStopped('printing must not restart an inactive cover');
""")


def test_context_restoration_only_restarts_a_visible_cover(runtime):
    runtime(r"""
assertRunning('initial cover');
const lost = {type: 'webglcontextlost'};
canvas.dispatchEvent(lost);
assert.equal(lost.defaultPrevented, true, 'context loss must allow restoration');
assertStopped('lost WebGL context');
navigate(1);
const before = contextRequests;
event(canvas, 'webglcontextrestored');
assert.equal(contextRequests, before, 'restoration off cover must stay lazy');
assertStopped('restored context off cover');
navigate(0);
assertRunning('cover after restoration');
event(canvas, 'webglcontextlost');
event(canvas, 'webglcontextrestored');
assertRunning('restored visible cover');
""")


def test_animation_frames_do_not_rescan_slide_geometry(runtime):
    runtime(r"""
assertRunning('initial cover');
slideGeometryReads = 0;
tick(120);
assert.equal(slideGeometryReads, 0, 'steady cover frames must not measure slides');
assert.equal(frames.size, 1, 'steady cover frames must keep exactly one callback');
""")


def test_deterministic_snapshot_cancels_the_live_animation_loop(runtime):
    runtime(r"""
assertRunning('initial cover');
qa.setDeterministicTime(123.4);
assertStopped('deterministic snapshot');
qa.setDeterministicTime(null);
assertRunning('live animation after snapshot');
""")
