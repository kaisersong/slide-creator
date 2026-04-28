from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from run_evals import run_suite  # noqa: E402


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def test_run_suite_supports_fixture_and_render_cases(tmp_path: Path):
    manifest = {
        "suite_id": "test-mixed-suite",
        "weights": {
            "route": 0.15,
            "compression": 0.25,
            "render": 0.45,
            "efficiency": 0.15,
        },
        "cases": [
            {
                "case_id": "fixture-blue-sky",
                "validation_profile": "required",
                "preset": "Blue Sky",
                "html_path": str(ROOT / "demos" / "ai-native-work-hub-blue-sky-zh.html"),
                "expectations": {
                    "expected_preset": "Blue Sky",
                    "expected_support_tier": "production",
                    "required_html_checks": [
                        "blue-sky-architecture",
                        "present-mode",
                        "edit-mode",
                        "watermark-injected",
                    ],
                    "required_quality_gates": [
                        "chrome-hidden-by-default",
                    ],
                },
            },
            {
                "case_id": "render-swiss",
                "validation_profile": "strict",
                "brief_path": str(ROOT / "evals" / "preset-surface-phase1" / "cases" / "core-swiss-modern-brief.json"),
                "expectations": {
                    "expected_mode": "auto",
                    "expected_preset": "Swiss Modern",
                    "expected_support_tier": "production",
                    "required_html_checks": [
                        "shared-runtime",
                        "present-mode",
                        "edit-mode",
                        "watermark-injected",
                    ],
                    "required_quality_gates": [
                        "chrome-hidden-by-default",
                        "no-content-occlusion-risk",
                    ],
                    "quality_thresholds": {
                        "narrative_role_coverage": 1.0,
                    },
                },
            },
        ],
    }
    manifest_path = tmp_path / "manifest.json"
    write_json(manifest_path, manifest)

    report = run_suite(manifest_path, output_dir=tmp_path / "out")

    assert report["summary"]["pass_count"] == 2
    assert report["summary"]["fail_count"] == 0
    assert {case["mode"] for case in report["cases"]} == {"html-fixture", "render"}
    fixture_case = next(case for case in report["cases"] if case["mode"] == "html-fixture")
    assert Path(fixture_case["html_path"]).exists()
    assert fixture_case["fixture_html_path"] is not None


def test_run_suite_compares_against_baseline_dir(tmp_path: Path):
    manifest = {
        "suite_id": "test-baseline-suite",
        "weights": {
            "route": 0.15,
            "compression": 0.25,
            "render": 0.45,
            "efficiency": 0.15,
        },
        "cases": [
            {
                "case_id": "render-swiss",
                "validation_profile": "strict",
                "brief_path": str(ROOT / "evals" / "preset-surface-phase1" / "cases" / "core-swiss-modern-brief.json"),
                "expectations": {
                    "expected_mode": "auto",
                    "expected_preset": "Swiss Modern",
                    "expected_support_tier": "production",
                    "required_html_checks": [
                        "shared-runtime",
                        "present-mode",
                        "edit-mode",
                        "watermark-injected",
                    ],
                    "non_regression_metrics": [
                        "layout-variety",
                        "component-diversity",
                        "style-signature-coverage",
                    ],
                },
            }
        ],
    }
    manifest_path = tmp_path / "manifest.json"
    write_json(manifest_path, manifest)

    baseline_dir = tmp_path / "baseline"
    report_a = run_suite(manifest_path, output_dir=baseline_dir)
    assert report_a["summary"]["pass_count"] == 1

    candidate_dir = tmp_path / "candidate"
    report_b = run_suite(manifest_path, output_dir=candidate_dir, baseline_dir=baseline_dir)
    case = report_b["cases"][0]

    assert report_b["summary"]["baseline_comparison_enabled"] is True
    assert case["baseline_html_path"] is not None
    assert case["diagnostics"]["low_context"]["layout_variety"] > 0
    assert case["pass"] is True


