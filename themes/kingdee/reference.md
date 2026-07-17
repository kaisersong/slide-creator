# Kingdee 金蝶 — Style Reference
# 金蝶品牌风格参考文档

Professional, tech-forward, enterprise-grade. Inspired by Kingdee's brand identity — trustworthy blue tones, clean layouts, and authoritative typography. Designed for B2B solution presentations, product decks, and enterprise communications.

专业，科技感、企业级。灵感来自金蝶品牌识别——可信赖的蓝色调、清晰的布局、权威的排版。专为 B2B 解决方案演示、产品方案和企业通信设计。

---

## Colors / 配色

```css
/* Primary palette / 主色系 */
:root {
    /* 蓝色渐变 */
    --kd-gradient-start:  #2372EF;   /* 渐变起点 */
    --kd-gradient-mid:    #238EF7;   /* 渐变中点 */
    --kd-gradient-end:    #22AAFE;   /* 渐变终点 */

    /* 品牌蓝 */
    --kd-blue:            #2971EB;   /* 品牌主蓝色 */

    /* 标准白 */
    --bg-white:           #FFFFFF;   /* 白色背景 */

    /* 辅助色系 / Secondary Colors */
    --kd-skyblue:         #22AAFE;   /* 天蓝 */
    --kd-skyblue-light:   #00CCFE;   /* 天蓝浅 */
    --kd-teal:            #05C8C8;   /* 蓝绿 */
    --kd-purple:          #A06EFF;   /* 紫色 */
    --kd-yellow:          #FFB61A;   /* 黄色 */

    /* 中性色 / Neutral Colors */
    --kd-black:           #000000;   /* 黑色（标准） */
    --kd-blue-purple:     #28235F;   /* 蓝紫 */
    --kd-gray-dark:       #3B3838;   /* 深灰 */
    --kd-gray:            #BFBFBF;   /* 灰色 */
    --kd-light-blue:      #E7F1FF;   /* 浅蓝 */

    /* 文字色（保持兼容） */
    --text-primary:       #1A1A1A;   /* 主要文字 */
    --text-secondary:     #666666;   /* 次要文字 */
    --text-on-blue:       #FFFFFF;   /* 蓝底上的文字 */

    /* 功能色（保持兼容） */
    --divider:            #E5E5E5;   /* 分割线 */
    --card-bg:            #F5F7FA;   /* 卡片背景 */
}
```

### 色彩规范汇总表

| 类别 | 色名 | 色值 | 用途 |
|------|------|------|------|
| **主色系** | 蓝色渐变起点 | #2372EF | 渐变背景起点 |
| | 蓝色渐变中点 | #238EF7 | 渐变背景中点 |
| | 蓝色渐变终点 | #22AAFE | 渐变背景终点 |
| | 品牌蓝 | #2971EB | 主要品牌色、按钮、链接 |
| | 白色 | #FFFFFF | 背景、反白文字 |
| **辅助色系** | 天蓝 | #22AAFE | 强调、图标 |
| | 天蓝浅 | #00CCFE | 高亮、装饰 |
| | 蓝绿 | #05C8C8 | 成功状态、数据图表 |
| | 紫色 | #A06EFF | 特殊强调、创意元素 |
| | 黄色 | #FFB61A | 警告、重点标注 |
| **中性色** | 黑色 | #000000 | 纯黑文字、边框 |
| | 蓝紫 | #28235F | 深色背景、标题 |
| | 深灰 | #3B3838 | 正文文字 |
| | 灰色 | #BFBFBF | 禁用状态、次要边框 |
| | 浅蓝 | #E7F1FF | 浅色背景、卡片 |

---

## Typography / 字体规范

