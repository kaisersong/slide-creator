"""
Tests for style reference file completeness.

Validates that all 21 presets have corresponding reference files with required sections.
This ensures the AI generator always has the information it needs to produce
style-faithful output.

Run: python -m pytest tests/test_style_reference_completeness.py -v
"""

import re
from pathlib import Path

import pytest

REFS_DIR = Path(__file__).parent.parent / "references"

# All 21 presets as listed in SKILL.md style reference table
PRESETS = [
    "bold-signal",
    "blue-sky",          # blue-sky-starter.html
    "aurora-mesh",
    "chinese-chan",
    "creative-voltage",
    "dark-botanical",
    "data-story",
    "electric-studio",
    "enterprise-dark",
    "glassmorphism",
    "modern-newspaper",
    "neo-brutalism",
    "neo-retro-dev",
    "neon-cyber",
    "notebook-tabs",
    "paper-ink",
    "pastel-geometry",
    "split-pastel",
    "swiss-modern",
    "terminal-green",
    "vintage-editorial",
]

# Presets that use .html instead of .md
HTML_PRESETS = {"blue-sky"}

# Required markdown sections every reference file must contain
# (HTML templates are checked differently)
REQUIRED_SECTIONS = [
    "## Colors",
    "## Background",
    "## Typography",
    "## Signature Elements",
    "## Style Preview Checklist",
]

# Presets with named layout variations (from STYLE-DESC.md) — must include all
PRESETS_WITH_NAMED_LAYOUTS = {
    "bold-signal",
    "enterprise-dark",
    "neon-cyber",
    "terminal-green",
    "swiss-modern",
    "paper-ink",
    "modern-newspaper",
    "neo-retro-dev",
}

# Minimum expected named layout count per preset (extracted from STYLE-DESC.md)
MIN_LAYOUT_COUNT = {
    "bold-signal": 7,
    "enterprise-dark": 7,
    "neon-cyber": 7,
    "terminal-green": 7,
    "swiss-modern": 7,
    "paper-ink": 7,
    "modern-newspaper": 8,
    "neo-retro-dev": 6,
}

# Dark presets that must NOT use pure black backgrounds
DARK_PRESETS = {
    "enterprise-dark",
    "neon-cyber",
    "terminal-green",
    "creative-voltage",
    "dark-botanical",
    "glassmorphism",
}


def get_ref_path(preset: str) -> Path:
    if preset in HTML_PRESETS:
        return REFS_DIR / f"{preset}-starter.html"
    return REFS_DIR / f"{preset}.md"


def load_ref(preset: str):
    path = get_ref_path(preset)
    content = path.read_text(encoding="utf-8")
    return path, content


class TestReferenceFileExistence:
    """All 21 presets must have a corresponding reference file."""

    @pytest.mark.parametrize("preset", PRESETS)
    def test_reference_file_exists(self, preset):
        path = get_ref_path(preset)
        assert path.exists(), f"Reference file missing: {path}"
        # Must be non-empty
        size = path.stat().st_size
        assert size > 500, f"Reference file suspiciously small: {path} ({size} bytes)"


