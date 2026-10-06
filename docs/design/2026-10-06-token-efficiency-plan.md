# slide-creator 上下文优化与持续评测方案

日期：2026-10-06。工作分支：`codex/slide-token-eval`。
基线：`v2.30.2 / 9e999874b2107c3a8a727962151c61d275f74bf3`。

## 1. 目标与交付边界

降低真实 `用户请求 → BRIEF → renderer → strict validation → 可打开 HTML` 链路的 token 与耗时，同时保留叙事、事实、视觉、风格和可编辑性。先冻结并启动当前版基线计量，再独立准备候选；完整基线完成并校准后，才用相同冻结任务运行候选。失败、超时和缺失指标必须进入报告。

本轮实现 P1（精简生成上下文）与技术语言策略，交付可复跑的端到端评测工具。基线先冻结并启动；首个有效样本有真实计量后可在候选 worktree 准备实现。基线全部终态且完成评测校准后，才冻结候选并启动后测。P2（结构化图表）与 P3（交互反馈）保留为下一轮方案，不能混入本轮以致无法归因。不上线、不合并主分支、不发布 release；独立 worktree 保留全部可审阅结果。

## 2. 问题与证据

现有 `SKILL.md` 的 `--generate` 路由要求读取风格、composition、标题、HTML 模板、JS 引擎、基础 CSS、反模式。仅 `html-template.md + js-engine.md + base-css.md` 就约 50.6 KB。程序却已在 `scripts/low_context.py` 自动编译风格、提取 runtime，并在两个 CLI 入口执行写入前严格校验。正常内容生成没有必要让模型同时读实现代码。

html-plan 的有用做法是：模型写声明式内容，runtime 展开交互，打包器内联资产，评论导出定位差异。其示例 14.6 KB 源码可打包到 223.5 KB 页面，这是程序展开的证据，不是实际 token 降低百分比。不能以字节 / 4、最终 HTML 大小或程序毫秒数代替端到端模型计量。

旧 `run-skill-evals.py` 强制最多 3 份参考文件，会覆盖当前 skill 的读取要求；style rubric 还可能来自 fixture。新基线不能沿用这两个约束。旧测试保留，新实验独立。

## 3. P0：冻结输入与计量

- 从基线提交复制实际发布的运行文件：`SKILL.md/main.py/scripts/schemas/references/themes`。只拷贝 Git 管理文件，记录每个文件 SHA-256 和快照摘要。企业私有主题不在此公开运行包内，报告必须说明。
- 每次模型运行得到全新的目录，目录只放运行包与该次任务；不放此前 deck、trace、评审结果、优化方案。
- 当前桌面配置 `gpt-6.1-sol` 被 CLI 账户拒绝；可用性探针确认 `gpt-5.5 / high` 返回真实 usage。两臂统一使用这个已验证可用的模型。冻结 CLI 版本、Python 版本、依赖版本、浏览器版本、模型设置。禁用额外 MCP 与个人项目 hooks，使两臂拥有相同工具面。这轮结果仅代表该 CLI 模型环境，不能称桌面模型实测。
- 不给旧版添加新语言/精简契约，不限制它只能读 3 个文件。两臂收到同样的任务与固定来源。
- 正向 8 案例，每案 3 个独立模型运行：5 个 native core（Data Story、Swiss Modern、Blue Sky、Enterprise Dark、Chinese Chan），1 个 Strategy Consulting profile，1 个 Fantasy Rainbow custom，1 个稀疏技术材料。覆盖英文技术、中文技术、数据、产品、思想与长篇 10 页。
- 2 个负向路由案例（报告、仅导出），每臂各 1 次。另有无效 BRIEF 拒绝写入、同 BRIEF 渲染一致性与既有内容/风格路径的确定性回归，不当作生成 token 实验。
- 每臂合计 26 次模型生成/路由任务。每个失败保留；不静默重试或挑选较好结果。超时保留部分 trace 和现有 side effects，独立重跑须标记。
- 两臂先后分块运行符合“先基线后优化”。运行时段与缓存变化是限制：报告 input、cached input、uncached input、output，不能据此把缓存效应归为产品优化。
- 环境预跑发现登录 shell 重置 PATH；两臂任务固定给出同一个 Python 绝对路径，避免搜索/安装依赖污染。预跑另存且不计入正式样本。正式评测并发 2 个独立任务，两臂相同；CPU 争用与服务端负载仍是时间指标的限制。

## 4. 指标与计时边界

