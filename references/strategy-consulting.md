# Strategy Consulting — Style Reference

Structured, authoritative, and insight-driven. Every slide delivers one message with pyramid-principle clarity. Inspired by top-tier management consulting deliverables — action titles, framework layouts, and evidence-based storytelling. Zero decoration — structure is the design.

---

## Colors

```css
/* Light variant (default) */
:root {
    --bg:              #ffffff;
    --bg-card:         #f7f8fa;
    --bg-accent:       #eef2f7;
    --border:          #d8dfe8;
    --text:            #1a2b4a;
    --text-muted:      #6b7a90;
    --accent:          #1b3a6b;   /* navy anchor */
    --accent-light:    #3366a8;
    --positive:        #2e7d5b;   /* muted green */
    --negative:        #c0392b;   /* muted red */
    --neutral:         #6b7a90;
    --highlight:       #f0c850;   /* warm gold for emphasis */
    --divider:         #c8d1dc;
}
```

---

## Background

```css
body {
    background-color: var(--bg);
    font-family: "Inter", "Noto Sans SC", "PingFang SC", system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
    color: var(--text);
}

/* No grid overlay — clean white canvas */
```

---

## Typography

```css
body {
    font-family: "Inter", "Noto Sans SC", "PingFang SC", system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
    line-height: 1.5;
}

/* Action title — the single takeaway message per slide */
.sc-action-title {
    font-size: clamp(1.2rem, 2.5vw, 1.6rem);
    font-weight: 700;
    color: var(--text);
    line-height: 1.3;
    border-bottom: 2px solid var(--accent);
    padding-bottom: 0.5rem;
    margin-bottom: clamp(1rem, 2vw, 1.5rem);
}

/* Section header */
.sc-section-header {
    font-size: clamp(0.7rem, 1vw, 0.8rem);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--accent);
}

/* Body text */
.sc-body {
    font-size: clamp(0.8rem, 1.3vw, 1rem);
    color: var(--text);
    line-height: 1.6;
}

/* Source/footnote */
.sc-source {
    font-size: clamp(0.55rem, 0.8vw, 0.7rem);
    color: var(--text-muted);
    position: absolute;
    bottom: clamp(0.5rem, 1vw, 1rem);
    left: clamp(1.5rem, 3vw, 3rem);
}
```

---

## Components

```css
/* Recommendation box — key takeaway highlight */
.sc-reco-box {
    background: var(--bg-accent);
    border-left: 4px solid var(--accent);
    padding: clamp(0.75rem, 1.5vw, 1.2rem);
    border-radius: 0 6px 6px 0;
    font-size: clamp(0.8rem, 1.2vw, 0.95rem);
    font-weight: 500;
    color: var(--text);
}

/* Evidence card */
.sc-evidence-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: clamp(0.75rem, 1.5vw, 1.2rem);
}
.sc-evidence-card .sc-metric {
    font-size: clamp(1.5rem, 4vw, 2.5rem);
    font-weight: 800;
    font-variant-numeric: tabular-nums;
    color: var(--accent);
    line-height: 1;
}
.sc-evidence-card .sc-metric-label {
    font-size: clamp(0.6rem, 0.9vw, 0.75rem);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-top: 0.4rem;
}

/* Harvey ball indicator */
.sc-harvey {
    display: inline-block;
    width: 1.2em;
    height: 1.2em;
    border-radius: 50%;
    border: 2px solid var(--accent);
    position: relative;
    vertical-align: middle;
}
.sc-harvey[data-fill="25"]::after { content:''; position:absolute; inset:2px; background: conic-gradient(var(--accent) 0deg 90deg, transparent 90deg); border-radius:50%; }
.sc-harvey[data-fill="50"]::after { content:''; position:absolute; inset:2px; background: conic-gradient(var(--accent) 0deg 180deg, transparent 180deg); border-radius:50%; }
.sc-harvey[data-fill="75"]::after { content:''; position:absolute; inset:2px; background: conic-gradient(var(--accent) 0deg 270deg, transparent 270deg); border-radius:50%; }
.sc-harvey[data-fill="100"]::after { content:''; position:absolute; inset:2px; background: var(--accent); border-radius:50%; }

/* Traffic light status */
.sc-status {
    display: inline-flex;
    align-items: center;
    gap: 0.4em;
    font-size: clamp(0.7rem, 1vw, 0.85rem);
    font-weight: 600;
}
.sc-status::before {
    content: '';
    width: 0.7em;
    height: 0.7em;
    border-radius: 50%;
}
.sc-status.green::before  { background: var(--positive); }
.sc-status.yellow::before { background: var(--highlight); }
.sc-status.red::before    { background: var(--negative); }

/* Pros/Cons markers */
.sc-pro { color: var(--positive); font-weight: 600; }
.sc-con { color: var(--negative); font-weight: 600; }

/* Waterfall bridge connector */
.sc-waterfall-connector {
    stroke: var(--text-muted);
    stroke-width: 1;
    stroke-dasharray: 3 2;
}
```

