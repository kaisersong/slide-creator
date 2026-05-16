# tests/test_renderer_layout_coverage.py
"""Layout diversity tests for all production presets.

Verifies that:
1. All canonical roles have a mapping in each preset's ROLE_LAYOUTS
2. build_slide_spec resolves to diverse layouts (not dominated by one)
3. Chinese Chan ornaments vary (no slide has both ghost+rule)
4. Signature components appear at minimum thresholds
"""
from __future__ import annotations

import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from low_context import (
    build_render_packet,
    build_slide_spec,
    BLUE_SKY_ROLE_LAYOUTS,
    CHINESE_CHAN_ROLE_LAYOUTS,
    DATA_STORY_ROLE_LAYOUTS,
    ENTERPRISE_ROLE_LAYOUTS,
    SWISS_ROLE_LAYOUTS,
)
from low_context import render_from_brief
from validate_html import validate


# -- helpers -------------------------------------------------------------

ALL_ROLE_LAYOUTS = {
    "Blue Sky": BLUE_SKY_ROLE_LAYOUTS,
    "Swiss Modern": SWISS_ROLE_LAYOUTS,
    "Enterprise Dark": ENTERPRISE_ROLE_LAYOUTS,
    "Data Story": DATA_STORY_ROLE_LAYOUTS,
    "Chinese Chan": CHINESE_CHAN_ROLE_LAYOUTS,
}

CANONICAL_ROLES = [
    "cover", "problem", "discovery", "solution", "features",
    "comparison", "dual", "process", "checkpoint", "recommendation",
    "evidence", "closing",
]

TEST_BRIEF_PRESETS = {
    "Blue Sky": str(ROOT / "demos" / "mode-paths" / "auto-BRIEF.json"),
    "Swiss Modern": "/tmp/openai-2025-brief-swiss.json",
    "Enterprise Dark": "/tmp/openai-2025-brief-enterprise.json",
    "Data Story": "/tmp/openai-2025-brief-datastory.json",
    "Chinese Chan": "/tmp/openai-2025-brief-chan.json",
}


def _load_brief(preset: str) -> dict[str, Any]:
    path = TEST_BRIEF_PRESETS[preset]
    if not Path(path).exists():
        pytest.skip(f"Brief not found: {path}")
    return json.loads(Path(path).read_text(encoding="utf-8"))


# -- tests ---------------------------------------------------------------

@pytest.mark.parametrize("preset_name,mapping", list(ALL_ROLE_LAYOUTS.items()))
def test_all_canonical_roles_mapped(preset_name, mapping):
    """Each preset maps all canonical roles to a layout."""
    unmapped = [r for r in CANONICAL_ROLES if r not in mapping]
    assert not unmapped, f"{preset_name}: unmapped roles {unmapped}"


@pytest.mark.parametrize("preset_name", list(ALL_ROLE_LAYOUTS.keys()))
def test_resolved_layouts_diverse(preset_name):
    """build_slide_spec resolves to diverse layouts, not dominated by one."""
    brief = _load_brief(preset_name)
    packet = build_render_packet(brief)
    specs = build_slide_spec(brief, packet=packet)

    layouts = [s["layout_id"] for s in specs]
    counts = Counter(layouts)
    max_count = max(counts.values())

    # Chinese Chan has a small palette (4 layouts); allow up to 60%
    threshold = 0.6 if preset_name == "Chinese Chan" else 0.5
    assert max_count <= len(specs) * threshold, (
        f"{preset_name}: layout '{max(counts, key=counts.get)}' "
        f"used {max_count}/{len(specs)} times"
    )

    # At least 3 distinct layouts for a 12-slide deck
    assert len(counts) >= 3, (
        f"{preset_name}: only {len(counts)} distinct layouts: {dict(counts)}"
    )


