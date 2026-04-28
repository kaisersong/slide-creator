#!/usr/bin/env python3
"""
validate_html.py — Quality validator for slide-creator HTML output.

Use this before publishing a major version or after modifying the skill.
Checks a generated presentation against the full slide-creator standard.

Usage:
    python scripts/validate_html.py path/to/presentation.html
    python scripts/validate_html.py demos/aurora-mesh.html --strict
    python tests/validate.py demos/aurora-mesh.html --strict   # compatibility wrapper

Exit codes:
    0  all checks passed
    1  one or more checks failed
    2  file not found

Checks (--strict enables all):
  REQUIRED (always run):
    - .slide elements present (>= 3 for a full deck)
    - viewport: height: 100vh in CSS
    - overflow: hidden in CSS for .slide
    - self-contained: no external script src or http stylesheet links (except Google Fonts)
    - minimum file size (> 10 KB signals real content)
    - HTML structure: doctype, html, body, style tags present
    - no raw markdown: no ## ** __ in slide text nodes

  RECOMMENDED (--strict):
    - keyboard nav: ArrowLeft / ArrowRight in JS
    - edit mode: edit-hotzone + contenteditable + saveFile
    - preset metadata: non-empty body[data-preset]
    - shared js-engine runtime: SlidePresentation + first-slide visible fix + presenter branch (non-Blue-Sky)
    - data-notes: each slide has a non-empty data-notes attribute
    - visual variety: not all slides use the same layout class
    - present mode: F5 listener + body.presenting CSS + PresentMode class
    - unicode: no U+FE0F variant selectors
    - watermark: JS-injected (heuristic check)
    - hero rhythm: no ≥3 consecutive hero pages
    - emoji: no emoji Unicode (recommend Lucide/SVG icons)

Requires: pip install beautifulsoup4
"""

import json
import sys
import re
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependency. Install with:  pip install beautifulsoup4")
    sys.exit(2)


def _discover_root() -> Path:
    file_value = globals().get("__file__")
    if file_value:
        return Path(file_value).resolve().parent.parent

    cwd = Path.cwd().resolve()
    candidates = [cwd, *cwd.parents]
    required = (
        ("scripts", "title_profiles.py"),
        ("references", "html-template.md"),
        ("tests", "validate.py"),
    )
    for candidate in candidates:
        if all((candidate / folder / leaf).exists() for folder, leaf in required):
            return candidate
    return cwd


ROOT = _discover_root()
SCRIPTS_DIR = ROOT / "scripts"
PRESET_USAGE_RULES = ROOT / "references" / "preset-usage-rules.json"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from title_profiles import (  # noqa: E402
    collect_title_candidate_nodes,
    detect_slide_layout_id,
    is_horizontal_title_profile,
    resolve_title_profile,
)


# ─── Individual check functions ───────────────────────────────────────────────


def _collect_css_text(soup) -> str:
    css_sources = [s.string or "" for s in soup.find_all("style")]
    css_sources.extend(tag.get("style", "") for tag in soup.find_all(style=True))
    return "\n".join(css_sources)


def _class_tokens(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(token) for token in value]
    return str(value).split()


def _has_exact_class(node, cls: str) -> bool:
    return bool(node.find(class_=lambda value, cls=cls: cls in _class_tokens(value)))


def _load_preset_usage_rules() -> dict:
    if not PRESET_USAGE_RULES.exists():
        return {}
    return json.loads(PRESET_USAGE_RULES.read_text(encoding="utf-8"))


def _preset_usage_rules(preset: str) -> dict:
    presets = _load_preset_usage_rules().get("presets", {})
    normalized = preset.strip().lower()
    for candidate, rules in presets.items():
        if candidate.strip().lower() == normalized:
            return rules
    return {}


def _normalize_ws(value: str) -> str:
    return re.sub(r"\s+", "", value)


def _extract_rule_blocks(css_text: str, selector: str) -> list[str]:
    pattern = re.compile(rf"{re.escape(selector)}\s*\{{(.*?)\}}", re.DOTALL)
    return [match.group(1) for match in pattern.finditer(css_text)]


def _selector_hidden_by_default(css_text: str, selector: str) -> bool:
    blocks = _extract_rule_blocks(css_text, selector)
    if not blocks:
        return False
    combined = " ".join(blocks).replace(" ", "").lower()
    hide_markers = (
        "display:none",
        "visibility:hidden",
        "opacity:0",
        "transform:translatex(110%)",
        "transform:translatex(100%)",
        "transform:translatey(110%)",
        "transform:translatey(100%)",
    )
    return any(marker in combined for marker in hide_markers)


def _body_preset(soup) -> str:
    body = soup.find("body")
    if not body:
        return ""
    return str(body.get("data-preset", "")).strip()


def _mask_js_comments_and_strings(source: str) -> str:
    """Mask JS comments and string contents so structural regexes ignore spoof text."""
    result: list[str] = []
    i = 0
    state = "code"
    quote = ""

    while i < len(source):
        ch = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ""

        if state == "code":
            if ch == "/" and nxt == "/":
                result.extend([" ", " "])
                i += 2
                state = "line_comment"
                continue
            if ch == "/" and nxt == "*":
                result.extend([" ", " "])
                i += 2
                state = "block_comment"
                continue
            if ch in ("'", '"', "`"):
                result.append(" ")
                i += 1
                state = "string"
                quote = ch
                continue
            result.append(ch)
            i += 1
            continue

        if state == "line_comment":
            if ch == "\n":
                result.append("\n")
                i += 1
                state = "code"
            else:
                result.append(" ")
                i += 1
            continue

        if state == "block_comment":
            if ch == "*" and nxt == "/":
                result.extend([" ", " "])
                i += 2
                state = "code"
            else:
                result.append("\n" if ch == "\n" else " ")
                i += 1
            continue

        # string
        if ch == "\\":
            result.append(" ")
            i += 1
            if i < len(source):
                result.append("\n" if source[i] == "\n" else " ")
                i += 1
            continue
        if ch == quote:
            result.append(" ")
            i += 1
            state = "code"
            quote = ""
            continue
        result.append("\n" if ch == "\n" else " ")
        i += 1

    return "".join(result)


