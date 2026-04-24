from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SWISS_REF = ROOT / "references" / "swiss-modern.md"

GENERIC = {
    "slide", "reveal", "visible", "grid", "body", "html", "card", "container",
    "content-box", "slide-content", "slide-image", "progress-bar", "nav-dots",
    "edit-hotzone", "edit-toggle", "notes-panel", "notes-body", "notes-textarea",
    "notes-panel-header", "notes-panel-label", "notes-drag-hint",
    "notes-collapse-btn", "slide-credit", "presenting", "presenting-black",
    "p-on", "title-slide", "show", "active", "collapsed",
}


def test_swiss_reference_exposes_user_content_layout_palette():
    content = SWISS_REF.read_text(encoding="utf-8")

    assert "### 8. User-Content 12-Page Route" in content
    for required in [
        ".left-panel",
        ".disc-step",
        ".data-table",
        ".feat-card",
        ".inst-block",
        ".cta-block",
    ]:
        assert required in content, f"Swiss Modern reference missing {required}"

    assert "--bg-primary" in content, (
        "Swiss Modern should explicitly forbid renamed token aliases like --bg-primary"
    )
    assert "data-export-role" in content, (
        "Swiss Modern should document per-slide export roles for native exporter fidelity"
    )


def test_swiss_reference_defines_canonical_export_contract():
    content = SWISS_REF.read_text(encoding="utf-8")

    assert "### 9. Canonical Export Contract" in content
    for required in [
        "title_grid",
        "column_content",
        "stat_block",
        "pull_quote",
        ".slide > .slide-content > .left-col/.right-col",
        ".bg-num",
        ".slide-num-label",
        "--text-primary",
        "--accent",
    ]:
        assert required in content, f"Swiss Modern canonical export contract missing {required}"


def test_swiss_named_layout_class_mentions_are_backed_by_css_or_signature():
    content = SWISS_REF.read_text(encoding="utf-8")
    sig_start = content.find("## Signature Elements")
    named_start = content.find("## Named Layout Variations")

    assert sig_start != -1 and named_start != -1

    pre_sig = content[:sig_start]
    named_section = content[named_start:sig_start]
    contract_start = named_section.find("### 9. Canonical Export Contract")
    if contract_start != -1:
        named_section = named_section[:contract_start]
    sig_section = content[sig_start:]

    defined = {
        match.group(1)
        for match in re.finditer(r"\.([a-z][a-z0-9_-]*)\s*\{", pre_sig)
        if match.group(1) not in GENERIC
    }

    declared = set()
    for section_name in ["Required CSS Classes", "Allowed Components"]:
        match = re.search(rf"### {section_name}\n(.*?)(?=\n###|\n---|\Z)", sig_section, re.DOTALL)
        if match:
            declared |= {
                item.group(1)
                for item in re.finditer(r"\.([a-z][a-z0-9_-]*)", match.group(1))
                if item.group(1) not in GENERIC
            }

    mentioned = {
        match.group(1)
        for match in re.finditer(r"\.([a-z][a-z0-9_-]*)", named_section)
        if len(match.group(1)) > 2 and match.group(1) not in GENERIC
    }

    missing = sorted(mentioned - defined - declared)
    assert not missing, (
        "Swiss Modern named layouts reference classes that are not backed by CSS or "
        f"signature declarations: {missing}"
    )
