# Neo-Brutalism — Style Reference

Bold, uncompromising, anti-aesthetic. Hard edges, offset shadows, zero apology. Inspired by Gumroad's 2022 rebrand and indie developer culture.

---

## Colors

Choose one background per presentation — commit to it:

```css
:root {
    /* Option A: Yellow (most iconic neo-brutal) */
    --bg: #FFEB3B;

    /* Option B: Orange-red (aggressive) */
    --bg: #FF5733;

    /* Option C: Mint (softer but still brutal) */
    --bg: #E8F5E9;

    /* Option D: White (clean brutalism) */
    --bg: #FAFAFA;

    /* Always black text, no exceptions */
    --text: #000000;

    /* Inverse accent (for buttons, badges) */
    --btn-bg: #000000;
    --btn-text: #FFEB3B;   /* or var(--bg) */
}
```

---

## Background

```css
body {
    background-color: var(--bg);
    font-family: "Space Grotesk", "Barlow Condensed", -apple-system, sans-serif;
}

/* Optional: subtle dot pattern for structure */
body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: radial-gradient(circle, rgba(0,0,0,0.08) 1px, transparent 1px);
    background-size: 12px 12px;
    pointer-events: none;
    z-index: 0;
}
```

---

## Signature Brutalist Effects

```css
/* The core brutalist card — hard shadow, zero radius */
.brute-card {
    background: #ffffff;
    border: 3px solid #000000;
    border-radius: 0;
    box-shadow: 4px 4px 0 #000000;
    padding: clamp(1rem, 2vw, 1.5rem);
}

/* On hover/focus: shadow shrinks, element shifts */
.brute-card:hover {
    transform: translate(2px, 2px);
    box-shadow: 2px 2px 0 #000000;
    transition: none;   /* instant — no easing in brutalism */
}

/* Stripe decoration (hatching) */
.brute-stripe {
    background: repeating-linear-gradient(
        -45deg,
        #000000 0px,
        #000000 2px,
        transparent 2px,
        transparent 10px
    );
    opacity: 0.15;
}

/* Slight rotation for handmade feel — apply sparingly */
.brute-rotated { transform: rotate(-1.5deg); }
.brute-rotated-right { transform: rotate(1deg); }

/* Button / badge */
.brute-btn {
    display: inline-block;
    background: #000000;
    color: #FFEB3B;   /* or var(--bg) */
    border: 3px solid #000000;
    border-radius: 0;
    box-shadow: 3px 3px 0 #000000;
    padding: 10px 20px;
    font-weight: 800;
    font-size: clamp(0.8rem, 1.2vw, 1rem);
    letter-spacing: 0.02em;
    cursor: pointer;
    text-transform: uppercase;
}

/* Tag / label */
.brute-tag {
    display: inline-block;
    background: #000000;
    color: var(--bg, #FFEB3B);
    border: 2px solid #000000;
    border-radius: 0;
    padding: 2px 8px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
```

---

## Components

```css
/* Core brutalist card */
.brute-card {
    background: #ffffff;
    border: 3px solid #000000;
    border-radius: 0;
    box-shadow: 4px 4px 0 #000000;
    padding: clamp(1rem, 2vw, 1.5rem);
}
.brute-card:hover {
    box-shadow: 2px 2px 0 #000000;
    transform: translate(2px, 2px);
    transition: none;
}

/* Brutalist button */
.brute-btn {
    background: #000000;
    color: var(--bg);
    border: 3px solid #000000;
    border-radius: 0;
    box-shadow: 3px 3px 0 #000000;
    padding: 10px 20px;
    font-weight: 800;
    text-transform: uppercase;
    cursor: pointer;
}

/* Stripe fill decoration */
.brute-stripe {
    background: repeating-linear-gradient(
        -45deg, #000 0px, #000 2px, transparent 2px, transparent 10px
    );
}

/* Hand-drawn style arrow */
.brute-arrow {
    display: inline-block;
}
.brute-arrow svg {
    stroke: #000;
    stroke-width: 3;
    stroke-linecap: square;
}
```

---

## Typography