def _has_active_raw_match(source: str, masked: str, pattern: str, code_prefix: str, flags: int = 0) -> bool:
    """Return True only when a raw regex match starts in actual code, not comments/strings."""
    expected = _normalize_ws(code_prefix)
    for match in re.finditer(pattern, source, flags):
        snippet = masked[match.start():match.start() + len(code_prefix)]
        if _normalize_ws(snippet) == expected:
            return True
    return False


def _direct_child_classes(node) -> set[str]:
    classes = set()
    for child in node.children:
        if getattr(child, "name", None):
            classes.update(_class_tokens(child.get("class", [])))
    return classes


def _defined_css_vars(css_text: str) -> set[str]:
    return {
        match.group(1)
        for match in re.finditer(r"(?<![a-zA-Z0-9_-])(--[a-zA-Z0-9_-]+)\s*:", css_text)
    }


def _missing_required_vars(css_text: str, required: list[str]) -> list[str]:
    defined = _defined_css_vars(css_text)
    return [token for token in required if token not in defined]


def _normalize_inline_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _title_visual_units(text: str) -> float:
    units = 0.0
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9%&+/#._:-]*|[\u3400-\u9fff]|[^\w\s]", text)
    for token in tokens:
        if re.fullmatch(r"[\u3400-\u9fff]", token):
            units += 1.0
        elif re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9%&+/#._:-]*", token):
            units += min(max(len(token) * 0.56, 1.0), 4.2)
        else:
            units += 0.25
    return round(units, 2)


def _is_title_line_class(token: str) -> bool:
    token = token.strip().lower()
    return token in {
        "title-line",
        "headline-line",
        "heading-line",
        "cta-line",
        "balance-line",
        "quote-line",
        "pull-line",
    }


def _extract_title_lines(node) -> list[str]:
    explicit_children = []
    for child in node.find_all(recursive=False):
        if not getattr(child, "name", None):
            continue
        classes = _class_tokens(child.get("class", []))
        if any(_is_title_line_class(token) for token in classes):
            explicit_children.append(child)

    if explicit_children:
        return [
            _normalize_inline_text(child.get_text(" ", strip=True))
            for child in explicit_children
            if _normalize_inline_text(child.get_text(" ", strip=True))
        ]

    if "<br" in str(node).lower():
        return [
            _normalize_inline_text(part)
            for part in re.split(r"\n+", node.get_text("\n", strip=True))
            if _normalize_inline_text(part)
        ]

    text = _normalize_inline_text(node.get_text(" ", strip=True))
    return [text] if text else []


def _is_orphan_title_line(text: str) -> bool:
    compact = re.sub(r"\s+", "", text)
    if not compact:
        return True
    if re.fullmatch(r"[\u3400-\u9fff]", compact):
        return True
    if re.fullmatch(r"[A-Za-z0-9%&+/#._:-]{1,3}", compact):
        return True
    return _title_visual_units(text) < 1.25 and len(compact) <= 3


def _has_collapsed_middle_line(units: list[float]) -> bool:
    if len(units) < 3:
        return False
    for index in range(1, len(units) - 1):
        longest_adjacent = max(units[index - 1], units[index + 1])
        shortest_adjacent = min(units[index - 1], units[index + 1])
        if units[index] <= longest_adjacent * 0.58 and units[index] + 1.8 <= shortest_adjacent:
            return True
    return False


def _is_globally_unbalanced_title(units: list[float]) -> bool:
    if len(units) < 2:
        return False
    longest = max(units)
    shortest = min(units)
    if longest <= 0:
        return False
    if len(units) == 2:
        return shortest <= longest * 0.48 and (longest - shortest) >= 3.0
    return shortest <= longest * 0.42 and (longest - shortest) >= 3.2


def _is_title_balance_exempt(node) -> bool:
    classes = set(_class_tokens(node.get("class", [])))
    if "zen-vertical-title" in classes:
        return True
    if "cyber-title" in classes or node.get("data-text"):
        return True
    return False


def _looks_like_risky_auto_wrap(node, slide, title_text: str) -> bool:
    units = _title_visual_units(title_text)
    if units < 14:
        return False

    style_tokens = []
    for current in (node, node.parent, getattr(node.parent, "parent", None)):
        if current and getattr(current, "name", None):
            style_tokens.append(str(current.get("style", "")))
    style_blob = " ".join(style_tokens).lower()
    has_width_constraint = "max-width" in style_blob or re.search(r"\b(?:10|11|12|13|14|15|16|17|18)ch\b", style_blob)

    slide_context = " ".join(_class_tokens(slide.get("class", []))).lower()
    display_context = any(
        hint in slide_context
        for hint in (
            "hero",
            "cover",
            "masthead",
            "pull",
            "quote",
            "cta",
            "close",
            "closing",
            "title_grid",
            "title-grid",
        )
    )

    return has_width_constraint or (display_context and units >= 22)


def _collect_role_issues(slides, valid_roles: set[str], warnings, preset: str) -> list[str]:
    issues = []
    missing = []
    for index, slide in enumerate(slides, start=1):
        role = slide.get("data-export-role", "").strip()
        if not role:
            missing.append(index)
            continue
        if role not in valid_roles:
            issues.append(f"slide {index}: invalid data-export-role '{role}'")
    if missing:
        warnings.append(
            f"{preset}: {len(missing)}/{len(slides)} slides missing data-export-role"
        )
    return issues

def check_slide_count(soup, content, warnings) -> tuple[bool, str]:
    slides = soup.find_all(class_="slide")
    n = len(slides)
    if n < 1:
        return False, f"No .slide elements found (0)"
    if n < 3:
        warnings.append(f"Only {n} slides — typical presentations have 5+")
    return True, f"{n} slides found"


def check_100vh(soup, content, warnings) -> tuple[bool, str]:
    style = " ".join(s.string or "" for s in soup.find_all("style"))
    has_100vh = "100vh" in style or "100dvh" in style
    if not has_100vh:
        return False, "CSS missing height: 100vh / 100dvh for slides"
    return True, "height: 100vh present"


