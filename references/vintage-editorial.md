# Vintage Editorial — Style Reference

Witty, confident, editorial, personality-driven. Cream background with abstract geometric accents.

---

## Colors

```css
:root {
    --bg-cream: #f5f3ee;
    --text-primary: #1a1a1a;
    --text-secondary: #555;
    --accent-warm: #e8d4c0;
}
```

---

## Background

```css
body {
    background: var(--bg-cream);
    font-family: "Fraunces", "Work Sans", -apple-system, sans-serif;
}

/* Abstract geometric shapes — no illustrations */
.editorial-circle {
    position: absolute;
    border: 2px solid var(--text-primary);
    border-radius: 50%;
    opacity: 0.15;
    pointer-events: none;
}
.editorial-line {
    position: absolute;
    width: 1px;
    height: clamp(60px, 12vh, 120px);
    background: var(--text-primary);
    opacity: 0.12;
}
.editorial-dot {
    position: absolute;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--text-primary);
    opacity: 0.2;
}
```

---

## Typography

```css
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Work+Sans:wght@400;500&display=swap');

.editorial-title {
    font-family: "Fraunces", Georgia, serif;
    font-size: clamp(28px, 5.5vw, 56px);
    font-weight: 900;
    color: var(--text-primary);
    line-height: 1.05;
}

.editorial-body {
    font-family: "Work Sans", sans-serif;
    font-size: clamp(13px, 1.4vw, 16px);
    font-weight: 400;
    color: var(--text-primary);
    opacity: 0.7;
    line-height: 1.65;
}

.editorial-quote {
    font-family: "Fraunces", Georgia, serif;
    font-size: clamp(20px, 3vw, 32px);
    font-weight: 700;
    font-style: italic;
    color: var(--text-primary);
    line-height: 1.3;
}

.editorial-cta-box {
    border: 2px solid var(--text-primary);
    border-radius: 4px;
    padding: clamp(16px, 2.5vw, 24px);
    text-align: center;
}
```

---

## Components

```css
/* Abstract geometric circle */
.editorial-circle {
    position: absolute;
    border: 2px solid var(--text-primary);
    border-radius: 50%;
    opacity: 0.15;
    pointer-events: none;
}

/* Accent line */
.editorial-line {
    position: absolute;
    width: 1px;
    height: clamp(60px, 12vh, 120px);
    background: var(--text-primary);
    opacity: 0.12;
}

/* Dot accent */
.editorial-dot {
    position: absolute;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--text-primary);
    opacity: 0.2;
}

/* Bold bordered CTA box */
.editorial-cta-box {
    border: 2px solid var(--text-primary);
    border-radius: 4px;
    padding: clamp(16px, 2.5vw, 24px);
    text-align: center;
    background: var(--bg-cream);
}
```

---

## Named Layout Variations

### 1. Editorial Hero (全屏宣告)

Cream `#f5f3ee` background. Abstract geometric shapes: `.editorial-circle` (border outline, opacity 0.15), `.editorial-line` (1px vertical), `.editorial-dot` (6px circle). Headline in Fraunces 900, `clamp(28px, 5.5vw, 56px)`. Bottom or center anchored.

```html
<section class="slide">
    <div class="editorial-circle" style="width:200px;height:200px;top:10%;right:10%;"></div>
    <div class="editorial-line" style="bottom:20%;left:8%;"></div>
    <div class="editorial-dot" style="top:15%;left:15%;"></div>
    <div class="slide-content">
        <h1 class="editorial-title">Title</h1>
    </div>
</section>
```

### 2. Editorial Split (分栏证据)

Two columns. Left: section number + headline in Fraunces 900. Right: body text in Work Sans. Geometric shapes float in background at 15% opacity. Thin 1px rule between columns (optional).

### 3. Editorial Cards (功能亮点/双列功能卡)

2 cards side by side. Each card: `.editorial-cta-box` style (border `2px solid #1a1a1a`, `border-radius: 4px`, `padding: clamp(16px, 2.5vw, 24px)`). Feature name + description. Geometric dot or line decoration between cards.

### 4. Editorial Quote (功能亮点)

Full-width `.editorial-quote` in Fraunces 700 italic, `clamp(20px, 3vw, 32px)`. Attribution in `.editorial-body` muted. Circle outline decoration behind quote at 15% opacity.

### 5. Editorial CTA (堆叠行动)

Stacked `.editorial-cta-box` blocks. Each: `border: 2px solid #1a1a1a`, `border-radius: 4px`, centered text. Number + command text. Geometric shapes (circle + line + dot) as background decoration. Clean editorial close.

