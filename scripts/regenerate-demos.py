#!/usr/bin/env python3
"""
Regenerate all 42 demo files using the new template + style references.

Each demo contains 8 slides about slide-creator features, styled according
to each preset's unique design tokens (colors, fonts, backgrounds, components).

Run: python3 scripts/regenerate-demos.py
"""

import os

DEMO_DIR = "demos"
os.makedirs(DEMO_DIR, exist_ok=True)

# ====================================================================
# SHARED CSS — PresentMode, Watermark, Edit Mode
# ====================================================================

PRESENT_MODE_CSS = """
/* ═══════════════════════════════════════════════
   Present Mode — F5 / ▶ to enter, ESC to exit
   ═══════════════════════════════════════════════ */
#present-btn {
  position: fixed; bottom: 1.5rem; right: 1.5rem; z-index: 9997;
  width: 44px; height: 44px; border-radius: 50%;
  background: rgba(0,0,0,0.50); color: rgba(255,255,255,0.80);
  border: 1.5px solid rgba(255,255,255,0.20);
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

body.presenting { background: #111 !important; overflow: hidden !important; }
body.presenting .slide {
  position: fixed !important; inset: 0;
  width: 1440px !important; height: 900px !important;
  transform-origin: top left;
  display: none !important; margin: 0; padding: 0;
}
body.presenting .slide.p-on { display: flex !important; }
body.presenting .slide.p-on .reveal { opacity: 1; transform: translateY(0); }
body.presenting #present-btn { display: none !important; }
body.presenting #present-counter { display: block; }
body.presenting .nav-dots,
body.presenting #slide-counter,
body.presenting .orb,
body.presenting #notes-panel,
body.presenting .edit-hotzone,
body.presenting .edit-toggle,
body.presenting .keyboard-hint { display: none !important; }

body.presenting.presenting-black { background: #000 !important; }
body.presenting.presenting-black .slide { display: none !important; }
"""

WATERMARK_CSS = """
.slide-credit {
  position: absolute; bottom: 8px; right: 14px;
  font-size: 9px; color: var(--text-secondary, #999);
  opacity: 0.35; pointer-events: none; z-index: 1;
  font-family: system-ui, sans-serif;
}
body.presenting .slide-credit { display: none; }
"""

EDIT_MODE_CSS = """
.edit-hotzone {
  position: fixed; top: 0; left: 0; width: 30px; height: 30px;
  z-index: 9998; cursor: pointer;
}
.edit-toggle {
  position: fixed; top: 12px; left: 12px; z-index: 9999;
  padding: 6px 12px; border-radius: 8px; border: none;
  background: rgba(0,0,0,0.50); color: rgba(255,255,255,0.70);
  font-size: 0.75rem; cursor: pointer;
  backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
  opacity: 0; transition: opacity 0.3s; pointer-events: none;
}
body:hover .edit-toggle { opacity: 1; pointer-events: auto; }
body.editing .edit-toggle { opacity: 1; background: rgba(16,185,129,0.80); color: #fff; }

#notes-panel {
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 9996;
  background: rgba(0,0,0,0.85); backdrop-filter: blur(12px);
  color: #fff; transform: translateY(100%); transition: transform 0.3s ease;
  max-height: 40vh; display: flex; flex-direction: column;
}
#notes-panel.active { transform: translateY(0); }
#notes-panel-header {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 16px; border-bottom: 1px solid rgba(255,255,255,0.10);
}
#notes-panel-label { font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase; color: rgba(255,255,255,0.50); }
#notes-body { flex: 1; padding: 8px; }
#notes-textarea {
  width: 100%; height: 100%; border: none; background: transparent;
  color: rgba(255,255,255,0.75); font-size: 0.88rem; line-height: 1.65;
  font-family: system-ui, sans-serif; resize: none; outline: none;
}
"""

# ====================================================================
# SHARED JS — SlidePresentation, PresentMode, Presenter, Watermark
# ====================================================================

SLIDE_JS = """
class SlidePresentation {
  constructor() {
    this.slides = document.querySelectorAll('.slide');
    this.currentSlide = 0;
    this.channel = new BroadcastChannel('slide-creator-presenter');
    // CRITICAL: Make first slide visible immediately
    this.slides[0]?.classList.add('visible');
    this.slides[0]?.querySelectorAll('.reveal').forEach(function(r) { r.classList.add('visible'); });
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
          this.updateNotesPanel();
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
  setupWheel() {}
  setupPresenter() {
    this.channel.addEventListener('message', e => {
      if (e.data.type === 'nav-next') this.next();
      else if (e.data.type === 'nav-prev') this.prev();
      else if (e.data.type === 'request-state') this.broadcastState();
    });
  }
  broadcastState() {
    const slide = this.slides[this.currentSlide];
    this.channel.postMessage({
      type: 'state', index: this.currentSlide,
      total: this.slides.length, notes: slide?.dataset.notes || ''
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
  updateNotesPanel() {
    const label = document.getElementById('notes-panel-label');
    const textarea = document.getElementById('notes-textarea');
    if (label) label.textContent = `SPEAKER NOTES — SLIDE ${this.currentSlide + 1} / ${this.slides.length}`;
    if (textarea) textarea.value = this.slides[this.currentSlide]?.dataset.notes || '';
  }
  setupEditor() {
    const panel = document.getElementById('notes-panel');
    const textarea = document.getElementById('notes-textarea');
    const toggle = document.getElementById('editToggle');
    const hotzone = document.querySelector('.edit-hotzone');
    const header = document.getElementById('notes-panel-header');
    const collapseBtn = document.getElementById('notes-collapse-btn');
    let hideTimeout = null;
    this.editor = { active: false };
    hotzone.addEventListener('mouseenter', () => { clearTimeout(hideTimeout); toggle.classList.add('show'); });
    hotzone.addEventListener('mouseleave', () => { hideTimeout = setTimeout(() => { if (!this.editor.active) toggle.classList.remove('show'); }, 400); });
    toggle.addEventListener('mouseenter', () => clearTimeout(hideTimeout));
    toggle.addEventListener('mouseleave', () => { hideTimeout = setTimeout(() => { if (!this.editor.active) toggle.classList.remove('show'); }, 400); });
    toggle.addEventListener('click', (e) => {
      e.stopPropagation();
      this.editor.active = !this.editor.active;
      document.body.classList.toggle('editing', this.editor.active);
      toggle.classList.toggle('active', this.editor.active);
      toggle.textContent = this.editor.active ? '✓ Done' : '✏ Edit';
      if (this.editor.active) {
        panel.classList.add('active');
        textarea.value = this.slides[this.currentSlide]?.dataset.notes || '';
        textarea.focus();
      } else {
        panel.classList.remove('active');
      }
    });
    header.addEventListener('click', (e) => {
      if (e.target === collapseBtn) { panel.classList.toggle('collapsed'); return; }
    });
    textarea.addEventListener('input', () => {
      const slide = this.slides[this.currentSlide];
      if (slide) slide.dataset.notes = textarea.value;
      this.channel.postMessage({ type: 'state', index: this.currentSlide, total: this.slides.length, notes: textarea.value });
    });
  }
}
"""

PRESENT_MODE_JS = """
class PresentMode {
  constructor(ctrl) {
    this.ctrl = ctrl; this.DW = 1440; this.DH = 900; this.active = false;
    this._resize = () => this._scale();
    const btn = document.createElement('button');
    btn.id = 'present-btn'; btn.title = 'Present (F5)';
    btn.setAttribute('aria-label', 'Present'); btn.textContent = '\\u25b6';
    document.body.appendChild(btn);
    const counter = document.createElement('div');
    counter.id = 'present-counter'; document.body.appendChild(counter);
    btn.addEventListener('click', () => this.enter());
    document.addEventListener('keydown', e => {
      if (e.key === 'F5') { e.preventDefault(); this.enter(); }
      if (e.key === 'Escape' && this.active) this.exit();
      if ((e.key === 'b' || e.key === 'B') && this.active) document.body.classList.toggle('presenting-black');
    });
    document.addEventListener('fullscreenchange', () => { if (!document.fullscreenElement && this.active) this.exit(); });
  }
  enter() {
    if (this.active) return; this.active = true;
    document.body.classList.add('presenting');
    document.documentElement.requestFullscreen?.().catch(() => {});
    window.addEventListener('resize', this._resize); this._scale(); this._show(this.ctrl.currentSlide);
    this._origGoTo = this.ctrl.goTo.bind(this.ctrl);
    this.ctrl.goTo = (i) => {
      const idx = Math.max(0, Math.min(i, this.ctrl.slides.length - 1));
      this.ctrl.currentSlide = idx;
      this.ctrl.slides.forEach((s, j) => s.classList.toggle('visible', j === idx));
      this._show(idx); this.ctrl.updateProgress?.(); this.ctrl.updateDots?.(); this.ctrl.broadcastState?.();
    };
  }
  exit() {
    if (!this.active) return; this.active = false;
    document.body.classList.remove('presenting', 'presenting-black');
    document.exitFullscreen?.().catch(() => {});
    window.removeEventListener('resize', this._resize);
    this.ctrl.goTo = this._origGoTo;
    this.ctrl.goTo(this.ctrl.currentSlide);
    setTimeout(() => this.ctrl.slides[this.ctrl.currentSlide]?.scrollIntoView(), 50);
  }
  _scale() {
    const sw = window.innerWidth / this.DW, sh = window.innerHeight / this.DH, s = Math.min(sw, sh);
    document.querySelectorAll('body.presenting .slide').forEach(sl => {
      sl.style.transform = `translate(-50%, -50%) scale(${s})`;
    });
  }
  _show(n) {
    this.ctrl.slides.forEach((sl, i) => {
      sl.classList.toggle('p-on', i === n);
      sl.querySelectorAll('.reveal').forEach(r => {
        r.classList.toggle('visible', i === n);
      });
    });
    const counter = document.getElementById('present-counter');
    if (counter) counter.textContent = `${n + 1} / ${this.ctrl.slides.length}`;
  }
}
"""