```css
/* 统一字体设置 */
/* 中文字体：微软雅黑 | 英文字体：微软雅黑 */

/* 大标题 / Main Title */
.kd-title {
    font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
    font-size: 24pt;          /* 24磅 */
    font-weight: 700;         /* 加粗 */
    color: var(--text-primary);
}

/* 副标题 / Subtitle */
.kd-subtitle {
    font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
    font-size: 16pt;          /* 16磅 */
    font-weight: 400;         /* 普通 */
    color: var(--text-secondary);
}

/* 段落标题 / Section Title */
.kd-section-title-primary {
    font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
    font-size: 22pt;          /* 22磅 - 一级段落标题 */
    font-weight: 700;         /* 加粗 */
    color: var(--text-primary);
}

.kd-section-title-secondary {
    font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
    font-size: 18pt;          /* 18磅 - 二级段落标题 */
    font-weight: 700;         /* 加粗 */
    color: var(--text-primary);
}

/* 正文 / Body Text */
.kd-body {
    font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
    font-size: 12pt;          /* 12磅 */
    font-weight: 400;         /* 普通 */
    line-height: 1.3;         /* 1.3倍行距 */
    color: var(--text-primary);
}

/* 标注文字 / Label Text */
.kd-label {
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
    font-size: 10pt;          /* 10磅 */
    font-weight: 400;         /* 普通 */
    line-height: 1.3;         /* 1.3倍行距 */
    color: var(--text-secondary);
}

/* 重点强调 / Emphasis */
.kd-emphasis {
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
    font-size: 20pt;          /* 20磅 */
    font-weight: 700;         /* 加粗 */
    color: var(--kd-blue);    /* 蓝色强调 */
}

.kd-emphasis-yellow {
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
    font-size: 20pt;          /* 20磅 */
    font-weight: 700;         /* 加粗 */
    color: #F59E0B;           /* 黄色强调 */
}

/* 蓝色背景页的文字 / Text on blue background */
.kd-text-inverse {
    color: var(--text-on-blue);
}
```

### 字体规范汇总表

| 类型 | 字号 | 字重 | 行距 | 颜色 |
|------|------|------|------|------|
| 大标题 | 24磅 | 加粗 | - | 主色 #1A1A1A |
| 副标题 | 16磅 | 普通 | - | 次要色 #666666 |
| 段落标题(一级) | 22磅 | 加粗 | - | 主色 #1A1A1A |
| 段落标题(二级) | 18磅 | 加粗 | - | 主色 #1A1A1A |
| 正文 | 12磅 | 普通 | 1.3倍 | 主色 #1A1A1A |
| 标注文字 | 10磅 | 普通 | 1.3倍 | 次要色 #666666 |
| 重点强调(蓝) | 20磅 | 加粗 | - | 品牌蓝 #0052D9 |
| 重点强调(黄) | 20磅 | 加粗 | - | 黄色 #F59E0B |

---

## Layout Types / 布局类型

Use canonical layout roles: `title_grid`, `contents_index`, `column_content`, `stat_block`, `geometric_diagram`, `data_table`, `pull_quote`, `toc`, `cta_close`.

### 1. 首页 / Title Slide

```css
.slide-title {
    background: var(--bg-white);
    display: flex;
    align-items: center;
    position: relative;
}

/* 左上角动态 Logo */
.kd-logo-left {
    position: absolute;
    top: 20px;
    left: 30px;
    height: 96px;
    z-index: 10;
}

/* 全屏背景图 - homepage.png 满铺整个页面 */
.kd-hero-image {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
}

/* 主标题区域 - 页面居中 */
.title-content {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    z-index: 2;
    width: 100%;
    padding: 0 60px;
}

/* 主标题 - 白色 54pt */
.title-main {
    font-size: 54pt;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1.2;
    margin-bottom: 20px;
}

/* 副标题 - 白色半透明 */
.title-sub {
    font-size: clamp(14pt, 2vw, 18pt);
    font-weight: 400;
    color: rgba(255,255,255,0.85);
    line-height: 1.6;
}

/* 首页左下角信息区域 */
.slide-title-footer {
    position: absolute;
    left: 60px;
    bottom: 60px;
    z-index: 10;
}

/* 撰稿人 - 白色 18pt 常规 */
.slide-title-author {
    font-size: 18pt;
    font-weight: 400;
    color: #FFFFFF;
    margin-bottom: 6px;
}

/* 撰稿部门 - 白色 18pt 加粗 */
.slide-title-dept {
    font-size: 18pt;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 6px;
}

/* 日期 - 白色 14pt */
.slide-title-time {
    font-size: 14pt;
    font-weight: 400;
    color: #FFFFFF;
}

/* 首页左下角版权信息 - 合并版：版权+保密同行 */
.slide-title .kd-copyright-white {
    color: #95B8F5;
}

/* 首页版权行内保密标识 - 深蓝 #1054B1 */
.slide-title .kd-copyright-white span {
    color: #1054B1;
}
```

