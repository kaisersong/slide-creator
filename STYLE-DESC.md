# Style Presets Reference

Curated visual styles for Slide Creator. Each preset is inspired by real design references—no generic "AI slop" aesthetics. **Abstract shapes only—no illustrations.**

---

## ⚠️ CRITICAL: Viewport Fitting (Non-Negotiable)

**Every slide MUST fit exactly in the viewport. No scrolling within slides, ever.**

### Content Density Limits Per Slide

| Slide Type | Maximum Content |
|------------|-----------------|
| Title slide | 1 heading + 1 subtitle |
| Content slide | 1 heading + 4-6 bullets (max 2 lines each) |
| Feature grid | 1 heading + 6 cards (2x3 or 3x2) |
| Code slide | 1 heading + 8-10 lines of code |
| Quote slide | 1 quote (max 3 lines) + attribution |

**Too much content? → Split into multiple slides. Never scroll.**

### Required Base CSS (Include in ALL Presentations)

```css
/* ===========================================
   VIEWPORT FITTING: MANDATORY
   Copy this entire block into every presentation
   =========================================== */

/* 1. Lock document to viewport */
html, body {
    height: 100%;
    overflow-x: hidden;
}

html {
    scroll-snap-type: y mandatory;
    scroll-behavior: smooth;
}

/* 2. Each slide = exact viewport height */
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

/* 3. Content wrapper */
.slide-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    max-height: 100%;
    overflow: hidden;
    padding: var(--slide-padding);
}

/* 4. ALL sizes use clamp() - scales with viewport */
:root {
    /* Typography */
    --title-size: clamp(1.5rem, 5vw, 4rem);
    --h2-size: clamp(1.25rem, 3.5vw, 2.5rem);
    --body-size: clamp(0.75rem, 1.5vw, 1.125rem);
    --small-size: clamp(0.65rem, 1vw, 0.875rem);

    /* Spacing */
    --slide-padding: clamp(1rem, 4vw, 4rem);
    --content-gap: clamp(0.5rem, 2vw, 2rem);
}

/* 5. Cards/containers use viewport-relative max sizes */
.card, .container {
    max-width: min(90vw, 1000px);
    max-height: min(80vh, 700px);
}

/* 6. Images constrained */
img {
    max-width: 100%;
    max-height: min(50vh, 400px);
    object-fit: contain;
}

/* 7. Grids adapt to space */
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr));
    gap: clamp(0.5rem, 1.5vw, 1rem);
}

/* ===========================================
   RESPONSIVE BREAKPOINTS - Height-based
   =========================================== */

/* Short screens (< 700px height) */
@media (max-height: 700px) {
    :root {
        --slide-padding: clamp(0.75rem, 3vw, 2rem);
        --content-gap: clamp(0.4rem, 1.5vw, 1rem);
        --title-size: clamp(1.25rem, 4.5vw, 2.5rem);
    }
}

/* Very short (< 600px height) */
@media (max-height: 600px) {
    :root {
        --slide-padding: clamp(0.5rem, 2.5vw, 1.5rem);
        --title-size: clamp(1.1rem, 4vw, 2rem);
        --body-size: clamp(0.7rem, 1.2vw, 0.95rem);
    }

    .nav-dots, .keyboard-hint, .decorative {
        display: none;
    }
}

/* Extremely short - landscape phones (< 500px) */
@media (max-height: 500px) {
    :root {
        --slide-padding: clamp(0.4rem, 2vw, 1rem);
        --title-size: clamp(1rem, 3.5vw, 1.5rem);
        --body-size: clamp(0.65rem, 1vw, 0.85rem);
    }
}

/* Narrow screens */
@media (max-width: 600px) {
    .grid {
        grid-template-columns: 1fr;
    }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.2s !important;
    }
}
```

### Viewport Fitting Checklist

Before finalizing any presentation, verify:

- [ ] Every `.slide` has `height: 100vh; height: 100dvh; overflow: hidden;`
- [ ] All font sizes use `clamp(min, preferred, max)`
- [ ] All spacing uses `clamp()` or viewport units
- [ ] Breakpoints exist for heights: 700px, 600px, 500px
- [ ] Content respects density limits (max 6 bullets, max 6 cards)
- [ ] No fixed pixel heights on content elements
- [ ] Images have `max-height` constraints
- [ ] No negated CSS functions (use `calc(-1 * clamp(...))` not `-clamp(...)`)

