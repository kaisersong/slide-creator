# Slide Creator Review 功能实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 slide-creator 增加内容层面的 Review 能力，Polish 模式默认执行，Auto 模式跳过，用户可手动调用 `--review` 命令。

**Architecture:** 新增 Phase 3.5 Review 作为生成后检查阶段，16项 Checkpoints 分为可自动修复（6项）和 AI 判断建议（10项），检测结果通过 AskUserQuestion 确认后输出修复后的 HTML 和诊断报告。

**Tech Stack:** Markdown skill docs, Python pytest, HTML parsing

---

## File Structure

| 文件 | 职责 |
|---|---|
| `references/review-checklist.md` | 16项 Checkpoints 定义、检测规则、修复方法、AI 建议模板 |
| `SKILL.md` | 增加 `--review` 命令路由、Phase 3.5 说明 |
| `references/workflow.md` | 增加 Phase 3.5 Review 章节 |
| `references/design-quality.md` | 增加 L1 内容检查索引 |
| `tests/test_review_checklist.py` | Review 功能测试 |

---

### Task 1: 创建 review-checklist.md

**Files:**
- Create: `references/review-checklist.md`

- [ ] **Step 1: 写 review-checklist.md 文件**

```markdown
# Slide Content Review Checklist

Load this file during Phase 3.5 (Polish mode) or when `--review` is called.

---

## Overview

16 checkpoints divided into two categories:
- **Auto-fixable (6)**: Can be detected and fixed automatically
- **AI-advised (10)**: AI provides judgment suggestions for user consideration

---

## Category 1: Auto-Fixable Checkpoints

These checkpoints can be detected programmatically and fixed without user input.

### 1.1 视角翻转 (Perspective Flip)

**Detection**: Scan slide titles and body text for first-person pronouns:
- Chinese: "我", "本系统", "本次分享", "我们"
- English: "I", "my", "our system", "this presentation"

**Auto-fix**: Replace with audience-centered pronouns:
- "我/我们" → "你/你们"
- "本系统" → "你的系统" / "这套方案"
- "本次分享" → "今天你将学会"
- "I/We" → "You"
- "my/our" → "your"

**Example fix**:
- Before: "我要分享的系统架构是..."
- After: "你将学会如何利用这套架构解决问题"

### 1.2 结论先行 (Conclusion First)

**Detection**: Check if slide title is a noun phrase (no verb) vs. a judgment/claim.

Noun phrase patterns:
- "XX架构概览", "XX系统介绍", "XX方案说明"
- "Overview", "Introduction", "Summary"

**Auto-fix**: Generate suggested title as a judgment statement:
- "XX架构概览" → "XX架构可确保流量峰值期零遗漏"
- "Overview" → "How XX ensures zero downtime during traffic spikes"

**Fix template**: `[Subject] + [benefit/claim/outcome]`

### 1.3 3概念法则 (3-Concept Rule)

**Detection**: Count new technical terms/concepts per slide. Flag if > 3.

Technical term indicators:
- CamelCase words
- Acronyms (API, SDK, LLM)
- Terms in quotes or with explicit definition
- English words in Chinese text (excluding common words)

**Auto-fix**: None (requires content restructuring)

**Suggestion**: "Slide X contains 5 new concepts. Consider splitting into 2 slides or using progressive disclosure."

### 1.4 禁止连续密集页 (No Consecutive Dense Slides)

**Detection**: Check if 3+ consecutive slides have same layout type:
- Full bullet lists
- Full grid of cards
- Full data tables

**Auto-fix**: None (requires content restructuring)

**Suggestion**: "Slides X-X+2 are all bullet lists. Insert a visual break (diagram/quote/stat) after slide X."

### 1.5 字号底线 (Font Size Floor)

**Detection**: Check if body text font-size is below readable threshold:
- CSS: `< 1rem` or `< clamp(1rem, 2vw, 1.25rem)`
- Inline style with px/pt below 16px/12pt

**Auto-fix**: None (may break layout)

**Suggestion**: "Slide X body text is below readable size. Increase font-size or reduce content."

### 1.6 眯眼测试 (Squint Test)

**Detection**: Check if page has a clear visual focal point:
- Largest element should be the most important content
- If multiple elements compete for attention (same size/weight), flag

**Auto-fix**: None (requires design decision)

**Suggestion**: "Slide X has no clear visual hierarchy. Make the key message larger/bolder or add emphasis color."

---

## Category 2: AI-Advised Checkpoints

These checkpoints require AI judgment. Provide specific suggestions.

### 2.1 痛点前置拦截 (Pain Point First)

**Detection**: Check slides 1-2 for:
- Specific user scenario
- Screenshot with annotation
- Real case study
- Pain/frustration keywords

**AI suggestion template**: "前2页未检测到具体痛点场景。建议在Slide 1补充真实用户痛点截图或案例，例如'大促期间客服手工核对几百个订单到崩溃'。"

### 2.2 WIIFM量化承诺 (WIIFM Quantified)

**Detection**: Check slides 1-3 for quantified benefit:
- Numbers with % or time units
- "节省XX%", "缩短XX分钟", "提升XX倍"
- "save X%", "reduce by X", "X times faster"

**AI suggestion template**: "前3页未检测到量化收益承诺。建议明确写出'掌握这个工作流能让你的日均处理时间缩短40%'。"

### 2.3 MECE原则 (MECE Principle)

**Detection**: Check step/category lists for:
- Overlapping keywords between items
- Items that could be merged
- Missing obvious category

**AI suggestion template**: "步骤X和步骤Y包含相似关键词'[word]'，可能存在重叠。建议合并为'XX'或明确区分边界。"

### 2.4 奥卡姆剃刀 (Occam's Razor)

**Detection**: Check each slide for:
- Content not directly supporting main goal
- Tangential information that could be appendix
- More than 5 bullet points (possible scope creep)

**AI suggestion template**: "Slide X与核心目标'[goal]'关联较弱。可考虑移到附录或删除。"

### 2.5 10分钟注意力重置 (10-Min Attention Reset)

**Detection**: After every 8-10 slides of dense content, check for:
- Interactive question
- Real case study
- Demo/screenshot
- Breathing room slide

**AI suggestion template**: "连续X页干货后未检测到注意力重置点。建议在Slide X后插入一个真实踩坑案例或互动提问。"

### 2.6 张力对比结构 (Tension Contrast)

**Detection**: Check for before/after or manual/auto contrast:
- "旧方法 → 新方法" structure
- "痛点 → 解决方案" contrast
- Side-by-side comparison

**AI suggestion template**: "未检测到张力对比结构。建议增加'手工操作繁琐步骤 → 自动化流程对比'形成强烈反差。"

### 2.7 留白缓冲页 (Breathing Room)

**Detection**: Check for visual-minimal slides every 5-6 slides:
- Single statement slide
- Big number/stat
- Quote with attribution
- Near-empty slide with intentional whitespace

**AI suggestion template**: "未检测到缓冲页。建议每5-6页插入一张呼吸页（单句陈述/大数字/引语），让听众大脑存储信息。"

### 2.8 黑话降维翻译 (Jargon Translation)

**Detection**: For each technical term on first appearance:
- Check if analogy/explanation follows within same slide or next slide
- Flag terms without plain-language translation

**AI suggestion template**: "'[term]'首次出现未附带类比解释。建议添加'相当于一个XX'或'类似于XX'让人话翻译。"

### 2.9 图像降噪 (Image Noise Reduction)

**Detection**: Check images for:
- 3D cartoon characters/stock people
- Emoji or meme images
- Low-quality screenshots
- Watermarked images

**AI suggestion template**: "检测到[X]类廉价图像元素。建议替换为专业图示或高质量截图。"

### 2.10 数据图表降噪 (Chart Noise Reduction)

**Detection**: Check SVG/charts for:
- Grid lines on line/bar charts
- 3D effects on charts
- More than 5 data series on single chart
- Redundant axis labels

**AI suggestion template**: "图表含网格线/3D效果。建议删除以降低视觉噪音，将核心数据线标为高亮主色，其余置灰。"

---

## Detection Result Categories

When running review, classify each checkpoint result:

| Symbol | Category | Description |
|---|---|---|
| ✅ | Passed | No issues detected |
| 🔧 | Auto-fixable | Can be fixed automatically |
| ⚠️ | Needs confirmation | AI suggestion provided, user decides |
| ❌ | Needs human judgment | Cannot auto-detect, AI provides guidance |

---

## Review Report Template

```markdown
## Review 诊断报告

