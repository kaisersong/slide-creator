#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent

THRESHOLDS = {
    "overall_pass_min": 0.72,
    "component_min": 0.50,
    "font_min": 0.60,
    "css_var_min": 0.50,
    "color_min_when_demo_has_colors": 0.35,
    "visual_warn_min": 0.75,
    "visual_fail_min": 0.55,
}

PRESETS = [
    ("Aurora Mesh", "aurora-mesh", "aurora-mesh-profile-render"),
    ("Bold Signal", "bold-signal", "bold-signal-profile-render"),
    ("Creative Voltage", "creative-voltage", "creative-voltage-profile-render"),
    ("Dark Botanical", "dark-botanical", "dark-botanical-profile-render"),
    ("Electric Studio", "electric-studio", "electric-studio-profile-render"),
    ("Glassmorphism", "glassmorphism", "glassmorphism-profile-render"),
    ("Modern Newspaper", "modern-newspaper", "modern-newspaper-profile-render"),
    ("Neo-Brutalism", "neo-brutalism", "neo-brutalism-profile-render"),
    ("Neo-Retro Dev Deck", "neo-retro-dev", "neo-retro-dev-deck-profile-render"),
    ("Neon Cyber", "neon-cyber", "neon-cyber-profile-render"),
    ("Notebook Tabs", "notebook-tabs", "notebook-tabs-profile-render"),
    ("Paper & Ink", "paper-ink", "paper-ink-profile-render"),
    ("Pastel Geometry", "pastel-geometry", "pastel-geometry-profile-render"),
    ("Split Pastel", "split-pastel", "split-pastel-profile-render"),
    ("Strategy Consulting", "strategy-consulting", "strategy-consulting-profile-render"),
    ("Terminal Green", "terminal-green", "terminal-green-profile-render"),
    ("Vintage Editorial", "vintage-editorial", "vintage-editorial-profile-render"),
]

PRESET_INSTANCE_CONTRACTS = {
    "terminal-green": {
        "required_candidate_selectors": [".terminal-scanlines"],
    },
}

RUNTIME_CLASS_STOPWORDS = {
    "slide",
    "content",
    "reveal",
    "visible",
    "p-on",
    "nav-dots",
    "progress-bar",
    "edit-hotzone",
    "edit-toggle",
    "keyboard-hint",
    "slide-credit",
    "title-line",
    "title-balance",
}

PROFILE_GENERIC_PREFIXES = ("profile-", "preset-signature-")

SIGNATURE_WORDS = {
    "aurora",
    "mesh",
    "signal",
    "voltage",
    "electric",
    "botanical",
    "glass",
    "newspaper",
    "brutal",
    "retro",
    "neon",
    "cyber",
    "notebook",
    "tabs",
    "pastel",
    "split",
    "strategy",
    "consulting",
    "terminal",
    "vintage",
    "editorial",
    "chan",
    "ink",
}


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def containment(expected: set[str], actual: set[str]) -> float:
    if not expected:
        return 1.0
    return round(len(expected & actual) / len(expected), 4)


