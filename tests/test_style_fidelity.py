"""Thin test wrapper around the skill's own style fidelity checker.

The canonical implementation lives in the skill package:
    ~/.claude/skills/slide-creator/scripts/check_style_fidelity.py

This file only imports and runs it under pytest for CI regression.
"""
import subprocess
import sys
from pathlib import Path
import pytest

DEMOS_DIR = Path(__file__).parent.parent / "demos"
CHECKER = Path.home() / ".claude" / "skills" / "slide-creator" / "scripts" / "check_style_fidelity.py"

ALL_DEMOS = sorted(DEMOS_DIR.glob("*.html"))


def preset_from_path(path: Path) -> str:
    name = path.stem
    parts = name.rsplit("-", 1)
    if len(parts) == 2 and parts[1] in ("en", "zh"):
        return parts[0]
    return name


@pytest.mark.skipif(not CHECKER.exists(), reason="Skill package not installed")
class TestStyleFidelity:
    """Run the skill's own style fidelity checker against all demos."""

    @pytest.fixture(params=ALL_DEMOS, ids=lambda p: p.name)
    def demo(self, request):
        return request.param

    def test_style_fidelity(self, demo):
        """Demo must pass the skill's style fidelity checks (bg, accent, font)."""
        result = subprocess.run(
            [sys.executable, str(CHECKER), str(demo)],
            capture_output=True, text=True
        )
        assert result.returncode == 0, (
            f"{demo.name} failed style fidelity:\n{result.stdout}"
        )
