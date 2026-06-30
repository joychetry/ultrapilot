---
name: example-discipline-gate
description: "Worked example — discipline activation gate decisions across five different task profiles, showing when the King Mode-derived layer is loaded and when it is not."
type: example
---

# Example 05: Discipline Activation Gate

Five task profiles showing the discipline gate in action. The gate decides whether to load `/ultrapilot:_discipline` (generalized King Mode) or use the default concise behavior.

---

## Task Profile 1 — "rename a button"

**User prompt:**
```
/ultrapilot rename the "Submit" button to "Save changes"
```

**Gate evaluation:**

| Signal | Value | Trigger? |
|--------|-------|----------|
| File count | 1 (probably) | No (< 3) |
| Line count | <10 | No (< 100) |
| New abstractions | None | No |
| Cross-cutting | None | No |
| Multi-service | No | No |
| Architectural decision | No | No |
| Prompt length | 8 words | No (< 200) |
| Keywords | "rename" — not on the trigger list | No |
| ULTRATHINK | Absent | No |
| `--deep` | Absent | No |
| `--quick` | Absent | No override |

**Decision:** **Discipline OFF.** Default concise behavior.

**Why:** AICodeKing's own advice — "If you want to rename a button, just ask it to rename the button. If you use deep reasoning on every small edit, you waste quota and make the model overcomplicate things."

The orchestrator dispatches the build command. The model renames the button. Verification confirms the change. Done in 1 turn.

---

## Task Profile 2 — "fix the mobile pipeline layout"

**User prompt:**
```
/ultrapilot fix the mobile pipeline layout — columns overflow horizontally on viewports under 768px
```

**Gate evaluation:**

| Signal | Value | Trigger? |
|--------|-------|----------|
| File count | 1–2 estimated | No |
| Line count | <50 | No |
| New abstractions | No | No |
| Cross-cutting | No | No |
| Multi-service | No | No |
| Architectural decision | No (existing layout, just responsive fix) | No |
| Prompt length | 13 words | No |
| Keywords | "fix" — not on the trigger list | No |
| ULTRATHINK | Absent | No |
| `--deep` | Absent | No |

**Decision:** **Discipline OFF.** Default concise behavior.

**Why:** This is a focused bug fix in a small number of files. The orchestrator's plan phase will probably produce 2–3 steps. Even if it produces more, the task is bounded and well-defined. Discipline would add overhead without changing the outcome.

The orchestrator runs explore → plan (3 steps) → build → verify → review. Done in 2 turns.

---

## Task Profile 3 — "migrate the auth module from JWT to session cookies"

**User prompt:**
```
/ultrapilot migrate the auth module from JWT to session cookies — all call sites must compile and existing tests must pass
```

**Gate evaluation:**

| Signal | Value | Trigger? |
|--------|-------|----------|
| File count | 47 call sites + middleware files = ~50 files | **YES** (> 3) |
| Line count | Will likely be >1000 | **YES** (> 100) |
| New abstractions | Possibly (session management pattern) | **YES** |
| Cross-cutting | **YES** (auth, security) | **YES** |
| Multi-service | No | No |
| Architectural decision | Yes (replacing one auth pattern with another) | **YES** |
| Prompt length | 21 words | No |
| Keywords | "migrate" — **on the trigger list** | **YES** |

**Decision:** **Discipline ON.** Load the discipline layer.

