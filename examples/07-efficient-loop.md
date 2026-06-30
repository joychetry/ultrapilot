---
name: example-efficient-loop
description: "Worked example — the new single-command orchestrator loop with token-optimized lazy phase loading, showing 82% token reduction vs the old full-spec design."
type: example
---

# Example 07: Efficient Single-Command Loop

The new ultrapilot loop is **state-machine driven**, **token-optimized**, and **single-command by default**. This example walks through the same "build sponsorship dashboard" task that examples 01 and 06 used, and shows the actual prompt the agent sees at each phase.

## Setup

```bash
# One goal, set once
python3 ~/.hermes/skills/ultrapilot/scripts/ultrapilot_goals.py set \
  --profile secure \
  --tokens 250K \
  "build the sponsorship dashboard"
```

Output:

```
Goal set.
Goal #d8a3116c
  Objective:     build the sponsorship dashboard
  Status:        active
  Profile:       secure
  Agent:         claude
  Weights:       correctness=25, cost=5, efficiency=5, reliability=15, safety=45, ux=5
  Tokens:        0 / 250K (0%)
  ...
```

## Turn 1: Get the explore phase prompt

```bash
python3 ~/.hermes/skills/ultrapilot/scripts/ultrapilot_run.py next
```

The agent sees **only the explore phase prompt** (200 tokens), not 2000+ lines of full spec:

```
# ultrapilot — next phase: explore

Goal: build the sponsorship dashboard
Profile: secure
Verbosity: compact
Prompt tokens (estimate): 200
Goal budget remaining: 250K

---

# Phase: Explore

## Goal
Produce a tight architecture map of the current project. Do not edit any files.

## What to do
1. Read the project structure (`ls`, `find`, or read tools).
2. Identify: framework, language, package manager, test command, styling system, ...
3. Output a structured map (see Output Format below).

## Output Format
[... ~150 tokens of structured format spec ...]

## Next step
When done, call: `ultrapilot_run.py report --phase explore --result /tmp/explore-result.txt`
```

**Token cost this turn: 200 tokens** (vs. 2,000+ in the old design)

The agent reads the project, produces the architecture map, writes it to `/tmp/explore-result.txt`, then:

```bash
python3 ~/.hermes/skills/ultrapilot/scripts/ultrapilot_run.py report \
  --phase explore \
  --result /tmp/explore-result.txt \
  --passed
```

Output:

```
Phase explore recorded: passed=True
Next phase: plan
```

## Turn 2: Get the plan phase prompt

```bash
python3 ~/.hermes/skills/ultrapilot/scripts/ultrapilot_run.py next
```

The agent sees **only the plan phase prompt** (250 tokens). The explore output is referenced by path, not re-included:

```
# ultrapilot — next phase: plan

Goal: build the sponsorship dashboard
Profile: secure
Verbosity: compact
Prompt tokens (estimate): 250
Goal budget remaining: 250K

---

# Phase: Plan

## Goal
Produce a tight, scoped plan with verifiable acceptance criteria. Do not edit code yet.

## What to do
1. If the goal is unclear, ask the user the minimum questions needed.
2. If the goal is clear, write the plan directly.
3. The plan MUST include: Goal, Acceptance Criteria, Files, Steps, Assumptions, Out of Scope, Verification.

[... ~150 tokens of plan format spec ...]

## Next step
When done, call: `ultrapilot_run.py report --phase plan --result /tmp/plan-result.md`
```

**Token cost this turn: 250 tokens**

The agent reads the explore output from `/tmp/explore-result.txt` to inform the plan, writes the plan, and reports.

## Turn 3-4: Build

```bash
python3 ~/.hermes/skills/ultrapilot/scripts/ultrapilot_run.py next
```

The agent sees the build prompt (250 tokens), executes the plan's steps, writes the build summary, and reports.

## Turn 5: Verify

The agent gets the verify prompt (220 tokens), runs the actual checks, reports pass/fail.

**If verify fails:** the runner automatically dispatches back to `build` with the bug report. The agent fixes and re-verifies.

**If verify passes:** the runner advances to `review`.

## Turn 6: Review

The agent gets the review prompt (400 tokens — the largest, because it has 4 reviewer roles), runs the multi-perspective audit, reports.

**If connected issues found:** the runner dispatches to `patch` (turn 7), which gets a 200-token prompt to apply the fixes, then loops back to `verify` (turn 8).

**If clean:** the runner advances to `audit` (turn 7 or 8).

## Turn 7-8: Audit (the gate)

The agent gets the audit prompt (500 tokens — the largest, because it has the 6-step audit procedure). It must produce real evidence (test output, file contents) for every deliverable claim. The script computes the aggregate and checks the floors.

**If audit passes:** the agent runs `ultrapilot_goals.py complete` and the goal is done.

