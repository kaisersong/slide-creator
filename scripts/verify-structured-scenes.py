#!/usr/bin/env python3
"""Verify the installed Fantasy Rainbow renderer against frozen source fixtures."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from browser_geometry_qa import analyze_browser_geometry_path
from playwright.sync_api import sync_playwright
from validate_source_fidelity import validate_source_fidelity


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    html = output / "structured.html"
    fixture = args.fixtures.resolve()
    subprocess.run([sys.executable, str(Path(__file__).resolve().parent.parent / "main.py"),
                    "--generate", "--brief", str(fixture / "BRIEF.json"),
                    "--output", str(html)], check=True)
    coverage = json.loads((fixture / "coverage.json").read_text())
    fidelity = validate_source_fidelity(html.read_text(), coverage)
    (output / "fidelity.json").write_text(json.dumps(fidelity, ensure_ascii=False, indent=2))
    assert fidelity["pass"], "Structured source text/relations/negative constraints failed"
    reports = []
    for name, viewports, modes in [
        ("desktop", [{"width": 1600, "height": 900}, {"width": 1280, "height": 720},
                     {"width": 1440, "height": 733}], ("window", "present")),
        ("mobile", [{"width": 390, "height": 844}], ("window",)),
    ]:
        report = analyze_browser_geometry_path(html, preset="Fantasy Rainbow", viewports=viewports,
                                               modes=modes, stable_runs=1, artifact_dir=output / name)
        (output / f"{name}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
        reports.append(report)
    errors = []
    edge_counts = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 733})
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.route("http://**/*", lambda route: route.abort())
        page.route("https://**/*", lambda route: route.abort())
        page.goto(html.as_uri())
        for presenting in (False, True):
            if presenting:
                page.goto(html.as_uri())
                page.keyboard.press("F5")
            for index in range(15):
                if not presenting:
                    page.locator("section.slide").nth(index).scroll_into_view_if_needed()
                elif index:
                    page.keyboard.press("ArrowRight")
                page.wait_for_timeout(150)
                if presenting:
                    assert page.locator("section.slide").nth(index).is_visible()
                paths = page.locator("section.slide").nth(index).locator(".iri-edge-path")
                for path in paths.all():
                    assert path.get_attribute("visibility") != "hidden"
                    assert path.get_attribute("d") != "M 0 0 C 0 0 0 0 0 0"
                    assert path.evaluate("p => p.getTotalLength()") > 1
                    assert path.evaluate("""p => {
                        const host = p.closest('svg').parentElement;
                        const rect = host.getBoundingClientRect();
                        const nodes = [...host.querySelectorAll('[data-node-id], [data-group-id]')];
                        const node = id => nodes.find(n => n.dataset.nodeId === id || n.dataset.groupId === id);
                        const within = (point, n) => {
                            const r = n.getBoundingClientRect();
                            const x = rect.left + point.x * rect.width / host.offsetWidth;
                            const y = rect.top + point.y * rect.height / host.offsetHeight;
                            return x >= r.left - 2 && x <= r.right + 2 && y >= r.top - 2 && y <= r.bottom + 2;
                        };
                        return within(p.getPointAtLength(0), node(p.dataset.edgeFrom)) &&
                            within(p.getPointAtLength(p.getTotalLength()), node(p.dataset.edgeTo));
                    }"""), "Visible arrow endpoints must meet the declared nodes"
                edge_counts.append(paths.count())
        page.keyboard.press("Escape")
        page.set_viewport_size({"width": 390, "height": 844})
        page.locator("section.slide").nth(14).scroll_into_view_if_needed()
        page.wait_for_timeout(200)
        assert page.locator("#slide-15 .iri-edge-path").first.evaluate("p => p.getTotalLength()") > 1
        browser.close()
    report = {"pass": all(r["pass"] for r in reports) and not errors,
              "scene_count": len(coverage["slides"]), "fidelity_pass": fidelity["pass"],
              "geometry_pass": [r["pass"] for r in reports], "page_errors": errors,
              "edge_counts_window_then_present": edge_counts}
    (output / "verification.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report), flush=True)
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
