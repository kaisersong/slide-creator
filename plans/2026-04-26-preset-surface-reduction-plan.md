# 2026-04-26 风格支持面收敛方案

## 目标

这份方案要回答的不是“21 个 preset 要不要继续存在”，而是：

1. 在高 context、晚阶段生成的真实使用场景下，继续维持 21 个风格的平权承诺，是否会伤害稳定性和首稿质量。
2. 如果要收敛，应该收敛到哪一层。
3. 收敛动作应该优先改哪里，才能在不粗暴砍掉资产库的前提下，先提升生成成功率和结果可信度。

结论先写在前面：

- **不建议先物理删除 preset 文件。**
- **建议先收敛“默认活跃支持面”和“对外承诺面”。**
- **第一阶段先把核心 4 个 preset 做深做稳，再根据使用量决定下一轮扩面。**
- **建议把 21 个风格改成分层支持模型，而不是继续按“21 个都同等稳定”来运营。**

---

## 现状判断

### 1. 真正的上下文压力不来自“把 21 个 preset 全读进去”

当前 skill 的公开契约已经写明，`--generate` 应该只读取：

- `references/html-template.md`
- `references/js-engine.md`
- `references/base-css.md`
- **单个已选风格文件**

证据：

- `SKILL.md` 明确写的是 `one style file`，不是全量 style bundle
- `README.md` 也明确把这一点作为“progressive disclosure for model context”的核心设计
- `scripts/low_context.py` 在构建 render packet 时，只把选中 preset 对应的 `style_contract["source_path"]` 放进 `required_refs`

因此，如果只从“render 阶段 prompt token 数量”看，`21 -> 15` 的收益有限；问题不是每次都喂 21 套，而是系统仍然要对外维护 21 套同等合法的选择。

### 2. 真正变重的是工程支持面

虽然渲染时只读单个风格，但工程层面对 21 个 preset 的承诺已经进入这些位置：

- `scripts/low_context.py` 的 `PRESET_REFERENCE_MAP`
- `tests/test_style_reference_completeness.py` 对 21 个 preset 的完整性要求
- `tests/test_title_profile_registry.py` 要求 title profile registry 覆盖全部 supported presets
- `tests/test_priority_preset_reference_contracts.py` 对一批高优先级 preset 的额外契约要求

这意味着 preset 数量增加的成本，主要不是“单次 prompt 更长”，而是：

- 参考文件更多
- title profile 维护面更广
- validate 特判更多
- layout / contract / shell 兼容面更宽
- demo、README、style picker、推荐逻辑一起膨胀

### 3. 对外承诺面已经大于稳定实现面

这是当前最关键的不对称。

repo 对外持续强调有 21 个 preset，但 deterministic low-context 主链当前真正实现的 user-content renderer 只有：

- `Swiss Modern`
- `Enterprise Dark`
- `Data Story`

另外 `Blue Sky` 是单独架构的 starter / product-demo 特例，不应与其他非 Blue Sky preset 视为同一运行时形态。

也就是说，现在的真实状态更接近：

- 对外：21 个平权 preset
- 对内：3 个 user-content 主力 preset + 1 个 Blue Sky 特例 + 若干 contract / reference 资产

这才是稳定性与质量波动的核心来源。

---

## 问题定义

本轮要解决的不是“风格够不够多”，而是以下三个失配：

### A. 选择面过宽，默认推荐成本过高

当用户没有强 style preference 时，系统需要在 21 个方向里做推荐。  
这会导致：

- 初选质量不稳定
- 用户经常重新换风格
- 更多上下文被浪费在“审美重抽”上，而不是内容结构

### B. 稳定支持面与营销口径不一致

当前实现上真正稳定的 user-content 主链远小于对外宣称的 preset 总数。  
这会导致：

- 用户把所有 preset 都理解为“质量和稳定性相同”
- bug 报告分散到大量边缘 preset
- 团队容易在很多方向上做浅维护，而不是在少数核心风格上做深维护

### C. 每新增或保留一个 preset，都会向下游扩散复杂度

一个 preset 并不只是一个 markdown 参考文件。它通常还会影响：

- title profile registry
- style contract parser
- strict validate 规则
- 优先级 preset 契约测试
- demo 与截图资产
- README 中的选择器、定位、推荐语

所以 preset 数量过多的问题，本质上是**支持矩阵过宽**，不是单纯的资产数量过多。

---

## 非目标

本方案不做以下事情：

1. 本轮不直接删除全部低频风格文件
2. 本轮不试图把 21 个 preset 全部补到 production-grade
3. 本轮不重写 style reference 系统
4. 本轮不把所有 legacy / experimental 风格全部迁移到 deterministic renderer

---

## 备选策略

### 方案 A：继续维持 21 个平权 preset

做法：