**幻灯片**: [filename].html
**检测结果**: [passed]/16 通过，[pending]项待处理

### 已修复项 ([count])
- ✅ [checkpoint]: [what was fixed]

### 未修复项 ([count])
- ⚠️ [checkpoint]: [issue description]
  - AI建议：[suggestion]

### 需人工判断项 (建议思考)
- 🔍 [checkpoint]: [AI analysis]

---
可再次运行 `/slide-creator --review` 继续优化
```
```

- [ ] **Step 2: 验证文件创建**

Run: `cat references/review-checklist.md | head -20`
Expected: 文件内容正确显示

- [ ] **Step 3: Commit**

```bash
git add references/review-checklist.md
git commit -m "feat: add review-checklist.md with 16 content checkpoints"
```

---

### Task 2: 更新 SKILL.md 增加 `--review` 命令

**Files:**
- Modify: `SKILL.md`

- [ ] **Step 1: 更新 Command Routing 表**

在 `SKILL.md` 的 Command Routing 部分增加 `--review` 行：

```markdown
| Command | What to load | What to do |
|---------|-------------|------------|
| `--plan [prompt]` | `references/planning-template.md` | Create PLANNING.md. Stop — no HTML. |
| `--generate` | `references/html-template.md` + chosen style file + `references/base-css.md` + `references/design-quality.md` | Read PLANNING.md, generate HTML. |
| `--review [file.html]` | `references/review-checklist.md` + target HTML | Execute 16 checkpoints → confirmation window → fix/report. |
| No flag (interactive) | `references/workflow.md` + **`references/html-template.md` before Phase 3** + `references/design-quality.md` before writing | Follow Phase 0-5. Phase 3.5 Review only in Polish mode. |
| Content + style given directly | `references/html-template.md` + style file + `references/base-css.md` | Generate immediately — no Phase 1/2 needed. |
```

