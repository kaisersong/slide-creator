# Swiss Modern — Style Reference

Clean, precise, Bauhaus-inspired — International Typographic Style as a presentation. Form follows function absolutely. The grid is not a tool; it is the design.

---

## Colors

```css
:root {
    --bg: #ffffff;
    --bg-dark: #0a0a0a;
    --text: #0a0a0a;
    --text-light: #ffffff;
    --text-muted: #666666;
    --red: #ff3300;       /* single accent — one element per slide maximum */
    --grid-line: rgba(0, 0, 0, 0.05);
}
```

---

## Background

```css
body {
    background: var(--bg);
    font-family: "Archivo Black", "Nunito", -apple-system, sans-serif;
}

/* Visible 12-column grid — faintly visible */
.swiss-grid {
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(var(--grid-line) 1px, transparent 1px),
        linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
    background-size: calc(100vw / 12) 100vh;
    pointer-events: none;
    z-index: 0;
}
```

---

## Typography

```css
@import url('https://fonts.googleapis.com/css2?family=Archivo+Black:wght@900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600&display=swap');

.swiss-title {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(32px, 7vw, 72px);
    font-weight: 900;
    color: var(--text);
    line-height: 1.0;
    letter-spacing: -0.02em;
    text-transform: uppercase;
}

.swiss-body {
    font-family: "Nunito", sans-serif;
    font-size: clamp(12px, 1.4vw, 15px);
    font-weight: 400;
    color: var(--text);
    line-height: 1.55;
    max-width: 55ch;
}

.swiss-label {
    font-family: "Archivo", sans-serif;
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
}

.swiss-stat {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(48px, 8vw, 96px);
    font-weight: 900;
    color: var(--text);
    line-height: 1.0;
}
```

---

## Components

```css
/* Hard horizontal rule — no decorative curves, no dashes */
.swiss-rule {
    height: 2px;
    background: var(--text);
    border: none;
}
.swiss-rule.red {
    background: var(--red);
}
.swiss-rule-thin {
    height: 1px;
    background: var(--text-muted);
    opacity: 0.2;
}
```

---

## Named Layout Variations

### 1. Title Grid

Slide number top-right in `Archivo Black` 1rem, red. Title bottom-left in 7rem, 2 lines max, `line-height: 0.95`. Empty upper-right quadrant. Red `2px` horizontal rule above the title.

### 2. Column Content

Left column 40%: large section heading + red `2px` rule below. Right column 55% (5% gap): body text in two typographic sub-columns. Section number top-right in small red.

### 3. Stat Block

One large number left half at 8rem `Archivo Black`. Vertical `2px` black rule to its right. Then: label in 1.2rem uppercase + 1-line supporting sentence in 0.9rem body. Red underline on the number only.

### 4. Data Table

Full-width table. Header row: `Archivo Black` 11px uppercase, `background: #0a0a0a`, white text. Body: alternating `#ffffff` / `#f7f7f7` rows, `1px #e0e0e0` dividers. Most important row: `3px` red left-border. No outer border.

### 5. Geometric Diagram

SVG diagram of boxes + connector lines, `stroke: #0a0a0a`, `stroke-width: 1.5`. No fills except primary node: `fill: #ff3300`. Labels in `Nunito` 12px. Grid visible behind. No shadows.

### 6. Pull Quote

One short sentence (max 12 words) in 3rem `Archivo Black`, top-left. Below it: `2px` red rule + attribution in 0.8rem `Nunito`. Remaining 50%+ of slide: pure white. Emptiness is the message.

### 7. Contents Index

Numbered list, left-aligned. Each item: section number in `3rem Archivo Black` red, em-dash, topic in `1.5rem Archivo Black` black. Max 5 items. Visible grid behind. No borders on items.

---

## Signature Elements

### CSS Overlays
- `body::before`: 12-column grid overlay — faint grid lines at 3% opacity `linear-gradient(rgba(0,0,0,0.03) 1px, transparent 1px)` + `linear-gradient(90deg, rgba(0,0,0,0.03) 1px, transparent 1px)`, `background-size: 40px 40px`, `position: fixed; inset: 0; z-index: 0; pointer-events: none`

### Animations
- `@keyframes fadeIn`: 元素淡入 — `from { opacity: 0; } to { opacity: 1; }`，配合 `.slide.visible .reveal` 使用 staggered delays (0.05s, 0.1s, 0.15s, 0.2s...)

### Required CSS Classes
- `.bg-num`: 背景大序号 — `position: absolute; right: clamp(2rem, 5vw, 5rem); top: 0; font-weight: 900; font-size: 25vw; color: #f0f0f0; line-height: 0.85; pointer-events: none; z-index: 0`
- `.content`: 内容层容器 — `position: relative; z-index: 1; flex: 1; display: flex; flex-direction: column`
- `.eyebrow`: 小标签 — `font-weight: 600; font-size: clamp(0.65rem, 1vw, 0.75rem); letter-spacing: 0.2em; text-transform: uppercase`
- `.swiss-stat`: 大数字 — `font-family: "Archivo Black", sans-serif; font-size: clamp(48px, 8vw, 96px); font-weight: 900; line-height: 1.0`
- `.swiss-rule`: 硬分隔线 — `height: 2px; background: var(--text); border: none`；`.swiss-rule.red` 使用 `background: var(--red)`
- `.swiss-rule-thin`: 细分隔线 — `height: 1px; background: var(--text-muted); opacity: 0.2`

### Background Rule
`.slide` 必须设置 `background: #ffffff`。body 为纯白，12 列网格通过 `body::before` 叠加。不使用渐变。

### Style-Specific Rules
- 每页最多一个红色 `#ff3300` 强调元素，不得用于大面积填充
- 标题必须非对称锚定（左或左下），永远不居中
- 无渐变、无阴影、无圆角、无插图
- 使用 Archivo Black (900) + Nunito (400/600) 字体组合
- 硬水平分隔线 `2px solid #0a0a0a`，无装饰曲线或虚线

### Signature Checklist
- [ ] body::before 12 列网格叠加（3% 不透明度）
- [ ] @keyframes fadeIn（staggered delays）
- [ ] .bg-num 背景大序号（25vw Archivo Black 900）
- [ ] .content 内容层（z-index: 1）
- [ ] .eyebrow 小标签（uppercase, 0.2em 字间距）
- [ ] .swiss-stat 大数字（Archivo Black 900）
- [ ] .swiss-rule 硬分隔线（2px solid #0a0a0a）
- [ ] .swiss-rule.red 红色分隔线（#ff3300）
- [ ] 每页最多一个红色强调元素
- [ ] 标题非对称锚定（左或左下）
- [ ] 无渐变、无阴影、无圆角

---

## Animation

```css
.reveal {
    opacity: 0;
    transition: opacity 0.4s ease;
}
.reveal.visible { opacity: 1; }
.reveal:nth-child(1) { transition-delay: 0.05s; }
.reveal:nth-child(2) { transition-delay: 0.15s; }
.reveal:nth-child(3) { transition-delay: 0.25s; }
```

---

## Style Preview Checklist

- [ ] White background with faint 12-column grid
- [ ] Archivo Black at 900 weight, uppercase headlines
- [ ] Red `#ff3300` accent on exactly one element per slide
- [ ] Hard horizontal rules (2px solid black)
- [ ] No gradients, no shadows, no rounded corners
- [ ] Asymmetric anchoring — left or bottom-left, never centered

---

## Best For

Corporate presentations · Data reports · Architecture firm decks · Design studio pitches · Swiss/International style showcases · Precise, data-heavy content
