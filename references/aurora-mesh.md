# Aurora Mesh — Style Reference

Inspired by Linear.app, Vercel, and Stripe marketing pages. Animated multi-layer radial-gradient background creates a slowly drifting aurora effect on deep space black.

---

## Colors

```css
:root {
    --bg-primary:   #0a0a1a;
    --accent:       #00f5c4;                   /* cyan-green emphasis */
    --text-primary: #ffffff;
    --text-body:    rgba(255,255,255,0.70);
    --text-muted:   rgba(255,255,255,0.45);
    --card-bg:      rgba(255,255,255,0.05);
    --card-border:  rgba(255,255,255,0.10);
    --divider:      rgba(255,255,255,0.15);
}
```

---

## Background

```css
body {
    background-color: #0a0a1a;
    background-image:
        radial-gradient(ellipse at 20% 50%, rgba(120,40,200,0.40) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(0,180,255,0.30) 0%, transparent 50%),
        radial-gradient(ellipse at 60% 80%, rgba(0,255,180,0.20) 0%, transparent 50%);
    animation: auroraDrift 20s ease-in-out infinite alternate;
}

@keyframes auroraDrift {
    0%   { background-position: 0%   50%; }
    33%  { background-position: 50%  20%; }
    66%  { background-position: 80%  80%; }
    100% { background-position: 100% 50%; }
}
```

---

## Typography

```css
/* Title — use a distinctive display font, NOT Inter (banned as display typeface) */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&display=swap');
font-family: "Space Grotesk", "PingFang SC", "Noto Sans CJK SC", "Microsoft YaHei", sans-serif;
font-weight: 700;
letter-spacing: -0.03em;
color: #ffffff;

/* Body */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500&display=swap');
font-family: "DM Sans", "PingFang SC", system-ui, sans-serif;
font-weight: 400;
color: rgba(255,255,255,0.70);
line-height: 1.7;
```

---

## Card Component

```css
/* Content card — subtle glass, doesn't compete with background aurora */
.aurora-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: clamp(1.2rem, 2.5vw, 2rem);
}

/* Accent line / divider */
.aurora-divider {
    height: 1px;
    background: rgba(255,255,255,0.15);
    margin: clamp(1rem, 2vw, 1.5rem) 0;
}

/* Accent text */
.aurora-accent {
    color: #00f5c4;
    font-weight: 600;
}

/* Pill badge */
.aurora-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 14px;
    background: rgba(0,245,196,0.12);
    border: 1px solid rgba(0,245,196,0.30);
    border-radius: 9999px;
    font-size: clamp(0.65rem, 1vw, 0.75rem);
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #00f5c4;
}
```

---

## Layout

Centered single-column layout. No side panels. Content sits in centered cards over the full-bleed animated background.

```css
.aurora-slide {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: clamp(2rem, 5vw, 5rem);
    text-align: center;        /* title slides */
}

/* Content slides: left-aligned inside centered container */
.aurora-content {
    width: 100%;
    max-width: min(90vw, 800px);
    text-align: left;
}

/* Headline sizing */
.aurora-title {
    font-size: clamp(2.5rem, 7vw, 6rem);
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1.05;
    color: #ffffff;
}

.aurora-subtitle {
    font-size: clamp(1rem, 2vw, 1.4rem);
    color: rgba(255,255,255,0.70);
    margin-top: 1rem;
    line-height: 1.6;
}
```

---

## Named Layout Variations

### 1. Aurora Hero (全屏宣告)

Full-bleed animated aurora background. Centered white headline in Space Grotesk, `clamp(2.5rem, 7vw, 6rem)`, weight 700, negative letter-spacing. Subtitle in `rgba(255,255,255,0.70)`. Optional accent line `.aurora-divider` below. No card on hero — text sits directly on gradient.

```html
<section class="slide aurora-slide">
    <h1 class="aurora-title">Big Statement</h1>
    <p class="aurora-subtitle">Supporting line</p>
</section>
```

### 2. Aurora Card (功能亮点)

