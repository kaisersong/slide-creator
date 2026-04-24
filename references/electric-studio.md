# Electric Studio — Style Reference

Bold, clean, professional, high contrast. Split panel design with confident typography.

---

## Colors

```css
:root {
    --bg-dark: #0a0a0a;
    --bg-white: #ffffff;
    --accent-blue: #4361ee;
    --text-dark: #0a0a0a;
    --text-light: #ffffff;
}
```

---

## Background

```css
body {
    background: var(--bg-dark);
    font-family: "Manrope", -apple-system, sans-serif;
}
```

---

## Typography

```css
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;800&display=swap');

.elec-title {
    font-family: "Manrope", sans-serif;
    font-size: clamp(32px, 6vw, 64px);
    font-weight: 800;
    line-height: 1.05;
    color: var(--text-dark);
}

.elec-body {
    font-family: "Manrope", sans-serif;
    font-size: clamp(14px, 1.5vw, 18px);
    font-weight: 400;
    line-height: 1.6;
    color: var(--text-dark);
    opacity: 0.7;
}

.elec-label {
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--accent-blue);
}

.elec-quote {
    font-family: "Manrope", sans-serif;
    font-size: clamp(20px, 3vw, 36px);
    font-weight: 800;
    line-height: 1.3;
    color: var(--text-dark);
}
```

---

## Components

```css
/* Accent bar on panel edge */
.elec-accent-bar {
    width: 4px;
    height: 100%;
    background: var(--accent-blue);
}

/* Split panel */
.elec-split {
    display: grid;
    grid-template-columns: 1fr 1fr;
    height: 100%;
}
.elec-panel-white {
    background: var(--bg-white);
    padding: clamp(24px, 4vw, 60px);
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.elec-panel-dark {
    background: var(--bg-dark);
    padding: clamp(24px, 4vw, 60px);
    display: flex;
    flex-direction: column;
    justify-content: center;
}

/* Quote typography as hero element */
.elec-quote-block {
    border-left: 4px solid var(--accent-blue);
    padding-left: clamp(16px, 2.5vw, 24px);
    margin: clamp(16px, 2.5vw, 28px) 0;
}
```

---

## Named Layout Variations

### 1. Studio Hero (全屏宣告)

Dark `#0a0a0a` background. White panel on one side (45-55% width) with headline in Manrope 800, `clamp(32px, 6vw, 64px)`. Blue accent bar `.elec-accent-bar` (4px) on panel edge. Label in `.elec-label` (small, uppercase, blue).

```html
<section class="slide" style="padding:0;">
    <div class="elec-split">
        <div class="elec-panel-dark">
            <span class="elec-label">Studio</span>
            <h1 class="elec-title" style="color:#fff;">Big Statement</h1>
        </div>
        <div class="elec-panel-white">
            <p class="elec-body">Supporting content</p>
        </div>
    </div>
</section>
```

### 2. Studio Split (分屏对比/分栏证据)

Full `.elec-split` — white left, dark right (or reversed). Left: section number + headline. Right: bullet list or evidence. No divider — color split creates the boundary. `.elec-accent-bar` between panels.

### 3. Studio Quote (功能亮点)

Single panel (white or dark) with `.elec-quote-block`: `border-left: 4px solid var(--accent-blue)`, `padding-left: clamp(16px, 2.5vw, 24px)`. Quote in `.elec-quote` (Manrope 800, `clamp(20px, 3vw, 36px)`). Attribution in `.elec-body` muted.

### 4. Studio Stat (大数字强调)

Dark background. Large white number in Manrope 800, `clamp(48px, 8vw, 96px)`. Blue accent label above. Clean, minimal — single focal point.

---

## Signature Elements

### CSS Overlays
- `.left-panel::after`: 垂直 4px 强调条 — `position: absolute; right: 0; top: 12%; bottom: 12%; width: 4px; background: #4361ee`
- `.top-panel::after`: 水平 4px 强调条 — `position: absolute; bottom: 0; left: 8%; right: 8%; height: 4px; background: #4361ee`
- `#slide-8 .left-panel::after`: CTA 页变体 — `background: rgba(255,255,255,0.08)`（白色而非蓝色）

### Animations
- 无 `@keyframes`，全部使用 CSS transitions
- `.reveal`: 入场动画 — `opacity: 0; transform: translateY(18px); transition: opacity 0.4s ease, transform 0.4s ease`；stagger delays `0.05s, 0.13s, 0.21s, 0.29s`

