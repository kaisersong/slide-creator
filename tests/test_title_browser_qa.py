from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from title_browser_qa import collect_title_browser_targets, summarize_title_browser_report  # noqa: E402


def test_collect_title_browser_targets_uses_registry_profiles():
    vertical_html = """
    <html>
      <body data-preset="Chinese Chan">
        <section class="slide zen_vertical" data-export-role="zen_vertical" id="slide-1">
          <div class="zen-vertical-title">竖排标题</div>
        </section>
      </body>
    </html>
    """
    glitch_html = """
    <html>
      <body data-preset="Neon Cyber">
        <section class="slide" id="slide-1">
          <h1 class="cyber-title" data-text="signal lockup">signal lockup</h1>
        </section>
      </body>
    </html>
    """

    vertical_payload = collect_title_browser_targets(vertical_html)
    glitch_payload = collect_title_browser_targets(glitch_html)
    profiles = [target["profile"] for target in vertical_payload["targets"]]
    glitch_profiles = [target["profile"] for target in glitch_payload["targets"]]

    assert vertical_payload["registry_version"] == 1
    assert "vertical_title" in profiles
    assert "glitch_lockup" in glitch_profiles
    assert "data-title-qa-id" in vertical_payload["annotated_html"]


def test_summarize_title_browser_report_flags_horizontal_failures():
    targets = [
        {
            "qa_id": "slide-1-title-1",
            "profile": "horizontal_balanced_left_anchor",
            "node_type": "ordinary_heading",
            "slide_index": 1,
            "layout_id": "title_grid",
            "max_lines": 3,
            "required_companion_selectors": [],
            "required_attributes": [],
            "text": "Visible Control Wins",
            "tag_name": "h1",
        }
    ]
    measurements = [
        {
            "qa_id": "slide-1-title-1",
            "missing": False,
            "line_count": 4,
            "line_widths": [420.0, 92.0, 408.0, 388.0],
            "clipped": True,
            "occluded": False,
            "occluded_by": [],
            "writing_mode": "horizontal-tb",
            "tag_name": "h1",
            "classes": ["swiss-title"],
            "attrs_present": True,
            "companions_present": True,
        }
    ]

    report = summarize_title_browser_report(targets, measurements, preset="Swiss Modern")

    assert report["pass"] is False
    assert "browser-title-too-many-lines" in report["hard_failures"]
    assert "browser-title-orphan-line" in report["hard_failures"]
    assert "browser-title-clipped" in report["hard_failures"]
    assert report["diagnostics"]["title_hard_fail_rate"] == 1.0
    assert report["diagnostics"]["orphan_line_rate"] == 1.0
    assert report["diagnostics"]["title_clipping_rate"] == 1.0


def test_summarize_title_browser_report_flags_structural_breaks():
    targets = [
        {
            "qa_id": "slide-2-title-1",
            "profile": "split_lockup",
            "node_type": "lockup_object",
            "slide_index": 2,
            "layout_id": None,
            "max_lines": 2,
            "required_companion_selectors": [".title-accent"],
            "required_attributes": [],
            "text": "slide-",
            "tag_name": "div",
        }
    ]
    measurements = [
        {
            "qa_id": "slide-2-title-1",
            "missing": False,
            "line_count": 1,
            "line_widths": [320.0],
            "clipped": False,
            "occluded": False,
            "occluded_by": [],
            "writing_mode": "horizontal-tb",
            "tag_name": "div",
            "classes": ["main-title"],
            "attrs_present": True,
            "companions_present": False,
        }
    ]

    report = summarize_title_browser_report(targets, measurements, preset="Creative Voltage")

    assert report["pass"] is False
    assert "browser-title-profile-mismatch" in report["hard_failures"]
    assert report["diagnostics"]["profile_mismatch_rate"] == 1.0
    assert report["diagnostics"]["structural_preset_break_rate"] == 1.0
