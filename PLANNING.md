**Task**: 制作一份介绍 kai-slide-creator 的 12 页幻灯片，Blue Sky 风格
**Mode**: 自动
**Slide count**: 12
**Language**: Chinese
**Audience**: 开发者、产品经理、内容创作者——需要快速制作高质量演示文稿的人群
**Goals**:
- 让听众理解 slide-creator 是什么、解决什么问题
- 展示核心功能：21 种设计预设、播放模式、演讲者模式、浏览器内编辑
- 演示使用方法和内容类型推荐
- 强调技术特点：零依赖、纯浏览器运行
**Style**: 清新、技术感、有视觉冲击力
**Preset**: Blue Sky

## Timing

- **Estimate**:
  - `plan`: 1 min
  - `generate`: 2-4 min
  - `validate`: <1 min
  - `polish`: 0-2 min
  - `total`: 3-7 min
- **Actual**:
  - `plan`:
  - `generate`:
  - `validate`:
  - `polish`:
  - `total`:

## Visual & Layout Guidelines

- **Overall tone**: 清新、技术感、企业级
- **Background**: Sky gradient #f0f9ff -> #e0f2fe with noise + grid
- **Primary text**: #0f172a
- **Accent**: #2563eb (blue-600)
- **Typography**: System fonts (PingFang SC, Microsoft YaHei, system-ui)
- **Components**: Use .g glass cards, .gt gradient text, .pill tags, .stat KPIs, .cloud elements, .layer rows, .bento grids, .ctable, .cmd blocks
- **Per-slide rule**: 每页 1 个核心观点 + 最多 5 个支撑要点；避免文字墙
- **Layout variety**: 不得连续 3 页使用相同布局，至少 50% 的幻灯片使用 2-3 种不同组件类型

## Slide-by-Slide Outline

**Slide 1 | Cover**
- Title: kai-slide-creator
- Subtitle: 零依赖 HTML 演示文稿生成器
- Pill: "21 种设计预设"
- Three stat cards in .g: 21 presets, 0 dependencies, 100% browser
- Visual: Cloud hero effect + gradient title + ambient orbs

**Slide 2 | Chapter: 问题**
- Chapter num: 01
- Title: 为什么需要另一种演示工具
- Subtitle: 现有工具的局限
- Visual: .cols2 对比卡片
  - .g .warn: 传统工具问题
    - PPT 模板千篇一律
    - AI 生成通用审美
    - 导出丢失设计细节
  - .g .green: 我们的思路
    - 从设计预设出发
    - 纯 HTML 运行
    - 浏览器内可编辑
- .info: 你拥有内容，AI 拥有结构和视觉表现

**Slide 3 | 21 种设计预设**
- Title: 21 种设计预设，每种都有签名视觉语言
- Subtitle: 避免通用 AI 审美
- Visual: .bento 网格展示 6 个代表风格
  - .span2: Bold Signal — 商业路演
  - .span2: Blue Sky — 清新技术
  - .g: Terminal Green — 开发工具
  - .g: Enterprise Dark — 数据看板
  - .span2: Modern Newspaper — 研究报告
  - .span2: Aurora Mesh — 产品发布

**Slide 4 | Chapter: 核心功能**
- Chapter num: 02
- Title: 三个核心模块，支撑全流程演示
- Subtitle: 播放、演讲、编辑——一个文件全部搞定
- Visual: .cols3 stat 卡片
  - .g: 播放模式 — F5 全屏
  - .g: 演讲者模式 — P 键同步窗口
  - .g: 浏览器内编辑 — E 键即改即存

**Slide 5 | 播放模式**
- Title: 播放模式 — 按 F5 即全屏
- Subtitle: 自动缩放适配，控制栏智能隐藏
- Visual: .layer 列表展示播放模式特性
  - .layer 1: F5 或点击播放按钮进入全屏
    - 自动隐藏控制栏和计数器
  - .layer 2: 幻灯片自动缩放适配屏幕
    - 保持设计比例不变形
  - .layer 3: 方向键/滚轮/触摸滑动翻页
    - 弹簧物理过渡动画
  - .layer 4: 无需安装任何播放器
    - 浏览器就是投影仪