- README、picker、prompt 继续把 21 个 preset 视为同级选择
- 所有风格默认都可被推荐
- 缺哪修哪

优点：

- 用户感知的“可选空间”最大
- 市场展示面最丰富
- 不需要重新定义产品口径

缺点：

- 与当前稳定实现面不匹配
- 默认推荐与 QA 成本持续升高
- 会把工程精力分散到大量边缘 preset
- 不利于提升高 context 场景下的首稿命中率

判断：

- **不建议继续沿用。**

### 方案 B：直接把 21 个 preset 砍到 6-8 个

做法：

- 物理删除一批 preset
- README 和 picker 同步只保留少数核心风格

优点：

- 对外口径最干净
- 决策空间直接收窄
- 长期维护成本最低

缺点：

- 现在就删，过于激进
- 容易误删未来仍有价值的 style asset
- 用户会把它理解为能力退化，而不是质量聚焦
- 如果没有 usage data 支撑，删减名单很容易主观

判断：

- **不建议作为第一步。**

### 方案 C：分层支持模型

做法：

- 保留 21 个 preset 资产
- 但将 preset 分为 `production / supported / experimental / archive-candidate`
- 默认推荐、低 context 主链、严格回归优先保障 `production`
- `supported` 保留可选，但默认不与 production 同权推荐
- `experimental` 仍可直选，但不作为默认推荐面

优点：

- 不需要粗暴删资产
- 能先降低默认决策面
- 更诚实地反映当前实现成熟度
- 后续可逐步升级或下调某个 preset，而不是只能“保留/删除”二选一

缺点：

- 需要补一层元数据与产品口径
- 文档、picker、推荐逻辑都要改
- 如果执行不彻底，容易形成新的“双轨复杂度”

判断：

- **推荐方案。**

---

## 推荐方案

### 一句话策略

**保留 21 个 preset 资产，但第一阶段只把真正 production-grade 的 user-content 主链收敛到 3+1；第二阶段再根据使用量决定是否把默认活跃支持面扩到 6-8 个。**

这里的 `3+1` 指：

- `Swiss Modern`
- `Enterprise Dark`
- `Data Story`
- `Blue Sky`（仅作为 starter / product-demo 特例，不与普通 user-content 同层）

### 推荐分层

#### Tier 0: Production

这些 preset 进入默认推荐主面，必须持续享受最高优先级回归保障。

- `Swiss Modern`
- `Enterprise Dark`
- `Data Story`
- `Blue Sky`（特殊标注：仅 starter / product-demo 主力）

标准：

- 已有 deterministic renderer 或等价稳定路径
- 已进入严格 contract/validate 主链
- 能支撑高频真实业务内容

#### Tier 1: Supported

这些 preset 保留在产品中，仍可直接选，但不与 Tier 0 同权推荐。  
其中是否进入下一轮“默认活跃 shortlist”，以使用量和真实命中率为准。

- `Paper & Ink`
- `Glassmorphism`
- `Chinese Chan`
- `Bold Signal`
- `Aurora Mesh`
- `Terminal Green`

标准：

- 风格辨识度高
- 代表某一类明显不同的用户偏好
- 有继续投入价值
- 但当前没有足够证据表明其应进入 production 主面

#### Tier 2: Experimental

这些 preset 暂时保留资产和入口，但从默认推荐和主宣传面退出。

- `Electric Studio`
- `Creative Voltage`
- `Dark Botanical`
- `Modern Newspaper`
- `Neon Cyber`
- `Notebook Tabs`
- `Pastel Geometry`
- `Split Pastel`
- `Vintage Editorial`
- `Neo-Brutalism`
- `Neo-Retro Dev Deck`

标准：

- 与其他风格有一定重叠
- 使用场景更窄
- 当前维护收益低于维护成本

#### Tier 3: Archive Candidate

本轮先不指定具体成员。  
只有在连续多个版本周期内没有被升级进 supported / production，也没有明确保留价值时，再考虑进入 archive candidate。

---

## 为什么不是直接删

因为当前最需要解决的不是磁盘上的文件数量，而是以下三个产品问题：

1. 用户在默认流程里看到太多同权选项
2. 团队对外承诺过宽，但对内主力支持面过窄
3. 缺少明确的 support tier，导致所有 bug 都像“核心事故”

分层方案先解决这三个问题，再决定哪些 preset 真的值得物理归档，会更稳。

---

## 当前执行决策

基于当前讨论，先把方案进一步收窄为下面这个执行顺序：

1. **核心 4 个先做深**
   - `Swiss Modern`
   - `Enterprise Dark`
   - `Data Story`
   - `Blue Sky`
2. `Tier 1 / Tier 2` 本轮只做分层定义，不立刻要求它们进入同等级的深维护。
3. editorial 代表优先保留 `Paper & Ink`，而不是 `Notebook Tabs`。
   原因不是抽象审美偏好，而是**已有使用量信号显示 `Paper & Ink` 更值得保留为下一轮候选**。
