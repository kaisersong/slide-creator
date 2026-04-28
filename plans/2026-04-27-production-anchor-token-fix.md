# Production Preset Anchor Token Fix

## Context

Target deck:

- [org-phase-change-ai-native-org-swiss-modern-zh.html](/Users/song/projects/slide-creator/demos/org-phase-change-ai-native-org-swiss-modern-zh.html)

User-reported issues:

1. Cover KPI cards on `Swiss Modern` all showed the same generic token: `AI`
2. P4 `stat_block` rendered the left anchor as `流体化不`
3. Need to verify whether the same heuristic problem exists across all four production presets

## Root Cause

The issue was not content loss in the BRIEF. It was the shared compact-anchor heuristic in [low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py):

- `_compact_display_token(...)` over-compressed long Chinese thesis sentences into naive prefixes
- `_metric_value_for_item(...)` reused that output in multiple visual slots
- repeated supporting facts starting with `AI ...` collapsed into the same generic token
- `Swiss Modern` `stat_block` used the compact token directly for the large left-side emphasis slot

This created two visible failures:

- semantic collapse: several different claims all became `AI`
- bad truncation: `流体化不是...` became `流体化不`

## Code Fix

Changed shared low-context logic in [low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py):

- added curated display-keyword extraction for concept-heavy Chinese content
- added bad-token guards for:
  - generic one-word anchors like `AI`
  - dangling suffixes like `不`
  - contrast phrases where action verbs should yield to the thesis-side noun
- added `used_tokens` support so repeated metric cards on one slide avoid collapsing to the same anchor
- wired uniqueness into:
  - `Swiss Modern` cover hero stats
  - `Enterprise Dark` KPI cards / close cards
  - `Data Story` KPI cards / close cards

Also added a Blue Sky-specific regression:

- [tests/test_generate_rendering.py](/Users/song/projects/slide-creator/tests/test_generate_rendering.py)
- confirms the Blue Sky cover helper still emits a stable, non-duplicated metrics triplet

## Cross-Preset Check

### Swiss Modern

After fix, the same article now renders:

- cover hero stats: `相变 / 竞争力 / 认知力`
- P4 left emphasis: `流体化`

This is the exact target deck path:

- [org-phase-change-ai-native-org-swiss-modern-zh.html](/Users/song/projects/slide-creator/demos/org-phase-change-ai-native-org-swiss-modern-zh.html)

### Enterprise Dark

The same source content does not surface the old failure on cover:

- cover goes through the narrative story-card path instead of generic KPI compression
- no `ent-kpi-number` value regressed to plain `AI`
- no bad `流体化不` anchor leaked into emphasis slots

### Data Story

The same source content now renders a non-generic hero value:

- hero KPI: `相变`

No `AI` leakage in the positive hero KPI slot.

### Blue Sky

Blue Sky does **not** share the same shared low-context path. Its cover metrics come from `_extract_cover_metrics(...)` in [generate.py](/Users/song/projects/slide-creator/scripts/generate.py), not from `_compact_display_token(...)`.

Result:

- no equivalent repeated-`AI` regression found in the cover metrics helper
- added a targeted regression test so this remains explicit

## Validation

Targeted regressions:

- `tests/test_low_context_pipeline.py`
  - compact token quality
  - production-preset cross-check on the phase-change article
- `tests/test_generate_rendering.py`
  - Blue Sky cover metric stability

Deck validation:

```bash
python3 tests/validate.py demos/org-phase-change-ai-native-org-swiss-modern-zh.html --strict
```

Result:

- strict validate passed

## Conclusion

This was a **shared skill-level heuristic bug**, not a one-off content issue.

The fix is now split correctly by runtime path:

- `Swiss Modern / Enterprise Dark / Data Story`: shared low-context anchor extraction hardened
- `Blue Sky`: separate cover helper checked and locked with regression
