from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup


GENERIC_TITLES = {
    "agenda",
    "contents",
    "conclusion",
    "intro",
    "introduction",
    "overview",
    "summary",
    "what we do",
    "next steps",
    "目录",
    "概览",
    "概述",
    "总结",
    "结论",
    "背景",
    "方案",
}

STRUCTURAL_ROLES = {"cover", "title", "intro", "opening", "closing", "cta", "cta_close", "toc"}
TITLE_SELECTORS = (
    "h1",
    "h2",
    "h3",
    ".title",
    ".title-balance",
    ".profile-title",
    ".profile-generated-title",
    ".hero-title",
    ".main-title",
    ".display-title",
    ".headline",
    ".manifesto-headline",
    ".pull-quote",
    ".cta-title",
    ".t-title",
    ".t-h2",
    ".a-title",
    ".a-h2",
    ".zen-vertical-title",
    ".aurora-subtitle.stat-sub",
    ".stat-label",
    ".sc-action-title",
    "[data-export-slot='title']",
)


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _normalize_key(text: str) -> str:
    return re.sub(r"[\W_]+", "", text.lower(), flags=re.UNICODE)


def _title_for_slide(slide: Any) -> str:
    for selector in TITLE_SELECTORS:
        title = slide.select_one(selector)
        if not title:
            continue
        text = _normalize_text(title.get_text(" ", strip=True))
        if len(text) >= 3 and not re.fullmatch(r"[\d\s/_.:-]+", text):
            return text
    return ""


def _body_for_slide(slide: Any, title: str) -> str:
    body = _normalize_text(slide.get_text(" ", strip=True))
    if title and body.startswith(title):
        body = body[len(title) :].strip()
    return body


def _role_for_slide(slide: Any) -> str:
    return _normalize_text(str(slide.get("data-export-role") or slide.get("aria-label") or "unknown")).lower()


def _signature_for_slide(slide: Any) -> str:
    signature = _normalize_text(str(slide.get("data-visual-signature") or ""))
    if signature:
        return signature
    role = _role_for_slide(slide)
    class_tokens = [token for token in slide.get("class", []) if token not in {"slide", "visible"}]
    return "|".join([role, *class_tokens[:3]]) or "unknown"


def _meaningful_tokens(text: str) -> set[str]:
    text = (text or "").lower()
    tokens: set[str] = set()
    for token in re.findall(r"[a-z0-9][a-z0-9._:/+\-]{2,}", text):
        if token not in GENERIC_TITLES:
            tokens.add(token)
    cjk = re.findall(r"[\u4e00-\u9fff]", text)
    tokens.update(cjk)
    for index in range(len(cjk) - 1):
        tokens.add("".join(cjk[index : index + 2]))
    return tokens


def _script_counts(text: str) -> dict[str, int]:
    return {
        "cjk": len(re.findall(r"[\u4e00-\u9fff]", text or "")),
        "latin": len(re.findall(r"[A-Za-z][A-Za-z0-9._:/+\-]{2,}", text or "")),
    }


def _max_direct_list_items(slide: Any) -> int:
    counts = [len(list_node.find_all("li", recursive=False)) for list_node in slide.select("ul, ol")]
    if counts:
        return max(counts)
    return len(slide.select("li"))


def _max_run(values: list[str]) -> int:
    best = 0
    current = 0
    previous = None
    for value in values:
        if value == previous:
            current += 1
        else:
            previous = value
            current = 1
        best = max(best, current)
    return best


def _violation(code: str, message: str, **extra: Any) -> dict[str, Any]:
    return {"code": code, "type": code.removeprefix("ai-advised-"), "severity": "hard", "message": message, **extra}


