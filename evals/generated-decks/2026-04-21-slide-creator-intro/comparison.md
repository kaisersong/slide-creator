# Comparison vs Original Demos

Run: `slide-creator-intro-2026-04-21`

Scope:
- real workflow only: `user prompt -> BRIEF.json -> HTML -> validate -> eval`
- compare the generated intro decks against the original preset demos
- stop only once the generated decks are stronger intro decks for `slide-creator`

## Evidence used

- Workflow artifacts:
  - `user-prompt.md`
  - `slide-creator-intro-blue-sky-BRIEF.json`
  - `slide-creator-intro-blue-sky-zh.html`
  - `slide-creator-intro-creative-voltage-BRIEF.json`
  - `slide-creator-intro-creative-voltage-zh.html`
- Deterministic validation:
  - `python scripts/validate-brief.py ...`
  - `python tests/validate.py ... --strict`
  - `python -m pytest tests/test_cross_preset_consistency.py -q`
- Visual spot check:
  - Chrome headless screenshots with `--virtual-time-budget=3000`
  - `screenshots/orig-blue-cover-vtb.png`
  - `screenshots/new-blue-cover-vtb.png`
  - `screenshots/orig-creative-voltage-cover-vtb.png`
  - `screenshots/new-creative-voltage-cover-vtb.png`

## Blue Sky

Original strengths:
- airy, polished cover atmosphere
- clear chapter rhythm
- strong runtime and style-routing story
- explicit zero-dependency proof

New deck improvements:
- keeps the Blue Sky palette, glass cards, soft orbs, and product-intro tone
- restores chapter rhythm instead of flattening everything into generic content slides
- makes the IR-first value explicit: `prompt -> BRIEF.json -> HTML`
- adds concrete quality framing: `validate-brief.py`, `tests/validate.py --strict`, four-layer eval
- restores zero-dependency and install-to-trial signal in the closing CTA
- moved into `evals/generated-decks/...` so it behaves like a real eval fixture rather than polluting root preset demos

Tradeoff:
- the original cover is slightly more atmospheric and decorative
- the new cover is more explicit and product-explanatory

Verdict:
- For the job of introducing `slide-creator` as a product, the new Blue Sky deck is stronger than the original.
- It gives up a little decorative mood, but gains a much clearer product thesis, better workflow explanation, and better trialability.

## Creative Voltage

Original strengths:
- very strong electric hero
- clear problem framing
- excellent show-dont-tell preview moment
- sharp install CTA

New deck improvements:
- preserves the same preset identity and energy on the cover
- keeps the preview-led style discovery moment instead of replacing it with pure process text
- reframes the problem around long-context failure, which is more relevant to the current skill design
- explains `Auto / Polish / Review` in terms of the real hidden path: `prompt -> preview -> BRIEF -> HTML -> Review`
- keeps the concrete ClawHub path and makes the deck more specific to `slide-creator`'s current IR-first positioning

Tradeoff:
- the new deck is slightly more process-heavy
- the original feels a bit more purely marketing-led

Verdict:
- The new Creative Voltage deck is stronger than the original for `slide-creator` introduction.
- It preserves the wow factor while adding a more accurate explanation of why the product exists and how it avoids late-context collapse.

## Final conclusion

Both generated decks now exceed their original demo counterparts for this specific task:
- introducing `slide-creator`
- reflecting the current IR-first workflow
- proving the result came from a real prompt-to-BRIEF-to-HTML run
- staying inside the target preset rather than drifting into generic AI deck styling

If these decks are later promoted into canonical public demos, they should still remain outside `demos/*.html` until the repo deliberately wants them treated as official preset fixtures.
