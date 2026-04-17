# Enterprise Dark — Style Reference

Authoritative, data-driven, trustworthy — McKinsey dark deck meets Bloomberg Terminal. Every element earns its place.

---

## Colors

```css
:root {
    --bg-primary:   #0d1117;
    --bg-secondary: #161b22;
    --bg-header:    #21262d;
    --border:       #30363d;
    --text-primary: #e6edf3;
    --text-body:    #c9d1d9;
    --text-muted:   #8b949e;
    --accent-blue:  #388bfd;
    --accent-green: #3fb950;   /* positive / up */
    --accent-red:   #f85149;   /* negative / down */
    --accent-amber: #d29922;   /* warning / neutral */
}
```

---

## Background

```css
body {
    background: var(--bg-primary);
}

/* Subtle density grid — adds visual weight without distraction */
body::before {
    content: '';
    position: fixed; inset: 0;
    background-image:
        linear-gradient(rgba(48,54,61,0.5) 1px, transparent 1px),
        linear-gradient(90deg, rgba(48,54,61,0.5) 1px, transparent 1px);
    background-size: 24px 24px;
    opacity: 0.03;
    pointer-events: none;
    z-index: 0;
}
```

---

## Typography

```css
/* All text — system fonts, tabular nums for all numeric content */
body {
    font-family: "PingFang SC", "Noto Sans CJK SC", "Segoe UI",
                 -apple-system, system-ui, sans-serif;
    font-feature-settings: "tnum"; /* tabular numbers throughout */
    -webkit-font-smoothing: antialiased;
}

/* Section label */
.ent-label {
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-muted);
}

/* Slide title */
.ent-title {
    font-size: clamp(22px, 3.5vw, 44px);
    font-weight: 600;
    color: var(--text-primary);
    line-height: 1.12;
    letter-spacing: -0.02em;
}

/* KPI number */
.ent-kpi-number {
    font-size: clamp(36px, 5vw, 56px);
    font-weight: 800;
    font-feature-settings: "tnum";
    line-height: 1;
}
.ent-kpi-number.positive { color: var(--accent-green); }
.ent-kpi-number.negative { color: var(--accent-red); }
.ent-kpi-number.neutral  { color: var(--text-primary); }

/* KPI label */
.ent-kpi-label {
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-top: 4px;
}
```

---

## KPI Card Component

```css
.ent-kpi-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: clamp(16px, 2.5vw, 24px) clamp(20px, 3vw, 32px);
    display: flex;
    flex-direction: column;
    gap: 4px;
}

/* KPI grid — 2 or 3 columns */
.ent-kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 180px), 1fr));
    gap: clamp(10px, 1.5vw, 16px);
}

/* Trend arrow */
.ent-trend {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: clamp(10px, 1.2vw, 12px);
    font-weight: 600;
}
.ent-trend.up   { color: var(--accent-green); }
.ent-trend.down { color: var(--accent-red); }
```

---

## Progress Bar

```css
.ent-progress-track {
    height: 2px;
    background: var(--border);
    border-radius: 2px;
    overflow: hidden;
}
.ent-progress-fill {
    height: 100%;
    background: var(--accent-blue);
    border-radius: 2px;
    transition: width 0.8s cubic-bezier(0.16,1,0.3,1);
}
```

---

## Table Component

```css
.ent-table {
    width: 100%;
    border-collapse: collapse;
    font-size: clamp(12px, 1.3vw, 15px);
    font-variant-numeric: tabular-nums;
}
.ent-table thead th {
    background: var(--bg-header);
    color: var(--text-muted);
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: clamp(8px, 1.2vw, 12px) clamp(12px, 1.5vw, 16px);
    text-align: left;
    border-bottom: 1px solid var(--border);
}
.ent-table tbody td {
    padding: clamp(10px, 1.3vw, 14px) clamp(12px, 1.5vw, 16px);
    color: var(--text-primary);
    border-bottom: 1px solid var(--border);
}
.ent-table tbody tr:last-child td { border-bottom: none; }
.ent-table tbody tr:hover td { background: rgba(48,54,61,0.5); }
```

---

## Layout — Consulting Split

```css
.ent-split {
    display: grid;
    grid-template-columns: clamp(160px, 22%, 240px) 1fr;
    gap: clamp(20px, 3vw, 36px);
    align-items: start;
}
.ent-split-label {
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: clamp(10px, 1.5vw, 14px) 0;
    border-bottom: 1px solid var(--border);
}
```

