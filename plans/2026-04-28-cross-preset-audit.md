# 2026-04-28 Cross-Preset Audit

## Goal

Confirm that the `Chinese Chan` fixes did not leak into other presets, with extra focus on the production path:

- `Swiss Modern`
- `Enterprise Dark`
- `Data Story`
- `Blue Sky`

Also harden the cross-preset gate itself, because a weak regression test is not a real guardrail.

## What was checked

### 1. Production release gate

Command:

```bash
python3 scripts/preset_release_gate.py \
  --suite evals/preset-surface-phase1/manifest.json \
  --output-dir /tmp/preset-surface-phase1-audit-20260428-b \
  --browser-titles
```

Result:

- `5/5 pass`
- report: [/private/tmp/preset-surface-phase1-audit-20260428-b/release-gate-report.json](/private/tmp/preset-surface-phase1-audit-20260428-b/release-gate-report.json)
- summary: [/private/tmp/preset-surface-phase1-audit-20260428-b/release-gate-summary.md](/private/tmp/preset-surface-phase1-audit-20260428-b/release-gate-summary.md)

### 2. Cross-preset regression suite

Command:

```bash
pytest -q \
  tests/test_cross_preset_consistency.py \
  tests/test_low_context_pipeline.py \
  tests/test_preset_surface_phase1.py \
  tests/test_validate_priority_preset_contracts.py \
  tests/test_priority_preset_reference_contracts.py
```

Result:

- `600 passed`
- `43 skipped`

## Problems found in the guardrail itself

The existing `tests/test_cross_preset_consistency.py` had false positives:

1. It inferred Blue Sky membership from demo filenames, which broke on generated files like `ai-native-work-hub-blue-sky-zh.html`.
2. It treated any `calc(100vw...)` usage as Blue Sky stage/track architecture, which is too broad.

That means the old test could tell us “cross-preset contamination” even when the actual preset architecture was fine.

## Fixes made

### `tests/test_cross_preset_consistency.py`

- Added `body_preset(content)` helper
- Switched architecture-isolation filtering to `data-preset`, not filename heuristics
- Narrowed the stage/track detector from any `calc(100vw` to the actual Blue Sky formula:
  - `calc(100vw * var(--slide-count))`

### `tests/test_low_context_pipeline.py`

Added a new regression:

- `test_production_presets_do_not_leak_chinese_chan_signatures`

It asserts that production outputs do not emit:

- `zen-ghost-kanji`
- `data-export-role="zen_*"`
- `Noto Serif SC`

This is a direct protection against Chan-specific typography/component leakage into production presets.

## Outcome

After the guardrail fixes:

- global cross-preset suite is green
- production release gate is green
- the `Chinese Chan` style fix remains green under strict validate and browser title QA

## Files touched

- [tests/test_cross_preset_consistency.py](/Users/song/projects/slide-creator/tests/test_cross_preset_consistency.py)
- [tests/test_low_context_pipeline.py](/Users/song/projects/slide-creator/tests/test_low_context_pipeline.py)

## Conclusion

This round is not just “Chinese Chan looks better”.

It also added a more reliable answer to the user’s real concern:

> do not fix one preset in a way that silently breaks others

The production chain and full cross-preset gate both passed after the changes.
