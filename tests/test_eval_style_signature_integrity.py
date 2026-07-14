from __future__ import annotations

import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from low_context import compile_style_contract  # noqa: E402
from quality_eval import _style_signature_coverage  # noqa: E402
from run_evals import _compute_style_signature_metrics  # noqa: E402
from preset_contracts import requirement_for_preset  # noqa: E402
from style_signature_eval import collect_signature_presence  # noqa: E402


def _class_names_required_by_contract(preset: str) -> tuple[str, ...]:
    contract = compile_style_contract(preset)
    classes: list[str] = []
    for selector in [*contract["required_signature_classes"], *contract["required_background_layers"]]:
        if not selector.startswith(".") or "::" in selector:
            continue
        class_name = selector[1:]
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", class_name) and class_name not in classes:
            classes.append(class_name)
    return tuple(classes)


def _coverage_from_run_evals(html_text: str, preset: str) -> float:
    coverage = _compute_style_signature_metrics(html_text, preset)["signature_coverage"]
    assert coverage is not None
    return coverage


def _coverage_from_quality_eval(html_text: str, preset: str) -> float:
    coverage = _style_signature_coverage(BeautifulSoup(html_text, "html.parser"), preset)
    assert coverage is not None
    return coverage


def _html_with_signature_classes(preset: str, *, carrier_markup: str) -> str:
    classes = " ".join(_class_names_required_by_contract(preset))
    return f"""<!doctype html>
<html>
<head>
<style>
.profile-signature-markers {{
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    opacity: 0.01;
}}
</style>
</head>
<body data-preset="{preset}">
<section class="slide" id="slide-1">
  <div class="slide-content">
    <h1>Visible slide title</h1>
    <p>Visible slide content with real words.</p>
    {carrier_markup.format(classes=classes)}
  </div>
</section>
</body>
</html>"""


def test_hidden_signature_marker_classes_do_not_count_as_style_coverage():
    html_text = _html_with_signature_classes(
        "Paper & Ink",
        carrier_markup='<div class="profile-signature-markers {classes}" aria-hidden="true"></div>',
    )

    assert _coverage_from_run_evals(html_text, "Paper & Ink") == 0
    assert _coverage_from_quality_eval(html_text, "Paper & Ink") == 0


def test_section_marker_classes_do_not_count_as_real_components():
    classes = " ".join(_class_names_required_by_contract("Strategy Consulting"))
    html_text = f"""<!doctype html>
<html>
<body data-preset="Strategy Consulting">
<section class="slide {classes}" id="slide-1">
  <div class="slide-content">
    <h1>Visible slide title</h1>
    <p>Visible slide content with real words.</p>
  </div>
</section>
</body>
</html>"""

    assert _coverage_from_run_evals(html_text, "Strategy Consulting") == 0
    assert _coverage_from_quality_eval(html_text, "Strategy Consulting") == 0


def test_invisible_nodes_do_not_contribute_style_coverage():
    hidden_carriers = [
        '<div class="{classes}" aria-hidden="true">Hidden marker text</div>',
        '<div class="{classes}" hidden>Hidden marker text</div>',
        '<div class="{classes}" style="display:none">Hidden marker text</div>',
        '<div class="{classes}" style="visibility:hidden">Hidden marker text</div>',
        '<div class="{classes}" style="opacity:0.01">Hidden marker text</div>',
        '<div class="{classes}" style="width:1px;height:1px;overflow:hidden">Hidden marker text</div>',
        '<div class="{classes}" style="position:absolute;left:-9999px">Hidden marker text</div>',
        '<div class="{classes}" style="font-size:0">Hidden marker text</div>',
        '<div class="{classes}" style="clip-path:inset(50%)">Hidden marker text</div>',
    ]
    for carrier in hidden_carriers:
        html_text = _html_with_signature_classes("Paper & Ink", carrier_markup=carrier)
        assert _coverage_from_run_evals(html_text, "Paper & Ink") == 0, carrier
        assert _coverage_from_quality_eval(html_text, "Paper & Ink") == 0, carrier


def test_empty_component_shell_does_not_count_as_signature_hit():
    html_text = _html_with_signature_classes(
        "Strategy Consulting",
        carrier_markup='<div class="{classes}"></div>',
    )

    assert _coverage_from_run_evals(html_text, "Strategy Consulting") == 0
    assert _coverage_from_quality_eval(html_text, "Strategy Consulting") == 0


def test_empty_pseudo_selector_does_not_count_as_visible_background_signature():
    html_text = """<!doctype html>
<html>
<head><style>.rule::before { --profile-component-present: 1; }</style></head>
<body data-preset="Paper & Ink">
<section class="slide" id="slide-1">
  <div class="slide-content">
    <h1>Visible slide title</h1>
    <p>Visible slide content with real words.</p>
  </div>
</section>
</body>
</html>"""

    assert _coverage_from_run_evals(html_text, "Paper & Ink") == 0
    assert _coverage_from_quality_eval(html_text, "Paper & Ink") == 0


def test_paper_ink_signature_requirement_matches_reference_demo_components():
    html_text = (ROOT / "demos" / "paper-ink-zh.html").read_text(encoding="utf-8")
    requirement = requirement_for_preset("Paper & Ink")
    presence = collect_signature_presence(html_text, requirement)

    assert requirement.groups
    assert ".hero-body" in requirement.classes
    assert requirement.backgrounds == ()
    assert presence.coverage is not None