---

## Dark Themes

### 1. Bold Signal

**Vibe:** Confident, bold, modern, high-impact

**Layout:** Colored card on dark gradient. Number top-left, navigation top-right, title bottom-left.

**Typography:**
- Display: `Archivo Black` (900)
- Body: `Space Grotesk` (400/500)

**Colors:**
```css
:root {
    --bg-primary: #1a1a1a;
    --bg-gradient: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%);
    --card-bg: #FF5722;
    --text-primary: #ffffff;
    --text-on-card: #1a1a1a;
}
```

**Signature Elements:**
- Bold colored card as focal point (orange, coral, or vibrant accent)
- Large section numbers (01, 02, etc.)
- Navigation breadcrumbs with active/inactive opacity states
- Grid-based layout for precise alignment

---

### 2. Electric Studio

**Vibe:** Bold, clean, professional, high contrast

**Layout:** Split panel—white top, blue bottom. Brand marks in corners.

**Typography:**
- Display: `Manrope` (800)
- Body: `Manrope` (400/500)

**Colors:**
```css
:root {
    --bg-dark: #0a0a0a;
    --bg-white: #ffffff;
    --accent-blue: #4361ee;
    --text-dark: #0a0a0a;
    --text-light: #ffffff;
}
```

**Signature Elements:**
- Two-panel vertical split
- Accent bar on panel edge
- Quote typography as hero element
- Minimal, confident spacing

---

### 3. Creative Voltage

**Vibe:** Bold, creative, energetic, retro-modern

**Layout:** Split panels—electric blue left, dark right. Script accents.

**Typography:**
- Display: `Syne` (700/800)
- Mono: `Space Mono` (400/700)

**Colors:**
```css
:root {
    --bg-primary: #0066ff;
    --bg-dark: #1a1a2e;
    --accent-neon: #d4ff00;
    --text-light: #ffffff;
}
```

**Signature Elements:**
- Electric blue + neon yellow contrast
- Halftone texture patterns
- Neon badges/callouts
- Script typography for creative flair

---

### 4. Dark Botanical

**Vibe:** Elegant, sophisticated, artistic, premium

**Layout:** Centered content on dark. Abstract soft shapes in corner.

**Typography:**
- Display: `Cormorant` (400/600) — elegant serif
- Body: `IBM Plex Sans` (300/400)

**Colors:**
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

**Signature Elements:**
- Abstract soft gradient circles (blurred, overlapping)
- Warm color accents (pink, gold, terracotta)
- Thin vertical accent lines
- Italic signature typography
- **No illustrations—only abstract CSS shapes**

---

## Light Themes

### 5. Blue Sky

> **Starter template available:** When generating a Blue Sky presentation, read and use [`references/blue-sky-starter.html`](references/blue-sky-starter.html) as the base file. All visual elements are pre-built — do not reimplement them. See SKILL.md Phase 3 for instructions.

**Vibe:** Clean, airy, enterprise-ready, modern SaaS — inspired by a real enterprise AI pitch deck. Light sky-blue canvas with floating glassmorphism cards and animated ambient orbs. Feels like a high-altitude clear day: open, confident, premium.

**Layout:** Full-bleed sky gradient with 3 animated blur orbs that reposition per slide. Content in centered glassmorphism cards. Horizontal slide transitions (spring physics). Pill pagination dots at bottom. Fullscreen button top-right.

**Typography:**
- System fonts: `-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif`
- All labels: `letter-spacing: 0.2em; text-transform: uppercase; font-weight: 600`
- Headlines: Bold/Black weight
- Body: `font-weight: 300` (light)
- Gradient headline: `#1e3a8a` → `#3b82f6` (deep navy to bright blue)