Centered frosted glass card on animated background. Card uses `backdrop-filter: blur(12px)`, `rgba(255,255,255,0.05)` background, `1px solid rgba(255,255,255,0.10)` border, `16px` border-radius. Content inside: title, body, optional badge.

```html
<section class="slide aurora-slide">
    <div class="aurora-content">
        <div class="aurora-card">
            <h2>Feature Name</h2>
            <p>1-2 line description</p>
            <span class="aurora-badge">Badge</span>
        </div>
    </div>
</section>
```

### 3. Aurora Stat (大数字强调)

Large gradient text number centered on slide. Use `-webkit-background-clip: text` with aurora gradient for hero numbers. Label below in muted text. Optional vertical divider.

```html
<section class="slide aurora-slide">
    <div class="aurora-stat" style="-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-image:linear-gradient(135deg,#00f5c4,#00b4ff);font-size:clamp(3rem,10vw,8rem);font-weight:700;">97%</div>
    <p class="aurora-subtitle">Metric label</p>
</section>
```

### 4. Aurora Split (分屏对比)

Two frosted glass cards side by side on animated background. `display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;`. Each card has its own content. Left panel = View A, right panel = View B.

```html
<section class="slide aurora-slide">
    <div class="aurora-content" style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;">
        <div class="aurora-card"><h3>View A</h3><p>Content</p></div>
        <div class="aurora-card"><h3>View B</h3><p>Content</p></div>
    </div>
</section>
```

### 5. Aurora Trio (多选项对比)

Three glass cards in a row. `grid-template-columns: repeat(3, 1fr)`. Active card has stronger border: `border-color: rgba(0,245,196,0.40)` and slightly more opaque background: `rgba(255,255,255,0.08)`. Each card: number + name + descriptor.

```html
<section class="slide aurora-slide">
    <div class="aurora-content" style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;">
        <div class="aurora-card active">01 Active</div>
        <div class="aurora-card">02 Option</div>
        <div class="aurora-card">03 Option</div>
    </div>
</section>
```

### 6. Aurora Timeline (流程步骤)

Horizontal step sequence with frosted glass cards as step markers. Active step: full accent border. Completed: outlined. Future: lower opacity. Track line: `2px solid rgba(0,245,196,0.3)`. Arrows between steps in accent color.

---

## Signature Elements

### CSS Overlays
- `body`: Mesh gradient 背景 — 3-4 个 `radial-gradient` 椭圆叠加，色标包括 `rgba(120,40,200,0.40)` / `rgba(0,180,255,0.30)` / `rgba(0,255,180,0.20)`，`background-size: 200% 200%`

### Animations
- `@keyframes auroraDrift`: 极光漂移 — `0% { background-position: 0% 50%; } 50% { background-position: 100% 20%; } 100% { background-position: 50% 100%; }`，`20s ease-in-out infinite alternate`，应用于 `body`

### Required CSS Classes
- `.aurora-card`: 毛玻璃卡片 — `background: rgba(255,255,255,0.05); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid var(--card-border); border-radius: 16px; padding: clamp(20px, 3vw, 36px)`
- `.aurora-slide`: 极光幻灯片容器 — `display: flex; flex-direction: column; align-items: center; justify-content: center; padding: clamp(2rem, 5vw, 5rem)`
- `.aurora-content`: 内容容器 — `width: 100%; max-width: min(90vw, 800px)`
- `.aurora-title`: 标题 — `font-size: clamp(2.5rem, 7vw, 6rem); font-weight: 700; letter-spacing: -0.03em; color: #ffffff`
- `.aurora-subtitle`: 副标题 — `font-size: clamp(1rem, 2vw, 1.4rem); color: rgba(255,255,255,0.70)`
- `.aurora-divider`: 分隔线 — `height: 1px; background: rgba(0,245,196,0.3); border: none; margin: 16px 0`
- `.aurora-accent` / `.aurora-emphasis`: 强调文字 — `color: #00f5c4; font-weight: 500/600`
- `.aurora-badge`: 徽章 — `display: inline-flex; padding: 4px 14px; background: rgba(0,245,196,0.12); border: 1px solid rgba(0,245,196,0.30); border-radius: 9999px; color: #00f5c4; font-size: clamp(0.65rem, 1vw, 0.75rem); text-transform: uppercase; letter-spacing: 0.12em`
- `.pill`: 同 `.aurora-badge` 的别名
- `.aurora-stat`: 渐变数字 — 使用 `-webkit-background-clip: text; -webkit-text-fill-color: transparent; background-image: linear-gradient(135deg, #00f5c4, #00b4ff)`
- `.reveal`: 淡入动画 — `opacity: 0; transform: translateY(20px); transition: opacity 0.7s cubic-bezier(0.16,1,0.3,1), transform 0.7s cubic-bezier(0.16,1,0.3,1)`

