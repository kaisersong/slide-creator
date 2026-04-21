# Failure Map

Use this table when a late-context eval fails. The point is not "the output looked bad"; the point is to locate the first fix site.

| Failure type | Typical symptom | First fix location | Secondary fix location |
| --- | --- | --- | --- |
| Route failure | `slide-creator` did not trigger, wrong mode, or wrong sibling skill won | `SKILL.md` | `references/workflow.md` |
| Compression failure | `BRIEF.json` drops thesis, audience, preset, or page roles from long context | `references/brief-template.json` | `schemas/generation-brief.schema.json` |
| Render failure | HTML ignores preset, skips signature CSS, or loses Present/Edit/Watermark contract | `references/html-template.md` | style reference files + `scripts/generate.py` |
| Efficiency failure | Thrashing, repeated full-context reads, too many retries, unnecessary file scans | `SKILL.md` | `references/workflow.md` |

## Notes

- Route failures should be fixed before touching any demos.
- Compression failures should tighten the IR before adding more post-hoc HTML checks.
- Render failures should move requirements out of prose and into deterministic validators when possible.
- Efficiency failures should reduce context and routing load, not add more narrative instructions.
