---
phase: patch
verbosity: compact
tokens_estimate: 200
---

# Phase: Patch

## Goal
Apply the fixes the reviewer found. Re-verify after patching. No scope creep.

## Issues to fix
`REVIEW_PATH: <filled in by runner>`

## Rules
1. Apply the fixes exactly as the reviewer described them. No "while I'm here" refactors.
2. After each fix, re-run the relevant check from verify (tests, typecheck, lint).
3. If a fix surfaces a new issue, note it. Do not chase it now.
4. If a fix cannot be applied (e.g., the issue is wrong, the code does something different), push back on the reviewer and explain why.

## Output Format

```markdown
# Patch Summary

## Fixes applied
1. `<file>:<line>` — <one-line description of fix> → <result>
2. `<file>:<line>` — <one-line description of fix> → <result>

## Re-verification
- tests: <pass/fail>
- typecheck: <pass/fail>
- lint: <pass/fail>
- build: <pass/fail>

## Pushed-back issues (with reason)
- `<file>:<line>` — <issue> → <why the reviewer was wrong>

## Drive-by candidates added
- `<file>:<line>` — <description> (noted, not fixed)
```

## Next step
`ultrapilot_run.py report --phase patch --result /tmp/patch-result.md`

The runner will dispatch back to verify.
