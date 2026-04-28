# 2026-04-27 Low-Context V2 约束升级方案

## 目标

这份方案回答三个问题：

1. 为什么 production preset 会反复出现“结构合法，但风格应用浅、内容节奏弱、组件语义不准”的问题。
2. low-context 这条路线本身是否正确。
3. 如果继续保留 low-context 作为主力生成链路，下一步该补哪些约束，才能把问题从“靠启发式补洞”转成“靠 contract 防错”。

结论先写在前面：

- **low-context 路线本身是对的。**
- **当前 low-context 的实现只做到“结构正确优先”，还没有做到“语义正确优先”。**
- **问题不在于 deterministic renderer 不该存在，而在于 BRIEF schema、style contract、renderer 决策门槛三者之间还缺一层更强的语义约束。**

---

## 背景

当前 user-content 主链是：

`user prompt -> BRIEF.json -> low-context deterministic render -> strict validate -> eval`

核心入口与约束位置：

- [SKILL.md](/Users/song/projects/slide-creator/SKILL.md:10)
- [references/workflow.md](/Users/song/projects/slide-creator/references/workflow.md:140)
- [schemas/generation-brief.schema.json](/Users/song/projects/slide-creator/schemas/generation-brief.schema.json:1)
- [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py:1024)

当前 deterministic low-context 主力 preset：

- `Swiss Modern`
- `Enterprise Dark`
- `Data Story`

`Blue Sky` 是单独 runtime 的 starter/helper 特例，不属于同一 shared low-context 路径。

---

## 问题定义

从最近几轮 production preset 修复看，出现的问题不是随机 bug，而是同一类结构性失配反复出现：

1. **风格应用浅**
   页面能过 contract 和 strict validate，但读起来更像“套了 preset token 的通用 scaffold”，不是该 preset 的原生节奏。

2. **内容节奏被打平**
   不同 page role 最后落到相同布局族，或者虽然 layout id 不同，但视觉推进感接近，导致 deck 看起来像“同一页改了几次标题”。

3. **全局事实压过页内事实**
   `must_include` 里的高频词会被多页复用，导致多个页面围绕同一个 token 旋转，局部内容辨识度下降。

4. **视觉意图字段和可见文本字段混淆**
   `visual` 有时是作者自己的内部提示语，有时又被 renderer 当成可见内容来源，容易产生 placeholder 感。

5. **图表生成决策不够保守**
   只要发现数字，渲染器就倾向于画 chart；但“有数字”不等于“这一页真的应该以数字图表为主”。

---

## 为什么会出现这些问题

### 1. BRIEF 现在是结构清楚、语义不够细

当前 schema 对 slide 的关键字段只有：

- `slide_number`
- `role`
- `title`
- `key_point`
- `visual`

见 [generation-brief.schema.json](/Users/song/projects/slide-creator/schemas/generation-brief.schema.json:161)。

这套字段足够支持“生成一页合法幻灯片”，但不够支持“稳定生成一页高质量、低歧义、强 preset 语气的幻灯片”。

原因是：

- `title` 是断言
- `key_point` 是解释
- `visual` 却同时承担了“视觉意图”“布局暗示”“作者内部注释”三种可能职责

这三个维度没有被拆开，所以 renderer 只能猜。

### 2. quality tier 判断的是“资料完整度”，不是“语义可渲染度”

`assess_quality_tier()` 当前主要依赖：

- `must_include` / `must_avoid` 数量
- `page_roles` / `slides` 数量完整性
- `thesis` 长度
- `key_point` / `visual` 长度
- `mode == polish`

见 [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py:966)。

这意味着：

- 一个 BRIEF 可以拿到 `tier0`
- 但 slide-level 语义仍然很稀
- 最终还是要靠 renderer 启发式把中间层补出来

所以 `tier0` 现在更像“表单完整”，不是“语义充分”。

### 3. style contract 现在更像“样式语法”而不是“使用规则”

`compile_style_contract()` 提取的主要是：

