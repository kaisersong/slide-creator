# Swiss Modern — Style Reference

Clean, precise, Bauhaus-inspired — International Typographic Style as a presentation. Form follows function absolutely. The grid is not a tool; it is the design.

---

## Colors

```css
:root {
    --bg: #ffffff;
    --bg-dark: #0a0a0a;
    --text: #0a0a0a;
    --text-light: #ffffff;
    --text-muted: #666666;
    --red: #ff3300;       /* single accent — one element per slide maximum */
    --grid-line: rgba(0, 0, 0, 0.05);
}
```

---

## Background

```css
body {
    background: var(--bg);
    font-family: "Archivo Black", "Nunito", -apple-system, sans-serif;
}

/* Visible 12-column grid — faintly visible */
.swiss-grid {
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(var(--grid-line) 1px, transparent 1px),
        linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
    background-size: calc(100vw / 12) 100vh;
    pointer-events: none;
    z-index: 0;
}
```

---

## Typography

```css
@import url('https://fonts.googleapis.com/css2?family=Archivo+Black:wght@900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600&display=swap');

.swiss-title {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(32px, 7vw, 72px);
    font-weight: 900;
    color: var(--text);
    line-height: 1.0;
    letter-spacing: -0.02em;
    text-transform: uppercase;
}

.swiss-body {
    font-family: "Nunito", sans-serif;
    font-size: clamp(12px, 1.4vw, 15px);
    font-weight: 400;
    color: var(--text);
    line-height: 1.55;
    max-width: 55ch;
}

.swiss-label {
    font-family: "Archivo", sans-serif;
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
}

.swiss-stat {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(48px, 8vw, 96px);
    font-weight: 900;
    color: var(--text);
    line-height: 1.0;
}
```

---

## Components

```css
/* Hard horizontal rule — no decorative curves, no dashes */
.swiss-rule {
    height: 2px;
    background: var(--text);
    border: none;
}
.swiss-rule.red {
    background: var(--red);
}
.swiss-rule-thin {
    height: 1px;
    background: var(--text-muted);
    opacity: 0.2;
}
```

---

## Named Layout Variations

### 1. Title Grid

Slide number top-right in `Archivo Black` 1rem, red. Title bottom-left in 7rem, 2 lines max, `line-height: 0.95`. Empty upper-right quadrant. Red `2px` horizontal rule above the title.

### 2. Column Content

Left column 40%: large section heading + red `2px` rule below. Right column 55% (5% gap): body text in two typographic sub-columns. Section number top-right in small red.

### 3. Stat Block

One large number left half at 8rem `Archivo Black`. Vertical `2px` black rule to its right. Then: label in 1.2rem uppercase + 1-line supporting sentence in 0.9rem body. Red underline on the number only.

### 4. Data Table

Full-width table. Header row: `Archivo Black` 11px uppercase, `background: #0a0a0a`, white text. Body: alternating `#ffffff` / `#f7f7f7` rows, `1px #e0e0e0` dividers. Most important row: `3px` red left-border. No outer border.

### 5. Geometric Diagram

SVG diagram of boxes + connector lines, `stroke: #0a0a0a`, `stroke-width: 1.5`. No fills except primary node: `fill: #ff3300`. Labels in `Nunito` 12px. Grid visible behind. No shadows.

### 6. Pull Quote

One short sentence (max 12 words) in 3rem `Archivo Black`, top-left. Below it: `2px` red rule + attribution in 0.8rem `Nunito`. Remaining 50%+ of slide: pure white. Emptiness is the message.

### 7. Contents Index

Numbered list, left-aligned. Each item: section number in `3rem Archivo Black` red, em-dash, topic in `1.5rem Archivo Black` black. Max 5 items. Visible grid behind. No borders on items.

---

## Signature Elements

- **Visible grid** — 12-column grid as `::before` pseudo on each `.slide`. Present, never overwhelming.
- **Red accent** — `#ff3300` for exactly one element per slide: a rule, a number, an underline, or a single word. Never a large fill.
- **Asymmetric anchoring** — Titles attach to left or bottom-left. Negative space is deliberately top-right.
- **Hard horizontal rules** — `2px solid #0a0a0a` for section separations. No decorative curves, no dashes.
- **Large structural numbers** — Section counts and stats in `6–9rem Archivo Black` as visual anchors.
- No gradients. No shadows. No rounded corners. No illustrations.

---

## Animation

```css
.reveal {
    opacity: 0;
    transition: opacity 0.4s ease;
}
.reveal.visible { opacity: 1; }
.reveal:nth-child(1) { transition-delay: 0.05s; }
.reveal:nth-child(2) { transition-delay: 0.15s; }
.reveal:nth-child(3) { transition-delay: 0.25s; }
```

---

## Style Preview Checklist

- [ ] White background with faint 12-column grid
- [ ] Archivo Black at 900 weight, uppercase headlines
- [ ] Red `#ff3300` accent on exactly one element per slide
- [ ] Hard horizontal rules (2px solid black)
- [ ] No gradients, no shadows, no rounded corners
- [ ] Asymmetric anchoring — left or bottom-left, never centered

---

## Best For

Corporate presentations · Data reports · Architecture firm decks · Design studio pitches · Swiss/International style showcases · Precise, data-heavy content