- [ ] **Step 2: 增加 Phase 3.5 Review 说明章节**

在 Generation Contract 章节后增加：

```markdown
---

## Review Mode (`--review`)

Run 16 content checkpoints against generated or existing HTML:

```
/slide-creator --review presentation.html
```

**Behavior:**
1. Load `references/review-checklist.md`
2. Execute all 16 checkpoints
3. Show confirmation window with results (✅ passed, 🔧 auto-fixable, ⚠️ needs confirmation, ❌ needs judgment)
4. User chooses: [全部自动修复] / [逐项确认] / [跳过]
5. Output fixed HTML + diagnostic report

**Polish mode**: Phase 3.5 Review runs automatically after generation.
**Auto mode**: Skips Phase 3.5 entirely.
```

- [ ] **Step 3: 验证修改**

Run: `grep -A 2 "\-\-review" SKILL.md`
Expected: 显示新增的 --review 命令行

- [ ] **Step 4: Commit**

```bash
git add SKILL.md
git commit -m "feat: add --review command and Phase 3.5 to SKILL.md"
```

---

### Task 3: 更新 workflow.md 增加 Phase 3.5

**Files:**
- Modify: `references/workflow.md`

- [ ] **Step 1: 在 Phase 3 后增加 Phase 3.5 章节**

在 `## Phase 4: PPT Conversion` 之前插入：

