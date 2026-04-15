# HTML Template & Code Patterns

Read this file when generating a presentation (Phase 3). It contains the full HTML architecture, required JavaScript patterns, animation recipes, and the edit button implementation.

---

## Generation Checklist — Copy These Exactly

Every generated HTML **must** include all of the following. Do not omit any item:

1. **Present mode CSS** — `#present-btn`, `#present-counter`, `body.presenting .slide`, `body.presenting .slide.p-on`, `body.presenting.presenting-black` (see CSS block below)
2. **Edit hotzone HTML** — `<div class="edit-hotzone">` + `<button class="edit-toggle" id="editToggle">` + `#notes-panel` with textarea
3. **`SlidePresentation` class** — navigation, dots, keyboard, touch, wheel, BroadcastChannel
4. **`?presenter` branch** — replaces body with notes/timer UI when `?presenter` in URL
5. **`PresentMode` class** — inside the `else` block, before `new PresentMode(...)`. **Never put it inside the `if (presenter)` block** (class is block-scoped; it would be inaccessible in the else branch)
6. **`setupEditor()` call** — edit hotzone + notes panel wired up
7. **`data-notes` on every `<section class="slide">`** — 1–3 sentence speaker note per slide
8. **Preset fidelity metadata** — if PLANNING.md or the workflow selected a preset, honor it exactly and stamp it into HTML as `data-preset="Preset Name"` on `<body>`
9. **Watermark footer** — injected by JS into the **last slide only** as `<div class="slide-credit">By kai-slide-creator v[version] · [preset-name]</div>` with CSS: `position: absolute; bottom: 8px; right: 14px; font-size: 9px; color: var(--text-secondary, #999); opacity: 0.35; pointer-events: none; z-index: 1; font-family: system-ui, sans-serif;` and `body.presenting .slide-credit { display: none; }`. Replace `[version]` with the current skill version from SKILL.md frontmatter. Replace `[preset-name]` with the selected style preset name (e.g. `Blue Sky`, `Enterprise Dark`).

---

## HTML Architecture

