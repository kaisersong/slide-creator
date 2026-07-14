#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - environment dependent
    sync_playwright = None

from preset_contracts import load_preset_contract


ROOT = Path(__file__).resolve().parent.parent
VIEWPORT = {"width": 1600, "height": 900}


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _launch_browser():
    if sync_playwright is None:
        raise RuntimeError("Playwright is not installed; runtime fidelity QA cannot run")
    playwright = sync_playwright().start()
    try:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
    except Exception:
        browser = playwright.chromium.launch(headless=True)
    return playwright, browser


def _bucket_for_index(index: int, total: int) -> str:
    if total <= 1 or index == 0:
        return "cover"
    if index == total - 1:
        return "closing"
    return "content"


MEASURE_SCENARIO_JS = r"""
async ({slideIndex, trigger, selectors}) => {
  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
  const frame = () => new Promise(resolve => requestAnimationFrame(() => resolve()));
  if (trigger === 'navigate') {
    if (typeof window.go !== 'function' || window.go(slideIndex) === false) {
      return {target_found:false, animation_found:false, visible:false, time_advanced:false, presentation_changed:false, reason:'go-unavailable'};
    }
  } else if (typeof window.go === 'function') {
    window.go(slideIndex);
  }

  await frame();
  const nodes = [];
  for (const selector of selectors) {
    try {
      for (const node of document.querySelectorAll(selector)) {
        if (!nodes.includes(node)) nodes.push(node);
      }
    } catch (_) {}
  }

  const inViewport = node => {
    const style = getComputedStyle(node);
    const rect = node.getBoundingClientRect();
    const opacity = Number.parseFloat(style.opacity || '1');
    return style.display !== 'none' && style.visibility !== 'hidden' && opacity >= 0.05 &&
      rect.width > 0 && rect.height > 0 && rect.right > 0 && rect.bottom > 0 &&
      rect.left < innerWidth && rect.top < innerHeight;
  };

  const isOpaqueFullCover = (node, target) => {
    if (node === target || target.contains(node) || node.contains(target)) return false;
    const style = getComputedStyle(node);
    const rect = node.getBoundingClientRect();
    const alpha = Number.parseFloat(style.opacity || '1');
    const color = style.backgroundColor || '';
    const colorAlpha = color.startsWith('rgba') ? Number.parseFloat(color.split(',').at(-1)) : (color === 'transparent' ? 0 : 1);
    return alpha >= 0.95 && colorAlpha >= 0.95 && rect.left <= 1 && rect.top <= 1 &&
      rect.right >= innerWidth - 1 && rect.bottom >= innerHeight - 1;
  };

  const notOccluded = target => {
    const hitTestingSuppressed = (() => {
      let node = target;
      while (node && node instanceof Element) {
        if (getComputedStyle(node).pointerEvents === 'none') return true;
        node = node.parentElement;
      }
      return false;
    })();
    const rect = target.getBoundingClientRect();
    const xs = [0.15, 0.5, 0.85];
    const ys = [0.15, 0.5, 0.85];
    for (const xp of xs) for (const yp of ys) {
      const x = Math.max(0, Math.min(innerWidth - 1, rect.left + rect.width * xp));
      const y = Math.max(0, Math.min(innerHeight - 1, rect.top + rect.height * yp));
      let blocked = false;
      let reached = false;
      for (const node of document.elementsFromPoint(x, y)) {
        if (node === target || target.contains(node)) { reached = true; break; }
        if (isOpaqueFullCover(node, target)) { blocked = true; break; }
      }
      if (!blocked && (reached || hitTestingSuppressed)) return true;
    }
    return false;
  };

  const visibleNodes = nodes.filter(node => inViewport(node) && notOccluded(node));
  const animationPairs = [];
  for (const node of visibleNodes) {
    for (const animation of node.getAnimations({subtree:true})) {
      if (!animationPairs.some(item => item.animation === animation)) animationPairs.push({node, animation});
    }
  }
  for (const animation of document.getAnimations()) {
    const effectTarget = animation.effect && animation.effect.target;
    if (!effectTarget) continue;
    const owner = visibleNodes.find(node => node === effectTarget || node.contains(effectTarget));
    if (owner && !animationPairs.some(item => item.animation === animation)) animationPairs.push({node:effectTarget, animation});
  }

  const snapshot = node => {
    const style = getComputedStyle(node);
    const rect = node.getBoundingClientRect();
    return {
      transform: style.transform,
      opacity: style.opacity,
      x: Math.round(rect.x * 100) / 100,
      y: Math.round(rect.y * 100) / 100,
      width: Math.round(rect.width * 100) / 100,
      height: Math.round(rect.height * 100) / 100,
    };
  };

  let durationValid = false;
  let presentationChanged = false;
  let timeAdvanced = false;
  let originallyPaused = false;
  let sampledAnimation = null;
  for (const pair of animationPairs) {
    const timing = pair.animation.effect && pair.animation.effect.getComputedTiming();
    const duration = timing && Number(timing.duration);
    if (!Number.isFinite(duration) || duration <= 0) continue;
    durationValid = true;
    sampledAnimation = pair.animation;
    originallyPaused = pair.animation.playState === 'paused' || getComputedStyle(pair.node).animationPlayState === 'paused';
    const effectTiming = pair.animation.effect.getTiming();
    const delay = Number(effectTiming.delay) || 0;
    pair.animation.pause();
    pair.animation.currentTime = Math.max(0, delay + duration * 0.10);
    await frame();
    const first = snapshot(pair.node);
    pair.animation.currentTime = Math.max(0, delay + duration * 0.60);
    await frame();
    const second = snapshot(pair.node);
    presentationChanged = JSON.stringify(first) !== JSON.stringify(second);
    if (presentationChanged) break;
  }

  if (sampledAnimation && durationValid && !originallyPaused) {
    sampledAnimation.currentTime = Math.max(0, Number(sampledAnimation.currentTime) || 0);
    sampledAnimation.play();
    const start = Number(sampledAnimation.currentTime) || 0;
    const deadline = performance.now() + 2000;
    while (performance.now() < deadline) {
      await sleep(120);
      const current = Number(sampledAnimation.currentTime) || 0;
      if (current > start + 1) { timeAdvanced = true; break; }
    }
  }

  return {
    target_found: nodes.length > 0,
    animation_found: animationPairs.length > 0,
    duration_valid: durationValid,
    visible: visibleNodes.length > 0,
    time_advanced: timeAdvanced,
    presentation_changed: presentationChanged,
    originally_paused: originallyPaused,
    target_count: nodes.length,
    visible_target_count: visibleNodes.length,
    animation_count: animationPairs.length,
  };
}
"""


