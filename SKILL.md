---
name: kai-slide-creator
description: Use when someone wants to CREATE or BUILD a slide deck, presentation, or 幻灯片/PPT/演示文稿 — from scratch, from notes, from a Word/PPTX file, or from an approved outline. Handles Chinese and English equally. Covers pitch decks, product launches, team standups, conference talks, capstone presentations, style previews, and converting existing files to web slides. Use for --plan (outline) and --generate (HTML from plan) flags. Does NOT apply to exporting finished HTML to PPTX/PNG (use kai-html-export), writing speeches, or non-slide documents.
version: 2.5.3
metadata: {"openclaw":{"emoji":"🎞","os":["darwin","linux","windows"],"homepage":"https://github.com/kaisersong/slide-creator","requires":{"bins":["python3"]},"install":[]}}
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

## Generation Contract (Non-Negotiable)

**Every generated HTML file MUST include both of these — no exceptions:**

1. **Presentation Mode** — F5 / ▶ button, fullscreen scaling, `PresentMode` class (`body.presenting`, `#present-btn`, `#present-counter`)
2. **Edit Mode** — top-left hotzone, `✏ Edit` toggle, `contenteditable` on all text, notes panel (`#notes-panel`, `setupEditor()`)

These are defined in `references/html-template.md`. **Read that file before writing any HTML**, regardless of how you entered the skill.

> Omitting either feature is a generation error — the same as missing viewport fitting or broken slide navigation.

---

## Command Routing

Parse the invocation first, then load only what that command needs:

| Command | What to load | What to do |
|---------|-------------|------------|
| `--plan [prompt]` | `references/planning-template.md` | Create PLANNING.md. Stop — no HTML. |
| `--generate` | `references/html-template.md` + chosen style file + `references/base-css.md` | Read PLANNING.md, generate HTML. |
| No flag (interactive) | `references/workflow.md` + **`references/html-template.md` before Phase 3** | Follow Phase 0–5. |
| Content + style given directly | `references/html-template.md` + style file + `references/base-css.md` | Generate immediately — no Phase 1/2 needed. |

**Progressive disclosure rule:** each command loads only its required files. `--plan` never touches CSS. This keeps context focused and fast.

---

## Phase 0: Detect Mode (No-flag entry point)

**Read `references/workflow.md` for the full interactive workflow (Phases 1–5).**

Quick routing before reading workflow.md:

- **PLANNING.md exists** → read it as source of truth, skip to Phase 3. Load `references/html-template.md` before generating.
- **User provides source content + style directly** (e.g. a .txt/.md file + style name) → skip Phase 1/2. Load `references/html-template.md` + style file + `references/base-css.md`, then generate immediately.
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
/kai-html-export presentation.html                    # image mode (pixel-perfect, default)
/kai-html-export --mode native presentation.html      # native mode (editable text/shapes)
```

---

## Related Skills

- **report-creator** — For long-form scrollable HTML reports (not slides)
- **frontend-design** — For interactive pages that go beyond slides
