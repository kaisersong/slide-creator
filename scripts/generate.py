#!/usr/bin/env python3
"""
slide-creator --generate (Blue Sky preset)

Reads PLANNING.md + blue-sky-starter.html -> generates a complete HTML presentation.

The starter template contains all CSS, JS, components, and infrastructure.
This script only replaces slide content inside #track.

Usage:
    python3 scripts/generate.py [--output FILE.html]
"""

import re
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def parse_planning(path):
    """Parse PLANNING.md and extract slides with component tree."""
    content = read_file(path)
    slides = []
    current = None
    current_items = []

    for line in content.split("\n"):
        m = re.match(r"\*\*Slide (\d+) \| (.+?)\*\*", line)
        if m:
            if current is not None:
                current["items"] = current_items
                slides.append(current)
            current = {"number": int(m.group(1)), "type": m.group(2).strip()}
            current_items = []
            continue

        if current is not None and line.strip().startswith("- "):
            indent = len(line) - len(line.lstrip())
            text = line.lstrip()[2:]
            if text.startswith("Visual:"):
                continue

            # Extract component: try patterns in order of specificity
            component = None
            modifiers = []

            # Pattern 1: .comp .variant: text  (e.g. ".g .warn: ❌ 传统方法")
            # Pattern 1: .comp .mod1 .mod2: text  (e.g. ".g .theme .highlight: 浅色 · 5 个主题")
            cm = re.match(r"\.(\w+)((?:\s+\.\w+)*):\s*(.*)", text)
            if cm:
                component = cm.group(1)
                mods_str = cm.group(2)
                modifiers = re.findall(r"\.(\w+)", mods_str)
                text = cm.group(3).strip()
            else:
                # Pattern 2: .comp: text  (e.g. ".pill: 工作流")
                cm = re.match(r"\.(\w+):\s*(.*)", text)
                if cm:
                    component = cm.group(1)
                    text = cm.group(2).strip()
                else:
                    # Pattern 3: .comp text  (e.g. ".layer 1: Title" or ".g 深色")
                    cm2 = re.match(r"\.(\w+)\s+(.*)", text)
                    if cm2:
                        component = cm2.group(1)
                        text = cm2.group(2).strip()
                    else:
                        # Pattern 4: bare .comp
                        cm3 = re.match(r"\.(\w+)$", text)
                        if cm3:
                            component = cm3.group(1)
                            text = ""

            current_items.append({
                "indent": indent,
                "component": component,
                "modifiers": modifiers,
                "text": text,
                "children": [],
            })

    if current is not None:
        current["items"] = current_items
        slides.append(current)

    # Build tree using stack-based indent tracking
    for slide in slides:
        items = slide.get("items", [])
        tree = []
        stack = []
        for item in items:
            while stack and stack[-1][0] >= item["indent"]:
                stack.pop()
            if stack:
                stack[-1][1]["children"].append(item)
            else:
                tree.append(item)
            stack.append((item["indent"], item))
        slide["tree"] = tree

    return slides


