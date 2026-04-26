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

## 设计理念：为真实的最后一步而设计

slide-creator 的出发点很具体：用户通常会先花很长时间生成内容、讨论结构，最后才说一句“帮我做成 slide”。这恰好是最容易翻车的时刻。上下文已经很长，风格信号被稀释，硬约束也最容易丢。

所以 slide-creator 的设计目标不是“会做 slide”，而是**保护最后这一步**。

### 一、IR-first，planning 退居可选

现在的主流程明确是 **IR-first 工作流**：

```
user prompt → BRIEF.json → HTML → validate → eval
```

`--plan` 的默认职责，是提炼可执行的 `BRIEF.json`，而不是强制先走一遍人工审阅。`PLANNING.md` 仍然保留，但定位已经变成“需要人看时才派生的人类可读视图”。

原因很简单：真正生成 HTML 时，不应该继续背整段聊天记录，而应该只背一个短、硬、结构化的真相源。

### 二、公开模式尽量简单，内部链路必须严格

对用户来说，公开心智模型应该尽量小：

- **Auto**，先出第一版
- **Polish**，把质量锁住

但内部流程不能因此变松。真正的路径仍然是风格发现、BRIEF 提炼、渲染、校验、review。外部更简单，内部更严格。

这也是为什么 README 和技能对外强调 Auto / Polish，而仓库内部仍然维护清晰的路由、review 逻辑和 eval 资产。

### 三、渐进式披露，不浪费模型上下文

技能文件每次调用都会进入模型上下文，所以“上下文预算”本身就是产品面。

slide-creator 把 `SKILL.md` 保持成一个薄路由层，把细节下沉到 references，让每条路径只加载当前需要的内容：

```
--plan        → 只读 references/brief-template.json
--generate    → references/html-template.md + references/js-engine.md + 单个风格文件 + base-css.md
交互模式      → references/workflow.md
风格选择      → references/style-index.md
```

这不是为了形式上的优雅，而是为了减少上下文压力，避免模型在真正渲染前把最重要的约束忘掉。

### 四、视觉选择必须“先看图，再落字”

大多数用户无法稳定地用抽象词描述自己想要的风格，但他们看到方案后会立刻知道喜欢什么。

所以 slide-creator 把风格选择看成“预览问题”，而不是“问卷问题”。先给 3 个强烈不同的方向，让用户选。然后再把选择写进 `BRIEF.json`。

风格如果一直停留在模糊描述，拖到 HTML 生成阶段才真正决定，就已经太晚了。

### 五、零依赖运行时，本身就是产品的一部分

输出结果不是截图，也不是还要交给另一套工具链继续处理的中间产物。输出本身就是浏览器原生 deck，包含：

- 视口适配的幻灯片
- 演讲者模式
- **Default-on** 浏览器内编辑
- 键盘导航
- 自包含运行时

零依赖约束会逼出纪律。如果一个 deck 必须依赖 bundler、远程字体或额外运行时胶水才能正常工作，那产品意义已经打折。

### 六、先验证，再相信结果

系统应该在用户打开坏 deck 之前就发现问题。

这就是为什么 slide-creator 把质量检查不断前移：

- `--plan` 先产出结构化 `BRIEF.json`
- `--generate` 从 IR 生成，而不是从整段对话硬生成
- `validate-brief.py` 校验 brief 契约
- `tests/validate.py --strict` 校验运行时契约
- eval 按 route / compression / render / efficiency 四层打分

这里最重要的设计思想不是”多写一点测试”，而是**更准确地定位失败发生在哪一层**。这样坏结果才能反过来推动 skill 本身变好。

**验证的定位：写入前门禁，不是可选复查**

validate.py 应当运行在 `--generate` 内部，但位置是在渲染完成之后、最终文件被接受之前。正确顺序是：组装 HTML → 写入临时文件 → 运行 `python3 tests/validate.py "$TMP_HTML" --strict` → 修复或重生直到通过 → 再写入最终输出。

这样做的含义是：
- 不增加规划阶段步骤 → 不增加构思时的 LLM 认知负担
- 不增加额外 style file 读取 → 仍然复用现有生成输入
- 硬失败直接拦住坏产物 → 不再把失败 deck 当成功交付
- warning 仍可进入 polish / retry 策略，但不能冒充“已经有效”

每次新增检查前，都要先判断：它是不是属于确定性的运行时门禁？如果本质上是主观审美判断，而不是契约校验，就应留在 review/eval，不要塞进 strict validate。

**契约对齐：验证脚本必须与生成契约一致**

validate.py 的检查项必须与 SKILL.md / html-template.md / js-engine.md 的实际契约保持一致。例如：
- 检查 hotzone → 必须用 `.edit-hotzone`（class）而不是 `id=”hotzone”`
- 检查 preset metadata → 生成结果必须写出真实的 `body[data-preset]`，不能省略，也不能保留模板占位值
- 检查外部链接 → 必须允许 Google Fonts（html-template.md 明确要求）
- 检查水印 → 必须验证 JS 注入逻辑（而不是硬编码位置）

契约对齐不是靠文档同步，而是靠脚本实测：每次改动 validate.py，都要跑一遍 demo，确保检查项真的匹配生成输出。

### 七、反对 slide slop，既反对视觉烂稿，也反对内容烂稿

AI 幻灯片最常见的问题不是明显报错，而是平庸。页面太空、布局重复、标题没判断、结构泛泛。这些最容易让结果看起来像“机器做的”。

slide-creator 把它同时当成设计问题和内容问题来处理：

