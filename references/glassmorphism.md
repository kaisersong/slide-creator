# Glassmorphism — Style Reference

Light, translucent, and modern. Inspired by Apple WWDC slides and iOS Control Center. Frosted glass cards float over a colorful blurred-orb background.

---

## Colors

```css
:root {
    --bg-gradient-1: #667eea;
    --bg-gradient-2: #764ba2;
    --bg-gradient-3: #f093fb;
    --glass-bg: rgba(255, 255, 255, 0.15);
    --glass-border: rgba(255, 255, 255, 0.30);
    --glass-text-dark: #1a1a2e;
    --glass-text-light: rgba(255,255,255,0.92);
    --orb-purple: rgba(102,126,234,0.5);
    --orb-pink: rgba(240,147,251,0.4);
    --orb-mint: rgba(168,237,234,0.4);
}
```

---

## Background

```css
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    font-family: -apple-system, "SF Pro Display", BlinkMacSystemFont, sans-serif;
    min-height: 100vh;
}

/* Blurred color orbs (required — backdrop-filter only works if there's something behind the card) */
.glass-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);
    pointer-events: none;
}
.orb-1 { width: 400px; height: 400px; background: var(--orb-purple); top: -10%; left: -5%; }
.orb-2 { width: 300px; height: 300px; background: var(--orb-pink); bottom: -5%; right: -5%; }
.orb-3 { width: 250px; height: 250px; background: var(--orb-mint); top: 30%; right: 15%; }
```

---

## Background Options

```css
/* Option A — Cool (purple to pink) */
.bg-cool {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
}

/* Option B — Warm (pink to ocean) */
.bg-warm {
    background: linear-gradient(135deg, #f8cdda 0%, #a6c1ee 50%, #1d6fa4 100%);
}

/* Option C — Mint (fresh, product feel) */
.bg-mint {
    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 50%, #a8edea 100%);
}
```

