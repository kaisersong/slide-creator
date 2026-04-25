from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from quality_eval import analyze_html_quality  # noqa: E402


QUALITY_EVAL_CLI = SCRIPTS / "eval-quality.py"


def test_detects_default_notes_panel_leak_and_occlusion_risk():
    html = """
    <html>
    <head>
    <style>
    .slide { overflow: hidden; }
    .slide-content { overflow: hidden; }
    #notes-panel { position: fixed; right: 18px; bottom: 18px; width: min(380px, 36vw); }
    .edit-toggle { opacity: 0; }
    </style>
    </head>
    <body data-preset="Swiss Modern">
      <button class="edit-toggle" id="editToggle">Edit</button>
      <div id="notes-panel">notes</div>
      <section class="slide" aria-label="cover" data-export-role="title_grid">
        <div class="slide-content"><h1>Visible Control Wins</h1><p>Body.</p></div>
      </section>
    </body>
    </html>
    """

    report = analyze_html_quality(html, preset="Swiss Modern")

    assert report["diagnostics"]["chrome_leak"] is True
    assert report["diagnostics"]["default_visible_chrome"] == ["notes-panel"]
    assert report["diagnostics"]["content_occlusion_risk"] is True
    assert report["quality_gates"]["chrome-hidden-by-default"] is False
    assert report["quality_gates"]["no-content-occlusion-risk"] is False
    assert "chrome-visible-by-default" in report["hard_failures"]
    assert "content-occlusion-risk" in report["hard_failures"]


def test_numeric_faithfulness_catches_hallucinated_chart_values():
    source = """
    76% 汽车、14% 能源、10% 服务。
    近四季度交付量分别为 44.4、46.3、49.6、33.7 万辆。
    """
    html = """
    <html>
    <body data-preset="Data Story">
      <section class="slide" aria-label="metrics" data-export-role="kpi_chart">
        <div class="slide-content">
          <div class="ds-kpi">76%</div>
          <svg><text class="chart-val">20</text><text class="chart-val">44</text><text class="chart-val">63</text><text class="chart-val">88</text></svg>
        </div>
      </section>
    </body>
    </html>
    """

    report = analyze_html_quality(html, source_text=source, preset="Data Story")

    assert report["diagnostics"]["numeric_faithfulness"] < 1.0
    assert report["diagnostics"]["hallucinated_numeric_tokens"] == ["20", "44", "63", "88"]
    assert report["quality_gates"]["numeric-faithfulness"] is False
    assert "hallucinated-numeric-chart-values" in report["hard_failures"]


def test_tracks_narrative_role_coverage_and_minimal_slide_ratio():
    brief = {
        "content": {"must_include": ["Salesforce 四阶段", "Tesla 76% / 14% / 10%"]},
        "narrative": {
            "slides": [
                {"role": "cover"},
                {"role": "comparison"},
                {"role": "closing"},
            ]
        },
    }
    html = """
    <html>
    <body data-preset="Swiss Modern">
      <section class="slide" aria-label="cover" data-export-role="title_grid"><h1>A</h1><p>Only one sentence.</p></section>
      <section class="slide" aria-label="comparison" data-export-role="title_grid"><h2>B</h2><p>Only one sentence.</p></section>
      <section class="slide" aria-label="closing" data-export-role="data_table"><h2>C</h2><table><tr><td>x</td></tr></table></section>
    </body>
    </html>
    """

    report = analyze_html_quality(html, brief=brief, preset="Swiss Modern")

    assert report["diagnostics"]["narrative_role_coverage"] == 1.0
    assert report["diagnostics"]["role_sequence_match"] is True
    assert report["diagnostics"]["minimal_slide_ratio"] == 0.6667
    assert report["diagnostics"]["max_minimal_slide_run"] == 2
    assert report["quality_gates"]["minimal-slide-run"] is True


