# Preset Surface Phase 1 Eval

This suite exists to prove two things after preset-surface optimization:

1. The default quality investment in the core presets actually improved output quality.
2. Narrowing the recommendation surface did not silently break the visible support surface.

## Buckets

- `core-enterprise-dark-render`
- `core-swiss-modern-render`
- `core-data-story-render`

These are the **deterministic-core** cases. They render from the current code path and are the real uplift benchmark set.

- `support-blue-sky-fixture`
- `support-paper-ink-fixture`

These are the **support-surface-smoke** cases. Blue Sky and Paper & Ink are still evaluated from known-good HTML fixtures because the deterministic BRIEF renderer currently only supports `Swiss Modern / Enterprise Dark / Data Story`.

## Why Blue Sky Is Fixture-Only

`render_from_brief()` in [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py) currently raises for non-deterministic presets outside the core three. Blue Sky remains a special starter path, so it should stay in support-surface smoke until a deterministic renderer exists.

## Why Paper & Ink Is Fixture-Only

`Paper & Ink` is now back in the green support-surface suite, but still as a fixture case rather than a deterministic render case.

- `demos/paper-ink-zh.html` now passes `python3 tests/validate.py --strict`
- the representative editorial fixture now carries the current shared runtime, watermark injection, and title-balance fixes
- the preset still does not have a deterministic BRIEF renderer, so it remains support-surface smoke rather than core-render benchmark coverage

## Recommended Workflow

Baseline run:

```bash
python3 scripts/run_evals.py \
  evals/preset-surface-phase1/manifest.json \
  --output-dir /tmp/preset-surface-baseline
```

Candidate run with non-regression comparison:

```bash
python3 scripts/run_evals.py \
  evals/preset-surface-phase1/manifest.json \
  --output-dir /tmp/preset-surface-candidate \
  --baseline-dir /tmp/preset-surface-baseline
```

Direct suite run with browser-title QA:

```bash
python3 scripts/run_evals.py \
  evals/preset-surface-phase1/manifest.json \
  --output-dir /tmp/preset-surface-candidate \
  --baseline-dir /tmp/preset-surface-baseline \
  --browser-titles
```

`browser-title-composition` is now a required title gate for every phase-1 case, so browser-backed title QA is part of the formal green path rather than an optional diagnostic.

Release gate wrapper:

```bash
python3 scripts/preset_release_gate.py \
  --output-dir /tmp/preset-surface-gate \
  --baseline-dir /tmp/preset-surface-baseline \
  --require-baseline
```

The release gate wrapper auto-enables browser title QA whenever the suite manifest contains `required_title_gates`, so the wrapper command above is sufficient for the formal phase-1 gate.

## What Counts As Quality Uplift

For the deterministic-core cases:

- strict validate still passes
- `chrome-hidden-by-default` and `no-content-occlusion-risk` stay green
- `layout_variety`, `component_diversity`, and `style_signature_coverage` do not regress materially
- `minimal_slide_ratio` does not drift upward beyond the configured threshold
- Data Story keeps `numeric_faithfulness >= 0.95`

For the support-surface smoke cases:

- the preset still renders as the named preset
- preset-specific architecture and runtime markers are still present
- the surface stays usable enough for contract validation
- Paper & Ink now proves editorial support-surface health without pretending it already has deterministic BRIEF rendering
