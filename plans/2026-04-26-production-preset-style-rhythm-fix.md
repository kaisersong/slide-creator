# 2026-04-26 Production Preset Style/Rhythm Fix Record

## Scope

This record covers the generator-level fixes for the three deterministic production presets:

- `Swiss Modern`
- `Enterprise Dark`
- `Data Story`

`Blue Sky` was fixed earlier on its own legacy helper path. This pass focuses on the shared low-context renderer in [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py), not on hand-editing any generated deck.

## Source Artifact And Outputs

- Source document: `/Users/song/Downloads/AI原生工作中枢设计推演v2.docx`
- Source summary used for deck generation: [ai-native-work-hub-v2-source.md](/Users/song/projects/slide-creator/plans/ai-native-work-hub-v2-source.md)

Generated production outputs:

- [Swiss Modern](/Users/song/projects/slide-creator/demos/ai-native-work-hub-swiss-modern-zh.html)
- [Enterprise Dark](/Users/song/projects/slide-creator/demos/ai-native-work-hub-enterprise-dark-zh.html)
- [Data Story](/Users/song/projects/slide-creator/demos/ai-native-work-hub-data-story-zh.html)
- [Blue Sky](/Users/song/projects/slide-creator/demos/ai-native-work-hub-blue-sky-zh.html)

Driving artifacts:

- [Swiss BRIEF](/Users/song/projects/slide-creator/plans/ai-native-work-hub-v2-swiss-modern-BRIEF.json)
- [Enterprise BRIEF](/Users/song/projects/slide-creator/plans/ai-native-work-hub-v2-enterprise-dark-BRIEF.json)
- [Data Story BRIEF](/Users/song/projects/slide-creator/plans/ai-native-work-hub-v2-data-story-BRIEF.json)
- [Blue Sky PLANNING](/Users/song/projects/slide-creator/plans/ai-native-work-hub-v2-blue-sky-PLANNING.md)

## User-Facing Problems

After Blue Sky was improved, the other three production presets still showed the same broader class of issues:

1. Style application was shallow.
   Renderers were producing structurally valid slides, but too many cards, matrices, and labels still felt like generic scaffolds rather than preset-native composition.

2. Narrative rhythm flattened out.
   Different roles were collapsing into the same layout family, especially in `Data Story`, which produced consecutive pages with nearly identical visual rhythm.

3. Slide-local content was weak.
   The generator overused global `must_include` evidence items such as `90/9/1`, `18 个月`, and `Workspace 是容器`, so many pages looked semantically recycled.

4. Some renderers still leaked visual-placeholder intent.
   Strings such as `before after comparison`, `risk ladder`, `reference archetypes`, or fallback label families like `Alpha/Beta` and `Input/Output` were structurally gone in some paths, but the root cause still existed in shared helpers.

5. `Data Story` was still willing to draw charts from borrowed numbers.
   If a page contained no slide-local numeric story but happened to inherit evidence numbers, the renderer could still choose a chart, creating a deck that was valid but not trustworthy.

## Root Cause

The issue was not a single preset bug. It was a shared renderer-design problem.

### 1. Role routing was only partially preset-aware

`build_slide_spec()` was already deterministic, but layout fallback logic still risked collapsing roles into coarse layouts when the role map did not fully align with the preset contract.

Relevant functions:

- `_layout_map_for_preset()`
- `_canonical_layout_for_role()`
- `build_slide_spec()`

### 2. Evidence selection overfit global must-include items

The renderer was too eager to reuse high-signal global evidence items on unrelated slides. That made multiple pages reuse the same labels and values, which damaged both rhythm and preset expression.

Relevant functions:

- `_select_relevant_evidence_items()`
- `_build_supporting_items()`

### 3. Detail pairing created mirrored cards

Visible items and body copy were being paired from the same small pool, so one slide could say:

- title A -> body B
- title B -> body A

That is visually acceptable, but it reads like generic matrix filler rather than authored composition.

Relevant function:

- `_spec_detail_pairs()`

### 4. `Data Story` chart readiness was too permissive

