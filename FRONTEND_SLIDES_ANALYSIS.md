# `frontend-slides` 对 `slide-creator` 的可借鉴优化分析

分析时间：2026-04-04

对比对象：

- 本地项目：`D:\projects\slide-creator`
- 参考项目：`https://github.com/zarazhangrui/frontend-slides`

## 先说结论

`slide-creator` 整体上已经明显强于 `frontend-slides`，尤其是在以下方面：

- 主题体系更完整：21 个预设 + `themes/` 自定义主题 + `starter.html` 扩展机制
- 运行时能力更强：Play Mode、Presenter Mode、讲稿 `data-notes`、演讲者窗口同步、远控按键
- 生成约束更成熟：`--plan / --generate` 两阶段、图表/流程图 SVG 约束、Blue Sky 模板化基座
- 输出链路更强：可接 `kai-html-export` 做 PPTX / PNG 导出，并支持 native 模式
- 文档和引用素材更丰富：`STYLE-DESC.md`、`diagram-patterns.md`、多个 style reference

所以这次对比的重点，不是“补齐核心能力”，而是看 `frontend-slides` 在**产品化闭环、规则显式化、结构拆分**上有哪些值得借鉴的地方。

## `frontend-slides` 里值得借鉴的点

### 1. 给“增强已有 HTML 演示稿”补一套明确规则

`frontend-slides` 在 `SKILL.md` 里专门写了 `Mode C: Enhancement`，把修改已有 deck 时最容易出问题的地方写得很具体：

- 加内容前先检查密度上限
- 加图片时强制检查 `max-height`
- 可能溢出时主动拆 slide
- 修改后强制验证 `overflow: hidden`、`clamp()`、1280x720 适配

而 `slide-creator` 虽然已经支持“增强 existing HTML”，但目前只是 `SKILL.md` 里一句：

- `User wants to enhance existing HTML → read it, then enhance. Split slides that overflow.`

这说明 `slide-creator` 已经有方向，但缺少执行级 guardrails。

建议：

- 在 [`SKILL.md`](D:\projects\slide-creator\SKILL.md) 或 [`references/workflow.md`](D:\projects\slide-creator\references\workflow.md) 增加一个明确的“Enhancement Rules”小节
- 把“增量修改 deck”的检查项写成固定 checklist，而不是一句原则
- 特别强调图片插入、长 bullet 增补、已有 slide 追加内容时的自动拆分策略

价值：

- 降低“改已有 deck 时破坏 viewport fitting”的概率
- 让 skill 在修改场景下更稳定，而不仅是从零生成时稳定

优先级：高

---

### 2. 给 `slide-creator` 增加“分享/分发”闭环

`frontend-slides` 的一个明显优点，不是生成本身，而是**生成后继续往前走了一步**：

- `scripts/deploy.sh`：一键部署到 Vercel，得到可分享链接
- `scripts/export-pdf.sh`：一键导出 PDF
- Skill 层面有一个明确的 “Would you like to share this presentation?” 后续分支

相比之下，`slide-creator` 当前的“生成后闭环”主要是：

- 浏览器直接打开 HTML
- 如需导出，交给 `kai-html-export`

这已经能解决 PPTX / PNG，但还有两个空档：

- 没有“直接给我一个可分享 URL”的官方路径
- 没有“给我一个 PDF 方便发邮件/IM”的轻量路径

建议：

- 给 `slide-creator` 加一个可选的 Phase 6: Share
- 轻量方案：不把部署逻辑塞进主 skill，而是提供一个姐妹 skill / 脚本
- 最小闭环：
  - `share as url`
  - `export as pdf`
  - `export as pptx/png`（继续复用 `kai-html-export`）

价值：

- 从“生成工具”变成“交付工具”
- 对非技术用户更友好，尤其是需要手机查看、微信/Slack/邮件转发的场景

注意：

- `slide-creator` 的核心哲学是零依赖 HTML；分享能力最好作为**可选后处理**，不要污染主生成链路
- 部署脚本可独立，避免把 npm / vercel 依赖引入核心路径

优先级：高

---

### 3. 把“动画策略”从 style 索引里再拆出来一层

`frontend-slides` 单独有一个 `animation-patterns.md`，好处是：

- “情绪 -> 动画”映射单独维护
- 背景效果、入场效果、交互效果、故障排查都放在一起
- 在 Phase 3 只按需加载，边界清晰

`slide-creator` 当前也有同类内容，但分散在：

- [`references/style-index.md`](D:\projects\slide-creator\references\style-index.md) 的 effect/feeling guide
- [`references/html-template.md`](D:\projects\slide-creator\references\html-template.md) 的 animation recipes

这不算缺能力，但在可维护性上还有提升空间。

建议：

- 新增一个独立的 [`references/animation-patterns.md`](D:\projects\slide-creator\references\animation-patterns.md)
- 把这些内容集中进去：
  - 情绪 -> 动画节奏映射
  - 常用 reveal 变体
  - 背景特效范式
  - 性能/减弱动画/移动端降级规则
