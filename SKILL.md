---
name: kai-slide-creator
description: 生成零依赖 HTML 演示文稿 — 21 种设计预设，视觉风格探索，播放/演讲者模式。适用于路演、产品发布、技术分享等场景。
version: 2.18.0
metadata: {"openclaw":{"emoji":"🎞","os":["darwin","linux","windows"],"homepage":"https://github.com/kaisersong/slide-creator","requires":{"bins":["python3"]},"install":[]}}
---

# kai-slide-creator

生成零依赖 HTML 演示文稿，纯浏览器运行。

## 核心亮点

- **21 种设计预设** — Bold Signal、Blue Sky、Terminal Green 等，避免通用 AI 审美
- **视觉风格探索** — 生成 3 个预览，看图选风格而非描述风格
- **播放模式** — F5/▶ 全屏，幻灯片缩放适配，控制栏自动隐藏
- **演讲者模式** — P 键打开同步窗口：备注、计时器、页数、翻页
- **浏览器内编辑** — E 键进入编辑模式，Ctrl+S 保存
- **两种规划深度** — 自动 (快速出稿) / 精修 (更强叙事和视觉锁定)
- **内容 Review 系统** — 14 个检查点，精修模式自动执行

---

## 安装

**Claude Code:** 告诉 Claude「安装 https://github.com/kaisersong/slide-creator」

**OpenClaw:** `clawhub install kai-slide-creator`

> ClawHub 页面：https://clawhub.ai/skills/kai-slide-creator

---

## 使用方式

```bash
/slide-creator --plan [prompt]       # 生成 PLANNING.md 大纲
/slide-creator --generate            # 从 PLANNING.md 生成 HTML
/slide-creator --review [file.html]  # 14 项检查点自动优化
/slide-creator                       # 交互式创建（风格探索）
```

**规划深度：**
- `自动` (Auto) — 快速出稿，约 3-6 分钟
- `精修` (Polish) — 深度规划，约 8-15 分钟，自动执行 Review

**内容类型 → 风格推荐：**

| 内容类型 | 推荐风格 |
|---|---|
| 数据报告 / KPI 看板 | Data Story、Enterprise Dark、Swiss Modern |
| 商业路演 / VC Deck | Bold Signal、Aurora Mesh、Enterprise Dark |
| 开发工具 / API 文档 | Terminal Green、Neon Cyber、Neo-Retro Dev Deck |
| 研究 / 思想领导力 | Modern Newspaper、Paper & Ink、Swiss Modern |
| 创意 / 个人品牌 | Vintage Editorial、Split Pastel、Neo-Brutalism |
| 产品发布 / SaaS | Aurora Mesh、Glassmorphism、Electric Studio |

---

## 命令路由

slide-creator now supports **two user-facing planning depths**:

- `自动` / `Auto` — default path for fast drafts, light interaction, and direct generation momentum
- `精修` / `Polish` — deeper planning for decks that need stronger structure, visual locking, and page-aware image decisions

`参考驱动` remains supported, but only as an internal reference-driven branch inside `精修`.
---

## 命令路由

| 命令 | 加载内容 | 行为 |
|------|----------|------|
| `--plan [prompt]` | `references/planning-template.md` | 检测规划深度，创建 PLANNING.md，不生成 HTML |
| `--generate` | SKILL.md HARD RULES + `references/html-template.md` + `references/js-engine.md` + composition 源（见 deck_type 路由）+ 风格文件 + `base-css.md` | 从 PLANNING.md 生成 HTML，执行 14 项生成前校验 |
| `--review [file.html]` | `references/review-checklist.md` + 目标 HTML | 执行 16 项检查点 → 确认窗口 → 修复/报告 |
| 风格一致性审计 | `tests/audit_style_consistency.py` | 检查所有风格文件的 CSS 类定义是否完整列入 Signature Required CSS Classes |
| 无 flag (交互式) | `references/workflow.md` + 其他按需 | 遵循 Phase 0-5（Phase 3 Step 7 必须执行 14 项校验） |
| 直接给内容 + 风格 | SKILL.md HARD RULES + `references/html-template.md` + `references/js-engine.md` + composition 源（见 deck_type 路由）+ 风格文件 + `base-css.md` | 立即生成，执行 14 项生成前校验 |

**渐进式披露：** 每个命令只加载所需文件。`--plan` 不接触 CSS。

### deck_type 路由

| deck_type | page_count | composition 源 | 使用场景 |
|-----------|-----------|---------------|---------|
| `product-demo` | 8 | `references/composition-8.md` | slide-creator 自身介绍 demo |
| `user-content` | 12 | `references/composition-guide.md` | 用户自定义内容（路演/产品发布/报告） |

**决策逻辑：**
- `--plan` 命令：在 PLANNING.md 中写入 `deck_type` 和 `page_count` 字段
- 用户直接给内容 + 风格：介绍 slide-creator → `product-demo`，否则 → `user-content`
- `--generate`：读取 PLANNING.md 中的 `deck_type` 决定使用哪个 composition 源

