from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from quality_eval import _style_signature_coverage, analyze_html_quality  # noqa: E402


QUALITY_EVAL_CLI = SCRIPTS / "eval-quality.py"
COPY_RESIDUAL_FIXTURES = ROOT / "tests" / "fixtures" / "copy-residual"


def _copy_residual_fixture_text(name: str) -> str:
    return (COPY_RESIDUAL_FIXTURES / name).read_text(encoding="utf-8")


def _copy_residual_fixture_json(name: str) -> dict:
    return json.loads(_copy_residual_fixture_text(name))


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


def test_numeric_faithfulness_keeps_decimal_tokens_separated_from_words():
    brief = {
        "content": {"must_include": ["Phase 3.5 Content Review"]},
        "narrative": {
            "slides": [
                {
                    "role": "workflow",
                    "title": "Deterministic workflow",
                    "key_point": "Phase 3.5 Content Review sits between render and export.",
                    "explanation": "Phase 3.5 Content Review（Polish mode） → 16 checkpoints → 修复",
                    "supporting_facts": ["Phase 3.5 — Content Review（Polish mode）"],
                }
            ]
        },
    }
    html = """
    <html>
    <body data-preset="Enterprise Dark">
      <section class="slide" aria-label="workflow" data-export-role="timeline">
        <div class="ent-timeline-date">3.5</div>
        <div class="ent-timeline-copy">Phase 3.5 Content Review</div>
      </section>
    </body>
    </html>
    """

    report = analyze_html_quality(html, brief=brief, preset="Enterprise Dark")

    assert report["diagnostics"]["hallucinated_numeric_tokens"] == []
    assert report["quality_gates"]["numeric-faithfulness"] is True
    assert "hallucinated-numeric-chart-values" not in report["hard_failures"]


def test_numeric_faithfulness_ignores_generated_zero_padded_ordinals():
    source = "PR 首次通过率 68% -> 84%，回归测试耗时 9.5 小时 -> 4.1 小时。"
    html = """
    <html>
    <body data-preset="Data Story">
      <section class="slide" aria-label="comparison" data-export-role="kpi_chart">
        <svg aria-label="line chart">
          <text>01</text><text class="chart-val">68%</text>
          <text class="chart-label">Signal 02</text><text class="chart-val">84%</text>
          <text class="chart-label">Signal 03</text><text class="chart-val">9.5</text>
          <text class="chart-label">Phase 04</text>
          <text class="chart-val">4.1</text>
        </svg>
      </section>
    </body>
    </html>
    """

    report = analyze_html_quality(html, source_text=source, preset="Data Story")

    assert report["diagnostics"]["hallucinated_numeric_tokens"] == []
    assert report["quality_gates"]["numeric-faithfulness"] is True


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


def test_quality_eval_counts_swiss_signature_blocks_as_components():
    html = """
    <html>
    <body data-preset="Swiss Modern">
      <section class="slide" aria-label="presets" data-export-role="contents_index">
        <h2>Preset surface</h2>
        <div class="feat-grid">
          <div class="feat-card"><div class="feat-name">A</div></div>
          <div class="feat-card"><div class="feat-name">B</div></div>
        </div>
      </section>
      <section class="slide" aria-label="validation" data-export-role="data_table">
        <h2>Validation</h2>
        <div class="inst-blocks"><div class="inst-block"><div class="inst-label">Strict</div></div></div>
      </section>
      <section class="slide" aria-label="cta_close" data-export-role="pull_quote">
        <h2>Close</h2>
        <div class="cta-block"><span class="cta-line">Ship the gallery</span></div>
      </section>
    </body>
    </html>
    """

    report = analyze_html_quality(html, preset="Swiss Modern")

    assert report["diagnostics"]["minimal_slide_ratio"] == 0.0
    assert report["diagnostics"]["max_minimal_slide_run"] == 0
    assert report["quality_gates"]["minimal-slide-run"] is True


