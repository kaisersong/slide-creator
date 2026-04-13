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
    --text: #e6edf3;
    --text-muted: #8b949e;
    --comment: #6e7681;
    --yellow: #e3b341;   /* warnings */
    --red: #f85149;      /* errors */
    --blue: #79c0ff;     /* info / links */
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

- **Blinking cursor** — `|` with `animation: blink 1s step-end infinite`
- **Scan lines** — `repeating-linear-gradient` fixed overlay at 50% opacity
- **Prompt prefix** — `$ ` or `> ` in `--green-muted` before any title or command text
- **Status dots** — ● in green/yellow/red for process status
- **Panel borders** — `border: 1px solid var(--border)`, `border-radius: 6px`, no shadows
- Every element: `font-family: 'JetBrains Mono', 'Fira Code', monospace` — no exceptions

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