### 首页布局示例

```html
<section class="slide slide-title">
    <img class="kd-hero-image" src="https://static.yunzhijia.com/home/download/png/homepage.png" alt="首页背景">
    <img class="kd-logo-left" src="https://static.yunzhijia.com/home/download/png/kingdee_ColorWhitedynamic.gif" alt="金蝶全彩动态Logo">
    <div class="title-content">
        <h1 class="title-main reveal">项目标题</h1>
        <p class="title-sub reveal">副标题（可选）</p>
    </div>
    <div class="slide-title-footer reveal">
        <div class="slide-title-author">KClaw</div>
        <div class="slide-title-dept">解决方案部</div>
        <div class="slide-title-time">2025.01.01</div>
    </div>
    <!-- 左下角版权+保密合并一行 -->
    <div class="kd-copyright-white">版权所有©金蝶国际软件集团有限公司 始创于1993  <span style="color:#1054B1;">④内部公开 请勿外传</span></div>
    <span class="slide-num-label">01</span>
</section>
```

### 2. 内容页 / Content Slide

```css
.slide-content {
    background: var(--bg-white);
    padding: 60px 80px;
    position: relative;
}

/* 右上角 Logo - 在 flex 容器中右对齐 */
.kd-logo-right {
    height: 35px;
}

/* 标题栏：flex 布局，标题左对齐，logo 右对齐，与目录页一致 */
.content-header {
    position: absolute;
    top: 30px;
    left: 80px;
    right: 60px;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    z-index: 10;
}

/* 内容页标题 - 24pt，与目录页一致 */
.content-title {
    font-size: 24pt;
    font-weight: 700;
    line-height: 1.0;
    color: var(--text-primary);
}

/* 副标题 - 16pt */
.content-subtitle {
    font-size: 16pt;
    font-weight: 400;
    color: var(--text-secondary);
    margin-top: 16px;
    margin-bottom: 30px;
}

/* 内容区域 */
.content-body {
    margin-top: 100px;
    font-size: 14pt;
    line-height: 1.8;
    color: var(--text-primary);
    max-width: 90%;
}

/* 列表样式 */
.content-body ul {
    list-style: none;
    padding-left: 0;
}

.content-body li {
    position: relative;
    padding-left: 24px;
    margin-bottom: 12px;
}

.content-body li::before {
    content: '';
    position: absolute;
    left: 0;
    top: 10px;
    width: 8px;
    height: 8px;
    background: var(--kd-blue);
    border-radius: 50%;
}

/* 右下角保密标识 - 灰色，所有内容页和目录页共用 */
.kd-confidential-gray {
    position: absolute;
    bottom: 20px;
    right: 90px;
    font-size: 9.4pt;
    color: #808080;
    letter-spacing: 1px;
    z-index: 10;
}

/* 左下角版权信息 - 灰色 */
.kd-copyright-gray {
    position: absolute;
    bottom: 20px;
    left: 60px;
    font-size: 9.4pt;
    color: #808080;
    letter-spacing: 1px;
    z-index: 10;
}
```

