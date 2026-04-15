---
name: kai-slide-creator
description: 生成零依赖 HTML 演示文稿 — 21 种设计预设，视觉风格探索，播放/演讲者模式。适用于路演、产品发布、技术分享等场景。
version: 2.17.0
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
| `--generate` | SKILL.md HARD RULES + `references/html-template.md` + `references/composition-guide.md` + 风格文件 + `base-css.md` | 从 PLANNING.md 生成 HTML，执行 16 项生成前校验 |
| `--review [file.html]` | `references/review-checklist.md` + 目标 HTML | 执行 16 项检查点 → 确认窗口 → 修复/报告 |
| 无 flag (交互式) | `references/workflow.md` + 其他按需 | 遵循 Phase 0-5（Phase 3 Step 7 必须执行 16 项校验） |
| 直接给内容 + 风格 | SKILL.md HARD RULES + `references/html-template.md` + `references/composition-guide.md` + 风格文件 + `base-css.md` | 立即生成，执行 16 项生成前校验 |

**渐进式披露：** 每个命令只加载所需文件。`--plan` 不接触 CSS。

---

## 生成契约

**每次生成的 HTML 必须包含播放模式和编辑模式（默认开启）。**

1. **播放模式** — F5 / ▶ 按钮，全屏缩放，`PresentMode` 类
2. **编辑模式** — 左上角热区，`✏ Edit` 开关，`contenteditable`，备注面板
3. **水印** — 由 JS 注入到**最后一页幻灯片**（`slides[slides.length - 1].appendChild`），CSS 使用 `position: absolute`，禁止 `position: fixed`。播放模式下隐藏，HTML 源码中不得出现 `<div class="slide-credit">` 硬编码在 `</body>` 前
4. **风格强制** — 所有 CSS 主题值（颜色、字体、图表色等）**必须且只能**来自选中的风格参考文件。模板 `html-template.md` 中的占位符（`[from style file]`）和注释示例值仅为结构示意，**禁止直接使用**。生成后对照风格文件的 checklist 验证。
5. **叙事弧线** — 所有 demo 必须遵循 `references/composition-guide.md` 定义的 12 页叙事结构（Hero → Problem → Discovery → Solution → Playback → Presenter → Edit → Planning → Review → Style Guide → Technical → CTA）。每页必须有独特的布局模式，禁止连续两页使用相同布局。每页必须使用风格参考文件中 2-3 种不同的组件类型。如果每页都是"卡片+列表"，是生成错误。

详见 `references/html-template.md`。**生成任何 HTML 前必读此文件**。

> 省略播放模式是生成错误。仅当用户明确选择「无需编辑」时可省略编辑模式。

---

### Pre-Write Validation Pipeline（生成前校验流水线）

这些规则在组装完整 HTML 后、写入文件前**自动执行**。逐条搜索违规项并修复。

