# Data Story — Style Reference

Clear, precise, and persuasive. Numbers are the hero. Inspired by Figma Annual Report, Stripe Annual Report, and Bloomberg Businessweek data visualizations. Zero external chart libraries — pure CSS + SVG only.

---

## Colors

```css
/* Dark variant (default) */
:root {
    --bg:              #0f1117;
    --bg-card:         #1a1f2e;
    --border:          #2d3748;
    --text:            #e2e8f0;
    --text-muted:      #64748b;
    --positive:        #00d4aa;   /* up / good */
    --negative:        #ff6b6b;   /* down / bad */
    --neutral:         #e2e8f0;
    --chart-primary:   #3b82f6;
    --chart-secondary: #8b5cf6;
    --chart-tertiary:  #10b981;
    --grid-line:       #1e293b;
    --axis-line:       #334155;
}

/* Light variant */
:root.ds-light {
    --bg:           #f8f9fc;
    --bg-card:      #ffffff;
    --border:       #e2e8f0;
    --text:         #0f172a;
    --text-muted:   #64748b;
    --grid-line:    #e2e8f0;
    --axis-line:    #cbd5e1;
}
```

---

## Background

```css
body {
    background-color: var(--bg);
    font-family: "Inter", "Noto Sans SC", "PingFang SC", system-ui, sans-serif;
    font-variant-numeric: tabular-nums;
    -webkit-font-smoothing: antialiased;
}

/* Subtle grid pattern for data alignment */
body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(var(--grid-line) 1px, transparent 1px),
        linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
    background-size: 40px 40px;
    opacity: 0.3;
    pointer-events: none;
    z-index: 0;
}
```

---

## Typography

```css
body {
    font-family: "Inter", "Noto Sans SC", "PingFang SC", system-ui, sans-serif;
    font-variant-numeric: tabular-nums;   /* CRITICAL: all numbers align */
    -webkit-font-smoothing: antialiased;
}

/* KPI hero number */
.ds-kpi {
    font-size: clamp(3rem, 8vw, 6rem);
    font-weight: 800;
    font-variant-numeric: tabular-nums;
    line-height: 1;
    letter-spacing: -0.02em;
}
.ds-kpi.positive { color: var(--positive); }
.ds-kpi.negative { color: var(--negative); }
.ds-kpi.neutral  { color: var(--neutral); }

/* KPI label */
.ds-kpi-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-muted);
    margin-top: 8px;
}

/* Trend comparison */
.ds-trend {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 13px;
    font-weight: 600;
    margin-top: 6px;
}
.ds-trend.up   { color: var(--positive); }
.ds-trend.down { color: var(--negative); }
/* Use ▲ ▼ characters */
```

---

## KPI Card Components

```css
/* Single KPI card */
.ds-kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: clamp(1rem, 2vw, 1.5rem);
    display: flex;
    flex-direction: column;
}

/* KPI grid */
.ds-kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%,160px),1fr));
    gap: clamp(0.5rem, 1.5vw, 1rem);
}
```

---

## Named Layout Variations

### 1. Hero Number (full-screen single KPI)

```css
.ds-hero-slide {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    gap: clamp(0.5rem, 1.5vw, 1rem);
    padding: clamp(2rem, 5vw, 5rem);
}
/* The KPI number occupies center stage */
/* Supporting context below in small text */
```

### 2. KPI Row + Chart (two columns)

```css
.ds-split-layout {
    display: grid;
    grid-template-columns: 1fr 1.5fr;
    gap: clamp(1rem, 3vw, 2.5rem);
    height: 100%;
    align-items: center;
    padding: clamp(2rem, 4vw, 4rem);
}
/* Left: stack of KPI cards */
/* Right: SVG line or bar chart */
```

### 3. Full-screen Bar Chart + Insight

```css
.ds-chart-layout {
    display: grid;
    grid-template-rows: auto 1fr auto;
    gap: 1rem;
    padding: clamp(1.5rem, 3vw, 3rem);
    height: 100%;
}
/* Row 1: slide title */
/* Row 2: SVG bar chart */
/* Row 3: insight pullquote */
```

### 4. 2×2 Comparison Matrix

```css
.ds-matrix {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: clamp(0.5rem, 1.5vw, 1rem);
    flex: 1;
}
.ds-matrix-cell {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: clamp(0.75rem, 1.5vw, 1.2rem);
    display: flex; flex-direction: column; justify-content: center;
}
/* Label each axis externally (row/column headers) */
```

---

## SVG Chart Styles (zero library, pure SVG)

