# Electric Studio — Style Reference

Bold, clean, professional, high contrast. Split panel design with confident typography.

---

## Colors

```css
:root {
    --bg-dark: #0a0a0a;
    --bg-white: #ffffff;
    --accent-blue: #4361ee;
    --text-dark: #0a0a0a;
    --text-light: #ffffff;
}
```

---

## Background

```css
body {
    background: var(--bg-dark);
    font-family: "Manrope", -apple-system, sans-serif;
}
```

---

## Typography

```css
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;800&display=swap');

.elec-title {
    font-family: "Manrope", sans-serif;
    font-size: clamp(32px, 6vw, 64px);
    font-weight: 800;
    line-height: 1.05;
    color: var(--text-dark);
}

.elec-body {
    font-family: "Manrope", sans-serif;
    font-size: clamp(14px, 1.5vw, 18px);
    font-weight: 400;
    line-height: 1.6;
    color: var(--text-dark);
    opacity: 0.7;
}

.elec-label {
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--accent-blue);
}

.elec-quote {
    font-family: "Manrope", sans-serif;
    font-size: clamp(20px, 3vw, 36px);
    font-weight: 800;
    line-height: 1.3;
    color: var(--text-dark);
}
```

---

## Components

```css
/* Accent bar on panel edge */
.elec-accent-bar {
    width: 4px;
    height: 100%;
    background: var(--accent-blue);
}

/* Split panel */
.elec-split {
    display: grid;
    grid-template-columns: 1fr 1fr;
    height: 100%;
}
.elec-panel-white {
    background: var(--bg-white);
    padding: clamp(24px, 4vw, 60px);
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.elec-panel-dark {
    background: var(--bg-dark);
    padding: clamp(24px, 4vw, 60px);
    display: flex;
    flex-direction: column;
    justify-content: center;
}

/* Quote typography as hero element */
.elec-quote-block {
    border-left: 4px solid var(--accent-blue);
    padding-left: clamp(16px, 2.5vw, 24px);
    margin: clamp(16px, 2.5vw, 28px) 0;
}
```

---

## Named Layout Variations

### 1. Studio Hero (全屏宣告)

Dark `#0a0a0a` background. White panel on one side (45-55% width) with headline in Manrope 800, `clamp(32px, 6vw, 64px)`. Blue accent bar `.elec-accent-bar` (4px) on panel edge. Label in `.elec-label` (small, uppercase, blue).

```html
<section class="slide" style="padding:0;">
    <div class="elec-split">
        <div class="elec-panel-dark">
            <span class="elec-label">Studio</span>
            <h1 class="elec-title" style="color:#fff;">Big Statement</h1>
        </div>
        <div class="elec-panel-white">
            <p class="elec-body">Supporting content</p>
        </div>
    </div>
</section>
```

### 2. Studio Split (分屏对比/分栏证据)

Full `.elec-split` — white left, dark right (or reversed). Left: section number + headline. Right: bullet list or evidence. No divider — color split creates the boundary. `.elec-accent-bar` between panels.

### 3. Studio Quote (功能亮点)

Single panel (white or dark) with `.elec-quote-block`: `border-left: 4px solid var(--accent-blue)`, `padding-left: clamp(16px, 2.5vw, 24px)`. Quote in `.elec-quote` (Manrope 800, `clamp(20px, 3vw, 36px)`). Attribution in `.elec-body` muted.

### 4. Studio Stat (大数字强调)

Dark background. Large white number in Manrope 800, `clamp(48px, 8vw, 96px)`. Blue accent label above. Clean, minimal — single focal point.

---

## Signature Elements

- Two-panel vertical split
- Accent bar on panel edge
- Quote typography as hero element
- Minimal, confident spacing

---

## Animation

```css
.reveal {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.5s ease, transform 0.5s ease;
}
.reveal.visible { opacity: 1; transform: translateY(0); }
.reveal:nth-child(1) { transition-delay: 0.05s; }
.reveal:nth-child(2) { transition-delay: 0.15s; }
.reveal:nth-child(3) { transition-delay: 0.25s; }
```

---

## Style Preview Checklist

- [ ] Split panel layout (white/dark or dark/white)
- [ ] Accent blue `#4361ee` on at least one element
- [ ] Manrope font at 800 weight for headlines
- [ ] Minimal decoration — confidence through spacing
- [ ] No pure black background — using `#0a0a0a`

---

## Best For

Agency presentations · Product showcases · Design portfolios · Brand identity decks · Professional pitches
