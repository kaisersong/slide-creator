# Terminal Green — Style Reference

Developer-focused, hacker aesthetic — GitHub's dark theme as a presentation. Every slide feels like a genuine terminal session. Content is the interface.

---

## Colors

```css
:root {
    --bg: #0d1117;
    --bg-panel: #161b22;
    --border: #30363d;
    --green: #39d353;
    --green-muted: rgba(57, 211, 83, 0.4);
    --text: #c9d1d9;
    --text-muted: #8b949e;
    --comment: #484f58;
    --yellow: #e3b341;   /* warnings */
    --red: #f85149;      /* errors */
    --blue: #58a6ff;     /* info / links */
}
```

---

## Background

```css
body {
    background: var(--bg);
    font-family: "JetBrains Mono", "Fira Code", monospace;
}

/* Scan lines — fixed overlay at 50% opacity */
.terminal-scanlines {
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
        transparent,
        transparent 2px,
        rgba(0,0,0,0.04) 2px,
        rgba(0,0,0,0.04) 4px
    );
    pointer-events: none;
    opacity: 0.5;
    z-index: 1;
}

/* Blinking cursor */
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
}
.terminal-cursor::after {
    content: '|';
    animation: blink 1s step-end infinite;
    color: var(--green);
}
```

---

## Typography

```css
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

/* Every element: JetBrains Mono — no exceptions */
.term-title {
    font-family: "JetBrains Mono", monospace;
    font-size: clamp(20px, 3.5vw, 40px);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--green);
    line-height: 1.2;
}

.term-body {
    font-family: "JetBrains Mono", monospace;
    font-size: clamp(12px, 1.3vw, 14px);
    font-weight: 400;
    color: var(--text);
    line-height: 1.75;
}

.term-prompt {
    color: var(--green-muted);
}
.term-prompt::before { content: '$ '; }

.term-comment {
    color: var(--comment);
}

.term-warning {
    color: var(--yellow);
}

.term-error {
    color: var(--red);
}

.term-info {
    color: var(--blue);
}

.term-label {
    font-family: "JetBrains Mono", monospace;
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-muted);
}
```

---

## Named Layout Variations

### 1. Boot Sequence

Title slide. ASCII box border around slide/project name. Below: line-by-line startup log — `[  OK  ] Loaded module...` in small mono. Last line: `> _` with blinking cursor. Feels like system initialization.

### 2. Command Output

Large `$ command --flags` in `--green` on line 1. Below: multi-line output in `--text`. 2–3 lines highlighted with `--bg-panel` row background. Bottom: next `$ ` prompt + blinking cursor.

### 3. Progress Board

Section title top. Below: 5–7 rows, each: label left, ASCII bar `[████████░░]` center, `nn%` right. Green = complete, yellow = in-progress, muted = pending. Scan lines at full opacity.

### 4. File Tree

ASCII directory structure, left-aligned. `├── `, `└── `, `│   ` in `--text-muted`. File names in `--text`. Key file highlighted in `--green`. One annotation `# ← this one` comment on highlighted line.

### 5. Diff View

`BEFORE` / `AFTER` headers in mono panels side by side. `+` prefix lines in green, unchanged lines in muted. No red deletion lines — frame changes as purely positive. Column rule `1px --border`.

### 6. Log Stream

Timestamp column `HH:MM:SS` left in `--comment`, level badge `INFO`/`WARN` center, message right. 8–10 lines. One `WARN` line in yellow. Last line: the key insight in `--green` 700. Scan line overlay.

### 7. EOF

Minimal closing. Centered. `exit 0` or `^D` in 4rem mono, `--green`. Below: `# thanks` in `--comment`. Blinking cursor. Nothing else. Feels like a respectful shell session ending.

---

## Components

```css
/* Panel borders */
.term-panel {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: clamp(12px, 2vw, 18px);
}

/* Highlighted row */
.term-highlight {
    background: var(--bg-panel);
    padding: 4px 8px;
    border-radius: 4px;
}

/* ASCII bar progress */
.term-bar {
    font-family: "JetBrains Mono", monospace;
    color: var(--green);
}
```

---

## Signature Elements

### CSS Overlays
- `body::before`: CRT 扫描线 — `repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,255,65,0.01) 2px, rgba(0,255,65,0.01) 4px)`，`position: fixed; inset: 0; z-index: 9999; pointer-events: none`
- `body::after`: CRT 暗角 — `box-shadow: inset 0 0 120px rgba(0,0,0,0.6), inset 0 0 40px rgba(0,255,65,0.04)`，`position: fixed; inset: 0; z-index: 9998; pointer-events: none`