- tokens
- font URLs / font families
- required signature classes
- required background layers
- allowed layout ids
- export rules

见 [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py:867)。

这能约束：

- 用什么 token
- 用哪些 class
- 允许哪些 layout
- 不能出现哪些 alias

但约束不了：

- 哪类 slide 在什么条件下该走哪个 layout
- 什么时候不能使用 KPI / chart / matrix
- 没有足够证据时该降级到什么结构

所以 style contract 能保证“像这个 preset”，但很难保证“像这个 preset 在这页内容下该有的样子”。

### 4. renderer 当前承担了过多“语义恢复”责任

`build_slide_spec()` 这一层在做的不是简单映射，而是一次再推理：

- route role -> layout
- select evidence
- build supporting items
- assemble visible tokens

见 [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py:1292)。

其中几段最关键的启发式是：

- `_select_relevant_evidence_items()`：[scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py:1127)
- `_build_supporting_items()`：[scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py:1167)
- `_spec_detail_pairs()`：[scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py:2078)
- `_chart_metric_values_from_spec()`：[scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py:1969)

这些逻辑本质上都不是 contract，而是 heuristic。  
heuristic 不是不能用，但只要输入语义不够强，它就一定会开始“像在猜”。

### 5. composition guide 规定了“布局分类”，没有规定“进入条件”

[references/composition-guide.md](/Users/song/projects/slide-creator/references/composition-guide.md:7) 对叙事弧线和布局多样性讲得很清楚：

- 每页的叙事角色是什么
- 布局分类应该是什么
- 连续两页不该相同

但它没有规定：

- 什么叫“这页足够数值化，允许走 chart”
- 什么叫“这页证据不足，只能走 stage grid / evidence list”
- `problem`、`risk`、`driver` 这类 role 在不同 preset 下的禁用布局

所以 renderer 只能把“布局分类”粗略地投射到 preset layouts 上，而不是按更细的进入门槛做决策。

---

## 对当前 low-context 的判断

### 正确的部分

low-context 的核心方向是对的，原因有四个：

1. **把 BRIEF 作为唯一真相源是对的**
   防止 prompt 漂移和 late-context 污染。

2. **把 render 压成 deterministic contract 是对的**
   能稳定约束 runtime、shell、preset metadata、title quality、strict validate。

3. **把风格文件编译成 style contract 是对的**
   至少保证 preset token 和 signature elements 不会完全跑偏。

4. **把 validate/eval 放在生成后门禁是对的**
   这样 bug 不会只停留在“感觉不对”，而能被固化成测试和质量指标。

### 不足的部分

当前 low-context 的问题不是“设计方向错”，而是它停在了一个中间态：

- 结构正确强于语义正确
- contract 强于 composition decision
- shell/runtime 约束强于 slide-local reasoning

所以我的判断是：

- **low-context 的架构正确**
- **当前 low-context 的决策层不够强**
- **需要升级约束，不是推翻路线**

---

## 当前“进入约束”是否清晰

### 结构层：清晰

这部分已经很明确：

- 风格强制：[SKILL.md](/Users/song/projects/slide-creator/SKILL.md:61)
- 叙事弧线优先：[SKILL.md](/Users/song/projects/slide-creator/SKILL.md:66)
- runtime 基线：[SKILL.md](/Users/song/projects/slide-creator/SKILL.md:72)
- strict validate 门禁：[SKILL.md](/Users/song/projects/slide-creator/SKILL.md:83)

所以系统已经清楚规定了：

- 必须走哪个 preset
- 必须带什么 shell
- 标题和布局不能怎么坏

### 语义层：不清晰

真正不清晰的是“什么输入足够支持什么输出”。

#### A. `visual` 的进入语义不清晰

当前 schema 只要求 `visual` 是非空字符串，见 [generation-brief.schema.json](/Users/song/projects/slide-creator/schemas/generation-brief.schema.json:191)。

它没有区分：

- `visual_intent`
- `layout_preference`
- `forbidden_treatment`
- `internal_author_note`

