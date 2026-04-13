# Split Pastel — Style Reference

Playful, modern, friendly, creative. Two-color vertical split with badge pills.

---

## Colors

```css
:root {
    --bg-peach: #f5e6dc;
    --bg-lavender: #e4dff0;
    --text-dark: #1a1a1a;
    --text-secondary: #666666;
    --badge-mint: #c8f0d8;
    --badge-yellow: #f0f0c8;
    --badge-pink: #f0d4e0;
}
```

---

## Background

```css
body {
    background: var(--bg-peach);
    font-family: "Outfit", -apple-system, sans-serif;
}

/* Two-color vertical split */
.split-pastel-left {
    background: var(--bg-peach);
    height: 100%;
}
.split-pastel-right {
    background: var(--bg-lavender);
    height: 100%;
}

/* Grid pattern overlay on right panel */
.split-pastel-grid {
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(0,0,0,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,0,0,0.04) 1px, transparent 1px);
    background-size: 24px 24px;
    pointer-events: none;
}
```

---

## Typography

```css
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;700;800&display=swap');

.split-title {
    font-family: "Outfit", sans-serif;
    font-size: clamp(28px, 5vw, 48px);
    font-weight: 800;
    color: var(--text-dark);
    line-height: 1.1;
    letter-spacing: -0.02em;
}

.split-body {
    font-family: "Outfit", sans-serif;
    font-size: clamp(13px, 1.4vw, 16px);
    font-weight: 400;
    color: var(--text-dark);
    opacity: 0.7;
    line-height: 1.6;
}

.split-label {
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-secondary);
}
```

---

## Components

```css
/* Badge pill with icon */
.split-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 700;
}
.split-badge.mint    { background: var(--badge-mint); }
.split-badge.yellow  { background: var(--badge-yellow); }
.split-badge.pink    { background: var(--badge-pink); }

/* Rounded CTA button */
.split-cta {
    display: inline-flex;
    align-items: center;
    padding: clamp(10px, 1.5vw, 14px) clamp(20px, 3vw, 32px);
    border-radius: 9999px;
    background: var(--text-dark);
    color: var(--bg-peach);
    font-family: "Outfit", sans-serif;
    font-size: clamp(12px, 1.3vw, 14px);
    font-weight: 700;
    border: none;
    cursor: pointer;
}
```

---

## Signature Elements

- Split background colors (peach left, lavender right)
- Playful badge pills with icons
- Grid pattern overlay on right panel
- Rounded CTA buttons

---

## Animation

```css
.reveal {
    opacity: 0;
    transform: translateY(16px);
    transition: opacity 0.5s ease, transform 0.5s ease;
}
.reveal.visible { opacity: 1; transform: translateY(0); }
.reveal:nth-child(1) { transition-delay: 0.05s; }
.reveal:nth-child(2) { transition-delay: 0.15s; }
.reveal:nth-child(3) { transition-delay: 0.25s; }
```

---

## Style Preview Checklist

- [ ] Peach `#f5e6dc` left panel, lavender `#e4dff0` right panel
- [ ] Badge pills (mint/yellow/pink) visible
- [ ] Grid pattern on right panel
- [ ] Outfit at 800 weight for headlines
- [ ] Rounded CTA buttons

---

## Best For

Creative agency presentations · Product launches · Friendly brand decks · Design showcases · Startup pitches
