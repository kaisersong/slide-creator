# Coral Dawn — Style Reference

Warm, optimistic, and human. Inspired by early morning light over terracotta rooftops — the feeling of a fresh start. Cream backgrounds with coral accents and generous whitespace. Approachable yet professional.

---

## Colors

```css
/* Light variant */
:root {
    --bg:           #FDFAF6;   /* warm cream */
    --bg-secondary: #F5EFE6;   /* slightly deeper cream for cards */
    --text:         #2C1A0E;   /* warm dark brown, not pure black */
    --text-muted:   #8C6F5A;   /* mid-tone warm brown */
    --accent:       #E8541A;   /* coral — use once per slide */
    --accent-soft:  #FDEEE7;   /* coral tint for backgrounds */
    --rule:         rgba(44,26,14,0.12);
}
```

**Forbidden:** cool grays, blue-tinted whites, neon colors, drop shadows, decorative borders.

---

## Typography

```css
/* Display — expressive serif for titles */
.cd-title {
    font-family: "Playfair Display", "Georgia", serif;
    font-weight: 700;
    font-size: clamp(2rem, 5vw, 4.5rem);
    line-height: 1.15;
    letter-spacing: -0.02em;
    color: var(--text);
}

/* Body — clean humanist sans */
.cd-body {
    font-family: "Source Sans 3", "Helvetica Neue", sans-serif;
    font-weight: 400;
    font-size: clamp(0.95rem, 1.6vw, 1.15rem);
    line-height: 1.8;
    color: var(--text);
}

/* Label / eyebrow */
.cd-label {
    font-family: "Source Sans 3", sans-serif;
    font-size: clamp(0.65rem, 1vw, 0.75rem);
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--accent);
}

/* Stat / number */
.cd-stat {
    font-family: "Playfair Display", serif;
    font-size: clamp(2.5rem, 6vw, 5rem);
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
}
```

---

## Layout

```css
.cd-slide {
    background: var(--bg);
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: clamp(2.5rem, 7vw, 7rem) clamp(2rem, 8vw, 10rem);
    position: relative;
    overflow: hidden;
}

/* Left accent bar — signature element, use on content slides */
.cd-slide.accented::before {
    content: '';
    position: absolute;
    left: 0; top: 15%; bottom: 15%;
    width: 4px;
    background: var(--accent);
    border-radius: 0 2px 2px 0;
}

/* Card */
.cd-card {
    background: var(--bg-secondary);
    border-radius: 16px;
    padding: clamp(1.25rem, 2.5vw, 2rem);
}

/* Horizontal rule with coral dot */
.cd-divider {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: clamp(1rem, 2.5vh, 2rem) 0;
    color: var(--rule);
}
.cd-divider::before {
    content: '';
    flex: 1;
    height: 1px;
    background: currentColor;
}
.cd-divider-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--accent);
    flex-shrink: 0;
}
.cd-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: currentColor;
}
```

---

## Animation

```css
/* Warm fade-up — relaxed, not snappy */
.cd-reveal {
    opacity: 0;
    transform: translateY(18px);
    transition: opacity 0.7s ease, transform 0.7s ease;
}
.slide.visible .cd-reveal { opacity: 1; transform: translateY(0); }
.slide.visible .cd-reveal:nth-child(1) { transition-delay: 0.05s; }
.slide.visible .cd-reveal:nth-child(2) { transition-delay: 0.18s; }
.slide.visible .cd-reveal:nth-child(3) { transition-delay: 0.31s; }
.slide.visible .cd-reveal:nth-child(4) { transition-delay: 0.44s; }
```

---

## Font Loading

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
```

---

## Signature Elements

1. **Left accent bar** — 4px coral vertical line on left edge of content slides (`.cd-slide.accented::before`)
2. **Eyebrow label** — small uppercase coral text above the main heading
3. **Mixed type pairing** — Playfair Display (serif) headlines + Source Sans 3 (sans) body
4. **Coral stat numbers** — large Playfair Display figures for metric slides

---

## Checklist

- [ ] Warm cream `#FDFAF6` background — no white, no cool grays
- [ ] Coral accent used on ONE element per slide (stat, label, or accent bar)
- [ ] Playfair Display for all headings, Source Sans 3 for body
- [ ] Left accent bar on content slides (not title or closing)
- [ ] Generous horizontal padding — content never fills full width

---

## Best For

Founder storytelling · Consumer brand launches · Education & EdTech · Health & wellness · Human-centered product decks · Any talk where warmth and approachability matter
