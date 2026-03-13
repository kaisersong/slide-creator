---
name: slide-creator
description: Create beautiful, animation-rich HTML presentations that run entirely in the browser — no npm, no build tools. Generates polished single-file slide decks with visual style discovery, responsive viewport fitting, and optional PPTX export. Use whenever someone asks to make a presentation, create slides, build a pitch deck, convert a PPT/PPTX to web, or prepare slides for a talk or demo — even if they don't mention HTML. Also use for planning a deck outline first (`--plan`), generating HTML from a plan (`--generate`), or exporting to PowerPoint (`--export pptx`).
version: 1.4.1
metadata: {"openclaw":{"emoji":"🎞️","os":["darwin","linux"],"homepage":"https://github.com/kaisersong/slide-creator","requires":{"bins":["python3"]},"install":[{"id":"pillow","kind":"uv","package":"Pillow","label":"Pillow (image processing)"},{"id":"python-pptx","kind":"uv","package":"python-pptx","label":"python-pptx (PPT import/export)"},{"id":"playwright","kind":"uv","package":"playwright","label":"Playwright (pixel-perfect PPTX export via system Chrome)"}]}}
---

# Slide Creator

Generate zero-dependency HTML presentations that run entirely in the browser. This skill guides users from raw ideas to a polished, animated slide deck — using visual style discovery ("show, don't tell") to nail the aesthetic before writing a line of code.

## Core Philosophy

1. **Zero Dependencies** — Single HTML files with inline CSS/JS. No npm, no build tools.
2. **Show, Don't Tell** — People can't articulate design preferences until they see options. Generate visual previews rather than asking abstract questions like "do you want minimalist or bold?"
3. **Distinctive Design** — Avoid generic AI aesthetics (Inter font, purple gradients, predictable heroes). Every deck should feel custom-crafted.
4. **Viewport Fitting** — Slides must fit exactly in the viewport with no scrolling. Content that overflows gets split across slides, not squished. A presentation that scrolls mid-slide is broken — this is why we enforce density limits.
5. **Plan Before Generate** — For complex decks, `--plan` creates a PLANNING.md outline first; `--generate` then produces HTML. Separating thinking from execution leads to better structure and less backtracking.

## Command Flags

Parse the invocation to determine mode:

- **`--plan [prompt]`** — Planning mode. Inspect `resources/`, analyze the prompt, create `PLANNING.md`. **Stop — do NOT generate HTML.**
- **`--generate [instructions]`** — Generation mode. Read `PLANNING.md` if present (skip Phase 1/2 questions), then generate HTML.
- **`--export pptx [--scale N]`** — Export the most recently modified HTML as PPTX via the bundled script. Requires Node ≥ 18.
- **No flag** — Auto-detect mode (Phase 0).

---

## Planning Mode (`--plan`)

1. Scan `resources/` — read text/markdown files, note images. Tell the user what was found (or "Planning from prompt only" if empty).
2. Extract: topic, audience, tone, language, slide count, goals from the prompt.
3. Draft the plan following [references/planning-template.md](references/planning-template.md).
4. Save as `PLANNING.md` in the working directory.
5. Present slide count, structure, and key decisions. Ask for approval.
6. **Stop. Do NOT generate HTML.**

---

## Export Mode (`--export pptx`)

1. Find `*.html` in current directory (prefer most recently modified).
2. Run: `python3 <skill-path>/scripts/export-pptx.py <presentation.html> [output.pptx]`
3. Report the PPTX file path and slide count.

The script uses Playwright with the user's **existing system Chrome** (no Chromium download). It captures pixel-perfect screenshots of each slide and assembles them into a PPTX. Only `pip install playwright python-pptx` required — no Node.js, no 300MB browser download.

---

## Phase 0: Detect Mode

Determine what the user wants:

- **Mode A — New Presentation:** Check for `PLANNING.md` first. If it exists, read it as source of truth and jump directly to Phase 3 — skip Phase 1/2.
- **Mode B — PPT Conversion:** User has a `.ppt/.pptx` file → go to Phase 4.
- **Mode C — Enhance Existing:** Read the existing HTML, understand its structure, then enhance. When adding content, always check viewport fit — if adding would overflow a slide, split the content rather than cramming it in. Proactively split and inform the user.

---

## Phase 1: Content Discovery

**First, silently scan for a `resources/` folder.** If found, read text/markdown files and note images as background context. Don't ask the user to take any action.

Then gather everything in a **single AskUserQuestion call with all 5 questions at once** — collecting everything before submitting avoids back-and-forth.

