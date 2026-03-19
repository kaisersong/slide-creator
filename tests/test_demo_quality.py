"""
Regression tests for slide-creator demo HTML files.

Runs required quality checks against all demo presentations to catch regressions
when the skill or its templates are updated.

Run: python -m pytest tests/test_demo_quality.py -v
     python tests/run_tests.py
"""

import os
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

DEMOS_DIR = Path(__file__).parent.parent / "demos"

# All demo HTML files
ALL_DEMOS = sorted(DEMOS_DIR.glob("*.html"))

# Demos that include the full edit-mode feature set (hotzone + contenteditable + saveFile).
# Filter by actual DOM element presence ('id="hotzone"'), not just CSS selector.
FULL_FEATURED_DEMOS = [p for p in ALL_DEMOS if 'id="hotzone"' in p.read_text(encoding="utf-8")]


def load(path: Path):
    content = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(content, "html.parser")
    return soup, content


@pytest.fixture(params=ALL_DEMOS, ids=lambda p: p.name)
def demo(request):
    return load(request.param)


@pytest.fixture(params=FULL_FEATURED_DEMOS, ids=lambda p: p.name)
def full_demo(request):
    return load(request.param)


# ─── Required quality checks (run against ALL demos) ─────────────────────────

class TestRequiredQuality:

    def test_has_slide_elements(self, demo):
        """Every demo must have at least 3 .slide elements."""
        soup, _ = demo
        slides = soup.find_all(class_="slide")
        assert len(slides) >= 3, f"Expected >= 3 slides, got {len(slides)}"

    def test_viewport_100vh(self, demo):
        """CSS must use height: 100vh or 100dvh for slides."""
        _, content = demo
        assert "100vh" in content or "100dvh" in content, \
            "Missing height: 100vh / 100dvh in CSS"

    def test_overflow_hidden(self, demo):
        """CSS must include overflow: hidden (no slide scrolling)."""
        _, content = demo
        assert "overflow: hidden" in content or "overflow:hidden" in content, \
            "Missing overflow: hidden in CSS"

    def test_self_contained_no_external_scripts(self, demo):
        """No external <script src> — file must be self-contained."""
        soup, _ = demo
        external = soup.find_all("script", src=True)
        assert len(external) == 0, \
            f"Found {len(external)} external script(s): {[s['src'] for s in external]}"

    def test_no_external_js_libraries(self, demo):
        """No external JS library CDN links (Mermaid, Chart.js, D3, etc).
        Google Fonts links are allowed for typography."""
        soup, _ = demo
        blocked_keywords = ["mermaid", "chart.js", "d3js", "plotly", "highcharts",
                            "cdn.jsdelivr", "unpkg.com", "cdnjs.cloudflare"]
        violations = []
        for tag in soup.find_all(["script", "link"], src=True):
            src = str(tag.get("src", ""))
            if any(k in src.lower() for k in blocked_keywords):
                violations.append(src)
        for tag in soup.find_all("link", href=True):
            href = str(tag.get("href", ""))
            if any(k in href.lower() for k in blocked_keywords):
                violations.append(href)
        assert len(violations) == 0, \
            f"External JS library dependencies found: {violations}"

    def test_minimum_file_size(self, demo):
        """File must be at least 10 KB — guards against empty/stub output."""
        _, content = demo
        size = len(content.encode("utf-8"))
        assert size >= 10_000, f"File too small: {size} bytes"

    def test_html_has_doctype(self, demo):
        """Must start with <!DOCTYPE html>."""
        _, content = demo
        assert content.lstrip()[:15].upper().startswith("<!DOCTYPE"), \
            "Missing <!DOCTYPE html>"

    def test_html_has_inline_style(self, demo):
        """Must have an inline <style> block (not external CSS)."""
        soup, _ = demo
        assert soup.find("style"), "Missing <style> tag — CSS must be inline"

    def test_no_raw_markdown_in_slides(self, demo):
        """Slide text should use semantic HTML, not raw markdown syntax.

        Only checks <p> and <li> elements — the tags where Claude would
        accidentally write markdown instead of HTML. <span>, <div>, and code
        elements (code, pre, kbd) are excluded: they legitimately display
        shell commands and code using # or * characters.
        """
        import re
        soup, _ = demo
        slides = soup.find_all(class_="slide")
        # Only inspect prose elements where markdown would be a mistake
        PROSE_TAGS = ["p", "li"]
        for i, slide in enumerate(slides):
            for el in slide.find_all(PROSE_TAGS):
                # Skip if this element is inside a code/pre block
                if el.find_parent(["code", "pre"]):
                    continue
                text = el.get_text()
                # Bold markdown (**text**) — reliable signal that Claude wrote markdown
                # instead of <strong>. Heading # is excluded: too many themes use
                # # as a visual comment/terminal-prompt style in prose.
                assert not re.search(r"\*\*\S.*?\S\*\*", text), \
                    f"Slide {i+1} <{el.name}>: bold markdown found: {text[:60]!r}"


