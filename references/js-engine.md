# JS Engine — SlidePresentation, PresentMode, Presenter, Editor

Non-Blue-Sky 风格共用的 JS 引擎代码。生成时直接插入 `<script>` 标签，无需修改。

---

## 完整 JS 代码（插入到 `</body>` 前）

```javascript
class SlidePresentation {
    constructor() {
        this.slides = document.querySelectorAll('.slide');
        this.currentSlide = 0;
        this.channel = new BroadcastChannel('slide-creator-presenter');
        this.slides[0]?.classList.add('visible');
        this.slides[0]?.querySelectorAll('.reveal').forEach(function(r) { r.classList.add('visible'); });
        this.setupNavDots(); this.setupObserver(); this.setupKeyboard();
        this.setupTouch(); this.setupWheel(); this.setupPresenter(); this.setupEditor(); this.updateProgress();
    }

    setupNavDots() {
        const nav = document.querySelector('.nav-dots');
        if (!nav) return;
        this.slides.forEach((_, i) => {
            const dot = document.createElement('button');
            dot.setAttribute('aria-label', 'Go to slide ' + (i + 1));
            dot.style.cssText = 'width:8px;height:8px;border-radius:50%;border:none;cursor:pointer;background:rgba(255,255,255,0.3);transition:all 0.3s;';
            dot.addEventListener('click', () => this.goTo(i)); nav.appendChild(dot);
        });
        nav.style.cssText = 'position:fixed;right:1.5rem;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;gap:8px;z-index:100;';
    }

    setupObserver() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    this.currentSlide = [...this.slides].indexOf(entry.target);
                    this.updateProgress(); this.updateDots(); this.broadcastState();
                    this.updateNotesPanel();
                }
            });
        }, { threshold: 0.5 });
        this.slides.forEach(s => observer.observe(s));
    }

    setupKeyboard() {
        document.addEventListener('keydown', (e) => {
            if (e.target.getAttribute('contenteditable') || e.target.tagName === 'TEXTAREA') return;
            if (['ArrowDown','ArrowRight',' ','PageDown','Enter'].includes(e.key)) { e.preventDefault(); this.next(); }
            else if (['ArrowUp','ArrowLeft','PageUp','Backspace'].includes(e.key)) { e.preventDefault(); this.prev(); }
            else if (e.key === 'p' || e.key === 'P') { window.open(location.href.split('?')[0] + '?presenter', 'slide-presenter-' + Date.now(), 'width=1100,menubar=no,toolbar=no,location=no'); }
            else if (e.key === 'e' || e.key === 'E') { if (this.editor && !this.editor.active) this.editor.enter(); else if (this.editor && this.editor.active) this.editor.exit(); }
        });
    }

    setupTouch() {
        let startY = 0;
        document.addEventListener('touchstart', e => { startY = e.touches[0].clientY; }, { passive: true });
        document.addEventListener('touchend', e => { const d = startY - e.changedTouches[0].clientY; if (Math.abs(d) > 50) d > 0 ? this.next() : this.prev(); });
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
        this.channel.postMessage({ type: 'state', index: this.currentSlide, total: this.slides.length, notes: slide?.dataset.notes || '' });
    }

    goTo(index) {
        this.slides.forEach((slide, i) => {
            slide.classList.toggle('visible', i === index);
            slide.querySelectorAll('.reveal').forEach(function(r) { r.classList.toggle('visible', i === index); });
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

    setupEditor() {
        const panel = document.getElementById('notes-panel');
        const label = document.getElementById('notes-panel-label');
        const textarea = document.getElementById('notes-textarea');
        const toggle = document.getElementById('editToggle');
        const hotzone = document.querySelector('.edit-hotzone');
        let hideTimeout = null;

        hotzone.addEventListener('mouseenter', () => { clearTimeout(hideTimeout); toggle.classList.add('show'); });
        hotzone.addEventListener('mouseleave', () => { hideTimeout = setTimeout(() => { if (this.editor.active) return; toggle.classList.remove('show'); }, 400); });
        toggle.addEventListener('mouseenter', () => clearTimeout(hideTimeout));
        toggle.addEventListener('mouseleave', () => { hideTimeout = setTimeout(() => { if (this.editor.active) return; toggle.classList.remove('show'); }, 400); });
        hotzone.addEventListener('click', () => this.editor.toggle());
        toggle.addEventListener('click', () => this.editor.toggle());

        document.getElementById('notes-panel-header').addEventListener('click', () => panel.classList.toggle('collapsed'));

        textarea.addEventListener('input', () => {
            const slide = this.slides[this.currentSlide];
            if (slide) { slide.dataset.notes = textarea.value; this.broadcastState(); }
        });

        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 's') { e.preventDefault(); this.saveFile(); }
        });

        this.editor = {
            active: false,
            toggle: () => this.editor.active ? this.editor.exit() : this.editor.enter(),
            enter: () => {
                this.editor.active = true;
                toggle.classList.add('active'); toggle.textContent = 'Done';
                this.slides.forEach(s => s.querySelectorAll('h1,h2,h3,p,li,span,td,th').forEach(el => {
                    el.setAttribute('contenteditable', 'true'); el.style.outline = 'none';
                }));
                panel.classList.add('active'); this.updateNotesPanel();
            },
            exit: () => {
                this.editor.active = false;
                toggle.classList.remove('active'); toggle.textContent = 'Edit';
                this.slides.forEach(s => s.querySelectorAll('[contenteditable]').forEach(el => {
                    el.removeAttribute('contenteditable'); el.style.outline = '';
                }));
                panel.classList.remove('active');
            }
        };
        this._notesLabel = label; this._notesTextarea = textarea;
    }

    updateNotesPanel() {
        if (!this.editor?.active) return;
        const slide = this.slides[this.currentSlide];
        this._notesLabel.textContent = 'SPEAKER NOTES \u2014 SLIDE ' + (this.currentSlide + 1) + ' / ' + this.slides.length;
        this._notesTextarea.value = slide?.dataset.notes || '';
    }

    saveFile() {
        const html = '<!DOCTYPE html>\n' + document.documentElement.outerHTML;
        const bytes = new TextEncoder().encode(html);
        fetch(location.pathname, { method: 'PUT', body: bytes, headers: { 'Content-Type': 'text/html' } })
            .catch(() => {
                const a = Object.assign(document.createElement('a'), {
                    href: URL.createObjectURL(new Blob([html], { type: 'text/html' })),
                    download: location.pathname.split('/').pop() || 'presentation.html'
                }); a.click(); URL.revokeObjectURL(a.href);
            });
    }
}
```

