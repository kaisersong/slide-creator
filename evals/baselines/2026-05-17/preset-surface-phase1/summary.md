# Preset Surface Release Gate

- Generated: `2026-05-17T14:31:31`
- Suite: `preset-surface-phase1`
- Output: `/private/tmp/slide-preset-release-gate`
- Baseline dir: `none`
- Require baseline: `false`
- Browser titles: `true`

## Summary

- Pass count: `6`
- Fail count: `0`
- Best case: `support-blue-sky-fixture`
- Baseline enabled: `false`
- Non-regression ready cases: `0`

## Deterministic Core

- `core-blue-sky-render` `PASS` preset=`Blue Sky` tier=`tier0` style=`0.8182` minimal-run=`1`
- `core-enterprise-dark-render` `PASS` preset=`Enterprise Dark` tier=`tier1` style=`1.0` minimal-run=`0`
- `core-swiss-modern-render` `PASS` preset=`Swiss Modern` tier=`tier0` style=`0.7143` minimal-run=`1`
- `core-data-story-render` `PASS` preset=`Data Story` tier=`tier0` style=`1.0` minimal-run=`0`

## Support Surface

- `support-blue-sky-fixture` `PASS` preset=`Blue Sky` support-tier=`production` style=`0.9545`
- `support-paper-ink-fixture` `PASS` preset=`Paper & Ink` support-tier=`supported` style=`0.8684`

## Gate Result

- `PASS`

## Captured-Run Skill Evals

- Command: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3 /Users/song/projects/slide-creator/scripts/run-skill-evals.py --root /Users/song/projects/slide-creator --runner fixture --format json --artifact-dir /private/tmp/slide-preset-release-gate/skill-runs --json-out /private/tmp/slide-preset-release-gate/skill-evals.json`
- Return code: `0`
- Total: `6`
- Passed: `6`
- Failed: `0`