```css
/* Axis lines */
.ds-axis { stroke: var(--axis-line); stroke-width: 1; fill: none; }

/* Grid lines */
.ds-grid { stroke: var(--grid-line); stroke-width: 1; stroke-dasharray: 4 4; fill: none; }

/* Bar chart */
.ds-bar {
    fill: var(--chart-primary);
    rx: 4px;   /* rounded top corners */
}
.ds-bar.secondary { fill: var(--chart-secondary); }

/* Line chart */
.ds-line { stroke: var(--chart-primary); stroke-width: 2.5; fill: none; stroke-linecap: round; }

/* Area fill (under line) */
.ds-area { fill: var(--chart-primary); opacity: 0.10; }

/* Data point dot */
.ds-dot { fill: var(--chart-primary); r: 4; }
```

### Minimal SVG Bar Chart Example

```html
<svg viewBox="0 0 400 160" class="ds-chart-svg">
  <!-- Grid lines -->
  <line x1="40" y1="0" x2="40" y2="140" class="ds-axis"/>
  <line x1="40" y1="140" x2="400" y2="140" class="ds-axis"/>
  <line x1="40" y1="30" x2="400" y2="30" class="ds-grid"/>
  <line x1="40" y1="70" x2="400" y2="70" class="ds-grid"/>
  <line x1="40" y1="110" x2="400" y2="110" class="ds-grid"/>
  <!-- Bars (heights represent values) -->
  <rect x="60"  y="60" width="40" height="80" rx="4" class="ds-bar"/>
  <rect x="120" y="40" width="40" height="100" rx="4" class="ds-bar"/>
  <rect x="180" y="20" width="40" height="120" rx="4" class="ds-bar"/>
  <rect x="240" y="50" width="40" height="90" rx="4" class="ds-bar"/>
  <rect x="300" y="10" width="40" height="130" rx="4" class="ds-bar"/>
  <!-- Labels -->
  <text x="80"  y="158" text-anchor="middle" class="ds-axis-label">Q1</text>
  <text x="140" y="158" text-anchor="middle" class="ds-axis-label">Q2</text>
  <text x="200" y="158" text-anchor="middle" class="ds-axis-label">Q3</text>
  <text x="260" y="158" text-anchor="middle" class="ds-axis-label">Q4</text>
  <text x="320" y="158" text-anchor="middle" class="ds-axis-label">Q5</text>
</svg>
```

```css
.ds-chart-svg { width: 100%; height: auto; }
.ds-axis-label {
    font-family: inherit;
    font-size: 10px;
    fill: var(--text-muted);
    font-variant-numeric: tabular-nums;
}
```

---

## Insight Pullquote

```css
.ds-insight {
    border-left: 3px solid var(--chart-primary);
    padding: 0.75rem 1rem;
    background: rgba(59,130,246,0.08);
    border-radius: 0 6px 6px 0;
    font-size: clamp(0.8rem, 1.3vw, 1rem);
    line-height: 1.5;
    color: var(--text);
}
.ds-insight strong { color: var(--chart-primary); }
```

---

## Components

```css
/* KPI hero card */
.ds-kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: clamp(16px, 2.5vw, 24px);
}

/* Trend arrow */
.ds-trend-up {
    color: var(--positive);
    font-weight: 600;
}
.ds-trend-down {
    color: var(--negative);
    font-weight: 600;
}

/* Pure CSS bar chart */
.ds-bar {
    display: inline-block;
    background: var(--chart-primary);
    border-radius: 2px;
    min-width: 24px;
}

/* Data annotation */
.ds-annotation {
    font-size: clamp(10px, 1.1vw, 12px);
    color: var(--text-muted);
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
```

---

## Signature Elements

### CSS Overlays
- `.slide::before`: 数据网格叠加 — `background-image: linear-gradient(rgba(30,41,59,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(30,41,59,0.5) 1px, transparent 1px); background-size: clamp(40px,6vw,80px) clamp(40px,6vw,80px); position: absolute; inset: 0; pointer-events: none`

### Animations
- `@keyframes fadeInUp`: 淡入上移 — `from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; }`，配合 `.slide.visible .reveal` staggered delays (0.05s, 0.12s, 0.19s, 0.26s, 0.33s, 0.40s, 0.47s)
- `@keyframes fadeIn`: 纯淡入 — `from { opacity: 0; } to { opacity: 1; }`
- `@keyframes growBar`: 柱状图生长 — `from { transform: scaleY(0); transform-origin: bottom; } to { transform: scaleY(1); transform-origin: bottom; }`

