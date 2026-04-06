# Slide Creator Mode Quality And Timing Design

## Goal

Fix `slide-creator` itself so that:

- the same source content keeps the same preset across `Auto` / `Polish`
- English users see English mode names instead of Chinese-only labels
- generation records segmented timings (`plan`, `generate`, `validate`, `polish`, `total`)
- the workflow can surface estimated time before generation starts
- regenerated demos come from the repaired skill contract, not from manual HTML edits

## Current Problems

### 1. Planning depth leaks into theme selection

The current mode simplification work only clarified planning depth. It did not make preset fidelity enforceable. As a result, two plans can both say `Preset: Enterprise Dark` while the generated decks drift into different visual systems.

### 2. Design quality rules are advisory, not operational

`references/design-quality.md` documents quality expectations, but the workflow does not force the generator to:

- shorten headings when they wrap excessively
- avoid dense 5-step grids inside half-width cards
- verify that generated HTML still reflects the chosen preset

### 3. Mode labels are not bilingual

The skill currently exposes `自动` and `精修` directly. That is correct for Chinese requests, but English users should see `Auto` and `Polish` as the user-facing labels.

### 4. No timing contract

The workflow has no standard timing schema, no estimate messaging, and no place to record measured durations for generated demos. That makes it hard to tell users what the fast path vs deep path really costs.

## Design Decisions

### A. Keep canonical internal depth keys, add English aliases

Canonical planning depth remains:

- `自动`
- `精修`

User-facing alias map:

- Chinese UI / Chinese requests: show `自动` / `精修`
- English UI / English requests: show `Auto` / `Polish`

Document both forms in `SKILL.md`, `workflow.md`, and the planning template so agents can parse either.

### B. Lock preset once chosen

Once a plan names a preset, generation must preserve it unless the user explicitly changes the style. Planning depth is allowed to change structure, not theme.

Operational rule:

- same content + same preset + different planning depth => same preset family in output

Implementation contract:

- generated HTML must include `data-preset="..."` on `<body>`
- tests compare planned preset against generated preset

### C. Add timing contract to planning and generation

Introduce one timing schema for both demos and future real runs:

```text
plan
generate
validate
polish
total
```

Rules:

- `plan`: time to create / confirm PLANNING.md
- `generate`: time to produce HTML
- `validate`: structural validation time
- `polish`: additional repair / rerun time after first generated result
- `total`: end-to-end elapsed wall time

For `Auto`, `polish` is expected to be zero or minimal.
For `Polish`, `polish` is expected to be non-zero when deeper refinement is requested.

### D. Add estimated-time messaging

Before generation starts, the workflow should tell the user the expected time range:

- `Auto`: quick draft estimate
- `Polish`: deeper-structure estimate

These are documented estimates in the skill / README, not guarantees. The demo rerun will produce initial measured numbers to publish.

### E. Keep demo verification focused on skill guarantees

Tests should not depend on hand-edited final decks. They should verify:

- preset fidelity
- bilingual mode naming contract
- timing metadata presence
- design-quality hard guards that map to known failure modes

Regenerated demos can then be validated against those rules.

## Files To Change

- `SKILL.md`
  - bilingual mode names
  - timing estimate guidance
  - preset fidelity language
- `README.md`
  - English naming
  - estimated timing section
  - measured demo timings after rerun
- `README.zh-CN.md`
  - Chinese timing section with English aliases where useful
- `references/workflow.md`
  - bilingual mode routing
  - estimate prompt before generation
  - timing capture requirements
- `references/planning-template.md`
  - bilingual mode value examples
  - timing section
- `references/html-template.md`
  - `data-preset`
  - timing metadata hook guidance
- `references/design-quality.md`
  - keep hard rules tied to actual failure modes
- `tests/test_mode_simplification.py`
  - update for bilingual naming
- `tests/test_design_quality_guards.py`
  - update for bilingual naming + timing contract
- `tests/test_mode_path_regressions.py`
  - refocus on skill guarantees instead of hand-authored current HTML quirks
- `tests/test_validate_console_output.py`
  - keep Windows-safe validation output

## Validation Plan

1. Run targeted doc / contract tests.
2. Regenerate `Auto` path demo from the Intent Broker spec with measured segmented timings.
3. Validate the generated HTML.
4. Regenerate `Polish` path demo from the same spec with measured segmented timings.
5. Validate the generated HTML.
6. Record timing results in README.

## Success Criteria

- English-facing docs use `Auto` / `Polish` as the visible mode names.
- Chinese-facing docs still explain `自动` / `精修`.
- The workflow explicitly records `plan`, `generate`, `validate`, `polish`, and `total`.
- README gives users estimated time ranges and includes measured demo timings.
- Re-generated `Auto` and `Polish` demos share the same preset for the same source content.
- All updated tests pass.