---

## Signature Elements

### CSS Overlays
- `.bordered-box::before`: 标签式卡片标题 — `content: attr(data-label); position: absolute; top: -12px; left: 16px; background: #f5f3ee; padding: 0 8px; font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #8b2635`

### Animations
- `@keyframes` 无独立命名动画，使用 `.reveal` + transition（opacity + translateX/translateY）staggered delays (0.08s, 0.16s, 0.24s...)
- `.slide-content-anim`: 标题侧滑 — `opacity: 0; transform: translateX(-30px); transition: opacity 0.6s ease, transform 0.6s ease`；`.slide.visible` 时归位
- `.fade-in`: 淡入 — `opacity: 0; transition: opacity 0.6s ease`，支持 `.delay-1/.delay-2/.delay-3`

### Required CSS Classes
- `.deco-circle`: 装饰圆 — `position: absolute; border: 2px solid var(--text-primary); border-radius: 50%; opacity: 0.15; pointer-events: none`
- `.deco-line`: 装饰线 — `position: absolute; width: 1px; height: clamp(60px, 12vh, 120px); background: var(--text-primary); opacity: 0.12`
- `.deco-dot`: 装饰点 — `position: absolute; width: 6px; height: 6px; border-radius: 50%; background: var(--text-primary); opacity: 0.2`
- `.bordered-box`: 带标签边框卡片 — `border: 2px solid #1a1a1a; border-radius: 4px; padding: clamp(16px, 2.5vw, 24px); position: relative`
- `.pain-row`: 痛点行 — `display: flex; gap: 0.8rem; opacity: 0; transform: translateX(-20px); transition: all 0.5s ease`
- `.step-editorial`: 步骤项 — `display: flex; gap: 0.8rem; align-items: flex-start; opacity: 0; transform: translateY(16px); transition: all 0.5s ease`
- `.feature-row`: 功能行 — `display: flex; align-items: center; justify-content: space-between; opacity: 0; transform: translateX(20px)`
- `.feature-name`: 功能名称 — `font-family: 'Fraunces', serif; font-weight: 700`
- `.feature-badge`: 功能标签 — `font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; background: #e8d4c0; color: #5a2a1a; padding: 3px 10px`
- `.slide-footer`: 页脚 — `padding: 12px clamp(32px, 6vw, 100px); display: flex; justify-content: space-between; border-top: 1px solid rgba(26,26,26,0.1)`

### Background Rule
`.slide` 必须设置 `background: #f5f3ee`。body 为纯米色，不使用渐变或纹理。装饰性几何图形通过 `.deco-circle`/`.deco-line`/`.deco-dot` 作为绝对定位元素叠加。

### Style-Specific Rules
- 装饰性元素仅限几何 CSS 形状（圆、线、点），不使用插图或 SVG
- 几何图形不透明度固定在 12-20% 范围内，不抢内容焦点
- 标题使用 Fraunces (700/900) + Work Sans (400/500) 字体组合
- 配色使用 `#8b2635` 作为次要强调色（标签、序号）
- 卡片边框 `2px solid #1a1a1a`，`border-radius: 4px`
- `.bordered-box` 使用 `data-label` 属性生成浮动标题

### Signature Checklist
- [ ] 米色背景 #f5f3ee
- [ ] 至少一个装饰性几何元素（circle/line/dot）
- [ ] .bordered-box 带 data-label 标题卡片
- [ ] .deco-circle 圆形装饰（2px outline, opacity 0.15）
- [ ] .deco-line 线条装饰（1px, opacity 0.12）
- [ ] .deco-dot 点装饰（6px, opacity 0.2）
- [ ] .pain-row 痛点行（侧滑 staggered 动画）
- [ ] .step-editorial 步骤项（上移 staggered 动画）
- [ ] .feature-row 功能行（右移 staggered 动画）
- [ ] .feature-badge 功能标签（#e8d4c0 背景）
- [ ] .slide-footer 页脚（brand + 页码）
- [ ] 无插图，纯 CSS 几何形状
- [ ] slide-content-anim 标题侧滑动画（标题页）

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

- [ ] Cream background `#f5f3ee`
- [ ] Fraunces serif at 900 weight for headlines
- [ ] At least one geometric shape (circle/line/dot)
- [ ] Bold bordered CTA boxes present
- [ ] No illustrations — only CSS shapes

---

## Best For

Personal brands · Thought leadership · Creative agency pitches · Witty presentations · Editorial content · Brand storytelling