```css
body {
    font-family: "Space Grotesk", "Plus Jakarta Sans", "PingFang SC",
                 "Noto Sans CJK SC", system-ui, sans-serif;
    background: var(--bg);
    color: #000000;
}

/* Display headline — very large, often uppercase */
.brute-title {
    font-size: clamp(3rem, 10vw, 9rem);
    font-weight: 900;
    line-height: 0.95;
    letter-spacing: -0.02em;
    text-transform: uppercase;
    color: #000000;
}

/* Section heading */
.brute-h2 {
    font-size: clamp(1.5rem, 4vw, 3.5rem);
    font-weight: 800;
    line-height: 1.05;
    color: #000000;
}

/* Body */
.brute-body {
    font-size: clamp(0.9rem, 1.5vw, 1.1rem);
    font-weight: 500;
    line-height: 1.5;
    color: #000000;
}
```

---

## Layout

```css
.brute-slide {
    background: var(--bg);
    padding: clamp(2rem, 4vw, 4rem);
    display: flex;
    flex-direction: column;
    justify-content: flex-end;  /* bottom-anchored like editorial */
    position: relative;
    overflow: hidden;
}

/* Numbered list */
.brute-list { list-style: none; display: flex; flex-direction: column; gap: 0; }
.brute-list li {
    border-top: 2px solid #000;
    padding: 0.75rem 0;
    display: grid;
    grid-template-columns: 2.5rem 1fr;
    gap: 0.75rem;
    align-items: start;
}
.brute-list li:last-child { border-bottom: 2px solid #000; }
.brute-list .num {
    font-size: 0.75rem;
    font-weight: 800;
    padding-top: 0.15em;
}
```

---

## Arrow Decoration (SVG, inline)

```html
<!-- Simple hand-drawn style arrow pointing right -->
<svg width="60" height="24" viewBox="0 0 60 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M0 12 H52 M40 4 L52 12 L40 20" stroke="#000" stroke-width="3" stroke-linecap="square"/>
</svg>
```

---

## Named Layout Variations

### 1. Brute Hero (全屏宣告)

Bold background color (yellow `#FFEB3B` / orange-red `#FF5733` / mint `#E8F5E9`). Headline in Space Grotesk 900, `clamp(3rem, 10vw, 9rem)`, uppercase, `#000000`. Bottom-anchored layout (`.brute-slide` uses `justify-content: flex-end`). Optional `.brute-tag` badge. Dot pattern `body::before` visible.

```html
<section class="slide brute-slide">
    <h1 class="brute-title">BIG STATEMENT</h1>
    <span class="brute-tag">Tagline</span>
</section>
```

### 2. Brute Split (分栏证据)

Two-column grid. Left: section number + headline. Right: `.brute-list` with hard-bordered rows (`.brute-list li { border-top: 2px solid #000; }`). Each list item: number + bold lead word + description. No divider — content density creates the split.

### 3. Brute Cards (多选项对比/双列功能卡)

2-3 `.brute-card` elements in a row. Each card: `background: #fff`, `border: 3px solid #000`, `border-radius: 0`, `box-shadow: 4px 4px 0 #000`. Active card: full black background with yellow text (`.brute-btn` style). Hover: `transform: translate(2px, 2px)`, shadow shrinks — instant, no easing.

### 4. Brute Stat (大数字强调)

Large black number in Space Grotesk 900, `clamp(3rem, 10vw, 9rem)`. Label in `.brute-tag` (black bg, yellow text). All text `#000000`. Optional `.brute-stripe` decoration at 15% opacity behind the number.

### 5. Brute CTA (堆叠行动)

Stacked `.editorial-cta-box` style blocks but brutalist: black border `3px solid #000`, `border-radius: 0`, `box-shadow: 4px 4px 0 #000`. Each block: number + command text. `.brute-btn` for action buttons. All transitions instant — `transition: none`.

---

## Signature Elements

### CSS Overlays
- `.stripe`: 斜线 hatch 装饰 — `background: repeating-linear-gradient(-45deg, #000 0, #000 2px, transparent 2px, transparent 10px); opacity: 0.12; position: absolute; pointer-events: none`

### Animations
- `@keyframes fadeIn`: 淡入 — `from { opacity: 0; } to { opacity: 1; }`
- `.reveal`: 入场动画 — `opacity: 0;`；`.slide.visible .reveal { animation: fadeIn 0.25s ease forwards; }`
- Stagger delays: `.slide.visible .reveal:nth-child(1-8)` — `0.04s` 递增
- 无缓动：brutalism 是即时的，`transition: none`

