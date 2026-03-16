# Slide Creator — Interactive Workflow (Phase 1–5)

Read this file when running in **no-flag / interactive mode**. For `--plan` read only the Planning Mode section. For `--generate` skip to Phase 3.

---

## Planning Mode (`--plan`)

1. Scan `resources/` — read text/markdown files, note images. Tell the user what was found (or "Planning from prompt only" if empty).
2. Extract: topic, audience, tone, language, slide count, goals from the prompt.
3. Draft the plan following [planning-template.md](planning-template.md).
4. Save as `PLANNING.md` in the working directory.
5. Present slide count, structure, and key decisions. Ask for approval.
6. **Stop. Do NOT generate HTML.**

---

## Phase 1: Content Discovery

**First, silently scan for a `resources/` folder.** If found, read text/markdown files and note images as background context. Don't ask the user to take any action.

Then gather everything in a **single AskUserQuestion call with all 5 questions at once**:

- **Purpose** (single select): Pitch deck / Teaching+Tutorial / Conference talk / Internal presentation
- **Length** (single select): Short 5-10 / Medium 10-20 / Long 20+
- **Content** (single select): All content ready / Rough notes / Topic only
- **Images** (single select): No images / ./assets / Other (user types path)
- **Inline Editing** (single select): Yes — edit text in-browser, auto-save (Recommended) / No — presentation only

> **Default:** Always include inline editing unless user explicitly selects "No". When `--generate` skips Phase 1, include inline editing by default.

If user has content, ask them to share it after submitting the form.

**Language:** Detect from the user's message — never default to a fixed language. Maintain the detected language throughout all slide text including labels, CTAs, and captions. English may appear as secondary annotation text only when the style calls for it.

### Image Evaluation

Skip if user chose "No images." Text-only decks are fully first-class — CSS-generated gradients, shapes, and typography create compelling visuals without any images.

If images are provided:

1. `ls` the folder, then use Read (multimodal) to view each image.
2. For each image: mark `USABLE` or `NOT USABLE` (with reason: blurry, irrelevant, broken) + what it represents + dominant colors + shape.
3. Build a slide outline that co-designs text and images from the start. This is not "plan slides, then fit images in after." Example: 3 usable product screenshots → 3 feature slides anchored by those screenshots.
4. Present the evaluation and proposed outline, then confirm via AskUserQuestion (Looks good / Adjust images / Adjust outline).

---

## Phase 2: Style Discovery

Most people can't articulate design preferences in words. Generate 3 mini visual previews and let them react — this is the "wow moment" of the skill.

### Style Path

Ask via AskUserQuestion:
- **"Show me options"** → ask mood question → generate 3 previews based on answer
- **"I know what I want"** → show preset picker (Bold Signal / Blue Sky / Modern Newspaper / Neo-Retro Dev Deck — with "Other" option for all 21 presets)

**Before showing presets, silently scan `<skill-path>/themes/` for subdirectories.**
Skip any directory whose name starts with `_`. Each remaining subdirectory with a `reference.md` is a custom theme — append as `Custom: <folder-name>` entries.

Read [style-index.md](style-index.md) for the full 21-preset table and mood → preset mapping.

### Generate Previews

Create 3 mini HTML files in `.claude-design/slide-previews/` (style-a/b/c.html). Each is a single title slide (~50-100 lines, self-contained) demonstrating typography, color palette, and animation style.

If a USABLE logo was found in Phase 1, embed it (base64) into each preview.

Never use: Inter/Roboto/Arial as display fonts, generic purple-on-white gradients, predictable centered hero layouts.

Present the 3 files with a one-sentence description each, then ask via AskUserQuestion which they prefer (Style A / B / C / Mix elements).

---

## Phase 3: Generate Presentation

Generate the presentation based on content from Phase 1 and style from Phase 2. If PLANNING.md exists, it's the source of truth — skip Phases 1 and 2.

### Step 1: Load the right references

