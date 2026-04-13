# Vintage Editorial — Style Reference

Witty, confident, editorial, personality-driven. Cream background with abstract geometric accents.

---

## Colors

```css
:root {
    --bg-cream: #f5f3ee;
    --text-primary: #1a1a1a;
    --text-secondary: #555;
    --accent-warm: #e8d4c0;
}
```

---

## Background

```css
body {
    background: var(--bg-cream);
    font-family: "Fraunces", "Work Sans", -apple-system, sans-serif;
}

/* Abstract geometric shapes — no illustrations */
.editorial-circle {
    position: absolute;
    border: 2px solid var(--text-primary);
    border-radius: 50%;
    opacity: 0.15;
    pointer-events: none;
}
.editorial-line {
    position: absolute;
    width: 1px;
    height: clamp(60px, 12vh, 120px);
    background: var(--text-primary);
    opacity: 0.12;
}
.editorial-dot {
    position: absolute;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--text-primary);
    opacity: 0.2;
}
```

---

## Typography

```css
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Work+Sans:wght@400;500&display=swap');

.editorial-title {
    font-family: "Fraunces", Georgia, serif;
    font-size: clamp(28px, 5.5vw, 56px);
    font-weight: 900;
    color: var(--text-primary);
    line-height: 1.05;
}

.editorial-body {
    font-family: "Work Sans", sans-serif;
    font-size: clamp(13px, 1.4vw, 16px);
    font-weight: 400;
    color: var(--text-primary);
    opacity: 0.7;
    line-height: 1.65;
}

.editorial-quote {
    font-family: "Fraunces", Georgia, serif;
    font-size: clamp(20px, 3vw, 32px);
    font-weight: 700;
    font-style: italic;
    color: var(--text-primary);
    line-height: 1.3;
}

.editorial-cta-box {
    border: 2px solid var(--text-primary);
    border-radius: 4px;
    padding: clamp(16px, 2.5vw, 24px);
    text-align: center;
}
```

---

## Components

```css
/* Abstract geometric circle */
.editorial-circle {
    position: absolute;
    border: 2px solid var(--text-primary);
    border-radius: 50%;
    opacity: 0.15;
    pointer-events: none;
}

/* Accent line */
.editorial-line {
    position: absolute;
    width: 1px;
    height: clamp(60px, 12vh, 120px);
    background: var(--text-primary);
    opacity: 0.12;
}

/* Dot accent */
.editorial-dot {
    position: absolute;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--text-primary);
    opacity: 0.2;
}

/* Bold bordered CTA box */
.editorial-cta-box {
    border: 2px solid var(--text-primary);
    border-radius: 4px;
    padding: clamp(16px, 2.5vw, 24px);
    text-align: center;
    background: var(--bg-cream);
}
```

---

## Signature Elements

- Abstract geometric shapes (circle outline + line + dot)
- Bold bordered CTA boxes
- Witty, conversational copy style
- **No illustrations — only geometric CSS shapes**

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

- [ ] Cream background `#f5f3ee`
- [ ] Fraunces serif at 900 weight for headlines
- [ ] At least one geometric shape (circle/line/dot)
- [ ] Bold bordered CTA boxes present
- [ ] No illustrations — only CSS shapes

---

## Best For

Personal brands · Thought leadership · Creative agency pitches · Witty presentations · Editorial content · Brand storytelling
