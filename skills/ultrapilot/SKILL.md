---
name: ultrapilot
description: "Single-command engineering orchestrator. After loading, run `ultrapilot-goals set '<task>'` then loop `ultrapilot-run next` / do the work / `ultrapilot-run report --phase <name> --result <path> --passed`. Wrappers are in `<install>/bin/` — add to $PATH or call by absolute path. Runs explore → plan → build → verify → review → patch → audit with multi-dimensional goal scoring. Token-optimized via lazy phase loading. Model-agnostic. Use when the user asks for a non-trivial build, refactor, migration, or feature with verifiable completion criteria."
license: MIT
allowed-tools: "Bash Read Write Edit Grep Glob"
metadata:
  author: joychetry
  version: "1.0.0"
  category: software-development
  public: true
  tags:
    - orchestrator
    - workflow
    - coding-agent
    - tdd
    - planning
    - verification
    - model-agnostic
    - state-machine
    - token-efficient
compatibility: "Requires Python 3.8+. Designed for Pi (pi.dev), Claude Code, Codex, Droid (Factory), Gemini CLI, Cursor, Aider, Continue, OpenCode, and any LLM tool that reads the Agent Skills spec and can run subprocess commands. Agent must bring its own web search, documentation fetcher (e.g. Context7), and browser/Playwright for UI verification."
---

# /ultrapilot — The Discipline-Driven Engineering Orchestrator

**One command. Full lifecycle. Every model. Token-optimized.**

`/ultrapilot [task]` runs a complete software engineering workflow with a single command. The orchestrator dispatches one phase at a time, lazy-loading only the prompt the model needs for the current phase (200-500 tokens, not 2000+). The model calls `ultrapilot_run.py next` to get the next phase prompt, does the work, and calls `ultrapilot_run.py report` to advance.

## Why this exists

Three failure modes in current AI coding workflows:

1. **Token waste.** Most skills load their full spec (2000+ lines) on every run, even when only 200 lines are relevant to the current phase.
2. **Unenforced control flow.** "Dispatch verify after build" is a *suggestion* in markdown, not an actual state machine. The model can skip phases.
3. **Two UX surfaces.** Some skills have a single command but a separate "invoke individual phases" surface. Users have to know both.

`/ultrapilot` fixes all three:

- **One command** that does the whole thing, with a state machine enforcing the order
- **Lazy-loaded prompts** (200-500 tokens per phase, not 2000+)
- **Token-aware sizing** — tight budgets get minimal prompts, full budgets get the full prompt
- **Companion commands still work** as "go to phase X" shortcuts, not separate surfaces

## When to use

Use `/ultrapilot` when the task is non-trivial: building a feature, refactoring, migrating, or any multi-file work. The orchestrator's state machine ensures explore → plan → build → verify → review → patch → audit all happen in order.

For trivial tasks (rename a button, fix a typo, ask a question), just ask the model directly. The orchestrator is overhead for those.

## How to invoke

```
/ultrapilot build a sponsorship dashboard inside this app
/ultrapilot migrate the auth module from JWT to session cookies
/ultrapilot fix the mobile pipeline layout
```

The orchestrator will:
1. Set a goal (or use the active one)
2. Dispatch the first phase prompt
3. Wait for the agent to do the work
4. Advance to the next phase on `report`
5. Loop until the goal is done or the budget is exhausted

## Single-command loop (what the agent does)

The agent's loop is simple:

```
# Set the goal (if not already set)
ultrapilot-goals set --profile secure --tokens 250K "[task]"

# Get the current phase prompt
ultrapilot-run next

# ... do the work the prompt describes ...

# Report back
ultrapilot-run report --phase <name> --result /tmp/<name>-result.md --passed

# Repeat until done
```

> The `ultrapilot-run` / `ultrapilot-goals` commands are thin shell wrappers from the
> `bin/` directory; they auto-resolve the install path via `ULTRAPILOT_HOME` or the
> conventional per-agent skills directory. Add `bin/` to your `$PATH`, or call the
> wrappers with their absolute path.

That's the entire loop. The script handles state, prompt sizing, and phase advancement.

## Companion commands (optional shortcuts)

These still work but are now just "go to phase X" wrappers around the runner:

