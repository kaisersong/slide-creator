from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def read_ref(name: str) -> str:
    return (ROOT / "references" / f"{name}.md").read_text(encoding="utf-8")


def test_enterprise_dark_reference_defines_user_content_route_and_contract():
    content = read_ref("enterprise-dark")
    assert "## User-Content 12-Page Route" in content
    assert "## Canonical Export Contract" in content
    assert "data-export-role" in content
    assert "kpi_dashboard" in content
    assert "Canonical emitted classes are `.ent-*`" in content


def test_data_story_reference_defines_chart_first_contract():
    content = read_ref("data-story")
    assert "## User-Content 12-Page Route" in content
    assert "## Canonical Export Contract" in content
    assert "hero_number" in content and "chart_insight" in content
    assert "Chart.js" in content and "ECharts" in content
    assert "Canonical emitted classes are `.ds-*`" in content


def test_glassmorphism_reference_defines_orb_backed_contract():
    content = read_ref("glassmorphism")
    assert "## User-Content 12-Page Route" in content
    assert "## Canonical Export Contract" in content
    assert "Orb layers stay as direct children of `.slide`" in content
    assert "glass_hero" in content and "glass_trio" in content
    assert "backdrop-filter" in content


def test_chinese_chan_reference_defines_minimalist_contract():
    content = read_ref("chinese-chan")
    assert "## User-Content 12-Page Route" in content
    assert "## Canonical Export Contract" in content
    assert "zen_center" in content and "zen_vertical" in content and "zen_stat" in content
    assert "Canonical emitted classes are `.zen-*`" in content
    assert "ghost-kanji" in content
    assert ".zen-h2" in content
    assert "Noto Serif SC" in content
    assert ".zen-stat .num" in content
