---
name: kai-slide-creator
description: 生成HTML演示文稿/幻灯片 — 21 种风格模版，播放/演讲者模式。适用于路演、产品发布、技术分享、方案宣讲等场景。
version: 2.23.1
metadata: {"openclaw":{"emoji":"🎞","os":["darwin","linux","windows"],"homepage":"https://github.com/kaisersong/slide-creator","requires":{"bins":["python3"]},"install":[]}}
---

# kai-slide-creator

生成零依赖 HTML 演示文稿，纯浏览器运行。主路径是 IR-first：`user prompt → BRIEF.json → HTML → validate`。

## 安装

**Claude Code:** 告诉 Claude「安装 https://github.com/kaisersong/slide-creator」  
**OpenClaw:** `clawhub install kai-slide-creator`

## 使用方式

```bash
/slide-creator --plan [prompt]       # 生成 BRIEF.json（IR）
/slide-creator --generate            # 从 BRIEF.json 生成 HTML
/slide-creator --review [file.html]  # 17 项检查点自动优化
/slide-creator                       # 交互式创建（先看风格预览）
```

**规划深度：**
- `自动` (Auto) — 快速出稿，约 3-6 分钟
- `精修` (Polish) — 深度规划，约 8-15 分钟，自动执行 Review

## 命令路由

`自动` (Auto) — 快速出稿 | `精修` (Polish) — 深度规划，自动执行 Review

| 命令 | 加载内容 | 行为 |
|------|----------|------|
| `--plan [prompt]` | `references/brief-template.json` | 创建 `BRIEF.json`；仅在用户明确要求时额外派生 `PLANNING.md` |
| `--generate` | SKILL.md + 风格文件 + composition 源 + `references/title-quality.md` + `references/html-template.md` + `references/js-engine.md` + `references/base-css.md` + `references/impeccable-anti-patterns.md` | 从 `BRIEF.json` 生成 HTML，并执行写入前门禁 |
| `--review [file.html]` | `references/review-checklist.md` + 目标 HTML | 执行 17 项检查点 → 确认窗口 → 修复/报告 |
| 无 flag (交互式) | `references/workflow.md` + 其他按需 | 遵循 Phase 0-5 |
| 直接给内容 + 风格 | 同 `--generate` | 立即生成，执行同一套写入前门禁 |

**渐进式披露：** 每个命令只加载所需文件。`--plan` 只提炼 IR，不接触 CSS。

### deck_type 路由

| deck_type | page_count | composition 源 | 使用场景 |
|-----------|-----------|---------------|---------|
| `product-demo` | 8 | `references/composition-8.md` | slide-creator 自身介绍 demo |
| `user-content` | 12 | `references/composition-guide.md` | 用户内容（路演/发布/报告） |

**决策逻辑：**
- `--plan` 在 `BRIEF.json` 中写入 `deck_type`、`page_count`、`page_roles`
- 直接给内容 + 风格：介绍 slide-creator → `product-demo`；其他 → `user-content`
- `--generate` 读取 `BRIEF.json` 中的 `deck_type`

## 核心规则（按优先级）

1. **风格强制**
   所有颜色、字体、组件、背景、动画、图表色、signature elements 都**必须且只能**来自选中的风格文件。模板里的 `[from style file]` 和示例值只是占位，禁止直接使用。  
   **Swiss Modern 额外要求 canonical export path**：面板保持 `.slide` direct child，token 保持 `--bg/--text/--red`，使用 canonical 类（`.left-panel/.right-panel/.stat-row/.cta-block`），并写入 `data-export-role`；不得生成 `.left-col/.right-col` 或 `--bg-primary/--accent` 这类兼容别名。

2. **叙事弧线**
   先锁 `deck_type`，再锁 composition route。`product-demo` 必须走 8 页结构，`user-content` 必须走 12 页结构。每页都要有明确 page role、不同布局意图和足够的信息推进，不能先拼播放/编辑壳子，再回头补叙事。

3. **标题质量**
   标题必须是断言式，禁止 Overview / Introduction / Summary / 结论 / 概览 这类通用标签。多行标题必须平衡，不能出现孤儿行、塌陷中间行或靠过窄 measure 硬挤换行。规则和示例只看 `references/title-quality.md`。

