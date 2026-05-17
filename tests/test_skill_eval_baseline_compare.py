import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "compare-skill-eval-baseline.py"


def write_payload(path: Path, case_score: int, passed: bool, artifact_dir: str) -> None:
    path.write_text(
        json.dumps(
            {
                "cases": [
                    {
                        "case_id": "explicit-generate",
                        "total_score": case_score,
                        "passed": passed,
                        "eval_complete": passed,
                        "scores": {
                            "outcome": 25 if passed else 0,
                            "process": 25,
                            "style": 25,
                            "efficiency": 25,
                        },
                        "failures": [] if passed else ["outcome.missing_html_artifact"],
                        "metrics": {
                            "runner": "fixture",
                            "wall_ms": 45000,
                            "artifact_dir": artifact_dir,
                        },
                        "artifact_dir": artifact_dir,
                    }
                ],
                "summary": {
                    "total": 1,
                    "passed": 1 if passed else 0,
                    "failed": 0 if passed else 1,
                    "incomplete": 0 if passed else 1,
                    "average_score": case_score,
                    "average_category_scores": {
                        "outcome": 25 if passed else 0,
                        "process": 25,
                        "style": 25,
                        "efficiency": 25,
                    },
                },
            }
        ),
        encoding="utf-8",
    )


def run_compare(old_path: Path, new_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--old",
            str(old_path),
            "--new",
            str(new_path),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        timeout=20,
    )


def test_baseline_compare_reports_score_pass_and_completeness_regressions(tmp_path: Path):
    old_path = tmp_path / "old.json"
    new_path = tmp_path / "new.json"
    write_payload(old_path, case_score=100, passed=True, artifact_dir="/tmp/a")
    write_payload(new_path, case_score=65, passed=False, artifact_dir="/tmp/b")

    result = run_compare(old_path, new_path)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["summary_delta"]["average_score"] == -35
    assert payload["summary_delta"]["passed"] == -1
    assert payload["summary_delta"]["incomplete"] == 1
    assert payload["case_deltas"][0]["total_score"] == -35
    assert "case.explicit-generate.pass_regressed" in payload["regressions"]
    assert "case.explicit-generate.completeness_regressed" in payload["regressions"]
    assert "case.explicit-generate.outcome_regressed" in payload["regressions"]


def test_baseline_compare_ignores_volatile_artifact_paths(tmp_path: Path):
    old_path = tmp_path / "old.json"
    new_path = tmp_path / "new.json"
    write_payload(old_path, case_score=100, passed=True, artifact_dir="/tmp/old")
    write_payload(new_path, case_score=100, passed=True, artifact_dir="/tmp/new")

    result = run_compare(old_path, new_path)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["regressions"] == []
    assert payload["case_deltas"][0]["total_score"] == 0
