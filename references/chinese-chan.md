# Chinese Chan — Style Reference

Still, focused, contemplative. Inspired by Chinese ink painting (水墨画), Huizhou architecture (徽州建筑), and the Chan Buddhist aesthetic of emptiness (虚空, xū kōng). Negative space is the primary design element.

---

## Colors

```css
/* Light variant — warm paper white */
:root {
    --bg:           #FAFAF8;
    --text:         #1a1a18;   /* warm ink, not pure black */
    --text-muted:   #6b6b68;
    --accent:       #C41E3A;   /* vermilion — use ONCE per slide, maximum */
    --accent-alt:   #1B3A6B;   /* indigo — alternative accent */
    --rule:         rgba(26,26,24,0.15);
}

/* Dark variant — warm ink black */
:root.zen-dark {
    --bg:           #1a1a18;
    --text:         #f0ede8;
    --text-muted:   #9a9790;
    --rule:         rgba(240,237,232,0.15);
}
```

**Forbidden:** gradients, multiple accent colors, high-saturation color blocks, decorative borders, drop shadows.

---

## Background

```css
body {
    background-color: var(--bg);
    font-family: "Noto Serif CJK SC", "Source Han Serif SC", "STSong", "SimSun", Georgia, serif;
}

/* Optional: subtle ink wash texture */
body::before {
    content: '';
    position: fixed;
    inset: 0;
    background: radial-gradient(ellipse at 30% 20%, rgba(26,26,24,0.03) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}
```

## Components

```css
/* Narrow content container */
.zen-content {
    max-width: 600px;
    margin: 0 auto;
    padding: 0 clamp(24px, 6vw, 60px);
}

/* Thin horizontal rule */
.zen-rule {
    height: 1px;
    background: var(--rule);
    border: none;
    margin: clamp(32px, 5vw, 80px) 0;
}

/* Ghost kanji background texture */
.zen-kanji {
    position: absolute;
    font-size: clamp(8rem, 20vw, 16rem);
    opacity: 0.06;
    pointer-events: none;
    user-select: none;
    font-family: "Noto Serif CJK SC", serif;
}

/* Accent emphasis (single use) */
.zen-accent {
    color: var(--accent);
    font-weight: 700;
}
```

---

## Typography

```css
/* Chinese — Noto Serif CJK SC preferred, graceful serif fallback */
.zen-cn {
    font-family: "Noto Serif CJK SC", "Source Han Serif SC",
                 "STSong", "SimSun", Georgia, serif;
    font-feature-settings: "palt";   /* CJK punctuation compression */
    font-weight: 300;
    line-height: 1.9;
    letter-spacing: 0.05em;
}

/* English — EB Garamond or Crimson Text */
.zen-en {
    font-family: "EB Garamond", "Crimson Text", Georgia, serif;
    font-weight: 400;
    line-height: 1.85;
}

/* Title — slightly heavier but still restrained */
.zen-title {
    font-size: clamp(1.8rem, 5vw, 4rem);
    font-weight: 400;   /* never bold */
    letter-spacing: 0.08em;
    line-height: 1.3;
    color: var(--text);
}

/* Body */
.zen-body {
    font-size: clamp(0.9rem, 1.6vw, 1.15rem);
    font-weight: 300;
    line-height: 1.9;
    color: var(--text);
}

/* Accent word — accent color, nothing else changes */
.zen-accent { color: var(--accent); }

/* Caption / label */
.zen-caption {
    font-size: clamp(0.65rem, 1vw, 0.8rem);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-muted);
}
```

---

## Layout — Ma (間) Philosophy

```css
.zen-slide {
    background: var(--bg);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: clamp(3rem, 8vw, 8rem) clamp(2rem, 6vw, 6rem);
}

/* Narrow content column — max 600px regardless of screen width */
.zen-content {
    width: 100%;
    max-width: 600px;
}

/* Generous top margin above every heading */
.zen-heading {
    margin-top: clamp(60px, 8vh, 100px);
}

/* Paragraph spacing */
.zen-body + .zen-body {
    margin-top: 40px;
}
```

---

## Decorative Elements (max 1 per slide)

