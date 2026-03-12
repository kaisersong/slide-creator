# slide-creator

A skill for [Claude Code](https://claude.ai/claude-code) and [OpenClaw](https://openclaw.ai) that generates stunning, zero-dependency HTML presentations.

**v1.3.0** — PPTX export uses Playwright with your existing system Chrome. Pixel-perfect screenshots, no 300MB Chromium download, no Node.js. Just `pip install playwright python-pptx`.

English | [简体中文](README.zh-CN.md)

## Features

- **Two-stage workflow** — `--plan` to outline, `--generate` to produce
- **12 design presets** — Bold Signal, Neon Cyber, Dark Botanical, and more
- **Style discovery** — Generate 3 visual previews before committing to a style
- **Image pipeline** — Auto-evaluate and process assets (Pillow)
- **PPT import** — Convert `.pptx` files to web presentations
- **PPTX export** — `--export pptx` via puppeteer + pptxgenjs
- **Inline editing** — Edit text in-browser, Ctrl+S to save
- **Viewport fitting** — Every slide fits exactly in 100vh, no scrolling ever
- **Bilingual** — Chinese / English support

---

## Install

### Claude Code

```bash
git clone https://github.com/kaisersong/slide-creator ~/.claude/skills/slide-creator
```

Restart Claude Code. Use as `/slide-creator`.

### OpenClaw

```bash
# Via ClawHub (recommended)
clawhub install html-slide-creator

# Or manually
git clone https://github.com/kaisersong/slide-creator ~/.openclaw/skills/slide-creator
```

> ClawHub page: https://clawhub.ai/skills/html-slide-creator

OpenClaw will automatically detect and install dependencies (Pillow, python-pptx, puppeteer, pptxgenjs) on first use.

---

## Usage

```
/slide-creator --plan       # Analyze content + resources/, create PLANNING.md
/slide-creator --generate   # Generate HTML presentation from PLANNING.md
/slide-creator --export pptx  # Export to PowerPoint
/slide-creator              # Start from scratch (interactive style discovery)
```

## Requirements

| Dependency | Purpose | Auto-installed (OpenClaw) |
|-----------|---------|--------------------------|
| Python 3 + `Pillow` | Image processing | ✅ via uv |
| Python 3 + `python-pptx` | PPT import/export | ✅ via uv |
| Python 3 + `playwright` | PPTX export (uses system Chrome) | ✅ via uv |

Node.js is not required. PPTX export uses your existing Chrome/Edge/Brave — no 300MB Chromium download.

**Claude Code users** — install manually:
```bash
pip install Pillow python-pptx playwright
```

## Output

Single-file `presentation.html` — zero dependencies, runs entirely in the browser.

Optionally exports `PRESENTATION_SCRIPT.md` (speaker notes) and `.pptx`.

---

## Compatibility

| Platform | Version | Install path |
|---------|---------|-------------|
| Claude Code | any | `~/.claude/skills/slide-creator/` |
| OpenClaw | ≥ 0.9 | `~/.openclaw/skills/slide-creator/` |
