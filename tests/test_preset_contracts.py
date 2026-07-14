from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from preset_capabilities import CANONICAL_PRESET_NAMES, PRESET_REFERENCE_MAP  # noqa: E402
from preset_contracts import (  # noqa: E402
    check_preset_contract_html,
    load_preset_contract,
    load_preset_manifest,
    manifest_projection,
    slug_for_preset,
    validate_preset_fidelity,
)
from preset_profile_specs import PROFILE_SPECS  # noqa: E402


REQUIRED_CONTRACT_FIELDS = {
    "contract_version",
    "preset",
    "support_state",
    "renderer_strategy",
    "renderer_version",
    "source_reference",
    "fonts",
    "tokens",
    "layout_families",
    "required_visible_components",
    "critical_selectors",
    "decorative_selectors",
    "non_critical_selectors",
    "allowed_overlaps",
    "forbidden_substitutions",
    "typography_policy",
    "background_strategy",
    "export_dom_mapping",
    "browser_qa_policy",
    "demo_parity_minimum_score",
}

REQUIRED_MANIFEST_FIELDS = {
    "version",
    "preset",
    "support_state",
    "fonts",
    "tokens",
    "layout_families",
    "signature_components",
    "required_visible_components",
    "decorative_selectors",
    "non_critical_selectors",
    "forbidden_substitutions",
}

REQUIRED_EXPORT_SLOTS = {
    "slide",
    "title",
    "subtitle",
    "body",
    "list_items",
    "code",
    "quote",
    "stat",
    "image",
    "speaker_notes",
}


def _builtin_presets() -> list[str]:
    return [
        CANONICAL_PRESET_NAMES[normalized]
        for normalized in sorted(PRESET_REFERENCE_MAP)
    ]


def test_all_builtin_presets_have_contract_and_manifest_files():
    for preset in _builtin_presets():
        slug = slug_for_preset(preset)
        assert (ROOT / "references" / "preset-contracts" / f"{slug}.json").exists(), preset
        assert (ROOT / "references" / "preset-manifests" / f"{slug}.json").exists(), preset


def test_contract_and_manifest_files_include_required_fields():
    for preset in _builtin_presets():
        contract = load_preset_contract(preset)
        manifest = load_preset_manifest(preset)

        assert REQUIRED_CONTRACT_FIELDS <= set(contract), preset
        assert REQUIRED_MANIFEST_FIELDS <= set(manifest), preset
        assert contract["preset"] == preset
        assert manifest["preset"] == preset
        assert REQUIRED_EXPORT_SLOTS <= set(contract["export_dom_mapping"]), preset
        assert contract["source_reference"].startswith("references/"), preset
        assert contract["demo_parity_minimum_score"] >= 0.8


def test_profile_contracts_require_real_visible_signature_components():
    for preset in sorted(PROFILE_SPECS):
        contract = load_preset_contract(preset)
        manifest = load_preset_manifest(preset)
        names = [item["name"] for item in contract["required_visible_components"]]
        assert len(names) >= 4, preset
        assert set(names) <= set(manifest["signature_components"]), preset


def test_contracts_do_not_require_known_decorative_or_optional_profile_classes():
    optional_by_preset = {
        "Aurora Mesh": {"aurora-divider"},
        "Terminal Green": {"preset-grid"},
        "Vintage Editorial": {"rule", "rule-thick", "editorial-rule"},
    }

    for preset, optional_names in optional_by_preset.items():
        contract = load_preset_contract(preset)
        required = {item["name"] for item in contract["required_visible_components"]}
        assert not (required & optional_names), preset


def test_terminal_green_export_mapping_includes_terminal_title_selectors():
    contract = load_preset_contract("Terminal Green")

    assert ".t-h1" in contract["export_dom_mapping"]["title"]
    assert ".t-h2" in contract["export_dom_mapping"]["title"]


def test_contract_checker_rejects_hidden_or_empty_required_component():
    html = """
    <!doctype html>
    <html>
      <body class="profile-aurora-mesh" data-preset="Aurora Mesh">
        <section class="slide profile-slide" data-export-role="cover" data-notes="cover: 产品发布">
          <div class="profile-content preset-aurora-mesh-content" style="display:none">
            <h1 class="profile-fit-title aurora-title">产品发布</h1>
            <p>隐藏正文</p>
          </div>
        </section>
      </body>
    </html>
    """

    result = check_preset_contract_html(html, "Aurora Mesh")

    assert result["pass"] is False
    assert "contract-required-visible-component-missing" in result["hard_failures"]
    assert any(".profile-content" in item.get("selectors", "") for item in result["violations"])


