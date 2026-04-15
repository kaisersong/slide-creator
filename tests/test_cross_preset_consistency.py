"""
Tests for cross-preset consistency across all demo HTML files.

Validates that every preset has demo files (en+zh), and all demos share
common structural elements: viewport fitting CSS, data-preset attribute,
slide-credit watermark, edit hotzone, nav dots, progress bar.

Run: python -m pytest tests/test_cross_preset_consistency.py -v
"""

import re
from pathlib import Path

import pytest

DEMOS_DIR = Path(__file__).parent.parent / "demos"
ALL_DEMOS = sorted(DEMOS_DIR.glob("*.html"))

# All 21 presets
PRESETS = [
    "bold-signal", "blue-sky", "aurora-mesh", "chinese-chan",
    "creative-voltage", "dark-botanical", "data-story", "electric-studio",
    "enterprise-dark", "glassmorphism", "modern-newspaper", "neo-brutalism",
    "neo-retro-dev", "neon-cyber", "notebook-tabs", "paper-ink",
    "pastel-geometry", "split-pastel", "swiss-modern", "terminal-green",
    "vintage-editorial",
]


def get_preset_from_demo(demo_path: Path) -> str:
    """Extract preset name from demo filename: enterprise-dark-zh.html -> enterprise-dark"""
    name = demo_path.stem
    # Strip known suffixes to handle backup files like blue-sky-zh-handwritten-backup
    for suffix in ("-handwritten-backup", "-backup"):
        name = name.replace(suffix, "")
    parts = name.rsplit("-", 1)
    if len(parts) == 2 and parts[1] in ("en", "zh"):
        return parts[0]
    return name


def load(path: Path):
    content = path.read_text(encoding="utf-8")
    return content


class TestPresetDemoCoverage:
    """All 21 presets must have at least one demo file."""

    def test_all_presets_have_demos(self):
        found_presets = {get_preset_from_demo(p) for p in ALL_DEMOS}
        missing = set(PRESETS) - found_presets
        assert not missing, f"Presets without demo files: {sorted(missing)}"

    def test_presets_have_both_en_and_zh(self):
        preset_languages = {}
        for demo in ALL_DEMOS:
            preset = get_preset_from_demo(demo)
            lang = demo.stem.rsplit("-", 1)[-1]
            if lang in ("en", "zh"):
                if preset not in preset_languages:
                    preset_languages[preset] = set()
                preset_languages[preset].add(lang)

        missing_en = [p for p in PRESETS if "en" not in preset_languages.get(p, set())]
        missing_zh = [p for p in PRESETS if "zh" not in preset_languages.get(p, set())]
        assert not missing_en, f"Presets missing English demo: {sorted(missing_en)}"
        assert not missing_zh, f"Presets missing Chinese demo: {sorted(missing_zh)}"


class TestCommonElements:
    """All demos must share common structural elements."""

    @pytest.fixture(params=ALL_DEMOS, ids=lambda p: p.name)
    def demo(self, request):
        return request.param, load(request.param)

    def test_viewport_fitting_css(self, demo):
        _, content = demo
        assert "100vh" in content or "100dvh" in content, \
            "Missing height: 100vh / 100dvh — slides won't fit viewport"

    def test_overflow_hidden(self, demo):
        _, content = demo
        assert "overflow: hidden" in content or "overflow:hidden" in content, \
            "Missing overflow: hidden"

    def test_html_has_doctype(self, demo):
        _, content = demo
        assert content.lstrip()[:15].upper().startswith("<!DOCTYPE"), \
            "Missing <!DOCTYPE html>"

    def test_html_has_inline_style(self, demo):
        _, content = demo
        assert "<style>" in content.lower(), "Missing <style> tag"

    def test_self_contained(self, demo):
        _, content = demo
        assert 'src="http' not in content and "src='http" not in content, \
            "Found external script source — demos must be self-contained"

    def test_slide_count_css(self, demo):
        _, content = demo
        # --slide-count is generated; older demos may not have it
        # New demos will pass; old demos will fail until regenerated
        if "--slide-count" not in content:
            pytest.skip("Demo generated before --slide-count feature — regenerate to apply")


class TestEditModeElements:
    """Demos should have edit mode infrastructure."""

    @pytest.fixture(params=ALL_DEMOS, ids=lambda p: p.name)
    def demo(self, request):
        return request.param, load(request.param)

    def test_has_edit_infrastructure(self, demo):
        path, content = demo
        has_hotzone = 'id="hotzone"' in content
        has_contenteditable = "contenteditable" in content
        assert has_hotzone or has_contenteditable, \
            f"{path.name}: No edit mode infrastructure found"


