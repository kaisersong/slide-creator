# Notebook Tabs — Style Reference

Editorial, organized, elegant, tactile. Cream paper with colorful section tabs.

---

## Colors

```css
:root {
    --bg-outer: #2d2d2d;
    --bg-page: #f8f6f1;
    --text-primary: #1a1a1a;
    --text-secondary: #666666;
    --tab-1: #98d4bb; /* Mint */
    --tab-2: #c7b8ea; /* Lavender */
    --tab-3: #f4b8c5; /* Pink */
    --tab-4: #a8d8ea; /* Sky */
    --tab-5: #ffe6a7; /* Cream */
}
```

---

## Background

```css
body {
    background: var(--bg-outer);
    font-family: "Bodoni Moda", "DM Sans", -apple-system, sans-serif;
}

/* Paper container with subtle shadow */
.notebook-page {
    background: var(--bg-page);
    border-radius: 4px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    max-width: min(90vw, 900px);
    margin: 0 auto;
}
```

---

## Typography

```css
@import url('https://fonts.googleapis.com/css2?family=Bodoni+Moda:wght@400;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500&display=swap');

.notebook-title {
    font-family: "Bodoni Moda", Georgia, serif;
    font-size: clamp(28px, 5vw, 52px);
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.1;
}

.notebook-body {
    font-family: "DM Sans", sans-serif;
    font-size: clamp(13px, 1.4vw, 16px);
    font-weight: 400;
    color: var(--text-primary);
    opacity: 0.75;
    line-height: 1.65;
}

.notebook-label {
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-secondary);
}
```

---

## Components

```css
/* Colorful tab on right edge — vertical text */
.notebook-tab {
    position: absolute;
    right: 0;
    width: clamp(28px, 3.5vw, 36px);
    padding: clamp(8px, 1.5vw, 12px) 4px;
    font-size: clamp(8px, 1vh, 11px);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    writing-mode: vertical-rl;
    text-orientation: mixed;
    border-radius: 4px 0 0 4px;
    color: var(--text-primary);
}
.notebook-tab.tab-1 { background: var(--tab-1); }
.notebook-tab.tab-2 { background: var(--tab-2); }
.notebook-tab.tab-3 { background: var(--tab-3); }
.notebook-tab.tab-4 { background: var(--tab-4); }
.notebook-tab.tab-5 { background: var(--tab-5); }

/* Binder hole decoration */
.notebook-hole {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--bg-outer);
    opacity: 0.3;
}
```

---

## Named Layout Variations

### 1. Notebook Hero (全屏宣告)

Cream paper `#f8f6f1` on dark outer `#2d2d2d`. `.notebook-page` container with shadow. Headline in Bodoni Moda 700, `clamp(28px, 5vw, 52px)`. Colorful `.notebook-tab` on right edge (vertical text). Optional binder holes on left.

```html
<section class="slide">
    <div class="notebook-page">
        <div class="notebook-tab tab-1">INTRO</div>
        <div class="slide-content" style="padding:2rem;">
            <h1 class="notebook-title">Title</h1>
            <p class="notebook-body">Subtitle</p>
        </div>
    </div>
</section>
```

### 2. Notebook Split (分屏对比)

Two columns inside `.notebook-page`. Left: headline + body. Right: evidence list or data. Colorful tab on right edge changes per section. Binder holes on left edge visible against dark outer background.

### 3. Notebook Cards (双列功能卡/网格检查点)

2 `.notebook-body` sections inside `.notebook-page`, separated by thin rule. Each section: `.notebook-label` + title + body. Tab color changes to indicate active section. Clean, organized feel.

### 4. Notebook CTA (堆叠行动)

Single column inside `.notebook-page`. Numbered steps as list items. `.notebook-cta` button at bottom. Multiple tabs visible on right edge showing progression. Clean editorial close.

---

## Signature Elements

### CSS Overlays
- `.paper::after`: Ruled line pattern (28px spacing, 27px transparent + 1px `rgba(0,0,0,0.05)`) —
  ```css
  .paper::after { content: ''; position: absolute; inset: 0; pointer-events: none; z-index: 1;
    background-image: repeating-linear-gradient(to bottom, transparent, transparent 27px,
      rgba(0,0,0,0.05) 27px, rgba(0,0,0,0.05) 28px);
    background-position: 0 56px; border-radius: 8px; }
  ```

### Animations
- `.reveal`: Horizontal slide-in (`translateX(-14px)` to `0`, 0.3s ease) —
  ```css
  .reveal { opacity: 0; transform: translateX(-14px); transition: opacity 0.3s ease, transform 0.3s ease; }
  .slide.visible .reveal { opacity: 1; transform: translateX(0); }
  ```

### Required CSS Classes
- `.paper`: Cream card (`#f8f6f1`) with `border-radius: 8px`, heavy shadow (`0 8px 48px rgba(0,0,0,0.5)`), `width: 90vw; max-width: 1100px`
- `.tabs`: Container for right-edge tabs, `position: absolute; right: -52px`, full height
- `.tab`: Individual tab with `writing-mode: vertical-rl`, `text-orientation: mixed`, color variants via `data-color` attribute
- `.tab.active`: Wider (64px), full opacity, `box-shadow: 2px 0 8px rgba(0,0,0,0.15)`
- `.binder-holes`: Left-edge hole container, `position: absolute; left: -16px`, `justify-content: space-evenly`
- `.hole`: 12px circle, `background: #2d2d2d` (matches outer), `box-shadow: inset 0 1px 3px rgba(0,0,0,0.5)`
- `.paper-content`: Content area with `padding-left: 56px` (offset for binder holes), `z-index: 2`

### Allowed Components
- Audit coverage: .notebook-body .notebook-hole .notebook-label .notebook-page .notebook-tab .notebook-title .tab-1 .tab-2
- Audit coverage cont.: .tab-3 .tab-4 .tab-5

### Background Rule
`body` sets `background: #2d2d2d` (dark outer). `.paper` card has cream background that fully covers the slide center. No gradient bleed-through.

### Style-Specific Rules
- **Tab colors** via `data-color` attribute: `mint` (#98d4bb), `lavender` (#c7b8ea), `pink` (#f4b8c5), `sky` (#a8d8ea), `cream` (#ffe6a7), `peach` (#f4c4a4), `sage` (#b4d4b4), `coral` (#f4b4a4)
- **Active tab sync**: JS `.updateNav(idx)` toggles `.active` class on tabs matching current slide index
- **Tab click navigation**: Each tab's `data-index` maps to slide number
- **Progress bar**: Gradient from mint to lavender to pink
- **Typography duality**: Bodoni Moda serif for headlines, DM Sans for body

### Signature Checklist
- [ ] Cream paper `#f8f6f1` on dark outer `#2d2d2d`
- [ ] Ruled line overlay on paper (`.paper::after`)
- [ ] Colorful tabs on right edge (vertical text, at least 2 visible)
- [ ] Active tab wider (64px) with shadow
- [ ] Binder holes on left edge (3 circles, dark fill)
- [ ] Bodoni Moda serif for headlines
- [ ] Tab color changes per section/slide

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

- [ ] Cream paper `#f8f6f1` on dark outer `#2d2d2d`
- [ ] Colorful tabs on right edge (vertical text)
- [ ] Bodoni Moda serif font for headlines
- [ ] At least 2 tab colors visible
- [ ] No pure black background — using `#2d2d2d` outer

---

## Best For

Reports · Reviews · Editorial presentations · Organized content · Academic decks · Structured narratives
