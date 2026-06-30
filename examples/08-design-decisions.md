---
name: design-decisions
description: "Self-audit documenting ultrapilot's deliberate design decisions and trade-offs. Each decision has a reason, an alternative that was rejected, and the boundary condition under which the decision would be revisited."
type: verification
---

# Design Decisions — ultrapilot self-audit

This is an internal self-audit. Every choice in ultrapilot is a trade-off; this document records the trade-offs explicitly so reviewers and future maintainers can see what was considered, what was rejected, and what would change the decision.

The audit is structured as: **Decision → Reason → Rejected alternative → Revisit when**.

---

## 1. The structured loop: explore → plan → build → verify → review → patch → audit

**Decision:** The orchestrator enforces a fixed sequence of phases with explicit gates between them. The agent cannot skip phases without an explicit `goto`.

**Reason:** free-form "just do the task" prompts drift. Even capable models lose focus, hallucinate acceptance criteria, and stop at "looks right" instead of verified completion. A forced sequence with gates concentrates reasoning at the points that need it (planning, verification, review) and forces verification before declaring done.

**Rejected alternative:** an unstructured loop where the model decides what to do next on its own turn-by-turn. Faster for trivial tasks, but the failure mode is silent completion-pretending.

**Revisit when:** a future model demonstrates verifiable, drift-free behavior without structured gates across at least 100 representative tasks. Until then, the gates are the cheap insurance.

---

## 2. Multi-dimensional goal scoring (six dimensions, not binary done/not-done)

**Decision:** tasks are scored on correctness, reliability, efficiency, safety, UX, and cost — each with its own weight, floor, and completion gate.

**Reason:** binary done/not-done hides failure modes. A task can be functionally correct but unsafe, or efficient but unusable. Six dimensions force the model and the user to consider trade-offs explicitly, and the floor mechanism (a dimension below its floor = task fails) catches the silent regressions that binary scoring misses.

**Rejected alternative:** a single quality score, or a pass/fail on tests alone. Tests alone miss UX and cost regressions; a single quality score hides which dimension is failing.

**Revisit when:** a project can prove it doesn't have trade-offs that the six dimensions surface. In practice, every non-trivial project has them.

---

## 3. Gated discipline layer (default OFF)

**Decision:** the discipline module (multi-lens analysis, project-discipline, anti-fluff response format) is loaded only when a task-complexity classifier triggers. Trivial tasks get concise default behavior.

**Reason:** loading the discipline layer for every task wastes quota. Renames, typos, and small fixes do not need multi-lens analysis. The gate concentrates reasoning on the tasks that need it.

**Rejected alternative:** always-on discipline. Easier to implement (one flag), but uniform cost for variable value.

**Revisit when:** the activation gate's classifier is wrong more than ~10% of the time. If it is, the cost of false negatives (discipline not loaded when needed) starts to dominate and always-on becomes the cheaper option. Track via session-level feedback.

---

## 4. Lazy-loaded phase prompts

**Decision:** phase prompts are loaded on demand by the runner, not bundled into one giant system prompt. A typical run loads 1-3 phase prompts sized to the remaining token budget, not all 7.

**Reason:** per-conversation prompt caching is sacred (cache hit = 10x cheaper tokens, cache miss = full prefix re-billed). Bundling everything breaks the cache every turn. Lazy loading keeps the system prompt stable for the life of a conversation.

**Rejected alternative:** one big prompt with everything. Simpler reasoning, but every turn re-bills the full prefix.

**Revisit when:** prompt caching becomes irrelevant (e.g., cache costs drop to zero) or per-phase prompts cause correctness regressions that the bundled prompt avoids.

---

## 5. State machine (not free-form prompt dispatch)

**Decision:** the runner is a state machine. Each phase has explicit entry/exit conditions, and the agent cannot move on without satisfying them. The state is persisted across sessions in SQLite.