### Allowed Components
- Audit coverage: .app

### Background Rule
`.slide` 不设 `background`，完全透出 `body` 上的 mesh gradient。`body` 使用 `background-color: #0a0a1a` + 多层 `radial-gradient` + `auroraDrift` 动画。所有幻灯片共享同一动态背景。

### Style-Specific Rules
- 卡片必须使用 `backdrop-filter: blur(12px)` 实现毛玻璃效果
- 不使用 Google Fonts 以外的字体（标题用 Space Grotesk，正文用 DM Sans）
- 强调色 `#00f5c4`（青绿）用于徽章、分隔线、数字
- 所有变体均为深色背景，不使用白色背景
- 卡片 `border-radius: 16px`，边框 `1px solid rgba(255,255,255,0.10)`
- 英雄页（hero）文字直接放在渐变上，不用卡片包裹
- 激活卡片使用更强边框 `border-color: rgba(0,245,196,0.40)` + 更高不透明度背景 `rgba(255,255,255,0.08)`

### Signature Checklist
- [ ] body mesh gradient（3-4 个 radial-gradient，可见色彩混合）
- [ ] @keyframes auroraDrift（20s 循环，可见运动）
- [ ] .aurora-card 毛玻璃卡片（backdrop-filter: blur(12px)）
- [ ] .aurora-slide 居中容器
- [ ] .aurora-title 白色大标题（letter-spacing: -0.03em）
- [ ] .aurora-badge 青绿徽章（rgba(0,245,196,0.12) 背景）
- [ ] .aurora-divider 青绿分隔线
- [ ] .aurora-stat 渐变文字数字（background-clip: text）
- [ ] 青绿色 #00f5c4 至少一处使用
- [ ] 无白色背景变体
- [ ] reveal 动画使用 cubic-bezier(0.16,1,0.3,1)

---

## Components

```css
/* Light glassmorphism card */
.aurora-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: clamp(16px, 2.5vw, 24px);
}

/* Accent divider line */
.aurora-divider {
    height: 1px;
    background: rgba(0,245,196,0.3);
    border: none;
    margin: 16px 0;
}

/* Emphasis text */
.aurora-emphasis {
    color: #00f5c4;
    font-weight: 500;
}
```

---

## Animation

```css
/* Entrance: elements fade+rise with stagger */
.reveal {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.7s cubic-bezier(0.16,1,0.3,1),
                transform 0.7s cubic-bezier(0.16,1,0.3,1);
}
.slide.visible .reveal { opacity: 1; transform: translateY(0); }
.reveal:nth-child(1) { transition-delay: 0.05s; }
.reveal:nth-child(2) { transition-delay: 0.15s; }
.reveal:nth-child(3) { transition-delay: 0.25s; }
.reveal:nth-child(4) { transition-delay: 0.35s; }
```

---

## Style Preview Checklist

When generating a preview for style selection, the preview MUST show:
- [ ] Animated aurora gradient background (visible motion within 3 seconds)
- [ ] Cyan-green `#00f5c4` accent on at least one element
- [ ] Subtle card with `backdrop-filter: blur(12px)`
- [ ] White headline with `letter-spacing: -0.02em`

---

## Best For

Product launches · VC pitch decks · SaaS marketing · AI / tech trend reports · Anything that should feel "Linear / Vercel-level" polished