| 层 | 指标 | 证据 |
|---|---|---|
| 模型端到端生成 | subprocess 启动到退出的墙钟耗时；输入、缓存输入、输出、总 token；工具调用、失败命令、修复命令 | 原始 JSONL、stderr、运行设置 |
| 程序 QA | strict、quality、浏览器检查各自耗时 | 独立检查日志与报告 |
| 审阅 | 截图 + 来源的匿名质量审阅耗时/token | judge prompt、trace、JSON |
| 完整评测成本 | 生成 + 程序 QA + judge，总耗时与总 token | 分项求和，缺失值不作 0 |
| 正确性 | 页数、preset、canonical provenance、必需事实、数字准确、来源遗漏 | BRIEF、HTML、固定事实清单 |
| 内容与视觉 | 叙事、视觉节奏、证据忠实、风格适配、演讲支持、语言 | 独立 rubric 与截图 |
| 浏览器 | clipping/overflow/contrast、window/present 两模式、console/page error | 1600×900 与 1280×720 截图及几何报告 |

JSONL 中 `turn.completed.usage` 按累计语义读取，不能重复求和。缺失 usage、运行错误、判分缺失、截图缺失、非法 judge JSON 均标记 incomplete。字体加载和浏览器检查错误单列，不能伪装为视觉通过。

校准记录：原几何 QA 在 present 模式只切换 `.p-on`，未通过真实 controller 更新 `.visible`、reveal 与页码，导致匿名控制器 deck 的假空白。评测 v2 必须通过实际导航按钮/控制器切页；activation 失败要报错。已完成生成的耗时/usage 保持原样，旧 QA/judge 收据保留为 initial，再用统一 v2 对两臂计量。截图标签包含 slide/mode/viewport，明确重复视口不是额外页或动画帧。校准的时间/token 作为额外开销单列，不能藏入优化收益。

事实依据来自冻结任务，不来自模型自己生成的 BRIEF。numeric faithfulness 的旧检查与来源文本一同运行；额外固定事实清单检查必须出现的信息。来源出现过的数字也可能配错单位或实体，匿名审阅仍需检查语义关系。

## 5. P1：供模型使用的精简契约

新增 `--model-context --preset <name>`：从现有 schema、风格 compiler 与 layout 能力生成简短 JSON，包含 BRIEF 形状、允许布局、风格辨识点、字体、内容约束、runtime 默认值；不输出 CSS/JS 源码。风格引用仍由程序完整读取，不制造另一份手维护真相源。

`references/generation-contract.md` 只说明模型需要做的内容任务、CLI、质量要求和按需读取方式。`--generate` 正常路径加载它与所选 preset 的机器契约；技术文稿另读语言规则。HTML template/runtime/base CSS 仅在实现故障或用户明确要求修改实现时读取。外部内容的清理、数字归属、论点证据和演讲 notes 不能因精简而省略。

保持 `BRIEF.json` schema、旧缺省配置、所有 preset 能力路由和 strict gate；不允许自由手拼 HTML。低上下文稳定与丰富材料质量同时测，不以更少内容换取 token。

基线发现的正确性修复：`_extract_numbers()` 将 `p95` 的 95 误作测量值，数据稿出现应为 310 ms 却显示 95 的指标。候选增加 ASCII identifier 边界，保留 CJK 相邻数字、百分比、单位、普通小数。独立回归核对 `p95/p99/v2.30.1/310ms/峰值120`，并使用基线 BRIEF 重渲染作同输入消融。它属于数字正确性修复，不是 P2 schema 扩展；报告必须将该修复的质量收益与上下文优化区分，不能只把成稿改善归因于 token 策略。

候选 1 后测发现的第二迭代：新增逐页可选 `speaker_note`，将讲者指令与观众正文分开；旧 BRIEF 没有此字段时保留原来 explanation 的备注 fallback。Data Story 行动卡片的三行 clamp 会裁切合法的 25 词短句，去掉该裁切后以同 BRIEF 做浏览器消融。模型契约增加短标题建议、卡片密度、真正的 before/after 才使用对比展示，并规范内置 preset 的查询别名。候选 1 保留为未采用实验；候选 2 使用新的 snapshot，在同一 manifest 下完整重测 26 次，不能把两候选的最好结果拼接。

## 6. 技术语言：ASD-STE100 项目目标 80%

仅在技术文稿启用。保持用户指定语言：英文使用 STE 写作规则；中文采用对应的简化技术语言，评分标注 `zh-CN adaptation`，不能称英文标准原文合规。代码、命令、产品名称、单位、原始引文允许保留，技术术语须定义且用法一致。

目标是项目 rubric ≥80/100，来源是 ASD-STE100 Issue 9 的规则框架，不是标准定义了“80% 认证”。官方标准还有词典、词义和词性要求；缺少完整词典或专业审查时，完整标准覆盖标记为未验证。不得将几个正则检查的通过率冒充标准覆盖率。

评分分为 10 项，每项 10 分：术语与词义一致、短句、单句单意、主动语态、清晰主语、简单时态、指令清楚、条件在动作之前、段落与名词组简洁、数字单位/歧义处理。自动检查给出长句、常见复杂词、被动/完成时线索和空文本；语义项由匿名模型审阅给分并引用文稿证据。自动规则只作诊断，不直接声称完整标准满足。

