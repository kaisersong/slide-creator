# HTML Template & Code Patterns

Read this file when generating a presentation (Phase 3). It contains the full HTML architecture, required JavaScript patterns, animation recipes, and the edit button implementation.

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

    <!-- Fonts: use Fontshare (api.fontshare.com) or Google Fonts -->
    <link rel="stylesheet" href="https://api.fontshare.com/v2/css?f[]=clash-display@700,800&f[]=satoshi@400,500&display=swap">

    <style>
        /* ===========================================
           CSS CUSTOM PROPERTIES (THEME)
           Change these values to change the whole look.
           =========================================== */
        :root {
            --bg-primary: #0a0f1c;
            --bg-secondary: #111827;
            --text-primary: #ffffff;
            --text-secondary: #9ca3af;
            --accent: #00ffcc;

            /* Typography — always use clamp() for responsive scaling */
            --font-display: 'Clash Display', sans-serif;
            --font-body: 'Satoshi', sans-serif;
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
            scroll-behavior: smooth;
            scroll-snap-type: y mandatory;
            height: 100%;
        }

        body {
            font-family: var(--font-body);
            background: var(--bg-primary);
            color: var(--text-primary);
            overflow-x: hidden;
            height: 100%;
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
        }

        .slide-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            max-height: 100%;
            overflow: hidden;
        }

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

        /* Grid */
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 250px), 1fr)); gap: clamp(0.5rem, 1.5vw, 1rem); }

        /* ... style-specific CSS goes here ... */
    </style>
</head>
<body>
    <!-- Progress bar -->
    <div class="progress-bar" style="position:fixed;top:0;left:0;height:3px;background:var(--accent);width:0%;z-index:100;transition:width 0.3s ease;"></div>

    <!-- Navigation dots -->
    <nav class="nav-dots" aria-label="Slide navigation">
        <!-- Generated by JS -->
    </nav>

    <!-- Slides -->
    <section class="slide title-slide" aria-label="Title slide">
        <div class="slide-content">
            <h1 class="reveal">Presentation Title</h1>
            <p class="reveal">Subtitle or author</p>
        </div>
    </section>

    <section class="slide" aria-label="Slide 2">
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
           Handles navigation, animations, progress bar, and nav dots.
           Keyboard: arrows, space. Touch: swipe. Mouse: wheel.
           =========================================== */
        class SlidePresentation {
            constructor() {
                this.slides = document.querySelectorAll('.slide');
                this.currentSlide = 0;
                this.isScrolling = false;

                this.setupNavDots();
                this.setupObserver();
                this.setupKeyboard();
                this.setupTouch();
                this.setupWheel();
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
                        }
                    });
                }, { threshold: 0.5 });
                this.slides.forEach(s => observer.observe(s));
            }

            setupKeyboard() {
                document.addEventListener('keydown', (e) => {
                    if (e.target.getAttribute('contenteditable')) return;
                    if (e.key === 'ArrowDown' || e.key === 'ArrowRight' || e.key === ' ') {
                        e.preventDefault(); this.next();
                    } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
                        e.preventDefault(); this.prev();
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
                document.addEventListener('wheel', (e) => {
                    if (this.isScrolling) return;
                    this.isScrolling = true;
                    e.deltaY > 0 ? this.next() : this.prev();
                    setTimeout(() => { this.isScrolling = false; }, 800);
                }, { passive: true });
            }

            goTo(index) {
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

        new SlidePresentation();
    </script>
</body>
</html>
```

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

## Edit Button (Only When User Opted In)

The CSS-only hover approach (`hotzone:hover ~ .edit-toggle`) fails because `pointer-events: none` breaks the hover chain — the button disappears before the user can click it. Use JS with a grace period instead.

```html
<div class="edit-hotzone"></div>
<button class="edit-toggle" id="editToggle" title="Edit mode (E)">✏️</button>
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
.edit-toggle.show, .edit-toggle.active { opacity: 1; pointer-events: auto; }
```

```javascript
const hotzone = document.querySelector('.edit-hotzone');
const editToggle = document.getElementById('editToggle');
let hideTimeout = null;

// Show on hotzone hover with 400ms grace so user can move to button
hotzone.addEventListener('mouseenter', () => { clearTimeout(hideTimeout); editToggle.classList.add('show'); });
hotzone.addEventListener('mouseleave', () => { hideTimeout = setTimeout(() => { if (!editor.isActive) editToggle.classList.remove('show'); }, 400); });
editToggle.addEventListener('mouseenter', () => { clearTimeout(hideTimeout); });
editToggle.addEventListener('mouseleave', () => { hideTimeout = setTimeout(() => { if (!editor.isActive) editToggle.classList.remove('show'); }, 400); });

// Direct click on hotzone or button
hotzone.addEventListener('click', () => editor.toggleEditMode());
editToggle.addEventListener('click', () => editor.toggleEditMode());

// Keyboard: E key (skip when editing text)
document.addEventListener('keydown', (e) => {
    if ((e.key === 'e' || e.key === 'E') && !e.target.getAttribute('contenteditable')) {
        editor.toggleEditMode();
    }
});
```
