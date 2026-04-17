# Paper & Ink — Style Reference

Editorial, literary, thoughtful — a well-designed book or long-read magazine. Content is the hero; design serves it with quiet authority.

---

## Colors

```css
:root {
    --bg: #faf9f7;          /* warm cream */
    --bg-dark: #1a1a18;     /* rich black */
    --text: #1a1a1a;
    --text-muted: #666666;
    --crimson: #c41e3a;     /* accent — one use per slide maximum */
    --rule: #c4b8a4;        /* warm paper rule color */
}
```

---

## Background

```css
body {
    background: var(--bg);
    font-family: "Cormorant Garamond", "Source Serif 4", Georgia, serif;
}

/* Narrow content column — feels like a printed page */
.paper-content {
    max-width: 680px;
    margin: 0 auto;
    padding: 0 clamp(24px, 8vw, 80px);
}
```

---

## Typography

```css
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600&display=swap');

.paper-title {
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: clamp(28px, 5vw, 52px);
    font-weight: 900;
    color: var(--text);
    line-height: 1.05;
}

.paper-body {
    font-family: "Source Serif 4", Georgia, serif;
    font-size: clamp(14px, 1.5vw, 18px);
    font-weight: 400;
    color: var(--text);
    line-height: 1.78;
}

.paper-quote {
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: clamp(20px, 3vw, 36px);
    font-weight: 400;
    font-style: italic;
    color: var(--text);
    line-height: 1.4;
}

.paper-roman {
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: clamp(14px, 1.8vw, 20px);
    font-weight: 400;
    font-variant: small-caps;
    color: var(--text-muted);
}

.paper-stat {
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: clamp(36px, 6vw, 60px);
    font-weight: 900;
    color: var(--crimson);
    line-height: 1.0;
}
```

---

## Components

```css
/* Drop cap — first letter */
.paper-dropcap::first-letter {
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: clamp(48px, 6vw, 72px);
    font-weight: 900;
    float: left;
    line-height: 0.85;
    margin-right: 0.1em;
    color: var(--crimson);
}

/* Horizontal rule — warm paper color */
.paper-rule {
    height: 1px;
    background: var(--rule);
    border: none;
    margin: clamp(24px, 4vw, 40px) 0;
}

/* Pull quote */
.paper-pullquote {
    font-family: "Cormorant Garamond", Georgia, serif;
    font-style: italic;
    font-size: clamp(20px, 3vw, 32px);
    line-height: 1.4;
    padding-left: clamp(16px, 2.5vw, 24px);
    border-top: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule);
    margin: clamp(20px, 3vw, 32px) 0;
    color: var(--text);
}

/* Roman numeral section marker */
.paper-roman-marker {
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: clamp(12px, 1.3vw, 16px);
    font-variant: small-caps;
    color: var(--text-muted);
    margin-bottom: 8px;
}
```

---

## Named Layout Variations

### 1. Chapter Opening

Roman numeral + chapter title in 5rem `Cormorant Garamond`, left-aligned. Thin horizontal rule below. Opening paragraph with drop cap beneath. Generous whitespace above the title (40%+ of slide height).

### 2. Long Read

Two-column body layout (magazine spread). Left: first 3 paragraphs. Right: continuation. `1px --rule` vertical separator. Pull quote spanning both columns at midpoint, breaking the grid intentionally.

### 3. Pull Quote

Single sentence in 2.5rem italic `Cormorant Garamond`, left-aligned or centered. Thin rule above and below. Attribution in 0.8rem `Source Serif 4`. Remaining slide: cream. The silence amplifies the quote.

### 4. Annotated

Main text in left 60% column. Right 40%: marginal annotation column in 0.75rem `--text-muted`, separated by `1px --rule`. Each annotation: small superscript number matching the main text.

### 5. The Statistic

One large number in `6rem Cormorant Garamond 900`, `--crimson`. Below: 2-line plain explanation in body size. Above: thin double-rule. Remaining space: cream.

### 6. Index Page

Reference list. Each entry: right-aligned page number (tabular-nums), dotted leader line `· · ·`, topic title. `Source Serif 4` body, `Cormorant Garamond` for the numbers. Max 8 entries.

### 7. Colophon (Closing)

Centered, small text only. Publication/deck title in `Cormorant Garamond` italic. Thin rule. 2–3 lines of closing copy. One crimson accent: a single word or `—` dash. Feels like the last page of a book.

---

## Signature Elements

### CSS Overlays
- No body-level overlays. Clean cream canvas throughout.

### Animations
- `@keyframes crossFade`: Simple opacity 0 to 1 (no transform, no movement) —
  ```css
  @keyframes crossFade { from { opacity: 0; } to { opacity: 1; } }
  .reveal { opacity: 0; }
  .slide.visible .reveal { animation: crossFade 0.8s ease forwards; }
  ```
- Stagger delays: 0.1s, 0.2s, 0.35s, 0.5s, 0.65s, 0.8s, 0.95s, 1.1s (up to 8 elements)

### Required CSS Classes
- `.rule`: Ornamental horizontal rule with flanking crimson diamonds —
  ```css
  .rule { display: flex; align-items: center; gap: 0.8rem; }
  .rule::before, .rule::after { content: '◆'; color: #c41e3a; font-size: 0.4rem; }
  .rule-line { flex: 1; height: 1px; background: #c41e3a; }
  ```
- `.drop-cap` (on `.body-text`): First letter at `4em`, crimson, `float: left`, `line-height: 0.8`
- `.pull-quote`: Centered, italic, crimson (`#c41e3a`), `max-width: 30ch`
- `.eyebrow`: Small-caps section label, `font-variant: small-caps`, `letter-spacing: 0.2em`, muted color
- `.page-footer`: Centered page number at bottom, small-caps, `— NN —` format
- `.pain-marker`: Crimson italic roman numeral (`.`, `ii`, `iii`) prefix for pain points
- `.install-block`: Dark code block (`#1a1a1a`) with `border-left: 3px solid #c41e3a`

### Background Rule
`body` and `.slide` both set `background: #faf9f7` (warm cream). No gradient, no pattern, no overlay. Pure typographic canvas.

### Style-Specific Rules
- **Crimson is the ONLY accent color** (`#c41e3a`) — max one use per slide for emphasis
- **No geometric shapes, no gradients, no illustrations** — typography and rules only
- **Narrow content column**: `max-width: 58ch` on `.body-text`, feels like a printed page
- **Two serif fonts**: Cormorant Garamond for headlines/stats, Source Serif 4 for body
- **Preset items**: Active item gets crimson italic styling (`.preset-item.active`)
- **Feature names**: Small-caps + crimson + `letter-spacing: 0.1em`
- **Progress bar**: Solid crimson `#c41e3a`, 2px height

### Signature Checklist
- [ ] Warm cream background `#faf9f7` — no gradients, no patterns
- [ ] Ornamental rules with crimson diamonds (`.rule::before/after`)
- [ ] Cormorant Garamond serif for headlines
- [ ] Source Serif 4 for body text
- [ ] Crimson accent `#c41e3a` used sparingly (once per slide max)
- [ ] Cross-fade animation only (no movement, no transforms)
- [ ] Small-caps for labels and page numbers

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
- [ ] Cormorant Garamond serif for headlines
- [ ] Source Serif 4 for body text
- [ ] Narrow content column (max 680px)
- [ ] No bright colors, no geometric shapes, no gradients
- [ ] Crimson accent used sparingly (once per slide max)

---

## Best For

Long-read presentations · Thought leadership · Literary topics · Academic talks · Brand storytelling · Content-heavy narratives · Editorial showcases