4. **运行时与壳子基线**
   非 Blue Sky 风格必须走共享壳子：`body[data-preset]`、`scroll-snap`、`SlidePresentation`、`PresentMode`、首屏 `.visible` 修复、`data-notes`、shell markers。Blue Sky 是唯一允许保留自身 `#stage/#track` 架构的 preset。

5. **可降级功能**
   播放模式、编辑模式、水印都默认开启，但优先级低于风格、叙事和标题。  
   - 播放模式：默认开启  
   - 编辑模式：默认开启，**可省略编辑模式**，尤其在用户明确说不要或 existing HTML/导入场景受约束时  
   - 水印：默认保留，但必须是 JS 注入到最后一页，`position: absolute`，禁止 `position: fixed`

详见 `references/html-template.md`。生成任何 HTML 前必读此文件。

## Pre-Write Validation Pipeline（写入前门禁）

组装完整 HTML 后，先写入临时文件，再运行：

```bash
python3 tests/validate.py "$TMP_HTML" --strict
```

任一失败都算生成失败，必须修复或重生直到通过。

**核心门禁顺序：**

1. **风格强制 / canonical export**
   选中风格的 Signature Elements、Typography、Components、Background 必须完整注入；不得遗漏 checklist 项。Blue Sky 例外：使用 `blue-sky-starter.html` 基底。

2. **叙事弧线 / composition route**
   `deck_type`、页数、page roles 必须完整；连续两页不得使用相同布局；每页至少使用 2-3 种组件类型，不得只用 `.g` + `.bl` 堆砌。

3. **标题质量**
   标题必须断言式；禁止通用标签；多行标题不得有孤儿行、塌陷中间行或浏览器自然换行失衡。规则只认 `references/title-quality.md`。

4. **架构隔离 / runtime**
   非 Blue Sky 风格必须使用 `scroll-snap-type: y mandatory` + `SlidePresentation`。`#stage/#track`/`translateX` 只允许 Blue Sky。

5. **Preset metadata / shell markers**
   `body[data-preset]` 必须存在且非占位；写出 `id="slide-N"`、`#brand-mark`、`.nav-dots`、`.progress-bar`、`.slide-num-label`、`data-export-role`。

6. **对比度 / token 使用**
   文字对比必须正确；浅底不用浅字，深底不用深字；优先用风格 token，不要发明局部颜色。

7. **字体 / CJK**
   Google Fonts 合并为单一链接；`<style>` 开头要有 `body { background-color: ... }` 回退；CJK 页面追加对应 `Noto Sans SC/JP/KR`。

8. **CSS 工程**
   布局、背景、间距通过 CSS 选择器定义；inline `style=""` ≤ 5 处，目标 0。

9. **低级错误与模板完整性**
   禁止 U+FE0F。Blue Sky 模板路径还要检查 REQUIRED BLOCK、`@keyframes`、以及 `go()` 返回 boolean。

> 更多视觉和内容规则在 `--review` / Phase 3.5 Review 中执行。完整反模式映射表见 `references/impeccable-anti-patterns.md`。

## 风格参考

只读取已选风格的文件；完整 preset 列表见 `references/style-index.md`。  
自定义主题路径：`themes/<name>/reference.md`

- 风格选择器：`references/style-index.md`
- 视口与共享 CSS：`references/base-css.md`
- 设计质量基线：`references/design-quality.md`
- 标题规则：`references/title-quality.md`
- 反模式：`references/impeccable-anti-patterns.md`

## 面向 AI 智能体

```bash
/slide-creator 为 [主题] 制作路演 deck
/slide-creator --plan "Acme v2 产品发布"
/slide-creator --generate
/kai-html-export presentation.html
/kai-html-export --mode native presentation.html
```

- `BRIEF.json` 已存在 → 直接读取并作为真相源
- 只有在用户明确要求人工审阅时才派生 `PLANNING.md`
- 现有 HTML 增强遵循 `references/workflow.md` 的 Enhancement Mode

## 相关技能

- **kai-html-export** — 导出 PPT（图片模式或 Native 模式）
