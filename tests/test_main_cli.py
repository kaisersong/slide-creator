from __future__ import annotations

import json
import importlib.util
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "main.py"
WRAPPER = ROOT / "slide-creator"
POLISH_DEMO = ROOT / "demos" / "mode-paths" / "polish-BRIEF.json"

SPEC = importlib.util.spec_from_file_location("slide_creator_main", MAIN)
assert SPEC and SPEC.loader
main_cli = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(main_cli)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def test_main_cli_validate_brief_accepts_valid_artifact():
    result = subprocess.run(
        [sys.executable, str(MAIN), "--validate-brief", "--brief", str(POLISH_DEMO)],
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert result.returncode == 0
    assert "VALID: polish-BRIEF.json" in result.stdout


def test_main_cli_generate_renders_html_from_brief(tmp_path: Path):
    brief = read_json(POLISH_DEMO)
    brief["style"]["preset"] = "Swiss Modern"
    brief["language"] = "en"
    brief["title"] = "Sandbox-safe render"
    brief["audience"] = "Operators"
    brief["desired_action"] = "Validate the CLI entrypoint"
    brief["narrative"]["thesis"] = "A real CLI entrypoint prevents sandbox misuse."
    for slide in brief["narrative"]["slides"]:
        slide["visual"] = "structured swiss modern evidence layout"

    brief_path = tmp_path / "brief.json"
    output_path = tmp_path / "deck.html"
    packet_path = tmp_path / "packet.json"
    write_json(brief_path, brief)

    result = subprocess.run(
        [
            sys.executable,
            str(MAIN),
            "--generate",
            "--brief",
            str(brief_path),
            "--output",
            str(output_path),
            "--packet-out",
            str(packet_path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert output_path.exists()
    assert packet_path.exists()
    assert "RENDERED:" in result.stdout
    assert 'data-preset="Swiss Modern"' in output_path.read_text(encoding="utf-8")


def test_main_cli_plan_explains_host_skill_boundary():
    result = subprocess.run(
        [sys.executable, str(MAIN), "--plan", "金蝶智能助手小K详细介绍"],
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert result.returncode == 2
    assert "slash-skill step" in result.stdout
    assert "references/brief-template.json" in result.stdout
    assert "python3 main.py --generate" in result.stdout


def test_shell_wrapper_forwards_to_main_help():
    os.chmod(WRAPPER, 0o755)
    result = subprocess.run(
        [str(WRAPPER), "--help"],
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert result.returncode == 0
    assert "Sandbox-friendly CLI" in result.stdout


def test_main_run_generate_refuses_to_write_invalid_render(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(main_cli, "load_brief", lambda _path: {"style": {"preset": "Chinese Chan"}})

    bad_html = """
    <!doctype html>
    <html>
      <body data-preset="Chinese Chan">
        <section class="slide" id="slide-1"></section>
      </body>
    </html>
    """
    monkeypatch.setattr(
        main_cli,
        "render_from_brief",
        lambda _brief: (
            bad_html,
            {"preset": "Chinese Chan", "quality_tier": "tier0", "runtime_path": "shared-js-engine"},
            {},
        ),
    )

    output_path = tmp_path / "invalid-deck.html"
    result = main_cli.run_generate(
        brief_path=tmp_path / "brief.json",
        context_file=None,
        output=output_path,
        packet_out=None,
        extract_brief_out=None,
    )

    assert result == 1
    assert not output_path.exists()