```markdown
---

## Phase 3.5: Review (Polish mode only)

**Auto mode**: Skip this phase entirely. Proceed directly to Phase 5 Delivery.

**Polish mode**: Run after Phase 3 generation completes.

**`--review` command**: Entry point for reviewing any existing HTML.

### Step 1: Load review rules

Read [review-checklist.md](review-checklist.md) for the 16 checkpoints.

### Step 2: Execute detection

Run all 16 checkpoints against the generated HTML:

- **Category 1 (Auto-fixable)**: 6 checkpoints that can be fixed automatically
- **Category 2 (AI-advised)**: 10 checkpoints where AI provides suggestions

### Step 3: Classify and present results

Group results by category:

| Symbol | Category | Action |
|---|---|---|
| ✅ | Passed | No action needed |
| 🔧 | Auto-fixable | Can fix without user input |
| ⚠️ | Needs confirmation | AI suggests fix, user confirms |
| ❌ | Needs judgment | AI provides guidance, user decides |

Present via AskUserQuestion with options:
- **[全部自动修复]** — Apply all 🔧 fixes automatically
- **[逐项确认]** — Review each 🔧/⚠️ item individually
- **[跳过Review]** — Output HTML as-is

### Step 4: Apply fixes

**If "全部自动修复"**:
1. Apply all 🔧 auto-fixable changes
2. Write updated HTML
3. Generate REVIEW_REPORT.md

**If "逐项确认"**:
1. For each 🔧/⚠️ item, show:
   - Checkpoint name
   - Issue description
   - Suggested fix
2. User selects: [修复] / [跳过] / [保持原样]
3. After all items, write updated HTML
4. Generate REVIEW_REPORT.md

**If "跳过Review"**:
1. Write HTML as-is
2. Skip report generation

### Step 5: Output diagnostic report

Generate REVIEW_REPORT.md in working directory:

```markdown
## Review 诊断报告

**幻灯片**: [filename].html
**检测结果**: [passed]/16 通过，[pending]项待处理

### 已修复项 ([count])
- ✅ [checkpoint]: [what was fixed]

### 未修复项 ([count])
- ⚠️ [checkpoint]: [issue description]
  - AI建议：[suggestion]

### 需人工判断项 (建议思考)
- 🔍 [checkpoint]: [AI analysis]

---
可再次运行 `/slide-creator --review` 继续优化
```

Tell user: "Review完成。可再次运行 `/slide-creator --review [filename].html` 继续优化。"
```

- [ ] **Step 2: 验证修改**

Run: `grep -A 5 "Phase 3.5" references/workflow.md`
Expected: 显示新增的 Phase 3.5 章节

- [ ] **Step 3: Commit**

```bash
git add references/workflow.md
git commit -m "feat: add Phase 3.5 Review to workflow.md"
```

---

### Task 4: 更新 design-quality.md 增加 L1 索引

**Files:**
- Modify: `references/design-quality.md`

- [ ] **Step 1: 在文件末尾增加 L1 内容检查索引**

```markdown
---

## L1 Content Quality Check

For content-level checkpoints (perspective, logic, pacing, clarity), see [review-checklist.md](review-checklist.md).

**L0 (Visual)**: This file — density, color, typography, layout
**L1 (Content)**: review-checklist.md — perspective flip, conclusion first, cognitive load, jargon translation

**When to apply:**
- L0: Always, before writing HTML
- L1: Polish mode after generation, or via `--review` command
```

- [ ] **Step 2: 验证修改**

Run: `tail -15 references/design-quality.md`
Expected: 显示新增的 L1 索引章节

- [ ] **Step 3: Commit**

```bash
git add references/design-quality.md
git commit -m "docs: add L1 content check index to design-quality.md"
```

---

### Task 5: 创建 Review 功能测试

**Files:**
- Create: `tests/test_review_checklist.py`

- [ ] **Step 1: 写测试文件**