**Blurred color orbs (required — backdrop-filter only works if there's something behind the card):**

```css
.glass-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);
    pointer-events: none;
}
/* Example orb placements */
.orb-1 { width: 400px; height: 400px; background: rgba(102,126,234,0.5); top: -10%; left: -5%; }
.orb-2 { width: 300px; height: 300px; background: rgba(240,147,251,0.4); bottom: -5%; right: -5%; }
.orb-3 { width: 250px; height: 250px; background: rgba(168,237,234,0.4); top: 30%; right: 15%; }
```

---

## Card Components

```css
/* Primary glass card */
.glass-card {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(20px) saturate(1.5);
    -webkit-backdrop-filter: blur(20px) saturate(1.5);
    border: 1px solid rgba(255, 255, 255, 0.30);
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.10);
    padding: clamp(1.2rem, 2.5vw, 2rem);
}

/* Secondary glass card (list items, smaller blocks) */
.glass-card-sm {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px) saturate(1.3);
    -webkit-backdrop-filter: blur(12px) saturate(1.3);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    padding: clamp(0.75rem, 1.5vw, 1.2rem);
}

/* Dark text variant (on lighter backgrounds) */
.glass-card.dark-text { color: #1a1a2e; }

/* Light text variant (on darker backgrounds) */
.glass-card.light-text { color: rgba(255,255,255,0.92); }
```

---

## Typography

```css
/* System font stack — SF Pro feel on Apple, Segoe on Windows */
body {
    font-family: -apple-system, "SF Pro Display", BlinkMacSystemFont,
                 "PingFang SC", "Noto Sans CJK SC", "Segoe UI", system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
}

.glass-title {
    font-size: clamp(2rem, 6vw, 5rem);
    font-weight: 700;
    letter-spacing: -0.01em;
    line-height: 1.1;
    /* Choose dark or light based on background */
    color: #1a1a2e;   /* or rgba(255,255,255,0.95) */
}

.glass-body {
    font-size: clamp(0.85rem, 1.5vw, 1.1rem);
    line-height: 1.65;
    color: rgba(30, 30, 60, 0.80);   /* or rgba(255,255,255,0.80) */
}

/* Icon-style circular badge */
.glass-icon-wrap {
    width: clamp(2rem, 4vw, 3rem);
    height: clamp(2rem, 4vw, 3rem);
    border-radius: 50%;
    border: 1.5px solid rgba(255,255,255,0.5);
    display: flex; align-items: center; justify-content: center;
    background: rgba(255,255,255,0.2);
    font-size: 1.1em;
}
```

---

## Layout

```css
/* Centered single column — title slides */
.glass-slide-center {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    text-align: center;
    padding: clamp(2rem, 5vw, 5rem);
    position: relative; overflow: hidden;
}

/* Content grid — feature cards */
.glass-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 200px), 1fr));
    gap: clamp(0.75rem, 1.5vw, 1.2rem);
}
```

---

## Components

```css
/* Primary glass card */
.glass-card {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(20px) saturate(1.5);
    -webkit-backdrop-filter: blur(20px) saturate(1.5);
    border: 1px solid rgba(255, 255, 255, 0.30);
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.10);
    padding: clamp(1.2rem, 2.5vw, 2rem);
}

/* Secondary glass card */
.glass-card-secondary {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 12px;
    padding: clamp(0.75rem, 1.5vw, 1.2rem);
}

/* SF Symbols-style circle icon */
.glass-icon {
    width: clamp(24px, 3vw, 32px);
    height: clamp(24px, 3vw, 32px);
    border-radius: 50%;
    border: 1.5px solid rgba(255,255,255,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
}
```

---

## Animation

```css
/* Gentle float entrance */
.reveal {
    opacity: 0;
    transform: translateY(16px);
    transition: opacity 0.6s ease, transform 0.6s cubic-bezier(0.34,1.2,0.64,1);
}
.slide.visible .reveal { opacity: 1; transform: translateY(0); }
.reveal:nth-child(1) { transition-delay: 0.08s; }
.reveal:nth-child(2) { transition-delay: 0.18s; }
.reveal:nth-child(3) { transition-delay: 0.28s; }
.reveal:nth-child(4) { transition-delay: 0.38s; }
```

---

## Named Layout Variations

### 1. Glass Hero (全屏宣告)

3-color gradient background (`linear-gradient(135deg, #667eea, #764ba2, #f093fb)`). 3 blurred color orbs (`.glass-orb`). Centered white/dark headline, `clamp(2rem, 6vw, 5rem)`, weight 700. Subtitle below. No card on hero — text sits directly on gradient.

```html
<section class="slide">
    <div class="glass-orb orb-1"></div>
    <div class="glass-orb orb-2"></div>
    <div class="glass-orb orb-3"></div>
    <div class="slide-content" style="text-align:center;">
        <h1 class="glass-title">Big Statement</h1>
        <p class="glass-body">Supporting line</p>
    </div>
</section>
```

### 2. Glass Card (功能亮点/双列功能卡)

Single `.glass-card` centered on orb background. Card: `backdrop-filter: blur(20px) saturate(1.5)`, `background: rgba(255,255,255,0.15)`, `border: 1px solid rgba(255,255,255,0.30)`, `border-radius: 16px`. Content: title, body, optional `.glass-icon` badge.

### 3. Glass Split (分屏对比)

Two `.glass-card` elements side by side. `display: grid; grid-template-columns: 1fr 1fr; gap: clamp(0.75rem, 1.5vw, 1.2rem)`. Each card has different content. Orbs visible behind both cards.

### 4. Glass Trio (多选项对比)

Three glass cards in a row. `grid-template-columns: repeat(3, 1fr)`. Active card uses full `.glass-card` styling. Inactive cards use `.glass-card-sm` (lower opacity: `rgba(255,255,255,0.08)`). Each card: number + name + descriptor.

### 5. Glass Stat (大数字强调)

Large gradient text number centered. Label below in `.glass-body`. 1-2 orbs positioned to frame the number without competing. Clean, minimal.

---

## Signature Elements

### CSS Overlays
- `.orb` / `.orb1` / `.orb2` / `.orb3` / `.orb4`: 模糊光球（3-4 个）— `position: absolute; border-radius: 50%; filter: blur(60px); pointer-events: none; z-index: 0`。尺寸使用 vw 单位（25vw-40vw），半透明渐变颜色

### Animations
- 无 `@keyframes`，全部使用 CSS transitions
- `.reveal`: 浮动入场 — `opacity: 0; transform: translateY(16px); transition: opacity 0.6s cubic-bezier(0.34,1.2,0.64,1), transform 0.6s cubic-bezier(0.34,1.2,0.64,1)`；`.reveal.visible { opacity: 1; transform: translateY(0); }`
- Stagger delays: 100ms 递增，最大 400ms

### Required CSS Classes
- `.glass-card`: 主玻璃卡片 — `background: rgba(255,255,255,0.15); backdrop-filter: blur(20px) saturate(1.5); border: 1px solid rgba(255,255,255,0.30); border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.10)`
- `.glass-item`: 次级玻璃元素 — `background: rgba(255,255,255,0.08); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.20); border-radius: 12px`
- `.pill` / `.pill-dark` / `.pill-light`: 药丸徽章 — `background: rgba(255,255,255,0.20); border-radius: 100px; backdrop-filter: blur(8px)`
- `.stat-card`: 统计卡片（配合 `.glass-card` 使用）
- `.icon-circle`: SF Symbols 风格圆形图标 — `border-radius: 50%; border: 1.5px solid rgba(255,255,255,0.45)`
- `.tag` / `.tag-dark` / `.tag-light` / `.tag-highlight`: 标签变体
- `.text-dark` / `.text-light-theme`: 幻灯片文字主题切换
- `.sep` / `.sep-dark`: 分隔线
- `.slide-0` 到 `.slide-7`: 每张幻灯片的渐变背景（3 种渐变模式循环）

### Background Rule
`.slide` 必须设置背景。每张幻灯片使用独立的 3 色渐变（`linear-gradient(135deg, ...)`）。三种渐变模式，文字主题必须匹配：
- **紫色系（深底 → 白字 `.text-dark`）：** `#667eea → #764ba2 → #f093fb`
- **粉蓝系（浅底 → 深字 `.text-light-theme`）：** `#f8cdda → #a6c1ee → #1d6fa4` — 起始色 `#f8cdda` 亮度高，白色文字对比度不足，必须使用深色文字
- **薄荷系（浅底 → 深字 `.text-light-theme`）：** `#a8edea → #fed6e3` — 整体亮度高，必须使用深色文字

光球直接放在 `.slide` 内、卡片后方。

### Style-Specific Rules
- `backdrop-filter: blur()` 必须有彩色背景在其后方才能生效——光球是必需的，不是装饰
- 所有圆角遵循 iOS 设计语言：卡片 16px，次级元素 12px，药丸 100px
- 系统字体栈：`-apple-system, "SF Pro Display", BlinkMacSystemFont, sans-serif`——不使用自定义 web 字体
- 不使用边框（body）、网格图案、或几何形状装饰——只有渐变和模糊
- 暗色幻灯片文字用 `rgba(255,255,255,0.92)`，浅色幻灯片文字用 `#1a1a2e`
- PPTX 导出注意：`backdrop-filter` 效果仅浏览器支持，PPTX 中玻璃卡片会退化为半透明纯色填充

### Signature Checklist
- [ ] 彩色渐变或光球背景可见
- [ ] 至少一张卡片有 `backdrop-filter: blur(20px)` 磨砂效果
- [ ] `1px solid rgba(255,255,255,0.30)` 边框在卡片上可见
- [ ] 模糊光球放在卡片后方（不重叠内容）
- [ ] 圆角一致：12-16px
- [ ] 无 body 边框、无网格、无几何形状

---

## PPTX Export Note

When this style is used and the user requests PPTX export, add a note in the speaker notes of slide 1:

> **Export note:** The glassmorphism backdrop-filter effect is browser-only. In the PPTX export, glass cards will appear as flat semi-transparent fills. Consider adjusting card opacity to `rgba(255,255,255,0.70)` before exporting for best results.

---

## Style Preview Checklist

- [ ] Colorful gradient or multi-orb background is visible
- [ ] At least one card with `backdrop-filter: blur(20px)` clearly showing the frosted effect
- [ ] `1px solid rgba(255,255,255,0.30)` border visible on cards
- [ ] Blurred orbs are placed behind the card (not overlapping it)

---

## Best For

Consumer product launches · Brand identity presentations · Creative tool demos · Design portfolio · Any context where the visual design IS the message
