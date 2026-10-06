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
    rendered = output_path.read_text(encoding="utf-8")
    assert 'data-preset="Swiss Modern"' in rendered
    assert 'data-generator="kai-slide-creator"' in rendered
    assert 'data-render-path="brief-canonical"' in rendered
    assert 'data-validate-strict="pass"' in rendered


def test_main_cli_generate_can_write_single_deck_eval_report(tmp_path: Path):
    brief = read_json(POLISH_DEMO)
    brief["style"]["preset"] = "Data Story"
    brief["title"] = "Single Deck Eval"
    brief["audience"] = "Operators"
    brief["desired_action"] = "Verify eval wiring"

    brief_path = tmp_path / "brief.json"
    output_path = tmp_path / "deck.html"
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
            "--eval",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    eval_path = tmp_path / "deck.eval.json"
    assert result.returncode == 0, result.stdout + result.stderr
    assert eval_path.exists()
    report = read_json(eval_path)
    assert report["preset"] == "Data Story"
    assert report["render_packet"]["preset"] == "Data Story"
    assert "style_score" in report["summary"]
    assert "quality_gates_passed" in report["summary"]
    assert "EVAL:" in result.stdout
    assert "STYLE SCORE:" in result.stdout


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


def test_main_run_generate_refuses_missing_canonical_provenance(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(main_cli, "load_brief", lambda _path: {"style": {"preset": "Swiss Modern"}})

    html_without_provenance = """
    <!doctype html>
    <html>
      <body data-preset="Swiss Modern">
        <section class="slide" id="slide-1" data-export-role="cta_close" data-notes="x"></section>
      </body>
    </html>
    """
    monkeypatch.setattr(
        main_cli,
        "render_from_brief",
        lambda _brief: (
            html_without_provenance,
            {"preset": "Swiss Modern", "quality_tier": "tier0", "runtime_path": "shared-js-engine"},
            {},
        ),
    )

    output_path = tmp_path / "invalid-provenance.html"
    result = main_cli.run_generate(
        brief_path=tmp_path / "brief.json",
        context_file=None,
        output=output_path,
        packet_out=None,
        extract_brief_out=None,
    )

    assert result == 1
    assert not output_path.exists()


def _run_requested_style(tmp_path, *arguments, context=False):
    brief = read_json(POLISH_DEMO)
    brief['style']['preset'] = 'Swiss Modern'
    source = tmp_path / 'brief.json'
    write_json(source, brief)
    if context:
        source.write_text('Source artifact\n```json\n' + json.dumps(brief) + '\n```\n')
    return subprocess.run(
        [sys.executable, str(MAIN), '--generate',
         '--context-file' if context else '--brief', str(source),
         '--output', str(tmp_path / 'deck.html'), *arguments],
        cwd=tmp_path, capture_output=True, text=True, timeout=30,
    )


def test_requested_style_rejects_wrong_brief_before_overwriting_artifacts(tmp_path):
    output = tmp_path / 'deck.html'
    output.write_text('previous completed deck')
    packet = tmp_path / 'packet.json'
    packet.write_text('previous packet')
    result = _run_requested_style(tmp_path, '--requested-preset', 'Strategy Consulting',
                                  '--packet-out', str(packet))
    assert result.returncode == 1
    assert 'PRESET MISMATCH' in result.stdout
    assert 'Strategy Consulting' in result.stdout and 'Swiss Modern' in result.stdout
    assert output.read_text() == 'previous completed deck'
    assert packet.read_text() == 'previous packet'


def test_request_file_cannot_be_bypassed_by_omitting_flag_or_conflicting_override(tmp_path):
    request = {'version': 1, 'preset': 'Strategy Consulting'}
    write_json(tmp_path / 'SLIDE_REQUEST.json', request)
    before = (tmp_path / 'SLIDE_REQUEST.json').read_bytes()
    for arguments in [(), ('--requested-preset', 'Swiss Modern')]:
        result = _run_requested_style(tmp_path, *arguments)
        assert result.returncode == 1
        assert not (tmp_path / 'deck.html').exists()
        assert (tmp_path / 'SLIDE_REQUEST.json').read_bytes() == before


def test_context_artifact_has_the_same_user_preset_guard(tmp_path):
    result = _run_requested_style(tmp_path, '--requested-preset', 'Strategy Consulting', context=True)
    assert result.returncode == 1
    assert 'PRESET MISMATCH' in result.stdout
    assert not (tmp_path / 'deck.html').exists()


def test_requested_style_alias_is_accepted_and_retains_brief_provenance(tmp_path):
    write_json(tmp_path / 'SLIDE_REQUEST.json', {'version': 1, 'preset': 'swiss-modern'})
    result = _run_requested_style(tmp_path, '--requested-preset', 'Swiss Modern')
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'data-preset="Swiss Modern"' in (tmp_path / 'deck.html').read_text()
    assert read_json(tmp_path / 'brief.json')['style']['preset'] == 'Swiss Modern'


def test_custom_style_identity_accepts_alias_and_reference_path(tmp_path):
    reference = ROOT / 'themes/fantasy-rainbow/reference.md'
    for requested in ['Fantasy Rainbow', 'custom:fantasy-rainbow', str(reference)]:
        main_cli.assert_requested_preset({'style': {'preset': 'fantasy-rainbow'}}, requested)


def test_invalid_or_missing_request_fails_without_output(tmp_path):
    for data in ['{', '{}', '{"version":true,"preset":"Swiss Modern"}',
                 '{"version":1,"preset":""}', '{"version":1,"preset":7}',
                 '{"version":1,"preset":"nonexistent-preset"}']:
        (tmp_path / 'SLIDE_REQUEST.json').write_text(data)
        result = _run_requested_style(tmp_path)
        assert result.returncode == 1, result.stdout + result.stderr
        assert not (tmp_path / 'deck.html').exists()
    (tmp_path / 'SLIDE_REQUEST.json').unlink()
    result = _run_requested_style(tmp_path, '--request-file', 'missing.json')
    assert result.returncode == 1
    assert not (tmp_path / 'deck.html').exists()


def test_explicit_request_file_outside_working_directory_is_checked(tmp_path):
    request = tmp_path / 'inputs/request.json'
    request.parent.mkdir()
    write_json(request, {'version': 1, 'preset': 'Strategy Consulting'})
    result = _run_requested_style(tmp_path, '--request-file', str(request))
    assert result.returncode == 1
    assert 'PRESET MISMATCH' in result.stdout