---

## Named Layout Variations

### 1. KPI Dashboard

2×2 or 1×3 grid of KPI cards. Each card: `border: 1px --border`, `background: --bg-secondary`, large number in `--text-primary`, uppercase mono label in `--text-secondary`, optional trend SVG arrow in `--accent-green`/`--accent-red`. All numbers: `font-variant-numeric: tabular-nums`.

### 2. Consulting Split

Left column 35% (`--bg-secondary` background, `1px --border` right edge): section number + title + 2-line context. Right column 65%: main content — bullets, table, or chart. `--accent-blue` overline on section title. No padding between columns except the border.

### 3. Data Table

Full-width. Header: `--bg-secondary` fill, `--text-secondary` 11px uppercase, `letter-spacing: 0.1em`. Body: `1px --border` row dividers. Numbers right-aligned, tabular-nums. Most important row: `3px --accent-blue` left-border. No outer border — open table style.

### 4. Architecture Map

SVG on dark background. Boxes: `1px --border` stroke, `--bg-secondary` fill, labels in 11px mono. Connector lines: `1px --text-muted`, dashed for optional paths. Key node: `2px --accent-blue` stroke. Strategic layer labels in uppercase `--text-secondary`.

### 5. Comparison Matrix

2-column. Column headers in `--accent-blue`. Row labels left in `--text-secondary`. `1px --border` grid lines. ✓ in `--accent-green`, ✗ in `--accent-red`, — in `--text-muted`. Summary/total row: `--bg-secondary` fill.

### 6. Insight Pull

Single key sentence in 2rem `--text-primary`, left-aligned, top-left 55% of slide. Below: `1px --accent-blue` rule + 2-line attribution in `--text-secondary` 0.8rem. Remaining right and bottom: empty dark. The emptiness signals authority.

### 7. Horizontal Timeline

Thin `1px --border` horizontal track across slide center. Milestone circles `8px`, `--accent-blue` fill, `2px` glow. Date labels above in 0.7rem mono `--text-muted`. Event labels below in 0.85rem `--text-secondary`. Active milestone: larger circle with subtle glow.

---

## Components