def extract_css(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    return "\n".join(style.get_text("\n") for style in soup.find_all("style"))


def extract_classes(soup: BeautifulSoup) -> set[str]:
    classes: set[str] = set()
    for node in soup.find_all(True):
        value = node.get("class")
        if not value:
            continue
        for item in value:
            if item:
                classes.add(item)
    return classes


def important_classes(classes: set[str]) -> set[str]:
    result = set()
    for item in classes:
        if item in RUNTIME_CLASS_STOPWORDS:
            continue
        if item.startswith(PROFILE_GENERIC_PREFIXES):
            continue
        if item in {"body-text", "stat", "stats", "card", "pill"}:
            result.add(item)
            continue
        if item.endswith("-layout"):
            result.add(item)
            continue
        lowered = item.lower()
        if any(word in lowered for word in SIGNATURE_WORDS):
            result.add(item)
            continue
        if any(word in lowered for word in ("quote", "rule", "terminal", "tab", "grid", "orb", "panel")):
            result.add(item)
    return result


def extract_vars(css: str) -> set[str]:
    return set(re.findall(r"--[A-Za-z0-9_-]+", css))


def extract_colors(css: str) -> set[str]:
    values = set(re.findall(r"#[0-9a-fA-F]{3,8}\b", css))
    values |= set(re.findall(r"rgba?\([^)]+\)", css))
    return {re.sub(r"\s+", "", item).lower() for item in values}


def extract_fonts(html: str, css: str) -> set[str]:
    fonts: set[str] = set()
    for href in re.findall(r"https://fonts\.googleapis\.com/css2\?family=([^\"']+)", html):
        for family in href.split("&family="):
            name = family.split(":")[0].replace("+", " ").strip()
            if name:
                fonts.add(name)
    for family in re.findall(r"font-family\s*:\s*([^;}{]+)", css, re.I):
        for token in family.split(","):
            cleaned = token.strip().strip("\"'")
            if cleaned and not cleaned.startswith("var("):
                fonts.add(cleaned)
    return {font.lower() for font in fonts}


def extract_layout_tokens(classes: set[str], css: str) -> set[str]:
    tokens = {item for item in classes if item.endswith("-layout") or item.startswith("profile_") or item.startswith("glass_")}
    for word in ("grid", "flex", "columns", "split", "timeline", "matrix", "hero", "quote", "card", "terminal", "tabs"):
        if re.search(rf"\b{word}\b", css, re.I):
            tokens.add(word)
    return tokens


def slide_nodes(soup: BeautifulSoup) -> list[Any]:
    return soup.select("section.slide, .slide")


def text_word_count(soup: BeautifulSoup) -> int:
    return len(re.findall(r"\w+", soup.get_text(" ", strip=True)))


@dataclass
class HtmlFeatures:
    path: Path
    title: str
    preset: str | None
    slide_count: int
    word_count: int
    classes: set[str]
    important_classes: set[str]
    vars: set[str]
    colors: set[str]
    fonts: set[str]
    layout_tokens: set[str]
    grid_count: int
    flex_count: int


def analyze_html(path: Path) -> HtmlFeatures:
    html = read(path)
    soup = BeautifulSoup(html, "html.parser")
    css = extract_css(html)
    classes = extract_classes(soup)
    body = soup.body
    return HtmlFeatures(
        path=path,
        title=soup.title.get_text(strip=True) if soup.title else path.name,
        preset=body.get("data-preset") if body else None,
        slide_count=len(slide_nodes(soup)),
        word_count=text_word_count(soup),
        classes=classes,
        important_classes=important_classes(classes),
        vars=extract_vars(css),
        colors=extract_colors(css),
        fonts=extract_fonts(html, css),
        layout_tokens=extract_layout_tokens(classes, css),
        grid_count=len(re.findall(r"\bgrid\b", css)),
        flex_count=len(re.findall(r"\bflex\b", css)),
    )


def rhythm_score(old: HtmlFeatures, new: HtmlFeatures) -> float:
    slide = 1.0 - min(abs(old.slide_count - new.slide_count) / max(old.slide_count, new.slide_count, 1), 1.0)
    density = 1.0 - min(abs(old.word_count / max(old.slide_count, 1) - new.word_count / max(new.slide_count, 1)) / 180, 1.0)
    layout = containment(old.layout_tokens, new.layout_tokens)
    css_motion = 1.0 - min(abs((old.grid_count + old.flex_count) - (new.grid_count + new.flex_count)) / max(old.grid_count + old.flex_count, 1), 1.0)
    return round((slide * 0.25) + (density * 0.25) + (layout * 0.35) + (css_motion * 0.15), 4)


def score_pair(old: HtmlFeatures, new: HtmlFeatures) -> dict[str, Any]:
    font_score = containment(old.fonts, new.fonts)
    color_score = containment(old.colors, new.colors)
    css_var_score = containment(old.vars, new.vars)
    component_score = containment(old.important_classes, new.important_classes)
    rhythm = rhythm_score(old, new)
    overall = round(
        font_score * 0.2
        + color_score * 0.2
        + css_var_score * 0.15
        + component_score * 0.25
        + rhythm * 0.2,
        4,
    )
    return {
        "overall": overall,
        "font_score": font_score,
        "color_score": color_score,
        "css_var_score": css_var_score,
        "component_score": component_score,
        "rhythm_score": rhythm,
        "shared_important_classes": sorted(old.important_classes & new.important_classes),
        "missing_important_classes": sorted(old.important_classes - new.important_classes),
        "shared_fonts": sorted(old.fonts & new.fonts),
        "missing_fonts": sorted(old.fonts - new.fonts),
        "shared_colors_count": len(old.colors & new.colors),
        "old_colors_count": len(old.colors),
        "new_colors_count": len(new.colors),
        "shared_vars": sorted(old.vars & new.vars),
        "missing_vars": sorted(old.vars - new.vars),
    }


def preset_instance_failures(preset: str, candidate_path: Path) -> list[str]:
    contract = PRESET_INSTANCE_CONTRACTS.get(slug(preset))
    if not contract:
        return []
    soup = BeautifulSoup(read(candidate_path), "html.parser")
    failures: list[str] = []
    for selector in contract.get("required_candidate_selectors", []):
        if not soup.select(selector):
            failures.append(f"missing required component instance {selector}")
    return failures


def verdict(scores: dict[str, Any], instance_failures: list[str] | None = None) -> str:
    if instance_failures:
        return "FAIL"
    if scores["overall"] < THRESHOLDS["overall_pass_min"]:
        return "WARN" if scores["overall"] >= 0.5 else "FAIL"
    if scores["component_score"] < THRESHOLDS["component_min"]:
        return "WARN"
    if scores["font_score"] < THRESHOLDS["font_min"]:
        return "WARN"
    if scores["css_var_score"] < THRESHOLDS["css_var_min"]:
        return "WARN"
    if scores["old_colors_count"] > 5 and scores["color_score"] < THRESHOLDS["color_min_when_demo_has_colors"]:
        return "WARN"
    return "PASS"


def main_issue(scores: dict[str, Any], instance_failures: list[str] | None = None) -> str:
    if instance_failures:
        return "required component instance missing"
    if scores["component_score"] < THRESHOLDS["component_min"]:
        return "component vocabulary diverges"
    if scores["css_var_score"] < THRESHOLDS["css_var_min"]:
        return "CSS token surface diverges"
    if scores["font_score"] < THRESHOLDS["font_min"]:
        return "font identity diverges"
    if scores["old_colors_count"] > 5 and scores["color_score"] < THRESHOLDS["color_min_when_demo_has_colors"]:
        return "palette diverges"
    if scores["rhythm_score"] < 0.5:
        return "layout rhythm diverges"
    return "minor parity drift"


def _worse_verdict(left: str, right: str) -> str:
    order = {"PASS": 0, "WARN": 1, "FAIL": 2}
    return left if order.get(left, 0) >= order.get(right, 0) else right


def assess_visual_gate(
    item: dict[str, Any],
    *,
    viewports: list[str],
    require_visual: bool,
    visual_available: bool,
    unavailable_reason: str | None = None,
) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    measured: dict[str, float] = {}
    if not visual_available:
        if require_visual:
            failures.append(f"visual capture unavailable: {unavailable_reason or 'unknown reason'}")
        return {
            "status": "FAIL" if failures else "SKIP",
            "required": require_visual,
            "failures": failures,
            "warnings": warnings,
            "measured": measured,
        }
    for viewport in viewports:
        key = f"{viewport}_visual_similarity"
        if key not in item:
            if require_visual:
                failures.append(f"{viewport} visual similarity missing")
            continue
        score = float(item[key])
        measured[viewport] = score
        if score < THRESHOLDS["visual_fail_min"]:
            failures.append(
                f"{viewport} visual similarity {score:.4f} below fail threshold "
                f"{THRESHOLDS['visual_fail_min']:.2f}"
            )
        elif score < THRESHOLDS["visual_warn_min"]:
            warnings.append(
                f"{viewport} visual similarity {score:.4f} below warn threshold "
                f"{THRESHOLDS['visual_warn_min']:.2f}"
            )
    status = "FAIL" if failures else "WARN" if warnings else "PASS"
    return {
        "status": status,
        "required": require_visual,
        "failures": failures,
        "warnings": warnings,
        "measured": measured,
    }


def apply_visual_gate(
    results: list[dict[str, Any]],
    *,
    visual: dict[str, Any],
    viewports: list[str],
    require_visual: bool,
) -> None:
    visual_available = bool(visual.get("available"))
    unavailable_reason = visual.get("reason")
    for item in results:
        gate = assess_visual_gate(
            item,
            viewports=viewports,
            require_visual=require_visual,
            visual_available=visual_available,
            unavailable_reason=unavailable_reason,
        )
        item["visual_gate"] = gate
        if gate["status"] in {"WARN", "FAIL"}:
            item["verdict"] = _worse_verdict(item["verdict"], gate["status"])
            if gate["status"] == "FAIL":
                item["main_issue"] = "visual parity diverges"
            elif item["main_issue"] == "minor parity drift":
                item["main_issue"] = "visual parity warning"
        item["assessment"] = (
            "Candidate keeps enough historical style signals for parity."
            if item["verdict"] == "PASS"
            else "Candidate renders, but historical preset identity still diverges."
        )


def selected_presets(label: str | None) -> list[tuple[str, str, str]]:
    if not label:
        return PRESETS
    normalized = slug(label)
    selected = [item for item in PRESETS if slug(item[0]) == normalized or item[1] == normalized]
    if not selected:
        raise ValueError(f"unknown preset for demo parity: {label}")
    return selected


def try_visual_capture(results: list[dict[str, Any]], *, output_dir: Path, viewports: list[str]) -> dict[str, Any]:
    try:
        from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        return {"available": False, "reason": f"imports failed: {exc}", "captured": []}

    screenshot_dir = output_dir / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    viewport_map = {
        "desktop": {"width": 1280, "height": 720},
        "mobile": {"width": 390, "height": 844},
    }
    captured: list[str] = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for viewport_name in viewports:
                viewport = viewport_map[viewport_name]
                page = browser.new_page(viewport=viewport, device_scale_factor=1)
                for item in results:
                    preset_slug = slug(item["preset"])
                    for label, path_key in (("demo", "baseline_demo_path"), ("candidate", "candidate_path")):
                        path = Path(item[path_key])
                        out = screenshot_dir / f"{preset_slug}-{viewport_name}-{label}.png"
                        page.goto(path.resolve().as_uri(), wait_until="load")
                        page.wait_for_timeout(250)
                        page.screenshot(path=out, full_page=False)
                        item[f"{viewport_name}_{label}_screenshot"] = str(out)
                    old_img = Image.open(item[f"{viewport_name}_demo_screenshot"]).convert("RGB").resize((320, 180))
                    new_img = Image.open(item[f"{viewport_name}_candidate_screenshot"]).convert("RGB").resize((320, 180))
                    diff = ImageChops.difference(old_img, new_img)
                    stat = ImageStat.Stat(diff)
                    rms = math.sqrt(sum(value * value for value in stat.rms) / len(stat.rms))
                    item[f"{viewport_name}_visual_similarity"] = round(max(0.0, 1.0 - rms / 255), 4)
                    item[f"{viewport_name}_visual_delta_rms"] = round(rms, 4)
                    captured.append(f"{preset_slug}:{viewport_name}")
                page.close()
            browser.close()
        contact_path = output_dir / "demo-parity-contact-sheet.png"
        _write_contact_sheet(results, contact_path, Image, ImageDraw, ImageFont)
    except Exception as exc:
        return {"available": False, "reason": str(exc), "captured": captured}
    return {"available": True, "captured": captured, "contact_sheet": str(output_dir / "demo-parity-contact-sheet.png")}


def _write_contact_sheet(results: list[dict[str, Any]], path: Path, Image: Any, ImageDraw: Any, ImageFont: Any) -> None:
    rows = []
    for item in results:
        demo = item.get("desktop_demo_screenshot") or item.get("mobile_demo_screenshot")
        candidate = item.get("desktop_candidate_screenshot") or item.get("mobile_candidate_screenshot")
        if not demo or not candidate:
            continue
        rows.append((item, Image.open(demo).convert("RGB").resize((320, 180)), Image.open(candidate).convert("RGB").resize((320, 180))))
    if not rows:
        return
    width = 720
    row_h = 226
    sheet = Image.new("RGB", (width, row_h * len(rows) + 44), "#f6f6f4")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    draw.text((16, 14), "Historical demo (left) vs generated candidate (right)", fill="#111", font=font)
    y = 44
    for item, demo_img, candidate_img in rows:
        draw.text((16, y + 4), f"{item['preset']}  {item['verdict']}  {item['overall']}", fill="#111", font=font)
        sheet.paste(demo_img, (16, y + 28))
        sheet.paste(candidate_img, (376, y + 28))
        y += row_h
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path)


