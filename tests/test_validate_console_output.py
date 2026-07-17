from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
VALIDATE_PY = ROOT / "tests" / "validate.py"
VALIDATE_HTML_PY = ROOT / "scripts" / "validate_html.py"


def load_validate_module():
    spec = importlib.util.spec_from_file_location("validate_module", VALIDATE_PY)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_validate_html_module():
    spec = importlib.util.spec_from_file_location("validate_html_module", VALIDATE_HTML_PY)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_skill_version_supports_source_and_packaged_layouts(tmp_path: Path, monkeypatch):
    validate_html = load_validate_html_module()

    plugin_root = tmp_path / "plugin-layout"
    plugin_root.mkdir()
    (plugin_root / "plugin.json").write_text(
        '{"version": " 3.2.1 "}',
        encoding="utf-8",
    )

    nested_root = tmp_path / "nested-skill-layout"
    nested_skill = nested_root / "skills" / "slide-planner" / "SKILL.md"
    nested_skill.parent.mkdir(parents=True)
    nested_skill.write_text("---\nversion: 3.2.0\n---\n", encoding="utf-8")

    root_skill_root = tmp_path / "root-skill-layout"
    root_skill_root.mkdir()
    (root_skill_root / "SKILL.md").write_text(
        "---\nversion: 3.1.9\n---\n",
        encoding="utf-8",
    )

    invalid_plugin_root = tmp_path / "invalid-plugin-layout"
    invalid_plugin_nested_skill = invalid_plugin_root / "skills" / "slide-planner" / "SKILL.md"
    invalid_plugin_nested_skill.parent.mkdir(parents=True)
    (invalid_plugin_root / "plugin.json").write_text("{not-json", encoding="utf-8")
    invalid_plugin_nested_skill.write_text("---\nversion: 3.1.8\n---\n", encoding="utf-8")

    for candidate_root, expected in (
        (plugin_root, "3.2.1"),
        (nested_root, "3.2.0"),
        (root_skill_root, "3.1.9"),
        (invalid_plugin_root, "3.1.8"),
    ):
        monkeypatch.setattr(validate_html, "ROOT", candidate_root)
        assert validate_html._skill_version() == expected


def test_validate_uses_ascii_fallback_for_gbk_terminals():
    validate = load_validate_module()

    assert validate.render_console_symbol("✓", "OK", encoding="gbk") == "OK"
    assert validate.render_console_symbol("✗", "FAIL", encoding="gbk") == "FAIL"
    assert validate.render_console_symbol("⚠", "WARN", encoding="gbk") == "WARN"


def test_validate_keeps_unicode_symbols_on_utf8_terminals():
    validate = load_validate_module()

    assert validate.render_console_symbol("✓", "OK", encoding="utf-8") == "✓"


def test_validate_module_executes_without___file___when_cwd_is_repo_root(monkeypatch):
    monkeypatch.chdir(ROOT)
    source = VALIDATE_PY.read_text(encoding="utf-8")
    namespace = {"__name__": "validate_module_exec"}

    exec(compile(source, str(VALIDATE_PY), "exec"), namespace)

    assert namespace["ROOT"] == ROOT
    assert namespace["SCRIPTS_DIR"] == ROOT / "scripts"
