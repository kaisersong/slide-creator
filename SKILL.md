---
name: kai-slide-creator
description: 生成零依赖 HTML 演示文稿 — 21 种设计预设，视觉风格探索，播放/演讲者模式。适用于路演、产品发布、技术分享等场景。
version: 2.10.0
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
| `--generate` | `references/html-template.md` + 风格文件 + `base-css.md` + `design-quality.md` | 从 PLANNING.md 生成 HTML |
| `--review [file.html]` | `references/review-checklist.md` + 目标 HTML | 执行 16 项检查点 → 确认窗口 → 修复/报告 |
| 无 flag (交互式) | `references/workflow.md` + 其他按需 | 遵循 Phase 0-5（仅精修模式执行 Phase 3.5 Review） |
| 直接给内容 + 风格 | `references/html-template.md` + 风格文件 + `base-css.md` | 立即生成，无需 Phase 1/2 |

**渐进式披露：** 每个命令只加载所需文件。`--plan` 不接触 CSS。

---

## 生成契约

**每次生成的 HTML 必须包含播放模式和编辑模式（默认开启）。**

1. **播放模式** — F5 / ▶ 按钮，全屏缩放，`PresentMode` 类
2. **编辑模式** — 左上角热区，`✏ Edit` 开关，`contenteditable`，备注面板
3. **水印** — 右下角固定显示 `By kai-slide-creator v[version]`，`[version]` 从 SKILL.md frontmatter 读取，播放模式下隐藏

详见 `references/html-template.md`。**生成任何 HTML 前必读此文件**。

> 省略播放模式是生成错误。仅当用户明确选择「无需编辑」时可省略编辑模式。

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
