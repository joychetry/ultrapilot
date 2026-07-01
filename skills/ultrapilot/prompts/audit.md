---
phase: audit
verbosity: compact
tokens_estimate: 500
---

# Phase: Completion Audit

## Goal
Real evidence for every claim. Self-assessment is not evidence. The audit decides if the goal is done.

## The objective
`OBJECTIVE: <filled in by runner>`

## Active weight configuration
`WEIGHTS: <filled in by runner>`
Aggregate threshold: 80
Floors: safety ≥ 60, correctness ≥ 70
No dimension < 50

## Step 1: Restate the objective
Convert the goal text above into a numbered list of concrete deliverables.
Each deliverable is one testable statement. "It works" is not a deliverable.
"the failing test in test/auth.test.ts:42 now passes and no other test regressed" is.

## Step 2: Build a deliverable checklist
For each deliverable, list the evidence that proves it was done:

```json
[
  {
    "deliverable": "<concrete thing>",
    "evidence_required": ["<command or file or test>"],
    "evidence_found":   ["<actual output, actual file content>"],
    "status":           "PASS | FAIL | PARTIAL"
  }
]
```

Inspect actual files, run actual commands, read actual test output. Do not infer.

## Step 3: Identify blockers
List every deliverable with `status: FAIL` or `status: PARTIAL`. These are blockers.

## Step 4: Score each dimension 0-100
```json
{
  "correctness": <0-100>,
  "reliability": <0-100>,
  "efficiency":  <0-100>,
  "safety":      <0-100>,
  "ux":          <0-100>,
  "cost":        <0-100>
}
```

## Step 5: Submit the audit

```bash
ultrapilot-goals record-audit \
  --checklist '<the JSON array from step 2>' \
  --missing  '<JSON array of blockers>' \
  --scores   '<the JSON object from step 4>' \
  --passed   # include if no blockers
```

The script computes the aggregate, checks the floors, and returns pass/fail.

## Step 6: If the script returned `passed: true`
```bash
ultrapilot-goals complete
```

Otherwise: loop back to the relevant phase and address the blockers.

## Next step
The runner will detect audit completion and either declare the goal done or dispatch the next phase.
