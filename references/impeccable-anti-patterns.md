# Impeccable Anti-Patterns (Slide-Adapted)

源自 https://impeccable.style/anti-patterns/ 的 37 个视觉反模式，经过筛选后保留适用于**幻灯片演示**的子集。不适用于幻灯片的反模式（如行宽 >75 字符、timeline 日期验证）已排除。

> **用法：** 在 Phase 3 Step 7 Pre-write Validation 中，加载此文件作为视觉硬规则参考。与 `design-quality.md` 配合使用。

---

## 检测方式分类

| 方式 | 说明 | 适用场景 |
|------|------|---------|
| **CLI（确定性）** | 正则/字符串搜索可检测 | 纯 CSS/HTML 违规 |
| **Browser（需布局）** | 需要渲染后判断 | 重叠、溢出、视口问题 |
| **LLM-only（需 AI 判断）** | 需要语义理解 | 标题质量、视觉噪音 |

---

## Visual Details（视觉细节）

### 1. 嵌套卡片（Nested Cards）— CLI
- **检测：** 幻灯片内出现 `.card .card` 或 `.glass-card .glass-card` 等嵌套选择器
- **修复：** 扁平化层级——用缩进、子列表、相邻区块替代
- **slide-creator 已有：** HARD RULES 中无直接对应，design-quality.md §8 Nested Grid Fit 相关

### 2. 全局居中文本（Centered Text Everywhere）— CLI
- **检测：** `text-align: center` 出现在 `.slide-content`、`.body-text`、`.bullet-list` 等容器上
- **修复：** 正文左对齐；仅标题页/大字强调页/引用页居中
- **slide-creator 已有：** 无直接对应

### 3. Glassmorphism 滥用（Glassmorphism as Decoration）— CLI
- **检测：** `backdrop-filter: blur()` 出现在 >2 张幻灯片上
- **修复：** 仅保留 1-2 张幻灯片使用毛玻璃效果；其余用纯色或微 tint 背景
- **slide-creator 已有：** design-quality.md §7 Anti-Slop Patterns 已覆盖

### 4. 过度圆角（Uniform Border Radius）— CLI
- **检测：** 所有卡片/按钮/徽章使用相同的 `border-radius`（如全是 `12px`）
- **修复：** 混合圆角：尖锐（2px）用于数据元素、柔和（8px）用于内容卡片、胶囊（999px）用于标签
- **slide-creator 已有：** design-quality.md §7 Anti-Slop Patterns 已覆盖

### 5. 图标瓦片堆叠（Icon Tile Above Heading）— LLM
- **检测：** 幻灯片标题上方有独立的圆角方形图标容器（无功能性，纯装饰）
- **修复：** 将图标内联到标题中，或完全移除
- **slide-creator 已有：** 无直接对应

---

## Typography（排版）

### 6. 正文行距过大（Wide Letter-Spacing on Body）— CLI
- **检测：** 非标题元素的 `letter-spacing` > `0.05em`
- **修复：** 正文 letter-spacing 不得超过 0.05em；负值可用于标题（-0.03em）和副标题（-0.02em）
- **slide-creator 已有：** 无直接对应

### 7. 全大写正文（All-Caps Body Text）— CLI
- **检测：** `text-transform: uppercase` 出现在正文段落/列表项上
- **修复：** 正文保持正常大小写；all-caps 仅用于小标签或芯片
- **slide-creator 已有：** 无直接对应

### 8. 等宽字体滥用（Monospace as Technical Shorthand）— CLI
- **检测：** `font-family: monospace` / `var(--font-mono)` 出现在非代码块的正文/标题中
- **修复：** 正文使用无衬线字体；等宽字体仅保留给实际代码块
- **slide-creator 已有：** 无直接对应

### 9. 标题换行 ≥4 行（Title Wrapping Excessively）— CLI
- **检测：** 幻灯片 `<h2>` / `.slide-title` 换行 ≥4 行
- **修复：** 缩短标题 → 调整布局 → 加大字号
- **slide-creator 已有：** HARD RULES Rule 3 已覆盖

---

## Color & Contrast（颜色与对比度）

### 10. 纯黑背景（#000 Background）— CLI
- **检测：** CSS 中出现 `background: #000` 或 `background: #000000`
- **修复：** 使用 `#111` 或 `#18181B` 替代——纯黑太刺眼
- **slide-creator 已有：** 无直接对应

### 11. 强调色泛滥（Accent Color Flood）— CLI
- **检测：** `var(--accent)` / `var(--primary)` 同时用于 >3 种元素类型（标题 + 卡片边框 + 图表 + 徽章 + 下划线）
- **修复：** 限制为 1-2 个精确命中；遵循 90/8/2 色彩律
- **slide-creator 已有：** HARD RULES Rule 7 / design-quality.md §3 已覆盖