---

## Named Layout Variations

### 1. Executive Summary (action title + summary + 3-column evidence)

```css
.sc-exec-summary {
    display: grid;
    grid-template-rows: auto 1fr auto;
    height: 100%;
    padding: clamp(1.5rem, 3vw, 3rem);
    gap: clamp(1rem, 2vw, 1.5rem);
}
.sc-exec-summary .sc-evidence-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: clamp(0.75rem, 1.5vw, 1.2rem);
    align-items: stretch;  /* equal-height cards */
}
/* Row 1: action title */
/* Optional: summary paragraph (1-2 sentences) between title and cards */
/* Row 2: three evidence cards (each may include metric + label + short description) */
/* Row 3: recommendation box */
/* The evidence row fills the remaining content height; distribute readable evidence within it. */
```

### 2. Framework Matrix (2×2 quadrant)

```css
.sc-matrix-layout {
    display: grid;
    grid-template-rows: auto 1fr;
    height: 100%;
    padding: clamp(1.5rem, 3vw, 3rem);
    gap: clamp(0.75rem, 1.5vw, 1rem);
}
.sc-matrix {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: clamp(0.5rem, 1vw, 0.75rem);
    flex: 1;
}
.sc-matrix-cell {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: clamp(0.75rem, 1.5vw, 1.2rem);
    display: flex;
    flex-direction: column;
}
.sc-matrix-cell.highlight {
    border-color: var(--accent);
    background: rgba(27, 58, 107, 0.04);
}
/* Axis labels outside the matrix */
.sc-axis-label {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    color: var(--text-muted);
}
/* Vertical axis: use writing-mode: vertical-rl — text reads top-to-bottom naturally.
   Do NOT use vertical-lr + rotate(180deg) which inverts character orientation.
   Place "High" label first (top) and "Low" label last (bottom) using flex + justify-content: space-between. */
```

### 3. MECE Breakdown (pillars / swimlanes)

```css
.sc-pillars-layout {
    display: grid;
    grid-template-rows: auto 1fr;
    height: 100%;
    padding: clamp(1.5rem, 3vw, 3rem);
    gap: clamp(0.75rem, 1.5vw, 1rem);
}
.sc-pillars {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 180px), 1fr));
    gap: clamp(0.5rem, 1vw, 0.75rem);
    align-items: stretch;
}
.sc-pillar {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-top: 3px solid var(--accent);
    border-radius: 0 0 6px 6px;
    padding: clamp(0.75rem, 1.5vw, 1.2rem);
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}
.sc-pillar-title {
    font-size: clamp(0.75rem, 1.1vw, 0.9rem);
    font-weight: 700;
    color: var(--accent);
}
```

### 4. Waterfall / Bridge Chart

```css
.sc-waterfall-layout {
    display: grid;
    grid-template-rows: auto 1fr auto;
    height: 100%;
    padding: clamp(1.5rem, 3vw, 3rem);
    gap: clamp(0.75rem, 1.5vw, 1rem);
}
/* Row 1: action title */
/* Row 2: SVG waterfall chart */
/* Row 3: insight / source */
```

### 5. Comparison Table (structured evaluation)

```css
.sc-comparison-layout {
    display: grid;
    grid-template-rows: auto 1fr;
    height: 100%;
    padding: clamp(1.5rem, 3vw, 3rem);
    gap: clamp(0.75rem, 1.5vw, 1rem);
}
.sc-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: clamp(0.7rem, 1vw, 0.85rem);
}
.sc-table th {
    background: var(--accent);
    color: #ffffff;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-size: clamp(0.6rem, 0.85vw, 0.75rem);
    padding: clamp(0.4rem, 0.8vw, 0.6rem) clamp(0.5rem, 1vw, 0.8rem);
    text-align: left;
}
.sc-table th:first-child { border-radius: 6px 0 0 0; }
.sc-table th:last-child  { border-radius: 0 6px 0 0; }
.sc-table td {
    padding: clamp(0.4rem, 0.8vw, 0.6rem) clamp(0.5rem, 1vw, 0.8rem);
    border-bottom: 1px solid var(--border);
    vertical-align: top;
}
.sc-table tr:nth-child(even) td {
    background: var(--bg-card);
}
```

### 6. Process / Timeline (horizontal steps)

```css
.sc-process-layout {
    display: grid;
    grid-template-rows: auto 1fr;
    height: 100%;
    padding: clamp(1.5rem, 3vw, 3rem);
    gap: clamp(1rem, 2vw, 1.5rem);
}
.sc-steps {
    display: flex;
    align-items: flex-start;
    gap: 0;
    width: 100%;
}
.sc-step {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    position: relative;
    padding: 0 clamp(0.3rem, 0.5vw, 0.5rem);
}
.sc-step-number {
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    background: var(--accent);
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.85rem;
    margin-bottom: 0.5rem;
}
.sc-step::after {
    content: '';
    position: absolute;
    top: 1rem;
    left: calc(50% + 1.2rem);
    width: calc(100% - 2.4rem);
    height: 2px;
    background: var(--border);
}
.sc-step:last-child::after { display: none; }
```