def test_quality_eval_counts_enterprise_visual_blocks_as_components():
    html = """
    <html>
    <body data-preset="Enterprise Dark">
      <section class="slide enterprise-contrast" aria-label="problem" data-export-role="contrast_split">
        <h2>Before and after</h2>
        <div class="ent-contrast-split">
          <div class="ent-contrast-block ent-contrast-block--negative">
            <h4>Before</h4>
            <div class="ent-contrast-item"><span class="ent-contrast-marker">x</span>Manual handoff</div>
          </div>
          <div class="ent-contrast-block ent-contrast-block--positive">
            <h4>After</h4>
            <div class="ent-contrast-item"><span class="ent-contrast-marker">v</span>Deterministic pipeline</div>
          </div>
        </div>
      </section>
      <section class="slide enterprise-timeline" aria-label="workflow" data-export-role="timeline">
        <h2>Workflow</h2>
        <div class="ent-timeline">
          <div class="ent-timeline-item"><div class="ent-timeline-date">Now</div><div class="ent-timeline-copy">Brief</div></div>
          <div class="ent-timeline-item"><div class="ent-timeline-date">Next</div><div class="ent-timeline-copy">Render</div></div>
        </div>
      </section>
    </body>
    </html>
    """

    report = analyze_html_quality(html, preset="Enterprise Dark")

    assert report["diagnostics"]["avg_component_kinds_per_slide"] == 3.0
    assert report["diagnostics"]["visual_families"] == ["contrast", "timeline"]
    assert report["diagnostics"]["visual_family_variety"] == 1.0
    assert report["diagnostics"]["layout_variety"] == 1.0


def test_layout_variety_uses_visual_rhythm_beyond_export_role_count():
    mixed_html = """
    <html>
    <body data-preset="Enterprise Dark">
      <section class="slide" data-export-role="comparison_matrix"><h2>A</h2><div class="ent-feature-grid"><div class="ent-feature-card">A</div></div></section>
      <section class="slide" data-export-role="comparison_matrix"><h2>B</h2><div class="ent-matrix"><div class="ent-kpi-card">B</div></div></section>
      <section class="slide" data-export-role="comparison_matrix"><h2>C</h2><div class="ent-feature-grid"><div class="ent-feature-card">C</div></div></section>
      <section class="slide" data-export-role="comparison_matrix"><h2>D</h2><div class="ent-matrix"><div class="ent-kpi-card">D</div></div></section>
    </body>
    </html>
    """
    repeated_html = """
    <html>
    <body data-preset="Enterprise Dark">
      <section class="slide" data-export-role="comparison_matrix"><h2>A</h2><div class="ent-feature-grid"><div class="ent-feature-card">A</div></div></section>
      <section class="slide" data-export-role="comparison_matrix"><h2>B</h2><div class="ent-feature-grid"><div class="ent-feature-card">B</div></div></section>
      <section class="slide" data-export-role="comparison_matrix"><h2>C</h2><div class="ent-feature-grid"><div class="ent-feature-card">C</div></div></section>
      <section class="slide" data-export-role="comparison_matrix"><h2>D</h2><div class="ent-feature-grid"><div class="ent-feature-card">D</div></div></section>
    </body>
    </html>
    """

    mixed = analyze_html_quality(mixed_html, preset="Enterprise Dark")["diagnostics"]
    repeated = analyze_html_quality(repeated_html, preset="Enterprise Dark")["diagnostics"]

    assert mixed["layout_role_variety"] == 0.25
    assert mixed["visual_family_variety"] == 0.5
    assert mixed["layout_variety"] > mixed["layout_role_variety"]
    assert mixed["layout_variety"] > repeated["layout_variety"]
    assert repeated["max_visual_family_run"] == 4


def test_data_story_visual_family_uses_specific_components_before_generic_chart():
    html = """
    <html>
    <body data-preset="Data Story">
      <section class="slide ds-workflow" data-export-role="workflow_chart">
        <h2>Workflow</h2>
        <div class="ds-workflow-layout">
          <div class="ds-chart-visual ds-workflow-visual">
            <svg class="ds-chart-svg ds-phase-timeline"></svg>
          </div>
        </div>
      </section>
      <section class="slide ds-chart-insight" data-export-role="chart_insight">
        <h2>Signal</h2>
        <div class="ds-chart-visual"><svg class="ds-chart-svg ds-signal-bars"></svg></div>
      </section>
      <section class="slide ds-chart-insight" data-export-role="chart_insight">
        <h2>Interaction</h2>
        <div class="ds-interaction-layout"><div class="ds-key-strip"><div class="ds-key-card">K</div></div></div>
      </section>
    </body>
    </html>
    """

    diagnostics = analyze_html_quality(html, preset="Data Story")["diagnostics"]

    assert diagnostics["visual_families"] == ["workflow", "bar-chart", "interaction"]
    assert diagnostics["visual_family_variety"] == 1.0


