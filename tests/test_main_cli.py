from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "main.py"
WRAPPER = ROOT / "slide-creator"
POLISH_DEMO = ROOT / "demos" / "mode-paths" / "polish-BRIEF.json"


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