### 7. Situation-Complication-Resolution (narrative arc)

```css
.sc-scr-layout {
    display: grid;
    grid-template-rows: auto 1fr;
    height: 100%;
    padding: clamp(1.5rem, 3vw, 3rem);
    gap: clamp(1rem, 2vw, 1.5rem);
}
.sc-scr-blocks {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: clamp(0.75rem, 1.5vw, 1.2rem);
}
.sc-scr-block {
    border-top: 3px solid var(--border);
    padding-top: clamp(0.75rem, 1.5vw, 1rem);
}
.sc-scr-block.situation  { border-color: var(--neutral); }
.sc-scr-block.complication { border-color: var(--negative); }
.sc-scr-block.resolution { border-color: var(--positive); }
.sc-scr-block-label {
    font-size: clamp(0.6rem, 0.85vw, 0.7rem);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
}
```

### 8. Before/After Split (dual-panel transformation)

```css
.sc-before-after-layout {
    display: grid;
    grid-template-rows: auto 1fr;
    height: 100%;
    padding: clamp(1.5rem, 3vw, 3rem);
    gap: clamp(0.75rem, 1.5vw, 1rem);
}
.sc-before-after {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: clamp(0.75rem, 1.5vw, 1.2rem);
    align-items: stretch;
}
.sc-before-panel, .sc-after-panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: clamp(0.75rem, 1.5vw, 1.2rem);
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}
.sc-before-panel { border-top: 3px solid var(--negative); }
.sc-after-panel  { border-top: 3px solid var(--positive); }
.sc-panel-label {
    font-size: clamp(0.6rem, 0.85vw, 0.7rem);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.sc-before-panel .sc-panel-label { color: var(--negative); }
.sc-after-panel .sc-panel-label  { color: var(--positive); }
/* List items: use font-size clamp(0.85rem, 1.2vw, 1rem) for readability.
   Prefix each item with ✗ (color: var(--negative)) in before-panel
   and ✓ (color: var(--positive)) in after-panel for instant visual differentiation. */
```

### 9. Three Things (icon + title + body × 3)

```css
.sc-three-things-layout {
    display: grid;
    grid-template-rows: auto 1fr;
    height: 100%;
    padding: clamp(1.5rem, 3vw, 3rem);
    gap: clamp(1rem, 2vw, 1.5rem);
}
.sc-three-things {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: clamp(0.75rem, 1.5vw, 1.2rem);
    align-items: center;  /* vertically center columns */
}
.sc-thing {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 0.75rem;
    padding: clamp(0.75rem, 1.5vw, 1.2rem);
}
.sc-thing-icon {
    width: 3rem;
    height: 3rem;
    border-radius: 50%;
    background: var(--bg-accent);
    border: 2px solid var(--accent);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--accent);
}
.sc-thing-title {
    font-size: clamp(0.8rem, 1.2vw, 1rem);
    font-weight: 700;
    color: var(--text);
}
.sc-thing-body {
    font-size: clamp(0.7rem, 1vw, 0.85rem);
    color: var(--text-muted);
    line-height: 1.5;
}
/* Body text should be 2-3 sentences — this layout needs content density to fill the viewport height. */
```

### 10. Funnel (SVG trapezoid layers)

```css
.sc-funnel-layout {
    display: grid;
    grid-template-rows: auto auto 1fr auto;
    height: 100%;
    padding: clamp(1.5rem, 3vw, 3rem);
    gap: clamp(0.75rem, 1.5vw, 1rem);
}
/* Row 1: action title */
/* Row 2: description paragraph (1-2 sentences explaining the funnel logic) */
/* Row 3: SVG funnel (centered) */
/* Row 4: summary line (key stats, e.g. "end-to-end < 60s · zero intervention") */
.sc-funnel-svg {
    width: 100%;
    max-width: 500px;
    height: auto;
    margin: 0 auto;
}
.sc-funnel-layer {
    fill: var(--accent);
    opacity: 0.9;
}
.sc-funnel-layer:nth-child(2) { opacity: 0.7; }
.sc-funnel-layer:nth-child(3) { opacity: 0.5; }
.sc-funnel-layer:nth-child(4) { opacity: 0.35; }
.sc-funnel-layer:nth-child(5) { opacity: 0.2; }
.sc-funnel-label {
    font-family: inherit;
    font-size: clamp(10px, 1vw, 13px);
    fill: #ffffff;
    font-weight: 600;
    text-anchor: middle;
}
.sc-funnel-value {
    font-family: inherit;
    font-size: clamp(9px, 0.8vw, 11px);
    fill: var(--text-muted);
    text-anchor: start;
    font-variant-numeric: tabular-nums;
}
```

### 11. Quote + Evidence (qualitative + quantitative)