| Command | What it does |
|---------|--------------|
| `/ultrapilot:explore` | `ultrapilot_run.py goto explore && ultrapilot_run.py next` |
| `/ultrapilot:plan` | `ultrapilot_run.py goto plan && ultrapilot_run.py next` |
| `/ultrapilot:build` | `ultrapilot_run.py goto build && ultrapilot_run.py next` |
| `/ultrapilot:verify` | `ultrapilot_run.py goto verify && ultrapilot_run.py next` |
| `/ultrapilot:review` | `ultrapilot_run.py goto review && ultrapilot_run.py next` |
| `/ultrapilot:steer` | Show the steer doc + tighten the current phase |

The user types one of these to skip the auto-advance and jump to a specific phase. The default `/ultrapilot` invocation just runs the loop.

## Tools the agent must bring (required, not provided)

ultrapilot is portable. The agent's runtime provides the tools. The minimal stack the agent needs:

| Tool | Used in | Why |
|------|---------|-----|
| **Web search / web reader** | Explore phase (read project structure) | Discover current API changes, package versions, recent docs |
| **Documentation fetcher** (e.g. Context 7) | Plan/Build phases | Get current framework docs (Next.js, Supabase, Tailwind, Prisma, etc.) without trusting the model's memory |
| **Browser / dev tools / Playwright** | Verify phase (UI work) | Open the app, check console errors, click through flows, test mobile |
| **Git worktree** (optional) | All phases | Isolated branches for parallel runs |
| **Vision model** (optional) | Build phase (UI references) | Convert screenshots to text descriptions if the active model can't process images — see `references/adapter-prompts.md` for per-model vision support |

ultrapilot references these in the verify prompt ("Open dev tools, check console") but does not ship them. The agent's runtime must provide them. If your runtime lacks any of these, ultrapilot still works — those steps become advisory.

## Token efficiency (the design)

The runner emits one phase prompt per turn, sized to the remaining budget:

| Budget remaining | Verbosity | Typical prompt size |
|------------------|-----------|---------------------|
| > 100K tokens | compact | 200-500 tokens |
| 20K - 100K | compact | 200-500 tokens |
| < 20K | minimal | 50-150 tokens (one-line directive) |

Each phase prompt references the **prior phase's result file path** rather than re-loading its full content. The agent reads the file when it needs the prior result; the prompt stays small.

Compare:
- **Old design:** agent reads 2000+ lines of full specs upfront, every run
- **New design:** agent reads 200-500 tokens per phase, lazy-loaded, only the current phase

For a 7-phase run, the total prompt cost drops from ~14,000 tokens to ~2,500 tokens — an 82% reduction.

## Why This Exists

Most AI coding sessions fail for the same reason: the model skips the boring engineering steps and then acts confident. It plans nothing, builds everything in one go, never reads its own diff, and reports "done" when the app is broken. The fix is not a smarter prompt. The fix is a **structured loop with explicit gates between phases**.

`/ultrapilot` is that loop. It treats the model as an engineer who must prove every step, not a vending machine that dispenses code on demand.

## When to Use

Use `/ultrapilot` when:
- Building a new feature in an existing codebase
- Refactoring or restructuring code
- Fixing a bug that requires touching more than one or two files
- Implementing a design doc, spec, or migration
- Any task that has a verifiable end state

Don't use `/ultrapilot` for:
- Renaming a single variable (just ask)
- One-line typo fixes (just ask)
- Pure questions or research (no implementation needed)

## Companion Commands

`/ultrapilot` is the orchestrator. Under the hood it dispatches these seven phase commands plus one internal module:

| Command | Purpose | Phase |
|---------|---------|-------|
| `/ultrapilot:goals` | Multi-dimensional success criteria. Sets weights, floors, completion gates. | 0 — Goals |
| `/ultrapilot:explore` | Read-only architecture mapping | 1 — Explore |
| `/ultrapilot:plan` | Produce a tight, scoped plan. Brainstorms if unclear. | 2 — Plan |
| `/ultrapilot:build` | Execute the plan in small, verifiable steps. | 3 — Build |
| `/ultrapilot:verify` | Run tests, lint, type checks, browser checks. | 4 — Verify |
| `/ultrapilot:review` | Multi-perspective diff audit with validation gating. | 5 — Review |
| `/ultrapilot:steer` | Tighten a vague plan mid-flight. | Any — Steering |
| `/ultrapilot:_discipline` | Internal discipline module. Gated thinking layer for heavy tasks. Loaded only when the task-complexity classifier triggers. Default OFF. | (Internal) |