英文描述句 ≤25 词，操作指令 ≤20 词；段落 ≤6 句；一个步骤一个动作；技术名词例外有明确清单。中文按自然句/动作与术语评价，不套英文词数到汉字。简化不得删除条件、风险、数字、单位和因果关系。

## 7. P2/P3 后续路线

P2：在单独 schema 版本中增加图表的 label/value/unit/source、流程 nodes/edges、比较 dimensions。先覆盖最高频组件；使用 renderer 统一解析与 strict lint。对照对象始终是当前最佳已验证版本，不能回到无 runtime 手写 HTML 来夸大收益。

P3：为精修提供逐页 claim、证据、notes 和评论；导出带 brief hash、slide id、字段路径的 JSON diff。浏览器中的反馈是数据，不是命令。只应用有效路径上的变更，明确区分默认未查看与用户已确认。Auto 路径继续直接出稿，不新增固定确认等待。

## 8. 通过条件与持续循环

- 两臂所有计划运行都有终态记录；usage、产物、QA、匿名审阅完整。失败可使优化不通过，但不能使报告消失。
- 页数、preset、strict、事实与浏览器硬错误不回退；负向案例不误生成。既有基线错误保留原样报告。
- 匿名质量分配对均值回退 ≤3/100，且任一案例均值回退 ≤5；技术语言 ≥80 项目评分。
- 生成 total token 中位数至少降低 10%，耗时中位数不增加超过 10%。同时报告完整 QA+judge 成本，不能只选择优化的那一项。
- 报告每案、每次、均值、中位数、p90、配对差异和 bootstrap 区间。3 次重复只支持方向判断，不能宣称广泛统计显著；下一轮扩大真实任务样本。
- gate 不过时，保存失败原因；调整候选再跑完整候选臂。每个候选使用新 snapshot hash，不能混合多个实现的结果。

## 9. 文件与验收

方案：本文件。评测输入：`evals/token-efficiency/manifest.json`。评测/对照入口：`scripts/token-efficiency-eval.py`。精简契约：`scripts/model_context.py`、`references/generation-contract.md`、`main.py/SKILL.md`。语言策略：`references/technical-language.md`。

结果：`evals/artifacts/token-efficiency/<run-id>/`，含 runtime snapshots、environment、每次 prompt/trace/usage/HTML/BRIEF/截图/quality/judge、baseline 汇总、candidate 汇总、comparison.json 和中文报告。机器结果与完整产物留在 worktree；可检视报告进入版本管理。新入口需运行有意义的契约/计量回归，现有 renderer、IR-first、旧配置、核心 preset 与 custom 路径测试继续执行。

来源：
- html-plan 本地源码：`/Users/kai/projects/refre-proj/html-plan/skills/html-plan/`。
- [OpenAI：Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills)。
- [OpenAI：Non-interactive mode](https://developers.openai.com/codex/noninteractive)。
- [ASD-STE100 官方下载与说明](https://www.asd-ste100.org/STE_downloads.html)。本机 web 抓取官方标准全文返回 403；语义评分与词典核验边界须保留，不能推断已验证官方全文。

## 10. 候选 3：在效率路径上修复内容质量

用户在候选 2 的报告后要求继续研究质量问题，并将技术语言降为尽力满足。新对照使用验收策略 v2：STE 评分继续逐次计量，80 分为观察目标，不阻止采用；效率、事实、版面和质量回退阈值全部保持。历史策略 v1 的报告与结论保留。CLI 必须显式指定 `--language-policy observe`，默认仍为历史 required 策略。

候选 3 先修 renderer，再做同一冻结 manifest 的完整 26 次生成：页内 supporting_facts/numeric_facts 不混入全局事实；显式事实不强制填满组件、不用无关句子作解释；Swiss 验收页不把多项条件压成单句引用，装饰标签用序号替代截断词；Enterprise 普通事实用中性面板，不推断正误或前后状态，正文不显示 visual 指令与 thesis 代码；咨询风格以原 demo CSS 的组件装载事实，清除嵌套示例文案、假指标与版本信息；Data Story 遵守 avoid 图表策略，不按卡片位置画方向箭头；Chinese Chan 竖排标题使用高度预算，并显示结尾动作事实。

测试顺序：先目标回归；用候选 2 的 24 份 BRIEF 做同输入消融（只用于识别 renderer 效果，不能当模型端到端结果）；检查真实浏览器截图；冻结新的 candidate3 snapshot；保持 gpt-5.5/high、2 并发、语料与 evaluator v2 不变，完整生成与匿名评审。基线沿用已完成的 26 次记录，明确它不是同期重新生成，缓存与服务时段差异继续作为限制。新候选绝不混用前轮最佳产物。结果不达质量门槛时保存失败与下一步，不声称已经可以发布。