def _failure_codes(measurement: dict[str, Any]) -> list[str]:
    failures = []
    if not measurement.get("target_found") or not measurement.get("animation_found"):
        failures.append("runtime-motion-target-missing")
    if not measurement.get("visible"):
        failures.append("runtime-motion-not-visible")
    if not measurement.get("duration_valid") or not measurement.get("time_advanced"):
        failures.append("runtime-motion-time-static")
    if not measurement.get("presentation_changed"):
        failures.append("runtime-motion-presentation-static")
    return failures


def analyze_preset_runtime_path(path: str | Path, preset: str) -> dict[str, Any]:
    html_path = Path(path).resolve()
    html_text = html_path.read_text(encoding="utf-8")
    contract = load_preset_contract(preset)
    runtime = contract.get("runtime_fidelity")
    contract_text = json.dumps(contract, ensure_ascii=False, sort_keys=True)
    base_report: dict[str, Any] = {
        "version": 1,
        "phase": "runtime-fidelity",
        "preset": preset,
        "html_path": str(html_path),
        "html_sha256": _sha256_text(html_text),
        "contract_sha256": _sha256_text(contract_text),
        "runtime_owner": runtime.get("runtime_owner") if isinstance(runtime, dict) else None,
        "scenarios": [],
        "violations": [],
        "hard_failures": [],
    }
    if not runtime:
        return {**base_report, "pass": True, "not_applicable": True}

    try:
        playwright, browser = _launch_browser()
    except Exception as exc:  # pragma: no cover - environment dependent
        return {
            **base_report,
            "pass": False,
            "unavailable": True,
            "error": str(exc),
            "hard_failures": ["runtime-qa-unavailable"],
        }

    try:
        context = browser.new_context(
            viewport=VIEWPORT,
            device_scale_factor=1,
            reduced_motion="no-preference",
        )
        page = context.new_page()
        page.goto(html_path.as_uri(), wait_until="load")
        page.wait_for_timeout(100)
        missing_dom = [selector for selector in runtime["required_dom"] if page.query_selector(selector) is None]
        if missing_dom:
            base_report["violations"].append({
                "code": "runtime-owner-mismatch",
                "missing_dom": missing_dom,
                "severity": "hard",
            })
        slide_buckets = page.eval_on_selector_all(
            "section.slide, .slide",
            """nodes => nodes.filter((node,index,self) => self.indexOf(node) === index).map((node,index,self) => {
              const value = (node.dataset.pageBucket || '').toLowerCase();
              if (['cover','content','closing'].includes(value)) return value;
              if (self.length <= 1 || index === 0) return 'cover';
              return index === self.length - 1 ? 'closing' : 'content';
            })""",
        )
        for scenario in runtime["motion_scenarios"]:
            wanted = set(scenario["required_page_buckets"])
            for index, bucket in enumerate(slide_buckets):
                if bucket not in wanted:
                    continue
                measured = page.evaluate(
                    MEASURE_SCENARIO_JS,
                    {
                        "slideIndex": index,
                        "trigger": scenario["trigger"],
                        "selectors": scenario["selectors"],
                    },
                )
                failures = _failure_codes(measured)
                result = {
                    "name": scenario["name"],
                    "trigger": scenario["trigger"],
                    "slide_index": index,
                    "page_bucket": bucket,
                    "visible": bool(measured.get("visible")),
                    "time_advanced": bool(measured.get("time_advanced")),
                    "presentation_changed": bool(measured.get("presentation_changed")),
                    "measurement": measured,
                    "failures": failures,
                }
                base_report["scenarios"].append(result)
                for code in failures:
                    base_report["violations"].append({
                        "code": code,
                        "scenario": scenario["name"],
                        "slide_index": index,
                        "page_bucket": bucket,
                        "severity": "hard",
                    })
        context.close()
    except Exception as exc:  # pragma: no cover - browser/runtime failure path
        base_report["violations"].append({"code": "runtime-qa-unavailable", "error": str(exc), "severity": "hard"})
    finally:
        browser.close()
        playwright.stop()

    hard_failures = list(dict.fromkeys(item["code"] for item in base_report["violations"]))
    return {**base_report, "pass": not hard_failures, "hard_failures": hard_failures}


def analyze_preset_runtime_html(html_text: str, preset: str) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as handle:
        handle.write(html_text)
        path = Path(handle.name)
    try:
        return analyze_preset_runtime_path(path, preset)
    finally:
        path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate browser runtime fidelity for a preset HTML deck")
    parser.add_argument("html")
    parser.add_argument("--preset", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    report = analyze_preset_runtime_path(args.html, args.preset)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
