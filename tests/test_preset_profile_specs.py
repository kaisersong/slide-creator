from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


def test_every_profile_renderer_preset_has_profile_spec():
    from preset_profile_renderer import PROFILE_FAMILY_REGISTRY
    from preset_profile_specs import PROFILE_SPECS

    assert set(PROFILE_SPECS) == set(PROFILE_FAMILY_REGISTRY)


def test_profile_specs_have_signature_classes_and_layouts():
    from preset_profile_specs import PROFILE_SPECS

    for preset, spec in PROFILE_SPECS.items():
        assert spec.signature_classes, preset
        assert spec.required_component_classes, preset
        assert spec.layout_sequence, preset
        assert "--bg" in spec.css_vars or any(key.startswith("--bg") for key in spec.css_vars), preset


def test_non_signal_specs_do_not_use_generic_purple_shell_tokens():
    from preset_profile_specs import PROFILE_SPECS

    historically_purple = {"Aurora Mesh", "Bold Signal", "Creative Voltage", "Electric Studio", "Glassmorphism"}
    forbidden = {"#667eea", "#764ba2", "#f093fb"}
    for preset, spec in PROFILE_SPECS.items():
        if preset in historically_purple:
            continue
        assert forbidden.isdisjoint({value.lower() for value in spec.css_vars.values()}), preset
