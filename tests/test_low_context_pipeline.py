from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from low_context import (  # noqa: E402
    _balance_title_lines,
    _has_collapsed_middle_line,
    _is_orphan_title_line,
    _title_visual_units,
    BriefExtractionError,
    build_render_packet,
    build_slide_spec,
    compile_style_contract,
    extract_brief_from_context,
    extract_brief_from_source_text,
    load_brief,
)


VALIDATE_BRIEF = SCRIPTS / "validate-brief.py"
RENDER_FROM_BRIEF = SCRIPTS / "render-from-brief.py"
STRICT_VALIDATE = ROOT / "tests" / "validate.py"
AUTO_DEMO = ROOT / "demos" / "mode-paths" / "auto-BRIEF.json"
POLISH_DEMO = ROOT / "demos" / "mode-paths" / "polish-BRIEF.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def test_validate_brief_cli_rejects_polish_without_polish_controls(tmp_path: Path):
    brief = read_json(POLISH_DEMO)
    brief.pop("polish_controls")
    path = tmp_path / "invalid-polish.json"
    write_json(path, brief)

    result = subprocess.run(
        [sys.executable, str(VALIDATE_BRIEF), str(path)],
        capture_output=True,
        text=True,
        timeout=15,
    )

    assert result.returncode == 1
    assert "polish_controls is required" in result.stdout


def test_extract_brief_from_noisy_context_preserves_render_packet():
    brief_text = POLISH_DEMO.read_text(encoding="utf-8")

    clean = f"```json\n{brief_text}\n```"
    noisy = (
        "Earlier we discussed unrelated rollout details, budget noise, and style debate.\n\n"
        "Keep the render boundary hard. Only this artifact should drive the deck.\n\n"
        f"```json\n{brief_text}\n```\n\n"
        "Ignore everything else."
    )

    direct_brief = extract_brief_from_context(clean)
    noisy_brief = extract_brief_from_context(noisy)

    assert direct_brief == noisy_brief

    direct_packet = build_render_packet(direct_brief)
    noisy_packet = build_render_packet(noisy_brief)

    assert direct_packet == noisy_packet
    assert direct_packet["runtime_path"] == "shared-js-engine"
    assert direct_packet["composition_source"] == "references/composition-guide.md"


def test_extract_brief_from_conflicting_context_fails_closed():
    auto_text = AUTO_DEMO.read_text(encoding="utf-8")
    polish_text = POLISH_DEMO.read_text(encoding="utf-8")
    context = (
        "These two artifacts conflict. Do not guess.\n\n"
        f"```json\n{auto_text}\n```\n\n"
        f"```json\n{polish_text}\n```"
    )

    try:
        extract_brief_from_context(context)
    except BriefExtractionError as exc:
        assert "Multiple conflicting BRIEF artifacts" in str(exc)
    else:
        raise AssertionError("expected conflicting BRIEF extraction to fail closed")


def test_extract_brief_from_messages_json_source():
    brief_text = POLISH_DEMO.read_text(encoding="utf-8")
    source = json.dumps(
        {
            "messages": [
                {"role": "user", "content": "Ignore the noise."},
                {"role": "user", "content": f"```json\n{brief_text}\n```"},
            ]
        },
        ensure_ascii=False,
    )

    extracted = extract_brief_from_source_text(source)
    assert extracted == read_json(POLISH_DEMO)


def test_compile_style_contract_swiss_modern_collects_canonical_export_contract():
    contract = compile_style_contract("Swiss Modern")

    assert contract["preset"] == "Swiss Modern"
    assert contract["source_path"] == "references/swiss-modern.md"
    assert "--bg" in contract["tokens"]
    assert "--red" in contract["tokens"]
    assert "title_grid" in contract["allowed_layout_ids"]
    assert "geometric_diagram" in contract["allowed_layout_ids"]
    assert ".bg-num" in contract["required_signature_classes"]
    assert ".left-panel" in contract["required_signature_classes"]
    assert "--bg-primary" in contract["forbidden_aliases"]


def test_compile_style_contract_glassmorphism_collects_orb_background_layers():
    contract = compile_style_contract("Glassmorphism")

    assert contract["preset"] == "Glassmorphism"
    assert contract["source_path"] == "references/glassmorphism.md"
    assert "--glass-bg" in contract["tokens"]
    assert "glass_hero" in contract["allowed_layout_ids"]
    assert ".glass-card" in contract["required_signature_classes"]
    assert ".orb-1" in contract["required_signature_classes"]
    assert ".glass-orb" in contract["required_background_layers"]


def test_build_render_packet_blue_sky_uses_starter_path():
    brief = load_brief(AUTO_DEMO)
    packet = build_render_packet(brief)

    assert packet["preset"] == "Blue Sky"
    assert packet["runtime_path"] == "blue-sky-starter"
    assert "references/blue-sky-starter.html" in packet["required_refs"]
    assert "blue-sky-architecture" in packet["required_contracts"]


