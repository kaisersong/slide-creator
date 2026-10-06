# 真实端到端 token / 耗时 / 效果评测

本目录保存固定输入；运行证据位于本地 `evals/artifacts/token-efficiency/`。
方案见 `docs/design/2026-10-06-token-efficiency-plan.md`。

## 运行

使用安装了 beautifulsoup4、Pillow、Playwright、jsonschema、pytest 的 Python；Chrome 用于浏览器检查。
`codex exec` 必须登录且支持 manifest 中的模型。不得用字节估算或 fixture usage 代替真实计量。

```sh
python scripts/token-efficiency-eval.py freeze --run-dir evals/artifacts/token-efficiency/RUN --arm baseline --revision BASE_SHA
python scripts/token-efficiency-eval.py run --run-dir evals/artifacts/token-efficiency/RUN --arm baseline
# 基线完成后才修改产品，再冻结候选。这里包含新文件，须先在 .gitignore 中允许它们。
python scripts/token-efficiency-eval.py freeze --run-dir evals/artifacts/token-efficiency/RUN --arm candidate
python scripts/token-efficiency-eval.py run --run-dir evals/artifacts/token-efficiency/RUN --arm candidate
python scripts/token-efficiency-eval.py compare --run-dir evals/artifacts/token-efficiency/RUN
```

每次生成在独立 runtime 副本中执行。原始 trace、stderr、prompt、answer、metrics 和产物全部保留。
程序 QA 使用同一个 evaluator，审阅器只看到匿名截图、文稿、来源和要求，看不到臂名或 skill 改动。
固定任务禁止委派，不读取前次结果。每个正向案例默认 3 次，负向路由各 1 次。

## 口径

- `generation.wall_ms`：完整 CLI 启动到退出，包含读文件、模型推理、工具、修复和 renderer。
- `input_tokens` 包含缓存输入；`uncached_input_tokens = input_tokens - cached_input_tokens`。缓存计数缺失时后者为 null。
- `total_tokens = input_tokens + output_tokens`；output 已含 reasoning 时不能再加 reasoning。
- `eval_wall_ms` 包含生成、程序 QA 和独立审阅；`eval_total_tokens` 另加审阅 usage。
- strict 或视觉失败是有效失败结果；usage/产物/审阅缺失是 incomplete。没有结果时不填 0。
- 首次启动的模型/认证/网络问题记录为环境失败，不能替代产品基线。
- 已有 result 可跳过；存在 workspace 而没有终态 receipt 时拒绝自动重放。先检查副作用，再用新的 run id。

## 语言评分

技术文稿采用 10 项 × 10 分的 STE-aligned 项目 rubric，目标 80/100。中文标记为适配，英文标记为标准规则对齐；完整词典、词性与词义符合度未验证，不能作标准认证结论。非技术文稿评分为 null。

## 持续优化

冻结 manifest 和版本后每轮都跑两臂。对照可复用此前已冻结基线，但模型、运行面或 evaluator 变化时重跑两臂。失败样本进入下一轮固定用例，报告不得删去。扩展用户真实文稿时先去除私密信息并固定事实依据；不能把当前 8 类任务的结果称为全部任务覆盖。

后续候选可用 `--arm candidate2` 冻结/运行，使用 `--candidate-arm candidate2` 对照。`compare` 保存完整报告，并在采用 gate 失败或证据缺失时返回 exit code 1，防止 CI 将低 token 但质量回退的候选当作通过。评测器修复只需对受影响产物用 `reassess --case-id <id> --force-reassess` 重查；原生成收据和旧评分保留，不自动重放生成。

## 用户指定风格的独立输入

支持 `--requested-preset` 的 runtime 版本：每个正向 workspace 在模型启动前由调用方按 manifest 写入 `SLIDE_REQUEST.json`（version=1，preset=用户指定值），并在 workspace 外保留 `requested-style.json` 收据。此项是明确请求的持久输入，模型不能按 BRIEF 改写。`main.py --generate` 自动核对；不同风格拒绝写出，模型应修正 BRIEF 后重试。QA 同时保留原 preset 检查并核对请求文件未被删除或改写；不降低原有几何、事实、质量或采用阈值。历史 runtime 不支持此输入时保持原协议，不能把新文件约束追溯成旧臂已验证的能力。
