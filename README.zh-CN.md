# slide-creator

> 很多人有很好的内容，却无法有效地展现。虽然大模型现在能帮你写 PPT，但输出效果不稳定，多次抽卡又很头疼。Slide-Creator 帮助你简单、稳定地输出演示文稿——根据场景选择喜欢的风格即可，其他的就让大模型去干，喝杯咖啡吧 ☕

适用于 [Claude Code](https://claude.ai/claude-code) 和 [OpenClaw](https://openclaw.ai) 的演示文稿生成 skill，零依赖、纯浏览器运行的 HTML 幻灯片。

**v2.3.3** — Bug 修复：macOS 触摸板滑动不再连续翻页。将 deltaY 阈值方案替换为基于事件间隔时间的动量检测——macOS 惯性滚动事件间隔约 16ms，新的主动滑动必然存在 >80ms 的停顿。21 种风格全部更新。**v2.3.2** — Bug 修复：鼠标滚轮翻页现在可靠工作。**v2.3.1** — Bug 修复：方向键现在能正确渲染幻灯片。`goTo()` 手动切换 `.visible` 类，修复键盘导航时 IntersectionObserver 触发时机问题。PPTX/PNG 导出功能已解耦至独立技能 [kai-html-export](https://github.com/kaisersong/kai-html-export)。渐进式披露架构：SKILL.md 是轻量命令路由器，完整工作流按需加载。

[English](README.md) | 简体中文

## 效果演示

用浏览器直接打开，零安装查看效果：

- 🇨🇳 [slide-creator 介绍（中文）](https://kaisersong.github.io/slide-creator/demos/blue-sky-zh.html) — 功能和使用方式介绍
- 🇺🇸 [slide-creator intro (English)](https://kaisersong.github.io/slide-creator/demos/blue-sky-en.html) — same in English

以上两个演示使用 Blue Sky 风格。点击下方任意截图可打开对应的在线演示：

<table>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/blue-sky-zh.html"><img src="demos/screenshots/blue-sky.png" width="240" alt="Blue Sky"/></a><br/><b>Blue Sky</b> ✨</td>
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
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/paper-ink-zh.html"><img src="demos/screenshots/paper-ink.png" width="240" alt="Paper &amp; Ink"/></a><br/><b>Paper &amp; Ink</b></td>
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

所有演示文稿内容相同（均为 slide-creator 自我介绍），方便直观感受不同设计哲学的视觉差异。

---

## 功能特性

- **两阶段工作流** — `--plan` 生成大纲，`--generate` 输出幻灯片
- **21 种设计预设** — Bold Signal、Blue Sky、Modern Newspaper、Neo-Retro Dev Deck 等，每种风格含命名布局变体
- **内容类型智能路由** — 根据路演、开发工具、数据报告、编辑内容等自动推荐最匹配的风格
- **视觉风格探索** — 先生成 3 个预览，看图选风格而非描述风格
- **播放模式** — 按 `F5` 或点击右下角 ▶ 按钮进入全屏播放模式；幻灯片缩放适配任意屏幕；控制栏自动隐藏，悬停显示；按 `Esc` 退出
- **演讲者模式** — 按 `P` 打开同步演讲者窗口：备注、计时器、页数、翻页导航；窗口高度随备注自动调整
- **备注编辑面板** — 编辑模式（`E` 键）下底部出现备注栏，点击标题可收起/展开，输入实时同步到演讲者窗口
- **内联 SVG 图表** — 流程图、时间轴、条形图、对比矩阵、组织架构图，无需 Mermaid.js 或外部库
- **自定义主题系统** — 在 `themes/你的主题/` 放入 `reference.md` 即可添加专属设计预设；可选提供 `starter.html`
- **Blue Sky Starter 模板** — 完整 boilerplate，任何模型都能正确实现全套视觉系统
- **图片处理流水线** — 自动评估和处理素材（Pillow）
- **PPT 导入** — 将 `.pptx` 文件转换为网页演示
- **PPTX / PNG 导出** — 通过 [kai-html-export](https://github.com/kaisersong/kai-html-export)（`clawhub install kai-html-export`）
- **浏览器内编辑** — 直接在浏览器中编辑文字，Ctrl+S 保存
- **视口自适应** — 每张幻灯片精确填充 100vh，永不出现滚动条
- **中英双语** — 完整支持中文内容

---

## 安装

### Claude Code

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

OpenClaw 首次使用时会自动安装依赖（Pillow）。

---

## 使用方法

```
/slide-creator --plan       # 分析内容和 resources/ 目录，生成 PLANNING.md 大纲
/slide-creator --generate   # 根据 PLANNING.md 生成 HTML 演示文稿
/slide-creator              # 从零开始（交互式风格探索）
/kai-html-export            # 导出为 PPTX 或 PNG（独立技能）
```

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
2. 运行 `/slide-creator`，Skill 会自动识别并提取内容

---

## 依赖要求

| 依赖 | 用途 | OpenClaw 自动安装 |
|------|------|------------------|
| Python 3 + `Pillow` | 生成时图片处理 | ✅ via uv |

不需要 Node.js。

**Claude Code 用户** 需手动安装：
```bash
pip install Pillow
```

如需导出 PPTX 或 PNG，安装 [kai-html-export](https://github.com/kaisersong/kai-html-export)：
```bash
clawhub install kai-html-export   # 或：pip install playwright python-pptx
```

---

## 输出文件

- `presentation.html` — 零依赖单文件，直接用浏览器打开
- `PRESENTATION_SCRIPT.md` — 演讲稿（幻灯片 8 张以上时自动生成）
- `*.pptx` — 通过 `--export pptx` 导出

---

## 浏览器内编辑

生成的演示文稿内置文字编辑功能，无需修改 HTML 源码。

**进入编辑模式：**

- 将鼠标移到屏幕**左上角** → 出现编辑按钮，点击即可
- 或直接按键盘 **`E`** 键

**编辑模式下：**

- 点击幻灯片上的任意文字，直接修改
- **底部备注栏** — 可编辑当前幻灯片的演讲备注；点击标题栏中央横线可收起/展开，避免遮挡内容
- **`Ctrl+S`**（Mac 上为 `Cmd+S`）— 保存所有修改（包括备注）到 HTML 文件
- **`Escape`** — 退出编辑模式，不保存

**如何开启：** 在 slide-creator 生成时，选择启用「浏览器内编辑」（默认推荐开启）。如果之前没有选，重新执行 `/slide-creator --generate` 并选择开启即可。

---

## 播放模式

生成的演示文稿内置全屏播放模式，无需额外软件。

**进入方式：**

- 在演示文稿中按 **`F5`**
- 或将鼠标移到右下角 → 点击出现的 **▶** 按钮

**播放模式下：**

- 幻灯片缩放填满整个屏幕（1440×900，其他比例自动加黑边）
- 导航控制栏和页码自动隐藏，悬停时显示
- 所有键盘快捷键仍可用：方向键、空格键、`P` 打开演讲者窗口
- 按 **`Esc`** 或再次按 `F5` 退出

**演讲者窗口** — 按 **`P`** 打开独立同步窗口，显示演讲备注、已用时计时器、当前/总页数及翻页控制。适合笔记本连接投影仪演讲时使用。

---

## 演讲者模式

按 **`P`** 键打开演讲者窗口，包含：

- 当前幻灯片备注（可在编辑模式下实时修改并同步）
- 已用时计时器
- 当前页 / 总页数
- 上一张 / 下一张导航

---

## 设计预设

| 预设 | 风格 | 适合场景 |
|------|------|----------|
| **Bold Signal** | 自信、强冲击 | 路演、主题演讲 |
| **Electric Studio** | 简洁、专业 | 商务演示 |
| **Creative Voltage** | 活力、复古现代 | 创意提案 |
| **Dark Botanical** | 优雅、精致 | 高端品牌 |
| **Blue Sky** ✨ | 清透、企业 SaaS | 产品发布、科技路演 |
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

附带完整 starter 模板（`references/blue-sky-starter.html`）—— 全部 10 个签名视觉元素预置完毕，模型只需填充幻灯片内容即可。

---

## 面向 AI 智能体与技能开发者

其他智能体和技能可直接调用 slide-creator：

```
# 根据主题或备注生成
/slide-creator 为 [主题] 制作路演 deck

# 两步流程：先规划，再生成（支持中间审查）
/slide-creator --plan "Acme v2 产品发布演讲稿"
# （如需要，编辑生成的 PLANNING.md）
/slide-creator --generate

# 生成后导出为 PPTX
/slide-creator --export pptx
```

---

## 设计理念

本节介绍 slide-creator 的设计原则——既包括作为用户工具的设计，也包括作为 Claude Code 技能的设计。

### 一、技能的渐进式披露

技能文件每次被调用时，会完整加载到 AI 的上下文窗口中。这意味着技能文件的大小直接影响 AI 的专注程度。

slide-creator 的解法是：**SKILL.md 是一个精简的指令路由层（约 150 行）**，将每条指令分发到所需的最小参考文件集合：

```
--plan        → 只读 references/planning-template.md
--generate    → references/html-template.md + 单个风格文件 + references/base-css.md
--export pptx → 运行脚本，不加载任何文件
交互模式      → references/workflow.md（完整 Phase 1–5）
风格选择      → references/style-index.md（21 个预设 + 心情映射）
```

**最终效果：** `--plan` 调用从不接触 CSS。`--generate` 运行时从不加载其他 20 种风格描述。`--export` 调用什么都不加载，只运行 Python 脚本。

这是渐进式披露原则在 AI 上下文管理中的应用：**在需要信息的那一刻才披露，而不是提前全部加载**。好的 UX 设计原则同样适用于好的 AI 技能设计。

### 二、以视觉代替语言：Show, Don't Tell

大多数人在没有看到样例之前，无法用语言描述自己的设计偏好。问"你想要极简风还是大胆风？"只会得到模糊的答案。生成三个 50 行的 HTML 预览，然后问"你更喜欢哪个？"，用户会立即做出反应。

Phase 2 正是围绕这一洞察设计的。当用户看到自己的内容标题以三种截然不同的设计语言呈现时，那种"wow 时刻"会把一个抽象的选择变成一种直觉体验。预览文件故意做得很小（约 50 行，自包含），几秒即可生成。

这正是 slide-creator 强调"以视觉代替语言"而非"提供 21 个主题"的原因。功能不产生参与感，选择的体验才会。

### 三、视口适配作为第一优先级约束

演示文稿中途出现滚动条，意味着这个幻灯片是坏的。这听起来显而易见，但在生成 HTML 时很容易犯错——如果一张幻灯片内容太多，浏览器会直接溢出显示。

slide-creator 将视口适配视为**不可妥协的硬约束**，而非最佳实践：

- 每个 `.slide` 必须有 `height: 100vh; overflow: hidden;`
- 按幻灯片类型规定了内容密度上限（例如最多 6 条要点、最多 6 个网格卡片）
- 内容超出时，规则永远是：**拆分幻灯片，不要压缩**

基础 CSS（`references/base-css.md`）对所有尺寸使用 `clamp()`，从横屏手机到 4K 显示器均可优雅缩放。CSS 陷阱备注栏也正因此而存在——`calc(-1 * clamp(...))` 与 `-clamp(...)` 的区别是一种静默失败，没有控制台报错，只是布局悄悄出了问题。

### 四、自定义主题系统：可组合的设计语言

`themes/` 目录允许任何用户以自己的品牌风格扩展 slide-creator。只需在 `themes/your-theme/` 目录中放入一个 `reference.md` 描述视觉系统，它就会立即以"Custom: folder-name"的形式出现在风格选择列表中。

两文件约定（`reference.md` + 可选的 `starter.html`）与 Blue Sky 模式一致：`reference.md` 描述设计语言（颜色、字体、组件类），`starter.html` 是复杂视觉系统的完整模板。

这种分离意味着简单的自定义主题只需一个文件，而复杂主题（带动画背景、自定义 JS、非常规布局系统）则可以附带完整的工作模板。

### 五、内容类型路由：有意义的智能默认值

21 个预设的数量足够丰富，同时又经过精心筛选。slide-creator 通过内容类型映射来推荐风格，而非让用户浏览所有选项：

```
数据报告 / KPI 看板    → Data Story、Enterprise Dark、Swiss Modern
商业路演 / VC Deck     → Bold Signal、Aurora Mesh、Enterprise Dark
开发工具 / API 文档    → Terminal Green、Neon Cyber、Neo-Retro Dev Deck
```

SKILL.md 中的这张路由表同时服务两类受众：希望获得合理起点的人类用户，以及以编程方式调用技能时可能知道内容类型但不知道选哪种风格的 AI 智能体。

---

## 兼容性

| 平台 | 版本 | 安装路径 |
|------|------|----------|
| Claude Code | 任意 | `~/.claude/skills/slide-creator/` |
| OpenClaw | ≥ 0.9 | `~/.openclaw/skills/slide-creator/` |