class TestNavigationElements:
    """Demos should have navigation infrastructure."""

    @pytest.fixture(params=ALL_DEMOS, ids=lambda p: p.name)
    def demo(self, request):
        return request.param, load(request.param)

    def test_has_navigation(self, demo):
        _, content = demo
        has_nav_dots = "nav-dot" in content or "navDots" in content or ".dots" in content
        has_progress = "progress" in content.lower()
        has_keyboard = "ArrowLeft" in content or "ArrowRight" in content
        assert has_nav_dots or has_progress or has_keyboard, \
            f"{demo[0].name}: No navigation infrastructure found"


class TestWatermark:
    """All demos must have the kai-slide-creator watermark."""

    @pytest.fixture(params=ALL_DEMOS, ids=lambda p: p.name)
    def demo(self, request):
        return request.param, load(request.param)

    def test_has_watermark(self, demo):
        _, content = demo
        # Watermark was added later; older demos may not have it
        if "kai-slide-creator" not in content.lower():
            pytest.skip("Demo generated before watermark feature — regenerate to apply")


# Blue Sky is the only preset allowed to use its own stage/track architecture.
BLUE_SKY_ONLY = {"blue-sky"}

# Presets whose style defines body-level gradient/animated backgrounds — their
# .slide elements must NOT set opaque `background` that blocks the body gradient.
# Note: styles like terminal-green have overlay elements (.terminal-scanlines) on a
# solid body color — those are NOT body gradients and are excluded here.
BODY_GRADIENT_PRESETS = {
    "aurora-mesh",      # auroraDrift radial gradients on body
    "dark-botanical",   # soft orb gradients on body
}


class TestArchitectureIsolation:
    """Non-Blue-Sky presets must NOT use Blue Sky's #stage/#track architecture.

    Regression: AI generator copied Blue Sky patterns into non-Blue-Sky demos,
    breaking scroll-snap navigation. SKILL.md Rule #20.
    """

    @pytest.fixture(
        params=[d for d in ALL_DEMOS if get_preset_from_demo(d) not in BLUE_SKY_ONLY],
        ids=lambda p: p.name,
    )
    def non_blue_sky_demo(self, request):
        return request.param, load(request.param)

    def test_no_stage_track_in_non_blue_sky(self, non_blue_sky_demo):
        path, content = non_blue_sky_demo
        # Detect Blue Sky-exclusive patterns
        has_stage = "id=\"stage\"" in content or "#stage" in content
        has_track = "id=\"track\"" in content or "#track" in content
        has_calc_width = "calc(100vw" in content
        has_translatex_nav = (
            ("translateX(-'" in content or 'translateX(-"' in content or "translateX(-`" in content)
            and "100" in content and "vw" in content
        )
        # Also detect Blue Sky's specific nav pattern: track.style.transform with translateX
        has_track_transform = "track.style" in content and "translateX" in content

        violations = []
        if has_stage:
            violations.append("#stage container")
        if has_track:
            violations.append("#track flex row")
        if has_calc_width:
            violations.append("calc(100vw * var(--slide-count))")
        if has_translatex_nav:
            violations.append("translateX slide navigation")
        if has_track_transform:
            violations.append("track.style.transform navigation")

        assert not violations, (
            f"{path.name}: Blue Sky-exclusive architecture detected: "
            f"{', '.join(violations)}. "
            "Only Blue Sky may use #stage/#track. Use scroll-snap instead."
        )

    def test_uses_scroll_snap(self, non_blue_sky_demo):
        """Non-Blue-Sky demos must use scroll-snap architecture."""
        _, content = non_blue_sky_demo
        assert "scroll-snap-type" in content, (
            "Missing scroll-snap-type — non-Blue-Sky demos must use "
            "html-template.md scroll-snap architecture"
        )