def test_non_regression_comparison_flags_flatter_candidate():
    baseline_html = """
    <html><body data-preset="Swiss Modern">
      <section class="slide" aria-label="cover" data-export-role="title_grid"><h1>A</h1><p>x</p><svg><text>2016</text></svg></section>
      <section class="slide" aria-label="comparison" data-export-role="data_table"><h2>B</h2><table><tr><td>76%</td></tr></table></section>
      <section class="slide" aria-label="closing" data-export-role="pull_quote"><h2>C</h2><ul><li>fact</li></ul></section>
    </body></html>
    """
    candidate_html = """
    <html><body data-preset="Swiss Modern">
      <section class="slide" aria-label="cover" data-export-role="title_grid"><h1>A</h1><p>x</p></section>
      <section class="slide" aria-label="comparison" data-export-role="title_grid"><h2>B</h2><p>y</p></section>
      <section class="slide" aria-label="closing" data-export-role="title_grid"><h2>C</h2><p>z</p></section>
    </body></html>
    """

    report = analyze_html_quality(
        candidate_html,
        preset="Swiss Modern",
        baseline_html=baseline_html,
    )

    comparison = report["comparison"]["non_regression"]
    assert comparison["layout_variety_delta"] < 0
    assert comparison["component_diversity_delta"] < 0
    assert comparison["minimal_slide_ratio_delta"] > 0
    assert comparison["pass"] is False


def test_quality_eval_cli_emits_json_report(tmp_path: Path):
    html_path = tmp_path / "deck.html"
    source_path = tmp_path / "source.md"
    output_path = tmp_path / "quality.json"

    html_path.write_text(
        """
        <html><body data-preset="Data Story">
          <section class="slide" aria-label="metrics" data-export-role="kpi_chart">
            <div class="slide-content">
              <div class="ds-kpi">76%</div>
              <svg><text class="chart-val">20</text></svg>
            </div>
          </section>
        </body></html>
        """,
        encoding="utf-8",
    )
    source_path.write_text("76% 汽车、14% 能源、10% 服务。", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(QUALITY_EVAL_CLI),
            str(html_path),
            "--source",
            str(source_path),
            "--preset",
            "Data Story",
            "--output",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["preset"] == "Data Story"
    assert report["diagnostics"]["numeric_faithfulness"] == 0.5
    assert report["hard_failures"] == ["hallucinated-numeric-chart-values"]


def test_quality_eval_merges_title_browser_report():
    html = """
    <html>
    <body data-preset="Swiss Modern">
      <section class="slide" aria-label="cover" data-export-role="title_grid">
        <div class="slide-content"><h1>Visible Control Wins</h1></div>
      </section>
    </body>
    </html>
    """
    browser_report = {
        "pass": False,
        "hard_failures": ["browser-title-too-many-lines", "browser-title-clipped"],
        "diagnostics": {
            "browser_title_target_count": 1,
            "title_hard_fail_rate": 1.0,
            "orphan_line_rate": 0.0,
            "collapsed_middle_line_rate": 0.0,
            "profile_mismatch_rate": 0.0,
            "structural_preset_break_rate": 0.0,
            "title_clipping_rate": 1.0,
            "title_occlusion_rate": 0.0,
        },
    }

    report = analyze_html_quality(html, preset="Swiss Modern", title_browser_report=browser_report)

    assert report["quality_gates"]["browser-title-composition"] is False
    assert report["diagnostics"]["browser_title_target_count"] == 1
    assert report["diagnostics"]["title_hard_fail_rate"] == 1.0
    assert "browser-title-too-many-lines" in report["hard_failures"]
    assert "browser-title-clipped" in report["hard_failures"]


def test_quality_eval_cli_accepts_precomputed_title_browser_report(tmp_path: Path):
    html_path = tmp_path / "deck.html"
    browser_report_path = tmp_path / "title-browser.json"
    output_path = tmp_path / "quality.json"

    html_path.write_text(
        """
        <html><body data-preset="Swiss Modern">
          <section class="slide" aria-label="cover" data-export-role="title_grid">
            <h1>Visible Control Wins</h1>
          </section>
        </body></html>
        """,
        encoding="utf-8",
    )
    browser_report_path.write_text(
        json.dumps(
            {
                "pass": False,
                "hard_failures": ["browser-title-too-many-lines"],
                "diagnostics": {
                    "browser_title_target_count": 1,
                    "title_hard_fail_rate": 1.0,
                    "orphan_line_rate": 0.0,
                    "collapsed_middle_line_rate": 0.0,
                    "profile_mismatch_rate": 0.0,
                    "structural_preset_break_rate": 0.0,
                    "title_clipping_rate": 0.0,
                    "title_occlusion_rate": 0.0
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(QUALITY_EVAL_CLI),
            str(html_path),
            "--preset",
            "Swiss Modern",
            "--title-browser-report",
            str(browser_report_path),
            "--output",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["quality_gates"]["browser-title-composition"] is False
    assert report["diagnostics"]["title_hard_fail_rate"] == 1.0
    assert "browser-title-too-many-lines" in report["hard_failures"]