The renderer previously treated any sufficiently large numeric pool as chart-ready, even if those numbers came from borrowed evidence rather than the slide’s own argument.

That produced:

- workflow pages with synthetic line charts
- metric pages with bars whose labels were real, but whose chart logic was not slide-native

Relevant functions:

- `_spec_explicit_numbers()`
- `_metric_values_from_spec()`
- `_has_chart_ready_numbers()`

## Generator Fixes

All fixes were implemented in [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py).

### Shared fixes

1. Added slide-relevant evidence ranking.
   `_select_relevant_evidence_items()` now scores items against slide-local title/key-point/visual content and penalizes overused evidence.

2. Added safer supporting-item construction.
   `_build_supporting_items()` now prefers slide-local phrasing before falling back to shared evidence.

3. Rebuilt detail pairing order.
   `_spec_detail_pairs()` now prefers key-point detail bodies before recycled evidence labels and explicitly avoids title-to-title mirror loops when possible.

4. Replaced fallback-visible placeholders with content-derived tokens.
   Helpers such as `_compact_display_token()`, `_spec_display_items()`, `_spec_detail_pairs()`, and the preset renderers now use slide-derived copy rather than exposing authoring-intent placeholders.

### `Swiss Modern`

Adjusted renderer usage so the preset reads more like Swiss editorial composition instead of generic structured scaffolds:

- `column_content` now uses content-derived pain titles and descriptions
- `stat_block` now derives stat value and supporting labels from slide-local meaning
- `geometric_diagram` and `data_table` no longer show generic token families
- `contents_index` and table rows now pull real content phrases instead of fallback archetypes

Primary renderer functions:

- `_render_swiss_title_grid()`
- `_render_swiss_column_content()`
- `_render_swiss_stat_block()`
- `_render_swiss_geometric_diagram()`
- `_render_swiss_data_table()`
- `_render_swiss_contents_index()`

### `Enterprise Dark`

The main issue here was not empty pages anymore; it was that consulting/data structures could still feel too generic if slide content was not mapped tightly enough.

Adjusted renderer behavior so Enterprise Dark keeps its consulting rhythm without leaking generic placeholders:

- dashboard cards use content-derived labels instead of fallback KPI filler
- split, architecture, and matrix structures use actual slide semantics
- narrative evidence and comparison pages no longer rely on raw `visual` placeholders for visible labels

Primary renderer functions:

- `_render_enterprise_kpi_dashboard()`
- `_render_enterprise_consulting_split()`
- `_render_enterprise_architecture_map()`
- `_render_enterprise_feature_grid()`
- `_render_enterprise_comparison_matrix()`
- `_render_enterprise_timeline()`
- `_render_enterprise_cta_close()`

### `Data Story`

This preset required the largest logic correction.

1. `risk` no longer routes to `comparison_matrix`.
   `DATA_STORY_ROLE_LAYOUTS["risk"]` now routes to `chart_insight`, which restores page-to-page rhythm.

2. Added slide-local chart gating.
   `_chart_metric_values_from_spec()` only enables charts when the slide itself carries enough numeric signal. Borrowed evidence alone is no longer enough.

3. Added stage-grid fallback for non-numeric chart contexts.
   `kpi_chart`, `chart_insight`, and `workflow_chart` now switch to stage-grid structures when a chart would be semantically fake.

Primary renderer functions:

- `_render_data_story_kpi_chart()`
- `_render_data_story_chart_insight()`
- `_render_data_story_workflow_chart()`
- `_render_data_story_stage_grid()`

## Verification

### Strict validation

All three deterministic outputs pass strict validation:

- [Swiss Modern](/Users/song/projects/slide-creator/demos/ai-native-work-hub-swiss-modern-zh.html)
- [Enterprise Dark](/Users/song/projects/slide-creator/demos/ai-native-work-hub-enterprise-dark-zh.html)
- [Data Story](/Users/song/projects/slide-creator/demos/ai-native-work-hub-data-story-zh.html)

Command:

```bash
python3 tests/validate.py demos/ai-native-work-hub-swiss-modern-zh.html --strict
python3 tests/validate.py demos/ai-native-work-hub-enterprise-dark-zh.html --strict
python3 tests/validate.py demos/ai-native-work-hub-data-story-zh.html --strict
```

