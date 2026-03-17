#!/usr/bin/env python3
"""
validate.py — Quality validator for slide-creator HTML output.

Use this before publishing a major version or after modifying the skill.
Checks a generated presentation against the full slide-creator standard.

Usage:
    python tests/validate.py path/to/presentation.html
    python tests/validate.py demos/aurora-mesh.html --strict

Exit codes:
    0  all checks passed
    1  one or more checks failed
    2  file not found

Checks (--strict enables all):
  REQUIRED (always run):
    - .slide elements present (>= 3 for a full deck)
    - viewport: height: 100vh in CSS
    - overflow: hidden in CSS for .slide
    - self-contained: no external script src or http stylesheet links
    - minimum file size (> 10 KB signals real content)
    - HTML structure: doctype, html, body, style tags present
    - no raw markdown: no ## ** __ in slide text nodes

  RECOMMENDED (--strict):
    - keyboard nav: ArrowLeft / ArrowRight in JS
    - edit mode: hotzone + contenteditable + saveFile
    - data-notes: each slide has a non-empty data-notes attribute
    - visual variety: not all slides use the same layout class

Requires: pip install beautifulsoup4
"""

import sys
import re
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependency. Install with:  pip install beautifulsoup4")
    sys.exit(2)


# ─── Individual check functions ───────────────────────────────────────────────

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


def check_self_contained(soup, content, warnings) -> tuple[bool, str]:
    external_scripts = soup.find_all("script", src=True)
    external_links = [
        t for t in soup.find_all("link", href=True)
        if str(t.get("href", "")).startswith("http")
    ]
    issues = []
    if external_scripts:
        issues.append(f"{len(external_scripts)} external <script src>")
    if external_links:
        issues.append(f"{len(external_links)} external <link href>")
    if issues:
        return False, "Not self-contained: " + ", ".join(issues)
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
    has_hotzone = bool(soup.find(id="hotzone"))
    scripts = " ".join(s.string or "" for s in soup.find_all("script"))
    has_contenteditable = "contenteditable" in scripts
    has_save = "saveFile" in scripts or "save-file" in scripts
    missing = []
    if not has_hotzone:
        missing.append("hotzone element")
    if not has_contenteditable:
        missing.append("contenteditable")
    if not has_save:
        missing.append("saveFile function")
    if missing:
        return False, "Edit mode incomplete: missing " + ", ".join(missing)
    return True, "Edit mode present (hotzone + contenteditable + saveFile)"


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


def check_visual_variety(soup, content, warnings) -> tuple[bool, str]:
    """Flag if too many consecutive slides share the same layout class."""
    slides = soup.find_all(class_="slide")
    if len(slides) < 4:
        return True, "Too few slides to check visual variety"

    # Extract the first non-'slide' class as the layout indicator
    def layout(slide):
        classes = [c for c in slide.get("class", []) if c != "slide"]
        return classes[0] if classes else "default"

    layouts = [layout(s) for s in slides]
    max_run = 1
    run = 1
    for i in range(1, len(layouts)):
        if layouts[i] == layouts[i - 1]:
            run += 1
            max_run = max(max_run, run)
        else:
            run = 1

    if max_run >= 4:
        return False, f"Low visual variety: {max_run} consecutive slides with same layout"
    if max_run >= 3:
        warnings.append(f"{max_run} consecutive slides with same layout class")
    return True, f"Visual variety OK (max run: {max_run})"


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
    check_data_notes,
    check_visual_variety,
]

GREEN = "\033[32m"
RED   = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"
BOLD  = "\033[1m"


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
        icon = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        print(f"  {icon}  {message}")

    for w in warnings:
        print(f"  {YELLOW}⚠{RESET}  {w}")

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
