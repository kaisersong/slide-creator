from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from preset_contracts import load_preset_contract  # noqa: E402


HARD_FAILURES = {
    "slot_missing": "export-smoke-missing-slot",
    "slide_role_missing": "export-smoke-slide-role-missing",
    "empty_slide": "export-smoke-empty-slide",
}

REQUIRED_SLOTS = ("slide", "title", "body", "speaker_notes")


def _selector_list(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return []


def _select(soup: BeautifulSoup, selectors: list[str]) -> list[Any]:
    matches: list[Any] = []
    seen: set[int] = set()
    for selector in selectors:
        try:
            selected = soup.select(selector)
        except Exception:
            selected = []
        for node in selected:
            marker = id(node)
            if marker not in seen:
                seen.add(marker)
                matches.append(node)
    return matches


def run_export_smoke(
    html_path: str | Path,
    *,
    preset: str,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    path = Path(html_path)
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    contract = load_preset_contract(preset)
    mapping = contract.get("export_dom_mapping", {})
    violations: list[dict[str, Any]] = []
    slot_counts: dict[str, int] = {}

    for slot, selector_value in mapping.items():
        selectors = _selector_list(selector_value)
        count = len(_select(soup, selectors))
        slot_counts[slot] = count
        if slot in REQUIRED_SLOTS and count == 0:
            violations.append(
                {
                    "code": HARD_FAILURES["slot_missing"],
                    "type": "slot_missing",
                    "slot": slot,
                    "selectors": ", ".join(selectors),
                    "severity": "hard",
                }
            )

    slide_selectors = _selector_list(mapping.get("slide", "section.slide"))
    slides = _select(soup, slide_selectors)
    for index, slide in enumerate(slides, start=1):
        if not slide.get("data-export-role"):
            violations.append(
                {
                    "code": HARD_FAILURES["slide_role_missing"],
                    "type": "slide_role_missing",
                    "slide_index": index,
                    "severity": "hard",
                }
            )
        if not (slide.get_text(" ", strip=True) or "").strip():
            violations.append(
                {
                    "code": HARD_FAILURES["empty_slide"],
                    "type": "empty_slide",
                    "slide_index": index,
                    "severity": "hard",
                }
            )

    hard_failures: list[str] = []
    for violation in violations:
        code = str(violation["code"])
        if code not in hard_failures:
            hard_failures.append(code)

    report = {
        "version": 1,
        "phase": "1.0-export-structure-smoke",
        "preset": contract["preset"],
        "html_path": str(path),
        "pass": not violations,
        "hard_failures": hard_failures,
        "violations": violations,
        "diagnostics": {
            "slide_count": len(slides),
            "slot_counts": slot_counts,
            "required_slots": list(REQUIRED_SLOTS),
        },
    }

    if output_dir:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        report["artifact_dir"] = str(out_dir)
    return report


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run slide-creator export DOM smoke validation.")
    parser.add_argument("html_path")
    parser.add_argument("--preset", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    report = run_export_smoke(args.html_path, preset=args.preset)
    if args.output:
        Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
