# Neon Cyber — Style Reference

Futuristic, techy, high-voltage confidence — Tron lightgrid meets hacker conference keynote. Dark canvas, electric glow, engineered precision.

---

## Colors

```css
:root {
    --bg: #0a0f1c;
    --bg-panel: #0e1525;
    --border-glow: rgba(0, 255, 204, 0.25);
    --cyan: #00ffcc;
    --magenta: #ff00aa;
    --text: #e0f0ff;
    --text-muted: rgba(224, 240, 255, 0.5);
    --grid: rgba(0, 255, 204, 0.04);
}
```

---

## Background

```css
body {
    background: var(--bg);
    font-family: "Clash Display", "Satoshi", -apple-system, sans-serif;
}

/* Grid overlay — 40px spacing, masked to center */
.neon-grid {
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(var(--grid) 1px, transparent 1px),
        linear-gradient(90deg, var(--grid) 1px, transparent 1px);
    background-size: 40px 40px;
    -webkit-mask-image: radial-gradient(ellipse 80% 50% at 50% 50%, #000 70%, transparent 100%);
    mask-image: radial-gradient(ellipse 80% 50% at 50% 50%, #000 70%, transparent 100%);
    pointer-events: none;
    opacity: 0.5;
}
```

---

## Typography

```css
@import url('https://api.fontshare.com/v2/css?f[]=clash-display@600,700&f[]=satoshi@400,500&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap');

.neon-title {
    font-family: "Clash Display", sans-serif;
    font-size: clamp(32px, 6vw, 64px);
    font-weight: 700;
    color: var(--text);
    line-height: 1.05;
    letter-spacing: -0.01em;
}

.neon-title.glow {
    text-shadow: 0 0 16px rgba(0,255,204,0.35), 0 0 48px rgba(0,255,204,0.1);
}

.neon-body {
    font-family: "Satoshi", sans-serif;
    font-size: clamp(13px, 1.4vw, 16px);
    font-weight: 400;
    color: var(--text);
    line-height: 1.6;
}

.neon-mono {
    font-family: "JetBrains Mono", monospace;
    font-size: clamp(10px, 1.1vw, 12px);
    color: var(--text-muted);
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

.neon-label {
    font-family: "Clash Display", sans-serif;
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--cyan);
}
```

---

## Components

```css
/* Corner-cut panel — sci-fi HUD feel */
.neon-panel {
    background: var(--bg-panel);
    border: 1px solid var(--border-glow);
    clip-path: polygon(0 0, calc(100% - 14px) 0, 100% 14px, 100% 100%, 0 100%);
    padding: clamp(16px, 2.5vw, 24px);
    box-shadow: 0 0 16px rgba(0,255,204,0.1);
}

/* Neon glow border */
.neon-glow {
    border: 1px solid rgba(0,255,204,0.25);
    box-shadow: 0 0 16px rgba(0,255,204,0.35), 0 0 48px rgba(0,255,204,0.1);
}

/* Gradient accent divider */
.neon-divider {
    height: 2px;
    background: linear-gradient(90deg, var(--cyan), var(--magenta));
}
```

---

## Named Layout Variations

### 1. Launch Screen

Title centered in `Clash Display` 7rem, cyan `text-shadow` glow. Subtitle in Satoshi below. Animated particle canvas behind (JS canvas, 60 dots, connecting lines < 120px). Bottom: `2px` gradient rule + mono `PRESS SPACE TO CONTINUE`.

### 2. Feature Grid

3-column grid (or 2×3). Each panel: `clip-path` corner cut, section number in mono top-right, SVG icon, feature name in Clash Display, 2-line desc in Satoshi. Hover: `border-glow` intensifies with transition.

### 3. Data Pulse

Left 55%: single KPI number in 8rem cyan with glow. Below: mono uppercase label, SVG trend arrow. Right 45%: inline SVG bar chart (cyan bars, `border-radius: 4px` top only). Faint radial-gradient pulse animation centered on the number.

### 4. Signal Timeline

Center `2px` vertical line, cyan-to-magenta gradient. Left/right alternating content blocks per milestone. Nodes: `10px` circle, cyan fill, glow. Labels in mono above each node. Line draws in via `stroke-dashoffset` animation on slide entry.

### 5. Code Insight

Full-slide terminal panel in `JetBrains Mono`. One key line highlighted with `rgba(0,255,204,0.08)` row background. Comments in `--text-muted`. One `/* ← key insight */` SVG callout arrow. Corner-cut panel edges.

### 6. Split Focus

Left 40%: slightly lighter panel (`--bg-panel`), vertical `2px` cyan rule on right edge, section label + large headline. Right 60%: body text + bullet list with cyan ▸ markers. Top-right: `SYS://SECTION_NAME` in mono 10px.

### 7. Signal Close

Centered headline in cyan glow. Below: 3 CTA/contact panels in a row (bordered, corner-cut). `TRANSMISSION COMPLETE` in mono at very bottom, 30% opacity. Background: particle canvas at reduced opacity.

---

## Signature Elements

### CSS Overlays
- `body::before`: Cyan grid overlay (50px spacing, `rgba(0,255,204,0.03)`) —
  ```css
  body::before { content: ''; position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image: linear-gradient(rgba(0,255,204,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,255,204,0.03) 1px, transparent 1px);
    background-size: 50px 50px; }
  ```