You do not need to call these directly. The orchestrator dispatches them. But they exist as standalone slash commands when you want to invoke a single phase. See `commands/` for each phase's full spec.

---

## The Goal System (Phase 0 — runs first)

The orchestrator starts every run with a goal-design phase. v1 of ultrapilot had a single binary goal: "is the task done?" That is not how real software engineering success works. Real success has six dimensions, and they can be in tension.

| # | Dimension | Default weight |
|---|-----------|----------------|
| 1 | Correctness — does the code do what the user asked? | 30% |
| 2 | Reliability — does it work consistently across edge cases? | 20% |
| 3 | Efficiency — does it run fast and use few resources? | 10% |
| 4 | Safety — does it respect auth, permissions, data integrity? | 25% |
| 5 | User experience — is the interface usable and accessible? | 10% |
| 6 | Cost — did the run consume more tokens/time than necessary? | 5% |

**Goal profiles (override the defaults):**

| Profile | When to use |
|---------|-------------|
| `default` | General purpose |
| `perf` | Performance-critical (rendering, queries, data pipelines) |
| `secure` | Auth, payments, PII, secrets (safety weight jumps to 45%) |
| `ship-it` | Production hotfixes, time-critical (good-enough beats perfect) |
| `prototype` | Design exploration, UX-heavy, throwaway code |
| `infra` | DevOps, CI/CD, infrastructure (reliability and cost matter) |

**Usage:**

```
/ultrapilot --profile secure build the payment flow
/ultrapilot --profile ship-it hotfix the production bug
/ultrapilot --profile perf optimize the dashboard queries
/ultrapilot --weights correctness=40,safety=40,ux=20 [task]
```

**Completion conditions:** the task is done when:
- Aggregate score ≥ 80% (weighted across all six dimensions)
- No dimension below 50%
- No dimension below its floor (safety ≥ 60%, correctness ≥ 70%)
- All four default gates pass (acceptance criteria + verify + review + build)
- Trial pass rate ≥ 80% (if `--trials` was used)

**The state engine** (`scripts/ultrapilot_goals.py`) is agent-agnostic. It runs without hooks, watchers, or agent-specific runtime. Any LLM coding tool (Claude Code, Codex, Gemini CLI, Cursor, Aider, etc.) calls it as a subprocess. The single entry point for agents is `ultrapilot_goals.py suggest`, which returns a JSON response describing the next action. See `commands/goals.md` for the full spec, three grader types, two-level evaluation, conflict-resolution hierarchy, and the agent-agnostic design.

---

## The Discipline Layer (gated, default OFF)

The orchestrator includes a discipline layer for heavy tasks. The layer is **not** always loaded. It is gated by a task-complexity classifier so the model does not waste quota on small tasks.

**Activation triggers (any one is enough):**

- Estimated file count > 3
- Estimated line count > 100
- New abstractions, cross-cutting changes (auth, payments, security, migrations)
- Multi-service / multi-layer changes
- Architectural decisions (no existing pattern to follow)
- User prompt length > 200 words
- Keywords in prompt: "refactor", "migrate", "redesign", "architect", "system", "overhaul", "from scratch", "production", "scale"
- Explicit user trigger: `ULTRATHINK` in the prompt, or `/ultrapilot --deep`

**Override (force OFF):**

- User passes `--quick` or `--trivial` flag
- The plan phase produces ≤ 2 steps

**What the discipline layer adds when loaded:**

- Zero-fluff default response style
- Multi-dimensional analysis (correctness, perf, security, accessibility, maintainability, consistency, reversibility)
- Explicit prohibition on surface-level logic — dig deeper if the answer feels easy
- Project-discipline enforcement (use existing libraries, match conventions, no silent deviation)
- Honored `ULTRATHINK` trigger throughout the run

**ULTRATHINK is announced explicitly when active:**

