# 用户指定风格约束修复与完整复测

日期：2026-10-07；代码 `f82e16617936585b84993ebc84d17f855e37fd78`；隔离分支 codex/slide-token-eval。

原失败：consulting-strategy-zh rep-1 请求 Strategy Consulting，模型在 BRIEF 写成 Swiss Modern。旧 CLI 只信任 BRIEF，因此即使文稿、strict和几何通过，最终风格仍选错。

修复：本次用户请求在生成前独立存为 SLIDE_REQUEST.json（version=1、preset=用户选择），生成器默认核对该文件，也支持 --requested-preset 和 --request-file。不匹配时在 renderer 和写文件前返回 PRESET MISMATCH，要求修正 BRIEF 后重试。请求文件优先，冲突参数不能覆盖；已有HTML与packet保持不变。按实际reference归一化内置别名、自定义theme别名及路径，未指定请求时保留旧流程。上下文抽取入口同样核对。

这是调用方已正确提供用户选择时的生成约束；不声称模型从任意自然语言抽取请求绝不会出错。交互skill要求先保存用户原始选择、不能按BRIEF改写；模型E2E由调用方在模型启动前从冻结manifest写入独立请求，并在workspace外保留收据。QA验证未删除或改写，保留原有preset、strict、几何、事实和质量门槛。

受控复现：直接使用candidate14失败的原始BRIEF，新CLI拒绝写出；只改BRIEF风格为用户请求后，原 strict/两视口两模式几何/页数/事实/风格检查全部通过。这不是新模型E2E，不填虚假model token。

回归：2878 passed、114 skipped、7 deselected，零失败。新增7项测试涵盖错误风格、自动请求文件、冲突覆盖、context入口、alias/custom路径、畸形/缺失请求及已有文件保护。

## 完整端到端评测

同一冻结manifest，8正向任务各3次 + 2负向路由各1次，gpt-5.5/high、2并发。不是只重跑失败样本，没有替换旧收据或从各臂选最好样本。沿用原独立来源评审和两视口×两模式浏览器QA，新增请求文件一致性检查为硬门槛。

全部26次完成，正式通过 26/26；24份正向稿用户指定风格检查 24/24，请求文件一致性 24/24。咨询案例3次的结果单列如下。

| 任务 | 通过 | 风格 | 请求一致 | 质量 |
|---|---|---|---|---:|
| consulting rep-1 | True | Strategy Consulting | True | 82 |
| consulting rep-2 | True | Strategy Consulting | True | 86 |
| consulting rep-3 | True | Strategy Consulting | True | 86 |

| 指标 | 初始基线 | 版本14 | 修复版15 |
|---|---:|---:|---:|
| 生成耗时中位数（秒） | 223.53 | 145.74 | 141.74 |
| 生成token中位数（含缓存输入） | 1,415,463.00 | 300,599.00 | 317,447.00 |
| 质量均分 | 77.88 | 87.96 | 88.54 |
| 评测全链路耗时中位数（秒） | 269.41 | 190.87 | 180.51 |
| 评测全链路token中位数 | 1,442,213.50 | 326,472.50 | 343,145.50 |
| 技术语言均分（观察项） | 78.33 | 88.13 | 88.47 |

相对初始基线：生成token中位数 -77.57%，耗时 -36.59%，质量配对均值 +10.67 分。相对历史通过版本5：token -0.65%，耗时 +2.29%，质量 +0.67 分。服务/缓存时段差异仍是限制，不把总token比例当付费比例。

自动维护采用门槛：通过。失败项：[]。修复风格选择不等于所有质量问题已消失，保留每次来源评审、慢样本和失败，不能把受控修复稿混入正式通过率。

人工来源复核仍发现：data-kpi-en rep-2标题Two Reviews Gate Expansion把客户数改写为审查数；consulting rep-3标题成本恶化即停省略满意度未改善的并列条件。正文保留原事实，但标题语义仍越过来源。这次只确认指定风格执行修复，不把自动通过当作全部内容质量通过，默认采用仍暂缓；评分、原稿及请求文件均不回写。详见review-disposition.candidate15.json。

累计完整生成/路由评测由286增至312次，另保留candidate9两个未评分生成的中止成本。旧版14的25/26结果不改写。模型未遵守来源、标题或视觉节奏的问题继续按真实结果记录。

## 演示

[最新完整原始模型稿](http://127.0.0.1:8796/preview.html)，每案默认rep-1，另外两次均保留；[咨询rep-1完整稿](http://127.0.0.1:8796/candidate15/consulting-strategy-zh/rep-1/workspace/output/deck.html)。本地HTML支持F5播放、方向键翻页。

原始结果在 evals/artifacts/token-efficiency/2026-10-06-p1-formal/candidate15/；受控复现 controls/candidate15-request-guard/。紧凑收据在 evals/token-efficiency/results/2026-10-06/。全部代码仅在worktree，未合并发布或替换安装版。


跨 Skill 复用参考：[Skill 优化方法论 v1.0](../methodology/skill-optimization/README.md)。方法文档保留本案例的人工来源复核边界；后续 bug 依其版本与回归规则更新。
