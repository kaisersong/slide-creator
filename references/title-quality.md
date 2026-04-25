# 标题质量参考

断言式标题的示例和模板。生成前校验时引用此文件。

机器可读的 title profile owner 位于 `references/title-profile-registry.json`。新增 preset 特例时，先更新 registry，再更新 prose 说明和校验逻辑。

---

## 禁止使用的通用标签

概览、Overview、架构介绍、Introduction、Summary、总结、结论、Key Insights、Next Steps、方法论、背景、问题分析、关键发现、展望、简介、说明、系统介绍、方案说明。

---

## 断言式标题示例

- ❌ `XX 架构概览` → ✅ `XX 架构可确保流量峰值期零遗漏`
- ❌ `Overview` → ✅ `How XX ensures zero downtime during traffic spikes`
- ❌ `系统介绍` → ✅ `三个核心模块，支撑日活百万级业务`
- ❌ `关键发现` → ✅ `80% 的用户流失来自首次加载超时`

---

## 标题模板

- "[Subject] 可确保/证明/支撑 [具体收益/结果]" — 技术/架构页
- "N 个 [核心概念]，解决 [关键痛点]" — 能力/特性页
- "[数据/事实] — [洞察/含义]" — 数据/发现页
- "[行动/决策] 的 N 个步骤/原则" — 方法/流程页
- 最短有力断言（≤12 字中文 / ≤6 英文词）— 强调/宣言页

---

## 多行标题平衡规则

多行标题不是浏览器自动换出来的副产物，而是需要**主动设计**的版式对象。

### 核心规则

- 桌面端标题超过 3 行，视为布局失败
- 当标题需要 2-3 行时，应显式控制断行；优先使用 `.title-line` 或风格文件约定的等价 line wrapper，而不是完全依赖自然换行
- 禁止出现单字孤儿行、单个短 token 孤儿行，尤其不能出现在中间行
- 禁止出现明显失衡的多行标题：中间行显著短于上下两行，或最短行明显少于最长行
- 不要靠把标题容器收得过窄来“制造设计感”；长标题优先缩短判断句，再增大 measure，再换布局

### 判断标准

- 2 行标题：两行视觉长度应接近；如果短行明显不到长行的一半，通常说明断行失败
- 3 行标题：中间行不能只有 1 个汉字或 1 个短 token，也不应明显短于上下两行
- 混排标题（中英数字混排）：`AI`、产品名、百分比、年份等短锁定词不能被单独甩成一条尴尬的孤儿行

### 修复顺序

1. 把标题改成更短、更硬的判断句
2. 放宽标题 measure，不要用过小的 `max-width` / `ch` 盒子强迫换行
3. 对 2-3 行标题做显式 line layout（`.title-line` / `<br>` / 风格等价结构）
4. 如果仍然失衡，换成给标题更多横向空间的布局

### 建议写法

```html
<h1 class="slide-title title-balance">
  <span class="title-line">越早把 AI 做成内核</span>
  <span class="title-line">越早锁定</span>
  <span class="title-line">下一轮壁垒</span>
</h1>
```

允许使用风格自己的等价类名，例如 `.cta-line`、`.headline-line`；关键是**断行被显式设计，并且行长平衡**。

### 风格特例

以下情况**不适用“水平多行平衡”**这条规则，必须尊重风格文件自己的标题构图：

- **竖排标题**：如 Chinese Chan 的 `.zen-vertical-title`，属于纵向构图，不用按横向 2-3 行平衡检查
- **分裂式标题 lockup**：如 Creative Voltage 的 `.main-title + .title-accent`，这是两个视觉块，不是普通自动换行标题
- **特效标题**：如 Neon Cyber 的 `.cyber-title[data-text]` glitch 结构，必须保留特效 DOM 契约，优先缩短标题或换布局，而不是随意拆 span
- **终端 / 命令行标题**：如 Terminal Green 的 boot sequence、command output、EOF，文本是终端对象，不按普通 heading measure 处理

以下情况仍然受“行长平衡”约束，只是**锚点和对齐方式不同**：

- Swiss Modern：左或左下锚定，不居中
- Modern Newspaper：底左锚定、保留大面积留白
- Paper & Ink / Dark Botanical / Vintage Editorial：可居中或底锚，但多行标题仍然不能失衡
