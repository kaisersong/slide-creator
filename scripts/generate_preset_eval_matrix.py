#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from preset_capabilities import CANONICAL_PRESET_NAMES


ROOT = Path(__file__).resolve().parent.parent
SUITE_DIR = ROOT / "evals" / "preset-surface-all"
MANIFEST_PATH = SUITE_DIR / "manifest.json"
BASE_BRIEF_PATH = ROOT / "evals" / "preset-surface-phase1" / "cases" / "core-swiss-modern-brief.json"
POLISH_BRIEF_PATH = ROOT / "demos" / "mode-paths" / "polish-BRIEF.json"
SHAPES = (
    ("minimal", "cases/minimal-brief.json"),
    ("representative-12-role", "cases/representative-12-role-brief.json"),
    ("image-heavy-restyle", "cases/image-heavy-restyle-brief.json"),
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _render_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def _minimal_brief(base: dict[str, Any]) -> dict[str, Any]:
    brief = copy.deepcopy(base)
    brief["brief_id"] = "preset-surface-all-minimal"
    selected = [base["narrative"]["slides"][index] for index in (0, 1, 4, 6, 7)]
    slides = []
    for slide_number, source in enumerate(selected, start=1):
        slide = copy.deepcopy(source)
        slide["slide_number"] = slide_number
        slides.append(slide)
    brief["deck"]["page_count"] = len(slides)
    brief["narrative"]["slides"] = slides
    brief["narrative"]["page_roles"] = [slide["role"] for slide in slides]
    brief["notes"] = "Minimal five-page matrix input with short and CJK titles."
    return brief


def _representative_brief(base: dict[str, Any]) -> dict[str, Any]:
    brief = copy.deepcopy(base)
    brief["brief_id"] = "preset-surface-all-representative-12-role"
    brief["narrative"]["slides"][-1]["role"] = "synthesis"
    brief["narrative"]["slides"][-1]["visual"] = "synthesis signal"
    additions = [
        {
            "role": "benchmark",
            "title": "🧭 用同一把尺子比较速度、质量与返工",
            "key_point": "评测必须同时观察交付耗时、验收通过率和返工轮次，避免只优化单一指标",
            "visual": "benchmark dashboard",
        },
        {
            "role": "governance",
            "title": "跨团队推广前，需要把职责、证据、失败回退与版本边界写成同一份可执行约定",
            "key_point": "清晰的责任边界和失败回退机制，决定自动化链路能否从局部试验进入稳定运营",
            "visual": "governance map",
        },
        {
            "role": "next_step",
            "title": "下一步只扩展相邻高频场景",
            "key_point": "先复用已经通过门禁的输入、模板和评测，再逐步增加新的场景复杂度",
            "visual": "three-step roadmap",
        },
        {
            "role": "closing",
            "title": "稳定复用，胜过即兴自动化",
            "key_point": "把可验证工作流沉淀成默认路径，团队才能持续获得 agent 交付的复利",
            "visual": "closing signal",
        },
    ]
    for slide_number, addition in enumerate(additions, start=9):
        brief["narrative"]["slides"].append({"slide_number": slide_number, **addition})
    brief["deck"]["page_count"] = 12
    brief["narrative"]["page_roles"] = [slide["role"] for slide in brief["narrative"]["slides"]]
    brief["notes"] = "Representative 12-role input with short, long, CJK, and emoji titles."
    return brief


def _image_heavy_brief() -> dict[str, Any]:
    brief = copy.deepcopy(_read_json(POLISH_BRIEF_PATH))
    brief["brief_id"] = "preset-surface-all-image-heavy-restyle"
    brief["notes"] = (
        "Polish-mode image plan is asset-only context; generated content must remain in real content DOM."
    )
    return brief


def _fixture_documents() -> dict[Path, dict[str, Any]]:
    base = _read_json(BASE_BRIEF_PATH)
    return {
        SUITE_DIR / "cases" / "minimal-brief.json": _minimal_brief(base),
        SUITE_DIR / "cases" / "representative-12-role-brief.json": _representative_brief(base),
        SUITE_DIR / "cases" / "image-heavy-restyle-brief.json": _image_heavy_brief(),
    }


def _canonical_presets() -> list[str]:
    return list(dict.fromkeys(CANONICAL_PRESET_NAMES.values()))


def _template_cases(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    templates: dict[str, dict[str, Any]] = {}
    for case in manifest["cases"]:
        if case.get("input_shape") not in (None, "minimal"):
            continue
        templates[case["preset"]] = case
    missing = sorted(set(_canonical_presets()) - set(templates))
    extra = sorted(set(templates) - set(_canonical_presets()))
    if missing or extra:
        raise ValueError(f"preset template mismatch: missing={missing}, extra={extra}")
    return templates


def _shape_case_id(base_case_id: str, shape: str) -> str:
    if shape == "minimal":
        return base_case_id
    suffix = f"-{shape}-render"
    return base_case_id[:-7] + suffix if base_case_id.endswith("-render") else base_case_id + suffix


def _generated_manifest(current: dict[str, Any]) -> dict[str, Any]:
    templates = _template_cases(current)
    generated = {key: copy.deepcopy(value) for key, value in current.items() if key != "cases"}
    generated["workflow"] = [
        "BRIEF.json",
        "capability packet",
        "HTML",
        "strict validate",
        "preset fidelity",
        "runtime fidelity when declared",
        "desktop and mobile browser geometry",
        "quality eval",
    ]
    cases: list[dict[str, Any]] = []
    for preset in _canonical_presets():
        template = templates[preset]
        for shape, brief_path in SHAPES:
            case = copy.deepcopy(template)
            case["case_id"] = _shape_case_id(template["case_id"], shape)
            case["brief_path"] = brief_path
            case["input_shape"] = shape
            case["run_contract"] = True
            case["run_browser_geometry"] = True
            case["run_mobile_geometry"] = True
            cases.append(case)
    generated["cases"] = cases
    return generated


def _check_document(path: Path, expected: dict[str, Any]) -> bool:
    return path.exists() and path.read_text(encoding="utf-8") == _render_json(expected)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the registry-complete preset eval matrix.")
    parser.add_argument("--check", action="store_true", help="Fail if generated artifacts are stale.")
    args = parser.parse_args()

    current = _read_json(MANIFEST_PATH)
    fixtures = _fixture_documents()
    manifest = _generated_manifest(current)
    documents = {**fixtures, MANIFEST_PATH: manifest}

    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, value in documents.items() if not _check_document(path, value)]
        if stale:
            print("stale preset eval matrix artifacts:")
            for path in stale:
                print(f"- {path}")
            return 1
        print(f"preset eval matrix is current: {len(manifest['cases'])} cases")
        return 0

    for path, value in documents.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_render_json(value), encoding="utf-8")
    print(f"generated preset eval matrix: {len(manifest['cases'])} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