class TestRequiredSections:
    """Every reference file must contain required markdown sections."""

    @pytest.mark.parametrize("preset", [p for p in PRESETS if p not in HTML_PRESETS])
    def test_has_colors_section(self, preset):
        _, content = load_ref(preset)
        assert "## Colors" in content, f"{preset}: missing '## Colors' section"

    @pytest.mark.parametrize("preset", [p for p in PRESETS if p not in HTML_PRESETS])
    def test_has_background_section(self, preset):
        _, content = load_ref(preset)
        assert "## Background" in content, f"{preset}: missing '## Background' section"

    @pytest.mark.parametrize("preset", [p for p in PRESETS if p not in HTML_PRESETS])
    def test_has_typography_section(self, preset):
        _, content = load_ref(preset)
        assert "## Typography" in content, f"{preset}: missing '## Typography' section"

    @pytest.mark.parametrize("preset", [p for p in PRESETS if p not in HTML_PRESETS])
    def test_has_signature_elements(self, preset):
        _, content = load_ref(preset)
        assert "## Signature Elements" in content, f"{preset}: missing '## Signature Elements' section"

    @pytest.mark.parametrize("preset", [p for p in PRESETS if p not in HTML_PRESETS])
    def test_has_style_preview_checklist(self, preset):
        _, content = load_ref(preset)
        assert "## Style Preview Checklist" in content, \
            f"{preset}: missing '## Style Preview Checklist' section"

    @pytest.mark.parametrize("preset", [p for p in PRESETS if p not in HTML_PRESETS])
    def test_has_animation_section(self, preset):
        _, content = load_ref(preset)
        assert "## Animation" in content, f"{preset}: missing '## Animation' section"

    @pytest.mark.parametrize("preset", [p for p in PRESETS if p not in HTML_PRESETS])
    def test_has_best_for_section(self, preset):
        _, content = load_ref(preset)
        assert "## Best For" in content, f"{preset}: missing '## Best For' section"


class TestBackgroundCompleteness:
    """Background section must define body/body::before background patterns."""

    @pytest.mark.parametrize("preset", PRESETS)
    def test_body_has_background_definition(self, preset):
        """Every preset must have a body or body::before background definition."""
        _, content = load_ref(preset)
        # Accept: body { background: ... }, body { background-image: ... },
        # body::before { background: ... }, or similar
        has_body_bg = re.search(
            r"body\s*(::before)?\s*\{[^}]*background",
            content, re.DOTALL
        )
        assert has_body_bg, f"{preset}: no 'body' background definition in reference file"

    @pytest.mark.parametrize("preset", PRESETS)
    def test_css_variables_defined(self, preset):
        """Every preset must define :root CSS variables."""
        _, content = load_ref(preset)
        assert ":root" in content or "--bg" in content, \
            f"{preset}: missing :root CSS variable definitions"


class TestDarkPresetBackgrounds:
    """Dark presets must NOT use pure black (#000 or #000000) as background."""

    @pytest.mark.parametrize("preset", DARK_PRESETS)
    def test_no_pure_black_background(self, preset):
        _, content = load_ref(preset)
        # Match #000, #000000 as background value (but not in comments)
        lines = content.split("\n")
        for line in lines:
            # Skip comments
            stripped = line.strip()
            if stripped.startswith("/*") or stripped.startswith("*") or stripped.startswith("//"):
                continue
            if re.search(r"background[^:]*:\s*#[0]{3}\b", line) or \
               re.search(r"background[^:]*:\s*#[0]{6}\b", line):
                pytest.fail(
                    f"{preset}: pure black background (#000/#000000) found — "
                    f"use #111 or #18181B instead. Line: {line.strip()}"
                )


class TestNamedLayoutCompleteness:
    """Presets with named layout variations must include all of them."""

    @pytest.mark.parametrize("preset", PRESETS_WITH_NAMED_LAYOUTS)
    def test_has_named_layouts_section(self, preset):
        _, content = load_ref(preset)
        assert "## Named Layout" in content, \
            f"{preset}: missing '## Named Layout Variations' section"

    @pytest.mark.parametrize("preset", PRESETS_WITH_NAMED_LAYOUTS)
    def test_minimum_layout_count(self, preset):
        _, content = load_ref(preset)
        # Count ### N. layout headers (e.g., "### 1. Hero Card")
        layouts = re.findall(r"###\s+\d+\.\s+", content)
        expected = MIN_LAYOUT_COUNT[preset]
        assert len(layouts) >= expected, \
            f"{preset}: expected >= {expected} named layouts, found {len(layouts)}"


class TestComponentSection:
    """Reference files must define a Components section with CSS classes."""

    @pytest.mark.parametrize("preset", [p for p in PRESETS if p not in HTML_PRESETS])
    def test_has_components_section(self, preset):
        """Must have an explicit '## Components' section."""
        _, content = load_ref(preset)
        assert "## Components" in content, \
            f"{preset}: missing '## Components' section — reference file must define component CSS classes"
