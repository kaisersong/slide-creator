#!/usr/bin/env python3
"""
Compatibility wrapper for the canonical HTML validator.

Preferred entrypoint:
    python scripts/validate_html.py deck.html --strict

Legacy entrypoint kept for compatibility:
    python tests/validate.py deck.html --strict
"""

from __future__ import annotations

import sys
from pathlib import Path


def _discover_root() -> Path:
    file_value = globals().get("__file__")
    if file_value:
        return Path(file_value).resolve().parent.parent

    cwd = Path.cwd().resolve()
    candidates = [cwd, *cwd.parents]
    required = (
        ("scripts", "validate_html.py"),
        ("scripts", "title_profiles.py"),
        ("references", "html-template.md"),
    )
    for candidate in candidates:
        if all((candidate / folder / leaf).exists() for folder, leaf in required):
            return candidate
    return cwd


ROOT = _discover_root()
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from validate_html import *  # noqa: F401,F403,E402


if __name__ == "__main__":
    main()