```
[ultrapilot] Discipline gate: TRIGGERED
[ultrapilot] ULTRATHINK ACTIVATED
[ultrapilot] Loading discipline module + ULTRATHINK response format
```

Mid-run toggle (`ULTRATHINK OFF`, `EXIT ULTRATHINK`, `RESUME NORMAL`) deactivates the deep-reasoning format and returns to concise. The announcement is sticky for the rest of the run unless explicitly deactivated. See `commands/_discipline.md` for the full activation protocol.

**Why gated, not always-on:** loading the discipline layer for every task wastes quota. Renames, typos, and small fixes do not need it. The gate concentrates reasoning on tasks that need it.

See `commands/_discipline.md` for the full module.

---

## How to Invoke

```
/ultrapilot build a sponsorship dashboard inside this app — track brand deals, deliverables, deadlines, invoice status, contacts
```

```
/ultrapilot migrate the auth module from JWT to session cookies — all call sites must compile and existing tests must pass
```

```
/ultrapilot fix the mobile pipeline layout — columns overflow horizontally on viewports under 768px
```

**Flags:**

```
/ultrapilot --deep [task]    # Force discipline layer ON (override gate)
/ultrapilot --quick [task]   # Force discipline layer OFF (skip gate)
/ultrapilot --trivial [task] # Alias for --quick
```

`ULTRATHINK` anywhere in the prompt also forces the discipline layer ON, regardless of other signals.

The orchestrator:
1. Runs the **goals phase** (sets weights, floors, completion gates — see `commands/goals.md`)
2. Runs the **discipline activation gate** (loads the discipline layer if the task is heavy)
3. Detects whether the goal is clear or needs brainstorming
4. Runs explore-first if working in an existing codebase
5. Plans before editing
6. Steers on vague plans
7. Builds in small steps
8. Verifies after each step
9. Reviews the full diff at the end
10. Patches what the reviewer catches
11. Scores the result against the goals (six dimensions)
12. Loops until the completion condition is met

---

## The Six Phases

### Phase 1: Explore (read-only)

Before any edit, map the codebase. This is non-negotiable for existing projects.

**Output:** an architecture map that includes:
- Framework and language
- Package manager and lockfile
- Test command and where tests live
- Styling system (Tailwind, CSS modules, etc.)
- Routing setup
- Database and auth layer
- Existing patterns for state, data fetching, error handling
- The safest way to add a new feature given what's already there

**Why:** the model needs a mental model of the repo before touching anything. A read-only exploration is cheap and prevents costly mistakes.

**Shortcut for greenfield projects:** if the directory is empty or you are starting fresh, skip explore and go straight to plan. The architecture map is the plan.

See `commands/explore.md` for full details.

### Phase 2: Plan (write a tight spec)

The plan is the contract. It must be:

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

**If the goal is unclear or the user has not specified a target,** the plan phase becomes a brainstorm. Ask the user the questions needed to make the goal concrete. Do not proceed to build with a vague goal.

See `commands/plan.md` for full details and the plan output format.

### Phase 3: Build (small steps with checkpoints)

The build phase must follow these rules:

- **One step at a time.** Complete a step, then check it.
- **Match the existing codebase.** Use its conventions, types, patterns. Do not invent a new architecture inside an existing one.
- **No scope creep.** If a step is not in the plan, do not add it.
- **Use negative constraints for UI work** (see Appendix B).
- **Run available checks after each meaningful step:** tests, type checks, lint, build.

The build phase is the longest. It can produce intermediate checkpoints, but it does not declare completion. That is the review phase's job.

See `commands/build.md` for full details.

### Phase 4: Verify (prove the work)

Verification is the part most agents skip. It is the part that matters most.

For backend / logic work:
- Run the test suite. Did the new tests pass? Did the existing tests still pass?
- Run type checks (TypeScript, mypy, etc.). Zero errors.
- Run lint. Zero errors.
- If the change touches data persistence, run a migration dry-run.

For UI / frontend work:
- Run the app and preview it.
- Click through the main user flow that was changed.
- Open dev tools, check the console for errors.
- Resize to mobile, check the layout.
- Test edge cases: empty state, loading state, error state.