```python
"""
Tests for slide-creator review checklist functionality.

Validates:
1. review-checklist.md exists and has required sections
2. SKILL.md documents --review command
3. workflow.md has Phase 3.5
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEW_CHECKLIST = ROOT / "references" / "review-checklist.md"
SKILL_MD = ROOT / "SKILL.md"
WORKFLOW_MD = ROOT / "references" / "workflow.md"
DESIGN_QUALITY_MD = ROOT / "references" / "design-quality.md"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestReviewChecklistExists:
    """Test that review-checklist.md exists with required content."""

    def test_review_checklist_file_exists(self):
        assert REVIEW_CHECKLIST.exists(), "references/review-checklist.md should exist"

    def test_review_checklist_has_16_checkpoints(self):
        content = read_text(REVIEW_CHECKLIST)
        # Category 1: 6 auto-fixable
        assert "### 1.1 视角翻转" in content or "### 1.1 Perspective Flip" in content
        assert "### 1.2 结论先行" in content or "### 1.2 Conclusion First" in content
        assert "### 1.3 3概念法则" in content or "### 1.3 3-Concept" in content
        assert "### 1.4 禁止连续密集页" in content or "### 1.4 No Consecutive" in content
        assert "### 1.5 字号底线" in content or "### 1.5 Font Size" in content
        assert "### 1.6 眯眼测试" in content or "### 1.6 Squint Test" in content
        # Category 2: 10 AI-advised
        assert "### 2.1 痛点前置拦截" in content or "### 2.1 Pain Point" in content
        assert "### 2.2 WIIFM" in content
        assert "### 2.3 MECE" in content
        assert "### 2.4 奥卡姆" in content or "### 2.4 Occam" in content

    def test_review_checklist_has_detection_rules(self):
        content = read_text(REVIEW_CHECKLIST)
        assert "**Detection**:" in content or "**检测**" in content
        assert "**Auto-fix**:" in content or "**自动修复**" in content
        assert "**AI suggestion" in content or "**AI建议" in content

    def test_review_checklist_has_result_categories(self):
        content = read_text(REVIEW_CHECKLIST)
        assert "✅" in content
        assert "🔧" in content
        assert "⚠️" in content
        assert "❌" in content


class TestSkillMdReviewCommand:
    """Test that SKILL.md documents --review command."""

    def test_skill_has_review_command(self):
        content = read_text(SKILL_MD)
        assert "--review" in content, "SKILL.md should document --review command"

    def test_skill_has_review_checklist_reference(self):
        content = read_text(SKILL_MD)
        assert "review-checklist.md" in content, "SKILL.md should reference review-checklist.md"

    def test_skill_documents_phase_35(self):
        content = read_text(SKILL_MD)
        assert "Phase 3.5" in content or "Phase 3.5" in content, "SKILL.md should mention Phase 3.5"


class TestWorkflowPhase35:
    """Test that workflow.md has Phase 3.5."""

    def test_workflow_has_phase_35(self):
        content = read_text(WORKFLOW_MD)
        assert "Phase 3.5" in content or "phase 3.5" in content.lower()

    def test_workflow_phase_35_polish_only(self):
        content = read_text(WORKFLOW_MD)
        phase_35_section = content[content.find("Phase 3.5"):] if "Phase 3.5" in content else ""
        assert "Polish" in phase_35_section or "精修" in phase_35_section
        assert "Auto" in phase_35_section or "自动" in phase_35_section

    def test_workflow_phase_35_links_review_checklist(self):
        content = read_text(WORKFLOW_MD)
        assert "review-checklist.md" in content


class TestDesignQualityL1Index:
    """Test that design-quality.md has L1 index."""

    def test_design_quality_has_l1_reference(self):
        content = read_text(DESIGN_QUALITY_MD)
        assert "L1" in content or "review-checklist" in content
```

- [ ] **Step 2: 运行测试验证**

Run: `cd /Users/song/projects/slide-creator && python3 -m pytest tests/test_review_checklist.py -v`
Expected: 所有测试通过

- [ ] **Step 3: Commit**

```bash
git add tests/test_review_checklist.py
git commit -m "test: add review checklist tests"
```

---

### Task 6: 运行完整测试验证

**Files:**
- Test: All tests in `tests/`

- [ ] **Step 1: 运行所有相关测试**

```bash
cd /Users/song/projects/slide-creator
python3 -m pytest tests/test_review_checklist.py tests/test_mode_simplification.py tests/test_design_quality_guards.py -v
```

Expected: All tests pass

- [ ] **Step 2: 最终提交**

```bash
git add docs/superpowers/specs/2026-04-06-slide-creator-review-design.md docs/superpowers/plans/2026-04-06-slide-creator-review.md
git commit -m "docs: add review feature design and implementation plan"
```

---

## Validation Summary

| Checkpoint | Task |
|---|---|
| review-checklist.md created with 16 checkpoints | Task 1 |
| SKILL.md has --review command | Task 2 |
| workflow.md has Phase 3.5 | Task 3 |
| design-quality.md has L1 index | Task 4 |
| Tests pass | Task 5, 6 |

## Success Criteria

- `--review` 命令可在 SKILL.md 中找到
- Phase 3.5 在 workflow.md 中定义
- 16项 Checkpoints 在 review-checklist.md 中完整定义
- Auto 模式跳过 Review，Polish 模式触发 Review
- 所有测试通过