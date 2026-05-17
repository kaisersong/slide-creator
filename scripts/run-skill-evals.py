#!/usr/bin/env python3
"""Run captured-run skill evals for kai-slide-creator."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
import time
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class NormalizedTraceMetrics:
    runner: str
    trace_format_version: str
    tool_calls: list[dict[str, Any]]
    shell_commands: list[str]
    failed_shell_commands: list[str]
    read_paths: list[str]
    write_paths: list[str]
    artifact_paths: list[str]
    input_tokens: int | None
    output_tokens: int | None
    wall_ms: int
    skill_evidence: dict[str, bool]
    runner_warnings: list[str]


@dataclass(frozen=True)
class SkillEvalCase:
    case_id: str
    total_score: int
    passed: bool
    eval_complete: bool
    scores: dict[str, int]
    failures: list[str]
    metrics: dict[str, Any]
    artifact_dir: str
    style_rubric: dict[str, Any] | None


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def bool_field(row: dict[str, str], key: str) -> bool:
    return row[key].strip().lower() == "true"


def int_field(row: dict[str, str], key: str, default: int) -> int:
    value = row.get(key, "").strip()
    return int(value) if value else default


def _suffix_match(paths: list[str], suffix: str) -> bool:
    normalized_suffix = suffix.replace("\\", "/").lstrip("./")
    return any(path.replace("\\", "/").lstrip("./").endswith(normalized_suffix) for path in paths)


def _contains_any(values: list[str], needles: list[str]) -> bool:
    haystack = "\n".join(values)
    return any(needle in haystack for needle in needles)


def _infer_paths_from_command(command: str) -> list[str]:
    return re.findall(
        r"(?:SKILL\.md|BRIEF\.json|brief\.json|references/[^\s'\";]+\.(?:md|html)|scripts/[^\s'\";]+\.py|main\.py)",
        command,
    )


def _is_failed_shell_command(command: str, exit_code: Any) -> bool:
    if exit_code in (None, 0):
        return False
    # `rg` returns 1 for no matches. In this harness it is often used as a
    # negative assertion for forbidden output patterns, so do not treat that as
    # command thrashing unless it fails with a harder error code.
    if exit_code == 1 and re.search(r"(^|[\s'\"])(rg|ripgrep)(\s|$)", command):
        return False
    return True


def _path_or_command_has_brief(paths: list[str], commands: list[str]) -> bool:
    return any(path.endswith(("BRIEF.json", "brief.json")) for path in paths) or _contains_any(
        commands,
        ["BRIEF.json", "brief.json", "scripts/render-from-brief.py", "main.py --generate"],
    )


def _infer_skill_evidence(
    read_paths: list[str],
    write_paths: list[str],
    artifact_paths: list[str],
    commands: list[str],
) -> dict[str, bool]:
    skill_contract_read = _suffix_match(read_paths, "SKILL.md") or _contains_any(commands, ["SKILL.md"])
    strict_validate_observed = _contains_any(commands, ["scripts/validate_html.py", "validate_html.py"]) and _contains_any(
        commands,
        ["--strict"],
    )
    brief_observed = _path_or_command_has_brief(read_paths + write_paths, commands)
    slide_flow_observed = (
        strict_validate_observed
        or brief_observed
        or any(path.endswith(".html") for path in write_paths)
        or any(path.endswith(".html") for path in artifact_paths)
    )
    return {
        "skill_contract_read": skill_contract_read,
        "slide_flow_observed": slide_flow_observed,
        "brief_observed": brief_observed,
        "strict_validate_observed": strict_validate_observed,
    }


def load_normalized_trace(path: Path) -> NormalizedTraceMetrics:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return NormalizedTraceMetrics(
        runner=str(payload.get("runner") or "fixture"),
        trace_format_version=str(payload.get("trace_format_version") or "normalized-v1"),
        tool_calls=list(payload.get("tool_calls") or []),
        shell_commands=list(payload.get("shell_commands") or []),
        failed_shell_commands=list(payload.get("failed_shell_commands") or []),
        read_paths=list(payload.get("read_paths") or []),
        write_paths=list(payload.get("write_paths") or []),
        artifact_paths=list(payload.get("artifact_paths") or []),
        input_tokens=payload.get("input_tokens"),
        output_tokens=payload.get("output_tokens"),
        wall_ms=int(payload.get("wall_ms") or 0),
        skill_evidence=dict(payload.get("skill_evidence") or {}),
        runner_warnings=list(payload.get("runner_warnings") or []),
    )


def normalize_codex_events(events: list[dict[str, Any]], wall_ms: int = 0) -> NormalizedTraceMetrics:
    shell_commands: list[str] = []
    failed_shell_commands: list[str] = []
    read_paths: list[str] = []
    write_paths: list[str] = []
    tool_calls: list[dict[str, Any]] = []
    runner_warnings: list[str] = []
    input_tokens: int | None = None
    output_tokens: int | None = None

    for event in events:
        usage = event.get("usage")
        if isinstance(usage, dict):
            if usage.get("input_tokens") is not None:
                input_tokens = int(usage["input_tokens"])
            if usage.get("output_tokens") is not None:
                output_tokens = int(usage["output_tokens"])

        item = event.get("item")
        if not isinstance(item, dict):
            continue
        item_type = item.get("type")
        if item_type == "error":
            message = str(item.get("message") or "")
            runner_warnings.append(f"codex.event_error:{message[:120]}")
            continue
        if item_type == "command_execution":
            command = str(item.get("command") or "")
            if event.get("type") == "item.completed" and command:
                shell_commands.append(command)
                read_paths.extend(_infer_paths_from_command(command))
                exit_code = item.get("exit_code")
                if _is_failed_shell_command(command, exit_code):
                    failed_shell_commands.append(command)
            tool_calls.append(
                {
                    "type": "command_execution",
                    "command": command,
                    "exit_code": item.get("exit_code"),
                    "status": item.get("status"),
                }
            )
            continue
        if item_type == "file_read":
            path = str(item.get("path") or "")
            if path:
                read_paths.append(path)
        elif item_type == "file_write":
            path = str(item.get("path") or "")
            if path:
                write_paths.append(path)

    artifact_paths = [path for path in write_paths if path.endswith(".html")]
    skill_evidence = _infer_skill_evidence(read_paths, write_paths, artifact_paths, shell_commands)
    return NormalizedTraceMetrics(
        runner="codex",
        trace_format_version="codex-jsonl-v1",
        tool_calls=tool_calls,
        shell_commands=shell_commands,
        failed_shell_commands=failed_shell_commands,
        read_paths=sorted(set(read_paths)),
        write_paths=write_paths,
        artifact_paths=artifact_paths,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        wall_ms=wall_ms,
        skill_evidence=skill_evidence,
        runner_warnings=runner_warnings,
    )


def _resolve_existing_path(root: Path, path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else root / path


def html_files_for_case(root: Path, metrics: NormalizedTraceMetrics, artifact_dir: Path) -> list[Path]:
    candidates: list[Path] = []
    candidates.extend(sorted(artifact_dir.rglob("*.html")) if artifact_dir.exists() else [])
    for path_text in metrics.artifact_paths + metrics.write_paths:
        if not path_text.endswith(".html"):
            continue
        path = _resolve_existing_path(root, path_text)
        if path.exists() and path not in candidates:
            candidates.append(path)
    return candidates


def html_text_for_case(root: Path, metrics: NormalizedTraceMetrics, artifact_dir: Path) -> str:
    html_files = html_files_for_case(root, metrics, artifact_dir)
    if not html_files:
        return ""
    return html_files[0].read_text(encoding="utf-8", errors="replace")


def _slide_count(html_text: str) -> int:
    return len(re.findall(r"<section\b[^>]*class=[\"'][^\"']*\bslide\b", html_text))


def score_outcome(
    root: Path,
    row: dict[str, str],
    metrics: NormalizedTraceMetrics,
    artifact_dir: Path,
) -> tuple[int, list[str]]:
    should_trigger = bool_field(row, "should_trigger")
    html_files = html_files_for_case(root, metrics, artifact_dir)

    if not should_trigger:
        if html_files or any(path.endswith(".html") for path in metrics.write_paths):
            return 0, ["outcome.negative_case_generated_deck"]
        return 25, []

    if not html_files:
        return 0, ["outcome.missing_html_artifact"]

    failures: list[str] = []
    score = 10
    html_text = html_files[0].read_text(encoding="utf-8", errors="replace")
    if metrics.skill_evidence.get("strict_validate_observed"):
        score += 5
    else:
        failures.append("outcome.strict_validate_not_observed")
    if _slide_count(html_text) >= 2:
        score += 5
    else:
        failures.append("outcome.slide_sections_missing")
    if 'data-generator="kai-slide-creator"' in html_text or "SlidePresentation" in html_text or "data-preset=" in html_text:
        score += 5
    else:
        failures.append("outcome.deck_runtime_markers_missing")
    return score, failures


def score_process(row: dict[str, str], metrics: NormalizedTraceMetrics) -> tuple[int, list[str]]:
    failures: list[str] = []
    should_trigger = bool_field(row, "should_trigger")
    if not should_trigger:
        used_slide_flow = (
            metrics.skill_evidence.get("slide_flow_observed")
            or metrics.skill_evidence.get("brief_observed")
            or metrics.skill_evidence.get("strict_validate_observed")
        )
        if used_slide_flow:
            return 0, ["process.negative_case_used_slide_generation_flow"]
        return 25, []

    score = 0
    if metrics.skill_evidence.get("skill_contract_read") or _suffix_match(metrics.read_paths, "SKILL.md"):
        score += 5
    else:
        failures.append("process.skill_contract_not_observed")

    route_refs = [
        "references/html-template.md",
        "references/workflow.md",
        "references/title-quality.md",
        "references/style-index.md",
    ]
    if any(_suffix_match(metrics.read_paths, ref) for ref in route_refs):
        score += 5
    else:
        failures.append("process.route_references_not_observed")

    if metrics.skill_evidence.get("brief_observed"):
        score += 5
    else:
        failures.append("process.brief_not_observed")

    if metrics.skill_evidence.get("slide_flow_observed"):
        score += 5
    else:
        failures.append("process.slide_flow_not_observed")

    if metrics.skill_evidence.get("strict_validate_observed"):
        score += 5
    else:
        failures.append("process.strict_validate_not_observed")

    return score, failures


def _display_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def default_style_rubric_fixture(root: Path, case_id: str) -> Path:
    return root / "tests" / "fixtures" / "skill-evals" / f"{case_id}-style-rubric.json"


def style_rubric_path_for_case(
    root: Path,
    case_id: str,
    artifact_dir: Path,
    allow_fixture_style_rubric: bool,
) -> tuple[Path | None, str | None]:
    artifact_path = artifact_dir / "style-rubric.json"
    if artifact_path.exists():
        return artifact_path, "artifact"
    fixture_path = default_style_rubric_fixture(root, case_id)
    if allow_fixture_style_rubric and fixture_path.exists():
        return fixture_path, "fixture"
    return None, None


def score_style(
    root: Path,
    row: dict[str, str],
    metrics: NormalizedTraceMetrics,
    artifact_dir: Path,
    allow_fixture_style_rubric: bool,
) -> tuple[int, list[str], dict[str, Any] | None]:
    failures: list[str] = []
    if not bool_field(row, "should_trigger"):
        return 25, [], None

    html_text = html_text_for_case(root, metrics, artifact_dir)
    if not html_text:
        return 0, ["style.missing_html_artifact"], None

    score = 0
    expected_preset = row.get("expected_preset", "").strip()
    if expected_preset and (
        f'data-preset="{expected_preset}"' in html_text or f"data-preset='{expected_preset}'" in html_text
    ):
        score += 5
    elif expected_preset:
        failures.append("style.expected_preset_not_found")

    if _slide_count(html_text) >= 3:
        score += 5
    else:
        failures.append("style.slide_count_too_low")

    generic_markers = ["Lorem ipsum", "TODO", "Untitled", "Your title here", "Overview", "Introduction"]
    if ":::" not in html_text and not any(marker in html_text for marker in generic_markers):
        score += 5
    else:
        failures.append("style.raw_ir_or_placeholder_text")

    rubric_path, rubric_source = style_rubric_path_for_case(
        root,
        row["id"],
        artifact_dir,
        allow_fixture_style_rubric,
    )
    style_rubric = None
    if rubric_path is not None and rubric_source is not None:
        rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
        score += round(int(rubric.get("score", 0)) * 10 / 100)
        style_rubric = {
            "source": rubric_source,
            "path": _display_path(root, rubric_path),
            "score": int(rubric.get("score", 0)),
            "overall_pass": bool(rubric.get("overall_pass")),
        }
        if not rubric.get("overall_pass"):
            failures.append("style.rubric_needs_work")
    else:
        failures.append("style.rubric_missing")

    return min(score, 25), failures, style_rubric


def score_efficiency(row: dict[str, str], metrics: NormalizedTraceMetrics) -> tuple[int, list[str]]:
    failures: list[str] = []
    score = 25
    max_shell_commands = int_field(row, "max_shell_commands", 12)
    max_input_tokens = int_field(row, "max_input_tokens", 90000)
    max_output_tokens = int_field(row, "max_output_tokens", 25000)
    max_wall_ms = int_field(row, "max_wall_ms", 240000)

    if len(metrics.shell_commands) > max_shell_commands:
        score -= 5
        failures.append("efficiency.shell_command_count_over_budget")

    failed_counts = Counter(metrics.failed_shell_commands)
    repeated_failed = sum(count - 1 for count in failed_counts.values() if count > 1)
    if metrics.failed_shell_commands:
        score -= 5
        failures.append("efficiency.failed_shell_command")
    if repeated_failed:
        score -= 10
        failures.append("efficiency.repeated_failed_command")

    if metrics.input_tokens is not None and metrics.input_tokens > max_input_tokens:
        score -= 5
        failures.append("efficiency.input_tokens_over_budget")
    if metrics.output_tokens is not None and metrics.output_tokens > max_output_tokens:
        score -= 5
        failures.append("efficiency.output_tokens_over_budget")
    if metrics.wall_ms > max_wall_ms:
        score -= 3
        failures.append("efficiency.wall_time_over_budget")

    return max(score, 0), failures


def default_normalized_fixture(root: Path, case_id: str) -> Path:
    return root / "tests" / "fixtures" / "skill-evals" / f"{case_id}-normalized.json"


def build_codex_live_prompt(root: Path, row: dict[str, str], artifact_dir: Path) -> str:
    prompt_text = (root / row["prompt_path"]).read_text(encoding="utf-8")
    relative_artifact_dir = artifact_dir.relative_to(root) if artifact_dir.is_relative_to(root) else artifact_dir
    return (
        "You are an isolated eval worker for exactly one kai-slide-creator case.\n"
        "Do not inherit or rely on coordinator conversation context.\n"
        "Before deciding or generating, read `SKILL.md` and follow it as the source of truth.\n\n"
        "Budget protocol:\n"
        "- Maximum shell commands: 12.\n"
        "- Read at most 3 reference files.\n"
        "- Do not run broad repo searches.\n"
        "- Do not inspect `tests/`, `demos/`, `evals/baselines/`, previous eval traces, or existing decks.\n"
        "- Do not write under `evals/artifacts/current/` and do not create symlinks.\n"
        "- Do not run `python3 main.py --help`, `python3 main.py --plan`, Python introspection, heredocs, or command discovery.\n"
        "- Do not read unrelated scripts unless a concrete command failed and that script is necessary to unblock it.\n"
        "- Do not create `style-rubric.json`; a separate style judge produces it.\n\n"
        "Routing rule:\n"
        "- If the request belongs to another skill, do not follow the generation flow; do not generate a deck artifact.\n\n"
        "Reference rule:\n"
        "- Use `references/brief-template.json` as the brief schema reference for positive generation cases.\n"
        "- Prefer the selected preset reference as the second reference file.\n"
        "- Use the third reference slot only when it materially improves title, style, or validation quality.\n\n"
        "Expected flow:\n"
        "1. Read `SKILL.md`.\n"
        "2. Read only the reference files needed for the selected route or preset.\n"
        f"3. Write lowercase `brief.json` under `{relative_artifact_dir}` when generating a deck.\n"
        "4. Run `python3 main.py --validate-brief --brief <BRIEF>`.\n"
        "5. Run `python3 main.py --generate --brief <BRIEF> --output <HTML>`.\n"
        "6. Run `python3 scripts/validate_html.py <HTML> --strict`.\n"
        "If a validation command fails, inspect its stderr/stdout and fix the artifact once; do not repeat the same failed command.\n"
        "7. Stop after strict validation.\n\n"
        + prompt_text
        + "\n\nEval harness constraints:\n"
        + f"- Save any deck artifacts exactly under `{relative_artifact_dir}`.\n"
        + "- If this request belongs to another skill, do not generate a deck artifact.\n"
        + "- If you generate HTML, strict validation is required before finishing.\n"
    )


def run_codex_live(root: Path, row: dict[str, str], raw_trace_path: Path, artifact_dir: Path) -> NormalizedTraceMetrics:
    eval_prompt = build_codex_live_prompt(root, row, artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    command = [
        "codex",
        "exec",
        "--json",
        "--cd",
        str(root),
        "--sandbox",
        "workspace-write",
        "--ephemeral",
        eval_prompt,
    ]
    started = time.perf_counter()
    completed = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=900)
    wall_ms = round((time.perf_counter() - started) * 1000)
    raw_trace_path.write_text(completed.stdout, encoding="utf-8")
    events = read_jsonl(raw_trace_path)
    metrics = normalize_codex_events(events, wall_ms=wall_ms)
    warnings = list(metrics.runner_warnings)
    if completed.returncode != 0:
        warnings.append(f"codex.returncode:{completed.returncode}")
    if completed.stderr.strip():
        warnings.append(f"codex.stderr:{completed.stderr.strip()[:160]}")
    return NormalizedTraceMetrics(**(asdict(metrics) | {"runner_warnings": warnings}))


def metrics_for_case(
    root: Path,
    row: dict[str, str],
    runner: str,
    artifact_dir: Path,
    normalized_trace: Path | None,
    raw_trace: Path | None,
    run_live: bool,
) -> NormalizedTraceMetrics:
    case_id = row["id"]
    if normalized_trace is not None:
        return load_normalized_trace(normalized_trace)
    if runner == "fixture":
        return load_normalized_trace(default_normalized_fixture(root, case_id))
    if raw_trace is not None:
        if runner != "codex":
            raise ValueError(f"Raw trace normalization is not implemented for runner {runner!r}")
        return normalize_codex_events(read_jsonl(raw_trace), wall_ms=0)
    if run_live:
        if runner != "codex":
            raise ValueError(f"Live runner {runner!r} has no verified adapter yet")
        raw_target = artifact_dir / "trace.raw.jsonl"
        return run_codex_live(root, row, raw_target, artifact_dir)
    raise ValueError("Use --runner fixture, --normalized-trace, --raw-trace, or --run-live.")


def evaluate_case(
    root: Path,
    row: dict[str, str],
    runner: str,
    artifact_root: Path,
    normalized_trace: Path | None,
    raw_trace: Path | None,
    run_live: bool,
    allow_fixture_style_rubric: bool,
) -> SkillEvalCase:
    case_id = row["id"]
    case_artifact_dir = artifact_root / case_id
    case_artifact_dir.mkdir(parents=True, exist_ok=True)
    metrics = metrics_for_case(root, row, runner, case_artifact_dir, normalized_trace, raw_trace, run_live)

    normalized_path = case_artifact_dir / "trace.normalized.json"
    normalized_path.write_text(json.dumps(asdict(metrics), ensure_ascii=False, indent=2), encoding="utf-8")

    outcome, outcome_failures = score_outcome(root, row, metrics, case_artifact_dir)
    process, process_failures = score_process(row, metrics)
    style, style_failures, style_rubric = score_style(
        root,
        row,
        metrics,
        case_artifact_dir,
        allow_fixture_style_rubric,
    )
    efficiency, efficiency_failures = score_efficiency(row, metrics)
    scores = {
        "outcome": outcome,
        "process": process,
        "style": style,
        "efficiency": efficiency,
    }
    failures = outcome_failures + process_failures + style_failures + efficiency_failures
    eval_failures: list[str] = []
    if bool_field(row, "should_trigger") and "style.rubric_missing" in style_failures:
        eval_failures.append("eval.style_rubric_missing")
    failures += eval_failures
    total_score = sum(scores.values())
    should_trigger = bool_field(row, "should_trigger")
    outcome_gate = outcome >= 20 if should_trigger else outcome == 25
    eval_complete = not eval_failures
    passed = eval_complete and outcome_gate and total_score >= 75 and not any(
        failure
        in {
            "outcome.negative_case_generated_deck",
            "process.negative_case_used_slide_generation_flow",
        }
        for failure in failures
    )

    return SkillEvalCase(
        case_id=case_id,
        total_score=total_score,
        passed=passed,
        eval_complete=eval_complete,
        scores=scores,
        failures=failures,
        metrics=asdict(metrics),
        artifact_dir=str(case_artifact_dir),
        style_rubric=style_rubric,
    )


def selected_rows(rows: list[dict[str, str]], case_id: str | None) -> list[dict[str, str]]:
    if case_id is None:
        return rows
    selected = [row for row in rows if row["id"] == case_id]
    if not selected:
        raise SystemExit(f"No eval case found for {case_id!r}")
    return selected


def build_payload(cases: list[SkillEvalCase]) -> dict[str, Any]:
    categories = ["outcome", "process", "style", "efficiency"]
    return {
        "cases": [asdict(case) for case in cases],
        "summary": {
            "total": len(cases),
            "passed": sum(1 for case in cases if case.passed),
            "failed": sum(1 for case in cases if not case.passed),
            "incomplete": sum(1 for case in cases if not case.eval_complete),
            "average_score": round(sum(case.total_score for case in cases) / len(cases), 2) if cases else 0,
            "average_category_scores": {
                category: round(sum(case.scores[category] for case in cases) / len(cases), 2) if cases else 0
                for category in categories
            },
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--manifest", default="evals/slide-skill-prompts.csv")
    parser.add_argument("--runner", choices=["fixture", "codex"], default="fixture")
    parser.add_argument("--case-id", help="Run one case id.")
    parser.add_argument("--normalized-trace", help="Use one normalized trace fixture for selected case(s).")
    parser.add_argument("--raw-trace", help="Normalize and score one raw runner trace for selected case(s).")
    parser.add_argument("--artifact-dir", default="evals/artifacts/current/skill-runs")
    parser.add_argument("--run-live", action="store_true", help="Invoke the selected live runner.")
    parser.add_argument(
        "--disable-fixture-style-rubric",
        action="store_true",
        help="Do not use checked-in style rubric fixtures when scoring fixture runs.",
    )
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--json-out", help="Optional JSON output path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    manifest = (root / args.manifest).resolve()
    artifact_root = (root / args.artifact_dir).resolve() if not Path(args.artifact_dir).is_absolute() else Path(args.artifact_dir)
    normalized_trace = Path(args.normalized_trace).resolve() if args.normalized_trace else None
    raw_trace = Path(args.raw_trace).resolve() if args.raw_trace else None

    rows = selected_rows(load_manifest(manifest), args.case_id)
    if (normalized_trace or raw_trace) and len(rows) != 1:
        raise SystemExit("--normalized-trace and --raw-trace require --case-id to select exactly one case")

    cases = [
        evaluate_case(
            root,
            row,
            args.runner,
            artifact_root,
            normalized_trace,
            raw_trace,
            args.run_live,
            args.runner == "fixture" and not args.disable_fixture_style_rubric,
        )
        for row in rows
    ]
    payload = build_payload(cases)

    if args.json_out:
        target = Path(args.json_out)
        target = target if target.is_absolute() else root / target
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for case in cases:
            status = "PASS" if case.passed else "FAIL"
            print(f"{status} {case.case_id}: {case.total_score}/100 {case.scores}")
            for failure in case.failures:
                print(f"  - {failure}")
        print(f"Summary: {payload['summary']['passed']} passed, {payload['summary']['failed']} failed.")
    return 0 if payload["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