For API / integration work:
- Hit the endpoint with the documented request shape.
- Check the response shape and status code.
- Check auth and permission boundaries.
- Check error responses.

If verification fails, do not declare success. The build phase is not done.

See `commands/verify.md` for the bug report format and per-work-type checklists.

### Phase 5: Review (multi-perspective audit with validation)

After verification passes, run a rigorous multi-agent review on the full diff.

The review runs five steps:

1. **Pre-flight check** — is review even possible? (diff present, not closed/draft, not already reviewed)
2. **Discover project conventions** — read AGENTS.md / CLAUDE.md / equivalents in the affected directories
3. **Multi-perspective parallel review** — four reviewers in parallel:
   - Convention compliance (×2 independent passes)
   - Bug detection, diff-only
   - Bug detection, context-aware
4. **Independent validation** — every candidate issue is re-validated by a separate agent. False positives get filtered.
5. **High-signal filter** — only confirmed issues that meet the bar (compile errors, definite bugs, clear convention violations, security issues) make it to the report.

This is **not** a single prompt asking the model to "review your own diff." That approach produces high false-positive rates because the model is over-invested in the code it just wrote. The multi-agent + validation design reduces that by having independent perspectives and a separate confirmation step.

See `commands/review.md` for the full five-step spec, the high-signal filter, and the output format.

### Phase 6: Patch (loop back if needed)

The patch phase fixes what the reviewer found. Then the loop restarts from Phase 4 (verify again) until the reviewer finds nothing actionable or the orchestrator's completion condition is met.

---

## Completion Conditions

The orchestrator considers a task done when **all** of the following hold:

1. The plan's acceptance criteria are met.
2. The verification suite passes (tests, lint, type checks, manual flow checks).
3. The review pass found no issues that are clearly connected to the task.
4. The app builds and runs.

If the user specified a goal with `/goal`-style phrasing (e.g., "until X passes"), the orchestrator keeps looping until that specific condition holds. Otherwise, it stops at the first clean pass.

To bound a long-running ultrapilot, include a turn or time clause in the task:

```
/ultrapilot refactor the auth module — stop after 15 turns or when all tests pass
```

---

## Steering (not Micromanaging)

The orchestrator watches the model's plan and intervenes only when the plan is vague. Steering is not controlling. It is making sure the model does not build the wrong thing.

**Vague plan → ask for specifics:**
- "Add dashboard components" → "Which components, where, and how will you test them?"
- "Add persistence" → "Local storage, SQLite, Supabase, or the existing database?"
- "Add validation" → "Client-side, server-side, or both? Which library?"

**Tight plan → let it build.** Do not dictate every line. Once the plan is solid, the model needs room to execute.

**Mid-flight correction:** if the model goes off-rails, stop it and re-plan. Do not let it dig deeper into a wrong direction. Reset to the last good checkpoint.

See `commands/steer.md` for the full steering playbook.

---

## Mistake Prevention (do not load everything at once)

The model is not a magic wand. Loading every discipline layer, every skill, every rule into one giant system prompt wastes context and produces rigid, weird output. The orchestrator handles this automatically, but if you are invoking sub-skills directly, follow these rules:

- **Discipline layer**: gated, default OFF. Loaded only when the task-complexity classifier triggers.
- **Planning and verification**: core. They run on every task.
- **Frontend design constraints**: only when building UI.
- **Security review**: only when touching auth, payments, permissions, or user data.
- **Performance review**: only when the task has a performance budget.

Do not make the agent carry a whole engineering department in one prompt. The right skill at the right time, in the right order.

---

## Appendix A: Explore Prompt Template

When invoking explore, use this exact structure:

```
Use explore only.
Read the project structure. Identify the framework, package manager, test commands, styling system, routing setup, and any database or auth layer. Do not edit files.
Give me a short architecture map and tell me the safest way to add a new feature.
```

If the model is operating on a fresh project, replace "the safest way to add a new feature" with "the recommended structure for a new [type] project."

## Appendix B: Negative Design Constraints (UI work)

When building UI, do not just say "make it modern." Say what you do **not** want:

- Avoid excessive cards
- Avoid purple gradients
- Avoid glassmorphism
- Avoid decorative blobs
- Avoid oversized hero sections
- Avoid generic AI imagery
- Keep information dense but readable