---

## 生成契约

**每次生成的 HTML 必须包含播放模式和编辑模式（默认开启）。**

1. **播放模式** — F5 / ▶ 按钮，全屏缩放，`PresentMode` 类
2. **编辑模式** — 左上角热区，`✏ Edit` 开关，`contenteditable`，备注面板
3. **水印** — 由 JS 注入到**最后一页幻灯片**（`slides[slides.length - 1].appendChild`），CSS 使用 `position: absolute`，禁止 `position: fixed`。播放模式下隐藏，HTML 源码中不得出现 `<div class="slide-credit">` 硬编码在 `</body>` 前
4. **风格强制** — 所有 CSS 主题值（颜色、字体、图表色等）**必须且只能**来自选中的风格参考文件。模板 `html-template.md` 中的占位符（`[from style file]`）和注释示例值仅为结构示意，**禁止直接使用**。生成后对照风格文件的 checklist 验证。**签名元素注入是风格强制的一部分**：风格文件的 `## Signature Elements` 章节中定义的 CSS（overlays、keyframes、required classes）必须完整插入到 `<style>` 标签中。
5. **叙事弧线** — 根据 `deck_type` 选择 8 页（product-demo，引用 `references/composition-8.md`）或 12 页（user-content，引用 `references/composition-guide.md`）结构。每页必须有独特的布局模式，禁止连续两页使用相同布局。每页必须使用风格参考文件中 2-3 种不同的组件类型。

详见 `references/html-template.md`。**生成任何 HTML 前必读此文件**。

> 省略播放模式是生成错误。仅当用户明确选择「无需编辑」时可省略编辑模式。

---

### Pre-Write Validation Pipeline（生成前校验流水线）

这些规则在组装完整 HTML 后、写入文件前**自动执行**。逐条搜索违规项并修复。

**14 条核心规则：**

1. **标题禁止通用标签（原 R4）：** 不得使用概览、Overview、Introduction、Summary、结论、Key Insights、Next Steps 等通用标签作为幻灯片标题。必须使用断言式标题（陈述结论或主张）
2. **禁止连续 3 页同布局（原 R5）：** 检测连续幻灯片是否使用相同布局模式（如连续 grid 3 列、连续 split panel）。超过 2 页即违规
3. **标题质量（原 R8）：** 标题必须是断言式、具体、有信息量。不得使用占位符或通用描述
4. **U+FE0F 零容忍（原 R9）：** HTML 中不得出现 U+FE0F 变体选择符（emoji 使用基础形式）
5. **亮色文字对比度（原 R15）：** 浅色文字（`#888`/`#999`/`#cbd5e1`/`var(--text-secondary)`）在浅色背景（亮度 >60%）上 → 加深文字为深色
6. **组件丰富度（原 R16）：** 整个 deck 中至少一半的幻灯片必须使用 2-3 种不同组件类型（step/callout/stat/kbd/table/quote 等），不得仅用 `.g` + `.bl` 或 `div` + `ul` 堆砌
7. **架构隔离（原 R20）：** `#stage`、`#track`、`calc(100vw * var(--slide-count))`、`translateX` 导航仅 Blue Sky 风格可用。其他 20 个风格必须使用 `scroll-snap-type: y mandatory` + `SlidePresentation` 类架构
8. **叙事弧线完整性（原 R23）：** 根据 deck_type 检测 8 页或 12 页结构完整性。标题不得全部使用通用标签。连续两页不得使用相同布局模式。每页必须使用风格参考文件中 2-3 种不同组件类型
9. **风格签名元素注入（原 R24）：** 生成 HTML 时，读取选中风格文件的 `## Signature Elements` 章节，将其中的 CSS Overlays、Animations (@keyframes)、Required CSS Classes、Background Rule、Style-Specific Rules **全部复制插入到 `<style>` 标签中 `/* [PASTE ALL Signature Elements CSS HERE] */` 标记处**。**此外，Typography 和 Components 章节中定义的所有 CSS 类也必须包含在生成的 `<style>` 中** — 风格文件的所有章节都是生成源，不仅仅是 Signature Elements。不得遗漏 Signature Checklist 中的任何一项。缺失即生成错误。Blue Sky 例外：使用 blue-sky-starter.html 基底，不执行 .md 签名注入
10. **字体加载无白屏（原 R25）：** Google Fonts URL 必须合并为单一链接（`&display=swap`），`<style>` 开头必须有 `body { background-color: ... }` 回退色
11. **布局分类一致性（原 R26）：** 每页必须遵循 composition guide 的布局分类映射（Hero = 全屏宣告，Problem = 分栏证据，Solution = 大数字，CTA = 堆叠行动等）。Chinese Chan / Paper & Ink 允许布局重复
12. **卡片内文字对比度（原 R27）：** 亮色背景容器内不得出现深色文字（`#1a1a1a`/`#333`），暗色背景容器内不得出现浅色文字。必须使用 `var(--text-on-card)` 或对应的 rgba 值
13. **播放模式（引用 GC-1）：** 必须包含 `PresentMode` 类或 `enterPresent()` 函数，存在 `F5` 键监听器、`#present-btn` CSS、`body.presenting` CSS。缺失即生成错误
14. **水印（引用 GC-3）：** 水印必须由 JS 注入到最后一页，CSS 必须是 `position: absolute`，禁止 `position: fixed`，禁止 `<div class="slide-credit">` 硬编码