def check_overflow_hidden(soup, content, warnings) -> tuple[bool, str]:
    style = " ".join(s.string or "" for s in soup.find_all("style"))
    has_overflow = "overflow: hidden" in style or "overflow:hidden" in style
    if not has_overflow:
        return False, "CSS missing overflow: hidden"
    return True, "overflow: hidden present"


def check_css_vars_defined(soup, content, warnings) -> tuple[bool, str]:
    """Fail when CSS uses custom properties that are never defined and have no fallback.

    This catches a common preset-fidelity failure mode where signature CSS is pasted
    into the deck, but the matching preset tokens were renamed or omitted.
    """
    css_text = _collect_css_text(soup)

    if "var(--" not in css_text:
        return True, "No CSS custom properties used"

    defined = _defined_css_vars(css_text)

    missing = set()
    for match in re.finditer(r"var\(\s*(--[a-zA-Z0-9_-]+)\s*(?:,([^)]*))?\)", css_text):
        var_name = match.group(1)
        fallback = match.group(2)
        if var_name not in defined and not (fallback and fallback.strip()):
            missing.add(var_name)

    if missing:
        sample = ", ".join(sorted(missing)[:6])
        if len(missing) > 6:
            sample += f" (+{len(missing) - 6} more)"
        return False, f"Undefined CSS variables used without fallback: {sample}"

    return True, f"All CSS variables resolved ({len(defined)} defined)"


def check_self_contained(soup, content, warnings) -> tuple[bool, str]:
    """Check for self-contained HTML (only Google Fonts external links allowed)."""
    external_scripts = soup.find_all("script", src=True)

    # Filter external stylesheets: allow Google Fonts, reject others
    external_styles = []
    for link in soup.find_all("link", href=True):
        href = str(link.get("href", ""))
        if href.startswith("http"):
            # Allow Google Fonts
            if "fonts.googleapis.com" in href or "fonts.gstatic.com" in href:
                continue
            external_styles.append(href)

    issues = []
    if external_scripts:
        issues.append(f"{len(external_scripts)} external <script src>")
    if external_styles:
        issues.append(f"{len(external_styles)} external <link href> (non-fonts)")

    if issues:
        return False, "Not self-contained: " + ", ".join(issues)

    # Check for Google Fonts links and report if present
    font_links = [l for l in soup.find_all("link", href=True)
                  if "fonts.googleapis.com" in str(l.get("href", ""))]
    if font_links:
        return True, f"Self-contained ({len(font_links)} Google Fonts links allowed)"
    return True, "Self-contained (no external dependencies)"


def check_file_size(soup, content, warnings) -> tuple[bool, str]:
    size = len(content.encode("utf-8"))
    if size < 5_000:
        return False, f"File too small ({size // 1000}KB) — likely incomplete"
    if size < 10_000:
        warnings.append(f"Small file ({size // 1000}KB) — check for missing content")
    return True, f"File size: {size // 1000}KB"


def check_html_structure(soup, content, warnings) -> tuple[bool, str]:
    issues = []
    if "<!DOCTYPE" not in content[:50].upper():
        issues.append("missing <!DOCTYPE html>")
    if not soup.find("html"):
        issues.append("missing <html>")
    if not soup.find("body"):
        issues.append("missing <body>")
    if not soup.find("style"):
        issues.append("missing <style> (CSS should be inline)")
    if issues:
        return False, "HTML structure issues: " + ", ".join(issues)
    return True, "HTML structure valid"


def check_no_markdown(soup, content, warnings) -> tuple[bool, str]:
    """Slide text should use semantic HTML, not raw markdown syntax."""
    slides = soup.find_all(class_="slide")
    violations = []
    md_patterns = [
        (r"^#{1,6}\s", "heading markdown (#)"),
        (r"\*\*.+?\*\*", "bold markdown (**)"),
        (r"(?<!\*)\*(?!\*)(?!\s).+?(?<!\s)\*(?!\*)", "italic markdown (*)"),
        (r"__[^_]+__", "bold markdown (__)"),
    ]
    for i, slide in enumerate(slides):
        text = slide.get_text()
        for pattern, name in md_patterns:
            if re.search(pattern, text, re.MULTILINE):
                violations.append(f"slide {i+1}: {name}")
    if violations:
        return False, "Raw markdown in slide text: " + "; ".join(violations[:3])
    return True, "No raw markdown in slide text"


# ─── Strict (recommended) checks ──────────────────────────────────────────────

def check_keyboard_nav(soup, content, warnings) -> tuple[bool, str]:
    scripts = " ".join(s.string or "" for s in soup.find_all("script"))
    has_arrow = "ArrowLeft" in scripts or "ArrowRight" in scripts
    has_key = "keydown" in scripts or "keyup" in scripts
    if not (has_arrow and has_key):
        return False, "Keyboard navigation missing (ArrowLeft/ArrowRight keydown)"
    return True, "Keyboard navigation present"


def check_edit_mode(soup, content, warnings) -> tuple[bool, str]:
    """Check for edit hotzone and editor functionality."""
    has_hotzone = bool(soup.find(class_="edit-hotzone"))
    scripts = " ".join(s.string or "" for s in soup.find_all("script"))
    has_contenteditable = "contenteditable" in scripts
    has_save = "saveFile" in scripts or "save-file" in scripts
    missing = []
    if not has_hotzone:
        missing.append("edit-hotzone element")
    if not has_contenteditable:
        missing.append("contenteditable")
    if not has_save:
        missing.append("saveFile function")
    if missing:
        return False, "Edit mode incomplete: missing " + ", ".join(missing)
    return True, "Edit mode present (edit-hotzone + contenteditable + saveFile)"


def check_default_hidden_chrome(soup, content, warnings) -> tuple[bool, str]:
    css_text = _collect_css_text(soup)
    visible = []
    if soup.select_one("#notes-panel") and not _selector_hidden_by_default(css_text, "#notes-panel"):
        visible.append("notes-panel")
    if soup.select_one("#editToggle") and not _selector_hidden_by_default(css_text, ".edit-toggle"):
        visible.append("edit-toggle")

    if visible:
        return False, "Default-visible editing chrome: " + ", ".join(visible)
    return True, "Editing chrome hidden by default"


