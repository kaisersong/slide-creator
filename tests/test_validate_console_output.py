from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
VALIDATE_PY = ROOT / "tests" / "validate.py"


def load_validate_module():
    spec = importlib.util.spec_from_file_location("validate_module", VALIDATE_PY)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_validate_uses_ascii_fallback_for_gbk_terminals():
    validate = load_validate_module()

    assert validate.render_console_symbol("✓", "OK", encoding="gbk") == "OK"
    assert validate.render_console_symbol("✗", "FAIL", encoding="gbk") == "FAIL"
    assert validate.render_console_symbol("⚠", "WARN", encoding="gbk") == "WARN"


def test_validate_keeps_unicode_symbols_on_utf8_terminals():
    validate = load_validate_module()

    assert validate.render_console_symbol("✓", "OK", encoding="utf-8") == "✓"
