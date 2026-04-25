# Slide Design Quality Baseline

Load this file alongside the chosen style file during `--generate` and Phase 3 generation.
Apply all rules before writing any HTML. Run the pre-output self-check last.

---

## 1. Content Density Balance

This is the most common quality failure in AI-generated slides. Fix it before anything else.

### Minimum Fill Rule

Every content slide must fill **at least 65% of its content area**. If the natural content fills less than 50% of the slide, do not just center it and call it done — that looks like a draft, not a finished slide.

**Decision tree when content is sparse:**

| Situation | Wrong response | Right response |
|-----------|---------------|----------------|
| 2 bullet points | Leave as 2 bullets, big whitespace below | Switch to a quote/big-stat layout; or expand each bullet to a 2-line statement |
| 1 key insight | Generic content slide with 60% empty space | Use a dedicated emphasis layout: large quote, single stat, or one-line manifesto with visual treatment |
| Section intro (1 sentence) | Center the sentence, rest is blank | Make it a breathing-room slide with intentional large type (≥2.5rem) — whitespace must be *designed*, not accidental |
| 3 bullets, each 3 words | Leave as-is | Expand: add a supporting detail sentence to each, or switch to a 3-card grid layout |

**Designing whitespace vs. accidental whitespace:**

Intentional whitespace has visual weight — it anchors the content, not floats it. Accidental whitespace makes the slide look unfinished. Ask: "Does the empty space *frame* the content or *expose* the slide as half-done?"

Signs of accidental whitespace:
- Content is top-aligned with more than 30% blank area below
- A single sentence is left-aligned with the right 50% of the slide empty
- A grid of 2 items is centered in a 4-item grid template, leaving 2 ghost cells

Signs of intentional whitespace:
- A single statement is centered with balanced space above and below
- Large negative space between two contrasting elements
- A quote occupies the center third with the speaker's name anchored to the bottom

---

## 2. Multi-Column Balance Rule

In any two-column or three-column layout, **no column should have less than 60% of the height of the tallest column**.

### Why this keeps happening

AI tends to make one column the "main" content and the other a footnote or supporting annotation. The result is one column that fills 80% of the slide and another that fills 30%, producing a lopsided layout that looks like a layout error.

### How to fix column imbalance

**Option A — Expand the shorter column.** Add a supporting detail, a relevant example, a sub-point that was omitted. Make both columns genuinely substantial.

**Option B — Redesign the layout.** If the content genuinely has an asymmetric relationship (one item is primary, the other is secondary), use an asymmetric layout *intentionally*: `grid-template-columns: 2fr 1fr` with visual styling that signals the hierarchy. Don't use a 50/50 grid and fill it 80/30.

**Option C — Merge into one column.** If the total content fits comfortably in a single column without being sparse, don't force two columns just because the slide type calls for it.

### Column balance checklist

Before writing a two-column slide:
- Roughly count the lines in each column
- If one column has ≥ 2× the lines of the other → trigger Option A, B, or C
- If using `2fr 1fr` intentionally → make the narrow column's role visually clear (label it "sidebar", "stat", "callout")

---

## 3. 90/8/2 Color Law

Allocate color in three tiers:

- **90% neutral surface** — background, body text, structural lines
- **8% structural accent** — one emphasis block, border treatments, a single highlight color
- **2% bullet point** — at most 1–2 precise high-contrast hits on important data or CTAs

When the accent color (`--accent`) floods headings, bullet points, card borders, badges, and underlines simultaneously — it stops being signal and becomes visual noise.

**Audit before writing:** Count how many distinct element types use `--accent`. If > 3 types use it at the same time on a single slide, reduce.

---

## 4. Typography Tension

The title should feel like an *anchor*, not a *label*. The largest element on a slide should be at least 5× the smallest readable element (clamp-based scales already handle this for viewport fitting — but check that the AI content choices respect the scale, not fight it).

**Patterns that break hierarchy:**
- A title at `2rem` and body text at `1.1rem` — barely distinguishable
- A quote slide where the attribution is the same size as the quote
- A data slide where the KPI number and the label are the same weight

**Minimum title treatment for emphasis layouts:**
Single-stat, quote, or breathing-room slides → title/stat element should be ≥ `clamp(2.5rem, 6vw, 5rem)`

---

## 4.5 Title Fit Guardrail

**A slide title wrapping to 4+ lines is a layout failure, not a typography style.**

Fix it in this order:

1. Rewrite the title to the shortest defensible judgment
2. Widen the title measure for that language or layout
3. Change the layout so the title has more horizontal room

Do **not** solve this by globally forcing tiny heading boxes such as `max-width: 10ch` or `14ch` for Chinese / mixed technical titles. That reliably turns reasonable titles into 5-6 line stacks.

**Hard rule:** if a heading wraps beyond 3 lines on desktop, regenerate the title or layout before shipping.

### Multi-Line Balance Rule

When a horizontal title needs 2-3 lines, those lines should feel intentionally composed, not accidentally wrapped.

- No single-character orphan lines
- No single short token orphan lines
- No obviously collapsed middle line that is much shorter than the lines above and below it
- If a title must stack, use explicit line control or widen the measure; do not squeeze the box until the browser creates an awkward stack

**Exception profile:** vertical-writing titles, split-lockup titles, glitch/data-text titles, and terminal-style command titles follow their preset-specific composition rules instead of this horizontal line-balance rule.

