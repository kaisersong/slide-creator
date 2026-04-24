# Paper & Ink — Style Reference

Editorial, literary, thoughtful — a well-designed book or long-read magazine. Content is the hero; design serves it with quiet authority.

---

## Colors

```css
:root {
    --bg: #faf9f7;          /* warm cream */
    --bg-dark: #1a1a18;     /* rich black */
    --text: #1a1a1a;
    --text-muted: #4a4a4a;
    --crimson: #c41e3a;     /* accent — one use per slide maximum */
    --rule: #c41e3a;        /* ornamental rule color — crimson */
    --font-display: "Cormorant Garamond", Georgia, serif;
    --font-body: "Source Serif 4", "Noto Sans SC", Georgia, serif;
    --title-size: clamp(2rem, 6vw, 4rem);
    --h2-size: clamp(1.5rem, 4vw, 2.5rem);
    --body-size: clamp(0.8125rem, 1.5vw, 1.125rem);
    --small-size: clamp(0.6875rem, 1.1vw, 0.875rem);
    --slide-padding: clamp(1.5rem, 4vw, 4rem);
    --content-gap: clamp(0.75rem, 2vw, 2rem);
}
```

---

## Background

```css
body {
    font-family: var(--font-body);
    background: var(--bg);
    color: var(--text);
}

/* Slide background — warm cream canvas */
.slide {
    background: var(--bg);
}

/* Editorial padding — generous, book-like */
.slide-content {
    padding: clamp(3rem, 6vw, 5rem) clamp(3rem, 10vw, 9rem);
}
```

---

## Typography

```css
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Source+Serif+4:wght@400;600&family=Noto+Sans+SC:wght@400;500;700&display=swap');

/* Two serif fonts: Cormorant Garamond for headlines, Source Serif 4 for body. Noto Sans SC as CJK fallback. */

h1 {
    font-family: var(--font-display);
    font-weight: 700;
    font-size: clamp(3.5rem, 9vw, 7rem);
    color: var(--text);
    line-height: 0.95;
    letter-spacing: -0.02em;
}
h1 .crimson { color: var(--crimson); }

h2 {
    font-family: var(--font-display);
    font-weight: 700;
    font-size: clamp(2rem, 5vw, 3.8rem);
    color: var(--text);
    line-height: 1.05;
    letter-spacing: -0.01em;
}
h2 .crimson { color: var(--crimson); }

.body-text {
    font-family: var(--font-body);
    font-size: clamp(0.9rem, 1.5vw, 1.05rem);
    line-height: 1.8;
    color: var(--text);
    max-width: 58ch;
}
```

---

## Components

