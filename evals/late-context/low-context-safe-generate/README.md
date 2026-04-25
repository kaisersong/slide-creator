# Low-Context-Safe Generate Eval Notes

Use these cases to prove the optimization improves robustness without flattening rich-context output.

This eval layer should answer two questions:

1. Does the pipeline stay stable when context is noisy or scarce?
2. Does the pipeline avoid making strong-context decks bland in order to get that stability?

Recommended protocol:

- compare current pipeline as control vs low-context-safe pipeline as treatment
- use the same case set, same model, and same settings
- run low-context buckets at least 5 times each
- run rich-context benchmarks at least 3 times each

Recommended buckets:

- same-BRIEF parity pair
- sparse-BRIEF fallback
- invalid BRIEF fail-closed
- high-context rich benchmark
- core runtime/style guard cases from `core-md-guard/`

Recommended diagnostics:

- `quality_tier`
- `strict_pass_first_try`
- `repair_rounds`
- `route_drift`
- `layout_variety`
- `avg_component_kinds_per_slide`
- `style_signature_coverage`
- `chrome_leak`
- `content_occlusion_risk`
- `numeric_faithfulness`
- `source_fact_coverage`
- `narrative_role_coverage`
- `minimal_slide_ratio`
- `max_minimal_slide_run`
- `latency_ms.packet`
- `latency_ms.assemble`
- `latency_ms.validate`

Recommended executable entrypoint:

- `python3 scripts/eval-quality.py <deck.html> --brief <BRIEF.json> --source <source.md>`

This quality layer exists because a deck can pass `strict validate` and still fail the user:

- runtime chrome leaks into the slide surface
- fixed panels occlude body copy
- chart values are invented instead of sourced
- narrative rhythm collapses into repeated title-only scaffolds

Success should be judged by both:

- stronger low-context stability
- no meaningful regression on rich-context benchmark cases
