# PLANNING.md View Template

Use this structure only when the user explicitly asks for a human-readable planning view derived from `BRIEF.json`.

---

## Template

```markdown
**Task**: [One-sentence description of the deck to generate]
**Mode**: [自动 / 精修 / Auto / Polish]
**Slide count**: [N] ± [tolerance]
**Language**: [Chinese / English / bilingual]
**Audience**: [Target audience description]
**Goals**:
- [Goal 1]
- [Goal 2]
**Style**: [Tone and style keywords, e.g., bold, minimal, editorial, futuristic]
**Preset**: [Style preset name from the available list, or "guided discovery"]

## Timing

- **Estimate**:
  - `plan`: [e.g., 1-2 min]
  - `generate`: [e.g., 1-3 min]
  - `validate`: [e.g., <1 min]
  - `polish`: [e.g., 0-2 min for Auto / 2-6 min for Polish]
  - `total`: [e.g., 3-6 min for Auto / 8-15 min for Polish]
- **Actual**:
  - `plan`: [fill after run]
  - `generate`: [fill after run]
  - `validate`: [fill after run]
  - `polish`: [fill after run]
  - `total`: [fill after run]

<!-- Only include this section when mode is `精修`. -->
## Deck Thesis

- [One sentence that defines the deck's core argument]

<!-- Only include this section when mode is `精修`. -->
## Narrative Arc

- Opening: [how the story starts]
- Middle: [how tension, proof, or explanation develops]
- Ending: [what decision, shift, or takeaway the deck lands]

<!-- Only include this section when mode is `精修`. -->
## Page Roles

- Slide 1: [role, e.g., hook / cover / context reset]
- Slide 2: [role, e.g., problem framing / agenda / bridge]
- Slide 3+: [role per slide or section]

<!-- Only include this section when mode is `精修`. -->
## Style Constraints

- [Hard visual rule, e.g., keep every section title left-aligned]
- [Hard narrative rule, e.g., every evidence slide must answer "why now"]
- [Brand or reference lock, if needed]

<!-- Only include this section when mode is `精修`. -->
## Image Intent

- Slide [N]: [why this slide needs an image, what communication job it serves, optional search/reference direction]

---

## Visual & Layout Guidelines

- **Overall tone**: [e.g., warm, minimal, high-contrast dark]
- **Background**: [hex color + description]
- **Primary text**: [hex color]
- **Accent (primary)**: [hex color + usage — if content tone matches a category below, use the suggested color as the starting point]
  - Contemplative / Research → `#7C6853` warm brown (grounded, editorial)
  - Technical / Engineering → `#3D5A80` navy (precise, authoritative)
  - Business / Data → `#0F7B6C` deep teal (confident, forward)
  - Narrative / Annual → `#B45309` amber (warm, momentum)
  - Creative / Personal brand → keep the preset's signature accent
- **Typography**: [Font pairing, e.g., Clash Display + Satoshi]
- **Per-slide rule**: 1 key point + up to 5 supporting bullets; no text walls
- **Animations**: [e.g., fade + slide-up, staggered 0.1s delay]

---

## Slide-by-Slide Outline

**Slide 1 | Cover**
- Title: [title]
- Subtitle: [subtitle]
- Visual: [background treatment, logo placement]

**Slide 2 | Agenda / Overview**
- [Topic 1]
- [Topic 2]
- [Topic 3]

**Slide 3 | [Section Title]**
- Key point: [one sentence]
- Supporting: [2-4 bullets]
- Visual element: [icon set / grid / chart / diagram / screenshot]
- Speaker note: [what to say on this slide]

[...continue for each slide...]

**Slide N | Closing**
- Summary statement
- Call to action or contact info

---

## Resources Used

- [List files from resources/ and how they map to slides]
- Example: `resources/report.pdf` → Slide 3 data, Slide 5 quote

---

## Images

- [List image files if provided and which slide they go on]
- Example: `assets/screenshot.png` → Slide 4 (feature demo)

---

## Deliverables

- Output: [filename].html (single-file, zero dependencies)
- Optional: PRESENTATION_SCRIPT.md (speaker notes)
- Inline editing: [Yes / No]
```

## Guidelines for Writing the Plan

1. **Choose the correct depth** — `自动` / `Auto` stays lightweight; `精修` / `Polish` adds thesis, arc, page roles, style constraints, and image intent only where justified
2. **Be specific** — Write actual key points and bullets per slide, not just "content about X"
3. **Map resources** — Reference which source file informs which slide
4. **Specify visuals** — Note what visual element each slide should have
5. **Speaker notes** — Note emphasis points for the presenter per slide
6. **Match audience** — Technical audience = more data; executive = more impact
7. **Treat preset as locked once chosen** — moving from `自动` / `Auto` to `精修` / `Polish` may deepen structure, but should not silently swap the visual preset for the same source content
8. **Record timing** — plans should carry estimate ranges up front and actual segmented timing after generation / validation runs