**Colors:**
```css
:root {
    /* Background — sky gradient */
    --bg-from: #f0f9ff;         /* sky-50 */
    --bg-to:   #e0f2fe;         /* sky-100 */

    /* Text */
    --text-primary:   #0f172a;  /* slate-900 */
    --text-secondary: #64748b;  /* slate-500 */
    --text-accent:    #2563eb;  /* blue-600 */

    /* Glassmorphism cards */
    --card-bg:     rgba(255, 255, 255, 0.70);
    --card-border: rgba(255, 255, 255, 0.90);
    --card-shadow: 0 10px 40px -10px rgba(37, 99, 235, 0.08), 0 1px 3px rgba(0,0,0,0.02);
    --card-radius: 24px;
    --card-blur:   blur(24px);

    /* Ambient orbs */
    --orb-blue:   rgba(37,  99,  235, 0.30);  /* blue-700 */
    --orb-indigo: rgba(79,  70,  229, 0.25);  /* indigo-600 */
    --orb-sky:    rgba(56,  189, 248, 0.25);  /* sky-400 */
}
```

**CSS Implementation:**
```css
/* === BLUE SKY BASE === */
body {
    background: linear-gradient(135deg, var(--bg-from) 0%, var(--bg-to) 100%);
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* Grainy noise texture — adds tactile depth */
body::before {
    content: '';
    position: fixed;
    inset: 0;
    z-index: 1;
    pointer-events: none;
    opacity: 0.35;
    mix-blend-mode: overlay;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

/* Tech grid underlay — 40px lines, fades to edges */
.sky-grid {
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(to right, rgba(14,165,233,0.08) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(14,165,233,0.08) 1px, transparent 1px);
    background-size: 40px 40px;
    -webkit-mask-image: radial-gradient(ellipse 80% 50% at 50% 50%, #000 70%, transparent 100%);
    mask-image: radial-gradient(ellipse 80% 50% at 50% 50%, #000 70%, transparent 100%);
    pointer-events: none;
}

/* Ambient orb — placed with CSS custom props */
.sky-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    pointer-events: none;
    transition: all 1.8s cubic-bezier(0.22, 1, 0.36, 1);
}

/* Glassmorphism card */
.glass-card {
    background: var(--card-bg);
    backdrop-filter: var(--card-blur);
    -webkit-backdrop-filter: var(--card-blur);
    border: 1px solid var(--card-border);
    box-shadow: var(--card-shadow);
    border-radius: var(--card-radius);
}
.glass-card:hover {
    background: rgba(255, 255, 255, 0.85);
    box-shadow: 0 20px 60px -15px rgba(37, 99, 235, 0.12), 0 2px 6px rgba(0,0,0,0.03);
    transform: translateY(-2px);
    transition: all 0.3s ease;
}

/* Section label (small caps above headline) */
.sky-label {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: clamp(0.65rem, 1vw, 0.75rem);
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-accent);
}
.sky-label::before {
    content: '';
    width: 8px; height: 8px;
    background: #3b82f6;
    border-radius: 50%;
}

/* Gradient headline */
.sky-title-gradient {
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Pill badge (top of hero slide) */
.sky-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 20px;
    border-radius: 9999px;
    background: rgba(255,255,255,0.8);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(147,197,253,0.5);
    font-size: clamp(0.65rem, 1vw, 0.75rem);
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #2563eb;
    box-shadow: 0 2px 8px rgba(37,99,235,0.08);
}
.sky-badge::before {
    content: '';
    width: 8px; height: 8px;
    background: #3b82f6;
    border-radius: 50%;
}

/* Animated connection lines (SVG, use in decorative layer) */
/* Example: <path stroke="url(#sky-line)" stroke-dasharray="10 15"
              style="animation: dash-flow 4s linear infinite" /> */
@keyframes dash-flow {
    from { stroke-dashoffset: 0; }
    to   { stroke-dashoffset: 100; }
}

/* ─── Horizontal slide transition — CORRECT layout pattern ───
 *
 * CRITICAL: The three values must be consistent or the layout breaks.
 *
 *   #stage  : overflow: hidden wrapper, fixed to viewport
 *   #track  : width = 100vw × N  (NOT 100% × N — percentages resolve differently)
 *   .slide  : width = 100vw      (NOT 100vw / N — each slide is one full viewport)
 *   JS      : translateX(-i × 100vw)   where i = 0-based slide index
 *
 * Common mistake: writing `width: calc(100vw / N)` for .slide — this makes each
 * slide 1/N of the viewport and completely collapses the layout.
 */
#stage {
    position: fixed;
    inset: 0;
    overflow: hidden;
    z-index: 1;
}
.slides-track {
    display: flex;
    flex-direction: row;
    width: calc(100vw * var(--slide-count)); /* e.g. 32 slides → 3200vw */
    height: 100%;
    transition: transform 0.7s cubic-bezier(0.22, 1, 0.36, 1); /* spring feel */
}
.slide {
    width: 100vw;          /* each slide = one full viewport, always */
    flex-shrink: 0;
    height: 100vh;
}

/* JS navigation — use vw units, not percentages */
/* track.style.transform = `translateX(-${currentIndex * 100}vw)`; */

/* Pill pagination dots */
.sky-nav {
    position: fixed;
    bottom: clamp(1rem, 2vw, 2rem);
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 12px;
    z-index: 50;
}
.sky-dot {
    height: 6px;
    border-radius: 9999px;
    background: rgba(147,197,253,0.5);
    transition: all 0.5s ease;
    width: 6px;
    cursor: pointer;
    border: none;
}
.sky-dot.active {
    background: #2563eb;
    width: 32px;
}

/* Scrollbar for content-heavy slides */
.sky-scroll {
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: rgba(147,197,253,0.5) transparent;
}
.sky-scroll::-webkit-scrollbar { width: 6px; }
.sky-scroll::-webkit-scrollbar-track { background: transparent; }
.sky-scroll::-webkit-scrollbar-thumb {
    background: rgba(147,197,253,0.5);
    border-radius: 10px;
}
```

