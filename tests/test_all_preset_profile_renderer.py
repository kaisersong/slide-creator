from __future__ import annotations

import html
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from low_context import render_from_brief  # noqa: E402
from preset_capabilities import CANONICAL_PRESET_NAMES  # noqa: E402
from preset_profile_specs import PROFILE_SPECS  # noqa: E402
from quality_eval import analyze_html_quality  # noqa: E402
from validate_html import validate  # noqa: E402


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _minimal_brief_for_preset(preset: str) -> dict:
    roles = ["cover", "problem", "solution", "workflow", "evidence", "cta_close"]
    slides = [
        {
            "slide_number": index,
            "role": role,
            "title": title,
            "claim": title,
            "key_point": key_point,
            "explanation": key_point,
            "visual": visual,
            "visual_intent": visual,
            "preferred_layout_family": visual,
            "chart_policy": "auto",
            "supporting_facts": facts,
        }
        for index, (role, title, key_point, visual, facts) in enumerate(
            [
                (
                    "cover",
                    "Stable preset output",
                    "Every explicit built-in style keeps its requested identity through rendering.",
                    "hero",
                    ["requested preset", "single renderer shell", "strict validation"],
                ),
                (
                    "problem",
                    "The old boundary was unclear",
                    "Users could pick a style but the product could reject it as not deterministic.",
                    "comparison",
                    ["generation surface", "support promise", "user intent"],
                ),
                (
                    "solution",
                    "Unified profile rendering",
                    "Native core and profile presets share BRIEF, runtime, metadata, and validation.",
                    "three-things",
                    ["native core", "profile branch", "shared runtime"],
                ),
                (
                    "workflow",
                    "Render path stays inspectable",
                    "Packets record generation status, renderer strategy, render path, and reference file.",
                    "timeline",
                    ["capability lookup", "profile payload", "HTML output"],
                ),
                (
                    "evidence",
                    "Validation is the gate",
                    "The output must strict validate before being written by either CLI entrypoint.",
                    "evidence",
                    ["strict validator", "canonical preset", "no substitution"],
                ),
                (
                    "cta_close",
                    "Ship the full preset surface",
                    "The default recommendation surface stays small while explicit styles still render.",
                    "close",
                    ["default shortlist", "contextual option", "explicit style"],
                ),
            ],
            start=1,
        )
    ]
    return {
        "schema_version": 1,
        "brief_id": f"all-preset-profile-{_slugify(preset)}",
        "mode": "auto",
        "language": "en",
        "title": f"{preset} Output Recovery",
        "audience": "slide-creator maintainers",
        "desired_action": "verify every built-in preset can generate",
        "deck": {
            "deck_type": "user-content",
            "page_count": len(slides),
            "output_format": "html-slides",
        },
        "style": {
            "preset": preset,
            "tone": "clear and production-focused",
            "visual_density": "medium",
        },
        "content": {
            "source_policy": "distill-only",
            "must_include": [
                "all built-in presets render",
                "native core remains most stable",
                "profile presets use strict validation",
            ],
            "must_avoid": [
                "preset substitution",
                "claiming equal stability",
                "external worker dependency",
            ],
            "global_facts": [
                "explicit selection must preserve canonical preset",
                "default recommendation surface remains four styles",
                "Chinese Chan is contextual only",
            ],
        },
        "narrative": {
            "thesis": "All built-in presets should generate through one product path while preserving support-tier honesty.",
            "page_roles": roles,
            "slides": slides,
        },
        "runtime": {
            "editing_mode": True,
            "presenter_mode": True,
            "watermark_mode": "injected-last-slide",
            "export_intent": "none",
        },
        "plan_view": {
            "emit_planning_view": False,
            "planning_view_path": "PLANNING.md",
        },
        "timing": {
            "estimate": {"plan": "1m", "generate": "1m", "validate": "1m", "polish": "0m", "total": "3m"},
            "actual": {"plan": "0m", "generate": "0m", "validate": "0m", "polish": "0m", "total": "0m"},
        },
    }


