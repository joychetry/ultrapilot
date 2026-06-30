---
name: ultrapilot-plan
description: "/ultrapilot:plan — Produce a tight, scoped implementation plan. Brainstorms if the goal is unclear. Standalone phase command for the ultrapilot orchestrator."
license: MIT
allowed-tools: Bash, Read, Write, Grep, Glob
metadata:
  author: joychetry
  version: "1.0"
  category: software-development
  parent: ultrapilot
---

# /ultrapilot:plan

**Phase 2 of /ultrapilot.** Write a tight, scoped plan before any code is written.

## When to Use

- Before any non-trivial implementation
- When a task is vague and needs scoping
- When the user has a goal but no concrete steps
- Before handing off work to another agent or human

## How to Invoke

```
/ultrapilot:plan build a sponsorship dashboard inside this app — track brand deals, deliverables, deadlines, invoice status, contacts
```

```
/ultrapilot:plan migrate auth from JWT to session cookies
```

## The Plan Must Be

1. **Scoped** — clear boundaries, no "and also" features
2. **Concrete** — real file paths, real function names, real data shapes
3. **Verifiable** — completion has a checkable end state
4. **Stepped** — broken into small, independent tasks

A good plan answers these questions before any code is written:

- What files will change?
- What new files will be created?
- What assumptions are we making?
- What are the acceptance criteria?
- How will we verify success (tests, build, manual flow)?
- What is explicitly out of scope?

## Brainstorm Mode

If the goal is unclear, the plan phase becomes a brainstorm. Ask the user the questions needed to make the goal concrete. Do not proceed to build with a vague goal.

**Questions to ask (pick the relevant ones, do not dump all of them):**
- What is the user's workflow that this is supposed to support?
- Which existing screen / flow does this hook into?
- What data does this need to read / write?
- What are the edge cases (empty, error, auth failure, slow network)?
- What is explicitly NOT in scope for this change?

Once you have enough to write the plan, write it. Do not keep asking forever.

## Plan Output Format

```markdown
# Plan: [task name]

## Goal
[One-sentence goal]

## Acceptance Criteria
- [ ] [Criterion 1 — must be testable]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Files to Change
- `path/to/file.ts` — [what changes]
- `path/to/new-file.ts` — [new file purpose]

## Files to Create
- `path/to/new.ts` — [purpose]

## Steps
1. [Step 1 — small, verifiable]
2. [Step 2]
3. [Step 3]

## Assumptions
- [Assumption 1]
- [Assumption 2]

## Out of Scope
- [Explicit non-goal 1]
- [Explicit non-goal 2]

## Verification
- [How to test this — specific commands, specific flows]
```

## Pitfalls

- **Do not write a vague plan.** "Add a dashboard" is not a plan. "Add a `/dashboard` page at `app/dashboard/page.tsx` showing the user's brand deals with columns: brand, value, status, deadline" is a plan.
- **Do not plan what you do not need to plan.** If the user asked to rename a button, you do not need a 5-step plan. Just say "rename the button."
- **Do not skip the out-of-scope section.** That section is what stops scope creep mid-build.

## Related Commands

- `/ultrapilot:explore` — run before plan if you have not mapped the codebase
- `/ultrapilot:build` — runs after plan approval
- `/ultrapilot` — full orchestrator