def check_preset_metadata(soup, content, warnings) -> tuple[bool, str]:
    body = soup.find("body")
    if not body:
        return False, "Preset metadata missing: <body> not found"

    preset = str(body.get("data-preset", "")).strip()
    if not preset:
        return False, "Preset metadata missing: body[data-preset] is required"
    if preset == "Preset Name":
        return False, "Preset metadata unresolved: body[data-preset] still uses template placeholder"
    return True, f"Preset metadata present ({preset})"


def check_shared_js_engine_contract(soup, content, warnings) -> tuple[bool, str]:
    """Enforce the non-Blue-Sky shared runtime from references/js-engine.md."""
    preset = _body_preset(soup)
    if not preset:
        return True, "Shared js-engine contract not applicable (missing data-preset)"
    if preset.lower() == "blue sky":
        return True, "Shared js-engine contract not applicable (Blue Sky)"

    scripts = "\n".join(s.string or "" for s in soup.find_all("script"))
    if not scripts.strip():
        return False, "Shared js-engine contract missing: no inline runtime script found"
    masked = _mask_js_comments_and_strings(scripts)

    has_slide_presentation_class = bool(re.search(r"\bclass\s+SlidePresentation\b", masked))
    has_slide_collection = bool(re.search(
        r"\bthis\.slides\s*=\s*document\.querySelectorAll\s*\(",
        masked,
    ))
    has_first_slide_visible = _has_active_raw_match(
        scripts,
        masked,
        r"slides\s*\[\s*0\s*]\s*(?:\?\.)?\s*classList\.add\s*\(\s*['\"]visible['\"]\s*\)",
        "slides[0",
    )
    has_first_reveal_visible = _has_active_raw_match(
        scripts,
        masked,
        r"slides\s*\[\s*0\s*]\s*(?:\?\.)?\s*querySelectorAll\s*\(\s*['\"]\.reveal['\"]\s*\)"
        r".*?classList\.add\s*\(\s*['\"]visible['\"]\s*\)",
        "slides[0",
        flags=re.DOTALL,
    )
    reveal_toggle_patterns = (
        r"querySelectorAll\s*\(\s*['\"]\.reveal['\"]\s*\)\s*"
        r"\.\s*forEach\s*\(\s*function\s*\([^)]*\)\s*\{[^}]*"
        r"classList\.toggle\s*\(\s*['\"]visible['\"]",
        r"querySelectorAll\s*\(\s*['\"]\.reveal['\"]\s*\)\s*"
        r"\.\s*forEach\s*\(\s*[A-Za-z_$][\w$]*\s*=>\s*[A-Za-z_$][\w$]*"
        r"\.classList\.toggle\s*\(\s*['\"]visible['\"]",
        r"querySelectorAll\s*\(\s*['\"]\.reveal['\"]\s*\)\s*"
        r"\.\s*forEach\s*\(\s*\([^)]*\)\s*=>\s*\{[^}]*"
        r"classList\.toggle\s*\(\s*['\"]visible['\"]",
    )
    has_reveal_toggle_runtime = any(
        _has_active_raw_match(scripts, masked, pattern, "querySelectorAll(", flags=re.DOTALL)
        for pattern in reveal_toggle_patterns
    )
    has_broadcast_channel_sync = _has_active_raw_match(
        scripts,
        masked,
        r"new\s+BroadcastChannel\s*\(\s*['\"]slide-creator-presenter['\"]\s*\)",
        "new BroadcastChannel(",
    )
    has_observer_runtime = bool(re.search(r"\bsetupObserver\s*\(\s*\)\s*\{", masked)) and "IntersectionObserver" in masked
    has_presenter_runtime = bool(re.search(r"\bsetupPresenter\s*\(\s*\)\s*\{", masked))
    has_editor_runtime = bool(re.search(r"\bsetupEditor\s*\(\s*\)\s*\{", masked))
    has_wheel_bootstrap = _has_active_raw_match(
        scripts,
        masked,
        r"\bthis\.setupWheel\s*\(\s*\)",
        "this.setupWheel(",
    )
    has_wheel_runtime = bool(re.search(r"\bsetupWheel\s*\(\s*\)\s*\{", masked)) and (
        ("addEventListener('wheel'" in scripts or 'addEventListener("wheel"' in scripts)
        and "wState" in scripts
        and "wLastTime" in scripts
        and ("addEventListener('scroll'" in scripts or 'addEventListener("scroll"' in scripts or "scrollend" in scripts)
        and "wheelLocked" not in scripts
    )
    has_presenter_branch = _has_active_raw_match(
        scripts,
        masked,
        r"new\s+URLSearchParams\s*\(\s*location\.search\s*\)\.has\s*\(\s*['\"]presenter['\"]\s*\)",
        "new URLSearchParams(",
    )
    has_present_mode_class = bool(re.search(r"\bclass\s+PresentMode\b", masked))
    has_present_mode_bootstrap = bool(re.search(
        r"new\s+PresentMode\s*\(\s*new\s+SlidePresentation\s*\(\s*\)\s*\)",
        masked,
    ))
    has_watermark_target = bool(re.search(
        r"slides\s*\[\s*slides\.length\s*-\s*1\s*]",
        masked,
    )) and "appendChild" in masked
    has_watermark_class = _has_active_raw_match(
        scripts,
        masked,
        r"\.className\s*=\s*['\"]slide-credit['\"]",
        ".className",
    )

    checks = [
        ("SlidePresentation class", has_slide_presentation_class),
        ("slide collection init", has_slide_collection),
        ("BroadcastChannel sync", has_broadcast_channel_sync),
        ("IntersectionObserver runtime", has_observer_runtime),
        ("setupPresenter runtime", has_presenter_runtime),
        ("setupEditor runtime", has_editor_runtime),
        ("wheel bootstrap", has_wheel_bootstrap),
        ("wheel pagination runtime", has_wheel_runtime),
        ("first-slide visible fix", has_first_slide_visible and has_first_reveal_visible),
        ("reveal toggle runtime", has_reveal_toggle_runtime),
        ("?presenter branch", has_presenter_branch),
        ("PresentMode class", has_present_mode_class),
        ("PresentMode bootstrap", has_present_mode_bootstrap),
        ("watermark injection", has_watermark_target and has_watermark_class),
    ]

    missing = [label for label, ok in checks if not ok]
    if missing:
        sample = ", ".join(missing[:4])
        if len(missing) > 4:
            sample += f" (+{len(missing) - 4} more)"
        return False, f"Shared js-engine contract incomplete: missing {sample}"

    return True, "Shared js-engine runtime present"


