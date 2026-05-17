# Captured Runner Trace Fixtures

The raw Codex JSONL fixtures in this directory were captured from real
`codex exec --json` runs before the adapter parser was implemented.

Observed event shape:

- Top-level lifecycle events include `thread.started`, `turn.started`, and `turn.completed`.
- Tool calls appear as `item.started` / `item.completed` events whose nested `item.type` is `command_execution`.
- Shell commands are stored at `item.command`; completed command events include `item.exit_code`.
- Token usage appears on `turn.completed` as `usage.input_tokens` and `usage.output_tokens`.
- File reads and writes are not guaranteed in these minimal traces; the adapter must degrade to warnings or partial metrics when fields are absent.
