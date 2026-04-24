# Neo-Retro Dev Deck — Style Reference

90s computer manuals meet modern AI dev tools — engineering notebook aesthetic. Pixel-art icons, thick black outlines, opinionated developer voice. Feels handmade and confident, like a zine printed at a hackathon.

---

## Colors

```css
:root {
    --bg: #f5f2e8;           /* engineering notebook cream */
    --grid: rgba(80, 100, 170, 0.10);  /* faint blue grid lines */
    --text: #111111;
    --pink: #FF3C7E;          /* hot pink — AI / intelligence concepts */
    --yellow: #FFE14D;        /* bright yellow — tools / builds */
    --cyan: #00C8FF;          /* cyan — web / networking */
    --border: #111111;        /* thick outlines */
    --block-bg: #ffffff;
    --block-dark: #1a1a1a;
}
```

---

## Background

```css
body {
    background-color: var(--bg);
    background-image:
        linear-gradient(var(--grid) 1px, transparent 1px),
        linear-gradient(90deg, var(--grid) 1px, transparent 1px);
    background-size: 24px 24px;
    font-family: "Barlow Condensed", "IBM Plex Sans", -apple-system, sans-serif;
}
```

---

## Typography

```css
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=swap');

.retro-title {
    font-family: "Barlow Condensed", sans-serif;
    font-size: clamp(28px, 6vw, 56px);
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: -0.01em;
    line-height: 1.0;
    color: var(--text);
}

.retro-body {
    font-family: "IBM Plex Sans", sans-serif;
    font-size: clamp(13px, 1.4vw, 16px);
    font-weight: 400;
    color: var(--text);
    line-height: 1.5;
}

.retro-mono {
    font-family: "IBM Plex Mono", monospace;
    font-size: clamp(11px, 1.2vw, 14px);
    color: var(--text);
}

.retro-comment {
    font-family: "IBM Plex Mono", monospace;
    font-size: clamp(11px, 1.2vw, 14px);
    color: var(--text);
    opacity: 0.5;
}
.retro-comment::before { content: '// '; }

.retro-label {
    font-family: "IBM Plex Mono", monospace;
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
```

---

## Components

```css
/* Thick bordered block — hard offset shadow */
.retro-block {
    background: var(--block-bg);
    border: 3px solid var(--border);
    border-radius: 0;
    box-shadow: 4px 4px 0 var(--border);
    padding: clamp(16px, 2.5vw, 24px);
}
.retro-block:hover {
    box-shadow: 2px 2px 0 var(--border);
    transform: translate(2px, 2px);
    transition: none;
}

/* Color-coded top border */
.retro-block.pink  { border-top: 4px solid var(--pink); }
.retro-block.yellow { border-top: 4px solid var(--yellow); }
.retro-block.cyan   { border-top: 4px solid var(--cyan); }

/* Section badge */
.retro-badge {
    display: inline-block;
    background: var(--yellow);
    border: 2px solid var(--border);
    border-radius: 0;
    padding: 2px 8px;
    font-family: "IBM Plex Mono", monospace;
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* Highlighted text */
.retro-highlight {
    background: var(--yellow);
    border: 2px solid var(--border);
    padding: 0 4px;
    display: inline;
}
```

---

## Named Layout Variations

### 1. System Architecture

Title top-left in `Barlow Condensed`. Center: stacked horizontal layer blocks (each = a system component). Colors indicate category: pink=AI, yellow=tools, cyan=web. Each block: `3px border`, monospace label inside, hard offset shadow. Arrow connectors `2px` between layers.

### 2. Evolution / Timeline

Horizontal flow left to right. Each era: thick-bordered box, era label in `IBM Plex Mono` badge, 2-line `Barlow Condensed` description. `→` arrow between boxes. Current era: `border-color: var(--pink)`, subtle pink fill. Future: dashed border.

### 3. Feature Cards

3-card row or 2×2 grid. Each card: pixel SVG icon top-right corner, feature name in `Barlow Condensed` 1.4rem, `// 1–2 line comment` in mono below. Border: `3px --border`, hard shadow. Top border accent: one of pink/yellow/cyan per card, consistent with color system.

### 4. Before / After

Two-panel split. `BEFORE` header left (muted, `#666`), `AFTER` right (green `#22c55e` or cyan). Each panel: thick border, content in `IBM Plex Mono` or `Barlow`. Divider: `4px` hard black center line. Clear improvement framing — no bad news.

### 5. Manifesto / Thesis

Large bold statement in `Barlow Condensed` 900 UPPERCASE, 40%+ of slide. Below: 3 `// supporting points` in `IBM Plex Mono` 0.9rem. One key word in the headline: `background: var(--yellow)` highlight, `2px --border`, inline. Everything in one thick-bordered content block.

### 6. Metrics Dashboard

Pixel-style bar chart: bars are thick-bordered rectangles (not rounded), fill with color codes. Y-axis: simple tick marks in mono. Each bar labeled below in `IBM Plex Mono`. Key bar: pink or yellow fill. Title above in `Barlow Condensed`. Chart sits inside one large bordered block.

---

## Signature Elements