PRESENTER_MODE_JS = """
if (new URLSearchParams(location.search).has('presenter')) {
  document.title = 'Presenter — ' + document.title;
  document.body.innerHTML = `
  <style>
  body { margin: 0; background: #111; color: #fff; font-family: system-ui, sans-serif; }
  #pv { display: flex; height: 100vh; }
  .pv-panel { background: #1a1a1a; border-right: 1px solid #333; padding: 12px; }
  #pv-right { flex: 1; display: flex; flex-direction: column; }
  #pv-nav { display: flex; align-items: center; gap: 12px; }
  .pv-arrow { background: #333; color: #fff; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; }
  #pv-counter { display: flex; align-items: baseline; gap: 4px; }
  #pv-num { font-size: 1.5rem; font-weight: 700; }
  #pv-of { font-size: 0.875rem; color: #888; }
  #pv-timer-label { font-size: 0.7rem; color: #888; text-transform: uppercase; letter-spacing: 0.1em; }
  #pv-timer { font-size: 2rem; font-weight: 700; font-family: monospace; }
  #pv-notes { white-space: pre-wrap; font-size: 0.875rem; line-height: 1.6; color: #ccc; margin-top: 8px; }
  #pv-label { font-weight: 600; font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 0.1em; }
  #pv-timer-box { margin-top: auto; padding: 12px !important; }
  </style>
  <div id="pv">
    <div class="pv-panel"><div id="pv-label">Speaker Notes</div><div id="pv-notes">Waiting for main window...</div></div>
    <div id="pv-right">
      <div class="pv-panel"><div id="pv-nav"><button class="pv-arrow" id="pv-prev">←</button><div id="pv-counter"><div id="pv-num">—</div><div id="pv-of">/ —</div></div><button class="pv-arrow" id="pv-next">→</button></div></div>
      <div class="pv-panel" id="pv-timer-box"><div id="pv-timer-label">Elapsed</div><div id="pv-timer">0:00</div></div>
    </div>
  </div>`;
  const ch = new BroadcastChannel('slide-creator-presenter');
  let startTime = null;
  const pv = document.getElementById('pv');
  let lastH = 0, roTimer = null;
  new ResizeObserver(() => { clearTimeout(roTimer); roTimer = setTimeout(() => { const h = Math.ceil(pv.getBoundingClientRect().height); if (h === lastH) return; lastH = h; const chrome = window.outerHeight - window.innerHeight; window.resizeTo(window.outerWidth, Math.max(260, h + chrome + 4)); }, 40); }).observe(pv);
  ch.addEventListener('message', e => { if (e.data.type !== 'state') return; if (!startTime) startTime = Date.now(); document.getElementById('pv-notes').textContent = e.data.notes || '(no notes for this slide)'; document.getElementById('pv-num').textContent = e.data.index + 1; document.getElementById('pv-of').textContent = `/ ${e.data.total}`; });
  ch.postMessage({ type: 'request-state' });
  setInterval(() => { if (!startTime) return; const s = Math.floor((Date.now() - startTime) / 1000); document.getElementById('pv-timer').textContent = `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`; }, 1000);
  document.getElementById('pv-prev').addEventListener('click', () => ch.postMessage({ type: 'nav-prev' }));
  document.getElementById('pv-next').addEventListener('click', () => ch.postMessage({ type: 'nav-next' }));
  document.addEventListener('keydown', e => {
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ' || e.key === 'PageDown' || e.key === 'Enter') ch.postMessage({ type: 'nav-next' });
    else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp' || e.key === 'PageUp' || e.key === 'Backspace') ch.postMessage({ type: 'nav-prev' });
  });
} else {
"""

WATERMARK_JS = """
(function() {
  var slides = document.querySelectorAll('.slide');
  if (!slides.length) return;
  var last = slides[slides.length - 1];
  var credit = document.createElement('div');
  credit.className = 'slide-credit';
  credit.textContent = 'By kai-slide-creator v2.15.0 · {preset}';
  last.appendChild(credit);
})();
"""

# ====================================================================
# PRESET CONFIGURATIONS — Colors, fonts, backgrounds, signature elements
# ====================================================================