---

## 5. Content-Tone Color Calibration

When no specific color is given, match the accent color to the content's emotional register:

| Content tone | `--accent` | Feel |
|---|---|---|
| Contemplative / Research | `#7C6853` warm brown | Grounded, editorial |
| Technical / Engineering | `#3D5A80` navy | Precise, authoritative |
| Business / Data | `#0F7B6C` deep teal | Confident, forward |
| Narrative / Annual | `#B45309` amber | Warm, momentum |
| Creative / Personal | keep the style preset | Style is the identity |

Apply only when the style preset uses a generic accent (purple, indigo, `#6366f1`). Do not override strong, intentional style identities like Terminal Green or Chinese Chan.

---

## 6. No 3 Consecutive Full-Bullet Slides

Reports use prose sections as the unit; slides use slides. The same cognitive pacing rule applies:

**Never place 3 or more consecutive slides with the same layout type** (especially full-bullet lists).

After 2 bullet-list slides, the next slide should be a layout break:
- A visual stat / big number
- A quote or emphasis slide
- An image or diagram
- A two-column grid with visual elements

This isn't decoration — it's cognitive pacing. Dense bullet slides fatigue attention. A layout break resets focus.

---

## 7. Anti-Slop Patterns

These patterns make slides look instantly AI-generated:

| Pattern | Fix |
|---------|-----|
| Section headings: "Overview", "Key Insights", "Next Steps", "Conclusion" | Write headings that state the actual point ("Q3 revenue grew despite churn — here's why") |
| Every card has the same icon + title + 2-line description format | Vary card density: some cards go deep, some are single statements |
| Three equal columns regardless of content count | 2 items → side-by-side with breathing room; 4 items → 2×2 |
| Border radius uniformly `12px` on everything | Vary: sharp badges (`2px`), rounded cards (`8px`), pill tags (`999px`) |
| Gradient + blur + card with `backdrop-filter` on every slide | Reserve glassmorphism for 1-2 slides max; rest are solid |

---

## 8. Nested Grid Fit

The most common overflow bug in technical decks is packing too many dense cards into a half-width column.

**Never put a 5-step state chain or API matrix inside a 50/50 column unless each item is extremely short.**

If a state sequence needs 5 items:
- use a full-width slide
- or reflow into `3 + 2`
- or turn it into a diagram instead of five verbose cards

If any card needs more than 2 short lines to stay readable, the grid is too dense for the container.

---

## 7.5 Visual Hard Rules (from Impeccable Anti-Patterns)

These are structural, auto-detectable violations. Scan the assembled HTML for each before writing.

| Rule | Detection | Fix |
|------|-----------|-----|
| letter-spacing > 0.05em on body | `letter-spacing:\s*(?:0\.[1-9][0-9]*\|[1-9])` on non-title elements | Reduce to ≤0.05em |
| Pure black background | `#000` or `#000000` as background | Use `#111` or `#18181B` |
| Bounce/elastic easing | `ease.*back\|bounce` in CSS | Use `cubic-bezier(0.16, 1, 0.3, 1)` |
| Nested cards | `.card` / `.glass-card` inside same class container | Flatten hierarchy |
| Cramped padding | `padding: 0.[1-5]rem` on cards/containers | Increase to ≥0.75rem |
| Gray text on colored bg | `color: #[89]99` on non-white background | Darken text or lighten background |
| Centered text everywhere | `text-align: center` on `.bullet-list` / `.body-text` | Left-align; center only titles/quotes |
| Monospace as body font | `font-family.*monospace` outside `<pre>`/`<code>` | Use system-ui |
| All-caps body text | `text-transform: uppercase` on paragraphs/lists | Remove; all-caps only for labels/chips |
| Inconsistent alignment | Same slide has both left + center text-align on body elements | Unify alignment |
| Gradient text without fallback | `-webkit-background-clip: text` without preceding `color:` | Add `color: var(--accent)` fallback |
| U+FE0F variant selectors | Any `\uFE0F` byte in HTML | Remove; use base emoji |

> See `references/impeccable-anti-patterns.md` for full detection patterns, rationale, and fix guidance.

## Pre-Output Self-Check

Run this before writing the final HTML:

```
□ Does any slide look less than 50% full without intentional design?
□ In multi-column layouts, is any column less than 60% of the tallest column's height?
□ Is the accent color used on more than 3 distinct element types simultaneously?
□ Are there 3+ consecutive bullet-list slides without a layout break?
□ Does any title/heading sound like a template ("Overview", "Summary", "Conclusion")?
□ Does any title wrap to 4+ lines on desktop? If yes, shorten it or widen the measure.
□ Does any 2-3 line horizontal title have an orphan line or an obviously collapsed middle line?
□ Did you pack a 5-step state chain or long API list inside a half-width card?
□ If you told someone "an AI made this" — would they immediately believe it?
  If yes — find the most generic slide and redesign it before writing.
```

Do not skip this check. It takes 30 seconds and prevents the most visible quality failures.

---

## L1 Content Quality Check

For content-level checkpoints (perspective, logic, pacing, clarity), see [review-checklist.md](review-checklist.md).

**L0 (Visual)**: This file — density, color, typography, layout
**L1 (Content)**: review-checklist.md — perspective flip, conclusion first, cognitive load, jargon translation

**When to apply:**
- L0: Always, before writing HTML
- L1: Polish mode after generation, or via `--review` command