**If audit fails:** the runner dispatches back to the relevant phase (build, usually) to address the blockers.

## Token accounting (the entire run)

| Phase | Prompt size (compact) | Cumulative |
|-------|------------------------|------------|
| explore | 200 | 200 |
| plan | 250 | 450 |
| build | 250 | 700 |
| verify | 220 | 920 |
| review | 400 | 1,320 |
| patch (if needed) | 200 | 1,520 |
| audit | 500 | 2,020 |

**Total prompt tokens for a 7-phase clean run: ~2,000 tokens.**

In the old design, the agent would have loaded:
- Full SKILL.md (470 lines ≈ 4,000 tokens)
- 7 command specs (200-300 lines each ≈ 14,000 tokens)
- Goal spec (232 lines ≈ 2,000 tokens)
- Discipline spec (199 lines ≈ 1,800 tokens)
- Total: **~22,000 tokens upfront**

**Reduction: 91% (22,000 → 2,000)**

Even on a small token budget where the runner picks "minimal" verbosity:

| Phase | Prompt size (minimal) |
|-------|------------------------|
| explore | 50 |
| plan | 50 |
| build | 50 |
| verify | 50 |
| review | 100 |
| patch | 50 |
| audit | 150 |
| **Total** | **500 tokens** |

**Reduction at minimal: 98% (22,000 → 500)**

## What changed in the design

### Before (v3 — docs-driven)
- Agent reads full SKILL.md on every run
- Agent reads all 7 command specs
- Agent reads the goal spec
- Agent reads the discipline spec
- Agent improvises the control flow
- "Dispatch verify after build" is a markdown suggestion
- Total: ~22,000 tokens loaded, no enforcement

### After (v4 — script-driven)
- Runner script enforces the state machine
- Each phase prompt is loaded only when needed
- Prior phase results are referenced by path, not re-loaded
- Prompt size adapts to the remaining budget
- Total: ~2,000 tokens, full control flow enforcement

## What the user sees

The user types one command:

```
/ultrapilot build the sponsorship dashboard
```

The agent handles everything else. The user sees the progress via `status`:

```
# ultrapilot run status

Goal: build the sponsorship dashboard
Profile: secure
Status: active

## Phase progress

- ✅ explore — passed=True, result=/tmp/explore-result.txt
- ✅ plan    — passed=True, result=/tmp/plan-result.md
- ✅ build   — passed=True, result=/tmp/build-result.md
- ✅ verify  — passed=True, result=/tmp/verify-result.md
- ⏳ review  — NEXT
- ⏸ patch   — pending
- ⏸ audit   — pending

Next phase: review
Tokens used: 87K / 250K
```

At the end, the user sees the final scorecard:

```
# ultrapilot:goals run complete
Profile: secure
Scorecard:
  - Correctness:  95/100  (weight 25%)  contribution: 23.75
  - Reliability:  78/100  (weight 15%)  contribution: 11.70
  - Efficiency:   85/100  (weight  5%)  contribution:  4.25
  - Safety:       95/100  (weight 45%)  contribution: 42.75
  - UX:           88/100  (weight  5%)  contribution:  4.40
  - Cost:         92/100  (weight  5%)  contribution:  4.60
  - Aggregate:    91.45%
Floors: all satisfied
Result: COMPLETE
```

## Companion commands (still work, now as shortcuts)

The user can still call individual phases:

```
/ultrapilot:plan    # jumps to plan phase
/ultrapilot:build   # jumps to build phase
/ultrapilot:review  # jumps to review phase
```

But these are now just `goto <phase> && next` wrappers. The default `/ultrapilot` invocation is the canonical entry point and does the right thing automatically.

## Comparison: which design for which situation?

| Situation | Use |
|-----------|-----|
| User wants a one-command full lifecycle | `/ultrapilot` |
| User wants to skip ahead to a specific phase | `/ultrapilot:<phase>` |
| Agent wants to invoke a phase programmatically | `ultrapilot_run.py goto <phase> && next` |
| Trivial task (rename, typo) | Just ask the model directly |
| Long-running multi-day task | Set token budget + run multiple sessions |

## Droid support

Droid is fully supported as of v4:

```bash
# Droid will auto-detect from $DROID_HOME or $FACTORY_API_KEY
DROID_HOME=/Users/droid python3 ~/.hermes/skills/ultrapilot/scripts/ultrapilot_goals.py set "..."

# Or invoke from droid exec:
droid exec --auto medium "$(cat ~/.hermes/skills/ultrapilot/scripts/ultrapilot_run.py next)"
```

The runner is agent-agnostic — it works with Claude Code, Codex, Gemini CLI, Cursor, Aider, **Droid**, and any other LLM coding tool that can run subprocess commands.