@pytest.mark.parametrize("preset", sorted(CANONICAL_PRESET_NAMES.values()))
def test_builtin_preset_renders_through_product_path(tmp_path: Path, preset: str):
    brief = _minimal_brief_for_preset(preset)
    html_text, packet, _contract = render_from_brief(brief)

    assert packet["canonical_preset"] == preset
    assert packet["render_path"]
    assert "reference_driven_generation_required" not in html_text
    if preset == "Blue Sky":
        assert 'id="stage"' in html_text
        assert 'id="track"' in html_text
    else:
        assert "class SlidePresentation" in html_text
    assert f'data-preset="{html.escape(preset)}"' in html_text or f'data-preset="{preset}"' in html_text

    if packet["renderer_strategy"] == "unified_profile":
        assert packet["preset_generation_status"] == "profile"
        assert packet["render_path"] == f"profile:{_slugify(preset)}"
    else:
        assert packet["renderer_strategy"] == "native"

    out = tmp_path / f"{_slugify(preset)}.html"
    out.write_text(html_text, encoding="utf-8")
    assert validate(out, strict=True) is True


@pytest.mark.parametrize("preset", sorted(CANONICAL_PRESET_NAMES.values()))
def test_main_generate_outputs_each_builtin_preset(tmp_path: Path, preset: str):
    brief_path = tmp_path / f"{_slugify(preset)}.json"
    output_path = tmp_path / f"{_slugify(preset)}.html"
    packet_path = tmp_path / f"{_slugify(preset)}.packet.json"
    brief_path.write_text(json.dumps(_minimal_brief_for_preset(preset), ensure_ascii=False), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "main.py"),
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
        timeout=60,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert output_path.exists()
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    assert packet["canonical_preset"] == preset
    assert packet["renderer_strategy"] in {"native", "unified_profile"}
    assert validate(output_path, strict=True) is True


@pytest.mark.parametrize("preset", sorted(CANONICAL_PRESET_NAMES.values()))
def test_render_from_brief_wrapper_outputs_each_builtin_preset(tmp_path: Path, preset: str):
    brief_path = tmp_path / f"{_slugify(preset)}.json"
    output_path = tmp_path / f"{_slugify(preset)}.wrapper.html"
    packet_path = tmp_path / f"{_slugify(preset)}.wrapper.packet.json"
    eval_path = tmp_path / f"{_slugify(preset)}.wrapper.eval.json"
    brief_path.write_text(json.dumps(_minimal_brief_for_preset(preset), ensure_ascii=False), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "render-from-brief.py"),
            "--context-file",
            str(brief_path),
            "--output",
            str(output_path),
            "--packet-out",
            str(packet_path),
            "--eval-out",
            str(eval_path),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert output_path.exists()
    assert validate(output_path, strict=True) is True
    html_text = output_path.read_text(encoding="utf-8")
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    eval_report = json.loads(eval_path.read_text(encoding="utf-8"))
    assert packet["canonical_preset"] == preset
    assert packet["renderer_strategy"] in {"native", "unified_profile"}
    assert packet["render_path"]
    assert f'data-preset="{html.escape(preset)}"' in html_text or f'data-preset="{preset}"' in html_text
    assert eval_report["render_packet"]["canonical_preset"] == preset
    assert eval_report["render_packet"]["renderer_strategy"] == packet["renderer_strategy"]
    assert eval_report["render_packet"]["render_path"] == packet["render_path"]


@pytest.mark.parametrize("preset", sorted(PROFILE_SPECS))
def test_profile_renderer_emits_visible_signature_components_for_each_profile_preset(preset: str):
    brief = _minimal_brief_for_preset(preset)
    html_text, packet, _contract = render_from_brief(brief)
    spec = PROFILE_SPECS[preset]
    report = analyze_html_quality(html_text, brief=brief, preset=preset)
    diagnostics = report["diagnostics"]

    assert packet["renderer_strategy"] == "unified_profile"
    assert packet["body_data_attrs"]["data-profile-family"] == spec.family
    assert packet["body_data_attrs"]["data-profile-spec"] == _slugify(preset)
    assert diagnostics["style_signature_coverage"] >= 0.5
    assert diagnostics["style_signature_integrity"] == 1.0
    assert diagnostics["ignored_marker_class_count"] == 0
    assert len(diagnostics["visible_signature_hits"]) >= 2


@pytest.mark.parametrize("preset", sorted(PROFILE_SPECS))
def test_profile_renderer_does_not_reuse_signal_shell_for_unrelated_presets(preset: str):
    html_text, _packet, _contract = render_from_brief(_minimal_brief_for_preset(preset))
    historically_purple = {"Aurora Mesh", "Bold Signal", "Creative Voltage", "Electric Studio", "Glassmorphism"}

    if preset not in historically_purple:
        assert "linear-gradient(135deg, #667eea" not in html_text
        assert "profile-signal-grid" not in html_text