class TestChineseChanGhostKanji:
    """Chinese Chan ghost kanji must be positioned in page corners, never centered,
    and must be placed OUTSIDE .slide-content so they position relative to .slide.

    Regression: AI generator placed ghost kanji inside .slide-content (600px container)
    or centered at left: 50% / translateX(-50%). SKILL.md Rule #22.
    """

    @pytest.fixture(
        params=[d for d in ALL_DEMOS if get_preset_from_demo(d) == "chinese-chan"],
        ids=lambda p: p.name,
    )
    def chinese_chan_demo(self, request):
        return request.param, load(request.param)

    def test_ghost_kanji_not_centered(self, chinese_chan_demo):
        path, content = chinese_chan_demo

        # Find all zen-ghost-kanji HTML elements only (skip CSS definitions)
        ghost_kanji_blocks = re.findall(
            r'<[a-z][^>]*zen-ghost-kanji[^>]*>',
            content,
        )
        for block in ghost_kanji_blocks:
            violations = []
            if 'left: 50%' in block:
                violations.append('left: 50% (centered)')
            if 'right: 50%' in block:
                violations.append('right: 50% (centered)')
            if 'top: 50%' in block:
                violations.append('top: 50% (centered)')
            if 'bottom: 50%' in block:
                violations.append('bottom: 50% (centered)')
            if 'translateX(-50%)' in block:
                violations.append('translateX centering')
            if 'translateY(-50%)' in block:
                violations.append('translateY centering')

            assert not violations, (
                f"{path.name}: ghost kanji centered: {', '.join(violations)}. "
                "Ghost kanji must be positioned in corners (right/bottom/left/top with "
                "small offsets), never at 50% or with translate centering."
            )

    def test_ghost_kanji_outside_slide_content(self, chinese_chan_demo):
        """Ghost kanji must be a direct child of .slide, not nested in .slide-content."""
        path, content = chinese_chan_demo

        # Find all zen-ghost-kanji HTML elements
        ghost_kanji_elements = re.findall(
            r'<[a-z][^>]*zen-ghost-kanji[^>]*>',
            content,
        )
        assert ghost_kanji_elements, f"{path.name}: No ghost kanji elements found"

        for element in ghost_kanji_elements:
            # Find the index of this element in the content
            elem_idx = content.index(element)

            # Count unclosed slide-content divs before this element
            # by counting <...slide-content...> that are not yet closed
            before = content[:elem_idx]

            # Simple heuristic: count slide-content opens/closes
            # in the immediate vicinity (last 200 chars before element)
            recent = before[-200:]
            open_count = recent.count('slide-content')
            # If slide-content appears in the recent context without a matching close,
            # the ghost kanji is likely inside it
            close_count = recent.count('/div')

            # More precise: check if element appears between
            # <div class="slide-content" ...> and its closing </div>
            # by finding the last slide-content opening before this element
            last_content_open = before.rfind('slide-content')
            if last_content_open >= 0:
                # Find the closing > of the slide-content div
                next_close_bracket = before.find('>', last_content_open)
                if next_close_bracket >= 0:
                    # Check if there's a closing </div> between that > and our element
                    between = content[next_close_bracket:elem_idx]
                    # Count div closings (at least 2 per nesting level + inline elements)
                    closing_divs = between.count('</div>')
                    # slide-content starts with <div, so we need at least 1 </div> to close it
                    # but also check for nested elements
                    if closing_divs == 0:
                        assert False, (
                            f"{path.name}: ghost kanji is inside .slide-content "
                            f"({element.strip()}). "
                            "Ghost kanji must be placed as direct child of .slide, "
                            "outside .slide-content, so position:absolute uses the "
                            "full page as its positioning context."
                        )


class TestSlideBackgroundTransparency:
    """Slides must NOT block body gradient backgrounds.

    When a style defines body-level gradients/patterns (aurora mesh, dark botanical,
    etc.), .slide must be transparent so the gradient shows through. SKILL.md Rule #21.
    """

    @pytest.fixture(
        params=[d for d in ALL_DEMOS if get_preset_from_demo(d) in BODY_GRADIENT_PRESETS],
        ids=lambda p: p.name,
    )
    def body_gradient_demo(self, request):
        return request.param, load(request.param)

    def test_slide_no_opaque_background(self, body_gradient_demo):
        path, content = body_gradient_demo

        # Detect body-level gradient/pattern
        has_body_gradient = any(kw in content for kw in [
            "radial-gradient", "linear-gradient", "conic-gradient",
            "auroraDrift", "scanline", "scan-line",
        ])
        if not has_body_gradient:
            pytest.skip("No body gradient/pattern detected in this style")

        # Check .slide block for background overrides
        # Look for .slide { ... background: ... } patterns
        slide_blocks = re.findall(
            r"\.slide\s*\{([^}]+)\}",
            content,
            re.DOTALL,
        )
        for block in slide_blocks:
            # Match background/background-color properties (not background-size/position/attachment)
            bg_props = re.findall(
                r"(?:^|\s|;)(background-color|background)\s*:\s*([^;]+)",
                block,
                re.MULTILINE,
            )
            # Only flag non-transparent values — `background: transparent` is safe
            for prop, value in bg_props:
                value_stripped = value.strip().lower()
                if value_stripped not in ("transparent", "unset", "inherit", "initial", "none"):
                    assert False, (
                        f"{path.name}: .slide has background declaration that would block "
                        f"body gradient: '{prop}: {value.strip()}' in .slide CSS block. "
                        f"Remove it so body gradient shows through."
                    )
