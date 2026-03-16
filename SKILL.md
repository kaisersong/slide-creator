---
name: slide-creator
description: Create beautiful, zero-dependency HTML presentations that run entirely in the browser — no npm, no build tools. 21 curated style presets with named layout variations, visual style discovery with live previews, viewport-fitted slides, inline browser editing, Presenter Mode, and optional PPTX export. Content-type routing suggests the best style for pitch decks, dev docs, data reports, and more. Supports --plan (outline), --generate (HTML from plan), and --export pptx flags.
version: 2.0.0
metadata: {"openclaw":{"emoji":"🎞","os":["darwin","linux","windows"],"homepage":"https://github.com/kaisersong/slide-creator","requires":{"bins":["python3"]},"install":[{"id":"pillow","kind":"uv","package":"Pillow","label":"Pillow (image processing)"},{"id":"python-pptx","kind":"uv","package":"python-pptx","label":"python-pptx (PPT import/export)"},{"id":"playwright","kind":"uv","package":"playwright","label":"Playwright (pixel-perfect PPTX export via system Chrome)"}]}}
---

# Slide Creator

Generate zero-dependency HTML presentations that run entirely in the browser.

## Core Philosophy

1. **Zero Dependencies** — Single HTML files with inline CSS/JS. No npm, no build tools.
2. **Show, Don't Tell** — Generate visual style previews; people can't articulate design preferences until they see options.
3. **Distinctive Design** — Avoid generic AI aesthetics (Inter font, purple gradients, predictable heroes).
4. **Viewport Fitting** — Slides fit exactly in the viewport. Overflowing content gets split, not squished.
5. **Plan Before Generate** — `--plan` creates an outline; `--generate` produces HTML from it.

---

## Command Routing

Parse the invocation first, then load only what that command needs:

| Command | What to load | What to do |
|---------|-------------|------------|
| `--plan [prompt]` | `references/planning-template.md` | Create PLANNING.md. Stop — no HTML. |
| `--generate` | `references/html-template.md` + chosen style file + `references/base-css.md` | Read PLANNING.md, generate HTML. |
| `--export pptx` | Nothing | Run `scripts/export-pptx.py`. |
| No flag (interactive) | `references/workflow.md` | Follow Phase 0–5. |

**Progressive disclosure rule:** each command loads only its required files. `--plan` never touches CSS. `--export` never loads style knowledge. This keeps context focused and fast.

---

## Phase 0: Detect Mode (No-flag entry point)

**Read `references/workflow.md` for the full interactive workflow (Phases 1–5).**

Quick routing before reading workflow.md:

- **PLANNING.md exists** → read it as source of truth, skip to Phase 3 (generation).
- **User has a `.ppt/.pptx` file** → Phase 4 (PPT conversion).
- **User wants to enhance existing HTML** → read it, then enhance. Split slides that overflow.
- **Everything else** → Phase 1 (Content Discovery).

**Content-type → Style hints** (use when user hasn't chosen a style):

| Content type | Suggested styles |
|---|---|
| Data report / KPI dashboard | Data Story, Enterprise Dark, Swiss Modern |
| Business pitch / VC deck | Bold Signal, Aurora Mesh, Enterprise Dark |
| Developer tool / API docs | Terminal Green, Neon Cyber, Neo-Retro Dev Deck |
| Research / thought leadership | Modern Newspaper, Paper & Ink, Swiss Modern |
| Creative / personal brand | Vintage Editorial, Split Pastel, Neo-Brutalism |
| Product launch / SaaS | Aurora Mesh, Glassmorphism, Electric Studio |
| Education / tutorial | Notebook Tabs, Paper & Ink, Pastel Geometry |
| Chinese content | Chinese Chan, Aurora Mesh, Blue Sky |
| Hackathon / indie dev | Neo-Retro Dev Deck, Neo-Brutalism, Terminal Green |

---

## Style Reference Files

Read only the file for the chosen style. Never load all styles into context.

| Style | File |
|-------|------|
| Blue Sky | `references/blue-sky-starter.html` (use as full base — do not rewrite visual CSS) |
| Aurora Mesh | `references/aurora-mesh.md` |
| Chinese Chan | `references/chinese-chan.md` |
| Data Story | `references/data-story.md` |
| Enterprise Dark | `references/enterprise-dark.md` |
| Glassmorphism | `references/glassmorphism.md` |
| Neo-Brutalism | `references/neo-brutalism.md` |
| All other styles | Relevant section in `STYLE-DESC.md` |
| Custom theme | `themes/<name>/reference.md` (use `starter.html` if it exists) |

**For style picker / mood mapping / effect guide** → read `references/style-index.md`.

**For viewport CSS, density limits, CSS gotchas** → read `references/base-css.md`.

---

## Export Mode (`--export pptx`)

1. Find `*.html` in current directory (prefer most recently modified).
2. Run: `python3 <skill-path>/scripts/export-pptx.py <presentation.html> [output.pptx]`
3. Report the PPTX file path and slide count.

Uses system Chrome via Playwright (`--channel chrome`, no Chromium download). Requires only `pip install playwright python-pptx`.

---

## For AI Agents & Skills

Other agents can call this skill programmatically:

```
# From a topic or notes
/slide-creator Make a pitch deck for [topic]

# From a plan file (skip interactive phases)
/slide-creator --generate  # reads PLANNING.md automatically

# Two-step (review the plan before generating)
/slide-creator --plan "Product launch deck for Acme v2"
# (edit PLANNING.md if needed)
/slide-creator --generate

# Export to PPTX after generation
/slide-creator --export pptx
```

---

## Related Skills

- **report-creator** — For long-form scrollable HTML reports (not slides)
- **frontend-design** — For interactive pages that go beyond slides
