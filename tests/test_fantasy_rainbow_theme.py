from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup
import pytest


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
THEME_DIR = ROOT / "themes" / "fantasy-rainbow"
REFERENCE = THEME_DIR / "reference.md"
STARTER = THEME_DIR / "starter.html"

sys.path.insert(0, str(SCRIPTS))


def _brief() -> dict:
    fixture = ROOT / "demos" / "mode-paths" / "auto-BRIEF.json"
    data = json.loads(fixture.read_text(encoding="utf-8"))
    data["title"] = "奇幻彩虹测试稿"
    data["style"]["preset"] = "custom:fantasy-rainbow"
    data["narrative"]["page_roles"][-1] = "cta"
    data["narrative"]["slides"][-1]["role"] = "cta"
    data["narrative"]["slides"][-1]["title"] = "一句话安装，生成你的第一份 deck"
    data["narrative"]["slides"][-1]["supporting_facts"] = [
        "Tell Claude: Install https://github.com/kaisersong/slide-creator",
        "clawhub install kai-slide-creator",
    ]
    data["narrative"]["page_roles"][5] = "feature"
    data["narrative"]["slides"][5]["role"] = "feature"
    data["narrative"]["slides"][5]["supporting_facts"] = [
        "tokens",
        "named layouts",
        "signature elements",
        "runtime contract",
    ]
    return data


def test_fantasy_rainbow_is_canonical_and_legacy_preset_remains_renderable():
    from preset_capabilities import get_preset_render_capability
    from low_context import render_from_brief

    canonical = get_preset_render_capability("custom:fantasy-rainbow")
    display_name = get_preset_render_capability("Fantasy Rainbow")
    legacy = get_preset_render_capability("custom:iridescence-convergence")

    assert canonical.can_render is True
    assert canonical.canonical_preset == "Fantasy Rainbow"
    assert canonical.reference_path == "themes/fantasy-rainbow/reference.md"
    assert display_name.can_render is True
    assert display_name.reference_path == canonical.reference_path
    assert legacy.can_render is True
    assert legacy.canonical_preset == "Fantasy Rainbow"
    assert legacy.reference_path == canonical.reference_path

    legacy_brief = _brief()
    legacy_brief["style"]["preset"] = "custom:iridescence-convergence"
    legacy_html, legacy_packet, legacy_contract = render_from_brief(legacy_brief)
    assert legacy_packet["canonical_preset"] == "Fantasy Rainbow"
    assert legacy_contract["preset"] == "Fantasy Rainbow"
    assert 'data-preset="Fantasy Rainbow"' in legacy_html
    assert "iri-scene--hero" in legacy_html


def test_iridescence_theme_is_discoverable_and_renderable():
    from preset_capabilities import discover_custom_themes, get_preset_render_capability

    themes = discover_custom_themes()
    assert "fantasy-rainbow" in themes
    assert themes["fantasy-rainbow"] == REFERENCE.resolve()

    capability = get_preset_render_capability("custom:fantasy-rainbow")
    assert capability.can_render is True
    assert capability.renderer_strategy == "custom_theme"
    assert capability.support_tier == "custom"


def _brief_with_page_count(page_count: int) -> dict:
    brief = _brief()
    source = brief["narrative"]["slides"][5]
    slides = []
    for index in range(1, page_count + 1):
        slide = copy.deepcopy(source)
        slide["slide_number"] = index
        slide["role"] = "cover" if index == 1 else "cta" if index == page_count else "feature"
        slide["title"] = f"Page {index}"
        slides.append(slide)
    brief["deck"]["page_count"] = page_count
    brief["narrative"]["slides"] = slides
    brief["narrative"]["page_roles"] = [slide["role"] for slide in slides]
    return brief


