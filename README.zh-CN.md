# slide-creator

> 很多人有很好的内容，却无法有效地展现。虽然大模型现在能帮你写 PPT，但输出效果不稳定，多次抽卡又很头疼。Slide-Creator 帮助你简单、稳定地输出演示文稿——根据场景选择喜欢的风格即可，其他的就让大模型去干，喝杯咖啡吧。
>
> **[看这份指南本身生成的报告 →](https://kaisersong.github.io/slide-creator/demos/blue-sky-zh.html)** — 本文档由 slide-creator 自己生成。

适用于 [Claude Code](https://claude.ai/claude-code) 和 [OpenClaw](https://openclaw.ai) 的演示文稿生成技能，零依赖、纯浏览器运行的 HTML 幻灯片。

[English](README.md) | 简体中文

---

## 效果展示

用浏览器直接打开，零安装查看效果：

- 🇨🇳 [slide-creator 介绍（中文）](https://kaisersong.github.io/slide-creator/demos/blue-sky-zh.html)
- 🇺🇸 [slide-creator intro (English)](https://kaisersong.github.io/slide-creator/demos/blue-sky-en.html)

点击下方任意截图可打开对应的在线演示（内容相同，风格不同）：

<table>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/blue-sky-zh.html"><img src="demos/screenshots/blue-sky.png" width="240" alt="Blue Sky"/></a><br/><b>Blue Sky</b></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/bold-signal-zh.html"><img src="demos/screenshots/bold-signal.png" width="240" alt="Bold Signal"/></a><br/><b>Bold Signal</b></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/electric-studio-zh.html"><img src="demos/screenshots/electric-studio.png" width="240" alt="Electric Studio"/></a><br/><b>Electric Studio</b></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/creative-voltage-zh.html"><img src="demos/screenshots/creative-voltage.png" width="240" alt="Creative Voltage"/></a><br/><b>Creative Voltage</b></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/dark-botanical-zh.html"><img src="demos/screenshots/dark-botanical.png" width="240" alt="Dark Botanical"/></a><br/><b>Dark Botanical</b></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/notebook-tabs-zh.html"><img src="demos/screenshots/notebook-tabs.png" width="240" alt="Notebook Tabs"/></a><br/><b>Notebook Tabs</b></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/pastel-geometry-zh.html"><img src="demos/screenshots/pastel-geometry.png" width="240" alt="Pastel Geometry"/></a><br/><b>Pastel Geometry</b></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/split-pastel-zh.html"><img src="demos/screenshots/split-pastel.png" width="240" alt="Split Pastel"/></a><br/><b>Split Pastel</b></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/vintage-editorial-zh.html"><img src="demos/screenshots/vintage-editorial.png" width="240" alt="Vintage Editorial"/></a><br/><b>Vintage Editorial</b></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/neon-cyber-zh.html"><img src="demos/screenshots/neon-cyber.png" width="240" alt="Neon Cyber"/></a><br/><b>Neon Cyber</b></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/terminal-green-zh.html"><img src="demos/screenshots/terminal-green.png" width="240" alt="Terminal Green"/></a><br/><b>Terminal Green</b></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/swiss-modern-zh.html"><img src="demos/screenshots/swiss-modern.png" width="240" alt="Swiss Modern"/></a><br/><b>Swiss Modern</b></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/paper-ink-zh.html"><img src="demos/screenshots/paper-ink.png" width="240" alt="Paper & Ink"/></a><br/><b>Paper & Ink</b></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/aurora-mesh-zh.html"><img src="demos/screenshots/aurora-mesh.png" width="240" alt="Aurora Mesh"/></a><br/><b>Aurora Mesh</b></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/enterprise-dark-zh.html"><img src="demos/screenshots/enterprise-dark.png" width="240" alt="Enterprise Dark"/></a><br/><b>Enterprise Dark</b></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/glassmorphism-zh.html"><img src="demos/screenshots/glassmorphism.png" width="240" alt="Glassmorphism"/></a><br/><b>Glassmorphism</b></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/neo-brutalism-zh.html"><img src="demos/screenshots/neo-brutalism.png" width="240" alt="Neo-Brutalism"/></a><br/><b>Neo-Brutalism</b></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/chinese-chan-zh.html"><img src="demos/screenshots/chinese-chan.png" width="240" alt="Chinese Chan"/></a><br/><b>Chinese Chan</b></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/data-story-zh.html"><img src="demos/screenshots/data-story.png" width="240" alt="Data Story"/></a><br/><b>Data Story</b></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/modern-newspaper-zh.html"><img src="demos/screenshots/modern-newspaper.png" width="240" alt="Modern Newspaper"/></a><br/><b>Modern Newspaper</b></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/neo-retro-dev-zh.html"><img src="demos/screenshots/neo-retro-dev.png" width="240" alt="Neo-Retro Dev Deck"/></a><br/><b>Neo-Retro Dev Deck</b></td>
</tr>
</table>

---

## 设计理念：Skills 作为领域 Harness 工程

本节介绍 slide-creator 的设计原则——既包括作为用户工具的设计，也包括作为 Claude Code 技能的设计。这些原则对任何编写技能的人都有参考价值。

### 一、渐进式披露

技能文件每次被调用时，会完整加载到 AI 的上下文窗口中。文件大小直接影响 AI 的专注程度。

slide-creator 的解法是：**SKILL.md 是一个精简的指令路由层（约 150 行）**，将每条指令分发到所需的最小参考文件集合：

```
--plan        → 只读 references/planning-template.md
--generate    → references/html-template.md + 单个风格文件 + base-css.md
交互模式      → references/workflow.md（完整 Phase 1–5）
风格选择      → references/style-index.md（21 个预设 + 心情映射）
```

**最终效果：** `--plan` 调用从不接触 CSS。`--generate` 运行时从不加载其他 20 种风格描述。导出能力继续放在独立的 `kai-html-export` 技能里。

这是渐进式披露原则在 AI 上下文管理中的应用：**在需要信息的那一刻才披露，而不是提前全部加载**。好的 UX 设计原则同样适用于好的 AI 技能设计。

### 二、以视觉代替语言：Show, Don't Tell

大多数人在没有看到样例之前，无法用语言描述自己的设计偏好。问"你想要极简风还是大胆风？"只会得到模糊的答案。生成三个 50 行的 HTML 预览，然后问"你更喜欢哪个？"，用户会立即做出反应。

Phase 2 正是围绕这一洞察设计的。当用户看到自己的内容标题以三种截然不同的设计语言呈现时，那种"wow 时刻"会把一个抽象的选择变成一种直觉体验。预览文件故意做得很小（约 50 行，自包含），几秒即可生成。

这正是 slide-creator 强调"以视觉代替语言"而非"提供 21 个主题"的原因。功能不产生参与感，选择的体验才会。

### 三、视口适配作为硬约束

演示文稿中途出现滚动条，意味着这个幻灯片是坏的。这听起来显而易见，但在生成 HTML 时很容易犯错——如果一张幻灯片内容太多，浏览器会直接溢出显示。

slide-creator 将视口适配视为**不可妥协的硬约束**：

- 每个 `.slide` 必须有 `height: 100vh; overflow: hidden;`
- 按幻灯片类型规定了内容密度上限（例如最多 6 条要点、最多 6 个网格卡片）
- 内容超出时，规则永远是：**拆分幻灯片，不要压缩**

基础 CSS 对所有尺寸使用 `clamp()`，从横屏手机到 4K 显示器均可优雅缩放。CSS 陷阱备注栏也正因此而存在——`calc(-1 * clamp(...))` 与 `-clamp(...)` 的区别是一种静默失败，没有控制台报错，只是布局悄悄出了问题。

### 四、自定义主题系统：可组合的设计语言

`themes/` 目录允许任何用户以自己的品牌风格扩展 slide-creator。只需在 `themes/your-theme/` 目录中放入一个 `reference.md` 描述视觉系统，它就会立即以"Custom: folder-name"的形式出现在风格选择列表中。

两文件约定（`reference.md` + 可选的 `starter.html`）与 Blue Sky 模式一致：
- `reference.md` 描述设计语言（颜色、字体、组件类）
- `starter.html` 是复杂视觉系统的完整模板（带动画背景、自定义 JS、非常规布局系统）

简单的自定义主题只需一个文件，而复杂主题则可以附带完整的工作模板。

### 五、内容类型路由：有意义的智能默认值

21 个预设的数量足够丰富，同时又经过精心筛选。slide-creator 通过内容类型映射来推荐风格，而非让用户浏览所有选项：

```
数据报告 / KPI 看板    → Data Story、Enterprise Dark、Swiss Modern
商业路演 / VC Deck     → Bold Signal、Aurora Mesh、Enterprise Dark
开发工具 / API 文档    → Terminal Green、Neon Cyber、Neo-Retro Dev Deck
```

SKILL.md 中的这张路由表同时服务两类受众：希望获得合理起点的人类用户，以及以编程方式调用技能时可能知道内容类型但不知道选哪种风格的 AI 智能体。

### 六、设计质量基准：拒绝 AI 烂稿

AI 生成幻灯片最常见的失败模式，不是 CSS 错误或配色问题——而是**意外的空洞感**。两条要点居中悬浮在整张幻灯片里，或者两栏布局中一栏放了四条内容、另一栏只有一条，不管设计系统多精致，看起来都像是没做完的半成品。

`references/design-quality.md`（在 `--generate` 阶段与风格文件一起加载）收录了一套规则，强制模型根据**内容密度**做布局决策：

**最低填充率规则。** 每张幻灯片必须使用至少 65% 的页面区域。内容稀少时，模型必须切换布局类型——而不是把内容居中就交差：

```
2 条要点      → 改用引言/大数字布局，或把每条扩写成 2 行陈述
1 个核心洞察  → 大引言 / 单一数字 / 视觉处理的宣言页
3 条细要点    → 每条补充支撑细节，或切换为三卡片网格
```

关键区别：*刻意的*留白（精心排版的呼吸页，用大字号、特意留白）是设计决策；*意外的*留白（内容漂浮在半空页面中间）是生成失误。

**多栏平衡规则。** 两栏或三栏布局中，任意一列的高度不得低于最高列的 60%。内容不均衡时，必须从三种修复路径中选择其一：为较短的列补充支撑内容、改为有明确视觉目的的非对称布局（如 `2fr 1fr`），或合并为单栏。

**90/8/2 配色法则。** 90% 中性底色，8% 结构强调色（最多用于 3 类元素），2% 点睛强调色（1-2 处精准点击）。这条规则防止了常见的"强调色泛滥"——每个标题、每个图标、每条边框、每个按钮都用强调色，结果产生视觉噪音而非层次感。

**禁止连续 3 张纯要点页。** 出现两张要点列表幻灯片后，下一张必须是视觉锚点：单个大数字、引用、图表，或布局突破页。这是认知节奏规则，而非审美偏好——密集列表缺乏视觉喘息会让读者失去专注。

**内容语调配色校准。** 规划模板根据内容类型推荐语调匹配的强调色：

```
沉思 / 研究类   → #7C6853 暖棕色（接地气、编辑感）
技术 / 工程类   → #3D5A80 深海军蓝（精确、权威）
商业 / 数据类   → #0F7B6C 深青绿（自信、前瞻）
叙事 / 年报类   → #B45309 琥珀色（温暖、动势）
```

**生成前自检门控。** 输出最终 HTML 前，模型执行六道自检：视口溢出、最低填充率、列平衡、配色法则合规、连续要点页规则，以及防烂稿终极问题：*"如果告诉别人'这是 AI 做的'，他们会立刻信吗？"* 如果是，先修改再输出。

### 七、内容 Review 系统：超越视觉的质量基准

设计质量基准（第六节）解决视觉烂稿。但 AI 生成幻灯片还有一个更深层问题：**内容烂稿**——标题是名词短语而非判断句、前三页没有量化收益、技术黑话没有类比翻译。

内容 Review 系统引入 16 个检查点，分为两类：

**第一类：可自动检测（6 个检查点）** 可编程识别：
- 视角翻转（第一人称 → 以听众为中心）
- 结论先行（名词短语标题 → 判断句）
- 三概念法则（每页最多 3 个新概念）
- 布局轮换（禁止连续 3 张同布局幻灯片）
- 字号底线
- 视觉层次（眯眼测试）

**第二类：AI 建议（10 个检查点）** 需要 AI 判断：
- 痛点前置（前 2 页展示真实用户痛点）
- 量化收益（前 3 页应有数字/百分比）
- MECE 原则（步骤定义不重叠）
- 奥卡姆剃刀（删除无关内容）
- 注意力重置（每 8-10 页干货插入喘息点）
- 张力对比（旧方法/新方法、痛点/方案）
- 留白缓冲页
- 黑话降维（术语首次出现需类比）
- 图像/图表降噪

**三种规则类型，执行策略不同：**

| 类型 | 触发条件 | 示例 |
|---|---|---|
| **硬规则** | 始终 | 布局轮换、字号底线 |
| **情境规则** | 根据内容类型 | 提案用判断句标题，简介保持名词短语 |
| **建议规则** | 仅提示 | "建议此处补充案例" |

**为什么情境规则重要：** "slide-creator 简介"这类简介型标题应保持名词短语。"XX 架构概览"这类提案型标题应改为"XX 架构可确保流量峰值零遗漏"。同样规则根据内容类型和用户意图表现不同。

**量化收益检测：** 如果内容包含数字（"效率提升约 40%"），提取并提升到前 3 页展示。如果无数字，Review 时提示——不硬编。

**生成时内嵌：** 这些规则应在 Phase 3 生成阶段（精修模式）内嵌执行，而非事后应用。质量保障左移——在问题产生前就预防。

---

## 安装

### Claude Code

对 Claude 说：「安装 https://github.com/kaisersong/slide-creator」

或手动：
```bash
git clone https://github.com/kaisersong/slide-creator ~/.claude/skills/slide-creator
```

重启 Claude Code，使用 `/slide-creator` 调用。

### OpenClaw

```bash
# 通过 ClawHub 安装（推荐）
clawhub install kai-slide-creator

# 或手动克隆
git clone https://github.com/kaisersong/slide-creator ~/.openclaw/skills/slide-creator
```

> ClawHub 页面：https://clawhub.ai/skills/kai-slide-creator

---

## 使用方式

### 基本命令

```
/slide-creator --plan       # 分析内容和 resources/ 目录，生成 PLANNING.md 大纲
/slide-creator --generate   # 根据 PLANNING.md 生成 HTML 演示文稿
/slide-creator --review     # 诊断并修复内容质量问题
/slide-creator              # 从零开始（交互式风格探索）
/kai-html-export            # 导出为 PPTX 或 PNG（独立技能）
```

### 规划深度

- `自动（Auto）` — 快速路径；跳过 Phase 3.5 Review
- `精修（Polish）` — 深度路径；自动执行 Phase 3.5 Review

同一份内容在 `自动` 与 `精修` 之间切换时，除非用户明确要求换风格，否则应保持相同 preset。

### 典型工作流

**方式一：交互式创建**
1. 运行 `/slide-creator`，回答目的、长度、内容和图片四个问题
2. 查看 3 个风格预览，选择喜欢的风格
3. 生成完整演示文稿，在浏览器中打开

**方式二：两阶段工作流（复杂内容推荐）**
1. 在项目目录放入素材（`resources/` 文件夹）
2. 运行 `/slide-creator --plan 我的AI创业公司融资路演`
3. 审阅 `PLANNING.md` 大纲，确认后运行 `/slide-creator --generate`

**方式三：PPT 转换**
1. 将 `.pptx` 文件放到当前目录
2. 运行 `/slide-creator`，技能会自动识别并提取内容

### Review 模式

```
/slide-creator --review presentation.html
```

**Review 行为：**
1. 加载 `references/review-checklist.md`
2. 执行全部 16 个检查点（6 个可自动检测 + 10 个 AI 建议）
3. 展示结果：✅ 通过 / 🔧 可自动修复 / ⚠️ 需确认 / ❌ 需人工判断
4. 用户选择：[全部自动修复] / [逐项确认] / [跳过]
5. 输出修复后 HTML + 诊断报告

**精修模式**：Phase 3.5 Review 在生成后自动执行。
**自动模式**：跳过 Phase 3.5。

### 耗时参考

端到端预计耗时：

- `自动（Auto）`：通常约 3-6 分钟
- `精修（Polish）`：通常约 8-15 分钟

---

## 功能特性

### 核心功能

- **两阶段工作流** — `--plan` 生成大纲，`--generate` 输出幻灯片
- **两种规划深度** — `自动` 适合快速出稿，`精修` 适合更强叙事和视觉锁定
- **内容 Review 系统** — 16 个质量检查点：`--review` 按需诊断；精修模式自动执行 Review
- **21 种设计预设** — 每种风格含命名布局变体
- **内容类型智能路由** — 根据路演、开发工具、数据报告等自动推荐风格
- **视觉风格探索** — 先生成 3 个预览，看图选风格而非描述风格
- **内联 SVG 图表** — 流程图、时间轴、条形图、对比矩阵、组织架构图，无需外部库
- **Blue Sky Starter 模板** — 完整 boilerplate，任何模型都能正确实现全套视觉系统

### 交互功能

- **播放模式** — 按 `F5` 或点击右下角 ▶ 按钮进入全屏播放；幻灯片缩放适配任意屏幕；控制栏自动隐藏；按 `Esc` 退出
- **演讲者模式** — 按 `P` 打开同步演讲者窗口：备注、计时器、页数、翻页导航；窗口高度随备注自动调整
- **备注编辑面板** — 编辑模式（`E` 键）下底部出现备注栏，点击标题可收起/展开，输入实时同步
- **浏览器内编辑** — 默认开启；直接在浏览器中编辑文字，Ctrl+S 保存
- **视口自适应** — 每张幻灯片精确填充 100vh，永不出现滚动条

### 输出功能

- **自定义主题系统** — 在 `themes/你的主题/` 放入 `reference.md` 即可添加专属预设；可选提供 `starter.html`
- **模板导出界面开关** — 在 `<body>` 上设置 `data-export-progress="false"`，同时隐藏进度条和导航点
- **图片处理流水线** — 自动评估和处理素材（Pillow）
- **PPT 导入** — 将 `.pptx` 文件转换为网页演示
- **PPTX / PNG 导出** — 通过 [kai-html-export](https://github.com/kaisersong/kai-html-export)
- **中英双语** — 完整支持中文内容

---

## 设计预设

| 预设 | 风格 | 适合场景 |
|------|------|----------|
| **Bold Signal** | 自信、强冲击 | 路演、主题演讲 |
| **Electric Studio** | 简洁、专业 | 商务演示 |
| **Creative Voltage** | 活力、复古现代 | 创意提案 |
| **Dark Botanical** | 优雅、精致 | 高端品牌 |
| **Blue Sky** | 清透、企业 SaaS | 产品发布、科技路演 |
| **Notebook Tabs** | 编辑感、有条理 | 报告、评审 |
| **Pastel Geometry** | 友好、亲切 | 产品介绍 |
| **Split Pastel** | 活泼、现代 | 创意机构 |
| **Vintage Editorial** | 个性鲜明 | 个人品牌 |
| **Neon Cyber** | 科技感、未来感 | 科技创业 |
| **Terminal Green** | 开发者风格 | 开发工具、API |
| **Swiss Modern** | 极简、精确 | 企业、数据 |
| **Paper & Ink** | 文学、沉思 | 叙事演讲 |
| **Aurora Mesh** | 鲜明、高端 SaaS | 产品发布、VC 融资路演 |
| **Enterprise Dark** | 权威、数据驱动 | B2B、投资者 deck、战略 |
| **Glassmorphism** | 轻盈、毛玻璃、现代 | 消费科技、品牌发布 |
| **Neo-Brutalism** | 大胆、不妥协 | 独立开发者、创意宣言 |
| **Chinese Chan** | 静谧、沉思 | 设计哲学、品牌、文化 |
| **Data Story** | 清晰、精确、说服力 | 业务回顾、KPI、数据分析 |
| **Modern Newspaper** | 犀利、权威、编辑感 | 业务报告、思想领导力演讲 |
| **Neo-Retro Dev Deck** | 有主见、技术感、手作风 | 开发工具发布、API 文档、黑客松 |

### Blue Sky

天空渐变背景（`#f0f9ff → #e0f2fe`）搭配浮动玻璃拟态卡片与动态环境光球。灵感来自真实的企业 AI 路演文稿（CloudHub V12 MVP），呈现出高空晴日般开阔、自信、精致的视觉气质。

标志性元素：SVG 颗粒噪声纹理叠层 · 3 个按幻灯片类型重新布阵的模糊光球 · `backdrop-filter: blur(24px)` 玻璃拟态卡片 · 40px 科技网格底层 · 弹簧物理横向切换动画 · 封面专属双层流动云朵效果。

**为什么 Blue Sky 是 starter 模板范本：** 它预置了全部 10 个签名视觉元素，模型只需填充幻灯片内容——没有误实现设计系统的风险。这种 `reference.md` + `starter.html` 的模式对任何复杂主题都可复用。

---

## 创建自定义主题

1. 创建 `themes/你的主题/` 目录
2. 编写 `reference.md`，描述：
   - 颜色（主色、强调色、中性色）
   - 字体（字体、字重、字号）
   - 布局模式（卡片、网格、全出血）
   - 组件类（如需自定义 CSS）
3. 可选添加 `starter.html` 用于复杂视觉系统（动画背景、自定义 JS、非常规布局）

你的主题会以"Custom: 你的主题"出现在风格选择列表中。

**附带的品牌主题示例：** `themes/cloudhub/` 和 `themes/kingdee/`

---

## 品牌风格迁移

将现有 `.pptx` 迁移到自定义品牌设计——同时输出像素级归档版和可编辑版。

```bash
# 第一步——风格迁移
/slide-creator --plan "将 company-deck.pptx 迁移到我们的品牌风格"
/slide-creator --generate  # → branded-deck.html

# 第二步——两种模式导出
/kai-html-export branded-deck.html              # 像素级
/kai-html-export --pptx --mode native branded-deck.html  # 可编辑
```

---

## 依赖要求

slide-creator **无外部依赖**。Python 3 仅用于规划阶段可选的图片评估，无需安装任何 Python 包。

如需导出 PPTX 或 PNG：`clawhub install kai-html-export` 或 `pip install playwright python-pptx`

---

## 输出文件

- `presentation.html` — 零依赖单文件，直接用浏览器打开
- `PRESENTATION_SCRIPT.md` — 演讲稿（幻灯片 8 张以上时自动生成）

---

## 兼容性

| 平台 | 版本 | 安装路径 |
|------|------|----------|
| Claude Code | 任意 | `~/.claude/skills/slide-creator/` |
| OpenClaw | ≥ 0.9 | `~/.openclaw/skills/slide-creator/` |

---

## 版本日志

**v2.18.0** — JS 引擎抽取（html-template.md 从 557 行缩减到 222 行）；风格签名注入扩展为要求 Typography/Components 章节的所有 CSS 类；neon-cyber 光晕效果明确要求；风格一致性审计工具（`tests/audit_style_consistency.py`）。

**v2.17.0** — 风格参考系统重构；浅色背景对比度修复；glassmorphism 文字主题映射。

**v2.9.0** — 内容 Review 系统：16 个检查点（6 个可自动检测 + 10 个 AI 建议）；精修模式自动执行 Phase 3.5 Review；`--review` 命令支持按需诊断；三种规则类型（硬规则/情境规则/建议规则）。

**v2.8.0** — 将规划深度简化为两个面向用户的模式（自动/精修）；双语命名规则；耗时预期；preset 锁定规则；回归测试覆盖。

**v2.7.1** — 零依赖的 `check-doc-sync.py` 文档契约检查器，用于保持 SKILL.md、README.md 与 workflow.md 三处说明同步。

**v2.7.0** — Enhancement Mode 守则；浏览器内编辑默认开启但可关闭；附带品牌主题示例（`themes/cloudhub/`、`themes/kingdee/`）。

**v2.6.1** — 品牌风格迁移工作流文档。

**v2.6.0** — 设计质量基准（`references/design-quality.md`）：最低 65% 填充率、多栏平衡、90/8/2 配色法则、禁止连续 3 张纯要点页、内容语调配色校准、生成前自检门控。修复 aurora-mesh Inter 字体矛盾。

**v2.5.0** — 21 个预设 + Blue Sky starter 模板；Show Don't Tell 风格探索。

**v2.0.0** — 两阶段工作流（`--plan` / `--generate`）；浏览器内编辑；演讲者模式。

**v1.0.0** — 初始发布，10 个预设。