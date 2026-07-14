from __future__ import annotations

import importlib.util
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
VALIDATE_PY = ROOT / "tests" / "validate.py"


def load_validate_module():
    spec = importlib.util.spec_from_file_location("validate_module", VALIDATE_PY)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_title_balance_accepts_balanced_three_line_title():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <body data-preset="Swiss Modern">
        <section class="slide title_grid" id="slide-1">
          <div class="slide-content">
            <h1 class="swiss-title title-balance">
              <span class="title-line">越早把 AI 做成内核</span>
              <span class="title-line">越早锁定</span>
              <span class="title-line">下一轮壁垒</span>
            </h1>
          </div>
        </section>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_title_balance(soup, html, [])

    assert ok
    assert "Title balance OK" in message


def test_title_balance_rejects_orphan_line():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <body data-preset="Swiss Modern">
        <section class="slide title_grid" id="slide-1">
          <div class="slide-content">
            <h1 class="swiss-title title-balance">
              <span class="title-line">越早把 AI 做成</span>
              <span class="title-line">内</span>
              <span class="title-line">核并锁定壁垒</span>
            </h1>
          </div>
        </section>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_title_balance(soup, html, [])

    assert not ok
    assert "orphan line" in message


def test_title_balance_rejects_collapsed_middle_line():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <body data-preset="Modern Newspaper">
        <section class="slide cover" id="slide-1">
          <div class="slide-content">
            <h1 class="np-headline title-balance">
              <span class="title-line">重新定义产业竞争的边界</span>
              <span class="title-line">与</span>
              <span class="title-line">下一轮增长的锁定方式</span>
            </h1>
          </div>
        </section>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_title_balance(soup, html, [])

    assert not ok
    assert (
        "collapsed middle line" in message
        or "unbalanced title lines" in message
        or "orphan line" in message
    )


def test_title_balance_rejects_semantic_cjk_breaks():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <body data-preset="Blue Sky">
        <section class="slide" id="slide-1">
          <h2 class="gt title-balance">
            <span class="title-line">我们正站在一个『</span>
            <span class="title-line">背水一战』的时刻</span>
          </h2>
        </section>
        <section class="slide" id="slide-2">
          <h2 class="gt title-balance">
            <span class="title-line">哲学 7.0 的升</span>
            <span class="title-line">级：把『辩证性』</span>
            <span class="title-line">写进客户哲学</span>
          </h2>
        </section>
        <section class="slide" id="slide-3">
          <h2 class="gt title-balance">
            <span class="title-line">生态哲学升级:智</span>
            <span class="title-line">能共生，不走邪道</span>
          </h2>
        </section>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_title_balance(soup, html, [])

    assert not ok
    assert "dangling opening punctuation" in message


def test_title_balance_rejects_common_cjk_word_splits():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <body data-preset="Blue Sky">
        <section class="slide" id="slide-1">
          <h2 class="gt title-balance">
            <span class="title-line">落地路线从低风</span>
            <span class="title-line">险真实场景开始</span>
          </h2>
        </section>
        <section class="slide" id="slide-2">
          <h2 class="gt title-balance">
            <span class="title-line">最终输出是一张授权地</span>
            <span class="title-line">图，而不是宣传等级</span>
          </h2>
        </section>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_title_balance(soup, html, [])

    assert not ok
    assert "bad CJK word split '风险'" in message
    assert "bad CJK word split '地图'" in message


def test_title_balance_rejects_long_display_title_that_relies_on_auto_wrap():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <body data-preset="Swiss Modern">
        <section class="slide pull_quote" id="slide-1">
          <div class="slide-content" style="padding-top:18vh;">
            <h2 class="swiss-title" style="max-width:14ch;">越早把 AI 做成内核越早锁定下一轮壁垒</h2>
          </div>
        </section>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_title_balance(soup, html, [])

    assert not ok
    assert "relies on auto-wrap" in message


def test_title_balance_accepts_explicit_profile_fit_auto_wrap_strategy():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <body data-preset="Bold Signal">
        <section class="slide cover" id="slide-1">
          <div class="slide-content">
            <h2 class="title-balance profile-fit-title" style="max-width:14ch;">用同一把尺子比较速度、质量与返工</h2>
          </div>
        </section>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_title_balance(soup, html, [])

    assert ok, message


def test_title_balance_skips_vertical_and_glitch_title_profiles():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <body data-preset="Chinese Chan">
        <section class="slide zen_vertical" id="slide-1">
          <div class="zen-vertical-title zen-cn">竖排标题</div>
        </section>
        <section class="slide" id="slide-2">
          <h1 class="cyber-title" data-text="signal lockup">signal lockup</h1>
        </section>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_title_balance(soup, html, [])

    assert ok
    assert "Title balance OK" in message


def test_title_balance_skips_split_lockup_and_terminal_object_profiles():
    validate = load_validate_module()
    html = """
    <!DOCTYPE html>
    <html>
      <body data-preset="Creative Voltage">
        <section class="slide halftone" id="slide-1">
          <div class="cover-inner">
            <div class="main-title">slide-</div>
            <div class="title-accent">creator</div>
          </div>
        </section>
        <section class="slide" id="slide-2">
          <div class="feature-title">&gt; VIEWPORT_FIT</div>
        </section>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    ok, message = validate.check_title_balance(soup, html, [])

    assert ok
    assert "Title balance OK" in message
