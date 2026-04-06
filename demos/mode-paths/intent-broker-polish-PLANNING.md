**Task**: 把 `Intent Broker v1` 设计文档做成一版更强叙事、更适合正式评审和对外同步的高保真架构幻灯片
**Mode**: 精修
**Slide count**: 10 ± 1
**Language**: Chinese
**Audience**: 对协议设计、可靠性和多 agent 协作基础设施有判断权的技术负责人、产品负责人、潜在协作者
**Goals**:
- 把 Intent Broker 讲成“为什么现在值得做”的基础设施故事，而不只是模块清单
- 用页面级结构和图示把本地优先、协议优先、可靠优先讲透
**Style**: 深色、高密度、克制但有节奏、偏产品化架构叙事
**Preset**: Enterprise Dark

## Timing

- **Estimate**:
  - `plan`: 2-4 min
  - `generate`: 2-4 min
  - `validate`: <1 min
  - `polish`: 2-6 min
  - `total`: 8-15 min
- **Actual**:
  - `plan`: 0m 00s (reused approved plan)
  - `generate`: 0m 13s
  - `validate`: 0m 14s
  - `polish`: 0m 00s
  - `total`: 0m 27s

## Deck Thesis

- Intent Broker 的价值不在“多一个聊天通道”，而在把多 agent 协作从临时对话升级成可重放、可审计、可恢复的本地协议基础设施。

## Narrative Arc

- Opening: 从“为什么现有协作方式不可靠”切入，制造必要性
- Middle: 依次解释设计原则、核心对象、可靠性模型和系统架构，建立可信度
- Ending: 用测试策略和演进路径说明它是一个可以从 v1 开始落地的基础设施项目

## Page Roles

- Slide 1: Hook / establish urgency
- Slide 2: Problem framing
- Slide 3: Product thesis and scope boundary
- Slide 4: Design principles
- Slide 5: Core concept map
- Slide 6: Task + approval lifecycle
- Slide 7: Event delivery and reliability proof
- Slide 8: Architecture decomposition
- Slide 9: API + testing readiness
- Slide 10: Closing and rollout framing

## Style Constraints

- 每一页必须回答一个完整判断，不允许泛泛“功能罗列”
- 图示页优先于 bullet 页，避免连续三页纯列表
- 所有标题保持左对齐，建立稳定的审阅节奏
- 状态推进和数据流都要用方向性图示，不只写名称
- 如果需要参考驱动，只用来锁定“Bloomberg / consulting dark deck”的视觉纪律，不引入第三模式

## Image Intent

- Slide 1: 不使用外部图片，改用高对比数字与抽象网格表达“基础设施”气质
- Slide 5: 使用页面级关系图承担“核心对象组织方式”的沟通任务
- Slide 7: 使用事件流图承担“先写事件再投递”的可靠性证明任务
- Slide 8: 使用组件架构图承担“六个核心部件如何围绕 event store 工作”的说明任务

---

## Visual & Layout Guidelines

- **Overall tone**: 深色、理性、偏评审会材料
- **Background**: `#0B1020` 到 `#101827` 的低调渐变 + 微弱网格
- **Primary text**: `#E8EEF6`
- **Accent (primary)**: `#B45309` amber 用于重点结论，`#3B82F6` blue 用于结构
- **Typography**: PingFang SC / system-ui
- **Per-slide rule**: 一页一种版式任务，图示页不再塞长 bullets
- **Animations**: 低幅 reveal，仅辅助视线顺序

---

## Slide-by-Slide Outline

**Slide 1 | Hook**
- Title: Intent Broker
- Subtitle: 把多 agent 协作从聊天提升为协议
- Visual: 大标题 + 三个核心价值指标

**Slide 2 | Problem**
- Key point: 现在的多窗口协作没有可靠任务语义
- Supporting:
  - 协作通道不统一
  - 状态推进不可审计
  - 断线后上下文容易断裂
- Visual element: 三段式问题卡
- Speaker note: 把痛点讲成“基础设施缺口”

**Slide 3 | Thesis & Boundary**
- Key point: Broker 只负责协作协议、事件日志、投递和聚合视图
- Supporting:
  - 不做推理
  - 不做工具执行
  - 不建模各家内部会话协议
- Visual element: Do / Not Do 双栏
- Speaker note: 清晰划边界，降低 scope 焦虑

**Slide 4 | Principles**
- Key point: v1 的设计由本地优先、协议优先、可靠优先三类原则驱动
- Supporting:
  - event-first
  - idempotency-first
  - simplify client integration
- Visual element: 原则矩阵
- Speaker note: 这页是后续所有技术选择的解释器

**Slide 5 | Concept Map**
- Key point: Participant / Intent / Task / Thread / Approval 组成协作骨架
- Supporting:
  - 少量稳定结构 + 自然语言 body
  - thread 保持上下文不碎裂
  - approval 独立于 task 但影响推进
- Visual element: 核心概念关系图
- Speaker note: 让听众脑中形成系统模型

**Slide 6 | Lifecycle**
- Key point: 状态来自 intent 事件聚合，而不是客户端直接写状态
- Supporting:
  - task 状态链
  - approval 状态链
  - follow-up task 代替 completed 回退
- Visual element: task / approval 双状态机
- Speaker note: 解释为什么状态机被刻意收敛

**Slide 7 | Reliability**
- Key point: “先落事件，再投递 inbox” 是 v1 的基础承诺
- Supporting:
  - SQLite event log
  - inbox entries + cursor
  - at-least-once + 幂等去重
- Visual element: 事件流时序图
- Speaker note: 这页承担技术可信度

**Slide 8 | Architecture**
- Key point: 六个组件围绕 event store 分工，形成单进程本地 broker
- Supporting:
  - server
  - router
  - projection-engine
  - policy-layer
  - adapters
- Visual element: 分层架构图
- Speaker note: 说明为什么这条技术路线足够小而完整

**Slide 9 | API & Test Readiness**
- Key point: v1 的接口和测试面已经足够支撑闭环验证
- Supporting:
  - register / intents / inbox / tasks / approvals / replay
  - 协议、路由、可靠性、集成四层测试
- Visual element: API surface + test matrix
- Speaker note: 让项目显得可以马上实施

**Slide 10 | Closing**
- Summary statement: Intent Broker 是本地协作基础设施，不是聊天系统
- Call to action or contact info: 先实现 v1 闭环，再向远程化和 UI 演进

---

## Resources Used

- `D:\projects\mydocs\intent-broker\docs\superpowers\specs\2026-03-31-intent-broker-design.md` → 全部页面的事实来源

---

## Images

- No external bitmap assets; diagrams are inline SVG

---

## Deliverables

- Output: `intent-broker-polish.html` (single-file, zero dependencies)
- Optional: `intent-broker-polish-script.md` (speaker notes)
- Inline editing: Yes