```css
/* Ornamental horizontal rule with flanking diamonds */
.rule {
    display: flex; align-items: center; gap: 0.8rem;
    margin: clamp(1.2rem, 2.5vh, 2rem) 0;
}
.rule::before, .rule::after {
    content: "\25C6"; color: var(--crimson);
    font-size: 0.4rem; flex-shrink: 0;
}
.rule-line { flex: 1; height: 1px; background: var(--crimson); }

/* Eyebrow — small-caps section label */
.eyebrow {
    font-family: var(--font-display);
    font-variant: small-caps;
    letter-spacing: 0.2em;
    font-size: clamp(0.65rem, 1vw, 0.8rem);
    color: var(--text-muted);
    margin-bottom: clamp(0.5rem, 1vh, 0.8rem);
}

/* Drop cap */
.body-text.drop-cap::first-letter {
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 4em;
    float: left;
    line-height: 0.8;
    margin-right: 0.1em;
    margin-top: 0.05em;
    color: var(--crimson);
}

/* Pull quote */
.pull-quote {
    font-family: var(--font-display);
    font-style: italic;
    font-size: clamp(1.5rem, 4vw, 3rem);
    font-weight: 400;
    color: var(--crimson);
    text-align: center;
    line-height: 1.25;
    max-width: 30ch;
    margin: 0 auto;
}

/* Stats */
.stat-row {
    display: flex; gap: clamp(2rem, 5vw, 4rem);
    margin-top: clamp(1.5rem, 3vh, 2.5rem);
}
.stat-val {
    font-family: var(--font-display);
    font-weight: 700;
    font-size: clamp(2rem, 4vw, 3rem);
    color: var(--crimson);
    display: block;
    line-height: 1;
}
.stat-label {
    font-family: var(--font-body);
    font-size: 0.7rem;
    font-variant: small-caps;
    letter-spacing: 0.15em;
    color: var(--text-muted);
    margin-top: 0.3rem;
    display: block;
}

/* Pain list */
.pain-list { list-style: none; margin-top: clamp(1.5rem, 3vh, 2rem); }
.pain-item {
    display: flex; gap: 1rem; align-items: baseline;
    padding: clamp(0.7rem, 1.2vh, 1rem) 0;
    border-bottom: 1px solid rgba(196,30,58,0.25);
    font-family: var(--font-body);
    font-size: clamp(0.85rem, 1.4vw, 1rem);
    line-height: 1.6;
}
.pain-item:first-child { border-top: 1px solid rgba(196,30,58,0.25); }
.pain-marker { color: var(--crimson); flex-shrink: 0; font-style: italic; }

/* Steps */
.steps { margin-top: clamp(1.5rem, 3vh, 2rem); }
.step {
    display: grid; grid-template-columns: 2.5rem 1fr;
    gap: 1rem; padding: clamp(0.8rem, 1.5vh, 1.2rem) 0;
    border-bottom: 1px solid rgba(26,26,26,0.12);
}
.step:first-child { border-top: 1px solid rgba(26,26,26,0.12); }
.step-num {
    font-family: var(--font-display);
    font-weight: 700;
    font-size: clamp(1.2rem, 2.5vw, 1.8rem);
    color: var(--crimson);
    line-height: 1;
}
.step-text {
    font-family: var(--font-body);
    font-size: clamp(0.85rem, 1.4vw, 1rem);
    line-height: 1.6;
}
.step-text strong { font-weight: 600; color: var(--text); }

/* Preset grid — two-column */
.preset-wrap {
    columns: 2; column-gap: 3rem;
    margin-top: clamp(1.5rem, 3vh, 2rem);
}
@media (max-width: 600px) { .preset-wrap { columns: 1; } }
.preset-item {
    font-family: var(--font-body);
    font-size: clamp(0.82rem, 1.3vw, 0.95rem);
    padding: 0.4rem 0;
    border-bottom: 1px solid rgba(26,26,26,0.1);
    color: var(--text);
    break-inside: avoid;
}
.preset-item.active { color: var(--crimson); font-style: italic; }
.preset-item::before { content: "—\00a0"; color: var(--crimson); }

/* Feature list */
.feature-list { margin-top: clamp(1.5rem, 3vh, 2rem); }
.feature-item {
    padding: clamp(0.8rem, 1.5vh, 1.2rem) 0;
    border-bottom: 1px solid rgba(26,26,26,0.12);
}
.feature-item:first-child { border-top: 1px solid rgba(26,26,26,0.12); }
.feature-name {
    font-family: var(--font-display);
    font-weight: 700;
    font-size: clamp(0.9rem, 1.5vw, 1.1rem);
    font-variant: small-caps;
    letter-spacing: 0.1em;
    color: var(--crimson);
    margin-bottom: 0.25rem;
}
.feature-desc {
    font-family: var(--font-body);
    font-size: clamp(0.8rem, 1.3vw, 0.95rem);
    color: var(--text-muted);
    line-height: 1.6;
}

/* Install block */
.install-block {
    background: #1a1a1a;
    color: #faf9f7;
    font-family: 'Courier New', monospace;
    font-size: clamp(0.7rem, 1.1vw, 0.85rem);
    padding: clamp(1rem, 2vw, 1.5rem) clamp(1.2rem, 2.5vw, 2rem);
    margin: clamp(0.8rem, 1.5vh, 1.2rem) 0;
    line-height: 1.7;
    border-left: 3px solid var(--crimson);
}
.install-block .comment { color: #888; font-style: italic; }

/* CTA command */
.cta-cmd {
    font-family: var(--font-display);
    font-weight: 700;
    font-size: clamp(3rem, 8vw, 6rem);
    color: var(--text);
    letter-spacing: -0.02em;
    line-height: 1;
    margin: clamp(1rem, 2vh, 1.5rem) 0;
}
.cta-cmd .crimson { color: var(--crimson); font-style: italic; }

/* How it works */
.how-items { margin-top: clamp(1.5rem, 3vh, 2rem); }
.how-item {
    display: grid; grid-template-columns: 3rem 1fr;
    gap: 1.2rem; align-items: start;
    padding: clamp(0.8rem, 1.5vh, 1.2rem) 0;
    border-bottom: 1px solid rgba(26,26,26,0.12);
}
.how-item:first-child { border-top: 1px solid rgba(26,26,26,0.12); }
.how-num {
    font-family: var(--font-display);
    font-weight: 700;
    font-size: clamp(1.2rem, 2.5vw, 1.8rem);
    color: var(--crimson);
    line-height: 1;
}
.how-body h3 {
    font-family: var(--font-display);
    font-weight: 700;
    font-size: clamp(1rem, 1.7vw, 1.2rem);
    margin-bottom: 0.2rem;
}
.how-body p {
    font-family: var(--font-body);
    font-size: clamp(0.78rem, 1.2vw, 0.9rem);
    color: var(--text-muted);
    line-height: 1.6;
}
```