Then say what you **do** want:

- Use the existing design system
- Clear hierarchy
- Strong spacing rhythm
- Accessible contrast
- Responsive behavior
- Realistic empty states, loading states, and error states

The model responds better to negative constraints than to positive abstractions. "Modern" means nothing. "Not glassmorphism" means something.

## Appendix C: Bug Report Format

When a verification step finds a bug, the orchestrator formats the report to the model like this:

> **Failure:** [exact observed behavior]
> **Expected:** [exact expected behavior]
> **Smallest possible cause:** [model's hypothesis, tested before patch]
> **Reproduction:** [steps to trigger it]

Specific bug reports produce specific fixes. "Fix the app" produces wasted tokens.

## Appendix D: Review Prompt

```
Review your own diff against the original goal. Look for:
- Missing states (empty, loading, error, success)
- Broken flows
- Type errors or untyped escapes
- Unhandled edge cases
- Duplicated logic
- Styling inconsistencies
- Unrelated changes

Then fix only the issues that are clearly connected to this task.
```

---

## Operating Principles

1. **The model is not magic. The loop is the magic.** The value is in the structure, not the prompt.
2. **Read before write.** Explore is non-negotiable for existing codebases.
3. **Plan before edit.** A vague plan produces vague code.
4. **Verify before claim.** Run the actual checks. Do not infer.
5. **Review before ship.** The diff is the product. It must match the goal.
6. **Loop until clean.** Stopping at "looks right" is not completion.
7. **Steer, don't dictate.** Tighten plans, do not control code.
8. **Right skill, right time.** Do not load everything at once.
9. **Right discipline, right time.** Load the discipline layer only when the task is heavy. Trivial tasks get concise behavior by default.
10. **Multi-dimensional goals over binary done/not-done.** Real success has six dimensions (correctness, reliability, efficiency, safety, UX, cost) and they can be in tension. Score them all, weight them appropriately, only then decide if the task is done.

---

## Installation

ultrapilot follows the [Agent Skills](https://agentskills.io) open standard,
which means it works on **Pi, Claude Code, Codex, Droid, Cursor, Aider, OpenCode,
Gemini CLI, and any LLM tool that implements the spec.** Install location
differs per agent — pick the one that matches yours.

### Quick install (per agent)

```bash
# Pi (pi.dev) — global
git clone https://github.com/joychetry/ultrapilot.git ~/.pi/agent/skills/ultrapilot
# Pi also accepts the universal ~/.agents/skills/ location:
#   git clone https://github.com/joychetry/ultrapilot.git ~/.agents/skills/ultrapilot

# Claude Code — global
git clone https://github.com/joychetry/ultrapilot.git ~/.claude/skills/ultrapilot

# Droid (Factory) — global
git clone https://github.com/joychetry/ultrapilot.git ~/.factory/skills/ultrapilot

# Codex — global
git clone https://github.com/joychetry/ultrapilot.git ~/.codex/skills/ultrapilot
```

Then add the `bin/` wrappers to your shell `$PATH` (or call them by absolute
path):

```bash
# Pick the one that matches your install above:
export PATH="$HOME/.pi/agent/skills/ultrapilot/bin:$PATH"       # Pi
export PATH="$HOME/.agents/skills/ultrapilot/bin:$PATH"         # Pi (universal)
export PATH="$HOME/.claude/skills/ultrapilot/bin:$PATH"         # Claude Code
export PATH="$HOME/.factory/skills/ultrapilot/bin:$PATH"        # Droid
export PATH="$HOME/.codex/skills/ultrapilot/bin:$PATH"         # Codex
```

The wrappers auto-resolve the install location via `ULTRAPILOT_HOME` first,
then the conventional per-agent directory, then a few common fallbacks. Set
`ULTRAPILOT_HOME` to override.

### Project-local install (per-agent)

If you want ultrapilot available only inside a specific project (and not
globally), install to the project-local skill location:

```bash
# Pi / Claude Code / Codex — project-local
cd /path/to/your/project
git clone https://github.com/joychetry/ultrapilot.git .pi/skills/ultrapilot
# or:                    git clone ... .agents/skills/ultrapilot
# or:                    git clone ... .claude/skills/ultrapilot
```

> Pi and Codex project skills are only loaded after the project is trusted.
> Claude Code loads them automatically.

### Marketplace install (where available)

Some agents ship a marketplace plugin system. The current marketplaces are:

```bash
# Claude Code
claude plugin install ultrapilot@ultrapilot-marketplace

# Droid (Factory)
droid plugin install ultrapilot@ultrapilot

# Codex
codex plugin install ultrapilot-marketplace
```

> Pi and most other spec-compliant agents don't have a marketplace concept —
> they load skills directly from the filesystem, so the manual install above
> is the canonical path. (`pi` does have a [Pi Packages](https://pi.dev/packages)
> system for npm-distributed skills; ultrapilot ships as a git repo, not an
> npm package, to keep zero runtime dependencies.)

### One-line tarball install

```bash
# Default: Claude Code install location. Substitute for Pi / Droid / Codex as needed.
curl -sL https://github.com/joychetry/ultrapilot/releases/latest/download/ultrapilot.tar.gz \
  | tar -xz -C ~/.claude/skills/ && mv ~/.claude/skills/ultrapilot ~/.claude/skills/ultrapilot
```

For Pi:

```bash
curl -sL https://github.com/joychetry/ultrapilot/releases/latest/download/ultrapilot.tar.gz \
  | tar -xz -C ~/.pi/agent/skills/ && mv ~/.pi/agent/skills/ultrapilot ~/.pi/agent/skills/ultrapilot
```

### Other agents

ultrapilot is a pure-standards SKILL.md plugin — any LLM tool that reads the
[agentskills.io](https://agentskills.io) spec can load it without modification.
That includes **Pi** (the `~/.pi/agent/skills/` and `~/.agents/skills/` locations
are scanned automatically), **Claude Code**, **Codex**, **Cursor**, **Aider**,
**Continue**, **OpenCode**, **Gemini CLI**, and any other spec-compliant
harness. The `bin/` wrappers are the only filesystem-level assumption, and
they're optional (you can call `scripts/ultrapilot_run.py` directly).

<!-- HERMES_FOOTNOTE_BEGIN: The blockquote below is the ONLY allowed place
     a ~/.hermes/ path may appear in user-facing docs. It documents the
     install path for Hermes users and is consumed by the no-hermes-paths
     CI check, which skips any '>'-prefixed line between this marker and
     the matching HERMES_FOOTNOTE_END below. Do not remove these markers
     without also updating .github/workflows/ci.yml. -->
> **Note for Hermes users:** ultrapilot also works inside Hermes via the agent's
> native skills loader. Install location: `~/.hermes/skills/ultrapilot`. The
> `bin/` wrappers handle this path automatically.
<!-- HERMES_FOOTNOTE_END -->

## Compatibility
`/ultrapilot` is model-agnostic. It dispatches structured prompts to whatever model is active. Verified against a representative capability mix; per-class adaptations are in `references/adapter-prompts.md`.

The only thing that changes between models is the raw capability ceiling. The discipline stays the same.

## Source & Inspiration

Built from the synthesis of:

- The **structured-loop-with-gates** pattern: spec → plan → build → verify → review → patch. This shape is widely used (Anthropic's internal workflows, Addy Osmani's agent skills repo, obra's Superpowers framework). ultrapilot's specific implementation is independent.
- **Capability-class adapters** (in `references/adapter-prompts.md`) for behavior patterns observed across many chat and code models — not model-specific tuning.
- **Anthropic's claude-code `code-review` plugin** — multi-perspective review with confidence scoring and validation gating. The 4-reviewer design in `commands/review.md` derives from this.
- **`jthack/claude-goal`** — persistent goal state via SQLite, completion audit, anti-prompt-injection wrapper. Adapted to be agent-agnostic in `scripts/ultrapilot_goals.py`.
- **Claude Code `/goal`** (closed-source, docs only) — the completion-condition pattern.
- **Braintrust + Brenndoerfer** — multi-dimensional agent evaluation and success-criteria taxonomy. The 6-dimension goal system derives from this.

## License

MIT — use it, fork it, ship it.
