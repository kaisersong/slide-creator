# Neo-Retro Dev Deck — Style Reference

90s computer manuals meet modern AI dev tools — engineering notebook aesthetic. Pixel-art icons, thick black outlines, opinionated developer voice. Feels handmade and confident, like a zine printed at a hackathon.

---

## Colors

```css
:root {
    --bg: #f5f2e8;           /* engineering notebook cream */
    --grid: rgba(80, 100, 170, 0.10);  /* faint blue grid lines */
    --text: #111111;
    --pink: #FF3C7E;          /* hot pink — AI / intelligence concepts */
    --yellow: #FFE14D;        /* bright yellow — tools / builds */
    --cyan: #00C8FF;          /* cyan — web / networking */
    --border: #111111;        /* thick outlines */
    --block-bg: #ffffff;
    --block-dark: #1a1a1a;
}
```

---

## Background

```css
body {
    background-color: var(--bg);
    background-image:
        linear-gradient(var(--grid) 1px, transparent 1px),
        linear-gradient(90deg, var(--grid) 1px, transparent 1px);
    background-size: 24px 24px;
    font-family: "Barlow Condensed", "IBM Plex Sans", -apple-system, sans-serif;
}
```

---

## Typography

```css
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=swap');

.retro-title {
    font-family: "Barlow Condensed", sans-serif;
    font-size: clamp(28px, 6vw, 56px);
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: -0.01em;
    line-height: 1.0;
    color: var(--text);
}

.retro-body {
    font-family: "IBM Plex Sans", sans-serif;
    font-size: clamp(13px, 1.4vw, 16px);
    font-weight: 400;
    color: var(--text);
    line-height: 1.5;
}

.retro-mono {
    font-family: "IBM Plex Mono", monospace;
    font-size: clamp(11px, 1.2vw, 14px);
    color: var(--text);
}

.retro-comment {
    font-family: "IBM Plex Mono", monospace;
    font-size: clamp(11px, 1.2vw, 14px);
    color: var(--text);
    opacity: 0.5;
}
.retro-comment::before { content: '// '; }

.retro-label {
    font-family: "IBM Plex Mono", monospace;
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
```

---

## Components

```css
/* Thick bordered block — hard offset shadow */
.retro-block {
    background: var(--block-bg);
    border: 3px solid var(--border);
    border-radius: 0;
    box-shadow: 4px 4px 0 var(--border);
    padding: clamp(16px, 2.5vw, 24px);
}
.retro-block:hover {
    box-shadow: 2px 2px 0 var(--border);
    transform: translate(2px, 2px);
    transition: none;
}

/* Color-coded top border */
.retro-block.pink  { border-top: 4px solid var(--pink); }
.retro-block.yellow { border-top: 4px solid var(--yellow); }
.retro-block.cyan   { border-top: 4px solid var(--cyan); }

/* Section badge */
.retro-badge {
    display: inline-block;
    background: var(--yellow);
    border: 2px solid var(--border);
    border-radius: 0;
    padding: 2px 8px;
    font-family: "IBM Plex Mono", monospace;
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* Highlighted text */
.retro-highlight {
    background: var(--yellow);
    border: 2px solid var(--border);
    padding: 0 4px;
    display: inline;
}
```

---

## Named Layout Variations

### 1. System Architecture

Title top-left in `Barlow Condensed`. Center: stacked horizontal layer blocks (each = a system component). Colors indicate category: pink=AI, yellow=tools, cyan=web. Each block: `3px border`, monospace label inside, hard offset shadow. Arrow connectors `2px` between layers.

### 2. Evolution / Timeline

Horizontal flow left to right. Each era: thick-bordered box, era label in `IBM Plex Mono` badge, 2-line `Barlow Condensed` description. `→` arrow between boxes. Current era: `border-color: var(--pink)`, subtle pink fill. Future: dashed border.

### 3. Feature Cards

3-card row or 2×2 grid. Each card: pixel SVG icon top-right corner, feature name in `Barlow Condensed` 1.4rem, `// 1–2 line comment` in mono below. Border: `3px --border`, hard shadow. Top border accent: one of pink/yellow/cyan per card, consistent with color system.

### 4. Before / After

Two-panel split. `BEFORE` header left (muted, `#666`), `AFTER` right (green `#22c55e` or cyan). Each panel: thick border, content in `IBM Plex Mono` or `Barlow`. Divider: `4px` hard black center line. Clear improvement framing — no bad news.

### 5. Manifesto / Thesis

Large bold statement in `Barlow Condensed` 900 UPPERCASE, 40%+ of slide. Below: 3 `// supporting points` in `IBM Plex Mono` 0.9rem. One key word in the headline: `background: var(--yellow)` highlight, `2px --border`, inline. Everything in one thick-bordered content block.

### 6. Metrics Dashboard

Pixel-style bar chart: bars are thick-bordered rectangles (not rounded), fill with color codes. Y-axis: simple tick marks in mono. Each bar labeled below in `IBM Plex Mono`. Key bar: pink or yellow fill. Title above in `Barlow Condensed`. Chart sits inside one large bordered block.

---

## Signature Elements

- **Thick bordered blocks** — `border: 3px solid var(--border)`, `border-radius: 0` or `4px` max
- **Hard offset shadow** — `box-shadow: 4px 4px 0 var(--border)` on all content blocks
- **Color coding** (consistent across the deck): pink = AI/intelligence, yellow = tools/builds, cyan = web/networking
- **Pixel-style SVG icons** — 32×32px, flat colors, `2px` grid-aligned strokes, black outlines, zero gradients
- **Section badge** — `IBM Plex Mono` uppercase label in `background: var(--yellow)` pill, `border: 2px solid var(--border)`, `border-radius: 0`
- **Opinionated annotations** — `// short comment` in `IBM Plex Mono` 0.8rem, max 8 words
- No stock photos. No gradients on large areas. No rounded corners above 4px.

## Tone Rules

- Declarative sentences only: `"It runs 3× faster"` not `"We're excited to share..."`
- No buzzwords: no "revolutionary", "game-changing", "cutting-edge", "robust"
- `//` comment style for sub-points and annotations
- Numbers over adjectives: `"83ms p95"` not `"blazing fast"`
- One opinion per slide, stated plainly

---

## Animation

```css
.reveal {
    opacity: 0;
    transition: opacity 0.3s ease;
}
.reveal.visible { opacity: 1; }
.reveal:nth-child(1) { transition-delay: 0.05s; }
.reveal:nth-child(2) { transition-delay: 0.1s; }
.reveal:nth-child(3) { transition-delay: 0.15s; }
```

---

## Style Preview Checklist

- [ ] Cream background `#f5f2e8` with faint blue grid
- [ ] Thick-bordered blocks with hard offset shadows
- [ ] Barlow Condensed at 900 weight, UPPERCASE headlines
- [ ] `//` comment style annotations in mono
- [ ] Color coding: pink/yellow/can consistent across deck
- [ ] No rounded corners above 4px
- [ ] No gradients on large areas

---

## Best For

Dev tool launches · API documentation · Engineering team updates · Hackathon presentations · Open-source project pitches · Technical architecture reviews
