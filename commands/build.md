---
name: ultrapilot-build
description: "/ultrapilot:build — Execute the approved plan in small, verifiable steps. Matches existing codebase conventions. Standalone phase command for the ultrapilot orchestrator."
license: MIT
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
metadata:
  author: joychetry
  version: "1.0"
  category: software-development
  parent: ultrapilot
---

# /ultrapilot:build

**Phase 3 of /ultrapilot.** Execute the approved plan. Small steps, checkpoints, no scope creep.

## When to Use

- After a plan exists and is approved
- When the user wants the orchestrator to skip planning and just build (the plan was already written elsewhere)
- Inside a larger ultrapilot run, this phase is dispatched automatically

## How to Invoke

```
/ultrapilot:build
```

Or with a reference plan:

```
/ultrapilot:build follow the plan in /tmp/plan.md
```

## Build Rules

The build phase must follow these rules:

1. **One step at a time.** Complete a step, then check it.
2. **Match the existing codebase.** Use its conventions, types, patterns. Do not invent a new architecture inside an existing one.
3. **No scope creep.** If a step is not in the plan, do not add it.
4. **Use negative constraints for UI work** (see ultrapilot SKILL.md Appendix B).
5. **Run available checks after each meaningful step:** tests, type checks, lint, build.
6. **TDD where it fits.** For logic-heavy code, write a failing test first, then make it pass.

## Mid-Build Steering

If a step turns out to require something not in the plan, **stop and re-plan** for that step. Do not improvise.

Examples of when to stop:
- The plan said "add a database column" but the existing schema needs a migration that affects other tables
- The plan said "use the existing dropdown component" but the existing component does not support the new use case
- A new requirement surfaces from a hidden dependency (auth, permissions, rate limits)

When in doubt, stop. Better to ask than to build the wrong thing.

## What "Done" Means in the Build Phase

The build phase is done when:
- All steps in the plan are complete
- Each step's checks pass
- The build does not declare overall completion — that is the review phase's job

The orchestrator will dispatch `/ultrapilot:verify` and `/ultrapilot:review` after this phase.

## Pitfalls

- **Do not skip checkpoints.** A 5-line change can break a 500-line test suite. Check after every meaningful step.
- **Do not "improve" unrelated code.** Stay in the lane the plan defined.
- **Do not trust successful-looking output.** The app can look right and still be broken. Run the actual verification.
- **Do not load every skill at once.** If you need design constraints, load them. If you do not, do not.

## Related Commands

- `/ultrapilot:plan` — should be run before build
- `/ultrapilot:verify` — runs after build
- `/ultrapilot:review` — runs after verify
- `/ultrapilot` — full orchestrator
