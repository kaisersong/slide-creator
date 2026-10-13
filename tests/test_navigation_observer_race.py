"""Delayed viewport notifications must not undo a recent keyboard direction."""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest


def test_reversed_scroll_retains_keyboard_target_until_visible():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node required to exercise shared navigation")
    text = (Path(__file__).resolve().parent.parent / "references/js-engine.md").read_text()
    source = re.search(r"class SlidePresentation \{.*?\n\}\n", text, re.S).group()
    scenario = r"""
const assert = require('node:assert/strict');
global.window = {innerHeight: 900};
global.document = {body: {classList: {contains: () => false}}};
let observer;
global.IntersectionObserver = class {constructor(cb) {observer=cb;} observe() {}};
let positions = [0, 900, 1800];
const slides = positions.map((_, i) => ({
  getBoundingClientRect: () => ({top:positions[i],bottom:positions[i]+900}),
  scrollIntoView() {}
}));
const ctrl = Object.create(SlidePresentation.prototype);
Object.assign(ctrl, {slides, currentSlide:0, pendingSlide:null});
for (const name of ['setActiveSlide','updateProgress','updateDots','broadcastState','updateNotesPanel']) ctrl[name]=()=>{};
ctrl.setupObserver();
ctrl.next(); assert.equal(ctrl.currentSlide,1);
// Cover remains physically visible while the outgoing smooth scroll begins.
observer([{target:slides[0],isIntersecting:true}]);
assert.equal(ctrl.currentSlide,1);
ctrl.prev(); assert.equal(ctrl.currentSlide,0);
// A delayed forward-scroll observation arrives after ArrowLeft.
positions=[-600,300,1200];
observer([{target:slides[1],isIntersecting:true}]);
assert.equal(ctrl.currentSlide,0); assert.equal(ctrl.pendingSlide,0);
positions=[0,900,1800];
observer([{target:slides[0],isIntersecting:true}]);
assert.equal(ctrl.pendingSlide,null); assert.equal(ctrl.currentSlide,0);
// Stale intersecting=true cannot move the target once the slide is off screen.
observer([{target:slides[1],isIntersecting:true}]);
assert.equal(ctrl.currentSlide,0);
// Native scrolling remains supported after the keyboard target settles.
positions=[-900,0,900];
observer([{target:slides[1],isIntersecting:true}]);
assert.equal(ctrl.currentSlide,1);
"""
    subprocess.run([node, "-e", source + scenario], check=True, capture_output=True, text=True)