---

## Named Layout Variations

### 1. Cover / Hero

Eyebrow label → large h1 with crimson accent word → ornamental rule with diamonds → body text (max 44ch) → stat row (3 stats with crimson values + small-caps labels) → page footer `— NN —`.

Per-slide CSS for `#slide-1`:
```css
#slide-1 {
    justify-content: flex-start;
    padding: clamp(3rem, 6vw, 5rem) clamp(3rem, 10vw, 9rem);
}
#slide-1 .slide-content {
    align-items: flex-start; text-align: left;
    padding-top: clamp(2rem, 5vh, 4rem);
}
#slide-1 h1 { margin-bottom: clamp(1rem, 2vh, 1.5rem); }
#slide-1 .hero-body { margin-bottom: clamp(1rem, 2vh, 1.5rem); }
```

### 2. Problem Statement

Eyebrow → h2 with crimson phrase → rule → pain list (3 items with roman numeral markers in crimson italic, crimson-bordered bottom lines).

### 3. Style Discovery

Eyebrow → h2 with crimson phrase → rule → body text with drop cap (large crimson first letter) → 3 steps (roman numerals in crimson, grid layout).

### 4. Preset Grid

Eyebrow → h2 with crimson phrase → rule → two-column preset list (preset items with crimson dash prefix, active item in crimson italic).

### 5. Manifesto (dark block)

Centered layout on dark background. Eyebrow → large headline in white with crimson accent → list of manifesto points with subtle borders.

Per-slide CSS for `#slide-5`:
```css
#slide-5 {
    background: var(--bg-dark) !important;
    justify-content: center; align-items: center;
}
#slide-5 .manifesto-inner { max-width: 680px; text-align: center; }
#slide-5 .manifesto-headline {
    font-family: var(--font-display); font-weight: 700;
    font-size: clamp(2rem, 5vw, 3.5rem);
    color: #fff; line-height: 1.2;
    margin-bottom: clamp(1.5rem, 3vh, 2.5rem);
}
#slide-5 .manifesto-headline .crimson { color: var(--crimson); }
#slide-5 .manifesto-points { list-style: none; text-align: left; }
#slide-5 .manifesto-points li {
    padding: clamp(0.7rem, 1.2vh, 1rem) 0;
    font-size: var(--body-size);
    color: rgba(255,255,255,0.55);
    line-height: 1.65;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
#slide-5 .manifesto-points li:first-child {
    border-top: 1px solid rgba(255,255,255,0.06);
}
#slide-5 .slide-num-label { color: rgba(255,255,255,0.15); }
```

### 6. Features

Eyebrow → h2 with crimson phrase → rule → feature list (small-caps crimson names + descriptions, bordered items).

### 7. Install

Eyebrow → h2 with crimson phrase → rule → install blocks (dark background, crimson left border, monospace code) → page footer.

### 8. CTA / Closing

Centered layout. Eyebrow → pull quote (large crimson italic) → rule → large cta command `/slide-creator` with crimson italic → body text → page footer.

Per-slide CSS for closing slide:
```css
#slide-8 { justify-content: center; text-align: center; align-items: center; }
```

---

## Signature Elements

### CSS Overlays
- No body-level overlays. Clean warm cream canvas throughout.

### Animations
- `@keyframes crossFade`: Simple opacity 0 to 1 (no transform, no movement) —
  ```css
  @keyframes crossFade { from { opacity: 0; } to { opacity: 1; } }
  .reveal { opacity: 0; }
  .slide.visible .reveal { animation: crossFade 0.8s ease forwards; }
  ```
