from __future__ import annotations

import sys
from pathlib import Path
from io import BytesIO

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from browser_geometry_qa import _capture_screenshot, _contrast_violations, analyze_browser_geometry_html  # noqa: E402


VIEWPORTS = [{"width": 1600, "height": 900}]


class _FlakyScreenshotPage:
    def __init__(self, failures: int) -> None:
        self.failures = failures
        self.calls = 0
        self.waits: list[int] = []

    def screenshot(self, **_kwargs):
        self.calls += 1
        if self.calls <= self.failures:
            raise RuntimeError("transient screenshot timeout")
        return b"png"

    def wait_for_timeout(self, timeout: int) -> None:
        self.waits.append(timeout)


def test_capture_screenshot_retries_one_transient_failure():
    page = _FlakyScreenshotPage(failures=1)

    assert _capture_screenshot(page) == b"png"
    assert page.calls == 2
    assert page.waits == [100]


def test_capture_screenshot_preserves_failure_after_retry():
    page = _FlakyScreenshotPage(failures=2)

    with pytest.raises(RuntimeError, match="transient screenshot timeout"):
        _capture_screenshot(page)
    assert page.calls == 2
    assert page.waits == [100]


def test_contrast_sampler_ignores_foreground_pixels_for_large_text_on_brand_panels():
    image = Image.new("RGB", (140, 80), (255, 87, 34))
    for x in range(68, 73):
        for y in range(38, 43):
            image.putpixel((x, y), (255, 255, 255))
    buffer = BytesIO()
    image.save(buffer, format="PNG")

    violations, telemetry = _contrast_violations(
        [
            {
                "text": "Large readable card title",
                "visible": True,
                "color": "rgb(255, 255, 255)",
                "role": "title",
                "font_size": 36,
                "rect": {"x": 20, "y": 20, "width": 100, "height": 40},
                "selector": "h1.card-title",
                "slide_index": 1,
            }
        ],
        buffer.getvalue(),
        evidence_image="foreground-sample.png",
    )

    assert violations == []
    assert telemetry == []


def test_contrast_sampler_composites_rgba_foreground_against_background():
    image = Image.new("RGB", (140, 80), (255, 255, 255))
    buffer = BytesIO()
    image.save(buffer, format="PNG")

    violations, _telemetry = _contrast_violations(
        [
            {
                "text": "Semi transparent muted copy",
                "visible": True,
                "color": "rgba(0, 0, 0, 0.4)",
                "role": "text",
                "font_size": 16,
                "rect": {"x": 20, "y": 20, "width": 100, "height": 40},
                "selector": "p.muted",
                "slide_index": 1,
            }
        ],
        buffer.getvalue(),
        evidence_image="rgba-sample.png",
    )

    assert [item["code"] for item in violations] == ["browser-geometry-low-contrast"]


def test_contrast_sampler_ignores_antialias_outlier_pixels_inside_text_rect():
    image = Image.new("RGB", (140, 80), (26, 26, 26))
    for x in range(68, 73):
        for y in range(38, 43):
            image.putpixel((x, y), (150, 150, 150))
    buffer = BytesIO()
    image.save(buffer, format="PNG")

    violations, telemetry = _contrast_violations(
        [
            {
                "text": "Readable muted copy with antialiasing",
                "visible": True,
                "color": "rgba(255, 255, 255, 0.6)",
                "role": "text",
                "font_size": 16,
                "rect": {"x": 20, "y": 20, "width": 100, "height": 40},
                "selector": "li",
                "slide_index": 1,
            }
        ],
        buffer.getvalue(),
        evidence_image="antialias-sample.png",
    )

    assert violations == []
    assert telemetry == []