```css
/* 1. Thin horizontal rule with flanking dots */
.zen-rule {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: clamp(1.5rem, 3vh, 2.5rem) 0;
}
.zen-rule::before,
.zen-rule::after {
    content: '';
    width: 4px; height: 4px;
    border-radius: 50%;
    background: var(--rule);
    flex-shrink: 0;
}
.zen-rule-line {
    flex: 1;
    height: 1px;
    background: var(--rule);
}

/* 2. Ghost kanji background character */
.zen-ghost-kanji {
    position: absolute;
    font-size: clamp(120px, 25vw, 240px);
    font-weight: 900;
    color: var(--text);
    opacity: 0.06;
    pointer-events: none;
    user-select: none;
    font-family: "Noto Serif CJK SC", "STSong", serif;
    line-height: 1;
    /* Position off-center for asymmetric composition */
    right: -0.1em;
    bottom: -0.1em;
}

/* 3. Single vertical line */
.zen-vline {
    width: 1px;
    height: clamp(40px, 8vh, 80px);
    background: var(--rule);
    margin: 0 auto;
}
```

---

## Vertical Title (optional variant)

```css
/* Writing mode vertical — for title slides */
.zen-vertical-title {
    writing-mode: vertical-rl;
    text-orientation: mixed;
    font-size: clamp(2rem, 6vw, 5rem);
    font-weight: 400;
    letter-spacing: 0.15em;
    line-height: 1.2;
    color: var(--text);
}
```

---

## Named Layout Variations

### 1. Zen Center (全屏宣告)

Narrow column centered vertically. Title in Noto Serif CJK SC, `clamp(1.8rem, 5vw, 4rem)`, weight 400 (never bold). Subtitle in `.zen-body` below. Maximum ONE decorative element: `.zen-rule` (horizontal rule with dots) OR `.zen-ghost-kanji` OR `.zen-dot`. 50%+ empty space required.

```html
<section class="slide">
    <div class="zen-content zen-center">
        <h1 class="zen-title zen-cn">Title</h1>
        <p class="zen-body zen-cn">Subtitle</p>
        <div class="zen-rule">
            <span class="zen-rule-line"></span>
        </div>
    </div>
</section>
```

### 2. Zen Split (分栏证据)

Single column, vertical flow. Section label in `.zen-caption` (small, uppercase, muted). Headline in `.zen-title`. Divider `.zen-rule`. Body text or numbered list below. No side-by-side panels — everything flows vertically.

```html
<section class="slide">
    <div class="zen-content">
        <span class="zen-caption">Section 01</span>
        <h2 class="zen-title zen-cn">Headline</h2>
        <div class="zen-rule"><span class="zen-rule-line"></span></div>
        <ol class="zen-list">
            <li>Point one</li>
            <li>Point two</li>
            <li>Point three</li>
        </ol>
    </div>
</section>
```

### 3. Zen Vertical (竖排标题 — optional)

Vertical writing mode for title slides. `writing-mode: vertical-rl`. Title runs top-to-bottom, right-to-left. Used for hero covers or philosophical statements. No other content except maybe a small seal (`.zen-accent` small square in vermilion `#C41E3A`).

```html
<section class="slide">
    <div class="zen-vertical-title zen-cn">竖排标题</div>
    <div class="zen-seal" style="width:12px;height:12px;background:#C41E3A;border-radius:2px;position:absolute;bottom:20%;left:15%;"></div>
</section>
```

---

## Signature Elements

### CSS Overlays
- `body::before`: 水墨纹理 — `radial-gradient(ellipse at 30% 20%, rgba(26,26,24,0.03) 0%, transparent 70%)`，`position: fixed; inset: 0; pointer-events: none; z-index: 0`（可选）

### Animations
- `@keyframes zenFadeIn`: 淡入 — `from { opacity: 0; } to { opacity: 1; }`，配合 `.slide.visible .reveal` 使用长间隔 staggered delays (0.1s, 0.3s, 0.5s, 0.7s, 0.9s, 1.1s, 1.3s)，仅透明度变化，无位移