def check_data_notes(soup, content, warnings) -> tuple[bool, str]:
    slides = soup.find_all(class_="slide")
    if not slides:
        return True, "No slides to check"
    with_notes = [s for s in slides if s.get("data-notes", "").strip()]
    ratio = len(with_notes) / len(slides)
    if ratio == 0:
        return False, f"No slides have data-notes (0/{len(slides)})"
    if ratio < 0.5:
        warnings.append(f"Only {len(with_notes)}/{len(slides)} slides have data-notes")
    return True, f"data-notes present on {len(with_notes)}/{len(slides)} slides"


def check_swiss_modern_contract(soup, content, warnings) -> tuple[bool, str]:
    body = soup.find("body")
    if not body or body.get("data-preset", "").strip() != "Swiss Modern":
        return True, "Swiss Modern contract not applicable"

    css_text = _collect_css_text(soup)

    issues = []

    alias_tokens = [
        "--bg-primary",
        "--bg-secondary",
        "--text-primary",
        "--text-secondary",
        "--accent",
    ]
    found_alias_tokens = [token for token in alias_tokens if token in css_text]
    if found_alias_tokens:
        issues.append("legacy token aliases " + ", ".join(found_alias_tokens[:5]))

    compatible_alias_classes = [
        "left-col",
        "right-col",
        "stat-block",
        "content-block",
        "quote-block",
    ]
    found_alias_classes = [
        cls for cls in compatible_alias_classes
        if _has_exact_class(soup, cls)
    ]
    if found_alias_classes:
        issues.append("compatible aliases " + ", ".join(found_alias_classes))

    for index, slide in enumerate(soup.find_all(class_="slide"), start=1):
        direct_child_classes = _direct_child_classes(slide)

        for cls in ("left-panel", "right-panel", "bg-num", "slide-num-label"):
            if _has_exact_class(slide, cls) and cls not in direct_child_classes:
                issues.append(f"slide {index}: .{cls} must be a direct child of .slide")
                break

        if not slide.get("data-export-role", "").strip():
            warnings.append(f"slide {index}: Swiss Modern slide missing data-export-role")

    if issues:
        sample = "; ".join(issues[:3])
        if len(issues) > 3:
            sample += f" (+{len(issues) - 3} more)"
        return False, f"Swiss Modern contract violations: {sample}"

    return True, "Swiss Modern contract OK"


def check_enterprise_dark_contract(soup, content, warnings) -> tuple[bool, str]:
    body = soup.find("body")
    if not body or body.get("data-preset", "").strip() != "Enterprise Dark":
        return True, "Enterprise Dark contract not applicable"

    css_text = _collect_css_text(soup)
    issues = []

    missing_tokens = _missing_required_vars(css_text, [
        "--bg-primary", "--bg-secondary", "--bg-header", "--border",
        "--text-primary", "--text-body", "--text-muted",
        "--accent-blue", "--accent-green", "--accent-red", "--accent-amber",
    ])
    if missing_tokens:
        issues.append("missing canonical tokens " + ", ".join(missing_tokens[:6]))

    alias_classes = [
        "label-tag", "kpi", "kpi-value", "kpi-label", "card", "badge",
        "status-dot", "sep", "code", "accent-blue", "accent-green",
        "accent-red", "accent-orange",
    ]
    found_alias_classes = [cls for cls in alias_classes if _has_exact_class(soup, cls)]
    if found_alias_classes:
        issues.append("generic alias classes " + ", ".join(found_alias_classes[:6]))

    slides = soup.find_all(class_="slide")
    issues.extend(_collect_role_issues(
        slides,
        {
            "kpi_dashboard", "consulting_split", "data_table",
            "architecture_map", "comparison_matrix", "insight_pull", "timeline", "cta_close",
        },
        warnings,
        "Enterprise Dark",
    ))

    for index, slide in enumerate(slides, start=1):
        direct_child_classes = _direct_child_classes(slide)
        if _has_exact_class(slide, "ent-split") and "ent-split" not in direct_child_classes:
            issues.append(f"slide {index}: .ent-split must be a direct child of .slide")
            break
        if _has_exact_class(slide, "slide-num-label") and "slide-num-label" not in direct_child_classes:
            issues.append(f"slide {index}: .slide-num-label must be a direct child of .slide")
            break

    if issues:
        sample = "; ".join(issues[:3])
        if len(issues) > 3:
            sample += f" (+{len(issues) - 3} more)"
        return False, f"Enterprise Dark contract violations: {sample}"

    return True, "Enterprise Dark contract OK"


def check_data_story_contract(soup, content, warnings) -> tuple[bool, str]:
    body = soup.find("body")
    if not body or body.get("data-preset", "").strip() != "Data Story":
        return True, "Data Story contract not applicable"

    css_text = _collect_css_text(soup)
    issues = []

    missing_tokens = _missing_required_vars(css_text, [
        "--bg", "--bg-card", "--border", "--text", "--text-muted",
        "--positive", "--negative", "--neutral",
        "--chart-primary", "--chart-secondary", "--chart-tertiary",
        "--grid-line", "--axis-line",
    ])
    if missing_tokens:
        issues.append("missing canonical tokens " + ", ".join(missing_tokens[:6]))

    alias_classes = [
        "kpi-number", "kpi-label", "kpi-trend", "kpi-grid", "kpi-card",
        "chart-layout", "eyebrow", "divider",
    ]
    found_alias_classes = [cls for cls in alias_classes if _has_exact_class(soup, cls)]
    if found_alias_classes:
        issues.append("generic alias classes " + ", ".join(found_alias_classes[:6]))

    chart_lib_markers = ["chart.js", "echarts", "highcharts", "apexcharts", "plotly", "d3."]
    found_markers = [marker for marker in chart_lib_markers if marker in content.lower()]
    if found_markers:
        issues.append("external chart libs " + ", ".join(found_markers))

    if ".slide::before" not in css_text and ".slide:before" not in css_text:
        issues.append("grid overlay must live on .slide::before")

    if "font-variant-numeric: tabular-nums" not in css_text and 'font-feature-settings: "tnum"' not in css_text:
        issues.append("tabular number styling missing")

    slides = soup.find_all(class_="slide")
    issues.extend(_collect_role_issues(
        slides,
        {"hero_number", "kpi_chart", "chart_insight", "comparison_matrix", "kpi_grid", "workflow_chart", "cta_close"},
        warnings,
        "Data Story",
    ))

    if issues:
        sample = "; ".join(issues[:3])
        if len(issues) > 3:
            sample += f" (+{len(issues) - 3} more)"
        return False, f"Data Story contract violations: {sample}"

    return True, "Data Story contract OK"