### 内容页布局示例

```html
<section class="slide slide-content">
    <div class="content-header">
        <div>
            <h2 class="content-title reveal">页面标题</h2>
            <p class="content-subtitle reveal">副标题（可选）</p>
        </div>
        <img class="kd-logo-right" src="https://static.yunzhijia.com/home/download/png/kingdee-blue.png" alt="金蝶AI Logo（蓝色）">
    </div>
    <div class="content-body">
        <ul>
            <li class="reveal">列表项 1</li>
            <li class="reveal">列表项 2</li>
        </ul>
        <div class="cols-2">
            <div class="kd-card reveal">
                <h3 class="kd-card-title">卡片标题</h3>
                <p class="kd-card-body">卡片内容</p>
            </div>
        </div>
    </div>
    <div class="kd-confidential-gray">④内部公开 请勿外传</div>
    <span class="slide-num-label">04</span>
</section>
```

### 内容适配布局指南

根据内容量选择合适的布局方式：

| 内容量 | 布局类 | 效果 | 适用场景 |
|--------|--------|------|----------|
| 较多（填满页面） | 无（默认） | 从顶部开始排列 | 多段落、多列表、复杂内容 |
| 中等（占1/2~2/3页面） | `.spread` | 内容均匀分布 | 3-5个卡片/列表项 |
| 较少（占1/3页面以下） | `.centered` | 内容垂直居中 | 单个高亮框、指标卡片组 |

**使用示例：**

```html
<!-- 内容较少时：垂直居中 -->
<div class="content-body centered">
    <div class="kd-highlight-box">...</div>
</div>

<!-- 内容中等时：弹性分布 -->
<div class="content-body spread">
    <div class="kd-feature-card">...</div>
    <div class="kd-feature-card">...</div>
</div>

<!-- 内容较多时：默认布局 -->
<div class="content-body">
    <p>...</p>
    <ul>...</ul>
    <div class="cols-2">...</div>
</div>
```

### 页码 / Slide Number

```css
/* 所有页面通用页码 */
.slide-num-label {
    position: absolute; bottom: 20px; right: 60px;
    font-size: 9pt; color: var(--kd-blue); font-weight: 400; z-index: 5;
}

/* 章节页页码白色 */
.slide-num-label.light {
    color: #FFFFFF;
}

/* 首页和尾页不显示页码 */
.slide-title .slide-num-label,
.slide-closing .slide-num-label {
    display: none;
}
```

| 页面类型 | 页码样式 | 说明 |
|---------|---------|------|
| 首页 | `slide-num-label`（隐藏） | CSS `display:none` |
| 目录页 | `slide-num-label`（蓝色） | 正常显示 |
| 章节页 | `slide-num-label light`（白色） | 加 `.light` class |
| 内容页 | `slide-num-label`（蓝色） | 正常显示 |
| 尾页 | `slide-num-label`（隐藏） | CSS `display:none` |

### 3. 目录页 / TOC Slide