- **Purpose** (single select): Pitch deck / Teaching+Tutorial / Conference talk / Internal presentation
- **Length** (single select): Short 5-10 / Medium 10-20 / Long 20+
- **Content** (single select): All content ready / Rough notes / Topic only
- **Images** (single select): No images / ./assets / Other (user types path)
- **Inline Editing** (single select): Yes — edit text in-browser, auto-save (Recommended) / No — presentation only

If user has content, ask them to share it after submitting the form.

### Image Evaluation

Skip if user chose "No images." Text-only decks are fully first-class — CSS-generated gradients, shapes, and typography create compelling visuals without any images.

If images are provided:

1. `ls` the folder, then use Read (multimodal) to view each image.
2. For each image: mark `USABLE` or `NOT USABLE` (with reason: blurry, irrelevant, broken) + what it represents + dominant colors + shape.
3. Build a slide outline that co-designs text and images from the start. This is not "plan slides, then fit images in after." Example: 3 usable product screenshots → 3 feature slides anchored by those screenshots.
4. Present the evaluation and proposed outline, then confirm via AskUserQuestion (Looks good → Style B / Adjust images / Adjust outline).

---

## Phase 2: Style Discovery

Most people can't articulate design preferences in words. Generate 3 mini visual previews and let them react — this is the "wow moment" of the skill.

### Style Path

Ask via AskUserQuestion:
- **"Show me options"** → ask mood question → generate 3 previews based on answer
- **"I know what I want"** → show preset picker (Bold Signal / Dark Botanical / Notebook Tabs / Pastel Geometry — with "Other" option for full list)

**Available Presets** (full details in [STYLE-DESC.md](STYLE-DESC.md)):

| Preset | Vibe | Best For |
|--------|------|----------|
| Bold Signal | Confident, high-impact | Pitch decks, keynotes |
| Electric Studio | Clean, professional | Agency presentations |
| Creative Voltage | Energetic, retro-modern | Creative pitches |
| Dark Botanical | Elegant, sophisticated | Premium brands |
| Notebook Tabs | Editorial, organized | Reports, reviews |
| Pastel Geometry | Friendly, approachable | Product overviews |
| Split Pastel | Playful, modern | Creative agencies |
| Vintage Editorial | Witty, personality-driven | Personal brands |
| Neon Cyber | Futuristic, techy | Tech startups |
| Terminal Green | Developer-focused | Dev tools, APIs |
| Swiss Modern | Minimal, precise | Corporate, data |
| Paper & Ink | Literary, thoughtful | Storytelling |

**Mood → Preset mapping:**

| Mood | Style Options |
|------|---------------|
| Impressed/Confident | Bold Signal, Electric Studio, Dark Botanical |
| Excited/Energized | Creative Voltage, Neon Cyber, Split Pastel |
| Calm/Focused | Notebook Tabs, Paper & Ink, Swiss Modern |
| Inspired/Moved | Dark Botanical, Vintage Editorial, Pastel Geometry |

### Generate Previews

Create 3 mini HTML files in `.claude-design/slide-previews/` (style-a/b/c.html). Each is a single title slide (~50-100 lines, self-contained) demonstrating typography, color palette, and animation style.

If a USABLE logo was found in Step 1.2, embed it (base64) into each preview — seeing their own brand in 3 different aesthetics makes the choice feel personal, not abstract.

Never use: Inter/Roboto/Arial as display fonts, generic purple-on-white gradients, predictable centered hero layouts.

Present the 3 files with a one-sentence description each, then ask via AskUserQuestion which they prefer (Style A / B / C / Mix elements).

---

## Phase 3: Generate Presentation

Generate the presentation based on content from Phase 1 and style from Phase 2. If PLANNING.md exists, it's the source of truth — skip Phases 1 and 2.

### If Blue Sky style is selected → use the starter template

**Read [references/blue-sky-starter.html](references/blue-sky-starter.html) and use it as the base.**

All 10 signature visual elements (orbs, noise texture, grid, glassmorphism, spring-physics horizontal track, gradient text, cloud hero, pill dots, counter, entrance animation) are already implemented in that file. You only need to:

1. Set `--slide-count` in `:root` to your actual slide count
2. Replace the example slides in `#track` with your content, following the slide-type patterns in the comment block
3. Fill the `orbPositions` array in JS — one `[l1,t1,s1, l2,t2,s2, l3,t3,s3]` entry per slide

Do **not** rewrite the visual system CSS. Do **not** change the track/slide layout. Content goes inside `.slide` wrappers using the pre-built component classes: `.g` (glass card), `.gt` (gradient text), `.pill`, `.stat`, `.divider`, `.cols2/3/4`, `.ctable`, `.co` (amber callout), `.warn` (red warning), `.info` (blue info), `.layer` (org row), `ul.bl` (bullet list).

### For all other styles → read the standard references