**Reason:** markdown-suggested phase ordering is ignored under pressure ("just finish the task"). A state machine with explicit gates is harder to ignore — the runner refuses to dispatch the next phase until the current one is satisfied.

**Rejected alternative:** prompts that say "do these in order" and trust the model. Cheap to implement, unreliable under load.

**Revisit when:** a model consistently satisfies phase gates voluntarily. Not seen in current production models.

---

## 6. Agent-agnostic runtime

**Decision:** the runtime (state machine, goal scoring, prompts) is plain Python 3.8+ with SQLite. No hooks, no agent-specific environment variables, no dependency on a particular LLM tool.

**Reason:** the skill should work wherever the user works — Claude Code, Codex CLI, Gemini CLI, Cursor, Aider, Continue, OpenCode, Droid, or any future agent. Hardcoding to one tool fragments the user base and creates maintenance debt when that tool's API changes.

**Rejected alternative:** an opinionated Claude Code plugin with hooks and shortcuts. Faster to build, narrower audience.

**Revisit when:** the agent landscape consolidates to one tool. Until then, portability is the right default.

---

## 7. Capability-class adapters, not model names

**Decision:** per-model adjustments are documented in `references/adapter-prompts.md` grouped by **capability class** (text-only, over-explainer, long-horizon drift, self-verification overconfidence, hallucinated paths, etc.), not by model name.

**Reason:** the skill should be model-agnostic. A doc that says "if you are using model X, do Y" couples the skill to a model and dates immediately. A doc that says "if the model exhibits the over-explainer class, do Y" stays useful as the model landscape changes.

**Rejected alternative:** a per-model matrix with one adapter per model. Higher maintenance, narrower applicability.

**Revisit when:** capability classes collapse — every model falls into the same class. Not seen in current model diversity.

---

## 8. Multi-perspective review with validation gating

**Decision:** the review phase runs 4 parallel reviewer perspectives, and each issue is re-validated by a separate validator before being surfaced. A confidence score is required on every issue.

**Reason:** single-reviewer reviews miss class-of-bug issues that a second perspective would catch. Validation gating prevents "the reviewer said there's a bug" from being treated as ground truth — the validator checks the bug exists.

**Rejected alternative:** a single reviewer prompt. Cheaper, less reliable.

**Revisit when:** single-reviewer reliability is proven equivalent to multi-reviewer. Not seen in current model behavior.

---

## 9. Anti-prompt-injection wrapper around goal text

**Decision:** goal text is wrapped in a marker that makes injection attempts visible to the orchestrator, and goal state is checked against a signed hash before use.

**Reason:** the goal text is the closest thing to a system prompt that the orchestrator has. Untrusted goal text is a prompt-injection vector — a malicious user could embed instructions in their goal that the orchestrator would then execute as system-level directives.

**Rejected alternative:** treat goal text as trusted. Simpler, exploitable.

**Revisit when:** the goal text source is fully trusted (e.g., read from a signed config file). Until then, the wrapper is cheap insurance.

---

## 10. Token-aware verbosity

**Decision:** the runner adjusts phase-prompt verbosity based on the remaining token budget. Above 100K tokens remaining, prompts are compact (200-500 tokens). Below 30K, prompts are even tighter.

**Reason:** the user shouldn't have to manage token budgets. The runner should fit prompts to the conversation's remaining room, not assume a fixed budget.

**Rejected alternative:** fixed-size prompts. Simpler, but wastes budget when the model can take more and overflows when it can't.

**Revisit when:** all models converge on a single fixed context window. Until then, the runner's adaptation is more useful.

---

## What this document is NOT

This is not a defense of ultrapilot against critics. If a section reads as defensive, it is. The point is to record the trade-offs that were considered, not to claim they are the only correct trade-offs.

If you are reading this and disagree with a decision, the right response is to propose an alternative with evidence (transcript, benchmark, failure mode). Disagreement without evidence is just preference.
