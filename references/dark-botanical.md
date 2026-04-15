# Dark Botanical — Style Reference

Elegant, sophisticated, artistic, premium. Abstract soft shapes on dark canvas.

---

## Colors

```css
:root {
    --bg-primary: #0f0f0f;
    --text-primary: #e8e4df;
    --text-secondary: #9a9590;
    --accent-warm: #d4a574;
    --accent-pink: #e8b4b8;
    --accent-gold: #c9b896;
}
```

---

## Background

```css
body {
    background: var(--bg-primary);
    font-family: "Cormorant", "IBM Plex Sans", -apple-system, sans-serif;
}

/* Abstract soft gradient circles (blurred, overlapping) */
.botanical-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);
    pointer-events: none;
}
.orb-terracotta {
    width: clamp(200px, 30vw, 400px);
    height: clamp(200px, 30vw, 400px);
    background: rgba(212,165,116,0.15);
}
.orb-pink {
    width: clamp(150px, 25vw, 300px);
    height: clamp(150px, 25vw, 300px);
    background: rgba(232,180,184,0.12);
}
.orb-gold {
    width: clamp(100px, 20vw, 250px);
    height: clamp(100px, 20vw, 250px);
    background: rgba(201,184,150,0.10);
}
```

---

## Typography

```css
@import url('https://fonts.googleapis.com/css2?family=Cormorant:wght@400;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400&display=swap');

.botanical-title {
    font-family: "Cormorant", Georgia, serif;
    font-size: clamp(28px, 5vw, 56px);
    font-weight: 400;
    font-style: italic;
    color: var(--text-primary);
    line-height: 1.2;
}

.botanical-body {
    font-family: "IBM Plex Sans", sans-serif;
    font-size: clamp(13px, 1.4vw, 16px);
    font-weight: 300;
    color: var(--text-secondary);
    line-height: 1.7;
}

.botanical-accent {
    font-family: "Cormorant", Georgia, serif;
    font-style: italic;
    color: var(--accent-warm);
}

.botanical-label {
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 400;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--text-secondary);
    opacity: 0.6;
}
```

---

## Components

```css
/* Thin vertical accent line */
.botanical-vline {
    width: 1px;
    height: clamp(40px, 8vh, 80px);
    background: var(--accent-warm);
    opacity: 0.4;
}

/* Elegant card */
.botanical-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(232,228,223,0.08);
    border-radius: 2px;
    padding: clamp(20px, 3vw, 32px);
}
```

---

## Named Layout Variations

### 1. Botanical Hero (全屏宣告)

Dark `#0f0f0f` background with 2-3 soft gradient orbs (`.botanical-orb`). Centered headline in Cormorant italic, `clamp(28px, 5vw, 56px)`. Subtitle in muted warm white. Orbs: terracotta `rgba(212,165,116,0.15)`, pink `rgba(232,180,184,0.12)`, gold `rgba(201,184,150,0.10)` — large (200-400px), `filter: blur(60px)`.

```html
<section class="slide">
    <div class="botanical-orb orb-terracotta" style="top:-5%;right:-5%;"></div>
    <div class="botanical-orb orb-pink" style="bottom:10%;left:-3%;"></div>
    <div class="slide-content" style="text-align:center;">
        <h1 class="botanical-title">Title</h1>
        <p class="botanical-body">Subtitle</p>
    </div>
</section>
```

### 2. Botanical Card (功能亮点/双列功能卡)

Single `.botanical-card` centered on dark background with orbs. Card: `background: rgba(255,255,255,0.02)`, `border: 1px solid rgba(232,228,223,0.08)`, `border-radius: 2px`. Warm accent text for emphasis. Minimal — card floats on dark canvas.

### 3. Botanical Split (分栏证据)

Two columns on dark background. Left: `.botanical-label` + headline + body. Right: evidence list with `.botanical-accent` lead words. Thin vertical accent line `.botanical-vline` (1px, warm gold, opacity 0.4) between columns. 1-2 orbs behind content.

### 4. Botanical Stat (大数字强调)

Large italic number in `.botanical-accent` (warm gold `#d4a574`), `clamp(3rem, 8vw, 6rem)`, Cormorant italic. Label below in `.botanical-label` (small, uppercase, muted). 1-2 orbs positioned at corners. Clean, minimal — let the number breathe.

---

## Signature Elements

- Abstract soft gradient circles (blurred, overlapping)
- Warm color accents (pink, gold, terracotta)
- Thin vertical accent lines
- Italic signature typography
- **No illustrations — only abstract CSS shapes**

---

## Animation

```css
.reveal {
    opacity: 0;
    transition: opacity 0.8s ease;
}
.reveal.visible { opacity: 1; }
.reveal:nth-child(1) { transition-delay: 0.1s; }
.reveal:nth-child(2) { transition-delay: 0.25s; }
.reveal:nth-child(3) { transition-delay: 0.4s; }
```

---

## Style Preview Checklist

- [ ] Dark `#0f0f0f` background with soft gradient orbs
- [ ] Warm accents: terracotta, pink, gold — not bright colors
- [ ] Cormorant italic for key headings
- [ ] Thin vertical accent lines
- [ ] Abstract shapes only — no illustrations
- [ ] No pure black background — using `#0f0f0f`

---

## Best For

Premium brand presentations · Art & design portfolios · Luxury product showcases · Contemplative topics · High-end B2B pitches
