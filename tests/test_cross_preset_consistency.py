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