def test_sparse_brief_degrades_to_tier2_and_uses_canonical_slide_spec():
    brief = read_json(AUTO_DEMO)
    brief["style"]["preset"] = "Swiss Modern"
    brief["style"]["tone"] = "Minimal"
    brief["style"]["visual_density"] = "low"
    brief["title"] = "Sparse deck"
    brief["content"]["must_include"] = ["agent control"]
    brief["content"]["must_avoid"] = ["noise"]
    brief["narrative"]["thesis"] = "Agent control matters."
    for slide in brief["narrative"]["slides"]:
        slide["key_point"] = "Control first"
        slide["visual"] = "grid"

    packet = build_render_packet(brief)
    specs = build_slide_spec(brief, packet)

    assert packet["quality_tier"] == "tier2"
    assert packet["fallback_policy"] == "deterministic-scaffolds-before-fail"
    assert all(spec["quality_tier"] == "tier2" for spec in specs)
    assert all(len(spec["supporting_items"]) == 1 for spec in specs)
    assert all(spec["layout_id"] in {"title_grid", "column_content", "contents_index", "pull_quote"} for spec in specs)


def test_balance_title_lines_produces_no_orphans_or_collapsed_middle_line():
    lines = _balance_title_lines("越早把 AI 做成内核, 越早锁定下一轮壁垒")

    assert 2 <= len(lines) <= 3
    assert not any(_is_orphan_title_line(line) for line in lines)
    assert not _has_collapsed_middle_line([_title_visual_units(line) for line in lines])


def test_render_from_brief_cli_outputs_strict_valid_swiss_html(tmp_path: Path):
    brief = read_json(POLISH_DEMO)
    brief["style"]["preset"] = "Swiss Modern"
    brief["style"]["tone"] = "Precise, assertive, structured"
    brief["title"] = "Visible Control Wins"
    brief["language"] = "en"
    brief["audience"] = "Engineering and product leaders"
    brief["desired_action"] = "Adopt visible-control collaboration patterns"
    brief["narrative"]["thesis"] = "Visible control makes team-grade agent collaboration trustworthy."
    for slide in brief["narrative"]["slides"]:
        slide["visual"] = "structured swiss modern evidence layout"

    brief_path = tmp_path / "swiss-brief.json"
    output_path = tmp_path / "swiss-output.html"
    packet_path = tmp_path / "packet.json"
    write_json(brief_path, brief)

    render = subprocess.run(
        [
            sys.executable,
            str(RENDER_FROM_BRIEF),
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

    assert render.returncode == 0, render.stdout + render.stderr
    assert output_path.exists()
    packet = read_json(packet_path)
    assert packet["preset"] == "Swiss Modern"
    assert packet["runtime_path"] == "shared-js-engine"
    assert packet["quality_tier"] == "tier0"

    validate = subprocess.run(
        [sys.executable, str(STRICT_VALIDATE), str(output_path), "--strict"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert validate.returncode == 0, validate.stdout + validate.stderr
    assert "All strict checks passed" in validate.stdout


def test_render_cli_keeps_file_backed_and_context_extracted_outputs_identical(tmp_path: Path):
    brief = read_json(POLISH_DEMO)
    brief["style"]["preset"] = "Swiss Modern"
    brief["style"]["tone"] = "Precise, assertive, structured"
    brief["title"] = "Visible Control Wins"
    brief["language"] = "en"
    brief["audience"] = "Engineering and product leaders"
    brief["desired_action"] = "Adopt visible-control collaboration patterns"
    brief["narrative"]["thesis"] = "Visible control makes team-grade agent collaboration trustworthy."
    for slide in brief["narrative"]["slides"]:
        slide["visual"] = "structured swiss modern evidence layout"

    brief_path = tmp_path / "source-brief.json"
    direct_html = tmp_path / "direct.html"
    context_html = tmp_path / "context.html"
    direct_packet = tmp_path / "direct-packet.json"
    context_packet = tmp_path / "context-packet.json"
    extracted_brief = tmp_path / "extracted-brief.json"
    context_file = tmp_path / "context.json"
    write_json(brief_path, brief)
    context_file.write_text(
        json.dumps(
            {
                "messages": [
                    {"role": "user", "content": "We discussed many noisy org details first."},
                    {"role": "user", "content": f"```json\n{json.dumps(brief, ensure_ascii=False, indent=2)}\n```"},
                ]
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    direct = subprocess.run(
        [
            sys.executable,
            str(RENDER_FROM_BRIEF),
            str(brief_path),
            "--output",
            str(direct_html),
            "--packet-out",
            str(direct_packet),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    extracted = subprocess.run(
        [
            sys.executable,
            str(RENDER_FROM_BRIEF),
            "--context-file",
            str(context_file),
            "--extract-brief-out",
            str(extracted_brief),
            "--output",
            str(context_html),
            "--packet-out",
            str(context_packet),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert direct.returncode == 0, direct.stdout + direct.stderr
    assert extracted.returncode == 0, extracted.stdout + extracted.stderr
    assert direct_html.read_text(encoding="utf-8") == context_html.read_text(encoding="utf-8")
    assert read_json(direct_packet) == read_json(context_packet)
    assert read_json(extracted_brief) == brief


def test_render_cli_context_without_valid_brief_fails_closed(tmp_path: Path):
    context_file = tmp_path / "bad-context.txt"
    context_file.write_text("This is noisy context with no parseable BRIEF artifact.", encoding="utf-8")
    output_path = tmp_path / "bad.html"

    result = subprocess.run(
        [
            sys.executable,
            str(RENDER_FROM_BRIEF),
            "--context-file",
            str(context_file),
            "--output",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 1
    assert "BRIEF ERROR" in result.stdout
    assert not output_path.exists()
