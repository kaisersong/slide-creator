# Modern Newspaper — Style Reference

Authoritative, punchy, "smart & pop" — Japan's new economy business media meets Swiss editorial design. Information feels curated and consequential, not decorative.

---

## Colors

```css
:root {
    --bg: #f7f5f0;           /* aged newsprint white */
    --bg-dark: #111111;      /* sumi black */
    --text: #111111;
    --text-muted: #555555;
    --yellow: #FFCC00;       /* electric yellow — accent only */
    --red: #FF3333;          /* alert red — sparingly */
    --rule: #111111;         /* column rules */
}
```

---

## Background

```css
body {
    background: var(--bg);
    font-family: 'Oswald', 'Source Serif 4', -apple-system, sans-serif;
}
```

---

## Typography

```css
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400&display=swap');

.np-headline {
    font-family: 'Oswald', 'Arial Narrow', sans-serif;
    font-size: clamp(3.5rem, 11vw, 8rem);
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: -0.02em;
    line-height: 0.95;
    color: var(--text);
}

.np-subhead {
    font-family: 'Oswald', sans-serif;
    font-size: clamp(1rem, 2.5vw, 1.8rem);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.np-body {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: clamp(0.65rem, 1vw, 0.85rem);
    line-height: 1.65;
    color: var(--text-muted);
    max-width: 38ch;
}

.np-stamp {
    font-family: 'IBM Plex Mono', monospace;
    font-size: clamp(0.55rem, 0.8vw, 0.7rem);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
}

.np-red { color: var(--red); }

.np-dark {
    background: var(--bg-dark);
    color: #f7f5f0;
}
.np-dark .np-body { color: rgba(247,245,240,0.6); }
```

---

## Components

```css
/* Yellow accent bar */
.np-bar-h {
    width: 100%;
    height: 10px;
    background: var(--yellow);
}
.np-bar-v {
    width: 8px;
    height: 100%;
    background: var(--yellow);
    flex-shrink: 0;
}

/* Column rule */
.np-rule {
    width: 1px;
    background: var(--rule);
    align-self: stretch;
    margin: 0 clamp(16px, 2.5vw, 40px);
}

/* 12-column grid base */
.np-grid {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: 0 clamp(8px, 1.5vw, 24px);
    height: 100%;
    padding: clamp(24px, 4vw, 64px);
}
```

---

## Named Layout Variations

### 1. Cover / Masthead

Publication name top-left (small, mono), yellow horizontal bar beneath it. Off-center headline fills 40% of slide bottom-left (2–5 words). Date and issue number top-right. Subtitle 3 lines max, bottom-right corner, 8px body. Large empty zone upper-right.

### 2. Breaking Headline

One-sentence headline in 9rem Oswald occupies top 45% of slide. Yellow 10px bar separates it from evidence zone below. Below bar: two columns — left is 4–5 line body, right is one bold statistic in 3rem + 1-line label. Nothing else.

### 3. Split Column

Vertical column rule divides slide 40/60. Left 40%: black panel, yellow bar on left edge, white headline in Oswald. Right 60%: newsprint background, body text in 3 short paragraphs, mono label top-right.

### 4. Data Brief

One number dominates center-left at 8–10rem, colored `var(--yellow)` outline text (webkit-text-stroke: 3px #111, fill transparent) or solid black. Below it: 1-line label in mono. Right side: 4-bullet context list in 0.75rem body. Massive negative space top and right.

### 5. Feature Story (Asymmetric)

Headline anchors bottom-left (4rem, 3 lines max). Upper-left: yellow bar 8px + section label. Body text column bottom-right (3 short paras). Upper-right 40% of slide: completely empty. Creates cinematic tension.

### 6. Contents / Index

4–6 numbered items in two columns. Each item: `01` in 2rem Oswald yellow, em-dash, topic in 1.2rem Oswald black, 1-line descriptor in 0.7rem body. Yellow horizontal rules between items. Issue stamp top-right.

### 7. Pull Quote

Large opening quote mark `"` in 12rem Oswald at 8% opacity as background texture. Quote text in 2rem Source Serif 4, 3 lines max, left-aligned. Attribution: 1px rule + name in 0.75rem mono. Nothing else on slide.

### 8. Closing / Back Page (Inverted)

Full slide `var(--bg-dark)`. Yellow bar top-full-width. White headline bottom-left. Mono CTA bottom-right. Optional: thin red single-word emphasis. Mirrors the Cover layout but dark — signals closure.

---

## Signature Elements

- **Yellow bar** — 8–14px solid `#FFCC00` horizontal or vertical rule; marks transitions, section openers, and emphasis anchors. Never used as a background fill for large areas.
- **Column rules** — `1px solid #111111` vertical lines to divide grid areas, evoking newspaper columns.
- **Issue stamp** — Top corner in `IBM Plex Mono` 10px: `VOL.01 · NO.03` or a date. Grounds the slide in journalistic convention.
- **Extreme headline scale** — The headline IS the slide. `font-size: clamp(4rem, 12vw, 9rem)`, `font-weight: 900`, `text-transform: uppercase`. Body text follows at ≤ 1/10th the size.
- **Negative space as editorial choice** — At least 30% of the slide should be empty. Do not fill it.
- **Red sparingly** — `#FF3333` for one word, one number, or one callout per slide maximum. Never for large backgrounds.
- No gradients. No shadows. No illustrations. No photos. Typography and geometry only.

## Prohibitions

- No markdown symbols in text (`#`, `*`, `**`)
- No gradients on large areas
- No drop shadows
- No centered layouts — always anchor to a corner or edge
- No more than 2 type sizes per slide (headline + body)
- `#FFCC00` and `#FF3333` never appear on the same slide together

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

- [ ] Aged newsprint white `#f7f5f0` background
- [ ] Extreme headline-to-body ratio (minimum 10:1)
- [ ] Yellow bar `#FFCC00` accent visible
- [ ] Oswald at 900 weight, UPPERCASE headlines
- [ ] At least 30% empty space on every slide
- [ ] Issue stamp in mono (VOL.01 · NO.XX)

---

## Best For

Business reports · Thought leadership · Annual reports · Journalism-style presentations · Economic briefings · Strategic communications
