import importlib.util
import json
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("token_eval", Path(__file__).parents[1] / "scripts/token-efficiency-eval.py")
EVAL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVAL)


def test_usage_is_cumulative_not_double_counted(tmp_path):
    path = tmp_path / "trace.jsonl"
    receipt = {"type":"turn.completed", "usage":{"input_tokens":100,"cached_input_tokens":60,"output_tokens":20}}
    path.write_text(json.dumps(receipt) + "\n" + json.dumps(receipt) + "\n")
    result = EVAL.parse_trace(path)
    assert result["total_tokens"] == 120
    assert result["uncached_input_tokens"] == 40
    assert result["usage_receipts"] == 2


def test_missing_usage_is_not_zero(tmp_path):
    path = tmp_path / "trace.jsonl"
    path.write_text('{"type":"turn.failed"}\n')
    result = EVAL.parse_trace(path)
    assert result["total_tokens"] is None
    assert result["cached_input_tokens"] is None
    assert not result["completed"]
    assert result["errors"]


def test_corrupt_tail_preserves_partial_evidence(tmp_path):
    path = tmp_path / "trace.jsonl"
    path.write_text('{"type":"turn.failed"}\n{')
    assert EVAL.parse_trace(path)["malformed_lines"] == 1


def test_snapshot_contains_runtime_and_refuses_replacement(tmp_path):
    import pytest
    root = Path(__file__).parents[1]
    out = tmp_path / "baseline"
    EVAL.freeze(root, out, "9e999874b2107c3a8a727962151c61d275f74bf3")
    assert (out / "scripts/validate_html.py").exists()
    assert not (out / "evals").exists()
    with pytest.raises(ValueError):
        EVAL.freeze(root, out)


def test_generation_prompt_does_not_override_reference_budget():
    prompt = EVAL.generation_prompt({"request":"create a deck", "source":"facts"})
    assert "No artificial limit" in prompt
    assert "at most 3" not in prompt


def test_compare_cli_cannot_pass_with_missing_evidence(tmp_path):
    import subprocess
    import sys
    (tmp_path/"manifest.json").write_text(json.dumps({"repetitions":1,"cases":[{"id":"missing"}]}))
    result=subprocess.run([sys.executable,str(Path(EVAL.__file__)),"compare","--run-dir",str(tmp_path)],capture_output=True,text=True)
    assert result.returncode==1
    payload=json.loads(result.stdout)
    assert not payload["adoption_gate"]["pass"]
    assert "baseline.planned_runs_missing_or_extra" in payload["adoption_gate"]["failures"]
