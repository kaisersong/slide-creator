# Slide Creator Review 功能设计

## Goal

为 slide-creator 增加内容层面的 Review 能力，帮助用户提升幻灯片基线质量：
- 在生成过程中实时检测问题，自动修复或提示用户确认
- Polish 模式默认执行 Review，Auto 模式跳过
- 用户可手动调用 `--review` 对任意 HTML 进行诊断修复

## Current Problems

### 1. 内容层面缺失检查

现有 `design-quality.md` 只覆盖视觉层面（密度、颜色、排版），缺少内容层面检查：
- 痛点前置、WIIFM量化承诺、视角翻转
- 结论先行、MECE原则、奥卡姆剃刀
- 认知负荷管理（3概念法则、注意力重置）
- 黑话降维翻译、张力对比结构

### 2. 用户输出质量基线不稳定

用户直接用 Auto 模式生成后，常见问题：
- 标题是名词短语而非判断句
- 主语是"我/本系统"而非"你"
- 缺少量化收益承诺
- 连续密集页无缓冲

### 3. 无独立诊断修复入口

用户生成后发现问题，无专门的诊断命令：
- 需手动逐页检查
- 不知道具体哪里有问题
- 缺少修复指导

## Design Decisions

### A. Review 作为 Phase 3.5，仅在 Polish 模式触发

在现有 Phase 3 Generate 后新增 Phase 3.5 Review：

| 模式 | Phase 3.5 行为 |
|---|---|
| Auto | 跳过，直接到 Phase 4 Delivery |
| Polish | 生成后进入确认窗口，16项检测 → 用户确认修复 → 输出HTML + 诊断报告 |
| `--review` | 直接进入，可对任意HTML进行诊断修复 |

### B. 16项 Checkpoints 分类处理

**可100%自动化检测（6项）**：

| Checkpoint | 检测方法 | 自动修复 |
|---|---|---|
| 视角翻转 | 扫描标题/正文主语，检测"我/本系统/本次分享" | Yes → 改为"你/你的" |
| 结论先行 | 检测标题是否为名词短语（无动词） | Yes → 生成建议标题 |
| 3概念法则 | 检测单页新概念数超过3个 | No → 提示拆分 |
| 禁止连续密集页 | 检测连续3页同布局类型 | No → 提示插入缓冲页 |
| 字号底线 | 检测正文字号过低 | No → 提示调整 |
| 眯眼测试 | 检测页面视觉焦点是否明确 | No → 提示重新分配权重 |

**AI给出判断建议（10项）**：

| Checkpoint | 检测方法 | 输出 |
|---|---|---|
| 痛点前置拦截 | 检测前2页是否有具体场景/截图 | "建议补充真实案例" |
| WIIFM量化承诺 | 检测前3页是否有量化数字 | "建议明确量化收益" |
| MECE原则 | 检测步骤分类是否重叠 | "步骤X和Y可能重叠，建议合并" |
| 奥卡姆剃刀 | 检测冗余信息 | "Slide X关联较弱，可考虑删除" |
| 10分钟注意力重置 | 检测是否有互动/案例环节 | "建议插入注意力重置点" |
| 张力对比结构 | 检测是否有对比（手工vs自动） | "建议增加对比结构" |
| 留白缓冲页 | 检测是否有视觉极简页 | "建议每5-6页插入呼吸页" |
| 黑话降维翻译 | 检测术语是否有类比解释 | "建议添加类比解释" |
| 图像降噪 | 检测图片是否有廉价元素 | "建议替换为专业图示" |
| 数据图表降噪 | 检测图表是否有网格线/3D | "建议删除网格线" |

### C. Review 流程交互设计

