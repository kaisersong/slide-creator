"""Regression coverage for play-mode geometry and animated-cover runtime guards.

These lock the two runtime failure classes that only surface on stage:
1. Root typography driven by window width, which truncates dense slides inside the
   fixed 1440x900 play-mode box.
2. Canvas buffers sized from a hidden element's rect, which collapse to 1x1.
Plus the detection gap that hid both: geometry QA only measured window mode at tall
viewports, and only titles were checked for slide-box clipping.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from browser_geometry_qa import (  # noqa: E402
    CLIPPING_TOLERANCE_PX,
    HARD_FAILURE_CODES,
    LAPTOP_WINDOW_VIEWPORT,
    MEASUREMENT_MODES,
    analyze_browser_geometry_html,
)
from validate_html import (  # noqa: E402
    STRICT_CHECKS,
    check_canvas_visibility_guard,
    check_playback_scale_safety,
)


def _run(check, html: str):
    soup = BeautifulSoup(html, "html.parser")
    warnings: list[str] = []
    passed, message = check(soup, html, warnings)
    return passed, message, warnings


SAFE_ROOT_CSS = """
<html><head><style>
html { height: 100%; }
:root { --title-size: clamp(1.5rem, 5vw, 4rem); }
body.presenting .slide { width: 1440px !important; height: 900px !important; }
</style></head><body></body></html>
"""


def test_playback_scale_safety_accepts_fixed_root_typography():
    passed, message, _ = _run(check_playback_scale_safety, SAFE_ROOT_CSS)
    assert passed, message


def test_playback_scale_safety_rejects_viewport_width_root_font_size():
    html = "<html><head><style>html { font-size: 1.25vw; }</style></head><body></body></html>"
    passed, message, _ = _run(check_playback_scale_safety, html)
    assert not passed
    assert "viewport width units" in message


def test_playback_scale_safety_rejects_width_media_root_font_override():
    html = """
    <html><head><style>
    html { font-size: 16px; }
    @media (min-width: 1440px) { html { font-size: 18px; } }
    </style></head><body></body></html>
    """
    passed, message, _ = _run(check_playback_scale_safety, html)
    assert not passed
    assert "width-based @media" in message


def test_playback_scale_safety_allows_height_based_media_queries():
    html = """
    <html><head><style>
    html { font-size: 16px; }
    @media (max-height: 860px) { :root { --slide-padding: 1rem; } }
    </style></head><body></body></html>
    """
    passed, message, _ = _run(check_playback_scale_safety, html)
    assert passed, message


UNGUARDED_CANVAS_JS = """
<html><body><canvas id="iriCanvas"></canvas><script>
const canvas = document.getElementById('iriCanvas');
function resize() {
  const rect = canvas.getBoundingClientRect();
  canvas.width = Math.max(1, Math.round(rect.width));
  canvas.height = Math.max(1, Math.round(rect.height));
}
window.addEventListener('resize', resize);
</script></body></html>
"""

GUARDED_CANVAS_JS = """
<html><body><canvas id="iriCanvas"></canvas><script>
const canvas = document.getElementById('iriCanvas');
function resize() {
  const rect = canvas.getBoundingClientRect();
  if (rect.width < 2 || rect.height < 2) return false;
  canvas.width = Math.round(rect.width);
  canvas.height = Math.round(rect.height);
  return true;
}
new ResizeObserver(() => resize()).observe(canvas);
window.addEventListener('resize', resize);
</script></body></html>
"""


def test_canvas_guard_rejects_math_max_one_fallback():
    passed, message, _ = _run(check_canvas_visibility_guard, UNGUARDED_CANVAS_JS)
    assert not passed
    assert "small-rect guard" in message


def test_canvas_guard_accepts_guarded_resize_with_observer():
    passed, message, warnings = _run(check_canvas_visibility_guard, GUARDED_CANVAS_JS)
    assert passed, message
    assert not warnings


def test_canvas_guard_ignores_decks_without_rect_driven_canvas():
    passed, message, _ = _run(check_canvas_visibility_guard, SAFE_ROOT_CSS)
    assert passed, message


def test_new_runtime_checks_are_registered_in_strict_mode():
    assert check_playback_scale_safety in STRICT_CHECKS
    assert check_canvas_visibility_guard in STRICT_CHECKS


def test_bundled_fantasy_rainbow_starter_keeps_the_hidden_element_guard():
    starter = (ROOT / "themes" / "fantasy-rainbow" / "starter.html").read_text(encoding="utf-8")
    assert "getBoundingClientRect()" in starter
    assert "rect.width < 2 || rect.height < 2" in starter
    passed, message, _ = _run(check_canvas_visibility_guard, starter)
    assert passed, message


def test_base_css_documents_short_window_tier_and_play_mode_contract():
    text = (ROOT / "references" / "base-css.md").read_text(encoding="utf-8")
    assert "@media (max-height: 860px)" in text
    assert "Play Mode Geometry Contract" in text
    assert "--mode both" in text
    assert "rect.width < 2" in text


def test_anti_patterns_document_playback_runtime_rules():
    text = (ROOT / "references" / "impeccable-anti-patterns.md").read_text(encoding="utf-8")
    assert "根字号跟随窗口宽度" in text
    assert "对隐藏元素测尺寸" in text
    assert "只在窗口模式验收" in text


def test_content_clipped_is_a_hard_failure_code():
    assert HARD_FAILURE_CODES["content_clipped"] == "browser-geometry-content-clipped"
    assert MEASUREMENT_MODES == ("window", "present")
    assert LAPTOP_WINDOW_VIEWPORT == {"width": 1440, "height": 733}
    assert CLIPPING_TOLERANCE_PX >= 2


CLIPPED_DECK = """
<html><head><style>
html { height: 100%; }
.slide { width: 100vw; height: 100vh; overflow: hidden; position: relative;
         display: flex; flex-direction: column; font-family: system-ui, sans-serif; }
