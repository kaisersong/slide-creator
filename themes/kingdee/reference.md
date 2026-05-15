# Kingdee 金蝶 — Style Reference
# 金蝶品牌风格参考文档

Professional, tech-forward, enterprise-grade. Inspired by Kingdee's brand identity — trustworthy blue tones, clean layouts, and authoritative typography. Designed for B2B solution presentations, product decks, and enterprise communications.

专业、科技感、企业级。灵感来自金蝶品牌识别——可信赖的蓝色调、清晰的布局、权威的排版。专为 B2B 解决方案演示、产品方案和企业通信设计。

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

### 1. 首页 / Title Slide

```css
.kd-slide-title {
    background: var(--bg-white);
    position: relative;
    height: 100vh;
}

/* 左上角 Logo */
.kd-logo-left {
    position: absolute;
    top: 40px;
    left: 60px;
    height: 48px;
}

/* 右上角装饰图 - 上移10% */
.kd-hero-image {
    position: absolute;
    top: -10%;           /* 上移10% */
    right: 0;
    width: 45%;
    height: 100%;
    object-fit: cover;
    opacity: 0.85;
}

/* 主标题区域 */
.kd-title-content {
    position: absolute;
    left: 60px;
    top: 50%;
    transform: translateY(-50%);
    max-width: 55%;
}

/* 主标题 - 蓝色，56磅，最多2行 */
.kd-title-main {
    font-size: 56pt;
    font-weight: 700;
    color: var(--kd-blue);    /* 蓝色 */
    line-height: 1.2;
    display: -webkit-box;
    -webkit-line-clamp: 2;    /* 最多2行 */
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* 左下角信息区域 */
.kd-slide-title-footer {
    position: absolute;
    left: 60px;
    bottom: 60px;
    z-index: 10;
}

/* 人名 - 蓝色，24磅 */
.kd-slide-title-author {
    font-size: 24pt;
    font-weight: 600;
    color: var(--kd-blue);
    margin-bottom: 8px;
}

/* 文档创建时间 - 蓝色，18磅 */
.kd-slide-title-time {
    font-size: 18pt;
    font-weight: 400;
    color: var(--kd-blue);
}

/* 首页右下角保密标识 - 白色 */
.kd-confidential-title {
    position: absolute;
    bottom: 20px;
    right: 60px;
    font-size: 9.4pt;
    color: #FFFFFF;
    letter-spacing: 1px;
}

/* 首页左下角版权信息 - 白色 */
.kd-copyright-title {
    position: absolute;
    bottom: 20px;
    left: 60px;
    font-size: 9.4pt;
    color: #FFFFFF;
    letter-spacing: 1px;
}
```

### 首页布局示例

```html
<section class="slide slide-title">
    <img class="kd-logo-left" src="https://kingdee-cdn.pages.dev/kingdee-blue.png" alt="金蝶AI Logo（蓝色）">
    <img class="kd-hero-image" src="https://kingdee-cdn.pages.dev/homepage.png" alt="首页右侧装饰">
    <div class="kd-title-content">
        <h1 class="kd-title-main kd-reveal">项目标题</h1>
    </div>
    <div class="kd-slide-title-footer">
        <div class="kd-slide-title-author">KClaw</div>
        <div class="kd-slide-title-time">2024年3月24日</div>
    </div>
    <!-- 左下角版权信息 -->
    <div class="kd-copyright-title">版权所有©金蝶国际软件集团有限公司 始创于1993</div>
    <!-- 右下角保密标识 -->
    <div class="kd-confidential-title">④内部公开 请勿外传</div>
</section>
```

### 2. 内容页 / Content Slide

