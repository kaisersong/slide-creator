# Swiss Modern — Style Reference

Clean, precise, Bauhaus-inspired — International Typographic Style as a presentation. Form follows function absolutely. The grid is not a tool; it is the design.

---

## Colors

```css
:root {
    --bg: #ffffff;
    --bg-dark: #0a0a0a;
    --text: #0a0a0a;
    --text-light: #ffffff;
    --text-muted: #666666;
    --red: #ff3300;       /* single accent — one element per slide maximum */
    --grid-line: rgba(0, 0, 0, 0.05);
}
```

---

## Background

```css
body {
    background: var(--bg);
    font-family: "Archivo Black", "Nunito", -apple-system, sans-serif;
}

/* Visible 12-column grid — faintly visible */
.swiss-grid {
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(var(--grid-line) 1px, transparent 1px),
        linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
    background-size: calc(100vw / 12) 100vh;
    pointer-events: none;
    z-index: 0;
}
```

---

## Typography

```css
@import url('https://fonts.googleapis.com/css2?family=Archivo+Black:wght@900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600&display=swap');

.swiss-title {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(32px, 7vw, 72px);
    font-weight: 900;
    color: var(--text);
    line-height: 1.0;
    letter-spacing: -0.02em;
    text-transform: uppercase;
}

.swiss-body {
    font-family: "Nunito", sans-serif;
    font-size: clamp(12px, 1.4vw, 15px);
    font-weight: 400;
    color: var(--text);
    line-height: 1.55;
    max-width: 55ch;
}

.swiss-label {
    font-family: "Archivo", sans-serif;
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
}

.swiss-stat {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(48px, 8vw, 96px);
    font-weight: 900;
    color: var(--text);
    line-height: 1.0;
}
```

---

## Components

