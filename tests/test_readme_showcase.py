import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
READMES = (ROOT / "README.md", ROOT / "README.zh-CN.md")
SCREENSHOT_RE = re.compile(r'src="(demos/screenshots/[^"?]+\.png)"')


def _screenshot_refs(readme: Path) -> list[str]:
    return SCREENSHOT_RE.findall(readme.read_text(encoding="utf-8"))


def test_fantasy_rainbow_has_one_preview_per_readme_and_live_demo_files():
    expected_links = {
        "README.md": "demos/fantasy-rainbow-en.html",
        "README.zh-CN.md": "demos/fantasy-rainbow-zh.html",
    }

    for readme in READMES:
        text = readme.read_text(encoding="utf-8")
        assert text.count('src="demos/screenshots/fantasy-rainbow.png"') == 1
        assert text.count(expected_links[readme.name]) == 1

    assert (ROOT / "demos/fantasy-rainbow-en.html").is_file()
    assert (ROOT / "demos/fantasy-rainbow-zh.html").is_file()


def test_each_readme_references_each_showcase_screenshot_once():
    for readme in READMES:
        refs = _screenshot_refs(readme)
        assert len(refs) == len(set(refs)), f"duplicate screenshot references in {readme.name}"


def test_showcase_screenshot_assets_are_complete_non_orphaned_and_unique():
    english_refs = set(_screenshot_refs(ROOT / "README.md"))
    chinese_refs = set(_screenshot_refs(ROOT / "README.zh-CN.md"))
    tracked_assets = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "demos/screenshots").glob("*.png")
    }

    assert english_refs == chinese_refs
    assert tracked_assets == english_refs

    hashes: dict[str, str] = {}
    for relative_path in sorted(tracked_assets):
        digest = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert digest not in hashes, (
            f"duplicate screenshot content: {relative_path} and {hashes[digest]}"
        )
        hashes[digest] = relative_path