```css
/* ── KPI card ── */
.ent-kpi-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: clamp(16px, 2.5vw, 24px);
    display: flex;
    flex-direction: column;
    gap: 4px;
    flex: 1;
    min-width: 120px;
}
.ent-kpi-number {
    font-size: clamp(32px, 5vw, 56px);
    font-weight: 700;
    font-variant-numeric: tabular-nums;
    line-height: 1;
    letter-spacing: -0.03em;
}
.ent-kpi-number.positive { color: var(--accent-green); }
.ent-kpi-number.negative { color: var(--accent-red); }
.ent-kpi-number.neutral  { color: var(--text-primary); }

.ent-kpi-label {
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
}

/* KPI row — flex container for multiple KPI cards */
.ent-kpi-row {
    display: flex;
    gap: clamp(12px, 2vw, 20px);
    flex-wrap: wrap;
}

/* ── Inline label tag ── */
.ent-label-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 3px 10px;
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 600;
    color: var(--text-muted);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    font-variant-numeric: tabular-nums;
}

/* ── Inline badge (status indicator) ── */
.ent-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 600;
    letter-spacing: 0.04em;
    font-variant-numeric: tabular-nums;
}
.ent-badge-blue {
    background: rgba(56,139,253,0.15);
    color: var(--accent-blue);
    border: 1px solid rgba(56,139,253,0.30);
}
.ent-badge-green {
    background: rgba(63,185,80,0.15);
    color: var(--accent-green);
    border: 1px solid rgba(63,185,80,0.30);
}

/* ── Status dot ── */
.ent-status-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    margin-right: 6px;
    vertical-align: middle;
}
.ent-dot-green { background: var(--accent-green); }
.ent-dot-blue  { background: var(--accent-blue); }
.ent-dot-red   { background: var(--accent-red); }

/* ── Accent color utilities ── */
.ent-accent-blue   { color: var(--accent-blue); }
.ent-accent-green  { color: var(--accent-green); }
.ent-accent-red    { color: var(--accent-red); }
.ent-accent-amber  { color: var(--accent-amber); }

/* ── Feature row (icon + text + optional badge) ── */
.ent-feature-row {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: clamp(12px, 1.8vw, 16px) 0;
    border-bottom: 1px solid var(--border);
}
.ent-feature-row:last-child { border-bottom: none; }

.ent-feature-icon {
    width: 28px;
    height: 28px;
    min-width: 28px;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
}

/* ── Progress bar ── */
.ent-prog-bar {
    height: 2px;
    background: var(--border);
    border-radius: 2px;
    overflow: hidden;
}
.ent-prog-fill {
    height: 100%;
    background: var(--accent-blue);
    border-radius: 2px;
    transition: width 0.8s ease;
}

/* ── Horizontal separator ── */
.ent-sep {
    height: 1px;
    background: var(--border);
    margin: clamp(14px, 2vw, 22px) 0;
}

/* ── Content container (max-width centered) ── */
.ent-content {
    width: 100%;
    max-width: 880px;
    padding: clamp(24px, 5vw, 60px);
}

/* ── 2-column grid ── */
.ent-grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: clamp(10px, 1.5vw, 16px);
}

/* ── Consulting split layout ── */
.ent-split {
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: clamp(20px, 3vw, 36px);
    align-items: start;
}
.ent-split-labels {
    display: flex;
    flex-direction: column;
    gap: clamp(10px, 1.5vw, 14px);
}
.ent-split-label {
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: clamp(10px, 1.5vw, 14px) 0;
    border-bottom: 1px solid var(--border);
}
.ent-split-label:last-child { border-bottom: none; }

/* ── Data table ── */
.ent-table {
    width: 100%;
    border-collapse: collapse;
    font-variant-numeric: tabular-nums;
}
.ent-table th {
    background: var(--bg-header);
    color: var(--text-muted);
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: clamp(8px, 1.2vw, 12px) clamp(12px, 1.5vw, 16px);
    text-align: left;
    border-bottom: 1px solid var(--border);
}
.ent-table td {
    padding: clamp(10px, 1.3vw, 14px) clamp(12px, 1.5vw, 16px);
    color: var(--text-primary);
    border-bottom: 1px solid var(--border);
    font-size: clamp(12px, 1.3vw, 15px);
}
.ent-table tr:last-child td { border-bottom: none; }

/* ── Code block ── */
.ent-code {
    font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
    background: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: clamp(12px, 1.8vw, 18px);
    font-size: clamp(11px, 1.2vw, 14px);
    color: var(--accent-blue);
    line-height: 1.6;
}
.ent-code .muted { color: var(--text-muted); }
.ent-code .green { color: var(--accent-green); }

/* ── Install command block ── */
.ent-install {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: clamp(12px, 1.8vw, 18px);
    margin-bottom: clamp(8px, 1.2vw, 12px);
}
.ent-install-label {
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
}
.ent-install-cmd {
    font-family: 'SF Mono', 'Fira Code', monospace;
    font-size: clamp(11px, 1.2vw, 14px);
    color: var(--accent-green);
    word-break: break-all;
}
```

### Slide Composition Guide

Every Enterprise Dark presentation should use these patterns per slide type:

| Slide | Required Components | Element Target |
|-------|--------------------|----------------|
| Cover | `.ent-label-tag` + `h1` with `.ent-accent-blue` + `.ent-sep` + `.ent-kpi-row` (4 cards) | 20+ elements |
| Problem | `.ent-label-tag` + `h2` + `.ent-sep` + card with 3× `.ent-feature-row` (each with `.ent-feature-icon` + `h3` + `p` + `.ent-badge`) | 25+ elements |
| Workflow | `.ent-label-tag` + `h2` + `.ent-sep` + `.ent-split` (labels + card with `.ent-feature-row`s) | 25+ elements |
| Data Table | `.ent-label-tag` + `h2` + `.ent-sep` + `.ent-table` (with `.ent-status-dot` + `.ent-badge` in cells) | 30+ elements |
| Steps | `.ent-label-tag` + `h2` + `.ent-sep` + card with 3× `.ent-feature-row` (numbered icons + `.ent-prog-bar`) | 30+ elements |
| Features | `.ent-label-tag` + `h2` + `.ent-sep` + `.ent-grid-2` (4 cards, each with `h3` + `.ent-badge` + `p` + `.ent-prog-bar`) | 30+ elements |
| Install | `.ent-label-tag` + `h2` + `.ent-sep` + 2× `.ent-install` + card with `.ent-table` (requirements) | 25+ elements |
| Closing | `.ent-label-tag` + `h1` with accent + `.ent-sep` + `.ent-code` + `.ent-kpi-row` (3 small cards) | 20+ elements |

