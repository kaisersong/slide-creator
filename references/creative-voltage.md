# Creative Voltage — Style Reference

Bold, creative, energetic, retro-modern. Electric blue meets neon yellow.

---

## Colors

```css
:root {
    --bg-primary: #0066ff;
    --bg-dark: #1a1a2e;
    --accent-neon: #d4ff00;
    --text-light: #ffffff;
}
```

---

## Background

```css
body {
    background: var(--bg-dark);
    font-family: "Syne", -apple-system, sans-serif;
}

/* Halftone texture pattern */
.voltage-halftone {
    position: absolute;
    inset: 0;
    background-image: radial-gradient(circle, rgba(255,255,255,0.08) 1px, transparent 1px);
    background-size: 12px 12px;
    pointer-events: none;
    opacity: 0.5;
}

/* Neon glow effect */
.voltage-glow {
    box-shadow: 0 0 20px rgba(212,255,0,0.3), 0 0 40px rgba(212,255,0,0.1);
}
```

---

## Typography

```css
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');

.voltage-title {
    font-family: "Syne", sans-serif;
    font-size: clamp(32px, 6vw, 64px);
    font-weight: 800;
    color: var(--text-light);
    line-height: 1.05;
}

.voltage-body {
    font-family: "Syne", sans-serif;
    font-size: clamp(14px, 1.5vw, 18px);
    font-weight: 400;
    color: rgba(255,255,255,0.7);
    line-height: 1.6;
}

.voltage-mono {
    font-family: "Space Mono", monospace;
    font-size: clamp(11px, 1.2vw, 14px);
    color: var(--accent-neon);
}

.voltage-neon-badge {
    display: inline-block;
    background: var(--accent-neon);
    color: var(--bg-dark);
    padding: 4px 12px;
    border-radius: 4px;
    font-family: "Space Mono", monospace;
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
```

---

## Components

```css
/* Split panel — electric blue left, dark right */
.voltage-split {
    display: grid;
    grid-template-columns: 1fr 1fr;
    height: 100%;
}
.voltage-blue-panel {
    background: var(--bg-primary);
    padding: clamp(24px, 4vw, 60px);
}
.voltage-dark-panel {
    background: var(--bg-dark);
    padding: clamp(24px, 4vw, 60px);
}

/* Neon callout */
.voltage-callout {
    border: 2px solid var(--accent-neon);
    border-radius: 8px;
    padding: clamp(16px, 2.5vw, 24px);
    background: rgba(212,255,0,0.05);
}

/* Diamond shape decoration */
.voltage-diamond {
    width: clamp(40px, 6vw, 60px);
    height: clamp(40px, 6vw, 60px);
    background: var(--accent-neon);
    transform: rotate(45deg);
    opacity: 0.15;
}
```

---

## Named Layout Variations

### 1. Voltage Hero (全屏宣告)

Dark `#1a1a2e` background with halftone texture. Electric blue `#0066ff` accent block (40-50% width) containing headline in Syne 800, `clamp(32px, 6vw, 64px)`. Neon yellow badge `#d4ff00`. Diamond decoration `.voltage-diamond` at 15% opacity in corner.

```html
<section class="slide">
    <div class="voltage-halftone"></div>
    <div class="voltage-blue-panel" style="position:absolute;left:0;top:0;bottom:0;width:50%;">
        <h1 class="voltage-title">Big Statement</h1>
        <span class="voltage-neon-badge">Tagline</span>
    </div>
    <div class="voltage-diamond" style="position:absolute;right:10%;top:15%;"></div>
</section>
```

### 2. Voltage Split (分栏证据)

`.voltage-split` — electric blue left panel, dark right panel. Left: section number + headline. Right: bullet list or evidence. No divider — color split creates the boundary.

```html
<section class="slide">
    <div class="voltage-split">
        <div class="voltage-blue-panel">
            <span class="voltage-mono">01</span>
            <h2 class="voltage-title" style="font-size:clamp(24px,4vw,48px);">Headline</h2>
        </div>
        <div class="voltage-dark-panel">
            <ul><li>Evidence one</li><li>Evidence two</li><li>Evidence three</li></ul>
        </div>
    </div>
</section>
```

### 3. Voltage Neon (大数字强调)

Dark background. Large neon yellow number `#d4ff00` in Space Mono, `clamp(48px, 8vw, 96px)`, weight 700. Label below in muted white. Optional neon glow `.voltage-glow` on the number.

```html
<section class="slide">
    <div class="voltage-halftone"></div>
    <div style="text-align:center;">
        <div class="voltage-glow" style="font-family:'Space Mono',monospace;font-size:clamp(48px,8vw,96px);font-weight:700;color:#d4ff00;">42</div>
        <p class="voltage-mono">Metric label</p>
    </div>
</section>
```

### 4. Voltage Cards (多选项对比)

3 cards in a row on dark background. Each card: neon yellow border `2px solid var(--accent-neon)`, halftone background inside. Active card has neon yellow background with dark text. Inactive: dark background with neon border.

### 5. Voltage Callout (功能亮点)

Neon callout box `.voltage-callout` with `border: 2px solid #d4ff00`, `background: rgba(212,255,0,0.05)`. Mono label + body description. Diamond decoration `.voltage-diamond` floats in corner at 15% opacity.

---

## Signature Elements

### CSS Overlays
- `.halftone::before`: 半调点阵纹理 — `background-image: radial-gradient(circle, rgba(255,255,255,0.055) 1px, transparent 1px); background-size: 22px 22px; pointer-events: none; z-index: 0`
- `#slide-8 .deco-bg`: CTA 页右侧深色装饰条 — `width: 34%; background: rgba(0,0,0,0.14);` 内含 Syne 800 180px 装饰文字

