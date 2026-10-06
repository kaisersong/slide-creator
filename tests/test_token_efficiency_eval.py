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


def test_best_effort_language_policy_retains_quality_guard(tmp_path):
    (tmp_path/"manifest.json").write_text(json.dumps({"repetitions":1,"cases":[{"id":"technical"}]}))
    for arm, tokens in (("baseline",1000),("candidate3",200)):
        result = {"case_id":"technical","rep":1,"complete":True,"passed":True,
                  "technical":True,"evaluator_version":2,
                  "generation":{"total_tokens":tokens,"wall_ms":100},
                  "judge":{"complete":True,"quality_score":85,"technical_language_score":70},
                  "qa":{"strict_pass":True,"geometry_pass":True,"page_count_pass":True,
                        "quality_failures":[],"geometry_failures":[]}}
        path=tmp_path/arm/"technical/rep-1/result.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(result))
    assert not EVAL.compare(tmp_path,"candidate3")["adoption_gate"]["pass"]
    observed=EVAL.compare(tmp_path,"candidate3","observe")
    assert observed["adoption_gate"]["pass"]
    assert observed["acceptance_policy"]["version"] == 2
    path=tmp_path/"candidate3/technical/rep-1/result.json"
    result=json.loads(path.read_text())
    result["qa"]["geometry_pass"]=False
    path.write_text(json.dumps(result))
    assert not EVAL.compare(tmp_path,"candidate3","observe")["adoption_gate"]["pass"]
    result["qa"]["geometry_pass"]=True
    result["qa"]["missing_required_terms"]=["24"]
    path.write_text(json.dumps(result))
    assert "guard.technical.rep1.missing_required_terms.added" in EVAL.compare(tmp_path,"candidate3","observe")["adoption_gate"]["failures"]


def test_visual_refinement_compares_to_passed_candidate_without_requiring_another_token_cut(tmp_path):
    (tmp_path/"manifest.json").write_text(json.dumps({"repetitions":1,"cases":[{"id":"visual"}]}))
    for arm,tokens in (("candidate5",200),("candidate6",205)):
        result={"case_id":"visual","rep":1,"complete":True,"passed":True,"technical":False,"evaluator_version":2,"generation":{"total_tokens":tokens,"wall_ms":100},"judge":{"complete":True,"quality_score":90},"qa":{"strict_pass":True,"geometry_pass":True,"page_count_pass":True,"quality_failures":[],"geometry_failures":[],"missing_required_terms":[]}}
        path=tmp_path/arm/"visual/rep-1/result.json";path.parent.mkdir(parents=True);path.write_text(json.dumps(result))
    comparison=EVAL.compare(tmp_path,"candidate6","observe","candidate5")
    assert comparison["adoption_gate"]["pass"]
    assert comparison["acceptance_policy"]["baseline_arm"]=="candidate5"
    assert (tmp_path/"comparison.candidate6.vs.candidate5.json").exists()