**If Blue Sky style:** Read [blue-sky-starter.html](blue-sky-starter.html) and use it as the base. All 10 signature visual elements are pre-built — only fill in slide content. Do not rewrite the visual system CSS. Content goes inside `.slide` wrappers using pre-built classes: `.g` (glass card), `.gt` (gradient text), `.pill`, `.stat`, `.divider`, `.cols2/3/4`, `.ctable`, `.co` (amber callout), `.warn`, `.info`, `.layer`, `ul.bl`.

**If a custom theme from themes/:** Read the theme's `reference.md`. If a `starter.html` exists in the theme folder, use it as the base.

**For all other styles:** Read [html-template.md](html-template.md) + [base-css.md](base-css.md). If the style has a dedicated reference file in `references/` (e.g. `aurora-mesh.md`, `enterprise-dark.md`), read that instead of scanning STYLE-DESC.md. Otherwise read the relevant section in STYLE-DESC.md.

### Step 2: Viewport fitting

Each slide must equal exactly one viewport height (`100vh` / `100dvh`). When content doesn't fit, split it across slides — never allow scrolling. See [base-css.md](base-css.md) for density limits and required CSS.

### Step 3: Diagrams (when content calls for a visual relationship)

When a slide needs to show a process, comparison, hierarchy, timeline, or data — generate an **inline SVG diagram** instead of bullet points. Read [diagram-patterns.md](diagram-patterns.md) for ready-to-use templates.

Rules:
- One diagram per slide, never combined with a bullet list
- Use `currentColor` so diagrams inherit the slide's text color automatically
- Apply `--accent` color to the most important element
- **Never use Mermaid.js, Chart.js, or any external library** — inline SVG only

### Step 4: Image pipeline (skip if no images)

For each USABLE image, determine processing needed and run it with Pillow. Reference images with relative paths (`assets/...`).

Rules:
- Never repeat an image across slides (logos may bookend title + closing)
- Always add style-matched CSS framing when image colors clash with the palette

### Step 5: Visual rhythm

Alternate between text-heavy and visual-heavy slides. Three or more consecutive slides with the same layout signal low effort. Vary between: headline-dominant → data/diagram → evidence list → quote or visual break → headline-dominant. Every 4–5 slides, one slide should be nearly empty (a single statement, a big number, or a quote).

### Step 6: Code quality

- Comment every section: what it does, why it exists, how to modify it
- Semantic HTML (`<section>`, `<nav>`, `<main>`)
- ARIA labels on nav elements and interactive controls
- `@media (prefers-reduced-motion: reduce)` support
- No markdown symbols (`#`, `*`, `**`, `_`) in slide text — use `<strong>`, `<em>`, `<h2>`

---

## Phase 4: PPT Conversion

Read [pptx-extraction.md](pptx-extraction.md) for the Python extraction script.

1. Run the extraction script to get slides_data (title, content, images, notes per slide)
2. Present extracted structure to user, confirm it looks right
3. Run Phase 2 (Style Discovery) with extracted content in mind
4. Generate HTML preserving all text, images (from `assets/`), and slide order. Put speaker notes in `data-notes` attributes (not HTML comments) so they work in Presenter Mode.

---

## Phase 5: Delivery

1. **Clean up:** delete `.claude-design/slide-previews/` if it exists.
2. **Embed speaker notes** — every `.slide` section must have a `data-notes="..."` attribute with 2-4 sentences (what to say, key emphasis, transition cue). These power the built-in Presenter Mode.
3. **Generate `PRESENTATION_SCRIPT.md`** if deck has 8+ slides or was created from PLANNING.md.
4. **Open:** `open [filename].html`
5. **Summarize:**

```
Your presentation is ready!

📁 File: [filename].html
🎨 Style: [Style Name]
📊 Slides: [count]

Navigation: Arrow keys or Space · Scroll or swipe · Click dots to jump
Presenter Mode: press P to open the presenter window (notes + timer + controls)

To customize: edit :root variables at the top of the CSS for colors, fonts, and spacing.
To export as PPTX or PNG: `/kai-html-export` (install: clawhub install kai-html-export)
```

Always mention: hover the top-left corner or press `E` to enter edit mode.
