# Modern Newspaper — Style Reference

Authoritative, punchy, "smart & pop" — Japan's new economy business media meets Swiss editorial design. Information feels curated and consequential, not decorative.

---

## Colors

```css
:root {
    --bg: #f7f5f0;           /* aged newsprint white */
    --bg-dark: #111111;      /* sumi black */
    --text: #111111;
    --text-muted: #555555;
    --yellow: #FFCC00;       /* electric yellow — accent only */
    --red: #FF3333;          /* alert red — sparingly */
    --rule: #111111;         /* column rules */
}
```

---

## Background

```css
body {
    background: var(--bg);
    font-family: 'Oswald', 'Source Serif 4', -apple-system, sans-serif;
}
```

---

## Typography

```css
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400&display=swap');

.np-headline {
    font-family: 'Oswald', 'Arial Narrow', sans-serif;
    font-size: clamp(3.5rem, 11vw, 8rem);
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: -0.02em;
    line-height: 0.95;
    color: var(--text);
}

.np-subhead {
    font-family: 'Oswald', sans-serif;
    font-size: clamp(1rem, 2.5vw, 1.8rem);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.np-body {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: clamp(0.65rem, 1vw, 0.85rem);
    line-height: 1.65;
    color: var(--text-muted);
    max-width: 38ch;
}

.np-stamp {
    font-family: 'IBM Plex Mono', monospace;
    font-size: clamp(0.55rem, 0.8vw, 0.7rem);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
}

.np-red { color: var(--red); }

.np-dark {
    background: var(--bg-dark);
    color: #f7f5f0;
}
.np-dark .np-body { color: rgba(247,245,240,0.6); }
```

---

## Components

```css
/* Yellow accent bar */
.np-bar-h {
    width: 100%;
    height: 10px;
    background: var(--yellow);
}
.np-bar-v {
    width: 8px;
    height: 100%;
    background: var(--yellow);
    flex-shrink: 0;
}

/* Column rule */
.np-rule {
    width: 1px;
    background: var(--rule);
    align-self: stretch;
    margin: 0 clamp(16px, 2.5vw, 40px);
}

/* 12-column grid base */
.np-grid {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: 0 clamp(8px, 1.5vw, 24px);
    height: 100%;
    padding: clamp(24px, 4vw, 64px);
}
```

---

## Named Layout Variations

### 1. Cover / Masthead

Publication name top-left (small, mono), yellow horizontal bar beneath it. Off-center headline fills 40% of slide bottom-left (2–5 words). Date and issue number top-right. Subtitle 3 lines max, bottom-right corner, 8px body. Large empty zone upper-right.

### 2. Breaking Headline

One-sentence headline in 9rem Oswald occupies top 45% of slide. Yellow 10px bar separates it from evidence zone below. Below bar: two columns — left is 4–5 line body, right is one bold statistic in 3rem + 1-line label. Nothing else.

### 3. Split Column

Vertical column rule divides slide 40/60. Left 40%: black panel, yellow bar on left edge, white headline in Oswald. Right 60%: newsprint background, body text in 3 short paragraphs, mono label top-right.

### 4. Data Brief