def check_glassmorphism_contract(soup, content, warnings) -> tuple[bool, str]:
    body = soup.find("body")
    if not body or body.get("data-preset", "").strip() != "Glassmorphism":
        return True, "Glassmorphism contract not applicable"

    css_text = _collect_css_text(soup)
    issues = []

    missing_tokens = _missing_required_vars(css_text, [
        "--bg-gradient-1", "--bg-gradient-2", "--bg-gradient-3",
        "--glass-bg", "--glass-border", "--glass-text-dark", "--glass-text-light",
        "--orb-purple", "--orb-pink", "--orb-mint",
    ])
    if missing_tokens:
        issues.append("missing canonical tokens " + ", ".join(missing_tokens[:6]))

    alias_classes = ["bg-cool", "bg-warm", "bg-mint", "dark-text", "light-text", "glass-grid", "glass-slide-center"]
    found_alias_classes = [cls for cls in alias_classes if _has_exact_class(soup, cls)]
    if found_alias_classes:
        issues.append("input-only helpers emitted " + ", ".join(found_alias_classes[:6]))

    if "backdrop-filter" not in css_text and "-webkit-backdrop-filter" not in css_text:
        issues.append("backdrop-filter glass cards missing")

    has_slide_backgrounds = bool(re.search(r"\.slide-\d+\s*\{[^}]*background\s*:", css_text, re.DOTALL))
    has_bg_modes = all(token in css_text for token in (".bg-cool", ".bg-warm", ".bg-mint"))
    if not has_slide_backgrounds and not has_bg_modes:
        issues.append("slide-owned gradient backgrounds missing")

    has_orb_element = any(_has_exact_class(soup, cls) for cls in ("orb", "orb1", "orb2", "orb3", "orb-1", "orb-2", "orb-3", "glass-orb"))
    if not has_orb_element:
        issues.append("blurred orb layers missing")

    slides = soup.find_all(class_="slide")
    issues.extend(_collect_role_issues(
        slides,
        {"glass_hero", "glass_card", "glass_split", "glass_trio", "glass_stat"},
        warnings,
        "Glassmorphism",
    ))

    if issues:
        sample = "; ".join(issues[:3])
        if len(issues) > 3:
            sample += f" (+{len(issues) - 3} more)"
        return False, f"Glassmorphism contract violations: {sample}"

    return True, "Glassmorphism contract OK"


def check_chinese_chan_contract(soup, content, warnings) -> tuple[bool, str]:
    body = soup.find("body")
    if not body or body.get("data-preset", "").strip() != "Chinese Chan":
        return True, "Chinese Chan contract not applicable"

    css_text = _collect_css_text(soup)
    issues = []
    usage_rules = _preset_usage_rules("Chinese Chan")
    title_component_by_layout = usage_rules.get("title_component_by_layout", {})

    missing_tokens = _missing_required_vars(css_text, [
        "--bg", "--text", "--text-muted", "--accent", "--accent-alt", "--rule",
    ])
    if missing_tokens:
        issues.append("missing canonical tokens " + ", ".join(missing_tokens[:6]))

    alias_classes = ["ghost-kanji", "flanked-rule", "vline", "col", "eyebrow", "accent"]
    found_alias_classes = [cls for cls in alias_classes if _has_exact_class(soup, cls)]
    if found_alias_classes:
        issues.append("input-only aliases emitted " + ", ".join(found_alias_classes[:6]))

    slides = soup.find_all(class_="slide")
    issues.extend(_collect_role_issues(
        slides,
        {"zen_center", "zen_split", "zen_vertical", "zen_stat"},
        warnings,
        "Chinese Chan",
    ))

    missing_roles = [index for index, slide in enumerate(slides, start=1) if not slide.get("data-export-role", "").strip()]
    if missing_roles:
        issues.append("missing data-export-role on one or more slides")

    for index, slide in enumerate(slides, start=1):
        role = slide.get("data-export-role", "").strip()
        direct_child_classes = _direct_child_classes(slide)
        if _has_exact_class(slide, "zen-ghost-kanji") and "zen-ghost-kanji" not in direct_child_classes:
            issues.append(f"slide {index}: .zen-ghost-kanji must be a direct child of .slide")
            break

        for elem in slide.find_all(class_=lambda value: "zen-ghost-kanji" in _class_tokens(value)):
            style = elem.get("style", "")
            centered_markers = ["left: 50%", "right: 50%", "top: 50%", "bottom: 50%", "translateX(-50%)", "translateY(-50%)"]
            if any(marker in style for marker in centered_markers):
                issues.append(f"slide {index}: .zen-ghost-kanji must stay off-center")
                break

        required_title_class = title_component_by_layout.get(role)
        if required_title_class and not _has_exact_class(slide, required_title_class):
            issues.append(f"slide {index}: {role} must use .{required_title_class} as the title component")
            break

    if issues:
        sample = "; ".join(issues[:3])
        if len(issues) > 3:
            sample += f" (+{len(issues) - 3} more)"
        return False, f"Chinese Chan contract violations: {sample}"

    return True, "Chinese Chan contract OK"


