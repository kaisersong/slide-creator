# Chinese Chan Contract Fix — 2026-04-27

## 背景

用户反馈 `Chinese Chan` 生成物与 demo 风格差异大，尤其表现为：

- 内容页标题过大，连续使用 hero 级标题组件
- 页面缺少 `data-export-role`
- 生成物虽然带 `Chinese Chan` 壳子，但没有走 formal canonical route

源文件：

- `/Users/song/Downloads/life-meaning (2).html`

## Root Cause

1. `Chinese Chan` 的正式 style reference 与历史 demo 长期漂移：
   - reference 的 `Zen Split` 写成 `.zen-title`
   - 实际更合适的内容页 headline 组件应为 `.zen-h2`
2. `Chinese Chan` 缺少 deterministic low-context renderer，生成路径更依赖 prose reference，导致漂移放大。
3. validator 之前只对 `data-export-role` 缺失做 warning，没有把 canonical route 漂移 fail closed。
4. layout 去重逻辑发生在 usage-rules 解析之后，可能把不该居中的内容页抬成 `zen_center`。

## 修复点

### Formal Contract

- 更新 [references/chinese-chan.md](/Users/song/projects/slide-creator/references/chinese-chan.md)
  - 新增 `.zen-h2`
  - 新增 `Zen Stat`
  - 明确 title component mapping
  - 明确 `zen_split / zen_stat` 不得直接复用 `.zen-title`

- 更新 [references/preset-usage-rules.json](/Users/song/projects/slide-creator/references/preset-usage-rules.json)
  - 新增 `Chinese Chan` machine-readable rules
  - 新增 `title_component_by_layout`
  - 新增 `layout_fallbacks`
  - 新增 `role_forbidden_layouts`

### Renderer

- 更新 [scripts/low_context.py](/Users/song/projects/slide-creator/scripts/low_context.py)
  - 新增 `CHINESE_CHAN_ROLE_LAYOUTS`
  - 新增 `render_chinese_chan_html`
  - 新增 `zen_center / zen_split / zen_stat / zen_vertical` 渲染函数
  - 新增 `Chinese Chan` extra CSS
  - 修复 layout 去重后未再次应用 usage-rules 的问题

### Validator

- 更新 [scripts/validate_html.py](/Users/song/projects/slide-creator/scripts/validate_html.py)
  - `Chinese Chan` 缺少 `data-export-role` 改为 contract failure
  - 按 layout 校验 title component：
    - `zen_center -> .zen-title`
    - `zen_split -> .zen-h2`
    - `zen_stat -> .zen-h2`
    - `zen_vertical -> .zen-vertical-title`

### Tests

- 更新：
  - [tests/test_priority_preset_reference_contracts.py](/Users/song/projects/slide-creator/tests/test_priority_preset_reference_contracts.py)
  - [tests/test_validate_priority_preset_contracts.py](/Users/song/projects/slide-creator/tests/test_validate_priority_preset_contracts.py)
  - [tests/test_low_context_pipeline.py](/Users/song/projects/slide-creator/tests/test_low_context_pipeline.py)

## 标准流程重生成产物

输入工件：

- [源内容提炼](/Users/song/projects/slide-creator/plans/life-meaning-source.md)
- [BRIEF](/Users/song/projects/slide-creator/plans/life-meaning-chinese-chan-BRIEF.json)
- [Render packet](/Users/song/projects/slide-creator/plans/life-meaning-chinese-chan-packet.json)

输出：

- [重新生成 HTML](/Users/song/projects/slide-creator/demos/life-meaning-chinese-chan-regenerated-zh.html)

## 验证结果

- `python3 main.py --validate-brief --brief plans/life-meaning-chinese-chan-BRIEF.json`
  - `VALID`
- `python3 main.py --generate --brief plans/life-meaning-chinese-chan-BRIEF.json --output demos/life-meaning-chinese-chan-regenerated-zh.html --packet-out plans/life-meaning-chinese-chan-packet.json`
  - `PRESET: Chinese Chan`
  - `QUALITY TIER: tier1`
  - `RUNTIME PATH: shared-js-engine`
- `python3 scripts/validate_html.py demos/life-meaning-chinese-chan-regenerated-zh.html --strict`
  - `All strict checks passed`

## 当前结论

这次修复后，`Chinese Chan` 不再依赖 demo 作为隐式标准，而是有了正式的：

- style reference contract
- machine-readable usage rules
- deterministic renderer
- validator gate

后续再分析其他 supported preset 时，可以沿用同一套“reference -> usage rules -> renderer -> validator”收口路径。
