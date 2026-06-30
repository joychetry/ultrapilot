---
phase: build
verbosity: compact
tokens_estimate: 250
---

# Phase: Build

## Goal
Execute the plan in small, verifiable steps. Match the existing codebase. No scope creep.

## Plan
`PLAN_PATH: <filled in by runner>`

## Rules
1. **One step at a time.** Complete a step, then check it.
2. **Match the existing codebase.** Use its conventions, types, patterns.
3. **No scope creep.** If a step is not in the plan, do not add it.
4. **Run available checks after each meaningful step** (tests, typecheck, lint, build).
5. **Use the discipline layer if it was loaded** (the goal phase may have set it).

**Note on step size:** ultrapilot is intentionally **conservative** — small steps, single-file when possible — because the skill is model-agnostic and a smaller step is safer across more models. Some models with very large context windows can edit multiple files in one step without losing coherence, but the orchestrator does not assume that capability. If you are using a model you know can hold the context, you can relax this by editing the build prompt's rule 1 in `prompts/build.md`.

## When to stop and steer
- Plan is vague → ask: "Which X, where, and how will you test it?"
- Going off-rails → reset to last good checkpoint, re-plan that step.
- Hidden dependency surfaces (auth, permissions, rate limits) → stop, mention it, ask user.

## Output Format

```markdown
# Build Summary

## Steps completed
1. <step> — <one-line result>
2. <step> — <one-line result>

## Files changed
- <path>
- <path>

## Files created
- <path>

## Tests
- added: <N>
- total: <N>
- passing: <N>
- failing: <N>

## Build status
- typecheck: <pass/fail>
- lint: <pass/fail>
- build: <pass/fail>

## Issues encountered
- <issue 1 + how resolved>
- <issue 2 + how resolved>
```

## Next step
When done, call: `ultrapilot_run.py report --phase build --result /tmp/build-result.md`