PRESETS = {
    "aurora-mesh": {
        "display": "Aurora Mesh",
        "bg": "#0a0a1a",
        "accent": "#00f5c4",
        "text_primary": "#ffffff",
        "text_body": "rgba(255,255,255,0.70)",
        "text_secondary": "rgba(255,255,255,0.45)",
        "text_muted": "rgba(255,255,255,0.35)",
        "card_bg": "rgba(255,255,255,0.05)",
        "card_border": "rgba(255,255,255,0.10)",
        "divider": "rgba(255,255,255,0.15)",
        "font_display": "'Space Grotesk', system-ui, sans-serif",
        "font_body": "'DM Sans', system-ui, sans-serif",
        "google_fonts": "Space+Grotesk:wght@700&family=DM+Sans:wght@400;500;600;700",
        "background": """body {
    background-color: #0a0a1a;
    background-image:
        radial-gradient(ellipse at 20% 50%, rgba(120,40,200,0.40) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(0,180,255,0.30) 0%, transparent 50%),
        radial-gradient(ellipse at 60% 80%, rgba(0,255,180,0.20) 0%, transparent 50%);
    animation: auroraDrift 20s ease-in-out infinite alternate;
}
@keyframes auroraDrift {
    0% { background-position: 0% 50%; }
    33% { background-position: 50% 20%; }
    66% { background-position: 80% 80%; }
    100% { background-position: 100% 50%; }
}""",
        "accent_text": "#00f5c4",
        "pill_bg": "rgba(0,245,196,0.12)",
        "pill_border": "rgba(0,245,196,0.30)",
        "signature": "Animated aurora gradient background, glass cards with backdrop-filter",
    },
    "blue-sky": {
        "display": "Blue Sky",
        "bg_from": "#f0f9ff",
        "bg_to": "#e0f2fe",
        "accent": "#2563eb",
        "text_primary": "#0f172a",
        "text_body": "#334155",
        "text_secondary": "#64748b",
        "text_muted": "#94a3b8",
        "card_bg": "rgba(255,255,255,0.70)",
        "card_border": "rgba(255,255,255,0.90)",
        "divider": "rgba(37,99,235,0.20)",
        "font_display": "'DM Sans', 'Inter', system-ui, sans-serif",
        "font_body": "'DM Sans', 'Inter', system-ui, sans-serif",
        "google_fonts": "DM+Sans:wght@400;500;600;700;800",
        "background": """body {
    background: linear-gradient(160deg, #f0f9ff, #e0f2fe);
}
/* Noise overlay */
body::before {
    content: ''; position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
}
/* Grid */
body::after {
    content: ''; position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background-image:
        linear-gradient(rgba(14,165,233,0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(14,165,233,0.06) 1px, transparent 1px);
    background-size: 40px 40px;
    -webkit-mask-image: radial-gradient(ellipse 70% 70% at 50% 50%, black 40%, transparent 100%);
    mask-image: radial-gradient(ellipse 70% 70% at 50% 50%, black 40%, transparent 100%);
}
/* Animated orbs */
.orb {
    position: fixed; border-radius: 50%; pointer-events: none; z-index: 0;
    filter: blur(80px);
    transition: top 1.2s cubic-bezier(0.22,1,0.36,1), left 1.2s cubic-bezier(0.22,1,0.36,1);
}
#orb1 { background: rgba(96,165,250,0.35); }
#orb2 { background: rgba(99,102,241,0.25); }
#orb3 { background: rgba(14,165,233,0.30); }""",
        "accent_text": "#2563eb",
        "pill_bg": "rgba(37,99,235,0.10)",
        "pill_border": "rgba(37,99,235,0.20)",
        "signature": "Light gradient background, glassmorphism cards, animated orbs, noise overlay, grid pattern",
    },
    "bold-signal": {
        "display": "Bold Signal",
        "bg": "#0f172a",
        "accent": "#3b82f6",
        "text_primary": "#f8fafc",
        "text_body": "rgba(248,250,252,0.70)",
        "text_secondary": "rgba(248,250,252,0.50)",
        "text_muted": "rgba(248,250,252,0.35)",
        "card_bg": "rgba(255,255,255,0.05)",
        "card_border": "rgba(255,255,255,0.10)",
        "divider": "rgba(255,255,255,0.12)",
        "font_display": "'Inter', system-ui, sans-serif",
        "font_body": "'Inter', system-ui, sans-serif",
        "google_fonts": "Inter:wght@400;500;600;700;800",
        "background": """body {
    background: #0f172a;
    background-image:
        radial-gradient(circle at 20% 80%, rgba(59,130,246,0.15) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(139,92,246,0.10) 0%, transparent 50%);
}""",
        "accent_text": "#3b82f6",
        "pill_bg": "rgba(59,130,246,0.15)",
        "pill_border": "rgba(59,130,246,0.30)",
        "signature": "Dark navy background, subtle gradient orbs, Inter font, bold typography",
    },
    "chinese-chan": {
        "display": "Chinese Chan",
        "bg": "#faf8f5",
        "accent": "#c45d3e",
        "text_primary": "#2d2a26",
        "text_body": "rgba(45,42,38,0.70)",
        "text_secondary": "rgba(45,42,38,0.55)",
        "text_muted": "rgba(45,42,38,0.40)",
        "card_bg": "rgba(196,93,62,0.06)",
        "card_border": "rgba(196,93,62,0.15)",
        "divider": "rgba(196,93,62,0.20)",
        "font_display": "'Noto Serif SC', 'Source Han Serif', serif",
        "font_body": "'Noto Sans SC', 'Source Han Sans', system-ui, sans-serif",
        "google_fonts": "Noto+Serif+SC:wght@700&family=Noto+Sans+SC:wght@400;500;600",
        "background": """body {
    background: #faf8f5;
    background-image:
        radial-gradient(circle at 30% 70%, rgba(196,93,62,0.06) 0%, transparent 50%),
        radial-gradient(circle at 70% 30%, rgba(45,42,38,0.03) 0%, transparent 50%);
}
body::before {
    content: '';
    position: fixed;
    inset: 0;
    background: radial-gradient(ellipse at 30% 20%, rgba(26,26,24,0.03) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}""",
        "accent_text": "#c45d3e",
        "pill_bg": "rgba(196,93,62,0.10)",
        "pill_border": "rgba(196,93,62,0.25)",
        "signature": "Warm cream background, serif display font, terracotta accent, zen minimal aesthetic",
    },
    "creative-voltage": {
        "display": "Creative Voltage",
        "bg": "#0a0a0a",
        "accent": "#ff5722",
        "text_primary": "#ffffff",
        "text_body": "rgba(255,255,255,0.70)",
        "text_secondary": "rgba(255,255,255,0.50)",
        "text_muted": "rgba(255,255,255,0.35)",
        "card_bg": "rgba(255,87,34,0.08)",
        "card_border": "rgba(255,87,34,0.20)",
        "divider": "rgba(255,87,34,0.25)",
        "font_display": "'Bebas Neue', 'Arial Black', sans-serif",
        "font_body": "'Roboto', system-ui, sans-serif",
        "google_fonts": "Bebas+Neue&family=Roboto:wght@400;500;700",
        "background": """body {
    background: #0a0a0a;
    background-image:
        radial-gradient(circle at 50% 50%, rgba(255,87,34,0.12) 0%, transparent 60%),
        repeating-linear-gradient(0deg, rgba(255,87,34,0.03) 0px, rgba(255,87,34,0.03) 1px, transparent 1px, transparent 4px),
        repeating-linear-gradient(90deg, rgba(255,87,34,0.03) 0px, rgba(255,87,34,0.03) 1px, transparent 1px, transparent 4px);
}""",
        "accent_text": "#ff5722",
        "pill_bg": "rgba(255,87,34,0.15)",
        "pill_border": "rgba(255,87,34,0.35)",
        "signature": "Dark background, neon orange accent, halftone dot pattern, Bebas Neue display font",
    },
    "dark-botanical": {
        "display": "Dark Botanical",
        "bg": "#1a1a2e",
        "accent": "#4ade80",
        "text_primary": "#f0fdf4",
        "text_body": "rgba(240,253,244,0.70)",
        "text_secondary": "rgba(240,253,244,0.50)",
        "text_muted": "rgba(240,253,244,0.35)",
        "card_bg": "rgba(74,222,128,0.06)",
        "card_border": "rgba(74,222,128,0.15)",
        "divider": "rgba(74,222,128,0.20)",
        "font_display": "'Playfair Display', Georgia, serif",
        "font_body": "'Inter', system-ui, sans-serif",
        "google_fonts": "Playfair+Display:wght@700&family=Inter:wght@400;500;600",
        "background": """body {
    background: #1a1a2e;
    background-image:
        radial-gradient(ellipse at 30% 20%, rgba(74,222,128,0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 70% 80%, rgba(34,197,94,0.06) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(16,185,129,0.04) 0%, transparent 70%);
}""",
        "accent_text": "#4ade80",
        "pill_bg": "rgba(74,222,128,0.12)",
        "pill_border": "rgba(74,222,128,0.25)",
        "signature": "Deep dark blue-green background, soft green gradient orbs, Playfair Display serif",
    },
    "data-story": {
        "display": "Data Story",
        "bg": "#0f172a",
        "accent": "#38bdf8",
        "text_primary": "#f1f5f9",
        "text_body": "rgba(241,245,249,0.70)",
        "text_secondary": "rgba(241,245,249,0.50)",
        "text_muted": "rgba(241,245,249,0.35)",
        "card_bg": "rgba(56,189,248,0.06)",
        "card_border": "rgba(56,189,248,0.15)",
        "divider": "rgba(56,189,248,0.20)",
        "font_display": "'JetBrains Mono', 'Fira Code', monospace",
        "font_body": "'Inter', system-ui, sans-serif",
        "google_fonts": "JetBrains+Mono:wght@700&family=Inter:wght@400;500;600;700",
        "background": """body {
    background: #0f172a;
    background-image:
        linear-gradient(rgba(56,189,248,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(56,189,248,0.04) 1px, transparent 1px);
    background-size: 32px 32px;
}""",
        "accent_text": "#38bdf8",
        "pill_bg": "rgba(56,189,248,0.12)",
        "pill_border": "rgba(56,189,248,0.25)",
        "signature": "Dark slate background, subtle grid pattern, JetBrains Mono display, sky blue accent, KPI cards",
    },
    "electric-studio": {
        "display": "Electric Studio",
        "bg": "#18181b",
        "accent": "#a855f7",
        "text_primary": "#fafafa",
        "text_body": "rgba(250,250,250,0.70)",
        "text_secondary": "rgba(250,250,250,0.50)",
        "text_muted": "rgba(250,250,250,0.35)",
        "card_bg": "rgba(168,85,247,0.08)",
        "card_border": "rgba(168,85,247,0.20)",
        "divider": "rgba(168,85,247,0.25)",
        "font_display": "'Manrope', system-ui, sans-serif",
        "font_body": "'Manrope', system-ui, sans-serif",
        "google_fonts": "Manrope:wght@400;500;600;700;800",
        "background": """body {
    background: #18181b;
    background-image:
        radial-gradient(circle at 20% 50%, rgba(168,85,247,0.12) 0%, transparent 50%),
        radial-gradient(circle at 80% 50%, rgba(236,72,153,0.08) 0%, transparent 50%);
}""",
        "accent_text": "#a855f7",
        "pill_bg": "rgba(168,85,247,0.15)",
        "pill_border": "rgba(168,85,247,0.30)",
        "signature": "Dark zinc background, purple/pink dual-tone orbs, Manrope font, bold color blocks",
    },
    "enterprise-dark": {
        "display": "Enterprise Dark",
        "bg": "#111317",
        "accent": "#0ea5e9",
        "text_primary": "#e5e7eb",
        "text_body": "rgba(229,231,235,0.70)",
        "text_secondary": "rgba(229,231,235,0.50)",
        "text_muted": "rgba(229,231,235,0.35)",
        "card_bg": "rgba(255,255,255,0.04)",
        "card_border": "rgba(255,255,255,0.08)",
        "divider": "rgba(255,255,255,0.10)",
        "font_display": "'Plus Jakarta Sans', system-ui, sans-serif",
        "font_body": "'Plus Jakarta Sans', system-ui, sans-serif",
        "google_fonts": "Plus+Jakarta+Sans:wght@400;500;600;700;800",
        "background": """body {
    background: #111317;
    background-image:
        radial-gradient(ellipse at 0% 0%, rgba(14,165,233,0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 100% 100%, rgba(99,102,241,0.06) 0%, transparent 50%);
}
body::before {
    content: '';
    position: fixed; inset: 0;
    background-image:
        linear-gradient(rgba(48,54,61,0.5) 1px, transparent 1px),
        linear-gradient(90deg, rgba(48,54,61,0.5) 1px, transparent 1px);
    background-size: 24px 24px;
    opacity: 0.03;
    pointer-events: none;
    z-index: 0;
}""",
        "accent_text": "#0ea5e9",
        "pill_bg": "rgba(14,165,233,0.12)",
        "pill_border": "rgba(14,165,233,0.25)",
        "signature": "Near-black background, subtle blue/indigo gradient corners, Plus Jakarta Sans, enterprise-clean aesthetic",
    },
    "glassmorphism": {
        "display": "Glassmorphism",
        "bg": "#1e1b4b",
        "accent": "#818cf8",
        "text_primary": "#e0e7ff",
        "text_body": "rgba(224,231,255,0.70)",
        "text_secondary": "rgba(224,231,255,0.50)",
        "text_muted": "rgba(224,231,255,0.35)",
        "card_bg": "rgba(255,255,255,0.08)",
        "card_border": "rgba(255,255,255,0.15)",
        "divider": "rgba(129,140,248,0.20)",
        "font_display": "'Outfit', system-ui, sans-serif",
        "font_body": "'Inter', system-ui, sans-serif",
        "google_fonts": "Outfit:wght@700;800&family=Inter:wght@400;500;600",
        "background": """body {
    background: #1e1b4b;
    background-image:
        radial-gradient(circle at 20% 30%, rgba(129,140,248,0.20) 0%, transparent 50%),
        radial-gradient(circle at 80% 70%, rgba(192,132,252,0.15) 0%, transparent 50%),
        radial-gradient(circle at 50% 50%, rgba(99,102,241,0.10) 0%, transparent 70%);
}
.glass-card {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 20px;
}""",
        "accent_text": "#818cf8",
        "pill_bg": "rgba(129,140,248,0.15)",
        "pill_border": "rgba(129,140,248,0.30)",
        "signature": "Deep indigo background, floating gradient orbs, glass cards with backdrop-filter blur",
    },
    "modern-newspaper": {
        "display": "Modern Newspaper",
        "bg": "#fafaf9",
        "accent": "#1c1917",
        "text_primary": "#1c1917",
        "text_body": "rgba(28,25,23,0.70)",
        "text_secondary": "rgba(28,25,23,0.55)",
        "text_muted": "rgba(28,25,23,0.40)",
        "card_bg": "rgba(28,25,23,0.04)",
        "card_border": "rgba(28,25,23,0.12)",
        "divider": "rgba(28,25,23,0.15)",
        "font_display": "'Playfair Display', Georgia, serif",
        "font_body": "'Source Sans 3', 'Source Sans Pro', system-ui, sans-serif",
        "google_fonts": "Playfair+Display:wght@700&family=Source+Sans+3:wght@400;500;600;700",
        "background": """body {
    background: #fafaf9;
    border-top: 4px solid #1c1917;
}
body::before {
    content: ''; position: fixed; top: 0; left: 0; right: 0; height: 4px;
    background: linear-gradient(90deg, #1c1917 0%, #44403c 50%, #1c1917 100%);
    z-index: 9999;
}""",
        "accent_text": "#1c1917",
        "pill_bg": "rgba(28,25,23,0.08)",
        "pill_border": "rgba(28,25,23,0.15)",
        "signature": "Warm off-white background, Playfair Display serif, 12-column grid, editorial newspaper aesthetic",
    },
    "neo-brutalism": {
        "display": "Neo Brutalism",
        "bg": "#fffef2",
        "accent": "#000000",
        "text_primary": "#1a1a1a",
        "text_body": "rgba(26,26,26,0.70)",
        "text_secondary": "rgba(26,26,26,0.55)",
        "text_muted": "rgba(26,26,26,0.40)",
        "card_bg": "#fffef2",
        "card_border": "#000000",
        "divider": "#000000",
        "font_display": "'Space Mono', monospace",
        "font_body": "'Space Mono', monospace",
        "google_fonts": "Space+Mono:wght@400;700",
        "background": """body {
    background: #fffef2;
    background-image:
        radial-gradient(circle, rgba(0,0,0,0.06) 1px, transparent 1px);
    background-size: 24px 24px;
}
.neo-card {
    background: #fffef2;
    border: 3px solid #000;
    box-shadow: 4px 4px 0 #000;
    border-radius: 0;
}""",
        "accent_text": "#000000",
        "pill_bg": "#fffef2",
        "pill_border": "#000000",
        "signature": "Cream background, dot grid pattern, bold black borders, 3px solid boxes with hard shadows, Space Mono",
    },
    "neo-retro-dev": {
        "display": "Neo Retro Dev",
        "bg": "#fdf6e3",
        "accent": "#268bd2",
        "text_primary": "#586e75",
        "text_body": "rgba(88,110,117,0.70)",
        "text_secondary": "rgba(88,110,117,0.55)",
        "text_muted": "rgba(88,110,117,0.40)",
        "card_bg": "#eee8d5",
        "card_border": "#93a1a1",
        "divider": "#93a1a1",
        "font_display": "'IBM Plex Mono', 'Fira Code', monospace",
        "font_body": "'IBM Plex Mono', 'Fira Code', monospace",
        "google_fonts": "IBM+Plex+Mono:wght@400;500;600;700",
        "background": """body {
    background: #fdf6e3;
    background-image:
        linear-gradient(rgba(147,161,161,0.10) 1px, transparent 1px),
        linear-gradient(90deg, rgba(147,161,161,0.10) 1px, transparent 1px);
    background-size: 20px 20px;
}""",
        "accent_text": "#268bd2",
        "pill_bg": "rgba(38,139,210,0.10)",
        "pill_border": "rgba(38,139,210,0.25)",
        "signature": "Solarized light background, graph paper grid, IBM Plex Mono, retro terminal aesthetic",
    },
    "neon-cyber": {
        "display": "Neon Cyber",
        "bg": "#0a0a0f",
        "accent": "#ff00ff",
        "text_primary": "#ffffff",
        "text_body": "rgba(255,255,255,0.70)",
        "text_secondary": "rgba(255,255,255,0.50)",
        "text_muted": "rgba(255,255,255,0.35)",
        "card_bg": "rgba(255,0,255,0.06)",
        "card_border": "rgba(255,0,255,0.20)",
        "divider": "rgba(255,0,255,0.25)",
        "font_display": "'Orbitron', system-ui, sans-serif",
        "font_body": "'Rajdhani', system-ui, sans-serif",
        "google_fonts": "Orbitron:wght@700&family=Rajdhani:wght@400;500;600;700",
        "background": """body {
    background: #0a0a0f;
    background-image:
        linear-gradient(rgba(255,0,255,0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,0,255,0.05) 1px, transparent 1px),
        radial-gradient(circle at 50% 50%, rgba(255,0,255,0.08) 0%, transparent 60%);
    background-size: 40px 40px, 40px 40px, 100% 100%;
}""",
        "accent_text": "#ff00ff",
        "pill_bg": "rgba(255,0,255,0.12)",
        "pill_border": "rgba(255,0,255,0.30)",
        "signature": "Near-black background, magenta grid overlay, Orbitron display font, cyberpunk neon glow",
    },
    "notebook-tabs": {
        "display": "Notebook Tabs",
        "bg": "#f5f0e8",
        "accent": "#d97706",
        "text_primary": "#451a03",
        "text_body": "rgba(69,26,3,0.70)",
        "text_secondary": "rgba(69,26,3,0.55)",
        "text_muted": "rgba(69,26,3,0.40)",
        "card_bg": "rgba(217,119,6,0.06)",
        "card_border": "rgba(217,119,6,0.15)",
        "divider": "rgba(217,119,6,0.20)",
        "font_display": "'Caveat', cursive",
        "font_body": "'Lora', Georgia, serif",
        "google_fonts": "Caveat:wght@700&family=Lora:wght@400;500;600",
        "background": """body {
    background: #f5f0e8;
    background-image:
        linear-gradient(rgba(217,119,6,0.10) 1px, transparent 1px);
    background-size: 100% 32px;
}
body::before {
    content: ''; position: fixed; left: 80px; top: 0; bottom: 0; width: 2px;
    background: rgba(217,119,6,0.15);
}""",
        "accent_text": "#d97706",
        "pill_bg": "rgba(217,119,6,0.10)",
        "pill_border": "rgba(217,119,6,0.25)",
        "signature": "Warm kraft paper background, horizontal ruled lines, left margin line, Caveat handwritten font",
    },
    "paper-ink": {
        "display": "Paper & Ink",
        "bg": "#fefdf8",
        "accent": "#1c1917",
        "text_primary": "#1c1917",
        "text_body": "rgba(28,25,23,0.70)",
        "text_secondary": "rgba(28,25,23,0.55)",
        "text_muted": "rgba(28,25,23,0.40)",
        "card_bg": "rgba(28,25,23,0.03)",
        "card_border": "rgba(28,25,23,0.10)",
        "divider": "rgba(28,25,23,0.12)",
        "font_display": "'Crimson Pro', Georgia, serif",
        "font_body": "'Crimson Pro', Georgia, serif",
        "google_fonts": "Crimson+Pro:wght@400;500;600;700;800",
        "background": """body {
    background: #fefdf8;
}""",
        "accent_text": "#1c1917",
        "pill_bg": "rgba(28,25,23,0.06)",
        "pill_border": "rgba(28,25,23,0.12)",
        "signature": "Warm white paper background, Crimson Pro serif throughout, narrow column, editorial print style",
    },
    "pastel-geometry": {
        "display": "Pastel Geometry",
        "bg": "#ffffff",
        "accent": "#6366f1",
        "text_primary": "#1e1b4b",
        "text_body": "rgba(30,27,75,0.70)",
        "text_secondary": "rgba(30,27,75,0.50)",
        "text_muted": "rgba(30,27,75,0.35)",
        "card_bg": "#ffffff",
        "card_border": "rgba(99,102,241,0.15)",
        "divider": "rgba(99,102,241,0.20)",
        "font_display": "'DM Sans', system-ui, sans-serif",
        "font_body": "'DM Sans', system-ui, sans-serif",
        "google_fonts": "DM+Sans:wght@400;500;600;700",
        "background": """body {
    background: #ffffff;
    background-image:
        radial-gradient(circle at 20% 20%, rgba(244,114,182,0.15) 0%, transparent 40%),
        radial-gradient(circle at 80% 80%, rgba(129,140,248,0.15) 0%, transparent 40%);
}""",
        "accent_text": "#6366f1",
        "pill_bg": "rgba(99,102,241,0.10)",
        "pill_border": "rgba(99,102,241,0.25)",
        "signature": "White card on pastel gradient background, pink/indigo orbs, DM Sans, geometric shapes",
    },
    "split-pastel": {
        "display": "Split Pastel",
        "bg": "#fef3c7",
        "accent": "#059669",
        "text_primary": "#064e3b",
        "text_body": "rgba(6,78,59,0.70)",
        "text_secondary": "rgba(6,78,59,0.50)",
        "text_muted": "rgba(6,78,59,0.35)",
        "card_bg": "rgba(255,255,255,0.60)",
        "card_border": "rgba(5,150,105,0.15)",
        "divider": "rgba(5,150,105,0.20)",
        "font_display": "'Nunito', system-ui, sans-serif",
        "font_body": "'Nunito', system-ui, sans-serif",
        "google_fonts": "Nunito:wght@400;500;600;700;800",
        "background": """body {
    background: linear-gradient(135deg, #fef3c7 50%, #d1fae5 50%);
}""",
        "accent_text": "#059669",
        "pill_bg": "rgba(5,150,105,0.10)",
        "pill_border": "rgba(5,150,105,0.25)",
        "signature": "Split diagonal background — warm amber / cool mint, Nunito rounded sans-serif",
    },
    "swiss-modern": {
        "display": "Swiss Modern",
        "bg": "#ffffff",
        "accent": "#dc2626",
        "text_primary": "#111827",
        "text_body": "rgba(17,24,39,0.70)",
        "text_secondary": "rgba(17,24,39,0.50)",
        "text_muted": "rgba(17,24,39,0.35)",
        "card_bg": "rgba(17,24,39,0.03)",
        "card_border": "rgba(17,24,39,0.10)",
        "divider": "rgba(17,24,39,0.12)",
        "font_display": "'Inter', system-ui, sans-serif",
        "font_body": "'Inter', system-ui, sans-serif",
        "google_fonts": "Inter:wght@400;500;600;700;800",
        "background": """body {
    background: #ffffff;
    border-left: 8px solid #dc2626;
}""",
        "accent_text": "#dc2626",
        "pill_bg": "rgba(220,38,38,0.08)",
        "pill_border": "rgba(220,38,38,0.20)",
        "signature": "White background, red left accent bar, Inter font, 12-column grid, Swiss typographic cleanliness",
    },
    "terminal-green": {
        "display": "Terminal Green",
        "bg": "#0a0f0a",
        "accent": "#22c55e",
        "text_primary": "#bbf7d0",
        "text_body": "rgba(187,247,208,0.70)",
        "text_secondary": "rgba(187,247,208,0.50)",
        "text_muted": "rgba(187,247,208,0.35)",
        "card_bg": "rgba(34,197,94,0.06)",
        "card_border": "rgba(34,197,94,0.15)",
        "divider": "rgba(34,197,94,0.20)",
        "font_display": "'JetBrains Mono', 'Fira Code', monospace",
        "font_body": "'JetBrains Mono', 'Fira Code', monospace",
        "google_fonts": "JetBrains+Mono:wght@400;500;600;700",
        "background": """body {
    background: #0a0f0a;
    background-image:
        repeating-linear-gradient(0deg, rgba(34,197,94,0.03) 0px, rgba(34,197,94,0.03) 1px, transparent 1px, transparent 3px);
}
body::after {
    content: ''; position: fixed; inset: 0; pointer-events: none; z-index: 9998;
    background: repeating-linear-gradient(0deg, rgba(0,0,0,0.15) 0px, rgba(0,0,0,0.15) 1px, transparent 1px, transparent 3px);
}""",
        "accent_text": "#22c55e",
        "pill_bg": "rgba(34,197,94,0.12)",
        "pill_border": "rgba(34,197,94,0.30)",
        "signature": "Dark terminal background, green scanline pattern, CRT scanline overlay, JetBrains Mono monospace",
    },
    "vintage-editorial": {
        "display": "Vintage Editorial",
        "bg": "#fef7ed",
        "accent": "#92400e",
        "text_primary": "#451a03",
        "text_body": "rgba(69,26,3,0.70)",
        "text_secondary": "rgba(69,26,3,0.55)",
        "text_muted": "rgba(69,26,3,0.40)",
        "card_bg": "rgba(146,64,14,0.06)",
        "card_border": "rgba(146,64,14,0.15)",
        "divider": "rgba(146,64,14,0.20)",
        "font_display": "'Playfair Display', Georgia, serif",
        "font_body": "'Libre Baskerville', Georgia, serif",
        "google_fonts": "Playfair+Display:wght@700&family=Libre+Baskerville:wght@400;700",
        "background": """body {
    background: #fef7ed;
    background-image:
        radial-gradient(ellipse at 20% 20%, rgba(146,64,14,0.05) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(217,119,6,0.04) 0%, transparent 50%);
}""",
        "accent_text": "#92400e",
        "pill_bg": "rgba(146,64,14,0.08)",
        "pill_border": "rgba(146,64,14,0.20)",
        "signature": "Warm cream background, Playfair Display serif, abstract geometric shapes, vintage magazine aesthetic",
    },
}