**Signature Elements:**

1. **Animated ambient orbs** — 3 blurred radial-gradient circles (blue/indigo/sky). They reposition smoothly between slides to match content mood. Typical orb size 40–60% viewport width, `blur(80px)`, `mix-blend-mode` not needed on light bg. Animate `top`/`left`/`transform: scale()` with CSS transitions or JS.

2. **Glassmorphism cards** (`glass-card`) — `rgba(255,255,255,0.7)` + `backdrop-filter: blur(24px)`. Every content block lives in one. Use `border-radius: 24px`, white border, and subtle blue-tinted shadow.

3. **Grainy noise texture** — SVG `feTurbulence` overlay (fixed, `mix-blend-mode: overlay`, opacity ~0.35). Adds premium tactile depth without photos or illustrations.

4. **Tech grid underlay** — 40px CSS grid lines at 8% opacity, masked with radial gradient so it fades to edges. Evokes a clean data visualization canvas.

5. **Section label + headline pairing** — Always pair: small-caps blue label above → bold dark headline below. Gap ~8px. Label must have the dot prefix.

6. **Gradient headline text** — Key hero titles use `sky-title-gradient`: deep navy `#1e3a8a` → bright blue `#3b82f6`.

7. **Spring-physics slide transitions** — Horizontal track, `cubic-bezier(0.22, 1, 0.36, 1)` easing. Feels like a physical carousel, not a CSS fade. **Use the correct layout pattern in the CSS block above**: `#stage` fixed wrapper → `#track` at `100vw × N` → `.slide` at `100vw` → JS `translateX(-i * 100vw)`. Never use `calc(100vw / N)` for slide width.

8. **Pill badge** (hero slides only) — Small white pill above the main title announcing the theme/category.

9. **Flowing SVG connection lines** (optional, decorative layer) — Animated `stroke-dashoffset` paths over gradient `linearGradient` stroke, opacity 0.3. Creates a sense of data flow without heavy graphics.

10. **Cloud hero effect** (title slide only) — CSS blur-circle clusters anchored to `bottom: 0`, animated with `translateX` (two-layer loop: slow back layer + fast front layer). Use SVG `feTurbulence/feDisplacementMap` filter for organic edges. Creates an "above the clouds" launch moment.

**Orb Positioning Guide (per slide type):**
```
Hero/Title:      orb1 center-bottom(large), orb2 left-low, orb3 right-mid
Data/Split:      orb1 far-left-mid, orb2 far-right-mid, orb3 top-center(small)
Architecture:    orb1 top-center, orb2 bottom-left, orb3 bottom-right (triangle)
Grid/Cards:      orb1 top-left(large), orb2 bottom-right(large), orb3 center(mid)
Stats/Numbers:   orb1 center(very large), orb2 top-left(small), orb3 bottom-right(small)
Timeline:        orb1 left-mid, orb2 center-mid, orb3 right-mid (horizontal row)
```

