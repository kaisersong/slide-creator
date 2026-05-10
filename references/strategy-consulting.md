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
/* NOTE: Do NOT use flex:1 on evidence-row — cards should take natural height, not stretch to fill the slide */
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
- 信息密度高 — 每页可承载更多文字（相比其他风格）
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