```css
/* Hard horizontal rule — no decorative curves, no dashes */
.swiss-rule {
    height: 2px;
    background: var(--text);
    border: none;
}
.swiss-rule.red {
    background: var(--red);
}
.swiss-rule-thin {
    height: 1px;
    background: var(--text-muted);
    opacity: 0.2;
}

/* Accent word or local numeric hit — never a full-page fill */
.accent {
    color: var(--red);
}

/* Hero helpers */
.hero-rule {
    width: clamp(40px, 8vw, 100px);
    height: 4px;
    background: var(--red);
}
.hero-sub {
    font-family: "Nunito", sans-serif;
    font-size: clamp(12px, 1.4vw, 16px);
    color: var(--text-muted);
    line-height: 1.6;
    max-width: 32rem;
}
.hero-stats {
    display: flex;
    flex-wrap: wrap;
    gap: clamp(20px, 3vw, 48px);
}
.hero-stat-num {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(28px, 4vw, 48px);
    font-weight: 900;
    color: var(--red);
    line-height: 1;
}
.hero-stat-label {
    font-family: "Nunito", sans-serif;
    font-size: clamp(9px, 0.85vw, 11px);
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* 40/60 split evidence layout */
.left-panel {
    width: 38%;
    background: var(--bg-dark);
    color: var(--text-light);
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: clamp(28px, 5vw, 56px);
    position: relative;
}
.right-panel {
    width: 62%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: clamp(28px, 5vw, 56px);
    gap: clamp(16px, 2vw, 28px);
}
.red-bar {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 8px;
    background: var(--red);
}
.left-rule {
    width: 40px;
    height: 3px;
    background: var(--red);
}
.pain-item {
    padding-left: clamp(12px, 2vw, 20px);
    border-left: 2px solid var(--grid-line);
}
.accent-border {
    border-left-color: var(--red);
}
.pain-num {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(16px, 2vw, 24px);
    font-weight: 900;
    color: var(--red);
    line-height: 1;
}
.pain-title {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(13px, 1.5vw, 18px);
    font-weight: 900;
    text-transform: uppercase;
}
.pain-desc {
    font-family: "Nunito", sans-serif;
    font-size: clamp(12px, 1.4vw, 16px);
    color: var(--text-muted);
    line-height: 1.5;
}

/* Big-stat row */
.stat-row {
    display: flex;
    align-items: center;
    gap: clamp(20px, 3vw, 36px);
}
.stat-divider {
    width: 2px;
    align-self: stretch;
    background: var(--text);
}
.stat-copy {
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.stat-label {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(12px, 1.3vw, 16px);
    font-weight: 900;
    color: var(--text);
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.stat-value {
    font-family: "Nunito", sans-serif;
    font-size: clamp(12px, 1.4vw, 16px);
    color: var(--text-muted);
    line-height: 1.5;
}

/* Discovery / process */
.disc-header {
    padding-top: clamp(48px, 8vh, 80px);
    display: flex;
    flex-direction: column;
    gap: 12px;
}
.disc-body {
    display: flex;
    gap: clamp(20px, 4vw, 60px);
    align-items: center;
}
.disc-steps {
    display: flex;
    flex-direction: column;
    gap: clamp(12px, 1.5vw, 20px);
    flex: 1;
}
.disc-step {
    display: flex;
    gap: 12px;
    align-items: flex-start;
}
.disc-step-num {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(18px, 2.5vw, 32px);
    font-weight: 900;
    color: var(--red);
    line-height: 1;
    min-width: 36px;
}
.disc-step-title {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(13px, 1.4vw, 18px);
    font-weight: 900;
    color: var(--text);
    text-transform: uppercase;
    line-height: 1.2;
}
.disc-step-desc {
    font-family: "Nunito", sans-serif;
    font-size: clamp(12px, 1.4vw, 16px);
    color: var(--text-muted);
    line-height: 1.45;
}
.disc-diagram {
    flex: 0 0 auto;
}
.diagram-svg {
    width: 100%;
    max-width: 500px;
    height: auto;
}

/* Table / code */
.data-table {
    width: 100%;
    border-collapse: collapse;
}
.data-table thead th {
    font-family: "Archivo Black", sans-serif;
    font-size: 11px;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    background: var(--bg-dark);
    color: var(--text-light);
    padding: 8px 14px;
    text-align: left;
}
.data-table tbody td {
    padding: 8px 14px;
    font-family: "Nunito", sans-serif;
    font-size: clamp(12px, 1.4vw, 16px);
    color: var(--text);
    border-bottom: 1px solid #e0e0e0;
}
.data-table tbody tr:nth-child(odd) {
    background: #ffffff;
}
.data-table tbody tr:nth-child(even) {
    background: #f7f7f7;
}
.highlight {
    border-left: 3px solid var(--red);
}
.terminal-line {
    font-family: "Nunito", "Noto Sans SC", monospace;
    font-size: clamp(11px, 1.2vw, 14px);
    background: var(--bg-dark);
    color: var(--text-light);
    padding: 10px 16px;
    display: inline-block;
}
.terminal-line::before {
    content: '$ ';
    color: var(--red);
}

/* Index and evidence grid */
.index-item {
    display: flex;
    align-items: baseline;
    gap: clamp(8px, 1.5vw, 20px);
    padding: clamp(6px, 1vw, 12px) 0;
    border-bottom: 1px solid var(--grid-line);
}
.index-num {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(1.5rem, 3vw, 3rem);
    font-weight: 900;
    color: var(--red);
    line-height: 1;
    min-width: clamp(2.5rem, 4vw, 4.5rem);
}
.index-title {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(1rem, 2vw, 1.5rem);
    font-weight: 900;
    color: var(--text);
    line-height: 1.2;
}
.index-desc {
    font-family: "Nunito", sans-serif;
    font-size: clamp(12px, 1.4vw, 16px);
    color: var(--text-muted);
    line-height: 1.4;
}
.feat-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: clamp(8px, 1.5vw, 16px);
}
.feat-card {
    padding: clamp(14px, 2vw, 24px);
    border: 1px solid var(--grid-line);
    position: relative;
}
.feat-key {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(20px, 3vw, 36px);
    font-weight: 900;
    color: var(--text);
    line-height: 1;
}
.feat-name {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(12px, 1.3vw, 16px);
    font-weight: 900;
    color: var(--text);
    text-transform: uppercase;
}
.feat-desc {
    font-family: "Nunito", sans-serif;
    font-size: clamp(12px, 1.4vw, 16px);
    color: var(--text-muted);
    line-height: 1.45;
}

/* Evidence blocks and CTA */
.inst-blocks {
    display: flex;
    flex-direction: column;
    gap: clamp(16px, 2vw, 28px);
}
.inst-block {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: clamp(16px, 2vw, 24px);
    border-left: 3px solid var(--bg-dark);
}
.inst-label {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(11px, 1.1vw, 14px);
    font-weight: 900;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.inst-link {
    font-family: "Nunito", sans-serif;
    font-size: clamp(12px, 1.4vw, 16px);
    color: var(--red);
    text-decoration: none;
    border-bottom: 1px solid var(--red);
}
.cta-block {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(1.2rem, 2.5vw, 2rem);
    font-weight: 900;
    background: var(--bg-dark);
    color: var(--text-light);
    padding: clamp(12px, 2vw, 20px) clamp(20px, 3vw, 36px);
    display: inline-block;
    letter-spacing: 0.02em;
}
.cta-title {
    max-width: 13ch;
}
.cta-line {
    display: block;
    white-space: nowrap;
}
.cta-echo {
    display: flex;
    gap: clamp(16px, 3vw, 40px);
}
.cta-echo-num {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(20px, 3vw, 36px);
    font-weight: 900;
    color: var(--red);
    line-height: 1;
}
.cta-echo-label {
    font-family: "Nunito", sans-serif;
    font-size: clamp(9px, 0.85vw, 11px);
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
```

