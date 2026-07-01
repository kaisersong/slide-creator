from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "compare_demo_parity.py"
sys.path.insert(0, str(ROOT / "scripts"))

import compare_demo_parity  # noqa: E402


def _write_html(path: Path, *, classes: str, css_extra: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""<!doctype html>
<html>
<head>
<title>Demo</title>
<style>
:root {{
  --bg: #f7f0df;
  --ink: #211612;
  --accent: #9b1c1f;
  --rule: #9b1c1f;
}}
body {{ font-family: "Inter", "Space Grotesk", sans-serif; color: var(--ink); }}
.layout {{ display: grid; grid-template-columns: 1fr 1fr; }}
.{classes.split()[0]} {{ color: #9b1c1f; }}
{css_extra}
</style>
</head>
<body data-preset="Synthetic">
<section class="slide {classes}">
  <h1 class="{classes}">Synthetic parity target</h1>
  <p>One clear sentence for a stable style comparison.</p>
</section>
</body>
</html>
""",
        encoding="utf-8",
    )


def test_demo_parity_scores_component_vocabulary_separately(tmp_path: Path):
    demo_dir = tmp_path / "demos"
    candidate_dir = tmp_path / "candidates"
    output_dir = tmp_path / "out"
    _write_html(demo_dir / "paper-ink-en.html", classes="paper-title ink-rule drop-cap editorial-rule")
    _write_html(candidate_dir / "paper-ink-profile-render" / "deck.html", classes="generic-title generic-card")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--candidate-dir",
            str(candidate_dir),
            "--demo-dir",
            str(demo_dir),
            "--output-dir",
            str(output_dir),
            "--preset",
            "Paper & Ink",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads((output_dir / "demo-parity-report.json").read_text(encoding="utf-8"))
    paper = report["results"][0]
    assert paper["component_score"] < 0.5
    assert paper["main_issue"] == "component vocabulary diverges"
    assert paper["verdict"] != "PASS"


def test_demo_parity_fails_when_required_candidate_deck_is_missing(tmp_path: Path):
    demo_dir = tmp_path / "demos"
    candidate_dir = tmp_path / "candidates"
    output_dir = tmp_path / "out"
    _write_html(demo_dir / "paper-ink-en.html", classes="paper-title ink-rule")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--candidate-dir",
            str(candidate_dir),
            "--demo-dir",
            str(demo_dir),
            "--output-dir",
            str(output_dir),
            "--preset",
            "Paper & Ink",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode != 0
    assert "missing candidate deck" in (result.stdout + result.stderr).lower()


def test_demo_parity_json_contains_thresholds_and_visual_capture_state(tmp_path: Path):
    demo_dir = tmp_path / "demos"
    candidate_dir = tmp_path / "candidates"
    output_dir = tmp_path / "out"
    _write_html(demo_dir / "paper-ink-en.html", classes="paper-title ink-rule")
    _write_html(candidate_dir / "paper-ink-profile-render" / "deck.html", classes="paper-title ink-rule")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--candidate-dir",
            str(candidate_dir),
            "--demo-dir",
            str(demo_dir),
            "--output-dir",
            str(output_dir),
            "--preset",
            "Paper & Ink",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads((output_dir / "demo-parity-report.json").read_text(encoding="utf-8"))
    assert report["thresholds"]["overall_pass_min"] == 0.72
    assert report["summary"]["preset_count"] == 1
    assert "visual_capture" in report
    assert report["results"][0]["preset"] == "Paper & Ink"


def test_demo_parity_visual_gate_changes_verdict_after_screenshot_metrics():
    item = {
        "preset": "Creative Voltage",
        "verdict": "PASS",
        "main_issue": "minor parity drift",
        "assessment": "Candidate keeps enough historical style signals for parity.",
        "desktop_visual_similarity": 0.2074,
        "mobile_visual_similarity": 0.5608,
    }

    compare_demo_parity.apply_visual_gate(
        [item],
        visual={"available": True},
        viewports=["desktop", "mobile"],
        require_visual=True,
    )

    assert item["verdict"] == "FAIL"
    assert item["main_issue"] == "visual parity diverges"
    assert item["visual_gate"]["failures"]
    assert item["visual_gate"]["warnings"]


def test_demo_parity_required_visual_fails_closed_when_capture_unavailable():
    item = {
        "preset": "Paper & Ink",
        "verdict": "PASS",
        "main_issue": "minor parity drift",
        "assessment": "Candidate keeps enough historical style signals for parity.",
    }

    compare_demo_parity.apply_visual_gate(
        [item],
        visual={"available": False, "reason": "playwright unavailable"},
        viewports=["desktop"],
        require_visual=True,
    )

    assert item["verdict"] == "FAIL"
    assert "visual capture unavailable" in item["visual_gate"]["failures"][0]


def test_demo_parity_checks_required_component_instances(tmp_path: Path):
    candidate = tmp_path / "terminal-green-profile-render" / "deck.html"
    _write_html(candidate, classes="terminal-window terminal-line")

    failures = compare_demo_parity.preset_instance_failures("Terminal Green", candidate)

    assert failures == ["missing required component instance .terminal-scanlines"]