def test_contract_checker_accepts_minimal_visible_profile_components():
    html = f"""
    <!doctype html>
    <html>
      <body class="profile-aurora-mesh" data-preset="Aurora Mesh">
        <section class="slide profile-slide" data-page-bucket="cover" data-export-role="cover" data-notes="cover: 产品发布">
          <div class="profile-content preset-aurora-mesh-content">
            <h1 class="profile-fit-title">产品发布</h1>
            <p>可见正文</p>
          </div>
        </section>
        <section class="slide profile-slide" data-page-bucket="content" data-export-role="content" data-notes="content: 核心能力">
          <div class="profile-content preset-aurora-mesh-content">
            <h2 class="profile-fit-title aurora-title">核心能力</h2>
            <p>真实内容节点</p>
          </div>
        </section>
        <section class="slide profile-slide" data-page-bucket="closing" data-export-role="closing" data-notes="closing: 下一步">
          <div class="profile-content preset-aurora-mesh-content">
            <h2 class="profile-fit-title aurora-title">下一步</h2><p>开始执行</p>
          </div>
        </section>
      </body>
    </html>
    """

    result = check_preset_contract_html(html, "Aurora Mesh")

    assert result["pass"] is True
    assert result["hard_failures"] == []


def test_preset_contract_schemas_are_json_documents():
    for schema_path in [
        ROOT / "schemas" / "preset-contract.schema.json",
        ROOT / "schemas" / "preset-manifest.schema.json",
    ]:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        assert schema["type"] == "object"
        assert "preset" in schema["required"]


def test_all_contracts_and_manifests_validate_against_their_schemas():
    contract_schema = json.loads(
        (ROOT / "schemas" / "preset-contract.schema.json").read_text(encoding="utf-8")
    )
    manifest_schema = json.loads(
        (ROOT / "schemas" / "preset-manifest.schema.json").read_text(encoding="utf-8")
    )
    registry = Registry().with_resource(
        contract_schema["$id"],
        Resource.from_contents(contract_schema),
    )
    contract_validator = Draft202012Validator(contract_schema)
    manifest_validator = Draft202012Validator(manifest_schema, registry=registry)

    for preset in _builtin_presets():
        contract_validator.validate(load_preset_contract(preset))
        manifest_validator.validate(load_preset_manifest(preset))


def test_blue_sky_contract_is_the_authoritative_style_and_runtime_source():
    contract = load_preset_contract("Blue Sky")
    manifest = load_preset_manifest("Blue Sky")

    assert contract["style_fidelity"]["minimum_coverage"] >= 0.8
    assert contract["style_fidelity"]["minimum_integrity"] == 1.0
    assert any(
        group["content_required"]
        for group in contract["style_fidelity"]["required_selector_groups"]
    )
    assert contract["runtime_fidelity"]["runtime_owner"] == "blue-sky-stage-track"
    assert manifest == manifest_projection(contract)


def test_blue_sky_reference_demos_and_native_product_use_one_fidelity_function():
    for language in ("en", "zh"):
        html = (ROOT / "demos" / f"blue-sky-{language}.html").read_text(encoding="utf-8")
        report = validate_preset_fidelity(html, "Blue Sky", mode="reference")
        assert report["pass"], report
        assert report["style"]["metrics"]["coverage"] >= 0.85


def test_blue_sky_fidelity_rejects_hidden_empty_and_single_page_signature_dump():
    shell = """<!doctype html><html><body data-preset="Blue Sky">
      <div id="stage"><div id="track">
        <section class="slide" data-page-bucket="cover"><h1>Title</h1>
          <div class="cloud-layer"><div class="cloud-strip"><div class="cloud-puff"></div></div></div>
          <div class="g">Visible cover-only signature</div>
        </section>
        <section class="slide" data-page-bucket="content"><h2>Content</h2><p>Generic body</p></section>
        <section class="slide" data-page-bucket="content"><h2>Content</h2><div class="bento" hidden>Hidden marker</div></section>
        <section class="slide" data-page-bucket="closing"><h2>Close</h2><div class="info"></div></section>
      </div></div>
    </body></html>"""

    report = validate_preset_fidelity(shell, "Blue Sky", mode="reference")

    assert report["pass"] is False
    assert "style-signature-integrity-low" in report["hard_failures"]
    assert "style-signature-slide-distribution-low" in report["hard_failures"]


def test_every_builtin_contract_has_bounded_canonical_style_groups():
    allowed_group_fields = {
        "name",
        "selectors",
        "match",
        "scope",
        "page_buckets",
        "weight",
        "minimum_group_score",
        "minimum_bucket_count",
        "content_required",
    }
    for preset in _builtin_presets():
        contract = load_preset_contract(preset)
        style = contract["style_fidelity"]
        groups = style["required_selector_groups"]
        assert groups, preset
        assert any(group["content_required"] for group in groups), preset
        assert all(set(group) <= allowed_group_fields for group in groups), preset
        assert "minimum_slide_ratio" not in json.dumps(style), preset
        assert load_preset_manifest(preset) == manifest_projection(contract), preset