def test_contrast_sampler_uses_dominant_background_cluster_over_text_antialias_pixels():
    image = Image.new("RGB", (140, 80), (26, 31, 46))
    antialias_pixels = {
        (22, 40): (173, 179, 189),
        (46, 60): (126, 132, 143),
        (70, 20): (156, 162, 172),
        (94, 20): (115, 120, 132),
        (118, 40): (162, 167, 178),
    }
    for point, color in antialias_pixels.items():
        image.putpixel(point, color)
    buffer = BytesIO()
    image.save(buffer, format="PNG")

    violations, telemetry = _contrast_violations(
        [
            {
                "text": "Small readable copy over a stable dark card",
                "visible": True,
                "color": "rgb(226, 232, 240)",
                "role": "text",
                "font_size": 15,
                "rect": {"x": 10, "y": 10, "width": 120, "height": 60},
                "selector": "p.card-copy",
                "slide_index": 1,
            }
        ],
        buffer.getvalue(),
        evidence_image="dominant-background.png",
    )

    assert violations == []
    assert telemetry == []


def test_contrast_sampler_does_not_choose_foreground_text_cluster_as_background():
    image = Image.new("RGB", (160, 80), (255, 255, 255))
    foreground_points = [
        (80, 40),
        (32, 20),
        (32, 40),
        (32, 60),
        (56, 20),
        (56, 40),
        (56, 60),
        (80, 20),
        (80, 60),
        (104, 20),
        (104, 40),
        (104, 60),
        (128, 40),
    ]
    for point in foreground_points:
        image.putpixel(point, (17, 17, 17))
    buffer = BytesIO()
    image.save(buffer, format="PNG")

    violations, telemetry = _contrast_violations(
        [
            {
                "text": "Readable black headline on white card",
                "visible": True,
                "color": "rgb(17, 17, 17)",
                "role": "title",
                "font_size": 28,
                "rect": {"x": 20, "y": 10, "width": 120, "height": 60},
                "selector": "div.headline",
                "slide_index": 1,
            }
        ],
        buffer.getvalue(),
        evidence_image="foreground-cluster.png",
    )

    assert violations == []
    assert telemetry == []


def test_browser_geometry_qa_flags_contract_independent_hard_failures():
    html = """
    <html>
      <head>
        <style>
          html, body { margin: 0; width: 100%; height: 100%; }
          body { background: #fff; color: #111; font-family: Arial, sans-serif; }
          .slide { position: relative; width: 1600px; height: 900px; overflow: hidden; background: #fff; }
          .bad-title {
            position: absolute;
            left: 72px;
            top: -24px;
            margin: 0;
            font-size: 64px;
            line-height: 1;
          }
          .overflow-copy {
            position: absolute;
            left: 72px;
            top: 160px;
            width: 180px;
            height: 34px;
            overflow: hidden;
            white-space: nowrap;
            font-size: 28px;
          }
          .empty-pill {
            position: absolute;
            left: 72px;
            top: 240px;
            width: 180px;
            height: 42px;
            border-radius: 999px;
            background: #111;
          }
          .bad-command {
            position: absolute;
            left: 72px;
            top: 330px;
            font-size: 32px;
            letter-spacing: -22px;
            font-family: Arial, sans-serif;
          }
          .low-contrast {
            position: absolute;
            left: 72px;
            top: 430px;
            font-size: 36px;
            color: #f9f9f9;
          }
        </style>
      </head>
      <body data-preset="Geometry QA Fixture">
        <section class="slide" data-slide-index="1">
          <h1 class="bad-title" data-geometry-target data-geometry-role="title">Clipped Title</h1>
          <div class="overflow-copy" data-geometry-target data-geometry-role="text">
            This long line should overflow its clipped text box.
          </div>
          <span class="empty-pill" data-geometry-target data-geometry-role="pill"></span>
          <code class="bad-command" data-geometry-target data-geometry-role="command">
            npm install https://github.com/kaisersong/slide-creator
          </code>
          <p class="low-contrast" data-geometry-target data-geometry-role="text">Nearly invisible text</p>
        </section>
      </body>
    </html>
    """

    report = analyze_browser_geometry_html(html, viewports=VIEWPORTS, stable_runs=1)

    assert report["pass"] is False
    assert {
        "browser-geometry-title-clipped",
        "browser-geometry-text-overflow",
        "browser-geometry-empty-component",
        "browser-geometry-character-overlap",
        "browser-geometry-low-contrast",
    }.issubset(set(report["hard_failures"]))
    assert report["diagnostics"]["hard_violation_count"] >= 5
    assert report["violations"][0]["evidence_image"]