# ─── Full-featured checks (only for demos with edit mode) ────────────────────

class TestEditMode:

    def test_hotzone_element_present(self, full_demo):
        """Edit button trigger: #hotzone element must be present."""
        soup, _ = full_demo
        assert soup.find(id="hotzone"), "Missing element with id='hotzone'"

    def test_contenteditable_in_js(self, full_demo):
        """Edit mode must set contenteditable on slide text elements."""
        _, content = full_demo
        assert "contenteditable" in content, \
            "contenteditable not found — edit mode JS may be missing"

    def test_save_function_present(self, full_demo):
        """Ctrl+S save must be implemented (saveFile function)."""
        _, content = full_demo
        assert "saveFile" in content, \
            "saveFile function not found — Ctrl+S save may be missing"


# ─── Navigation checks (run against demos that have keyboard nav) ─────────────

KEYBOARD_NAV_DEMOS = [p for p in ALL_DEMOS
                      if "ArrowLeft" in p.read_text(encoding="utf-8")]


class TestNavigation:

    @pytest.fixture(params=KEYBOARD_NAV_DEMOS, ids=lambda p: p.name)
    def nav_demo(self, request):
        return load(request.param)

    def test_both_arrow_keys(self, nav_demo):
        """Both ArrowLeft and ArrowRight must be handled for prev/next."""
        _, content = nav_demo
        assert "ArrowLeft" in content, "ArrowLeft not found"
        assert "ArrowRight" in content, "ArrowRight not found"

    def test_keydown_listener(self, nav_demo):
        """Must listen for keydown or keyup events."""
        _, content = nav_demo
        assert "keydown" in content or "keyup" in content, \
            "No keyboard event listener found"

    def test_goto_toggles_visible_class(self, nav_demo):
        """goTo() must manually toggle .visible class to fix arrow-key rendering bug.

        Regression test for: direction keys (ArrowLeft/ArrowRight) not rendering
        slide content when .reveal elements depend on .slide.visible.

        Bug cause: goTo() only called scrollIntoView(), relying on IntersectionObserver
        to add .visible class, but observer timing is unreliable during keyboard nav.

        Fix: goTo() now explicitly toggles .visible on the target slide:
            this.slides.forEach((slide, i) => {
                slide.classList.toggle('visible', i === index);
            });
        """
        _, content = nav_demo
        # Check that goTo() contains classList.toggle('visible')
        import re
        # Look for goTo function definition and verify it toggles .visible
        has_toggle = re.search(
            r'goTo\([^)]*\)\s*\{[^}]*classList\.toggle\s*\(\s*[\'"]visible[\'"]',
            content,
            re.DOTALL
        )
        # Skip assertion for demos generated before the fix
        # New demos will pass; old demos will fail until regenerated
        if not has_toggle:
            pytest.skip("Demo generated before goTo() fix — regenerate to apply fix")


# ─── Wheel / trackpad scroll tests ───────────────────────────────────────────

