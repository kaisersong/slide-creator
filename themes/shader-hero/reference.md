# Shader Hero — 极光封面

A cinematic aurora opening with green-cyan curtains, violet tips, fine vertical filaments and sparse stars, followed by calm ivory editorial pages and a dark closing. Typography retains restrained teal-and-amber accents. Select `custom:shader-hero` or 极光封面; cover animation is automatic. Never ask the user to specify animated page ranges or technical parameters.

## Colors

```css
:root {
  --sh-night: #081B23;
  --sh-paper: #F5F3EB;
  --sh-ink: #152D31;
  --sh-muted: #4F6262;
  --sh-teal: #0B6E6E;
  --sh-light: #C1E7D5;
  --sh-amber: #F5B45C;
  --sh-rule: #CDD4CC;
  --sh-sky: #040A12;
  --sh-aurora-green: #1FFF8A;
  --sh-aurora-cyan: #08ABD4;
  --sh-aurora-violet: #A33BDB;
}
```

## Typography

System sans-serif only: Inter, Helvetica Neue, PingFang SC, Microsoft YaHei, sans-serif. Monospaced labels use SFMono-Regular, Consolas, monospace. No network fonts. Titles use generous line boxes, explicit newline handling, and optional semantic title_emphasis. Body copy remains editable text.

## Layout Types

Use canonical layout roles: `title_grid`, `column_content`, `contents_index`, `geometric_diagram`, `pull_quote`, `cta_close`.

The first slide is always the cover, irrespective of role or layout hints. All remaining pages, including chapter dividers and the closing page, are static. Content layouts use split comparison, ruled index, process sequence, and editorial quote compositions. Preserve caller titles and facts without inserting brand-specific sample copy.

## Signature Elements

- `.sh-label`: small monospaced editorial label.
- `.sh-headline`: large assertion headline; semantic emphasis is amber on dark surfaces and teal on paper.
- `.sh-facts`: ruled facts, spacious columns, or a sequence; avoid generic rounded card walls.
- `.sh-cover-field`: an embedded WebP poster captured from the actual shader at deterministic time zero. Static and animated versions share the same curtain geometry and fine detail.

## Background

One decorative canvas belongs to the first slide only. No content page animation, canvas, gradient field, or transition on slide transforms. An opaque ivory content surface covers the full viewport. The final slide is opaque night ink. Cover text is protected by a permanent dark directional veil; dynamic light is strongest on the right. The sky uses three asymmetric emissive folds, dense narrow vertical filaments, a faint surrounding glow and sparse static stars. Do not replace these with oversized blurred orbs or a plain gradient. Star placement is deterministic and shares the single shader pass; never add a separate animation loop.

## Cover lifecycle

A single canvas and one RAF, using WebGL2 directly for local file:// playback and ordinary HTTP/IP links; HTTPS prefers WebGPU when available. A double-clicked single HTML must animate offline without a local server or additional files. Both shader variants keep the same noise, curtain geometry, colors and bounded 60-second phase. Cache the cover node; measure cover visibility on navigation/scroll/state changes, never inside the animation frame. Stop on leaving the cover, document hidden, pagehide, presentation black screen, print, or reduced motion; resume one loop when eligible. Never copy Fantasy Rainbow's period into an unrelated noise field. Cap pixel ratio at 1.5 and render at 30 fps. Resize uses a small-rect guard and ResizeObserver, including after presentation changes. WebGL context loss stops rendering and reveals the poster; restoration waits for an eligible visible cover before recreating resources.

GPU adapter/device/pipeline acquisition has timeouts. Missing WebGPU or a null adapter selects WebGL2. If both GPU backends are unavailable, or initialization/validation fails, reveal the poster immediately. WebGPU device.lost also reveals the poster. Pending async initialization must not restart a suspended loop. Expose window.__shaderHeroQA backend, frame state, fixed time, fallback, device loss and WebGL context loss/restore controls for verification.

## Export and accessibility

runtime.export_intent of pptx or png removes the canvas and both GPU runtimes at generation time. The result is fully static. Reduced motion, unavailable GPU backends, and @media print show the detailed embedded poster, never a generic gradient substitute. Animation never carries information; canvas is aria-hidden and pointer-events none. Dark text on ivory and light text on night ink; focus remains visible. No CDN scripts or external assets. Source attribution and full MIT license remain in starter and generated animated HTML. When updating curtain geometry, update both WGSL and GLSL and regenerate the embedded poster from the shader canvas at time zero with a 1600×900 viewport and WebP quality 0.9.

## Canonical Export Contract

- Each `.slide` is one viewport with aspect-ratio 16 / 9 and overflow hidden.
- Keep data-notes, data-export-role, direct slide-num-label, and shared playback/editor/presenter shell.
- Only the first page may use a transparent surface; all subsequent pages are opaque and static.
- Preserve all supplied facts, numeric evidence, and title emphasis as real HTML.

## Best For

Product launches, keynote openings, brand stories, and technology presentations that benefit from one memorable first impression.
