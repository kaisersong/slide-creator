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

- **Drop caps** — First letter at `clamp(3rem,6vw,5rem)`, `Cormorant Garamond` 900, `float: left`, `line-height: 0.85`, color `--crimson`
- **Horizontal rules** — `1px solid var(--rule)`, full column width, `margin: 2rem 0`. Double-rule variant: two thin lines 4px apart for section breaks.
- **Pull quotes** — Italic `Cormorant Garamond` 400, preceded and followed by thin rule, 20px left indent. No typographic quote marks needed.
- **Roman numeral section markers** — `I`, `II`, `III` in `Cormorant Garamond` 400 small, `--text-muted`, above headings
- **Narrow column** — Content `max-width: 680px`, centered, `padding: 0 clamp(2rem,8vw,6rem)`. Feels like a page, not a screen.
- No bright colors. No geometric shapes. No gradients. Typography and rules only.

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
