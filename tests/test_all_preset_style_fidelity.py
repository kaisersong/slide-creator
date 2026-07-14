from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from low_context import render_from_brief  # noqa: E402
from preset_contracts import (  # noqa: E402
    builtin_preset_names,
    requirement_for_preset,
    slug_for_preset,
    validate_preset_fidelity,
)
from preset_profile_specs import PROFILE_SPECS  # noqa: E402
from style_signature_eval import collect_signature_presence  # noqa: E402


BASE_BRIEF = json.loads((ROOT / "demos" / "mode-paths" / "auto-BRIEF.json").read_text(encoding="utf-8"))
GENERIC_SHELL = (ROOT / "tests" / "fixtures" / "style-fidelity" / "generic-shell.html").read_text(encoding="utf-8")
FULL_SLIDE_IMAGE = (ROOT / "tests" / "fixtures" / "style-fidelity" / "full-slide-image.html").read_text(encoding="utf-8")


def _render(preset: str, *, page_count: int = 8) -> str:
    brief = copy.deepcopy(BASE_BRIEF)
    brief["brief_id"] = f"style-fidelity-{slug_for_preset(preset)}-{page_count}"
    brief["style"]["preset"] = preset
    if page_count != 8:
        slides = brief["narrative"]["slides"]
        while len(slides) < page_count:
            source = copy.deepcopy(slides[-2])
            source["slide_number"] = len(slides)
            source["role"] = f"evidence-{len(slides)}"
            source["title"] = f"Evidence {len(slides)}"
            slides.insert(-1, source)
        brief["deck"]["page_count"] = len(slides)
        brief["narrative"]["page_roles"] = [slide["role"] for slide in slides]
        for index, slide in enumerate(slides, start=1):
            slide["slide_number"] = index
    return render_from_brief(brief)[0]


def test_registry_derived_renderer_outputs_pass_and_generic_shells_fail():
    for preset in builtin_preset_names():
        html = _render(preset)
        report = validate_preset_fidelity(html, preset, mode="product")
        generic = validate_preset_fidelity(GENERIC_SHELL, preset, mode="reference")

        assert report["pass"], (preset, report)
        assert report["style"]["metrics"]["coverage"] >= 0.85, preset
        assert report["style"]["metrics"]["integrity"] == 1.0, preset
        assert generic["pass"] is False, preset
        assert (generic["style"]["metrics"]["coverage"] or 0) < 0.5, preset


def test_historical_demo_reference_oracles_pass_style_only_mode():
    for preset in builtin_preset_names():
        for language in ("en", "zh"):
            path = ROOT / "demos" / f"{slug_for_preset(preset)}-{language}.html"
            if not path.exists():
                continue
            report = validate_preset_fidelity(path.read_text(encoding="utf-8"), preset, mode="reference")
            assert report["pass"], (path.name, report["hard_failures"], report["style"]["metrics"])
            assert report["style"]["metrics"]["coverage"] >= 0.85, path.name


def test_wrong_neighbor_contract_cannot_claim_renderer_output():
    presets = builtin_preset_names()
    for index, preset in enumerate(presets):
        neighbor = presets[(index + 1) % len(presets)]
        html = _render(preset)
        correct = validate_preset_fidelity(html, preset, mode="reference")["style"]["metrics"]["coverage"] or 0
        wrong_report = validate_preset_fidelity(html, neighbor, mode="reference")
        wrong = wrong_report["style"]["metrics"]["coverage"] or 0
        assert not wrong_report["pass"] or correct - wrong >= 0.15, (preset, neighbor, correct, wrong)


def test_hidden_marker_and_single_slide_dump_fail_every_profile_family():
    marker_template = (ROOT / "tests" / "fixtures" / "style-fidelity" / "marker-only.html").read_text(encoding="utf-8")
    dump_template = (ROOT / "tests" / "fixtures" / "style-fidelity" / "single-slide-signature-dump.html").read_text(encoding="utf-8")
    for preset in sorted(PROFILE_SPECS):
        classes = " ".join(item.lstrip(".") for item in requirement_for_preset(preset).classes)
        marker = marker_template.replace("preset-signature-dump", classes)
        dump = dump_template.replace("signature-dump", classes)
        assert validate_preset_fidelity(marker, preset, mode="reference")["pass"] is False, preset
        report = validate_preset_fidelity(dump, preset, mode="reference")
        assert report["pass"] is False, preset
        assert "style-signature-slide-distribution-low" in report["hard_failures"], preset


def test_full_slide_image_cannot_replace_real_preset_dom():
    for preset in builtin_preset_names():
        report = validate_preset_fidelity(FULL_SLIDE_IMAGE, preset, mode="reference")
        assert report["pass"] is False, preset
        assert "style-signature-coverage-low" in report["hard_failures"], preset


def test_renderer_emits_deterministic_page_buckets_for_short_and_long_decks():
    for preset in builtin_preset_names():
        for page_count in (8, 12):
            html = _render(preset, page_count=page_count)
            assert html.count('data-page-bucket="cover"') == 1, (preset, page_count)
            assert html.count('data-page-bucket="closing"') == 1, (preset, page_count)
            assert html.count('data-page-bucket="content"') == page_count - 2, (preset, page_count)


def test_profile_family_registry_is_not_hand_maintained_or_silently_partial():
    assert {spec.family for spec in PROFILE_SPECS.values()} == {
        "editorial_static",
        "signal_pitch",
        "technical_terminal",
        "glass_material",
        "brutalist_graphic",
        "geometric_soft",
        "split_editorial",
        "consulting_structured",
    }


def test_style_metrics_helper_has_no_contract_or_renderer_dependency():
    source = (ROOT / "scripts" / "style_signature_eval.py").read_text(encoding="utf-8")
    assert "preset_contracts" not in source
    assert "low_context" not in source
    assert "PROFILE_SPECS" not in source

    html = _render("Aurora Mesh")
    presence = collect_signature_presence(html, requirement_for_preset("Aurora Mesh"))
    assert presence.coverage == 1.0
