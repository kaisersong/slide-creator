**Task**: Create a product intro deck for slide-creator in Blue Sky style
**Mode**: 自动 / Auto
**Slide count**: 8
**Language**: Chinese
**Audience**: Developers and product people evaluating presentation tools
**Goals**:
- Introduce slide-creator's core value proposition
- Show the 21 presets and visual quality
- Demonstrate key features (present mode, editor, presenter view)
- Drive adoption (GitHub star, install)
**Style**: Clean, airy, premium SaaS
**Preset**: Blue Sky

## Timing

- **Estimate**:
  - `plan`: 1 min
  - `generate`: 3-5 min
  - `validate`: <1 min
  - `polish`: 0 min (Auto mode)
  - `total`: 4-6 min

## Visual & Layout Guidelines

- **Overall tone**: Clean, airy, enterprise-ready
- **Background**: Sky gradient #f0f9ff → #e0f2fe with noise + grid
- **Primary text**: #0f172a
- **Accent**: #2563eb (blue-600)
- **Typography**: System fonts (PingFang SC, Microsoft YaHei, system-ui)
- **Components**: Use .g glass cards, .gt gradient text, .pill tags, .stat KPIs, .cloud elements
- **Per-slide rule**: 1 key point + up to 5 supporting bullets; no text walls

## Slide-by-Slide Outline

**Slide 1 | Cover**
- Title: AI 驱动的 HTML 演示文稿
- Subtitle: 从提示词到精美演示，秒速完成。零依赖。浏览器原生。无限编辑。
- Visual: Cloud layer at bottom, 3 ambient orbs, .pill + .stat x3

**Slide 2 | Problem**
- Title: 传统工具限制了你
- .pill: 为什么选择 slide-creator
- .cols2
  - .g .warn: ❌ 传统方法
    - 从空白幻灯片开始 — 结构是你的问题
    - 花费数小时调整字体、对齐和颜色
    - PPTX 在其他机器上损坏，字体丢失
  - .g .green: ✓ slide-creator
    - 描述你的主题 — AI 规划结构
    - 21 个主题，自动匹配你的内容类型
    - 单个 HTML 文件，在任何地方呈现完全相同
- .info: **设计原则：**你拥有内容。AI 拥有结构和视觉表现。

**Slide 3 | Solution**
- Title: 从想法到演示的三步
- .pill: 工作流
- .layer 1: 描述你的主题
  - 告诉 slide-creator 你想呈现什么 — 受众、目标、核心信息
  - .cmd: /slide "第一季度业务审查，面向领导层 — 重点关注增长和留存"
- .layer 2: 审查计划（可选）
  - 使用 `--plan` 先获得结构化大纲文件。编辑它，然后在准备好时运行 `--generate`
- .layer 3: 在浏览器中打开 — 完成
  - 单个自包含的 HTML 文件。内置键盘导航、触摸滑动、全屏和编辑模式

**Slide 4 | Presets**
- Title: 21 个主题适应所有场景
- .pill: 按内容类型自动匹配
- .cols4
  - .g .theme: 深色 · 4 个主题
    - Bold Signal
    - Electric Studio
    - Creative Voltage
    - Dark Botanical
    - 演讲 · 品牌 · 技术分享
  - .g .theme .highlight: 浅色 · 5 个主题
    - Blue Sky ★ 本演示
    - Notebook Tabs
    - Pastel Geometry
    - Split Pastel
    - Vintage Editorial
    - 教育 · 内部 · 创意
  - .g .theme: 专业 · 4 个主题
    - Neon Cyber
    - Terminal Green
    - Swiss Modern
    - Paper & Ink
    - 开发 · 学术 · 极简
  - .g .theme .highlight: v1.5 新增 · 8 个主题
    - Aurora Mesh
    - Enterprise Dark
    - Glassmorphism
    - Neo-Brutalism
    - Chinese Chan
    - Data Story
    - Modern Newspaper
    - Neo-Retro Dev Deck
    - 高级 · 数据 · 创意

**Slide 5 | Present Mode**
- Title: 演示模式 — 自由导航
- .pill: 功能
- .cols2
  - .g: 导航快捷键
    - .kbd: → Space ↓ 下一个幻灯片
    - .kbd: ← ↑ 上一个幻灯片
    - .kbd: Home / End 第一个/最后一个
    - .kbd: F 切换全屏
    - .kbd: E 切换编辑模式
  - .layer ⛶: 按 F 或点击按钮
    - 进入原生浏览器全屏，模式栏和计数器自动隐藏
  - .layer 🎞: 弹簧物理过渡
    - 水平轨道带 cubic-bezier — 幻灯片感觉有重量和自然
  - .layer 📱: 触摸和移动就绪
    - 带惯性防抖的左/右滑动

**Slide 6 | Editor**
- Title: 编辑模式 — 立即修复任何内容
- .pill: 功能
- .cols2
  - .layer ✏: 点击任何文本进行编辑
    - 每个标题、段落和列表项都变成 `contenteditable`
  - .layer ⌨: 键盘快捷键
    - 按 `E` 在演示文稿的任何位置切换编辑模式
  - .layer 💾: 在浏览器中实时编辑
    - 使用 `⌘S` / `Ctrl+S` 保存文件以捕获更改
  - .info: 立即切换到编辑模式 — 按 `E` 或点击左上角 **✏ 编辑**

**Slide 7 | Quality**
- Title: 为 AI 时代而建
- .pill: 架构
- .cols3
  - .g: 0
    - npm 包 — 纯 HTML/CSS/JS
  - .g: 3
    - AI 可读层 — 摘要 JSON → 注释 → 组件数据
  - .g: ∞
    - 保质期 — 无 SaaS 订阅，无厂商锁定
- .cols2
  - .co: **图表库：**通过 CDN 使用 Chart.js。使用 `--bundle` 内联所有 JS 供离线使用。
  - .info: **AI 管道友好：**每个幻灯片嵌入 `data-component` 属性，下游代理可以解析和复用内容

**Slide 8 | CTA**
- Title: 别再"做幻灯片"了，开始讲故事
- .gt: GitHub Star → github.com/kaisersong/slide-creator
- .cmd: pipx install slide-creator
