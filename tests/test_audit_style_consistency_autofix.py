from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "tests" / "audit_style_consistency.py"

spec = importlib.util.spec_from_file_location("audit_style_consistency", MODULE_PATH)
audit = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(audit)


def test_apply_fix_adds_allowed_components_when_missing():
    content = """
## Components

.foo {
  color: red;
}

.bar {
  color: blue;
}

## Signature Elements

### Required CSS Classes
- `.foo`: already documented

### Background Rule
- Plain background
""".lstrip()

    fixed = audit.apply_fix_to_content(content)

    assert "### Allowed Components" in fixed
    assert "- Audit coverage: .bar" in fixed
    assert audit.find_missing_classes(fixed) == []


def test_apply_fix_preserves_existing_allowed_components_and_is_idempotent():
    content = """
## Components

.foo {
  color: red;
}

.bar {
  color: blue;
}

.baz {
  color: green;
}

## Signature Elements

### Required CSS Classes
- `.foo`: already documented

### Allowed Components
- Existing group: `.bar`

### Background Rule
- Plain background
""".lstrip()

    fixed_once = audit.apply_fix_to_content(content)
    fixed_twice = audit.apply_fix_to_content(fixed_once)

    assert "- Existing group: `.bar`" in fixed_once
    assert ".baz" in fixed_once
    assert fixed_once == fixed_twice
    assert audit.find_missing_classes(fixed_once) == []
