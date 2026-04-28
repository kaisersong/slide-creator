# 2026-04-27 Low-Context V2 约束升级方案对抗性评审

评审对象：

- [2026-04-27 Low-Context V2 约束升级方案](/Users/song/projects/slide-creator/plans/2026-04-27-low-context-v2-constraint-upgrade-plan.md)

评审目标：

- 不站在方案作者的角度，而站在最苛刻反对者的角度，判断这份方案哪里可能高估了约束升级的收益，哪里可能把 renderer 问题错误地归因成 schema 问题，哪里可能引入新的系统复杂度。

---

## 先给结论

这份方案**方向基本正确**，但有五个必须正视的风险：

1. 它可能高估“把语义写进 BRIEF”就能直接解决质量问题。
2. 它容易把 renderer 的创造性判断问题，过多转移成 schema 责任。
3. 它可能让 `--plan` 产物变得太重，牺牲当前 IR-first 的效率优势。
4. 它可能让 preset reference 从“风格参考”膨胀成“半个规则引擎”。
5. 如果只升级约束，不同步升级质量门禁，最终只会得到更复杂的输入表单，不会得到更好的 deck。

所以我的 red-team 结论不是 “No-Go”，而是：

- **可以推进**
- **但必须按最小闭环推进**
- **先验证 4 个 production preset 的收益，再决定是否普遍推广**

---

## 反对意见 1：你可能把问题过度归因给输入约束

最强反对点：

- 有些问题并不是输入不够清晰，而是 renderer 的审美判断不够强。
- 即使把 `visual` 拆成 `visual_intent / preferred_layout_family / chart_policy`，也不自动意味着 render 质量就会明显提升。

这条反对成立的部分：

- low-context 的问题确实不只出在 schema。
- 比如 `Swiss Modern` 的“留白什么时候成立”、`Enterprise Dark` 的“什么时候该像咨询页而不是数据页”，这类问题本质上仍然需要 renderer 有强设计判断。

如果误判，会出现什么：

- 团队花很多时间扩 BRIEF
- 但 renderer 仍然做出平庸的 layout choices
- 最后只是“输入更复杂，输出没显著变好”

修正要求：

- 方案落地时必须把收益拆开验证：
  - schema 升级带来的收益
  - renderer 逻辑升级带来的收益
- 不允许把所有提升都归功于 IR 变复杂

评审结论：

- **约束升级必要**
- **但不能假设约束升级足够**

---

## 反对意见 2：你会把 deterministic render 变成“填表驱动设计”

最强反对点：

- slide-creator 的优势之一，是用户不需要手工指定太多设计元信息。
- 如果每页都要多填 `claim / explanation / visual_intent / preferred_layout_family / chart_policy`，那就有把工具做成“设计问卷系统”的风险。

这条反对成立。

当前系统的产品优势在于：

- `--plan` 先把 prompt 提炼成 BRIEF
- 用户不需要自己成为排版工程师

如果 V2 把 BRIEF 变得太细，有两个后果：

1. `--plan` 变慢
2. schema 更难维护，也更容易让 planning 过程本身 hallucinate 新字段

修正要求：

- 新字段不应全部对用户显式暴露
- 应优先作为 `--plan` 内部生成的 richer IR
- 用户只在必要时看到更细语义，而不是默认每次都要指定

评审结论：

- **可以升级 IR**
- **但不要把用户入口变成多字段问卷**

---

## 反对意见 3：你可能让 style reference 过度膨胀

最强反对点：

- 现在的 style reference 之所以易维护，是因为它更接近“视觉合同”
- 如果再往里塞 `role_layout_forbidden / numeric_gate_rules / fallback_route_rules / density_preferences`
- reference 文件会开始同时承担：
  - 视觉参考
  - 结构约束
  - 渲染策略
  - 验证规则

这很容易失控。

这条反对成立的部分：

- 如果所有规则都直接写在 markdown reference 里，维护体验会很差。
- 还会导致文档化语言和机器可执行规则混在一起，最后两边都不可靠。

修正要求：

- 风格 reference 保留“人类可读的设计原则”
- 机器可执行的 usage rules 另存为结构化 metadata
- 不要让 `compile_style_contract()` 再从 prose 中硬解析太多行为规则

更具体一点：

- `references/*.md` 保留视觉和 canonical export 文档
- 新增 `references/preset-usage-rules.json` 或等价结构化文件
- renderer 只消费结构化规则

评审结论：

- **方案可推进**
- **但执行层必须避免把 markdown 文档变成规则 DSL**

---

## 反对意见 4：fail-closed 很容易让“可用率”短期下降

最强反对点：

