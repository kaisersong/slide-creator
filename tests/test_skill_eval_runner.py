import json
import subprocess
import sys
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "run-skill-evals.py"
FIXTURES = ROOT / "tests" / "fixtures" / "skill-evals"


def run_script(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(ROOT), *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_runner_module():
    spec = importlib.util.spec_from_file_location("run_skill_evals", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_prompt_manifest_paths_exist():
    manifest = ROOT / "evals" / "slide-skill-prompts.csv"
    assert manifest.exists()
    for line in manifest.read_text(encoding="utf-8").splitlines()[1:]:
        fields = line.split(",")
        assert (ROOT / fields[3]).is_file(), fields[3]


def test_rubric_schema_parses():
    schema = json.loads((ROOT / "evals" / "skill-run-rubric.schema.json").read_text(encoding="utf-8"))
    assert schema["title"] == "kai-slide-creator captured-run style rubric"
    assert "narrative_arc" in schema["properties"]["checks"]["items"]["properties"]["id"]["enum"]


def test_fixture_runner_scores_all_cases_with_four_categories(tmp_path: Path):
    result = run_script(
        "--runner",
        "fixture",
        "--artifact-dir",
        str(tmp_path),
        "--format",
        "json",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["summary"]["total"] == 6
    assert payload["summary"]["passed"] == 6
    assert payload["summary"]["failed"] == 0
    assert payload["summary"]["average_score"] == 100
    assert payload["summary"]["average_category_scores"]["style"] == 25
    for category in ["outcome", "process", "style", "efficiency"]:
        assert category in payload["summary"]["average_category_scores"]
        assert payload["summary"]["average_category_scores"][category] > 0


def test_fixture_runner_scores_success_case_and_style_fixture(tmp_path: Path):
    result = run_script(
        "--runner",
        "fixture",
        "--case-id",
        "explicit-generate",
        "--normalized-trace",
        str(FIXTURES / "explicit-generate-normalized.json"),
        "--artifact-dir",
        str(tmp_path),
        "--format",
        "json",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    case = payload["cases"][0]
    assert case["scores"] == {
        "outcome": 25,
        "process": 25,
        "style": 25,
        "efficiency": 25,
    }
    assert case["total_score"] == 100
    assert case["passed"] is True
    assert case["eval_complete"] is True
    assert case["style_rubric"]["source"] == "fixture"
    assert case["style_rubric"]["score"] >= 90
    assert case["metrics"]["runner"] == "fixture"
    assert len(case["metrics"]["shell_commands"]) == 2
    assert case["metrics"]["input_tokens"] == 12000
    assert case["metrics"]["output_tokens"] == 3400
    assert "style.rubric_missing" not in case["failures"]


def test_positive_case_without_style_rubric_is_eval_incomplete(tmp_path: Path):
    result = run_script(
        "--runner",
        "fixture",
        "--case-id",
        "explicit-generate",
        "--normalized-trace",
        str(FIXTURES / "explicit-generate-normalized.json"),
        "--artifact-dir",
        str(tmp_path),
        "--disable-fixture-style-rubric",
        "--format",
        "json",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    case = payload["cases"][0]
    assert case["scores"]["style"] == 15
    assert case["total_score"] == 90
    assert case["passed"] is False
    assert case["eval_complete"] is False
    assert "style.rubric_missing" in case["failures"]
    assert "eval.style_rubric_missing" in case["failures"]


def test_negative_case_allows_skill_contract_read_for_routing(tmp_path: Path):
    result = run_script(
        "--runner",
        "fixture",
        "--case-id",
        "negative-report",
        "--normalized-trace",
        str(FIXTURES / "negative-report-normalized.json"),
        "--artifact-dir",
        str(tmp_path),
        "--format",
        "json",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    case = payload["cases"][0]
    assert case["scores"] == {
        "outcome": 25,
        "process": 25,
        "style": 25,
        "efficiency": 25,
    }
    assert case["total_score"] == 100
    assert case["passed"] is True


def test_outcome_hard_gate_prevents_clean_process_from_passing(tmp_path: Path):
    result = run_script(
        "--runner",
        "fixture",
        "--case-id",
        "explicit-generate",
        "--normalized-trace",
        str(FIXTURES / "thrashy-normalized.json"),
        "--artifact-dir",
        str(tmp_path),
        "--format",
        "json",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    case = payload["cases"][0]
    assert case["passed"] is False
    assert case["scores"]["outcome"] == 0
    assert "outcome.missing_html_artifact" in case["failures"]
    assert "efficiency.repeated_failed_command" in case["failures"]


def test_codex_raw_trace_normalizes_real_command_events(tmp_path: Path):
    result = run_script(
        "--runner",
        "codex",
        "--case-id",
        "negative-report",
        "--raw-trace",
        str(FIXTURES / "real-codex-tool-smoke.jsonl"),
        "--artifact-dir",
        str(tmp_path),
        "--format",
        "json",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    case = payload["cases"][0]
    assert case["metrics"]["runner"] == "codex"
    assert case["metrics"]["shell_commands"] == ["/bin/zsh -lc pwd"]
    assert case["metrics"]["input_tokens"] == 38572
    assert case["metrics"]["output_tokens"] == 384
    assert "codex.event_error" in case["metrics"]["runner_warnings"][0]


def test_codex_rg_no_match_is_not_counted_as_failed_shell_command(tmp_path: Path):
    result = run_script(
        "--runner",
        "codex",
        "--case-id",
        "negative-report",
        "--raw-trace",
        str(FIXTURES / "real-codex-rg-no-match.jsonl"),
        "--artifact-dir",
        str(tmp_path),
        "--format",
        "json",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    case = payload["cases"][0]
    assert case["metrics"]["failed_shell_commands"] == []
    assert case["scores"]["efficiency"] == 25


def test_codex_live_prompt_uses_isolated_budgeted_worker_protocol():
    runner = load_runner_module()
    row = {
        "id": "explicit-generate",
        "prompt_path": "evals/skill-prompts/explicit-generate.md",
    }

    prompt = runner.build_codex_live_prompt(ROOT, row, ROOT / ".tmp-run" / "skill-live-codex" / "explicit-generate")

    for marker in [
        "You are an isolated eval worker for exactly one kai-slide-creator case.",
        "Do not inherit or rely on coordinator conversation context.",
        "Maximum shell commands: 12.",
        "Read at most 3 reference files.",
        "Do not run broad repo searches.",
        "Do not inspect `tests/`, `demos/`, `evals/baselines/`, previous eval traces, or existing decks.",
        "Do not write under `evals/artifacts/current/` and do not create symlinks.",
        "Do not run `python3 main.py --help`, `python3 main.py --plan`, Python introspection, heredocs, or command discovery.",
        "Do not create `style-rubric.json`; a separate style judge produces it.",
        "If the request belongs to another skill, do not follow the generation flow; do not generate a deck artifact.",
        "Use `references/brief-template.json` as the brief schema reference for positive generation cases.",
        "Write lowercase `brief.json` under",
        "python3 main.py --validate-brief --brief",
        "python3 main.py --generate --brief",
        "python3 scripts/validate_html.py",
        "do not repeat the same failed command.",
        "Stop after strict validation.",
    ]:
        assert marker in prompt


def test_design_docs_document_captured_run_eval_architecture():
    doc_path = "docs/design/2026-05-17-slide-creator-captured-run-eval-architecture.md"
    index = read("docs/design/README.md")
    doc = read(doc_path)

    assert Path(doc_path).name in index
    for marker in [
        "Supervisor",
        "Generate Worker",
        "Style Judge",
        "fresh isolated worker",
        "Do not inspect `tests/`, `demos/`, `evals/baselines/`, previous eval traces, or existing decks.",
        "All generation-worker token costs count toward Efficiency.",
    ]:
        assert marker in doc


def test_readmes_document_captured_run_skill_evals():
    readme_en = read("README.md")
    readme_zh = read("README.zh-CN.md")
    for marker in [
        "scripts/run-skill-evals.py",
        "--runner codex",
        "--runner fixture",
        "Outcome",
        "Process",
        "Style",
        "Efficiency",
    ]:
        assert marker in readme_en
    for marker in [
        "scripts/run-skill-evals.py",
        "--runner codex",
        "--runner fixture",
        "Outcome",
        "Process",
        "Style",
        "Efficiency",
        "四类目标",
    ]:
        assert marker in readme_zh