4. 下一轮是否把默认活跃面扩到 6-8 个，不凭主观拍板，而看真实使用量、推荐命中率和维护收益。

---

## 实施顺序

### Phase 1：先固化核心 4 个，不删资产

目标：

- 把“21 个平权 preset”改成“核心稳定 preset + 扩展风格库”
- 先把核心 4 个 preset 的深维护优先级钉住

动作：

1. 引入 preset metadata tier 文件
2. 更新 README / README.zh-CN 的对外表述
3. 更新 style picker 文案与分组
4. 默认推荐第一阶段只从 Tier 0 里出
5. 明确 `Blue Sky` 的特殊定位：starter / product-demo，不再隐含为通用 user-content 主链
6. 将 `Paper & Ink` 标记为 editorial 类下一轮优先候选，`Notebook Tabs` 降为扩展位

完成标准：

- 对外文档不再暗示 21 个 preset 全部同级稳定
- 第一阶段默认推荐明确聚焦核心 4 个
- `Paper & Ink` 的层级调整反映到方案与推荐口径中

### Phase 2：让路由与验证承认 tier

目标：

- 让“分层”从文案变成真实系统行为

动作：

1. `Auto` 模式默认只推荐 Tier 0
2. `Polish` 模式允许引导到 Tier 1
3. 低 context deterministic path 对非 Tier 0 失败时更早 fail closed
4. 优先级回归矩阵明确只对 Tier 0 做 release gate
5. Tier 1 / Tier 2 走较轻的 contract 与 smoke check

完成标准：

- release gate 不再被大量边缘 preset 稀释
- bug 修复优先级与 preset 层级对齐

### Phase 3：按使用量决定是否扩面或归档

目标：

- 只在确有必要时才物理移除 preset
- 判断下一轮是否要把默认活跃面从 4 扩到 6-8

动作：

1. 记录一段时间内的问题集中度、推荐命中情况、使用量和维护成本
2. 先判断哪些 Tier 1 preset 值得进入下一轮默认活跃面
3. 对高重叠、低价值 preset 给出 archive candidate 名单
4. 真正删除前先退到隐藏组或内部组

完成标准：

- 默认活跃面的扩张或删减都建立在使用证据和维护证据上，而不是主观审美

---

## 预期收益

### 对稳定性

- release gate 聚焦在少数主力 preset
- shared runtime 和主力 renderer 的回归更容易守住
- 边缘风格不再频繁把主线质量拉散

### 对输出质量

- 默认推荐更集中，首稿命中率更高
- 用户更少陷入“先换风格再重抽”的循环
- 团队可以把内容节奏、标题质量、layout diversity 的深修集中在主力 preset 上

### 对高 context 场景

- render 阶段 token 收益有限，但**决策复杂度**显著下降
- 更少的默认选择意味着更少的 late-stage 风格摇摆
- `BRIEF.json` 中的 style 选择更容易稳定下来

---

## 风险

### 风险 1：用户会觉得能力缩水

缓解：

- 不删除资产
- 文案上强调“核心稳定 preset + 扩展风格库”
- 保留直接点名 preset 的能力

### 风险 2：支持 tier 本身变成新的复杂度

缓解：

- Tier 不要超过 4 层
- 第一轮只真正启用 `production / supported / experimental`
- `archive-candidate` 仅作为内部标签，不先暴露给用户

### 风险 3：生产级集合过度偏企业审美

缓解：

- Tier 1 里必须保留 editorial / creative / dev-focused 代表风格
- 默认主面不等于唯一可用面

### 风险 4：没有 usage data，分类会带主观性

缓解：

- 本轮先做“分层与口径”而不做最终删除
- 分类名单允许在 1-2 个版本周期后调整

---

## 成功标准

如果推进这件事，至少要满足以下结果，才算方案真的有效：

1. 第一阶段默认推荐面先聚焦核心 4 个；后续若扩面，仍覆盖企业、数据、创意、开发者四类主场景
2. 文档、picker、validate、renderer 的口径一致
3. `production` preset 的回归门禁更清晰，而不是“21 套都沾一点”
4. 团队能明确回答：哪个 bug 是核心面事故，哪个 bug 属于扩展风格债务

---

## 最终建议

下一步不做“删 preset 文件”，而做下面三件事：

1. 定义 preset support tier 元数据
2. 把 production-grade 主链明确收敛到 `Swiss Modern / Enterprise Dark / Data Story / Blue Sky`
3. 把 `Paper & Ink` 提升为 editorial 方向的下一轮优先候选
4. 等使用量证据稳定后，再决定默认活跃面是否扩到 6-8 个

这一步完成后，再决定是否需要做第二轮物理归档。
