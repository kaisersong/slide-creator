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