```css
.kd-slide-content {
    background: var(--bg-white);
    padding: 60px;
    position: relative;
}

/* 右上角 Logo */
.kd-logo-right {
    position: absolute;
    top: 50px;
    right: 60px;
    height: 54px;      /* 54px，与目录页一致 */
}

/* 右下角保密标识 - 所有页面通用 */
.kd-confidential {
    position: absolute;
    bottom: 20px;
    right: 60px;
    font-size: 9.4pt;
    letter-spacing: 1px;
}

/* 白色字体版本：章节页 */
.kd-confidential-white {
    color: #FFFFFF;
}

/* 灰色字体版本：目录页、内容页、尾页 */
.kd-confidential-gray {
    color: #808080;
}

/*
 * 保密级别选项（根据序号或关键词选择）：
 * 1、绝密：①绝密信息 严禁泄露
 * 2、机密：②机密信息 严禁泄露
 * 3、秘密：③秘密信息 严禁泄露
 * 4、内部：④内部公开 请勿外传（默认）
 */

/* 左下角版权信息 - 所有页面通用 */
.kd-copyright {
    position: absolute;
    bottom: 20px;
    left: 60px;
    font-size: 9.4pt;
    letter-spacing: 1px;
}

/* 白色字体版本：首页、章节页、尾页 */
.kd-copyright-white {
    color: #FFFFFF;
}

/* 灰色字体版本：目录页、内容页 */
.kd-copyright-gray {
    color: #808080;
    opacity: 0.7;
}

/* 标题栏：标题位置上移，与logo齐平 */
.kd-content-header {
    position: absolute;
    top: 50px;             /* 与logo的top位置一致 */
    left: 60px;
    right: 200px;          /* 为右侧logo留空间 */
    z-index: 10;
}

.kd-content-title {
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
    font-size: 22pt;       /* 段落标题一级：22磅 */
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.2;
}

.kd-content-subtitle {
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
    font-size: 18pt;       /* 段落标题二级：18磅 */
    font-weight: 400;
    color: var(--text-secondary);
    margin-top: 8px;
}

/* 内容区域 - 标题下方 */
.kd-content-body {
    margin-top: 100px;     /* 为标题区域留出空间 */
    font-size: 12pt;       /* 正文：12磅 */
    line-height: 1.3;      /* 1.3倍行距 */
}

/* 内容页右下角保密标识 - 灰色 */
.kd-confidential-content {
    position: absolute;
    bottom: 20px;
    right: 60px;
    font-size: 9.4pt;
    color: #808080;
    opacity: 0.7;
    letter-spacing: 1px;
}

/* 内容页左下角版权信息 - 灰色 */
.kd-copyright-content {
    position: absolute;
    bottom: 20px;
    left: 60px;
    font-size: 9.4pt;
    color: #808080;
    opacity: 0.7;
    letter-spacing: 1px;
}

/* ===========================================
   内容适配 / Content Adaptation
   解决内容较少时页面下半部分空白的问题
   =========================================== */

/* 内容垂直居中 - 适用于内容较少的页面 */
.kd-content-body.centered {
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: calc(100vh - 220px);  /* 减去header和footer */
    margin-top: 100px;                /* 为标题区域留空间 */
}

/* 内容弹性分布 - 适用于内容中等的页面 */
.kd-content-body.spread {
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;    /* 均匀分布，首尾有间距 */
    min-height: calc(100vh - 220px);
    margin-top: 100px;
}

/* 底部装饰条 - 可选，为空白区域增加视觉元素 */
.kd-bottom-accent {
    position: absolute;
    bottom: 80px;
    left: 80px;
    right: 80px;
    height: 3px;
    background: linear-gradient(90deg, var(--kd-blue) 0%, transparent 100%);
    opacity: 0.3;
    z-index: 5;
}
```

### 内容页布局示例

```html
<section class="slide slide-content">
    <img class="kd-logo-right" src="https://kingdee-cdn.pages.dev/kingdee-blue.png" alt="金蝶AI Logo（蓝色）">
    <div class="kd-content-header">
        <h2 class="kd-content-title kd-reveal">页面标题</h2>
        <p class="kd-content-subtitle kd-reveal">副标题（可选）</p>
    </div>
    <div class="kd-content-body">
        <!-- 正文内容 -->
        <p class="kd-reveal">这里是正文内容...</p>
    </div>
    <!-- 左下角版权信息 -->
    <div class="kd-copyright-content">版权所有©金蝶国际软件集团有限公司 始创于1993</div>
    <!-- 右下角保密标识 -->
    <div class="kd-confidential-content">④内部公开 请勿外传</div>
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
<div class="kd-content-body centered">
    <div class="kd-highlight-box">
        ...
    </div>
</div>

<!-- 内容中等时：弹性分布 -->
<div class="kd-content-body spread">
    <div class="kd-feature-card">...</div>
    <div class="kd-feature-card">...</div>
    <div class="kd-feature-card">...</div>
</div>

<!-- 内容较多时：默认布局 -->
<div class="kd-content-body">
    <p>...</p>
    <ul>...</ul>
    <div class="kd-two-col">...</div>
</div>
```