```css
.slide-toc {
    background: var(--bg-white);
    padding: 60px;
    position: relative;
}

/* 右上角 Logo - 在 flex 容器中右对齐 */
.kd-logo-right-toc {
    height: 35px;
}

/* 全屏背景图 - kingdee_catalogue.png 平铺整个页面 */
.kd-toc-image {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 1;
}

/* 标题栏：flex 布局，标题左对齐，logo 右对齐 */
.toc-header {
    position: absolute;
    top: 30px;
    left: 80px;
    right: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    z-index: 10;
}

/* 目录标题 - 24磅，加粗 */
.toc-title {
    font-size: 24pt;
    font-weight: 700;
    line-height: 1.0;
    color: var(--text-primary);
    margin: 0;
}

/* 目录内容区域 */
.toc-content {
    position: absolute;
    left: 80px;
    right: 60px;
    top: 50%;
    transform: translateY(-50%);
    z-index: 5;
    padding: 0;
}

/* 目录项容器 */
.toc-item {
    display: flex;
    align-items: center;
    margin-bottom: 28px;
    position: relative;
}

/* 目录条数>9时的紧凑间距 */
.toc-item.compact {
    margin-bottom: 12px;
}

/* 目录序号 - 蓝色 54磅 */
.toc-number {
    font-size: 54pt;
    font-weight: 700;
    color: var(--kd-blue);
    margin-right: 24px;
    min-width: 100px;
    line-height: 1;
}

/* 目录条数>5时的序号样式 */
.toc-number.compact {
    font-size: 35pt;
    min-width: 70px;
    margin-right: 20px;
}

.toc-number.ultra-compact {
    font-size: 24pt;
    min-width: 50px;
    margin-right: 16px;
}

/* 目录内容 - 24磅加粗 */
.toc-text {
    font-size: 24pt;
    font-weight: 700;
    color: var(--text-primary);
    flex: 1;
}

/* 目录页码 - 蓝色加粗 */
.toc-page {
    font-size: 20pt;
    font-weight: 700;
    color: var(--kd-blue);
    position: absolute;
    right: 90px;
}

/* 目录页右下角保密标识 - 与内容页共用的灰色版 */
/* 使用 .kd-confidential-gray */
/* 目录页左下角版权 - 与内容页共用的灰色版 */
/* 使用 .kd-copyright-gray */
```

### 目录页布局示例

```html
<section class="slide slide-toc">
    <img class="kd-toc-image" src="https://static.yunzhijia.com/home/download/png/kingdee_catalogue.png" alt="目录背景">
    <div class="toc-header">
        <h2 class="toc-title reveal">目 录</h2>
        <img class="kd-logo-right-toc" src="https://static.yunzhijia.com/home/download/png/kingdee-blue.png" alt="金蝶AI Logo（蓝色）">
    </div>
    <div class="toc-content">
        <div class="toc-item reveal">
            <span class="toc-number">01</span>
            <span class="toc-text">目录项标题</span>
            <span class="toc-page">P 03</span>
        </div>
        <!-- 更多目录项... -->
    </div>
    <div class="kd-copyright-gray">版权所有©金蝶国际软件集团有限公司 始创于1993</div>
    <div class="kd-confidential-gray">④内部公开 请勿外传</div>
    <span class="slide-num-label">02</span>
</section>
```

**目录项三要素检查清单：**
- [ ] `toc-number` — 序号（蓝色54磅，格式01、02...；>5条用35pt；>9条用24pt）
- [ ] `toc-text` — 标题（24磅加粗）
- [ ] `toc-page` — 页码（蓝色20磅加粗，格式 P XX）← **不可遗漏！**

### 4. 章节页 / Section Slide

```css
.slide-section {
    background: var(--kd-blue);
    display: flex;
    align-items: flex-start;
    position: relative;
}

/* 全屏背景图 - kingdee_chapter.png */
.kd-section-image {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 1;
}

/* 右上角 Logo - 白色版，位置与目录页一致 */
.kd-logo-right-section {
    position: absolute;
    top: 30px;
    right: 60px;
    height: 35px;
    z-index: 10;
}

/* 章节内容层 - 左上角定位 */
.section-content {
    position: absolute;
    top: 80px;
    left: 80px;
    z-index: 5;
}

/* 章节序号 - 125磅，天蓝色 #00CCFE */
.section-number {
    font-size: clamp(60pt, 12vw, 125pt);
    font-weight: 700;
    color: #00CCFE;
    line-height: 1;
}

/* 短横线 - 天蓝色 */
.section-divider {
    width: 6em;
    height: 8px;
    background: #00CCFE;
    margin: 20px 0;
}

/* 章节标题 - 24磅，白色 */
.section-title {
    font-size: clamp(18pt, 2.5vw, 24pt);
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1.3;
}

/* 白色版权（首页和尾页使用；章节页不显示版权） */
.kd-copyright-white {
    position: absolute;
    bottom: 20px;
    left: 60px;
    font-size: 9pt;
    color: #FFFFFF;
    letter-spacing: 1px;
    z-index: 10;
}
```

