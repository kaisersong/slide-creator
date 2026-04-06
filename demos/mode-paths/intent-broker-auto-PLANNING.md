**Task**: 把 `Intent Broker v1` 设计文档做成一版可快速讲解的架构说明幻灯片
**Mode**: 自动
**Slide count**: 8 ± 1
**Language**: Chinese
**Audience**: 正在评估是否立项或接入 Intent Broker 的工程负责人、架构师、Agent 工具开发者
**Goals**:
- 快速讲清 Intent Broker 是什么、解决什么问题
- 让听众在一轮演示内理解协议边界、核心模型和系统结构
**Style**: 清晰、可信、技术架构感、偏咨询式表达
**Preset**: Enterprise Dark

## Timing

- **Estimate**:
  - `plan`: 1-2 min
  - `generate`: 1-3 min
  - `validate`: <1 min
  - `polish`: 0-2 min
  - `total`: 3-6 min
- **Actual**:
  - `plan`: 0m 00s (reused approved plan)
  - `generate`: 0m 22s
  - `validate`: 0m 13s
  - `polish`: 0m 00s
  - `total`: 0m 35s

---

## Visual & Layout Guidelines

- **Overall tone**: 冷静、清晰、偏系统设计评审
- **Background**: 深色底 + 细网格，突出架构和状态机
- **Primary text**: 高对比浅色文字
- **Accent (primary)**: `#3D5A80` navy / blue，用于结构和关键术语
- **Typography**: PingFang SC / system-ui
- **Per-slide rule**: 一页一个关键判断，最多 4 个支持点
- **Animations**: 最轻量 reveal，只做层级提示

---

## Slide-by-Slide Outline

**Slide 1 | Cover**
- Title: Intent Broker
- Subtitle: 本地优先、多 agent 协作协议中间层
- Visual: 标题 + 3 个关键特征数字

**Slide 2 | Problem**
- Key point: 现有 agent 协作依赖聊天和临时约定，缺少稳定任务语义
- Supporting:
  - 任务流不可审计
  - 断线易丢上下文
  - 不同 agent 接入成本高
- Visual element: 痛点列表
- Speaker note: 先解释为什么需要 broker，而不是直接介绍实现

**Slide 3 | Product Definition**
- Key point: Intent Broker 不做推理和工具执行，只做协作协议与可靠投递
- Supporting:
  - 协议优先
  - 事件优先
  - HTTP pull 为主
- Visual element: 责任边界对照
- Speaker note: 用“做什么 / 不做什么”快速划边界

**Slide 4 | Core Concepts**
- Key point: 系统围绕 Participant、Intent、Task、Thread、Approval 五个对象组织
- Supporting:
  - Participant 表示协作方
  - Intent 表示协作动作
  - Task/Thread/Approval 组织上下文与决策
- Visual element: 关系图
- Speaker note: 这是后续状态机和架构图的基础

**Slide 5 | State Machines**
- Key point: 任务和审批都由少量稳定状态推进，不允许客户端随意写状态
- Supporting:
  - Task: open → assigned → in_progress → submitted → completed
  - Approval: pending → approved / rejected / expired
- Visual element: 双状态机摘要
- Speaker note: 强调聚合状态来自 intent 事件，而不是直接写库

**Slide 6 | Reliability Model**
- Key point: 先写事件，再投递 inbox；WebSocket 只是增强，不是真相源
- Supporting:
  - SQLite append-only events
  - participant cursor
  - 至少一次投递 + 幂等
- Visual element: 事件流流程图
- Speaker note: 这页是 v1 的核心价值

**Slide 7 | Architecture & API**
- Key point: v1 是本地单进程 broker，六个核心组件围绕 event store 工作
- Supporting:
  - broker-server
  - event-store / projection-engine / router / policy-layer / adapters
  - 核心 HTTP API
- Visual element: 组件分层图
- Speaker note: 解释为什么它适合先从本地基础设施切入

**Slide 8 | Verification & Next Step**
- Key point: v1 要先验证任务协作 + 审批闭环，再考虑远程化和 UI
- Supporting:
  - 协议单测
  - 路由 / 可靠性 / 集成测试
  - 后续演进路径
- Visual element: 验证清单 + next step
- Speaker note: 用测试策略收束，让方案显得可落地

---

## Resources Used

- `D:\projects\mydocs\intent-broker\docs\superpowers\specs\2026-03-31-intent-broker-design.md` → 全部页面的事实来源

---

## Images

- No external images required

---

## Deliverables

- Output: `intent-broker-auto.html` (single-file, zero dependencies)
- Optional: `intent-broker-auto-script.md` (speaker notes)
- Inline editing: Yes