def build_markdown(results: list[dict[str, Any]], visual: dict[str, Any]) -> str:
    counts = Counter(item["verdict"] for item in results)
    avg = round(statistics.mean(item["overall"] for item in results), 4) if results else 0.0
    lines = [
        "# Demo Parity Eval",
        "",
        "Scope: compare the 17 non-core profile-rendered preset outputs against checked-in historical demos.",
        "",
        "## Summary",
        "",
        f"- Presets compared: `{len(results)}`",
        f"- PASS: `{counts.get('PASS', 0)}`",
        f"- WARN: `{counts.get('WARN', 0)}`",
        f"- FAIL: `{counts.get('FAIL', 0)}`",
        f"- Average parity score: `{avg}`",
        f"- Screenshot capture: `{'available' if visual.get('available') else 'unavailable'}`",
    ]
    if visual.get("contact_sheet"):
        lines.append(f"- Contact sheet: `{visual['contact_sheet']}`")
    if not visual.get("available"):
        lines.append(f"- Screenshot reason: `{visual.get('reason')}`")
    lines += [
        "",
        "## Per Preset",
        "",
        "| Preset | Verdict | Overall | Font | Color | CSS vars | Components | Rhythm | Desktop visual | Mobile visual | Required instances | Main issue |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for item in results:
        desktop_visual = item.get("desktop_visual_similarity", "")
        mobile_visual = item.get("mobile_visual_similarity", "")
        instance_failures = "; ".join(item.get("required_instance_failures") or []) or "-"
        lines.append(
            f"| {item['preset']} | {item['verdict']} | {item['overall']} | {item['font_score']} | "
            f"{item['color_score']} | {item['css_var_score']} | {item['component_score']} | "
            f"{item['rhythm_score']} | {desktop_visual} | {mobile_visual} | {instance_failures} | "
            f"{item['main_issue']} |"
        )
    return "\n".join(lines) + "\n"


def run_demo_parity(
    *,
    candidate_dir: Path,
    demo_dir: Path,
    output_dir: Path,
    preset: str | None = None,
    viewports: list[str] | None = None,
    require_visual: bool = False,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    viewports = viewports or ["desktop"]
    results: list[dict[str, Any]] = []
    errors: list[str] = []
    for preset_name, demo_slug, output_slug in selected_presets(preset):
        candidate_path = candidate_dir / output_slug / "deck.html"
        if not candidate_path.exists():
            errors.append(f"{preset_name}: missing candidate deck {candidate_path}")
            continue
        new = analyze_html(candidate_path)
        scored_candidates = []
        for baseline_path in (demo_dir / f"{demo_slug}-en.html", demo_dir / f"{demo_slug}-zh.html"):
            if baseline_path.exists():
                old = analyze_html(baseline_path)
                scored_candidates.append((baseline_path, old, score_pair(old, new)))
        if not scored_candidates:
            errors.append(f"{preset_name}: missing baseline demo under {demo_dir}")
            continue
        baseline_path, old, scores = max(scored_candidates, key=lambda item: item[2]["overall"])
        instance_failures = preset_instance_failures(preset_name, candidate_path)
        item_verdict = verdict(scores, instance_failures)
        results.append(
            {
                "preset": preset_name,
                "baseline_demo_path": str(baseline_path),
                "candidate_path": str(candidate_path),
                "baseline_slide_count": old.slide_count,
                "candidate_slide_count": new.slide_count,
                "baseline_word_count": old.word_count,
                "candidate_word_count": new.word_count,
                "verdict": item_verdict,
                "main_issue": main_issue(scores, instance_failures),
                "assessment": "Candidate keeps enough historical style signals for parity."
                if item_verdict == "PASS"
                else "Candidate renders, but historical preset identity still diverges.",
                "required_instance_failures": instance_failures,
                **scores,
            }
        )
    if errors:
        raise RuntimeError("\n".join(errors))

    visual = try_visual_capture(results, output_dir=output_dir, viewports=viewports)
    apply_visual_gate(results, visual=visual, viewports=viewports, require_visual=require_visual)
    verdict_counts = Counter(item["verdict"] for item in results)
    payload = {
        "suite_id": "demo-parity-17",
        "source": "historical demos vs generated profile-rendered decks",
        "thresholds": THRESHOLDS,
        "visual_capture": visual,
        "visual_gate_required": require_visual,
        "pass": not any(item["verdict"] != "PASS" for item in results),
        "summary": {
            "preset_count": len(results),
            "verdicts": dict(verdict_counts),
            "average_score": round(statistics.mean(item["overall"] for item in results), 4) if results else 0.0,
        },
        "results": results,
    }
    (output_dir / "demo-parity-report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "demo-parity-report.md").write_text(build_markdown(results, visual), encoding="utf-8")
    return payload


def run(args: argparse.Namespace) -> int:
    try:
        payload = run_demo_parity(
            candidate_dir=Path(args.candidate_dir),
            demo_dir=Path(args.demo_dir),
            output_dir=Path(args.output_dir),
            preset=args.preset,
            viewports=args.viewport,
            require_visual=args.require_visual,
        )
    except RuntimeError as exc:
        print(str(exc))
        return 2
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    output_dir = Path(args.output_dir)
    print(f"REPORT_MD: {output_dir / 'demo-parity-report.md'}")
    print(f"REPORT_JSON: {output_dir / 'demo-parity-report.json'}")
    if args.fail_under_pass and any(item["verdict"] != "PASS" for item in payload["results"]):
        return 1
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare generated profile decks against historical demo style signatures.")
    parser.add_argument("--candidate-dir", default=".tmp-preset-surface-all")
    parser.add_argument("--demo-dir", default="demos")
    parser.add_argument("--output-dir", default=".tmp-demo-parity")
    parser.add_argument("--preset", help="Optional single preset display name or slug")
    parser.add_argument("--viewport", choices=("desktop", "mobile"), action="append", default=None)
    parser.add_argument("--require-visual", action="store_true", help="Fail closed when visual screenshots cannot be captured")
    parser.add_argument("--fail-under-pass", action="store_true")
    args = parser.parse_args()
    args.viewport = args.viewport or ["desktop"]
    return args


def main() -> int:
    try:
        return run(parse_args())
    except ValueError as exc:
        print(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
