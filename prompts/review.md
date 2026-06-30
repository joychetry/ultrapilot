---
phase: review
verbosity: compact
tokens_estimate: 400
---

# Phase: Review

## Goal
Multi-perspective diff audit. Independent validation. High-signal only.

## 4 reviewers (run them sequentially or in parallel)

**Reviewer 1 — Convention compliance**
- Read `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, or equivalents in the affected directories.
- Find clear, unambiguous violations of those rules.
- Output: list of issues with file:line + the rule violated.

**Reviewer 2 — Bug detection (diff-only)**
- Scan the diff itself. Do not consult surrounding context.
- Flag only significant bugs that produce wrong results regardless of inputs.
- Skip nitpicks, style, "could be cleaner."

**Reviewer 3 — Bug detection (context-aware)**
- Read the changed code AND its callers.
- Look for: security issues, type errors, broken control flow, missing error handling.
- Scoped to the changed code, not the whole codebase.

**Reviewer 4 — Convention compliance (independent pass)**
- Same as Reviewer 1, but launched separately so it does not see Reviewer 1's output.

## For each issue, validate
- Is it real? (Re-check the file/line)
- Is it in the changed code? (Not pre-existing)
- Is it on the "flag" list (not on the "do not flag" list)?
- Is it fixable?

**Flag these (high signal):**
- Compile/parse errors, type errors, missing imports
- Code that produces wrong results regardless of inputs
- Clear, unambiguous project-instruction violations (with the exact rule quoted)
- Security vulnerabilities introduced by the change
- Data loss or corruption risks

**Do NOT flag (false positives):**
- Pre-existing issues in unchanged code
- Pedantic nitpicks
- Linter-detectable issues (the linter ran in verify)
- General code quality concerns unless explicitly required
- Issues mentioned in project instructions but explicitly silenced (e.g., via lint ignore)

## Output Format

```markdown
# Review Report

## Validated issues
1. **[category]** `<file>:<line>` — <description>
   - Rule / check violated: <quote>
   - Suggested fix: <one line>
   - [PASS]

2. **[category]** `<file>:<line>` — <description>
   - [REJECTED — false positive: <reason>]

## Drive-by candidates (noted, not blockers)
- `<file>:<line>` — <description> (pre-existing, not from this diff)

## Reviewer summary
| Reviewer | Flagged | Validated | Reported |
|----------|---------|-----------|----------|
| Convention | <N> | <N> | <N> |
| Bug diff-only | <N> | <N> | <N> |
| Bug context | <N> | <N> | <N> |
| Convention (2) | <N> | <N> | <N> |
| **Total** | <N> | <N> | <N> |
```

## Next step
`ultrapilot_run.py report --phase review --result /tmp/review-result.md`

If the report has connected issues, loop back to build (the runner will dispatch).
