from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from promotion_gate import run_promotion_gate, validate_release_report_routes  # noqa: E402


def test_promotion_gate_passes_current_support_matrix_and_contracts():
    report = run_promotion_gate()

    assert report["pass"] is True
    assert report["hard_failures"] == []
    assert report["diagnostics"]["native_count"] == 5
    assert report["diagnostics"]["profile_count"] == 17


def test_promotion_gate_rejects_profile_preset_claimed_as_native():
    release_report = {
        "cases": [
            {
                "case_id": "aurora-mesh-profile-render",
                "preset": "Aurora Mesh",
                "packet": {
                    "renderer_strategy": "native",
                    "preset_generation_status": "ready",
                    "render_path": "brief-canonical",
                },
            }
        ]
    }

    route_report = validate_release_report_routes(release_report)

    assert route_report["pass"] is False
    assert "promotion-profile-renderer-claimed-native" in route_report["hard_failures"]


def test_promotion_gate_rejects_native_core_rendered_as_profile():
    release_report = {
        "cases": [
            {
                "case_id": "swiss-modern-native-render",
                "preset": "Swiss Modern",
                "packet": {
                    "renderer_strategy": "unified_profile",
                    "preset_generation_status": "profile",
                    "render_path": "profile:swiss-modern",
                },
            }
        ]
    }

    route_report = validate_release_report_routes(release_report)

    assert route_report["pass"] is False
    assert "promotion-native-renderer-regressed" in route_report["hard_failures"]
