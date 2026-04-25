# AI Native Org Deck Skill Bug Record

日期：2026-04-25，更新：2026-04-26  
状态：问题已记录，且 **skill / 生成链路修复已完成并回归验证通过**

## 1. 原始提示词

```text
生成一个《AI原生组织转型指南》的对内分享的文稿，结合目前AI原生企业的最佳实践，金蝶集团的转型要求，以及云之家产研团队的实际工作流程来深度分析，给出切实可行的操作过程
```

## 2. 本次产物地址

- HTML deck：`/Users/song/projects/slide-creator/demos/ai-native-org-transformation-guide-zh.html`
- BRIEF：`/Users/song/projects/slide-creator/plans/ai-native-org-transformation-guide-brief.json`
- 分享文稿：`/Users/song/projects/slide-creator/plans/ai-native-org-transformation-guide-share-script.md`
- 真实浏览器截图证据：`/tmp/ai-native-playwright-doc.png`

## 3. 用户反馈

用户反馈原文：

```text
你看过生成的效果吗，除了标题，都是空的，另外右下角怎么多出来一个小框SPEAKER NOTES - SLIDE 1 / 12
```

## 4. 复现方式

### 4.1 生成当前 deck

```bash
python3 scripts/validate-brief.py plans/ai-native-org-transformation-guide-brief.json
python3 scripts/render-from-brief.py plans/ai-native-org-transformation-guide-brief.json --output demos/ai-native-org-transformation-guide-zh.html
```

### 4.2 本地打开并截图

```bash
python3 -m http.server 8123
playwright screenshot -b chromium \
  http://127.0.0.1:8123/demos/ai-native-org-transformation-guide-zh.html \
  /tmp/ai-native-playwright-doc.png
```

### 4.3 实际观察结果

- 标题区正常渲染。
- 页面正文**并非真的没有生成**，而是只剩下少量低对比度 KPI 卡片文案，主观上非常像“空白页”。
- 右下角默认出现 `SPEAKER NOTES - SLIDE 1 / 12` 面板，遮挡内容。

## 5. 问题拆解

### Bug A：备注面板默认可见，不应出现在成品默认态

#### 现象

- 成品 HTML 在未进入编辑态时，右下角直接显示 `SPEAKER NOTES` 面板。
- 这属于 shell 级 UI 泄漏，不是内容层问题。

#### 代码证据

非 Swiss shell CSS：

- [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py:1431)

关键点：

- `#notes-panel` 默认定义了 fixed 定位、尺寸、背景、边框、阴影。
- 没有 `display: none;`
- 只有 `#notes-panel.collapsed #notes-body`，没有“默认隐藏，仅在编辑态显示”的基线样式。

Swiss shell CSS 同样存在同类问题：

- [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py:1975)
- [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py:1986)

这里虽然有 `#notes-panel.active { display: block; }`，但基础态仍未隐藏，所以 `.active` 规则并不能起到“从隐藏切到显示”的作用。

#### 判断

这是一个明确的 skill / shell bug。  
输出物不应该在默认预览态暴露 speaker notes 编辑面板。

---

### Bug B：Enterprise Dark 的 narrative cover 被错误地做成 KPI 仪表盘，导致“正文看起来像空的”

#### 现象

- 首屏不是没有内容，而是被渲染成了“大标题 + 3 个很弱的 KPI 卡片”。
- 在中文长标题场景下，标题占据了绝大部分视觉重量，下方卡片文字过小、颜色过弱、信息过薄，用户主观感受接近“除了标题都是空的”。

#### 真实浏览器证据

- 真实截图：`/tmp/ai-native-playwright-doc.png`
- 该截图表明：正文存在，但信息密度和对比度严重不达标。

#### 代码证据 1：当前 preset 路由把封面做成 KPI Dashboard

- [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py:2249)

当前 `_render_enterprise_kpi_dashboard(...)` 会在 cover 页生成：

- 一个巨大 hero 标题
- 三张 KPI 卡
- 卡片结构固定为：数字 / 标签 / trend 一句话

具体渲染逻辑：

- [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py:2266)
- [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py:2267)
- [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py:2268)
- [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py:2269)

这套结构适合经营看板，不适合观点型、叙述型的内部分享封面。

#### 代码证据 2：数字是从文本里抽数字，不够就回退到伪数字

- [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py:1565)

`_metric_values_from_spec(...)` 的行为是：

- 从 `title / key_point / visual / supporting_items / evidence_items` 中抽数字
- 如果抽不到足够数量，就用 fallback 补齐

而 cover renderer 的 fallback 是：

- [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py:2259)

也就是 `["2", "4", "1"]`

这意味着：当 narrative 内容是概念型、策略型、无强数字时，系统仍然会硬生成 KPI 呈现。  
结果不是“信息被增强”，而是“叙事被错误 KPI 化”。

#### 代码证据 3：卡片文字样式过弱

当前输出物中的卡片正文样式：

- [demos/ai-native-org-transformation-guide-zh.html](/Users/song/projects/slide-creator/demos/ai-native-org-transformation-guide-zh.html:77)
- [demos/ai-native-org-transformation-guide-zh.html](/Users/song/projects/slide-creator/demos/ai-native-org-transformation-guide-zh.html:103)

