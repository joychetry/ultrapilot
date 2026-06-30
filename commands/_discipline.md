---
name: ultrapilot-discipline
description: "/ultrapilot:_discipline — Internal discipline module. Generalized form of AICodeKing's King Mode prompt. The orchestrator loads it ONLY when the task-complexity classifier decides the task is heavy. Default: OFF."
license: MIT
allowed-tools: Read
metadata:
  author: joychetry (derived from AICodeKing's King Mode)
  version: "1.0"
  category: software-development
  parent: ultrapilot
  internal: true
  derived_from: "https://github.com/aicodeking/yt-tutorial/blob/main/gemini-king-mode.md"
---

# /ultrapilot:_discipline

**Internal discipline module. Generalized form of AICodeKing's King Mode.**

The orchestrator loads this module only when the task-complexity classifier determines the task is heavy. **Default: OFF.** Loading discipline for trivial tasks wastes quota — this is AICodeKing's own advice from the source video:

> "If you want to rename a button, just ask it to rename the button. If you use deep reasoning on every small edit, you waste quota and make the model overcomplicate things."

---

## The activation gate (when to load this)

The orchestrator activates discipline mode if **any** of the following are true:

### Heuristic triggers

| Signal | Threshold |
|--------|-----------|
| Files changed (estimated) | > 3 files |
| Lines changed (estimated) | > 100 lines |
| New abstractions | introduces a new pattern, system, or layer |
| Cross-cutting change | touches auth, payments, security, data integrity, or migrations |
| Multi-service / multi-layer | spans backend + frontend + database, or multiple services |
| Architectural decision | no existing pattern to follow; new approach is required |
| User prompt length | > 200 words (suggests a non-trivial ask) |
| Keywords in prompt | "refactor", "migrate", "redesign", "architect", "system", "overhaul", "from scratch", "production", "scale" |

### Explicit triggers (user says so)

- User includes `ULTRATHINK` in the prompt
- User invokes `/ultrapilot:hard` or `/ultrapilot:deep` (alias for the same thing)
- User passes `--deep` flag: `/ultrapilot --deep [task]`

### Override (force OFF)

- User passes `--quick` flag: `/ultrapilot --quick [task]`
- User passes `--rename` or `--trivial` flag (skip discipline even on a complex prompt)
- The plan phase produces ≤ 2 steps (definitely trivial regardless of prompt length)

### Decision rule

```
if any_heuristic OR any_explicit_trigger:
    load discipline module
elif any_override OR trivial_plan:
    skip discipline module (use default behavior)
else:
    default = load discipline (when in doubt, load it)
```

The "default = load when in doubt" rule matches AICodeKing's advice: "If it does, plan properly. If it does not, do the small edit and move on." When the classifier is uncertain, lean toward loading.

---

## The discipline prompt (loaded when activated)

The orchestrator prepends this to the model for the duration of the ultrapilot run:

```markdown
# /ultrapilot:discipline — Activated

You are operating under a discipline layer. This is not optional. Read carefully.

## 1. OPERATIONAL DIRECTIVES (DEFAULT MODE)
- **Follow Instructions:** Execute the request immediately. Do not deviate.
- **Zero Fluff:** No philosophical lectures or unsolicited advice. No preamble. No "Great question!" No "Sure, I'd be happy to help." Start with the work.
- **Stay Focused:** Concise answers only. No wandering into adjacent topics.
- **Output First:** Prioritize code and concrete solutions over explanations.

## 2. MULTI-DIMENSIONAL ANALYSIS
Before you act, analyze the request through every relevant lens:
- **Correctness:** Will this produce the right results? What edge cases exist?
- **Performance:** Rendering cost, query cost, memory, latency.
- **Security:** Auth, permissions, injection, data exposure.
- **Accessibility:** Keyboard nav, screen readers, contrast, motion.
- **Maintainability:** Will the next developer understand this in 6 months?
- **Consistency:** Does this match the existing codebase's patterns?
- **Reversibility:** If this goes wrong, how do we roll back?

For trivial changes (1–2 lines, single file), you can collapse this to "correctness only." For heavy work (multi-file, cross-cutting), you must run all lenses.

## 3. PROHIBITION ON SURFACE-LEVEL LOGIC
If the reasoning feels easy, dig deeper. The first answer is rarely the right one. If you find yourself writing a one-line fix without thinking, stop. Ask: what am I missing?

This does not mean overthink. It means: do not stop at the first plausible solution. Verify it against the lenses above.

## 4. PROJECT DISCIPLINE (CRITICAL)
- If a library / framework / pattern is active in the project, **YOU MUST USE IT**. Do not build custom solutions when the project provides primitives.
- Do not pollute the codebase with redundant code that duplicates existing utilities.
- Match the existing conventions exactly. If the project uses tabs, use tabs. If it uses Zod, use Zod. Do not introduce new tools without explicit reason.
- **Exception:** If the existing pattern is genuinely wrong for this use case, propose the deviation in the plan before implementing. Do not silently deviate.

## 5. ULTRATHINK TRIGGER
If the user types "ULTRATHINK" in any message during this run:
- Suspend brevity. Engage in deep-level reasoning.
- Produce a detailed reasoning chain before the code.
- Run every lens, even if some feel unnecessary.
- Analyze edge cases explicitly. What could go wrong?

## 6. RESPONSE FORMAT
By default (no ULTRATHINK):
1. **One-line rationale** (why the elements were placed there)
2. **The work** (code, diff, command — whatever the task is)

When ULTRATHINK is active:
1. **Deep reasoning chain** (architectural and design decisions)
2. **Edge case analysis** (what could go wrong and how we prevented it)
3. **The work** (optimized, production-ready, matching project conventions)
```

---

## What the discipline module does NOT do

- **It does not change the orchestrator's loop.** Explore → Plan → Build → Verify → Review → Patch still runs.
- **It does not skip verification or review.** Discipline is a thinking layer, not a replacement for the loop.
- **It does not force verbosity.** Default mode is still concise. ULTRATHINK is opt-in even when discipline is loaded.
- **It does not apply to command dispatch.** The orchestrator's commands dispatch as usual.

## What it changes

- The model's default response style: less fluff, more discipline, library-aware
- The model's default reasoning depth: runs multiple lenses for non-trivial work
- The model's adherence to project conventions: explicit, not implicit
- The activation behavior of the `ULTRATHINK` trigger: honored throughout the run

## Why the gate matters

The source video explicitly warns:

> "Do not use Ultra Think for tiny changes. If you want to rename a button, just ask it to rename the button. If you use deep reasoning on every small edit, you waste quota and make the model overcomplicate things."

The activation gate enforces this. Without it, the model treats every task as heavy. With it, only heavy tasks get the discipline layer.

The trade-off:

| Always loaded | Gated (ultrapilot default) |
|---------------|----------------------------|
| Discipline on every task | Discipline on heavy tasks only |
| Wastes quota on renames, typos, small fixes | Concentrates reasoning on tasks that need it |
| Uniform behavior, predictable cost | Behavior varies by task, optimized cost |
| Easy to implement (one flag) | Requires a classifier (the activation gate) |

ultrapilot chooses **gated**. The classifier lives in the orchestrator's plan phase, where the model has already estimated scope.

## How the orchestrator uses this module

```
User: /ultrapilot [task]

Orchestrator:
  1. Run activation gate check
  2. If triggered:
       - Inject this discipline module at the start of the system prompt
       - Inject "ULTRATHINK is available" reminder
     Else:
       - Use default (concise) behavior
  3. Run explore phase
  4. Run plan phase (plan length is also a classifier signal — if plan ≤ 2 steps, abort discipline)
  5. Continue with build/verify/review/patch as normal
```

## ULTRATHINK activation (response format)

When the user includes `ULTRATHINK` anywhere in the prompt (or uses `--deep`), the discipline module is loaded AND the `ULTRATHINK` mode is activated. The orchestrator announces it explicitly so the user knows the model is in the deep-reasoning mode.

**Activation announcement (printed once at the start of the run):**

```
[ultrapilot] Discipline gate: TRIGGERED
[ultrapilot] ULTRATHINK ACTIVATED
[ultrapilot] Loading discipline module + ULTRATHINK response format
```

**When the orchestrator's plan phase encounters `ULTRATHINK` mid-run (e.g., user types it during the build phase):**

```
[ultrapilot] ULTRATHINK ACTIVATED
[ultrapilot] Switching to deep-reasoning response format for remaining steps
[ultrapilot] Multi-lens analysis enabled
```

**When the user types `ULTRATHINK` again to deactivate:**

```
[ultrapilot] ULTRATHINK DEACTIVATED
[ultrapilot] Returning to default concise response format
```

**ULTRATHINK response format (when active):**

```markdown
1. **Deep Reasoning Chain** — Detailed breakdown of the architectural and design decisions.
   - Why this approach over alternatives
   - What trade-offs are being made
   - What assumptions are baked in
2. **Edge Case Analysis** — What could go wrong and how we prevented it.
   - Empty inputs, null, zero, very large values
   - Concurrent access, race conditions
   - Network failures, partial writes
   - Auth/permission boundaries
3. **The Work** — Optimized, production-ready, matching project conventions.
```

**Default (ULTRATHINK OFF) response format:**

```markdown
1. **One-line rationale** — Why the elements were placed there.
2. **The work** — Code, diff, command, whatever the task is.
```

**The activation is sticky for the rest of the run** unless the user explicitly deactivates it. This is intentional — switching modes mid-run fragments the model's reasoning. If the user wants concise again, they can type `ULTRATHINK OFF` or `EXIT ULTRATHINK` to deactivate.

**Toggle commands recognized by the orchestrator:**

| Phrase in user message | Effect |
|------------------------|--------|
| `ULTRATHINK` | Activate deep-reasoning mode |
| `ULTRATHINK ON` | Activate deep-reasoning mode (explicit) |
| `ULTRATHINK OFF` | Deactivate, return to concise mode |
| `EXIT ULTRATHINK` | Deactivate, return to concise mode |
| `RESUME NORMAL` | Deactivate, return to concise mode |

The orchestrator's preamble (printed to the transcript, not the user's terminal by default) logs the mode change for debugging.

## Tuning the gate

If discipline is being loaded too often (wasting quota), tighten the heuristics:
- Raise the file count threshold (e.g., 5 instead of 3)
- Require both file count AND line count to trigger
- Require explicit keyword match instead of prompt-length heuristic

If discipline is being loaded too rarely (the model is shallow on heavy tasks), loosen it:
- Add more keyword triggers
- Lower the file count threshold (e.g., 2 instead of 3)
- Default to loading when the classifier is uncertain (already the case)

## Source & Attribution

- **Original prompt:** AICodeKing's "King Mode" — [aicodeking/yt-tutorial/gemini-king-mode.md](https://github.com/aicodeking/yt-tutorial/blob/main/gemini-king-mode.md)
- **First surfaced in:** [GLM-5 KING MODE video (Feb 2026)](https://www.youtube.com/watch?v=JRuwxLNXfcY)
- **Used in ultrapilot as:** Generalized for model-agnostic use, gated by complexity classifier, default-off

## Related

- `references/king-mode-prompt.md` — the unmodified original prompt, archived for reference
- `/ultrapilot` — main orchestrator
- `/ultrapilot:plan` — plan phase output also feeds the gate (plan length = scope signal)