这会直接导致 renderer 误把作者的“构图短语”当成可见语义素材。

#### B. `must_include` 的进入层级不清晰

当前 `must_include` 只是一个平铺数组，见 [generation-brief.schema.json](/Users/song/projects/slide-creator/schemas/generation-brief.schema.json:122)。

它没有区分：

- deck-global facts
- slide-scoped facts
- numeric facts
- optional support

所以 renderer 不知道哪些信息应该全局复用，哪些只能局部调用。

#### C. preset reference 缺少 negative rules

以 `Data Story` 为例，风格文件明确讲了：

- numbers 是 hero
- 可以用 KPI row + chart
- 可以用 full-screen bar chart + insight

见 [references/data-story.md](/Users/song/projects/slide-creator/references/data-story.md:138)。

但没有明确写：

- 没有 slide-local 数字时禁止走 chart
- 借来的 evidence numbers 不能升级为 chart
- `risk` 这类 role 在没有真实 time/metric arc 时优先落为 evidence/stage 结构

同样的问题也存在于 `Enterprise Dark` 和 `Swiss Modern`：

- `Enterprise Dark` 的 layout 很清楚，但没有足够强的“何时禁用 KPI card 的伪数值表达”规则，见 [references/enterprise-dark.md](/Users/song/projects/slide-creator/references/enterprise-dark.md:209)
- `Swiss Modern` 的视觉 token 和 canonical class 很清楚，但没有明确“何时必须保留留白、何时不能把标题词切成 fake stat”的进入条件，见 [references/swiss-modern.md](/Users/song/projects/slide-creator/references/swiss-modern.md:91)

---

## V2 升级目标

Low-context v2 不该追求“更复杂的 heuristic”，而该追求“更少的猜测”。

目标是三件事：

1. **把语义约束前移到 BRIEF**
2. **把 preset 使用条件写进 style contract**
3. **把 renderer 从猜内容改成执行规则**

---

## 推荐升级项

### 升级 1：把 slide 语义从 3 个字段扩成 6 个字段

当前：

- `title`
- `key_point`
- `visual`

建议新增或拆分为：

- `title`
- `claim`
- `explanation`
- `visual_intent`
- `preferred_layout_family`
- `chart_policy`

建议定义：

- `claim`：这一页的断言
- `explanation`：这一页的展开说明
- `visual_intent`：只描述可视化方向，不允许作为直接可见文案
- `preferred_layout_family`：例如 `stat / split / matrix / flow / evidence / chart / close`
- `chart_policy`：`required / allowed / avoid`

这样可以直接消灭一大类 `visual` 被误当可见文本的问题。

### 升级 2：把 `must_include` 拆层

建议从：

- `must_include: string[]`

升级为：

- `global_facts`
- `slide_facts`
- `numeric_facts`
- `optional_support`

其中：

- `global_facts` 允许跨页复用
- `slide_facts` 只允许指定 slide 使用
- `numeric_facts` 只用于数值验证和 chart gating
- `optional_support` 只在信息不足时作为补充，不直接提升优先级

这样 renderer 就不会再把几个 deck-level 高频事实循环塞进多页。

### 升级 3：style contract 增加 usage rules

`compile_style_contract()` 现在抽取的是样式资产。  
V2 应该让 style reference 多一层“使用规则元数据”。

建议每个 production preset 至少新增：

- `role_layout_preferences`
- `role_layout_forbidden`
- `numeric_gate_rules`
- `fallback_route_rules`
- `density_preferences`

例子：

- `Data Story`
  - `risk`: forbid `comparison_matrix` when no contrast axis is explicit
  - chart layouts require `chart_policy != avoid` and slide-local numeric facts
- `Enterprise Dark`
  - `kpi_dashboard`: forbid fake KPI fallback when no numeric claim exists
  - `consulting_split`: prefer for strategic argument pages with 2-3 evidence rows
- `Swiss Modern`
  - `stat_block`: only allowed when title/claim contains a compact anchor suitable for one focal stat
  - `contents_index`: prefer for principles/checklists, not as generic dump fallback