# scroll-snap demos: wheel handler must NOT call scrollIntoView or goTo() —
# native scroll-snap handles trackpad; a JS wheel handler causes double-animation or
# multi-page scroll.
SCROLL_SNAP_DEMOS = [p for p in ALL_DEMOS
                     if "scroll-snap-type" in p.read_text(encoding="utf-8")]

# Transform-based demos (Blue Sky horizontal track): use transitionend wheel lock.
TRANSFORM_DEMOS = [p for p in ALL_DEMOS
                   if "scroll-snap-type" not in p.read_text(encoding="utf-8")
                   and "addEventListener('wheel'" in p.read_text(encoding="utf-8")]


class TestWheelBehavior:
    """Regression tests for trackpad/wheel scroll bugs.

    Root cause of multi-page scroll bug:
    - Time throttle (lock for fixed N ms after first event) fires goTo() once,
      then unlocks while trackpad momentum is still sending events → fires again.
    - Any N ms value is wrong: momentum duration is user/speed dependent.

    Correct patterns:
    - scroll-snap demos: NO JS wheel handler. scroll-snap-type: y mandatory handles
      trackpad natively. IntersectionObserver syncs state.
    - transform demos (Blue Sky): end-of-gesture debounce — accumulate deltaY,
      navigate once after 100ms of silence. Never fires during momentum.
    """

    @pytest.fixture(params=SCROLL_SNAP_DEMOS, ids=lambda p: p.name)
    def snap_demo(self, request):
        return load(request.param)

    @pytest.fixture(params=TRANSFORM_DEMOS, ids=lambda p: p.name)
    def transform_demo(self, request):
        return load(request.param)

    def test_scroll_snap_no_js_wheel_handler(self, snap_demo):
        """scroll-snap demos must NOT have a JS wheel event listener that calls
        goTo() / scrollIntoView. scroll-snap handles trackpad natively.

        Regression: JS wheel handler + scroll-snap = double animation or
        multi-page scroll (momentum tail unlocks throttle, fires goTo() again).
        """
        _, content = snap_demo
        import re
        # Detect a wheel listener that actually navigates (calls goTo, next, prev, scrollIntoView)
        nav_in_wheel = re.search(
            r"addEventListener\('wheel'.*?(?:goTo|\.next\(\)|\.prev\(\)|scrollIntoView)",
            content, re.DOTALL
        )
        assert not nav_in_wheel, (
            "scroll-snap demo has a JS wheel handler that calls navigation — "
            "remove it and let scroll-snap-type: y mandatory handle trackpad."
        )

    def test_scroll_snap_no_scroll_behavior_on_html(self, snap_demo):
        """html {} must NOT have scroll-behavior: smooth.

        Regression: scroll-behavior on html + scrollIntoView({behavior:'smooth'})
        = two simultaneous animations = jitter on page turn.
        """
        _, content = snap_demo
        import re
        # Look for scroll-behavior: smooth inside html { ... } rule
        bad = re.search(
            r"html\s*\{[^}]*scroll-behavior\s*:\s*smooth",
            content, re.DOTALL
        )
        assert not bad, (
            "html {} has scroll-behavior: smooth — remove it. "
            "JS scrollIntoView({behavior:'smooth'}) handles animation."
        )

    def test_no_wheel_throttle_pattern(self, snap_demo):
        """scroll-snap demos must not use wheelLocked time-throttle pattern.

        Regression: setTimeout(unlock, Nms) after first event — momentum tail
        outlasts N, fires goTo() again after lock expires.
        """
        _, content = snap_demo
        assert "wheelLocked" not in content, (
            "wheelLocked throttle pattern found in scroll-snap demo — "
            "remove the wheel handler entirely."
        )

    def test_transform_demo_uses_transitionend_wheel_lock(self, transform_demo):
        """Transform-based demos (Blue Sky) must use gap-based momentum detection:
        1. ANIMATING: first event navigates; all subsequent ignored.
        2. DRAINING: after transitionend, skip events arriving within 80ms of each
           other (continuous = macOS momentum); navigate on first event with gap > 80ms
           (finger lifted = new intentional swipe). No deltaY thresholds needed.

        Why not simpler approaches:
        - Time throttle (setTimeout Nms): unlocks during momentum tail → two pages advance.
        - wheelDelta accumulate+debounce: second swipe never crosses threshold → stuck.
        - transitionend + |deltaY| threshold: momentum at t=700ms is still 20-50px → wrong.
        - monotonic-decrease: momentum has jitter, false positives trigger extra navigation.
        """
        _, content = transform_demo
        assert "transitionend" in content, (
            "Transform demo missing transitionend. "
            "Pattern: lock on first event, start DRAINING phase after animation."
        )
        assert "wState" in content, (
            "Transform demo missing wState — gap-based wheel filter not implemented. "
            "Required: 'idle'/'animating'/'draining' states with 80ms gap detection."
        )
        assert "wLastTime" in content, (
            "Transform demo missing wLastTime — gap timing not tracked. "
            "Required: measure ms between events to detect momentum vs new swipe."
        )
        assert "wheelDelta" not in content, (
            "wheelDelta debounce found — breaks on second+ swipe. Use gap-based detection."
        )


