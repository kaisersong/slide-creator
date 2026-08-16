from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_evals  # noqa: E402
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
                "html_path": str(ROOT / "demos" / "blue-sky-zh.html"),
                "expectations": {
                    "expected_preset": "Blue Sky",
                    "expected_support_tier": "production",
                    "required_html_checks": [
                        "blue-sky-architecture",
                        "present-mode",
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
                "preset_fidelity_mode": "reference",
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
                "preset_fidelity_mode": "reference",
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


def test_run_suite_merges_browser_geometry_hard_failures(tmp_path: Path, monkeypatch):
    manifest = {
        "suite_id": "test-browser-geometry-suite",
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

    def fake_geometry(path, *, preset=None, artifact_dir=None, stable_runs=1, viewports=None, modes=None):
        assert Path(path).name == "deck.html"
        assert preset == "Paper & Ink"
        assert artifact_dir is not None
        assert stable_runs == 1
        # Desktop geometry must cover the laptop window and both playback modes.
        assert viewports == [
            {"width": 1600, "height": 900},
            {"width": 1280, "height": 720},
            {"width": 1440, "height": 733},
        ]
        assert tuple(modes) == ("window", "present")
        return {
            "pass": False,
            "hard_failures": ["browser-geometry-character-overlap"],
            "violations": [
                {
                    "type": "character_overlap",
                    "code": "browser-geometry-character-overlap",
                    "slide_index": 7,
                    "selector": "div.code-block",
                }
            ],
            "diagnostics": {"hard_violation_count": 1},
        }

    monkeypatch.setattr(run_evals, "analyze_browser_geometry_path", fake_geometry)

    report = run_suite(manifest_path, output_dir=tmp_path / "out", run_browser_geometry=True)
    case = report["cases"][0]

    assert report["summary"]["fail_count"] == 1
    assert case["pass"] is False
    assert "browser-geometry-character-overlap" in case["hard_failures"]
    assert case["validations"]["browser_geometry"]["hard_failures"] == ["browser-geometry-character-overlap"]
    assert Path(case["validations"]["browser_geometry_report_path"]).exists()


def test_run_suite_merges_contract_export_mobile_ai_and_pptx_gate_reports(tmp_path: Path, monkeypatch):
    manifest = {
        "suite_id": "test-contract-export-mobile-suite",
        "weights": {
            "route": 0.15,
            "compression": 0.25,
            "render": 0.45,
            "efficiency": 0.15,
        },
        "cases": [
            {
                "case_id": "fixture-paper-ink",
                "validation_profile": "required",
                "preset": "Paper & Ink",
                "html_path": str(ROOT / "demos" / "paper-ink-zh.html"),
                "expectations": {
                    "expected_preset": "Paper & Ink",
                    "expected_support_tier": "supported",
                },
            }
        ],
    }
    manifest_path = tmp_path / "manifest.json"
    write_json(manifest_path, manifest)

    def fake_contract(path, preset=None):
        assert Path(path).name == "deck.html"
        assert preset == "Paper & Ink"
        return {
            "pass": False,
            "hard_failures": ["contract-required-visible-component-missing"],
            "violations": [{"code": "contract-required-visible-component-missing"}],
        }

    def fake_export(path, *, preset=None, output_dir=None):
        assert Path(path).name == "deck.html"
        assert preset == "Paper & Ink"
        assert output_dir is not None
        return {
            "pass": True,
            "hard_failures": [],
            "violations": [],
            "diagnostics": {"slot_count": 10},
            "output_dir": str(output_dir),
        }

    def fake_ai(path, *, preset=None):
        assert Path(path).name == "deck.html"
        assert preset == "Paper & Ink"
        return {
            "pass": True,
            "hard_failures": [],
            "violations": [],
            "diagnostics": {"max_visual_signature_run": 1},
        }

    def fake_pptx(path, *, preset=None, output_dir=None):
        assert Path(path).name == "deck.html"
        assert preset == "Paper & Ink"
        assert output_dir is not None
        return {
            "pass": True,
            "hard_failures": [],
            "violations": [],
            "diagnostics": {"html_slide_count": 8, "pptx_slide_count": 8},
            "pptx_path": str(Path(output_dir) / "paper-ink.pptx"),
        }

    def fake_geometry(path, *, preset=None, artifact_dir=None, stable_runs=1, viewports=None, modes=None):
        assert Path(path).name == "deck.html"
        assert preset == "Paper & Ink"
        assert artifact_dir is not None
        assert stable_runs == 1
        assert viewports == [{"width": 390, "height": 844}]
        return {
            "pass": False,
            "hard_failures": ["mobile-browser-geometry-text-overflow"],
            "violations": [{"code": "mobile-browser-geometry-text-overflow"}],
            "diagnostics": {"hard_violation_count": 1},
            "runner": {"viewports": viewports},
        }

    monkeypatch.setattr(run_evals, "check_preset_contract_path", fake_contract, raising=False)
    monkeypatch.setattr(run_evals, "run_export_smoke", fake_export, raising=False)
    monkeypatch.setattr(run_evals, "analyze_ai_advised_path", fake_ai, raising=False)
    monkeypatch.setattr(run_evals, "run_pptx_export_smoke", fake_pptx, raising=False)
    monkeypatch.setattr(run_evals, "analyze_browser_geometry_path", fake_geometry)

    report = run_suite(
        manifest_path,
        output_dir=tmp_path / "out",
        run_contract=True,
        run_export_smoke=True,
        run_mobile_geometry=True,
        run_ai_advised=True,
        run_pptx_export=True,
    )
    case = report["cases"][0]

    assert report["summary"]["fail_count"] == 1
    assert case["pass"] is False
    assert "contract-required-visible-component-missing" in case["hard_failures"]
    assert "mobile-browser-geometry-text-overflow" in case["hard_failures"]
    assert case["validations"]["preset_fidelity"]["pass"] is False
    assert case["validations"]["export_smoke"]["pass"] is True
    assert case["validations"]["mobile_geometry"]["pass"] is False
    assert case["validations"]["ai_advised"]["pass"] is True
    assert case["validations"]["pptx_export"]["pass"] is True
    assert Path(case["validations"]["preset_fidelity_report_path"]).exists()
    assert Path(case["validations"]["export_smoke_report_path"]).exists()
    assert Path(case["validations"]["mobile_geometry_report_path"]).exists()
    assert Path(case["validations"]["ai_advised_report_path"]).exists()
    assert Path(case["validations"]["pptx_export_report_path"]).exists()


def test_run_suite_attaches_promotion_gate_report(tmp_path: Path, monkeypatch):
    manifest = {
        "suite_id": "test-promotion-gate-suite",
        "weights": {
            "route": 0.15,
            "compression": 0.25,
            "render": 0.45,
            "efficiency": 0.15,
        },
        "cases": [
            {
                "case_id": "fixture-paper-ink",
                "validation_profile": "required",
                "preset": "Paper & Ink",
                "html_path": str(ROOT / "demos" / "paper-ink-zh.html"),
                "expectations": {
                    "expected_preset": "Paper & Ink",
                    "expected_support_tier": "supported",
                },
            }
        ],
    }
    manifest_path = tmp_path / "manifest.json"
    write_json(manifest_path, manifest)

    def fake_promotion_gate(*, release_report=None, release_report_path=None):
        assert release_report is not None
        assert release_report_path is None
        return {
            "pass": False,
            "hard_failures": ["promotion-profile-renderer-claimed-native"],
            "violations": [{"code": "promotion-profile-renderer-claimed-native"}],
            "diagnostics": {"checked_case_count": 1},
        }

    monkeypatch.setattr(run_evals, "run_promotion_gate", fake_promotion_gate, raising=False)

    report = run_suite(
        manifest_path,
        output_dir=tmp_path / "out",
        run_promotion_gate=True,
    )

    assert report["promotion_gate"]["pass"] is False
    assert report["promotion_gate"]["hard_failures"] == ["promotion-profile-renderer-claimed-native"]
    assert Path(report["promotion_gate_report_path"]).exists()


def test_run_suite_attaches_demo_parity_gate_report(tmp_path: Path, monkeypatch):
    manifest = {
        "suite_id": "test-demo-parity-gate-suite",
        "weights": {
            "route": 0.15,
            "compression": 0.25,
            "render": 0.45,
            "efficiency": 0.15,
        },
        "cases": [
            {
                "case_id": "fixture-paper-ink",
                "validation_profile": "required",
                "preset": "Paper & Ink",
                "html_path": str(ROOT / "demos" / "paper-ink-zh.html"),
                "expectations": {
                    "expected_preset": "Paper & Ink",
                    "expected_support_tier": "supported",
                },
            }
        ],
    }
    manifest_path = tmp_path / "manifest.json"
    write_json(manifest_path, manifest)

    called: dict[str, object] = {}

    def fake_demo_parity(*, candidate_dir, demo_dir, output_dir, viewports=None, require_visual=False):
        called["candidate_dir"] = Path(candidate_dir)
        called["demo_dir"] = Path(demo_dir)
        called["output_dir"] = Path(output_dir)
        called["viewports"] = viewports
        called["require_visual"] = require_visual
        return {
            "pass": False,
            "summary": {"preset_count": 17, "verdicts": {"FAIL": 1}, "average_score": 0.9},
            "results": [
                {
                    "preset": "Creative Voltage",
                    "verdict": "FAIL",
                    "main_issue": "visual parity diverges",
                    "visual_gate": {"failures": ["desktop visual similarity 0.2 below fail threshold 0.55"]},
                    "required_instance_failures": [],
                }
            ],
        }

    monkeypatch.setattr(run_evals, "run_demo_parity_gate", fake_demo_parity, raising=False)

    output_dir = tmp_path / "out"
    report = run_suite(
        manifest_path,
        output_dir=output_dir,
        run_demo_parity=True,
        demo_parity_require_visual=True,
        demo_parity_viewports=["desktop", "mobile"],
    )

    assert called["candidate_dir"] == output_dir
    assert called["demo_dir"] == ROOT / "demos"
    assert called["output_dir"] == output_dir / "demo-parity"
    assert called["viewports"] == ["desktop", "mobile"]
    assert called["require_visual"] is True
    assert report["demo_parity"]["pass"] is False
    assert report["demo_parity_report_path"] == str(output_dir / "demo-parity" / "demo-parity-report.json")