### 章节页布局示例

```html
<section class="slide slide-section">
    <img class="kd-section-image" src="https://static.yunzhijia.com/home/download/png/kingdee_chapter.png" alt="章节背景">
    <img class="kd-logo-right-section" src="https://static.yunzhijia.com/home/download/png/kingdee-white.png" alt="金蝶AI Logo（白色）">
    <div class="section-content">
        <div class="section-number reveal">01</div>
        <div class="section-divider reveal"></div>
        <h2 class="section-title reveal">章节标题</h2>
    </div>
    <!-- 章节页不显示版权和保密标识 -->
    <span class="slide-num-label light">03</span>
</section>
```

### 5. 尾页 / Closing Slide

```css
.slide-closing {
    background: var(--bg-white);
    position: relative;
}

/* 左上角动态 Logo - 与首页一致 */
/* 使用 .kd-logo-left（top:20px, left:30px, height:96px） */

/* 全屏背景图 - kingdee_endpage.png 满铺 */
.kd-closing-image {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
}

/* 尾页左边居中装饰图 - kingdee-thanks.png */
.kd-closing-image-left {
    position: absolute;
    top: 50%;
    left: 5%;
    transform: translateY(-50%);
    max-height: 40%;
    width: auto;
    object-fit: contain;
    z-index: 5;
}

/* 尾页版权+保密 - 合并一行，浅蓝 #95B8F5 */
.slide-closing .kd-copyright-white {
    color: #95B8F5;
}

.slide-closing .kd-copyright-white span {
    color: #95B8F5;
}
```

### 尾页布局示例

```html
<section class="slide slide-closing">
    <img class="kd-logo-left" src="https://static.yunzhijia.com/home/download/png/kingdee_ColorWhitedynamic.gif" alt="金蝶全彩动态Logo">
    <img class="kd-closing-image" src="https://static.yunzhijia.com/home/download/png/kingdee_endpage.png" alt="尾页背景">
    <img class="kd-closing-image-left" src="https://static.yunzhijia.com/home/download/png/kingdee-thanks.png" alt="感谢页面">
    <!-- 左下角版权+保密合并一行 -->
    <div class="kd-copyright-white">版权所有©金蝶国际软件集团有限公司 始创于1993  <span style="color:#95B8F5;">④内部公开 请勿外传</span></div>
    <span class="slide-num-label">05</span>
</section>
```

---

## Animation / 动画

```css
/* 专业简洁的入场动画 / Professional entrance animation */
.kd-reveal {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.5s ease, transform 0.5s ease;
}

.slide.visible .kd-reveal { opacity: 1; transform: translateY(0); }

/* 尊重减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
    .kd-reveal { transition: none; opacity: 1; transform: none; }
}
```

---

## Signature Elements / 签名视觉元素