```css
.sc-quote-evidence-layout {
    display: grid;
    grid-template-rows: auto 1fr;
    height: 100%;
    padding: clamp(1.5rem, 3vw, 3rem);
    gap: clamp(0.75rem, 1.5vw, 1rem);
}
.sc-quote-evidence {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: clamp(1rem, 2vw, 1.5rem);
    align-items: start;
}
.sc-quote-block {
    border-left: 3px solid var(--accent);
    padding-left: clamp(0.75rem, 1.5vw, 1.2rem);
}
.sc-quote-text {
    font-size: clamp(0.9rem, 1.4vw, 1.1rem);
    font-style: italic;
    color: var(--text);
    line-height: 1.6;
    margin-bottom: 0.75rem;
}
.sc-quote-attribution {
    font-size: clamp(0.65rem, 0.9vw, 0.8rem);
    font-weight: 600;
    color: var(--text-muted);
}
.sc-evidence-stack {
    display: flex;
    flex-direction: column;
    gap: clamp(0.5rem, 1vw, 0.75rem);
}
```

### 12. Driver Breakdown (2-layer issue tree, max 4 children)

```css
.sc-driver-layout {
    display: grid;
    grid-template-rows: auto 1fr;
    height: 100%;
    padding: clamp(1.5rem, 3vw, 3rem);
    gap: clamp(1rem, 2vw, 1.5rem);
}
.sc-driver-tree {
    --driver-gap: 2.5rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--driver-gap);
}
.sc-driver-root {
    background: var(--accent);
    color: #ffffff;
    font-weight: 700;
    font-size: clamp(0.8rem, 1.2vw, 1rem);
    padding: clamp(0.5rem, 1vw, 0.75rem) clamp(1rem, 2vw, 1.5rem);
    border-radius: 6px;
    position: relative;
}
.sc-driver-root::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translate(-50%, 100%);
    width: 2px;
    height: var(--driver-gap);
    background: var(--border);
}
.sc-driver-children {
    display: flex;
    gap: clamp(0.5rem, 1vw, 0.75rem);
    position: relative;
    padding-top: 0.5rem;  /* space for horizontal connector */
}
.sc-driver-children::before {
    content: '';
    position: absolute;
    top: 0;
    left: calc(12.5% + 0.25rem);
    right: calc(12.5% + 0.25rem);
    height: 2px;
    background: var(--border);
}
.sc-driver-child {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: clamp(0.6rem, 1.2vw, 1rem);
    flex: 1;
    text-align: center;
    position: relative;
}
.sc-driver-child::before {
    content: '';
    position: absolute;
    top: -0.5rem;
    left: 50%;
    transform: translateX(-50%);
    width: 2px;
    height: 0.5rem;
    background: var(--border);
}
.sc-driver-child-title {
    font-size: clamp(0.7rem, 1vw, 0.85rem);
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 0.3rem;
}
.sc-driver-child-body {
    font-size: clamp(0.6rem, 0.9vw, 0.75rem);
    color: var(--text-muted);
    line-height: 1.4;
}
```

---

## SVG Chart Styles

```css
/* Axis */
.sc-axis { stroke: var(--divider); stroke-width: 1; fill: none; }

/* Bar */
.sc-bar { fill: var(--accent); rx: 3; }
.sc-bar.positive { fill: var(--positive); }
.sc-bar.negative { fill: var(--negative); }

/* Waterfall bridge */
.sc-bar.bridge { fill: var(--accent-light); opacity: 0.6; }

/* Labels */
.sc-chart-label {
    font-family: inherit;
    font-size: clamp(9px, 0.8vw, 11px);
    fill: var(--text-muted);
    font-variant-numeric: tabular-nums;
}
.sc-chart-value {
    font-family: inherit;
    font-size: clamp(10px, 0.9vw, 12px);
    fill: var(--text);
    font-weight: 600;
    font-variant-numeric: tabular-nums;
}
```

---

## User-Content 12-Page Route

- P1 Cover -> `cover`: 简洁白底，公司名 + 项目标题 + 日期
- P2 Executive Summary -> `exec_summary`: action title + 3 证据卡 + 建议框
- P3 Situation -> `scr_narrative`: 现状描述，数据支撑
- P4 Complication -> `before_after`: 变革前后对比
- P5 Market Sizing -> `funnel`: TAM/SAM/SOM 漏斗量化
- P6 Analysis -> `waterfall_chart`: 瀑布图量化影响
- P7 Stakeholder Voice -> `quote_evidence`: 关键利益方引言 + 支撑数据
- P8 Recommendation -> `three_things`: 三大战略支柱
- P9 Drivers -> `driver_breakdown`: 营收/增长驱动因素分解
- P10 Implementation -> `process_timeline`: 实施路线图
- P11 Evaluation -> `comparison_table`: 方案对比评估表
- P12 Close -> `closing`: 行动号召 + 联系方式

---

## Canonical Export Contract