### Animations
- `@keyframes blink`: 闪烁光标 — `0%, 100% { opacity: 1; } 50% { opacity: 0; }`
- `@keyframes lineReveal`: 逐行出现 — `from { opacity: 0; max-height: 0; } to { opacity: 1; max-height: 3rem; }`
- `@keyframes glow`: 辉光脉冲 — `0%, 100% { text-shadow: 0 0 8px rgba(57,211,83,0.6); } 50% { text-shadow: 0 0 20px rgba(57,211,83,0.9), 0 0 40px rgba(57,211,83,0.4); }`

### Required CSS Classes
- `.terminal-block`: 代码块容器 — `background: var(--bg-panel); border: 1px solid rgba(57,211,83,0.2); border-left: 3px solid var(--green); padding: 0.8-1.2rem;`
- `.pain-list`: 痛点列表 — `list-style: none; li::before { content: '✗'; color: var(--red); }`
- `.steps`: 步骤卡片 — `display: flex; flex-direction: column; gap: 0.8-1.2rem;` 每个 step 有 panel 背景 + 绿色序号
- `.preset-grid`: 标签云 — `display: flex; flex-wrap: wrap; gap: 0.5rem;` 每个 tag 有绿色边框 + 半透明背景
- `.feature-grid`: 功能卡片网格 — `display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));` 卡片顶部 2px 绿色边框
- `.boot-lines`: 启动序列容器 — 4 行，每行使用 lineReveal 动画 staggered (0.3s, 0.8s, 1.3s, 1.8s)
- `.stat-row`: 数据统计行 — `display: flex; gap: 1.5-3rem;` 蓝色数值 + 绿色标签
- `.cta-block`: CTA 命令块 — `background: rgba(57,211,83,0.08); border: 1px solid rgba(57,211,83,0.4);` 内部命令使用 glow 动画
- `.cursor`: 闪烁光标 — `display: inline-block; color: var(--green); animation: blink 1s step-end infinite;`
- `.slide-num`: 页码 — `font-size: var(--small-size); color: var(--green); letter-spacing: 0.1em;`
- `.label`: 小标签 — `font-size: var(--small-size); color: var(--green); letter-spacing: 0.12em; opacity: 0.8;`
- `.rule`: 分隔线 — `border: none; border-top: 1px solid rgba(57,211,83,0.2);`
- `.how-steps`: 纵向流程图 — `display: flex; flex-direction: column; gap: 1-1.5rem;` 绿色序号 + 标题 + 灰色描述

### Background Rule（R21 迁移）
`.slide` 必须设置 `background: var(--bg)`。body 无渐变，纯色背景。CRT 叠加层通过 body::before/::after 实现。

### Style-Specific Rules
- 所有元素必须使用 JetBrains Mono 字体，无例外
- 不使用 Google Fonts 以外的字体
- Terminal 语法使用 `[01/08] > BOOT_SEQUENCE` 格式，非 `1/8` 或 `Slide 1`

### Signature Checklist
- [ ] body::before CRT 扫描线（绿色 tint）
- [ ] body::after CRT 暗角（box-shadow）
- [ ] @keyframes blink（闪烁光标）
- [ ] @keyframes lineReveal（逐行出现，仅标题页）
- [ ] @keyframes glow（h1 辉光脉冲）
- [ ] .cursor 闪烁光标元素
- [ ] .terminal-block 代码块容器
- [ ] .pain-list 痛点列表（红色 ✗）
- [ ] .steps 步骤卡片
- [ ] .preset-grid 标签云
- [ ] .feature-grid 功能卡片网格
- [ ] .boot-lines 启动序列容器（标题页）
- [ ] .stat-row 数据统计行
- [ ] .cta-block CTA 命令块
- [ ] .how-steps 纵向流程图
- [ ] .slide-num 页码（terminal 语法）
- [ ] .label 小标签
- [ ] .rule 分隔线
- [ ] 启动序列 lineReveal staggered timing (0.3s, 0.8s, 1.3s, 1.8s)

---

## Animation

```css
.reveal {
    opacity: 0;
    transition: opacity 0.3s ease;
}
.reveal.visible { opacity: 1; }
.reveal:nth-child(1) { transition-delay: 0.05s; }
.reveal:nth-child(2) { transition-delay: 0.1s; }
.reveal:nth-child(3) { transition-delay: 0.15s; }
```

---

## Style Preview Checklist

- [ ] Dark `#0d1117` background
- [ ] JetBrains Mono on every element — no exceptions
- [ ] Green `#39d353` for titles and key text
- [ ] Scan lines overlay visible
- [ ] At least one terminal layout pattern used
- [ ] Blinking cursor on appropriate slides
- [ ] No pure black background — using `#0d1117`

---

## Best For

Developer tools · API documentation · DevOps presentations · Technical architecture · Security talks · Hackathon pitches · Engineering team updates