- 视觉密度必须是刻意的
- 版式节奏必须变化
- 该用判断句标题时就不能偷懒用名词短语
- 有数字时要尽量前置
- 有术语时要翻译给目标受众

目标不是让每一页都很满，而是避免“意外的空”和“意外的虚”。

### 八、自定义主题可以扩展，但必须有契约

支持自定义主题，不代表允许 prompt soup。

theme 的约束是明确的：

- 创建 `themes/your-theme/`
- 用 `reference.md` 描述视觉语言
- 复杂主题再附带 `starter.html`

这样 theme 才是可组合、可审查、可复用的渲染契约，而不只是“帮我套一下品牌色”。

### 九、内容类型路由，本质上是质量功能

21 个预设只有在“系统能帮用户先站到对的位置”时才真正有价值。

所以 slide-creator 会先按内容类型给出合理起点：

```
数据报告 / KPI 看板    → Data Story、Enterprise Dark、Swiss Modern
商业路演 / VC Deck     → Bold Signal、Aurora Mesh、Enterprise Dark
开发工具 / API 文档    → Terminal Green、Neon Cyber、Neo-Retro Dev Deck
```

好的默认值会直接减少返工。结果就是更少的坏第一稿，更少的风格重置，也更少被上下文浪费掉的 token。

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
/slide-creator --plan       # 分析内容和 resources/ 目录，生成 BRIEF.json
/slide-creator --generate   # 根据 BRIEF.json 生成 HTML 演示文稿
/slide-creator --review     # 诊断并修复内容质量问题
/slide-creator              # 从零开始（交互式风格探索）
/kai-html-export            # 导出为 PPTX 或 PNG（独立技能）
```

### 原始沙箱 fallback

`/slide-creator ...` 是 Claude/OpenClaw 的 slash 技能调用，不是原始 bash / python 命令。

如果你在原始沙箱或外部 agent runner 里执行，请改用：

```bash
python3 main.py --validate-brief --brief BRIEF.json
python3 main.py --generate --brief BRIEF.json --output presentation.html
```

内置 preset 仍然从 `references/` / `references/style-index.md` 读取；`themes/<name>/reference.md` 只用于自定义主题。

### 规划深度

- `自动（Auto）` — 快速路径；跳过 Phase 3.5 Review
- `精修（Polish）` — 深度路径；自动执行 Phase 3.5 Review

同一份内容在 `自动` 与 `精修` 之间切换时，除非用户明确要求换风格，否则应保持相同 preset。

### 典型工作流

**方式一：交互式创建**
1. 运行 `/slide-creator`，回答目的、长度、内容和图片四个问题
2. 查看 3 个风格预览，选择喜欢的风格
3. 生成完整演示文稿，在浏览器中打开

**方式二：IR-first 工作流（复杂内容推荐）**
1. 在项目目录放入素材（`resources/` 文件夹）
2. 运行 `/slide-creator --plan 我的AI创业公司融资路演`
3. 先检查 `BRIEF.json`；只有需要给人审阅时再派生 `PLANNING.md`
4. 运行 `/slide-creator --generate`

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

- **IR-first 工作流** — `--plan` 提炼 `BRIEF.json`，`--generate` 从 IR 输出幻灯片
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

**v2.23.2** — 沙箱入口与技能表面修补：新增根目录 `main.py` 与 `slide-creator` wrapper，用于原始沙箱里的 BRIEF 校验与渲染；`--plan` 现在会明确提示“这是 slash-skill 步骤”，不再抛出误导性的运行时错误；同时修正 `SKILL.md` 的用户入口层，恢复风格推荐表，并明确内置 preset 在 `references/` 下，`themes/<name>/reference.md` 只用于自定义主题。

**v2.23.1** — Enterprise Dark 运行时稳定性补丁：修复 shared js-engine 的 active-slide reveal 切换、默认隐藏编辑 chrome、将 watermark 占位符替换为真实版本/风格元数据、把 scroll-snap deck 的滚轮翻页稳定为“一次手势一页”，并修正 Enterprise Dark 的 narrative cover 路由、split 标题裁切、治理页节奏以及若隐若现的网格强度。

**v2.23.0** — 标题编排与低上下文质量发版：新增 preset-aware 的标题 profile registry 与浏览器级 title QA；扩展 low-context diagnostics / eval buckets 用于验证质量是否真的提升；严格门禁补强共享 runtime 与 `body[data-preset]`；`SKILL.md` 也按优先级重排为风格强制 → 叙事弧线 → 标题质量，再到可降级的播放 / 编辑 / 水印能力。

**v2.22.0** — 风格参考与严格门禁收口：全部 preset 通过 style-reference audit；Swiss Modern 以及 Enterprise Dark / Data Story / Glassmorphism / Chinese Chan 补齐 canonical export contract 与 user-content 路由；`tests/validate.py --strict` 被文档化并测试为 `--generate` 的写入前门禁；新增回归测试锁住 CSS 变量解析、布局多样性与高优先级 preset 契约检查。

**v2.19.0** — IR-first 发版：`BRIEF.json` 升级为主要真相源，`PLANNING.md` 降级为可选的人类视图；新增 `evals/generated-decks/` 下的 late-context 评估产物；README 的设计思想改写为 `prompt → BRIEF → HTML → validate → eval` 主线；并补齐与新契约对应的回归测试。

**v2.18.1** — Paper & Ink 风格参考修复：恢复正确的编辑风格定义（Cormorant Garamond 标题、Source Serif 4 正文、crimson 装饰线、首字母下沉）；slide HTML 添加 `.slide-content` 包裹以实现垂直居中；中文标题字体回退从 Noto Sans SC 改为系统宋体。

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