### 3. 目录页 / TOC Slide

```css
.kd-slide-toc {
    background: var(--bg-white);    /* 白色底 */
    padding: 60px;
    position: relative;
}

/* 右上角 Logo - 放大50% (54px) */
.kd-logo-right-toc {
    position: absolute;
    top: 50px;
    right: 60px;
    height: 54px;                   /* 放大50% (原36px) */
    z-index: 10;
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

.kd-toc-content {
    position: absolute;
    left: 80px;
    right: 60px;                   /* 延伸到页面右边 */
    top: 50%;
    transform: translateY(-50%);
    z-index: 5;
    padding: 40px 0;               /* 无背景，仅垂直间距 */
    /* 移除白色背景卡片 */
}

/* 目录标题 - 位置上移与logo齐平 */
.kd-toc-title {
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
    font-size: 24pt;               /* 24磅 */
    font-weight: 700;              /* 加粗 */
    line-height: 1.0;              /* 行距1.0 */
    color: var(--text-primary);
    margin-bottom: 40px;
    position: absolute;
    top: 50px;                     /* 与logo齐平 */
    left: 80px;
}

/* 目录副标题 - 微软雅黑常规16磅 */
.kd-toc-subtitle {
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
    font-size: 16pt;               /* 16磅 */
    font-weight: 400;              /* 常规 */
    color: var(--text-secondary);
    margin-bottom: 30px;
}

/* 目录项容器 - 统一布局 */
.kd-toc-item {
    display: flex;
    align-items: center;
    margin-bottom: 28px;           /* 默认间距28px */
    color: var(--text-primary);
    position: relative;            /* 为页码定位 */
}

/* 目录条数>9时的紧凑间距 */
.kd-toc-item.compact {
    margin-bottom: 12px;           /* 紧凑间距12px，适用于目录条数>9的情况 */
}

/* 目录序号 - 蓝色，格式01、02等 */
.kd-toc-number {
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
    font-size: 54pt;               /* 默认54磅；若目录条数>5，调整为35pt */
    font-weight: 700;              /* 加粗 */
    color: var(--kd-blue);         /* 蓝色 */
    margin-right: 24px;
    min-width: 100px;
    line-height: 1;
}

/* 目录条数>5时的序号样式 */
.kd-toc-number.compact {
    font-size: 35pt;               /* 35磅，适用于目录条数>5的情况 */
}

/* 目录条数>9时的超紧凑序号样式 */
.kd-toc-number.ultra-compact {
    font-size: 24pt;               /* 24磅，适用于目录条数>9的情况 */
}

/* 目录内容 - 24磅，加粗 */
.kd-toc-text {
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
    font-size: 24pt;               /* 24磅 */
    font-weight: 700;              /* 加粗 */
    color: var(--text-primary);
    flex: 1;
}

/* 目录页码 - 蓝色，加粗，距离页面右边150px */
.kd-toc-page {
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
    font-size: 20pt;               /* 20磅 */
    font-weight: 700;              /* 加粗 */
    color: var(--kd-blue);         /* 蓝色 */
    position: absolute;
    right: 90px;                   /* 距离页面右边：60px(内容区域) + 90px = 150px */
}

/* 目录页右下角保密标识 - 灰色 */
.kd-confidential-toc {
    position: absolute;
    bottom: 20px;
    right: 60px;
    font-size: 9.4pt;
    color: #808080;
    opacity: 0.7;
    letter-spacing: 1px;
}

/* 目录页左下角版权信息 - 灰色 */
.kd-copyright-toc {
    position: absolute;
    bottom: 20px;
    left: 60px;
    font-size: 9.4pt;
    color: #808080;
    opacity: 0.7;
    letter-spacing: 1px;
}
```

### 目录页布局示例

**⚠️ 重要：每个目录项必须包含三个元素：序号 + 标题 + 页码，缺一不可！**

