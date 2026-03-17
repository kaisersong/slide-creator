# slide-creator

> You have great content — but great content deserves a great presentation. AI can generate slides, but the results are inconsistent and re-rolling gets old fast. Slide-Creator gives you stable, polished output every time: pick a style that fits your audience, and let the model handle the rest. Go grab a coffee ☕

A skill for [Claude Code](https://claude.ai/claude-code) and [OpenClaw](https://openclaw.ai) that generates stunning, zero-dependency HTML presentations.

**v2.1.0** — PPTX/PNG export decoupled to [kai-html-export](https://github.com/kaisersong/kai-html-export). kai-slide-creator now focuses solely on HTML presentation creation — only Pillow required, no Playwright or python-pptx. Progressive disclosure architecture: SKILL.md is a thin command router, full workflow loaded on demand.

English | [简体中文](README.zh-CN.md)

## Live Demo

See what slide-creator produces — open directly in your browser:

- 🇺🇸 [slide-creator intro (English)](https://kaisersong.github.io/slide-creator/demos/intro-en.html) — what the skill is and how it works
- 🇨🇳 [slide-creator 介绍（中文）](https://kaisersong.github.io/slide-creator/demos/intro-zh.html) — 同上，中文版

Both demos above use the Blue Sky style. Click any screenshot below to open the live demo:

<table>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/intro-en.html"><img src="demos/screenshots/blue-sky.png" width="240" alt="Blue Sky"/><br/><b>Blue Sky</b> ✨</a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/bold-signal.html"><img src="demos/screenshots/bold-signal.png" width="240" alt="Bold Signal"/><br/><b>Bold Signal</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/electric-studio.html"><img src="demos/screenshots/electric-studio.png" width="240" alt="Electric Studio"/><br/><b>Electric Studio</b></a></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/creative-voltage.html"><img src="demos/screenshots/creative-voltage.png" width="240" alt="Creative Voltage"/><br/><b>Creative Voltage</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/dark-botanical.html"><img src="demos/screenshots/dark-botanical.png" width="240" alt="Dark Botanical"/><br/><b>Dark Botanical</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/notebook-tabs.html"><img src="demos/screenshots/notebook-tabs.png" width="240" alt="Notebook Tabs"/><br/><b>Notebook Tabs</b></a></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/pastel-geometry.html"><img src="demos/screenshots/pastel-geometry.png" width="240" alt="Pastel Geometry"/><br/><b>Pastel Geometry</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/split-pastel.html"><img src="demos/screenshots/split-pastel.png" width="240" alt="Split Pastel"/><br/><b>Split Pastel</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/vintage-editorial.html"><img src="demos/screenshots/vintage-editorial.png" width="240" alt="Vintage Editorial"/><br/><b>Vintage Editorial</b></a></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/neon-cyber.html"><img src="demos/screenshots/neon-cyber.png" width="240" alt="Neon Cyber"/><br/><b>Neon Cyber</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/terminal-green.html"><img src="demos/screenshots/terminal-green.png" width="240" alt="Terminal Green"/><br/><b>Terminal Green</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/swiss-modern.html"><img src="demos/screenshots/swiss-modern.png" width="240" alt="Swiss Modern"/><br/><b>Swiss Modern</b></a></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/paper-ink.html"><img src="demos/screenshots/paper-ink.png" width="240" alt="Paper &amp; Ink"/><br/><b>Paper &amp; Ink</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/aurora-mesh.html"><img src="demos/screenshots/aurora-mesh.png" width="240" alt="Aurora Mesh"/><br/><b>Aurora Mesh</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/enterprise-dark.html"><img src="demos/screenshots/enterprise-dark.png" width="240" alt="Enterprise Dark"/><br/><b>Enterprise Dark</b></a></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/glassmorphism.html"><img src="demos/screenshots/glassmorphism.png" width="240" alt="Glassmorphism"/><br/><b>Glassmorphism</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/neo-brutalism.html"><img src="demos/screenshots/neo-brutalism.png" width="240" alt="Neo-Brutalism"/><br/><b>Neo-Brutalism</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/chinese-chan.html"><img src="demos/screenshots/chinese-chan.png" width="240" alt="Chinese Chan"/><br/><b>Chinese Chan</b></a></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/data-story.html"><img src="demos/screenshots/data-story.png" width="240" alt="Data Story"/><br/><b>Data Story</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/intro-modern-newspaper.html"><img src="demos/screenshots/modern-newspaper.png" width="240" alt="Modern Newspaper"/><br/><b>Modern Newspaper</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/intro-neo-retro-dev.html"><img src="demos/screenshots/neo-retro-dev.png" width="240" alt="Neo-Retro Dev Deck"/><br/><b>Neo-Retro Dev Deck</b></a></td>
</tr>
</table>

Every demo uses the same content (slide-creator's own introduction) — making it easy to compare how the same topic looks across completely different design philosophies.

---

## Features

- **Two-stage workflow** — `--plan` to outline, `--generate` to produce
- **21 design presets** — Bold Signal, Blue Sky, Modern Newspaper, Neo-Retro Dev Deck, and more — each with named layout variations
- **Content-type routing** — Automatically suggests the best style for pitch decks, dev tools, data reports, editorial, and more
- **Style discovery** — Generate 3 visual previews before committing to a style
- **Presenter Mode** — Press `P` to open a synced speaker window: notes, timer, slide counter, prev/next nav; window height auto-adapts to notes length
- **Inline SVG diagrams** — Flowcharts, timelines, bar charts, comparison grids, org charts — no Mermaid.js, no external libs
- **Custom theme system** — Drop a `reference.md` into `themes/your-theme/` to add your own design preset; `starter.html` optional for complex visual systems
- **Blue Sky starter template** — Complete boilerplate so models never mis-implement the visual system
- **Image pipeline** — Auto-evaluate and process assets (Pillow)
- **PPT import** — Convert `.pptx` files to web presentations
- **PPTX / PNG export** — via [kai-html-export](https://github.com/kaisersong/kai-html-export) (`clawhub install kai-html-export`)
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
clawhub install kai-slide-creator

# Or manually
git clone https://github.com/kaisersong/slide-creator ~/.openclaw/skills/slide-creator
```

> ClawHub page: https://clawhub.ai/skills/kai-slide-creator

OpenClaw will automatically detect and install dependencies (Pillow) on first use.

---

## Usage

```
/slide-creator --plan       # Analyze content + resources/, create PLANNING.md
/slide-creator --generate   # Generate HTML presentation from PLANNING.md
/slide-creator              # Start from scratch (interactive style discovery)
/kai-html-export            # Export to PPTX or PNG (separate skill)
```

## Requirements

| Dependency | Purpose | Auto-installed (OpenClaw) |
|-----------|---------|--------------------------|
| Python 3 + `Pillow` | Image processing during generation | ✅ via uv |

Node.js is not required.

**Claude Code users** — install manually:
```bash
pip install Pillow
```

For PPTX or PNG export, install [kai-html-export](https://github.com/kaisersong/kai-html-export):
```bash
clawhub install kai-html-export   # or: pip install playwright python-pptx
```

## Output

Single-file `presentation.html` — zero dependencies, runs entirely in the browser.

Optionally generates `PRESENTATION_SCRIPT.md` (speaker notes). For PPTX/PNG export, use [kai-html-export](https://github.com/kaisersong/kai-html-export).

---

## Inline Editing

Every generated presentation includes a built-in text editor — no need to touch the HTML file.

**How to enter edit mode:**

- Hover the **top-left corner** of the screen → an edit button appears, click it
- Or press **`E`** on your keyboard

**In edit mode:**

- Click any text on the slide to edit it directly
- **`Ctrl+S`** (or `Cmd+S` on Mac) — save changes back to the HTML file
- **`Escape`** — exit edit mode without saving

**To enable inline editing**, answer "Yes" when slide-creator asks during setup (it's the recommended default). If you generated a presentation without it, just re-run `/slide-creator --generate` and opt in.

---

## Design Presets

**21 curated styles — no generic AI aesthetics.**

| Preset | Vibe | Best For |
|--------|------|----------|
| **Bold Signal** | Confident, high-impact | Pitch decks, keynotes |
| **Electric Studio** | Clean, professional | Agency presentations |
| **Creative Voltage** | Energetic, retro-modern | Creative pitches |
| **Dark Botanical** | Elegant, sophisticated | Premium brands |
| **Blue Sky** ✨ | Airy, enterprise SaaS | Product launches, tech decks |
| **Notebook Tabs** | Editorial, organized | Reports, reviews |
| **Pastel Geometry** | Friendly, approachable | Product overviews |
| **Split Pastel** | Playful, modern | Creative agencies |
| **Vintage Editorial** | Witty, personality-driven | Personal brands |
| **Neon Cyber** | Futuristic, techy | Tech startups |
| **Terminal Green** | Developer-focused | Dev tools, APIs |
| **Swiss Modern** | Minimal, precise | Corporate, data |
| **Paper & Ink** | Literary, thoughtful | Storytelling |
| **Aurora Mesh** | Vibrant, premium SaaS | Product launches, VC pitch |
| **Enterprise Dark** | Authoritative, data-driven | B2B, investor decks, strategy |
| **Glassmorphism** | Light, translucent, modern | Consumer tech, brand launches |
| **Neo-Brutalism** | Bold, uncompromising | Indie dev, creative manifesto |
| **Chinese Chan** | Still, contemplative | Design philosophy, brand, culture |
| **Data Story** | Clear, precise, persuasive | Business review, KPI, analytics |
| **Modern Newspaper** | Punchy, authoritative, editorial | Business reports, thought leadership |
| **Neo-Retro Dev Deck** | Opinionated, technical, handmade | Dev tool launches, API docs, hackathons |

### Blue Sky

Light sky-blue gradient background (`#f0f9ff → #e0f2fe`) with floating glassmorphism cards and animated ambient orbs. Inspired by a real enterprise AI pitch deck — the CloudHub V12 MVP presentation. Feels like a high-altitude clear day: open, confident, premium.

Signature elements: grainy noise texture overlay · 3 animated blur orbs repositioning per slide · glassmorphism cards with backdrop-filter · 40px tech grid with radial mask · spring-physics horizontal slide transitions · cloud hero effect on title slides.

A complete starter template (`references/blue-sky-starter.html`) ships with the skill — all 10 signature visual elements are pre-built so models only need to fill in slide content.

---

## For AI Agents & Skills

Other agents and skills can call slide-creator programmatically:

```
# From a topic or notes
/slide-creator Make a pitch deck for [topic]

# Two-step: plan first, then generate (supports review in between)
/slide-creator --plan "Product launch deck for Acme v2"
# (edit PLANNING.md if needed)
/slide-creator --generate

# Export to PPTX after generation
/slide-creator --export pptx
```

---

## Design Philosophy

This section explains the design principles behind slide-creator — both as a user-facing tool and as a Claude Code skill.

### 1. Skill as Progressive Disclosure

A skill file is loaded entirely into the AI's context window every time it's invoked. This means skill size directly affects what the AI can focus on.

slide-creator solves this with a **command routing table**: SKILL.md is a thin router (~150 lines) that dispatches each command to the smallest possible set of reference files.

```
--plan        → references/planning-template.md only
--generate    → references/html-template.md + one style file + references/base-css.md
--export pptx → runs a script, loads nothing
interactive   → references/workflow.md (full Phase 1–5)
style picker  → references/style-index.md (21 presets + mood mapping)
```

**The result:** a `--plan` invocation never touches CSS. A `--generate` run never loads the other 20 style descriptions. An `--export` call loads nothing at all — it just runs a Python script.

This is progressive disclosure applied to AI context management: **reveal information at the moment it's needed, not before.** The same principle that makes good UX design also makes good AI skill design.

### 2. Show, Don't Tell: Visual Style Discovery

Most people cannot articulate design preferences in words until they see examples. Asking "do you want minimalist or bold?" produces vague answers. Generating three 50-line HTML previews and asking "which of these?" produces an instant reaction.

Phase 2 is designed around this insight. The "wow moment" — when someone sees their own content title rendered in three completely different aesthetic directions — turns an abstract choice into a visceral one. The preview files are deliberately tiny (~50 lines each) and self-contained, so they generate in seconds.

This is why the skill description says "Show, Don't Tell" rather than "21 themes available." Features don't create engagement; the experience of choosing creates engagement.

### 3. Viewport Fitting as a First-Class Constraint

A presentation slide that scrolls mid-viewing is broken. This sounds obvious but is easy to violate when generating HTML — if you put too much content on a slide, the browser will just let it overflow.

slide-creator treats viewport fitting as a **non-negotiable constraint** rather than a best practice:

- Every `.slide` must have `height: 100vh; overflow: hidden;`
- Content density limits are specified per slide type (e.g., max 6 bullets, max 6 grid cards)
- When content would overflow, the rule is always: **split the slide, don't squish**

The base CSS (`references/base-css.md`) uses `clamp()` for all sizes so they scale gracefully from landscape phones to 4K displays. This is also why the CSS gotchas section exists — `calc(-1 * clamp(...))` vs `-clamp(...)` is a silent failure that has no console error and causes layouts to break invisibly.

### 4. Custom Theme System: Composable Design Language

The `themes/` directory lets any user extend slide-creator with their own brand style. Drop in a `reference.md` describing the visual system, and it immediately appears as a "Custom: folder-name" option in the style picker.

The two-file convention (`reference.md` + optional `starter.html`) mirrors the Blue Sky pattern: `reference.md` describes the design language (colors, typography, component classes), while `starter.html` is a pre-built boilerplate for complex visual systems that would be hard to reconstruct from prose alone.

This separation means simple custom themes need only one file, while complex ones (with animated backgrounds, custom JS, non-trivial layout systems) can ship a complete working template.

### 5. Content-Type Routing as Intelligent Defaults

The 21-preset library is large enough to be expressive but small enough to be curated. Rather than asking users to browse all 21 options, slide-creator maps content types to style recommendations:

```
Data report / KPI dashboard → Data Story, Enterprise Dark, Swiss Modern
Business pitch / VC deck    → Bold Signal, Aurora Mesh, Enterprise Dark
Developer tool / API docs   → Terminal Green, Neon Cyber, Neo-Retro Dev Deck
```

This routing table in SKILL.md serves two audiences simultaneously: human users who want a sensible starting point, and AI agents calling the skill programmatically (where the agent may know the content type but not which style to choose).

---

## Compatibility

| Platform | Version | Install path |
|---------|---------|-------------|
| Claude Code | any | `~/.claude/skills/slide-creator/` |
| OpenClaw | ≥ 0.9 | `~/.openclaw/skills/slide-creator/` |
