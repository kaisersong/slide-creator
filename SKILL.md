---
name: kai-slide-creator
description: 生成零依赖 HTML 演示文稿 — 21 种设计预设，视觉风格探索，播放/演讲者模式。适用于路演、产品发布、技术分享等场景。
version: 2.12.0
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
- **内容 Review 系统** — 16 个检查点，精修模式自动执行

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
/slide-creator --review [file.html]  # 16 项检查点自动优化
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
| `--generate` | SKILL.md HARD RULES + `references/html-template.md` + 风格文件 + `base-css.md` | 从 PLANNING.md 生成 HTML，执行 16 项生成前校验 |
| `--review [file.html]` | `references/review-checklist.md` + 目标 HTML | 执行 16 项检查点 → 确认窗口 → 修复/报告 |
| 无 flag (交互式) | `references/workflow.md` + 其他按需 | 遵循 Phase 0-5（Phase 3 Step 7 必须执行 16 项校验） |
| 直接给内容 + 风格 | SKILL.md HARD RULES + `references/html-template.md` + 风格文件 + `base-css.md` | 立即生成，执行 16 项生成前校验 |

**渐进式披露：** 每个命令只加载所需文件。`--plan` 不接触 CSS。

---

## 生成契约

**每次生成的 HTML 必须包含播放模式和编辑模式（默认开启）。**

1. **播放模式** — F5 / ▶ 按钮，全屏缩放，`PresentMode` 类
2. **编辑模式** — 左上角热区，`✏ Edit` 开关，`contenteditable`，备注面板
3. **水印** — 右下角固定显示 `By kai-slide-creator v[version]`，`[version]` 从 SKILL.md frontmatter 读取，播放模式下隐藏

详见 `references/html-template.md`。**生成任何 HTML 前必读此文件**。

> 省略播放模式是生成错误。仅当用户明确选择「无需编辑」时可省略编辑模式。

---

### Pre-Write Validation Pipeline（生成前校验流水线）

这些规则在组装完整 HTML 后、写入文件前**自动执行**。逐条搜索违规项并修复。

**现有 8 项（HARD RULES Rule 1-7 + 标题质量）+ 9 项视觉/组件硬规则：**
1. 内容密度 ≥65%（Rule 1）
2. 列平衡 ≥60%（Rule 2）
3. 标题换行 ≤3 行（Rule 3）
4. 标题禁止通用标签（Rule 4）
5. 禁止连续 3 页同布局（Rule 5）
6. 三概念法则 ≤3（Rule 6）
7. 90/8/2 色彩律（Rule 7）
8. 标题质量（断言式，非通用标签）

**新增视觉硬规则（来自 impeccable-anti-patterns.md）：**
9. **U+FE0F 零容忍：** HTML 中不得出现 U+FE0F 变体选择符（emoji 使用基础形式）
10. **letter-spacing 上限：** 正文/列表/卡片元素的 `letter-spacing` 不得超过 `0.05em`
11. **纯黑背景禁用：** `#000` / `#000000` 背景 → 替换为 `#111` 或 `#18181B`
12. **bounce/elastic easing 禁用：** 检测 `ease.*back|bounce` → 替换为 `cubic-bezier(0.16, 1, 0.3, 1)`
13. **嵌套卡片：** 检测 `.card` / `.glass-card` 等容器内再嵌套同类容器 → 扁平化
14. **cramped padding：** 卡片/容器 padding < `0.75rem` → 增加到 ≥0.75rem
15. **gray text on colored bg：** 灰色文字（`#888`/`#999`/`var(--text-secondary)`）在非白色背景上 → 加深文字
16. **组件丰富度：** 检测整个 deck 中是否超过 50% 的幻灯片仅使用同一种组件模式（如全是 `.g` + `.bl`）→ 至少一半的幻灯片必须使用 2-3 种不同组件类型（step/callout/stat/kbd/table/callout/quote 等）

> 完整反模式映射表见 `references/impeccable-anti-patterns.md`。

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
| Blue Sky | `references/blue-sky-starter.html` |
| Aurora Mesh | `references/aurora-mesh.md` |
| Chinese Chan | `references/chinese-chan.md` |
| Data Story | `references/data-story.md` |
| Enterprise Dark | `references/enterprise-dark.md` |
| Glassmorphism | `references/glassmorphism.md` |
| Neo-Brutalism | `references/neo-brutalism.md` |
| 其他风格 | `STYLE-DESC.md` 相关章节 |
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
