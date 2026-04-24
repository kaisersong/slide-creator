# 2026-04-25 Style Reference 收口方案

## 目标

这轮的目标不是继续手工修某一份输出物，而是把 `slide-creator` 的 style reference 体系收口到可持续状态。

本次收口分三层：

1. **Reference 完整性基线**
   所有 preset 的参考文件都必须通过 `tests/audit_style_consistency.py`，保证样式里真实出现的 class 已登记进 `Required CSS Classes` 或 `Allowed Components`。
2. **重点 preset 深修**
   只对高频、高复杂度、或已出过事故的 preset 做 Swiss Modern 级别的深修，包括 user-content 路由、canonical export contract、token 约束、`data-export-role` 等。
3. **生成入口硬阻断**
   `validate` 不能只作为人工检查工具，必须接回生成流程，失败时阻断或触发自动重生。

## 现状判断

- 目前全量审计显示，只有 `swiss-modern` 已完全通过。
- 其余 preset 还有大量“参考文件定义不完整”的债务，当前规模为 `229` 个缺项，分布在 `21` 个文件中。
- 这些问题里，大部分不是视觉设计错误，而是 **reference 文档没有把已存在的 CSS/组件列完整**。
- 因此不能把所有风格都按 Swiss Modern 的强度重做一遍；正确策略是：
  - **先机械收口所有 preset**
  - **再重点深修少数高风险 preset**

## 执行顺序

### Phase 1: 全量 Mechanical Audit 收口

目标：把所有 preset 拉到“reference 文件完整、可审计、可维护”的基线。

动作：

- 为 `tests/audit_style_consistency.py` 增加 `--fix` 能力
- 统一把漏登记的 class 自动补入 `Allowed Components`
- 对 `Allowed Components` 不存在的 reference 自动创建该区块
- 保持幂等，重复执行不能持续改写文件
- 补测试，锁住 autofix 行为

完成标准：

- `python3 tests/audit_style_consistency.py` 全量通过
- `python3 tests/audit_style_consistency.py --fix` 再次执行无 diff

### Phase 2: 重点 Preset 深修

目标：避免 Swiss Modern 之外的高复杂度风格继续出现“审计过了，但生成很差”的问题。

优先级：

1. `enterprise-dark`
2. `data-story`
3. `chinese-chan`
4. `glassmorphism`

每个深修 preset 必须补齐：

- `user-content` 路由建议
- canonical export contract
- token 命名约束
- `data-export-role` 约束
- 关键反模式说明

完成标准：

- 单 preset 审计通过
- 严格校验通过
- 至少一份真实样本不会退化成连续重复布局

### Phase 3: 生成入口硬阻断

目标：不再依赖人工看结果判断好坏。

动作：

- 把 `tests/validate.py --strict` 接进 `--generate`
- 将失败分成两类：
  - hard fail：token / contract / missing required blocks / CSS vars 未定义
  - soft fail：visual variety 警告等可进入自动重试
- 输出明确失败原因，避免“生成成功但质量失控”

完成标准：

- 生成流程默认执行 strict validate
- 严重失败时不落盘，或落盘后标记为失败产物并停止返回“成功”

## 风险控制

- Phase 1 只做 **reference 清账**，不改每个 preset 的视觉设计和生成路由，避免大范围行为漂移。
- 自动补齐的内容统一进 `Allowed Components`，不假装所有 class 都属于“签名必须元素”。
- 深修与机械清账分离，避免在一次提交里同时引入结构变化和审计变化。

## 本轮立即执行

本轮先完成 Phase 1：

1. 给审计脚本加 `--fix`
2. 批量补齐所有 reference 缺项
3. 跑全量审计验证
4. 同步到 `/Users/song/projects/genppt`

Phase 2 和 Phase 3 作为下一轮连续推进项，不在本轮里混做。