### CSS Overlays
- `.slide::after`: 方格纸网格叠加（24px 间距，淡蓝）— `background-image: linear-gradient(rgba(80,100,170,0.10) 1px, transparent 1px), linear-gradient(90deg, rgba(80,100,170,0.10) 1px, transparent 1px); background-size: 24px 24px; pointer-events: none; z-index: 0`（注意：备份 HTML 中网格直接设置在 body 上而非 `::after`，两者等效）

### Animations
- 无 `@keyframes`，全部使用 CSS transitions
- `.reveal`: 入场动画 — `opacity: 0; transform: translateY(20px); transition: opacity 0.5s cubic-bezier(0.16,1,0.3,1), transform 0.5s cubic-bezier(0.16,1,0.3,1)`；`.slide.visible .reveal { opacity: 1; transform: translateY(0); }`
- Stagger delays: `.reveal:nth-child(1-7)` — `0.05s, 0.12s, 0.19s, 0.26s, 0.33s, 0.40s, 0.47s`

### Required CSS Classes
- `.block` (`.retro-block`): 厚边框卡片 — `background: var(--block-bg); border: 3px solid var(--border); box-shadow: 4px 4px 0 var(--border); padding: clamp(0.8rem,2vw,1.5rem)`
- `.block-dark` (`.retro-block` dark var): 深色变体 — `background: var(--block-dark); color: #f7f5f0`
- `.accent-pink` / `.accent-yellow` / `.accent-cyan`: 顶部彩色边框 — `border-top: 5px solid var(--pink/yellow/cyan)`
- `.badge` / `.badge-pink` / `.badge-cyan` (`.retro-badge`): 章节徽章 — `font-family: 'IBM Plex Mono'; text-transform: uppercase; border: 2px solid var(--border); background: var(--yellow)`
- `.hl` / `.hl-pink` / `.hl-cyan` (`.retro-highlight`): 行内高亮 — `background: var(--yellow); border: 1.5px solid var(--border); padding: 0 4px`
- `.headline` (`.retro-title`): 标题 — `font-family: 'Barlow Condensed'; font-weight: 900; text-transform: uppercase`
- `.comment` (`.retro-comment`): 注释风格 — `font-family: 'IBM Plex Mono'; color: #666; &::before { content: '// ' }`
- `.bc`: Barlow Condensed 缩写类
- `.mono`: IBM Plex Mono 缩写类

### Allowed Components
- Audit coverage: .cyan .pink .retro-body .retro-label .retro-mono .yellow

### Background Rule
`.slide` 不设置 background。body 使用米色 `#f5f2e8` + 24px 淡蓝网格（`rgba(80,100,170,0.10)`）。网格通过 `body` 的 `background-image` 设置。

### Style-Specific Rules
- 颜色编码（全 deck 一致）：pink=AI/intelligence，yellow=tools/builds，cyan=web/networking
- 硬偏移阴影 `box-shadow: 4px 4px 0 var(--border)` 在所有内容块上
- 所有容器 `border: 3px solid #000`，`border-radius: 0`（或最大 4px）
- `//` 注释风格用于子点和标注，`IBM Plex Mono`，最多 8 个词
- 声明式语句：只用 `"It runs 3x faster"` 不用 `"We're excited to share..."`
- 数字胜过形容词：`"83ms p95"` 不用 `"blazing fast"`
- 禁止：库存照片、大面积渐变、超过 4px 的圆角、buzzwords（"revolutionary"、"game-changing" 等）
- 导航点使用厚边框方块（`border: 2px solid var(--border)`），激活时 `background: var(--yellow); box-shadow: 2px 2px 0 var(--border)`

### Signature Checklist
- [ ] 米色背景 `#f5f2e8` + 淡蓝 24px 网格可见
- [ ] 厚边框卡片（`3px solid #000`）+ 硬偏移阴影（`4px 4px 0 #000`）
- [ ] Barlow Condensed 900 weight，UPPERCASE 标题
- [ ] `//` 注释风格标注（mono 文字）
- [ ] 颜色编码（pink/yellow/cyan）全 deck 一致
- [ ] 无超过 4px 的圆角
- [ ] 无大面积渐变

## Tone Rules

- Declarative sentences only: `"It runs 3× faster"` not `"We're excited to share..."`
- No buzzwords: no "revolutionary", "game-changing", "cutting-edge", "robust"
- `//` comment style for sub-points and annotations
- Numbers over adjectives: `"83ms p95"` not `"blazing fast"`
- One opinion per slide, stated plainly

---

## Animation

```css
.reveal {
    opacity: 0;
    transition: opacity 0.3s ease;
}
.reveal.visible { opacity: 1; }
.reveal:nth-child(1) { transition-delay: 0.05s; }
.reveal:nth-child(2) { transition-delay: 0.1s; }
.reveal:nth-child(3) { transition-delay: 0.15s; }
```

---

## Style Preview Checklist

- [ ] Cream background `#f5f2e8` with faint blue grid
- [ ] Thick-bordered blocks with hard offset shadows
- [ ] Barlow Condensed at 900 weight, UPPERCASE headlines
- [ ] `//` comment style annotations in mono
- [ ] Color coding: pink/yellow/can consistent across deck
- [ ] No rounded corners above 4px
- [ ] No gradients on large areas

---

## Best For

Dev tool launches · API documentation · Engineering team updates · Hackathon presentations · Open-source project pitches · Technical architecture reviews