- `body::after`: Scanline overlay (alternating 2px/4px rows) —
  ```css
  body::after { content: ''; position: fixed; inset: 0; z-index: 1; pointer-events: none;
    background: repeating-linear-gradient(0deg, transparent, transparent 2px,
      rgba(0,255,204,0.01) 2px, rgba(0,255,204,0.01) 4px); }
  ```

### Animations
- `@keyframes glitch-1`: Cyan title glitch (clip-path shifts at 92-98% timestamps) — `clip-path: inset(20% 0 60% 0); transform: translate(-4px, 1px)`
- `@keyframes glitch-2`: Magenta/blue title glitch (offset timing, opacity fades) — `clip-path: inset(60% 0 20% 0); transform: translate(4px, -2px)`
- `@keyframes neonPulse`: Cyan text-shadow breathing (20px to 80px glow spread) — `text-shadow: 0 0 20px rgba(0,255,204,0.5), 0 0 40px rgba(0,255,204,0.2)` to `0 0 80px rgba(0,255,204,0.1)`
- `@keyframes magentaPulse`: Magenta text-shadow breathing (same pattern, different color)
- `@keyframes borderPulse`: Card border glow oscillation (1px to 2px box-shadow spread)
- `@keyframes particleDrift`: Floating particles rising from bottom (scale 0 to 1, opacity fade in/out)

### Required CSS Classes
- `.cyber-title`: 主标题 — **必须有 `neonPulse` 动画产生呼吸光晕**（`text-shadow` 从 20px 扩展到 80px），**同时**通过 `data-text` 属性实现 glitch 伪元素叠加。两者缺一不可：光晕 = 基础层呼吸发光，glitch = 伪元素色彩偏移
- `.neon-title.glow`: 静态霓虹光晕 — `text-shadow: 0 0 16px rgba(0,255,204,0.35), 0 0 48px rgba(0,255,204,0.1)`。用于内容页 h2 标题和需要光晕但不需要 glitch 的元素
- `.cyber-label`: Section label in cyan with `neonPulse` animation, uppercase, `letter-spacing: 0.2em`
- `.cyber-heading`: Sub-headline — **基元素本身应有 `.neon-title.glow` 的 text-shadow 光晕**，`.accent` (cyan pulse) 和 `.mg` (magenta pulse) spans 额外加 `neonPulse`/`magentaPulse` 动画
- `.cyber-card`: Terminal-style card with cyan border, `::before` (top accent bar, 40px), `::after` (left accent bar, 40px)
- `.corner-br` / `.corner-tl`: Bottom-right and top-left bracket decorations (1px cyan borders)
- `.particle`: Floating dots (JS-generated, 18 particles, 3 color variants)

### Allowed Components
- Audit coverage: .neon-body .neon-divider .neon-glow .neon-grid .neon-label .neon-mono .neon-panel

### Background Rule
`.slide` sets `background: #0a0f1c` with `z-index: 2`, preventing body gradient from showing through. Body overlays (`::before`/`::after`) are fixed-position and visible behind slides.

### Style-Specific Rules
- **Glitch title requires `data-text` attribute**: `<h1 class="cyber-title" data-text="slide-creator">` — pseudo-elements use `content: attr(data-text)` to create glitch layers
- **No illustrations** — geometric CSS shapes and inline SVG only
- **Code blocks** have a 3px cyan left bar with `neonPulse` animation via `::before`
- **Progress bar** uses cyan-to-magenta gradient with `box-shadow: 0 0 8px rgba(0,255,204,0.6)` glow

### Signature Checklist
- [ ] Dark `#0a0f1c` background with cyan grid + scanline overlays
- [ ] `.cyber-title` 同时有 `neonPulse` 呼吸光晕 AND `data-text` glitch 效果
- [ ] 内容页 h2 标题有 `.neon-title.glow` 静态光晕（text-shadow）
- [ ] `neonPulse` animation on cyan text and borders
- [ ] Corner bracket decorations (`.corner-br` / `.corner-tl`)
- [ ] At least one magenta accent (`.magenta` span or `.mg` class)
- [ ] Floating particles (18 dots, 3 colors)
- [ ] Satoshi for body, Clash Display for headlines, JetBrains Mono for code/labels

---

## Animation

```css
.reveal {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.5s ease, transform 0.5s cubic-bezier(0.16,1,0.3,1);
}
.reveal.visible { opacity: 1; transform: translateY(0); }
.reveal:nth-child(1) { transition-delay: 0.05s; }
.reveal:nth-child(2) { transition-delay: 0.15s; }
.reveal:nth-child(3) { transition-delay: 0.25s; }
```

---

## Style Preview Checklist

- [ ] Dark `#0a0f1c` background with cyan grid overlay
- [ ] Neon glow on borders and key headings
- [ ] Corner-cut panels (clip-path)
- [ ] Cyan `#00ffcc` + magenta `#ff00aa` gradient accent
- [ ] JetBrains Mono for metadata/labels
- [ ] Clash Display for headlines
- [ ] No pure black background — using `#0a0f1c`

---

## Best For

Tech startups · Developer tools · Product launches · AI/ML presentations · Cybersecurity decks · Innovation showcases · Hackathon pitches
