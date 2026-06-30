---
name: methodology
description: "Why the explore → plan → build → verify → review → patch loop works. The cognitive science behind structured engineering workflows for AI agents."
type: reference
---

# Methodology — Why the Loop Works

This document explains the design rationale behind `/ultrapilot`. It is the answer to "why this loop and not a cleverer prompt?"

## The core insight

> The model is not magic. **The loop is the magic.**

Modern AI models are extremely capable at any single step. The failure mode is not "the model can't write the code." The failure mode is "the model skips the boring engineering steps and then acts confident."

The fix is not a smarter prompt. The fix is a **structured loop with explicit gates between phases.** Each phase has a clear input, a clear output, and a clear failure mode. If a phase fails, the loop does not advance. If a phase succeeds, the next phase gets a known-good input.

This is the same principle that makes TDD, CI/CD, and code review work for human engineers. It is not specific to AI. It is good engineering applied to a new kind of executor.

## The six phases, justified

### Why Explore first

A model that edits a codebase it hasn't read is gambling. It will make assumptions about file structure, naming conventions, dependency versions, and architectural patterns. Some of those assumptions will be wrong. The cost of each wrong assumption is a broken build, a failing test, or a refactor.

A 2-minute read-only exploration prevents 20 minutes of "let me check how the existing code does this" thrashing during the build phase. It also surfaces constraints the model would not see otherwise (existing types, conventions, dependencies that aren't in the package.json readme).

**The cost of skipping explore:** model builds a feature that doesn't match the codebase, gets it 80% right, then has to refactor half of it.

**The cost of running explore:** 2 minutes of context. Zero side effects.

The trade-off is obvious. Explore is non-negotiable for existing codebases.

### Why Plan before Build

A model that starts building without a plan will make implicit decisions about scope, architecture, and acceptance criteria. The user will not see those decisions until the model is 80% done with something they didn't want.

A plan forces those decisions to be explicit, in front of the user, before any code is written. The user can correct the plan in 30 seconds. Correcting a half-built feature takes 30 minutes.

**A good plan is also a contract.** When the build phase is done, the verify phase can check against the plan's acceptance criteria. Without a plan, verify has nothing to check against.

### Why Build in small steps

A model that builds the entire feature in one shot has no checkpoints. If something breaks at step 47 of 50, the model has to debug a half-built feature with a half-understood state. That's hard for humans. It's brutal for AI.

A model that builds one step at a time, and verifies each step, has a known-good state at every checkpoint. If something breaks, the rollback is one step. The debug surface is small.

**Small steps also let the user steer.** If the model goes off-rails at step 4, the user can stop it and redirect before the wrong direction has compounded.

### Why Verify with actual checks

A model that says "I think this works" is guessing. A model that says "I ran `npm test` and got `12 passed, 0 failed`" is reporting.

The difference is the difference between a vibe and an engineering outcome. Verification is not a vibe. It is a command output.

**The model also has a confirmation bias problem.** Once it has produced code, it is invested in that code being correct. Self-reported "it works" claims are unreliable. Actual test output is reliable.

### Why Review the diff

Verification checks "does it work?" Review checks "does it work *for the goal*?" These are different questions.

A feature can pass all tests and still be wrong:
- Tests cover the happy path but not the edge cases
- Type checks pass but a runtime error lurks
- Lint passes but the UX is broken on mobile
- The feature works but the implementation introduced duplication

The review pass catches these. It is the model auditing its own work with fresh eyes.

### Why Patch, not rewrite

When the reviewer finds issues, the patch phase makes targeted fixes. It does not rewrite the whole feature. This is for the same reason as small build steps: the diff is the product. Surgical patches are reviewable. Wholesale rewrites are not.

## What this loop is not

This loop is not:

- **A replacement for thinking.** The user still has to provide the goal, the constraints, and the acceptance criteria. The loop structures the work; it does not invent the work.
- **A silver bullet.** A bad model with this loop will produce bad code. A good model with this loop will produce good code. The loop widens the gap between good and bad models; it does not eliminate the bad ones.
- **A substitute for review by humans.** A human should still review the final diff before merging. The loop catches model-introduced errors. It does not catch requirement mismatches, design flaws, or business logic bugs that the model is not equipped to see.

## When the loop is overkill

The loop is overkill for:

- Renaming a single variable
- Fixing a typo
- A one-line config change
- Pure questions or research

For these, just ask the model directly. The loop adds value when the task has scope, multiple files, and a verifiable end state. If the task has none of those, the loop is bureaucracy.

## The deeper principle

The loop embodies one principle: **structure beats intelligence.**

A model with mediocre capability and a strong loop will outperform a model with top capability and no structure. The loop catches the errors. The loop surfaces the trade-offs. The loop gives the model feedback at every step. Without that feedback, even the best model drifts.

This is why `/ultrapilot` exists. Not to make the model smarter. To give the model a workflow that makes its existing capability reliable.