```
Step 1: 执行16项检测
        ↓
Step 2: 分类检测结果
        - ✅ 通过项（绿色）
        - 🔧 可自动修复项（黄色）
        - ⚠️ 需用户确认项（橙色）
        - ❌ 需人工判断项（红色，AI建议）
        ↓
Step 3: 展示确认窗口（AskUserQuestion）
        - 选项：[全部自动修复] / [逐项确认] / [跳过Review直接输出]
        ↓
Step 4a: 全部自动修复
        → 执行6项自动修复 → 输出HTML → 生成诊断报告
        ↓
Step 4b: 逐项确认
        → 对每项展示修复建议 → 用户选择 [修复]/[跳过]/[保持原样]
        → 输出HTML → 生成诊断报告
        ↓
Step 5: 输出诊断报告
        - 通过项数 / 总项数
        - 已修复项清单
        - 未修复项清单（含AI建议）
        - "可再次运行 --review 继续优化"
```

### D. 诊断报告格式

```markdown
## Review 诊断报告

**幻灯片**: [filename].html
**检测结果**: 12/16 通过，4项待处理

### 已修复项 (3)
- ✅ 视角翻转：Slide 2-5 主语已改为"你"
- ✅ 结论先行：Slide 3 标题改为判断句
- ✅ 字号调整：Slide 6 正文已调整

### 未修复项 (1)
- ⚠️ 痛点前置：前2页未检测到具体场景
  - AI建议：建议在Slide 1补充真实用户痛点截图或案例

### 需人工判断项 (建议思考)
- 🔍 MECE原则：步骤2和步骤3可能重叠，请检查业务逻辑
- 🔍 10分钟注意力：连续10页干货，建议插入互动环节

---
可再次运行 `/slide-creator --review` 继续优化
```

### E. `--review` 独立命令

用户可对任意已生成的 HTML 调用 `--review`：

```
/slide-creator --review presentation.html
```

行为：
1. 读取目标 HTML
2. 执行16项检测
3. 逐项交互修复（用户选择修复/跳过/保持）
4. 输出修复后的 HTML
5. 生成诊断报告
6. 用户可继续 review

## Files To Change

### 新增文件

| 文件 | 内容 |
|---|---|
| `references/review-checklist.md` | 16项Checkpoints定义、检测规则、修复方法、AI建议模板 |
| `tests/test_review_checklist.py` | Review 功能测试 |

### 修改文件

| 文件 | 变更内容 |
|---|---|
| `SKILL.md` | 增加 `--review` 命令路由、Phase 3.5 说明 |
| `references/workflow.md` | 增加 Phase 3.5 Review 章节 |
| `references/planning-template.md` | 增加 Review Results 字段（Polish模式专用） |
| `references/design-quality.md` | 增加 L1 内容检查索引 |

### SKILL.md 命令路由表

| 命令 | What to load | What to do |
|---|---|---|
| `--plan [prompt]` | `references/planning-template.md` | Create PLANNING.md. Stop. |
| `--generate` | `html-template.md` + style + `design-quality.md` | Generate HTML, run L0 check. |
| `--review [file.html]` | `review-checklist.md` + target HTML | 16项检测 → 确认窗口 → 修复/报告. |
| No flag (interactive) | `workflow.md` + `review-checklist.md` (Polish) | Phase 0-5, Phase 3.5 only in Polish. |

## Validation Plan

1. 写 `references/review-checklist.md`，定义16项规则
2. 更新 `SKILL.md` 和 `workflow.md`，增加 Phase 3.5
3. 写 `tests/test_review_checklist.py`，测试 Review 触发和结果分类
4. 用 Intent Broker demo 验证 Polish 模式 Review 流程
5. 用已生成 HTML 验证 `--review` 命令

## Success Criteria

- Auto 模式不触发 Review，保持快速路径
- Polish 模式生成后自动进入 Review 确认窗口
- `--review` 可对任意 HTML 进行诊断修复
- 16项 Checkpoints 分类执行（自动修复 / AI建议）
- 诊断报告清晰展示通过/已修复/未修复/需人工判断项
- 用户可继续 review 继续优化