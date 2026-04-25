# Core-MD Guard Late-Context Eval Notes

Use these cases to measure whether guard hardening improved real late-context reliability.

Primary goals:

- catch omitted shared runtime on non-Blue-Sky decks
- prevent `data-preset` omission from bypassing strict validate
- preserve the Blue Sky control path
- confirm style-heavy presets still retain signature layers under long context

Suggested before/after metrics:

- guard catch rate
- false-positive rate
- late-context contract pass rate
- failure localization quality

Case IDs live in `../cases/` and are listed in `../manifest.json`.
