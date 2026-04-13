# Slide Content Review Checklist

Load this file during Phase 3.5 (Polish mode) or when `--review` is called.

---

## Overview

17 checkpoints divided into two categories:
- **Category 1: Auto-Detectable (7)**: Can be detected programmatically; only 1.1 and 1.6 can be fully auto-fixed
- **Category 2: AI-Advised (10)**: AI provides judgment suggestions for user consideration

---

## Category 1: Auto-Detectable Checkpoints

These checkpoints can be detected programmatically without user input.

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

**Auto-fix capability**: ✅ Yes — can automatically replace pronouns

### 1.2 结论先行 (Conclusion First)

**Detection**: Check if slide title is a noun phrase (no verb) vs. a judgment/claim.

Noun phrase patterns:
- "XX架构概览", "XX系统介绍", "XX方案说明", "XX简介", "XX说明"
- "Overview", "Introduction", "Summary", "Key Insights", "Next Steps", "Conclusion"
- "背景", "方法论", "问题分析", "关键发现", "总结", "展望"

**Auto-fix**: Generate suggested title as a judgment statement:
- "XX架构概览" → "XX架构可确保流量峰值期零遗漏"
- "Overview" → "How XX ensures zero downtime during traffic spikes"

**Fix template**: `[Subject] + [benefit/claim/outcome]`

**Auto-fix capability**: ⚠️ Partial — can generate suggestion, user confirms

### 1.3 三概念法则 (3-Concept Rule)

**Detection**: Count new technical terms/concepts per slide. Flag if > 3.

Technical term indicators:
- CamelCase words
- Acronyms (API, SDK, LLM)
- Terms in quotes or with explicit definition
- English words in Chinese text (excluding common words)

**Auto-fix**: None (requires content restructuring)

**Suggestion**: "Slide X contains 5 new concepts. Consider splitting into 2 slides or using progressive disclosure."

**Auto-fix capability**: ❌ No — detection only, requires manual intervention

### 1.4 禁止连续密集页 (No Consecutive Dense Slides)

**Detection**: Check if 3+ consecutive slides have same layout type:
- Full bullet lists
- Full grid of cards
- Full data tables

**Auto-fix**: None (requires content restructuring)

**Suggestion**: "Slides X-X+2 are all bullet lists. Insert a visual break (diagram/quote/stat) after slide X."

**Auto-fix capability**: ❌ No — detection only, requires manual intervention

### 1.6 文字/背景对比度 (Text/Background Contrast)

**Detection**: Check if any element has light text on light background:
- Search for `color: #cbd5e1` / `#888` / `#999` / `#aaa` / `var(--text-secondary)` inside elements with light inline backgrounds (`#f0f4f8`, `#fef3c7`, `#e8eef7`, `#e8f5e9`, `#f3e5f5`, `#fff`, or any background starting with `#f` or `#e`)
- This is a common issue when global CSS defines light text colors for dark-theme slides, but individual blocks use light backgrounds

**Auto-fix**: Add `color: #1e293b` to the container and `color: #334155` to child `li`/`p` elements

**Suggestion**: "Slide X has light text (#cbd5e1) on a light background (#f0f4f8). Text is nearly invisible — deepen text to #334155."

**Auto-fix capability**: ✅ Yes — can auto-insert color overrides on the container

---

### 1.5 字号底线 (Font Size Floor)

**Detection**: Check if body text font-size is below readable threshold:
- CSS: `< 1rem` or `< clamp(1rem, 2vw, 1.25rem)`
- Inline style with px/pt below 16px/12pt

**Auto-fix**: None (may break layout)

**Suggestion**: "Slide X body text is below readable size. Increase font-size or reduce content."

**Auto-fix capability**: ❌ No — detection only, requires manual intervention

### 1.6 眯眼测试 (Squint Test)

**Detection**: Check if page has a clear visual focal point:
- Largest element should be the most important content
- Flag if 2+ elements have font-size within 10% of each other and both > 1.5rem
- Flag if page has no element with font-size > 2rem (no clear hierarchy anchor)

