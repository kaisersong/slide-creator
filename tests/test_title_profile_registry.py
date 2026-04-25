from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
VALIDATE_PY = ROOT / "tests" / "validate.py"
sys.path.insert(0, str(SCRIPTS))

from low_context import PRESET_REFERENCE_MAP, _render_title_markup, resolve_title_profile as low_context_resolve  # noqa: E402
from title_profiles import (  # noqa: E402
    collect_title_candidate_nodes,
    list_registry_presets,
    registry_version,
    resolve_title_profile,
)


def load_validate_module():
    spec = importlib.util.spec_from_file_location("validate_module", VALIDATE_PY)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_title_profile_registry_covers_all_supported_presets():
    registry_presets = set(list_registry_presets())
    assert registry_version() == 1
    assert set(PRESET_REFERENCE_MAP.keys()) == {preset.lower() for preset in registry_presets}


def test_renderer_and_validator_consume_same_profile_resolver():
    validate = load_validate_module()
    assert low_context_resolve is resolve_title_profile
    assert validate.resolve_title_profile is resolve_title_profile


def test_resolve_title_profile_marks_structural_presets_correctly():
    html = """
    <html>
      <body>
        <section class="slide zen_vertical" data-export-role="zen_vertical" id="s1">
          <div class="zen-vertical-title">竖排标题</div>
        </section>
        <section class="slide halftone" id="s2">
          <div class="cover-inner">
            <div class="main-title">slide-</div>
            <div class="title-accent">creator</div>
          </div>
        </section>
        <section class="slide" id="s3">
          <h1 class="cyber-title" data-text="signal lockup">signal lockup</h1>
        </section>
        <section class="slide" id="s4">
          <div class="feature-title">&gt; VIEWPORT_FIT</div>
        </section>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    chinese = soup.select_one(".zen-vertical-title")
    voltage = soup.select_one(".main-title")
    cyber = soup.select_one(".cyber-title")
    terminal = soup.select_one(".feature-title")

    assert resolve_title_profile("Chinese Chan", node=chinese)["profile"] == "vertical_title"
    assert resolve_title_profile("Creative Voltage", node=voltage)["profile"] == "split_lockup"
    assert resolve_title_profile("Neon Cyber", node=cyber)["profile"] == "glitch_lockup"
    assert resolve_title_profile("Terminal Green", node=terminal)["profile"] == "terminal_object"


def test_collect_title_candidate_nodes_includes_structural_targets():
    html = """
    <html>
      <body>
        <section class="slide halftone" id="slide-1">
          <div class="cover-inner">
            <div class="main-title">slide-</div>
            <div class="title-accent">creator</div>
          </div>
          <h2 class="voltage-title">Ordinary headline</h2>
        </section>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    slide = soup.select_one(".slide")

    nodes = collect_title_candidate_nodes(slide, "Creative Voltage")
    texts = [node.get_text(" ", strip=True) for node in nodes]

    assert "slide-" in texts
    assert "Ordinary headline" in texts


def test_renderer_skips_generic_line_wrappers_for_structural_profiles():
    markup, multiline = _render_title_markup(
        "竖排标题",
        preset="Chinese Chan",
        layout_id="zen_vertical",
        line_class="title-line",
    )

    assert multiline is False
    assert "title-line" not in markup