- .info: 零依赖播放体验，任何设备打开即用

**Slide 6 | 演讲者模式**
- Title: 演讲者模式 — P 键打开同步窗口
- Subtitle: 观众看不到备注，你能看到一切
- Visual: .cols2 分栏
  - 左 .g: 观众看到的
    - 全屏幻灯片
    - 纯净无干扰
    - 自动缩放适配
  - 右 .cmd: 演讲者窗口
    - 演讲者备注
    - 倒计时器
    - 当前页/总页数
    - 翻页控制
- .co: 按 P 键打开，与主窗口同步翻页

**Slide 7 | 浏览器内编辑**
- Title: 浏览器内编辑 — 所见即所改
- Subtitle: 不用打开 PowerPoint 或 Figma
- Visual: .step 步骤卡片
  - .g: .step 1: 按 E 键进入编辑模式
    - 所有文字变为可编辑
  - .g: .step 2: 直接点击文字修改
    - 实时预览效果
  - .g: .step 3: Ctrl+S 保存为 HTML
    - 修改持久化到文件
- .info: 编辑模式默认开启，无需额外配置

**Slide 8 | Chapter: 使用方法**
- Chapter num: 03
- Title: 一条命令，三分钟出稿
- Subtitle: 从规划到生成，全程自动化
- Visual: .cols3 命令卡片
  - .g: /slide-creator --plan
    - 生成 PLANNING.md 大纲
    - 可编辑后再生成
  - .g: /slide-creator --generate
    - 从 PLANNING.md 生成 HTML
    - 执行 16 项质量校验
  - .g: /slide-creator --review
    - 对已有 HTML 执行检查点
    - 自动修复常见问题
- .divider
- .info: 也可直接给内容 + 风格，立即生成

**Slide 9 | 内容类型与风格推荐**
- Title: 什么内容配什么风格，一眼匹配
- Visual: .cols2 对比卡片
  - .g: 数据报告/KPI → Data Story, Enterprise Dark, Swiss Modern
  - .g: 商业路演/VC → Bold Signal, Aurora Mesh, Enterprise Dark
  - .g: 开发工具/API → Terminal Green, Neon Cyber, Neo-Retro Dev
  - .g: 研究报告 → Modern Newspaper, Paper & Ink, Swiss Modern
  - .g: 创意/个人品牌 → Vintage Editorial, Split Pastel, Neo-Brutalism
  - .g: 产品发布/SaaS → Aurora Mesh, Glassmorphism, Electric Studio

**Slide 10 | 技术特点**
- Title: 零依赖，纯浏览器运行
- Subtitle: 不依赖服务器、npm、构建工具
- Visual: .cols4 stat 行
  - .g: 0 — npm 包依赖
  - .g: 3 — 核心文件 HTML/CSS/JS
  - .g: ∞ — 可扩展场景
  - .g: 1 — 浏览器即运行环境
- .info: 生成的 HTML 文件完整自包含，双击即可在浏览器中打开

**Slide 11 | 版本历史**
- Title: 持续迭代，每周都在变强
- Visual: .layer 时间线
  - .layer 1: v1.x — 基础框架
    - 播放模式、编辑模式、首批 7 个预设
  - .layer 2: v1.5 — 风格扩展
    - 21 个预设、Cloud Bank Hero、Orbital Rings
  - .layer 3: v2.x — 智能生成
    - AI 规划、Review 系统、PPT 转换
  - .layer 4: v2.16 — 渲染引擎升级
    - 主题卡片、组件修饰符、26 项回归测试
- .co: GitHub + ClawHub 双渠道发布

**Slide 12 | Closing**
- Title: 从设计预设开始，让内容自己说话
- Subtitle: 不再从空白幻灯片挣扎
- Visual: Cloud hero effect + 中心 .g 卡片
  - .g (居中, 大 padding):
    - .pill: "开始使用"
    - .gt: /slide-creator "你的主题"
    - 3 分钟出第一稿
- Ambient orbs + cloud drift animation
