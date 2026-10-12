from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from preset_profile_specs import PROFILE_SPECS


def copy_runtime(destination: Path) -> None:
    destination.mkdir(parents=True)
    for name in ("SKILL.md", "main.py"):
        shutil.copy2(ROOT / name, destination / name)
    for name in ("scripts", "schemas", "references"):
        shutil.copytree(ROOT / name, destination / name,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


@pytest.fixture(scope="module")
def installed_runtime(tmp_path_factory):
    # A surrounding repository must never become the installed renderer's root.
    outer = tmp_path_factory.mktemp("profile-runtime")
    for name in ("demos", "references", "schemas"):
        (outer / name).mkdir()
    runtime = outer / "installed"
    copy_runtime(runtime)
    assert not (runtime / "demos").exists()
    return runtime


def generate(runtime: Path, brief: Path, output: Path):
    return subprocess.run(
        [sys.executable, str(runtime / "main.py"), "--generate", "--brief", str(brief), "--output", str(output)],
        cwd=runtime, capture_output=True, text=True,
    )


@pytest.mark.parametrize("preset", sorted(PROFILE_SPECS))
@pytest.mark.parametrize("language", ("en", "zh"))
def test_installed_profile_matches_source_without_demos(installed_runtime, tmp_path, preset, language):
    brief = json.loads((ROOT / "evals/preset-surface-all/cases/minimal-brief.json").read_text())
    brief["style"]["preset"] = preset
    brief["language"] = language
    path = tmp_path / "brief.json"
    path.write_text(json.dumps(brief, ensure_ascii=False))
    source_output = tmp_path / "source.html"
    installed_output = tmp_path / "installed.html"
    source = generate(ROOT, path, source_output)
    installed = generate(installed_runtime, path, installed_output)
    assert source.returncode == 0, source.stdout + source.stderr
    assert installed.returncode == 0, installed.stdout + installed.stderr
    assert installed_output.read_bytes() == source_output.read_bytes()
    assert 'data-profile-renderer-source="demo-derived:' in installed_output.read_text()


def test_missing_installed_template_preserves_existing_output(installed_runtime, tmp_path):
    brief = json.loads((ROOT / "evals/preset-surface-all/cases/minimal-brief.json").read_text())
    brief["style"]["preset"] = "Aurora Mesh"
    path = tmp_path / "brief.json"
    path.write_text(json.dumps(brief))
    output = tmp_path / "existing.html"
    output.write_text("preserve this artifact")
    templates = [installed_runtime / f"references/profile-templates/aurora-mesh-{language}.html"
                 for language in ("en", "zh")]
    saved = [p.read_bytes() for p in templates]
    try:
        for p in templates:
            p.unlink()
        result = generate(installed_runtime, path, output)
        assert result.returncode != 0
        assert "Runtime profile template missing" in result.stdout + result.stderr
        assert "Traceback" not in result.stdout + result.stderr
        assert output.read_text() == "preserve this artifact"
    finally:
        for p, content in zip(templates, saved):
            p.write_bytes(content)


@pytest.mark.parametrize("corruption", ("missing", "checksum"))
def test_packaging_rejects_incomplete_or_corrupt_profile_assets(tmp_path, corruption):
    runtime = tmp_path / "runtime"
    copy_runtime(runtime)
    subprocess.run(["git", "init", "-q"], cwd=runtime, check=True)
    subprocess.run(["git", "add", "."], cwd=runtime, check=True)
    relative = "references/profile-templates/aurora-mesh-en.html"
    if corruption == "missing":
        subprocess.run(["git", "rm", "--cached", relative], cwd=runtime, check=True, capture_output=True)
    else:
        (runtime / relative).write_text("corrupted template")
        subprocess.run(["git", "add", relative], cwd=runtime, check=True)
    output_dir = tmp_path / "dist"
    result = subprocess.run([sys.executable, str(runtime / "scripts/package-runtime.py"),
                             "--output-dir", str(output_dir)], cwd=runtime, capture_output=True, text=True)
    assert result.returncode != 0
    expected = "template missing from git index" if corruption == "missing" else "template checksum mismatch"
    assert expected in result.stderr
    assert not list(output_dir.glob("*.zip"))