```html
<section class="slide slide-toc">
    <img class="kd-toc-image" src="https://kingdee-cdn.pages.dev/kingdee_catalogue.png" alt="目录页背景">
    <img class="kd-logo-right-toc" src="kingdeeAI1.png" alt="金蝶AI Logo（白底用）">
    <h2 class="kd-toc-title">目 录</h2>
    <div class="kd-toc-content">
        <div class="kd-toc-item">
            <span class="kd-toc-number">01</span>
            <span class="kd-toc-text">本周项目全景图</span>
            <span class="kd-toc-page">P 03</span>  <!-- 必须包含页码！格式：P XX -->
        </div>
        <div class="kd-toc-item">
            <span class="kd-toc-number">02</span>
            <span class="kd-toc-text">项目漏斗分析</span>
            <span class="kd-toc-page">P 04</span>  <!-- 必须包含页码！格式：P XX -->
        </div>
        <!-- 更多目录项...每个都必须有 kd-toc-page -->
    </div>
    <!-- 左下角版权信息 -->
    <div class="kd-copyright-toc">版权所有©金蝶国际软件集团有限公司 始创于1993</div>
    <!-- 右下角保密标识 -->
    <div class="kd-confidential-toc">④内部公开 请勿外传</div>
</section>
```

**目录项三要素检查清单：**
- [ ] `kd-toc-number` — 序号（蓝色54磅，格式01、02...）
- [ ] `kd-toc-text` — 标题（24磅加粗）
- [ ] `kd-toc-page` — 页码（蓝色20磅加粗，格式 P XX）← **不可遗漏！**

### 4. 章节页 / Section Slide

```css
.kd-slide-section {
    background: var(--kd-blue);
    display: flex;
    align-items: flex-start;     /* 改为顶部对齐 */
    position: relative;
}

/* 全屏背景图 - kingdee_chapter.png 平铺整个页面 */
.kd-section-image {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 1;
}

/* 右上角 Logo */
.kd-logo-right-section {
    position: absolute;
    top: 50px;
    right: 60px;
    height: 54px;               /* 与目录页/内容页一致 */
    z-index: 10;
}

/* 章节内容层 - 左上角定位 */
.kd-section-content {
    position: absolute;
    top: 80px;                  /* 距顶部80px */
    left: 80px;                 /* 距左边80px */
    z-index: 5;
}

/* 章节序号 - 125磅，天蓝色 #00CCFE */
.kd-section-number {
    font-size: 125pt;
    font-weight: 700;
    color: #00CCFE;             /* 天蓝色 */
    line-height: 1;
}

/* 短横线 - 天蓝色 */
.kd-section-divider {
    width: 6em;
    height: 8px;
    background: #00CCFE;        /* 天蓝色 */
    margin: 20px 0;
}

/* 章节标题 - 24磅，白色 */
.kd-section-title {
    font-size: 24pt;
    font-weight: 700;
    color: #FFFFFF;             /* 白色 */
    line-height: 1.3;
}

/* 章节页右下角保密标识 - 白色 */
.kd-confidential-section {
    position: absolute;
    bottom: 20px;
    right: 60px;
    font-size: 9.4pt;
    color: #FFFFFF;
    letter-spacing: 1px;
}

/* 章节页左下角版权信息 - 白色 */
.kd-copyright-section {
    position: absolute;
    bottom: 20px;
    left: 60px;
    font-size: 9.4pt;
    color: #FFFFFF;
    letter-spacing: 1px;
}
```

### 章节页布局示例

```html
<section class="slide slide-section">
    <img class="kd-section-image" src="https://kingdee-cdn.pages.dev/kingdee_chapter.png" alt="章节背景">
    <img class="kd-logo-right-section" src="https://kingdee-cdn.pages.dev/kingdee-white.png" alt="金蝶AI Logo（白色）">
    <div class="kd-section-content">
        <div class="kd-section-number kd-reveal">01</div>
        <div class="kd-section-divider kd-reveal"></div>
        <h2 class="kd-section-title kd-reveal">本周项目全景图</h2>
    </div>
    <!-- 左下角版权信息 -->
    <div class="kd-copyright-section">版权所有©金蝶国际软件集团有限公司 始创于1993</div>
    <!-- 右下角保密标识 -->
    <div class="kd-confidential-section">④内部公开 请勿外传</div>
</section>
```