### Required CSS Classes
- `.left-panel`: 左侧面板 — `flex: 0 0 58%; display: flex; flex-direction: column; justify-content: center; padding: 80px 60px 80px 80px`
- `.right-panel`: 右侧面板 — `flex: 0 0 42%; display: flex; flex-direction: column; justify-content: center; padding: 80px 48px`
- `.top-panel`: 上方面板 — `flex: 0 0 52%; width: 100%; display: flex; flex-direction: column; justify-content: flex-end; padding: 56px 80px 40px`
- `.bottom-panel`: 下方面板 — `flex: 0 0 48%; width: 100%; display: flex; flex-direction: column; justify-content: flex-start; padding: 40px 80px 56px`
- `#brand-mark`: 固定品牌标识 — `position: fixed; top: 20px; left: 28px; font-family: 'Manrope'; font-weight: 800; font-size: 15px; color: #4361ee; z-index: 1000`
- `.label`: 蓝色小标签 — `font-size: 10px; font-weight: 700; letter-spacing: 0.22em; text-transform: uppercase; color: #4361ee`
- `.label.white`: 暗面板上的白色标签 — `color: rgba(255,255,255,0.5)`
- `.slide-num-label`: 页码 — `position: absolute; bottom: 28px; right: 36px; font-size: 11px; color: rgba(0,0,0,0.18)`；`.light` 变体 `rgba(255,255,255,0.2)`
- `.badge-pill`: 描边标签 — `padding: 6px 16px; border: 1.5px solid rgba(67,97,238,0.3); font-size: 12px; font-weight: 600; color: #4361ee`
- `.code-block`: 代码块 — `background: #0a0a0a; padding: 14px 18px;` 内含 `code { font-family: 'Manrope', monospace; font-size: 12px; color: rgba(255,255,255,0.8) }`
- `.feat-name::before`: 功能列表蓝点 — `content: ''; display: inline-block; width: 6px; height: 6px; background: #4361ee`
- `.cta-pill`: CTA 圆角块 — `background: #fff; color: #4361ee; font-weight: 800; font-size: 26px; padding: 18px 36px`
- `.dot` / `.dot.active`: 导航圆点 — 默认 `rgba(67,97,238,0.25) + 1px solid rgba(67,97,238,0.4)`；激活 `#4361ee + scale(1.5)`
- `.pt-cell` / `.pt-cell.featured`: 预设网格单元 — featured 为 `background: #4361ee`

### Allowed Components
- Audit coverage: .elec-accent-bar .elec-body .elec-label .elec-panel-dark .elec-panel-white .elec-quote .elec-quote-block .elec-split
- Audit coverage cont.: .elec-title

### Background Rule
`.slide` 不设固定 background。各面板自行定义背景色：`.left-panel` / `.right-panel` / `.top-panel` / `.bottom-panel` 通过内联 style 设置为 `#ffffff`、`#0a0a0a`、`#f8f9ff`、`#f2f4ff` 等。无 body 渐变或伪元素覆盖。

### Style-Specific Rules
- 双面板垂直分割为主（58/42 或 55/45），水平分割为辅（52/48）
- 强调条 4px 蓝色自动出现在面板边缘（`::after`），不需要手动添加
- 所有文字使用 Manrope 字体，权重 400/500/700/800
- 装饰极少 — 通过留白和间距传递信心，无纹理/网格/图案
- `#brand-mark` 固定在左上角，全程可见

### Signature Checklist
- [ ] `.left-panel::after` 垂直 4px 蓝色强调条（top 12% to bottom 12%）
- [ ] `.top-panel::after` 水平 4px 蓝色强调条（left 8% to right 8%）
- [ ] `#brand-mark` 固定品牌标识（Manrope 800, 15px, #4361ee）
- [ ] `.label` / `.label.white` 蓝色小标签
- [ ] `.slide-num-label` / `.light` 右下角页码
- [ ] `.badge-pill` 蓝色描边标签
- [ ] `.feat-name::before` 蓝色圆点列表标记
- [ ] `.cta-pill` 白色背景蓝色文字 CTA
- [ ] `.code-block` 暗黑代码块
- [ ] `.dot` 导航圆点（激活 scale 1.5）
- [ ] `.reveal` 入场动画（translateY 18px，stagger 0.05s-0.29s）
- [ ] 双面板分割布局（垂直 58/42 或水平 52/48）
- [ ] 无纹理/网格/图案 — 纯面板背景色

---

## Animation

```css
.reveal {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.5s ease, transform 0.5s ease;
}
.reveal.visible { opacity: 1; transform: translateY(0); }
.reveal:nth-child(1) { transition-delay: 0.05s; }
.reveal:nth-child(2) { transition-delay: 0.15s; }
.reveal:nth-child(3) { transition-delay: 0.25s; }
```

---

## Style Preview Checklist

- [ ] Split panel layout (white/dark or dark/white)
- [ ] Accent blue `#4361ee` on at least one element
- [ ] Manrope font at 800 weight for headlines
- [ ] Minimal decoration — confidence through spacing
- [ ] No pure black background — using `#0a0a0a`

---

## Best For

Agency presentations · Product showcases · Design portfolios · Brand identity decks · Professional pitches