def _render_inline_bold(text):
    """Convert **bold** to <strong>, then handle code ticks."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    parts = []
    in_code = False
    for ch in text:
        if ch == "`":
            parts.append("</code>" if in_code else "<code>")
            in_code = not in_code
        else:
            parts.append(ch)
    return "".join(parts)


def _render_children(children, parent_component=None):
    """Recursively render component tree to HTML."""
    parts = []
    i = 0
    while i < len(children):
        item = children[i]
        comp = item["component"]
        text = item["text"]
        kids = item["children"]
        mods = item.get("modifiers", [])

        if comp == "pill":
            parts.append(f'<span class="pill" style="margin-bottom:14px;display:inline-block;">{text}</span>')

        elif comp == "gt":
            parts.append(f'<h2 class="gt">{text}</h2>')

        elif comp == "cols2":
            inner = ""
            for ci in kids:
                inner += _render_col_child(ci)
            parts.append(f'<div class="cols2">\n{inner}</div>')

        elif comp == "cols3":
            inner = ""
            for ci in kids:
                inner += _render_col_child(ci)
            parts.append(f'<div class="cols3">\n{inner}</div>')

        elif comp == "cols4":
            inner = ""
            for ci in kids:
                inner += _render_col_child(ci)
            parts.append(f'<div class="cols4" style="gap:10px;align-items:start;">\n{inner}</div>')

        elif comp == "g":
            # Theme showcase card (P4 preset page)
            if "theme" in mods and kids:
                theme_names_raw = [c["text"] for c in kids if c["component"] is None]
                # Separate footer (last item that looks like a category footer)
                footer = ""
                theme_names = theme_names_raw
                if len(theme_names_raw) >= 2:
                    last = theme_names_raw[-1]
                    # Footer typically has 2+ Chinese words separated by middot
                    if "·" in last and len(last) < 30:
                        footer = last
                        theme_names = theme_names_raw[:-1]

                # Parse title from card text: "深色 · 4 个主题"
                title_parts = text.split("·", 1) if "·" in text else [text, ""]
                category = title_parts[0].strip()
                count_text = title_parts[1].strip() if len(title_parts) > 1 else ""

                # Color mapping per category
                is_highlight = "highlight" in mods
                if is_highlight:
                    dot_bg = "linear-gradient(135deg,#2563eb,#0ea5e9)"
                    chip_bg = "rgba(37,99,235,0.08)"
                    chip_color = "#1e3a8a"
                    card_border = "border:1px solid rgba(37,99,235,0.25);"
                elif "深" in category or "Dark" in category:
                    dot_bg = "#0f172a"
                    chip_bg = "rgba(15,23,42,0.08)"
                    chip_color = "#1e293b"
                    card_border = ""
                elif "浅" in category or "Light" in category or "蓝" in category:
                    dot_bg = "#0ea5e9"
                    chip_bg = "rgba(14,165,233,0.10)"
                    chip_color = "#0c4a6e"
                    card_border = ""
                elif "专" in category or "Pro" in category:
                    dot_bg = "#8b5cf6"
                    chip_bg = "rgba(139,92,246,0.10)"
                    chip_color = "#4c1d95"
                    card_border = ""
                else:
                    dot_bg = "#2563eb"
                    chip_bg = "rgba(37,99,235,0.08)"
                    chip_color = "#1e3a8a"
                    card_border = ""

                # Build theme chips
                chips_html = ""
                for tn in theme_names:
                    chip_style = f"font-size:0.77rem;padding:3px 10px;background:{chip_bg};border-radius:6px;color:{chip_color};"
                    # Mark current preset
                    is_current = "本演示" in tn or ("Blue Sky" in tn and "★" not in tn)
                    if is_current:
                        chip_style += "display:flex;align-items:center;gap:6px;"
                        chips_html += f'<span style="{chip_style}">{tn} <span class="pill green" style="font-size:0.65rem;padding:1px 7px;">本演示</span></span>\n'
                    else:
                        chips_html += f'<span style="{chip_style}">{tn}</span>\n'

                footer_html = ""
                if footer:
                    footer_html = f'<p style="font-size:0.72rem;color:var(--text-muted);margin-top:10px;">{footer}</p>'

                border_attr = f' style="padding:16px 18px;{card_border}"' if card_border else ' style="padding:16px 18px;"'
                parts.append(f'''<div class="g"{border_attr}>
<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
<div style="width:10px;height:10px;border-radius:50%;background:{dot_bg};flex-shrink:0;"></div>
<h4 style="font-size:0.88rem;">{category}</h4>
<span style="font-size:0.7rem;color:var(--text-muted);">{count_text}</span>
</div>
<div style="display:flex;flex-direction:column;gap:5px;">
{chips_html}</div>
{footer_html}</div>''')
            # Check for modifier variants (.warn = red border, .green = green border)
            elif "warn" in mods or "green" in mods:
                border_style = ""
                title_color = ""
                if "warn" in mods:
                    border_style = "border-left:4px solid #ef4444;"
                    title_color = 'style="color:#b91c1c;"'
                elif "green" in mods:
                    border_style = "border-left:4px solid #10b981;"
                    title_color = 'style="color:#065f46;"'

                padding = 'style="padding:22px 24px;' + border_style + '"'

                if kids:
                    has_bullets = any(c["component"] is None for c in kids)
                    has_kbd = any(c["component"] == "kbd" for c in kids)
                    has_stat = any(_looks_stat(c) for c in kids)

                    if has_stat:
                        # Stat KPI card: center-aligned with .stat number
                        inner = ""
                        for c in kids:
                            if c["component"] is None:
                                inner += f'<p style="font-size:0.8rem;">{_render_inline_bold(c["text"])}</p>\n'
                            elif c["component"] == "stat":
                                inner += f'<div class="stat">{c["text"]}</div>\n'
                            elif c["children"]:
                                inner += _render_children([c])
                            else:
                                inner += f"<p>{_render_inline_bold(c['text'])}</p>\n"
                        parts.append(f'<div class="g" style="padding:22px;text-align:center;">\n{inner}</div>')
                    elif has_bullets:
                        # Glass card with title + bullet list
                        items_html = ""
                        for c in kids:
                            if c["component"] is None:
                                items_html += f'<li>{_render_inline_bold(c["text"])}</li>\n'
                            elif c["component"] == "kbd":
                                items_html += _render_kbd_child(c)
                            else:
                                items_html += _render_children([c])
                        h4_styles = "margin-bottom:10px;"
                        if title_color:
                            color_val = title_color.replace('style="', '').replace('"', '')
                            h4_styles = color_val + ";margin-bottom:10px;"
                        title_html = f'<h4 style="{h4_styles}">{text}</h4>\n' if text else ""
                        parts.append(f'<div class="g" {padding}>\n{title_html}<ul class="bl">\n{items_html}</ul></div>')
                    elif has_kbd:
                        items_html = ""
                        for c in kids:
                            if c["component"] == "kbd":
                                items_html += _render_kbd_child(c)
                            elif c["children"]:
                                items_html += _render_children([c])
                            else:
                                items_html += f"<p>{_render_inline_bold(c['text'])}</p>\n"
                        parts.append(f'<div class="g" {padding}>\n{items_html}</div>')
                    else:
                        inner = _render_children(kids)
                        parts.append(f'<div class="g" {padding}>\n{inner}</div>')
                else:
                    parts.append(f'<div class="g" {padding}>\n{_render_inline_bold(text)}\n</div>')
            # Plain .g card with no modifier
            else:
                if kids:
                    inner = _render_children(kids)
                    parts.append(f'<div class="g" style="padding:22px 24px;">\n{inner}</div>')
                else:
                    parts.append(f'<div class="g" style="padding:22px 24px;">\n{_render_inline_bold(text)}\n</div>')

        elif comp == "layer":
            step_html = ""
            title = text
            # ".layer 1: Title" or ".layer emoji: Title"
            num_match = re.match(r"(\d+):\s*(.*)", text)
            if num_match:
                step_html = f'<div class="step">{num_match.group(1)}</div>'
                title = num_match.group(2)
            else:
                emoji_match = re.match(r"(.+?):\s*(.*)", text)
                if emoji_match and len(emoji_match.group(1).strip()) <= 4:
                    step_html = f'<div style="font-size:1.5rem;flex-shrink:0;">{emoji_match.group(1)}</div>'
                    title = emoji_match.group(2)

            inner_html = f"<h4 style=\"margin-bottom:4px;\">{title}</h4>\n"
            for child in kids:
                if child["component"] == "cmd":
                    inner_html += f'<div class="cmd" style="margin-top:7px;">{child["text"]}</div>\n'
                elif child["component"] == "kbd":
                    inner_html += _render_kbd_child(child)
                elif child["component"]:
                    inner_html += _render_children([child])
                else:
                    inner_html += f"<p>{_render_inline_bold(child['text'])}</p>\n"
            parts.append(f'<div class="layer">\n{step_html}<div>\n{inner_html}</div>\n</div>')

        elif comp == "info":
            parts.append(f'<div class="info">{_render_inline_bold(text)}</div>')

        elif comp == "co":
            parts.append(f'<div class="co">{_render_inline_bold(text)}</div>')

        elif comp == "cmd":
            parts.append(f'<div class="cmd">{text}</div>')

        elif comp == "kbd":
            parts.append(_render_kbd_child(item))

        elif comp is None:
            if kids:
                parts.append(_render_children(kids))
            else:
                parts.append(_render_inline_bold(text))

        i += 1

    return "\n".join(parts)


def _looks_stat(item):
    """Check if a .g card item looks like a stat KPI."""
    t = item.get("text", "").strip()
    if not t or len(t) > 2:
        return False
    # Stat KPIs are single characters/digits like "0", "3", "∞"
    # Reject CJK characters and Chinese punctuation
    if re.search(r"[\u4e00-\u9fff，。、！？：；（）【】《》]", t):
        return False
    return True


def _render_col_child(item):
    """Render a child inside a cols2/3/4 column."""
    comp = item["component"]
    text = item["text"]
    kids = item["children"]
    mods = item.get("modifiers", [])

    if comp == "g":
        # Theme showcase card (P4 preset page)
        if "theme" in mods and kids:
            theme_names_raw = [c["text"] for c in kids if c["component"] is None]
            footer = ""
            theme_names = theme_names_raw
            if len(theme_names_raw) >= 2:
                last = theme_names_raw[-1]
                if "·" in last and len(last) < 30:
                    footer = last
                    theme_names = theme_names_raw[:-1]

            title_parts = text.split("·", 1) if "·" in text else [text, ""]
            category = title_parts[0].strip()
            count_text = title_parts[1].strip() if len(title_parts) > 1 else ""

            is_highlight = "highlight" in mods
            if is_highlight:
                dot_bg = "linear-gradient(135deg,#2563eb,#0ea5e9)"
                chip_bg = "rgba(37,99,235,0.08)"
                chip_color = "#1e3a8a"
                card_border = "border:1px solid rgba(37,99,235,0.25);"
            elif "深" in category or "Dark" in category:
                dot_bg = "#0f172a"
                chip_bg = "rgba(15,23,42,0.08)"
                chip_color = "#1e293b"
                card_border = ""
            elif "浅" in category or "Light" in category or "蓝" in category:
                dot_bg = "#0ea5e9"
                chip_bg = "rgba(14,165,233,0.10)"
                chip_color = "#0c4a6e"
                card_border = ""
            elif "专" in category or "Pro" in category:
                dot_bg = "#8b5cf6"
                chip_bg = "rgba(139,92,246,0.10)"
                chip_color = "#4c1d95"
                card_border = ""
            else:
                dot_bg = "#2563eb"
                chip_bg = "rgba(37,99,235,0.08)"
                chip_color = "#1e3a8a"
                card_border = ""

            chips_html = ""
            for tn in theme_names:
                chip_style = f"font-size:0.77rem;padding:3px 10px;background:{chip_bg};border-radius:6px;color:{chip_color};"
                is_current = "本演示" in tn
                if is_current:
                    tn = re.sub(r'\s*★\s*本演示\s*', '', tn).strip()
                    chip_style += "display:flex;align-items:center;gap:6px;"
                    chips_html += f'<span style="{chip_style}">{tn} <span class="pill green" style="font-size:0.65rem;padding:1px 7px;">本演示</span></span>\n'
                else:
                    chips_html += f'<span style="{chip_style}">{tn}</span>\n'

            footer_html = f'<p style="font-size:0.72rem;color:var(--text-muted);margin-top:10px;">{footer}</p>' if footer else ""
            border_attr = f' style="padding:16px 18px;{card_border}"' if card_border else ' style="padding:16px 18px;"'
            return f'''<div class="g"{border_attr}>
<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
<div style="width:10px;height:10px;border-radius:50%;background:{dot_bg};flex-shrink:0;"></div>
<h4 style="font-size:0.88rem;">{category}</h4>
<span style="font-size:0.7rem;color:var(--text-muted);">{count_text}</span>
</div>
<div style="display:flex;flex-direction:column;gap:5px;">
{chips_html}</div>
{footer_html}</div>'''

        # Check for variant styling
        border_style = ""
        title_color = ""
        if "warn" in mods:
            border_style = "border-left:4px solid #ef4444;"
            title_color = 'style="color:#b91c1c;"'
        elif "green" in mods:
            border_style = "border-left:4px solid #10b981;"
            title_color = 'style="color:#065f46;"'

        if _looks_stat(item) and kids:
            # Stat KPI card: single char number + description
            inner = f'<div class="stat">{text}</div>\n'
            for c in kids:
                if c["component"] is None:
                    inner += f'<p style="font-size:0.8rem;">{_render_inline_bold(c["text"])}</p>\n'
                else:
                    inner += _render_children([c])
            return f'<div class="g" style="padding:22px;text-align:center;">\n{inner}</div>'

        if kids:
            has_bullets = any(c["component"] is None for c in kids)

            if has_bullets:
                items_html = ""
                for c in kids:
                    if c["component"] is None:
                        items_html += f'<li>{_render_inline_bold(c["text"])}</li>\n'
                    else:
                        items_html += _render_children([c])
                h4_styles = "margin-bottom:10px;"
                if title_color:
                    color_val = title_color.replace('style="', '').replace('"', '')
                    h4_styles = color_val + ";margin-bottom:10px;"
                title_html = f'<h4 style="{h4_styles}">{text}</h4>\n' if text else ""
                return f'<div class="g" style="padding:22px 24px;{border_style}">\n{title_html}<ul class="bl">\n{items_html}</ul></div>'

            # No bullets, just render children
            inner = _render_children(kids)
            title_html = f'<h4 {title_color}>{text}</h4>\n' if text else ""
            return f'<div class="g" style="padding:22px 24px;{border_style}">\n{title_html}{inner}</div>'
        else:
            return f'<div class="g" style="padding:22px 24px;{border_style}">\n{_render_inline_bold(text)}\n</div>'

    elif comp:
        return _render_children([item])
    else:
        return f"<div>{_render_inline_bold(text)}</div>\n"


def _render_kbd_child(item):
    """Render a .kbd item: split keys from description."""
    text = item["text"]
    kbd_match = re.match(r"(.+?)\s+([\u4e00-\u9fff].*)", text)
    if kbd_match:
        keys = kbd_match.group(1)
        desc = kbd_match.group(2)
        keys_html = " ".join(f"<kbd>{k.strip()}</kbd>" for k in re.split(r"\s+", keys))
        return (
            f'<div style="display:flex;align-items:center;gap:10px;padding:6px 0;'
            f'border-bottom:1px solid rgba(14,165,233,0.10);">\n'
            f'{keys_html}\n'
            f'<span style="color:var(--text-secondary);font-size:0.82rem;">{desc}</span>\n'
            f'</div>\n'
        )
    return f'<div style="padding:6px 0;">{text}</div>'


def _get_title(tree, default="Title"):
    """Extract title from first non-component item, stripping 'Title: ' prefix."""
    if tree and tree[0]["component"] is None:
        t = tree[0]["text"]
        if t.startswith("Title: "):
            return t[7:]
        return t
    return default


def _get_subtitle(tree):
    """Extract subtitle from second tree item."""
    for item in tree[1:]:
        if item["component"] is None:
            t = item["text"]
            if t.startswith("Subtitle: "):
                return t[10:]
            return t
    return ""


def build_slide_html(si):
    """Build slide HTML from the component tree, matching backup template structure."""
    tree = si.get("tree", [])
    slide_type = si["type"].lower()

    # Cover slide (slide 1)
    if slide_type == "cover" and si["number"] == 1:
        title = _get_title(tree, "AI 驱动的<br>HTML 演示文稿")
        subtitle = _get_subtitle(tree)
        return f"""  <!-- ══════════════════════════════════════════
       01 — COVER
       ══════════════════════════════════════════ -->
  <section class="slide cover" style="overflow:hidden;" data-notes="欢迎！slide-creator 从提示词生成精美的 HTML 演示文稿 — 零依赖，浏览器原生。21 个主题，单文件输出。">

    <svg width="0" height="0" style="position:absolute;pointer-events:none;">
      <defs>
        <filter id="cloud-filter">
          <feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="4" seed="5" result="noise"/>
          <feDisplacementMap in="SourceGraphic" in2="noise" scale="60" xChannelSelector="R" yChannelSelector="G"/>
        </filter>
      </defs>
    </svg>

    <div style="position:absolute;width:50%;height:60%;top:5%;left:-10%;border-radius:50%;background:rgba(96,165,250,0.28);filter:blur(90px);pointer-events:none;z-index:1;"></div>
    <div style="position:absolute;width:55%;height:65%;top:8%;right:-12%;border-radius:50%;background:rgba(14,165,233,0.22);filter:blur(100px);pointer-events:none;z-index:1;"></div>
    <div style="position:absolute;width:35%;height:40%;bottom:32%;left:30%;border-radius:50%;background:rgba(99,102,241,0.18);filter:blur(80px);pointer-events:none;z-index:1;"></div>

    <div class="cloud-layer" style="filter:url(#cloud-filter);">
      <div class="cloud-strip">
        <div style="position:relative;width:1920px;height:100%;flex-shrink:0;">
          <div class="cloud-group" style="left:192px;bottom:-54px;width:576px;height:216px;opacity:0.65;">
            <div class="cloud-puff" style="bottom:0;left:10%;width:288px;height:288px;filter:blur(18px);"></div>
            <div class="cloud-puff" style="bottom:22px;left:30%;width:384px;height:384px;filter:blur(22px);"></div>
            <div class="cloud-puff" style="bottom:-22px;left:60%;width:346px;height:346px;filter:blur(18px);"></div>
          </div>
          <div class="cloud-group" style="left:1100px;bottom:-86px;width:480px;height:194px;opacity:0.5;">
            <div class="cloud-puff" style="bottom:0;left:0%;width:230px;height:230px;filter:blur(14px);"></div>
            <div class="cloud-puff" style="bottom:32px;left:40%;width:346px;height:346px;filter:blur(20px);"></div>
            <div class="cloud-puff" style="bottom:11px;left:70%;width:288px;height:288px;filter:blur(16px);"></div>
          </div>
        </div>
        <div style="position:relative;width:1920px;height:100%;flex-shrink:0;">
          <div class="cloud-group" style="left:192px;bottom:-54px;width:576px;height:216px;opacity:0.65;">
            <div class="cloud-puff" style="bottom:0;left:10%;width:288px;height:288px;filter:blur(18px);"></div>
            <div class="cloud-puff" style="bottom:22px;left:30%;width:384px;height:384px;filter:blur(22px);"></div>
            <div class="cloud-puff" style="bottom:-22px;left:60%;width:346px;height:346px;filter:blur(18px);"></div>
          </div>
          <div class="cloud-group" style="left:1100px;bottom:-86px;width:480px;height:194px;opacity:0.5;">
            <div class="cloud-puff" style="bottom:0;left:0%;width:230px;height:230px;filter:blur(14px);"></div>
            <div class="cloud-puff" style="bottom:32px;left:40%;width:346px;height:346px;filter:blur(20px);"></div>
            <div class="cloud-puff" style="bottom:11px;left:70%;width:288px;height:288px;filter:blur(16px);"></div>
          </div>
        </div>
      </div>
      <div class="cloud-strip fast" style="z-index:2;">
        <div style="position:relative;width:1920px;height:100%;flex-shrink:0;">
          <div class="cloud-group" style="left:580px;bottom:-70px;width:420px;height:170px;opacity:0.42;">
            <div class="cloud-puff" style="bottom:0;left:5%;width:200px;height:200px;filter:blur(12px);"></div>
            <div class="cloud-puff" style="bottom:20px;left:35%;width:300px;height:300px;filter:blur(16px);"></div>
            <div class="cloud-puff" style="bottom:-15px;left:65%;width:250px;height:250px;filter:blur(13px);"></div>
          </div>
        </div>
        <div style="position:relative;width:1920px;height:100%;flex-shrink:0;">
          <div class="cloud-group" style="left:580px;bottom:-70px;width:420px;height:170px;opacity:0.42;">
            <div class="cloud-puff" style="bottom:0;left:5%;width:200px;height:200px;filter:blur(12px);"></div>
            <div class="cloud-puff" style="bottom:20px;left:35%;width:300px;height:300px;filter:blur(16px);"></div>
            <div class="cloud-puff" style="bottom:-15px;left:65%;width:250px;height:250px;filter:blur(13px);"></div>
          </div>
        </div>
      </div>
    </div>

    <div style="text-align:center;position:relative;z-index:10;">
      <span class="pill" style="margin-bottom:20px;display:inline-block;">slide-creator v2.14</span>
      <h1 class="gt" style="margin-bottom:14px;">{title}</h1>
      <p style="font-size:1.1rem;max-width:560px;margin:0 auto 28px;">
        {subtitle}
      </p>
      <div style="display:flex;gap:14px;justify-content:center;flex-wrap:wrap;">
        <div class="g" style="padding:16px 28px;text-align:center;">
          <div class="stat" style="font-size:2.8rem;">21</div>
          <p style="font-size:0.78rem;margin-top:2px;">主题</p>
        </div>
        <div class="g" style="padding:16px 28px;text-align:center;">
          <div class="stat" style="font-size:2.8rem;">0</div>
          <p style="font-size:0.78rem;margin-top:2px;">依赖</p>
        </div>
        <div class="g" style="padding:16px 28px;text-align:center;">
          <div class="stat" style="font-size:2.8rem;">1</div>
          <p style="font-size:0.78rem;margin-top:2px;">HTML 文件</p>
        </div>
      </div>
    </div>
  </section>"""

    # Content slides
    title = _get_title(tree)
    body_items = tree[1:] if tree and tree[0]["component"] is None else tree

    # Extract first pill from body if present
    pill_html = ""
    body_to_render = body_items
    if body_items and body_items[0]["component"] == "pill":
        pill_html = f'<span class="pill" style="margin-bottom:14px;display:inline-block;">{body_items[0]["text"]}</span>\n      '
        body_to_render = body_items[1:]

    # Check if the first non-pill item is a layout component (cols2/3/4)
    # If so, wrap layers in a flex column container
    body_html = _render_body(body_to_render)

    return f"""  <!-- ══════════════════════════════════════════
       {str(si['number']).zfill(2)} — {title.upper()}
       ══════════════════════════════════════════ -->
  <section class="slide" data-notes="{_get_notes(si)}">
    <div style="max-width:860px;width:100%;">
      {pill_html}<h2 class="gt">{title}</h2>
      <div class="divider"></div>
      {body_html}
    </div>
  </section>"""


def _get_notes(si):
    """Get speaker notes for a slide."""
    notes_map = {
        2: "解释传统幻灯片工具的摩擦点。让对比表发言 — 停留在 PPTX 兼容性和图表更新的痛点。",
        3: "三个命令：--plan 生成可编辑的结构化大纲。--generate 将大纲转换为样式化的 HTML。",
        4: "21 个主题跨越 4 个类别 — 内容类型路由自动建议最适合的。Blue Sky 和 Aurora Mesh 对业务内容最通用。",
        5: "单个 HTML 文件：内联 CSS、内联 JS、无 CDN。离线工作，可作为附件发送，在任何浏览器中打开。",
        6: "演示：将鼠标悬停在左上角以显示编辑按钮。单击任何文本可实时编辑。Ctrl+S 保存。",
        7: "按 F5 或点击 ▶ 按钮进入演示模式。幻灯片缩放以填充任何屏幕。按 P 打开演示者窗口。",
        8: "行动呼吁：在 Claude Code 中输入 /slide-creator 以开始使用。",
    }
    return notes_map.get(si["number"], "")


def _render_body(items):
    """Render body items with proper layout wrapping."""
    BLOCK_COMPONENTS = ("cols2", "cols3", "cols4", "bento", "info", "co", "cmd", "gt")

    def _is_block(item):
        if item["component"] in BLOCK_COMPONENTS:
            return True
        if item["component"] is None:
            return False
        return False

    def _render_item(item):
        if item["component"] == "layer":
            return _render_children([item])
        elif item["component"] in ("cols2", "cols3", "cols4", "bento"):
            return _render_children([item])
        elif item["component"] in ("info", "co", "cmd", "gt", "pill"):
            return _render_children([item])
        elif item["component"] is None:
            if item["children"]:
                return _render_children(item["children"])
            return _render_inline_bold(item["text"])
        else:
            return _render_children([item])

    parts = []
    i = 0
    while i < len(items):
        item = items[i]

        if item["component"] == "layer":
            # Collect consecutive layers
            layers = [item]
            j = i + 1
            while j < len(items) and items[j]["component"] == "layer":
                layers.append(items[j])
                j += 1
            layer_parts = [_render_children([ly]) for ly in layers]
            nl = "\n"
            parts.append(f'<div style="display:flex;flex-direction:column;gap:11px;">{nl}{nl.join(layer_parts)}{nl}</div>')
            i = j
        elif item["component"] in ("cols2", "cols3", "cols4", "bento"):
            # Collect consecutive block elements (cols + info/co)
            blocks = [item]
            j = i + 1
            while j < len(items) and items[j]["component"] in ("cols2", "cols3", "cols4", "bento", "info", "co", "cmd"):
                blocks.append(items[j])
                j += 1
            rendered_parts = [_render_item(b) for b in blocks]
            if len(rendered_parts) == 1:
                parts.append(rendered_parts[0])
            else:
                nl = "\n"
                parts.append(f'<div style="display:flex;flex-direction:column;gap:14px;">{nl}{nl.join(rendered_parts)}{nl}</div>')
            i = j
        elif item["component"] in ("info", "co", "cmd", "gt", "pill"):
            parts.append(_render_item(item))
            i += 1
        elif item["component"] is None:
            if item["children"]:
                parts.append(_render_children(item["children"]))
            else:
                parts.append(_render_inline_bold(item["text"]))
            i += 1
        else:
            parts.append(_render_children([item]))
            i += 1

    return "\n".join(parts)


def generate():
    output = None
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--output" and i + 1 < len(args):
            output = args[i + 1]
            i += 2
        else:
            i += 1

    planning = os.path.join(ROOT, "PLANNING.md")
    if not os.path.exists(planning):
        print(f"ERROR: {planning} not found. Run --plan first.")
        sys.exit(1)

    starter = os.path.join(ROOT, "references/blue-sky-starter.html")
    if not os.path.exists(starter):
        print(f"ERROR: {starter} not found.")
        sys.exit(1)

    if not output:
        output = os.path.join(ROOT, "output.html")

    slides_info = parse_planning(planning)
    if not slides_info:
        print("ERROR: No slides found in PLANNING.md")
        sys.exit(1)

    slide_count = len(slides_info)
    base_html = read_file(starter)

    # ── Step 1: Update slide count ──
    html = re.sub(r"--slide-count:\s*\d+", f"--slide-count: {slide_count}", base_html)

    # ── Step 2: Build slides ──
    new_slides = []
    for si in slides_info:
        new_slides.append(build_slide_html(si))

    # ── Step 3: Replace slides in #track ──
    track_pattern = re.compile(r'(<div id="track">)(.*?)(</div><!-- /#track -->)', re.DOTALL)
    slides_html = "\n\n".join(new_slides)
    html = track_pattern.sub(f'\\1\n\n{slides_html}\n\n  </div><!-- /#track -->', html)

    # ── Step 4: Update slide counter text ──
    html = re.sub(r'SLIDE \d+ / \d+', f'SLIDE 1 / {slide_count}', html)

    # ── Step 5: Update orbPositions array ──
    orb_positions = []
    for si in slides_info:
        slide_type = si["type"].lower()
        if slide_type == "cover":
            orb_positions.append([-15, -20, 500, 80, -10, 400, 50, 65, 350])
        else:
            orb_positions.append([-20, 40, 460, 75, -15, 400, 55, 70, 300])

    orb_array = re.compile(r"const orbPositions = \[.*?\];", re.DOTALL)
    orb_entries = []
    for pos in orb_positions:
        orb_entries.append(f"  [{', '.join(str(x) for x in pos)}]")
    html = orb_array.sub("const orbPositions = [\n" + ",\n".join(orb_entries) + "\n];", html)

    # ── Step 6: Write ──
    with open(output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated {output} ({slide_count} slides, Blue Sky preset)")


if __name__ == "__main__":
    generate()