def test_browser_geometry_qa_defers_complex_background_contrast_to_contract_policy():
    html = """
    <html>
      <head>
        <style>
          html, body { margin: 0; width: 100%; height: 100%; }
          body {
            background: radial-gradient(circle at 30% 30%, #7c3aed, transparent 35%),
                        radial-gradient(circle at 70% 40%, #06b6d4, transparent 30%),
                        #0b1020;
            font-family: Arial, sans-serif;
          }
          .slide { position: relative; width: 1600px; height: 900px; overflow: hidden; }
          .glass {
            position: absolute;
            left: 120px;
            top: 160px;
            padding: 32px 40px;
            color: #f8fafc;
            font-size: 42px;
            background: rgba(255,255,255,0.12);
            backdrop-filter: blur(18px);
          }
        </style>
      </head>
      <body data-preset="Aurora Mesh">
        <section class="slide" data-slide-index="1">
          <div class="glass" data-geometry-target data-geometry-role="text">
            Composite background text
          </div>
        </section>
      </body>
    </html>
    """

    report = analyze_browser_geometry_html(html, viewports=VIEWPORTS, stable_runs=1)

    assert "browser-geometry-low-contrast" not in report["hard_failures"]
    assert any(item["type"] == "needs_contract_policy" for item in report["telemetry"])


def test_browser_geometry_qa_records_deterministic_runner_metadata():
    html = """
    <html>
      <head>
        <style>
          html, body { margin: 0; width: 100%; height: 100%; }
          .slide { width: 1600px; height: 900px; overflow: hidden; background: #fff; }
          h1 { margin: 80px; font-size: 56px; color: #111; }
        </style>
      </head>
      <body>
        <section class="slide">
          <h1 data-geometry-target data-geometry-role="title">Clean Title</h1>
        </section>
      </body>
    </html>
    """

    report = analyze_browser_geometry_html(html, viewports=VIEWPORTS, stable_runs=1)

    assert report["pass"] is True
    assert report["runner"]["viewports"] == VIEWPORTS
    assert report["runner"]["device_pixel_ratio"] == 1
    assert report["runner"]["stable_runs"] == 1
    assert report["runner"]["fonts_ready"] is True
    assert report["runner"]["animation_frozen"] is True
    assert report["runner"]["layout_settled"] is True


def test_browser_geometry_qa_measures_each_slide_in_viewport_for_horizontal_tracks():
    html = """
    <html>
      <head>
        <style>
          html, body { margin: 0; width: 100%; height: 100%; overflow: hidden; }
          #track {
            display: flex;
            width: 200vw;
            height: 100vh;
            transition: transform 0.2s ease;
          }
          .slide {
            position: relative;
            flex: 0 0 100vw;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            background: #fff;
          }
          h1 { position: absolute; left: 80px; top: 80px; margin: 0; font-size: 56px; color: #111; }
        </style>
      </head>
      <body>
        <main id="track">
          <section class="slide"><h1 data-geometry-target="first" data-geometry-role="title">First</h1></section>
          <section class="slide"><h1 data-geometry-target="second" data-geometry-role="title">Second</h1></section>
        </main>
      </body>
    </html>
    """

    report = analyze_browser_geometry_html(html, viewports=VIEWPORTS, stable_runs=1)

    assert report["pass"] is True
    assert report["diagnostics"]["target_count"] == 2
    measured = {item["qa_id"]: item for item in report["measurements"]}
    assert measured["first"]["rect"]["x"] == 80
    assert measured["second"]["rect"]["x"] == 80
    assert measured["second"]["slide_index"] == 2