---

## Named Layout Variations

### 1. Title Grid

Slide number top-right in `Archivo Black` 1rem, red. Title bottom-left in 7rem, 2 lines max, `line-height: 0.95`. Empty upper-right quadrant. Red `2px` horizontal rule above the title.

### 2. Column Content

Left column 40%: large section heading + red `2px` rule below. Right column 55% (5% gap): body text in two typographic sub-columns. Section number top-right in small red.

### 3. Stat Block

One large number left half at 8rem `Archivo Black`. Vertical `2px` black rule to its right. Then: label in 1.2rem uppercase + 1-line supporting sentence in 0.9rem body. Red underline on the number only.

### 4. Data Table

Full-width table. Header row: `Archivo Black` 11px uppercase, `background: #0a0a0a`, white text. Body: alternating `#ffffff` / `#f7f7f7` rows, `1px #e0e0e0` dividers. Most important row: `3px` red left-border. No outer border.

### 5. Geometric Diagram

Discovery / process layout: `.disc-header` with `padding-top: clamp(48px, 8vh, 80px)` to clear fixed `#brand-mark` at `top: 20px`. Eyebrow + h2 gap ≥ 12px. h2 `line-height: 1.2` for CJK readability (never 1.05 with Chinese text). SVG diagram of boxes + connector lines, `stroke: #0a0a0a`, `stroke-width: 1.5`. No fills except primary node: `fill: #ff3300`. Labels in `Nunito` 12px. Grid visible behind. No shadows.

### 6. Pull Quote

One short sentence (max 12 words) in 3rem `Archivo Black`, top-left. Below it: `2px` red rule + attribution in 0.8rem `Nunito`. Remaining 50%+ of slide: pure white. Emptiness is the message.

### 7. Contents Index

Numbered list, left-aligned. Each item: section number in `3rem Archivo Black` red, em-dash, topic in `1.5rem Archivo Black` black. Max 5 items. Visible grid behind. No borders on items.

### 8. User-Content 12-Page Route

When the deck type is the 12-page `user-content` arc from `composition-guide.md`, map roles like this:

