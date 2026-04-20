# Base CSS Reference

Read this file during Phase 3 generation for all non-Blue-Sky styles.
Contains: required viewport CSS, content density limits, and CSS gotchas.

---

## ⚠ Viewport Fitting (Non-Negotiable)

Every slide must equal exactly one viewport height. No scrolling within slides, ever.

### Required Base CSS (Include in ALL Presentations)

```css
/* ===========================================
   VIEWPORT FITTING: MANDATORY
   =========================================== */

html {
    height: 100%;
    overflow-x: hidden;
    scroll-snap-type: y mandatory;
    /* scroll-behavior intentionally omitted — JS scrollIntoView({behavior:'smooth'}) handles animation;
       CSS scroll-behavior + JS smooth scroll = double animation = jitter */
}

/* Each slide = exact viewport height */
.slide {
    width: 100vw;
    height: 100vh;
    height: 100dvh; /* Dynamic viewport for mobile */
    overflow: hidden; /* CRITICAL: No overflow ever */
    scroll-snap-align: start;
    display: flex;
    flex-direction: column;
    position: relative;
}

.slide-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    max-height: 100%;
    overflow: hidden;
    padding: var(--slide-padding);
}

/* ALL sizes use clamp() - scales with viewport */
:root {
    --title-size: clamp(1.5rem, 5vw, 4rem);
    --h2-size: clamp(1.25rem, 3.5vw, 2.5rem);
    --body-size: clamp(0.75rem, 1.5vw, 1.125rem);
    --small-size: clamp(0.65rem, 1vw, 0.875rem);
    --slide-padding: clamp(1rem, 4vw, 4rem);
    --content-gap: clamp(0.5rem, 2vw, 2rem);
}

.card, .container {
    max-width: min(90vw, 1000px);
    max-height: min(80vh, 700px);
}

img {
    max-width: 100%;
    max-height: min(50vh, 400px);
    object-fit: contain;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr));
    gap: clamp(0.5rem, 1.5vw, 1rem);
}

/* Responsive breakpoints - height-based */
@media (max-height: 700px) {
    :root {
        --slide-padding: clamp(0.75rem, 3vw, 2rem);
        --content-gap: clamp(0.4rem, 1.5vw, 1rem);
        --title-size: clamp(1.25rem, 4.5vw, 2.5rem);
    }
}

@media (max-height: 600px) {
    :root {
        --slide-padding: clamp(0.5rem, 2.5vw, 1.5rem);
        --title-size: clamp(1.1rem, 4vw, 2rem);
        --body-size: clamp(0.7rem, 1.2vw, 0.95rem);
    }
    .nav-dots, .keyboard-hint, .decorative { display: none; }
}

@media (max-height: 500px) {
    :root {
        --slide-padding: clamp(0.4rem, 2vw, 1rem);
        --title-size: clamp(1rem, 3.5vw, 1.5rem);
        --body-size: clamp(0.65rem, 1vw, 0.85rem);
    }
}

@media (max-width: 600px) {
    .grid { grid-template-columns: 1fr; }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.2s !important;
    }
}
```

### Content Density Limits

| Slide Type | Maximum |
|------------|---------|
| Title slide | 1 heading + 1 subtitle |
| Content slide | 1 heading + 4-6 bullets |
| Feature grid | 1 heading + 6 cards max (2×3 or 3×2) |
| Code slide | 1 heading + 8-10 lines |
| Quote slide | 1 quote (3 lines max) + attribution |
| Image slide | 1 heading + 1 image (max 60vh height) |

When in doubt → split the slide.

---

## DO NOT USE (Generic AI Patterns)

**Fonts:** Inter, Roboto, Arial, system fonts as display typeface

**Colors:** `#6366f1` (generic indigo), purple gradients on white

**Layouts:** Everything centered, generic hero sections, identical card grids

**Decorations:** Realistic illustrations, gratuitous glassmorphism, drop shadows without purpose

---

## CSS Gotchas

### Negating CSS Functions

**WRONG — silently ignored by browsers:**
```css
right: -clamp(28px, 3.5vw, 44px);   /* ❌ Invalid! */
margin-left: -min(10vw, 100px);      /* ❌ Invalid! */
```

**CORRECT — wrap in `calc()`:**
```css
right: calc(-1 * clamp(28px, 3.5vw, 44px));  /* ✅ */
margin-left: calc(-1 * min(10vw, 100px));     /* ✅ */
```

CSS does not allow a leading `-` before `clamp()`, `min()`, `max()`. The browser silently discards the declaration with no console error — the element simply appears in the wrong position.

### Content Overflow

1. Check slide has `overflow: hidden`
2. Reduce content — split into multiple slides
3. Ensure all fonts use `clamp()` not fixed `px`/`rem`
4. Check images have `max-height: min(50vh, 400px)`

### Viewport Checklist

- [ ] Every `.slide` has `height: 100vh; height: 100dvh; overflow: hidden;`
- [ ] All font sizes use `clamp(min, preferred, max)`
- [ ] No negated CSS functions (use `calc(-1 * clamp(...))`)
- [ ] Breakpoints at 700px, 600px, 500px heights
- [ ] Images have `max-height` constraints
- [ ] Content respects density limits

---

## Universal UI Elements (Mandatory for ALL Styles)

These elements MUST appear in every generated HTML, regardless of whether the style file explicitly defines them. Style files may override colors/positions but cannot omit them.

### Brand Mark

Fixed identifier in top-left corner. Always visible (z-index: 1000).

```css
#brand-mark {
    position: fixed;
    top: 20px;
    left: 28px;
    font-weight: 800;
    font-size: 15px;
    z-index: 1000;
    /* color and font-family from style file's accent color and display font */
}
```

```html
<span id="brand-mark">slide-creator</span>
```

### Slide Number Label

Page indicator, bottom-right of each slide. Two variants for light/dark backgrounds.

```css
.slide-num-label {
    position: absolute;
    bottom: 28px;
    right: 36px;
    font-size: 11px;
    font-weight: 500;
    color: rgba(0,0,0,0.18);
}
.slide-num-label.light { color: rgba(255,255,255,0.2); }
```

### Navigation Dots

Right-side dot navigation. Active dot scaled up.

```css
.nav-dots {
    position: fixed; right: 1.5rem; top: 50%; transform: translateY(-50%);
    display: flex; flex-direction: column; gap: 8px; z-index: 100;
}
.nav-dots button {
    width: 8px; height: 8px; border-radius: 50%; border: none; cursor: pointer;
    transition: all 0.3s;
}
```

### Progress Bar

Top-edge progress indicator. Color from style accent.

```css
.progress-bar {
    position: fixed; top: 0; left: 0; height: 3px;
    background: var(--accent); width: 0%; z-index: 100; transition: width 0.3s ease;
}
```

### Per-Slide CSS Pattern

Each slide MUST have `id="slide-N"` (1-indexed). Layout direction, panel backgrounds, and slide-specific overrides go in `<style>` via `#slide-N` selectors — never inline.

```css
/* Per-slide layout */
#slide-1 { flex-direction: row; }
#slide-1 .left-panel { background: #fff; }
#slide-1 .slide-num-label { color: rgba(255,255,255,0.12); }

#slide-2 { flex-direction: column; }
#slide-2 .top-panel { background: #fff; }
```

```html
<section class="slide" id="slide-1" data-notes="...">
    <div class="left-panel">...</div>
    <div class="right-panel">...</div>
</section>
```
