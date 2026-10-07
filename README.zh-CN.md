# slide-creator

> 很多人有很好的内容，却无法有效地展现。虽然大模型现在能帮你写 PPT，但输出效果不稳定，多次抽卡又很头疼。Slide-Creator 帮助你简单、稳定地输出演示文稿——根据场景选择喜欢的风格即可，其他的就让大模型去干，喝杯咖啡吧。
>
> **[看这份指南本身生成的报告 →](https://kaisersong.github.io/slide-creator/demos/blue-sky-zh.html)** — 本文档由 slide-creator 自己生成。

适用于 [Claude Code](https://claude.ai/claude-code) 和 [OpenClaw](https://openclaw.ai) 的演示文稿生成技能，零依赖、纯浏览器运行的 HTML 幻灯片。

[English](README.md) | 简体中文

---

## 下载 v2.31.0

[精简 Skill 安装 ZIP](https://github.com/kaisersong/slide-creator/releases/download/v2.31.0/kai-slide-creator-v2.31.0-skill-runtime.zip) · [Release 与 SHA-256](https://github.com/kaisersong/slide-creator/releases/tag/v2.31.0) · [优化方法论 v1.0.1 ZIP](https://github.com/kaisersong/slide-creator/releases/download/v2.31.0/skill-optimization-methodology-v1.0.1.zip)

方法论正文、优化计划、评测报告与bug模板见[跨 Skill 优化指南](docs/methodology/skill-optimization/README.md)。运行包与方法包分开下载，研究文档不会占用正常生成上下文。

---


## 效果展示

用浏览器直接打开，零安装查看效果：

- 🇨🇳 [slide-creator 介绍（中文）](https://kaisersong.github.io/slide-creator/demos/blue-sky-zh.html)
- 🇺🇸 [slide-creator intro (English)](https://kaisersong.github.io/slide-creator/demos/blue-sky-en.html)

点击下方任意截图可打开对应的在线演示（内容相同，风格不同）：

<table>
<tr>
<td colspan="3" align="center"><a href="https://kaisersong.github.io/slide-creator/demos/fantasy-rainbow-zh.html"><img src="demos/screenshots/fantasy-rainbow.png" width="740" alt="奇幻彩虹"/></a><br/><b>奇幻彩虹 · Fantasy Rainbow</b> — 自定义主题</td>
</tr>
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
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/strategy-consulting-zh.html"><img src="demos/screenshots/strategy-consulting.png" width="240" alt="Strategy Consulting"/></a><br/><b>Strategy Consulting</b></td>
</tr>
</table>

---

## 设计理念：模型组织内容，程序执行交付

slide-creator 面向内容工作流的最后一步：把已经形成的论点变成可使用的演示文稿。这一步往往发生在长对话之后。架构保留原始材料和用户明确选择，向模型提供精简的内容契约，并把重复实现交给渲染程序。

```mermaid
flowchart LR
    R["用户指定风格"] --> V["请求与 BRIEF 校验"]
    S["原始来源"] --> M["模型组织内容"]
    C["程序编译的能力契约"] --> M
    M --> B["BRIEF.json"]
    B --> V
    V --> G["Canonical renderer"]
    G --> H["写入前门禁"]
    H --> O["浏览器原生 HTML"]
    O --> Q["Review 与任务评测"]
    S --> Q
```

Review 和评测按用户所选流程执行；普通生成不会自动调用独立模型评分器。各层有明确的责任。

### 一、内容判断与重复实现分工

模型组织论点、证据、页间叙事、展示意图、本页事实、结尾请求和演讲备注。程序完整读取所选风格和 runtime，选择具体布局，实现 CSS/JavaScript，组装导出 DOM，并在写出前校验。

这种分工减少重复读取源码和实现返工。Renderer 缺陷应在 renderer 中修复；让每份新稿都由模型读源码、改程序来补偿，会掩盖缺陷并消耗上下文。Native core、统一 profile 和受支持的 custom theme 都走 `render_from_brief()`。

Auto 和 Polish 使用同一执行路径。Auto 先出第一稿，Polish 增加内容和设计审阅。Polish 是更深入的 review 流程，不能保证任意稿件的来源语义都完美。

### 二、BRIEF 是派生计划，不是已经验证的真相

原始材料定义事实，用户明确选择定义交付要求。`BRIEF.json` 是模型对两者的结构化理解，因此仍可能写错；schema 有效不等于论点真实。

计划把逐页 claim、explanation、`supporting_facts`、数值证据和 visual intent 放在一起。`numeric_facts` 是数值绑定的辅助索引，不应再作为额外表格行。`speaker_note` 将讲者指令与观众正文分开，`desired_action` 保留结尾请求的范围与时间。旧 BRIEF 继续使用已定义的 fallback。

`--plan` 负责提炼可执行计划，`PLANNING.md` 只在需要时派生成人类可读视图。直接给内容和风格也先物化 BRIEF，再调用渲染程序，不绕过产品路径手拼最终 HTML。

### 三、从完整实现的 owner 编译精简模型契约

`SKILL.md` 负责路由。生成契约来自现有 schema、风格 compiler、标题 profile 和能力注册表，向模型提供字段形状、允许布局、token 和内容规则，避免重复读取实现源码。

```text
模型读取 → generation-contract.md + main.py --model-context --preset <风格>
程序读取 → 完整的所选风格、模板与共享 runtime
技术内容 → 按任务读取 technical-language.md
深度设计 → 具体决策不在契约中时，再读取相关风格章节
```

完整能力仍留在程序中。精简上下文要保留证据、条件和必要设计选择；机械规定最多读取几个文件，不能替代有效契约。

### 四、用户明确选择应当可以独立执行

未选风格时，提供合适的预览和推荐。用户已经明确选好时，保留该选择，不再重新推荐。

在编写 BRIEF 前，将原始选择保存到本次工作目录的 `SLIDE_REQUEST.json`。`--generate` 独立核对请求与 `BRIEF.style.preset`，不一致就返回 `PRESET MISMATCH`，不写出产物。调用方也可以通过 `--requested-preset` 或 `--request-file` 提供约束。别名按实际风格 reference 归一化，冲突参数不能覆盖请求文件。

这要求调用方先正确记录用户选择。它是对已提供请求的程序约束，不代表自然语言理解永不出错。冲突后修正 BRIEF，不能把请求文件改成模型选的风格；不支持的风格明确报告，不悄悄替换。

### 五、排版适配不能改变内容含义

每页承载完整的本页声明。数字与来源对象、单位一起保留；目标仍是目标，未知值明确保留，访谈线索不能升级为已证明根因。客户数不能直接当成审查数，AND 条件不能变成单一触发条件。

空间不足时应重排、选择合适展示，或删除完整同文重复。不能裁掉最后一条事实、编造数值，或重复填满固定卡片数。排重保护否定、十进制、不同条件和解释指标所需的标签。不同单位不组成同一数值系列；材料稀疏时可以说明下一项测试。

标题需要单独对照来源。短标题可能删掉条件或改变数量对象，与正确正文产生矛盾。可读性、对比度和视觉节奏以实际渲染结果检查，布局变化应帮助论证，而不只是增加装饰。

### 六、共享浏览器壳子也是程序的责任

主题负责视觉语言和内容构图，生成器负责共享编辑、备注、导航、进度和播放契约。Starter 没提供必需节点时，由生成器补齐；主题已提供时只保留一份。通过实际 Edit/Done 和键盘操作验证壳子能用。

交付的 HTML 无需 Python 或 JavaScript 构建工具，直接由浏览器运行；网络字体不可用时回退本地字体。生成器本身则需要 Python 3.10+ 和已说明的运行依赖，这两类要求分别说明。

能力路由区分五个 native core、四个默认推荐、按场景推荐的 Chinese Chan、reference-backed profile 和 custom theme。存在 reference 或打包了资产，不等于可执行渲染或历史 demo 保真已经通过。当前 Cloudhub 限制明确记录，不将其描述成已验证支持。

### 七、互补验证不能被一个绿色分数替代

| 层级 | 责任 | 通过意味着什么 |
|---|---|---|
| 请求与 BRIEF | 核对指定风格和输入结构 | 已提供的请求与计划兼容 |
| 写入前门禁 | 检查 canonical 来源标记、必需可见数字、严格 HTML/runtime 规则 | 在这些程序检查下允许写出 |
| 真实浏览器 | 使用真实 controller，测几何与对比度，操作备注、编辑与播放 | 被测交互和视口可用 |
| 来源复核 | 检查实体、单位、并列条件、否定、目标、未知与标题强度 | 审查范围内内容忠于来源 |
| 完整模型任务 | 从请求到生成、检查与独立评分，保留实际 trace | 该任务有真实结果和成本记录 |
| 发行包 | 实际解压、安装最小依赖、比对远端下载字节 | 被测下载包与发行 runtime 一致 |

完整执行、自动通过、来源复核通过和已经发布是不同状态。均分较高不能抵消关键语义错误；即使自动检查通过，已知标题问题也继续保留。

普通 CLI 在写出前检查来源标记、必需数字可见性和 strict HTML。用户要求的单 deck `--eval` 在门禁后增加诊断报告；它本身不代表完整模型任务评测。

### 八、效率与质量、研究成本一起计量

优化使用冻结输入与实现快照、新任务工作区、多次模型运行、provider 真实 usage 和独立评分。同一 BRIEF 在两版程序中重渲染，可以隔离 renderer 行为；它不能说明模型会写出什么。完整提示词到演示稿的任务评测回答另一个问题。

记录 input、cached input、uncached input、output 和耗时，把 QA/评分与校准成本单列。失败和慢样本保留在结果中；总 token 包含缓存输入，不能直接把减少比例当作付费下降比例。

比较配对任务与每类任务，而不只看总均分。完整验收前，先用低成本复现、针对性回归和固定输入实验定位问题。研究总成本与每份稿件提效分别记录，不从不同版本挑选最好样本拼成通过结论。

### 九、用版本化失败证据持续改进 Skill

新 bug 要定位失败层，保留原要求和产物，并成为回归输入。契约或生成行为变化应做适用的任务评测；检查器缺陷应校准受影响的比较。包验证和文档检查保留各自更窄的范围。

[Skill 优化方法论](docs/methodology/skill-optimization/README.md)提供计划、评测和 bug 模板及更新记录，[效率评测指南](evals/token-efficiency/README.md)定义本项目的实际计量协议。这条反馈链改进程序与契约，让普通用户任务能够复用成果。

---

## 评测与维护

以下命令用于完整仓库、已安装评测依赖的环境；模型任务还需要 runner 的登录状态。精简运行 ZIP 不包含测试和评测输入。

当前前后比较协议见[evals/token-efficiency/README.md](evals/token-efficiency/README.md)：冻结语料和 runtime，运行基线与候选，比较真实成本、质量和失败；来源复核判定与自动结果分别保留。

早期 captured-run harness 仍可使用：

```sh
python3 scripts/run-skill-evals.py --runner codex --run-live --format json --json-out .tmp-run/skill-evals/results.json
```

其中 Supervisor、Generate Worker 和 Style Judge 描述评测角色，不代表普通生成必须调用多个 agent。Fixture 运行验证 harness，不是模型任务证据。该独立协议见[captured-run架构](docs/design/2026-05-17-slide-creator-captured-run-eval-architecture.md)。

公开 preset 交付矩阵使用：

```sh
python3 scripts/preset_release_gate.py \
  --suite evals/preset-surface-all/manifest.json \
  --output-dir .tmp-run/release-gate \
  --contract --browser-geometry --mobile-geometry --export-smoke
```

这些检查覆盖确定性渲染、契约、实际几何与导出 DOM。`--pptx-export` 是独立的真实导出检查，`--demo-parity` 和 `--promotion-gate` 对应其他风格声明；报告实际运行的选项。单份 HTML 可运行 `scripts/browser_geometry_qa.py deck.html --mode both --laptop-window --strict`，覆盖窗口与播放两种形态。

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
python3 main.py --generate --brief BRIEF.json --output presentation.html --eval
```

内置 preset 仍然从 `references/` / `references/style-index.md` 读取；`themes/<name>/reference.md` 只用于自定义主题。
裸 CLI renderer 覆盖 native deterministic 内置 preset、统一 profile 内置 preset 和 custom theme，全部走同一条 BRIEF-to-HTML 路径，再使用同一套 strict validator 后输出最终 HTML。

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
- **22 种设计预设** — 每种风格含命名布局变体
- **内容类型智能路由** — 根据路演、开发工具、数据报告等自动推荐风格
- **视觉风格探索** — 先生成 3 个预览，看图选风格而非描述风格
- **内联 SVG 图表** — 流程图、时间轴、条形图、对比矩阵、组织架构图，无需外部库
- **Blue Sky Starter 模板** — 完整 boilerplate，任何模型都能正确实现全套视觉系统

### 交互功能

- **播放模式** — 按 `F5` 或点击右下角标准 44px 圆形 ▶ 按钮进入全屏播放；共享壳子主题统一使用圆点导航、顶部进度条和 `NN / 总页数` 页码；按 `Esc` 退出
- **演讲者模式** — 按 `P` 打开同步演讲者窗口：备注、计时器、页数、翻页导航；窗口高度随备注自动调整
- **备注编辑面板** — 编辑模式（`E` 键）下底部出现备注栏，点击标题可收起/展开，输入实时同步
- **浏览器内编辑** — 默认开启；将鼠标移到左上角标准 Edit hotzone 或按 `E`，可直接编辑文字和演讲者备注，然后按 `Ctrl+S` 保存
- **视口自适应** — 每张幻灯片精确填充 100vh，永不出现滚动条

### 输出功能

- **自定义主题系统** — 在 `themes/你的主题/` 放入 `reference.md` 即可添加专属预设；复杂系统可选提供 `starter.html`，仓库内置的“奇幻彩虹（Fantasy Rainbow）”是可直接生成的完整示例
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
| **Strategy Consulting** | 结构化、权威、干净 | 咨询报告、战略方案、尽职调查 |

### Blue Sky

天空渐变背景（`#f0f9ff → #e0f2fe`）搭配浮动玻璃拟态卡片与动态环境光球。灵感来自真实的企业 AI 路演文稿（CloudHub V12 MVP），呈现出高空晴日般开阔、自信、精致的视觉气质。

标志性元素：SVG 颗粒噪声纹理叠层 · 3 个按幻灯片类型重新布阵的模糊光球 · `backdrop-filter: blur(24px)` 玻璃拟态卡片 · 40px 科技网格底层 · 弹簧物理横向切换动画 · 封面专属双层流动云朵效果。

**为什么 Blue Sky 是 starter 模板范本：** 它预置了全部 10 个签名视觉元素，模型只需填充幻灯片内容——没有误实现设计系统的风险。这种 `reference.md` + `starter.html` 的模式对任何复杂主题都可复用。

### 内置自定义主题：奇幻彩虹（Fantasy Rainbow）

`themes/fantasy-rainbow/` 是一个可直接生成的自定义主题，使用 `style.preset: "custom:fantasy-rainbow"` 选中。它只在封面使用动态 WebGL 虹彩，内容页保持不透明白底编辑风格，以克制的蓝/紫/青语义色组织视觉节奏，并用不透明近黑收尾页完成收束。主题继续使用标准非 Blue-Sky 共享壳子：44px 圆形播放按钮、圆点导航、顶部进度条、直属页码、默认开启的 Edit 模式、演讲者备注、Presenter 模式、reduced-motion fallback、可打印输出，且没有远程运行时依赖。封面与收尾页的重点短语由可选字段 `narrative.slides[].title_emphasis` 明确声明；旧 BRIEF 会使用通用的标题结构降级规则，不再匹配任何预设专用文案。旧的 `custom:iridescence-convergence` preset 继续作为兼容别名使用。

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

**内置自定义主题：** `themes/fantasy-rainbow/`（可直接生成）、`themes/ascii-stream/` 和 `themes/kingdee/`

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

生成器需要 **Python 3.10+** 和 **beautifulsoup4**；生成后的 HTML 不需要 Python 或 JavaScript 构建工具，直接用浏览器打开。网络字体不可用时使用本地字体回退。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements-runtime.txt
.venv/bin/python main.py --model-context --preset "Data Story"
```

以上命令在解压后的 `kai-slide-creator/` 中执行，后续 CLI 也使用该虚拟环境的 Python。Windows 对应路径为 `.venv\Scripts\python.exe`。浏览器 QA 与 PPTX 导出属于额外工具依赖，不是普通生成路径的必需项。

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

## 仅运行所需的 Skill ZIP

下载 [`kai-slide-creator-v2.31.0-skill-runtime.zip`](https://github.com/kaisersong/slide-creator/releases/download/v2.31.0/kai-slide-creator-v2.31.0-skill-runtime.zip)，即可获得精简的 Skill 安装包。将压缩包顶层的 `kai-slide-creator/` 目录解压到代理的 skills 目录。压缩包只包含 `SKILL.md`、`main.py`、`scripts/`、`schemas/`、`references/` 和 `themes/`；不会包含仓库 README、Demo、测试、eval fixture、设计文档和 Git 元数据。

---

本次保留上一版的 Cloudhub 企业主题资产，但其旧参考缺少可执行布局，canonical 生成仍被视觉重复门禁阻止；没有将其标记为可生成主题。Kingdee 已完成解压生成与共享编辑壳子修复。

---

## 版本日志

**v2.31.0** — 上下文与质量优化：模型只编写 BRIEF，程序加载完整风格和 runtime；新增独立用户风格约束、完整事实与数字对象绑定、正文可读性及同文排重修复。优化阶段冻结版本的8类任务、26次自动评测通过，24份正向稿风格均正确；相对原始基线生成token中位数降低77.57%、耗时降低36.59%、质量均分77.88→88.54。标题仍可能改变数量对象或省略并列条件，关键稿件需要来源复核；这些结果不代表所有任务或安装环境的质量保证。新增跨Skill优化方法论与模板，独立下载包更新到v1.0.1；发布检查补齐小屏布局和自定义主题备注面板的隐藏/打开规则。

**v2.30.2** — 奇幻彩虹播放性能修复：离开封面或暂停播放时停止 WebGL 与封面 CSS 动画，返回后恢复单个动画循环；移除逐帧页面几何遍历。禁用整页位移缩放过渡，保留放映固定缩放，内容改用短淡入，并补齐黑屏遮罩。新增 36 项生命周期回归测试，同步提供精简运行安装 ZIP。

**v2.30.1** — 奇幻彩虹长时间动画与播放界面修复：将 GPU 时间限制在原动画周期内，避免浮点精度下降产生色带和色块；播放模式隐藏全局浏览页码，退出后恢复。同步更新模板、生成器共享壳子和中英文奇幻彩虹 Demo，提供便于企业安装的精简运行 ZIP 包。

**v2.30.0** — 播放模式与矮窗口几何发版：播放模式从此是被测量的交付面，而不是靠假设。`scripts/browser_geometry_qa.py` 新增 `--mode window|present|both`、`--laptop-window` 视口（`1440x733`），以及新的硬失败码 `browser-geometry-content-clipped`——它会抓住被幻灯片盒子裁掉的正文、列表行、表格单元与页脚；此前只检查标题，而且只在窗口模式、900px 高的视口下检查。发布门的桌面几何步骤现在跑三种窗口形状 × 两种模式。两条新的 strict 校验把这个盲区背后的运行时 bug 固化下来：`playback_scale_safety` 拒绝按窗口宽度驱动的根字号（播放模式把幻灯片钉成固定 `1440x900` 盒子，宽度驱动的排版会在投屏上截断密集页，而窗口里看起来完全正常），`canvas_visibility_guard` 拒绝用 `getBoundingClientRect()` 定尺寸却没有小尺寸守卫的画布（隐藏的幻灯片报告 `0x0`，动效封面会塌成 1×1 缓冲再被拉成一片纯渐变）。生成器补上了缺失的矮窗口节奏：native core 两个 shell、Swiss Modern 证据栈、统一 profile 渲染器、Blue Sky starter 与奇幻彩虹主题都在 `max-height: 860px` 收紧，而不是在真实笔记本窗口高度下裁切；展示型数字保留足够容纳字形的行盒；手机端的长展示列表回退成两列紧凑排布，而不是丢行。Blue Sky 与 Vintage Editorial 生产 demo 同步修复，`references/base-css.md` 与 `references/impeccable-anti-patterns.md` 补齐播放模式几何契约、不得对隐藏元素测尺寸的规则，以及「只在窗口模式验收」这条反模式。

**v2.29.3** — 奇幻彩虹内容忠实度发版：虹彩渲染器不再输出 slide-creator 自身的产品文案。hero、fracture、brief、contract、gates、runtime、modes 与 closing 场景全部改为渲染调用方的 `BRIEF.json`，并新增统一的「小标题 + 说明」拆分逻辑供双段式组件复用。spectrum 的展示总数改为按要点数派生，不再固定为 `22`；显式给出的 `supporting_facts` 优先于从 `claim` 和 `explanation` 派生的事实，被截断的重复碎片不再出现；`brief` 字段改为输出三个网格单元，正文不再挤在窄标签列里换行。超过十二个场景的 deck 现在会循环复用中间场景，而不是重复 `use-cases`——后者会触发视觉多样性门禁，导致十一页以上的 deck 根本无法生成；前十个内容页的场景映射保持不变。

**v2.29.2** — 语义标题强调发版：“奇幻彩虹（Fantasy Rainbow）”现在从结构化 `title_emphasis` 字段读取封面或收尾页的重要短语，彻底移除按固定标题和固定短语查表的实现；旧 BRIEF 则根据标点、语言结构和视觉长度进行通用降级。结构分隔符 `|` / `｜` 不再泄漏到最终标题中，多行封面标题也新增了仅封面生效的字形安全间距。同步新增任意业务文案回归测试、更新中英文说明、刷新 production Demo 水印，并发布新的仅运行所需 Skill ZIP。

**v2.29.1** — “奇幻彩虹（Fantasy Rainbow）”运行包发版：内置自定义主题由“虹彩汇聚（Iridescence Convergence）”正式更名为“奇幻彩虹（Fantasy Rainbow）”，canonical preset 调整为 `custom:fantasy-rainbow`，旧的 `custom:iridescence-convergence` 保留为兼容别名；同步更新中英文 README、production Demo 水印，并新增仅包含 Skill 运行文件的 ZIP Release Asset。

**v2.29.0** — “虹彩汇聚”与共享壳子一致性发版：新增可直接生成的自定义主题，只在封面使用 WebGL 虹彩，内容页保持不透明白底和克制语义色，并以深色收尾；该主题运行时恢复为标准 44px 圆形播放按钮、圆点导航、顶部进度条、直属页码和可发现的 80px Edit hotzone；无 starter 的 custom theme 补齐必需视口壳子，Enterprise Dark insight-pull 标题补上 canonical export slot；同时扩充 strict / Browser 回归覆盖，并把当前 production demo 水印刷新到 v2.29.0。

**v2.28.0** — 生成质量门禁发版：单 deck eval 现在会对未授权的占位文案 / demo 文案残留给出 hard failure；Paper & Ink 的 signature 评分改为对齐真实 reference demo；同时优化 CJK 标题换行，Blue Sky 报告里的中等长度标题会优先充分利用横向空间，不再把“风险”“地图”等词拆到两行。

**v2.27.0** — Captured-run eval 架构发版：新增 OpenAI-style skill eval prompts、归一化 trace 评分、fixture style rubric、live Codex baseline、回归比较器和可选 release-gate 集成。README 与 design docs 现在记录 Supervisor / Generate Worker / Style Judge 三段式架构、上下文隔离规则和 token 计费策略，确保 live eval 成本可见，而不是被 subagent 隐藏。

**v2.26.0** — Blue Sky 确定性渲染与自定义主题发版：Blue Sky 现在走正式 BRIEF 渲染链路并补齐 strict 校验覆盖；自定义主题在源仓库和插件包布局下都能正确解析；Kingdee / Cloudhub 私有主题素材完成路径清理、压缩和回归测试锁定。

**v2.25.0** — 新增 Strategy Consulting 咨询风格预设：12 种 canonical 布局（执行摘要、前后对比、三大支柱、漏斗图、框架矩阵、引言+证据、驱动因素分解树等），白底 navy 强调色，灵感源自 MBB 咨询报告。预设总数增至 22 种。

**v2.24.3** — 单 deck eval 与 production 验证发版：`--generate` / `render-from-brief` 现在支持通过 `--eval` 或 `--eval-out` 产出单份 deck 的评测 JSON；Data Story 的图表路由与标签逻辑会在数值信号不足时 fail closed，避免画出假趋势图；production demo fixture 也同步重验并更新到当前水印版本，保证核心 preset 验证持续为绿。

**v2.24.2** — Enterprise Dark / Chinese Chan 顶层 chrome 门禁加固：对于正式要求隐藏 `#brand-mark` 的 preset，校验器现在会直接拒绝泄漏左上角小标题；同时水印检查会校验当前 skill 版本号与 preset，防止旧 shell / 非 canonical 产物带着过期版本和技能名误过 `--strict`。

**v2.24.1** — 直接生成链路与写入前门禁修复：把“直接给内容 + 风格”的生成强制收回 `BRIEF.json -> render_from_brief()` 正式路径；让两个 CLI 渲染入口都在写最终文件前执行 `scripts/validate_html.py --strict`；并同步收紧 SKILL / workflow / 文档契约与回归测试，防止当前版本再次产出不符合 Chinese Chan canonical contract 的 HTML。

**v2.24.0** — 核心 preset 稳定性与质量门禁发版：新增 preset support tier 与 manifest 驱动的 eval / release gate 工具链，升级 low-context BRIEF 语义字段和 preset usage rules，修复 Chinese Chan 正式 contract 与 production/shared runtime 漂移，补齐第二轮家族 demo 运行时债务，把正式 HTML 校验器迁到 `scripts/validate_html.py` 并保留兼容 wrapper，同时收紧 Swiss Modern / shared shell 的页码与导航点 chrome，确保不同 preset 下都能正确可见。

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
