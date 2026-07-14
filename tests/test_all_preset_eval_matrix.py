from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "evals" / "preset-surface-all" / "manifest.json"
RUN_EVALS = ROOT / "scripts" / "run_evals.py"
GENERATE_MATRIX = ROOT / "scripts" / "generate_preset_eval_matrix.py"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from preset_capabilities import CANONICAL_PRESET_NAMES  # noqa: E402
from low_context import render_from_brief  # noqa: E402


def _run_evals(manifest: Path, output_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(RUN_EVALS),
            str(manifest),
            "--output-dir",
            str(output_dir),
            "--report-path",
            str(output_dir / "report.json"),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )


def _single_case_manifest(tmp_path: Path, case_id: str) -> tuple[Path, dict]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    case = next(case for case in manifest["cases"] if case["case_id"] == case_id)
    case["brief_path"] = str(ROOT / "evals" / "preset-surface-phase1" / "cases" / "core-swiss-modern-brief.json")
    manifest["cases"] = [case]
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return path, manifest


def _minimal_only_manifest(tmp_path: Path) -> Path:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["cases"] = [case for case in manifest["cases"] if case["input_shape"] == "minimal"]
    for case in manifest["cases"]:
        case["brief_path"] = str((MANIFEST.parent / case["brief_path"]).resolve())
        case["run_contract"] = False
        case["run_browser_geometry"] = False
        case["run_mobile_geometry"] = False
    path = tmp_path / "minimal-manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def test_eval_matrix_is_registry_complete_and_reproducible():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    canonical_presets = set(CANONICAL_PRESET_NAMES.values())
    expected_shapes = {"minimal", "representative-12-role", "image-heavy-restyle"}

    assert len(manifest["cases"]) == len(canonical_presets) * len(expected_shapes)
    for preset in canonical_presets:
        cases = [case for case in manifest["cases"] if case["preset"] == preset]
        assert {case["input_shape"] for case in cases} == expected_shapes
        assert all(case["run_contract"] is True for case in cases)
        assert all(case["run_browser_geometry"] is True for case in cases)
        assert all(case["run_mobile_geometry"] is True for case in cases)

    result = subprocess.run(
        [sys.executable, str(GENERATE_MATRIX), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_representative_native_render_sanitizes_pictorial_emoji():
    brief = json.loads(
        (MANIFEST.parent / "cases" / "representative-12-role-brief.json").read_text(encoding="utf-8")
    )
    brief["style"]["preset"] = "Data Story"

    html_text, _packet, _contract = render_from_brief(brief)

    assert "🧭" not in html_text
    assert 'body[data-preset="Data Story"] .ds-comparison .ds-matrix-title' in html_text
    assert "-webkit-line-clamp: unset" in html_text


def test_eval_matrix_enforces_packet_generation_status_strategy_render_path(tmp_path: Path):
    result = _run_evals(_minimal_only_manifest(tmp_path), tmp_path / "all")

    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads((tmp_path / "all" / "report.json").read_text(encoding="utf-8"))
    by_preset = {case["packet"]["canonical_preset"]: case for case in report["cases"]}
    assert set(by_preset) == set(CANONICAL_PRESET_NAMES.values())

    terminal = by_preset["Terminal Green"]
    assert terminal["packet"]["preset_generation_status"] == "profile"
    assert terminal["packet"]["renderer_strategy"] == "unified_profile"
    assert terminal["packet"]["render_path"] == "profile:terminal-green"
    assert terminal["packet"]["reference_path"] == "references/terminal-green.md"
    assert terminal["pass"] is True


def test_eval_matrix_fails_when_expected_packet_fields_are_ignored(tmp_path: Path):
    manifest_path, manifest = _single_case_manifest(tmp_path, "terminal-green-profile-render")
    manifest["cases"][0]["expectations"]["expected_renderer_strategy"] = "native"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    output_dir = tmp_path / "bad-strategy"
    result = _run_evals(manifest_path, output_dir)

    assert result.returncode != 0
    report = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
    assert "expected_renderer_strategy" in report["cases"][0]["expectations"]["failures"]


def test_eval_matrix_fails_on_unknown_expected_keys(tmp_path: Path):
    manifest_path, manifest = _single_case_manifest(tmp_path, "terminal-green-profile-render")
    manifest["cases"][0]["expectations"]["expected_profile_magic"] = "nope"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    output_dir = tmp_path / "unknown-key"
    result = _run_evals(manifest_path, output_dir)

    assert result.returncode != 0
    report = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
    assert "unknown_expectation:expected_profile_magic" in report["cases"][0]["expectations"]["failures"]