- P1 Hero → Title Grid with `.hero-rule`, `.hero-sub`, optional `.hero-stats`
- P2 Problem → Column Content with `.left-panel`, `.right-panel`, `.pain-item`
- P3 Discovery → Geometric Diagram with `.disc-steps` + inline SVG; never a generic quote card
- P4 Solution → Stat Block or Contents Index; use `.stat-row` or `.index-item`, not long bullet columns
- P5 Feature / data proof → `.data-table`, `.terminal-line`, or `.inst-block`
- P6 Split comparison → two true panels (`.left-panel` + `.right-panel`) or two equal `.feat-card`
- P7 Dual feature cards → `.feat-grid` or `.inst-blocks`
- P8 Process / depth → `.disc-steps` sequence or numbered `.index-item` flow; not a single callout
- P9 Checkpoint grid → 2×2 `.feat-grid` with short labels + evidence
- P10 Recommendation grid → `.feat-grid` or `.index-item` stack; not a repeated quote / callout slide
- P11 Evidence list → `.inst-blocks`, `.data-table`, or mixed proof stack
- P12 CTA → left-anchored close with `.cta-block`; title stays left or bottom-left, never centered. Long CTA titles follow the global title-balance rule from `title-quality.md`: no browser-only auto-wrap, no orphan line, no obviously collapsed middle line. `.cta-line` is the preferred Swiss line-control wrapper when explicit stacking is needed

### 9. Canonical Export Contract

Swiss Modern native PPT export only stays high-fidelity when the generated HTML follows the canonical structure used by the reference demo.

- Use canonical layout roles: `title_grid`, `column_content`, `stat_block`, `pull_quote`, `geometric_diagram`, `data_table`, `contents_index`
- Panels are direct children of `.slide`
  Correct: `.slide > .left-panel > .slide-content`, `.slide > .right-panel > .slide-content`
  Wrong: `.slide > .slide-content > .left-panel`, `.slide > .slide-content > .left-col/.right-col`
- Anchored chrome stays at slide root: `.bg-num` and `.slide-num-label` are direct children of `.slide`, not nested in `.slide-content`
- Keep canonical tokens: `--bg`, `--bg-dark`, `--text`, `--text-light`, `--text-muted`, `--red`, `--grid-line`
- Add `data-export-role` on every `<section class="slide">` matching the chosen named layout slug
- Compatible aliases are input-only and must not be emitted by `--generate`: `.left-col`, `.right-col`, `.stat-block`, `.content-block`, `.quote-block`, `--bg-primary`, `--bg-secondary`, `--text-primary`, `--text-secondary`, `--accent`

---

## Signature Elements

### CSS Overlays
- `body::before`: 12-column grid overlay — faint grid lines at 3% opacity `linear-gradient(rgba(0,0,0,0.03) 1px, transparent 1px)` + `linear-gradient(90deg, rgba(0,0,0,0.03) 1px, transparent 1px)`, `background-size: calc(100vw / 12) 100vh`, `position: fixed; inset: 0; z-index: 0; pointer-events: none`

### Animations
- `@keyframes fadeIn`: 元素淡入 — `from { opacity: 0; } to { opacity: 1; }`，配合 `.slide.visible .reveal` 使用 staggered delays (0.05s, 0.1s, 0.15s, 0.2s...)

### Required CSS Classes
- `.bg-num`: 背景大序号 — `position: absolute; right: clamp(2rem, 5vw, 5rem); top: 0; font-weight: 900; font-size: 25vw; color: #f0f0f0; line-height: 0.85; pointer-events: none; z-index: 0`
- `.content`: 内容层容器 — `position: relative; z-index: 1; flex: 1; display: flex; flex-direction: column`
- `.eyebrow`: 小标签 — `font-weight: 600; font-size: clamp(0.65rem, 1vw, 0.75rem); letter-spacing: 0.2em; text-transform: uppercase`
- `.swiss-stat`: 大数字 — `font-family: "Archivo Black", sans-serif; font-size: clamp(48px, 8vw, 96px); font-weight: 900; line-height: 1.0`
- `.swiss-rule`: 硬分隔线 — `height: 2px; background: var(--text); border: none`；`.swiss-rule.red` 使用 `background: var(--red)`
- `.swiss-rule-thin`: 细分隔线 — `height: 1px; background: var(--text-muted); opacity: 0.2`

