from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SUITE_DIR = ROOT / "evals" / "preset-surface-phase1"
MANIFEST = SUITE_DIR / "manifest.json"
README = SUITE_DIR / "README.md"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase1_suite_covers_core_three_plus_blue_sky_and_paper_ink_support():
    manifest = read_json(MANIFEST)
    cases = {case["case_id"]: case for case in manifest["cases"]}

    assert {
        "core-enterprise-dark-render",
        "core-swiss-modern-render",
        "core-data-story-render",
        "support-blue-sky-fixture",
        "support-paper-ink-fixture",
    } <= set(cases)

    paper_ink = cases["support-paper-ink-fixture"]
    assert paper_ink["validation_profile"] == "strict"
    assert paper_ink["preset"] == "Paper & Ink"
    assert paper_ink["expectations"]["expected_support_tier"] == "supported"
    assert set(paper_ink["expectations"]["required_quality_gates"]) == {
        "chrome-hidden-by-default",
        "no-content-occlusion-risk",
    }
    assert paper_ink["expectations"]["required_title_gates"] == ["browser-title-composition"]

    for case in cases.values():
        assert case["expectations"]["required_title_gates"] == ["browser-title-composition"]


def test_phase1_readme_documents_release_gate_wrapper_and_paper_ink_fixture():
    readme = read_text(README)

    assert "support-paper-ink-fixture" in readme
    assert "python3 scripts/preset_release_gate.py" in readme
    assert "`Paper & Ink` is now back in the green support-surface suite" in readme
    assert "browser-title-composition" in readme
    assert "auto-enables browser title QA" in readme
