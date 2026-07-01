from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from preset_capabilities import CANONICAL_PRESET_NAMES, PRESET_REFERENCE_MAP  # noqa: E402
from preset_contracts import (  # noqa: E402
    check_preset_contract_html,
    load_preset_contract,
    load_preset_manifest,
    slug_for_preset,
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
      <body class="profile-aurora-mesh">
        <section class="slide" data-export-role="cover" data-notes="cover: 产品发布">
          <h1>产品发布</h1>
          <p>可见正文</p>
          <div class="aurora-card" style="display:none">隐藏卡片</div>
          <div class="aurora-badge"></div>
        </section>
      </body>
    </html>
    """

    result = check_preset_contract_html(html, "Aurora Mesh")

    assert result["pass"] is False
    assert "contract-required-visible-component-missing" in result["hard_failures"]
    assert any("aurora-card" in item["selectors"] for item in result["violations"])


def test_contract_checker_accepts_minimal_visible_profile_components():
    contract = load_preset_contract("Aurora Mesh")
    component_html = "\n".join(
        f'<div class="{component["selectors"][0].lstrip(".")}">{component["name"]}</div>'
        for component in contract["required_visible_components"]
    )
    html = f"""
    <!doctype html>
    <html>
      <body class="profile-aurora-mesh">
        <section class="slide" data-export-role="cover" data-notes="cover: 产品发布">
          <h1>产品发布</h1>
          <p>可见正文</p>
          {component_html}
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
        assert schema["type"] == "object"
        assert "preset" in schema["required"]
