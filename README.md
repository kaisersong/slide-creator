# slide-creator

A skill for [Claude Code](https://claude.ai/claude-code) and [OpenClaw](https://openclaw.ai) that generates stunning, zero-dependency HTML presentations.

**v1.7** — Presenter Mode (`P` key opens speaker notes + timer + nav window), inline SVG diagram patterns (flowcharts, timelines, charts — no external libs), and a local custom theme system (`themes/` directory). 19 design presets. PPTX export via Playwright + system Chrome, no Node.js.

English | [简体中文](README.zh-CN.md)

<details>
<summary>📖 简体中文 / 点击展开（ClawHub 用户）</summary>

## slide-creator

适用于 [Claude Code](https://claude.ai/claude-code) 和 [OpenClaw](https://openclaw.ai) 的演示文稿生成 skill，零依赖、纯浏览器运行的 HTML 幻灯片。

## 功能特性

- **两阶段工作流** — `--plan` 生成大纲，`--generate` 输出幻灯片
- **19 种设计预设** — Bold Signal、Blue Sky、Neon Cyber、Dark Botanical 等
- **视觉风格探索** — 先生成 3 个预览，看图选风格而非描述风格
- **演讲者模式** — 按 `P` 打开同步演讲者窗口：备注、计时器、页数、翻页导航；窗口高度随备注内容自动调整
- **内联 SVG 图表** — 流程图、时间轴、条形图、对比矩阵、组织架构图，无需 Mermaid.js 或外部库
- **自定义主题系统** — 在 `themes/你的主题/` 放入 `reference.md` 即可添加专属设计预设；可选提供 `starter.html`
- **Blue Sky Starter 模板** — 完整 boilerplate，任何模型都能正确实现全套视觉系统
- **图片处理流水线** — 自动评估和处理素材（Pillow）
- **PPT 导入** — 将 `.pptx` 文件转换为网页演示
- **PPTX 导出** — `--export pptx`，通过 Playwright + 系统 Chrome 导出
- **浏览器内编辑** — 直接在浏览器中编辑文字，Ctrl+S 保存
- **视口自适应** — 每张幻灯片精确填充 100vh，永不出现滚动条
- **中英双语** — 完整支持中文内容

## 安装

### Claude Code

```bash
git clone https://github.com/kaisersong/slide-creator ~/.claude/skills/slide-creator
```

重启 Claude Code，使用 `/slide-creator` 调用。

### OpenClaw

```bash
# 通过 ClawHub 安装（推荐）
clawhub install html-slide-creator

# 或手动克隆
git clone https://github.com/kaisersong/slide-creator ~/.openclaw/skills/slide-creator
```

OpenClaw 首次使用时会自动安装依赖（Pillow、python-pptx、playwright）。

## 使用方法

```
/slide-creator --plan       # 分析内容和 resources/ 目录，生成 PLANNING.md 大纲
/slide-creator --generate   # 根据 PLANNING.md 生成 HTML 演示文稿
/slide-creator --export pptx  # 导出为 PowerPoint
/slide-creator              # 从零开始（交互式风格探索）
```

### 典型工作流

**方式一：交互式创建**
1. 运行 `/slide-creator`，回答目的、长度、内容和图片等问题
2. 查看 3 个风格预览，选择喜欢的风格
3. 生成完整演示文稿，在浏览器中打开

**方式二：两阶段工作流（复杂内容推荐）**
1. 在项目目录放入素材（`resources/` 文件夹）
2. 运行 `/slide-creator --plan 我的AI创业公司融资路演`
3. 审阅 `PLANNING.md` 大纲，确认后运行 `/slide-creator --generate`

**方式三：PPT 转换**
1. 将 `.pptx` 文件放到当前目录
2. 运行 `/slide-creator`，Skill 会自动识别并提取内容

## 依赖要求

| 依赖 | 用途 | OpenClaw 自动安装 |
|------|------|------------------|
| Python 3 + `Pillow` | 图片处理 | ✅ via uv |
| Python 3 + `python-pptx` | PPT 导入/导出 | ✅ via uv |
| Python 3 + `playwright` | PPTX 导出（使用系统 Chrome） | ✅ via uv |

不需要 Node.js。PPTX 导出使用你已安装的 Chrome/Edge/Brave，无需下载 300MB 的 Chromium。

**Claude Code 用户** 需手动安装：
```bash
pip install Pillow python-pptx playwright
```

## 输出文件

- `presentation.html` — 零依赖单文件，直接用浏览器打开
- `PRESENTATION_SCRIPT.md` — 演讲稿（幻灯片 8 张以上时自动生成）
- `*.pptx` — 通过 `--export pptx` 导出

## 浏览器内编辑

生成的演示文稿内置文字编辑功能，无需修改 HTML 源码。

- 将鼠标移到屏幕**左上角** → 出现编辑按钮，点击即可
- 或直接按键盘 **`E`** 键
- **`Ctrl+S`**（Mac 上为 `Cmd+S`）— 保存修改到 HTML 文件

## 演讲者模式

按 **`P`** 键打开演讲者窗口，包含：当前幻灯片备注、计时器、上一张/下一张导航、总页数。窗口高度根据备注内容自动调整。

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

## 兼容性

| 平台 | 版本 | 安装路径 |
|------|------|----------|
| Claude Code | 任意 | `~/.claude/skills/slide-creator/` |
| OpenClaw | ≥ 0.9 | `~/.openclaw/skills/slide-creator/` |

</details>

## Live Demo

See what slide-creator produces — open directly in your browser:

- 🇺🇸 [slide-creator intro (English)](https://kaisersong.github.io/slide-creator/demos/intro-en.html) — what the skill is and how it works
- 🇨🇳 [slide-creator 介绍（中文）](https://kaisersong.github.io/slide-creator/demos/intro-zh.html) — 同上，中文版

Both demos above use the Blue Sky style. Click any screenshot below to open the live demo:

<table>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/intro-en.html"><img src="demos/screenshots/blue-sky.png" width="240" alt="Blue Sky"/><br/><b>Blue Sky</b> ✨</a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/bold-signal.html"><img src="demos/screenshots/bold-signal.png" width="240" alt="Bold Signal"/><br/><b>Bold Signal</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/electric-studio.html"><img src="demos/screenshots/electric-studio.png" width="240" alt="Electric Studio"/><br/><b>Electric Studio</b></a></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/creative-voltage.html"><img src="demos/screenshots/creative-voltage.png" width="240" alt="Creative Voltage"/><br/><b>Creative Voltage</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/dark-botanical.html"><img src="demos/screenshots/dark-botanical.png" width="240" alt="Dark Botanical"/><br/><b>Dark Botanical</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/notebook-tabs.html"><img src="demos/screenshots/notebook-tabs.png" width="240" alt="Notebook Tabs"/><br/><b>Notebook Tabs</b></a></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/pastel-geometry.html"><img src="demos/screenshots/pastel-geometry.png" width="240" alt="Pastel Geometry"/><br/><b>Pastel Geometry</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/split-pastel.html"><img src="demos/screenshots/split-pastel.png" width="240" alt="Split Pastel"/><br/><b>Split Pastel</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/vintage-editorial.html"><img src="demos/screenshots/vintage-editorial.png" width="240" alt="Vintage Editorial"/><br/><b>Vintage Editorial</b></a></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/neon-cyber.html"><img src="demos/screenshots/neon-cyber.png" width="240" alt="Neon Cyber"/><br/><b>Neon Cyber</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/terminal-green.html"><img src="demos/screenshots/terminal-green.png" width="240" alt="Terminal Green"/><br/><b>Terminal Green</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/swiss-modern.html"><img src="demos/screenshots/swiss-modern.png" width="240" alt="Swiss Modern"/><br/><b>Swiss Modern</b></a></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/paper-ink.html"><img src="demos/screenshots/paper-ink.png" width="240" alt="Paper &amp; Ink"/><br/><b>Paper &amp; Ink</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/aurora-mesh.html"><img src="demos/screenshots/aurora-mesh.png" width="240" alt="Aurora Mesh"/><br/><b>Aurora Mesh</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/enterprise-dark.html"><img src="demos/screenshots/enterprise-dark.png" width="240" alt="Enterprise Dark"/><br/><b>Enterprise Dark</b></a></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/glassmorphism.html"><img src="demos/screenshots/glassmorphism.png" width="240" alt="Glassmorphism"/><br/><b>Glassmorphism</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/neo-brutalism.html"><img src="demos/screenshots/neo-brutalism.png" width="240" alt="Neo-Brutalism"/><br/><b>Neo-Brutalism</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/chinese-chan.html"><img src="demos/screenshots/chinese-chan.png" width="240" alt="Chinese Chan"/><br/><b>Chinese Chan</b></a></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/data-story.html"><img src="demos/screenshots/data-story.png" width="240" alt="Data Story"/><br/><b>Data Story</b></a></td>
<td></td><td></td>
</tr>
</table>

Every demo uses the same content (slide-creator's own introduction) — making it easy to compare how the same topic looks across completely different design philosophies.

---

## Features

- **Two-stage workflow** — `--plan` to outline, `--generate` to produce
- **19 design presets** — Bold Signal, Blue Sky, Neon Cyber, Dark Botanical, and more
- **Style discovery** — Generate 3 visual previews before committing to a style
- **Presenter Mode** — Press `P` to open a synced speaker window: notes, timer, slide counter, prev/next nav; window height auto-adapts to notes length
- **Inline SVG diagrams** — Flowcharts, timelines, bar charts, comparison grids, org charts — no Mermaid.js, no external libs
- **Custom theme system** — Drop a `reference.md` into `themes/your-theme/` to add your own design preset; `starter.html` optional for complex visual systems
- **Blue Sky starter template** — Complete boilerplate so models never mis-implement the visual system
- **Image pipeline** — Auto-evaluate and process assets (Pillow)
- **PPT import** — Convert `.pptx` files to web presentations
- **PPTX export** — `--export pptx` via Playwright + system Chrome
- **Inline editing** — Edit text in-browser, Ctrl+S to save
- **Viewport fitting** — Every slide fits exactly in 100vh, no scrolling ever
- **Bilingual** — Chinese / English support

---

## Install

### Claude Code

```bash
git clone https://github.com/kaisersong/slide-creator ~/.claude/skills/slide-creator
```

Restart Claude Code. Use as `/slide-creator`.

### OpenClaw

```bash
# Via ClawHub (recommended)
clawhub install html-slide-creator

# Or manually
git clone https://github.com/kaisersong/slide-creator ~/.openclaw/skills/slide-creator
```

> ClawHub page: https://clawhub.ai/skills/html-slide-creator

OpenClaw will automatically detect and install dependencies (Pillow, python-pptx, playwright) on first use.

---

## Usage

```
/slide-creator --plan       # Analyze content + resources/, create PLANNING.md
/slide-creator --generate   # Generate HTML presentation from PLANNING.md
/slide-creator --export pptx  # Export to PowerPoint
/slide-creator              # Start from scratch (interactive style discovery)
```

## Requirements

| Dependency | Purpose | Auto-installed (OpenClaw) |
|-----------|---------|--------------------------|
| Python 3 + `Pillow` | Image processing | ✅ via uv |
| Python 3 + `python-pptx` | PPT import/export | ✅ via uv |
| Python 3 + `playwright` | PPTX export (uses system Chrome) | ✅ via uv |

Node.js is not required. PPTX export uses your existing Chrome/Edge/Brave — no 300MB Chromium download.

**Claude Code users** — install manually:
```bash
pip install Pillow python-pptx playwright
```

## Output

Single-file `presentation.html` — zero dependencies, runs entirely in the browser.

Optionally exports `PRESENTATION_SCRIPT.md` (speaker notes) and `.pptx`.

---

## Inline Editing

Every generated presentation includes a built-in text editor — no need to touch the HTML file.

**How to enter edit mode:**

- Hover the **top-left corner** of the screen → an edit button appears, click it
- Or press **`E`** on your keyboard

**In edit mode:**

- Click any text on the slide to edit it directly
- **`Ctrl+S`** (or `Cmd+S` on Mac) — save changes back to the HTML file
- **`Escape`** — exit edit mode without saving

**To enable inline editing**, answer "Yes" when slide-creator asks during setup (it's the recommended default). If you generated a presentation without it, just re-run `/slide-creator --generate` and opt in.

---

## Design Presets

**19 curated styles — no generic AI aesthetics.**

| Preset | Vibe | Best For |
|--------|------|----------|
| **Bold Signal** | Confident, high-impact | Pitch decks, keynotes |
| **Electric Studio** | Clean, professional | Agency presentations |
| **Creative Voltage** | Energetic, retro-modern | Creative pitches |
| **Dark Botanical** | Elegant, sophisticated | Premium brands |
| **Blue Sky** ✨ | Airy, enterprise SaaS | Product launches, tech decks |
| **Notebook Tabs** | Editorial, organized | Reports, reviews |
| **Pastel Geometry** | Friendly, approachable | Product overviews |
| **Split Pastel** | Playful, modern | Creative agencies |
| **Vintage Editorial** | Witty, personality-driven | Personal brands |
| **Neon Cyber** | Futuristic, techy | Tech startups |
| **Terminal Green** | Developer-focused | Dev tools, APIs |
| **Swiss Modern** | Minimal, precise | Corporate, data |
| **Paper & Ink** | Literary, thoughtful | Storytelling |
| **Aurora Mesh** | Vibrant, premium SaaS | Product launches, VC pitch |
| **Enterprise Dark** | Authoritative, data-driven | B2B, investor decks, strategy |
| **Glassmorphism** | Light, translucent, modern | Consumer tech, brand launches |
| **Neo-Brutalism** | Bold, uncompromising | Indie dev, creative manifesto |
| **Chinese Chan** | Still, contemplative | Design philosophy, brand, culture |
| **Data Story** | Clear, precise, persuasive | Business review, KPI, analytics |

### Blue Sky

Light sky-blue gradient background (`#f0f9ff → #e0f2fe`) with floating glassmorphism cards and animated ambient orbs. Inspired by a real enterprise AI pitch deck — the CloudHub V12 MVP presentation. Feels like a high-altitude clear day: open, confident, premium.

Signature elements: grainy noise texture overlay · 3 animated blur orbs repositioning per slide · glassmorphism cards with backdrop-filter · 40px tech grid with radial mask · spring-physics horizontal slide transitions · cloud hero effect on title slides.

A complete starter template (`references/blue-sky-starter.html`) ships with the skill — all 10 signature visual elements are pre-built so models only need to fill in slide content.

---

## Compatibility

| Platform | Version | Install path |
|---------|---------|-------------|
| Claude Code | any | `~/.claude/skills/slide-creator/` |
| OpenClaw | ≥ 0.9 | `~/.openclaw/skills/slide-creator/` |