.slide-content { padding: 24px; }
#present-btn { position: fixed; bottom: 1.5rem; right: 1.5rem; }
body.presenting .slide { position: fixed; top: 0; left: 0; width: 1440px !important;
                         height: 900px !important; transform-origin: top left; display: none !important; }
body.presenting .slide.p-on { display: flex !important; }
.row { font-size: 40px; line-height: 1.6; color: #111; }
</style></head>
<body data-preset="Test">
<section class="slide" aria-label="One" data-notes="n"><div class="slide-content">
<h2>Dense table</h2>
<p class="row">row one</p><p class="row">row two</p><p class="row">row three</p>
<p class="row">row four</p><p class="row">row five</p><p class="row">row six</p>
<p class="row">row seven</p><p class="row">row eight</p><p class="row">row nine</p>
<p class="row">last row falls off the slide box</p>
</div></section>
<button id="present-btn">&#9654;</button>
<script>
const slides = Array.from(document.querySelectorAll('.slide'));
document.getElementById('present-btn').addEventListener('click', () => {
  document.body.classList.add('presenting');
  const s = Math.min(window.innerWidth / 1440, window.innerHeight / 900);
  slides.forEach((slide) => { slide.style.transform = 'scale(' + s + ')'; });
  slides[0].classList.add('p-on');
});
</script>
</body></html>
"""


@pytest.mark.slow
def test_geometry_qa_flags_content_clipped_by_the_slide_box():
    report = analyze_browser_geometry_html(
        CLIPPED_DECK,
        viewports=[{"width": 1280, "height": 400}],
        stable_runs=1,
    )
    clipped = [item for item in report["violations"] if item["type"] == "content_clipped"]
    assert clipped, report["violations"]
    assert report["pass"] is False
    assert HARD_FAILURE_CODES["content_clipped"] in report["hard_failures"]
    assert clipped[0]["edge"] == "bottom"
    assert clipped[0]["mode"] == "window"


@pytest.mark.slow
def test_geometry_qa_measures_play_mode_geometry():
    report = analyze_browser_geometry_html(
        CLIPPED_DECK,
        viewports=[{"width": 1600, "height": 900}],
        stable_runs=1,
        modes=("window", "present"),
    )
    assert report["runner"]["modes"] == ["window", "present"]
    assert report["runner"]["present_mode_entered"] == {"1600x900": True}
    assert report["diagnostics"]["mode_count"] == 2
    measured_modes = {item.get("mode") for item in report["measurements"]}
    assert measured_modes == {"window", "present"}


def test_geometry_qa_rejects_unknown_measurement_modes():
    with pytest.raises(ValueError):
        analyze_browser_geometry_html(CLIPPED_DECK, modes=("fullscreen",))


def test_native_core_shells_emit_the_short_window_tier():
    """Both native-core shells must carry the shared short-window compaction."""
    sys.path.insert(0, str(SCRIPTS))
    import low_context  # noqa: PLC0415

    assert "@media (max-height: 860px)" in low_context.SHORT_WINDOW_SHELL_CSS
    assert "@media (max-height: 760px)" in low_context.SHORT_WINDOW_SHELL_CSS

    style_contract = {"css_blocks": [":root { --demo: 1px; }"], "tokens": {"--bg": "#0b1020"}}
    non_swiss = low_context._build_non_swiss_shell_css(style_contract, "Enterprise Dark")
    swiss = low_context._build_swiss_shell_css(style_contract)
    for css in (non_swiss, swiss):
        assert "@media (max-height: 860px)" in css
        assert "@media (max-height: 760px)" in css
    # Swiss dense evidence stacks get their own compaction.
    assert ".inst-blocks" in swiss


def test_profile_renderer_emits_short_window_and_phone_density_tiers():
    sys.path.insert(0, str(SCRIPTS))
    import preset_profile_renderer  # noqa: PLC0415

    source = Path(preset_profile_renderer.__file__).read_text(encoding="utf-8")
    assert "@media (max-height: 860px)" in source
    # Display numerals must keep a line box tall enough for their glyphs.
    assert "line-height: 1.12 !important" in source
    # Phone density: long showcase lists become two compact columns instead of being cropped.
    assert "grid-template-columns: repeat(2, minmax(0, 1fr)) !important" in source


def test_blue_sky_starter_uses_viewport_aware_dense_grid_rows():
    starter = (ROOT / "references" / "blue-sky-starter.html").read_text(encoding="utf-8")
    assert ".bento-dense" in starter
    assert "@media (max-height: 860px)" in starter
    assert "grid-auto-rows:168px" not in starter


def test_fantasy_rainbow_theme_has_short_window_tiers():
    starter = (ROOT / "themes" / "fantasy-rainbow" / "starter.html").read_text(encoding="utf-8")
    assert "@media (max-height: 860px)" in starter
    assert "@media (max-height: 780px)" in starter


def test_release_gate_desktop_geometry_covers_laptop_window_and_play_mode():
    """run_evals must gate on the laptop window and on play-mode geometry."""
    run_evals_source = (SCRIPTS / "run_evals.py").read_text(encoding="utf-8")
    assert "LAPTOP_WINDOW_VIEWPORT" in run_evals_source
    assert "MEASUREMENT_MODES" in run_evals_source
    assert "modes=MEASUREMENT_MODES" in run_evals_source