def test_blue_sky_visual_family_uses_layout_primitives_not_role_names():
    html = """
    <html>
    <body data-preset="Blue Sky">
      <section class="slide" data-export-role="pain-solution">
        <div class="layer"><div class="step">A</div></div>
      </section>
      <section class="slide" data-export-role="workflow">
        <div class="layer"><div class="step">B</div></div>
      </section>
      <section class="slide" data-export-role="features">
        <div class="bento"><div class="g"><div class="stat">42</div></div></div>
      </section>
      <section class="slide" data-export-role="validation">
        <div class="cols2"><div class="g">A</div><div class="bl">B</div></div>
      </section>
    </body>
    </html>
    """

    diagnostics = analyze_html_quality(html, preset="Blue Sky")["diagnostics"]

    assert diagnostics["visual_families"] == ["layer-flow", "layer-flow", "bento-stat", "list-split"]
    assert diagnostics["layout_role_variety"] == 1.0
    assert diagnostics["visual_family_variety"] == 0.75
    assert diagnostics["max_visual_family_run"] == 2
    assert diagnostics["layout_variety"] < diagnostics["layout_role_variety"]


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
    assert report["quality_gates"]["baseline-non-regression"] is False
    assert "baseline-regression" in report["hard_failures"]


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


def test_quality_eval_cli_accepts_prior_eval_report_for_non_regression(tmp_path: Path):
    html_path = tmp_path / "deck.html"
    baseline_report_path = tmp_path / "baseline-quality.json"
    output_path = tmp_path / "quality.json"

    html_path.write_text(
        """
        <html><body data-preset="Enterprise Dark">
          <section class="slide" aria-label="problem" data-export-role="contrast_split">
            <h1>Problem</h1><p>Only text.</p>
          </section>
          <section class="slide" aria-label="solution" data-export-role="contrast_split">
            <h2>Solution</h2><p>Still only text.</p>
          </section>
        </body></html>
        """,
        encoding="utf-8",
    )
    baseline_report_path.write_text(
        json.dumps(
            {
                "diagnostics": {
                    "layout_variety": 0.5,
                    "avg_component_kinds_per_slide": 3.0,
                    "style_signature_coverage": None,
                    "minimal_slide_ratio": 1.0,
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
            "Enterprise Dark",
            "--baseline-report",
            str(baseline_report_path),
            "--output",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["comparison"]["non_regression"]["component_diversity_delta"] < -0.05
    assert report["comparison"]["non_regression"]["pass"] is False
    assert report["quality_gates"]["baseline-non-regression"] is False
    assert "baseline-regression" in report["hard_failures"]


def test_quality_eval_passes_clean_copy_residual_fixture():
    brief = _copy_residual_fixture_json("good-brief.json")
    html = _copy_residual_fixture_text("good.html")

    report = analyze_html_quality(html, brief=brief, preset="Swiss Modern")

    assert report["quality_gates"]["no-copy-residual-hard-failures"] is True
    assert report["diagnostics"]["copy_residual_hits"] == []
    assert report["diagnostics"]["must_avoid_residual_hits"] == []
    assert not any(code.endswith("-residual") for code in report["hard_failures"])


def test_quality_eval_hard_fails_visible_placeholder_residual():
    brief = _copy_residual_fixture_json("good-brief.json")
    html = _copy_residual_fixture_text("placeholder-leak.html")

    report = analyze_html_quality(html, brief=brief, preset="Swiss Modern")

    assert report["quality_gates"]["no-copy-residual-hard-failures"] is False
    assert "placeholder-residual" in report["hard_failures"]
    assert report["diagnostics"]["copy_residual_hit_count"] == 1
    assert report["diagnostics"]["copy_residual_hits"] == [
        {
            "code": "placeholder-residual",
            "term": "请输入文本",
            "category": "placeholder",
            "severity": "hard",
            "source": "references/copy-residual-blocklist.json",
            "evidence": "generic editable placeholder text",
        }
    ]


def test_quality_eval_hard_fails_unauthorized_demo_copy_residual():
    brief = _copy_residual_fixture_json("good-brief.json")
    html = _copy_residual_fixture_text("demo-copy-leak.html")

    report = analyze_html_quality(html, brief=brief, preset="Swiss Modern")

    assert report["quality_gates"]["no-copy-residual-hard-failures"] is False
    assert "demo-copy-residual" in report["hard_failures"]
    assert report["diagnostics"]["copy_residual_hits"][0]["term"] == "Salesforce 的产品里程碑几乎逐点映射了行业分水岭"


def test_quality_eval_allows_demo_copy_when_source_authorizes_it():
    brief = _copy_residual_fixture_json("good-brief.json")
    html = _copy_residual_fixture_text("demo-copy-leak.html")
    source = "本次报告主题：Salesforce 的产品里程碑几乎逐点映射了行业分水岭。"

    report = analyze_html_quality(html, brief=brief, source_text=source, preset="Swiss Modern")

    assert report["quality_gates"]["no-copy-residual-hard-failures"] is True
    assert report["diagnostics"]["copy_residual_hits"] == []
    assert "demo-copy-residual" not in report["hard_failures"]


def test_quality_eval_reports_must_avoid_residuals_without_hard_failing():
    brief = _copy_residual_fixture_json("good-brief.json")
    html = _copy_residual_fixture_text("must-avoid-warning.html")

    report = analyze_html_quality(html, brief=brief, preset="Swiss Modern")

    assert report["quality_gates"]["no-copy-residual-hard-failures"] is True
    assert report["diagnostics"]["copy_residual_hits"] == []
    assert report["diagnostics"]["must_avoid_residual_hits"] == [
        {
            "term": "泛泛开场",
            "severity": "warning",
            "source": "brief.content.must_avoid",
        },
        {
            "term": "内部策略禁句：不要外传",
            "severity": "warning",
            "source": "brief.content.must_avoid",
        },
    ]
    assert not any(code in report["hard_failures"] for code in ("must-avoid-copy-residual", "copy-residual"))


def test_quality_eval_flags_chart_without_slide_local_numeric_signal():
    brief = {
        "content": {
            "must_include": ["90/9/1", "18 个月"],
            "global_facts": ["90/9/1", "18 个月"],
        },
        "narrative": {
            "slides": [
                {
                    "role": "driver",
                    "title": "ERP 连通深度是切换的硬开关",
                    "key_point": "没有深连通就切不过去",
                    "visual": "workflow chart",
                    "chart_policy": "auto",
                }
            ]
        },
    }
    html = """
    <html>
    <body data-preset="Data Story">
      <section class="slide" aria-label="driver" data-export-role="workflow_chart">
        <svg aria-label="line chart"><text class="chart-val">90</text><text class="chart-val">18</text></svg>
      </section>
    </body>
    </html>
    """

    report = analyze_html_quality(html, brief=brief, preset="Data Story")

    assert report["diagnostics"]["chart_signal_mismatch_count"] == 1
    assert report["diagnostics"]["chart_signal_mismatch_rate"] == 1.0
    assert report["quality_gates"]["chart-local-signal"] is False
    assert "chart-without-local-numeric-signal" in report["hard_failures"]


def test_quality_eval_tracks_global_fact_overuse_without_forcing_hard_fail():
    brief = {
        "content": {
            "must_include": ["唯一入口", "90/9/1"],
            "global_facts": ["唯一入口", "90/9/1"],
        },
        "narrative": {
            "slides": [
                {"role": "cover"},
                {"role": "problem"},
                {"role": "solution"},
                {"role": "closing"},
            ]
        },
    }
    html = """
    <html>
    <body data-preset="Swiss Modern">
      <section class="slide" aria-label="cover" data-export-role="title_grid"><h1>唯一入口</h1><p>90/9/1</p></section>
      <section class="slide" aria-label="problem" data-export-role="column_content"><h2>唯一入口</h2><p>90/9/1</p></section>
      <section class="slide" aria-label="solution" data-export-role="stat_block"><h2>唯一入口</h2><p>90/9/1</p></section>
      <section class="slide" aria-label="closing" data-export-role="pull_quote"><h2>唯一入口</h2><p>90/9/1</p></section>
    </body>
    </html>
    """

    report = analyze_html_quality(html, brief=brief, preset="Swiss Modern")

    assert report["diagnostics"]["global_fact_overuse_count"] == 2
    assert "chart-without-local-numeric-signal" not in report["hard_failures"]


def test_enterprise_dark_style_coverage_uses_curated_signature_set():
    html = """
    <html>
    <head>
      <style>body::before { content: ""; }</style>
    </head>
    <body data-preset="Enterprise Dark">
      <section class="slide" data-page-bucket="content">
        <div class="ent-shell ent-title ent-label-tag ent-kpi-card ent-kpi-number ent-kpi-label ent-badge ent-sep ent-split ent-split-panel ent-feature-row ent-arch-grid preset-enterprise-dark-content">content</div>
      </section>
    </body>
    </html>
    """

    coverage = _style_signature_coverage(BeautifulSoup(html, "html.parser"), "Enterprise Dark")

    assert coverage == 1.0


def test_data_story_style_coverage_counts_slide_before_background():
    html = """
    <html>
    <head>
      <style>.slide::before { content: ""; }</style>
    </head>
    <body data-preset="Data Story">
      <section class="slide" data-page-bucket="content">
        <div class="ds-shell ds-heading ds-hero-slide ds-kpi ds-kpi-card ds-kpi-grid ds-kpi-label ds-chart-svg ds-insight ds-divider ds-split-layout ds-stage-grid preset-data-story-content">content</div>
      </section>
    </body>
    </html>
    """

    coverage = _style_signature_coverage(BeautifulSoup(html, "html.parser"), "Data Story")

    assert coverage == 1.0