- Use canonical layout roles: `cover`, `exec_summary`, `scr_narrative`, `framework_matrix`, `waterfall_chart`, `comparison_table`, `pillars_mece`, `process_timeline`, `before_after`, `three_things`, `funnel`, `quote_evidence`, `driver_breakdown`, `closing`
- Keep canonical tokens: `--bg`, `--bg-card`, `--bg-accent`, `--border`, `--text`, `--text-muted`, `--accent`, `--accent-light`, `--positive`, `--negative`, `--neutral`, `--highlight`, `--divider`
- Add `data-export-role` on every `<section class="slide">`
- Charts must stay pure SVG/CSS
- Canonical emitted classes are `.sc-*`

---

## Signature Elements

### CSS Overlays
- 无装饰性叠加层 — 白底干净画布是核心视觉语言

### Animations
- `@keyframes fadeIn`: 纯淡入 — `from { opacity: 0; } to { opacity: 1; }`
- `@keyframes slideInLeft`: 左侧滑入 — `from { opacity: 0; transform: translateX(-16px); } to { opacity: 1; transform: none; }`
- 配合 `.slide.visible .reveal` staggered delays (0.1s, 0.2s, 0.3s, 0.4s, 0.5s)
- 动画克制 — 咨询风格强调内容本身，动画仅辅助阅读顺序

### Required CSS Classes
- `.sc-action-title`: 行动标题 — 每页标题即结论，`border-bottom: 2px solid var(--accent)`
- `.sc-section-header`: 板块标头 — `uppercase, letter-spacing: 0.1em, color: var(--accent)`
- `.sc-reco-box`: 建议框 — `border-left: 4px solid var(--accent); background: var(--bg-accent)`
- `.sc-evidence-card`: 证据卡 — `background: var(--bg-card); border: 1px solid var(--border)`
- `.sc-matrix`: 2×2 矩阵 — `grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr`
- `.sc-pillars`: MECE 分栏 — `grid, auto-fit, border-top: 3px solid var(--accent)`
- `.sc-table`: 对比评估表 — `th background: var(--accent), color: white`
- `.sc-steps`: 流程步骤 — `flex, numbered circles with connector lines`
- `.sc-harvey`: Harvey ball — `conic-gradient 填充百分比指示`
- `.sc-status`: 交通灯 — `::before 圆点 + green/yellow/red`
- `.sc-source`: 数据来源 — `absolute bottom-left, 小字灰色`
- `.sc-waterfall-connector`: 瀑布图连接线 — `dashed stroke`

### Allowed Components
- `.sc-action-title` `.sc-section-header` `.sc-body` `.sc-source`
- `.sc-reco-box` `.sc-evidence-card` `.sc-metric` `.sc-metric-label`
- `.sc-exec-summary` `.sc-evidence-row`
- `.sc-matrix-layout` `.sc-matrix` `.sc-matrix-cell` `.sc-axis-label`
- `.sc-pillars-layout` `.sc-pillars` `.sc-pillar` `.sc-pillar-title`
- `.sc-comparison-layout` `.sc-table`
- `.sc-process-layout` `.sc-steps` `.sc-step` `.sc-step-number`
- `.sc-waterfall-layout` `.sc-waterfall-connector`
- `.sc-scr-layout` `.sc-scr-blocks` `.sc-scr-block` `.sc-scr-block-label`
- `.sc-before-after-layout` `.sc-before-after` `.sc-before-panel` `.sc-after-panel` `.sc-panel-label`
- `.sc-three-things-layout` `.sc-three-things` `.sc-thing` `.sc-thing-icon` `.sc-thing-title` `.sc-thing-body`
- `.sc-funnel-layout` `.sc-funnel-svg` `.sc-funnel-layer` `.sc-funnel-label` `.sc-funnel-value`
- `.sc-quote-evidence-layout` `.sc-quote-evidence` `.sc-quote-block` `.sc-quote-text` `.sc-quote-attribution` `.sc-evidence-stack`
- `.sc-driver-layout` `.sc-driver-tree` `.sc-driver-root` `.sc-driver-children` `.sc-driver-child` `.sc-driver-child-title` `.sc-driver-child-body`
- `.sc-harvey` `.sc-status` `.sc-pro` `.sc-con`
- `.sc-bar` `.sc-axis` `.sc-chart-label` `.sc-chart-value`
- `.highlight` `.positive` `.negative` `.bridge`
- `.situation` `.complication` `.resolution`
- `.green` `.yellow` `.red`

### Background Rule
`.slide` 必须设置 `background: #ffffff`（白底）。无网格叠加层。白色留白本身是设计语言。

### Style-Specific Rules
- 每页必须有 `.sc-action-title`（行动标题 = 该页结论），标题不超过两行
- 必须包含 `#slide-counter` 导航计数器（fixed, top-right, 格式 `01 / 08`），演示模式下隐藏
- 遵循金字塔原则：结论先行 → 证据支撑 → 数据细节
- 配色极度克制 — 仅 navy accent + 少量红绿用于正/负评价
- 不使用渐变、阴影（最多 1px border）、圆角不超过 6px
- 所有数字使用 `font-variant-numeric: tabular-nums`
- Harvey ball 和交通灯是唯一装饰元素
- 信息密度高，但不能以缩小字体换取更多内容；超过 5 条证据或两行标题时拆页。
- 数据来源必须标注在页面底部（`.sc-source`）
- 内容节奏：避免仅有图表的空洞页面，图表页应搭配描述段落或摘要行

