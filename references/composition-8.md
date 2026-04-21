# Composition Guide — 8 页精简版（slide-creator 自身介绍）

用于 slide-creator 自身 demo 文件。所有 21 种预设的自我介绍演示均使用此 8 页结构。

---

## 叙事弧线（8 页）

| # | 叙事角色 | 布局分类 | 推荐组件模式 | 叙事目的 |
|---|---------|---------|-------------|---------|
| **1** | **Hero 封面** | 全屏宣告 | 产品名大字号 + 3 个 stat block（每种 accent 色一个）+ 风格签名元素 | 产品名 + 核心主张 + 关键数据 |
| **2** | **系统架构** | 分层堆叠图 | 3-4 层 `arch-layer`（INPUT → SKILL → OUTPUT）+ `arch-arrow`（↓）分隔 + 每层带 badge | 工作原理：内容输入 → 技能处理 → HTML 输出 |
| **3** | **核心功能** | 卡片网格 | 3 张 `feat-card`，每张带图标方块 + 标题 + 描述 + accent top border | 21 种预设 / 内联编辑 / 演讲者模式 |
| **4** | **Before/After** | 分栏对比 | 左右两栏各带 `ba-header` + `ba-list`（minus/green-plus 样式），中间分隔线 | 旧工具链 vs slide-creator 一句话出稿 |
| **5** | **宣言/哲学** | 暗色宣告块 | `manifesto-block` 大字号断言 + `points-list` 要点列表 | "一个命令。一个文件。零借口。" |
| **6** | **命令参考** | 数据表格 | `cmd-table`（命令列 + 描述列），4 行，`border-bottom` 分隔 | /slide-creator / --plan / --generate / --export |
| **7** | **数据指标** | 指标面板 | 3 列 `metric-block`，每列带 `metric-num` 大数字 + `px-bar` 进度条可视化 | 21 styles / 1 file / 0 dependencies |
| **8** | **CTA/安装** | 暗色行动块 | `close-block` 暗色背景 + 安装命令代码块 + 3 步 badge 流程 | git clone → /slide-creator → 发布 |

---

## 布局定义

### Slide 1 — Hero 封面

必须包含以下语义角色：
1. **主题标识** — badge/pill/section number/label（风格文件推荐形式）
2. **产品名** — 最突出的视觉锚点，可拆分强调（如 accent 色拆分关键词）
3. **副标题** — 1-2 行补充说明，与标题形成明暗层次
4. **3 个 stat block** — 每种 accent 色一个，block 容器包裹 headline + accent 高亮（如 "21 **种样式**" / "零 **依赖**" / "1 **HTML 文件**"）
5. **风格签名元素** — 至少一个该风格的标志性组件（ASCII 启动日志、终端日志、装饰图形等）

各角色的具体呈现方式遵循风格文件的 "Named Layout Variations" → Hero 推荐。

### Slide 2 — 系统架构

用分层堆叠图展示工作流程：
- **第 1 层（INPUT）** — "你的内容"：笔记、文档、BRIEF.json、图片、PPTX，accent 色半透明背景
- **↓ 箭头** — `arch-arrow` 连接
- **第 2 层（PROCESS）** — "/SLIDE-CREATOR"：样式发现 → 布局生成 → 代码质量检查
- **↓ 箭头** — `arch-arrow` 连接
- **第 3 层（OUTPUT）** — "PRESENTATION.HTML"：内联 CSS + JS · 编辑模式 · 演讲者模式 · PPTX 导出

每层右侧带对应 badge（输入/技能/输出），层间用 `margin-top: -3px` 重叠边框形成连贯堆叠感。

### Slide 3 — 核心功能

3 列卡片网格，每张 `feat-card`：
- 顶部行：headline 标题 + 图标方块（右上角）
- 中间：`comment` 描述行
- 底部：`body-text` 详细说明
- accent top border（3 种不同 accent 色各一张）

### Slide 4 — Before/After

左右分栏（`flex-direction: row`）：
- **左栏（BEFORE）** — `ba-header.bad`（灰色）+ `ba-list`，每个 `li.minus` 带灰色左边框 + `text-decoration: line-through`
- **右栏（AFTER）** — `ba-header.good`（绿色/accent）+ `ba-list`，每个 `li.plus` 带绿色左边框
- 中间：`border-left: 4px solid var(--border)` 分隔
- 每项内容：`border: 2px solid var(--border)` + `box-shadow: 2px 2px 0 var(--border)` 硬边风格

### Slide 5 — 宣言/哲学

单个 `manifesto-block`（暗色背景）：
- 大字号 headline：3-4 行断言式文案（如 "一个命令。一个文件。零 借口。"），关键词用 accent 色高亮
- `points-list`：4 条 `comment` 要点，每行一句话哲学

### Slide 6 — 命令参考

`cmd-table` 表格：
- 第 1 列（35% 宽）：命令名，用不同 accent 色区分主命令和 flag
- 第 2 列（65% 宽）：描述，1-2 行说明
- 行分隔：`border-bottom: 2px solid var(--border)`
- 交替行背景色（odd/even）
- 第 1 列右侧：`border-right: 2px solid var(--border)` 分隔命令和描述

### Slide 7 — 数据指标

3 列 `metric-block`：
- `metric-num`：超大数字（`clamp(3.5rem,8vw,6.5rem)`），accent 色
- headline h-sm：指标名
- `comment`：副说明
- `px-bar-wrap`：进度条可视化组，每行 `px-bar` + `px-label`，条宽百分比表达相对关系

### Slide 8 — CTA/安装

单个 `close-block`（暗色背景）：
- badge 标识（如 "安装"）
- 大 headline："开始使用" + accent 色高亮 "只需 30 秒"
- 安装命令代码块：`border: 2px solid rgba(255,255,255,0.15)` + 半透明背景
- 3 步 badge 流程：步骤 1 → → 步骤 2 → → 步骤 3，箭头用 monospace "→"
- 底部 `comment`：收尾标语

---

## 密度规则

| 页码 | 目标密度 |
|------|---------|
| 1 (Hero) | 40-50% |
| 2 (Architecture) | 55-65% |
| 3 (Features) | 60-70% |
| 4 (Before/After) | 50-60% |
| 5 (Manifesto) | 35-45% |
| 6 (Commands) | 55-65% |
| 7 (Metrics) | 60-70% |
| 8 (CTA) | 45-55% |