1. **首页全屏背景** — `homepage.png` 全屏满铺（`object-fit: cover`），无透明度
2. **金蝶 Logo** — 首页/尾页左上角使用动态 logo `kingdee_ColorWhitedynamic.gif`（96px, top:20px, left:30px）；内容页/目录页右上角使用蓝色 logo `kingdee-blue.png`（35px，flex 布局右对齐）；章节页右上角使用白色 logo `kingdee-white.png`（35px, top:30px, right:60px）
3. **白色内容页** — 干净专业，突出内容
4. **统一字体规范** — 微软雅黑（中英文），首页标题54pt白色居中，内容/目录页标题24pt，副标题16pt，正文14pt
5. **标题与Logo flex对齐** — 目录页和内容页标题通过 flex 容器与 logo 同行排列，`top:30px`
6. **首页标题样式** — 白色 54pt，页面居中
7. **首页左下角信息** — 撰稿人（白色18pt常规）、部门（白色18pt加粗）、日期（白色14pt），默认撰稿人"KClaw"、部门"解决方案部"、日期"2025.01.01"
8. **目录页全屏背景** — `kingdee_catalogue.png` 全屏平铺，目录内容区无白色背景卡片
9. **章节页全屏背景** — `kingdee_chapter.png` 全屏平铺，序号天蓝色125pt，标题白色24pt，**无版权、无保密标识**
10. **尾页全屏背景** — `kingdee_endpage.png` 全屏满铺，`kingdee-thanks.png` 左侧居中（left:5%, max-height:40%）
11. **首页版权+保密合并一行** — 版权浅蓝 #95B8F5，保密深蓝 #1054B1，同行显示；尾页版权+保密均浅蓝 #95B8F5 同行显示
12. **目录页版权+保密分开** — 版权左下灰色 #808080，保密右下灰色 #808080（right:90px）。**内容页仅保密标识（无版权）**
13. **保密级别选项** — ①绝密 / ②机密 / ③秘密 / ④内部（默认）。目录页和内容页使用 `.kd-confidential-gray`（灰色；章节页不显示；首页/尾页合并到版权行中；可替换保密文本
14. **页码** — 所有页面使用 `.slide-num-label`（蓝色9pt, right:60px, bottom:20px），章节页加 `.light` 变白色。**首页和尾页通过 CSS `display:none` 隐藏页码**。目录页/内容页用蓝色，章节页用白色。

---

## Page Type Checklist / 页面类型检查

