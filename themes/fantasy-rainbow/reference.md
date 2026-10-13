# Fantasy Rainbow — Reference-Fidelity Style Contract

This custom theme is visually derived from the local reference `iridescence-hero.html`. Its identity is deliberately three-part: a full-viewport animated iridescent cover, opaque white editorial report pages, and a dark closing surface. The iridescent field is a hero treatment, not a deck-wide background.

## Colors

```css
:root {
  --iri-ink: #0A0A12;
  --iri-ink-soft: #252532;
  --iri-accent-blue: #5B6CFF;
  --iri-accent-purple: #9B5CFF;
  --iri-accent-cyan: #20BFC4;
  --iri-accent-blue-text: #4152CC;
  --iri-accent-purple-text: #7037D8;
  --iri-accent-cyan-text: #007B83;
  --iri-tint-blue: rgba(91, 108, 255, .08);
  --iri-tint-purple: rgba(155, 92, 255, .08);
  --iri-tint-cyan: rgba(32, 191, 196, .08);
  --iri-cover-keyword-veil-alpha: .81;
  --iri-blue: var(--iri-accent-blue);
  --iri-line: rgba(10, 10, 18, 0.20);
  --iri-paper: rgba(255, 255, 255, 0.26);
  --ic-bg: #EEF7FF;
  --ic-text: #0A0A12;
  --ic-blue: #5B6CFF;
  --ic-cyan: #57E5E9;
  --ic-violet: #A76CFF;
  --ic-pink: var(--ic-violet);
  --ic-purple: #B995FF;
  --ic-ice: #7D70FF;
}
```

On the cover, cyan-blue → blue-violet → limited pink-violet bands come from the shared shader rather than component fills. Pink-violet is a small transition highlight, not a dominant surface; `--ic-pink` remains only as a compatibility alias for `--ic-violet`. The warm-color correction is selective: green-dominant mint and cyan pixels remain on the original field output. Content pages remain opaque white. On content pages, vivid accents occupy only 10%–15% of the visual surface: ordinary prose remains `--iri-ink`, while small text uses the text-safe `--iri-accent-blue-text`, `--iri-accent-purple-text`, or `--iri-accent-cyan-text` variants rather than vivid blue, purple, or cyan. `--iri-accent-blue-text` is the same-hue accessible blue for white content surfaces (6.36:1 contrast); reserve `--iri-accent-blue` for large/display accents. The fixed brand mark uses ink on the dynamic cover, text-safe blue on white content pages, and high-contrast light text on the closing page. The closing page uses a near-black surface with high-contrast light type.

Accent placement follows semantic structure rather than page position. Use blue, purple, and cyan only for restrained title emphasis, small indices, timeline markers, flow edges, borders, and tint surfaces. Never generate oversized decorative words or business phrases that are absent from the BRIEF. The content plan declares an important cover or closing phrase through `narrative.slides[].title_emphasis`; the renderer must never match a preset-specific title or phrase table. When an older BRIEF omits that field, the renderer selects one restrained anchor from the title structure without relying on business copy. Do not color ordinary paragraphs, `.iri-copy`, or `.iri-scene` backgrounds. Vivid cyan has no generic text helper; it is reserved for marker, border, and tint surfaces.

For legacy scene-based BRIEFs, the renderer retains the following accent map:

Accent placement is fixed by page so the deck keeps an editorial rhythm rather than becoming a colored surface: P1 uses blue only for headline `<em>`, while its small label and fact indices remain `--iri-ink` for dynamic-surface contrast; P2 uses a blue fracture scar; P3 outlines `LAST MILE` in blue; P4 uses primary text-safe blue for field numbers and codes; P5 cycles blue, purple, and cyan pipeline tints; P6 uses a vivid blue display total with four small blue/purple/cyan spectrum markers while every spectrum label remains `--iri-ink`; P7 uses primary text-safe blue for contract numbers; P8 cycles gate borders through vivid blue, purple, cyan, and blue, with each `GATE nn` label using the matching text-safe blue, purple, cyan, and blue cycle while gate titles and descriptions remain `--iri-ink`; P9 uses vivid blue for PLAY, vivid purple for EDIT, and text-safe cyan for PRESENT, while keys use primary text-safe blue; P10 uses blue and purple mode numbers; P11 cycles quadrant numbers through text-safe blue, purple, cyan, and blue; and P12 uses blue for closing headline `<em>`. The content plan declares the important cover or closing phrase through `narrative.slides[].title_emphasis`; the renderer must never match a preset-specific title or phrase table. When an older BRIEF omits that field, the renderer selects one restrained anchor from the title structure without relying on business copy. These are semantic anchors only: do not color ordinary paragraphs, `.iri-copy`, or `.iri-scene` backgrounds. Vivid cyan has no generic text helper; it is reserved for marker, border, and tint surfaces.

## Typography

The display stack is `Space Grotesk`, `Noto Sans SC`, `Helvetica Neue`, Arial, and sans-serif. The technical stack is `JetBrains Mono`, `SFMono-Regular`, Menlo, Consolas, and monospace. Do not request fonts over the network. Headlines use very large sizes, line-height near `0.93`, heavy weight, and negative tracking; labels use small uppercase monospaced type with wide tracking.