### Required CSS Classes
- `.ghost-kanji`: 幽灵汉字底纹 — `position: absolute; font-family: 'Noto Serif SC', serif; font-weight: 900; font-size: clamp(120px, 25vw, 200px); opacity: 0.05; color: #1a1a18; pointer-events: none; user-select: none; line-height: 1`；必须放在 `.slide` 直接子元素位置
- `.flanked-rule`: 带点分隔线 — `display: flex; align-items: center; gap: 12px`；`.flanked-rule::before` / `.flanked-rule::after` 为 5px 圆点 `rgba(26,26,24,0.2)`；内部 `hr` 为 `1px solid rgba(26,26,24,0.12)`
- `.vline`: 垂直线 — `width: 1px; height: 60px; background: rgba(26,26,24,0.15)`
- `.col`: 内容列 — `max-width: min(90vw, 580px); padding: 0 clamp(24px, 6vw, 60px)`
- `.eyebrow`: 小标签 — `font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase; color: var(--text-muted)`
- `.accent`: 强调色 — `color: var(--accent)`（朱红 `#C41E3A`）

### Background Rule
`.slide` 必须设置 `background: #FAFAF8`。body 为暖白纸色，可选 `body::before` 水墨纹理叠加。不使用渐变。

### Style-Specific Rules
- `.ghost-kanji` 必须作为 `.slide` 的直接子元素，使用 `position: absolute` 定位在页面边角（如 `right: -0.1em; bottom: -0.15em` 或 `left: -0.05em; top: 0.1em`）
- 每页最多一个装饰元素：`.ghost-kanji` 或 `.flanked-rule` 或 `.vline`，不得同时使用多个
- 内容列最大宽度 580px，极端水平留白
- 标题权重 400，永远不使用 bold
- 行高 ≥ 1.8（中文）/ 1.85（英文）
- 使用 Noto Serif CJK SC + EB Garamond 字体组合
- `font-feature-settings: "palt"` 用于中文标点压缩
- 朱红 `#C41E3A` 每页最多使用一次（单个字或小方块）

### Signature Checklist
- [ ] body::before 水墨纹理（可选，3% 不透明度）
- [ ] @keyframes zenFadeIn（纯淡入，长间隔 staggered）
- [ ] .ghost-kanji 幽灵汉字（absolute, 25vw, opacity 0.05）
- [ ] .ghost-kanji 定位在 .slide 边角（right/bottom 或 left/top 负偏移）
- [ ] .flanked-rule 带点分隔线（5px 圆点 + 1px 线）
- [ ] .vline 垂直线（60px, opacity 0.15）
- [ ] .col 窄内容列（max-width 580px）
- [ ] .accent 朱红强调（#C41E3A, 每页最多一次）
- [ ] 50%+ 空白区域
- [ ] 标题 weight 400（非 bold）
- [ ] 行高 ≥ 1.8
- [ ] font-feature-settings: "palt"

---

## Animation

```css
/* Slow, gentle opacity fade — no movement */
.reveal {
    opacity: 0;
    transition: opacity 0.8s ease;
}
.slide.visible .reveal { opacity: 1; }
.reveal:nth-child(1) { transition-delay: 0.1s; }
.reveal:nth-child(2) { transition-delay: 0.3s; }
.reveal:nth-child(3) { transition-delay: 0.5s; }
.reveal:nth-child(4) { transition-delay: 0.7s; }
```

---

## Chinese Font Loading

```html
<!-- Noto Serif CJK SC via Google Fonts (preconnect first) -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400&display=swap" rel="stylesheet">
```

---

## Style Preview Checklist

- [ ] Warm cream `#FAFAF8` or ink `#1a1a18` background — no color other than accent
- [ ] Content column clearly narrow (max 600px, lots of horizontal breathing room)
- [ ] Line height ≥ 1.8 visible in body text
- [ ] Maximum ONE decorative element (rule, ghost kanji, or dot)
- [ ] Accent color used on ONE word or element only

---

## Best For

Brand philosophy presentations · Design thinking talks · Cultural storytelling · Product principle documents · East Asian audience contexts · Any talk where silence communicates as much as words