### 5. 尾页 / Closing Slide

```css
.kd-slide-closing {
    background: var(--bg-white);
    position: relative;
    height: 100vh;
}

/* 左上角 Logo */
.kd-logo-left-closing {
    position: absolute;
    top: 40px;
    left: 60px;
    height: 40px;
}

/* 尾页左边居中装饰图 */
.kd-closing-image-left {
    position: absolute;
    top: 50%;
    left: 5%;           /* 向左移动10% (原15%) */
    transform: translateY(-50%);
    max-height: 30%;    /* 缩小50% (原60%) */
    width: auto;
    object-fit: contain;
    z-index: 5;
}

/* 右侧背景图 */
.kd-closing-image {
    position: absolute;
    top: -40%;
    right: 0;
    width: 87%;         /* 放大20% (原72%) */
    height: auto;       /* 保持图片原始比例，不强制拉伸 */
    object-fit: contain; /* 确保图片完整显示，不被裁剪 */
    opacity: 0.85;
}

/* 尾页右下角保密标识 - 灰色 */
.kd-confidential-closing {
    position: absolute;
    bottom: 20px;
    right: 60px;
    font-size: 9.4pt;
    color: #808080;
    letter-spacing: 1px;
}

/* 尾页左下角版权信息 - 灰色 */
.kd-copyright-closing {
    position: absolute;
    bottom: 20px;
    left: 60px;
    font-size: 9.4pt;
    color: #808080;
    letter-spacing: 1px;
}
```

### 尾页布局示例

```html
<section class="slide slide-closing">
    <img class="kd-logo-left-closing" src="https://kingdee-cdn.pages.dev/kingdee-blue.png" alt="金蝶AI Logo（蓝色）">
    <img class="kd-closing-image-left" src="https://kingdee-cdn.pages.dev/kingdee-thanks.png" alt="感谢页面">
    <img class="kd-closing-image" src="https://kingdee-cdn.pages.dev/kingdee_endpage.png" alt="尾页右侧装饰">
    <!-- 左下角版权信息 - 灰色 -->
    <div class="kd-copyright-closing">版权所有©金蝶国际软件集团有限公司 始创于1993</div>
    <!-- 右下角保密标识 - 灰色 -->
    <div class="kd-confidential-closing">④内部公开 请勿外传</div>
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

1. **品牌蓝背景** — 章节页使用 `#0052D9` 蓝色底
2. **金蝶 AI Logo** — 首页/尾页左上角、内容页/目录页右上角使用 `kingdee-blue.png`（蓝色logo）；章节页右上角使用 `kingdee-white.png`（白色logo）
3. **白色内容页** — 干净专业，突出内容
4. **统一字体规范** — 微软雅黑（中英文），大标题24pt加粗，副标题16pt，段落标题一级22pt加粗，段落标题二级18pt加粗，正文12pt普通1.3倍行距，标注10pt普通1.3倍行距，重点强调20pt加粗蓝/黄色
5. **标题与Logo对齐** — 内容页标题位置上移至top:50px，与右上角Logo齐平
6. **首页右上角装饰图** — `homepage.png` 上移10%
7. **首页标题样式** — 蓝色56磅，最多2行
8. **首页左下角信息** — 人名（蓝色24磅，仅显示姓名无前缀）+ 时间（蓝色18磅，仅显示日期无前缀）。若内容中无法识别汇报人，默认显示"KClaw"
9. **目录页全屏背景** — `kingdee_catalogue.png` 全屏平铺，目录内容带半透明白色背景卡片
10. **尾页双装饰图** — `kingdee-thanks.png` 左边居中(left:5%, max-height:30%) + `kingdee_endpage.png` 右侧(width:87%, top:-40%)，无文字
11. **右下角保密标识（所有页面）** — 字体9.4磅，可选项：①绝密信息 严禁泄露 / ②机密信息 严禁泄露 / ③秘密信息 严禁泄露 / ④内部公开 请勿外传（默认）；章节页白色字体，目录页/内容页/尾页灰色#808080
12. **左下角版权信息（所有页面）** — 版权所有©金蝶国际软件集团有限公司 始创于1993，字体9.4磅；章节页白色字体，目录页/内容页/尾页灰色#808080