**现有 8 项（HARD RULES Rule 1-7 + 标题质量）+ 16 项视觉/组件硬规则：**
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
15. **light text on light bg：** 浅色文字（`#888`/`#999`/`#cbd5e1`/`var(--text-secondary)`）在浅色背景（`#f0f4f8`/`#fef3c7`/`#e8f5e9`/`#fff` 等亮度 >60% 的颜色）上 → 加深文字为深色（`#1e293b`/`#334155`）或覆盖 `color: inherit` 到卡片上
16. **组件丰富度：** 检测整个 deck 中是否超过 50% 的幻灯片仅使用同一种组件模式（如全是 `.g` + `.bl`）→ 至少一半的幻灯片必须使用 2-3 种不同组件类型（step/callout/stat/kbd/table/callout/quote 等）
17. **SVG 箭头连线可见：** `<line>` 元素的起点和终点距离必须 ≥30px，确保线段可见。箭头从外框边缘指向中心图形边缘（如圆外切点），不得指向圆心或进入圆内部。下侧/右侧/左侧的箭头都需要足够的连线长度，rect 位置应与圆保持 ≥30px 间距
18. **播放模式 JS：** 必须包含 `PresentMode` 类或 `enterPresent()` 函数，且存在 `F5` 键监听器、`#present-btn` CSS、`body.presenting` CSS。缺失即生成错误
19. **水印位置：** 水印必须由 JS 注入到最后一页（`slides[slides.length - 1].appendChild`），CSS 必须是 `position: absolute`，禁止 `position: fixed`，禁止 `<div class="slide-credit">` 硬编码在 `</body>` 前
20. **架构隔离（非 Blue Sky 风格）：** 检测 `#stage`、`#track`、`calc(100vw * var(--slide-count))`、`translateX` 幻灯片导航 — 仅 Blue Sky 风格可使用这些模式。其他 20 个风格必须使用 `html-template.md` 的 `scroll-snap-type: y mandatory` + `SlidePresentation` 类架构。发现违规立即替换为 scroll-snap 模式
21. **`.slide` 背景透明度：** 当风格参考文件中 `body` 定义了 `radial-gradient`、`linear-gradient`、`background-image` 图案或 `animation` 背景时，`.slide` 不得设置 `background` / `background-color` 覆盖体渐变——必须移除 `.slide` 的 `background` 声明，让 `body` 渐变透出来。通用模板建议的 `background: var(--bg-primary)` 安全网对此类风格不适用
22. **Chinese Chan 幽灵汉字必须贴页面边角：** `.zen-ghost-kanji` 是底纹元素，必须放在 `.slide-content` 容器之外（作为 `.slide` 的直接子元素），使其 `position: absolute` 的 `right: -0.1em; bottom: -0.1em` 定位基准是 `.slide`（整个页面），而非 600px 内容块。禁止放在 `.slide-content` 内部，禁止使用 `left: 50%`、`top: 50%`、`translateX(-50%)` 等居中定位
23. **叙事弧线完整性：** 检测幻灯片是否遵循 12 页叙事结构（Hero → Problem → Discovery → Solution → Playback → Presenter → Edit → Planning → Review → Style Guide → Technical → CTA）。标题不得全部使用通用标签（概览、Overview、Introduction、Summary 等）。连续两页不得使用相同布局模式（如连续 grid 3 列、连续 split panel、连续 2 列卡片）。每页必须使用风格参考文件中定义的 2-3 种不同组件类型，不得仅用通用 `div` + `ul` 堆砌
24. **风格签名元素完整性（全部 21 风格）：** 读取选中风格的参考文件 `## Signature Elements` 章节，检查 HTML 中是否注入了对应的签名元素。按风格逐一检查：
    - **Bold Signal:** 每页 `.slide-num`（左上角大数字）+ `.breadcrumb`（右上角面包屑）+ `.slide::after` 网格叠加
    - **Enterprise Dark:** `.slide::after` 网格叠加（24px 间距，rgba(48,54,61,0.3)）
    - **Neon Cyber:** `.slide::after` 青色网格叠加（40px 间距，rgba(0,255,255,0.06)）
    - **Terminal Green:** `.slide::after` 扫描线叠加（repeating-linear-gradient，rgba(0,255,65,0.03)）
    - **Creative Voltage:** `.slide::after` halftone 点阵（radial-gradient circle，rgba(212,255,0,0.08)）
    - **Dark Botanical:** 每页 2-3 个 `.botanical-orb` 元素（terracotta/pink/gold 渐变软光球，200-400px）
    - **Glassmorphism:** 每页 3 个 `.glass-orb` 元素 + 卡片 `backdrop-filter: blur(12px)`
    - **Swiss Modern:** `.slide::after` 12 列网格叠加 + 硬水平规则 `2px solid #0a0a0a`
    - **Neo-Retro Dev:** `.slide::after` 方格纸网格（20px 间距，rgba(70,130,180,0.08)，cream `#f5f2e8` 背景）
    - **Chinese Chan:** 每页最多 1 个装饰元素（`.zen-rule` / `.zen-ghost-kanji` / `.zen-dot`），不得更多
    - **Aurora Mesh:** body 上 mesh gradient 4-6 色标 + 卡片 `backdrop-filter: blur(12px)`，无 Google Fonts
    - **Data Story:** 数据组件（`.chart-container` / `.data-callout` / `.data-stat`），无背景图案
    - **Electric Studio:** 双面板垂直分割 + `.accent-bar`（4px 宽，var(--accent)），Manrope 字体
    - **Modern Newspaper:** 黄色条 `#FFCC00`（8-14px）+ 列规则 `1px solid #111` + issue stamp（`VOL.01 · NO.03`）
    - **Neo-Brutalism:** 所有容器 `box-shadow: 4px 4px 0 #000` + `border-radius: 0` + `border: 3px solid #000`
    - **Notebook Tabs:** 彩色竖排标签（右侧 edge）+ 纸张容器阴影 + 左侧 binder hole 装饰
    - **Paper & Ink:** 窄列布局（max-width ~680px 居中），无背景图案，纯 typography + rule divider
    - **Pastel Geometry:** 白卡（border-radius: 20px）在粉蓝渐变背景上 + 右侧垂直 pills（不同高度）
    - **Split Pastel:** 双色分割背景（peach 左 / lavender 右）+ 右面板网格叠加 + badge pills
    - **Vintage Editorial:** cream `#f5f0e8` 背景 + 抽象几何（circle outline + line + dot）+ Cormorant italic
    - **Blue Sky:** 使用 `blue-sky-starter.html` 作为基础，所有签名元素（orbs / clouds / glass cards）已预建
    如果风格参考文件定义了背景纹理但 HTML 中缺失，即生成错误
25. **字体加载无白屏：** 检查 Google Fonts URL 是否合并为单一链接（`&display=swap`），且 `<style>` 开头是否有 `body { background-color: ... }` 回退色。多个 `<link>` 标签加载字体 = 生成错误
26. **布局分类一致性：** 检查每页是否遵循 `composition-guide.md` 的布局分类映射（Hero = 全屏宣告，Problem = 分栏证据，Solution = 大数字强调，CTA = 堆叠行动等）。Hero 页必须有装饰元素（大数字/几何/图形），不能只是"标题+列表"。CTA 页必须有堆叠命令/链接，不能只是"标题+列表"。Chinese Chan / Paper & Ink 允许布局重复（极简主义哲学），但其他风格至少一半的幻灯片必须使用 2-3 种不同组件类型
27. **卡片内文字对比度（亮色卡片）：** 检测 `background: var(--card-bg)` 或高亮度纯色背景（`#FF5722`、`#FFEB3B`、`#0066ff` 等亮度 >40% 的颜色）的容器及其所有子元素。容器内不得出现 `color: #1a1a1a`、`rgba(26,26,26,*)`、`#333`、`#222` 等深色文字——必须使用 `color: var(--text-on-card)` 或 `rgba(255,255,255,*)` 等浅色文字。同样，暗色背景容器内不得出现深色文字。检测范围包括 CSS 类和 inline `style="color: ..."` 属性。这是三层问题：(1) 风格参考文件中 `--text-on-card` 变量定义错误 → 修复参考文件；(2) CSS 变量继承错误 → 修复 `:root`；(3) inline style 直接写死深色值覆盖变量 → 替换为 `var(--text-on-card)` 或 `rgba(255,255,255,*)`

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