- `style-index.md` 只保留“风格选择”和高层映射
- `html-template.md` 只保留必要模板骨架与少量示例

价值：

- 继续强化 `slide-creator` 的 progressive disclosure
- 降低 `html-template.md` 的混合职责
- 后续扩展新主题时，更容易统一 motion language

优先级：中

---

### 4. 明确“生成后预览比较”的交互落点

`frontend-slides` 明确要求：

- 生成 3 个 mini preview
- 自动打开给用户看

`slide-creator` 已经有 preview 机制，而且比它更先进：

- mood -> preset 映射更完整
- 可以嵌入 logo
- 主题数量更多

但在文档表达上，还可以把“预览怎么被看见”描述得更清楚一些。现在流程里写了生成 preview 文件，但没有像 `frontend-slides` 那样把“立刻打开”作为显式动作强调出来。

建议：

- 在 [`references/workflow.md`](D:\projects\slide-creator\references\workflow.md) 的 preview 步骤里明确：
  - 生成后立即打开
  - 或直接生成一个统一 comparison board（比三个独立文件更好）

如果升级，可以进一步做成：

- `index.html` 风格对比页
- 同屏展示 A/B/C 三种预览
- 支持 “pick A / pick B / mix A+B”

价值：

- 降低 preview 阶段的交互摩擦
- 让“Show, Don’t Tell”更完整落地

优先级：中

---

### 5. 把 inline editing 策略说清楚，解决文档层的不一致

这是这次对比里最值得顺手修掉的一个点。

`frontend-slides` 对 inline editing 的描述比较一致：

- Phase 1 询问是否需要
- 如果用户选 No，就完全不生成相关代码

而 `slide-creator` 当前文档里有轻微不一致：

- [`SKILL.md`](D:\projects\slide-creator\SKILL.md) 的 generation contract 写的是：**每个生成的 HTML 都必须包含 Edit Mode**
- [`references/workflow.md`](D:\projects\slide-creator\references\workflow.md) 写的是：默认包含，但用户可以显式选 No
- [`README.md`](D:\projects\slide-creator\README.md) 也暗示 inline editing 是可选项

建议二选一：

- 要么把 edit mode 定义为真正的强制能力，那么 workflow / README 一并改成“不可关闭”
- 要么保留现在更合理的“默认开启，但允许关闭”，那就把 `SKILL.md` 的 non-negotiable contract 改掉

我更推荐后者：

- 默认开启
- 用户可关闭
- 关闭时减小 HTML 体积，适合纯交付场景

价值：

- 减少技能自身规则冲突
- 让 agent 在生成时少一个自相矛盾的判断

优先级：高

## 可以参考，但不建议直接照搬的点

### 1. 内建 PDF 导出脚本

`frontend-slides` 的 `export-pdf.sh` 很实用，但它本质是“截图拼 PDF”。

对 `slide-creator` 来说，这条路可以有，但不应该替代现有导出体系：

- 你已经有 `kai-html-export`
- 而且 native PPTX 是更高价值能力

所以更合理的借鉴方式是：

- 补一个“轻量 PDF 交付”选项
- 作为补充，不要成为主要导出路径

优先级：中

---

### 2. 内建 Vercel deploy 脚本

它对分享很方便，但 `slide-creator` 不一定适合直接把这个责任塞进主 skill。

更好的方式可能是：

- 做一个独立的 `share-slides` skill / helper
- 或在 `slide-creator` 最后提示“要不要帮你部署分享”

这样可以保住主 skill 的纯度。

优先级：中

## 不建议从 `frontend-slides` 反向引入的点

### 1. 核心生成能力本身

在生成架构上，`slide-creator` 已经比 `frontend-slides` 更完整：

- 更强的模板基座
- 更多主题
- 更强的 presenter / notes / edit / export 组合
- 更清晰的自定义主题机制

所以不要为了“向它看齐”去简化现有结构。

---

### 2. 把所有规则重新集中回一个更大的主 skill

`frontend-slides` 的分拆已经不错，但 `slide-creator` 目前的模块化程度其实更高。

尤其是：

- `STYLE-DESC.md`
- `diagram-patterns.md`
- `themes/`
- `kai-html-export` 外部协作

这些都说明你的边界划分已经更成熟。优化方向应该是**继续拆清职责**，而不是回退到更厚的单文件说明。

## 建议的落地顺序

### 第一批：最值得做

1. 给“enhance existing HTML”补完整 guardrails
2. 统一 inline editing 的规则表述
3. 增加分享闭环设计：URL / PDF / PPTX / PNG 的统一出口

### 第二批：结构优化

1. 抽离 `animation-patterns.md`
2. 把 preview 阶段升级成 comparison board 或显式 auto-open

## 一个更务实的判断

如果只问一句：“`frontend-slides` 对 `slide-creator` 最有价值的启发是什么？”

答案不是视觉风格，也不是核心生成逻辑，而是：

**把生成后的最后一公里补完整，以及把“修改已有 deck”这条高风险路径写成硬规则。**

这两个点一旦补上，`slide-creator` 会从“很强的生成器”更接近“完整可交付的演示文稿工作流”。