| 页面类型 | 背景 | Logo 位置 | 特殊元素 |
|---------|------|----------|---------|
| 首页 | 白色 + homepage.png 全屏满铺 | 左上角 kingdee_ColorWhitedynamic.gif（96px, top:20px, left:30px） | 标题白色54pt居中；撰稿人/部门/日期左下白色；版权浅蓝#95B8F5 + 保密深蓝#1054B1 合并一行；**页码隐藏** |
| 目录页 | 白色 + kingdee_catalogue.png 全屏 | 右上角 kingdee-blue.png（35px, flex右对齐, top:30px） | 标题"目 录"24pt行距1.0，flex同行与logo齐平；序号蓝色54磅（>5则35pt）；内容24pt加粗；页码蓝色20pt(P 01)；版权左下灰色；保密右下灰色(right:90px)；**页码蓝色** |
| 章节页 | 蓝色 + kingdee_chapter.png 全屏 | 右上角 kingdee-white.png（35px, top:30px, right:60px） | 序号125pt天蓝色(#00CCFE)左上角；标题24pt白色；**无版权；无保密标识**；页码白色(light) |
| 内容页 | 白色 | 右上角 kingdee-blue.png（35px, flex右对齐, top:30px） | 标题24pt/副标题16pt，flex同行与logo对齐；正文14pt 1.8倍行距；**无版权**；保密右下灰色(right:90px)；**页码蓝色** |
| 尾页 | 白色 + kingdee_endpage.png 全屏满铺 | 左上角 kingdee_ColorWhitedynamic.gif（96px, top:20px, left:30px） | kingdee-thanks 左侧居中(left:5%, max-height:40%)；版权+保密均浅蓝#95B8F5 合并一行；**页码隐藏** |

---

## Best For / 适用场景

Product solutions · Solution proposals · Enterprise software demos · B2B presentations · Corporate training · Investor pitch

产品方案 · 解决方案 · 企业软件演示 · B2B 演示文稿 · 企业培训 · 投资者路演

---

## Assets / 资源文件

源文件位于 `assets/` 目录（主题文件夹内），已部署到 Cloudflare Pages CDN：

### 命名规范

**命名规则：** `kingdee-[类型]-[用途/变体].png`

| 文件名 | 命名含义 | 规则说明 |
|-------|---------|---------|
| `kingdee-blue.png` | Logo（蓝色） | 品牌名+颜色，用于白色背景页面 |
| `kingdee-white.png` | Logo（白色） | 品牌名+颜色，用于蓝色背景页面 |
| `kingdee-thanks.png` | 尾页感谢图 | 品牌名+功能，左侧居中显示"谢谢" |
| `homepage.png` | 首页装饰图 | 页面+功能组合命名 |
| `kingdee_catalogue.png` | 目录页背景 | 页面类型命名 |
| `kingdee_chapter.png` | 章节页背景 | 页面类型命名 |
| `kingdee_endpage.png` | 尾页装饰（右侧） | 页面+序号，右侧背景装饰 |

**扩展示例：**
```
kingdee-logo-white-sm.png    # Logo 小尺寸版
kingdee-watermark.png        # 水印
kingdee-bg-pattern.png       # 背景纹理
```

### alt 属性规范

```html
<!-- Logo 系列：说明颜色 -->
alt="金蝶AI Logo（蓝色）"    <!-- kingdee-blue.png -->
alt="金蝶AI Logo（白色）"    <!-- kingdee-white.png -->

<!-- 背景系列：说明页面类型 -->
alt="目录页背景"              <!-- kingdee_catalogue.png -->
alt="章节页背景"              <!-- kingdee_chapter.png -->

<!-- 装饰系列：说明位置/功能 -->
alt="首页全屏背景"            <!-- homepage.png -->
alt="尾页全屏背景"            <!-- kingdee_endpage.png -->
alt="感谢页面"                <!-- kingdee-thanks.png -->
```

### 文件用途速查表

| 文件 | 用途 | 页面 |
|-----|------|-----|
| `kingdee-blue.png` | 金蝶 AI Logo（蓝色） | 内容页/目录页右上角 |
| `kingdee-white.png` | 金蝶 AI Logo（白色） | 章节页右上角 |
| `kingdee-thanks.png` | 尾页感谢图（left:5%, max-height:40%） | 尾页左侧 |
| `homepage.png` | 首页全屏背景图 | 首页 |
| `kingdee_catalogue.png` | 目录页全屏背景图 | 目录页 |
| `kingdee_chapter.png` | 章节页全屏背景图 | 章节页 |
| `kingdee_endpage.png` | 尾页背景图（全屏满铺） | 尾页 |
| `kingdee_ColorWhitedynamic.gif` | 金蝶全彩动态 Logo（白色版） | 首页/尾页左上角 |
| `kingdee_Colordynamic.gif` | 金蝶全彩动态 Logo（彩色版） | 备用 |

---

## CDN Links / CDN 链接

图片已部署到 Cloudflare Pages CDN：

| 文件 | CDN 链接 |
|-----|---------|
| kingdee-blue.png | https://static.yunzhijia.com/home/download/png/kingdee-blue.png |
| kingdee-white.png | https://static.yunzhijia.com/home/download/png/kingdee-white.png |
| kingdee-thanks.png | https://static.yunzhijia.com/home/download/png/kingdee-thanks.png |
| homepage.png | https://static.yunzhijia.com/home/download/png/homepage.png |
| kingdee_catalogue.png | https://static.yunzhijia.com/home/download/png/kingdee_catalogue.png |
| kingdee_chapter.png | https://static.yunzhijia.com/home/download/png/kingdee_chapter.png |
| kingdee_endpage.png | https://static.yunzhijia.com/home/download/png/kingdee_endpage.png |
| kingdee_ColorWhitedynamic.gif | https://static.yunzhijia.com/home/download/png/kingdee_ColorWhitedynamic.gif |
| kingdee_Colordynamic.gif | https://static.yunzhijia.com/home/download/png/kingdee_Colordynamic.gif |
