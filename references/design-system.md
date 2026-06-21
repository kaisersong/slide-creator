# Design System Reference

Default visual system for generated presentations. Users may override in their prompt or BRIEF.json.

## Style Preset Quick Reference

This table describes design direction. Render capability is controlled by
[preset-support-tiers.json](preset-support-tiers.json), not by this file.

| Preset | Background | Primary Text | Accent | Best For | Render Status |
|--------|-----------|-------------|--------|----------|---------------|
| **Swiss Modern** | `#FFFFFF` | `#000000` | `#FF3300` | Corporate, data, precise systems | Production |
| **Enterprise Dark** | `#05070D` | `#E6EDF3` | `#58A6FF` | B2B, investor decks, strategy | Production |
| **Data Story** | `#0F1117` | `#E2E8F0` | `#3B82F6` | Business review, KPI, analytics | Production |
| **Blue Sky** | `#EAF6FF` | `#0F172A` | `#0EA5E9` | SaaS pitches, AI/tech decks | Production |
| **Chinese Chan** | `#F7F3EA` | `#2B2118` | `#B45309` | Philosophy, brand, culture | Generator-ready contextual |
| **Bold Signal** | `#0A0A0A` | `#FFFFFF` | `#FF3D00` | Pitch decks, keynotes | Reference-only |
| **Aurora Mesh** | `#0B1020` | `#F8FAFC` | `#8B5CF6` | Premium SaaS, launches, VC pitch | Reference-only |
| **Paper & Ink** | `#F4EFE6` | `#1A1008` | `#8B4513` | Storytelling, literary | Reference-only candidate |
| **Glassmorphism** | `#F8FAFC` | `#0F172A` | `#6366F1` | Consumer tech, brand launches | Reference-only |
| **Terminal Green** | `#0D1117` | `#30F030` | `#00FF41` | Developer, API docs | Reference-only |
| **Strategy Consulting** | `#F8F8F5` | `#1A1A1A` | `#1F4E79` | Board materials, due diligence | Reference-only |
| **Electric Studio** | `#F5F5F5` | `#111111` | `#0052FF` | Agency, corporate | Reference-only |
| **Creative Voltage** | `#1A1A2E` | `#EAEAEA` | `#FFE600` | Retro-modern, creative | Reference-only |
| **Dark Botanical** | `#0F1C15` | `#E8E0D0` | `#C5A059` | Luxury, premium brands | Reference-only |
| **Modern Newspaper** | `#F7F1E8` | `#111111` | `#D72638` | Reports, thought leadership | Reference-only |
| **Neo-Brutalism** | `#F5F5F5` | `#111111` | `#FF5C00` | Indie dev, manifesto | Reference-only |
| **Neo-Retro Dev Deck** | `#101018` | `#F8F5E8` | `#FFB000` | Dev tool launches, hackathon | Reference-only |
| **Neon Cyber** | `#080C14` | `#E0F0FF` | `#00FFCC` | Tech startups | Reference-only |
| **Notebook Tabs** | `#FBF7F0` | `#2C2C2C` | `#E84545` | Editorial, reports | Reference-only |
| **Pastel Geometry** | `#FDF6EE` | `#333333` | `#FF8FAB` | Friendly, product | Reference-only |
| **Split Pastel** | `#FFF0F5` | `#2D2D2D` | `#A78BFA` | Creative agencies | Reference-only |
| **Vintage Editorial** | `#EDE8DF` | `#2A1810` | `#B85C00` | Personal brands, witty | Reference-only |

## Typography Pairings

Use the font contract from the selected preset reference. Do not replace a
preset's display/body pairing with a generic Inter/Roboto/Arial treatment unless
that preset explicitly names it. Generated HTML may use Google Fonts links when
the style reference requires them; other external font or script dependencies are
not allowed.