### Allowed Components
- Core text: `.swiss-title` `.swiss-body` `.swiss-label` `.swiss-grid` `.accent`
- Hero helpers: `.hero-rule` `.hero-sub` `.hero-stats` `.hero-stat-num` `.hero-stat-label`
- Split evidence: `.left-panel` `.right-panel` `.red-bar` `.left-rule` `.pain-item` `.accent-border` `.pain-num` `.pain-title` `.pain-desc`
- Big stat: `.stat-row` `.stat-divider` `.stat-copy` `.stat-label` `.stat-value`
- Process / diagram: `.disc-header` `.disc-body` `.disc-steps` `.disc-step` `.disc-step-num` `.disc-step-title` `.disc-step-desc` `.disc-diagram` `.diagram-svg`
- Table / code: `.data-table` `.highlight` `.terminal-line`
- Index / grid: `.index-item` `.index-num` `.index-title` `.index-desc` `.feat-grid` `.feat-card` `.feat-key` `.feat-name` `.feat-desc`
- Evidence / CTA: `.inst-blocks` `.inst-block` `.inst-label` `.inst-link` `.cta-block` `.cta-title` `.cta-line` `.cta-echo` `.cta-echo-num` `.cta-echo-label`

### Background Rule
`.slide` 必须设置 `background: #ffffff`。body 为纯白，12 列网格通过 `body::before` 叠加。不使用渐变。

### Style-Specific Rules
- 每页最多一个红色 `#ff3300` 强调元素，不得用于大面积填充
- 标题必须非对称锚定（左或左下），永远不居中
- 无渐变、无阴影、无圆角、无插图
- 使用 Archivo Black (900) + Nunito (400/600) 字体组合
- 硬水平分隔线 `2px solid #0a0a0a`，无装饰曲线或虚线
- Token 名称必须保持为 `--bg` `--bg-dark` `--text` `--text-light` `--text-muted` `--red` `--grid-line`；不要改写成 `--bg-primary` `--text-primary` `--accent`
- `user-content` 12 页 deck 的 P8-P10 必须是步骤 / 网格 / 证据页，不能退化成 3 页连续的单卡 callout 或 pull quote
- CTA 页允许一个局部深色 `.cta-block`，但标题锚点仍然保持左或左下；禁止居中收尾
- CTA 页长标题不得依赖浏览器自然换行；必须符合全局 title-balance 规则，必要时使用 `.cta-line` 显式控行

### Signature Checklist
- [ ] body::before 12 列网格叠加（3% 不透明度）
- [ ] @keyframes fadeIn（staggered delays）
- [ ] .bg-num 背景大序号（25vw Archivo Black 900）
- [ ] CTA 长标题符合全局 title-balance 规则；必要时使用 `.cta-line` 显式控行
- [ ] .content 内容层（z-index: 1）
- [ ] .eyebrow 小标签（uppercase, 0.2em 字间距）
- [ ] .swiss-stat 大数字（Archivo Black 900）
- [ ] .swiss-rule 硬分隔线（2px solid #0a0a0a）
- [ ] .swiss-rule.red 红色分隔线（#ff3300）
- [ ] Token 名称保持为 `--bg` / `--text` / `--red` / `--text-muted`（无别名变量）
- [ ] Swiss panels are direct children of `.slide`（无 `.slide > .slide-content > .left-col/.right-col`）
- [ ] `.bg-num` 和 `.slide-num-label` 作为 `.slide` 直接子元素存在
- [ ] 每页带有 `data-export-role`，值属于 `title_grid / column_content / stat_block / pull_quote / geometric_diagram / data_table / contents_index`
- [ ] 每页最多一个红色强调元素
- [ ] 标题非对称锚定（左或左下）
- [ ] 无渐变、无阴影、无圆角

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

- [ ] White background with faint 12-column grid
- [ ] Archivo Black at 900 weight, uppercase headlines
- [ ] Red `#ff3300` accent on exactly one element per slide
- [ ] Hard horizontal rules (2px solid black)
- [ ] No gradients, no shadows, no rounded corners
- [ ] Asymmetric anchoring — left or bottom-left, never centered

---

## Best For

Corporate presentations · Data reports · Architecture firm decks · Design studio pitches · Swiss/International style showcases · Precise, data-heavy content