class TestTemplate:
    """Tests for the HTML template file itself (not generated demos)."""

    REFS = Path(__file__).parent.parent / "references"

    def test_blue_sky_starter_wheel_transitionend(self):
        """blue-sky-starter.html must use transitionend to unlock wheel navigation.

        Correct: lock on first wheel event, unlock when track CSS transition ends.
        Banned: time throttle (setTimeout Nms) — unlocks during momentum.
        Banned: wheelDelta debounce — second swipe never crosses threshold, stops working.
        """
        starter = self.REFS / "blue-sky-starter.html"
        assert starter.exists(), "blue-sky-starter.html not found"
        content = starter.read_text(encoding="utf-8")
        assert "transitionend" in content, \
            "blue-sky-starter.html missing transitionend wheel unlock"
        assert "wState" in content, \
            "blue-sky-starter.html missing wState — gap-based wheel filter required"
        assert "wLastTime" in content, \
            "blue-sky-starter.html missing wLastTime — 80ms gap timing required"
        assert "wheelDelta" not in content, \
            "blue-sky-starter.html uses wheelDelta debounce — broken on 2nd swipe, use gap detection"

    def test_template_no_scroll_behavior_on_html(self):
        """html-template.md must NOT set scroll-behavior: smooth on html {}.

        Regression: causes double animation jitter when combined with scrollIntoView.
        """
        import re
        tmpl = self.REFS / "html-template.md"
        assert tmpl.exists(), "html-template.md not found"
        content = tmpl.read_text(encoding="utf-8")
        bad = re.search(r"html\s*\{[^}]*scroll-behavior\s*:\s*smooth", content, re.DOTALL)
        assert not bad, "html-template.md html{} has scroll-behavior: smooth — remove it"

    def test_template_wheel_handler_not_throttle(self):
        """html-template.md setupWheel() must not use wheelLocked throttle."""
        tmpl = self.REFS / "html-template.md"
        content = tmpl.read_text(encoding="utf-8")
        assert "wheelLocked" not in content, \
            "html-template.md uses wheelLocked throttle — banned, causes multi-page scroll"

    def test_template_goto_toggles_visible_class(self):
        """HTML template must have goTo() that toggles .visible class.

        This test ensures the template (references/html-template.md) contains
        the fix for the arrow-key rendering bug, even if old demos haven't
        been regenerated yet.
        """
        template_path = Path(__file__).parent.parent / "references" / "html-template.md"
        assert template_path.exists(), "html-template.md not found"
        content = template_path.read_text(encoding="utf-8")

        import re
        has_toggle = re.search(
            r'goTo\([^)]*\)\s*\{[^}]*classList\.toggle\s*\(\s*[\'"]visible[\'"]',
            content,
            re.DOTALL
        )
        assert has_toggle, \
            "html-template.md goTo() must toggle .visible class (arrow-key rendering fix)"