| Style | Display Font | Body Font | Import |
|-------|-------------|-----------|--------|
| Bold Signal | `Clash Display` | `Satoshi` | Fontshare |
| Dark Botanical | `Cormorant Garamond` | `DM Sans` | Google Fonts |
| Notebook Tabs | `Libre Baskerville` | `Lato` | Google Fonts |
| Swiss Modern | `Neue Haas Grotesk` | `Neue Haas Grotesk` | Fontshare |
| Terminal Green | `JetBrains Mono` | `JetBrains Mono` | Google Fonts |
| Vintage Editorial | `Playfair Display` | `Source Serif 4` | Google Fonts |
| Creative Voltage | `Space Grotesk` | `DM Mono` | Google Fonts |
| Neon Cyber | `Oxanium` | `Rajdhani` | Google Fonts |
| Data Story | `Inter` | `Inter` | Google Fonts or local/system fallback |
| Chinese Chan | `Noto Serif SC` | `Noto Serif SC` | Google Fonts or local/system fallback |

**Font size scale (must use `clamp()`):**
```css
--title-size: clamp(2rem, 6vw, 5rem);
--h2-size: clamp(1.25rem, 3.5vw, 2.5rem);
--body-size: clamp(0.75rem, 1.5vw, 1.125rem);
--small-size: clamp(0.65rem, 1vw, 0.875rem);
```

**Chinese font fallback (always include):**
```css
font-family: var(--font-body), 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
```

## Slide Dimensions

- **Canvas**: 100vw × 100vh (scroll-snap, not fixed pixel)
- **Padding**: `clamp(1.5rem, 4vw, 4rem)`
- **Max content width**: `min(90vw, 1000px)`

## Animation Defaults

```css
/* Entrance animation */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Stagger delays */
.reveal:nth-child(1) { animation-delay: 0.1s; }
.reveal:nth-child(2) { animation-delay: 0.2s; }
.reveal:nth-child(3) { animation-delay: 0.3s; }
.reveal:nth-child(4) { animation-delay: 0.4s; }

/* Duration */
--duration-normal: 0.6s;
--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
```

## Layout Rules

- **One key point per slide** + up to 5 supporting bullets
- **No text walls** — if > 60 words on a slide, split it
- **Every slide has a visual element** — icon, grid, chart, diagram, or color block
- **Footer** — include slide number on content slides
- **No scrolling** — slides must fit exactly in viewport (use `overflow: hidden`)
- **Visual rhythm is signature-based** — do not repeat the same component signature for 3 consecutive slides. A repeated export role can be acceptable only when the visible component changes, such as Data Story `chart_insight` rotating from evidence ladder to interaction panel to phase timeline.

## Generator-Ready Signature Notes

- **Blue Sky** uses `references/blue-sky-starter.html`. Cover KPI cards must contain numeric signals, the top pill must not be empty, and repeated bento pages should rotate placement variants rather than reusing identical grid coordinates.
- **Data Story** remains chart-first. If slide-local numeric facts are weak, use pure SVG fallbacks with distinct visual signatures: signal bars, flow map, phase timeline, signal map, evidence ladder, state grid, or interaction panel. Do not turn most pages into repeated text matrices.
- **Swiss Modern** uses background page numbers only on rhythm-anchor pages. `.bg-num` stays at slide-root `z-index: 0`; `.slide-content`, `.left-panel`, and `.right-panel` stay above it.
- **Enterprise Dark** should rotate dashboard, contrast, split, matrix/feature, timeline, architecture, table, and CTA families. Do not hard-code a single deck sequence; derive the route from slide role, content signal, and style contract.
- **Chinese Chan** is the minimalist exception. Layout repetition is allowed, but decorative treatment must still vary between ghost kanji, rule, vline, seal, or pure whitespace.

## Decorative Elements

```css
/* Background accent (low opacity) */
.accent-blob {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, var(--accent-glow) 0%, transparent 70%);
  opacity: 0.15;
}

/* Card style */
.card {
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

/* Bullet marker (accent bar) */
li::before {
  content: '';
  display: inline-block;
  width: 3px;
  height: 1em;
  background: var(--accent);
  margin-right: 12px;
  border-radius: 2px;
  vertical-align: middle;
}
```