### Signature Checklist
- [ ] 白底无叠加层 — 画布干净
- [ ] .sc-action-title 每页行动标题（border-bottom: 2px navy）
- [ ] .sc-reco-box 建议框（border-left: 4px navy）
- [ ] .sc-evidence-card 证据卡片（浅灰底 + 1px border）
- [ ] .sc-matrix 2×2 框架矩阵
- [ ] .sc-pillars MECE 分栏（border-top: 3px navy）
- [ ] .sc-table 深色表头对比表
- [ ] .sc-steps 带数字圆点的流程图
- [ ] .sc-harvey Harvey ball 指示器
- [ ] .sc-status 交通灯状态指示
- [ ] .sc-source 底部数据来源标注
- [ ] .sc-before-after 双面板对比（红/绿 border-top）
- [ ] .sc-three-things 三栏要点（icon + title + body）
- [ ] .sc-funnel-svg SVG 漏斗图（opacity 递减）
- [ ] .sc-quote-evidence 引言+证据（左引言右数据）
- [ ] .sc-driver-tree 驱动因素分解树（2层限定）
- [ ] font-variant-numeric: tabular-nums
- [ ] 无渐变、无阴影、border-radius ≤ 6px
- [ ] 金字塔叙事结构（结论→证据→细节）

---

## Animation

```css
.reveal {
    opacity: 0;
    transform: translateX(-12px);
    transition: opacity 0.4s ease, transform 0.4s ease;
}
.slide.visible .reveal { opacity: 1; transform: none; }
.reveal:nth-child(1) { transition-delay: 0.1s; }
.reveal:nth-child(2) { transition-delay: 0.2s; }
.reveal:nth-child(3) { transition-delay: 0.3s; }
.reveal:nth-child(4) { transition-delay: 0.4s; }
.reveal:nth-child(5) { transition-delay: 0.5s; }
```

---

## Style Preview Checklist

- [ ] 白色背景 — 干净、专业
- [ ] Action title 带 navy 底线可见
- [ ] 至少一个 evidence card 或 metric 数字
- [ ] 建议框（border-left navy）可见
- [ ] 表格或矩阵结构清晰
- [ ] 信息层级分明（标题→内容→来源）
- [ ] 无多余装饰元素

---

## Best For

战略咨询报告 · 尽职调查 · 管理层汇报 · 董事会材料 · 商业计划书 · 方案评估与推荐 · 任何需要"金字塔原理"结构化表达的场景


## Canvas Sizing Contract

The following CSS is the authoritative viewport and typography layer, applied after historical demo CSS and shared compatibility rules. The program synchronizes it into both language demos and packaged profile templates with `python3 scripts/build-profile-templates.py`. Keep the white / navy palette and canonical `.sc-*` components.

- Size text against both width and height: at 1440 × 900, action titles are about 44px, body copy 30px, table text 27px, labels 22px. Presentation pins the same scale to its 1440 × 900 canvas.
- Use the full content rectangle between the title and footer: evidence, tables, panels and conclusions stretch into remaining height. Avoid a centered miniature content block.
- Use `.sc-heading` for title and optional explanation, then one flexible exhibit. Two/four facts use two columns; three use three; the fifth spans the last row. Never turn ordinal labels into oversized metrics.
- Use `.sc-dense` only for four/five longer facts. If source copy still exceeds the canvas, split the page; preserve all conditions and numbers. Do not crop text or clamp lines.
- The final typography layer must win over shared `audience-copy`, title-fit and short-window rules; unrelated presets keep their existing behavior.