def test_chinese_chan_ornament_variety():
    """Chinese Chan uses multiple ornament types, no consecutive-3 repeats."""
    brief = _load_brief("Chinese Chan")
    html = render_from_brief(brief)[0]
    soup = _parse(html)
    slides = soup.find_all("section", class_="slide")

    ornaments = []
    for slide in slides:
        if slide.find(class_="zen-ghost-kanji"):
            ornaments.append("ghost")
        elif slide.find(class_="zen-vline"):
            ornaments.append("vline")
        elif slide.find(class_="zen-seal"):
            ornaments.append("seal")
        elif slide.find(class_="zen-rule"):
            ornaments.append("rule")
        else:
            ornaments.append("none")

    distinct = set(ornaments) - {"none"}
    assert len(distinct) >= 3, (
        f"Only {distinct} ornament types used, expected >= 3"
    )

    # No 3 consecutive slides with the same ornament
    for i in range(len(ornaments) - 2):
        if ornaments[i] == ornaments[i + 1] == ornaments[i + 2]:
            pytest.fail(
                f"3 consecutive '{ornaments[i]}' ornaments starting at page {i + 1}"
            )


@pytest.mark.parametrize("preset_name,component,min_slides", [
    ("Swiss Modern", "hero-rule", 1),
    ("Swiss Modern", "left-panel", 1),
    ("Swiss Modern", "stat-value", 1),
    ("Enterprise Dark", "ent-kpi-card", 3),
    ("Data Story", "ds-kpi", 3),
    ("Data Story", "ds-chart-svg", 1),
    ("Chinese Chan", "zen-ghost-kanji", 2),
    ("Chinese Chan", "zen-rule", 1),
])
def test_signature_component_minimum(preset_name, component, min_slides):
    """Each preset has at least min_slides showing its signature component."""
    brief = _load_brief(preset_name)
    html = render_from_brief(brief)[0]
    soup = _parse(html)
    slides = soup.find_all("section", class_="slide")

    count = sum(1 for s in slides if s.find(class_=component))
    assert count >= min_slides, (
        f"{preset_name}: {component} in {count}/{len(slides)} slides, "
        f"expected >= {min_slides}"
    )


def test_new_mappings_not_blocked_by_usage_rules():
    """New role mappings should not have unhandled requirements."""
    rules_path = ROOT / "references" / "preset-usage-rules.json"
    if not rules_path.exists():
        pytest.skip("preset-usage-rules.json not found")

    rules = json.loads(rules_path.read_text(encoding="utf-8"))
    new_mappings = {
        "Blue Sky": {"workflow", "style-discovery", "output-contract", "best-fit"},
        "Swiss Modern": {"discovery", "comparison", "dual", "process", "checkpoint", "recommendation"},
        "Enterprise Dark": {"dual", "process", "recommendation"},
        "Data Story": {"dual", "process", "recommendation"},
        "Chinese Chan": {"features", "dual", "process", "recommendation"},
    }

    for preset_name, new_roles in new_mappings.items():
        preset_rules = rules["presets"].get(preset_name, {})
        layout_reqs = preset_rules.get("layout_requirements", {})
        mapping = ALL_ROLE_LAYOUTS[preset_name]

        for role in new_roles:
            layout = mapping.get(role)
            if layout and layout in layout_reqs:
                req = layout_reqs[layout]
                assert "fallback" in req, (
                    f"{preset_name}: {role}->{layout} has requirements "
                    f"but no fallback defined"
                )


def test_existing_demos_still_validate():
    """Current Blue Sky renderer output passes strict validation."""
    brief = json.loads((ROOT / "demos" / "mode-paths" / "auto-BRIEF.json").read_text(encoding="utf-8"))
    html = render_from_brief(brief)[0]

    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as handle:
        handle.write(html)
        path = Path(handle.name)
    try:
        assert validate(path, strict=True)
    finally:
        path.unlink(missing_ok=True)


# -- internal helpers -----------------------------------------------------

def _parse(html: str):
    from bs4 import BeautifulSoup
    return BeautifulSoup(html, "html.parser")