One number dominates center-left at 8–10rem, colored `var(--yellow)` outline text (webkit-text-stroke: 3px #111, fill transparent) or solid black. Below it: 1-line label in mono. Right side: 4-bullet context list in 0.75rem body. Massive negative space top and right.

### 5. Feature Story (Asymmetric)

Headline anchors bottom-left (4rem, 3 lines max). Upper-left: yellow bar 8px + section label. Body text column bottom-right (3 short paras). Upper-right 40% of slide: completely empty. Creates cinematic tension.

### 6. Contents / Index

4–6 numbered items in two columns. Each item: `01` in 2rem Oswald yellow, em-dash, topic in 1.2rem Oswald black, 1-line descriptor in 0.7rem body. Yellow horizontal rules between items. Issue stamp top-right.

### 7. Pull Quote

Large opening quote mark `"` in 12rem Oswald at 8% opacity as background texture. Quote text in 2rem Source Serif 4, 3 lines max, left-aligned. Attribution: 1px rule + name in 0.75rem mono. Nothing else on slide.

### 8. Closing / Back Page (Inverted)

Full slide `var(--bg-dark)`. Yellow bar top-full-width. White headline bottom-left. Mono CTA bottom-right. Optional: thin red single-word emphasis. Mirrors the Cover layout but dark — signals closure.

---

## Signature Elements

### CSS Overlays
- `.np-ghost`: 幽灵数字（背景装饰）— `position: absolute; font-family: 'Oswald', sans-serif; font-weight: 900; font-size: clamp(12rem, 30vw, 28rem); color: rgba(0,0,0,0.05); line-height: 1; pointer-events: none`

### Animations
- 无 `@keyframes`，全部使用 CSS transitions
- `.reveal`: 入场动画 — `opacity: 0; transform: translateY(24px); transition: opacity 0.7s cubic-bezier(0.16,1,0.3,1), transform 0.7s cubic-bezier(0.16,1,0.3,1)`
- `.reveal-left`: 左向入场 — `opacity: 0; transform: translateX(-32px)`，相同 transition
- Stagger delays: `.reveal:nth-child(1-6)` — `0.05s, 0.15s, 0.25s, 0.35s, 0.42s, 0.49s`

### Required CSS Classes
- `.np-headline` / `.np-headline-lg` / `.np-headline-sm`: 主标题 — `font-family: 'Oswald'; font-weight: 900; text-transform: uppercase; letter-spacing: -0.02em; line-height: 0.92`
- `.np-subhead`: 副标题 — `font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em`
- `.np-body`: 正文 — `font-family: 'Source Serif 4', serif; max-width: 38ch; line-height: 1.7`
- `.np-stamp`: 期刊印章 — `font-family: 'IBM Plex Mono'; font-size: 0.55-0.72rem; letter-spacing: 0.12em; text-transform: uppercase`
- `.np-bar-h` / `.np-bar-v`: 黄色强调条 — `background: var(--yellow); height: 10px / width: 8px`
- `.np-rule-h` / `.np-rule-v`: 列分隔线 — `background: var(--rule); height: 1px / width: 1px`
- `.np-dark`: 深色变体 — `background: var(--bg-dark); color: #f7f5f0`（分隔线颜色自动反转）
- `.np-red` / `.np-yellow-text`: 强调色文字工具类
- `.big-num`: 描边大数字 — `color: transparent; -webkit-text-stroke: 3px var(--text)`

### Allowed Components
- Audit coverage: .np-grid .np-rule

### Background Rule
`.slide` 不设置 background。body 使用 `#f7f5f0`（新闻纸白）。深色幻灯片（`.np-dark`）单独设置 `background: var(--bg-dark)`。

### Style-Specific Rules
- 黄色条 `#FFCC00` 高度 8-14px，仅作水平/垂直分隔或强调锚点，不用于大面积背景填充
- 列规则 `1px solid #111111` 垂直线分隔网格区域，唤起报纸栏感
- 期刊印章：顶角 `IBM Plex Mono` 文字，如 `VOL.01 · NO.03` 或日期，锚定新闻惯例
- 极端标题比例：标题就是幻灯片。`font-size: clamp(4rem, 12vw, 9rem)`，正文不超过 1/10
- 负空间作为编辑选择：每张幻灯片至少 30% 空白，不要填满
- 红色 `#FF3333` 每页最多一个词/一个数字/一个强调，永远不用于大面积背景
- `#FFCC00` 和 `#FF3333` 绝不出现同一页
- 禁止：渐变、阴影、插图、照片、居中布局、markdown 符号、超过 2 种字号

### Signature Checklist
- [ ] 新闻纸白 `#f7f5f0` 背景
- [ ] 极端标题/正文比例（最小 10:1）
- [ ] 黄色条 `#FFCC00` 强调可见
- [ ] Oswald 900 weight，UPPERCASE 标题
- [ ] 每张幻灯片至少 30% 空白
- [ ] 期刊印章（mono 文字，VOL.01 · NO.XX）
- [ ] 无渐变、无阴影、无插图、无照片

## Prohibitions

- No markdown symbols in text (`#`, `*`, `**`)
- No gradients on large areas
- No drop shadows
- No centered layouts — always anchor to a corner or edge
- No more than 2 type sizes per slide (headline + body)
- `#FFCC00` and `#FF3333` never appear on the same slide together

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

- [ ] Aged newsprint white `#f7f5f0` background
- [ ] Extreme headline-to-body ratio (minimum 10:1)
- [ ] Yellow bar `#FFCC00` accent visible
- [ ] Oswald at 900 weight, UPPERCASE headlines
- [ ] At least 30% empty space on every slide
- [ ] Issue stamp in mono (VOL.01 · NO.XX)

---

## Best For

Business reports · Thought leadership · Annual reports · Journalism-style presentations · Economic briefings · Strategic communications