**Read [references/html-template.md](references/html-template.md)** — it contains the required HTML structure, JavaScript patterns, animation recipes, and edit button implementation.

**Also read [STYLE-DESC.md](STYLE-DESC.md)** for viewport fitting CSS, responsive breakpoints, style preset details, and CSS gotchas (especially: never negate CSS functions directly — use `calc(-1 * clamp(...))` not `-clamp(...)`).

### Viewport Fitting

Each slide must equal exactly one viewport height (`100vh` / `100dvh`). When content doesn't fit, split it across slides — never allow scrolling within a slide. This is what separates a polished presentation from a broken one.

**Content density limits:**

| Slide Type | Maximum |
|------------|---------|
| Title slide | 1 heading + 1 subtitle |
| Content slide | 1 heading + 4-6 bullets |
| Feature grid | 1 heading + 6 cards max (2×3 or 3×2) |
| Code slide | 1 heading + 8-10 lines |
| Quote slide | 1 quote (3 lines max) + attribution |
| Image slide | 1 heading + 1 image (max 60vh height) |

When in doubt → split the slide.

### Image Pipeline (skip if no images)

For each USABLE image from Step 1.2, determine processing needed (circular crop for logos, resize for large files, padding for screenshots needing breathing room) and run it with Pillow. Reference images with relative paths (`assets/...`) — don't base64 encode unless the user explicitly wants a fully self-contained file.

Rules:
- Never repeat an image across slides (logos may bookend title + closing)
- Always add style-matched CSS framing (border/glow matching the style's accent color) when image colors clash with the palette

### Code Quality

- Comment every section: what it does, why it exists, how to modify it
- Semantic HTML (`<section>`, `<nav>`, `<main>`)
- ARIA labels on nav elements and interactive controls
- `@media (prefers-reduced-motion: reduce)` support

---

## Phase 4: PPT Conversion

Read [references/pptx-extraction.md](references/pptx-extraction.md) for the Python extraction script.

1. Run the extraction script to get slides_data (title, content, images, notes per slide)
2. Present extracted structure to user, confirm it looks right
3. Run Phase 2 (Style Discovery) with extracted content in mind
4. Generate HTML preserving all text, images (from `assets/`), and slide order. Add speaker notes as HTML comments if present.

---

## Phase 5: Delivery

1. **Clean up:** delete `.claude-design/slide-previews/` if it exists.
2. **Generate speaker notes** if deck has 8+ slides or was created from PLANNING.md:
   - Create `PRESENTATION_SCRIPT.md` with 2-4 sentences per slide: what to say, emphasis points, transition cue.
3. **Open:** `open [filename].html`
4. **Summarize:**

```
Your presentation is ready!

📁 File: [filename].html
🎨 Style: [Style Name]
📊 Slides: [count]

Navigation: Arrow keys or Space · Scroll or swipe · Click dots to jump

To customize: edit :root variables at the top of the CSS for colors, fonts, and spacing.

To export as PPTX: run `/slide-creator --export pptx` (requires Node.js ≥ 18)
```

If inline editing was opted in: mention hovering the top-left corner or pressing `E` to enter edit mode.

---

## Effect → Feeling Guide

| Feeling | Techniques |
|---------|-----------|
| Dramatic/Cinematic | Slow fade-ins 1-1.5s, dark backgrounds, full-bleed images, parallax |
| Techy/Futuristic | Neon glow, particle canvas, grid patterns, monospace accents, glitch text effects |
| Playful/Friendly | Bouncy easing, large rounded corners, pastels, floating/bobbing animations |
| Professional | Subtle 200-300ms animations, clean sans-serif, minimal decoration, data-focus |
| Calm/Minimal | Very slow motion, high whitespace, muted palette, generous padding, serif type |
| Editorial | Strong typography hierarchy, pull quotes, serif headlines, one accent color |

---

## Example: New Presentation

1. "Make a pitch deck for my AI startup"
2. Single form → purpose=pitch, length=medium, content=rough notes, images=./assets, editing=yes
3. User shares notes; skill evaluates assets (4 USABLE, 1 blurry — excluded with explanation)
4. Slide outline co-designed around text + images; confirmed via AskUserQuestion
5. Mood=Impressed+Excited → 3 previews generated → user picks Neon Cyber
6. Pillow processes images; HTML generated with full viewport CSS + JS suite
7. Browser opens; user requests tweaks; final deck delivered

## Example: PPT Conversion

1. "Convert slides.pptx to a web presentation"
2. Run extraction script → present extracted content → user confirms
3. Style Discovery (Phase 2) → HTML generation with preserved assets
4. Final presentation delivered

---

## Related Skills

- **frontend-design** — For interactive pages that go beyond slides
- **design-and-refine:design-lab** — For iterating on component designs
