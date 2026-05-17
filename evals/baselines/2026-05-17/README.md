# Slide-Creator Eval Baseline — 2026-05-17

This directory captures the current green eval baseline after adding captured-run
skill evals and fixing current demo fixture gates.

## Test Baseline

Command:

```bash
python3 -m pytest tests/ -q
```

Result:

```text
2260 passed, 132 skipped in 37.25s
```

## Captured-Run Skill Eval Baseline

File: `skill-evals/skill-evals.json`

Command:

```bash
python3 scripts/run-skill-evals.py \
  --runner fixture \
  --artifact-dir /private/tmp/slide-skill-eval-runs-rubric \
  --format json \
  --json-out /private/tmp/slide-skill-evals-rubric.json
```

Summary:

| Metric | Value |
|---|---:|
| Total cases | 6 |
| Passed | 6 |
| Failed | 0 |
| Incomplete | 0 |
| Average score | 100.00 |
| Outcome avg | 25.00 |
| Process avg | 25.00 |
| Style avg | 25.00 |
| Efficiency avg | 25.00 |

Case scores:

| Case | Total | Outcome | Process | Style | Efficiency |
|---|---:|---:|---:|---:|---:|
| explicit-generate | 100 | 25 | 25 | 25 | 25 |
| implicit-exec-update | 100 | 25 | 25 | 25 | 25 |
| contextual-product-launch | 100 | 25 | 25 | 25 | 25 |
| boundary-report-to-deck | 100 | 25 | 25 | 25 | 25 |
| negative-report | 100 | 25 | 25 | 25 | 25 |
| negative-html-export | 100 | 25 | 25 | 25 | 25 |

Positive fixture cases use checked-in `*-style-rubric.json` files so a missing
style rubric now marks the case `eval_complete: false` and fails the eval.

## Live Codex Captured-Run Baseline

File: `live-codex/explicit-generate.json`

Artifacts: `live-codex/explicit-generate/`

Command:

```bash
python3 scripts/run-skill-evals.py \
  --runner codex \
  --case-id explicit-generate \
  --run-live \
  --artifact-dir .tmp-run/skill-live-codex \
  --format json \
  --json-out /private/tmp/slide-skill-live-codex-explicit.json
```

The live run produced `deck.html`, `brief.json`, raw trace, and normalized
trace. It was then rescored with an external `style-rubric.json` artifact.

Summary:

| Metric | Value |
|---|---:|
| Total cases | 1 |
| Passed | 1 |
| Failed | 0 |
| Incomplete | 0 |
| Average score | 89.00 |
| Outcome avg | 25.00 |
| Process avg | 25.00 |
| Style avg | 24.00 |
| Efficiency avg | 15.00 |
| Shell commands | 35 |
| Input tokens | 1,216,207 |
| Output tokens | 10,285 |
| Wall time | 221,990 ms |

Case scores:

| Case | Total | Outcome | Process | Style | Efficiency | Failures |
|---|---:|---:|---:|---:|---:|---|
| explicit-generate | 89 | 25 | 25 | 24 | 15 | `efficiency.shell_command_count_over_budget`, `efficiency.input_tokens_over_budget` |

## Preset Surface Release Gate Baseline

Directory: `preset-surface-phase1/`

This directory is a reusable `--baseline-dir` for non-regression comparison.
It includes each case's `deck.html`, `packet.json`, `quality-report.json`, and
browser title report where applicable.

Command:

```bash
python3 scripts/preset_release_gate.py \
  --output-dir /private/tmp/slide-preset-release-gate \
  --report-path /private/tmp/slide-preset-release-gate/report.json \
  --summary-md /private/tmp/slide-preset-release-gate/summary.md \
  --include-skill-evals \
  --skill-evals-runner fixture \
  --skill-evals-json-out /private/tmp/slide-preset-release-gate/skill-evals.json
```

Summary:

| Metric | Value |
|---|---:|
| Pass count | 6 |
| Fail count | 0 |
| Best case | support-blue-sky-fixture |
| Best overall | 1.00 |
| HTML fixture pass/fail | 2 / 0 |
| Render pass/fail | 4 / 0 |

Case scores:

| Case | Route | Compression | Render | Efficiency |
|---|---:|---:|---:|---:|
| support-blue-sky-fixture | 1.00 | 1.00 | 1.00 | 1.00 |
| core-blue-sky-render | 1.00 | 1.00 | 1.00 | 1.00 |
| support-paper-ink-fixture | 1.00 | 1.00 | 1.00 | 1.00 |
| core-enterprise-dark-render | 1.00 | 1.00 | 1.00 | 1.00 |
| core-swiss-modern-render | 1.00 | 1.00 | 1.00 | 1.00 |
| core-data-story-render | 1.00 | 1.00 | 1.00 | 1.00 |

## Future Comparison

Run the future candidate against this baseline:

```bash
python3 scripts/preset_release_gate.py \
  --output-dir /private/tmp/slide-preset-release-gate-candidate \
  --baseline-dir evals/baselines/2026-05-17/preset-surface-phase1 \
  --require-baseline \
  --report-path /private/tmp/slide-preset-release-gate-candidate/report.json \
  --summary-md /private/tmp/slide-preset-release-gate-candidate/summary.md \
  --include-skill-evals \
  --skill-evals-runner fixture \
  --skill-evals-json-out /private/tmp/slide-preset-release-gate-candidate/skill-evals.json
```

Because the command above passes `--baseline-dir
evals/baselines/2026-05-17/preset-surface-phase1`, the release gate also
compares the new captured-run `skill-evals.json` against
`preset-surface-phase1/skill-evals.json` automatically and fails on pass,
completeness, total-score, or category-score regressions.

For standalone captured-run score comparison, run:

```bash
python3 scripts/compare-skill-eval-baseline.py \
  --old evals/baselines/2026-05-17/skill-evals/skill-evals.json \
  --new /path/to/candidate/skill-evals.json \
  --format json
```
