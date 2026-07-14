from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from low_context import render_from_brief  # noqa: E402
from preset_runtime_qa import analyze_preset_runtime_html  # noqa: E402


BRIEF = ROOT / "demos" / "mode-paths" / "auto-BRIEF.json"


def _native_blue_sky_html() -> str:
    brief = json.loads(BRIEF.read_text(encoding="utf-8"))
    return render_from_brief(brief)[0]


def test_native_blue_sky_runtime_proves_cover_content_and_closing_motion():
    report = analyze_preset_runtime_html(_native_blue_sky_html(), "Blue Sky")

    if report.get("unavailable"):
        pytest.fail(report.get("error", "runtime QA unavailable"))
    assert report["pass"], report
    buckets = {scenario["page_bucket"] for scenario in report["scenarios"]}
    assert {"cover", "content", "closing"} <= buckets
    assert all(scenario["visible"] for scenario in report["scenarios"])
    assert all(scenario["time_advanced"] for scenario in report["scenarios"])
    assert all(scenario["presentation_changed"] for scenario in report["scenarios"])


def test_runtime_qa_rejects_keyframes_without_an_attached_animation():
    html = _native_blue_sky_html().replace(
        "animation: cloud-scroll 30s linear infinite;",
        "animation: none;",
    ).replace(
        "animation: cloud-scroll 18s linear infinite;",
        "animation: none;",
    )

    report = analyze_preset_runtime_html(html, "Blue Sky")

    assert report["pass"] is False
    assert "runtime-motion-target-missing" in report["hard_failures"]


def test_runtime_qa_rejects_paused_animation_and_opaque_foreground_overlay():
    paused = _native_blue_sky_html().replace(
        "animation: cloud-scroll 30s linear infinite;",
        "animation: cloud-scroll 30s linear infinite; animation-play-state: paused;",
    ).replace(
        "animation: cloud-scroll 18s linear infinite;",
        "animation: cloud-scroll 18s linear infinite; animation-play-state: paused;",
    )
    paused_report = analyze_preset_runtime_html(paused, "Blue Sky")
    assert paused_report["pass"] is False
    assert "runtime-motion-time-static" in paused_report["hard_failures"]

    overlay = _native_blue_sky_html().replace(
        "</body>",
        '<div style="position:fixed;inset:0;background:#fff;z-index:999999"></div></body>',
    )
    overlay_report = analyze_preset_runtime_html(overlay, "Blue Sky")
    assert overlay_report["pass"] is False
    assert "runtime-motion-not-visible" in overlay_report["hard_failures"]


def test_runtime_qa_rejects_wrong_runtime_owner_dom():
    report = analyze_preset_runtime_html(
        _native_blue_sky_html().replace('id="track"', 'id="wrong-track"'),
        "Blue Sky",
    )

    assert report["pass"] is False
    assert "runtime-owner-mismatch" in report["hard_failures"]
