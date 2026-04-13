# Pastel Geometry — Style Reference

Friendly, organized, modern, approachable. White card on pastel background with vertical pills.

---

## Colors

```css
:root {
    --bg-primary: #c8d9e6;
    --card-bg: #faf9f7;
    --pill-pink: #f0b4d4;
    --pill-mint: #a8d4c4;
    --pill-sage: #5a7c6a;
    --pill-lavender: #9b8dc4;
    --pill-violet: #7c6aad;
    --text-primary: #1a1a1a;
    --text-secondary: #666666;
}
```

---

## Background

```css
body {
    background: var(--bg-primary);
    font-family: "Plus Jakarta Sans", -apple-system, sans-serif;
}
```

---

## Typography

```css
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700;800&display=swap');

.pastel-title {
    font-family: "Plus Jakarta Sans", sans-serif;
    font-size: clamp(28px, 5vw, 48px);
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1.1;
    letter-spacing: -0.02em;
}

.pastel-body {
    font-family: "Plus Jakarta Sans", sans-serif;
    font-size: clamp(13px, 1.4vw, 16px);
    font-weight: 400;
    color: var(--text-primary);
    opacity: 0.7;
    line-height: 1.6;
}

.pastel-label {
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
/* Rounded card with soft shadow */
.pastel-card {
    background: var(--card-bg);
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.08);
    padding: clamp(20px, 3vw, 32px);
}

/* Vertical pills on right edge */
.pastel-pill {
    position: absolute;
    right: 0;
    width: clamp(24px, 3vw, 32px);
    border-radius: 4px 0 0 4px;
}
.pastel-pill.short  { height: clamp(30px, 5vh, 50px); }
.pastel-pill.medium { height: clamp(50px, 8vh, 80px); }
.pastel-pill.tall   { height: clamp(80px, 12vh, 120px); }
.pastel-pill.pink   { background: var(--pill-pink); }
.pastel-pill.mint   { background: var(--pill-mint); }
.pastel-pill.sage   { background: var(--pill-sage); }
.pastel-pill.lavender { background: var(--pill-lavender); }
.pastel-pill.violet { background: var(--pill-violet); }
```

---

## Signature Elements

- Rounded card with soft shadow
- **Vertical pills on right edge** with varying heights (like tabs)
- Consistent pill width, heights: short → medium → tall → medium → short
- Download/action icon in corner

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

- [ ] Pastel blue background `#c8d9e6`
- [ ] White card with soft shadow
- [ ] Vertical pills on right edge with varying heights
- [ ] Plus Jakarta Sans at 800 weight for headlines
- [ ] Friendly, approachable feel

---

## Best For

Product overviews · Onboarding presentations · Team introductions · User-friendly pitches · Educational content
