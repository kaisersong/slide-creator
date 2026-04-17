# Bold Signal — Style Reference

Confident, bold, modern, high-impact. Dark canvas with colored card focal points.

---

## Colors

```css
:root {
    --bg-primary: #1a1a1a;
    --bg-gradient: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%);
    --card-bg: #FF5722;
    --text-primary: #ffffff;
    --text-on-card: #ffffff;
}
```

---

## Background

```css
body {
    background: var(--bg-gradient);
    font-family: "Space Grotesk", -apple-system, sans-serif;
}

/* Ghost section number as texture */
.bold-ghost-number {
    position: absolute;
    font-size: clamp(6rem, 12vw, 10rem);
    font-family: "Archivo Black", sans-serif;
    color: var(--card-bg);
    opacity: 0.08;
    pointer-events: none;
    user-select: none;
}
```

---

## Typography

```css
/* Display */
@import url('https://fonts.googleapis.com/css2?family=Archivo+Black&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500&display=swap');

.bold-title {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(32px, 6vw, 72px);
    font-weight: 900;
    color: var(--text-primary);
    line-height: 1.0;
    letter-spacing: -0.02em;
}

.bold-body {
    font-family: "Space Grotesk", sans-serif;
    font-size: clamp(14px, 1.5vw, 18px);
    font-weight: 400;
    color: rgba(255,255,255,0.6);
    line-height: 1.6;
}

.bold-label {
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: rgba(255,255,255,0.4);
}

/* Bullet marker */
.bold-bullet { color: var(--card-bg); }
```

---

## Components

```css
/* Hero card — colored focal point */
.bold-hero-card {
    background: var(--card-bg);
    border-radius: 8px;
    padding: clamp(24px, 4vw, 48px);
    color: var(--text-on-card);
}

/* Section number badge */
.bold-section-num {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(14px, 1.8vw, 20px);
    color: var(--card-bg);
    opacity: 0.9;
}

/* Bullet point with card-colored marker */
.bold-bullet::before {
    content: '▸';
    color: var(--card-bg);
    margin-right: 0.5em;
}

/* Timeline step */
.bold-step {
    border: 2px solid var(--card-bg);
    border-radius: 4px;
    padding: 8px 16px;
    text-align: center;
    font-size: clamp(12px, 1.3vw, 16px);
}
.bold-step.active {
    background: var(--card-bg);
    color: var(--text-on-card);
}
```

---

## Named Layout Variations

### 1. Hero Card

Large colored card (`--card-bg`) occupies 60% of width, centered vertically, anchored left. Card: section number `01` small top-left, headline 2–3 lines. Dark background outside card. Ghost section number in 10rem at 8% opacity as texture. Nav breadcrumbs top-right.

### 2. Manifesto Statement

`01` in 8rem `Archivo Black` top-left, card color. Below: 2-line statement in 3rem. Right half: supporting 3-line body paragraph in muted white `rgba(255,255,255,0.6)`. Bottom-left: next section teaser in 0.75rem mono.

### 3. Feature Trio

Three full-width horizontal rows, shorter height than a normal card. Active/highlighted row: full `--card-bg` color. Other rows: 20% opacity, outlined. Each row: number left, feature name center-left in 1.3rem, 1-line descriptor right.

### 4. Stat + Story

Left 40%: single large number `5rem` in `--card-bg` color, label below in 0.75rem uppercase. `1px` vertical rule (card color). Right 55%: 3-line supporting paragraph + 2–3 bullet points with card-colored ▸ markers.

### 5. Timeline Track

Horizontal numbered steps `01 → 02 → 03 → 04`. Active step: full colored card above the track line. Completed steps: full opacity outlined. Future steps: 30% opacity outlined. Track line: `2px --card-bg`.

### 6. Quote Block

Full-width colored card (`--card-bg` background). Large `"` in near-black at top-left, barely visible (8% opacity). Quote in `Archivo Black` 2rem, dark text. Attribution bottom-right: `—Name, Role` in small body.

### 7. Split Evidence

Left 42%: section number in 3rem + headline in 2rem + 1-line sub. `1px` vertical rule (card color). Right 53%: 4–5 bullet list, each bullet: card-colored ▸ + bold lead word + 1-line description.

---

## Signature Elements

### CSS Overlays
- `.slide::after`: 半透明网格叠加 — `background-image: linear-gradient(rgba(255,87,34,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,87,34,0.04) 1px, transparent 1px); background-size: 60px 60px; pointer-events: none; z-index: 0`
- `#slide-8::after`: CTA 页禁用网格 — `display: none;`（全橙色背景页不需要网格）

