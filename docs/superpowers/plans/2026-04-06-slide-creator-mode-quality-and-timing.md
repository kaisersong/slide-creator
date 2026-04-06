# Slide Creator Mode Quality And Timing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair `slide-creator` so mode depth does not change preset selection, English users see `Auto / Polish`, segmented timing is recorded and documented, and both Intent Broker demos are regenerated from the repaired skill.

**Architecture:** Treat this as a skill-contract and verification upgrade. First tighten the documentation and tests around bilingual mode names, preset fidelity, and timing capture. Then regenerate both mode-path demos from the same source content and record measured timings in the docs.

**Tech Stack:** Markdown skill docs, Python `pytest`, existing HTML validator, manual timing capture during demo regeneration

---

### Task 1: Lock bilingual mode naming and timing contract in docs and tests

**Files:**
- Modify: `SKILL.md`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `references/workflow.md`
- Modify: `references/planning-template.md`
- Modify: `tests/test_mode_simplification.py`
- Modify: `tests/test_design_quality_guards.py`

- [ ] Add bilingual mode naming to the skill contract: Chinese shows `自动 / 精修`, English shows `Auto / Polish`, with explicit alias mapping.
- [ ] Add segmented timing contract (`plan`, `generate`, `validate`, `polish`, `total`) to workflow and planning docs.
- [ ] Add pre-generation estimate guidance for `Auto` vs `Polish` to skill and README docs.
- [ ] Update tests so they assert bilingual mode naming and timing sections instead of only Chinese naming.
- [ ] Run: `D:\projects\.venv\Scripts\python.exe -m pytest tests/test_mode_simplification.py tests/test_design_quality_guards.py -q -p no:cacheprovider`

### Task 2: Tighten preset fidelity and quality guard tests around skill behavior

**Files:**
- Modify: `references/html-template.md`
- Modify: `references/design-quality.md`
- Modify: `tests/test_mode_path_regressions.py`
- Modify: `tests/validate.py`
- Modify: `tests/test_validate_console_output.py`

- [ ] Keep `data-preset` as a required generation contract in the template docs.
- [ ] Keep title-wrap and dense half-width state-grid failures documented as hard quality failures.
- [ ] Refocus mode-path regression tests onto skill guarantees: planned preset must equal generated preset, narrow global title caps are banned, timing metadata must exist after regeneration.
- [ ] Keep Windows-safe validator output passing.
- [ ] Run: `D:\projects\.venv\Scripts\python.exe -m pytest tests/test_mode_path_regressions.py tests/test_validate_console_output.py -q -p no:cacheprovider`

### Task 3: Regenerate the Auto demo with measured segmented timings

**Files:**
- Modify: `demos/mode-paths/intent-broker-auto-PLANNING.md`
- Modify: `demos/mode-paths/intent-broker-auto.html`

- [ ] Start a timer and record `plan` time while producing the final `Auto` planning artifact from `D:\projects\mydocs\intent-broker\docs\superpowers\specs\2026-03-31-intent-broker-design.md`.
- [ ] Start a timer and record `generate` time while creating the HTML from the repaired skill contract.
- [ ] Start a timer and record `validate` time while running strict validation.
- [ ] Record `polish` time if any regeneration fixes are required after validation; otherwise record zero.
- [ ] Record `total` elapsed time and embed the timing block in the planning artifact or sibling notes.

### Task 4: Regenerate the Polish demo with measured segmented timings

**Files:**
- Modify: `demos/mode-paths/intent-broker-polish-PLANNING.md`
- Modify: `demos/mode-paths/intent-broker-polish.html`

- [ ] Start a timer and record `plan` time while producing the final `Polish` planning artifact from the same source spec.
- [ ] Start a timer and record `generate` time while creating the HTML from the repaired skill contract.
- [ ] Start a timer and record `validate` time while running strict validation.
- [ ] Record `polish` time for any additional refinement required by the deep path.
- [ ] Record `total` elapsed time and embed the timing block in the planning artifact or sibling notes.

### Task 5: Publish measured timing guidance and run final verification

**Files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Test: `tests/test_mode_simplification.py`
- Test: `tests/test_design_quality_guards.py`
- Test: `tests/test_mode_path_regressions.py`
- Test: `tests/test_validate_console_output.py`

- [ ] Add an estimated-timing section to both READMEs.
- [ ] Add the measured Auto / Polish demo timings to both READMEs.
- [ ] Run: `D:\projects\.venv\Scripts\python.exe -m pytest tests/test_mode_simplification.py tests/test_design_quality_guards.py tests/test_mode_path_regressions.py tests/test_validate_console_output.py -q -p no:cacheprovider`
- [ ] Run: `D:\projects\.venv\Scripts\python.exe tests\validate.py demos\mode-paths\intent-broker-auto.html --strict`
- [ ] Run: `D:\projects\.venv\Scripts\python.exe tests\validate.py demos\mode-paths\intent-broker-polish.html --strict`