def check_visual_variety(soup, content, warnings) -> tuple[bool, str]:
    """Flag if too many consecutive slides share the same layout signature."""
    slides = soup.find_all(class_="slide")
    if len(slides) < 4:
        return True, "Too few slides to check visual variety"

    generic = {
        "slide", "slide-content", "content", "reveal", "visible", "bg-num",
        "slide-num-label", "light", "eyebrow", "swiss-rule", "swiss-rule-thin",
        "swiss-title", "swiss-body", "swiss-label", "swiss-stat",
    }

    slide_descendant_classes = []
    class_frequency = {}
    for slide in slides:
        classes = set()
        for node in slide.find_all(class_=True):
            for cls in node.get("class", []):
                if cls not in generic:
                    classes.add(cls)
        slide_descendant_classes.append(classes)
        for cls in classes:
            class_frequency[cls] = class_frequency.get(cls, 0) + 1

    shared_threshold = max(2, len(slides) // 2)

    def layout_signature(index, slide):
        section_classes = tuple(c for c in slide.get("class", []) if c != "slide")
        distinctive = sorted(
            cls for cls in slide_descendant_classes[index]
            if class_frequency.get(cls, 0) < shared_threshold
        )
        if distinctive:
            return tuple(distinctive[:8])
        if section_classes:
            return section_classes
        fallback = sorted(slide_descendant_classes[index])
        return tuple(fallback[:8]) if fallback else ("default",)

    layouts = [layout_signature(i, slide) for i, slide in enumerate(slides)]
    max_run = 1
    run = 1
    for i in range(1, len(layouts)):
        if layouts[i] == layouts[i - 1]:
            run += 1
            max_run = max(max_run, run)
        else:
            run = 1

    if max_run >= 3:
        return False, f"Low visual variety: {max_run} consecutive slides with same layout"
    if max_run >= 2:
        warnings.append(f"{max_run} consecutive slides with same layout signature")
    return True, f"Visual variety OK (max run: {max_run})"


def check_title_balance(soup, content, warnings) -> tuple[bool, str]:
    """Detect uncontrolled or visibly unbalanced multi-line slide titles."""
    slides = soup.find_all(class_="slide")
    if not slides:
        return True, "No slides found for title balance check"

    preset = _body_preset(soup)
    issues = []
    balanced_multiline_titles = 0

    for slide_index, slide in enumerate(slides, start=1):
        layout_id = detect_slide_layout_id(slide)
        title_nodes = collect_title_candidate_nodes(slide, preset)

        for title_index, node in enumerate(title_nodes, start=1):
            profile = resolve_title_profile(preset, layout_id=layout_id, node=node, slide=slide)
            if not is_horizontal_title_profile(profile["profile"]):
                continue

            lines = _extract_title_lines(node)
            if not lines:
                continue

            label = f"slide {slide_index} title {title_index}"
            if len(lines) >= 4:
                issues.append(f"{label}: wraps to {len(lines)} lines")
                continue

            if len(lines) == 1:
                if _looks_like_risky_auto_wrap(node, slide, lines[0]):
                    issues.append(f"{label}: long display title relies on auto-wrap")
                continue

            units = [_title_visual_units(line) for line in lines]
            orphan_line = next((line for line in lines if _is_orphan_title_line(line)), None)
            if orphan_line:
                issues.append(f"{label}: orphan line '{orphan_line}'")
                continue
            if _has_collapsed_middle_line(units):
                issues.append(f"{label}: collapsed middle line ({lines})")
                continue
            if _is_globally_unbalanced_title(units):
                issues.append(f"{label}: unbalanced title lines ({lines})")
                continue

            balanced_multiline_titles += 1

    if issues:
        sample = "; ".join(issues[:3])
        if len(issues) > 3:
            sample += f" (+{len(issues) - 3} more)"
        return False, f"Title balance violations: {sample}"

    return True, f"Title balance OK ({balanced_multiline_titles} controlled multi-line titles)"


def check_hero_rhythm(soup, content, warnings) -> tuple[bool, str]:
    """Check theme rhythm rules — detect consecutive hero pages."""
    slides = soup.find_all(class_="slide")
    if len(slides) < 3:
        return True, "Too few slides to check hero rhythm"

    hero_runs = []
    current_run = 0

    for slide in slides:
        classes = slide.get("class", [])
        is_hero = any("hero" in c for c in classes)

        if is_hero:
            current_run += 1
        else:
            if current_run >= 3:
                hero_runs.append(current_run)
            current_run = 0

    # Check last run
    if current_run >= 3:
        hero_runs.append(current_run)

    if hero_runs:
        warnings.append(f"Consecutive hero pages: {max(hero_runs)} (recommend ≤2)")
        return True, f"Hero rhythm warning: {max(hero_runs)} consecutive hero pages"

    return True, "Hero rhythm OK (no ≥3 consecutive hero pages)"


def check_emoji_usage(soup, content, warnings) -> tuple[bool, str]:
    """Check for pictorial emoji icons in raw HTML content (excluding decorative chars)."""
    import re

    # Emoji pictographs only (excluding box drawing / decorative characters / dingbats)
    # Focus on actual emoji icons that should use Lucide/SVG instead
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons (😀-🙏)
        "\U0001F300-\U0001F5FF"  # symbols & pictographs (🌀-🗿)
        "\U0001F680-\U0001F6FF"  # transport & map (🚀-🛿)
        "\U0001F1E0-\U0001F1FF"  # flags (🇦-🇿)
        "\U0001F900-\U0001F9FF"  # supplemental symbols (🤀-🧿)
        "\U0001FA70-\U0001FAFF"  # symbols extended-A (🥰-🧿)
        # Exclude: misc symbols (2600-26FF includes ☀☃⚠⚡), dingbats (2700-27BF includes ✏✎),
        # chess symbols (FA00-FA6F), box drawing (2500-257F), arrows (2190-21FF)
        "]+",
        flags=re.UNICODE
    )

    matches = emoji_pattern.findall(content)
    if matches:
        # Show first few emoji for debugging
        sample = matches[:3] if len(matches) <= 3 else matches[:3] + [f"({len(matches)-3} more)"]
        return False, f"Pictorial emoji detected: {sample} (recommend Lucide/SVG icons)"

    return True, "No pictorial emoji detected"


