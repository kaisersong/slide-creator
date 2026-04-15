# Slide Creator - Interactive Workflow (Phase 1-5)

Read this file when running in **no-flag / interactive mode**. For `--plan` read only the Planning Mode section. For `--generate` skip to Phase 3.

---

## Planning Mode (`--plan`)

### Planning Depth Routing

Default: if the user does not specify a mode, route to `自动` (`Auto` in English UI).

Route to `精修` (`Polish`) when:

- the user explicitly says `精修` or `Polish`
- the request emphasizes thesis, pacing, narrative arc, or page roles
- the deck needs stronger visual lock or brand alignment beyond preset selection
- the user wants page-level image reasoning instead of simple image placement
- the user wants to confirm planning decisions before generation
- the deck should follow a specific visual reference or precedent

Stay in `自动` (`Auto`) when:

- the user wants a quick draft or says "先出一版"
- the content is already prepared and mainly needs design plus rendering
- the request does not require stronger image strategy

`参考驱动` is only an internal branch inside `精修` / `Polish`.

Image intent exists only in `精修` / `Polish`.

If the same source content already has a chosen preset, do not silently switch presets when moving between `自动` and `精修`. Planning depth can deepen structure and page roles, but preset changes require either a user request or a content-type routing reason strong enough to explain explicitly.

Mode label display rule:

- Chinese requests: show `自动` / `精修`
- English requests: show `Auto` / `Polish`
- Keep the underlying two-depth contract the same in both languages

1. Scan `resources/` — read text/markdown files, note images. Tell the user what was found (or "Planning from prompt only" if empty).
2. Extract: topic, audience, tone, language, slide count, goals, and the correct planning depth from the prompt.
3. Draft the plan following [planning-template.md](planning-template.md).
4. In `自动` / `Auto`, keep the plan lightweight: outline, style direction, images as resources, and deliverables only.
5. In `精修` / `Polish`, add deck thesis, narrative arc, page roles, style constraints, and image intent for only the slides that truly need imagery. If the visual lock benefits from references, run `参考驱动` as an internal sub-step here instead of exposing it as a user-facing mode.
6. Save as `PLANNING.md` in the working directory.
7. Add a `Timing` section with estimated `plan`, `generate`, `validate`, `polish`, and `total` ranges.
8. Present slide count, structure, planning depth, timing estimate, and key decisions. Ask for approval.
9. **Stop. Do NOT generate HTML.**

---

## Enhancement Mode (existing HTML)

Use this mode when the user asks to improve an existing HTML deck instead of generating from scratch.

1. Count existing content before adding new text or images.
2. Compare the target slide against the same density limits used for fresh generation.
3. If the slide is already full, split it before appending more bullets, screenshots, or notes.
4. Images added during enhancement must keep viewport-safe constraints such as `max-height: min(50vh, 400px)`.
5. After every modification, verify `.slide` still uses `height: 100vh; height: 100dvh; overflow: hidden;`.
6. Re-check that modified typography and spacing still use `clamp()`-based sizing where required.
7. If a change would exceed density limits, split the slide proactively.
8. Validate the edited deck at a practical presentation size such as 1280x720 before handing it back.

---

## Phase 1: Content Discovery

**First, silently scan for a `resources/` folder.** If found, read text/markdown files and note images as background context. Don't ask the user to take any action.

Before moving into style discovery, detect whether the request should stay in `自动` / `Auto` or switch to `精修` / `Polish` using the Planning Depth Routing rules above. Keep the default path lightweight; only add deeper planning when the request clearly justifies it.

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

In `自动` / `Auto`, stop here — treat images as usable resources, not page-level design jobs.

In `精修` / `Polish`, keep going after the usability pass: decide which slides should have images, what communication task each image serves, and record image intent plus search/reference direction only where it improves the deck.

---

## Phase 2: Style Discovery

Most people can't articulate design preferences in words. Generate 3 mini visual previews and let them react — this is the "wow moment" of the skill.

If the deck is in `精修` / `Polish`, add a short design-lock step before generating previews: define deck thesis, narrative arc, page roles, and style constraints so the previews support the presentation's rhetorical structure rather than acting as disconnected skins.