### Required CSS Classes
- `.kpi-number`: KPI 大数字 — `font-size: clamp(4rem, 10vw, 8rem); font-weight: 800; font-variant-numeric: tabular-nums; line-height: 1; letter-spacing: -0.02em`；变体 `.pos`（#00d4aa）、`.neg`（#ff6b6b）、`.neu`（#e2e8f0）、`.blue`（#3b82f6）
- `.kpi-label`: KPI 标签 — `font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; color: #64748b`
- `.kpi-trend`: 趋势箭头 — `display: inline-flex; align-items: center; gap: 4px; font-size: 13px; font-weight: 600`；`.up`（#00d4aa）、`.down`（#ff6b6b）
- `.kpi-grid`: KPI 网格 — `display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: clamp(0.5rem, 1.5vw, 1rem)`
- `.kpi-card`: KPI 卡片 — `background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: clamp(16px, 2.5vw, 24px)`；`.highlight` 变体使用 `border-color: #3b82f6; background: rgba(59,130,246,0.06)`
- `.chart-axis`: SVG 轴线 — `stroke: #334155; stroke-width: 1; fill: none`
- `.chart-grid`: SVG 网格 — `stroke: #1e293b; stroke-width: 1; stroke-dasharray: 4 4; fill: none`
- `.chart-bar`: SVG 柱状图 — `fill: #3b82f6`；`.secondary`（#8b5cf6）、`.tertiary`（#10b981）
- `.chart-line`: SVG 折线 — `stroke: #3b82f6; stroke-width: 2.5; fill: none; stroke-linecap: round; stroke-linejoin: round`
- `.chart-area`: SVG 面积填充 — `fill: url(#areaGrad); opacity: 0.15`
- `.chart-label` / `.chart-val`: SVG 文字标签
- `.chart-layout`: 图表布局 — `display: grid; grid-template-columns: 1fr 1.5fr; gap: clamp(1rem, 3vw, 2.5rem)`
- `.eyebrow`: 小标签 — `font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; color: #64748b`
- `.divider`: 分隔线 — `border: none; border-top: 1px solid var(--border)`
- `.ds-insight`: 洞察卡片 — `border-left: 3px solid var(--chart-primary); padding: 0.75rem 1rem; background: rgba(59,130,246,0.08); border-radius: 0 6px 6px 0`

### Background Rule
`.slide` 必须设置 `background: #0f1117`（深色）或 `var(--bg)`（浅色变体）。网格通过 `.slide::before` 叠加在幻灯片自身上，不使用 `body::before`。

### Style-Specific Rules
- 所有数字元素必须使用 `font-variant-numeric: tabular-nums`
- 不使用外部图表库 — 纯 CSS + SVG 图表
- 图表颜色 token：`--chart-primary: #3b82f6`、`--chart-secondary: #8b5cf6`、`--chart-tertiary: #10b981`
- 情感颜色编码：`--positive: #00d4aa`（上升/好）、`--negative: #ff6b6b`（下降/差）
- 背景网格 `opacity: 0.3`（深色）/ `opacity: 0.3`（浅色）
- 不使用装饰性元素 — 数据是视觉焦点
- 不使用大面积渐变
- Insight 卡片必须使用左侧 3px 彩色边框 + 淡色背景

### Signature Checklist
- [ ] .slide::before 数据网格叠加（clamp(40px,6vw,80px) 间距）
- [ ] @keyframes fadeInUp（staggered 0.05s-0.47s）
- [ ] @keyframes growBar（柱状图生长动画）
- [ ] .kpi-number KPI 大数字（tabular-nums, 4-8rem）
- [ ] .kpi-label KPI 标签（11px uppercase）
- [ ] .kpi-trend 趋势箭头（.up/.down 颜色编码）
- [ ] .kpi-grid KPI 网格（auto-fit, minmax 160px）
- [ ] .kpi-card KPI 卡片（border-radius: 8px）
- [ ] .chart-bar SVG 柱状图（主/次/第三色）
- [ ] .chart-line SVG 折线（stroke-width: 2.5）
- [ ] .chart-grid SVG 网格线（stroke-dasharray: 4 4）
- [ ] .ds-insight 洞察卡片（左侧 3px 彩色边框）
- [ ] .divider 分隔线（1px solid var(--border)）
- [ ] font-variant-numeric: tabular-nums
- [ ] 无外部图表库，纯 SVG

---

## Animation

```css
/* Numbers animate via CSS counter-like approach */
/* Use JS for counting-up effect if desired: */
/* element.textContent changes from 0 to value over 1s */

.reveal {
    opacity: 0;
    transform: translateY(12px);
    transition: opacity 0.5s ease, transform 0.5s ease;
}
.slide.visible .reveal { opacity: 1; transform: translateY(0); }
.reveal:nth-child(1) { transition-delay: 0.05s; }
.reveal:nth-child(2) { transition-delay: 0.15s; }
.reveal:nth-child(3) { transition-delay: 0.25s; }
```

---

## Style Preview Checklist

- [ ] At least one KPI number at 48px+ visible
- [ ] An SVG chart element (bars or line) present
- [ ] `font-variant-numeric: tabular-nums` applied
- [ ] Positive/negative color coding shown (green up, red down)
- [ ] `--grid-line` dashed grid lines visible in chart area

---

## Best For

Quarterly business reviews · Growth reporting · Analyst briefings · Data product demos · KPI dashboards presented as slides · Any talk where the numbers tell the story