**Animation Timings:**
- Slide entry: `0.8s ease [0.22, 1, 0.36, 1]`, stagger children by `0.15s`
- Orb transitions: `1.8s cubic-bezier(0.22, 1, 0.36, 1)`
- Hover effects: `0.3s ease`
- Floating orbs (continuous): `20–28s easeInOut infinite`
- Connection lines: `4–6s linear infinite`
- Cloud layers: back `30s linear infinite`, front `18s linear infinite`

---

### 6. Notebook Tabs

**Vibe:** Editorial, organized, elegant, tactile

**Layout:** Cream paper card on dark background. Colorful tabs on right edge.

**Typography:**
- Display: `Bodoni Moda` (400/700) — classic editorial
- Body: `DM Sans` (400/500)

**Colors:**
```css
:root {
    --bg-outer: #2d2d2d;
    --bg-page: #f8f6f1;
    --text-primary: #1a1a1a;
    --tab-1: #98d4bb; /* Mint */
    --tab-2: #c7b8ea; /* Lavender */
    --tab-3: #f4b8c5; /* Pink */
    --tab-4: #a8d8ea; /* Sky */
    --tab-5: #ffe6a7; /* Cream */
}
```

**Signature Elements:**
- Paper container with subtle shadow
- Colorful section tabs on right edge (vertical text)
- Binder hole decorations on left
- Tab text must scale with viewport: `font-size: clamp(0.5rem, 1vh, 0.7rem)`

---

### 7. Pastel Geometry

**Vibe:** Friendly, organized, modern, approachable

**Layout:** White card on pastel background. Vertical pills on right edge.

**Typography:**
- Display: `Plus Jakarta Sans` (700/800)
- Body: `Plus Jakarta Sans` (400/500)

**Colors:**
```css
:root {
    --bg-primary: #c8d9e6;
    --card-bg: #faf9f7;
    --pill-pink: #f0b4d4;
    --pill-mint: #a8d4c4;
    --pill-sage: #5a7c6a;
    --pill-lavender: #9b8dc4;
    --pill-violet: #7c6aad;
}
```

**Signature Elements:**
- Rounded card with soft shadow
- **Vertical pills on right edge** with varying heights (like tabs)
- Consistent pill width, heights: short → medium → tall → medium → short
- Download/action icon in corner

---

### 8. Split Pastel

**Vibe:** Playful, modern, friendly, creative

**Layout:** Two-color vertical split (peach left, lavender right).

**Typography:**
- Display: `Outfit` (700/800)
- Body: `Outfit` (400/500)

**Colors:**
```css
:root {
    --bg-peach: #f5e6dc;
    --bg-lavender: #e4dff0;
    --text-dark: #1a1a1a;
    --badge-mint: #c8f0d8;
    --badge-yellow: #f0f0c8;
    --badge-pink: #f0d4e0;
}
```

**Signature Elements:**
- Split background colors
- Playful badge pills with icons
- Grid pattern overlay on right panel
- Rounded CTA buttons

---

### 9. Vintage Editorial

**Vibe:** Witty, confident, editorial, personality-driven

**Layout:** Centered content on cream. Abstract geometric shapes as accent.

**Typography:**
- Display: `Fraunces` (700/900) — distinctive serif
- Body: `Work Sans` (400/500)

**Colors:**
```css
:root {
    --bg-cream: #f5f3ee;
    --text-primary: #1a1a1a;
    --text-secondary: #555;
    --accent-warm: #e8d4c0;
}
```

**Signature Elements:**
- Abstract geometric shapes (circle outline + line + dot)
- Bold bordered CTA boxes
- Witty, conversational copy style
- **No illustrations—only geometric CSS shapes**

---

## Specialty Themes

### 10. Neon Cyber

**Vibe:** Futuristic, techy, confident

**Typography:** `Clash Display` + `Satoshi` (Fontshare)