If the user already approved a preset or PLANNING.md already names one, skip fresh preset routing and keep that preset. Do not reinterpret the same deck into a different theme just because the planning depth changed.

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

Before writing HTML, tell the user the expected end-to-end time window based on planning depth:

- `Auto`: usually ~3-6 minutes
- `Polish`: usually ~8-15 minutes

When running checked-in demos or formal validation, record segmented timing for:

- `plan`
- `generate`
- `validate`
- `polish`
- `total`

### Step 1: Load and integrate references (3-step process)

**Step 1a: Read composition-guide.md** → Get the 12 narrative roles and their layout categories.
The composition guide defines the layout category for each slide role:
- Slide 1 (Hero Cover) = 全屏宣告 (Full-Bleed Statement)
- Slide 2 (Problem Frame) = 分栏证据 (Split Evidence)
- Slide 3 (Style Discovery) = 多选项对比 (Multi-Option)
- Slide 4 (Solution Reveal) = 大数字强调 (Big Stat)
- Slide 5 (Playback Mode) = 功能亮点 (Feature Spotlight)
- Slide 6 (Presenter Mode) = 分屏对比 (Side-by-Side)
- Slide 7 (Edit Mode) = 双列功能卡 (Two-Column Cards)
- Slide 8 (Planning Depths) = 流程步骤 (Process Track)
- Slide 9 (Review System) = 网格检查点 (Grid Checklist)
- Slide 10 (Style Guide) = 推荐网格 (Recommendation Grid)
- Slide 11 (Technical Proof) = 证据列表 (Proof Points)
- Slide 12 (CTA / Close) = 堆叠行动 (Stacked Action)

**Step 1b: Read the selected style's reference file** → Extract:
- Named layout variations (match each to a layout category from Step 1a)
- Signature element CSS (grid overlay / orbs / scan-lines / geometric shapes / etc.)
- Visual tokens (colors, fonts, component classes, background patterns)
- Style Preview Checklist (all items MUST appear in generated HTML)

**Step 1c: Read html-template.md + base-css.md** → Get:
- HTML architecture (scroll-snap, slide structure, present mode, edit mode)
- Animation patterns, responsive breakpoints, density limits

**If Blue Sky style:** Read [blue-sky-starter.html](blue-sky-starter.html) instead. All 10 signature visual elements are pre-built — only fill in slide content. Do not rewrite the visual system CSS.

**If a custom theme from themes/:** Read the theme's `reference.md`. If a `starter.html` exists in the theme folder, use it as the base.

---

### Step 1.5: Map layout categories to style-specific layouts

For each of the 12 slides:

1. Get the layout category from composition-guide.md (Step 1a)
2. Search the style file's `## Named Layout Variations` section for a matching layout
3. If a matching named layout exists → use its HTML structure
4. If no matching named layout exists → use the layout category definition from composition-guide.md to compose the layout from the style's individual components
5. Inject the style's signature elements as direct children of `<section class="slide">` (grid overlays via `.slide::after`, orbs as direct child divs, etc.)
6. Fill content and components with the style's visual tokens

**Architecture note:** Signature elements ARE layout constraints, not a separate injection step. The `.bold-ghost` positioned at the bottom-right, the `.slide-num` at the top-left — these define the spatial composition that all other content responds to.

**CRITICAL: Use the style's full component palette.** Every style provides multiple component patterns. Do NOT put every piece of content inside a generic card with bullets. Each slide should use 2-3 distinct component types. If every slide looks like "card + bullet list," redesign at least half before writing HTML.

**Exception for minimalist styles:** Chinese Chan, Paper & Ink, and similar minimalist styles may repeat the core narrow-column layout. For these styles, diversity comes from content treatment (different decorative elements, typography scale) rather than layout structure.

---

### Step 1.6: Style value extraction (MANDATORY)

**Before writing any CSS**, extract ALL theme values from the style reference file:

1. **Colors** — background, text, accent, semantic colors (success/error/etc.)
2. **Fonts** — display font, body font, CDN URL (combine into SINGLE Google Fonts link with `&display=swap`)
3. **Typography** — title/body sizes, line-heights, letter-spacing
4. **Components** — any style-specific classes (e.g. Data Story's `.ds-kpi`, `.ds-kpi-card`)
5. **Background pattern** — grid / gradient / orbs / scan-lines / halftone (MUST be present in generated HTML)
6. **Checklist** — each style file has a "Style Preview Checklist" section; these items MUST appear in the generated HTML

**Font loading rule:** Combine ALL font families into a SINGLE `<link>` tag with `&display=swap`. Add `body { background-color: [style's bg color]; }` as the first rule inside `<style>` so the page never flashes white while fonts load.

**Critical:** The template `html-template.md` uses placeholder values (`[from style file]`). **Never emit these placeholders into the final HTML.** Every color, font, and token must resolve to an actual value from the style reference file.

---

### Architectural Firewall — Read Before Generating

Blue Sky is the **only** style that uses `#stage` (fixed container) + `#track` (flex row) + `translateX` navigation. This architecture is **exclusive** to `blue-sky-starter.html`. All other 20 styles **MUST** use `html-template.md`'s architecture:
- `<html>` with `scroll-snap-type: y mandatory`
- `<section class="slide">` elements with `scroll-snap-align: start`
- `.slide-content` wrapper inside each slide
- `SlidePresentation` JS class (IntersectionObserver + BroadcastChannel)
- `PresentMode` class for fullscreen playback

**Do NOT** emit `#stage`, `#track`, `calc(100vw * var(--slide-count))`, or `translateX` navigation CSS/JS for any style other than Blue Sky. These are Blue Sky's internal patterns, not a universal template. If the generated HTML contains `#stage` or `#track` for a non-Blue-Sky style, it is a generation error — revert to `html-template.md`'s scroll-snap architecture.

Honor the chosen preset exactly. `自动` and `精修` may produce different structure, density, and diagrams, but they should still render inside the same preset family unless the user explicitly changed the style.

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

### Step 7: Pre-write validation (ALL modes — Auto, Polish, --generate)

Before writing the final HTML, scan the assembled output for these violations and fix each one found:

**Core 8 checks:**
1. **Search `:::` in HTML** → convert any unconverted directive blocks
2. **Search generic slide titles** from forbidden list (概览, Overview, 架构介绍, Key Insights, 总结, 结论, Next Steps, 简介, 说明, 关键发现) → rewrite as assertion-style titles
3. **Search slide title line wraps** → flag any title wrapping ≥4 lines; shorten or restructure
4. **Search content density** → any slide filling <50% of its area → switch to emphasis layout (large stat, quote, single statement)
5. **Search column balance** → in two/three-column slides, verify no column <60% of tallest; fix imbalance
6. **Search consecutive same-layout slides** → 3+ consecutive identical layouts → insert visual break (quote, diagram, big stat)
7. **Search `--accent` usage** → count distinct element types using accent color on each slide; if >3 types → reduce
8. **Search concept density** → any slide introducing >3 new technical terms → split or use progressive disclosure

**Visual hard rules (from impeccable-anti-patterns.md):**
9. **Search U+FE0F** → remove all variant selectors from emoji
10. **Search `letter-spacing`** → any non-title element > `0.05em` → reduce
11. **Search `#000` / `#000000` background** → replace with `#111` or `#18181B`
12. **Search bounce/elastic easing** → `ease.*back|bounce` → replace with `cubic-bezier(0.16, 1, 0.3, 1)`
13. **Search nested cards** → `.card` / `.glass-card` inside same class → flatten hierarchy
14. **Search cramped padding** → `padding: 0.[1-5]rem` on cards → increase to ≥0.75rem
15. **Search gray on colored bg** → `color: #[89]99` or `var(--text-secondary)` on non-white background → darken text
16. **Search component monotony** → if >50% of slides use the same component pattern (e.g., only `.g` + `.bl`) → redesign at least half to use 2-3 distinct component types (step/callout/stat/kbd/table/quote)
17. **Search present mode JS** → must contain `PresentMode` class or `enterPresent()` function, `'F5'` key listener, `#present-btn` CSS, and `body.presenting` CSS → missing = generation error, must fix
18. **Search watermark placement** → must be JS-injected into last slide (`slides[slides.length - 1].appendChild`), CSS must be `position: absolute` → if `position: fixed` or hardcoded `<div class="slide-credit">` before `</body>`, move to JS injection
19. **Search architecture contamination (non-Blue-Sky only)** → if style is NOT Blue Sky, search for `#stage`, `#track`, `calc(100vw * var(--slide-count))`, or `translateX` slide navigation → these are Blue Sky-exclusive patterns. Replace with `html-template.md`'s `scroll-snap-type: y mandatory` + `SlidePresentation` class architecture
20. **Search `.slide` background overriding body gradient** → if the style reference file defines `radial-gradient`, `linear-gradient`, `background-image` patterns, or `animation` on `body`, search for `.slide` elements with `background` / `background-color` → these block the body gradient. Remove `background` from `.slide` rules. The template's `background: var(--bg-primary)` safety net does NOT apply to gradient/animated body backgrounds

> Load `references/impeccable-anti-patterns.md` for the full detection patterns and fix guidance.

**These checks are NOT optional.** Run them in every generation mode (Auto, Polish, --generate). Auto-fix violations. Then proceed to Phase 3.5 Review (Polish mode only).

---

## Phase 3.5: Review (Polish mode only)

**Auto mode**: Phase 3 Step 7 already ran the 8 pre-write validation checks. Proceed directly to Phase 5 Delivery.

**Polish mode**: Run after Phase 3 generation completes. Phase 3 Step 7 already fixed basic violations; Phase 3.5 runs the full 16-point review for deeper content quality issues.

**`--review` command**: Entry point for reviewing any existing HTML.

### Step 1: Load review rules

Read [review-checklist.md](review-checklist.md) for the 16 checkpoints.

### Step 2: Execute detection

Run all 16 checkpoints against the generated HTML:

- **Category 1 (Auto-Detectable)**: 6 checkpoints that can be detected; only 1.1 can be fully auto-fixed
- **Category 2 (AI-advised)**: 10 checkpoints where AI provides suggestions

### Step 3: Classify and present results

Group results by category:

| Symbol | Category | Action |
|---|---|---|
| ✅ | Passed | No action needed |
| 🔧 | Auto-fixable | Can fix without user input |
| ⚠️ | Needs confirmation | AI suggests fix, user confirms |
| ❌ | Needs judgment | AI provides guidance, user decides |

Present via AskUserQuestion with options:
- **[全部自动修复]** — Apply all 🔧 fixes automatically
- **[逐项确认]** — Review each 🔧/⚠️ item individually
- **[跳过 Review]** — Output HTML as-is

### Step 4: Apply fixes

**If "全部自动修复"**:
1. Apply all 🔧 auto-fixable changes
2. Write updated HTML
3. Generate REVIEW_REPORT.md

**If "逐项确认"**:
1. For each 🔧/⚠️ item, show:
   - Checkpoint name
   - Issue description
   - Suggested fix
2. User selects: [修复] / [跳过] / [保持原样]
3. After all items, write updated HTML
4. Generate REVIEW_REPORT.md

**If "跳过 Review"**:
1. Write HTML as-is
2. Skip report generation

### Step 5: Output diagnostic report

Generate REVIEW_REPORT.md in working directory:

```markdown
## Review 诊断报告

**幻灯片**: [filename].html
**检测结果**: [passed]/16 通过，[pending] 项待处理

### 已修复项 ([count])
- ✅ [checkpoint]: [what was fixed]

### 未修复项 ([count])
- ⚠️ [checkpoint]: [issue description]
  - AI 建议：[suggestion]

### 需人工判断项 (建议思考)
- 🔍 [checkpoint]: [AI analysis]

---
可再次运行 `/slide-creator --review` 继续优化
```

Tell user: "Review 完成。可再次运行 `/slide-creator --review [filename].html` 继续优化。"

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

---
