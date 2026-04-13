# Bold Signal — Style Reference

Confident, bold, modern, high-impact. Dark canvas with colored card focal points.

---

## Colors

```css
:root {
    --bg-primary: #1a1a1a;
    --bg-gradient: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%);
    --card-bg: #FF5722;
    --text-primary: #ffffff;
    --text-on-card: #1a1a1a;
}
```

---

## Background

```css
body {
    background: var(--bg-gradient);
    font-family: "Space Grotesk", -apple-system, sans-serif;
}

/* Ghost section number as texture */
.bold-ghost-number {
    position: absolute;
    font-size: clamp(6rem, 12vw, 10rem);
    font-family: "Archivo Black", sans-serif;
    color: var(--card-bg);
    opacity: 0.08;
    pointer-events: none;
    user-select: none;
}
```

---

## Typography

```css
/* Display */
@import url('https://fonts.googleapis.com/css2?family=Archivo+Black&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500&display=swap');

.bold-title {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(32px, 6vw, 72px);
    font-weight: 900;
    color: var(--text-primary);
    line-height: 1.0;
    letter-spacing: -0.02em;
}

.bold-body {
    font-family: "Space Grotesk", sans-serif;
    font-size: clamp(14px, 1.5vw, 18px);
    font-weight: 400;
    color: rgba(255,255,255,0.6);
    line-height: 1.6;
}

.bold-label {
    font-size: clamp(10px, 1.1vw, 12px);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: rgba(255,255,255,0.4);
}

/* Bullet marker */
.bold-bullet { color: var(--card-bg); }
```

---

## Components

```css
/* Hero card — colored focal point */
.bold-hero-card {
    background: var(--card-bg);
    border-radius: 8px;
    padding: clamp(24px, 4vw, 48px);
    color: var(--text-on-card);
}

/* Section number badge */
.bold-section-num {
    font-family: "Archivo Black", sans-serif;
    font-size: clamp(14px, 1.8vw, 20px);
    color: var(--card-bg);
    opacity: 0.9;
}

/* Bullet point with card-colored marker */
.bold-bullet::before {
    content: '▸';
    color: var(--card-bg);
    margin-right: 0.5em;
}

/* Timeline step */
.bold-step {
    border: 2px solid var(--card-bg);
    border-radius: 4px;
    padding: 8px 16px;
    text-align: center;
    font-size: clamp(12px, 1.3vw, 16px);
}
.bold-step.active {
    background: var(--card-bg);
    color: var(--text-on-card);
}
```

---

## Named Layout Variations

### 1. Hero Card

Large colored card (`--card-bg`) occupies 60% of width, centered vertically, anchored left. Card: section number `01` small top-left, headline 2–3 lines. Dark background outside card. Ghost section number in 10rem at 8% opacity as texture. Nav breadcrumbs top-right.

### 2. Manifesto Statement

`01` in 8rem `Archivo Black` top-left, card color. Below: 2-line statement in 3rem. Right half: supporting 3-line body paragraph in muted white `rgba(255,255,255,0.6)`. Bottom-left: next section teaser in 0.75rem mono.

### 3. Feature Trio

Three full-width horizontal rows, shorter height than a normal card. Active/highlighted row: full `--card-bg` color. Other rows: 20% opacity, outlined. Each row: number left, feature name center-left in 1.3rem, 1-line descriptor right.

### 4. Stat + Story

Left 40%: single large number `5rem` in `--card-bg` color, label below in 0.75rem uppercase. `1px` vertical rule (card color). Right 55%: 3-line supporting paragraph + 2–3 bullet points with card-colored ▸ markers.

### 5. Timeline Track

Horizontal numbered steps `01 → 02 → 03 → 04`. Active step: full colored card above the track line. Completed steps: full opacity outlined. Future steps: 30% opacity outlined. Track line: `2px --card-bg`.

### 6. Quote Block

Full-width colored card (`--card-bg` background). Large `"` in near-black at top-left, barely visible (8% opacity). Quote in `Archivo Black` 2rem, dark text. Attribution bottom-right: `—Name, Role` in small body.

### 7. Split Evidence

Left 42%: section number in 3rem + headline in 2rem + 1-line sub. `1px` vertical rule (card color). Right 53%: 4–5 bullet list, each bullet: card-colored ▸ + bold lead word + 1-line description.

---

## Signature Elements

- Bold colored card as focal point (orange, coral, or vibrant accent)
- Large section numbers (01, 02, etc.)
- Navigation breadcrumbs with active/inactive opacity states
- Grid-based layout for precise alignment

---

## Animation

```css
.reveal {
    opacity: 0;
    transform: translateY(24px);
    transition: opacity 0.6s cubic-bezier(0.16,1,0.3,1),
                transform 0.6s cubic-bezier(0.16,1,0.3,1);
}
.reveal.visible { opacity: 1; transform: translateY(0); }
.reveal:nth-child(1) { transition-delay: 0.08s; }
.reveal:nth-child(2) { transition-delay: 0.18s; }
.reveal:nth-child(3) { transition-delay: 0.28s; }
```

---

## Style Preview Checklist

- [ ] Dark gradient background `#1a1a1a → #2d2d2d`
- [ ] Colored card (`--card-bg`) as focal point
- [ ] Large section number (01, 02, etc.) visible
- [ ] Ghost section number at 8% opacity as texture
- [ ] At least one named layout pattern used
- [ ] No pure black background — using `#1a1a1a`

---

## Best For

Pitch decks · Keynotes · Product launches · High-impact presentations · Brand statements · Investor pitches
