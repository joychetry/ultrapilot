---
name: completion-conditions-legacy
description: "DEPRECATED — see /ultrapilot:goals in commands/goals.md. Kept for historical reference only. Will be removed in v3.0."
type: reference
status: deprecated
---

# DEPRECATED — Completion Conditions (v1)

**This document is superseded by `/ultrapilot:goals` (in `commands/goals.md`).** Kept for historical reference only. The v1 design used a single binary goal ("is the task done?") which has been replaced with a multi-dimensional weighted score.

## What changed

| v1 (this doc) | v2 (`commands/goals.md`) |
|---------------|--------------------------|
| Single binary goal | Six dimensions with weights |
| Four-gate default completion | Aggregate score ≥ 80% + per-dimension floors + four-gate default |
| No goal profile | Six preset profiles + custom weights |
| No trial support | `--trials N` for non-deterministic tasks |
| No goal conflict resolution | Priority hierarchy (safety > correctness > reliability > efficiency > UX > cost) |

## Quick v1 reference (if you need it)

The four-gate default completion logic from v1:

1. The plan's acceptance criteria are met.
2. The verification suite passes (tests, lint, type checks, manual flow checks).
3. The review pass found no connected issues.
4. The app builds and runs.

This is still part of v2 as one of the five completion conditions, but it is no longer the only one.

## Migration

Replace any reference to "ultrapilot completion" in your project docs with the v2 goal system. Use:

```
/ultrapilot:goals [task]
```

to invoke the new module.

## See also

- `commands/goals.md` — the new v2 multi-dimensional goal system
- `SKILL.md` — the main ultrapilot spec, which now references v2 goals