# ====================================================================
# SLIDE CONTENT — 8 slides about slide-creator for each preset
# ====================================================================

def make_slides(lang="en", preset_key="aurora-mesh"):
    """Generate 8 slides about slide-creator, themed to the preset."""
    zh = lang == "zh"
    p = PRESETS[preset_key]
    accent_text = p['accent_text']  # extracted for use in f-string expressions

    # Helper to pick EN/ZH text
    def t(en_text, zh_text):
        return zh_text if zh else en_text

    # Slide content tuples: (label, notes_en, notes_zh, html_content_en, html_content_zh)
    slides = []

    # ---- SLIDE 1: COVER ----
    slides.append({
        "label": "cover",
        "notes": {"en": "Welcome audience. Introduce slide-creator vision.",
                  "zh": "欢迎观众。介绍产品愿景。"},
        "content": f"""<div class="content" style="text-align:center;">
    <div class="reveal">
        <span class="pill">{t('Open Source · Claude Code · OpenClaw', '开源 · Claude Code · OpenClaw')}</span>
    </div>
    <div class="reveal" style="transition-delay:0.1s">
        <h1>slide<span style="color:{p['accent_text']};">-creator</span></h1>
    </div>
    <div class="reveal" style="transition-delay:0.2s; max-width:560px; margin:0 auto;">
        <p style="font-size:clamp(16px,2vw,22px); margin-bottom:clamp(20px,3vw,36px);">
            {t('Zero-dependency HTML presentations for<br>Claude Code &amp; OpenClaw', '面向 Claude Code 与 OpenClaw 的<br>零依赖 HTML 演示文稿')}
        </p>
    </div>
    <div class="reveal" style="transition-delay:0.3s">
        <div class="stats" style="justify-content:center; display:flex; gap:clamp(24px,4vw,48px);">
            <div class="stat">
                <span class="stat-value" style="font-size:clamp(2rem,5vw,3.5rem); font-weight:800; color:{p['accent_text']};">21</span>
                <span class="stat-label" style="font-size:clamp(10px,1.2vw,13px); color:{p['text_muted']}; text-transform:uppercase; letter-spacing:0.08em;">{t('Presets', '预设')}</span>
            </div>
            <div style="width:1px; background:{p['divider']}; align-self:stretch;"></div>
            <div class="stat">
                <span class="stat-value" style="font-size:clamp(2rem,5vw,3.5rem); font-weight:800; color:{p['accent_text']};">0</span>
                <span class="stat-label" style="font-size:clamp(10px,1.2vw,13px); color:{p['text_muted']}; text-transform:uppercase; letter-spacing:0.08em;">{t('Dependencies', '依赖')}</span>
            </div>
            <div style="width:1px; background:{p['divider']}; align-self:stretch;"></div>
            <div class="stat">
                <span class="stat-value" style="font-size:clamp(2rem,5vw,3.5rem); font-weight:800; color:{p['accent_text']};">{t('∞', '∞')}</span>
                <span class="stat-label" style="font-size:clamp(10px,1.2vw,13px); color:{p['text_muted']}; text-transform:uppercase; letter-spacing:0.08em;">{t('Slides', '幻灯片')}</span>
            </div>
        </div>
    </div>
    <div class="reveal" style="transition-delay:0.4s; margin-top:clamp(20px,3vw,36px);">
        <p style="font-size:clamp(12px,1.3vw,15px); color:{p['text_muted']}; letter-spacing:0.06em; text-transform:uppercase;">{t('Build the deck that closes the deal.', '构建能拿下交易的演示文稿。')}</p>
    </div>
</div>"""
    })

    # ---- SLIDE 2: PROBLEM ----
    slides.append({
        "label": "problem",
        "notes": {"en": "Frame the problem: existing presentation tools are broken.",
                  "zh": "提出问题：现有演示工具都是破碎的。"},
        "content": f"""<div class="content">
    <div class="reveal">
        <span class="pill">{t('The Problem', '问题所在')}</span>
    </div>
    <div class="reveal" style="transition-delay:0.1s">
        <h2 style="margin-top:clamp(12px,2vw,20px);">{t("Presentations shouldn't<br>require a <span style=&quot;color:var(--accent)&quot;>build system</span>", "演示文稿不应该<br>需要一套<span style=&quot;color:var(--accent)&quot;>构建工具</span>")}</h2>
    </div>
    <div class="sep reveal" style="transition-delay:0.15s; height:1px; background:{p['divider']}; margin:clamp(12px,2vw,20px) 0;"></div>
    <div class="reveal" style="transition-delay:0.2s">
        <div style="display:grid; gap:clamp(16px,3vw,32px);">
            <div style="display:flex; gap:16px; align-items:start;">
                <div style="flex-shrink:0; width:32px; height:32px; border-radius:8px; background:{p['pill_bg']}; display:flex; align-items:center; justify-content:center; font-size:16px;">⚙️</div>
                <div>
                    <h3 style="font-size:clamp(14px,1.8vw,18px); font-weight:600; margin-bottom:4px;">{t('Complex Toolchain', '复杂的工具链')}</h3>
                    <p style="font-size:clamp(13px,1.4vw,15px); color:{p['text_body']};">{t('Node, Webpack, npm, plugins — just to make slides. Hours before you can present anything.', 'Node、Webpack、npm、插件——只为做幻灯片。能讲之前要花几小时配置。')}</p>
                </div>
            </div>
            <div style="display:flex; gap:16px; align-items:start;">
                <div style="flex-shrink:0; width:32px; height:32px; border-radius:8px; background:{p['pill_bg']}; display:flex; align-items:center; justify-content:center; font-size:16px;">📋</div>
                <div>
                    <h3 style="font-size:clamp(14px,1.8vw,18px); font-weight:600; margin-bottom:4px;">{t('Generic Output', '千篇一律的输出')}</h3>
                    <p style="font-size:clamp(13px,1.4vw,15px); color:{p['text_body']};">{t('Every deck looks like every other deck. Templates that scream "I used the same tool as everyone else."', '每份 deck 看起来都一样。模板在呐喊"我和别人用的一样"。')}</p>
                </div>
            </div>
            <div style="display:flex; gap:16px; align-items:start;">
                <div style="flex-shrink:0; width:32px; height:32px; border-radius:8px; background:{p['pill_bg']}; display:flex; align-items:center; justify-content:center; font-size:16px;">🔒</div>
                <div>
                    <h3 style="font-size:clamp(14px,1.8vw,18px); font-weight:600; margin-bottom:4px;">{t('No Ownership', '没有所有权')}</h3>
                    <p style="font-size:clamp(13px,1.4vw,15px); color:{p['text_body']};">{t("Your slides live in someone else's cloud. Export is an afterthought. Vendor lock-in is the business model.", '你的幻灯片存在别人的云里。导出是事后补救。供应商锁定就是商业模式。')}</p>
                </div>
            </div>
        </div>
    </div>
</div>"""
    })

    # ---- SLIDE 3: WORKFLOW ----
    slides.append({
        "label": "workflow",
        "notes": {"en": "Explain the style discovery workflow.",
                  "zh": "解释风格发现的工作流。"},
        "content": f"""<div class="content">
    <div class="reveal">
        <span class="pill">{t('Workflow', '工作流')}</span>
    </div>
    <div class="reveal" style="transition-delay:0.1s">
        <h2 style="margin-top:clamp(12px,2vw,20px);">{t('Style discovery that<br><span style=&quot;color:var(--accent)&quot;>actually works</span>', '风格发现<br><span style=&quot;color:var(--accent)&quot;>真正能用</span>')}</h2>
    </div>
    <div class="sep reveal" style="transition-delay:0.15s; height:1px; background:{p['divider']}; margin:clamp(12px,2vw,20px) 0;"></div>
    <div class="reveal" style="transition-delay:0.2s">
        <p style="font-size:clamp(14px,1.6vw,17px); color:{p['text_body']};">{t('Describe your mood. Get three visual previews. Pick what feels right — before a single slide is written.', '描述你的心情。获得三个视觉预览。选一个感觉对的——在写第一页幻灯片之前。')}</p>
    </div>
    <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:clamp(12px,2vw,24px); margin-top:clamp(16px,3vw,32px);" class="reveal" style="transition-delay:0.3s">
        <div style="background:{p['card_bg']}; border:1px solid {p['card_border']}; border-radius:12px; padding:clamp(16px,3vw,24px);">
            <div style="font-size:24px; margin-bottom:8px;">{t('🎨', '🎨')}</div>
            <h3 style="font-size:clamp(13px,1.5vw,16px); font-weight:600;">{t('Ask Mood', '描述 mood')}</h3>
            <p style="font-size:clamp(12px,1.3vw,14px); color:{p['text_body']}; margin-top:4px;">{t('"Bold and minimal" or "warm and creative" — natural language input.', '"大胆且极简"或"温暖而创意"——自然语言输入。')}</p>
        </div>
        <div style="background:{p['card_bg']}; border:1px solid {p['card_border']}; border-radius:12px; padding:clamp(16px,3vw,24px);">
            <div style="font-size:24px; margin-bottom:8px;">👁</div>
            <h3 style="font-size:clamp(13px,1.5vw,16px); font-weight:600;">{t('3 Mini Previews', '3 个迷你预览')}</h3>
            <p style="font-size:clamp(12px,1.3vw,14px); color:{p['text_body']}; margin-top:4px;">{t('Side-by-side renders of three matched styles before full generation.', '完全生成前并排渲染三种匹配风格。')}</p>
        </div>
        <div style="background:{p['card_bg']}; border:1px solid {p['card_border']}; border-radius:12px; padding:clamp(16px,3vw,24px);">
            <div style="font-size:24px; margin-bottom:8px;">✓</div>
            <h3 style="font-size:clamp(13px,1.5vw,16px); font-weight:600;">{t('Pick & Build', '选择并构建')}</h3>
            <p style="font-size:clamp(12px,1.3vw,14px); color:{p['text_body']}; margin-top:4px;">{t('Choose your style. The full presentation is generated in your chosen aesthetic.', '选择你的风格。完整的演示文稿按你选的美学生成。')}</p>
        </div>
    </div>
</div>"""
    })

    # ---- SLIDE 4: PRESETS ----
    preset_names = [
        ("Bold Signal", "Electric Studio", "Creative Voltage"),
        ("Dark Botanical", "Blue Sky", "Notebook Tabs"),
        ("Pastel Geometry", "Split Pastel", "Vintage Editorial"),
    ]
    if preset_key == "aurora-mesh":
        tag_html = lambda n, highlight: f'<span class="tag" style="background:{p["pill_bg"]}; border-color:{p["pill_border"]}; color:{p["accent_text"]};">{n} ✦</span>' if highlight else f'<span class="tag">{n}</span>'
    else:
        tag_html = lambda n, highlight: f'<span style="display:inline-block; padding:4px 12px; border-radius:999px; background:{p["pill_bg"]}; border:1px solid {p["pill_border"]}; color:{p["accent_text"]}; font-size:clamp(10px,1.2vw,13px); font-weight:600;">{n} ✦</span>' if highlight else f'<span style="display:inline-block; padding:4px 12px; border-radius:999px; background:{p["pill_bg"]}; border:1px solid {p["card_border"]}; color:{p["text_body"]}; font-size:clamp(10px,1.2vw,13px); font-weight:500;">{n}</span>'

    all_presets = ["Aurora Mesh", "Bold Signal", "Blue Sky", "Chinese Chan", "Creative Voltage",
                   "Dark Botanical", "Data Story", "Electric Studio", "Enterprise Dark",
                   "Glassmorphism", "Modern Newspaper", "Neo Brutalism", "Neo Retro Dev",
                   "Neon Cyber", "Notebook Tabs", "Paper & Ink", "Pastel Geometry", "Split Pastel",
                   "Swiss Modern", "Terminal Green", "Vintage Editorial"]
    tags_html = ""
    for name in all_presets:
        is_highlight = (name.lower().replace(" ", "-") == preset_key)
        tags_html += "        " + tag_html(name, is_highlight) + "\n"

    display_name = PRESETS[preset_key]["display"]

    slides.append({
        "label": "presets",
        "notes": {"en": f"Showcase all 21 presets. Highlight {display_name}.",
                  "zh": f"展示全部 21 个预设。高亮 {display_name}。"},
        "content": f"""<div class="content">
    <div class="reveal">
        <span class="pill">{t('21 Presets', '21 个预设')}</span>
    </div>
    <div class="reveal" style="transition-delay:0.1s">
        <h2 style="margin-top:clamp(12px,2vw,20px);">{t('Every presentation style,<br><span style=&quot;color:var(--accent)&quot;>already built</span>', '所有演示文稿风格，<br><span style=&quot;color:var(--accent)&quot;>已内置</span>')}</h2>
    </div>
    <div class="sep reveal" style="transition-delay:0.15s; height:1px; background:{p['divider']}; margin:clamp(12px,2vw,20px) 0;"></div>
    <div class="reveal" style="transition-delay:0.2s; display:flex; flex-wrap:wrap; gap:8px;">
{tags_html}    </div>
</div>"""
    })

    # ---- SLIDE 5: PRESENT MODE ----
    slides.append({
        "label": "present-mode",
        "notes": {"en": "Explain present mode: F5, fullscreen, speaker notes.",
                  "zh": "解释播放模式：F5、全屏、演讲者备注。"},
        "content": f"""<div class="content">
    <div class="reveal">
        <span class="pill">{t('Present Mode', '播放模式')}</span>
    </div>
    <div class="reveal" style="transition-delay:0.1s">
        <h2 style="margin-top:clamp(12px,2vw,20px);">{t('F5 to present.<br><span style=&quot;color:var(--accent)&quot;>Any screen, any size</span>', 'F5 即可播放。<br><span style=&quot;color:var(--accent)&quot;>任意屏幕，任意尺寸</span>')}</h2>
    </div>
    <div class="sep reveal" style="transition-delay:0.15s; height:1px; background:{p['divider']}; margin:clamp(12px,2vw,20px) 0;"></div>
    <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:clamp(12px,2vw,20px);" class="reveal" style="transition-delay:0.2s">
        <div style="background:{p['card_bg']}; border:1px solid {p['card_border']}; border-radius:12px; padding:clamp(16px,3vw,24px);">
            <div style="font-size:28px; margin-bottom:8px;">F5</div>
            <h3 style="font-size:clamp(13px,1.5vw,16px); font-weight:600;">{t('Fullscreen', '全屏')}</h3>
            <p style="font-size:clamp(12px,1.3vw,14px); color:{p['text_body']}; margin-top:4px;">{t('Slides scale to fill any display at 1440×900 aspect ratio.', '幻灯片以 1440×900 比例缩放适配任何显示器。')}</p>
        </div>
        <div style="background:{p['card_bg']}; border:1px solid {p['card_border']}; border-radius:12px; padding:clamp(16px,3vw,24px);">
            <div style="font-size:28px; margin-bottom:8px;">P</div>
            <h3 style="font-size:clamp(13px,1.5vw,16px); font-weight:600;">{t('Presenter View', '演讲者视图')}</h3>
            <p style="font-size:clamp(12px,1.3vw,14px); color:{p['text_body']}; margin-top:4px;">{t('Separate window with notes, timer, and slide counter.', '独立窗口，含备注、计时器和页数。')}</p>
        </div>
        <div style="background:{p['card_bg']}; border:1px solid {p['card_border']}; border-radius:12px; padding:clamp(16px,3vw,24px);">
            <div style="font-size:28px; margin-bottom:8px;">B</div>
            <h3 style="font-size:clamp(13px,1.5vw,16px); font-weight:600;">{t('Black Screen', '黑屏')}</h3>
            <p style="font-size:clamp(12px,1.3vw,14px); color:{p['text_body']}; margin-top:4px;">{t('Toggle black background during Q&A to focus attention.', '问答时切换黑屏，集中注意力。')}</p>
        </div>
    </div>
</div>"""
    })

    # ---- SLIDE 6: EDIT MODE ----
    slides.append({
        "label": "edit-mode",
        "notes": {"en": "Explain edit mode: E key, contenteditable, save.",
                  "zh": "解释编辑模式：E 键、contenteditable、保存。"},
        "content": f"""<div class="content">
    <div class="reveal">
        <span class="pill">{t('Edit Mode', '编辑模式')}</span>
    </div>
    <div class="reveal" style="transition-delay:0.1s">
        <h2 style="margin-top:clamp(12px,2vw,20px);">{t('Edit in the browser.<br><span style=&quot;color:var(--accent)&quot;>Save to disk</span>', '在浏览器中编辑。<br><span style=&quot;color:var(--accent)&quot;>保存到本地</span>')}</h2>
    </div>
    <div class="sep reveal" style="transition-delay:0.15s; height:1px; background:{p['divider']}; margin:clamp(12px,2vw,20px) 0;"></div>
    <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:clamp(12px,2vw,20px);" class="reveal" style="transition-delay:0.2s">
        <div style="background:{p['card_bg']}; border:1px solid {p['card_border']}; border-radius:12px; padding:clamp(16px,3vw,24px);">
            <div style="font-size:28px; margin-bottom:8px;">E</div>
            <h3 style="font-size:clamp(13px,1.5vw,16px); font-weight:600;">{t('Toggle Edit', '切换编辑')}</h3>
            <p style="font-size:clamp(12px,1.3vw,14px); color:{p['text_body']}; margin-top:4px;">{t('Hover the hotzone top-left. Click ✏ Edit. All text becomes editable.', '悬停左上角热区。点击 ✏ 编辑。所有文本变为可编辑。')}</p>
        </div>
        <div style="background:{p['card_bg']}; border:1px solid {p['card_border']}; border-radius:12px; padding:clamp(16px,3vw,24px);">
            <div style="font-size:28px; margin-bottom:8px;">📝</div>
            <h3 style="font-size:clamp(13px,1.5vw,16px); font-weight:600;">{t('Speaker Notes', '演讲备注')}</h3>
            <p style="font-size:clamp(12px,1.3vw,14px); color:{p['text_body']}; margin-top:4px;">{t('Notes panel slides up from bottom. Notes sync to presenter view.', '备注面板从底部滑出。备注同步到演讲者视图。')}</p>
        </div>
        <div style="background:{p['card_bg']}; border:1px solid {p['card_border']}; border-radius:12px; padding:clamp(16px,3vw,24px);">
            <div style="font-size:28px; margin-bottom:8px;">⌘S</div>
            <h3 style="font-size:clamp(13px,1.5vw,16px); font-weight:600;">{t('Save File', '保存文件')}</h3>
            <p style="font-size:clamp(12px,1.3vw,14px); color:{p['text_body']}; margin-top:4px;">{t('Ctrl+S downloads the edited HTML. Self-contained, zero dependencies.', 'Ctrl+S 下载编辑后的 HTML。自包含，零依赖。')}</p>
        </div>
    </div>
</div>"""
    })

    # ---- SLIDE 7: INSTALL / USAGE ----
    slides.append({
        "label": "install",
        "notes": {"en": "How to install and use slide-creator.",
                  "zh": "如何安装和使用 slide-creator。"},
        "content": f"""<div class="content">
    <div class="reveal">
        <span class="pill">{t('Getting Started', '快速开始')}</span>
    </div>
    <div class="reveal" style="transition-delay:0.1s">
        <h2 style="margin-top:clamp(12px,2vw,20px);">{t('Three commands.<br><span style=&quot;color:var(--accent)&quot;>Zero friction</span>', '三条命令。<br><span style=&quot;color:var(--accent)&quot;>零摩擦</span>')}</h2>
    </div>
    <div class="sep reveal" style="transition-delay:0.15s; height:1px; background:{p['divider']}; margin:clamp(12px,2vw,20px) 0;"></div>
    <div style="display:grid; gap:clamp(12px,2vw,20px);" class="reveal" style="transition-delay:0.2s">
        <div style="background:{p['card_bg']}; border:1px solid {p['card_border']}; border-radius:12px; padding:clamp(16px,3vw,24px); display:flex; align-items:center; gap:16px;">
            <div style="font-size:clamp(14px,1.5vw,18px); font-weight:800; color:{p['accent_text']}; font-family:monospace;">/slide-creator</div>
            <p style="font-size:clamp(13px,1.4vw,15px); color:{p['text_body']}; flex:1;">{t('Interactive mode — describe your mood, pick a style, get a deck', '交互模式——描述心情，选择风格，获得演示文稿')}</p>
        </div>
        <div style="background:{p['card_bg']}; border:1px solid {p['card_border']}; border-radius:12px; padding:clamp(16px,3vw,24px); display:flex; align-items:center; gap:16px;">
            <div style="font-size:clamp(14px,1.5vw,18px); font-weight:800; color:{p['accent_text']}; font-family:monospace;">/slide-creator --plan</div>
            <p style="font-size:clamp(13px,1.4vw,15px); color:{p['text_body']}; flex:1;">{t('Generate outline — review and edit before building', '生成大纲——构建前审阅和编辑')}</p>
        </div>
        <div style="background:{p['card_bg']}; border:1px solid {p['card_border']}; border-radius:12px; padding:clamp(16px,3vw,24px); display:flex; align-items:center; gap:16px;">
            <div style="font-size:clamp(14px,1.5vw,18px); font-weight:800; color:{p['accent_text']}; font-family:monospace;">/slide-creator --generate</div>
            <p style="font-size:clamp(13px,1.4vw,15px); color:{p['text_body']}; flex:1;">{t('Build from PLANNING.md — full HTML with all modes', '从 PLANNING.md 构建——完整 HTML 含所有模式')}</p>
        </div>
    </div>
</div>"""
    })

    # ---- SLIDE 8: CLOSING ----
    slides.append({
        "label": "closing",
        "notes": {"en": "Closing CTA. Install link and takeaway.",
                  "zh": "结束 CTA。安装链接和总结。"},
        "content": f"""<div class="content" style="text-align:center;">
    <div class="reveal">
        <h1 style="font-size:clamp(2rem,5.5vw,4rem);">{t('Stop making slides.<br>Start telling stories.', '别再"做幻灯片"了。<br>开始讲故事。')}</h1>
    </div>
    <div class="sep reveal" style="transition-delay:0.1s; height:1px; background:{p['divider']}; margin:clamp(16px,3vw,28px) auto; width:60px;"></div>
    <div class="reveal" style="transition-delay:0.2s">
        <p style="font-size:clamp(14px,2vw,20px); color:{p['text_body']}; max-width:520px; margin:0 auto;">
            {t('One HTML file. Every style. Any browser. No build step.', '一个 HTML 文件。涵盖所有风格。任意浏览器。无需构建步骤。')}
        </p>
    </div>
    <div class="reveal" style="transition-delay:0.3s; margin-top:clamp(20px,3vw,36px);">
        <div style="font-size:clamp(13px,1.5vw,16px); font-family:monospace; background:{p['card_bg']}; border:1px solid {p['card_border']}; border-radius:12px; padding:clamp(12px,2vw,20px); display:inline-block;">
            <span style="color:{p['accent_text']};">$</span> clawhub install kai-slide-creator
        </div>
    </div>
    <div class="reveal" style="transition-delay:0.4s; margin-top:clamp(12px,2vw,24px);">
        <p style="font-size:clamp(11px,1.2vw,14px); color:{p['text_muted']}; letter-spacing:0.04em;">{t('github.com/kaisersong/slide-creator', 'github.com/kaisersong/slide-creator')}</p>
    </div>
</div>"""
    })

    return slides


