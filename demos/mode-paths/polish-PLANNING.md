**Task**: 为 slide-creator 准备一份 10 页的对外能力介绍 deck，强调结构、视觉锁定和页面级图片表达
**Mode**: 精修
**Slide count**: 10 ± 1
**Language**: Chinese
**Audience**: 希望把现有内容升级成高质量演示稿的产品负责人、设计负责人、技术负责人
**Goals**:
- 证明 slide-creator 不只是快速出稿，也能支持高保真规划
- 展示从叙事结构到视觉锁定的完整精修路径
**Style**: 稳定、克制、叙事驱动、偏高端产品营销
**Preset**: Aurora Mesh

## Deck Thesis

- slide-creator 的真正优势不只是生成速度，而是能在需要时把 deck 的叙事、视觉系统和图片表达一起锁住。

## Narrative Arc

- Opening: 先指出“快出稿”和“高质量成稿”常被迫二选一
- Middle: 证明 slide-creator 用 `精修` 把 thesis、page roles、style constraints 和 image intent 一起前置
- Ending: 给出产品 framing：默认快，必要时深

## Page Roles

- Slide 1: Hook cover，建立“速度与质量不必二选一”
- Slide 2: Problem framing，解释为什么普通 AI deck 容易散
- Slide 3: Product framing，给出 `自动` / `精修` 两档
- Slide 4: Narrative proof，解释 thesis + arc 的价值
- Slide 5: Visual lock，解释 style constraints 的作用
- Slide 6: Image reasoning，说明 image intent 只在必要页面出现
- Slide 7: `参考驱动` internal branch，说明它不是第三模式
- Slide 8: Workflow proof，展示从 plan 到 generate 的精修路径
- Slide 9: Output quality，强调浏览器原生交付与可编辑性
- Slide 10: Closing CTA，邀请用真实内容试跑精修路径

## Style Constraints

- 所有标题左对齐，正文区保持 8 栏栅格的稳定边界
- 每 3 页至少有 1 页明显的视觉节奏变化，避免连续 bullet wall
- 强证据页必须使用图像、图表或大数字其中之一，不允许只用泛 bullets
- 参考驱动仅用于锁定视觉 precedent，不改变 `精修` 作为唯一深度模式的产品表述

## Image Intent

- Slide 1: 使用抽象 hero image，表达“质量提升”的情绪，而不是产品截图；搜索方向为 premium editorial abstract light beam
- Slide 6: 使用单张产品界面或 deck 预览图，承担“页面级视觉证据”任务；搜索方向为 polished browser presentation UI
- Slide 7: 若需要引用视觉 precedent，可走 `参考驱动` 子步骤，记录参考方向为 clean SaaS keynote / editorial product launch，而不是新增第三模式

---

## Visual & Layout Guidelines

- **Overall tone**: 高保真、克制、叙事感强
- **Background**: `#07111F` deep navy with soft mesh lighting
- **Primary text**: `#F6F8FB`
- **Accent (primary)**: `#B45309` amber for narrative emphasis
- **Typography**: Space Grotesk + DM Sans
- **Per-slide rule**: 每页只服务一个 page role
- **Animations**: 低频次 reveal，重点页允许更明显的 staged motion

---

## Slide-by-Slide Outline

**Slide 1 | Cover**
- Title: Slide Creator
- Subtitle: 默认快，必要时深
- Visual: 深色 mesh 背景 + 单句 thesis

**Slide 2 | Problem**
- Key point: 快速生成常常牺牲叙事和视觉一致性
- Supporting:
  - 结构松散
  - 节奏重复
  - 图片只是“塞进去”
- Visual element: tension diagram
- Speaker note: 建立为什么需要 `精修`

**Slide 3 | Two Depths**
- Key point: 用户只需要理解 `自动` 和 `精修`
- Supporting:
  - `自动` 负责速度
  - `精修` 负责结构与锁定
  - `参考驱动` 只是内部视觉分支
- Visual element: 双栏对照
- Speaker note: 这是产品 framing 页

**Slide 4 | Thesis + Arc**
- Key point: 先锁叙事，再写页面
- Supporting:
  - thesis 决定主张
  - arc 决定节奏
  - page roles 决定每页职责
- Visual element: story arc diagram
- Speaker note: 解释上游决策如何改善输出质量

**Slide 5 | Style Constraints**
- Key point: 精修不是“挑个好看主题”就结束
- Supporting:
  - 视觉边界更明确
  - 页面节奏更稳定
  - 品牌约束更可控
- Visual element: constraint cards
- Speaker note: 把视觉锁定讲清楚

**Slide 6 | Image Intent**
- Key point: 图片只在承担沟通任务时出现
- Supporting:
  - 决定要不要图
  - 决定图为何存在
  - 决定搜索或参考方向
- Visual element: image-role matrix
- Speaker note: 强调 image intent 不是默认成本

**Slide 7 | Internal Reference Branch**
- Key point: `参考驱动` 留在 `精修` 里，而不是变成第三模式
- Supporting:
  - 降低用户认知负担
  - 保留高保真视觉锁定能力
  - 产品结构更好解释
- Visual element: nested flow diagram
- Speaker note: 这里明确产品简化逻辑

**Slide 8 | Workflow**
- Key point: 精修路径只是多了更强的 planning，而不是多文件工厂
- Supporting:
  - 仍然只产出一个 `PLANNING.md`
  - 生成契约不变
  - HTML 交付能力不变
- Visual element: linear workflow
- Speaker note: 强调改的是 planning depth，不是 rendering contract

**Slide 9 | Output Contract**
- Key point: 精修输出仍是单文件 HTML，可播放、可编辑、可导出
- Supporting:
  - Presentation Mode
  - Edit Mode 默认开启
  - 可接 kai-html-export
- Visual element: output capability strip
- Speaker note: 连接产品价值闭环

**Slide 10 | Closing**
- Summary statement: 用两档深度覆盖大多数 deck 需求
- Call to action or contact info: 先跑自动，再在关键 deck 上用精修锁质量

---

## Resources Used

- Planning from prompt only

---

## Images

- `hero-abstract` → Slide 1 情绪化封面图
- `ui-preview` → Slide 6 页面级证据图

---

## Deliverables

- Output: `slide-creator-polish-demo.html` (single-file, zero dependencies)
- Optional: PRESENTATION_SCRIPT.md (speaker notes)
- Inline editing: Yes