**Colors:** Deep navy (#0a0f1c), cyan accent (#00ffcc), magenta (#ff00aa)

**Signature:** Particle backgrounds, neon glow, grid patterns

---

### 11. Terminal Green

**Vibe:** Developer-focused, hacker aesthetic

**Typography:** `JetBrains Mono` (monospace only)

**Colors:** GitHub dark (#0d1117), terminal green (#39d353)

**Signature:** Scan lines, blinking cursor, code syntax styling

---

### 12. Swiss Modern

**Vibe:** Clean, precise, Bauhaus-inspired

**Typography:** `Archivo` (800) + `Nunito` (400)

**Colors:** Pure white, pure black, red accent (#ff3300)

**Signature:** Visible grid, asymmetric layouts, geometric shapes

---

### 13. Paper & Ink

**Vibe:** Editorial, literary, thoughtful

**Typography:** `Cormorant Garamond` + `Source Serif 4`

**Colors:** Warm cream (#faf9f7), charcoal (#1a1a1a), crimson accent (#c41e3a)

**Signature:** Drop caps, pull quotes, elegant horizontal rules

---

## Font Pairing Quick Reference

| Preset | Display Font | Body Font | Source |
|--------|--------------|-----------|--------|
| Bold Signal | Archivo Black | Space Grotesk | Google |
| Electric Studio | Manrope | Manrope | Google |
| Creative Voltage | Syne | Space Mono | Google |
| Dark Botanical | Cormorant | IBM Plex Sans | Google |
| Blue Sky | System / SF Pro | System / SF Pro | System |
| Notebook Tabs | Bodoni Moda | DM Sans | Google |
| Pastel Geometry | Plus Jakarta Sans | Plus Jakarta Sans | Google |
| Split Pastel | Outfit | Outfit | Google |
| Vintage Editorial | Fraunces | Work Sans | Google |
| Neon Cyber | Clash Display | Satoshi | Fontshare |
| Terminal Green | JetBrains Mono | JetBrains Mono | JetBrains |

---

## DO NOT USE (Generic AI Patterns)

**Fonts:** Inter, Roboto, Arial, system fonts as display

**Colors:** `#6366f1` (generic indigo), purple gradients on white

**Layouts:** Everything centered, generic hero sections, identical card grids

**Decorations:** Realistic illustrations, gratuitous glassmorphism, drop shadows without purpose

---

## CSS Gotchas (Common Mistakes)

### Negating CSS Functions

**WRONG — silently ignored by browsers:**
```css
right: -clamp(28px, 3.5vw, 44px);   /* ❌ Invalid! Browser ignores this */
margin-left: -min(10vw, 100px);      /* ❌ Invalid! */
top: -max(2rem, 4vh);                /* ❌ Invalid! */
```

**CORRECT — wrap in `calc()`:**
```css
right: calc(-1 * clamp(28px, 3.5vw, 44px));  /* ✅ */
margin-left: calc(-1 * min(10vw, 100px));     /* ✅ */
top: calc(-1 * max(2rem, 4vh));               /* ✅ */
```

CSS does not allow a leading `-` before function names like `clamp()`, `min()`, `max()`. The browser silently discards the entire declaration, causing the property to fall back to its initial/inherited value. This is especially dangerous because there is no console error — the element simply appears in the wrong position.

**Rule: Always use `calc(-1 * ...)` to negate CSS function values.**

---

## Troubleshooting Viewport Issues

### Content Overflows the Slide

**Symptoms:** Scrollbar appears, content cut off, elements outside viewport

**Solutions:**
1. Check slide has `overflow: hidden` (not `overflow: auto` or `visible`)
2. Reduce content — split into multiple slides
3. Ensure all fonts use `clamp()` not fixed `px` or `rem`
4. Add/fix height breakpoints for smaller screens
5. Check images have `max-height: min(50vh, 400px)`

### Text Too Small on Mobile / Too Large on Desktop

**Symptoms:** Unreadable text on phones, oversized text on big screens

**Solutions:**
```css
/* Use clamp with viewport-relative middle value */
font-size: clamp(1rem, 3vw, 2.5rem);
/*              ↑       ↑      ↑
            minimum  scales  maximum */
```

### Content Doesn't Fill Short Screens

**Symptoms:** Excessive whitespace on landscape phones or short browser windows

**Solutions:**
1. Add `@media (max-height: 600px)` and `(max-height: 500px)` breakpoints
2. Reduce padding at smaller heights
3. Hide decorative elements (`display: none`)
4. Consider hiding nav dots and hints on short screens

### Testing Recommendations

Test at these viewport sizes:
- **Desktop:** 1920×1080, 1440×900, 1280×720
- **Tablet:** 1024×768 (landscape), 768×1024 (portrait)
- **Mobile:** 375×667 (iPhone SE), 414×896 (iPhone 11)
- **Landscape phone:** 667×375, 896×414

Use browser DevTools responsive mode to quickly test multiple sizes.