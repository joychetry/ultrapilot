---
name: ultrapilot-steer
description: "/ultrapilot:steer — Tighten a vague plan mid-flight. Steering, not micromanaging. Standalone phase command for the ultrapilot orchestrator."
license: MIT
allowed-tools: Bash, Read, Grep, Glob
metadata:
  author: joychetry
  version: "1.0"
  category: software-development
  parent: ultrapilot
---

# /ultrapilot:steer

**Mid-flight intervention.** The plan is vague. The model is about to build the wrong thing. Steer it back.

## When to Use

- The orchestrator detects a vague step in the plan
- The model proposes a "build everything at once" approach
- The model chooses a technology / pattern that does not match the existing codebase
- The model goes off-rails mid-build

## How to Invoke

```
/ultrapilot:steer
```

Or with a specific concern:

```
/ultrapilot:steer the plan says "add persistence" — clarify which one
```

## Steering Patterns

**Vague plan → ask for specifics:**

| Vague | Steer to |
|-------|----------|
| "Add dashboard components" | "Which components, where, and how will you test them?" |
| "Add persistence" | "Local storage, SQLite, Supabase, or the existing database?" |
| "Add validation" | "Client-side, server-side, or both? Which library?" |
| "Add auth" | "Which provider? New users or existing? What are the protected routes?" |
| "Refactor the auth module" | "What is the target pattern? What tests must still pass?" |
| "Make it work on mobile" | "Which breakpoints? Which screens? Which interactions?" |

**Wrong-direction → reset to last good checkpoint:**

If the model has already started building the wrong thing:
1. Stop the build
2. Identify the last good checkpoint (last passing test, last green build, last plan step that worked)
3. Re-plan from that point
4. Resume

Do not let the model dig deeper into a wrong direction. Reset is cheaper than patch.

**Scope creep → redirect to plan:**

If the model starts adding features that are not in the plan:
1. Stop
2. Reference the plan
3. Add the new feature to a "future candidates" list, not the current build

## What Steering Is NOT

Steering is not:
- Dictating every line of code
- Pre-deciding the implementation
- Doing the work for the model
- Rejecting the model's choices because of personal preference

Steering IS:
- Making sure the model does not build the wrong thing
- Forcing the plan to be concrete enough to verify
- Catching wrong-direction choices early
- Re-anchoring the model to the goal

## When to Let It Build

Once the plan is concrete and matches the existing codebase, **let the model execute.** Do not steer every decision. Trust the model for the in-line implementation details. Only intervene when something is off-rails.

## Pitfalls

- **Do not over-steer.** If you intervene on every decision, you are doing the work, not orchestrating.
- **Do not under-steer.** If the model is building a SQL database for a project that uses Supabase, you must intervene.
- **Do not re-plan in the middle of a build unless something is actually wrong.** Re-planning mid-build for stylistic reasons wastes the work that was already done.

## Related Commands

- `/ultrapilot:plan` — for full re-planning
- `/ultrapilot:build` — returns here after steering
- `/ultrapilot` — full orchestrator
