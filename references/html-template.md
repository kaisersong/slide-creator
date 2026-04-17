# HTML Template & Code Patterns

Reference for Phase 3 generation. Contains HTML architecture, JS patterns, animation recipes, and edit button implementation.

**Note:** `#stage` / `#track` URL fragments are Blue Sky only. Blue Sky uses `blue-sky-starter.html` as its base.

---

## Generation Checklist

Every generated HTML must include all of the following:

1. **Present mode CSS** — `#present-btn`, `#present-counter`, `body.presenting .slide`, `body.presenting .slide.p-on`, `body.presenting.presenting-black`
2. **Edit hotzone HTML** — `<div class="edit-hotzone">` + `<button class="edit-toggle" id="editToggle">` + `#notes-panel`
3. **`SlidePresentation` class** — navigation, dots, keyboard, touch, wheel, BroadcastChannel
4. **`?presenter` branch** — replaces body with notes/timer UI when `?presenter` in URL
5. **`PresentMode` class** — inside the `else` block, never inside `if (presenter)`
6. **`setupEditor()` call** — edit hotzone + notes panel wired up
7. **`data-notes` on every `<section class="slide">`** — 1-3 sentence speaker note per slide
8. **Preset fidelity metadata** — `data-preset="Preset Name"` on `<body>` when a preset is selected
9. **Watermark footer** — injected by JS into last slide as `<div class="slide-credit">By kai-slide-creator v[version] · [preset-name]</div>` with CSS: `position: absolute; bottom: 8px; right: 14px; font-size: 9px; color: var(--text-secondary, #999); opacity: 0.35; pointer-events: none; z-index: 1; font-family: system-ui, sans-serif;` and `body.presenting .slide-credit { display: none; }`

---

