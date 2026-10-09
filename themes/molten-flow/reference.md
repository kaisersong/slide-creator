# Molten Flow — 熔金流体

A sculptural, twisted liquid-metal ribbon with a bright gold/amber/orange reflected surface on a near-black warm field. The ribbon rotates and changes its folds smoothly; it must look dimensional with sharp glints and dark recesses, never a blurred gradient orb. Ray marching stays inside the sculpture bounding sphere. The content pages are warm ivory editorial surfaces with burnt-orange text accents.

Select `custom:molten-flow` or 熔金流体. Defaults are sufficient: only the first slide animates; no follow-up questions about page ranges or shader parameters.

## Colors

```css
:root {
  --sh-night: #160C0A;
  --sh-paper: #F9F2E5;
  --sh-ink: #321D17;
  --sh-muted: #70544A;
  --sh-teal: #A3421E;
  --sh-light: #FFE5B9;
  --sh-amber: #FFCA70;
  --sh-rule: #DDCFC1;
}
```

The shader's lighting colors and shape are authoritative in effect.frag. Starter CSS carries the local typography, shell contrast, cover veil and embedded fallback image. Do not recolor ordinary content paragraphs with bright shader colors.

## Typography

System sans-serif: Inter, Helvetica Neue, PingFang SC, Microsoft YaHei, sans-serif. Labels use SFMono-Regular, Consolas, monospace. No network font requests. Large statement headlines preserve explicit newline handling and caller title_emphasis. Keep glyph-safe line boxes and strong contrast.

## Layout Types

Use canonical layout roles: `title_grid`, `column_content`, `contents_index`, `geometric_diagram`, `pull_quote`, `cta_close`.

The first slide is the animated cover, independent of role hints. Comparison/split, ruled index, process sequence and quote compositions make content-page rhythm. Content and closing pages are opaque and static. Keep all caller facts in real editable DOM; numeric_facts is an auxiliary index rather than extra invented rows.

## Signature Elements

- `.sh-label`: monospaced opening/content/finish label.
- `.sh-headline`: large editable assertion with restrained semantic emphasis.
- `.sh-facts`: ruled facts, columns or a sequence, not a generic rounded card wall.
- `.sh-cover-field`: a detailed poster captured from this actual shader at time zero and embedded as a WebP data URI.

## Background

A sculptural, twisted liquid-metal ribbon with a bright gold/amber/orange reflected surface on a near-black warm field. The ribbon rotates and changes its folds smoothly; it must look dimensional with sharp glints and dark recesses, never a blurred gradient orb. Ray marching stays inside the sculpture bounding sphere. The content pages are warm ivory editorial surfaces with burnt-orange text accents.

The only canvas is decorative, fixed behind the first slide, aria-hidden and pointer-events none. A permanent dark directional veil protects cover text. All subsequent pages use opaque surfaces. No shader field or animation on content pages, including chapter dividers and closing.

## Runtime and offline playback

Use the shared references/cover-effects-runtime.js controller embedded by scripts/build-cover-themes.py. Both the starter and generated HTML are self-contained. Single canvas, one RAF, WebGL2 on file://, plain HTTP/IP and HTTPS; no server, modules, CDN, additional files or network access are needed for local playback. Cap at 30 fps and DPR 1.25. The shared controller bounds phase to a 30-second period; shader coordinates must remain seamless at wrap. Resolution scale is 1.

Cache the cover node and check its visibility only on navigation, scroll and state changes. Stop RAF on leaving the cover, document hidden, pagehide, presentation black screen, print and reduced motion. Resume at most one RAF on an eligible visible cover. Rect-driven canvas sizing needs the small-rect guard and ResizeObserver. WebGL context loss reveals the poster; restoration must not restart while the cover is inactive or suspended. Shader or program failure also reveals the poster. Expose window.__coverEffectQA state, fixed time, fallback and context loss/restore controls.

## Export and accessibility

runtime.export_intent pptx/png removes canvas and GPU runtime at generation time. Static export, unavailable graphics, reduced motion and @media print all retain the detailed embedded poster, not a plain gradient. Focus, navigation, edit mode and speaker notes remain usable. Text and facts carry all information; animation is purely decorative.

When effect.frag or the shared controller changes, run scripts/build-cover-themes.py molten-flow. When shader geometry changes, capture with window.__coverEffectQA.capturePoster() in a 1600×900 viewport (the draw and read must share one task), save the returned WebP as cover.webp, then rebuild so it is embedded in the starter. Do not add independent animations.

## Canonical Export Contract

- Every `.slide` is one viewport, aspect-ratio 16 / 9, with overflow hidden.
- Keep data-notes, data-export-role, direct slide-num-label and the shared playback/editor/presenter shell.
- Exactly one animated cover and one canvas; all content and closing scenes remain static.
- Static export output contains no canvas or graphics initialization.
- Preserve supplied titles, local facts, numeric evidence and semantic title emphasis.
