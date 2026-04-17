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

## Named Layout Variations

### 1. Split Hero (全屏宣告)

Peach `#f5e6dc` left panel, lavender `#e4dff0` right panel. Grid pattern overlay on right (`.split-pastel-grid`). Headline in Outfit 800, `clamp(28px, 5vw, 48px)`, spans both panels. `.split-badge` (mint/yellow/pink) as accent.

```html
<section class="slide" style="padding:0;position:relative;">
    <div class="split-pastel-left" style="position:absolute;left:0;top:0;bottom:0;width:50%;"></div>
    <div class="split-pastel-right" style="position:absolute;right:0;top:0;bottom:0;width:50%;">
        <div class="split-pastel-grid"></div>
    </div>
    <div class="slide-content" style="position:relative;z-index:1;">
        <h1 class="split-title">Title</h1>
        <span class="split-badge mint">Badge</span>
    </div>
</section>
```

### 2. Split Evidence (分栏证据)

Full split layout. Left panel: `.split-label` + headline in Outfit 800. Right panel (with grid overlay): bullet list or evidence. Badge pill at top of right panel. Color boundary creates natural divider.

### 3. Split Cards (多选项对比/双列功能卡)

2-3 cards on split background. Each card: white/light background, `border-radius: 12px`, subtle shadow. Active card has mint badge. `.split-badge` pills scattered as accents. Grid visible behind cards on right side.

### 4. Split CTA (堆叠行动)

Single column centered over split. Numbered command blocks with rounded corners. `.split-cta` buttons (pill-shaped, dark bg, light text). Badge pills at top. Grid overlay on right panel visible behind content.

---

## Signature Elements

### CSS Overlays
- `.slide::before`: Two-color vertical split gradient —
  ```css
  .slide::before { content: ''; position: absolute; inset: 0;
    background: linear-gradient(to right, #f5e6dc 50%, #e4dff0 50%); z-index: 0; }
  ```
- `.slide::after`: Dot pattern on right half only (radial gradient dots, 24px grid) —
  ```css
  .slide::after { content: ''; position: absolute; top: 0; right: 0;
    width: 50%; height: 100%; z-index: 1; pointer-events: none;
    background-image: radial-gradient(circle, rgba(100,80,160,0.12) 1.5px, transparent 1.5px);
    background-size: 24px 24px; }
  ```

### Animations
- `.slide-content`: Scale + translate entrance (`translateY(40px) scale(0.97)` to `0`, 0.5s cubic-bezier) —
  ```css
  .slide-content { opacity: 0; transform: translateY(40px) scale(0.97);
    transition: opacity 0.5s cubic-bezier(0.34,1.2,0.64,1),
                transform 0.5s cubic-bezier(0.34,1.2,0.64,1); }
  .slide.visible .slide-content { opacity: 1; transform: translateY(0) scale(1); }
  ```
- `.card`: Staggered card entrance (4 cards, 0.05s/0.12s/0.19s/0.26s delays)
- `.step`: Staggered step entrance from left (3 steps, 0.1s/0.2s/0.3s delays)

### Required CSS Classes
- `.slide-content`: Centered content wrapper, `width: min(780px, 90vw)`, `z-index: 2`, text-align center
- `.badge` / `.badge-mint` / `.badge-yellow` / `.badge-pink` / `.badge-lavender` / `.badge-peach`: Rounded pill (`border-radius: 100px`) with colored background and dark text
- `.stat-pill`: White rounded card (`border-radius: 100px`), `box-shadow: 0 4px 16px rgba(0,0,0,0.08)`, centered stat number + label
- `.card`: White rounded card (`border-radius: 24px`), soft shadow, per-card entrance animation
- `.grid-item`: White rounded card (`border-radius: 16px`), small shadow, for preset grid items
- `.step`: White rounded card (`border-radius: 20px`) with colored circular step number
- `.step-num-N`: Colored circle backgrounds (mint, lavender, pink) with dark text
- `.slide-num`: White pill-shaped badge, `position: absolute; top: 24px; right: 24px`
- `.cta-btn` / `.cta-primary` / `.cta-secondary`: Rounded pill buttons, primary = dark bg, secondary = lavender bg

### Background Rule
No body background set. `.slide::before` creates the peach/lavender split gradient. `.slide::after` dots overlay only the right 50%. Content sits at `z-index: 2` above both.

### Style-Specific Rules
- **Split is always 50/50 vertical**: peach (`#f5e6dc`) left, lavender (`#e4dff0`) right
- **Dot pattern only on right half**: `width: 50%; right: 0` on `::after`
- **Badge pills use semantic colors**: mint (#c8f0d8), yellow (#f0f0c8), pink (#f0d4e0), lavender (#d4cef5), peach (#f5d4c4) — each with matching dark text color
- **Progress bar**: Gradient mint to lavender
- **Nav dots**: Bottom-centered, pill-shaped (8px circles, active stretches to 24px)
- **Install cards**: White background, `border-radius: 20px`, code blocks in dark (`#1a1a1a`) with mint text

### Signature Checklist
- [ ] Peach `#f5e6dc` left / lavender `#e4dff0` right split
- [ ] Dot pattern overlay on right half only
- [ ] Badge pills (mint/yellow/pink/lavender/peach) visible
- [ ] Rounded white cards with soft shadows
- [ ] Outfit at 800 weight for headlines
- [ ] Centered content layout (min 780px, 90vw)
- [ ] Pill-shaped CTA buttons

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
