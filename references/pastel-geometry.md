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

## Named Layout Variations

### 1. Pastel Hero (全屏宣告)

Pastel blue background `#c8d9e6`. Centered white `.pastel-card` with soft shadow `0 8px 32px rgba(0,0,0,0.08)`, `border-radius: 16px`. Headline in Plus Jakarta Sans 800, `clamp(28px, 5vw, 48px)`. Vertical pills on right edge (`.pastel-pill` short/medium/tall in pink/mint/lavender).

```html
<section class="slide">
    <div class="pastel-pill short pink" style="top:20%;"></div>
    <div class="pastel-pill medium mint" style="top:40%;"></div>
    <div class="pastel-pill tall lavender" style="top:55%;"></div>
    <div class="pastel-pill medium sage" style="top:75%;"></div>
    <div class="pastel-card" style="max-width:800px;margin:0 auto;">
        <h1 class="pastel-title">Title</h1>
        <p class="pastel-body">Subtitle</p>
    </div>
</section>
```

### 2. Pastel Split (分栏证据)

Two columns inside `.pastel-card`. Left: section label + headline. Right: numbered list or evidence. Pills on right edge outside the card. Clean white card on pastel background.

### 3. Pastel Grid (网格检查点/推荐网格)

2×2 or 2×3 grid of `.pastel-card` sub-cards inside the main card. Each sub-card: `.pastel-label` + item name + descriptor. Pills on right edge. Soft, approachable grid feel.

### 4. Pastel Stat (大数字强调)

Large number in Plus Jakarta Sans 800, `clamp(3rem, 8vw, 6rem)`, `letter-spacing: -0.02em`. Label above in `.pastel-label`. Card below with 2-3 line supporting text. Pills on right edge frame the content.

---

## Signature Elements

### CSS Overlays
- No body-level overlays. Clean pastel blue canvas.
- `.geo-accent`: Floating decorative circles (absolute position, `border-radius: 50%`, `opacity: 0.08`) — placed per-slide as background decoration

### Animations
- `.reveal`: Bouncy scale + translate (`translateY(16px) scale(0.97)` to `0`) —
  ```css
  .reveal { opacity: 0; transform: translateY(16px) scale(0.97);
    transition: opacity 0.4s cubic-bezier(0.34, 1.56, 0.64, 1),
                transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1); }
  .slide.visible .reveal { opacity: 1; transform: translateY(0) scale(1); }
  ```
- Stagger delays: 0.05s, 0.12s, 0.2s, 0.3s, 0.4s, 0.5s (up to 6 elements)

### Required CSS Classes
- `.card`: White card (`#faf9f7`) with `border-radius: 20px`, soft shadow (`0 4px 32px rgba(100,120,140,0.18)`), `width: clamp(320px, 88vw, 1000px)`, `height: clamp(500px, 84vh, 780px)`
- `.pills`: Vertical pill container on right edge, `position: absolute; right: 20px`, centered vertically, flex-column with `gap: 6px`
- `.pill`: Individual pill (`width: 12px`, `border-radius: 6px`), heights vary: 40px, 80px, 120px, 80px, 60px, 40px (short-tall-short rhythm)
- `.card-content`: Content area with `padding-right: clamp(56px, 6vw, 80px)` (offset for pills), `z-index: 10`
- `.divider`: 40px wide, 4px tall colored accent bar (`border-radius: 2px`)

### Background Rule
`body` sets `background: #c8d9e6` (pastel blue). Card has solid white background that covers the center. No gradient bleed-through.

### Style-Specific Rules
- **Pill color sequence** (nth-child): pink (#f0b4d4), mint (#a8d4c4), sage (#8fad9a), lavender (#9b8dc4), sky (#7bb8d4), peach (#f0c4a0)
- **Geo accents**: Positioned absolutely per-slide, 5 pastel colors, low opacity circles
- **Progress bar**: Gradient pink to mint to lavender
- **Nav dots**: Bottom-centered, 8px circles, active stretches to 28px width
- **Preset tags**: Hover `scale(1.05)` with bouncy cubic-bezier
- **Code blocks**: Dark background (`#1a2530`) with mint text (`#a8d4c4`), contrasting with pastel theme

### Signature Checklist
- [ ] Pastel blue background `#c8d9e6`
- [ ] White card with soft shadow, `border-radius: 20px`
- [ ] Vertical pills on right edge with varying heights (short-tall-short rhythm)
- [ ] At least 3 pill colors visible
- [ ] Plus Jakarta Sans at 800 weight for headlines
- [ ] Geometric accent circles (low opacity, per-slide)
- [ ] Bouncy animation (`cubic-bezier(0.34, 1.56, 0.64, 1)`)

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
