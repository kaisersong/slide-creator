from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from pptx import Presentation


ROOT = Path(__file__).resolve().parent.parent

HARD_FAILURES = {
    "command_failed": "pptx-export-command-failed",
    "missing_output": "pptx-export-missing-output",
    "too_small": "pptx-export-output-too-small",
    "unreadable": "pptx-export-unreadable",
    "slide_count": "pptx-export-slide-count-mismatch",
}


def _slugify(text: str) -> str:
    import re

    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "deck"


def _html_slide_count(path: Path) -> int:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    return len(soup.select(".slide"))


def _default_export_script() -> Path:
    script_env = os.environ.get("KAI_HTML_EXPORT_SCRIPT")
    if script_env:
        return Path(script_env).expanduser().resolve()
    export_dir = Path(os.environ.get("KAI_HTML_EXPORT_DIR", "/Users/song/projects/kai-html-export")).expanduser()
    return (export_dir / "scripts" / "export-pptx.py").resolve()


def _read_pptx(path: Path) -> tuple[int | None, str | None]:
    try:
        prs = Presentation(path)
    except Exception as exc:  # pragma: no cover - defensive corrupt pptx path
        return None, str(exc)
    return len(prs.slides), None


def _violation(code: str, message: str, **extra: Any) -> dict[str, Any]:
    return {"code": code, "type": code.removeprefix("pptx-export-"), "severity": "hard", "message": message, **extra}


def run_pptx_export_smoke(
    html_path: str | Path,
    *,
    preset: str,
    output_dir: str | Path | None = None,
    export_script: str | Path | None = None,
    mode: str = "image",
    width: int = 1280,
    height: int = 720,
    scale: int = 1,
    timeout_seconds: int = 180,
) -> dict[str, Any]:
    path = Path(html_path).resolve()
    out_dir = Path(output_dir).resolve() if output_dir else path.parent / "pptx-export-smoke"
    out_dir.mkdir(parents=True, exist_ok=True)
    pptx_path = out_dir / f"{_slugify(preset)}.pptx"
    script = Path(export_script).resolve() if export_script else _default_export_script()
    html_slide_count = _html_slide_count(path)
    violations: list[dict[str, Any]] = []

    command = [
        sys.executable,
        str(script),
        str(path),
        str(pptx_path),
        "--mode",
        mode,
        "--width",
        str(width),
        "--height",
        str(height),
        "--scale",
        str(scale),
    ]

    try:
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        completed = subprocess.CompletedProcess(command, 124, stdout=exc.stdout or "", stderr=exc.stderr or "timeout")

    if completed.returncode != 0:
        violations.append(
            _violation(
                HARD_FAILURES["command_failed"],
                "kai-html-export PPTX command failed",
                returncode=completed.returncode,
            )
        )

    file_size = pptx_path.stat().st_size if pptx_path.exists() else 0
    if not pptx_path.exists():
        violations.append(_violation(HARD_FAILURES["missing_output"], "PPTX output file was not created"))
    elif file_size < 1_000:
        violations.append(
            _violation(
                HARD_FAILURES["too_small"],
                "PPTX output file is too small to be credible",
                file_size=file_size,
            )
        )

    pptx_slide_count = None
    pptx_read_error = None
    if pptx_path.exists():
        pptx_slide_count, pptx_read_error = _read_pptx(pptx_path)
        if pptx_read_error:
            violations.append(
                _violation(HARD_FAILURES["unreadable"], "PPTX output cannot be opened", error=pptx_read_error)
            )
        elif pptx_slide_count != html_slide_count:
            violations.append(
                _violation(
                    HARD_FAILURES["slide_count"],
                    "PPTX slide count does not match HTML slide count",
                    expected=html_slide_count,
                    actual=pptx_slide_count,
                )
            )

    hard_failures: list[str] = []
    for violation in violations:
        code = str(violation["code"])
        if code not in hard_failures:
            hard_failures.append(code)

    return {
        "version": 1,
        "phase": "1.0-real-pptx-export-smoke",
        "preset": preset,
        "html_path": str(path),
        "pptx_path": str(pptx_path),
        "export_script": str(script),
        "command": subprocess.list2cmdline(command),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "pass": not violations,
        "hard_failures": hard_failures,
        "violations": violations,
        "diagnostics": {
            "mode": mode,
            "width": width,
            "height": height,
            "scale": scale,
            "html_slide_count": html_slide_count,
            "pptx_slide_count": pptx_slide_count,
            "pptx_file_size": file_size,
        },
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run a real HTML-to-PPTX export smoke gate.")
    parser.add_argument("html_path")
    parser.add_argument("--preset", required=True)
    parser.add_argument("--output-dir")
    parser.add_argument("--export-script")
    parser.add_argument("--mode", default="image", choices=["image", "native"])
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--scale", type=int, default=1)
    parser.add_argument("--timeout-seconds", type=int, default=180)
    parser.add_argument("--output")
    args = parser.parse_args()

    report = run_pptx_export_smoke(
        args.html_path,
        preset=args.preset,
        output_dir=args.output_dir,
        export_script=args.export_script,
        mode=args.mode,
        width=args.width,
        height=args.height,
        scale=args.scale,
        timeout_seconds=args.timeout_seconds,
    )
    if args.output:
        Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