Key outcome:

- all 3 strict-green
- `Data Story` visual variety improved from a repeated layout run to `max run: 1`
- no visible placeholder leakage in rendered slide text

### Quality evaluation with BRIEF context

All three now pass quality gates when evaluated with their source BRIEF:

- `Swiss Modern`
  - `style_signature_coverage = 0.7143`
  - `source_fact_coverage = 0.8333`
  - `numeric_faithfulness = 1.0`
- `Enterprise Dark`
  - `style_signature_coverage = 0.6222`
  - `source_fact_coverage = 1.0`
  - `numeric_faithfulness = 1.0`
- `Data Story`
  - `style_signature_coverage = 0.4615`
  - `source_fact_coverage = 0.8333`
  - `numeric_faithfulness = 1.0`

### Tests added

Added regression coverage in [tests/test_low_context_pipeline.py](/Users/song/projects/slide-creator/tests/test_low_context_pipeline.py):

- production work-hub presets keep style signature above minimum thresholds
- no placeholder strings are allowed to leak into rendered visible text
- no consecutive repeated export-role runs are allowed for these production benchmark outputs
- `Data Story` driver/metrics pages must fall back to stage-grid composition when numbers are not slide-local
- `Data Story` risk page must stay off the old repeated `comparison_matrix` route

Current result:

```bash
pytest -q tests/test_low_context_pipeline.py
```

Result:

- `20 passed`

## Why Other Presets Likely Share The Same Issue Class

This is the important forward-looking conclusion.

The bug class was not caused by the visual assets of `Swiss Modern`, `Enterprise Dark`, or `Data Story`. It came from the shared low-context generation pattern:

- coarse role-to-layout routing
- overuse of global evidence
- visible fallback labels
- chart decisions made from weak numeric signals
- insufficient preset-specific rhythm rules

That means any preset family promoted into deterministic low-context rendering is at risk unless it gets the same level of routing and content-assembly discipline.

### Highest-risk families

#### Editorial family

- `Paper & Ink`
- `Notebook Tabs`
- `Modern Newspaper`
- `Vintage Editorial`

Likely shared failure mode:

- mirrored text blocks
- visible `visual`/authoring phrase leakage
- multiple pages collapsing into similar quote/table/list scaffolds

#### Launch / brand / presentation family

- `Aurora Mesh`
- `Bold Signal`
- `Glassmorphism`
- `Electric Studio`
- `Dark Botanical`
- `Creative Voltage`
- `Pastel Geometry`
- `Split Pastel`

Likely shared failure mode:

- overuse of hero + card + split compositions
- deck-level rhythm flattening even when each page is individually valid
- weak preset signature beyond token-level color/typography

#### Technical / dev family

- `Terminal Green`
- `Neon Cyber`
- `Neo-Retro Dev Deck`

Likely shared failure mode:

- borrowed numeric tokens or code-like labels being over-promoted into metric/chart structures
- repetitive terminal/log/table scaffolds

#### Restraint / cultural family

- `Chinese Chan`

Likely shared failure mode:

- evidence density too high for the visual language
- placeholder-derived labels breaking the intended restraint of the preset

## Recommended Next Pass

Before expanding more presets into the deterministic path, add one family-level eval bucket per style family:

1. editorial family benchmark
2. launch/brand family benchmark
3. dev/technical family benchmark
4. restraint/minimal family benchmark

Each bucket should explicitly test:

- style signature coverage
- layout run limits
- placeholder leakage
- source-fact coverage
- chart misuse / numeric-faithfulness

## Final Conclusion

This fix was completed at the skill/generator level, not by patching output files.

The main improvement is not just that the three production presets now render “better looking” decks. The deeper improvement is that the shared low-context renderer now:

- uses slide-local evidence more correctly
- avoids leaking authoring placeholders
- reduces mirrored filler structures
- makes chart decisions more conservatively
- preserves stronger preset-specific rhythm across the deck

That directly lowers the chance that the same class of “looks valid but feels generic” bug will reappear when more presets are promoted.