具体问题：

- `.ent-kpi-label` 只有 `10-12px`，大写、低对比度、弱信息层级。
- `.ent-trend` 也是 `10-12px` 左右，且依赖绿色/红色辅助色，不适合大段叙述。

而本次实际输出的首屏卡片内容其实已经被手工精修成了：

- [demos/ai-native-org-transformation-guide-zh.html](/Users/song/projects/slide-creator/demos/ai-native-org-transformation-guide-zh.html:778)

例如：

- `战略目标`
- `协同模式`
- `核心主链`

这些内容本身不是空的，但被 KPI 式样式渲染后，视觉重量太轻，无法支撑“正文已存在”的感知。

#### 判断

这不是单纯的内容问题，而是 **skill/preset renderer 与内容类型错配**：

- narrative deck 被错误套入 KPI dashboard cover
- KPI 字体层级又不足以承载 narrative 内容

---

### Bug C：skill 在“是否生成了可读正文”上缺少浏览器级验收

#### 现象

- 当前流程能通过 strict validate，但 strict validate 只验证结构、运行时、契约和若干视觉规则。
- 它不会拦截“首屏除了大标题外，其余内容虽然存在但几乎不可读/不可感知”的情况。

#### 证据

- 本次 deck 严格校验通过，但用户一眼仍然认为“除了标题都是空的”。
- 说明 skill 的验证闭环缺了一层“真实浏览器首屏可读性验收”。

#### 判断

这是 skill 工作流问题，不是单个 deck 的偶发问题。

## 6. 根因总结

本次问题不是“模型没有生成内容”，而是三件事叠加：

1. shell UI bug：speaker notes 面板默认可见，污染成品默认态。
2. renderer 选型 bug：`Enterprise Dark` 对非数字 narrative cover 仍强制走 KPI dashboard。
3. 验收缺口：缺少浏览器级“首屏正文可感知性”检查。

## 7. 修改方案

### 方案 1：修 shell，默认隐藏 notes 面板

目标：

- 成品默认预览态不显示 `SPEAKER NOTES`
- 仅在编辑态时显示 notes 面板

建议修改：

- `#notes-panel` 基础态改为 `display: none;`
- 由 `.active` 或编辑态 class 明确切换到 `display: block;`
- 非 Swiss 与 Swiss 两套 shell CSS 一起修，避免分支行为不一致

影响文件：

- `scripts/low_context.py`

验收：

- 默认打开 deck 时右下角无 notes 面板
- 点击编辑后 notes 面板出现
- `?presenter` 模式不受影响

---

### 方案 2：为 Enterprise Dark 增加“叙述型封面”分支，而不是一律 KPI 化

目标：

- 当 deck 是观点型、策略型、长文本型中文分享时，cover 不使用 KPI dashboard
- 改为更适合 narrative 的 cover layout，例如：
  - insight lead
  - consulting split hero
  - thesis + three action blocks

建议修改方向：

- 在 `Enterprise Dark` renderer 中，为 `cover` 增加内容类型判断
- 如果 `must_include/supporting_items/evidence_items` 缺乏真实数字信号，或者 `title/key_point` 明显是 thesis 型长句，则走 narrative hero
- 只有在明确存在真实数值信号时才走 KPI dashboard

候选修改位点：

- `scripts/low_context.py`
- `ENTERPRISE_ROLE_LAYOUTS`
- `_render_enterprise_kpi_dashboard(...)`
- 可新增 `_render_enterprise_narrative_hero(...)`

验收：

- 同类中文内部分享首屏不再出现伪 KPI
- 首屏正文区在不放大截图的情况下也能明确感知有内容层次

---

### 方案 3：禁止对非数值 narrative 强灌 fallback KPI 数字

目标：

- 不再对策略型内容注入 `2/4/1` 这类伪数字

建议修改：

- `_metric_values_from_spec(...)` 维持抽数功能
- 但 narrative renderer 若抽不到真实数字，不应回落到 KPI 语义
- 应直接转为 bullets / action cards / thesis blocks

## 8. 最终修复状态（2026-04-26 更新）

以下问题已不再停留在“方案”层，而是已经落实到 skill 程序页：

### 8.1 已完成的共享运行时修复

1. **后续页 reveal 不显示**
   - 根因：shared js-engine 只让第一页 `.reveal` 可见，后续页切页时没有同步切换 `.reveal.visible`
   - 修复：统一引入 `setActiveSlide(index)`，在切页时同时切换 slide 容器和 `.reveal` 子元素
   - 位置：
     - [references/js-engine.md](/Users/song/projects/slide-creator/references/js-engine.md)
     - [tests/test_validate_js_engine_contract.py](/Users/song/projects/slide-creator/tests/test_validate_js_engine_contract.py)

2. **默认暴露 speaker notes / edit chrome**
   - 根因：shell CSS 没有把 `#notes-panel` 作为默认隐藏态
   - 修复：默认预览态隐藏，仅在编辑态显示；新增校验防止回归
   - 位置：
     - [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py)
     - [tests/validate.py](/Users/song/projects/slide-creator/tests/validate.py)

