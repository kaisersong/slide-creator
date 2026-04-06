# Slide Creator Mode Simplification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Simplify slide-creator's planning depth into two user-facing modes, `自动` and `精修`, while keeping `参考驱动` only as an internal `精修` branch.

**Architecture:** Treat this as a skill-contract change, not a rendering rewrite. Update the user-facing router (`SKILL.md`), the interactive workflow (`references/workflow.md`), and the `PLANNING.md` contract (`references/planning-template.md`) together, then lock the new behavior with doc-regression tests and two checked-in demo planning outputs.

**Tech Stack:** Markdown skill docs, Python `pytest` regression tests, checked-in `PLANNING.md` demo artifacts

---

### Task 1: Lock the Mode Contract With Failing Tests

**Files:**
- Create: `tests/test_mode_simplification.py`
- Test: `tests/test_mode_simplification.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_MD = ROOT / "SKILL.md"
WORKFLOW_MD = ROOT / "references" / "workflow.md"
PLANNING_TEMPLATE_MD = ROOT / "references" / "planning-template.md"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_skill_exposes_only_two_user_facing_planning_depths():
    skill = read_text(SKILL_MD)
    assert "`自动`" in skill
    assert "`精修`" in skill
    assert "two user-facing planning depths" in skill
    assert "Do not add a third top-level mode." in skill


def test_workflow_routes_to_polish_and_hides_reference_as_top_level_mode():
    workflow = read_text(WORKFLOW_MD)
    assert "Default: if the user does not specify a mode, route to `自动`." in workflow
    assert "Route to `精修` when" in workflow
    assert "`参考驱动` is only an internal branch inside `精修`." in workflow


def test_planning_template_supports_auto_and_polish_depths():
    template = read_text(PLANNING_TEMPLATE_MD)
    assert "**Mode**: [自动 / 精修]" in template
    assert "Only include this section when mode is `精修`." in template
    assert "## Deck Thesis" in template
    assert "## Image Intent" in template
```

- [ ] **Step 2: Run test to verify it fails**

Run: `D:\projects\.venv\Scripts\python.exe -m pytest tests/test_mode_simplification.py -q -p no:cacheprovider`
Expected: FAIL because the current docs do not yet describe the two-depth model.

- [ ] **Step 3: Write minimal implementation**

```markdown
- add the two-depth contract to `SKILL.md`
- add routing rules and polish-only reference handling to `references/workflow.md`
- add mode-aware sections to `references/planning-template.md`
```

- [ ] **Step 4: Run test to verify it passes**

Run: `D:\projects\.venv\Scripts\python.exe -m pytest tests/test_mode_simplification.py -q -p no:cacheprovider`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_mode_simplification.py SKILL.md references/workflow.md references/planning-template.md
git commit -m "feat: simplify slide-creator planning modes"
```

### Task 2: Add Demo Planning Outputs For Both Paths

**Files:**
- Create: `demos/mode-paths/auto-PLANNING.md`
- Create: `demos/mode-paths/polish-PLANNING.md`
- Modify: `tests/test_mode_simplification.py`
- Test: `tests/test_mode_simplification.py`

- [ ] **Step 1: Write the failing test**

```python
AUTO_DEMO = ROOT / "demos" / "mode-paths" / "auto-PLANNING.md"
POLISH_DEMO = ROOT / "demos" / "mode-paths" / "polish-PLANNING.md"


def test_demo_auto_path_stays_lightweight():
    auto_demo = read_text(AUTO_DEMO)
    assert "**Mode**: 自动" in auto_demo
    assert "## Deck Thesis" not in auto_demo
    assert "## Image Intent" not in auto_demo


def test_demo_polish_path_embeds_deeper_planning_sections():
    polish_demo = read_text(POLISH_DEMO)
    assert "**Mode**: 精修" in polish_demo
    assert "## Deck Thesis" in polish_demo
    assert "## Narrative Arc" in polish_demo
    assert "## Page Roles" in polish_demo
    assert "## Style Constraints" in polish_demo
    assert "## Image Intent" in polish_demo
    assert "参考驱动" in polish_demo
```

- [ ] **Step 2: Run test to verify it fails**

Run: `D:\projects\.venv\Scripts\python.exe -m pytest tests/test_mode_simplification.py -q -p no:cacheprovider`
Expected: FAIL because the demo planning artifacts do not yet exist.

- [ ] **Step 3: Write minimal implementation**

```markdown
- create one checked-in `自动` planning example
- create one checked-in `精修` planning example with thesis / arc / role / style / image-intent sections
```

- [ ] **Step 4: Run test to verify it passes**

Run: `D:\projects\.venv\Scripts\python.exe -m pytest tests/test_mode_simplification.py -q -p no:cacheprovider`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add demos/mode-paths/auto-PLANNING.md demos/mode-paths/polish-PLANNING.md tests/test_mode_simplification.py
git commit -m "test: cover auto and polish planning demos"
```

### Task 3: Run Full Verification And Demo The Two Paths

**Files:**
- Test: `tests/test_mode_simplification.py`
- Test: `tests/test_workflow_polish.py`
- Test: `tests/test_demo_quality.py`

- [ ] **Step 1: Run targeted regression tests**

```bash
D:\projects\.venv\Scripts\python.exe -m pytest tests/test_mode_simplification.py tests/test_workflow_polish.py -q -p no:cacheprovider
```

- [ ] **Step 2: Run broader demo regression suite**

```bash
D:\projects\.venv\Scripts\python.exe -m pytest tests/test_demo_quality.py -q -p no:cacheprovider
```

- [ ] **Step 3: Run demo inspection commands**

```bash
Get-Content demos/mode-paths/auto-PLANNING.md
Get-Content demos/mode-paths/polish-PLANNING.md
```

- [ ] **Step 4: Verify expected outcomes**

```text
auto demo: contains Mode=自动 and omits Deck Thesis / Image Intent
polish demo: contains Mode=精修 and includes Deck Thesis / Narrative Arc / Page Roles / Style Constraints / Image Intent
all selected tests: PASS
```

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/plans/2026-04-06-slide-creator-mode-simplification.md
git commit -m "docs: add implementation plan for mode simplification"
```