def test_run_suite_writes_fixture_html_for_baseline_ready_reuse(tmp_path: Path):
    manifest = {
        "suite_id": "test-fixture-baseline-suite",
        "weights": {
            "route": 0.15,
            "compression": 0.25,
            "render": 0.45,
            "efficiency": 0.15,
        },
        "cases": [
            {
                "case_id": "fixture-paper-ink",
                "validation_profile": "strict",
                "preset": "Paper & Ink",
                "html_path": str(ROOT / "demos" / "paper-ink-zh.html"),
                "expectations": {
                    "expected_preset": "Paper & Ink",
                    "expected_support_tier": "supported",
                    "required_html_checks": [
                        "shared-runtime",
                        "present-mode",
                        "edit-mode",
                        "watermark-injected",
                    ],
                },
            }
        ],
    }
    manifest_path = tmp_path / "manifest.json"
    write_json(manifest_path, manifest)

    baseline_dir = tmp_path / "baseline"
    report_a = run_suite(manifest_path, output_dir=baseline_dir)
    assert report_a["summary"]["pass_count"] == 1
    assert (baseline_dir / "fixture-paper-ink" / "deck.html").exists()

    candidate_dir = tmp_path / "candidate"
    report_b = run_suite(manifest_path, output_dir=candidate_dir, baseline_dir=baseline_dir)
    case = report_b["cases"][0]

    assert case["baseline_html_path"] == str(baseline_dir / "fixture-paper-ink" / "deck.html")


def test_run_suite_handles_invalid_brief_fail_closed_case(tmp_path: Path):
    manifest = {
        "suite_id": "test-invalid-brief-suite",
        "weights": {
            "route": 0.15,
            "compression": 0.25,
            "render": 0.45,
            "efficiency": 0.15,
        },
        "cases": [
            {
                "case_id": "invalid-brief",
                "brief_path": str(
                    ROOT / "evals" / "late-context" / "cases" / "lc-011-invalid-brief-fail-closed" / "expected-brief.json"
                ),
                "expectations": {
                    "artifact_status": "invalid",
                    "should_fail_closed": True,
                },
            }
        ],
    }
    manifest_path = tmp_path / "manifest.json"
    write_json(manifest_path, manifest)

    report = run_suite(manifest_path, output_dir=tmp_path / "out")
    case = report["cases"][0]

    assert report["summary"]["pass_count"] == 1
    assert case["pass"] is True
    assert case["mode"] == "invalid-brief"
    assert case["validations"]["brief"]["passed"] is False


def test_run_suite_degrades_gracefully_when_browser_title_qa_is_unavailable(tmp_path: Path, monkeypatch):
    manifest = {
        "suite_id": "test-browser-title-fallback-suite",
        "weights": {
            "route": 0.15,
            "compression": 0.25,
            "render": 0.45,
            "efficiency": 0.15,
        },
        "cases": [
            {
                "case_id": "fixture-paper-ink",
                "validation_profile": "strict",
                "preset": "Paper & Ink",
                "html_path": str(ROOT / "demos" / "paper-ink-zh.html"),
                "expectations": {
                    "expected_preset": "Paper & Ink",
                    "expected_support_tier": "supported",
                    "required_html_checks": [
                        "shared-runtime",
                        "present-mode",
                        "edit-mode",
                        "watermark-injected",
                    ],
                },
            }
        ],
    }
    manifest_path = tmp_path / "manifest.json"
    write_json(manifest_path, manifest)

    def boom(*_args, **_kwargs):
        raise RuntimeError("playwright unavailable")

    monkeypatch.setattr("run_evals.analyze_title_composition_path", boom)
    report = run_suite(manifest_path, output_dir=tmp_path / "out", run_browser_titles=True)
    case = report["cases"][0]

    assert report["summary"]["pass_count"] == 1
    assert case["validations"]["title_browser"]["unavailable"] is True
    assert "playwright unavailable" in case["validations"]["title_browser"]["error"]
