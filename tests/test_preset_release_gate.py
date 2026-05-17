from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "preset_release_gate.py"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import preset_release_gate  # noqa: E402


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def test_preset_release_gate_writes_report_and_summary(tmp_path: Path):
    manifest = {
        "suite_id": "gate-smoke-suite",
        "weights": {
            "route": 0.15,
            "compression": 0.25,
            "render": 0.45,
            "efficiency": 0.15,
        },
        "cases": [
            {
                "case_id": "support-paper-ink",
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
                    "required_quality_gates": [
                        "chrome-hidden-by-default",
                        "no-content-occlusion-risk",
                    ],
                },
            }
        ],
    }
    manifest_path = tmp_path / "manifest.json"
    write_json(manifest_path, manifest)

    output_dir = tmp_path / "out"
    report_path = tmp_path / "gate-report.json"
    summary_path = tmp_path / "gate-summary.md"
    result = subprocess.run(
        [
            sys.executable,
            str(GATE),
            "--suite",
            str(manifest_path),
            "--output-dir",
            str(output_dir),
            "--report-path",
            str(report_path),
            "--summary-md",
            str(summary_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    report = json.loads(report_path.read_text(encoding="utf-8"))
    summary = summary_path.read_text(encoding="utf-8")

    assert report["gate"]["passed"] is True
    assert report["summary"]["pass_count"] == 1
    assert "Preset Surface Release Gate" in summary
    assert "`PASS`" in summary


def test_preset_release_gate_can_require_baseline(tmp_path: Path):
    manifest = {
        "suite_id": "gate-baseline-suite",
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
                },
            }
        ],
    }
    manifest_path = tmp_path / "manifest.json"
    write_json(manifest_path, manifest)

    result = subprocess.run(
        [
            sys.executable,
            str(GATE),
            "--suite",
            str(manifest_path),
            "--output-dir",
            str(tmp_path / "out"),
            "--require-baseline",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "missing baseline compare artifact" in (result.stdout + result.stderr)


def test_preset_release_gate_auto_enables_browser_titles_when_suite_requires_them(tmp_path: Path, monkeypatch):
    manifest = {
        "suite_id": "gate-browser-title-suite",
        "weights": {
            "route": 0.15,
            "compression": 0.25,
            "render": 0.45,
            "efficiency": 0.15,
        },
        "cases": [
            {
                "case_id": "support-paper-ink",
                "validation_profile": "strict",
                "preset": "Paper & Ink",
                "html_path": str(ROOT / "demos" / "paper-ink-zh.html"),
                "expectations": {
                    "expected_preset": "Paper & Ink",
                    "expected_support_tier": "supported",
                    "required_title_gates": [
                        "browser-title-composition",
                    ],
                },
            }
        ],
    }
    manifest_path = tmp_path / "manifest.json"
    write_json(manifest_path, manifest)

    called: dict[str, object] = {}

    def fake_run_suite(suite_path, *, output_dir, baseline_dir=None, run_browser_titles=False):
        called["suite_path"] = Path(suite_path)
        called["output_dir"] = Path(output_dir)
        called["baseline_dir"] = baseline_dir
        called["run_browser_titles"] = run_browser_titles
        return {
            "suite_id": "gate-browser-title-suite",
            "output_dir": str(output_dir),
            "baseline_dir": None,
            "cases": [],
            "summary": {
                "pass_count": 0,
                "fail_count": 0,
                "best_case": None,
                "baseline_comparison_enabled": False,
                "non_regression_ready_cases": 0,
            },
        }

    monkeypatch.setattr(preset_release_gate, "run_suite", fake_run_suite)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "preset_release_gate.py",
            "--suite",
            str(manifest_path),
            "--output-dir",
            str(tmp_path / "out"),
        ],
    )

    exit_code = preset_release_gate.main()

    assert exit_code == 0
    assert called["run_browser_titles"] is True


