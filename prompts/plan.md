---
phase: plan
verbosity: compact
tokens_estimate: 250
---

# Phase: Plan

## Goal
Produce a tight, scoped plan with verifiable acceptance criteria. Do not edit code yet.

## What to do
1. If the goal is unclear, ask the user the minimum questions needed. Do not dump 10 questions — pick the 2-3 that block planning.
2. If the goal is clear, write the plan directly.
3. The plan MUST include:
   - Goal (1 sentence)
   - Acceptance criteria (testable checkboxes)
   - Files to change / create
   - Steps (numbered, max 8)
   - Assumptions
   - Out of scope (explicit non-goals)
   - Verification (specific commands + flows)

## Rules
- A plan is a contract. Vague plans produce vague code.
- The plan's acceptance criteria become the correctness dimension in the goal audit.
- If the explore phase produced a map, USE IT — match existing conventions, don't invent new ones.

## Output Format

```markdown
# Plan: <task name>

## Goal
<one sentence>

## Acceptance Criteria
- [ ] <criterion 1>
- [ ] <criterion 2>
- [ ] <criterion 3>

## Files to Change
- `<path>` — <what changes>

## Files to Create
- `<path>` — <purpose>

## Steps
1. <step 1>
2. <step 2>
3. <step 3>

## Assumptions
- <assumption>

## Out of Scope
- <non-goal>

## Verification
- <test command + expected result>
- <manual flow + expected behavior>
```

## Next step
When done, call: `ultrapilot_run.py report --phase plan --result /tmp/plan-result.md`
