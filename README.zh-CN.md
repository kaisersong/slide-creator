# slide-creator

适用于 [Claude Code](https://claude.ai/claude-code) 和 [OpenClaw](https://openclaw.ai) 的演示文稿生成 skill，零依赖、纯浏览器运行的 HTML 幻灯片。

**v1.4.1** — 新增 **Blue Sky** 设计预设（天空渐变 · 玻璃拟态卡片 · 动态光球），共 13 种风格。Blue Sky 现在附带完整 starter 模板，确保任何模型都能正确生成全套视觉效果。PPTX 导出使用 Playwright + 系统已安装的 Chrome，像素级还原，无需下载 Chromium 或 Node.js。

[English](README.md) | 简体中文

## 效果演示

用浏览器直接打开，零安装查看效果：

- 🇨🇳 [slide-creator 介绍（中文）](demos/intro-zh.html) — 功能和使用方式介绍
- 🇺🇸 [slide-creator intro (English)](demos/intro-en.html) — same in English

以上演示文稿均由 slide-creator 自己生成，使用 Blue Sky 风格。

---

## 功能特性

- **两阶段工作流** — `--plan` 生成大纲，`--generate` 输出幻灯片
- **13 种设计预设** — Bold Signal、Blue Sky、Neon Cyber、Dark Botanical 等
- **视觉风格探索** — 先生成 3 个预览，看图选风格而非描述风格
- **Blue Sky Starter 模板** — 完整 boilerplate，任何模型都能正确实现全套视觉系统
- **图片处理流水线** — 自动评估和处理素材（Pillow）
- **PPT 导入** — 将 `.pptx` 文件转换为网页演示
- **PPTX 导出** — `--export pptx`，通过 Playwright + 系统 Chrome 导出
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
clawhub install html-slide-creator

# 或手动克隆
git clone https://github.com/kaisersong/slide-creator ~/.openclaw/skills/slide-creator
```

> ClawHub 页面：https://clawhub.ai/skills/html-slide-creator

OpenClaw 首次使用时会自动安装依赖（Pillow、python-pptx、playwright）。

---

## 使用方法

```
/slide-creator --plan       # 分析内容和 resources/ 目录，生成 PLANNING.md 大纲
/slide-creator --generate   # 根据 PLANNING.md 生成 HTML 演示文稿
/slide-creator --export pptx  # 导出为 PowerPoint
/slide-creator              # 从零开始（交互式风格探索）
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
| Python 3 + `Pillow` | 图片处理 | ✅ via uv |
| Python 3 + `python-pptx` | PPT 导入/导出 | ✅ via uv |
| Python 3 + `playwright` | PPTX 导出（使用系统 Chrome） | ✅ via uv |

不再需要 Node.js。PPTX 导出使用你已安装的 Chrome/Edge/Brave，无需下载 300MB 的 Chromium。

**Claude Code 用户** 需手动安装：
```bash
pip install Pillow python-pptx playwright
```

---

## 输出文件

- `presentation.html` — 零依赖单文件，直接用浏览器打开
- `PRESENTATION_SCRIPT.md` — 演讲稿（幻灯片 8 张以上时自动生成）
- `*.pptx` — 通过 `--export pptx` 导出

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

### Blue Sky

天空渐变背景（`#f0f9ff → #e0f2fe`）搭配浮动玻璃拟态卡片与动态环境光球。灵感来自真实的企业 AI 路演文稿（CloudHub V12 MVP），呈现出高空晴日般开阔、自信、精致的视觉气质。

标志性元素：SVG 颗粒噪声纹理叠层 · 3 个按幻灯片类型重新布阵的模糊光球 · `backdrop-filter: blur(24px)` 玻璃拟态卡片 · 40px 科技网格底层 · 弹簧物理横向切换动画 · 封面专属双层流动云朵效果。

附带完整 starter 模板（`references/blue-sky-starter.html`）—— 全部 10 个签名视觉元素预置完毕，模型只需填充幻灯片内容即可。

---

## 兼容性

| 平台 | 版本 | 安装路径 |
|------|------|----------|
| Claude Code | 任意 | `~/.claude/skills/slide-creator/` |
| OpenClaw | ≥ 0.9 | `~/.openclaw/skills/slide-creator/` |