# ====================================================================
# BUILD SLIDES HTML
# ====================================================================

def build_slides_html(slides, lang="en"):
    """Build HTML string from slide list."""
    html = ""
    for i, slide in enumerate(slides):
        notes = slide["notes"][lang]
        content = slide["content"]
        nl = '\n'
        html += f'<section class="slide" data-notes="{notes}">{nl}{content}{nl}</section>{nl}{nl}'
    return html


# ====================================================================
# GENERATE DEMO
# ====================================================================

def generate_demo(preset_key, lang="en"):
    """Generate a single demo file."""
    p = PRESETS[preset_key]
    display = p["display"]
    lang_attr = "zh-CN" if lang == "zh" else "en"
    title = f"{display} · " + ("下一代开发者平台" if lang == "zh" else "Next-Gen Developer Platform")

    slides = make_slides(lang, preset_key)
    slides_html = build_slides_html(slides, lang)

    # Google Fonts URL
    gfonts_url = f"https://fonts.googleapis.com/css2?family={p['google_fonts']}&display=swap"

    html = f"""<!DOCTYPE html>
<html lang="{lang_attr}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{gfonts_url}" rel="stylesheet">
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

:root {{
    --bg: {p.get('bg', '#1a1a1a')};
    --accent: {p['accent']};
    --text-primary: {p['text_primary']};
    --text-body: {p['text_body']};
    --text-secondary: {p['text_secondary']};
    --text-muted: {p['text_muted']};
    --card-bg: {p['card_bg']};
    --card-border: {p['card_border']};
    --divider: {p['divider']};
    --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
    --duration-normal: 0.6s;
}}

html {{ scroll-snap-type: y mandatory; height: 100%; }}

body {{
    height: 100%;
    overflow-x: hidden;
    font-family: {p['font_body']};
    color: var(--text-primary);
}}

/* Background */
{p['background']}

.slide {{
    width: 100vw; height: 100vh; height: 100dvh;
    scroll-snap-align: start; overflow: hidden;
    position: relative; display: flex;
    flex-direction: column; align-items: center; justify-content: center;
    padding: clamp(1.5rem, 4vw, 4rem);
}}

.slide .content {{
    width: 100%; max-width: min(90vw, 800px);
    padding: clamp(24px, 5vw, 64px);
    position: relative; z-index: 1;
}}

h1 {{ font-size: clamp(2rem, 5.5vw, 4rem); font-weight: 800; line-height: 1.1; letter-spacing: -0.02em; }}
h2 {{ font-size: clamp(1.4rem, 3.5vw, 2.4rem); font-weight: 700; line-height: 1.2; letter-spacing: -0.01em; }}
h3 {{ font-size: clamp(0.9rem, 1.6vw, 1.2rem); font-weight: 600; }}
p {{ font-size: clamp(0.82rem, 1.4vw, 1.05rem); line-height: 1.6; color: var(--text-body); }}

.pill {{
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 14px; border-radius: 999px;
    font-size: 12px; font-weight: 600; letter-spacing: 0.05em;
    background: {p['pill_bg']}; color: {p['accent_text']};
    border: 1px solid {p['pill_border']};
}}

.reveal {{
    opacity: 0; transform: translateY(20px);
    transition: opacity var(--duration-normal) var(--ease-out-expo),
                transform var(--duration-normal) var(--ease-out-expo);
}}
.slide.visible .reveal {{ opacity: 1; transform: translateY(0); }}

/* Progress bar */
.progress-bar {{ position: fixed; top: 0; left: 0; height: 3px; background: var(--accent); width: 0%; z-index: 100; transition: width 0.3s ease; }}

/* Nav dots placeholder */
.nav-dots {{}}

{PRESENT_MODE_CSS}
{WATERMARK_CSS}
{EDIT_MODE_CSS}

@media (max-height: 700px) {{
    :root {{ --slide-padding: clamp(0.75rem, 3vw, 2rem); }}
}}
@media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{ animation-duration: 0.01ms !important; transition-duration: 0.2s !important; }}
}}
</style>
</head>
<body data-export-progress="true" data-preset="{display}">

<div class="progress-bar"></div>
<nav class="nav-dots" aria-label="Slide navigation"></nav>

<div class="edit-hotzone"></div>
<button class="edit-toggle" id="editToggle" title="{'编辑模式' if lang == 'zh' else 'Edit mode'} (E)">{'✏ 编辑' if lang == 'zh' else '✏ Edit'}</button>
<div id="notes-panel">
  <div id="notes-panel-header">
    <div id="notes-panel-label">{'演讲者备注' if lang == 'zh' else 'SPEAKER NOTES'}</div>
    <button id="notes-collapse-btn" title="{'折叠' if lang == 'zh' else 'Collapse'}">&#9660;</button>
  </div>
  <div id="notes-body">
    <textarea id="notes-textarea" placeholder="{'添加备注...' if lang == 'zh' else 'Add notes...'}"></textarea>
  </div>
</div>

{slides_html}
<script>
{PRESENT_MODE_JS}
{SLIDE_JS}
/* Presenter Mode */
{PRESENTER_MODE_JS}
  new PresentMode(new SlidePresentation());
}}
</script>
<script>
{WATERMARK_JS.replace('{preset}', display)}
</script>
</body>
</html>"""

    return html


# ====================================================================
# MAIN
# ====================================================================

presets = list(PRESETS.keys())

count = 0
total_lines = 0

for preset in presets:
    for lang in ["en", "zh"]:
        filename = f"{preset}-{lang}.html"
        html = generate_demo(preset, lang)

        path = os.path.join(DEMO_DIR, filename)
        with open(path, 'w') as f:
            f.write(html)

        lines = html.count('\n')
        count += 1
        total_lines += lines
        print(f"  ✓ {filename} ({lines} lines)")

print(f"\n{'='*60}")
print(f"Generated {count} demo files, {total_lines} total lines")
print(f"Files: demos/*-en.html + *-zh.html")
print(f"{'='*60}")
