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

`自动` (Auto) — 快速出稿 | `精修` (Polish) — 深度规划，自动执行 Review

| 命令 | 加载内容 | 行为 |
|------|----------|------|
| `--plan [prompt]` | `references/planning-template.md` | 创建 PLANNING.md，不生成 HTML |
| `--generate` | SKILL.md + `references/html-template.md` + `references/js-engine.md` + composition 源 + 风格文件 + `base-css.md` + `impeccable-anti-patterns.md` + `title-quality.md` | 生成 HTML，执行 11 项生成前校验 |
| `--review [file.html]` | `references/review-checklist.md` + 目标 HTML | 执行 17 项检查点 → 确认窗口 → 修复/报告 |
| 风格一致性审计 | `tests/audit_style_consistency.py` | 检查所有风格文件的 CSS 类定义是否完整列入 Signature Required CSS Classes |
| 无 flag (交互式) | `references/workflow.md` + 其他按需 | 遵循 Phase 0-5 |
| 直接给内容 + 风格 | 同 `--generate` | 立即生成，执行 11 项生成前校验 |

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

**11 条核心规则：**

1. **标题质量（R4+R8）：** 标题必须是断言式、具体、有信息量。禁止通用标签（概览/Overview/Introduction/Summary/结论等）。示例和模板见 `references/title-quality.md`
2. **布局多样性（R5+R23）：** 禁止连续 3 页相同布局模式。每页必须使用 2-3 种不同组件类型（step/callout/stat/kbd/table/quote 等），不得仅用 `.g` + `.bl` 堆砌
3. **U+FE0F 零容忍（R9）：** HTML 中不得出现 U+FE0F 变体选择符
4. **文字对比度（R15+R27）：** 浅色文字不得出现在浅色背景上，深色文字不得出现在深色背景上。必须使用 `var(--text-on-card)` 或风格文件定义的对比色
5. **架构隔离（R20）：** `#stage`/`#track`/`translateX` 导航仅 Blue Sky 可用。其他风格必须使用 `scroll-snap-type: y mandatory` + `SlidePresentation` 类
6. **叙事弧线（R23）：** 根据 deck_type 检测页数完整性。连续两页不得使用相同布局模式。每页必须使用 2-3 种不同组件类型
7. **风格签名注入（R24）：** 风格文件的 Signature Elements（overlays/keyframes/required classes/background/rules）+ Typography + Components 章节的 CSS **全部**插入 `<style>` 中。不得遗漏 Signature Checklist 任何一项。缺失即生成错误。Blue Sky 例外：使用 blue-sky-starter.html 基底
8. **字体（R25+R28）：** Google Fonts URL 合并为单一链接（`&display=swap`），`<style>` 开头必须有 `body { background-color: ... }` 回退色。CJK 页面（`lang="zh"`/`ja"`/`ko"`）必须追加对应 CJK 字体（中文→`Noto Sans SC`，日文→`Noto Sans JP`，韩文→`Noto Sans KR`），fallback 链必须包含该字体
9. **布局分类（R26）：** 每页遵循 layout classification — P1 Hero / P2 Problem / P3 Discovery / P4 Solution(大数字/极简, density 35-45%) / P5+ 按叙事角色分配。Chinese Chan / Paper & Ink 允许布局重复
10. **功能完整性（GC-1+GC-3）：** 必须包含 `PresentMode` 类 + `F5` 监听 + `body.presenting` CSS（缺失即生成错误）。水印由 JS 注入到最后一页，CSS `position: absolute`，禁止 `position: fixed` 和硬编码
11. **CSS 工程（R29+R30）：** 每页 `id="slide-N"`，布局/背景/间距通过 `#slide-N` CSS 选择器定义，inline `style=""` ≤ 5 处。5 项通用 UI 强制存在：① `#brand-mark` ② `.slide-num-label`/`.light` ③ `.nav-dots` ④ `.progress-bar` ⑤ `id="slide-N"`。CSS 和 HTML 见 `references/base-css.md`

> 完整反模式映射表见 `references/impeccable-anti-patterns.md`。更多视觉/组件规则在 `--review` 模式下执行。

### 标题质量规则

标题必须是断言式，禁止通用标签。完整示例和模板见 `references/title-quality.md`。

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

**风格选择器** → `style-index.md` | **视口** → `base-css.md` | **质量** → `design-quality.md` | **反模式** → `impeccable-anti-patterns.md`

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