> 完整反模式映射表见 `references/impeccable-anti-patterns.md`。更多视觉/组件规则在 `--review` 模式下执行。

### 标题质量规则

**Do NOT 使用这些通用标签作为幻灯片标题：**
概览、Overview、架构介绍、Introduction、Summary、总结、结论、Key Insights、Next Steps、方法论、背景、问题分析、关键发现、展望、简介、说明、系统介绍、方案说明。

**Instead，使用断言式标题（陈述结论或主张）：**
- ❌ `XX 架构概览` → ✅ `XX 架构可确保流量峰值期零遗漏`
- ❌ `Overview` → ✅ `How XX ensures zero downtime during traffic spikes`
- ❌ `系统介绍` → ✅ `三个核心模块，支撑日活百万级业务`
- ❌ `关键发现` → ✅ `80% 的用户流失来自首次加载超时`

**幻灯片标题模板（选一种匹配）：**
- "[Subject] 可确保/证明/支撑 [具体收益/结果]" — 技术/架构页
- "N 个 [核心概念]，解决 [关键痛点]" — 能力/特性页
- "[数据/事实] — [洞察/含义]" — 数据/发现页
- "[行动/决策] 的 N 个步骤/原则" — 方法/流程页
- 最短有力断言（≤12 字中文 / ≤6 英文词）— 强调/宣言页

**快速路由：**

- **PLANNING.md 已存在** → 读取并作为真相源，跳至 Phase 3
- **用户直接给内容 + 风格** → 跳过 Phase 1/2，立即生成
- **用户有 `.ppt/.pptx` 文件** → Phase 4（PPT 转换）
- **用户要增强现有 HTML** → 读取后遵循 Enhancement Mode 守则
- **其他情况** → Phase 1（内容发现）

---

## 风格参考文件

仅读取已选风格的文件。

| 风格 | 文件 |
|------|------|
| Bold Signal | `references/bold-signal.md` |
| Blue Sky | `references/blue-sky-starter.html` |
| Aurora Mesh | `references/aurora-mesh.md` |
| Chinese Chan | `references/chinese-chan.md` |
| Creative Voltage | `references/creative-voltage.md` |
| Dark Botanical | `references/dark-botanical.md` |
| Data Story | `references/data-story.md` |
| Electric Studio | `references/electric-studio.md` |
| Enterprise Dark | `references/enterprise-dark.md` |
| Glassmorphism | `references/glassmorphism.md` |
| Modern Newspaper | `references/modern-newspaper.md` |
| Neo-Brutalism | `references/neo-brutalism.md` |
| Neo-Retro Dev | `references/neo-retro-dev.md` |
| Neon Cyber | `references/neon-cyber.md` |
| Notebook Tabs | `references/notebook-tabs.md` |
| Paper & Ink | `references/paper-ink.md` |
| Pastel Geometry | `references/pastel-geometry.md` |
| Split Pastel | `references/split-pastel.md` |
| Swiss Modern | `references/swiss-modern.md` |
| Terminal Green | `references/terminal-green.md` |
| Vintage Editorial | `references/vintage-editorial.md` |
| 自定义主题 | `themes/<name>/reference.md` |

**风格选择器 / 心情映射** → `references/style-index.md`

**视口 CSS / 密度限制** → `references/base-css.md`

**设计质量规则** → `references/design-quality.md`

**Impeccable 反模式（视觉硬规则）** → `references/impeccable-anti-patterns.md`

---

## 面向 AI 智能体

其他智能体可直接调用：

```bash
# 从主题或备注生成
/slide-creator 为 [主题] 制作路演 deck

# 从计划文件生成（跳过交互式 Phase）
/slide-creator --generate  # 自动读取 PLANNING.md

# 两阶段（生成前审查大纲）
/slide-creator --plan "Acme v2 产品发布"
# （如需要，编辑 PLANNING.md）
/slide-creator --generate

# 生成后导出 PPTX
/kai-html-export presentation.html                    # 图片模式（像素级，默认）
/kai-html-export --mode native presentation.html      # Native 模式（文字可编辑）
```

---

## 相关技能

- **kai-report-creator** — 长篇幅可滚动 HTML 报告（非幻灯片）
- **kai-html-export** — 导出 PPTX/PNG，或发布为分享链接