```css
/* Strategy Consulting canvas contract */
body[data-preset="Strategy Consulting"] {
    --sc-unit: min(1vw, 1.6vh);
    --sc-title-size: calc(var(--sc-unit) * 3.05);
    --sc-body-size: calc(var(--sc-unit) * 2.05);
    --sc-table-size: calc(var(--sc-unit) * 1.85);
    --sc-label-size: calc(var(--sc-unit) * 1.5);
    --sc-metric-size: calc(var(--sc-unit) * 4.2);
    --sc-gap: calc(var(--sc-unit) * 1.6);
    --sc-inset: calc(var(--sc-unit) * 4.2);
    --sc-top: calc(var(--sc-unit) * 5.6);
    --sc-bottom: calc(var(--sc-unit) * 4.2);
    font-variant-numeric: tabular-nums;
}
/* Presentation uses a fixed 1440 x 900 design canvas, independent of the window. */
body.presenting[data-preset="Strategy Consulting"] { --sc-unit: 14.4px; }
body[data-preset="Strategy Consulting"] .slide {
    padding: var(--sc-top) var(--sc-inset) var(--sc-bottom) !important;
    background: var(--bg);
}
body[data-preset="Strategy Consulting"] .slide > .slide-content,
body[data-preset="Strategy Consulting"] .slide > .profile-content {
    display: flex !important;
    flex-direction: column;
    flex: 1;
    width: 100%;
    height: 100%;
    min-height: 0;
    max-width: none;
    padding: 0 !important;
    gap: var(--sc-gap) !important;
    justify-content: flex-start;
}
body[data-preset="Strategy Consulting"] .strategy-consulting-block {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-height: 0;
    width: 100%;
    gap: var(--sc-gap);
}
body[data-preset="Strategy Consulting"] .sc-fact-panel { border-top-color: var(--accent); }
body[data-preset="Strategy Consulting"] .sc-fact-panel .sc-panel-label { color: var(--accent); }
body[data-preset="Strategy Consulting"] .sc-heading { display: grid; gap: var(--sc-gap); flex: none; }
body[data-preset="Strategy Consulting"] .slide :is(h1, h2, .sc-action-title, .profile-fit-title) {
    font-size: var(--sc-title-size) !important;
    line-height: 1.3 !important;
    font-weight: 700;
    letter-spacing: -.025em;
    color: var(--text);
    max-width: 100% !important;
    margin: 0;
    padding-bottom: calc(var(--sc-unit) * 1.2);
    border-bottom: 2px solid var(--accent);
    flex: none;
}
body[data-preset="Strategy Consulting"] .slide .title-line {
    display: inline !important;
    white-space: normal !important;
}
body[data-preset="Strategy Consulting"] .slide .title-line + .title-line::before { content: ' '; }
body[data-preset="Strategy Consulting"] .slide :is(p, li, .sc-body, .sc-metric-label, .sc-thing-body) {
    font-size: var(--sc-body-size) !important;
    line-height: 1.48 !important;
    max-width: none !important;
    overflow-wrap: break-word;
    color: var(--text);
}
body[data-preset="Strategy Consulting"] .slide :is(.sc-section-header, .sc-panel-label, .sc-quote-attribution) {
    font-size: var(--sc-label-size) !important;
    letter-spacing: .04em;
}
body[data-preset="Strategy Consulting"] .sc-evidence-row {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    grid-auto-rows: 1fr;
    flex: 1;
    margin: 0 !important;
    min-height: 0;
    gap: var(--sc-gap);
    align-items: stretch;
}
body[data-preset="Strategy Consulting"] .sc-evidence-row--2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
body[data-preset="Strategy Consulting"] .sc-evidence-row--1 { grid-template-columns: minmax(0, 1fr); }
body[data-preset="Strategy Consulting"] .sc-evidence-row[data-fact-count="5"] > :last-child { grid-column: 1 / -1; }
body[data-preset="Strategy Consulting"] :is(.sc-evidence-card, .sc-pillar, .sc-before-panel, .sc-after-panel, .sc-thing) {
    min-width: 0;
    padding: calc(var(--sc-unit) * 1.8);
    border-radius: 0;
}
body[data-preset="Strategy Consulting"] .sc-evidence-card {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: calc(var(--sc-unit) * 1.2);
    border-top: 3px solid var(--accent);
}
body[data-preset="Strategy Consulting"] .slide .sc-metric {
    font-size: var(--sc-metric-size) !important;
    line-height: 1.16;
    margin: 0;
    color: var(--accent);
}
/* Ordinal labels are wayfinding, not evidence metrics. */
body[data-preset="Strategy Consulting"] .slide .sc-evidence-card--fact .sc-metric {
    font-size: var(--sc-label-size) !important;
}
body[data-preset="Strategy Consulting"] .slide .sc-metric-label {
    text-transform: none;
    letter-spacing: normal;
    margin: 0;
}
body[data-preset="Strategy Consulting"] .sc-evidence-card > p { margin: 0; }
body[data-preset="Strategy Consulting"] .sc-reco-box {
    flex: none;
    font-size: var(--sc-table-size);
    line-height: 1.45;
    padding: calc(var(--sc-unit) * 1.25) calc(var(--sc-unit) * 1.6);
    border-radius: 0;
}
body[data-preset="Strategy Consulting"] :is(.sc-before-after, .sc-three-things, .sc-quote-evidence) {
    flex: 1;
    min-height: 0;
    align-items: stretch;
    gap: var(--sc-gap);
}
body[data-preset="Strategy Consulting"] .sc-quote-evidence { grid-template-columns: minmax(0, .9fr) minmax(0, 1.1fr); }
body[data-preset="Strategy Consulting"] :is(.sc-before-panel, .sc-after-panel) { gap: var(--sc-gap); }
body[data-preset="Strategy Consulting"] .sc-panel-label { padding-bottom: var(--sc-gap); border-bottom: 1px solid var(--border); }
body[data-preset="Strategy Consulting"] :is(.sc-before-panel, .sc-after-panel) ul {
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;
    gap: var(--sc-gap);
    flex: 1;
    margin: 0;
    padding-left: 1.1em;
}
body[data-preset="Strategy Consulting"] .sc-quote-block {
    display: flex;
    flex-direction: column;
    justify-content: center;
    font-size: calc(var(--sc-unit) * 2.5);
    line-height: 1.5;
    padding: calc(var(--sc-unit) * 2);
}
body[data-preset="Strategy Consulting"] .sc-quote-text { font-size: inherit; font-style: normal; }
body[data-preset="Strategy Consulting"] .sc-quote-evidence > ol {
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;
    padding-left: 1.4em;
    gap: var(--sc-gap);
}
body[data-preset="Strategy Consulting"] .sc-thing { justify-content: center; gap: var(--sc-gap); }
body[data-preset="Strategy Consulting"] .sc-thing-title { font-size: var(--sc-body-size); }
body[data-preset="Strategy Consulting"] .sc-evidence-stack { justify-content: center; gap: var(--sc-gap); }
body[data-preset="Strategy Consulting"] :is(.sc-table, .sc-fact-table) {
    width: 100%;
    flex: 1;
    table-layout: fixed;
    border-collapse: collapse;
    font-size: var(--sc-table-size);
}
body[data-preset="Strategy Consulting"] .slide :is(.sc-table, .sc-fact-table) :is(td, th) {
    font-size: var(--sc-table-size) !important;
    line-height: 1.45 !important;
    padding: calc(var(--sc-unit) * 1.1) calc(var(--sc-unit) * 1.3);
    vertical-align: middle;
    border-bottom: 1px solid var(--border);
    overflow-wrap: break-word;
}
body[data-preset="Strategy Consulting"] .sc-fact-table td:first-child { width: 8%; color: var(--accent); }
body[data-preset="Strategy Consulting"] .sc-rule-table td:first-child { width: 58%; }
body[data-preset="Strategy Consulting"] .sc-fact-table th { background: var(--accent); color: var(--bg); text-align: left; }
body[data-preset="Strategy Consulting"] .sc-fact-table tr:nth-child(even) td { background: var(--bg-card); }
body[data-preset="Strategy Consulting"] .sc-close-facts {
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;
    flex: 1;
    gap: var(--sc-gap);
    padding-left: 1.2em;
}
body[data-preset="Strategy Consulting"] .slide .sc-source {
    position: absolute;
    bottom: calc(var(--sc-unit) * 1.3);
    left: var(--sc-inset);
    max-width: 78%;
    font-size: calc(var(--sc-unit) * .95) !important;
    line-height: 1.4 !important;
}
body[data-preset="Strategy Consulting"] .profile-eyebrow { display: none; }
body[data-preset="Strategy Consulting"] #brand-mark { left: var(--sc-inset); top: calc(var(--sc-unit) * 1.8); }
body[data-preset="Strategy Consulting"] #slide-counter { right: var(--sc-inset); top: calc(var(--sc-unit) * 1.8); }
body[data-preset="Strategy Consulting"] .slide-num-label { right: var(--sc-inset); bottom: calc(var(--sc-unit) * 1.3); }
/* Dense exhibits use the table scale; do not reduce unrelated presets' body type. */
body[data-preset="Strategy Consulting"] .slide .sc-dense :is(p, li, .sc-metric-label) { font-size: var(--sc-table-size) !important; }
@media (max-width: 600px) {
    body:not(.presenting)[data-preset="Strategy Consulting"] {
        --sc-unit: 6px;
        --sc-title-size: 26px;
        --sc-body-size: 18px;
        --sc-table-size: 17px;
        --sc-label-size: 14px;
        --sc-gap: 14px;
        --sc-inset: 20px;
        --sc-top: 48px;
        --sc-bottom: 36px;
    }
    body:not(.presenting)[data-preset="Strategy Consulting"] .slide .sc-evidence-row {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    body:not(.presenting)[data-preset="Strategy Consulting"] .slide .sc-evidence-row > :last-child:nth-child(odd) { grid-column: 1 / -1; }
    body:not(.presenting)[data-preset="Strategy Consulting"] .slide :is(.sc-before-after, .sc-quote-evidence) { grid-template-columns: 1fr; }
    body:not(.presenting)[data-preset="Strategy Consulting"] .slide .sc-quote-block { font-size: 20px; }
    body:not(.presenting)[data-preset="Strategy Consulting"] .slide :is(.sc-fact-table, .sc-fact-table tbody) { display: block; }
    body:not(.presenting)[data-preset="Strategy Consulting"] .slide .sc-fact-table tr { display: grid; grid-template-columns: 1fr; }
    body:not(.presenting)[data-preset="Strategy Consulting"] .slide .sc-fact-table td { display: block; width: 100%; padding: 7px 10px; }
    body:not(.presenting)[data-preset="Strategy Consulting"] .slide .sc-fact-table:not(.sc-rule-table) td:first-child { display: none; }
}
```