## Layout Types

Use canonical layout roles: `title_grid`, `contents_index`, `column_content`, `stat_block`, `geometric_diagram`, `data_table`, `pull_quote`, `toc`, `cta_close`, `bento`. Legacy BRIEFs may map those roles to hero, fracture, convergence, brief, pipeline, spectrum, contract, gates, runtime, modes, use-cases, bento, and closing.

A source-faithful BRIEF must declare `structured_content.kind`; that semantic structure takes precedence over role, layout family, and page-index scene cycling.

The safe area is 42–66px horizontally and 42–64px vertically at 1440×900. Every scene preserves one editorial headline anchor. Only the hero preserves an uninterrupted region of the light field; content scenes preserve uninterrupted white space instead. Every data-bearing container must remain orthogonal: no `rotate()` or `skew()` on profiles, timelines, pipelines, diagrams, tables, polls, architecture layers, or their text. A skewed line is allowed only when it is `aria-hidden` decoration. Content topology overrides preset composition: the theme may style typography, color, borders, backgrounds, and accents, but may not replace source grouping, direction, hierarchy, bands, or reading order. Screenshots may be used as QA evidence but never as the final slide surface.

### Structured content

Explicit structured roles may select architecture-stack, context-matrix, call-chain, dual-mode, workshop-grid, capability-landscape, or comparison-table for legacy BRIEFs. Source-faithful `structured_content` may select `personal-profile`, `title-only`, `challenge-flow`, `milestone-timeline`, `three-column-conclusion`, `capability-bridge`, `context-package`, `takeaway-stack`, `interaction-flow-poll`, `layered-architecture`, `layered-call-graph`, `card-sequence`, `card-grid`, `paired-panels`, or `parallel-flows`. These preserve nested groups, nodes, edges, rails, bands, source wording, and stable evidence IDs rather than flattening them into a short list. `title-only` may omit groups. The four generic card/flow kinds may use root `nodes` or `items` instead of groups; their optional `badge`, `title`, and `description` supply the header. Structured content takes precedence over cover/title roles, closing roles, bento layouts, and page-index scene cycling.

### Business content layouts

Keep content text, panels, process strips, and dividers upright and aligned to a horizontal/vertical grid. Do not rotate or skew content containers, text, or comparison dividers. Cover shader bands may remain diagonal.

Use `preferred_layout_family: "bento"` in a BRIEF slide for capabilities, solution summaries, or business use cases. The canonical renderer emits the bento layout regardless of the content page’s position in the deck. Borrow Blue Sky’s mixed-size card composition: one prominent card with supporting smaller cards, handling one through six facts without empty placeholder cards. Keep facts in source order; split a fact at a colon or em dash into its heading and description. Use white paper, thin ink borders, modest 12px corner rounding, and a blue tint on the leading card. Card text stays ink; only small indices use text-safe accent colors. Do not borrow Blue Sky’s glass backgrounds or cloud/orb decoration. On narrow screens use two columns with the leading card spanning the row. Keep bento pages interspersed with report, comparison, and workflow pages.

### Source-dense scene contract

Use editable HTML for source-dense flows, layered architectures, call graphs, matrices, polls, and tables. Never flatten a source screenshot into the final slide, place a screenshot behind replacement text, or use an image as the relationship model. Screenshots are QA references only. Preserve source order and wording in visible nodes, groups, rails, bands, tags, and edges; carry stable IDs and source references into `data-*` evidence attributes.

All content-bearing source-dense containers are orthogonal. Keep task and poll groups independent, architecture layers vertical, safeguards cross-cutting, comparison rows aligned, and relationship lines horizontal or vertical. Do not rotate, skew, clip, or add an inner scrolling region to fit content. At 1280×720, reflow and tighten spacing while keeping body copy at least 11px and interface labels at least 10px.

## Signature Elements

- `.iri-label` — tiny monospaced editorial label without a pill container.
- `.iri-headline` — oversized black assertion title directly on the light field.
- `.iri-facts` and `.iri-fact` — facts separated by thin rules, never cards.
- `.iri-panel` — square black surface reserved for commands and code.
- `.iri-rule` — one-pixel structural divider.
- `.iri-bento` and `.iri-bento-card` — mixed-size business summary cards on white paper; an optional content composition.
- `#iridescence-canvas` — the single full-viewport canvas, visible and animated only behind the cover.

Legacy `.ic-orbit`, `.ic-prism`, `.ic-hero-metric`, glass cards, technical grids, repetitive equal-size rounded card walls, and decorative gradient orbs are forbidden.

## Background

- The single canvas is visible only when the active page is the cover (`slide-1`).
- The hero is transparent and may use a low-opacity directional veil with maximum opacity `0.26`.
- The cover headline emphasis only uses a tight soft white radial veil at `--iri-cover-keyword-veil-alpha: .81` behind the blue glyphs. It is a local bloom without padding, border, pill, plate, or card geometry; the closing headline emphasis receives no veil.
- Content pages (`slide-2` through the penultimate slide) use an opaque `#FFFFFF` or near-white paper surface. They must not reveal the canvas or use large iridescent gradients.
- The final closing page uses an opaque `#0A0A12` surface with light type and no iridescent fill.
- The fallback uses layered diagonal color bands only for the cover. It must not become a radial-gradient orb or a plain blue wash.