### Required CSS Classes
- `.brute-card`: 核心卡片 — `background: white; border: 3px solid #000; border-radius: 0; box-shadow: 4px 4px 0 #000`
- `.brute-btn`: 按钮 — `background: #000; color: var(--bg); border: 3px solid #000; border-radius: 0; box-shadow: 3px 3px 0 #000; font-weight: 900; text-transform: uppercase`
- `.brute-tag`: 标签 — `background: #000; color: var(--bg); border: 2px solid #000; border-radius: 0; font-size: 0.75rem; text-transform: uppercase`
- `.eyebrow`: 章节标识 — `font-weight: 800; letter-spacing: 0.2em; text-transform: uppercase; border-left: 4px solid #000; padding-left: 0.8rem`
- `.heavy-rule`: 粗横线 — `border-top: 3px solid #000`
- `.rotated`: 微旋转 — `transform: rotate(-1.5deg)`（手工感）
- `.code-block`: 代码块 — `background: #000; color: #FFEB3B; font-family: 'Courier New'; border: 3px solid #000; box-shadow: 4px 4px 0 #000`
- `.cta-cmd`: 行动号召 — `font-weight: 900; background: #000; color: #FFEB3B; box-shadow: 6px 6px 0 rgba(0,0,0,0.3)`
- `.preset-tag`: 预设标签 — `border: 2px solid #000; background: #fff; box-shadow: 2px 2px 0 #000`；当前项反转 `background: #000; color: #FFEB3B`
- `.dot`: 导航点 — 黑色方块（`border-radius: 0`），激活时高度变 20px

### Allowed Components
- Audit coverage: .brute-arrow .brute-body .brute-h2 .brute-list .brute-rotated .brute-rotated-right .brute-slide .brute-stripe
- Audit coverage cont.: .brute-title .num

### Background Rule
`.slide` 设置背景为 `#FFEB3B`（黄色，最经典）。也可选 `#FF5733`（橙红）、`#E8F5E9`（薄荷）、`#FAFAFA`（纯白）。不使用渐变，纯色块。

### Style-Specific Rules
- 所有容器：`box-shadow: 4px 4px 0 #000` 硬偏移阴影，无模糊
- `border-radius: 0` 永远是锐角，从不圆角
- `border: 3px solid #000` 最小粗黑边框
- 高对比色块：每张幻灯片一个大胆的纯色背景
- 文字始终 `#000000`，无例外
- 悬停效果：`transform: translate(2px, 2px); box-shadow: 2px 2px 0 #000`——即时，无缓动
- 可选微旋转（`.rotated` `-1.5deg`）营造手工感
- 禁止：渐变、柔和阴影、圆角、微妙边框

### Signature Checklist
- [ ] 高饱和度纯色背景（黄色/橙色/薄荷）
- [ ] `3px solid #000` 边框 + `4px 4px 0 #000` 阴影至少出现在一张卡片上
- [ ] 标题 900 weight，超大字号，UPPERCASE
- [ ] 所有文字 `#000000`——无例外
- [ ] 结构元素零圆角
- [ ] 悬停效果即时，无缓动

---

## Animation

```css
/* No transitions. No easing. Brutalism is instant. */
/* Only exception: entrance reveal (subtle) */
.reveal {
    opacity: 0;
    transition: opacity 0.2s linear;
}
.slide.visible .reveal { opacity: 1; }
.reveal:nth-child(1) { transition-delay: 0.0s; }
.reveal:nth-child(2) { transition-delay: 0.05s; }
.reveal:nth-child(3) { transition-delay: 0.10s; }
```

---

## Style Preview Checklist

- [ ] High-saturation solid background (yellow / orange / mint)
- [ ] `3px solid #000` border + `4px 4px 0 #000` shadow visible on at least one card
- [ ] Headline at 900 weight, very large, uppercase
- [ ] All text is `#000000` — no exceptions
- [ ] Zero border-radius on structural elements

---

## Best For

Hackathon presentations · Indie product launches · Design manifestos · Creative agency pitches · Anti-corporate brand statements · Developer conference talks