## HTML Architecture

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Presentation Title</title>
    <!-- Fonts from selected style reference -- single Google Fonts URL with display=swap -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="[SINGLE COMBINED GOOGLE FONTS URL]&display=swap" rel="stylesheet">

    <style>
        body { background-color: [from style file]; }
        /* CSS custom properties — ALL values from selected style reference file */
        :root {
            --bg-primary: [from style file]; --bg-secondary: [from style file];
            --text-primary: [from style file]; --text-secondary: [from style file]; --accent: [from style file];
            --font-display: '[font name from style file]', sans-serif; --font-body: '[font name from style file]', sans-serif;
            --title-size: clamp(2rem, 6vw, 5rem); --subtitle-size: clamp(0.875rem, 2vw, 1.25rem); --body-size: clamp(0.75rem, 1.5vw, 1.125rem);
            --slide-padding: clamp(1.5rem, 4vw, 4rem); --content-gap: clamp(1rem, 2vw, 2rem);
            --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1); --duration-normal: 0.6s;
        }

        /* Reset */
        *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
        html { scroll-snap-type: y mandatory; height: 100%; }

        body { font-family: var(--font-body); background: var(--bg-primary); color: var(--text-primary); overflow-x: hidden; height: 100%; }
        body[data-export-progress="false"] .progress-bar,
        body[data-export-progress="false"] .nav-dots { display: none !important; }

        /* Slide container — exactly fills viewport, no scrolling within */
        .slide {
            width: 100vw; height: 100vh; height: 100dvh;
            /* No padding — full-bleed panels touch screen edges. Per-slide padding via style file or inline style. */
            scroll-snap-align: start; display: flex; flex-direction: column; justify-content: center;
            position: relative; overflow: hidden;
            /* Must carry own background so present mode (body.presenting = #000) doesn't bleed through.
               EXCEPTION: If style file defines body gradient/pattern/image, set background: transparent instead. */
            background: var(--bg-primary);
        }

        .slide-content { flex: 1; display: flex; flex-direction: column; justify-content: center; max-height: 100%; overflow: hidden; padding: var(--slide-padding); }

        /* LAYOUT PANEL RULE: style-defined panels MUST be direct children of .slide, NOT nested in .slide-content. .slide-content is for text inside panels only. WRONG: .slide > .slide-content > .panel | RIGHT: .slide > .panel > .slide-content */

        /* Responsive breakpoints */
        @media (max-height: 700px) { :root { --slide-padding: clamp(0.75rem, 3vw, 2rem); --content-gap: clamp(0.4rem, 1.5vw, 1rem); --title-size: clamp(1.25rem, 4.5vw, 2.5rem); } }
        @media (max-height: 600px) { :root { --slide-padding: clamp(0.5rem, 2.5vw, 1.5rem); --title-size: clamp(1.1rem, 4vw, 2rem); --body-size: clamp(0.7rem, 1.2vw, 0.95rem); } .nav-dots, .keyboard-hint, .decorative { display: none; } }
        @media (max-height: 500px) { :root { --slide-padding: clamp(0.4rem, 2vw, 1rem); --title-size: clamp(1rem, 3.5vw, 1.5rem); } }
        @media (max-width: 600px) { .grid { grid-template-columns: 1fr; } }
        @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.2s !important; } html { scroll-behavior: auto; } }

        /* Scroll-triggered animations */
        .reveal { opacity: 0; transform: translateY(30px); transition: opacity var(--duration-normal) var(--ease-out-expo), transform var(--duration-normal) var(--ease-out-expo); }
        .slide.visible .reveal { opacity: 1; transform: translateY(0); }
        .reveal:nth-child(1) { transition-delay: 0.1s; }
        .reveal:nth-child(2) { transition-delay: 0.2s; }
        .reveal:nth-child(3) { transition-delay: 0.3s; }
        .reveal:nth-child(4) { transition-delay: 0.4s; }

        /* Image constraints */
        .slide-image { max-width: 100%; max-height: min(50vh, 400px); object-fit: contain; border-radius: 8px; }
        .slide-image.screenshot { border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); }
        .slide-image.logo { max-height: min(30vh, 200px); }
        .card, .container, .content-box { max-width: min(90vw, 1000px); max-height: min(80vh, 700px); }
        /* Contrast fallback: light backgrounds force dark text */
        .bl[style*="background:#f"], .bl[style*="background: #f"], .bl[style*="background:#e"], .bl[style*="background: #e"], .card[style*="background:#f"], .card[style*="background: #f"], .card[style*="background:#e"], .card[style*="background: #e"], [style*="background:#fff"], [style*="background: #fff"] { color: #1e293b !important; }
        .bl[style*="background:#f"] li, .bl[style*="background: #f"] li, .bl[style*="background:#e"] li, .bl[style*="background: #e"] li, .card[style*="background:#f"] li, .card[style*="background: #f"] li, .card[style*="background:#e"] li, .card[style*="background: #e"] li, [style*="background:#fff"] li, [style*="background: #fff"] li { color: #334155 !important; }

        /* Grid */
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 250px), 1fr)); gap: clamp(0.5rem, 1.5vw, 1rem); }

        /* ═══════════════════════════════════════════════════════
         * STYLE SIGNATURE INJECTION — MANDATORY
         * Read the selected style file's "## Signature Elements" section.
         * Copy ALL of the following into <style> at this exact position:
         *   1. CSS Overlays  → body::before, body::after (scan lines, vignette, textures)
         *   2. Animations    → all @keyframes definitions (blink, glow, lineReveal, etc.)
         *   3. Required CSS Classes → every class listed (.terminal-block, .badge, .corner-accent, etc.)
         *   4. Background Rule → follow the style's .slide / body background directive
         *   5. Style-Specific Rules → font restrictions, syntax patterns, etc.
         * Do NOT skip any item from the Signature Checklist. Missing signature elements = generation error.
         * Blue Sky exception: uses blue-sky-starter.html base, not .md signature injection.
         * ═══════════════════════════════════════════════════════ */

        /* [PASTE ALL Signature Elements CSS HERE — overlays, keyframes, required classes] */

        /* PRESENTATION MODE — button outside .slide, never in PPTX screenshots */
        #present-btn { position: fixed; bottom: 1.5rem; right: 1.5rem; z-index: 9997; width: 44px; height: 44px; border-radius: 50%; background: rgba(0,0,0,0.5); color: rgba(255,255,255,0.8); border: 1.5px solid rgba(255,255,255,0.2); font-size: 1rem; cursor: pointer; backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); display: flex; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.2s; pointer-events: none; }
        body:hover #present-btn { opacity: 1; pointer-events: auto; }
        #present-btn:hover { background: rgba(0,0,0,0.78); }

        #present-counter { display: none; position: fixed; bottom: 1.4rem; left: 50%; transform: translateX(-50%); z-index: 9997; font-size: 0.65rem; letter-spacing: 0.14em; font-family: system-ui, sans-serif; color: rgba(255,255,255,0.28); }

        body.presenting { background: #000 !important; overflow: hidden !important; }
        body.presenting .slide { position: fixed !important; inset: 0; width: 100vw !important; height: 100vh !important; transform-origin: center center; scroll-snap-align: none !important; display: none !important; }
        body.presenting .slide.p-on { display: flex !important; }
        body.presenting #present-btn { display: none !important; }
        body.presenting #present-counter { display: block; }
        body.presenting.presenting-black .slide { visibility: hidden !important; }
        body.presenting.presenting-black::after { content: ''; position: fixed; inset: 0; background: #000; z-index: 99999; }

        .slide-credit { position: absolute; bottom: 8px; right: 14px; font-size: 9px; color: var(--text-secondary, #999); opacity: 0.35; pointer-events: none; z-index: 1; font-family: system-ui, sans-serif; }
        body.presenting .slide-credit { display: none !important; }
    </style>
</head>
<body data-export-progress="true" data-preset="Enterprise Dark">
    <div class="progress-bar" style="position:fixed;top:0;left:0;height:3px;background:var(--accent);width:0%;z-index:100;transition:width 0.3s ease;"></div>
    <nav class="nav-dots" aria-label="Slide navigation"></nav>

    <!-- Slides — always add data-notes to every slide -->
    <section class="slide title-slide" data-notes="..." aria-label="Title slide">
        <div class="slide-content">
            <h1 class="reveal">Presentation Title</h1>
            <p class="reveal">Subtitle or author</p>
        </div>
    </section>

    <section class="slide" data-notes="..." aria-label="Slide 2">
        <div class="slide-content">
            <h2 class="reveal">Slide Title</h2>
            <ul class="reveal bullet-list">
                <li>Point one</li>
                <li>Point two</li>
            </ul>
        </div>
    </section>

    <!-- JS Engine: read references/js-engine.md and insert verbatim -->
    <script>
    /* [INSERT JS ENGINE FROM references/js-engine.md — SlidePresentation class, ?presenter branch, PresentMode class, watermark] */
    </script>
</body>
</html>
```

---

## Additional Animation & Effect Patterns

```css
.reveal-scale { opacity: 0; transform: scale(0.9); transition: opacity 0.6s, transform 0.6s var(--ease-out-expo); }
.slide.visible .reveal-scale { opacity: 1; transform: scale(1); }
.reveal-left { opacity: 0; transform: translateX(-50px); transition: opacity 0.6s, transform 0.6s var(--ease-out-expo); }
.slide.visible .reveal-left { opacity: 1; transform: translateX(0); }
.reveal-blur { opacity: 0; filter: blur(10px); transition: opacity 0.8s, filter 0.8s var(--ease-out-expo); }
.slide.visible .reveal-blur { opacity: 1; filter: blur(0); }
.gradient-bg { background: radial-gradient(ellipse at 20% 80%, rgba(120, 0, 255, 0.3) 0%, transparent 50%), radial-gradient(ellipse at 80% 20%, rgba(0, 255, 200, 0.2) 0%, transparent 50%), var(--bg-primary); }
.grid-bg { background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px); background-size: 50px 50px; }
```

---

## Edit Button + Notes Panel

CSS 和 HTML 结构（JS 逻辑已包含在 `references/js-engine.md` 的 SlidePresentation 类中）。

```html
<div class="edit-hotzone"></div>
<button class="edit-toggle" id="editToggle" title="Edit mode (E)">Edit</button>
<div id="notes-panel">
    <div id="notes-panel-header">
        <div id="notes-panel-label">SPEAKER NOTES — SLIDE 1 / N</div>
        <div id="notes-drag-hint"></div>
        <button id="notes-collapse-btn" title="Collapse / expand">▾</button>
    </div>
    <div id="notes-body">
        <textarea id="notes-textarea" placeholder="Add speaker notes…"></textarea>
    </div>
</div>
```

```css
.edit-hotzone { position: fixed; top: 0; left: 0; width: 80px; height: 80px; z-index: 10000; cursor: pointer; }
.edit-toggle { position: fixed; top: 16px; left: 16px; opacity: 0; pointer-events: none; transition: opacity 0.3s ease; z-index: 10001; }
.edit-toggle.show { opacity: 1; pointer-events: auto; }
.edit-toggle.active { opacity: 1; pointer-events: auto; background: var(--accent, #4f46e5); color: #fff; }

#notes-panel { display: none; position: fixed; bottom: 0; left: 0; right: 0; z-index: 9998; background: rgba(8,8,18,0.94); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border-top: 1px solid rgba(255,255,255,0.08); }
#notes-panel.active { display: flex; flex-direction: column; }
#notes-panel-header { display: flex; align-items: center; justify-content: space-between; padding: 0.45rem 1.4rem; cursor: pointer; user-select: none; }
#notes-panel-header:hover { background: rgba(255,255,255,0.03); }
#notes-panel-label { flex: 1; font-size: 0.58rem; letter-spacing: 0.16em; text-transform: uppercase; color: rgba(255,255,255,0.3); }
#notes-drag-hint { flex: 1; display: flex; justify-content: center; }
#notes-drag-hint::after { content: ''; display: block; width: 36px; height: 3px; border-radius: 2px; background: rgba(255,255,255,0.25); }
#notes-panel-header:hover #notes-drag-hint::after { background: rgba(255,255,255,0.45); }
#notes-collapse-btn { flex: 1; text-align: right; font-size: 1rem; color: rgba(255,255,255,0.4); background: none; border: none; cursor: pointer; transition: color 0.15s, transform 0.2s; }
#notes-collapse-btn:hover { color: rgba(255,255,255,0.85); }
#notes-body { padding: 0 1.4rem 0.75rem; }
#notes-panel.collapsed #notes-body { display: none; }
#notes-panel.collapsed #notes-collapse-btn { transform: rotate(180deg); }
#notes-textarea { width: 100%; height: 72px; min-height: 48px; max-height: 200px; resize: vertical; background: transparent; border: none; outline: none; color: rgba(255,255,255,0.75); font-size: 0.88rem; line-height: 1.65; font-family: system-ui, sans-serif; }
#notes-textarea::placeholder { color: rgba(255,255,255,0.18); }
```
