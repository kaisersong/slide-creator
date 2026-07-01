from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from ai_advised_eval import analyze_ai_advised_html  # noqa: E402


def test_ai_advised_eval_passes_assertive_varied_deck():
    html = """
    <main>
      <section class="slide" aria-label="cover" data-export-role="cover" data-visual-signature="a-cover">
        <h1>发布路径先收敛到可验证交付</h1>
        <p>产品发布需要先锁定目标用户、核心承诺和验证口径。</p>
      </section>
      <section class="slide" aria-label="problem" data-export-role="problem" data-visual-signature="a-problem">
        <h2>分散需求会拖慢团队响应</h2>
        <p>销售、交付和研发使用不同描述，导致优先级反复变化，客户反馈也无法闭环。</p>
      </section>
      <section class="slide" aria-label="workflow" data-export-role="workflow" data-visual-signature="a-flow">
        <h2>统一入口让计划、执行、复盘连续</h2>
        <ul>
          <li>先收集高频场景</li>
          <li>再拆成发布批次</li>
          <li>最后用数据复盘</li>
        </ul>
      </section>
      <section class="slide" aria-label="evidence" data-export-role="metrics" data-visual-signature="a-metric">
        <h2>三项指标证明发布节奏变稳</h2>
        <p>响应时间下降 32%，重复沟通减少 41%，关键客户续费风险提前两周暴露。</p>
      </section>
    </main>
    """

    report = analyze_ai_advised_html(html, preset="Aurora Mesh")

    assert report["pass"] is True
    assert report["hard_failures"] == []
    assert report["diagnostics"]["max_visual_signature_run"] == 1


def test_ai_advised_eval_flags_generic_repeated_deck():
    html = """
    <main>
      <section class="slide" aria-label="intro" data-export-role="title" data-visual-signature="same">
        <h1>Overview</h1><p>Brief text.</p>
      </section>
      <section class="slide" aria-label="content" data-export-role="content" data-visual-signature="same">
        <h2>Overview</h2><p>Brief text.</p>
      </section>
      <section class="slide" aria-label="content" data-export-role="content" data-visual-signature="same">
        <h2>Overview</h2><p>Brief text.</p>
      </section>
      <section class="slide" aria-label="content" data-export-role="content" data-visual-signature="same">
        <h2>Overview</h2><p>Brief text.</p>
      </section>
    </main>
    """

    report = analyze_ai_advised_html(html, preset="Bold Signal")

    assert report["pass"] is False
    assert "ai-advised-generic-title" in report["hard_failures"]
    assert "ai-advised-repeated-title" in report["hard_failures"]
    assert "ai-advised-repeated-visual-signature" in report["hard_failures"]
    assert "ai-advised-shallow-content" in report["hard_failures"]


def test_ai_advised_eval_flags_unsupported_title_body_relationship():
    html = """
    <main>
      <section class="slide" aria-label="problem" data-export-role="problem" data-visual-signature="p1">
        <h2>渠道效率必须先被量化</h2>
        <p>Apple banana cloud window river music coffee garden paper mountain.</p>
      </section>
      <section class="slide" aria-label="workflow" data-export-role="workflow" data-visual-signature="p2">
        <h2>复盘机制决定发布速度</h2>
        <p>Orange mirror candle highway planet notebook violin summer ocean fabric.</p>
      </section>
      <section class="slide" aria-label="evidence" data-export-role="metrics" data-visual-signature="p3">
        <h2>客户风险需要提前暴露</h2>
        <p>Table forest camera library airport velvet mineral compass bicycle radio.</p>
      </section>
    </main>
    """

    report = analyze_ai_advised_html(html, preset="Strategy Consulting")

    assert report["pass"] is False
    assert "ai-advised-title-support-low" in report["hard_failures"]
