---
name: ultrapilot-verify
description: "/ultrapilot:verify — Run the actual verification suite. Tests, type checks, lint, manual flow checks. Standalone phase command for the ultrapilot orchestrator."
license: MIT
allowed-tools: Bash, Read, Grep, Glob
metadata:
  author: joychetry
  version: "1.0"
  category: software-development
  parent: ultrapilot
---

# /ultrapilot:verify

**Phase 4 of /ultrapilot.** Prove the work. Run the actual checks. Do not infer.

## When to Use

- After the build phase, before the review phase
- Whenever the model claims something "works" without running it
- For UI work, after every meaningful change

## How to Invoke

```
/ultrapilot:verify
```

Or with a focus area:

```
/ultrapilot:verify focus on the dashboard flow
```

## Verification by Work Type

### Backend / Logic

- Run the test suite. Did the new tests pass? Did the existing tests still pass?
- Run type checks (TypeScript, mypy, etc.). Zero errors.
- Run lint. Zero errors.
- If the change touches data persistence, run a migration dry-run.
- If the change touches auth or permissions, run those tests explicitly.

### UI / Frontend

- Run the app and preview it.
- Click through the main user flow that was changed.
- Open dev tools, check the console for errors.
- Resize to mobile, check the layout.
- Test edge cases: empty state, loading state, error state.
- Check accessibility (keyboard nav, screen reader labels, contrast).

### API / Integration

- Hit the endpoint with the documented request shape.
- Check the response shape and status code.
- Check auth and permission boundaries.
- Check error responses.
- Check rate limits if they exist.

## Required Output

The verification step must produce:

1. **List of checks run** (specific commands, not "tests pass")
2. **Pass/fail per check** with the actual output
3. **Any failures with reproduction steps**

If verification fails, do not declare success. The build phase is not done. The orchestrator will loop back to `/ultrapilot:build` to fix the failure.

## Bug Report Format

When a check fails, format the report to the model like this:

> **Failure:** [exact observed behavior]
> **Expected:** [exact expected behavior]
> **Smallest possible cause:** [model's hypothesis, tested before patch]
> **Reproduction:** [steps to trigger it]

Specific bug reports produce specific fixes. "Fix the app" produces wasted tokens.

## Pitfalls

- **Do not skip running the actual checks.** A test that you "think will pass" has not passed.
- **Do not just check the happy path.** Edge cases are where the bugs hide.
- **Do not trust successful-looking output.** AI-generated apps can look good and still be broken.
- **Do not run the same check twice to "be sure."** If it passed once with the same code, it will pass again. Move on.

## Related Commands

- `/ultrapilot:build` — runs before verify
- `/ultrapilot:review` — runs after verify
- `/ultrapilot` — full orchestrator
