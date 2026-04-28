from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BRIEF_TEMPLATE = ROOT / "references" / "brief-template.json"
BRIEF_SCHEMA = ROOT / "schemas" / "generation-brief.schema.json"
SCORING_SCHEMA = ROOT / "evals" / "scoring-schema.json"
FAILURE_MAP = ROOT / "evals" / "failure-map.md"
LATE_CONTEXT = ROOT / "evals" / "late-context"
VALIDATE_BRIEF = ROOT / "scripts" / "validate-brief.py"
GENERATED_DECK_EVAL = (
    ROOT / "evals" / "generated-decks" / "2026-04-21-slide-creator-intro" / "eval-results.json"
)
CORE_MD_CASES = {
    "lc-004-core-runtime-guard",
    "lc-005-preset-metadata-bypass",
    "lc-006-blue-sky-runtime-control",
    "lc-007-style-signature-near-limit",
}
LOW_CONTEXT_SAFE_CASES = {
    "lc-008-same-brief-parity-control",
    "lc-009-same-brief-parity-noisy-wrapper",
    "lc-010-sparse-brief-fallback",
    "lc-011-invalid-brief-fail-closed",
    "lc-012-high-context-rich-benchmark",
}
QUALITY_UPLIFT_CASES = {
    "lc-013-default-chrome-leak-regression",
    "lc-014-data-story-numeric-fidelity",
    "lc-015-high-context-richness-non-regression",
}
TITLE_COMPOSITION_CASES = {
    "lc-016-title-balance-negative-fixture",
    "lc-017-structural-preset-title-control",
    "lc-018-mixed-language-title-balance",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def test_ir_first_assets_exist():
    assert BRIEF_TEMPLATE.exists()
    assert BRIEF_SCHEMA.exists()
    assert SCORING_SCHEMA.exists()
    assert FAILURE_MAP.exists()
    assert (LATE_CONTEXT / "manifest.json").exists()
    assert VALIDATE_BRIEF.exists()


def test_brief_schema_lists_required_quality_fields():
    schema = read_json(BRIEF_SCHEMA)
    required = set(schema["required"])
    assert {
        "schema_version",
        "mode",
        "language",
        "deck",
        "style",
        "content",
        "narrative",
        "runtime",
        "plan_view",
        "timing",
    } <= required


def test_scoring_schema_covers_four_layers():
    schema = read_json(SCORING_SCHEMA)
    properties = schema["properties"]["scores"]["properties"]
    assert set(properties) == {"route", "compression", "render", "efficiency"}


def test_scoring_schema_allows_optional_low_context_diagnostics():
    schema = read_json(SCORING_SCHEMA)
    diagnostics = schema["properties"]["diagnostics"]["properties"]["low_context"]["properties"]
    assert {
        "quality_tier",
        "strict_pass_first_try",
        "repair_rounds",
        "route_drift",
        "layout_variety",
        "avg_component_kinds_per_slide",
        "style_signature_coverage",
        "chrome_leak",
        "content_occlusion_risk",
        "numeric_faithfulness",
        "source_fact_coverage",
        "chart_signal_mismatch_count",
        "chart_signal_mismatch_rate",
        "global_fact_overuse_count",
        "narrative_role_coverage",
        "minimal_slide_ratio",
        "max_minimal_slide_run",
        "browser_title_target_count",
        "title_hard_fail_rate",
        "orphan_line_rate",
        "collapsed_middle_line_rate",
        "profile_mismatch_rate",
        "structural_preset_break_rate",
        "title_clipping_rate",
        "title_occlusion_rate",
        "latency_ms",
    } <= set(diagnostics)


def test_failure_map_points_to_fix_locations():
    content = read_text(FAILURE_MAP)
    assert "Route failure" in content
    assert "Compression failure" in content
    assert "Render failure" in content
    assert "Efficiency failure" in content
    assert "SKILL.md" in content
    assert "references/workflow.md" in content
    assert "references/html-template.md" in content


def test_late_context_cases_have_expected_shape():
    manifest = read_json(LATE_CONTEXT / "manifest.json")
    assert len(manifest["cases"]) >= 3
    for case_id in manifest["cases"]:
        case_dir = LATE_CONTEXT / "cases" / case_id
        assert (case_dir / "context.json").exists(), case_id
        assert (case_dir / "expected-brief.json").exists(), case_id
        assert (case_dir / "expectations.json").exists(), case_id


def test_late_context_manifest_includes_core_md_guard_cases():
    manifest = read_json(LATE_CONTEXT / "manifest.json")
    assert CORE_MD_CASES <= set(manifest["cases"])


def test_late_context_manifest_includes_low_context_safe_cases():
    manifest = read_json(LATE_CONTEXT / "manifest.json")
    assert LOW_CONTEXT_SAFE_CASES <= set(manifest["cases"])


def test_late_context_manifest_includes_quality_uplift_cases():
    manifest = read_json(LATE_CONTEXT / "manifest.json")
    assert QUALITY_UPLIFT_CASES <= set(manifest["cases"])


def test_late_context_manifest_includes_title_composition_cases():
    manifest = read_json(LATE_CONTEXT / "manifest.json")
    assert TITLE_COMPOSITION_CASES <= set(manifest["cases"])


def test_core_md_guard_cases_define_runtime_expectations():
    for case_id in CORE_MD_CASES:
        expectations = read_json(LATE_CONTEXT / "cases" / case_id / "expectations.json")
        required_html_checks = set(expectations.get("required_html_checks", []))
        assert "preset-metadata" in required_html_checks, case_id
        if case_id == "lc-006-blue-sky-runtime-control":
            assert "blue-sky-architecture" in required_html_checks
            assert "shared-runtime" not in required_html_checks
        else:
            assert "shared-runtime" in required_html_checks, case_id


def test_low_context_safe_cases_define_protocol_expectations():
    parity_cases = {
        "lc-008-same-brief-parity-control",
        "lc-009-same-brief-parity-noisy-wrapper",
    }
    for case_id in LOW_CONTEXT_SAFE_CASES:
        expectations = read_json(LATE_CONTEXT / "cases" / case_id / "expectations.json")
        if case_id in parity_cases:
            assert expectations["parity_group"] == "same-brief-swiss-modern-001"
            assert expectations["parity_role"] in {"control", "noisy-wrapper"}
            assert "style.preset" in expectations["compare_brief_fields"]
            assert "shared-runtime" in expectations["compare_html_checks"]
            assert expectations["expected_quality_tier"] == "tier0"
        elif case_id == "lc-010-sparse-brief-fallback":
            assert set(expectations["allowed_quality_tiers"]) == {"tier1", "tier2"}
            assert "present-mode" in expectations["required_html_checks"]
        elif case_id == "lc-011-invalid-brief-fail-closed":
            assert expectations["artifact_status"] == "invalid"
            assert expectations["should_fail_closed"] is True
            assert expectations["expected_error_layer"] == "compression"
        elif case_id == "lc-012-high-context-rich-benchmark":
            assert expectations["expected_quality_tier"] == "tier0"
            assert expectations["rich_context_benchmark"] is True
            assert set(expectations["non_regression_metrics"]) == {
                "layout-variety",
                "component-diversity",
                "style-signature-coverage",
            }


def test_quality_uplift_cases_define_quality_gate_expectations():
    for case_id in QUALITY_UPLIFT_CASES:
        expectations = read_json(LATE_CONTEXT / "cases" / case_id / "expectations.json")
        assert expectations["should_trigger"] is True
        assert expectations["expected_skill"] == "slide-creator"
        assert expectations["expected_mode"] == "polish"
        assert expectations["required_quality_gates"]
        assert "quality_thresholds" in expectations

        if case_id == "lc-013-default-chrome-leak-regression":
            assert set(expectations["required_quality_gates"]) == {
                "chrome-hidden-by-default",
                "no-content-occlusion-risk",
            }
            assert expectations["quality_thresholds"] == {
                "chrome_leak": False,
                "content_occlusion_risk": False,
            }
        elif case_id == "lc-014-data-story-numeric-fidelity":
            assert set(expectations["required_quality_gates"]) == {
                "numeric-faithfulness",
                "source-fact-coverage",
            }
            assert expectations["quality_thresholds"]["numeric_faithfulness_min"] == 0.95
            assert expectations["quality_thresholds"]["source_fact_coverage_min"] == 0.75
        elif case_id == "lc-015-high-context-richness-non-regression":
            assert expectations["rich_context_benchmark"] is True
            assert set(expectations["non_regression_metrics"]) == {
                "layout-variety",
                "component-diversity",
                "style-signature-coverage",
                "minimal-slide-ratio",
            }
            assert expectations["quality_thresholds"]["narrative_role_coverage"] == 1.0
            assert expectations["quality_thresholds"]["max_minimal_slide_run"] == 2
            assert expectations["quality_thresholds"]["minimal_slide_ratio_max_delta"] == 0.1


def test_title_composition_cases_define_browser_title_expectations():
    for case_id in TITLE_COMPOSITION_CASES:
        expectations = read_json(LATE_CONTEXT / "cases" / case_id / "expectations.json")
        assert expectations["should_trigger"] is True
        assert expectations["expected_skill"] == "slide-creator"
        assert expectations["required_title_gates"] == ["browser-title-composition"]
        assert "quality_thresholds" in expectations

        if case_id == "lc-016-title-balance-negative-fixture":
            assert expectations["eval_bucket"] == "negative-fixtures"
            assert expectations["quality_thresholds"] == {
                "title_hard_fail_rate_max": 0.0,
                "orphan_line_rate_max": 0.0,
                "title_clipping_rate_max": 0.0,
            }
        elif case_id == "lc-017-structural-preset-title-control":
            assert expectations["eval_bucket"] == "structural-preset-control"
            assert expectations["expected_title_profiles"] == ["split_lockup"]
            assert expectations["quality_thresholds"] == {
                "profile_mismatch_rate_max": 0.0,
                "structural_preset_break_rate_max": 0.0,
            }
        elif case_id == "lc-018-mixed-language-title-balance":
            assert expectations["eval_bucket"] == "same-preset-different-language"
            assert expectations["quality_thresholds"] == {
                "title_hard_fail_rate_max": 0.0,
                "orphan_line_rate_max": 0.0,
                "collapsed_middle_line_rate_max": 0.0,
                "profile_mismatch_rate_max": 0.0,
            }


def test_generated_deck_eval_results_include_low_context_diagnostics_examples():
    report = read_json(GENERATED_DECK_EVAL)
    assert report["cases"], "expected at least one benchmark case"
    for case in report["cases"]:
        diagnostics = case["diagnostics"]["low_context"]
        assert diagnostics["quality_tier"] == "tier0"
        assert diagnostics["strict_pass_first_try"] is True
        assert diagnostics["repair_rounds"] == 0
        assert diagnostics["route_drift"] is False
        assert diagnostics["layout_variety"] > 0
        assert diagnostics["avg_component_kinds_per_slide"] >= 2
        assert diagnostics["style_signature_coverage"] > 0
        assert diagnostics["chrome_leak"] is False
        assert diagnostics["content_occlusion_risk"] is False
        assert diagnostics["numeric_faithfulness"] >= 0.95
        assert diagnostics["source_fact_coverage"] >= 0.67
        assert diagnostics["narrative_role_coverage"] == 1.0
        assert diagnostics["minimal_slide_ratio"] <= 0.4
        assert diagnostics["max_minimal_slide_run"] <= 2


def test_brief_validator_accepts_template():
    result = subprocess.run(
        [sys.executable, str(VALIDATE_BRIEF), str(BRIEF_TEMPLATE)],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "VALID" in result.stdout


def test_brief_validator_accepts_mode_path_examples():
    for path in sorted((ROOT / "demos" / "mode-paths").glob("*BRIEF.json")):
        result = subprocess.run(
            [sys.executable, str(VALIDATE_BRIEF), str(path)],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0, f"{path.name}: {result.stdout}{result.stderr}"