---

## Presenter Window (`?presenter` branch)

放在 `SlidePresentation` 类定义之后，`else` 分支内。

```javascript
if (new URLSearchParams(location.search).has('presenter')) {
    document.title = 'Presenter \u2014 ' + document.title;
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
        .pv-arrow { width: 32px; height: 32px; border-radius: 6px; border: 1px solid #333; background: #2a2a2a; color: #aaa; font-size: 1rem; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .pv-arrow:hover { background: #383838; color: #fff; }
        #pv-counter { text-align: center; flex: 1; }
        #pv-num { font-size: 1.6rem; font-weight: 700; font-variant-numeric: tabular-nums; line-height: 1; }
        #pv-of { color: #555; font-size: 0.75rem; margin-top: 0.2rem; }
        #pv-timer { font-size: 1.5rem; font-weight: 700; font-family: monospace; font-variant-numeric: tabular-nums; }
        #pv-timer-label { font-size: 0.6rem; letter-spacing: 0.18em; text-transform: uppercase; color: #555; }
    </style>
    <div id="pv">
        <div class="pv-panel"><div id="pv-label">Speaker Notes</div><div id="pv-notes">Waiting for main window...</div></div>
        <div id="pv-right">
            <div class="pv-panel"><div id="pv-nav">
                <button class="pv-arrow" id="pv-prev">\u2190</button>
                <div id="pv-counter"><div id="pv-num">\u2014</div><div id="pv-of">/ \u2014</div></div>
                <button class="pv-arrow" id="pv-next">\u2192</button>
            </div></div>
            <div class="pv-panel"><div id="pv-timer-label">Elapsed</div><div id="pv-timer">0:00</div></div>
        </div>
    </div>`;

    const ch = new BroadcastChannel('slide-creator-presenter');
    let startTime = null;
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
        document.getElementById('pv-of').textContent = '/ ' + e.data.total;
    });
    ch.postMessage({ type: 'request-state' });

    setInterval(() => {
        if (!startTime) return;
        const s = Math.floor((Date.now() - startTime) / 1000);
        document.getElementById('pv-timer').textContent = Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0');
    }, 1000);

    document.getElementById('pv-prev').addEventListener('click', () => ch.postMessage({ type: 'nav-prev' }));
    document.getElementById('pv-next').addEventListener('click', () => ch.postMessage({ type: 'nav-next' }));
    document.addEventListener('keydown', e => {
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ' || e.key === 'PageDown' || e.key === 'Enter') ch.postMessage({ type: 'nav-next' });
        else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp' || e.key === 'PageUp' || e.key === 'Backspace') ch.postMessage({ type: 'nav-prev' });
    });

} else {
// PresentMode class goes here, then: new PresentMode(new SlidePresentation());
```

---

## PresentMode Class

```javascript
class PresentMode {
    constructor(ctrl) {
        this.ctrl = ctrl;
        this.baseW = 1440; this.baseH = 900;
        this.active = false;
        const btn = document.createElement('button');
        btn.id = 'present-btn'; btn.title = 'Present (F5)'; btn.setAttribute('aria-label', 'Present'); btn.textContent = '\u25B6';
        document.body.appendChild(btn);
        const counter = document.createElement('div');
        counter.id = 'present-counter'; document.body.appendChild(counter);
        btn.addEventListener('click', () => this.enter());
        document.addEventListener('keydown', e => {
            if (e.key === 'F5') { e.preventDefault(); this.enter(); }
            if (e.key === 'Escape' && this.active) this.exit();
            if ((e.key === 'b' || e.key === 'B') && this.active) document.body.classList.toggle('presenting-black');
        });
        document.addEventListener('fullscreenchange', () => { if (this.active) { setTimeout(() => this._scale(), 100); } if (!document.fullscreenElement && this.active) this.exit(); });
        window.addEventListener('resize', () => { if (this.active) this._scale(); });
    }
    enter() {
        if (this.active) return;
        this.active = true;
        document.body.classList.add('presenting');
        if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen().catch(() => {});
        this._scale();
        this._show(this.ctrl.currentSlide);
        this._updateCounter();
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
        this._reset();
        if (document.fullscreenElement) document.exitFullscreen?.();
        if (this._origGoTo) { this.ctrl.goTo = this._origGoTo; this._origGoTo = null; }
        this.ctrl.slides[this.ctrl.currentSlide]?.scrollIntoView({ behavior: 'instant' });
    }
    _scale() {
        const vw = window.innerWidth;
        const vh = window.innerHeight;
        const s = Math.min(vw / this.baseW, vh / this.baseH);
        const ox = (vw - this.baseW * s) / 2;
        const oy = (vh - this.baseH * s) / 2;
        this.ctrl.slides.forEach(slide => {
            slide.style.transform = 'translate(' + ox + 'px, ' + oy + 'px) scale(' + s + ')';
        });
    }
    _reset() {
        this.ctrl.slides.forEach(slide => { slide.style.transform = ''; slide.classList.remove('p-on'); });
    }
    _show(i) {
        this.ctrl.slides.forEach((s, idx) => s.classList.toggle('p-on', idx === i));
    }
    _updateCounter() {
        const c = document.getElementById('present-counter');
        if (c) c.textContent = (this.ctrl.currentSlide + 1) + ' / ' + this.ctrl.slides.length;
    }
}
new PresentMode(new SlidePresentation());
}
```

---

## Watermark Script（独立 `<script>` 标签）

```javascript
(function() {
    var slides = document.querySelectorAll('.slide');
    if (!slides.length) return;
    var last = slides[slides.length - 1];
    var credit = document.createElement('div');
    credit.className = 'slide-credit';
    credit.textContent = 'By kai-slide-creator v[version] · [preset-name]';
    last.appendChild(credit);
})();
```