**Why:** Three independent triggers fired before the keyword check. This is exactly the kind of task that benefits from:
- Multi-dimensional analysis (security, correctness, maintainability all matter)
- Project discipline (don't introduce new auth libraries mid-migration)
- Prohibition on surface-level logic (auth migrations are notorious for "looks done" but isn't)

The orchestrator runs the full loop with discipline active. The model is more careful about each call site. Review catches more issues. Higher quality output, but more turns consumed.

This is the trade-off the gate is designed to make: spend more on the tasks that need it, less on the ones that don't.

---

## Task Profile 4 — "refactor the entire notification system"

**User prompt:**
```
/ultrapilot refactor the entire notification system — currently we have 4 separate implementations (email, SMS, push, in-app) all with different APIs. Standardize them behind a single NotificationService interface, keep backward compatibility for the next release, and ensure all existing tests still pass. Stop after 30 turns or when all tests pass.
```

**Gate evaluation:**

| Signal | Value | Trigger? |
|--------|-------|----------|
| File count | 4+ services + tests + adapters = 20+ files | **YES** |
| Line count | Will likely be >500 | **YES** |
| New abstractions | **YES** (NotificationService interface) | **YES** |
| Cross-cutting | **YES** (touches every consumer of notifications) | **YES** |
| Multi-service | **YES** (4 notification services) | **YES** |
| Architectural decision | **YES** (standardizing interfaces) | **YES** |
| Prompt length | 76 words | No |
| Keywords | "refactor", "system", "entire" — **multiple matches** | **YES** |
| Explicit bound | "Stop after 30 turns" | (Not a trigger, but bounds the run) |

**Decision:** **Discipline ON.** Six independent triggers fired.

**Why:** Every signal is loud. This is a heavy refactor with backward-compat requirements, multiple existing services, and a new abstraction. Loading discipline is unambiguous.

The orchestrator runs the full loop with discipline active. The model:
- Reads every existing notification implementation (multi-lens analysis: consistency, maintainability, reversibility)
- Designs the interface carefully (project discipline: matches existing patterns)
- Catches the corner case where one service has sync-only behavior and another is async-only (the "if it feels easy, dig deeper" rule)
- Plans backward compat adapters explicitly
- Verifies every consumer

Without discipline, this would have shipped a half-baked interface that broke edge cases. With discipline, it shipped in 22 turns with 3 review-pass patches.

---

## Task Profile 5 — "ULTRATHINK: design the API for a new billing system"

**User prompt:**
```
/ultrapilot ULTRATHINK: design the API for a new billing system — needs to support subscriptions, one-time charges, refunds, proration, tax handling, multi-currency, and webhook delivery. Output a complete API spec.
```

**Gate evaluation:**

| Signal | Value | Trigger? |
|--------|-------|----------|
| File count | N/A (no code yet, design task) | No |
| Line count | N/A | No |
| New abstractions | **YES** (entire new system) | **YES** |
| Cross-cutting | **YES** (payments, money) | **YES** |
| Multi-service | **YES** (webhooks, multiple integrations) | **YES** |
| Architectural decision | **YES** (designing from scratch) | **YES** |
| Prompt length | 33 words | No |
| Keywords | "design", "system" — **matches** | **YES** |
| ULTRATHINK | **Present** | **YES (explicit trigger)** |

**Decision:** **Discipline ON + ULTRATHINK ACTIVE.** The explicit trigger fires regardless of any other signal.

**Why:** The user explicitly invoked ULTRATHINK. That is the bypass for the gate. The orchestrator loads the discipline module AND activates the ULTRATHINK response format (deep reasoning chain, edge case analysis, then output).

For a billing system, this is correct. Money-handling code is exactly where surface-level logic kills you. ULTRATHINK forces the model to dig deeper than the obvious REST endpoints.

The orchestrator dispatches explore (the codebase doesn't have a billing system yet, so this maps to a greenfield plan) → plan → build (with the discipline layer active throughout, ULTRATHINK format on) → verify → review.

The review phase flags fewer issues because the design phase caught them. The verify phase runs successfully. Done in 8 turns with high confidence.

---

## Summary Table

| Profile | Decision | Why | Estimated turns |
|---------|----------|-----|-----------------|
| 1. Rename a button | OFF | Trivial, single file | 1 |
| 2. Fix mobile layout | OFF | Focused bug fix | 2 |
| 3. Auth migration | **ON** | 3+ triggers (size, security, keyword) | 12 |
| 4. Refactor notification system | **ON** | 6 triggers (all signals loud) | 22 |
| 5. ULTRATHINK: design billing API | **ON + ULTRATHINK** | Explicit user trigger | 8 |

**Pattern:** discipline is loaded when the task complexity justifies it. Trivial tasks skip it. Heavy tasks get it. Explicit user triggers always activate it. The gate is a cost-control mechanism, not a discipline check.

## What the orchestrator logs

After the gate decides, the orchestrator logs the decision for transparency:

```
[ultrapilot] Discipline gate evaluation:
  - file_count: 47 (> 3) → TRIGGER
  - cross_cutting: auth, security → TRIGGER
  - keyword: "migrate" → TRIGGER
  - explicit: none
  - override: none
  Decision: LOAD discipline module

[ultrapilot] Discipline module loaded for this run.
[ultrapilot] ULTRATHINK is available (will activate on user trigger).
```

The log goes to the transcript, not the user's terminal by default. It is there for debugging and tuning the gate later.