def test_preset_release_gate_can_include_fixture_skill_evals(tmp_path: Path, monkeypatch):
    called: dict[str, object] = {}

    def fake_run_suite(suite_path, *, output_dir, baseline_dir=None, run_browser_titles=False):
        called["suite_path"] = Path(suite_path)
        called["output_dir"] = Path(output_dir)
        called["baseline_dir"] = baseline_dir
        called["run_browser_titles"] = run_browser_titles
        return {
            "suite_id": "gate-skill-eval-suite",
            "output_dir": str(output_dir),
            "baseline_dir": None,
            "cases": [],
            "summary": {
                "pass_count": 0,
                "fail_count": 0,
                "best_case": None,
                "baseline_comparison_enabled": False,
                "non_regression_ready_cases": 0,
            },
        }

    monkeypatch.setattr(preset_release_gate, "run_suite", fake_run_suite)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "preset_release_gate.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--report-path",
            str(tmp_path / "gate-report.json"),
            "--include-skill-evals",
            "--skill-evals-runner",
            "fixture",
            "--skill-evals-case-id",
            "explicit-generate",
            "--skill-evals-normalized-trace",
            "tests/fixtures/skill-evals/explicit-generate-normalized.json",
            "--skill-evals-json-out",
            str(tmp_path / "skill-evals.json"),
        ],
    )

    exit_code = preset_release_gate.main()

    assert exit_code == 0
    report = json.loads((tmp_path / "gate-report.json").read_text(encoding="utf-8"))
    assert report["gate"]["passed"] is True
    assert report["skill_evals"]["summary"]["total"] == 1
    assert report["skill_evals"]["summary"]["failed"] == 0
    assert "scripts/run-skill-evals.py" in report["skill_evals"]["command"]


def test_preset_release_gate_compares_skill_evals_against_baseline(tmp_path: Path, monkeypatch):
    baseline_dir = tmp_path / "baseline"
    baseline_dir.mkdir()
    write_json(
        baseline_dir / "skill-evals.json",
        {
            "cases": [
                {
                    "case_id": "explicit-generate",
                    "total_score": 100,
                    "passed": True,
                    "eval_complete": True,
                    "scores": {"outcome": 25, "process": 25, "style": 25, "efficiency": 25},
                    "failures": [],
                    "metrics": {},
                    "artifact_dir": "/tmp/baseline",
                    "style_rubric": {"source": "fixture", "score": 96},
                }
            ],
            "summary": {
                "total": 1,
                "passed": 1,
                "failed": 0,
                "incomplete": 0,
                "average_score": 100,
                "average_category_scores": {"outcome": 25, "process": 25, "style": 25, "efficiency": 25},
            },
        },
    )

    def fake_run_suite(suite_path, *, output_dir, baseline_dir=None, run_browser_titles=False):
        return {
            "suite_id": "gate-skill-eval-suite",
            "output_dir": str(output_dir),
            "baseline_dir": str(baseline_dir),
            "cases": [],
            "summary": {
                "pass_count": 0,
                "fail_count": 0,
                "best_case": None,
                "baseline_comparison_enabled": True,
                "non_regression_ready_cases": 0,
            },
        }

    def fake_run(command, cwd=None, capture_output=False, text=False, timeout=None):
        json_out = Path(command[command.index("--json-out") + 1])
        write_json(
            json_out,
            {
                "cases": [
                    {
                        "case_id": "explicit-generate",
                        "total_score": 90,
                        "passed": True,
                        "eval_complete": True,
                        "scores": {"outcome": 25, "process": 25, "style": 15, "efficiency": 25},
                        "failures": [],
                        "metrics": {},
                        "artifact_dir": "/tmp/candidate",
                        "style_rubric": None,
                    }
                ],
                "summary": {
                    "total": 1,
                    "passed": 1,
                    "failed": 0,
                    "incomplete": 0,
                    "average_score": 90,
                    "average_category_scores": {"outcome": 25, "process": 25, "style": 15, "efficiency": 25},
                },
            },
        )
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(preset_release_gate, "run_suite", fake_run_suite)
    monkeypatch.setattr(preset_release_gate.subprocess, "run", fake_run)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "preset_release_gate.py",
            "--output-dir",
            str(tmp_path / "out"),
            "--baseline-dir",
            str(baseline_dir),
            "--report-path",
            str(tmp_path / "gate-report.json"),
            "--include-skill-evals",
            "--skill-evals-runner",
            "fixture",
            "--skill-evals-json-out",
            str(tmp_path / "skill-evals.json"),
        ],
    )

    exit_code = preset_release_gate.main()

    assert exit_code == 1
    report = json.loads((tmp_path / "gate-report.json").read_text(encoding="utf-8"))
    assert report["gate"]["passed"] is False
    assert "case.explicit-generate.score_regressed" in report["skill_evals"]["baseline_compare"]["regressions"]
    assert "skill-evals: baseline regression case.explicit-generate.style_regressed" in report["gate"]["failures"]