def check_present_mode(soup, content, warnings) -> tuple[bool, str]:
    """Check for present mode functionality (F5 + body.presenting CSS + PresentMode class)."""
    style = " ".join(s.string or "" for s in soup.find_all("style"))
    scripts = " ".join(s.string or "" for s in soup.find_all("script"))

    has_presenting_css = "body.presenting" in style
    has_f5_listener = "'F5'" in scripts or '"F5"' in scripts or "e.key === 'F5'" in scripts
    has_present_mode_class = "PresentMode" in scripts or "presentMode" in scripts.lower()

    missing = []
    if not has_presenting_css:
        missing.append("body.presenting CSS")
    if not has_f5_listener:
        missing.append("F5 key listener")
    if not has_present_mode_class:
        missing.append("PresentMode class/function")

    if missing:
        return False, "Present mode incomplete: missing " + ", ".join(missing)
    return True, "Present mode present (F5 + body.presenting CSS + PresentMode)"


def check_unicode_fe0f(soup, content, warnings) -> tuple[bool, str]:
    """Check for U+FE0F variant selector (emoji presentation modifier) in raw HTML."""
    if "️" in content:
        # Find positions for reporting
        positions = []
        idx = 0
        while idx < len(content):
            if content[idx] == "️":
                # Get surrounding context (up to 20 chars)
                start = max(0, idx - 10)
                end = min(len(content), idx + 10)
                context = content[start:end].replace("️", "⟨FE0F⟩")
                positions.append(f"near '{context}'")
                idx += 1
            else:
                idx += 1

        if positions:
            sample = positions[0] if len(positions) == 1 else f"{positions[0]} (and {len(positions)-1} more)"
            return False, f"U+FE0F variant selector found {sample}"
    return True, "No U+FE0F variant selectors"


def check_watermark_injection(soup, content, warnings) -> tuple[bool, str]:
    """Heuristic check for JS-injected watermark (not hardcoded in HTML body)."""
    # Check if hardcoded watermark exists outside script tags
    # Strip script content to check HTML structure
    hardcoded_watermark = False

    # Look for slide-credit div outside of script context
    for div in soup.find_all(class_="slide-credit"):
        # If it's in the actual DOM (not inside a script string), it's hardcoded
        parent = div.parent
        while parent:
            if parent.name == "script":
                break
            parent = parent.parent
        # If we didn't find a script parent, it's hardcoded in HTML
        if parent is None:
            hardcoded_watermark = True
            break

    if hardcoded_watermark:
        warnings.append("Watermark appears hardcoded in HTML - should be JS-injected")
        # Still pass, just warn - heuristic can't be 100% certain
        return True, "Watermark check: appears hardcoded (heuristic)"

    # Check for JS injection pattern
    scripts = " ".join(s.string or "" for s in soup.find_all("script"))
    has_js_injection = "slides[slides.length - 1]" in scripts and "slide-credit" in scripts
    unresolved_placeholders = "[version]" in scripts or "[preset-name]" in scripts

    if unresolved_placeholders:
        return False, "Watermark placeholder unresolved: version or preset name not substituted"

    if has_js_injection:
        return True, "Watermark appears JS-injected (heuristic)"

    # If no watermark found at all, that's OK for minimal decks
    return True, "Watermark not detected (heuristic)"


# ─── Runner ───────────────────────────────────────────────────────────────────

REQUIRED_CHECKS = [
    check_slide_count,
    check_100vh,
    check_overflow_hidden,
    check_self_contained,
    check_file_size,
    check_html_structure,
    check_no_markdown,
]

STRICT_CHECKS = [
    check_keyboard_nav,
    check_edit_mode,
    check_default_hidden_chrome,
    check_preset_metadata,
    check_shared_js_engine_contract,
    check_data_notes,
    check_swiss_modern_contract,
    check_enterprise_dark_contract,
    check_data_story_contract,
    check_glassmorphism_contract,
    check_chinese_chan_contract,
    check_title_balance,
    check_visual_variety,
    check_css_vars_defined,
    check_present_mode,
    check_unicode_fe0f,
    check_watermark_injection,
    check_hero_rhythm,
    check_emoji_usage,
]

GREEN = "\033[32m"
RED   = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"
BOLD  = "\033[1m"


def render_console_symbol(symbol: str, fallback: str, encoding: str | None = None) -> str:
    encoding = encoding or getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        symbol.encode(encoding)
    except UnicodeEncodeError:
        return fallback
    return symbol


def validate(html_path: str | Path, strict: bool = False) -> bool:
    path = Path(html_path)
    if not path.exists():
        print(f"{RED}File not found: {path}{RESET}")
        return False

    content = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(content, "html.parser")
    warnings = []

    checks = REQUIRED_CHECKS + (STRICT_CHECKS if strict else [])
    results = []

    for check_fn in checks:
        try:
            passed, message = check_fn(soup, content, warnings)
        except Exception as e:
            passed, message = False, f"Check error: {e}"
        results.append((passed, check_fn.__name__.replace("check_", ""), message))

    # Print results
    print(f"\n{BOLD}Validating:{RESET} {path.name}")
    print("─" * 60)
    for passed, name, message in results:
        if passed:
            glyph = render_console_symbol("✓", "OK")
            icon = f"{GREEN}{glyph}{RESET}"
        else:
            glyph = render_console_symbol("✗", "FAIL")
            icon = f"{RED}{glyph}{RESET}"
        print(f"  {icon}  {message}")

    for w in warnings:
        glyph = render_console_symbol("⚠", "WARN")
        print(f"  {YELLOW}{glyph}{RESET}  {w}")

    failed = [r for r in results if not r[0]]
    print("─" * 60)
    if failed:
        print(f"  {RED}{BOLD}{len(failed)} check(s) failed{RESET}")
    else:
        label = "strict" if strict else "required"
        print(f"  {GREEN}{BOLD}All {label} checks passed{RESET}")
    print()

    return len(failed) == 0


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("html", help="Path to HTML presentation to validate")
    parser.add_argument("--strict", action="store_true",
                        help="Also run recommended checks (edit mode, data-notes, keyboard nav)")
    args = parser.parse_args()

    if not Path(args.html).exists():
        print(f"File not found: {args.html}")
        sys.exit(2)

    ok = validate(args.html, strict=args.strict)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