Every presentation follows this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Presentation Title</title>

    <!-- Fonts: MUST come from the selected style reference file (e.g., references/data-story.md).
         DO NOT use Clash Display / Satoshi unless the style file explicitly specifies them.
         
         FONT LOADING RULE: Combine ALL font families into a SINGLE Google Fonts URL.
         Use display=swap so the browser renders immediately with system fonts, then swaps.
         Example: https://fonts.googleapis.com/css2?family=Archivo+Black&family=Space+Grotesk:wght@400;500;700&family=Noto+Sans+SC:wght@400;700&display=swap
         
         CRITICAL: Add a background-color fallback immediately after <style> starts,
         so the page never flashes white while fonts load. -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="[SINGLE COMBINED GOOGLE FONTS URL]&display=swap" rel="stylesheet">

    <style>
        /* Background fallback — must match the style's body background color
           so the page never flashes white while Google Fonts loads. */
        body { background-color: [from style file, e.g. #1a1a1a or #ffffff]; }
        /* ===========================================
           CSS CUSTOM PROPERTIES (THEME)
           CRITICAL: ALL values below MUST come from the selected
           style reference file (e.g., references/data-story.md).
           DO NOT copy these placeholder examples verbatim.
           Replace every color, font, and token with the style file's values.
           =========================================== */
        :root {
            /* REPLACE with values from the style reference file: */
            --bg-primary: [from style file];
            --bg-secondary: [from style file];
            --text-primary: [from style file];
            --text-secondary: [from style file];
            --accent: [from style file];

            /* Typography — always use clamp() for responsive scaling.
               Font names MUST come from the style reference file. */
            --font-display: '[font name from style file]', sans-serif;
            --font-body: '[font name from style file]', sans-serif;
            --title-size: clamp(2rem, 6vw, 5rem);
            --subtitle-size: clamp(0.875rem, 2vw, 1.25rem);
            --body-size: clamp(0.75rem, 1.5vw, 1.125rem);

            /* Spacing — viewport-relative so everything scales together */
            --slide-padding: clamp(1.5rem, 4vw, 4rem);
            --content-gap: clamp(1rem, 2vw, 2rem);

            /* Animation */
            --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
            --duration-normal: 0.6s;
        }

        /* Reset */
        *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

        html {
            scroll-snap-type: y mandatory;
            height: 100%;
            /* scroll-behavior intentionally omitted — JS scrollIntoView({behavior:'smooth'}) handles animation;
               CSS scroll-behavior + JS smooth scroll = double animation = jitter */
        }

        body {
            font-family: var(--font-body);
            background: var(--bg-primary);
            color: var(--text-primary);
            overflow-x: hidden;
            height: 100%;
        }
        body[data-export-progress="false"] .progress-bar,
        body[data-export-progress="false"] .nav-dots {
            display: none !important;
        }

        /* ===========================================
           SLIDE CONTAINER
           Slides must exactly fill the viewport — no scrolling within a slide.
           height: 100dvh accounts for mobile browser chrome.
           overflow: hidden is the safety net.
           =========================================== */
        .slide {
            width: 100vw;
            height: 100vh;
            height: 100dvh;
            padding: var(--slide-padding);
            scroll-snap-align: start;
            display: flex;
            flex-direction: column;
            justify-content: center;
            position: relative;
            overflow: hidden;
            /* Must carry its own background so present mode (body.presenting = #000)
               doesn't bleed through the transparent slide.
               
               EXCEPTION: If the style reference file defines body with radial-gradient,
               linear-gradient, background-image pattern, or animation background,
               DO NOT set background on .slide — let the body gradient show through.
               Instead, set background: transparent. The style file should handle this. */
            background: var(--bg-primary);
        }

        .slide-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            max-height: 100%;
            overflow: hidden;
        }

        /* Title fit guardrail:
           do not globally cap CJK or technical titles to tiny measures such as 10ch / 14ch.
           If a heading wants more than ~3 lines, rewrite the title or change the layout
           instead of forcing a six-line wrap with an artificially narrow max-width. */

        /* ===========================================
           RESPONSIVE BREAKPOINTS
           =========================================== */
        @media (max-height: 700px) {
            :root {
                --slide-padding: clamp(0.75rem, 3vw, 2rem);
                --content-gap: clamp(0.4rem, 1.5vw, 1rem);
                --title-size: clamp(1.25rem, 4.5vw, 2.5rem);
            }
        }
        @media (max-height: 600px) {
            :root {
                --slide-padding: clamp(0.5rem, 2.5vw, 1.5rem);
                --title-size: clamp(1.1rem, 4vw, 2rem);
                --body-size: clamp(0.7rem, 1.2vw, 0.95rem);
            }
            .nav-dots, .keyboard-hint, .decorative { display: none; }
        }
        @media (max-height: 500px) {
            :root {
                --slide-padding: clamp(0.4rem, 2vw, 1rem);
                --title-size: clamp(1rem, 3.5vw, 1.5rem);
            }
        }
        @media (max-width: 600px) {
            .grid { grid-template-columns: 1fr; }
        }
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                transition-duration: 0.2s !important;
            }
            html { scroll-behavior: auto; }
        }

        /* ===========================================
           SCROLL-TRIGGERED ANIMATIONS
           JS adds .visible when slide enters viewport.
           nth-child delays create a stagger effect.
           =========================================== */
        .reveal {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity var(--duration-normal) var(--ease-out-expo),
                        transform var(--duration-normal) var(--ease-out-expo);
        }
        .slide.visible .reveal { opacity: 1; transform: translateY(0); }
        .reveal:nth-child(1) { transition-delay: 0.1s; }
        .reveal:nth-child(2) { transition-delay: 0.2s; }
        .reveal:nth-child(3) { transition-delay: 0.3s; }
        .reveal:nth-child(4) { transition-delay: 0.4s; }

        /* Image constraints */
        .slide-image { max-width: 100%; max-height: min(50vh, 400px); object-fit: contain; border-radius: 8px; }
        .slide-image.screenshot { border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); }
        .slide-image.logo { max-height: min(30vh, 200px); }

        /* Cards/containers */
        .card, .container, .content-box { max-width: min(90vw, 1000px); max-height: min(80vh, 700px); }

        /* Contrast fallback: when a card/block has a light inline background,
           force dark text so #cbd5e1 / var(--text-secondary) doesn't disappear.
           Covers #f0f4f8, #fef3c7, #e8eef7, #e8f5e9, #f3e5f5, #fff, etc. */
        .bl[style*="background:#f"], .bl[style*="background: #f"],
        .bl[style*="background:#e"], .bl[style*="background: #e"],
        .card[style*="background:#f"], .card[style*="background: #f"],
        .card[style*="background:#e"], .card[style*="background: #e"],
        [style*="background:#fff"], [style*="background: #fff"] {
            color: #1e293b !important;
        }
        .bl[style*="background:#f"] li, .bl[style*="background: #f"] li,
        .bl[style*="background:#e"] li, .bl[style*="background: #e"] li,
        .card[style*="background:#f"] li, .card[style*="background: #f"] li,
        .card[style*="background:#e"] li, .card[style*="background: #e"] li,
        [style*="background:#fff"] li, [style*="background: #fff"] li {
            color: #334155 !important;
        }

        /* Grid */
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 250px), 1fr)); gap: clamp(0.5rem, 1.5vw, 1rem); }

        /* ... style-specific CSS goes here ... */

        /* ===========================================
           PRESENTATION MODE
           ▶ button is position:fixed and lives outside .slide elements.
           PPTX export uses locator('.slide').nth(i).screenshot() which
           captures each element independently — the button is never included.

           Enter: click ▶ or press F5. Exit: press ESC or Escape fullscreen.
           Slides are fixed to 1440×900px and CSS-scaled to fill any screen
           while preserving aspect ratio. Black background fills the margins.
           =========================================== */
        #present-btn {
            position: fixed; bottom: 1.5rem; right: 1.5rem; z-index: 9997;
            width: 44px; height: 44px; border-radius: 50%;
            background: rgba(0,0,0,0.5); color: rgba(255,255,255,0.8);
            border: 1.5px solid rgba(255,255,255,0.2);
            font-size: 1rem; cursor: pointer;
            backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
            display: flex; align-items: center; justify-content: center;
            opacity: 0; transition: opacity 0.2s; pointer-events: none;
        }
        body:hover #present-btn { opacity: 1; pointer-events: auto; }
        #present-btn:hover { background: rgba(0,0,0,0.78); }

        #present-counter {
            display: none; position: fixed; bottom: 1.4rem; left: 50%;
            transform: translateX(-50%); z-index: 9997;
            font-size: 0.65rem; letter-spacing: 0.14em; font-family: system-ui, sans-serif;
            color: rgba(255,255,255,0.28);
        }

        body.presenting { background: #000 !important; overflow: hidden !important; }
        body.presenting .slide {
            position: fixed !important; inset: 0;
            width: var(--pdw, 1440px) !important; height: var(--pdh, 900px) !important;
            transform-origin: top left;
            transform: translate(var(--pox, 0px), var(--poy, 0px)) scale(var(--ps, 1)) !important;
            scroll-snap-align: none !important; display: none !important;
        }
        body.presenting .slide.p-on { display: flex !important; }
        body.presenting #present-btn { display: none !important; }
        body.presenting #present-counter { display: block; }
        body.presenting.presenting-black .slide { visibility: hidden !important; }
        body.presenting.presenting-black::after { content: ''; position: fixed; inset: 0; background: #000; z-index: 99999; }

        /* ===========================================
           WATERMARK — implicit, inside last slide only.
           Low opacity, pointer-events: none, hidden in present mode.
           =========================================== */
        .slide-credit {
            position: absolute; bottom: 8px; right: 14px;
            font-size: 9px; color: var(--text-secondary, #999);
            opacity: 0.35; pointer-events: none; z-index: 1;
            font-family: system-ui, sans-serif;
        }
        body.presenting .slide-credit { display: none !important; }
    </style>
</head>
<body data-export-progress="true" data-preset="Enterprise Dark">
    <!-- Progress bar
         Set body[data-export-progress="false"] to hide both the progress bar and nav dots
         on the page and omit them from native PPT export. -->
    <div class="progress-bar" style="position:fixed;top:0;left:0;height:3px;background:var(--accent);width:0%;z-index:100;transition:width 0.3s ease;"></div>

    <!-- Navigation dots -->
    <nav class="nav-dots" aria-label="Slide navigation">
        <!-- Generated by JS -->
    </nav>

    <!-- Slides -->
    <!-- IMPORTANT: Always add data-notes="..." to every slide section.
         Notes appear in Presenter Mode (P key). Keep to 2-4 sentences.
         Example: data-notes="Introduce the problem. Pause after the headline." -->
    <section class="slide title-slide" data-notes="Welcome the audience. Briefly introduce yourself and what this talk covers." aria-label="Title slide">
        <div class="slide-content">
            <h1 class="reveal">Presentation Title</h1>
            <p class="reveal">Subtitle or author</p>
        </div>
    </section>

    <section class="slide" data-notes="Walk through each point slowly. The second bullet tends to surprise people — give it a beat." aria-label="Slide 2">
        <div class="slide-content">
            <h2 class="reveal">Slide Title</h2>
            <ul class="reveal bullet-list">
                <li>Point one</li>
                <li>Point two</li>
            </ul>
        </div>
    </section>

    <script>
        /* ===========================================
           SLIDE PRESENTATION CONTROLLER
           Navigation: arrow keys, space, swipe, scroll wheel.
           Presenter Mode: press P to open presenter window.
           =========================================== */
        class SlidePresentation {
            constructor() {
                this.slides = document.querySelectorAll('.slide');
                this.currentSlide = 0;
                this.channel = new BroadcastChannel('slide-creator-presenter');

                // CRITICAL: Make first slide visible immediately on page load.
                // IntersectionObserver with threshold:0.5 may not fire for the first slide
                // since it's already in the viewport — without this, all .reveal elements
                // stay at opacity:0 and the page renders black.
                this.slides[0]?.classList.add('visible');
                this.slides[0]?.querySelectorAll('.reveal').forEach(function(r) {
                    r.classList.add('visible');
                });

                this.setupNavDots();
                this.setupObserver();
                this.setupKeyboard();
                this.setupTouch();
                this.setupWheel();
                this.setupPresenter();
                this.updateProgress();
            }

            setupNavDots() {
                const nav = document.querySelector('.nav-dots');
                if (!nav) return;
                this.slides.forEach((_, i) => {
                    const dot = document.createElement('button');
                    dot.setAttribute('aria-label', `Go to slide ${i + 1}`);
                    dot.style.cssText = 'width:8px;height:8px;border-radius:50%;border:none;cursor:pointer;background:rgba(255,255,255,0.3);transition:all 0.3s;';
                    dot.addEventListener('click', () => this.goTo(i));
                    nav.appendChild(dot);
                });
                nav.style.cssText = 'position:fixed;right:1.5rem;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;gap:8px;z-index:100;';
            }

            setupObserver() {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.classList.add('visible');
                            this.currentSlide = [...this.slides].indexOf(entry.target);
                            this.updateProgress();
                            this.updateDots();
                            this.broadcastState();
                        }
                    });
                }, { threshold: 0.5 });
                this.slides.forEach(s => observer.observe(s));
            }

            setupKeyboard() {
                document.addEventListener('keydown', (e) => {
                    if (e.target.getAttribute('contenteditable')) return;
                    if (e.key === 'ArrowDown' || e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown' || e.key === 'Enter') {
                        e.preventDefault(); this.next();
                    } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft' || e.key === 'PageUp' || e.key === 'Backspace') {
                        e.preventDefault(); this.prev();
                    } else if (e.key === 'p' || e.key === 'P') {
                        /* Open presenter window — same file, ?presenter param */
                        const url = location.href.split('?')[0] + '?presenter';
                        window.open(url, 'slide-presenter-' + Date.now(), 'width=1100,menubar=no,toolbar=no,location=no');
                    }
                });
            }

            setupTouch() {
                let startY = 0;
                document.addEventListener('touchstart', e => { startY = e.touches[0].clientY; }, { passive: true });
                document.addEventListener('touchend', e => {
                    const delta = startY - e.changedTouches[0].clientY;
                    if (Math.abs(delta) > 50) delta > 0 ? this.next() : this.prev();
                });
            }

            setupWheel() {
                /* scroll-snap-type: y mandatory handles trackpad/mouse wheel natively.
                   No JS wheel handler needed — IntersectionObserver keeps state in sync.
                   DO NOT add a JS wheel handler here: it will fight scroll-snap and cause
                   jitter (double animation) or multi-page advancement (momentum tail). */
            }

            setupPresenter() {
                /* Listen for navigation commands from the presenter window */
                this.channel.addEventListener('message', e => {
                    if (e.data.type === 'nav-next') this.next();
                    else if (e.data.type === 'nav-prev') this.prev();
                    else if (e.data.type === 'request-state') this.broadcastState();
                });
            }

            broadcastState() {
                const slide = this.slides[this.currentSlide];
                this.channel.postMessage({
                    type: 'state',
                    index: this.currentSlide,
                    total: this.slides.length,
                    notes: slide?.dataset.notes || ''
                });
            }

            goTo(index) {
                this.slides.forEach((slide, i) => {
                    slide.classList.toggle('visible', i === index);
                    var reveals = slide.querySelectorAll('.reveal');
                    reveals.forEach(function(r) { r.classList.toggle('visible', i === index); });
                });
                this.slides[index]?.scrollIntoView({ behavior: 'smooth' });
            }
            next() { this.goTo(Math.min(this.currentSlide + 1, this.slides.length - 1)); }
            prev() { this.goTo(Math.max(this.currentSlide - 1, 0)); }

            updateProgress() {
                const pct = (this.currentSlide / (this.slides.length - 1)) * 100;
                const bar = document.querySelector('.progress-bar');
                if (bar) bar.style.width = pct + '%';
            }

            updateDots() {
                document.querySelectorAll('.nav-dots button').forEach((dot, i) => {
                    dot.style.background = i === this.currentSlide ? 'var(--accent)' : 'rgba(255,255,255,0.3)';
                    dot.style.transform = i === this.currentSlide ? 'scale(1.3)' : 'scale(1)';
                });
            }
        }

        /* ===========================================
           PRESENTER MODE
           Activated when URL contains ?presenter.
           Shows notes, timer, and nav controls.
           Syncs with the main window via BroadcastChannel.
           =========================================== */
        if (new URLSearchParams(location.search).has('presenter')) {
            document.title = 'Presenter — ' + document.title;
            document.body.innerHTML = `
            <style>
                * { box-sizing: border-box; margin: 0; }
                body { background: #111; color: #fff; font-family: system-ui, sans-serif; }
                #pv { display: grid; grid-template-columns: 1fr 220px; gap: 1rem; padding: 1.25rem; align-items: start; }
                .pv-panel { background: #1e1e1e; border-radius: 12px; padding: 1.25rem; }
                #pv-label { font-size: 0.6rem; letter-spacing: 0.18em; text-transform: uppercase; color: #555; margin-bottom: 0.6rem; }
                #pv-notes { font-size: 1.05rem; line-height: 1.85; color: #d0d0d0; }
                #pv-right { display: flex; flex-direction: column; gap: 1rem; }
                #pv-nav { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }
                .pv-arrow { width: 32px; height: 32px; border-radius: 6px; border: 1px solid #333; background: #2a2a2a; color: #aaa; font-size: 1rem; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.15s, color 0.15s; flex-shrink: 0; }
                .pv-arrow:hover { background: #383838; color: #fff; }
                #pv-counter { text-align: center; flex: 1; }
                #pv-num { font-size: 1.6rem; font-weight: 700; font-variant-numeric: tabular-nums; line-height: 1; }
                #pv-of { color: #555; font-size: 0.75rem; margin-top: 0.2rem; }
                #pv-timer-box { text-align: center; }
                #pv-timer-label { font-size: 0.6rem; letter-spacing: 0.18em; text-transform: uppercase; color: #555; margin-bottom: 0.3rem; }
                #pv-timer { font-size: 1.5rem; font-weight: 700; font-family: monospace; font-variant-numeric: tabular-nums; }
            </style>
            <div id="pv">
                <div class="pv-panel">
                    <div id="pv-label">Speaker Notes</div>
                    <div id="pv-notes">Waiting for main window…</div>
                </div>
                <div id="pv-right">
                    <div class="pv-panel">
                        <div id="pv-nav">
                            <button class="pv-arrow" id="pv-prev">←</button>
                            <div id="pv-counter">
                                <div id="pv-num">—</div>
                                <div id="pv-of">/ —</div>
                            </div>
                            <button class="pv-arrow" id="pv-next">→</button>
                        </div>
                    </div>
                    <div class="pv-panel" id="pv-timer-box">
                        <div id="pv-timer-label">Elapsed</div>
                        <div id="pv-timer">0:00</div>
                    </div>
                </div>
            </div>`;

            const ch = new BroadcastChannel('slide-creator-presenter');
            let startTime = null;

            /* ResizeObserver fires whenever #pv height changes (content update or text rewrap).
               Only HEIGHT is changed — width stays fixed — so no infinite loop. */
            const pv = document.getElementById('pv');
            let lastH = 0, roTimer = null;
            new ResizeObserver(() => {
                clearTimeout(roTimer);
                roTimer = setTimeout(() => {
                    const h = Math.ceil(pv.getBoundingClientRect().height);
                    if (h === lastH) return;
                    lastH = h;
                    const chrome = window.outerHeight - window.innerHeight;
                    window.resizeTo(window.outerWidth, Math.max(260, h + chrome + 4));
                }, 40);
            }).observe(pv);

            ch.addEventListener('message', e => {
                if (e.data.type !== 'state') return;
                if (!startTime) startTime = Date.now();
                document.getElementById('pv-notes').textContent = e.data.notes || '(no notes for this slide)';
                document.getElementById('pv-num').textContent = e.data.index + 1;
                document.getElementById('pv-of').textContent = `/ ${e.data.total}`;
            });

            /* Request current state from main window */
            ch.postMessage({ type: 'request-state' });

            /* Elapsed timer */
            setInterval(() => {
                if (!startTime) return;
                const s = Math.floor((Date.now() - startTime) / 1000);
                document.getElementById('pv-timer').textContent =
                    `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
            }, 1000);

            /* Nav buttons and keyboard */
            document.getElementById('pv-prev').addEventListener('click', () => ch.postMessage({ type: 'nav-prev' }));
            document.getElementById('pv-next').addEventListener('click', () => ch.postMessage({ type: 'nav-next' }));
            document.addEventListener('keydown', e => {
                if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ' || e.key === 'PageDown' || e.key === 'Enter') ch.postMessage({ type: 'nav-next' });
                else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp' || e.key === 'PageUp' || e.key === 'Backspace') ch.postMessage({ type: 'nav-prev' });
            });

        } else {
        /* ===========================================
           PRESENTATION MODE CONTROLLER
           Scales slides to fill any screen. Intercepts goTo() so arrow-key
           navigation works without scrollIntoView() (which breaks when slides
           are position:fixed).

           IMPORTANT: this class must stay in the else block (main window only).
           The ?presenter branch replaces document.body entirely so PresentMode
           is never needed there.
           =========================================== */
        class PresentMode {
            constructor(ctrl) {
                this.ctrl = ctrl;
                this.DW = 1440; this.DH = 900;
                this.active = false;
                this._resize = () => this._scale();

                // Create play button and slide counter in JS —
                // both live outside .slide so they never appear in PPTX screenshots
                const btn = document.createElement('button');
                btn.id = 'present-btn';
                btn.title = 'Present (F5)';
                btn.setAttribute('aria-label', 'Present');
                btn.textContent = '▶';
                document.body.appendChild(btn);

                const counter = document.createElement('div');
                counter.id = 'present-counter';
                document.body.appendChild(counter);

                btn.addEventListener('click', () => this.enter());
                document.addEventListener('keydown', e => {
                    if (e.key === 'F5')                  { e.preventDefault(); this.enter(); }
                    if (e.key === 'Escape' && this.active) this.exit();
                    if ((e.key === 'b' || e.key === 'B') && this.active) document.body.classList.toggle('presenting-black');
                });
                document.addEventListener('fullscreenchange', () => {
                    if (!document.fullscreenElement && this.active) this.exit();
                });
            }

            enter() {
                if (this.active) return;
                this.active = true;
                document.body.classList.add('presenting');
                document.documentElement.requestFullscreen?.().catch(() => {});
                window.addEventListener('resize', this._resize);
                this._scale();
                this._show(this.ctrl.currentSlide);

                // Override goTo: skip scrollIntoView, keep visible class + reveal animations
                this._origGoTo = this.ctrl.goTo.bind(this.ctrl);
                this.ctrl.goTo = (i) => {
                    const idx = Math.max(0, Math.min(i, this.ctrl.slides.length - 1));
                    this.ctrl.currentSlide = idx;
                    this.ctrl.slides.forEach((s, j) => s.classList.toggle('visible', j === idx));
                    this._show(idx);
                    this.ctrl.updateProgress?.();
                    this.ctrl.updateDots?.();
                    this.ctrl.broadcastState?.();
                };
            }

            exit() {
                if (!this.active) return;
                this.active = false;
                document.body.classList.remove('presenting', 'presenting-black');
                document.querySelectorAll('.slide').forEach(s => s.classList.remove('p-on'));
                if (document.fullscreenElement) document.exitFullscreen?.();
                window.removeEventListener('resize', this._resize);
                if (this._origGoTo) { this.ctrl.goTo = this._origGoTo; this._origGoTo = null; }
                // Restore scroll position to current slide
                this.ctrl.slides[this.ctrl.currentSlide]?.scrollIntoView({ behavior: 'instant' });
            }

            _scale() {
                const s  = Math.min(window.innerWidth / this.DW, window.innerHeight / this.DH);
                const ox = (window.innerWidth  - this.DW * s) / 2;
                const oy = (window.innerHeight - this.DH * s) / 2;
                const r  = document.documentElement;
                r.style.setProperty('--pdw', this.DW + 'px');
                r.style.setProperty('--pdh', this.DH + 'px');
                r.style.setProperty('--ps',  s);
                r.style.setProperty('--pox', ox + 'px');
                r.style.setProperty('--poy', oy + 'px');
            }

            _show(i) {
                document.querySelectorAll('.slide').forEach((s, idx) => s.classList.toggle('p-on', idx === i));
                const c = document.getElementById('present-counter');
                if (c) c.textContent = `${i + 1} / ${this.ctrl.slides.length}`;
            }
        }

            new PresentMode(new SlidePresentation());
        }
    </script>
    <script>
    // Watermark — injected into last slide only
    (function() {
        var slides = document.querySelectorAll('.slide');
        if (!slides.length) return;
        var last = slides[slides.length - 1];
        var credit = document.createElement('div');
        credit.className = 'slide-credit';
        credit.textContent = 'By kai-slide-creator v[version] · [preset-name]';
        last.appendChild(credit);
    })();
    </script>
</body>
</html>
```

---

## Signature Elements Per Style

**CRITICAL:** Each style has signature visual elements that MUST be injected into **every slide** as direct children of `<section class="slide">`. These are NOT optional — they are what gives each preset its distinctive identity.

When generating, read the selected style's reference file and check its `## Signature Elements` section. For each signature element, inject the corresponding HTML into every slide.

### Bold Signal

Every slide must have:
```html
<section class="slide" data-notes="..." aria-label="...">
    <div class="slide-num">01</div>          <!-- top-left large section number -->
    <div class="breadcrumb">Title</div>       <!-- top-right breadcrumb -->
    <div class="slide-content">...</div>
</section>
```
Plus `.slide::after` grid overlay CSS (see style file).

### Enterprise Dark

Every slide must have `.slide::after` grid overlay:
```css
.slide::after {
    content: ''; position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(48,54,61,0.3) 1px, transparent 1px),
        linear-gradient(90deg, rgba(48,54,61,0.3) 1px, transparent 1px);
    background-size: 24px 24px;
    pointer-events: none; z-index: 0;
}
```

### Neon Cyber

Every slide must have `.slide::after` grid overlay (cyan):
```css
.slide::after {
    content: ''; position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(0,255,255,0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,255,0.06) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none; z-index: 0;
}
```

### Terminal Green

Every slide must have `.slide::after` scan-line overlay:
```css
.slide::after {
    content: ''; position: absolute; inset: 0;
    background: repeating-linear-gradient(
        0deg, transparent, transparent 2px, rgba(0,255,65,0.03) 2px, rgba(0,255,65,0.03) 4px
    );
    pointer-events: none; z-index: 0;
}
```

### Creative Voltage

Every slide must have `.slide::after` halftone pattern:
```css
.slide::after {
    content: ''; position: absolute; inset: 0;
    background-image: radial-gradient(circle, rgba(212,255,0,0.08) 1px, transparent 1px);
    background-size: 8px 8px;
    pointer-events: none; z-index: 0;
}
```

### Dark Botanical

Every slide must have 2-3 `.botanical-orb` elements placed in background corners:
```html
<section class="slide">
    <div class="botanical-orb orb-terracotta" style="width:300px;height:300px;top:-5%;right:-5%;"></div>
    <div class="botanical-orb orb-pink" style="width:200px;height:200px;bottom:10%;left:-3%;"></div>
    <div class="slide-content">...</div>
</section>
```

### Glassmorphism

Every slide must have 3 `.glass-orb` elements:
```html
<section class="slide">
    <div class="glass-orb orb-1"></div>
    <div class="glass-orb orb-2"></div>
    <div class="glass-orb orb-3"></div>
    <div class="slide-content">...</div>
</section>
```

### Swiss Modern

Every slide must have `.slide::after` 12-column grid overlay:
```css
.slide::after {
    content: ''; position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(10,10,10,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(10,10,10,0.04) 1px, transparent 1px);
    background-size: calc(100% / 12) 24px;
    pointer-events: none; z-index: 0;
}
```

### Neo-Retro Dev

Every slide must have `.slide::after` graph-paper grid:
```css
.slide::after {
    content: ''; position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(70,130,180,0.08) 1px, transparent 1px),
        linear-gradient(90deg, rgba(70,130,180,0.08) 1px, transparent 1px);
    background-size: 20px 20px;
    pointer-events: none; z-index: 0;
}
```

### Chinese Chan

Every slide may have at most ONE decorative element (`.zen-rule`, `.zen-ghost-kanji`, or `.zen-dot`). Never more than one per slide.

### Aurora Mesh

Every slide must have a mesh gradient body background with 4-6 color stops. No `.slide::after` pattern — the background IS the signature element.

```css
body {
    background:
        radial-gradient(ellipse at 20% 50%, rgba(120, 0, 255, 0.4) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, rgba(0, 255, 200, 0.3) 0%, transparent 50%),
        radial-gradient(ellipse at 40% 80%, rgba(255, 0, 128, 0.25) 0%, transparent 50%),
        radial-gradient(ellipse at 90% 80%, rgba(0, 128, 255, 0.3) 0%, transparent 50%),
        #0a0a1a;
    background-attachment: fixed;
}
```

Cards must use frosted glass treatment:
```css
.glass-card {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
}
```

No Google Fonts — use system font stack: `font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`.

### Data Story

Clean white/light background. No background patterns or overlays. Signature comes from data-focused components:

```html
<section class="slide">
    <div class="slide-content">
        <div class="chart-container">
            <!-- SVG or canvas chart goes here -->
        </div>
        <div class="data-callout">
            <span class="data-stat">87%</span>
            <span class="data-label">Key metric</span>
        </div>
    </div>
</section>
```

Chart components: `.chart-container`, `.data-callout`, `.data-stat`, `.data-label`, `.mini-chart`. White cards with subtle shadow on light background. Typography: clear hierarchy with numbers as focal points.

### Electric Studio

Every slide must have a two-panel vertical split layout with accent bar:

```html
<section class="slide">
    <div class="split-left">
        <div class="accent-bar"></div>
        <div class="slide-content">...</div>
    </div>
    <div class="split-right">
        <div class="slide-content">...</div>
    </div>
</section>
```

```css
.split-left { flex: 1; position: relative; padding-left: 4px; }
.accent-bar {
    position: absolute; left: 0; top: 0; bottom: 0;
    width: 4px; background: var(--accent);
}
.split-right { flex: 1; }
.slide { flex-direction: row; }
```

Bold color blocking with electric blue + hot pink accents. Manrope font family. No background patterns — split colors create the visual interest.

### Modern Newspaper

Every slide must have yellow accent bar and issue stamp:

```html
<section class="slide">
    <div class="yellow-bar"></div>
    <div class="issue-stamp">VOL.01 · NO.03</div>
    <div class="slide-content">
        <div class="headline">...</div>
        <div class="columns">
            <div class="col">...</div>
            <div class="col">...</div>
        </div>
    </div>
</section>
```

```css
.yellow-bar {
    position: absolute; top: 0; left: 0; right: 0;
    height: 12px; background: #FFCC00;
}
.issue-stamp {
    position: absolute; top: 20px; right: 20px;
    font-size: 0.65rem; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--text-secondary);
    border: 1px solid currentColor; padding: 4px 8px;
}
.columns { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
.col { border-left: 1px solid #111111; padding-left: 1rem; }
```

Cream background `#faf8f0`. Serif display font + sans-serif body. Column rules `1px solid #111111`. Yellow bar `#FFCC00` (8-14px) as section opener.

### Neo-Brutalism

Every container must have hard offset shadows and zero border-radius:

```css
.brutal-card {
    background: var(--card-bg);
    border: 3px solid #000;
    border-radius: 0;
    box-shadow: 4px 4px 0 #000;
    padding: 1rem;
}
.brutal-stat {
    font-size: clamp(2rem, 5vw, 4rem);
    font-weight: 900;
    background: var(--accent);
    border: 3px solid #000;
    box-shadow: 6px 6px 0 #000;
    padding: 0.75rem 1.5rem;
    display: inline-block;
}
.brutal-btn {
    background: var(--accent);
    border: 3px solid #000;
    border-radius: 0;
    box-shadow: 4px 4px 0 #000;
    padding: 0.75rem 1.5rem;
    font-weight: 700;
    cursor: pointer;
    transition: transform 0.1s, box-shadow 0.1s;
}
.brutal-btn:hover { transform: translate(2px, 2px); box-shadow: 2px 2px 0 #000; }
```

High-contrast color blocking. Thick borders everywhere. No rounded corners. Offset shadows are the signature — every elevated element casts a hard 4px shadow.

### Notebook Tabs

Every slide must have paper container, binder holes, and side tabs:

```html
<section class="slide">
    <div class="paper-container">
        <div class="binder-holes">
            <div class="hole"></div>
            <div class="hole"></div>
            <div class="hole"></div>
        </div>
        <div class="side-tabs">
            <div class="tab active">Section 1</div>
            <div class="tab">Section 2</div>
            <div class="tab">Section 3</div>
        </div>
        <div class="slide-content">...</div>
    </div>
</section>
```

```css
.paper-container {
    background: #faf8f0;
    box-shadow: 2px 4px 12px rgba(0,0,0,0.15);
    border-radius: 2px;
    position: relative;
    padding: 2rem;
}
.binder-holes {
    position: absolute; left: 12px; top: 0; bottom: 0;
    display: flex; flex-direction: column; gap: 80px;
    padding: 40px 0;
}
.hole {
    width: 16px; height: 16px;
    border-radius: 50%;
    background: var(--bg-primary);
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.3);
}
.side-tabs {
    position: absolute; right: -60px; top: 20px;
    display: flex; flex-direction: column; gap: 4px;
}
.tab {
    background: var(--tab-color);
    color: #fff; font-size: 0.6rem; font-weight: 700;
    padding: 6px 12px; border-radius: 0 4px 4px 0;
    writing-mode: vertical-lr; text-orientation: mixed;
    letter-spacing: 0.08em;
}
.tab.active { background: var(--accent); padding-right: 16px; }
```

Kraft paper aesthetic. Warm background. Colorful vertical tabs on right edge. Binder hole decorations on left. Paper container with subtle shadow.

### Paper & Ink

Narrow column layout — no background patterns, no geometric shapes, no gradients:

```html
<section class="slide">
    <div class="narrow-column">
        <div class="slide-content">
            <h1 class="display-title">Title</h1>
            <p class="body-text">Content</p>
        </div>
    </div>
</section>
```

```css
.narrow-column {
    max-width: 680px;
    margin: 0 auto;
    padding: var(--slide-padding);
}
.display-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 400;
    line-height: 1.15;
}
.body-text {
    font-size: clamp(0.875rem, 1.8vw, 1.125rem);
    line-height: 1.7;
    color: var(--text-secondary);
}
.rule-divider {
    width: 40px; height: 1px;
    background: var(--text-primary);
    margin: 1rem 0;
}
```

Typography-driven design. Narrow centered column. Generous whitespace. Rule dividers between sections. Serif display font + clean sans-serif body. No bright colors, no geometric shapes, no gradients.

### Pastel Geometry

White card on pastel background with vertical pills:

```html
<section class="slide">
    <div class="pastel-bg"></div>
    <div class="white-card">
        <div class="slide-content">...</div>
    </div>
    <div class="pill-strip">
        <div class="pill" style="height: 40px;"></div>
        <div class="pill" style="height: 60px;"></div>
        <div class="pill" style="height: 30px;"></div>
    </div>
</section>
```

```css
.pastel-bg {
    position: absolute; inset: 0;
    background: linear-gradient(135deg, #fce4ec, #e3f2fd, #f3e5f5);
}
.white-card {
    position: relative; z-index: 1;
    background: #fff;
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.08);
    padding: 2rem;
    max-width: 900px;
    margin: 0 auto;
}
.pill-strip {
    position: absolute; right: 2rem; top: 50%;
    transform: translateY(-50%);
    display: flex; flex-direction: column; gap: 8px;
}
.pill {
    width: 12px; border-radius: 6px;
    background: var(--pill-color);
}
```

Pink/blue gradient background. Clean white card with generous rounded corners (20px). Vertical pill strips on right edge with varying heights. Soft pastel colors throughout.

### Split Pastel

Split background colors with grid overlay on right panel:

```html
<section class="slide">
    <div class="split-bg-left"></div>
    <div class="split-bg-right">
        <div class="grid-overlay"></div>
    </div>
    <div class="slide-content">
        <div class="left-panel">...</div>
        <div class="right-panel">...</div>
    </div>
    <div class="badge-pill">
        <span class="badge-icon">★</span>
        <span class="badge-text">Highlight</span>
    </div>
</section>
```

```css
.split-bg-left {
    position: absolute; left: 0; top: 0; bottom: 0; width: 50%;
    background: var(--split-left-color); /* e.g. peach */
}
.split-bg-right {
    position: absolute; right: 0; top: 0; bottom: 0; width: 50%;
    background: var(--split-right-color); /* e.g. lavender */
}
.grid-overlay {
    position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(0,0,0,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,0,0,0.04) 1px, transparent 1px);
    background-size: 24px 24px;
    pointer-events: none;
}
.badge-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--accent);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.75rem;
    font-weight: 600;
}
```

Peach left / lavender right split. Grid pattern overlay on right panel only. Badge pills with icons. Soft pastel color palette.

### Vintage Editorial

Cream background with abstract geometric shapes and serif typography:

```html
<section class="slide">
    <div class="geo-circle"></div>
    <div class="geo-line"></div>
    <div class="geo-dot"></div>
    <div class="slide-content">
        <div class="editorial-headline">...</div>
        <div class="editorial-body">...</div>
    </div>
</section>
```

```css
.geo-circle {
    position: absolute;
    width: 200px; height: 200px;
    border: 1px solid rgba(0,0,0,0.15);
    border-radius: 50%;
    top: 10%; right: 10%;
}
.geo-line {
    position: absolute;
    width: 120px; height: 1px;
    background: rgba(0,0,0,0.2);
    bottom: 20%; left: 8%;
    transform: rotate(-15deg);
}
.geo-dot {
    position: absolute;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent);
    top: 15%; left: 15%;
}
.editorial-headline {
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-size: clamp(1.5rem, 4vw, 3rem);
    line-height: 1.2;
}
.editorial-body {
    font-family: 'Source Sans 3', sans-serif;
    font-size: clamp(0.8rem, 1.5vw, 1rem);
    line-height: 1.6;
    color: var(--text-secondary);
}
```

Cream background `#f5f0e8`. Abstract geometric shapes: circle outline + line + dot positioned at various points. Cormorant Garamond italic for display, Source Sans 3 for body. Editorial column feel.

### Blue Sky

Use `blue-sky-starter.html` as the base. All signature elements are pre-built (orbs, clouds, glass cards). Only fill in slide content. Do not regenerate the CSS from scratch.

### Creative Voltage

Every slide must have `.slide::after` halftone pattern:
```css
.slide::after {
    content: ''; position: absolute; inset: 0;
    background-image: radial-gradient(circle, rgba(212,255,0,0.08) 1px, transparent 1px);
    background-size: 8px 8px;
    pointer-events: none; z-index: 0;
}
```

Neon yellow accent `#d4ff00` on dark `#1a1a2e`. Diamond-shaped decorative elements. Bold, high-contrast visual treatment.

### Dark Botanical

Every slide must have 2-3 `.botanical-orb` elements placed in background corners:
```html
<div class="botanical-orb orb-terracotta" style="width:300px;height:300px;top:-5%;right:-5%;"></div>
<div class="botanical-orb orb-pink" style="width:200px;height:200px;bottom:10%;left:-3%;"></div>
```

Soft gradient orbs in terracotta/pink/gold on `#0f0f0f` background. Orbs are large (200-400px) with soft radial gradients.

### Glassmorphism

Every slide must have 3 `.glass-orb` elements:
```html
<div class="glass-orb orb-1"></div>
<div class="glass-orb orb-2"></div>
<div class="glass-orb orb-3"></div>
```

Cards use `backdrop-filter: blur(12px)`. Orbs are positioned at different corners with varying sizes and colors.

### Neo-Brutalism

All containers: `box-shadow: 4px 4px 0 #000`, `border-radius: 0`, `border: 3px solid #000` minimum. High-contrast color blocking. Zero border-radius everywhere.

### Neo-Retro Dev

Every slide must have `.slide::after` graph-paper grid:
```css
.slide::after {
    content: ''; position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(70,130,180,0.08) 1px, transparent 1px),
        linear-gradient(90deg, rgba(70,130,180,0.08) 1px, transparent 1px);
    background-size: 20px 20px;
    pointer-events: none; z-index: 0;
}
```

Cream background `#f5f2e8` with faint blue grid. Monospace + sans-serif font pairing.

### Neon Cyber

Every slide must have `.slide::after` grid overlay (cyan):
```css
.slide::after {
    content: ''; position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(0,255,255,0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,255,0.06) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none; z-index: 0;
}
```

Dark `#0a0f1c` with cyan grid. Neon glow effects on accent elements.

### Notebook Tabs

Must have colorful section tabs on right edge (vertical text). Paper container with subtle shadow. Binder hole decorations on left edge.

### Paper & Ink

Narrow column layout. No background patterns. Typography and rules only — no bright colors, no geometric shapes, no gradients. Max-width ~680px centered.

### Pastel Geometry

White card on pink/blue gradient background. Vertical pills on right edge with varying heights. Soft pastel colors. Rounded corners (20px) on cards.

### Split Pastel

Split background colors (peach left, lavender right). Grid pattern overlay on right panel. Badge pills with icons.

### Swiss Modern

Every slide must have `.slide::after` 12-column grid overlay:
```css
.slide::after {
    content: ''; position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(10,10,10,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(10,10,10,0.04) 1px, transparent 1px);
    background-size: calc(100% / 12) 24px;
    pointer-events: none; z-index: 0;
}
```

White background. Hard horizontal rules `2px solid #0a0a0a`. 12-column grid system.

### Terminal Green

Every slide must have `.slide::after` scan-line overlay:
```css
.slide::after {
    content: ''; position: absolute; inset: 0;
    background: repeating-linear-gradient(
        0deg, transparent, transparent 2px, rgba(0,255,65,0.03) 2px, rgba(0,255,65,0.03) 4px
    );
    pointer-events: none; z-index: 0;
}
```

Monospace font, dark background. Green `#00ff41` as primary accent. Terminal-style command blocks.

### Vintage Editorial

Cream background `#f5f0e8` with abstract geometric shapes: circle outline (`border: 1px solid`) + line (`1px` rule) + dot (`border-radius: 50%`). Serif typography (Cormorant italic).

### All Other Styles

If the style reference file's `## Signature Elements` section mentions background patterns (grids, orbs, lines, halftones, scan-lines, geometric shapes), those patterns MUST be injected as either:
- `.slide::after` / `.slide::before` CSS pseudo-elements (for grid/line patterns)
- Direct child `<div>` elements of `.slide` (for orbs, shapes, kanji)

**Rule of thumb:** If a style's original demos had visible background textures that are NOT just a solid color, the generated HTML MUST replicate those textures. A missing grid overlay or missing orb elements = generation error.

---

## Additional Animation Patterns

### Entrance Variations

```css
/* Scale In */
.reveal-scale { opacity: 0; transform: scale(0.9); transition: opacity 0.6s, transform 0.6s var(--ease-out-expo); }
.slide.visible .reveal-scale { opacity: 1; transform: scale(1); }

/* Slide from Left */
.reveal-left { opacity: 0; transform: translateX(-50px); transition: opacity 0.6s, transform 0.6s var(--ease-out-expo); }
.slide.visible .reveal-left { opacity: 1; transform: translateX(0); }

/* Blur In */
.reveal-blur { opacity: 0; filter: blur(10px); transition: opacity 0.8s, filter 0.8s var(--ease-out-expo); }
.slide.visible .reveal-blur { opacity: 1; filter: blur(0); }
```

### Background Effects

```css
/* Gradient Mesh */
.gradient-bg {
    background:
        radial-gradient(ellipse at 20% 80%, rgba(120, 0, 255, 0.3) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, rgba(0, 255, 200, 0.2) 0%, transparent 50%),
        var(--bg-primary);
}

/* Subtle Grid Pattern */
.grid-bg {
    background-image:
        linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 50px 50px;
}
```

### Interactive: 3D Tilt on Hover

```javascript
class TiltEffect {
    constructor(element) {
        element.style.transformStyle = 'preserve-3d';
        element.addEventListener('mousemove', (e) => {
            const rect = element.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;
            element.style.transform = `rotateY(${x * 10}deg) rotateX(${-y * 10}deg)`;
        });
        element.addEventListener('mouseleave', () => { element.style.transform = ''; });
    }
}
```

---

## Edit Button + Notes Panel (Included by Default — omit only if user explicitly chose "No")

The CSS-only hover approach (`hotzone:hover ~ .edit-toggle`) fails because `pointer-events: none` breaks the hover chain — the button disappears before the user can click it. Use JS with a grace period instead.

The notes panel appears at the bottom in edit mode. Users click the header row to collapse/expand it so it doesn't block slide content. Edits to notes are written to `data-notes` in real time and broadcast to any open presenter window.

```html
<div class="edit-hotzone"></div>
<button class="edit-toggle" id="editToggle" title="Edit mode (E)">✏ Edit</button>

<!-- Notes editor panel — shown only in edit mode -->
<div id="notes-panel">
    <div id="notes-panel-header">
        <div id="notes-panel-label">SPEAKER NOTES — SLIDE 1 / N</div>
        <div id="notes-drag-hint"></div>
        <button id="notes-collapse-btn" title="Collapse / expand">▾</button>
    </div>
    <div id="notes-body">
        <textarea id="notes-textarea" placeholder="Add speaker notes for this slide…"></textarea>
    </div>
</div>
```

```css
.edit-hotzone {
    position: fixed; top: 0; left: 0;
    width: 80px; height: 80px;
    z-index: 10000; cursor: pointer;
}
.edit-toggle {
    position: fixed; top: 16px; left: 16px;
    opacity: 0; pointer-events: none;
    transition: opacity 0.3s ease; z-index: 10001;
}
.edit-toggle.show { opacity: 1; pointer-events: auto; }
.edit-toggle.active { opacity: 1; pointer-events: auto; background: var(--accent, #4f46e5); color: #fff; }

/* Notes panel */
#notes-panel {
    display: none; position: fixed; bottom: 0; left: 0; right: 0;
    z-index: 9998;
    background: rgba(8, 8, 18, 0.94);
    backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
    border-top: 1px solid rgba(255,255,255,0.08);
}
#notes-panel.active { display: flex; flex-direction: column; }
#notes-panel-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.45rem 1.4rem; cursor: pointer; user-select: none;
}
#notes-panel-header:hover { background: rgba(255,255,255,0.03); }
#notes-panel-label {
    flex: 1; font-size: 0.58rem; letter-spacing: 0.16em;
    text-transform: uppercase; color: rgba(255,255,255,0.3);
}
#notes-drag-hint { flex: 1; display: flex; justify-content: center; }
#notes-drag-hint::after {
    content: ''; display: block; width: 36px; height: 3px;
    border-radius: 2px; background: rgba(255,255,255,0.25);
}
#notes-panel-header:hover #notes-drag-hint::after { background: rgba(255,255,255,0.45); }
#notes-collapse-btn {
    flex: 1; text-align: right;
    font-size: 1rem; color: rgba(255,255,255,0.4);
    background: none; border: none; cursor: pointer;
    transition: color 0.15s, transform 0.2s;
}
#notes-collapse-btn:hover { color: rgba(255,255,255,0.85); }
#notes-body { padding: 0 1.4rem 0.75rem; }
#notes-panel.collapsed #notes-body { display: none; }
#notes-panel.collapsed #notes-collapse-btn { transform: rotate(180deg); }
#notes-textarea {
    width: 100%; height: 72px; min-height: 48px; max-height: 200px;
    resize: vertical; background: transparent; border: none; outline: none;
    color: rgba(255,255,255,0.75); font-size: 0.88rem; line-height: 1.65;
    font-family: system-ui, sans-serif; caret-color: var(--accent, #4f46e5);
}
#notes-textarea::placeholder { color: rgba(255,255,255,0.18); }
```

```javascript
// ── Edit mode + notes panel ──────────────────────────────────────
// Must integrate with SlidePresentation: call setupEditor() in constructor
// and call updateNotesPanel() from setupObserver() after currentSlide changes.

setupEditor() {
    const panel    = document.getElementById('notes-panel');
    const label    = document.getElementById('notes-panel-label');
    const textarea = document.getElementById('notes-textarea');
    const toggle   = document.getElementById('editToggle');
    const hotzone  = document.querySelector('.edit-hotzone');
    let hideTimeout = null;

    // Show toggle on hotzone hover (400ms grace period)
    hotzone.addEventListener('mouseenter', () => { clearTimeout(hideTimeout); toggle.classList.add('show'); });
    hotzone.addEventListener('mouseleave', () => { hideTimeout = setTimeout(() => { if (!this.editor.active) toggle.classList.remove('show'); }, 400); });
    toggle.addEventListener('mouseenter', () => clearTimeout(hideTimeout));
    toggle.addEventListener('mouseleave', () => { hideTimeout = setTimeout(() => { if (!this.editor.active) toggle.classList.remove('show'); }, 400); });
    hotzone.addEventListener('click', () => this.editor.toggle());
    toggle.addEventListener('click', () => this.editor.toggle());

    // Collapse/expand notes panel by clicking the header row
    document.getElementById('notes-panel-header').addEventListener('click', () => {
        panel.classList.toggle('collapsed');
    });

    // Textarea input → update data-notes in real time + broadcast to presenter
    textarea.addEventListener('input', () => {
        const slide = this.slides[this.currentSlide];
        if (slide) {
            slide.dataset.notes = textarea.value;
            this.broadcastState();
        }
    });

    // Ctrl+S / Cmd+S save
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            this.saveFile();
        }
    });

    this.editor = {
        active: false,
        toggle: () => this.editor.active ? this.editor.exit() : this.editor.enter(),
        enter: () => {
            this.editor.active = true;
            toggle.classList.add('active');
            toggle.textContent = '✓ Done';
            this.slides.forEach(s => {
                s.querySelectorAll('h1,h2,h3,p,li,span,td,th').forEach(el => {
                    el.setAttribute('contenteditable', 'true');
                    el.style.outline = 'none';
                });
            });
            panel.classList.add('active');
            this.updateNotesPanel();
        },
        exit: () => {
            this.editor.active = false;
            toggle.classList.remove('active');
            toggle.textContent = '✏ Edit';
            this.slides.forEach(s => {
                s.querySelectorAll('[contenteditable]').forEach(el => {
                    el.removeAttribute('contenteditable');
                    el.style.outline = '';
                });
            });
            panel.classList.remove('active');
        }
    };

    this._notesLabel    = label;
    this._notesTextarea = textarea;
}

updateNotesPanel() {
    if (!this.editor?.active) return;
    const slide = this.slides[this.currentSlide];
    this._notesLabel.textContent =
        `SPEAKER NOTES — SLIDE ${this.currentSlide + 1} / ${this.slides.length}`;
    this._notesTextarea.value = slide?.dataset.notes || '';
}

saveFile() {
    const html  = '<!DOCTYPE html>\n' + document.documentElement.outerHTML;
    const bytes = new TextEncoder().encode(html);
    fetch(location.pathname, {
        method: 'PUT', body: bytes,
        headers: { 'Content-Type': 'text/html' }
    }).catch(() => {
        // Fallback: download
        const a = Object.assign(document.createElement('a'), {
            href: URL.createObjectURL(new Blob([html], { type: 'text/html' })),
            download: location.pathname.split('/').pop() || 'presentation.html'
        });
        a.click(); URL.revokeObjectURL(a.href);
    });
}
```

**Integration checklist:**
- Add `this.setupEditor()` to `SlidePresentation` constructor
- Add `this.updateNotesPanel()` inside `setupObserver()` after `this.broadcastState()`
- Skip arrow-key navigation when textarea is focused: add `|| e.target.tagName === 'TEXTAREA'` to the keyboard guard in `setupKeyboard()`
