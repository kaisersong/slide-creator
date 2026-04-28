# 2026-04-28 Family Audit Round 2

## Scope

Second-round family audit after the `Chinese Chan` fix, focused on cross-preset safety.

Priority groups:

1. Editorial family
   - `Paper & Ink`
   - `Notebook Tabs`
   - `Modern Newspaper`
   - `Vintage Editorial`
2. Launch / visual-impact family
   - `Glassmorphism`
   - `Aurora Mesh`
   - `Bold Signal`
3. Dev / terminal family
   - `Terminal Green`
   - `Neon Cyber`
   - `Neo-Retro Dev`

Production presets were also re-verified:

- `Swiss Modern`
- `Enterprise Dark`
- `Data Story`
- `Blue Sky`

## Commands run

### Production gate

```bash
python3 scripts/preset_release_gate.py \
  --suite evals/preset-surface-phase1/manifest.json \
  --output-dir /tmp/preset-surface-phase1-audit-20260428-b \
  --browser-titles
```

### Cross-preset regression

```bash
pytest -q \
  tests/test_family_demo_strict_validate.py \
  tests/test_cross_preset_consistency.py \
  tests/test_low_context_pipeline.py \
  tests/test_preset_surface_phase1.py \
  tests/test_validate_priority_preset_contracts.py \
  tests/test_priority_preset_reference_contracts.py
```

### Strict validate per-family demo

Ran `python3 scripts/validate_html.py <demo> --strict` for all targeted `-zh` demos above.

## Overall result

### Production chain

Green.

- release gate: `5/5 pass`
- cross-preset regression: `609 passed, 43 skipped`
- production work-hub outputs all pass strict validate:
  - [ai-native-work-hub-swiss-modern-zh.html](/Users/song/projects/slide-creator/demos/ai-native-work-hub-swiss-modern-zh.html)
  - [ai-native-work-hub-enterprise-dark-zh.html](/Users/song/projects/slide-creator/demos/ai-native-work-hub-enterprise-dark-zh.html)
  - [ai-native-work-hub-data-story-zh.html](/Users/song/projects/slide-creator/demos/ai-native-work-hub-data-story-zh.html)
  - [ai-native-work-hub-blue-sky-zh.html](/Users/song/projects/slide-creator/demos/ai-native-work-hub-blue-sky-zh.html)

Conclusion:

- the `Chinese Chan` fix did **not** leak into the production path
- shared low-context / shared runtime changes stayed contained

### Family demos

Green after demo-asset cleanup.

The editorial / launch / dev families did expose real issues during the audit, but the important distinction held:

- most failures were **stale demo/runtime debt**
- they were **not evidence that the latest production shared path was broken by the Chan fix**
- after targeted fixes, all audited `-zh` family demos now pass `strict validate`
- final production re-check stayed green:
  - report: [/private/tmp/preset-surface-phase1-audit-20260428-final/release-gate-report.json](/private/tmp/preset-surface-phase1-audit-20260428-final/release-gate-report.json)
  - summary: [/private/tmp/preset-surface-phase1-audit-20260428-final/release-gate-summary.md](/private/tmp/preset-surface-phase1-audit-20260428-final/release-gate-summary.md)

## Family findings

### 1. Editorial family

- `Paper & Ink`: strict green
- `Notebook Tabs`: strict green after:
  - shared js-engine runtime refresh
  - cover title rebalance
- `Modern Newspaper`: strict green after:
  - shared js-engine runtime refresh
- `Vintage Editorial`: strict green after:
  - shared js-engine runtime refresh
  - explicit title balancing on the long editorial headline

Interpretation:

- `Paper & Ink` remains the strongest editorial preset
- the other three were mostly old demo-shell debt, not broken visual direction

### 2. Launch / visual-impact family

- `Glassmorphism`: strict green after shared runtime refresh
- `Aurora Mesh`: strict green after shared runtime refresh
- `Bold Signal`: strict green after:
  - shared runtime refresh
  - `--text-muted` token fix
  - CTA title balance fix
  - PresentMode class/bootstrap normalization

Interpretation:

- this family was structurally sound
- `Bold Signal` did have one real style-contract bug on top of runtime debt, and that bug is now fixed

### 3. Dev / terminal family

- `Terminal Green`: strict green after:
  - raw markdown cleanup in slide text
  - shared runtime refresh
  - broken `self` event-handler references removed
- `Neon Cyber`: strict green after:
  - removal of external non-font Fontshare links
  - shared runtime refresh
- `Neo-Retro Dev`: strict green after shared runtime refresh

Interpretation:

- this family had the most obvious content/export hygiene debt
- `Terminal Green` and `Neon Cyber` were the only ones needing more than shared runtime modernization

## Evidence that many failing demos are stale

The audited non-production demos carry older release watermarks such as:

- `v2.16.0`
- `v2.17.0`
- `v2.18.0`

Examples:

- [bold-signal-zh.html](/Users/song/projects/slide-creator/demos/bold-signal-zh.html)
- [glassmorphism-zh.html](/Users/song/projects/slide-creator/demos/glassmorphism-zh.html)
- [aurora-mesh-zh.html](/Users/song/projects/slide-creator/demos/aurora-mesh-zh.html)
- [modern-newspaper-zh.html](/Users/song/projects/slide-creator/demos/modern-newspaper-zh.html)
- [notebook-tabs-zh.html](/Users/song/projects/slide-creator/demos/notebook-tabs-zh.html)
- [terminal-green-zh.html](/Users/song/projects/slide-creator/demos/terminal-green-zh.html)

That lines up with the validator output: many failures are “shared js-engine contract incomplete”, which is consistent with older demo assets rather than a fresh regression.

## Guardrail improvements made during the audit

### `tests/test_cross_preset_consistency.py`

The old test had false positives:

- it inferred Blue Sky membership from filename
- it over-matched any `calc(100vw...)`

It now:

- detects preset via `body[data-preset]`
- matches only the actual Blue Sky stage/track formula

### `tests/test_low_context_pipeline.py`

Added a production isolation assertion:

- production presets must not leak `Chinese Chan` signatures such as:
  - `zen-ghost-kanji`
  - `data-export-role="zen_*"`
  - `Noto Serif SC`

## Regression coverage added

- Added [tests/test_family_demo_strict_validate.py](/Users/song/projects/slide-creator/tests/test_family_demo_strict_validate.py)
- This locks the audited nine `-zh` family demos to `strict validate` green, so the cleanup is no longer only “one-time manual QA”

## Practical conclusion

1. Production presets are still safe after the `Chinese Chan` work.
2. The non-production family backlog identified in round 2 has been repaired for the audited demo set.
3. The remaining risk is no longer these nine demo assets drifting silently again; it is future long-tail presets outside this audited set.

## Related artifacts

- [2026-04-28-chinese-chan-style-drift-fix.md](/Users/song/projects/slide-creator/plans/2026-04-28-chinese-chan-style-drift-fix.md)
- [2026-04-28-cross-preset-audit.md](/Users/song/projects/slide-creator/plans/2026-04-28-cross-preset-audit.md)