3. **watermark 占位符未替换**
   - 根因：`references/js-engine.md` 中 `By kai-slide-creator v[version] · [preset-name]` 仅是模板 token，但生成器没有注入真实值
   - 修复：render 阶段替换为真实 skill version 和 preset name，并增加 unresolved placeholder 校验
   - 位置：
     - [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py)
     - [tests/validate.py](/Users/song/projects/slide-creator/tests/validate.py)

4. **scroll-snap deck 翻页不稳定**
   - 根因：先后出现过两个极端问题
     - `setupWheel()` 为空，某些环境里 wheel 不触发稳定翻页
     - 简单 JS wheel 拦截会把 momentum 尾巴误判成第二次翻页，导致“一次翻几页”
   - 最终修复：shared js-engine 改为 `animating -> draining -> idle` 的单手势一页状态机，并用 scroll settle 重新解锁
   - 位置：
     - [references/js-engine.md](/Users/song/projects/slide-creator/references/js-engine.md)
     - [tests/test_demo_quality.py](/Users/song/projects/slide-creator/tests/test_demo_quality.py)
     - [tests/test_validate_js_engine_contract.py](/Users/song/projects/slide-creator/tests/test_validate_js_engine_contract.py)

### 8.2 已完成的 Enterprise Dark preset 修复

1. **narrative cover 被错误 KPI 化**
   - 修复：为 `Enterprise Dark` 的 cover 增加 narrative/story 分支，不再对无真实数字信号的中文策略型封面强制灌 KPI dashboard

2. **P2 / P5 split 页标题裁切**
   - 根因：split rail 对中文长标题容错不足，左栏过窄、字号过大
   - 修复：调整 split rail 的列宽、间距和标题字号，避免标题被截

3. **左上角 brand mark 显示为 `slide-creator`**
   - 修复：brand mark 改为上下文文本，并在 Enterprise Dark 下默认隐藏

4. **网格线缺失或过强**
   - 根因：先前 shell 背景层压制了 preset 网格；后续一次修复又把网格拉得过强
   - 最终修复：保留 Enterprise Dark 的弱灰网格 + 更淡的蓝色叠层，回到“若隐若现”的底纹强度

5. **布局节奏重复**
   - 修复：
     - `feature` 不再和 `features` 共用同一个 matrix
     - `checkpoint` 不再和 `timeline` 共用同一个 timeline
   - 现在：
     - P6 是 feature grid
     - P7 是 matrix
     - P10 是 timeline
     - P11 是 governance table

主要代码位置：

- [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py)

## 9. 当前验证状态

本次不是只修单个输出物，而是改完 skill 后重新生成目标 deck，并通过以下验证：

1. 生成物：
   - [ai-native-org-transformation-guide-zh.html](/Users/song/projects/slide-creator/demos/ai-native-org-transformation-guide-zh.html)

2. 严格校验：
   - `python3 tests/validate.py demos/ai-native-org-transformation-guide-zh.html --strict`
   - 结果：通过

3. 回归测试：
   - shared js-engine / Enterprise Dark / demo-quality 相关测试通过

4. 浏览器截图证据：
   - [首页](/Users/song/projects/slide-creator/plans/ai-native-slide-01-final2.png)
   - [P2](/Users/song/projects/slide-creator/plans/ai-native-slide-02-final2.png)
   - [P5](/Users/song/projects/slide-creator/plans/ai-native-slide-05-final2.png)

## 10. 结论

这份记录文档现在已经不是“只有 bug 分析，没有落地结果”的初稿，而是：

1. 记录了原始提示词、问题、根因和修改方案
2. 同步了最终 skill 级修复结果
3. 补上了验证入口、测试位置和生成物证据

换句话说，这次修复已经落到了程序页，不是手改成品。

验收：

- 无真实数值的 deck，不再被包装成经营指标页

---

### 方案 4：把浏览器级首屏可读性加入 skill 验收

目标：

- 不再出现“HTML 合法、strict validate 通过，但实际看上去像空页”的情况

建议修改：

- 在 skill 工作流中加入浏览器截图或首屏 QA
- 至少对首页做一条人工规则：
  - 除主标题外，首屏必须存在一个可感知的第二信息层
  - 第二信息层的文本字号、对比度、可视面积不能过弱

可落地为：

- 浏览器截图对比检查
- 或更轻量的 DOM + CSS rule 组合检测

验收：

- 新生成的内部分享首页，不再因信息层级失衡被用户判断为“空”

## 8. 建议执行顺序

1. 先修 `notes-panel` 默认显示问题
2. 再修 `Enterprise Dark` narrative cover 分支
3. 最后补浏览器级验收，避免同类问题再次漏过

原因：

- `notes-panel` 是明确 bug，改动最小，收益直接
- cover renderer 是本次用户体验问题的主因
- QA 验收应在前两项明确后再补，避免把错误模板永久固化成测试

## 9. 本文档边界

本文档只记录：

- 用户问题
- 复现方式
- 根因分析
- 修改方案
- 原始提示词与输出物地址

本文档**不包含任何修复实现**，也**不修改当前输出物**。
