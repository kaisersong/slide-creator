"""
Regression tests for scripts/generate.py component rendering.

Catches the bugs that caused P2/P4/P5/P7 to render poorly:
- .g .warn/.green modifiers not parsed (plain bullets instead of colored borders)
- .g .theme cards not rendered (plain bullets instead of theme showcase chips)
- stat KPI cards not detected (no .stat gradient)
- consecutive block elements no gap (capsules stuck together)
- double style attribute on <h4> (browser ignores second style)
- f-string syntax errors with backslash in join

Run: python -m pytest tests/test_generate_rendering.py -v
"""

import re
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts/ to path
SCRIPTS = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from generate import (
    parse_planning,
    _render_children,
    _render_col_child,
    _render_body,
    _looks_stat,
)


def _parse_markdown(markdown):
    """Parse markdown string (not file) by writing to temp file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown)
        f.flush()
        return parse_planning(f.name)


# ─── Parser tests ───────────────────────────────────────────────────────────

class TestModifierParsing:
    """Component modifier parsing: single and multiple modifiers."""

    def test_single_modifier(self):
        """'.g .warn: text' → component='g', modifiers=['warn']"""
        markdown = (
            "**Slide 1 | Test**\n"
            "- .g .warn: Error message\n"
            "  - Detail 1\n"
        )
        slides = _parse_markdown(markdown)
        assert len(slides) == 1
        tree = slides[0]["tree"]
        g_item = tree[0]
        assert g_item["component"] == "g"
        assert g_item["modifiers"] == ["warn"]
        assert g_item["text"] == "Error message"

    def test_multiple_modifiers(self):
        """'.g .theme .highlight: text' → component='g', modifiers=['theme', 'highlight']"""
        markdown = (
            "**Slide 1 | Test**\n"
            "- .g .theme .highlight: 浅色 · 5 个主题\n"
            "  - Blue Sky ★ 本演示\n"
            "  - Notebook Tabs\n"
        )
        slides = _parse_markdown(markdown)
        tree = slides[0]["tree"]
        g_item = tree[0]
        assert g_item["component"] == "g"
        assert g_item["modifiers"] == ["theme", "highlight"]

    def test_bare_component(self):
        """'.cols4' with no text → component='cols4', text=''"""
        markdown = (
            "**Slide 1 | Test**\n"
            "- .cols4\n"
        )
        slides = _parse_markdown(markdown)
        tree = slides[0]["tree"]
        assert tree[0]["component"] == "cols4"
        assert tree[0]["text"] == ""


# ─── Stat detection tests ──────────────────────────────────────────────────

class TestStatDetection:
    """Stat KPI card detection: single-char number + bullet child."""

    def test_single_digit_is_stat(self):
        assert _looks_stat({"text": "0", "component": None}) is True
        assert _looks_stat({"text": "3", "component": None}) is True

    def test_single_char_is_stat(self):
        assert _looks_stat({"text": "∞", "component": None}) is True

    def test_long_text_not_stat(self):
        assert _looks_stat({"text": "123", "component": None}) is False
        assert _looks_stat({"text": "npm 包", "component": None}) is False

    def test_chinese_not_stat(self):
        assert _looks_stat({"text": "一", "component": None}) is False
        assert _looks_stat({"text": "主题", "component": None}) is False

    def test_punctuation_not_stat(self):
        assert _looks_stat({"text": "。", "component": None}) is False
        assert _looks_stat({"text": "！", "component": None}) is False


# ─── .g card rendering tests ────────────────────────────────────────────────

class TestGCardRendering:
    """Glass card rendering with modifiers."""

    def _make_g(self, text, modifiers=None, children=None):
        return {
            "component": "g",
            "modifiers": modifiers or [],
            "text": text,
            "children": children or [],
        }

    def _make_child(self, text, component=None):
        return {
            "component": component,
            "modifiers": [],
            "text": text,
            "children": [],
        }

    def test_warn_card_has_red_border(self):
        card = self._make_g(
            "传统方法",
            modifiers=["warn"],
            children=[
                self._make_child("从空白开始"),
                self._make_child("调整字体"),
            ]
        )
        html = _render_col_child(card)
        assert "border-left:4px solid #ef4444" in html
        assert "color:#b91c1c" in html

    def test_green_card_has_green_border(self):
        card = self._make_g(
            "slide-creator",
            modifiers=["green"],
            children=[self._make_child("描述你的主题")]
        )
        html = _render_col_child(card)
        assert "border-left:4px solid #10b981" in html
        assert "color:#065f46" in html

    def test_plain_g_card_no_border(self):
        card = self._make_g(
            "导航快捷键",
            modifiers=[],
            children=[self._make_child("→ 下一个")]
        )
        html = _render_col_child(card)
        assert "border-left" not in html

    def test_theme_card_has_colored_dot(self):
        card = self._make_g(
            "深色 · 4 个主题",
            modifiers=["theme"],
            children=[
                self._make_child("Bold Signal"),
                self._make_child("Electric Studio"),
                self._make_child("演讲 · 品牌 · 技术分享"),
            ]
        )
        html = _render_col_child(card)
        # Dark category → black dot
        assert "background:#0f172a" in html
        # Should NOT have bullet list
        assert "<ul" not in html
        assert "<li>" not in html
        # Should have chip-style theme names
        assert "Bold Signal" in html
        assert "border-radius:6px" in html
        # Should have footer
        assert "演讲" in html

    def test_theme_highlight_card_has_blue_border(self):
        card = self._make_g(
            "浅色 · 5 个主题",
            modifiers=["theme", "highlight"],
            children=[
                self._make_child("Blue Sky ★ 本演示"),
                self._make_child("Notebook Tabs"),
                self._make_child("教育 · 内部 · 创意"),
            ]
        )
        html = _render_col_child(card)
        assert "border:1px solid rgba(37,99,235,0.25)" in html
        assert "linear-gradient(135deg,#2563eb,#0ea5e9)" in html
        # Blue Sky should have 本演示 pill
        assert "本演示" in html
        assert "pill green" in html
        # ★ should be stripped from name
        assert "★" not in html

    def test_theme_card_no_double_style(self):
        """Theme cards must not have duplicate style attributes."""
        card = self._make_g(
            "v1.5 新增 · 8 个主题",
            modifiers=["theme", "highlight"],
            children=[
                self._make_child("Aurora Mesh"),
                self._make_child("Enterprise Dark"),
                self._make_child("高级 · 数据 · 创意"),
            ]
        )
        html = _render_col_child(card)
        g_match = re.search(r'<div class="g"[^>]*>', html)
        assert g_match, "Missing .g card outer div"
        g_tag = g_match.group()
        assert g_tag.count("style=") == 1, f"Double style attribute in: {g_tag}"

    def test_stat_card_has_stat_class(self):
        card = self._make_g(
            "0",
            modifiers=[],
            children=[
                self._make_child("npm 包 — 纯 HTML/CSS/JS"),
            ]
        )
        html = _render_col_child(card)
        assert '<div class="stat">0</div>' in html
        assert "text-align:center" in html

    def test_warn_card_title_color_merged(self):
        """warn card <h4> style must merge color + margin-bottom into ONE style attr."""
        card = self._make_g(
            "标题",
            modifiers=["warn"],
            children=[self._make_child("内容")]
        )
        html = _render_col_child(card)
        h4_matches = re.findall(r'<h4 style="[^"]*"[^>]*>', html)
        assert len(h4_matches) == 1, f"Expected 1 <h4>, got {len(h4_matches)}"
        h4_tag = h4_matches[0]
        assert h4_tag.count("style=") == 1
        assert "color:#b91c1c" in h4_tag
        assert "margin-bottom:10px" in h4_tag


# ─── Block element gap tests ───────────────────────────────────────────────

class TestBlockGap:
    """Consecutive block elements must be wrapped in flex column with gap."""

    def test_cols2_plus_info_has_gap(self):
        """P2 style: .cols2 followed by .info → gap wrapper."""
        markdown = (
            "**Slide 1 | Test**\n"
            "- Title: Test\n"
            "- .cols2\n"
            "  - .g .warn: Left\n"
            "    - item1\n"
            "  - .g .green: Right\n"
            "    - item2\n"
            "- .info: Design principle\n"
        )
        slides = _parse_markdown(markdown)
        tree = slides[0]["tree"]
        body_items = tree[1:] if tree and tree[0]["component"] is None else tree
        body = _render_body(body_items)
        assert "display:flex;flex-direction:column;gap:14px;" in body

    def test_cols3_plus_cols2_has_gap(self):
        """P7 style: .cols3 stat row + .cols2 callouts → gap wrapper."""
        markdown = (
            "**Slide 1 | Test**\n"
            "- Title: Test\n"
            "- .cols3\n"
            "  - .g: 0\n"
            "    - desc1\n"
            "  - .g: 3\n"
            "    - desc2\n"
            "  - .g: ∞\n"
            "    - desc3\n"
            "- .cols2\n"
            "  - .co: callout 1\n"
            "  - .info: info 2\n"
        )
        slides = _parse_markdown(markdown)
        tree = slides[0]["tree"]
        body_items = tree[1:] if tree and tree[0]["component"] is None else tree
        body = _render_body(body_items)
        assert "display:flex;flex-direction:column;gap:14px;" in body

    def test_single_col_no_extra_gap_wrapper(self):
        """A single .cols2 alone should NOT be wrapped in an extra gap div."""
        markdown = (
            "**Slide 1 | Test**\n"
            "- Title: Test\n"
            "- .cols2\n"
            "  - .g: Left\n"
            "    - item\n"
            "  - .g: Right\n"
            "    - item\n"
        )
        slides = _parse_markdown(markdown)
        tree = slides[0]["tree"]
        body_items = tree[1:] if tree and tree[0]["component"] is None else tree
        body = _render_body(body_items)
        assert '<div class="cols2">' in body
        assert "display:flex;flex-direction:column;gap:14px;" not in body

    def test_layers_have_own_gap(self):
        """Consecutive .layer elements should be wrapped in gap:11px."""
        markdown = (
            "**Slide 1 | Test**\n"
            "- Title: Test\n"
            "- .layer 1: Step one\n"
            "  - detail 1\n"
            "- .layer 2: Step two\n"
            "  - detail 2\n"
        )
        slides = _parse_markdown(markdown)
        tree = slides[0]["tree"]
        body_items = tree[1:] if tree and tree[0]["component"] is None else tree
        body = _render_body(body_items)
        assert "display:flex;flex-direction:column;gap:11px;" in body


# ─── Integration: full generation from PLANNING.md ─────────────────────────

class TestFullGeneration:
    """End-to-end: generate from PLANNING.md and verify output quality."""

    DEMOS = Path(__file__).parent.parent / "demos"

    def test_blue_sky_zh_exists(self):
        assert (self.DEMOS / "blue-sky-zh.html").exists()

    def test_no_double_style_attributes(self):
        """No element should have duplicate style="..." style="..." attributes."""
        content = (self.DEMOS / "blue-sky-zh.html").read_text(encoding="utf-8")
        bad = re.findall(r'<\w+[^>]*style="[^"]*"[^>]*style="', content)
        assert len(bad) == 0, f"Elements with double style attribute: {len(bad)}"

    def test_theme_cards_render_not_bullets(self):
        """P4 theme cards must use chip-style rendering, not bullet lists."""
        content = (self.DEMOS / "blue-sky-zh.html").read_text(encoding="utf-8")
        p4_match = re.search(r'04 — 21 个主题.*?</section>', content, re.DOTALL)
        assert p4_match, "P4 slide not found"
        p4_html = p4_match.group()
        assert "border-radius:6px" in p4_html
        assert "display:flex;flex-direction:column;gap:5px;" in p4_html
        g_cards = re.findall(r'<div class="g"[^>]*>(.*?)</div>\s*</div>\s*<p', p4_html, re.DOTALL)
        for card in g_cards:
            if "演讲" in card or "教育" in card or "开发" in card or "高级" in card:
                assert "<ul" not in card, f"Theme card rendered as bullet list: {card[:100]}"

    def test_p2_warn_green_cards(self):
        """P2 must have red/green bordered comparison cards."""
        content = (self.DEMOS / "blue-sky-zh.html").read_text(encoding="utf-8")
        p2_match = re.search(r'02 — 传统工具.*?</section>', content, re.DOTALL)
        assert p2_match, "P2 slide not found"
        p2_html = p2_match.group()
        assert "border-left:4px solid #ef4444" in p2_html
        assert "border-left:4px solid #10b981" in p2_html

    def test_stat_kpi_cards(self):
        """P7 must have stat KPI cards with .stat class."""
        content = (self.DEMOS / "blue-sky-zh.html").read_text(encoding="utf-8")
        assert '<div class="stat">0</div>' in content
        assert '<div class="stat">3</div>' in content
        assert '<div class="stat">∞</div>' in content

    def test_no_u_fe0f_variant_selector(self):
        """HTML must not contain U+FE0F variant selector (impeccable anti-pattern)."""
        content = (self.DEMOS / "blue-sky-zh.html").read_text(encoding="utf-8")
        fe0f_positions = [i for i, c in enumerate(content) if ord(c) == 0xFE0F]
        assert len(fe0f_positions) == 0, f"Found {len(fe0f_positions)} U+FE0F variant selectors"