- Stagger delays: 0.1s, 0.2s, 0.35s, 0.5s, 0.65s, 0.8s, 0.95s, 1.1s (up to 8 elements)

### Required CSS Classes
- `.rule`: Ornamental horizontal rule with flanking crimson diamonds
- `.rule-line`: The line inside `.rule` — `height: 1px; background: var(--crimson)`
- `.eyebrow`: Small-caps section label — `font-variant: small-caps; letter-spacing: 0.2em`
- `.body-text`: Body copy — `max-width: 58ch; font-family: var(--font-body)`
- `.body-text.drop-cap`: First letter at `4em`, crimson, `float: left`
- `.pull-quote`: Centered, italic, crimson, `max-width: 30ch`
- `.pain-list` / `.pain-item` / `.pain-marker`: Roman numeral markers in crimson italic
- `.stat-row` / `.stat-val` / `.stat-label`: Row of stats with crimson values + small-caps labels
- `.preset-wrap`: Two-column list with crimson dash prefix; `.active` = crimson italic
- `.feature-list` / `.feature-item` / `.feature-name`: Small-caps crimson names + descriptions
- `.install-block`: Dark code block with `border-left: 3px solid var(--crimson)`
- `.cta-cmd`: Large command text — `clamp(3rem, 8vw, 6rem)`
- `.steps` / `.step` / `.step-num`: Grid layout with crimson numerals
- `.how-items` / `.how-item` / `.how-num`: Alternative step layout with h3 + p

### Allowed Components
- Audit coverage: .comment .crimson .feature-desc .hero-body .manifesto-headline .manifesto-inner .manifesto-points .preset-item
- Audit coverage cont.: .slide-num-label .step-text

### Background Rule
`body` sets `background: var(--bg)` (warm cream). No gradient, no pattern, no overlay. Pure typographic canvas. Per-slide backgrounds (e.g., manifesto) use `#slide-N { background: var(--bg-dark) }`.

### Style-Specific Rules
- **Crimson is the ONLY accent color** (`#c41e3a`) — max one use per slide for emphasis
- **No geometric shapes, no gradients, no illustrations** — typography and rules only
- **Narrow content column**: `max-width: 58ch` on `.body-text`, feels like a printed page
- **Two serif fonts**: Cormorant Garamond for headlines/stats, Source Serif 4 for body, Noto Sans SC as CJK fallback
- **Preset items**: Active item gets crimson italic styling (`.preset-item.active`)
- **Feature names**: Small-caps + crimson + `letter-spacing: 0.1em`
- **Progress bar**: Solid crimson `#c41e3a`, 2px height

### Signature Checklist
- [ ] Warm cream background `var(--bg)` / `#faf9f7` — no gradients, no patterns
- [ ] Ornamental rules with crimson diamonds (`.rule::before/after`)
- [ ] Cormorant Garamond serif for headlines via `var(--font-display)` — Chinese text falls back to system serif (宋体)
- [ ] Source Serif 4 for body text via `var(--font-body)` with Noto Sans SC as CJK fallback
- [ ] Crimson accent `var(--crimson)` / `#c41e3a` used sparingly (once per slide max)
- [ ] Cross-fade animation only (no movement, no transforms)
- [ ] Small-caps for labels and page numbers
- [ ] CSS variables for all style tokens (--font-display, --font-body, --bg, --text, --crimson, etc.)

---

## Animation

```css
.reveal {
    opacity: 0;
    transition: opacity 0.6s ease;
}
.reveal.visible { opacity: 1; }
.reveal:nth-child(1) { transition-delay: 0.1s; }
.reveal:nth-child(2) { transition-delay: 0.25s; }
.reveal:nth-child(3) { transition-delay: 0.4s; }
```

---

## Style Preview Checklist

- [ ] Warm cream background `#faf9f7`
- [ ] Cormorant Garamond serif for headlines (中文标题回退到系统宋体，保持衬线风格)
- [ ] Source Serif 4 for body text
- [ ] Noto Sans SC as body CJK fallback only
- [ ] Narrow content column (max 58ch body text)
- [ ] No bright colors, no geometric shapes, no gradients
- [ ] Crimson accent used sparingly (once per slide max)
- [ ] All style tokens use CSS variables

---

## Best For

Long-read presentations · Thought leadership · Literary topics · Academic talks · Brand storytelling · Content-heavy narratives · Editorial showcases