- 当前系统虽然会生成一些 generic 页，但总体出稿率高。
- 一旦增加大量 fail-closed gate，可能让更多 deck 卡在“不能生成”。

这条反对完全成立。

必须明确：

- fail-closed 的价值是防止伪成功
- 但产品上仍需要 graceful degradation

也就是说，不能把策略写成：

- “不够数值化 -> 直接失败”

而应该写成：

- “不够数值化 -> 禁止 chart -> 降级到 stage/evidence route”
- “只有在安全降级也不可行时才 fail”

修正要求：

1. 先定义 `safe fallback`
2. 再定义 `hard fail`
3. release gate 只在“本应可降级却没降级”时视为质量问题

评审结论：

- **fail-closed 要保留**
- **但必须先定义 fail-open 到哪里、fail-closed 从哪里开始**

---

## 反对意见 5：你可能低估了 eval 体系的改造量

最强反对点：

- 方案写得像是在升级 schema 和 renderer
- 但真实要证明收益，必须同步改 eval
- 否则升级以后，团队还是只能靠肉眼说“看起来更好了”

这条反对成立。

必须同步增加的评估能力包括：

- chart-without-local-numeric-signal
- repeated-global-fact-overuse
- visual-placeholder-surface-leak
- mirrored-detail-pairing-risk
- role-layout-distinctiveness

如果没有这些指标，会发生什么：

- 新 contract 已经写了
- renderer 也改了
- 但未来回归时没人能定量发现“又开始 generic 了”

评审结论：

- **V2 不只是 schema 升级**
- **它必须同时是 eval 升级**

---

## 反对意见 6：你可能在 production preset 上过拟合

最强反对点：

- 这次的结论主要来自 `Swiss Modern / Enterprise Dark / Data Story / Blue Sky`
- 如果直接把同一套规则推广到所有 preset family，可能会过拟合 production preset 的表达习惯

这条反对成立。

比如：

- editorial family 天然允许更高的重复版式
- cultural/minimal family 天然允许更少组件种类
- dev family 的 token 结构和 numeric signal 也不同

所以不能把：

- production preset 的 eval 门槛

直接当成：

- 全部 preset family 的统一门槛

修正要求：

- V2 先只覆盖 production preset
- 其他 family 采用 family-specific contract 和 gate
- 不要求“所有 preset 一套标准”

评审结论：

- **生产级先行是对的**
- **不要把 production 经验直接当 universal rule**

---

## 修正后的可接受落地版本

经过 red-team 后，方案应该收敛成下面这个更稳的执行版本。

### 1. 只扩 internal IR，不扩用户手填负担

- 新字段进入 BRIEF/IR
- 默认由 `--plan` 生成
- 不要求用户显式逐页填写

### 2. usage rules 结构化，不埋进 prose 文档

- `references/*.md` 继续做人类可读参考
- 可执行规则进入独立 metadata 文件

### 3. 先定义 safe fallback，再定义 hard fail

- 优先减少“伪成功”
- 但不能粗暴降低“可生成率”

### 4. renderer、schema、eval 同步升级

如果只改其中一层，方案收益会非常有限。

### 5. 先只在 production preset 落地

- `Swiss Modern`
- `Enterprise Dark`
- `Data Story`
- `Blue Sky` 单独例外处理

验证通过后，再决定是否推广到其他风格家族。

---

## Go / No-Go 标准

### Go

满足以下条件时，可以推进：

1. 新约束首先作为 internal IR 使用，而不是要求用户手填更多字段
2. usage rules 结构化存储，不继续让 markdown reference 承担规则引擎职责
3. safe fallback 和 hard fail 的边界先定义清楚
4. eval 和 release gate 同步补齐
5. rollout 范围先限定在 production preset

### No-Go

出现以下任一情况时，不建议推进：

1. 只扩 schema，不改 renderer 和 eval
2. 只改 renderer，不补结构化 usage rules
3. 让 `--plan` 变成沉重的多字段问卷
4. 把 production preset 的门槛直接推广到全部 preset
5. 把 fail-closed 做成“稍微不确定就拒绝生成”

---

## 最终评审结论

这份方案**可以推进，但必须按保守版本推进**：

- 不是“把所有问题都甩给 schema”
- 不是“把 reference 文档变成 DSL”
- 不是“宁可拒绝生成也不要 generic”

而是：

- **先把 richer IR 建起来**
- **再把 usage rules 结构化**
- **再让 renderer 少猜一点**
- **最后用 eval 验证它是否真的比现在更稳、更准**

如果按这个顺序做，low-context v2 有很大价值。  
如果跳过中间层，直接做“大 schema + 大 fail-closed + 大文档规则”，那很可能只会得到一个更重、更慢、但不一定更好的系统。 