## WebGL lifecycle

- Use a single canvas, one `IridescenceController`, and one requestAnimationFrame id.
- Start the RAF only while the active page is `slide-1`. Leaving the cover hides the canvas and stops the RAF; returning to the cover restores both.
- Resolve cover visibility on navigation, scroll, and presentation-mode changes. Cache slide nodes; never scan slide geometry from the animation frame callback. Repeated navigation must leave at most one pending RAF.
- Keep GPU time bounded: wrap elapsed seconds modulo `4 * Math.PI` in JavaScript double precision before uploading `uTime`. The field is periodic because time enters at half speed; wrapping preserves the motion and prevents long-running float quantization, banding, and blocks. Never wrap after conversion to a GPU float.
- Preserve the reference field geometry: 8 iterations, `uTime * 0.5`, and the original cosine color field. Immediately before direct `gl_FragColor` output, derive `warmBias` only when red exceeds green, then blend toward the approved cold-purple mapping. When `warmBias` is zero, leave the original RGB output untouched so mint, cyan, and neutral highlights survive.
- Do not add luminance lift, `smoothstep` whitening, or `mix(col, vec3(1.0), ...)`.
- Shader compile or program link failure triggers fallback without hiding content.
- Handle `webglcontextlost` and `webglcontextrestored`.
- Cancel pending RAF immediately while the document is hidden, printing, on `pagehide`, in presentation black-screen mode, or when reduced motion is requested. Resize, context restoration, and other state updates must not draw or restart it while suspended. Resume only when the cover is visible again.
- CSS starfields or other decorations inside `.iri-scene--hero` automatically share the cover lifecycle. Cover decorations mounted outside the hero must put `data-cover-animation` on their container. The shared runtime sets `data-cover-animating` on the body; the starter pauses animations on the container, descendants, and pseudo-elements whenever the cover is inactive or suspended. Do not hide an infinite animation with opacity alone. Any optional canvas-based starfield must share the same start/stop conditions and cancel its RAF; do not introduce an independent unconditional animation loop.
- Expose deterministic QA controls for time, fallback, context loss/restore, frame statistics, and lifecycle state.

## Navigation performance

- Never animate `transform`, `filter`, or scale on `.slide`, `.slide-content`, or a full-page image wrapper. Do not apply persistent `will-change` to slides, images, or their wrappers.
- Use a short opacity reveal for content. Keep the static `PresentMode` viewport transform used to fit the 1440 × 900 presentation box; it is not a slide transition and must not be removed.
- Verify cover → content → cover in both browsing and presentation mode, including repeated navigation: hidden-cover draw counts must stay unchanged, optional CSS starfields must be paused, and returning to the cover must resume exactly one RAF. Check background-tab, reduced-motion, print, and black-screen transitions too.

## Accessibility and fallback

- Display titles target 7:1 contrast; body text targets 4.5:1 across sampled time frames.
- `prefers-reduced-motion` hides the cover canvas and reveals the deterministic diagonal-band fallback.
- Focus indicators and keyboard navigation remain visible.
- Decorative backgrounds are `aria-hidden` and never intercept input.

## Export and print

- `@media print` hides canvas animation and all non-slide chrome while preserving the cover fallback, white content pages, and dark closing page.
- Every slide remains a 16:9 page without clipping.
- No remote asset, remote font request, module loader, or third-party runtime is allowed.

## Canonical Export Contract

- `.slide` occupies `100vw × 100vh`, retains `aspect-ratio: 16 / 9`, and uses `overflow: hidden`; only the hero is transparent.
- `#iridescence-canvas` appears exactly once.
- `.iri-label`, `.iri-headline`, `.iri-fact`, and `.iri-panel` are required component primitives.
- Each generated slide has exactly one unique `.iri-scene--*` composition class.
- `data-notes`, `data-export-role`, `data-page-bucket`, and `data-preset` provenance survive generation.

## Style Preview Checklist

- The first impression is saturated, continuous, full-screen mint-cyan, cyan-blue, and blue-violet iridescence with large black type; pink-violet remains a limited transition highlight.
- Only the cover shows the light field. Every middle slide reads as an opaque white editorial report page; the final slide reads as a dark closing surface.
- No technical grid, decorative orbit, glass card, pill kicker, high-opacity page background, or shader whitening remains.
- Adjacent content pages change composition, hierarchy, and text anchoring while retaining a disciplined black-on-white report language.
- Business content stays upright: horizontal workflows and vertical comparison dividers; use preferred_layout_family="bento" for a mixed-size capability, solution, or use-case summary.
- The single canvas, fallback, prefers-reduced-motion, WebGL lifecycle, and @media print paths stay testable.
- The visual safe area remains intact at 1280×720 and 1440×900.
