# slide-creator

A [Claude Code](https://claude.ai/claude-code) skill for generating stunning, zero-dependency HTML presentations.

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

## Install

```bash
git clone https://github.com/kaisersong/slide-creator ~/.claude/skills/slide-creator
```

Restart Claude Code. The skill is now available as `/slide-creator`.

## Usage

```
/slide-creator --plan       # Analyze content, create PLANNING.md outline
/slide-creator --generate   # Generate HTML from PLANNING.md
/slide-creator --export pptx  # Export to PowerPoint
/slide-creator              # Start from scratch (interactive)
```

## Requirements

- [Claude Code](https://claude.ai/claude-code)
- Python + `Pillow` (for image processing): `pip install Pillow`
- Node.js + npm (for PPTX export): auto-installed on first use
- `python-pptx` (for PPT import): `pip install python-pptx`

## Output

Single-file `presentation.html` — zero dependencies, runs entirely in the browser.
