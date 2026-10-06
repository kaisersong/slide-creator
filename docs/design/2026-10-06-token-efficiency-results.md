# 上下文优化与真实端到端评测结果

后续质量恢复结果见 [完整评测报告](2026-10-06-quality-recovery-results.md)：候选 5 的 26 次全部通过，生成 token 中位数降低 77.43%，耗时降低 38.0%，质量均分提升到 87.88。下文保留前两候选的历史拒绝结论。
日期：2026-10-06。工作分支：`codex/slide-token-eval`。

## 结论

完成详细方案、真实基线、两个候选的完整评测。每臂 26 次模型任务，共 78 次，全部有终态和真实 usage。正向产物 24 个/臂均有 strict、来源/质量检查、两个视口 × window/present 的截图和独立匿名评审；负向路由各 2 次/臂。

第二候选生成累计 token 中位数下降 **76.95%**，耗时中位数下降 **36.48%**。但两个候选均未通过采用门槛：总体质量分略降，部分场景回退，技术语言的 80/100 项目目标没有在全部技术样本中达到。保留实验分支和证据，不合并、不发布，不宣称生产可用。

本轮回答的是“此 CLI 环境的显式 preset → BRIEF → canonical renderer → 可打开 HTML”的效率与效果。它不是 Claude Code、OpenClaw、桌面 GPT-6.1、安装消费者或 22 风格全部真人任务的验证。

## 输入与环境

- 基线：`v2.30.2 / 9e999874b2107c3a8a727962151c61d275f74bf3`。原项目目录未修改。
- 冻结输入：8 类正向文稿 × 3 次；2 类负向 × 1 次。文稿是固定测试材料，不是生产客户数据。
- 5 个 native core、Strategy Consulting profile、Fantasy Rainbow custom、稀疏 API 材料；包含中英文技术、产品、思想、数据和 10 页战略稿。
- 运行包使用 Git 管理的公开 runtime 文件；不包含私有 Cloudhub/Kingdee 资产。
- 模型：本机 CLI 实测可用 `gpt-5.5 / high`，CLI `0.158.0`，Python `3.12.14`，并发 2。桌面配置 `gpt-6.1-sol` 被 CLI 账户拒绝，探针/环境预跑另外保留，未代入正式样本。
- 使用同一个 Python 绝对路径。核心依赖 bs4/Playwright/Pillow/jsonschema 版本两臂相同；中途为仓库回归新增的 pptx/lxml 与 Chromium 测试安装不参与该生成路径。浏览器 QA 使用 Chrome 154。
- 两臂分时运行，服务负载、网络重连、缓存和机器并发仍会影响耗时；不能把本次 wall time 差异全部解释为模型计算改善。

## 完整生成链计量

正向 n=24/臂。累计输入包含多次工具调用重新带入的上下文，不是单个文档长度。缓存输入包含在 input_tokens 内；output 包含 reasoning 时不再另加。

| 指标 | 基线 | 候选 1 | 候选 2 |
|---|---:|---:|---:|
| 生成耗时中位数 | 223.53 秒 | 139.52 秒 | 141.97 秒 |
| 生成耗时均值 | 230.17 秒 | 172.36 秒 | 161.28 秒 |
| 生成耗时 p90 | 306.67 秒 | 243.10 秒 | 212.76 秒 |
| 累计输入 token 中位数 | 1,405,614 | 364,150 | 318,865 |
| 缓存输入 token 中位数 | 1,316,800 | 332,992 | 281,600 |
| 非缓存输入 token 中位数 | 93,760 | 35,774 | 37,649 |
| 输出 token 中位数 | 9,126 | 6,302 | 5,763 |
| 累计输入+输出 token 中位数 | 1,415,463 | 369,328 | 326,308 |
| 累计输入+输出 token 均值 | 1,606,165 | 628,648 | 489,285 |
| 质量均分 /100 | 77.88 | 76.88 | 76.75 |
| 技术语言均分 /100 (n=15) | 78.33 | 80.07 | 81.40 |
| 含 QA+judge 耗时中位数 | 269.41 秒 | 199.14 秒 | 185.53 秒 |
| 含 judge token 中位数 | 1,442,214 | 398,754 | 354,409 |

候选 1：token 中位数变化 -73.91%，耗时 -37.58%。候选 2：token -76.95%，耗时 -36.48%。这是 provider usage 实测，未用字节/4、HTML 大小、程序渲染毫秒数代替。

## 效果与采用判断

质量由匿名图片/来源审阅的六项等权均分构成：叙事、视觉节奏、证据忠实、无生成残留、风格适配、演讲支持。它是模型评审指标，存在主观与重复判分误差；程序检查与硬错误另外记录。

| 案例 | 基线质量均分 | 候选 1 | 候选 2 | 候选 2 配对变化 |
|---|---:|---:|---:|---:|
| data-kpi-en | 67.33 | 67.00 | 64.67 | -2.67 |
| swiss-architecture-zh | 82.67 | 82.33 | 77.00 | -5.67 |
| blue-launch-zh | 84.33 | 82.67 | 85.67 | +1.33 |
| enterprise-security-en | 81.67 | 76.33 | 73.00 | -8.67 |
| chan-learning-zh | 85.00 | 76.67 | 84.00 | -1.00 |
| consulting-strategy-zh | 59.00 | 61.33 | 59.67 | +0.67 |
| fantasy-custom-zh | 88.33 | 85.33 | 87.00 | -1.33 |
| sparse-api-en | 74.67 | 83.33 | 83.00 | +8.33 |

