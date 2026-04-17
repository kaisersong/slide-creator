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

### CSS Overlays
- 无伪元素叠加层。暗色画布完全由 `body { background: #0f0f0f }` 提供，不使用网格/纹理覆盖。光球（`.orb`）是唯一视觉叠加。

### Animations
- `.orb`: 光球淡入 — `opacity: 0; filter: blur(80px); pointer-events: none; transition: opacity 1.2s ease`；`.slide.visible .orb { opacity: 1 }`
- `.accent-line`: 垂直线条动画 — `opacity: 0; transform: scaleY(0); transform-origin: top; transition: opacity 0.8s ease 0.3s, transform 0.8s ease 0.3s`；`.slide.visible .accent-line { opacity: 0.4; transform: scaleY(1) }`
- `.reveal`: 内容入场 — `opacity: 0; transform: translateY(20px); transition: opacity 0.8s ease, transform 0.8s ease`；stagger delays `.reveal-1` 到 `.reveal-5`（0.1s, 0.25s, 0.4s, 0.55s, 0.7s）

### Required CSS Classes
- `.orb`: 软光球基类 — `position: absolute; border-radius: 50%; filter: blur(80px); pointer-events: none; opacity: 0; transition: opacity 1.2s ease`
- `.orb-pink`: 粉色光球 — `background: radial-gradient(circle, rgba(232,180,184,0.18), transparent 70%)`
- `.orb-gold`: 金色光球 — `background: radial-gradient(circle, rgba(201,184,150,0.15), transparent 70%)`
- `.orb-terra`: 赤土色光球 — `background: radial-gradient(circle, rgba(212,165,116,0.12), transparent 70%)`
- `.accent-line`: 垂直渐变线条 — `position: absolute; left: clamp(32px, 6vw, 72px); top: 20%; height: 60%; width: 1px; background: linear-gradient(to bottom, transparent, #c9b896 30%, #e8b4b8 70%, transparent)`
- `.slide-label`: 章节斜体标签 — `font-family: 'Cormorant', serif; font-style: italic; font-size: clamp(11px, 1.2vw, 14px); letter-spacing: 0.25em; text-transform: uppercase; color: #c9b896`
- `.divider`: 短分隔线 — `width: 48px; height: 1px; background: linear-gradient(90deg, #c9b896, #e8b4b8); margin: auto`
- `.badge` + `.badge strong`: 统计徽章 — `padding: 8px 20px; border: 1px solid #2a2520; border-radius: 2px;` 数值用 Cormorant 600 金色
- `.pain-list`: 要点列表 — `list-style: none; li::before { content: '—'; color: #e8b4b8; font-family: 'Cormorant', serif }`
- `.steps` + `.step-num`: 步骤列表 — 斜体序号 `font-family: 'Cormorant'; font-style: italic; color: #c9b896`
- `.feature` + `.feature-grid`: 功能卡片 — `border: 1px solid #1e1e1e; border-left: 1px solid #c9b896; background: rgba(255,255,255,0.015)`
- `.code-block`: 代码块 — `background: #0a0a0a; border: 1px solid #1e1e1e; border-left: 2px solid #c9b896; font-family: 'IBM Plex Mono'`
- `.preset.tag`: 预设标签 — `border: 1px solid #2a2520;` hover 变金色，`.current` 变实色
- `.dot` / `.dot.active`: 导航圆点 — 默认 `#3a3530 + 1px solid #5a5550`；激活 `#c9b896 + box-shadow: 0 0 8px rgba(201,184,150,0.5)`

### Background Rule
`.slide` 不设 background，完全由 `body { background: #0f0f0f }` 纯色提供暗色画布。不使用伪元素覆盖。光球直接作为子元素放置在 slide 内（绝对定位）。

### Style-Specific Rules
- 每页 2-3 个光球，位置错开（top-right / bottom-left / center），大小 350-600px
- `.accent-line` 固定在左侧 `clamp(32px, 6vw, 72px)` 处，渐变从透明到金色到粉色
- 所有文字使用 Cormorant（标题/装饰）+ IBM Plex Sans（正文）两种字体，无第三种
- 不使用插图或图标，仅用抽象 CSS 形状（光球、线条）
- 颜色全部为低饱和暖色调，不使用鲜艳颜色

### Signature Checklist
- [ ] `.orb` 软光球（3 种颜色：pink / gold / terra，blur 80px）
- [ ] `.accent-line` 垂直渐变线条（金到粉渐变）
- [ ] `.slide-label` Cormorant 斜体小标签
- [ ] `.divider` 短分隔线（金到粉渐变）
- [ ] `.badge` 统计徽章（Cormorant 金色数值）
- [ ] `.pain-list` 要点列表（破折号前缀 #e8b4b8）
- [ ] `.steps` + `.step-num` 斜体步骤序号
- [ ] `.feature-grid` + `.feature` 功能卡片（左金色边框）
- [ ] `.code-block` 代码块（IBM Plex Mono，左金色 2px 边框）
- [ ] `.reveal` 入场动画（stagger 5 级 0.1s-0.7s）
- [ ] `.dot` 导航圆点（激活时金色光晕）
- [ ] 无伪元素叠加 — 纯 `#0f0f0f` 画布 + 光球

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