---

## Signature Elements

### CSS Overlays
- `body::before`: 密度网格叠加（24px 间距，极淡）— `background-image: linear-gradient(rgba(48,54,61,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(48,54,61,0.5) 1px, transparent 1px); background-size: 24px 24px; opacity: 0.03; pointer-events: none; z-index: 0`

### Animations
- 无 `@keyframes`，全部使用 CSS transitions
- `.reveal`: 入场淡入 — `opacity: 0; transition: opacity 0.3s ease;`；`.reveal.visible { opacity: 1; }`
- Stagger delays: `.reveal:nth-child(1-4)` — `0.05s, 0.12s, 0.19s, 0.26s`

### Required CSS Classes
- `.label-tag` (`.ent-label-tag`): 章节标签 — `background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 4px; padding: 3px 10px; font-size: 10-12px; text-transform: uppercase; letter-spacing: 0.06em`
- `.kpi` (`.ent-kpi-card`): KPI 卡片 — `background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 6px; padding: 16-24px`
- `.kpi-value` (`.ent-kpi-number`): KPI 数值 — `font-size: clamp(36px, 5vw, 56px); font-weight: 700; font-variant-numeric: tabular-nums`
- `.kpi-label` (`.ent-kpi-label`): KPI 标签 — `font-size: 10-12px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted)`
- `.card`: 通用卡片容器 — `background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px`
- `.badge` / `.badge-blue` / `.badge-green`: 状态徽章 — `padding: 2px 8px; border-radius: 4px; font-variant-numeric: tabular-nums`
- `.status-dot` / `.dot-green` / `.dot-blue` / `.dot-red`: 状态圆点 — `width: 7px; height: 7px; border-radius: 50%`
- `.sep`: 水平分隔线 — `height: 1px; background: var(--border)`
- `.code`: 代码块 — `font-family: 'SF Mono', monospace; background: var(--bg); border: 1px solid var(--border); border-radius: 6px; color: var(--accent-blue)`
- `.accent-blue` / `.accent-green` / `.accent-red` / `.accent-orange`: 强调色工具类

### Background Rule
`.slide` 不设置 background。body 使用 `#0d1117` 深色背景 + 24px 网格叠加。所有卡片使用 `--bg-secondary (#161b22)` 形成层次感。

### Style-Specific Rules
- 所有数值内容必须使用 `font-variant-numeric: tabular-nums`
- 内容始终左对齐，从不居中（consulting 风格信号）
-  accent 色仅用于数据强调：blue=中性，green=正向，red=负向，amber=警告
- 卡片 border-radius 最大 6px，不使用圆角装饰
- 网格间距固定 24px，`rgba(48,54,61,0.5)` 线条色
- 不使用渐变、明亮装饰色、或纯黑色 `#000` 背景

### Signature Checklist
- [ ] `#0d1117` 深色背景 + faint 24px 网格可见
- [ ] 至少一个 KPI 数字（48px+）使用绿色或蓝色
- [ ] 所有面板有 `1px solid #30363d` 边框
- [ ] 章节标签（uppercase mono text）出现在数据上方
- [ ] 所有数值使用 tabular-nums
- [ ] 内容左对齐，无居中布局
- [ ] 动画仅限 300ms 淡入

---

## Animation

```css
/* Minimal: 300ms fade only. No movement. */
.reveal {
    opacity: 0;
    transition: opacity 0.3s ease;
}
.reveal.visible { opacity: 1; }
.reveal:nth-child(1) { transition-delay: 0.05s; }
.reveal:nth-child(2) { transition-delay: 0.12s; }
.reveal:nth-child(3) { transition-delay: 0.19s; }
.reveal:nth-child(4) { transition-delay: 0.26s; }
```

---

## Style Preview Checklist

- [ ] Dark `#0d1117` background with faint grid
- [ ] At least one KPI number (48px+) in green or blue
- [ ] `1px #30363d` border on all panels
- [ ] Consulting-style left label column visible
- [ ] Tabular numbers on all numeric content
- [ ] No pure black `#000` background
- [ ] Animations limited to 300ms fade max

---

## Best For

Quarterly business reviews · Strategy presentations · Investor updates · B2B sales decks · Management consulting · Board materials · KPI dashboards · Data-driven storytelling