### Animations
- 无 `@keyframes`，全部使用 CSS transitions + cubic-bezier(0.34, 1.56, 0.64, 1) 弹性曲线
- `.reveal`: 入场动画 — `opacity: 0; transform: translateY(22px); transition: opacity 0.35s cubic-bezier(...), transform 0.35s cubic-bezier(...)`；stagger delays `0.04s, 0.11s, 0.18s, 0.25s`
- `#progress-bar` 过渡使用同一条弹性曲线，0.35s

### Required CSS Classes
- `.halftone`: 应用到需要半调纹理的 `.slide` 上（通过 `::before` 伪元素）
- `.pill`: 霓虹黄色药丸标签 — `background: #d4ff00; color: #0a0a14; font-family: 'Space Mono'; font-size: 10px; font-weight: 700; padding: 5px 14px`
- `.pill.outline`: 描边变体 — `background: transparent; border: 1.5px solid #d4ff00; color: #d4ff00`
- `.pill.small`: 小号变体 — `font-size: 9px; padding: 4px 10px`
- `.blue-panel`: 电蓝面板 — `background: #0066ff; position: relative; overflow: hidden`
- `.dark-panel`: 暗黑面板 — `background: #1a1a2e; position: relative; overflow: hidden`
- `.neon`: 霓虹文字色 — `color: #d4ff00`
- `.panel-content`: 面板内容容器 — `position: relative; z-index: 2; padding: 60px 52px; height: 100%`
- `.big-mark`: 大型装饰符号 — `font-family: 'Syne'; font-weight: 800; font-size: 130px; color: rgba(212,255,0,0.14)`
- `.deco-num`: 背景装饰数字 — `position: absolute; right: -30px; bottom: -60px; font-family: 'Syne'; font-size: 42vw; color: rgba(212,255,0,0.04)`
- `.dot` / `.dot.active`: 导航菱形点 — `transform: rotate(45deg)` 默认 `rgba(212,255,0,0.22)`；激活 `#d4ff00 + scale(1.4)`
- `.voltage-grid`: 预设网格 — `display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px`
- `.vg-cell`: 网格单元 — 半透明背景 + 1px 边框，hover 时霓虹黄 tint
- `.vg-cell.hot`: 高亮单元 — `background: rgba(212,255,0,0.07); border-color: rgba(212,255,0,0.3)`
- `.step-card`: 步骤卡片 — `background: rgba(212,255,0,0.05); border: 1px solid rgba(212,255,0,0.14)`
- `.how-card`: 流程卡片 — `background: rgba(255,255,255,0.03); border-left: 3px solid rgba(212,255,0,0.18)`
- `.terminal-block`: 终端代码块 — `background: rgba(0,0,0,0.5); border: 1px solid rgba(212,255,0,0.14);` 含 `::before { content: '$ '; color: #d4ff00 }`

### Background Rule
`.slide` 不设固定 background，由各面板（`.blue-panel` / `.dark-panel`）或父级 slide 自行定义。`.slide::before` 无内容。纹理通过 `.halftone::before` 在选中 slide 上启用。CTA 页 `#slide-8` 使用 `background: #0066ff`。

### Style-Specific Rules
- 双面板布局（flex row）：`.blue-panel` + `.dark-panel` 比例自由组合（36/64, 55/45, 40/60, 46/54）
- 所有标点/序号/装饰文字优先使用霓虹黄 `#d4ff00` 或低透明度版本
- Syne 800 仅用于标题和大装饰文字，Space Mono 用于所有标签/正文
- `.halftone` class 显式加到 slide 上，非全局应用

### Signature Checklist
- [ ] `.halftone::before` 半调点阵纹理（22px 间距，5.5% 白点）
- [ ] `.pill` / `.pill.outline` 霓虹黄标签系统
- [ ] `.blue-panel` + `.dark-panel` 双面板分割布局
- [ ] `.panel-content` 面板内容容器（z-index: 2）
- [ ] `.big-mark` 大型装饰符号（Syne 800, 130px）
- [ ] `.deco-num` / `.deco-bg` 背景装饰文字
- [ ] `.dot` 导航菱形点（rotate 45deg）
- [ ] `.voltage-grid` + `.vg-cell` 预设网格
- [ ] `.step-card` 步骤卡片（霓虹黄边框）
- [ ] `.how-card` 流程卡片（左侧霓虹黄 3px 边框）
- [ ] `.terminal-block` 终端代码块（含 `$ ` 前缀）
- [ ] `.reveal` 弹性曲线动画（cubic-bezier(0.34, 1.56, 0.64, 1)）

---

## Animation

```css
.reveal {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.5s ease, transform 0.5s cubic-bezier(0.34,1.2,0.64,1);
}
.reveal.visible { opacity: 1; transform: translateY(0); }
.reveal:nth-child(1) { transition-delay: 0.05s; }
.reveal:nth-child(2) { transition-delay: 0.15s; }
.reveal:nth-child(3) { transition-delay: 0.25s; }
```

---

## Style Preview Checklist

- [ ] Dark `#1a1a2e` background with halftone texture
- [ ] Neon yellow `#d4ff00` on at least one element
- [ ] Electric blue `#0066ff` accent panel
- [ ] Syne font at 800 weight for headlines
- [ ] Space Mono for labels/callouts

---

## Best For

Creative pitches · Design agency decks · Brand launches · Artist portfolios · Innovation showcases · High-energy presentations