第二候选质量配对均值变化 **-1.12**；按案例聚类 bootstrap 95% 区间 **[-4.33, 2.25]**。只有 8 个固定主题，不作广泛统计显著性或非劣性证明。

技术语言平均 **81.40/100**，10/15 达到 80；以下 5 次未达到：

- data-kpi-en / rep-3: 69/100。
- enterprise-security-en / rep-1: 78/100。
- enterprise-security-en / rep-2: 76/100。
- enterprise-security-en / rep-3: 76/100。
- swiss-architecture-zh / rep-3: 78/100。

80/100 是 ASD-STE100 原则对齐的项目 rubric。英文与中文适配单列，完整官方词典、词性/词义和全标准符合度未核验，不能把这个分数称为标准认证或全标准覆盖率。自动语言诊断只提供线索，语义和数字归属由独立审阅检查。

采用 gate：两候选均 **FAIL**。第二候选速度/token 达标，但 Swiss 与安全稿质量回退超过单案例 5 分；技术语言还有低于 80 的样本；Chinese Chan 出现新的裁切/逐次 pass 回退。未以整体平均分掩盖局部失效。

## 两次候选做了什么

候选 1：从原 schema/style compiler 生成约 4–5 KB 模型契约；模型写内容与 BRIEF，程序仍完整读风格与 runtime。按需加载技术语言规则。修复 p95/v2 标识符中的数字被误当测量值。

候选 2：增加可选逐页 speaker_note，旧 BRIEF 保留 explanation fallback；去掉 Data Story 行动卡片三行 clamp；增加短标题/卡片密度/真实比较语义规则和查询别名。没有引入 P2 图表 schema 或 P3 反馈页面。

正文与备注隔离改善了 Blue Sky 与部分样本，但不足以解决 renderer 的内容忠实度问题：部分文字被截成片段、全局数字串入不相关页、真实规则被放在红叉 Before 区、栏目仍混用中文、缺少真正 source-aware 的组件语义与字段预算。多读实现能让旧模型绕过一些模板问题；只缩上下文不自动保持这种补偿能力。

## 独立控制与回归

- 22 个内置 + 2 个公开 custom 的同 BRIEF CLI/strict 控制：23 个两版通过且 HTML 字节一致；ASCII Stream 两版均 strict 失败。这是确定性程序层证据，不是模型 E2E/所有内容覆盖。
- 数字修复消融：基线 Data Story 的同一个 BRIEF 原输出包含无来源的 95；仅修数字解析重渲染后该额外数字消失。不能据此说整个图表/文稿质量已完全修复。
- CTA 修复消融：同一个失败 BRIEF 原三行卡片溢出，取消裁切后在两视口 × 两模式检查中不再出现该溢出。
- 7 种风格中 speaker_note 仅写入 data-notes，不进入观众可见正文；旧配置 fallback 回归通过。
- 最近全量非 slow 仓库回归：**2829 passed / 114 skipped / 7 deselected / 2 failed**。两项 Fantasy Rainbow 失败已在基线原提交复现，未伪装为全绿。新增真实播放导航 slow 回归两 preset 通过。

## 评测校准与成本边界

旧几何 QA 强切 p-on 导致匿名 shared controller 的假空白；Blue Sky 的窗口导航点会平移 track，不能用作播放导航。修复后通过真实控制器/键盘进入目标页，检查 counter、active/visible 与视口位置，并记录页面错误。基线与受影响候选的生成收据保持原样，只重新检查截图/判分；旧收据与无效评分全部保留。

初始评测错误和重判不是优化收益。比较表使用统一最终 QA；被废弃检查/judge 的额外耗时和 token 在 calibration_overhead 中单列。模型不可用与依赖预跑的部分调用没有完整 usage，标记未知而不是填 0。协调者写代码/分析本身的 token 不在滑稿生成计量中，也没有伪造计数。

## 下一轮应做的改变

1. 先修内容承载：禁止静默截断与补齐重复项；仅使用本页来源事实；没有真实 Before/After 时不渲染红叉对比。
2. 给组件增加 source-aware 的 label/detail/value/unit/condition/actor，采用兼容旧 BRIEF 的显式结构；不要继续增加长篇提示词来补偿 renderer。
3. 对技术文稿从最终可见正文检查条件、执行者、单位和清晰步骤；80 门槛失败时保留失败事实并修复，不能只看备注或平均分。
4. 保留该 manifest，加失败样本的独立内容控制；新候选重新冻结、完整跑同一套，再扩大到用户真实文稿与其他模型/运行面。

## 文件与复跑

详细方案：[2026-10-06-token-efficiency-plan.md](2026-10-06-token-efficiency-plan.md)。命令与口径：`evals/token-efficiency/README.md`。原始证据：`evals/artifacts/token-efficiency/2026-10-06-p1-formal/`；每次有 prompt、raw trace、stderr、usage、BRIEF、HTML、strict/quality/geometry、截图与 judge。精简可版本管理结果：`evals/token-efficiency/results/2026-10-06/`。

```sh
python scripts/token-efficiency-eval.py summarize --run-dir evals/artifacts/token-efficiency/2026-10-06-p1-formal --arm baseline
python scripts/token-efficiency-eval.py compare --run-dir evals/artifacts/token-efficiency/2026-10-06-p1-formal --candidate-arm candidate2
```

此分支是实验结果与后续优化基础，不是已批准的新默认生成器。主目录、main 分支和发布资产均未改动。


后续字号、重复文案、基线失败与完整复测：[2026-10-06-visual-polish-results.md](2026-10-06-visual-polish-results.md)。新正式臂25/26，未通过维护门槛；此处保留原历史结果。
