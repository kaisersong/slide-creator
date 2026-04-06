from pathlib import Path
import re

from bs4 import BeautifulSoup


ROOT = Path(__file__).parent.parent
MODE_PATHS = ROOT / "demos" / "mode-paths"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def soup(path: Path) -> BeautifulSoup:
    return BeautifulSoup(read(path), "html.parser")


def extract_preset(path: Path) -> str:
    match = re.search(r"^\*\*Preset\*\*:\s*(.+)$", read(path), re.MULTILINE)
    assert match, f"Missing preset in {path.name}"
    return match.group(1).strip()


def extract_root_var(path: Path, name: str) -> str:
    match = re.search(rf"{re.escape(name)}:\s*([^;]+);", read(path))
    assert match, f"Missing {name} in {path.name}"
    return match.group(1).strip()


def extract_actual_timing_fields(path: Path) -> list[str]:
    content = read(path)
    match = re.search(r"\*\*Actual\*\*:(.*?)(?:\n## |\Z)", content, re.DOTALL)
    assert match, f"Missing actual timing block in {path.name}"
    block = match.group(1)
    return re.findall(r"`(plan|generate|validate|polish|total)`", block)


AUTO_PLAN = MODE_PATHS / "intent-broker-auto-PLANNING.md"
POLISH_PLAN = MODE_PATHS / "intent-broker-polish-PLANNING.md"
AUTO_HTML = MODE_PATHS / "intent-broker-auto.html"
POLISH_HTML = MODE_PATHS / "intent-broker-polish.html"


class TestIntentBrokerModePaths:
    def test_planning_files_share_same_preset(self):
        auto_preset = extract_preset(AUTO_PLAN)
        polish_preset = extract_preset(POLISH_PLAN)
        assert auto_preset == polish_preset == "Enterprise Dark"

    def test_generated_html_embeds_preset_metadata(self):
        auto = soup(AUTO_HTML)
        polish = soup(POLISH_HTML)

        assert auto.body["data-preset"] == extract_preset(AUTO_PLAN)
        assert polish.body["data-preset"] == extract_preset(POLISH_PLAN)

    def test_planning_files_record_segmented_actual_timing(self):
        expected = ["plan", "generate", "validate", "polish", "total"]
        assert extract_actual_timing_fields(AUTO_PLAN) == expected
        assert extract_actual_timing_fields(POLISH_PLAN) == expected

    def test_titles_do_not_use_overly_narrow_global_measure(self):
        for path in (AUTO_HTML, POLISH_HTML):
            content = read(path)
            assert "max-width: 10ch" not in content, f"{path.name} still caps h1 at 10ch"
            assert "max-width: 14ch" not in content, f"{path.name} still caps h2 at 14ch"

    def test_titles_stay_brief_enough_for_clean_single_slide_layouts(self):
        for path in (AUTO_HTML, POLISH_HTML):
            headings = [
                el.get_text(" ", strip=True)
                for el in soup(path).select("section.slide h2")
            ]
            longest = max(len(text) for text in headings)
            assert longest <= 24, f"{path.name} has an overlong slide title ({longest} chars)"

    def test_half_width_state_cards_do_not_use_five_column_timelines(self):
        for path in (AUTO_HTML, POLISH_HTML):
            assert "grid-template-columns: repeat(5, minmax(0, 1fr));" not in read(path), (
                f"{path.name} still uses a 5-column timeline inside a constrained card"
            )
