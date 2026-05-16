from __future__ import annotations

import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
THEMES_DIR = ROOT / "themes"
CUSTOM_THEMES = ["kingdee", "cloudhub"]
CDN_PREFIX = "https://static.yunzhijia.com/home/download/png/"

pytestmark = pytest.mark.skipif(
    not all((THEMES_DIR / theme).exists() for theme in CUSTOM_THEMES),
    reason="private custom themes are not present in this checkout",
)


def read_theme_file(theme: str, name: str) -> str:
    return (THEMES_DIR / theme / name).read_text(encoding="utf-8")


def existing_theme_text_files(theme: str, names: tuple[str, ...]) -> list[str]:
    return [name for name in names if (THEMES_DIR / theme / name).exists()]


def extract_style(html: str) -> str:
    match = re.search(r"<style>(.*?)</style>", html, re.DOTALL)
    assert match, "starter.html must contain a <style> block"
    return match.group(1)


def test_custom_theme_starters_have_balanced_css_blocks():
    for theme in CUSTOM_THEMES:
        style = extract_style(read_theme_file(theme, "starter.html"))
        assert style.count("{") == style.count("}"), f"{theme} starter CSS braces are unbalanced"


def test_custom_theme_starters_end_with_single_html_document():
    for theme in CUSTOM_THEMES:
        text = read_theme_file(theme, "starter.html").strip()
        assert text.endswith("</html>"), f"{theme} starter has trailing content after </html>"
        assert text.count("</body>") == 1
        assert text.count("</html>") == 1
        assert text.rfind("</body>") < text.rfind("</html>")


def test_custom_theme_assets_use_static_yunzhijia_cdn_not_kingdee_pages_host():
    for theme in CUSTOM_THEMES:
        for filename in ("reference.md", "starter.html"):
            text = read_theme_file(theme, filename)
            assert "kingdee-cdn.pages.dev" not in text
            assert CDN_PREFIX in text


def test_custom_theme_references_use_current_kingdee_background_names():
    legacy_name = re.compile(r"(?<![A-Za-z0-9_-])(catalogue|chapter)\.png")
    for theme in CUSTOM_THEMES:
        for filename in existing_theme_text_files(theme, ("reference.md", "assets/README.md")):
            text = read_theme_file(theme, filename)
            assert not legacy_name.search(text), f"{theme}/{filename} uses legacy background asset names"
            assert "kingdee_catalogue.png" in text
            assert "kingdee_chapter.png" in text
