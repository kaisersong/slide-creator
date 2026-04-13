"""
Tests for preset background pattern rendering in demo HTML files.

Validates that each demo has its signature background elements (grid, gradient orbs,
halftone, scan lines, etc.) matching the preset description.

Background patterns are the visual signature that distinguishes one preset from another.
If a demo lacks its background pattern, it will look generic and style-less.

Run: python -m pytest tests/test_preset_background_patterns.py -v
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
    name = demo_path.stem  # e.g., "enterprise-dark-zh"
    parts = name.rsplit("-", 1)
    if len(parts) == 2 and parts[1] in ("en", "zh"):
        return parts[0]
    return name


def load(path: Path):
    content = path.read_text(encoding="utf-8")
    return content


class TestDemoCoverage:
    """All 21 presets must have demo files."""

    def test_all_presets_have_demos(self):
        found_presets = {get_preset_from_demo(p) for p in ALL_DEMOS}
        missing = set(PRESETS) - found_presets
        assert not missing, f"Presets without demo files: {sorted(missing)}"

    def test_presets_have_en_and_zh(self):
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


class TestBackgroundPatterns:
    """Check demos for their signature background elements."""

    @pytest.fixture(params=ALL_DEMOS, ids=lambda p: p.name)
    def demo(self, request):
        path = request.param
        content = load(path)
        preset = get_preset_from_demo(path)
        return path, content, preset

    def test_grid_based_presets_have_grid_pattern(self, demo):
        """Grid-based presets must have grid or scan-line patterns."""
        grid_presets = {
            "enterprise-dark", "neon-cyber", "swiss-modern",
            "split-pastel", "neo-retro-dev",
        }
        scan_presets = {"terminal-green"}  # uses repeating-linear-gradient for scan lines
        path, content, preset = demo
        if preset in grid_presets:
            has_grid = re.search(
                r"linear-gradient.*rgba.*1px.*transparent",
                content, re.DOTALL
            ) or re.search(r"background-size.*\d+px\s+\d+px", content)
            assert has_grid, \
                f"{path.name}: grid-based preset '{preset}' missing grid pattern"
        if preset in scan_presets:
            has_scan = re.search(r"repeating-linear-gradient", content)
            assert has_scan, \
                f"{path.name}: scan-line preset '{preset}' missing repeating-linear-gradient"

    def test_orb_based_presets_have_gradient_blur(self, demo):
        """Orb/gradient-based presets must have radial-gradient or blur effects."""
        orb_presets = {"aurora-mesh", "dark-botanical", "glassmorphism"}
        path, content, preset = demo
        if preset in orb_presets:
            has_orb = re.search(r"radial-gradient|filter.*blur|backdrop-filter", content, re.DOTALL | re.IGNORECASE)
            assert has_orb, \
                f"{path.name}: orb-based preset '{preset}' missing gradient/blur effect"

    def test_dark_presets_have_dark_background(self, demo):
        """Dark presets should have a dark background color."""
        dark_presets = {
            "enterprise-dark", "neon-cyber", "terminal-green",
            "creative-voltage", "dark-botanical", "glassmorphism",
            "aurora-mesh", "bold-signal", "data-story",
        }
        path, content, preset = demo
        if preset in dark_presets:
            has_dark = re.search(
                r"background[^:]*:\s*#[0-1][0-9a-fA-F]{2,5}",
                content
            ) or re.search(r"background[^:]*:\s*linear-gradient.*#[0-1][0-9a-fA-F]", content)
            # Also accept CSS variable references to dark colors
            has_dark_var = re.search(r"--bg[^:]*:\s*#[01]", content)
            assert has_dark or has_dark_var, \
                f"{path.name}: dark preset '{preset}' missing dark background value"

    def test_no_pure_black_background(self, demo):
        """Dark demos should not use pure black (#000 / #000000) background."""
        dark_presets = {"enterprise-dark", "neon-cyber", "terminal-green",
                        "creative-voltage", "dark-botanical", "glassmorphism"}
        path, content, preset = demo
        if preset in dark_presets:
            for line in content.split("\n"):
                stripped = line.strip()
                if stripped.startswith("/*") or stripped.startswith("*"):
                    continue
                if re.search(r"background(?:-color)?\s*:\s*#[0]{3}(?:\s|;|})", stripped) or \
                   re.search(r"background(?:-color)?\s*:\s*#[0]{6}(?:\s|;|})", stripped):
                    pytest.fail(
                        f"Pure black background in {path.name} — use #111 or #18181B"
                    )