### 12. 灰色文字在彩色背景上（Gray Text on Colored Background）— CLI
- **检测：** `color: #888` / `#999` / `var(--text-secondary)` 出现在非白色背景上
- **修复：** 加深文字颜色或减淡背景色，确保 WCAG AA 对比度
- **slide-creator 已有：** 无直接对应

---

## Motion（动画）

### 13. Bounce / Elastic Easing — CLI
- **检测：** CSS 中使用 `cubic-bezier` 的 overshoot 值（如 y > 1.0）或 `ease-out-back`、`ease-in-out-back`、`bounce`
- **修复：** 使用 `cubic-bezier(0.16, 1, 0.3, 1)`（ease-out-expo）或 `cubic-bezier(0.22, 1, 0.36, 1)`
- **slide-creator 已有：** html-template.md 中 `--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1)` 已定义，但无反向检测

---

## Interaction（交互）

### 14. 移动端隐藏关键功能（Mobile Hidden Functionality）— CLI
- **检测：** `@media (max-width: 768px)` 规则中 `display: none` 隐藏了 `.slide` 内容、`.nav-dots`、`.edit-toggle`
- **修复：** 不在移动端隐藏核心交互功能；可以调整布局但不应消失
- **slide-creator 已有：** 无直接对应

---

## General Quality（通用质量）

### 15. 拥挤内边距（Cramped Padding）— CLI
- **检测：** 卡片/容器的 `padding` < `0.75rem`（数据元素）或 `0.9rem`（内容卡片）
- **修复：** 增加内边距；拥挤的 padding 让幻灯片显得廉价
- **slide-creator 已有：** 无直接对应

### 16. 对齐不一致（Inconsistent Alignment）— CLI
- **检测：** 同一幻灯片中同时存在 `text-align: left` 和 `text-align: center` 的正文元素
- **修复：** 统一对齐方向；仅特殊布局（如居中大数字）可例外
- **slide-creator 已有：** 无直接对应

### 17. 渐变文字无降级（Gradient Text Without Fallback）— CLI
- **检测：** `background: linear-gradient(...) ; -webkit-background-clip: text` 但没有 `color` 降级后备
- **修复：** 添加 `color: var(--accent)` 作为不支持渐变浏览器的后备
- **slide-creator 已有：** 无直接对应

---

## 排除项（不适用于幻灯片）

| 反模式 | 排除原因 |
|--------|---------|
| Line width >75 chars | 幻灯片是全屏展示，行宽由布局决定 |
| Justified text | 幻灯片正文默认左对齐，无此问题 |
| Nested cards 在报告中 | 已适配为 slide-creator 的嵌套网格检测 |
| Timeline 日期验证 | 幻灯片时间线使用 SVG/inline，不是 report-creator 的 :::timeline 组件 |

---

## Pre-Write Validation 集成

在 Phase 3 Step 7 中加入以下新增检测项（与现有 8 项并行）：

| # | 检测 | 正则/搜索模式 | 修复动作 |
|---|------|-------------|---------|
| 9 | 嵌套卡片 | `\.(?:card|glass-card|slide-card)\s*\.\1` 或 HTML 中 `<div class="...card..."` 内再嵌套 `<div class="...card..."` | 扁平化层级 |
| 10 | 全局居中 | `text-align:\s*center` 出现在非 `.title` / `.stat` / `.quote` 容器上 | 改为 left-align |
| 11 | letter-spacing >0.05em | `letter-spacing:\s*(?:0\.[1-9][0-9]*|[1-9])` | 缩减到 ≤0.05em |
| 12 | 纯黑背景 | `#000000` 或 `#000[` 或 `#000;` 或 `#000}` | 替换为 #111 |
| 13 | gray on colored bg | `color:\s*(?:#[89]99|var\(--text-secondary)` 在非 `#fff` / `var(--bg)` 背景上 | 加深文字 |
| 14 | bounce easing | `ease.*back|bounce|cubic-bezier\([^)]*[2-9]\.[0-9][^)]*\)` | 替换为 ease-out-expo |
| 15 | mobile hidden | `@media.*max-width.*768.*display:\s*none` 作用于 `.slide` / `.nav` / `.edit` | 改为调整布局 |
| 16 | cramped padding | `padding:\s*0\.[1-5]rem` | 增加到 ≥0.75rem |
| 17 | monospace body | `font-family.*monospace` 非 `<pre>`/`<code>` 内 | 改为 system-ui |
| 18 | all-caps body | `text-transform:\s*uppercase` 非标签/芯片元素 | 移除 |
| 19 | icon tile | 独立的圆角方形 `<div>` 含图标 + 紧随其后的 `<h2>` | 内联到标题 |
| 20 | inconsistent align | 同一 `<section class="slide">` 内同时出现 left + center 的 text-align | 统一对齐 |
| 21 | gradient no fallback | `-webkit-background-clip:\s*text` 前无 `color:` 声明 | 添加 color 降级 |
