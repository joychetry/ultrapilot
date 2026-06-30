---
phase: verify
verbosity: compact
tokens_estimate: 220
---

# Phase: Verify

## Goal
Run the actual checks. Prove the work. Do not infer.

## What to do

### Backend / logic
- [ ] Run the test suite. Capture exit code + pass/fail count.
- [ ] Run type check (TypeScript, mypy, etc.). Zero errors.
- [ ] Run lint. Zero errors.
- [ ] If migration, run dry-run.

### UI / frontend
- [ ] Run the app, preview it.
- [ ] Click through the main user flow.
- [ ] Open dev tools, check console: 0 errors.
- [ ] Resize to mobile, check the layout.
- [ ] Test edge cases: empty, loading, error states.

### API / integration
- [ ] Hit the endpoint with the documented request.
- [ ] Check response shape and status code.
- [ ] Check auth / permission boundaries.
- [ ] Check error responses.

## Output Format

```markdown
# Verification Report

## Checks run
- <command> — <result>
- <command> — <result>

## Pass/fail
- ✅ <check>
- ❌ <check> — <failure details>

## Edge cases tested
- <edge case> — <result>

## Console / runtime
- errors: <N>
- warnings: <N>
```

## Next step
If all green: `ultrapilot_run.py report --phase verify --result /tmp/verify-result.md`
If failures: do not advance. Return to build phase with the bug report.
