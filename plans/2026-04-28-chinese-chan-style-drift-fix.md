# 2026-04-28 Chinese Chan Style Drift Fix

## Scope

- Input source: `/Users/song/Downloads/life-meaning (2).html`
- Standard-flow regenerated deck: [life-meaning-chinese-chan-regenerated-zh.html](/Users/song/projects/slide-creator/demos/life-meaning-chinese-chan-regenerated-zh.html)
- BRIEF: [life-meaning-chinese-chan-BRIEF.json](/Users/song/projects/slide-creator/plans/life-meaning-chinese-chan-BRIEF.json)
- Render packet: [life-meaning-chinese-chan-packet.json](/Users/song/projects/slide-creator/plans/life-meaning-chinese-chan-packet.json)

## User-visible problems

1. `Noto Serif CJK SC` metrics looked larger/heavier than the demo reference.
2. Cover felt visually left-shifted from P1 onward.
3. Titles and emphasis rhythm did not match `Chinese Chan`.
4. Divider looked like a horizontal line first, dots second.
5. `EB Garamond` rhythm was largely absent from generated content.
6. `ghost-kanji` rendered as near-black instead of muted gray.
7. P8 stat row showed meaningless `10 / 1 / 1`.
8. Long close-page vertical titles could collide or clip.

## Root cause

### 1. Reference drift inside `references/chinese-chan.md`

The file had two overlapping generations of CSS:

- an older block that defined `.zen-rule` as a plain horizontal line and used `Noto Serif CJK SC`
- a later block that defined the intended flanked-dot rule and more restrained Chan rhythm

Because the generated HTML consumes the style reference directly, both definitions were emitted. The older line-first rule kept contributing `height/background`, which made the divider feel heavier than the demo.

### 2. Font stack drift

The formal reference had drifted to `Noto Serif CJK SC` as the primary Chinese serif, while the demo rhythm was closer to `Noto Serif SC`. That changed perceived weight, width, and line color.

### 3. Missing stat component contract

The formal reference had almost no complete `.zen-stat` base styles. As a result:

- `EB Garamond` was not strongly present in generated stat numerals
- the stat row looked generic

### 4. Weak `zen_stat` semantic mapping

The renderer treated `numeric_facts` and `supporting_facts` too mechanically:

- value extraction kept numeric prefixes such as `10`, `1`, `1`
- labels were compacted again, so the cards lost the action meaning

### 5. Fragile vertical close layout

`zen_vertical` originally placed the caption and seal with absolute positioning, which made long titles vulnerable to clipping/overlap in browser QA.

## Fixes

### Reference / contract

Updated [references/chinese-chan.md](/Users/song/projects/slide-creator/references/chinese-chan.md):

- switched primary serif stack to `Noto Serif SC`, with `Songti SC` and `Noto Serif CJK SC` as fallbacks
- removed the stale line-first `.zen-rule` block
- restored explicit `.zen-stat`, `.zen-stat .num`, `.zen-stat .label` component styles
- made `ghost-kanji` muted gray with lower opacity
- aligned prose contract text with the actual intended font and ornament rules

### Renderer

Updated [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py):

- strengthened `Chinese Chan` stat number typography with `EB Garamond`
- changed `zen_vertical` shell from absolute-positioned caption/seal to a safer flow layout
- added `numeric_facts` priority for `zen_stat`
- added `label` derivation from `supporting_facts` suffixes, so `10分钟：写下最近让你开心的小事` becomes:
  - `num = 10分钟`
  - `label = 写下最近让你开心的小事`
- shortened long vertical close titles to the semantic tail when needed, instead of forcing the full sentence into one vertical object
- pushed `ghost-kanji` farther off-canvas and lighter, reducing the false “left shift” perception on the cover

## Verification

- `python3 main.py --validate-brief --brief plans/life-meaning-chinese-chan-BRIEF.json`
- `python3 main.py --generate --brief plans/life-meaning-chinese-chan-BRIEF.json --output demos/life-meaning-chinese-chan-regenerated-zh.html --packet-out plans/life-meaning-chinese-chan-packet.json`
- `python3 scripts/validate_html.py demos/life-meaning-chinese-chan-regenerated-zh.html --strict`
- `python3 scripts/title_browser_qa.py demos/life-meaning-chinese-chan-regenerated-zh.html --preset 'Chinese Chan' --strict --output /tmp/life-meaning-chinese-chan-title-qa-20260428.json`
- `pytest -q tests/test_priority_preset_reference_contracts.py tests/test_low_context_pipeline.py tests/test_validate_priority_preset_contracts.py`

## Result

- `strict validate`: pass
- `title_browser_qa`: pass
- targeted tests: `38 passed`

## Notes

- The standard-flow regenerated deck is `9` slides, not `10`.
- The user-mentioned “P10 title overlap” maps to the same underlying `zen_vertical` fragility. The formal fix was applied at the renderer/layout level anyway, so long closing titles now degrade safely.