---

## Page Type Checklist / 页面类型检查

| 页面类型 | 背景 | Logo 位置 | 特殊元素 |
|---------|------|----------|---------|
| 首页 | 白色 | 左上角 kingdee-blue.png（高度72px） | 右上角 homepage.png（上移10%）；标题蓝色56磅最多2行；左下角人名24磅（仅姓名）+时间18磅（仅日期），默认KClaw；**左下角版权（灰色#808080，9.4磅）；右下角保密标识（灰色#808080，9.4磅，默认④内部）** |
| 目录页 | 白色 | 右上角 kingdee-blue.png（高度54px） | 全屏背景 kingdee_catalogue.png；标题"目 录"24磅行距1.0，位置与logo齐平；序号蓝色54磅（若条数>5则35磅）；内容24磅加粗；页码蓝色加粗20磅(P 01/P 02)，距离右边150px；无白色背景卡片；**条数>9时行间距改为紧凑（margin-bottom: 12px）**；**左下角版权（灰色#808080，9.4磅）；右下角保密标识（灰色#808080，9.4磅，默认④内部）** |
| 章节页 | 蓝色 + 全屏背景图 | 右上角 kingdee-white.png（高度54px） | 全屏背景 kingdee_chapter.png；序号125pt天蓝色(#00CCFE)左上角；短横线与0同宽同色；标题24pt白色；**左下角版权（白色9.4磅）；右下角保密标识（白色9.4磅，默认④内部）** |
| 内容页 | 白色 | 右上角 kingdee-blue.png（高度54px） | 标题22pt/副标题18pt，位置top:50px与logo齐平；正文12pt 1.3倍行距；**左下角版权（灰色#808080，9.4磅）；右下角保密标识（灰色#808080，9.4磅，可选项：①绝密/②机密/③秘密/④内部）** |
| 尾页 | 白色 | 左上角 kingdee-blue.png（高度72px） | 左边居中kingdee-thanks(left:5%,max-height:30%) + 右侧kingdee_endpage(width:87%,top:-40%)，无文字；**左下角版权（灰色#808080，9.4磅）；右下角保密标识（灰色#808080，9.4磅，默认④内部）** |

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
alt="首页右侧装饰"            <!-- homepage.png -->
alt="尾页右侧装饰"            <!-- kingdee_endpage.png -->
alt="感谢页面"                <!-- kingdee-thanks.png -->
```

### 文件用途速查表

| 文件 | 用途 | 页面 |
|-----|------|-----|
| `kingdee-blue.png` | 金蝶 AI Logo（蓝色） | 首页/尾页左上角、内容页/目录页右上角 |
| `kingdee-white.png` | 金蝶 AI Logo（白色） | 章节页右上角 |
| `kingdee-thanks.png` | 尾页感谢图（left:5%, max-height:30%） | 尾页左侧 |
| `homepage.png` | 首页右侧装饰图 | 首页 |
| `kingdee_catalogue.png` | 目录页全屏背景图 | 目录页 |
| `kingdee_chapter.png` | 章节页全屏背景图 | 章节页 |
| `kingdee_endpage.png` | 尾页右侧背景图（width:87%, top:-40%） | 尾页 |

---

## CDN Links / CDN 链接

图片已部署到 Cloudflare Pages CDN：

| 文件 | CDN 链接 |
|-----|---------|
| kingdee-blue.png | https://kingdee-cdn.pages.dev/kingdee-blue.png |
| kingdee-white.png | https://kingdee-cdn.pages.dev/kingdee-white.png |
| kingdee-thanks.png | https://kingdee-cdn.pages.dev/kingdee-thanks.png |
| homepage.png | https://kingdee-cdn.pages.dev/homepage.png |
| kingdee_catalogue.png | https://kingdee-cdn.pages.dev/kingdee_catalogue.png |
| kingdee_chapter.png | https://kingdee-cdn.pages.dev/kingdee_chapter.png |
| kingdee_endpage.png | https://kingdee-cdn.pages.dev/kingdee_endpage.png |