**Auto-fix**: None (requires design decision)

**Suggestion**: "Slide X has no clear visual hierarchy. Make the key message larger/bolder or add emphasis color."

**Auto-fix capability**: ❌ No — detection only, requires manual intervention

---

## Category 2: AI-Advised Checkpoints

These checkpoints require AI judgment. Provide specific suggestions.

### 2.1 痛点前置拦截 (Pain Point First)

**Detection**: Check slides 1-2 for:
- Specific user scenario
- Screenshot with annotation
- Real case study
- Pain/frustration keywords: "痛点", "难点", "问题", "崩溃", "pain", "frustration", "issue", "problem", "struggle"

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

---

## 规则类型与触发条件

Review 规则分为三类，执行策略不同：

### 硬规则 (Hard Rules)

强制执行，不依赖内容判断。

| 规则 | 行为 |
|---|---|
| 1.3 三概念法则 | 单页新概念 ≤ 3，超出提示拆分 |
| 1.4 布局轮换 | 检测连续 3 页同布局 → 提示插入缓冲 |
| 1.5 字号底线 | 检测字号过低 → 提示调整 |
| 1.6 眯眼测试 | 检测视觉焦点不明确 → 提示重新分配权重 |

### 情境规则 (Context-Aware Rules)

根据内容类型和用户意图决定是否触发。

#### 1.2 结论先行 (标题判断句)

**触发条件**（同时满足）：
- 内容类型为：论证 / 提案 / 方案汇报 / 问题分析 / 技术方案
- 用户未在提示词中明确指定标题
- 当前标题为名词短语（无动词/判断词）

**不触发**：
- 内容类型为：简介 / 介绍 / 教程 / 产品说明 / 个人介绍
- 用户已明确指定标题（如"做一个 slide-creator 简介"）

**示例**：
- 论证型输入 → 标题改为"XX架构可确保流量峰值零遗漏" ✓
- 简介型输入 → 保持"slide-creator 简介" ✓

#### 2.2 量化收益 (原 WIIFM量化承诺)

**触发条件**：
- 内容中已包含量化数据（%、时间、倍数）
- 内容类型为：方案汇报 / 提案 / 效果展示

**行为**：
- 检测到量化数据 → 自动提升到 Slide 1-3 展示
- 未检测到量化数据 → Review 时提示"建议补充量化数据"，不硬编

**示例**：
- 内容含"效率提升约40%" → Slide 2 展示"效率提升 40%"
- 内容无量化的概念介绍 → 不强制添加

### 建议规则 (Advisory Rules)

Review 时提示，不强制执行。

| 规则 | 行为 |
|---|---|
| 1.6 文字对比 | 浅色背景+浅色文字 → 自动加深文字颜色 |
| 2.1 痛点前置 | 前2页无痛点场景 → 提示补充案例 |
| 2.5 注意力重置点 | 连续 8-10 页干货 → 提示插入案例/提问 |
| 2.7 留白缓冲页 | 每 5-6 页 → 提示插入呼吸页 |
| 2.8 术语类比 | 技术术语首次出现 → 提示添加类比解释 |

---

## 生成时内嵌规则

以下规则应在 Phase 3 生成阶段自动遵循，减少事后 Review 工作量：

| 规则 | 阶段 | 内嵌方式 |
|---|---|---|
| 1.6 文字对比 | Generate | 浅色背景 block 自动覆盖深色文字 |
| 1.3 三概念法则 | Generate | 生成时控制单页概念密度 |
| 1.4 布局轮换 | Generate | 自动轮换布局类型 |
| 1.5 字号底线 | Generate | 使用 clamp() 响应式字号 |
| 1.2 结论先行 | Plan/Generate | 根据内容类型决定标题风格 |
| 2.2 量化收益 | Plan | 检测并提取内容中的量化数据 |
| 2.8 术语类比 | Generate | 技术术语首次出现时附带类比 |