def test_browser_geometry_qa_measures_each_slide_in_viewport_for_vertical_scroll_decks():
    html = """
    <html>
      <head>
        <style>
          html, body { margin: 0; width: 100%; min-height: 100%; }
          .slide {
            position: relative;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            background: #fff;
            scroll-snap-align: start;
          }
          h1 { position: absolute; left: 96px; top: 72px; margin: 0; font-size: 52px; color: #111; }
        </style>
      </head>
      <body>
        <section class="slide"><h1 data-geometry-target="first" data-geometry-role="title">First</h1></section>
        <section class="slide"><h1 data-geometry-target="second" data-geometry-role="title">Second</h1></section>
      </body>
    </html>
    """

    report = analyze_browser_geometry_html(html, viewports=VIEWPORTS, stable_runs=1)

    assert report["pass"] is True
    measured = {item["qa_id"]: item for item in report["measurements"]}
    assert measured["first"]["rect"]["y"] == 72
    assert measured["second"]["rect"]["y"] == 72
    assert measured["second"]["slide_index"] == 2


def test_browser_geometry_qa_scrolls_even_when_runtime_controller_reports_success():
    html = """
    <html>
      <head>
        <style>
          html, body { margin: 0; width: 100%; min-height: 100%; }
          .slide { position: relative; width: 100vw; height: 100vh; overflow: hidden; background: #fff; }
          h1 { position: absolute; left: 120px; top: 64px; margin: 0; font-size: 52px; color: #111; }
        </style>
      </head>
      <body>
        <script>
          window.goTo = function (_index) {
            return true;
          };
        </script>
        <section class="slide"><h1 data-geometry-target="first" data-geometry-role="title">First</h1></section>
        <section class="slide"><h1 data-geometry-target="second" data-geometry-role="title">Second</h1></section>
      </body>
    </html>
    """

    report = analyze_browser_geometry_html(html, viewports=VIEWPORTS, stable_runs=1)

    assert report["pass"] is True
    measured = {item["qa_id"]: item for item in report["measurements"]}
    assert measured["second"]["rect"]["y"] == 64


def test_browser_geometry_qa_auto_targets_unmarked_code_block_commands():
    html = """
    <html>
      <head>
        <style>
          html, body { margin: 0; width: 100%; height: 100%; overflow: hidden; }
          .slide { position: relative; width: 1600px; height: 900px; overflow: hidden; background: #101522; }
          .code-block {
            position: absolute;
            left: 160px;
            top: 300px;
            width: 520px;
            color: #ffffff;
            font: 34px/1.2 Arial, sans-serif;
            letter-spacing: -20px;
            white-space: nowrap;
          }
        </style>
      </head>
      <body>
        <section class="slide">
          <div class="code-block">安装 https://github.com/kaisersong/slide-creator</div>
        </section>
      </body>
    </html>
    """

    report = analyze_browser_geometry_html(html, viewports=VIEWPORTS, stable_runs=1)

    command = next((item for item in report["measurements"] if "github.com/kaisersong" in item["text"]), None)
    assert command is not None
    assert command["role"] == "command"
    assert command["character_overlap"] is True
    assert "browser-geometry-character-overlap" in report["hard_failures"]


def test_browser_geometry_qa_flags_compressed_command_letter_spacing():
    html = """
    <html>
      <head>
        <style>
          html, body { margin: 0; width: 100%; height: 100%; overflow: hidden; }
          .slide { position: relative; width: 1600px; height: 900px; overflow: hidden; background: #101522; }
          .code-block {
            position: absolute;
            left: 437px;
            top: 546px;
            width: 351px;
            color: #ffffff;
            font: 14.4px/1.42 Arial, sans-serif;
            letter-spacing: -2.88px;
            white-space: normal;
            overflow-wrap: anywhere;
          }
        </style>
      </head>
      <body>
        <section class="slide">
          <div class="code-block">安装 https://github.com/kaisersong/slide-creator</div>
        </section>
      </body>
    </html>
    """

    report = analyze_browser_geometry_html(html, viewports=VIEWPORTS, stable_runs=1)

    command = next((item for item in report["measurements"] if "github.com/kaisersong" in item["text"]), None)
    assert command is not None
    assert command["letter_spacing"] == -2.88
    assert command["character_overlap"] is True
    assert "browser-geometry-character-overlap" in report["hard_failures"]
