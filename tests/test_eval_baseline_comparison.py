from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from compare_eval_reports import _markdown_summary, compare_reports  # noqa: E402


def _case(
    preset: str,
    *,
    passed: bool,
    score: float,
    strict: bool,
    status: str = "profile",
    repair_rounds: int = 0,
    style_signature: float = 1.0,
) -> dict:
    return {
        "case_id": preset.lower().replace(" ", "-"),
        "pass": passed,
        "overall": score,
        "packet": {
            "canonical_preset": preset,
            "preset_generation_status": status,
            "repair_rounds": repair_rounds,
        },
        "validations": {"html_validate": {"passed": strict}},
        "diagnostics": {"low_context": {"style_signature_coverage": style_signature}},
    }


def test_compare_reports_returns_overall_and_per_preset_deltas():
    baseline = {
        "git_head": "old-sha",
        "cases": [
            _case("Swiss Modern", passed=True, score=0.5, strict=True, repair_rounds=1, style_signature=0.4),
            _case("Terminal Green", passed=True, score=0.75, strict=True, repair_rounds=2, style_signature=0.6),
        ],
    }
    candidate = {
        "git_head": "new-sha",
        "git_dirty": True,
        "cases": [
            _case("Swiss Modern", passed=True, score=1.0, strict=True, repair_rounds=0, style_signature=0.9),
            _case("Terminal Green", passed=True, score=0.25, strict=False, repair_rounds=1, style_signature=0.5),
        ],
    }

    delta = compare_reports(baseline=baseline, candidate=candidate, manifest="evals/preset-surface-all/manifest.json")

    assert delta["baseline_status"] == "found"
    assert delta["overall"] == {
        "baseline_score": 0.625,
        "candidate_score": 0.625,
        "candidate_full_score": 0.625,
        "delta": 0.0,
    }
    assert delta["comparable_preset_count"] == 2
    assert delta["by_preset"]["Swiss Modern"]["delta"] == 0.5
    assert delta["by_preset"]["Swiss Modern"]["repair_rounds_delta"] == -1
    assert delta["by_preset"]["Swiss Modern"]["style_signature_delta"] == 0.5
    assert delta["by_preset"]["Terminal Green"]["delta"] == -0.5
    assert delta["by_preset"]["Terminal Green"]["strict_validation_delta"] == -1
    assert delta["candidate_git_sha"] == "new-sha"
    assert delta["candidate_git_dirty"] is True


def test_compare_reports_marks_fixed_and_new_failures():
    baseline = {
        "cases": [
            _case("Paper & Ink", passed=False, score=0.0, strict=False, status="unsupported_archive"),
            _case("Terminal Green", passed=True, score=1.0, strict=True, status="profile"),
        ]
    }
    candidate = {
        "cases": [
            _case("Paper & Ink", passed=True, score=1.0, strict=True, status="profile"),
            _case("Terminal Green", passed=False, score=0.0, strict=False, status="profile"),
        ]
    }

    delta = compare_reports(baseline=baseline, candidate=candidate, manifest=None)

    assert "Paper & Ink: eval case now passes" in delta["fixed_failures"]
    assert "Terminal Green: candidate eval case regressed to failure" in delta["new_failures"]
    assert delta["by_preset"]["Paper & Ink"]["generation_status_delta"] == "unsupported_archive_fail_to_profile_pass"
    assert delta["by_preset"]["Terminal Green"]["generation_status_delta"] == "profile_pass_to_profile_fail"
    assert delta["new_coverage"] == []


def test_compare_reports_uses_only_intersection_for_comparable_overall():
    baseline = {"cases": [_case("Swiss Modern", passed=True, score=0.5, strict=True)]}
    candidate = {
        "cases": [
            _case("Swiss Modern", passed=True, score=1.0, strict=True),
            _case("Paper & Ink", passed=True, score=0.0, strict=True),
        ]
    }

    delta = compare_reports(baseline=baseline, candidate=candidate, manifest=None)

    assert delta["baseline_preset_count"] == 1
    assert delta["candidate_preset_count"] == 2
    assert delta["comparable_preset_count"] == 1
    assert delta["overall"]["baseline_score"] == 0.5
    assert delta["overall"]["candidate_score"] == 1.0
    assert delta["overall"]["candidate_full_score"] == 0.5
    assert delta["overall"]["delta"] == 0.5
    assert "Paper & Ink" in delta["baseline_missing_presets"]
    assert "Paper & Ink: newly covered passing case" in delta["new_coverage"]
    assert "baseline score missing" not in delta["non_comparable_metrics"]


def test_missing_baseline_does_not_claim_improvement_or_regression():
    candidate = {
        "git_head": "new-sha",
        "cases": [_case("Swiss Modern", passed=True, score=1.0, strict=True, status="native")],
    }

    delta = compare_reports(baseline=None, candidate=candidate, manifest="evals/preset-surface-all/manifest.json")
    summary = _markdown_summary(delta)

    assert delta["baseline_status"] == "missing"
    assert delta["overall"]["baseline_score"] is None
    assert delta["overall"]["delta"] is None
    assert delta["overall"]["candidate_full_score"] == 1.0
    assert delta["comparable_preset_count"] == 0
    assert delta["fixed_failures"] == []
    assert delta["new_failures"] == []
    assert delta["new_coverage"] == []
    assert delta["by_preset"]["Swiss Modern"]["delta"] is None
    assert delta["by_preset"]["Swiss Modern"]["generation_status_delta"] is None
    assert "does not claim improvement or regression" in summary
