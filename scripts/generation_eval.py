from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from quality_eval import analyze_html_quality


def default_eval_output_path(output_path: str | Path) -> Path:
    target = Path(output_path)
    return target.with_name(f"{target.stem}.eval.json")


def build_generation_eval_report(
    *,
    html_text: str,
    brief: dict[str, Any],
    packet: dict[str, Any],
    html_path: str | Path,
) -> dict[str, Any]:
    report = analyze_html_quality(
        html_text,
        brief=brief,
        preset=packet.get("preset"),
    )
    diagnostics = report.get("diagnostics", {})
    gates = report.get("quality_gates", {})
    report["html_path"] = str(html_path)
    report["render_packet"] = {
        "preset": packet.get("preset"),
        "preset_support_tier": packet.get("preset_support_tier"),
        "quality_tier": packet.get("quality_tier"),
        "runtime_path": packet.get("runtime_path"),
        "render_path": packet.get("render_path"),
        "brief_hash": packet.get("brief_hash"),
    }
    report["summary"] = {
        "style_score": diagnostics.get("style_signature_coverage"),
        "layout_variety": diagnostics.get("layout_variety"),
        "layout_role_variety": diagnostics.get("layout_role_variety"),
        "visual_family_variety": diagnostics.get("visual_family_variety"),
        "visual_signature_variety": diagnostics.get("visual_signature_variety"),
        "avg_component_kinds_per_slide": diagnostics.get("avg_component_kinds_per_slide"),
        "minimal_slide_ratio": diagnostics.get("minimal_slide_ratio"),
        "quality_tier": diagnostics.get("quality_tier"),
        "hard_failure_count": len(report.get("hard_failures", [])),
        "quality_gates_passed": sorted(key for key, passed in gates.items() if passed),
        "quality_gates_failed": sorted(key for key, passed in gates.items() if not passed),
    }
    return report


def write_generation_eval_report(path: str | Path, report: dict[str, Any]) -> Path:
    target = Path(path)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target