def analyze_ai_advised_html(html_text: str, *, preset: str | None = None) -> dict[str, Any]:
    soup = BeautifulSoup(html_text, "html.parser")
    slides = soup.select(".slide")
    violations: list[dict[str, Any]] = []
    slide_reports: list[dict[str, Any]] = []

    for index, slide in enumerate(slides, start=1):
        title = _title_for_slide(slide)
        body = _body_for_slide(slide, title)
        role = _role_for_slide(slide)
        signature = _signature_for_slide(slide)
        title_key = _normalize_key(title)
        body_chars = len(re.sub(r"\s+", "", body))
        bullet_count = _max_direct_list_items(slide)
        media_count = len(slide.select("img,svg,canvas,video,picture,table"))
        title_tokens = _meaningful_tokens(title)
        body_tokens = _meaningful_tokens(body)
        title_scripts = _script_counts(title)
        body_scripts = _script_counts(body)
        support_overlap = len(title_tokens & body_tokens)
        support_ratio = round(support_overlap / max(1, len(title_tokens)), 4)
        script_mismatch = (
            (title_scripts["cjk"] >= 3 and body_scripts["cjk"] == 0)
            or (title_scripts["latin"] >= 2 and body_scripts["latin"] == 0 and body_chars >= 36)
        )
        shallow = role not in STRUCTURAL_ROLES and body_chars < 18 and media_count == 0
        generic = title_key in {_normalize_key(item) for item in GENERIC_TITLES}

        if not title:
            violations.append(_violation("ai-advised-missing-title", "slide title is missing", slide_index=index))
        if generic:
            violations.append(_violation("ai-advised-generic-title", "slide title is generic", slide_index=index, title=title))
        if shallow:
            violations.append(
                _violation(
                    "ai-advised-shallow-content",
                    "non-structural slide has too little body content",
                    slide_index=index,
                    body_chars=body_chars,
                )
            )
        if bullet_count > 7:
            violations.append(
                _violation(
                    "ai-advised-overloaded-list",
                    "slide has too many list items",
                    slide_index=index,
                    bullet_count=bullet_count,
                )
            )

        slide_reports.append(
            {
                "slide_index": index,
                "role": role,
                "visual_signature": signature,
                "title": title,
                "title_token_count": len(title_tokens),
                "body_chars": body_chars,
                "bullet_count": bullet_count,
                "media_count": media_count,
                "title_body_support_ratio": support_ratio,
                "title_body_script_mismatch": script_mismatch,
            }
        )

    titles = [_normalize_key(report["title"]) for report in slide_reports if report.get("title")]
    title_counts = Counter(titles)
    repeated_titles = [title for title, count in title_counts.items() if title and count > 1]
    for title in repeated_titles:
        violations.append(
            _violation(
                "ai-advised-repeated-title",
                "same title appears on multiple slides",
                title_key=title,
                count=title_counts[title],
            )
        )

    roles = [report["role"] for report in slide_reports]
    signatures = [report["visual_signature"] for report in slide_reports]
    max_role_run = _max_run(roles)
    max_signature_run = _max_run(signatures)
    unique_roles = len(set(roles))
    unique_signatures = len(set(signatures))
    slide_count = len(slides)

    if slide_count >= 3 and max_signature_run >= 3:
        violations.append(
            _violation(
                "ai-advised-repeated-visual-signature",
                "three or more consecutive slides use the same visual signature",
                max_run=max_signature_run,
            )
        )
    if slide_count >= 4 and max_role_run >= 3:
        violations.append(
            _violation(
                "ai-advised-repeated-role-run",
                "three or more consecutive slides use the same narrative role",
                max_run=max_role_run,
            )
        )
    if slide_count >= 4 and unique_signatures < 3:
        violations.append(
            _violation(
                "ai-advised-low-rhythm-variety",
                "deck has too little visual rhythm variety",
                unique_signatures=unique_signatures,
            )
        )
    if slide_count >= 4 and unique_roles < 3:
        violations.append(
            _violation(
                "ai-advised-low-role-variety",
                "deck has too little narrative role variety",
                unique_roles=unique_roles,
            )
        )

    low_support = [
        report
        for report in slide_reports
        if report["role"] not in STRUCTURAL_ROLES
        and report["body_chars"] >= 36
        and report["title_token_count"] >= 3
        and report["title_body_script_mismatch"]
    ]
    if len(low_support) >= max(2, slide_count // 2):
        violations.append(
            _violation(
                "ai-advised-title-support-low",
                "titles are not supported by nearby body content across too many slides",
                slide_indices=[report["slide_index"] for report in low_support],
            )
        )

    hard_failures: list[str] = []
    for violation in violations:
        code = str(violation["code"])
        if code not in hard_failures:
            hard_failures.append(code)

    return {
        "version": 1,
        "phase": "1.0-ai-advised-semantic-proxy",
        "preset": preset,
        "pass": not violations,
        "hard_failures": hard_failures,
        "violations": violations,
        "diagnostics": {
            "slide_count": slide_count,
            "unique_role_count": unique_roles,
            "unique_visual_signature_count": unique_signatures,
            "max_role_run": max_role_run,
            "max_visual_signature_run": max_signature_run,
            "low_title_support_slide_count": len(low_support),
            "generic_title_count": sum(1 for item in violations if item["code"] == "ai-advised-generic-title"),
        },
        "slides": slide_reports,
    }


def analyze_ai_advised_path(path: str | Path, *, preset: str | None = None) -> dict[str, Any]:
    html_path = Path(path)
    report = analyze_ai_advised_html(html_path.read_text(encoding="utf-8"), preset=preset)
    report["html_path"] = str(html_path)
    return report


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run AI-advised semantic/rhythm proxy eval for a rendered deck.")
    parser.add_argument("html_path")
    parser.add_argument("--preset")
    parser.add_argument("--output")
    args = parser.parse_args()

    report = analyze_ai_advised_path(args.html_path, preset=args.preset)
    if args.output:
        Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
