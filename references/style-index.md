# Style Index

Read this file when the user is choosing a style preset (Phase 2).

---

## Generator-Ready Recommendation Surface

Use these 4 presets as the default recommendation surface when the user did not explicitly name a style:

- `Swiss Modern`
- `Enterprise Dark`
- `Data Story`
- `Blue Sky`

These presets have stable deterministic renderers and are safe first-line recommendations.

- All built-in presets are explicitly renderable.
- The five native deterministic core presets are the most stable generation surface: `Swiss Modern`, `Enterprise Dark`, `Data Story`, `Blue Sky`, and contextual `Chinese Chan`.
- The remaining reference-backed presets use the unified profile renderer with the same `BRIEF.json`, shared runtime, strict validation, and eval/release gates. Profile-rendered presets are demo-parity gated against the historical checked-in demos before being described as restored to historical style fidelity, but they are not native deterministic core and they are not default recommendations.

Machine-readable source of truth: `references/preset-support-tiers.json`

---

## 22 Presets

| Preset | Vibe | Best For |
|--------|------|----------|
| Bold Signal | Confident, high-impact | Pitch decks, keynotes |
| Electric Studio | Clean, professional | Agency presentations |
| Creative Voltage | Energetic, retro-modern | Creative pitches |
| Dark Botanical | Elegant, sophisticated | Premium brands |
| Blue Sky | Clean, airy, enterprise-ready | SaaS pitches, AI/tech decks |
| Notebook Tabs | Editorial, organized | Reports, reviews |
| Pastel Geometry | Friendly, approachable | Product overviews |
| Split Pastel | Playful, modern | Creative agencies |
| Vintage Editorial | Witty, personality-driven | Personal brands |
| Neon Cyber | Futuristic, techy | Tech startups |
| Terminal Green | Developer-focused | Dev tools, APIs |
| Swiss Modern | Minimal, precise | Corporate, data |
| Paper & Ink | Literary, thoughtful | Storytelling |
| Aurora Mesh | Vibrant, premium SaaS | Product launches, VC pitch |
| Enterprise Dark | Authoritative, data-driven | B2B, investor decks, strategy |
| Glassmorphism | Light, translucent, modern | Consumer tech, brand launches |
| Neo-Brutalism | Bold, uncompromising | Indie dev, creative manifesto |
| Chinese Chan | Still, contemplative | Design philosophy, brand, culture |
| Data Story | Clear, precise, persuasive | Business review, KPI, analytics |
| Modern Newspaper | Punchy, authoritative, editorial | Business reports, thought leadership |
| Neo-Retro Dev Deck | Opinionated, technical, handmade | Dev tool launches, API docs, hackathon |
| Strategy Consulting | Structured, authoritative, insight-driven | Strategy decks, board materials, due diligence |

## Custom Themes

If `themes/` contains subdirectories with `reference.md`, those are custom themes.
Custom themes are first-class presets — they take **priority** over content-type routing and mood-mapping.
The code layer auto-discovers them via directory scan; no manual registration needed.
When a custom theme is selected, read `themes/<name>/reference.md` as the style reference.
Built-in canonical names still resolve to built-ins first. Use `custom:<name>` when the user explicitly wants a custom theme whose folder name collides with a built-in preset.

**Per-style detail files** (read only the chosen one):
`references/aurora-mesh.md`, `references/bold-signal.md`, `references/chinese-chan.md`,
`references/creative-voltage.md`, `references/dark-botanical.md`, `references/data-story.md`,
`references/electric-studio.md`, `references/enterprise-dark.md`, `references/glassmorphism.md`,
`references/modern-newspaper.md`, `references/neo-brutalism.md`, `references/neo-retro-dev.md`,
`references/neon-cyber.md`, `references/notebook-tabs.md`, `references/paper-ink.md`,
`references/pastel-geometry.md`, `references/split-pastel.md`, `references/strategy-consulting.md`,
`references/swiss-modern.md`, `references/terminal-green.md`, `references/vintage-editorial.md`

Blue Sky uses `references/blue-sky-starter.html` as its reference file.

---

## Support Tier Snapshot

| Tier | Current Presets | Notes |
|------|-----------------|-------|
| Production | Swiss Modern, Enterprise Dark, Data Story, Blue Sky | Default generator-ready recommendation surface |
| Supported | Chinese Chan, Aurora Mesh, Bold Signal, Creative Voltage, Dark Botanical, Electric Studio, Glassmorphism, Modern Newspaper, Neo-Brutalism, Neo-Retro Dev Deck, Neon Cyber, Notebook Tabs, Paper & Ink, Pastel Geometry, Split Pastel, Strategy Consulting, Terminal Green, Vintage Editorial | `Chinese Chan` is contextual native core; the rest render through the unified profile renderer |
| Experimental | None | Do not add profile-rendered presets to default recommendations until promoted |
| Archive Candidate | None yet | Do not archive before usage evidence exists |

---

## Mood → Preset Mapping

Use when the user answers the mood question in Phase 2.

| Mood | Style Options |
|------|---------------|
| Impressed/Confident | Enterprise Dark, Swiss Modern, Blue Sky |
| Excited/Energized | Blue Sky, Data Story, Enterprise Dark |
| Calm/Focused | Chinese Chan, Swiss Modern, Data Story |
| Inspired/Moved | Chinese Chan, Blue Sky, Swiss Modern |
| Clean/Enterprise | Blue Sky, Enterprise Dark, Data Story |
| Data-Driven | Data Story, Enterprise Dark, Swiss Modern |
| Playful/Creative | Blue Sky, Chinese Chan, Swiss Modern |
| Developer-Focused | Data Story, Blue Sky, Enterprise Dark |
| Editorial/Organized | Swiss Modern, Data Story, Chinese Chan |

---

## Effect → Feeling Guide

Use when designing animations and visual treatments for a chosen style.

| Feeling | Techniques |
|---------|-----------|
| Dramatic/Cinematic | Slow fade-ins 1–1.5s, dark backgrounds, full-bleed images, parallax |
| Techy/Futuristic | Neon glow, particle canvas, grid patterns, monospace accents, glitch text |
| Playful/Friendly | Bouncy easing, large rounded corners, pastels, floating/bobbing animations |
| Professional | Subtle 200–300ms animations, clean sans-serif, minimal decoration |
| Calm/Minimal | Very slow motion, high whitespace, muted palette, generous padding, serif type |
| Editorial | Strong typography hierarchy, pull quotes, serif headlines, one accent color |