### 升级 4：quality tier 改成“可渲染度评分”

当前 `assess_quality_tier()` 过于形式化。  
建议加入真正影响质量的信号：

- slide-local numeric fact density
- role-layout specificity
- slide fact coverage
- visual_intent specificity
- repeated-global-fact risk
- title distinctiveness

这样 `tier0` 的意义才会从“字段都填了”变成“这份 BRIEF 足够支撑高质量 deterministic render”。

### 升级 5：render 前增加 fail-closed gate

一些情况不该继续猜，而该直接降级或拒绝：

1. role 需要 chart，但没有 slide-local numeric facts
2. role 需要 comparison，但没有明确对照轴
3. slide 只有 deck-global facts，没有 slide-local claim material
4. preset usage rule 与当前 layout 冲突

处理方式：

- 不满足进入条件时，不是继续硬走首选 layout
- 而是显式改走 fallback route
- 如果 fallback 也不安全，就 fail closed

### 升级 6：validate 和 eval 增加“语义错配”门禁

strict validate 现在主要查结构和壳子。  
V2 应该把以下检查升级进至少 eval 层，部分可进入 strict：

- chart-without-local-numeric-signal
- repeated-global-fact-overuse
- visual-placeholder-surface-leak
- low-role-distinctiveness
- mirrored-detail-pairing-risk

这样 future regressions 才不会再表现成“HTML 合法但看起来还是 generic”。

---

## 实施顺序

### Phase 1：先补 contract，不动大架构

1. 扩 BRIEF schema 的 slide-level 语义字段
2. 给 4 个 production preset 增加 usage rules
3. 增加 renderer 侧 fail-closed gate
4. 给 validate/eval 增加语义错配诊断

目标：

- 不重写 low-context 主链
- 先减少 heuristic 猜测空间

### Phase 2：再改 quality tier 和 render packet

1. 重写 `assess_quality_tier()`
2. 让 `build_render_packet()` 带上更强的 semantic sufficiency 信号
3. 把 tier 从“资料齐不齐”变成“能不能稳定渲染到 preset-native 水平”

### Phase 3：最后再考虑 family rollout

只有在 production preset 的 v2 contract 跑稳后，才应该把同类规则扩到：

- editorial family
- launch/brand family
- dev/technical family
- minimal/cultural family

---

## 风险

### 风险 1：schema 变复杂，`--plan` 成本上升

这是成立的。  
但更准确地说，是把原来藏在 renderer 里的隐性复杂度，转移到了显式 IR。

如果不做这步，复杂度不会消失，只会继续伪装成 heuristic。

### 风险 2：fail-closed 会降低首稿成功率

短期内可能会。  
但这是健康的，因为现在的一部分“成功”其实只是“生成了看上去合法但内容很虚的 deck”。

### 风险 3：style reference 维护成本会上升

是的。  
但 production preset 本来就应该承担更严格的规则说明成本；否则所谓 production-grade 只是 marketing label。

---

## 成功标准

low-context v2 完成后，至少要达成：

1. production preset 不再依赖 placeholder-style fallback 才能过关
2. chart/matrix/split 的进入条件可以被 contract 明确解释
3. `tier0` 与高质量首稿命中率显著相关
4. “结构合法但语义 generic”的回归可以被测试抓住
5. 其他 preset family 可以按同一套 contract 方式扩展，而不是每个 preset 再单写一套 ad hoc heuristic

---

## 最终判断

这次暴露出来的问题，不是 low-context 不该存在，而是它的 contract 边界还停留在“结构层”，没有 fully 升级到“语义层”。

所以下一步不该推翻这条链路，而应该做：

- **BRIEF 语义升级**
- **preset usage rule 升级**
- **renderer fail-closed 升级**
- **validate/eval 语义门禁升级**

如果这四件事做完，low-context 才会真正从“能稳定出 HTML”升级成“能稳定出 production-grade deck”。 