def test_generation_brief_page_count_accepts_40_and_rejects_41():
    from jsonschema import Draft202012Validator
    from low_context import validate_brief_data

    schema = json.loads((ROOT / "schemas" / "generation-brief.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    forty = _brief_with_page_count(40)
    forty_one = _brief_with_page_count(41)

    assert schema["properties"]["deck"]["properties"]["page_count"]["maximum"] == 40
    assert list(validator.iter_errors(forty)) == []
    assert validate_brief_data(forty) == []
    assert any(error.validator == "maximum" for error in validator.iter_errors(forty_one))
    assert any("page_count must be <= 40" in error for error in validate_brief_data(forty_one))


def test_structured_content_is_optional_semantic_ir_and_survives_slide_spec():
    from jsonschema import Draft202012Validator
    from low_context import build_slide_spec, validate_brief_data

    brief = _brief()
    structured = {
        "kind": "interaction-flow-poll",
        "groups": [
            {"id": "task", "nodes": [{"id": "step-1"}, {"id": "step-2", "source_refs": ["S2"]}]},
            {"id": "poll", "source_refs": ["S3"], "nodes": [{"id": "option-a"}, {"id": "option-b"}]},
        ],
        "edges": [
            {"from": "step-1", "to": "step-2", "relation": "ordered-before", "source_refs": ["S1"]}
        ],
    }
    brief["narrative"]["slides"][1]["structured_content"] = structured
    schema = json.loads((ROOT / "schemas" / "generation-brief.schema.json").read_text(encoding="utf-8"))

    assert validate_brief_data(_brief()) == []
    assert list(Draft202012Validator(schema).iter_errors(brief)) == []
    assert validate_brief_data(brief) == []
    assert build_slide_spec(brief)[1]["structured_content"] is structured

    duplicate = copy.deepcopy(brief)
    duplicate["narrative"]["slides"][1]["structured_content"]["groups"][1]["nodes"][0]["id"] = "step-1"
    assert any("reuses structured id: step-1" in error for error in validate_brief_data(duplicate))

    dangling = copy.deepcopy(brief)
    dangling["narrative"]["slides"][1]["structured_content"]["edges"][0]["to"] = "missing"
    assert any("references unknown structured id: missing" in error for error in validate_brief_data(dangling))


def test_source_faithful_structured_kinds_validate_with_title_only_groups_optional():
    from jsonschema import Draft202012Validator
    from low_context import validate_brief_data

    schema = json.loads((ROOT / "schemas" / "generation-brief.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    fixtures = {
        "personal-profile": [{"id": "identity"}, {"id": "credentials"}],
        "challenge-flow": [{"id": "challenges"}, {"id": "process"}],
        "milestone-timeline": [{"id": "timeline"}],
        "three-column-conclusion": [{"id": "problems"}],
        "capability-bridge": [{"id": "capabilities"}],
        "context-package": [{"id": "package"}, {"id": "components"}],
        "takeaway-stack": [{"id": "principles"}],
    }
    for kind, groups in fixtures.items():
        brief = _brief()
        brief["narrative"]["slides"][1]["structured_content"] = {"kind": kind, "groups": groups}
        assert list(validator.iter_errors(brief)) == []
        assert validate_brief_data(brief) == []

    title_only = _brief()
    title_only["narrative"]["slides"][1]["structured_content"] = {"kind": "title-only"}
    assert list(validator.iter_errors(title_only)) == []
    assert validate_brief_data(title_only) == []


def test_iridescence_reference_compiles_the_approved_contract():
    from low_context import compile_style_contract

    contract = compile_style_contract("custom:fantasy-rainbow")

    assert contract["preset"] == "Fantasy Rainbow"
    assert contract["allowed_layout_ids"] == [
        "title_grid",
        "contents_index",
        "column_content",
        "stat_block",
        "geometric_diagram",
        "data_table",
        "pull_quote",
        "toc",
        "cta_close",
        "bento",
    ]
    for token in (
        "--ic-bg",
        "--ic-text",
        "--ic-blue",
        "--ic-cyan",
        "--ic-pink",
        "--ic-purple",
        "--ic-ice",
    ):
        assert token in contract["tokens"]

    reference = REFERENCE.read_text(encoding="utf-8")
    for requirement in (
        "WebGL lifecycle",
        "fallback",
        "prefers-reduced-motion",
        "@media print",
        "safe area",
        "single canvas",
    ):
        assert requirement in reference
    assert "http://" not in reference
    assert "https://" not in reference
    assert "@font-face" not in reference
    assert not re.search(r"\b(?:TODO|TBD|LOREM)\b", reference, re.IGNORECASE)


@pytest.mark.parametrize("count", range(1, 7))
@pytest.mark.parametrize("preset", ["custom:fantasy-rainbow", "奇幻彩虹", "custom:iridescence-convergence"])
def test_business_bento_is_rendered_from_brief_with_all_local_facts(count, preset):
    from low_context import render_from_brief, build_slide_spec

    brief = _brief()
    brief["style"]["preset"] = preset
    slide = brief["narrative"]["slides"][3]
    slide["preferred_layout_family"] = "bento"
    slide["supporting_facts"] = [f"业务 {index}：证据 <{index}> & 条件" for index in range(count)]
    html, packet, _ = render_from_brief(brief)
    spec = build_slide_spec(brief, packet)[3]
    assert spec["layout_id"] == "bento"
    soup = BeautifulSoup(html, "html.parser")
    rendered = soup.select_one('#slide-4.iri-scene--bento[data-export-role="bento"]')
    assert rendered is not None
    cards = rendered.select(".iri-bento-card")
    assert len(cards) == count
    assert [card.h3.get_text() for card in cards] == [f"业务 {index}" for index in range(count)]
    assert [card.p.get_text() for card in cards] == [f"证据 <{index}> & 条件" for index in range(count)]
    assert soup.select_one('#slide-1.iri-scene--hero') is not None
    assert soup.select_one('.iri-scene--closing') is not None


def test_business_bento_preference_survives_low_detail_brief():
    from low_context import render_from_brief, assess_quality_tier

    brief = _brief()
    brief["content"]["must_include"] = ["本地事实"]
    brief["content"]["must_avoid"] = ["编造数据"]
    brief["narrative"]["thesis"] = "演示主题"
    for slide in brief["narrative"]["slides"]:
        slide["key_point"] = "关键观点"
    assert assess_quality_tier(brief) == "tier2"
    brief["narrative"]["slides"][3]["preferred_layout_family"] = "bento"
    html, _, _ = render_from_brief(brief)
    assert BeautifulSoup(html, "html.parser").select_one('#slide-4.iri-scene--bento') is not None


def test_iridescence_starter_has_self_contained_runtime_contract():
    html = STARTER.read_text(encoding="utf-8")

    assert html.count("</body>") == 1
    assert html.count("</html>") == 1
    assert html.rstrip().endswith("</html>")
    style = re.search(r"<style>(.*?)</style>", html, re.DOTALL)
    assert style
    assert style.group(1).count("{") == style.group(1).count("}")

    for marker in (
        "scroll-snap-type",
        "height: 100vh",
        "aspect-ratio: 16 / 9",
        "@media print",
        "prefers-reduced-motion",
        "theme-decor",
        "data-theme-runtime",
        "iridescence-canvas",
        "IridescenceController",
        "requestAnimationFrame",
        "cancelAnimationFrame",
        "webglcontextlost",
        "webglcontextrestored",
        "restoreContext",
        "compileShader",
        "LINK_STATUS",
        "forceFallback",
        "setDeterministicTime",
        "getFrameStats",
    ):
        assert marker in html

    assert html.count('<canvas id="iridescence-canvas"') == 1
    assert "http://" not in html
    assert "https://" not in html
    assert "@font-face" not in html
    assert "--kd-blue:" in html
    assert "--text-secondary:" in html


def test_iridescence_is_cover_only():
    from low_context import render_from_brief

    starter = STARTER.read_text(encoding="utf-8")
    reference = REFERENCE.read_text(encoding="utf-8")
    brief = _brief()
    html, _, _ = render_from_brief(brief)
    soup = BeautifulSoup(html, "html.parser")

    assert ".iri-scene:not(.iri-scene--hero):not(.iri-scene--closing)" in starter
    assert re.search(
        r"\.iri-scene:not\(\.iri-scene--hero\):not\(\.iri-scene--closing\)\s*\{[^}]*background:\s*#fff",
        starter,
        re.DOTALL | re.IGNORECASE,
    )
    assert re.search(
        r"\.iri-scene--closing\s*\{[^}]*background:\s*#0a0a12",
        starter,
        re.DOTALL | re.IGNORECASE,
    )
    assert "isCoverActive()" in starter
    assert "this.active = this.isCoverActive();" in starter
    assert "this.canvas.hidden = !this.active;" in starter
    assert "visible on every slide" not in reference
    assert "primary surface on every page" not in reference
    assert "light field remains the dominant surface on all pages" not in reference

    slides = soup.select(".slide")
    assert len(slides) == brief["deck"]["page_count"]
    assert "iri-scene--hero" in slides[0].get("class", [])
    assert all("iri-scene--hero" not in slide.get("class", []) for slide in slides[1:])
    assert "iri-scene--closing" in slides[-1].get("class", [])
    assert len(soup.select("#iridescence-canvas")) == 1


def test_iridescence_restrained_accent_palette_contract():
    starter = STARTER.read_text(encoding="utf-8")
    reference = REFERENCE.read_text(encoding="utf-8")

    for token, value in (
        ("--iri-accent-blue", "#5B6CFF"),
        ("--iri-accent-purple", "#9B5CFF"),
        ("--iri-accent-cyan", "#20BFC4"),
        ("--iri-accent-blue-text", "#4152CC"),
        ("--iri-accent-purple-text", "#7037D8"),
        ("--iri-accent-cyan-text", "#007B83"),
        ("--iri-tint-blue", "rgba(91, 108, 255, .08)"),
        ("--iri-tint-purple", "rgba(155, 92, 255, .08)"),
        ("--iri-tint-cyan", "rgba(32, 191, 196, .08)"),
    ):
        assert f"{token}: {value}" in starter
        assert f"{token}: {value}" in reference

    for selector in (
        ".iri-accent-primary",
        ".iri-accent-secondary",
        ".iri-accent-tint-primary",
        ".iri-accent-tint-secondary",
        ".iri-accent-tint-tertiary",
        ".iri-spectrum-marker.iri-marker-primary",
        ".iri-spectrum-marker.iri-marker-secondary",
        ".iri-spectrum-marker.iri-marker-tertiary",
    ):
        assert selector in starter

    assert not re.search(r"^\.iri-accent-tertiary\s*\{", starter, re.MULTILINE)

    for selector, token in (
        (".iri-accent-text-primary", "--iri-accent-blue-text"),
        (".iri-accent-text-secondary", "--iri-accent-purple-text"),
        (".iri-accent-text-tertiary", "--iri-accent-cyan-text"),
    ):
        assert re.search(
            rf"{re.escape(selector)}\s*\{{[^}}]*color:\s*var\({token}\)",
            starter,
            re.DOTALL,
        )

    assert "10%–15%" in reference
    assert "small text" in reference
    assert "Content pages remain opaque white" in reference


def test_iridescence_cover_selectively_rebalances_warm_pink_and_preserves_mint():
    starter = STARTER.read_text(encoding="utf-8")
    reference = REFERENCE.read_text(encoding="utf-8")

    for signature in (
        "float warmBias=clamp((col.r-col.g-0.02)*4.0,0.0,1.0);",
        "vec3 shifted=col;",
        "shifted.r=col.r*0.82+col.b*0.04;",
        "shifted.b=min(1.0,col.b*1.08+col.r*0.16);",
        "col=mix(col,shifted,warmBias);",
    ):
        assert signature in starter

    assert "balanced.g=col.g*0.98;" not in starter
    assert "green-dominant mint and cyan pixels remain on the original field output" in reference

    assert "rgba(255, 110, 221, .82)" not in starter
    assert "rgba(167, 108, 255, .48)" in starter
    assert "rgba(167, 108, 255, 0) 34%" in starter
    assert "--ic-violet: #A76CFF" in reference
    assert "--ic-pink: var(--ic-violet)" in reference
    assert "cyan-blue → blue-violet → limited pink-violet" in reference


def test_iridescence_cover_keyword_veil_is_a_cover_only_soft_bloom():
    starter = STARTER.read_text(encoding="utf-8")
    reference = REFERENCE.read_text(encoding="utf-8")
    style = re.search(r"<style>(.*?)</style>", starter, re.DOTALL)
    assert style
    css = style.group(1)

    assert "--iri-accent-blue: #5B6CFF" in css
    assert "--iri-cover-keyword-veil-alpha: .81" in css
    veil = re.search(
        r"\.iri-scene--hero \.iri-headline em\.iri-accent-primary::before\s*\{(?P<body>[^}]*)\}",
        css,
        re.DOTALL,
    )
    assert veil
    assert "radial-gradient(" in veil.group("body")
    assert "rgba(255,255,255,var(--iri-cover-keyword-veil-alpha))" in veil.group("body")
    assert "inset: -.12em -.20em" in veil.group("body")
    assert "38%" in veil.group("body")
    assert "78%" in veil.group("body")
    assert "filter: blur(.09em)" in veil.group("body")
    assert "pointer-events: none" in veil.group("body")
    assert not re.search(r"(?:padding|border(?:-radius)?|box-shadow)\s*:", veil.group("body"))
    assert css.count(".iri-headline em.iri-accent-primary::before") == 1
    assert ".iri-scene--closing .iri-headline em.iri-accent-primary::before" not in css

    assert "--iri-cover-keyword-veil-alpha: .81" in reference
    assert "cover headline emphasis only" in reference
    assert "soft white radial veil" in reference
    assert "closing headline emphasis receives no veil" in reference


def test_iridescence_multiline_cover_headline_has_glyph_clearance():
    starter = STARTER.read_text(encoding="utf-8")
    match = re.search(
        r"\.iri-scene--hero \.iri-title-line \+ \.iri-title-line\s*\{(?P<body>[^}]*)\}",
        starter,
    )

    assert match is not None
    margin = re.search(r"margin-top:\s*(?P<value>[0-9.]+)em", match.group("body"))
    assert margin is not None
    assert float(margin.group("value")) >= 0.06


def test_iridescence_cover_keyword_veil_meets_worst_pixel_contrast():
    starter = STARTER.read_text(encoding="utf-8")
    alpha_match = re.search(r"--iri-cover-keyword-veil-alpha:\s*([0-9.]+)", starter)
    assert alpha_match
    alpha = float(alpha_match.group(1))
    assert alpha == 0.81

    foreground = (91.0, 108.0, 255.0)
    worst_canvas_pixel = (169.0, 137.0, 254.0)
    composited_background = tuple(
        channel * (1.0 - alpha) + 255.0 * alpha for channel in worst_canvas_pixel
    )

    def relative_luminance(rgb: tuple[float, float, float]) -> float:
        channels = []
        for channel in rgb:
            value = channel / 255.0
            channels.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

    foreground_luminance = relative_luminance(foreground)
    background_luminance = relative_luminance(composited_background)
    contrast = (background_luminance + 0.05) / (foreground_luminance + 0.05)

    assert contrast >= 3.0


def test_iridescence_closing_credit_uses_readable_light_palette():
    starter = STARTER.read_text(encoding="utf-8")
    style = re.search(r"<style>(.*?)</style>", starter, re.DOTALL)
    assert style
    css = style.group(1)

    override = re.search(
        r"\.iri-scene--closing \.slide-credit\s*\{(?P<body>[^}]*)\}",
        css,
        re.DOTALL,
    )
    assert override
    color = re.search(
        r"color:\s*rgba\(247\s*,\s*247\s*,\s*251\s*,\s*([0-9.]+)\)",
        override.group("body"),
    )
    assert color

    alpha = float(color.group(1))
    foreground = (247.0, 247.0, 251.0)
    background = (10.0, 10.0, 18.0)
    composited = tuple(
        foreground_channel * alpha + background_channel * (1.0 - alpha)
        for foreground_channel, background_channel in zip(foreground, background)
    )

    def relative_luminance(rgb: tuple[float, float, float]) -> float:
        channels = []
        for channel in rgb:
            value = channel / 255.0
            channels.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

    contrast = (relative_luminance(composited) + 0.05) / (relative_luminance(background) + 0.05)
    assert contrast >= 4.5


def test_iridescence_cover_keyword_veil_lower_right_fade_has_contrast_margin():
    starter = STARTER.read_text(encoding="utf-8")
    alpha_match = re.search(r"--iri-cover-keyword-veil-alpha:\s*([0-9.]+)", starter)
    assert alpha_match
    alpha = float(alpha_match.group(1))

    foreground = (91.0, 108.0, 255.0)
    lower_right_raw_canvas_pixel = (136.0, 155.0, 252.0)
    cover_veil_alpha = 0.08
    cover_composited_canvas_pixel = tuple(
        channel * (1.0 - cover_veil_alpha) + 255.0 * cover_veil_alpha
        for channel in lower_right_raw_canvas_pixel
    )
    effective_radial_factor = 0.82
    effective_alpha = alpha * effective_radial_factor
    composited_background = tuple(
        channel * (1.0 - effective_alpha) + 255.0 * effective_alpha
        for channel in cover_composited_canvas_pixel
    )

    def relative_luminance(rgb: tuple[float, float, float]) -> float:
        channels = []
        for channel in rgb:
            value = channel / 255.0
            channels.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

    foreground_luminance = relative_luminance(foreground)
    background_luminance = relative_luminance(composited_background)
    contrast = (background_luminance + 0.05) / (foreground_luminance + 0.05)

    assert contrast >= 3.1


def test_iridescence_reference_matches_renderer_owned_accent_map():
    reference = REFERENCE.read_text(encoding="utf-8")
    accent_contract = next(
        line for line in reference.splitlines() if line.startswith("Accent placement is fixed by page")
    )

    assert "P4 uses primary text-safe blue for field numbers and codes" in accent_contract
    assert (
        "P6 uses a vivid blue display total with four small blue/purple/cyan spectrum markers while every spectrum label remains `--iri-ink`"
        in accent_contract
    )
    assert "P7 uses primary text-safe blue for contract numbers" in accent_contract
    assert (
        "P8 cycles gate borders through vivid blue, purple, cyan, and blue, with each `GATE nn` label "
        "using the matching text-safe blue, purple, cyan, and blue cycle while gate titles and descriptions remain `--iri-ink`"
    ) in accent_contract
    assert (
        "P9 uses vivid blue for PLAY, vivid purple for EDIT, and text-safe cyan for PRESENT, while keys use primary text-safe blue"
    ) in accent_contract
    assert "P11 cycles quadrant numbers through text-safe blue, purple, cyan, and blue" in accent_contract

    for stale_mapping in (
        "P4 uses text-safe cyan field numbers",
        "P7 uses text-safe purple contract numbers",
        "P8 uses purple gate borders",
        "P9 uses cyan for runtime verbs",
        "P9 uses vivid blue, purple, and cyan for PLAY, EDIT, and PRESENT respectively",
        "P11 alternates text-safe purple and cyan quadrant numbers",
    ):
        assert stale_mapping not in accent_contract


def test_iridescence_text_safe_cyan_meets_body_text_contrast_on_white():
    starter = STARTER.read_text(encoding="utf-8")
    token_match = re.search(r"--iri-accent-cyan-text:\s*(#[0-9A-Fa-f]{6})", starter)
    assert token_match, "missing --iri-accent-cyan-text token"

    hex_color = token_match.group(1)
    assert hex_color.upper() == "#007B83"
    foreground = tuple(int(hex_color[index : index + 2], 16) for index in (1, 3, 5))

    def relative_luminance(rgb: tuple[int, int, int]) -> float:
        channels = []
        for channel in rgb:
            value = channel / 255.0
            channels.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

    foreground_luminance = relative_luminance(foreground)
    white_luminance = relative_luminance((255, 255, 255))
    contrast = (white_luminance + 0.05) / (foreground_luminance + 0.05)

    assert contrast >= 4.5


def test_iridescence_semantic_accent_css_controls_the_cascade():
    html = STARTER.read_text(encoding="utf-8")
    style = re.search(r"<style>(.*?)</style>", html, re.DOTALL)
    assert style
    css = style.group(1)

    def rule(selector: str) -> str:
        match = re.search(rf"{re.escape(selector)}\s*\{{(?P<body>[^}}]*)\}}", css, re.DOTALL)
        assert match, f"missing CSS rule for {selector}"
        return match.group("body")

    assert "color: var(--iri-ink)" in rule(".iri-number")
    assert "color: var(--iri-ink)" in rule(".iri-fact-index")
    assert "color: var(--iri-ink)" in rule(".iri-scene--hero .iri-label")
    assert "color: var(--iri-accent-blue-text)" in rule("#brand-mark")
    assert "color: var(--iri-ink)" in rule("body:has(.iri-scene--hero.visible) #brand-mark")
    assert "color: rgba(247,247,251,.72)" in rule("body:has(.iri-scene--closing.visible) #brand-mark")
    assert "background: #fff" in rule(".iri-pipeline-step")
    assert "color:" not in rule(".iri-spectrum-total")
    assert "color:" not in rule(".iri-runtime-screen strong")
    for selector in (
        ".iri-field .iri-number {",
        ".iri-contract-layer .iri-number {",
        ".iri-mode + .iri-mode .iri-number {",
        ".iri-quadrant:nth-child(even) .iri-number {",
        ".iri-quadrant:nth-child(odd) .iri-number {",
    ):
        assert selector not in css
    assert not re.search(r"\.iri-pipeline-step:nth-child\([^)]*\)\s*\{[^}]*background", css, re.DOTALL)
    assert not re.search(r"\.iri-spectrum-item:nth-child\([^)]*\)\s*\{[^}]*color", css, re.DOTALL)

    component_end = css.index("/* 12 — closing */")
    primary_helper = re.search(r"^\.iri-accent-primary\s*\{", css, re.MULTILINE)
    tertiary_tint_helper = re.search(r"^\.iri-accent-tint-tertiary\s*\{", css, re.MULTILINE)
    assert primary_helper and primary_helper.start() > component_end
    assert tertiary_tint_helper and tertiary_tint_helper.start() > component_end

    convergence = rule(".iri-convergence-word.iri-accent-primary")
    assert "color: rgba(255,255,255,.10)" in convergence
    assert "-webkit-text-stroke: 2.4px var(--iri-accent-blue)" in convergence

    for marker, border_token, label_token in (
        ("primary", "--iri-accent-blue", "--iri-accent-blue-text"),
        ("secondary", "--iri-accent-purple", "--iri-accent-purple-text"),
        ("tertiary", "--iri-accent-cyan", "--iri-accent-cyan-text"),
    ):
        assert f"border-left-color: var({border_token})" in rule(f".iri-gate.iri-gate-accent-{marker}")
        assert f"color: var({label_token})" in rule(f".iri-gate.iri-gate-accent-{marker} > span")
    assert "color: var(--iri-ink)" in rule(".iri-gate strong, .iri-gate small")


def test_iridescence_runtime_chrome_and_editing_cover_custom_components():
    starter = STARTER.read_text(encoding="utf-8")
    engine = (ROOT / "references" / "js-engine.md").read_text(encoding="utf-8")

    assert re.search(r"#present-btn\s*\{[^}]*position:\s*fixed", starter, re.DOTALL)
    assert re.search(r"#present-counter\s*\{[^}]*position:\s*fixed", starter, re.DOTALL)
    override = re.search(
        r"this\.ctrl\.goTo\s*=\s*\(i\)\s*=>\s*\{(?P<body>.*?)\n\s*\};",
        engine,
        re.DOTALL,
    )
    assert override
    assert "this._updateCounter();" in override.group("body")
    assert "h1,h2,h3,p,li,span,strong,small,b,code,td,th" in engine


def test_iridescence_uses_standard_slide_creator_shell_contract():
    from low_context import render_from_brief

    starter = STARTER.read_text(encoding="utf-8")
    brief = _brief()
    html, _, _ = render_from_brief(brief)
    soup = BeautifulSoup(html, "html.parser")
    css = "\n".join(node.get_text() for node in soup.select("style"))

    present = re.search(r"#present-btn\s*\{(?P<body>[^}]*)\}", starter, re.DOTALL)
    assert present
    assert "width: 44px" in present.group("body")
    assert "height: 44px" in present.group("body")
    assert "border-radius: 50%" in present.group("body")
    assert "display: flex" in present.group("body")

    idle_dot = re.search(r"\.nav-dots button\s*\{(?P<body>[^}]*)\}", starter, re.DOTALL)
    active_dot = re.search(r"\.nav-dots button\.active\s*\{(?P<body>[^}]*)\}", starter, re.DOTALL)
    assert idle_dot and active_dot
    assert "width: 8px" in idle_dot.group("body")
    assert "height: 8px" in idle_dot.group("body")
    assert "transform: scale(1.3)" in active_dot.group("body")
    assert "height: 24px" not in active_dot.group("body")

    progress = re.search(r"\.progress-bar\s*\{(?P<body>[^}]*)\}", starter, re.DOTALL)
    assert progress
    assert "position: fixed" in progress.group("body")
    assert "top: 0" in progress.group("body")
    assert "height: 4px" in progress.group("body")
    assert "progress-track" not in starter

    slides = soup.select("section.slide")
    total = brief["deck"]["page_count"]
    assert len(slides) == total
    labels = [slide.select_one(":scope > .slide-num-label") for slide in slides]
    assert all(labels)
    assert [label.get_text(strip=True) for label in labels] == [
        f"{index:02d} / {total:02d}" for index in range(1, total + 1)
    ]

    credit = re.search(r"^\.slide-credit\s*\{(?P<body>[^}]*)\}", starter, re.DOTALL | re.MULTILINE)
    assert credit
    assert "right: 14px" in credit.group("body")
    assert "bottom: 8px" in credit.group("body")

    edit_toggle = soup.select_one("#editToggle")
    assert edit_toggle
    assert edit_toggle.get("title") == "Edit mode (E)"
    edit_rule = re.search(r"#editToggle,\s*\.edit-toggle\s*\{(?P<body>[^}]*)\}", css, re.DOTALL)
    edit_show_rule = re.search(r"#editToggle\.show,\s*\.edit-toggle\.show\s*\{(?P<body>[^}]*)\}", css, re.DOTALL)
    assert edit_rule and edit_show_rule
    assert "display: none" not in edit_rule.group("body")
    assert "opacity: 0" in edit_rule.group("body")
    assert "pointer-events: none" in edit_rule.group("body")
    assert "opacity: 1" in edit_show_rule.group("body")
    assert "pointer-events: auto" in edit_show_rule.group("body")


def test_iridescence_starter_preserves_reference_visual_language():
    html = STARTER.read_text(encoding="utf-8")

    for signature in (
        '"Space Grotesk"',
        '"JetBrains Mono"',
        '"Noto Sans SC"',
        "float d=-uTime*0.5;",
        "for(float i=0.0;i<8.0;++i)",
        "d+=uTime*0.5;",
        "gl_FragColor=vec4(col,1.0);",
        ".iri-label",
        ".iri-headline",
        ".iri-fact",
        ".iri-panel",
    ):
        assert signature in html

    slide_rule = re.search(r"\.slide\s*\{(.*?)\}", html, re.DOTALL)
    assert slide_rule
    assert "background: transparent" in slide_rule.group(1)
    assert re.search(
        r"\.iri-scene--hero\s+\.iri-facts\s*\{[^}]*grid-template-columns:\s*repeat\(4,",
        html,
        re.DOTALL,
    )
    assert "linear-gradient(180deg" in html
    assert "rgba(255,255,255,.45) 100%" in html
    assert ".slide:nth-of-type(even)::before" not in html
    assert re.search(r"\.iri-number\s*\{[^}]*color:\s*var\(--iri-ink\)", html, re.DOTALL)
    assert re.search(r"\.iri-scene--convergence\s+\.iri-headline\s*\{[^}]*clamp\(48px,\s*5\.4vw,\s*80px\)", html, re.DOTALL)
    assert re.search(r"\.iri-scene--brief\s+\.iri-headline\s*\{[^}]*clamp\(38px,\s*3\.6vw,\s*54px\)", html, re.DOTALL)

    for forbidden in (
        "background-size: 48px 48px",
        ".ic-orbit",
        ".ic-prism",
        "backdrop-filter",
        "border-radius: 999px",
        "smoothstep(",
        "float lift=",
        "mix(col,vec3(1.0)",
        "rgba(246,251,255,.985)",
        "rgba(237,247,255,.97)",
    ):
        assert forbidden not in html


def test_rendered_iridescence_deck_injects_theme_decor_and_runtime_once():
    from low_context import render_from_brief

    html, packet, contract = render_from_brief(_brief())

    assert packet["renderer_strategy"] == "custom_theme"
    assert contract["preset"] == "Fantasy Rainbow"
    assert 'data-preset="Fantasy Rainbow"' in html
    assert html.count('<canvas id="iridescence-canvas"') == 1
    assert html.count("class IridescenceController") == 1
    assert html.count("window.__iridescenceQA") == 1
    assert "SlidePresentation" in html
    assert "document.body.classList.contains('presenting')" in html
    assert "data-notes" in html
    assert "scroll-snap-type" in html
    assert "iri-scene--closing" in html
    assert "http://" not in html

    soup = BeautifulSoup(html, "html.parser")
    assert soup.select_one("#notes-panel-header") is not None
    assert soup.select_one("#notes-panel-label") is not None
    assert soup.select_one("#notes-textarea") is not None
    slides = soup.select("section.slide")
    assert len(soup.select("section.slide.iri-scene--closing")) == 1
    assert slides[0]["aria-label"] == "cover"
    assert len(slides[1].select(".iri-fracture-item")) >= 2
    assert len(soup.select(".iri-pipeline-step")) >= 4
    assert len(slides[-1].select(".iri-command")) >= 2
    assert "clawhub install kai-slide-creator" in slides[-1].get_text(" ", strip=True)
    assert "版权所有" not in html
    assert "内部公开" not in html
    assert not [
        node
        for node in soup.select("link[href],script[src],img[src],video[src],audio[src],source[src]")
        if (node.get("href") or node.get("src") or "").startswith(("http://", "https://", "//"))
    ]


def test_rendered_iridescence_deck_uses_distinct_reference_fidelity_scenes():
    from low_context import render_from_brief

    html, _, _ = render_from_brief(_brief())
    soup = BeautifulSoup(html, "html.parser")
    slides = soup.select("section.slide")
    scenes = [
        scene_class
        for slide in slides
        for scene_class in slide.get("class", [])
        if scene_class.startswith("iri-scene--")
    ]

    assert len(scenes) == len(slides)
    assert len(set(scenes)) == len(slides)
    assert slides[0].select_one(".iri-headline") is not None
    assert slides[0].select_one(".iri-facts") is not None
    assert slides[-1].select_one(".iri-panel") is not None

    for forbidden in (
        "ic-orbit",
        "ic-prism",
        "ic-hero-metric",
        "ic-index-card",
        "ic-stat-card",
        "kd-card",
    ):
        assert forbidden not in html


def test_iridescence_structured_roles_preserve_relationship_layouts():
    from low_context import render_from_brief

    brief = _brief()
    roles_and_items = [
        ("architecture-stack", [f"Layer {index}：detail" for index in range(1, 8)]),
        ("call-chain", [f"Node {index}：interface" for index in range(1, 6)]),
        ("dual-mode", ["Agent Loop：closed cognitive loop", "Workflow：fixed execution track"]),
        ("workshop", [f"Card {index}：choice" for index in range(1, 13)]),
        ("capability-landscape", [f"Capability {index}：detail" for index in range(1, 7)] + ["Runtime：route and execute", "Model / MaaS：foundation"]),
        ("enterprise-comparison", [f"Dimension {index}｜Open source {index}｜Enterprise {index}" for index in range(1, 6)]),
    ]
    for slide, (role, items) in zip(brief["narrative"]["slides"][1:-1], roles_and_items):
        slide["role"] = role
        slide["supporting_facts"] = items
    brief["narrative"]["page_roles"] = [slide["role"] for slide in brief["narrative"]["slides"]]

    html, _, _ = render_from_brief(brief)
    soup = BeautifulSoup(html, "html.parser")

    assert len(soup.select(".iri-scene--architecture-stack .iri-architecture-layer")) == 5
    assert len(soup.select(".iri-scene--architecture-stack .iri-architecture-guard")) == 2
    assert len(soup.select(".iri-scene--call-chain .iri-chain-node")) == 5
    assert len(soup.select(".iri-scene--dual-mode .iri-dual-track")) == 2
    assert len(soup.select(".iri-scene--workshop-grid .iri-workshop-cell")) == 12
    assert len(soup.select(".iri-scene--capability-landscape .iri-capability")) == 6
    assert len(soup.select(".iri-scene--comparison-table .iri-comparison-row")) == 6

    context_brief = _brief()
    context_brief["narrative"]["slides"][1]["role"] = "enterprise-context"
    context_brief["narrative"]["slides"][1]["supporting_facts"] = [f"Context {index}：detail" for index in range(1, 17)]
    context_brief["narrative"]["page_roles"] = [slide["role"] for slide in context_brief["narrative"]["slides"]]
    context_html, _, _ = render_from_brief(context_brief)
    context_soup = BeautifulSoup(context_html, "html.parser")
    assert len(context_soup.select(".iri-scene--context-matrix .iri-context-column")) == 2
    assert len(context_soup.select(".iri-scene--context-matrix .iri-context-row")) == 16
    assert len(context_soup.select('.iri-context-column[data-group-id]')) == 2
    assert len(context_soup.select('.iri-context-row[data-node-id]')) == 16


def test_iridescence_source_dense_scenes_preserve_nested_structure_without_tilt():
    from low_context import render_from_brief, validate_brief_data

    brief = _brief()
    poll_slide = brief["narrative"]["slides"][1]
    poll_slide["role"] = "interaction-poll"
    poll_slide["structured_content"] = {
        "kind": "interaction-flow-poll",
        "direction": "left-to-right",
        "groups": [
            {
                "id": "task",
                "label": "任务",
                "nodes": [
                    {"id": "step-1", "label": "发起"},
                    {"id": "step-2", "label": "提取"},
                    {"id": "step-3", "label": "提交"},
                ],
            },
            {
                "id": "poll",
                "label": "现场举手",
                "nodes": [
                    {"id": "option-a", "label": "A 容易"},
                    {"id": "option-b", "label": "B 很难"},
                ],
            },
        ],
        "edges": [
            {"from": "step-1", "to": "step-2", "relation": "ordered-before"},
            {"from": "step-2", "to": "step-3", "relation": "ordered-before"},
        ],
    }

    architecture_slide = brief["narrative"]["slides"][2]
    architecture_slide["role"] = "architecture-stack"
    architecture_slide["structured_content"] = {
        "kind": "layered-architecture",
        "direction": "top-to-bottom",
        "groups": [
            {"id": f"layer-{index}", "label": f"Layer {index}", "items": [f"Detail {index}"]}
            for index in range(1, 6)
        ],
        "edges": [
            {"from": f"layer-{index}", "to": f"layer-{index + 1}", "relation": "ordered-before"}
            for index in range(1, 5)
        ],
        "rails": [
            {"id": "security", "label": "安全与治理", "items": ["IAM"]},
            {"id": "observability", "label": "可观测与优化", "items": ["Trace"]},
        ],
        "bands": [{"id": "loop", "label": "运行闭环", "items": ["反馈"]}],
    }

    chain_slide = brief["narrative"]["slides"][3]
    chain_slide["role"] = "call-chain"
    chain_slide["structured_content"] = {
        "kind": "layered-call-graph",
        "direction": "top-to-bottom",
        "groups": [
            {
                "id": f"call-layer-{index}",
                "label": "SaaS" if index == 5 else f"LAYER {index}",
                "nodes": [{"id": f"node-{index}", "label": f"Node {index}", "items": [f"Item {index}"]}],
            }
            for index in range(1, 6)
        ],
        "edges": [
            {
                "from": f"call-layer-{index}",
                "to": f"call-layer-{index + 1}",
                "relation": "directed-edge",
                "label": f"Handoff {index}",
            }
            for index in range(1, 5)
        ],
    }
    brief["narrative"]["page_roles"] = [slide["role"] for slide in brief["narrative"]["slides"]]

    assert validate_brief_data(brief) == []
    html, _, _ = render_from_brief(brief)
    soup = BeautifulSoup(html, "html.parser")

    assert len(soup.select(".iri-scene--interaction-flow-poll .iri-interaction-step")) == 3
    assert len(soup.select(".iri-scene--interaction-flow-poll .iri-interaction-edge")) == 2
    interaction_sequence = soup.select_one(".iri-scene--interaction-flow-poll .iri-interaction-steps")
    assert ["iri-interaction-step" in child.get("class", []) for child in interaction_sequence.find_all(recursive=False)] == [True, False, True, False, True]
    assert len(soup.select(".iri-scene--interaction-flow-poll .iri-poll")) == 1
    assert len(soup.select(".iri-scene--interaction-flow-poll .iri-poll-option")) == 2
    assert not soup.select(".iri-scene--interaction-flow-poll .iri-pipeline")
    assert len(soup.select(".iri-scene--layered-architecture .iri-layered-architecture-layer")) == 5
    assert len(soup.select(".iri-scene--layered-architecture .iri-architecture-rail")) == 2
    assert len(soup.select(".iri-scene--layered-architecture .iri-architecture-band")) == 1
    assert len(soup.select(".iri-scene--layered-call-graph .iri-call-graph-layer")) == 5
    assert len(soup.select(".iri-scene--layered-call-graph [data-edge-from][data-edge-to]")) == 4

    starter = STARTER.read_text(encoding="utf-8")
    pipeline_rule = re.search(r"\.iri-pipeline\s*\{([^}]*)\}", starter, re.DOTALL)
    assert pipeline_rule
    assert "rotate(" not in pipeline_rule.group(1)
    for selector in ("iri-interaction-layout", "iri-layered-architecture", "iri-layered-call-graph"):
        rule = re.search(rf"\.{selector}\s*\{{([^}}]*)\}}", starter, re.DOTALL)
        assert rule
        assert "rotate(" not in rule.group(1)
        assert "skew(" not in rule.group(1)


def test_source_native_profile_title_challenge_and_timeline_scenes():
    from low_context import _render_iridescence_theme_slide

    profile = _scene_spec(slide_number=2, role="profile", title="个人介绍", items=[])
    profile["structured_content"] = {
        "kind": "personal-profile",
        "groups": [
            {
                "id": "identity",
                "label": "示例讲者",
                "description": "Demo Speaker",
                "items": ["示例研发负责人（虚构）"],
            },
            {
                "id": "credentials",
                "nodes": [
                    {"id": "award", "label": "示例创新奖（虚构）"},
                    {"id": "tokens", "label": "演示数据量 100 万条（虚构）"},
                    {"id": "tenure", "label": "示例工作经验 5 年（虚构）"},
                ],
            },
        ],
    }
    profile_soup = BeautifulSoup(_render_iridescence_theme_slide(profile, 32, role_index=1), "html.parser")
    assert profile_soup.select_one(".iri-scene--personal-profile")
    assert profile_soup.select_one('[data-group-id="identity"]')
    assert len(profile_soup.select(".iri-profile-fact[data-node-id]")) == 3

    title_only = _scene_spec(slide_number=3, role="title", title="问题一：进入职场独立完成第一个任务的挑战？", items=[])
    title_only["layout_id"] = "bento"
    title_only["structured_content"] = {"kind": "title-only"}
    title_soup = BeautifulSoup(_render_iridescence_theme_slide(title_only, 32, role_index=2), "html.parser")
    assert title_soup.select_one(".iri-scene--title-only")
    assert not title_soup.select(".iri-bento, .iri-lead, .iri-convergence-word")
    assert "用于验证评审修正。" not in title_soup.get_text(" ", strip=True)

    challenge = _scene_spec(slide_number=6, role="problem-complexity", title="真实场景", items=[])
    challenge["structured_content"] = {
        "kind": "challenge-flow",
        "direction": "left-to-right",
        "groups": [
            {
                "id": "challenges",
                "nodes": [{"id": f"challenge-{index}", "label": f"Challenge {index}"} for index in range(1, 6)],
            },
            {
                "id": "process",
                "label": "端到端流程",
                "nodes": [{"id": f"process-{index}", "label": f"Step {index}"} for index in range(1, 6)],
            },
        ],
        "edges": [
            {"from": f"process-{index}", "to": f"process-{index + 1}", "relation": "ordered-before", "label": "→"}
            for index in range(1, 5)
        ],
    }
    challenge_soup = BeautifulSoup(_render_iridescence_theme_slide(challenge, 32, role_index=5), "html.parser")
    assert len(challenge_soup.select(".iri-challenge-bar")) == 5
    assert len(challenge_soup.select(".iri-process-node")) == 5
    assert len(challenge_soup.select(".iri-process-edge[data-edge-from][data-edge-to]")) == 4

    timeline = _scene_spec(slide_number=7, role="timeline", title="企业生产力阶段", items=[])
    timeline["structured_content"] = {
        "kind": "milestone-timeline",
        "direction": "left-to-right",
        "groups": [
            {
                "id": "timeline",
                "nodes": [{"id": f"milestone-{index}", "label": f"Date {index}"} for index in range(1, 6)],
            }
        ],
        "edges": [
            {"from": f"milestone-{index}", "to": f"milestone-{index + 1}", "relation": "ordered-before", "label": "→"}
            for index in range(1, 5)
        ],
    }
    timeline_soup = BeautifulSoup(_render_iridescence_theme_slide(timeline, 32, role_index=6), "html.parser")
    assert len(timeline_soup.select(".iri-timeline-milestone")) == 5
    assert len(timeline_soup.select(".iri-timeline-edge[data-edge-from][data-edge-to]")) == 4
    assert "LAST MILE" not in " ".join(
        soup.get_text(" ", strip=True) for soup in (profile_soup, title_soup, challenge_soup, timeline_soup)
    )


def test_source_native_later_scene_hierarchies_do_not_fall_back_to_scene_cycle():
    from low_context import _render_iridescence_theme_slide

    fixtures = (
        (
            8,
            "enterprise-problem",
            "three-column-conclusion",
            [{"id": "problems", "nodes": [{"id": f"problem-{i}", "label": f"Problem {i}"} for i in range(3)]}],
            [{"id": "warning", "label": "Warning"}, {"id": "conclusion", "label": "Conclusion"}],
            ".iri-problem-column",
            3,
        ),
        (
            15,
            "capability-bridge",
            "capability-bridge",
            [{"id": "capabilities", "nodes": [{"id": f"capability-{i}", "label": f"Capability {i}"} for i in range(5)]}],
            [{"id": "bridge-conclusion", "label": "Conclusion"}],
            ".iri-bridge-column",
            5,
        ),
        (
            16,
            "context-package",
            "context-package",
            [
                {"id": "package", "label": "Package"},
                {"id": "components", "nodes": [{"id": f"component-{i}", "label": f"Component {i}"} for i in range(4)]},
            ],
            [{"id": "tool-directory", "label": "Tools"}],
            ".iri-context-package-card",
            4,
        ),
        (
            31,
            "takeaway",
            "takeaway-stack",
            [{"id": "principles", "label": "Enterprise AI framing", "nodes": [{"id": f"principle-{i}", "label": f"Principle {i}"} for i in range(4)]}],
            [
                {"id": "formula", "label": "Formula"},
                {"id": "result", "label": "Result"},
                {"id": "cta", "label": "CTA"},
            ],
            ".iri-takeaway-principle",
            4,
        ),
    )
    for slide_number, role, kind, groups, bands, selector, expected_count in fixtures:
        slide = _scene_spec(slide_number=slide_number, role=role, title=f"Slide {slide_number}", items=[])
        slide["structured_content"] = {"kind": kind, "groups": groups, "bands": bands}
        soup = BeautifulSoup(
            _render_iridescence_theme_slide(slide, 32, role_index=slide_number - 1),
            "html.parser",
        )
        assert soup.select_one(f".iri-scene--{kind}")
        assert len(soup.select(selector)) == expected_count
        if kind == "takeaway-stack":
            assert soup.select_one(".iri-takeaway-frame").get_text(" ", strip=True) == "Enterprise AI framing"
        assert not soup.select(".iri-convergence-word, .iri-pipeline, .iri-spectrum, .iri-use-cases")


def test_source_dense_page_contracts_preserve_p5_p12_p13_and_p17_evidence():
    from low_context import _render_iridescence_theme_slide

    p5 = _scene_spec(
        slide_number=5,
        role="interaction-case",
        title="Interaction flow",
        items=[],
    )
    p5["structured_content"] = {
        "kind": "interaction-flow-poll",
        "groups": [
            {
                "id": "task",
                "label": "Task",
                "source_refs": ["P5-task"],
                "nodes": [
                    {"id": "task-1", "label": "Start"},
                    {"id": "task-2", "label": "Extract"},
                    {"id": "task-3", "label": "Submit"},
                ],
            },
            {
                "id": "poll",
                "label": "Poll",
                "nodes": [
                    {"id": "poll-a", "label": "A"},
                    {"id": "poll-b", "label": "B"},
                ],
            },
        ],
        "edges": [
            {"from": "task-1", "to": "task-2", "relation": "ordered-before"},
            {"from": "task-2", "to": "task-3", "relation": "ordered-before"},
        ],
    }
    p5_soup = BeautifulSoup(_render_iridescence_theme_slide(p5, 32, role_index=4), "html.parser")
    assert len(p5_soup.select("#slide-5 .iri-interaction-step")) == 3
    assert len(p5_soup.select('#slide-5 .iri-poll[data-group-id="poll"]')) == 1
    assert len(p5_soup.select("#slide-5 .iri-poll-option")) == 2
    assert p5_soup.select_one('[data-group-id="task"][data-source-ref="P5-task"]')

    p12 = _scene_spec(slide_number=12, role="architecture-stack", title="Five layers", items=[])
    p12["structured_content"] = {
        "kind": "layered-architecture",
        "groups": [
            {"id": f"layer-{index}", "label": f"Layer {index}", "source_refs": [f"P12-{index}"]}
            for index in range(1, 6)
        ],
        "edges": [
            {"from": f"layer-{index}", "to": f"layer-{index + 1}", "relation": "feeds"}
            for index in range(1, 5)
        ],
        "rails": [
            {"id": "security-rail", "label": "Security"},
            {"id": "observability-rail", "label": "Observability"},
        ],
        "bands": [{"id": "runtime-loop", "label": "Runtime loop"}],
    }
    p12_soup = BeautifulSoup(_render_iridescence_theme_slide(p12, 32, role_index=11), "html.parser")
    assert len(p12_soup.select("#slide-12 .iri-layered-architecture-layer")) == 5
    assert len(p12_soup.select("#slide-12 .iri-architecture-rail")) == 2
    assert len(p12_soup.select("#slide-12 .iri-architecture-band")) == 1
    assert p12_soup.select_one('[data-edge-from="layer-1"][data-edge-to="layer-2"][data-relation="feeds"]')

    p13 = _scene_spec(slide_number=13, role="call-chain", title="Layered call graph", items=[])
    p13["structured_content"] = {
        "kind": "layered-call-graph",
        "groups": [
            {"id": "call-layer-1", "label": "LAYER1", "nodes": [{"id": "activity-workflow", "label": "Activity-Workflow"}]},
            {
                "id": "call-layer-2",
                "label": "LAYER2",
                "nodes": [{"id": "l2", "label": "L2"}, {"id": "l3", "label": "L3"}],
            },
            {"id": "call-layer-3", "label": "LAYER3", "nodes": [{"id": "supplier-flow", "label": "supplier flow"}]},
            {
                "id": "call-layer-4",
                "label": "LAYER4",
                "nodes": [
                    {"id": f"mcp-cluster-{index}", "label": f"MCP cluster {index}"}
                    for index in range(1, 5)
                ],
            },
            {"id": "saas-foundation", "label": "SaaS", "items": ["Foundation"]},
        ],
        "edges": [
            {"from": "call-layer-1", "to": "call-layer-2", "relation": "handoff", "label": "Activity handoff"},
            {"from": "call-layer-2", "to": "call-layer-3", "relation": "handoff", "label": "L2/L3 handoff"},
            {"from": "call-layer-3", "to": "call-layer-4", "relation": "handoff", "label": "supplier handoff"},
            {"from": "call-layer-4", "to": "saas-foundation", "relation": "handoff", "label": "SaaS handoff"},
            {"from": "l2", "to": "l3", "relation": "internal-call"},
            {"from": "mcp-cluster-1", "to": "mcp-cluster-2", "relation": "cluster-call"},
        ],
    }
    p13_soup = BeautifulSoup(_render_iridescence_theme_slide(p13, 32, role_index=12), "html.parser")
    p13_text = p13_soup.get_text(" ", strip=True)
    for expected in ("LAYER1", "LAYER2", "LAYER3", "LAYER4", "SaaS", "Activity-Workflow", "L2", "L3", "supplier flow"):
        assert expected in p13_text
    assert len(p13_soup.select('[data-node-id^="mcp-cluster-"]')) == 4
    assert len(p13_soup.select(".iri-call-graph-handoff[data-edge-from][data-edge-to][data-relation]")) == 4
    assert p13_soup.select_one(".iri-call-graph-layer--foundation[data-group-id='saas-foundation']")

    p17 = _scene_spec(
        slide_number=17,
        role="enterprise-context",
        title="Business and environment context",
        items=[f"Context {index}：Detail {index}" for index in range(1, 17)],
    )
    p17_soup = BeautifulSoup(_render_iridescence_theme_slide(p17, 32, role_index=16), "html.parser")
    business = p17_soup.select_one('[data-group-id="business-context"]')
    environment = p17_soup.select_one('[data-group-id="environment-context"]')
    assert business and environment
    assert [node["data-node-id"] for node in business.select("[data-node-id]")] == [
        f"business-context-{index}" for index in range(1, 9)
    ]
    assert [node["data-node-id"] for node in environment.select("[data-node-id]")] == [
        f"environment-context-{index}" for index in range(1, 9)
    ]


def test_relation_markers_are_stable_on_p20_p26_p27_p28_and_p29():
    from low_context import _render_iridescence_theme_slide

    p20 = _scene_spec(
        slide_number=20,
        role="dual-mode",
        title="Two modes",
        items=["Agent Loop：adaptive", "Workflow：fixed"],
    )
    p20_soup = BeautifulSoup(_render_iridescence_theme_slide(p20, 32, role_index=19), "html.parser")
    relation = p20_soup.select_one(
        '#slide-20 [data-group-id="dual-mode"][data-edge-from="agent-loop"]'
        '[data-edge-to="workflow"][data-relation="parallel-tracks"]'
    )
    assert relation
    assert {node["data-node-id"] for node in relation.select("[data-node-id]")} == {"agent-loop", "workflow"}

    routing = _scene_spec(
        slide_number=21,
        role="routing-comparison",
        title="Routing modes",
        items=["Agent route：adaptive", "Workflow route：fixed"],
    )
    routing_soup = BeautifulSoup(_render_iridescence_theme_slide(routing, 32, role_index=20), "html.parser")
    assert routing_soup.select_one('[data-group-id="routing-comparison"]')
    assert {node["data-node-id"] for node in routing_soup.select(".iri-dual-track")} == {
        "routing-agent-path",
        "routing-workflow-path",
    }

    workshop_items = [f"Card {index}：Choice {index}" for index in range(1, 13)]
    workshop_orders = []
    for slide_number, role in ((26, "workshop"), (27, "workshop-reveal")):
        spec = _scene_spec(slide_number=slide_number, role=role, title=role, items=workshop_items)
        soup = BeautifulSoup(_render_iridescence_theme_slide(spec, 32, role_index=slide_number - 1), "html.parser")
        group = soup.select_one('[data-group-id="workshop-cards"]')
        assert group
        order = [node["data-node-id"] for node in group.select(".iri-workshop-cell")]
        assert order == [f"workshop-card-{index:02d}" for index in range(1, 13)]
        workshop_orders.append(order)
    assert workshop_orders[0] == workshop_orders[1]

    p28 = _scene_spec(
        slide_number=28,
        role="capability-landscape",
        title="Capability landscape",
        items=[f"Module {index}：Detail {index}" for index in range(1, 7)]
        + ["Runtime：route and execute", "Foundation：models"],
    )
    p28_soup = BeautifulSoup(_render_iridescence_theme_slide(p28, 32, role_index=27), "html.parser")
    assert p28_soup.select_one('[data-group-id="capability-landscape"]')
    modules = p28_soup.select_one('[data-group-id="capability-modules"]')
    assert modules
    assert [node["data-node-id"] for node in modules.select(".iri-capability")] == [
        f"capability-module-{index:02d}" for index in range(1, 7)
    ]
    assert p28_soup.select_one(
        '[data-node-id="capability-foundation"][data-edge-from="capability-foundation"]'
        '[data-edge-to="capability-runtime"][data-relation="supports"]'
    )
    assert p28_soup.select_one(
        '[data-node-id="capability-runtime"][data-edge-from="capability-runtime"]'
        '[data-edge-to="capability-modules"][data-relation="executes"]'
    )

    p29 = _scene_spec(
        slide_number=29,
        role="enterprise-comparison",
        title="Enterprise comparison",
        items=[
            "OS Harness｜Open source",
            "Enterprise Harness｜Enterprise",
            *[f"Dimension {index}｜Open {index}｜Enterprise {index}" for index in range(1, 6)],
            "Conclusion：Execution responsibility matters",
        ],
    )
    p29_soup = BeautifulSoup(_render_iridescence_theme_slide(p29, 32, role_index=28), "html.parser")
    assert p29_soup.select_one('[data-group-id="enterprise-comparison-table"]')
    assert p29_soup.select_one(".iri-comparison-head").get_text(" ", strip=True) == "维度 OS Harness Open source Enterprise Harness Enterprise"
    assert p29_soup.select_one(".iri-comparison-conclusion").get_text(" ", strip=True) == "Conclusion Execution responsibility matters"
    rows = p29_soup.select('.iri-comparison-row[data-relation="row-aligned"]')
    assert len(rows) == 5
    for index, row in enumerate(rows, start=1):
        assert row["data-group-id"] == f"comparison-row-{index:02d}"
        assert row.select_one(f'[data-node-id="comparison-dimension-{index:02d}"]')
        assert row.select_one(f'[data-node-id="comparison-open-source-{index:02d}"]')
        assert row.select_one(f'[data-node-id="comparison-enterprise-{index:02d}"]')


def test_content_bearing_scene_css_is_orthogonal_and_has_no_inner_scrolling():
    starter = STARTER.read_text(encoding="utf-8")
    style = re.search(r"<style>(.*?)</style>", starter, re.DOTALL)
    assert style
    css = style.group(1)
    content_classes = (
        "iri-pipeline",
        "iri-bento",
        "iri-profile-layout",
        "iri-title-only",
        "iri-challenge-flow",
        "iri-challenge-list",
        "iri-process-strip",
        "iri-process-sequence",
        "iri-milestone-timeline",
        "iri-timeline-sequence",
        "iri-three-column-conclusion",
        "iri-problem-columns",
        "iri-conclusion-bands",
        "iri-capability-bridge",
        "iri-bridge-columns",
        "iri-context-package",
        "iri-context-package-grid",
        "iri-takeaway-stack",
        "iri-takeaway-principles",
        "iri-interaction-layout",
        "iri-interaction-flow",
        "iri-poll",
        "iri-layered-architecture",
        "iri-architecture-rails",
        "iri-architecture-bands",
        "iri-layered-call-graph",
        "iri-context-matrix",
        "iri-call-chain",
        "iri-dual-mode",
        "iri-workshop",
        "iri-capability-landscape",
        "iri-comparison-table",
    )
    assert "rotate(" not in css
    assert "skew(" not in css
    for selector, declarations in re.findall(r"([^{}]+)\{([^{}]*)\}", css, re.DOTALL):
        if any(f".{class_name}" in selector for class_name in content_classes):
            assert not re.search(r"overflow(?:-x|-y)?\s*:\s*(?:auto|scroll|hidden)", declarations)


def test_custom_theme_generation_eval_skips_missing_builtin_signature_contract():
    from low_context import render_from_brief
    from quality_eval import analyze_html_quality

    brief = _brief()
    html, packet, _ = render_from_brief(brief)

    report = analyze_html_quality(html, brief=brief, preset=packet["preset"])

    assert report["preset"] == "Fantasy Rainbow"
    assert report["diagnostics"]["style_signature_coverage"] is None
    assert report["diagnostics"]["style_signature_integrity"] is None


def test_iridescence_scene_primitives_count_as_real_eval_components():
    from low_context import render_from_brief
    from quality_eval import analyze_html_quality

    brief = _brief()
    html, packet, _ = render_from_brief(brief)
    report = analyze_html_quality(html, brief=brief, preset=packet["preset"])

    assert report["quality_gates"]["minimal-slide-run"] is True
    assert report["diagnostics"]["avg_component_kinds_per_slide"] >= 2.0


def _scene_spec(
    *,
    slide_number: int,
    role: str,
    title: str,
    items: list[str],
    title_emphasis: str = "",
    claim: str = "",
) -> dict:
    spec = {
        "slide_number": slide_number,
        "role": role,
        "layout_id": "column_content",
        "speaker_note": "review regression",
        "title": title,
        "key_point": "用于验证评审修正。",
        "supporting_facts": items,
        "numeric_facts": [],
        "supporting_items": [],
        "evidence_items": [],
    }
    if title_emphasis:
        spec["title_emphasis"] = title_emphasis
    if claim:
        spec["claim"] = claim
    return spec


def test_iridescence_cover_uses_structured_emphasis_for_arbitrary_business_copy():
    from low_context import render_from_brief

    brief = _brief()
    cover = brief["narrative"]["slides"][0]
    cover["title"] = "灵基 Lingee｜企业 AI 操作系统"
    cover["title_emphasis"] = "企业 AI 操作系统"

    html, _, _ = render_from_brief(brief)
    soup = BeautifulSoup(html, "html.parser")
    emphasis = soup.select("#slide-1 .iri-headline em.iri-accent-primary")

    assert len(emphasis) == 1
    assert emphasis[0].get_text(strip=True) == "企业 AI 操作系统"
    headline = soup.select_one("#slide-1 .iri-headline")
    assert headline.get_text(" ", strip=True) == "灵基 Lingee 企业 AI 操作系统"
    assert "｜" not in headline.get_text()
    assert [line.get_text("", strip=True) for line in headline.select(".iri-title-line")] == [
        "灵基 Lingee",
        "企业 AI 操作系统",
    ]


def test_iridescence_cover_fallback_emphasis_is_content_independent():
    from low_context import _render_iridescence_theme_slide

    soup = BeautifulSoup(
        _render_iridescence_theme_slide(
            _scene_spec(
                slide_number=1,
                role="cover",
                title="灵基 Lingee",
                items=["企业 AI 操作系统"],
            ),
            10,
            role_index=0,
        ),
        "html.parser",
    )

    emphasis = soup.select(".iri-headline em.iri-accent-primary")
    assert len(emphasis) == 1
    assert emphasis[0].get_text(strip=True) == "Lingee"


def test_iridescence_renderer_emits_restrained_accent_semantics():
    from low_context import _render_iridescence_theme_slide

    semantic_classes = {
        "iri-accent-primary",
        "iri-accent-secondary",
        "iri-accent-text-primary",
        "iri-accent-text-secondary",
        "iri-accent-text-tertiary",
        "iri-accent-tint-primary",
        "iri-accent-tint-secondary",
        "iri-accent-tint-tertiary",
        "iri-gate-accent-primary",
        "iri-gate-accent-secondary",
        "iri-gate-accent-tertiary",
        "iri-marker-primary",
        "iri-marker-secondary",
        "iri-marker-tertiary",
    }

    def accents(node) -> set[str]:
        return set(node.get("class", [])) & semantic_classes

    cover = BeautifulSoup(
        _render_iridescence_theme_slide(
            _scene_spec(
                slide_number=1,
                role="cover",
                title="把 AI 生成，变成可交付的演示文稿",
                items=["22 design presets", "16 review checkpoints"],
                title_emphasis="可交付",
            ),
            12,
            role_index=0,
        ),
        "html.parser",
    )
    assert cover.select_one(".iri-headline em.iri-accent-primary").get_text(strip=True) == "可交付"

    fracture = BeautifulSoup(
        _render_iridescence_theme_slide(
            _scene_spec(
                slide_number=2,
                role="problem",
                title="AI 会写内容，最后一步却最容易翻车",
                items=["context", "style", "validation"],
            ),
            12,
            role_index=1,
        ),
        "html.parser",
    )
    fracture_headings = fracture.select(".iri-fracture-side h3")
    assert len(fracture_headings) == 2
    assert all(accents(node) == {"iri-accent-text-primary"} for node in fracture_headings)

    convergence = BeautifulSoup(
        _render_iridescence_theme_slide(
            _scene_spec(
                slide_number=3,
                role="solution",
                title="真正需要保护的，是内容到成品的最后一公里",
                items=["brief", "preset", "runtime"],
            ),
            12,
            role_index=2,
        ),
        "html.parser",
    )
    assert convergence.select_one(".iri-convergence-word.iri-accent-primary")
    assert [accents(node) for node in convergence.select(".iri-fact-index")] == [
        {"iri-accent-text-primary"},
        {"iri-accent-text-secondary"},
        {"iri-accent-text-tertiary"},
    ]

    pipeline = BeautifulSoup(
        _render_iridescence_theme_slide(
            _scene_spec(
                slide_number=5,
                role="workflow",
                title="Prompt 到成品，只走一条可验证路径",
                items=["brief", "route", "render", "validate", "evaluate", "deliver"],
            ),
            12,
            role_index=4,
        ),
        "html.parser",
    )
    pipeline_numbers = pipeline.select(".iri-pipeline-step > span")
    assert len(pipeline_numbers) == 6
    assert all(accents(node) == {"iri-accent-text-primary"} for node in pipeline_numbers)
    assert [accents(node) for node in pipeline.select(".iri-pipeline-step:nth-child(2), .iri-pipeline-step:nth-child(4), .iri-pipeline-step:nth-child(5)")] == [
        {"iri-accent-tint-primary"},
        {"iri-accent-tint-secondary"},
        {"iri-accent-tint-tertiary"},
    ]

    deck_titles = [
        "把 AI 生成，变成可交付的演示文稿",
        "AI 会写内容，最后一步却最容易翻车",
        "真正需要保护的，是内容到成品的最后一公里",
        "把整段对话，压成一个短、硬、可执行的真相源",
        "Prompt 到成品，只走一条可验证路径",
        "风格选择不再靠猜：先看图，再落字",
        "22 种预设不是皮肤，而是 22 套布局契约",
        "严格检查，让问题停在交付之前",
        "输出本身就是演示工具，不是一次性截图",
        "Auto 负责速度，Polish 负责把质量锁住",
        "一条生成链，覆盖四类真实交付",
        "一句话安装，生成你的第一份 deck",
    ]
    deck_html = "".join(
        _render_iridescence_theme_slide(
            _scene_spec(
                slide_number=index + 1,
                role="cta" if index == 11 else "cover" if index == 0 else "content",
                title=title,
                items=["A", "B", "C", "D", "E", "F"],
                title_emphasis="第一份 deck" if index == 11 else "可交付" if index == 0 else "",
            ),
            12,
            role_index=index,
        )
        for index, title in enumerate(deck_titles)
    )
    deck = BeautifulSoup(deck_html, "html.parser")
    assert all(accents(node) == set() for node in deck.select("#slide-1 .iri-fact-index"))
    assert [accents(node) for node in deck.select(".iri-field .iri-number, .iri-field code")] == [
        {"iri-accent-text-primary"},
    ] * 10
    assert deck.select_one(".iri-spectrum-total.iri-accent-primary")
    assert all(accents(node) == set() for node in deck.select(".iri-spectrum-item"))
    assert [accents(node) for node in deck.select(".iri-spectrum-marker")[:4]] == [
        {"iri-marker-primary"},
        {"iri-marker-secondary"},
        {"iri-marker-tertiary"},
        {"iri-marker-primary"},
    ]
    assert [accents(node) for node in deck.select(".iri-spectrum-marker")[4:]] == [set(), set()]
    assert all(node.name == "span" and node.get("aria-hidden") == "true" for node in deck.select(".iri-spectrum-marker"))
    contract_numbers = deck.select(".iri-contract-layer .iri-number")
    assert len(contract_numbers) == 5
    assert all(accents(node) == {"iri-accent-text-primary"} for node in contract_numbers)
    assert [accents(node) for node in deck.select(".iri-gate")] == [
        {"iri-gate-accent-primary"},
        {"iri-gate-accent-secondary"},
        {"iri-gate-accent-tertiary"},
        {"iri-gate-accent-primary"},
    ]
    assert [accents(node) for node in deck.select(".iri-gate > span")] == [
        {"iri-accent-text-primary"},
        {"iri-accent-text-secondary"},
        {"iri-accent-text-tertiary"},
        {"iri-accent-text-primary"},
    ]
    assert [accents(node) for node in deck.select(".iri-runtime-screen strong > span")] == [
        {"iri-accent-primary"},
        {"iri-accent-secondary"},
        {"iri-accent-text-tertiary"},
    ]
    runtime_keys = deck.select(".iri-key b")
    assert len(runtime_keys) == 6
    assert all(accents(node) == {"iri-accent-text-primary"} for node in runtime_keys)
    assert [accents(node) for node in deck.select(".iri-mode .iri-number")] == [
        {"iri-accent-primary"},
        {"iri-accent-secondary"},
    ]
    assert [accents(node) for node in deck.select(".iri-quadrant .iri-number")] == [
        {"iri-accent-text-primary"},
        {"iri-accent-text-secondary"},
        {"iri-accent-text-tertiary"},
        {"iri-accent-text-primary"},
    ]
    assert deck.select_one(".iri-scene--closing .iri-headline em.iri-accent-primary").get_text(strip=True) == "第一份 deck"


def test_iridescence_title_emphasis_preserves_html_escaping():
    from low_context import _render_iridescence_theme_slide

    html = _render_iridescence_theme_slide(
        _scene_spec(
            slide_number=1,
            role="cover",
            title="把 AI 生成，变成可交付的 <script>",
            items=[],
        ),
        12,
        role_index=0,
    )
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_reviewed_scenes_remove_truncated_and_echoed_content():
    from low_context import _render_iridescence_theme_slide

    fracture = BeautifulSoup(
        _render_iridescence_theme_slide(
            _scene_spec(
                slide_number=2,
                role="problem",
                title="AI 会写内容，最后一步却最容易翻车",
                items=["上下文遗忘关键约束", "抽象风格难以落地", "错误打开浏览器后才发现"],
            ),
            12,
            role_index=1,
        ),
        "html.parser",
    )
    # Generic scenes must not pad with unrelated product-demo delivery claims.
    assert [node.get_text(strip=True) for node in fracture.select(".iri-fracture-item")] == [
        "上下文遗忘关键约束", "抽象风格难以落地", "错误打开浏览器后才发现",
    ]
    assert len(fracture.select(".iri-fracture-side h3")) == 2
    assert "打开即播放、验证即交付" not in fracture.get_text(" ", strip=True)

    brief = BeautifulSoup(
        _render_iridescence_theme_slide(
            _scene_spec(
                slide_number=4,
                role="definition",
                title="把整段对话，压成一个短、硬、可执行的真相源",
                items=[
                    "audience: 决定受众与期望动作",
                    "deck.style: 锁定页数、语言和 preset",
                    "content: 固定必须包含的事实与边界",
                    "narrative.slides: 逐页声明角色、断言和证据",
                    "runtime: 约束播放、编辑、备注与耗时",
                    "渲染器读取的是结构化 brief",
                ],
                claim='{"deck": {"style": "..."}, "content": {}, "narrative": {"slides": []}, "runtime": {}}',
            ),
            12,
            role_index=3,
        ),
        "html.parser",
    )
    assert [node.get_text(" ", strip=True) for node in brief.select(".iri-field code")] == [
        "audience",
        "deck.style",
        "content",
        "narrative.slides",
        "runtime",
    ]
    preview = brief.select_one(".iri-brief-code pre").get_text(" ", strip=True)
    assert json.loads(preview) == {"deck":{"style":"..."},"content":{},"narrative":{"slides":[]},"runtime":{}}
    assert '"desired_action"' not in preview
    assert '"page_roles"' not in preview
    assert "渲染器读取的是结构化" not in brief.get_text(" ", strip=True)

    runtime = BeautifulSoup(
        _render_iridescence_theme_slide(
            _scene_spec(
                slide_number=9,
                role="reliability",
                title="输出本身就是演示工具，不是一次性截图",
                items=["F5 — Present Mode", "P — Presenter Window", "E — Inline Editing", "Ctrl+S — Save", "NOTES — Speaker Notes", "← ↑ → ↓ — Keyboard Navigation"],
            ),
            12,
            role_index=8,
        ),
        "html.parser",
    )
    assert [node.get_text(" ", strip=True) for node in runtime.select(".iri-key b")] == [
        "F5",
        "P",
        "E",
        "Ctrl+S",
        "NOTES",
        "← ↑ → ↓",
    ]


def test_reviewed_titles_use_semantic_line_breaks_and_cover_only_runtime():
    from low_context import _render_iridescence_theme_slide

    cases = [
        (1, "problem", "AI 会写内容，最后一步却最容易翻车"),
        (2, "solution", "真正需要保护的，是内容到成品的最后一公里"),
        (3, "definition", "把整段对话，压成一个短、硬、可执行的真相源"),
        (10, "best-fit", "一条生成链，覆盖四类真实交付"),
        (11, "cta", "一句话安装，生成你的第一份 deck"),
    ]
    for role_index, role, title in cases:
        soup = BeautifulSoup(
            _render_iridescence_theme_slide(
                _scene_spec(slide_number=role_index + 1, role=role, title=title, items=["A", "B", "C", "D"]),
                12,
                role_index=role_index,
            ),
            "html.parser",
        )
        assert len(soup.select(".iri-title-line")) >= 2

    closing = BeautifulSoup(
        _render_iridescence_theme_slide(
            _scene_spec(
                slide_number=12,
                role="cta",
                title="一句话安装，生成你的第一份 deck",
                items=["A", "B"],
                title_emphasis="第一份 deck",
            ),
            12,
            role_index=11,
        ),
        "html.parser",
    )
    assert [node.get_text("", strip=True) for node in closing.select(".iri-title-line")] == [
        "一句话安装，",
        "生成你的第一份 deck",
    ]

    starter = STARTER.read_text(encoding="utf-8")
    assert "activeIndex()" in starter
    assert "isCoverActive()" in starter
    assert "this.active = this.isCoverActive();" in starter
    assert "seconds + this.activeIndex() * .61" not in starter


def test_iridescence_gpu_time_stays_precise_after_long_runtime():
    """Exercise the real upload expression, including all shipped runtimes."""
    import shutil
    import subprocess

    import pytest

    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required to exercise JavaScript float uploads")
    for path in (STARTER, ROOT / "demos/fantasy-rainbow-zh.html", ROOT / "demos/fantasy-rainbow-en.html"):
        html = path.read_text(encoding="utf-8")
        draw = re.search(r"    draw\(seconds\) \{(.*?)\n    \}", html, re.DOTALL)
        assert draw
        script = """
const assert = require('node:assert/strict');
let uploaded;
const controller = {
  ready: true, contextLost: false, resize: () => true,
  intervals: [], lastFrameAt: 0, drawCount: 0, canvas: {width: 1280, height: 720},
  uniforms: {time: 'time', resolution: 'resolution'},
  gl: {useProgram() {}, uniform1f(_, value) {uploaded = Math.fround(value)},
       uniform3f() {}, viewport() {}, drawArrays() {}}
};
const draw = new Function('seconds', DRAW_BODY).bind(controller);
const period = 4 * Math.PI;
for (const seconds of [0, 1, 60, 3600, 86400, 604800, 1e7, 1e9]) {
  assert.equal(draw(seconds), true);
  assert.ok(uploaded >= 0 && uploaded <= period);
  assert.ok(Math.abs(uploaded - seconds % period) < 1e-6);
}
// Both sides of the wrap represent adjacent angles, with no motion jump.
draw(period - 1e-5); const before = uploaded * .5;
draw(period + 1e-5); const after = uploaded * .5;
assert.ok(Math.abs(Math.sin(before) - Math.sin(after)) < 2e-5);
assert.ok(Math.abs(Math.cos(before) - Math.cos(after)) < 2e-5);
""".replace("DRAW_BODY", json.dumps(draw.group(1)))
        subprocess.run([node, "-e", script], check=True, capture_output=True, text=True)