### Animations
- 无 `@keyframes`，全部使用 CSS transitions
- `.reveal`: 入场动画 — `opacity: 0; transform: translateY(28px); transition: opacity 0.5s ease-out, transform 0.5s ease-out;`；`.slide.visible .reveal` 触发恢复
- Stagger delays: `.slide.visible .reveal:nth-child(1-4)` — `0.05s, 0.15s, 0.25s, 0.35s`

### Required CSS Classes
- `.slide-num`: 幽灵章节号 — `position: absolute; font-family: 'Archivo Black'; font-size: 120px; color: #FF5722; opacity: 0.12; z-index: 1; pointer-events: none`
- `.breadcrumb`: 顶部导航面包屑 — `position: absolute; top: 36px; right: 56px; font-size: 12px; font-weight: 600; letter-spacing: 0.15em; color: rgba(255,255,255,0.3); text-transform: uppercase`
- `.corner-accent`: 左上角强调条 — `position: absolute; top: 0; left: 0; width: 100px; height: 3px; background: #FF5722`
- `.big-num-bg`: 背景装饰大字 — `position: absolute; font-family: 'Archivo Black'; font-size: 38vw; color: rgba(255,87,34,0.04); pointer-events: none`
- `.badge`: 实心底色标签 — `background: #FF5722; color: #fff; font-family: 'Archivo Black'; padding: 9px 20px; font-size: 13px`
- `.badge.outline`: 描边标签 — `background: transparent; border: 1.5px solid rgba(255,87,34,0.4); color: rgba(255,255,255,0.55)`
- `.hero-card`: 主强调卡片 — `background: #FF5722; padding: 52px 56px; color: #fff; position: relative; z-index: 2`
- `.deco-text`: CTA 页装饰文字 — `position: absolute; right: -40px; bottom: -60px; font-family: 'Archivo Black'; font-size: 36vw; color: rgba(255,255,255,0.06); pointer-events: none`
- `.dot` / `.dot.active`: 导航圆点 — 默认 `rgba(255,87,34,0.3)` + `1px solid rgba(255,87,34,0.5)`；激活 `background: #FF5722; transform: scale(1.4)`

### Background Rule
`.slide` 必须设置 `background: #1a1a1a`（纯色，非渐变）。body 设置 `background: #1a1a1a`。网格叠加通过 `.slide::after` 伪元素实现。CTA 页（`#slide-8`）使用 `background: #FF5722` 并禁用 `::after`。

### Style-Specific Rules
- 所有章节号使用 Archivo Black 字体，大尺寸半透明作为纹理
- 导航面包屑固定于右上角，使用 rgba 透明度区分活跃状态
- 彩色卡片 `#FF5722` 作为唯一强调色，不引入其他颜色
- 装饰文字（`.big-num-bg`, `.deco-text`）使用超大字号 + 极低透明度

### Signature Checklist
- [ ] `.slide::after` 网格叠加（rgba(255,87,34,0.04)，60px 间距）
- [ ] `.slide-num` 幽灵章节号（Archivo Black, 120px, opacity 0.12）
- [ ] `.breadcrumb` 顶部导航面包屑
- [ ] `.hero-card` 彩色主卡片（#FF5722）
- [ ] `.badge` + `.badge.outline` 标签系统
- [ ] `.corner-accent` 左上角强调条
- [ ] `.big-num-bg` / `.deco-text` 背景装饰文字
- [ ] `.dot` 导航圆点（橙色 + 激活缩放）
- [ ] `.reveal` 入场动画（translateY 28px，stagger 0.05s-0.35s）
- [ ] CTA 页 `background: #FF5722` 且 `::after { display: none }`

---

## Animation

```css
.reveal {
    opacity: 0;
    transform: translateY(24px);
    transition: opacity 0.6s cubic-bezier(0.16,1,0.3,1),
                transform 0.6s cubic-bezier(0.16,1,0.3,1);
}
.reveal.visible { opacity: 1; transform: translateY(0); }
.reveal:nth-child(1) { transition-delay: 0.08s; }
.reveal:nth-child(2) { transition-delay: 0.18s; }
.reveal:nth-child(3) { transition-delay: 0.28s; }
```

---

## Style Preview Checklist

- [ ] Dark gradient background `#1a1a1a → #2d2d2d`
- [ ] Colored card (`--card-bg`) as focal point
- [ ] Large section number (01, 02, etc.) visible
- [ ] Ghost section number at 8% opacity as texture
- [ ] At least one named layout pattern used
- [ ] No pure black background — using `#1a1a1a`

---

## Best For

Pitch decks · Keynotes · Product launches · High-impact presentations · Brand statements · Investor pitches
