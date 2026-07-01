# Changelog

All notable changes to `/ultrapilot` are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed
- **Public-readiness hardening.** ultrapilot is now genuinely agent-agnostic from the user's perspective. The previous release shipped a hardcoded per-agent invocation pattern (the form `python3 <agent-home>/skills/ultrapilot/scripts/...`) that worked on the author's internal Hermes install but silently broke on Claude Code, Droid, and Codex. This release replaces every hardcoded per-agent path with the new `bin/ultrapilot-run` / `bin/ultrapilot-goals` shell wrappers, which auto-resolve the install location via `ULTRAPILOT_HOME` or any of the conventional per-agent skills directories.

### Added
- `bin/ultrapilot-run` and `bin/ultrapilot-goals`: thin shell wrappers that resolve the install path across all supported agents (Claude Code, Droid, Codex, Hermes, custom `ULTRAPILOT_HOME`).
- `no-hermes-paths` CI job: scans for hardcoded `~/.hermes/` paths in user-facing files and fails the build on regression. A synthetic-violation test confirms the check is real, not vacuous.
- Functional CI step that copies ultrapilot to each of `~/.claude/`, `~/.factory/`, `~/.codex/` and verifies the wrappers resolve correctly in a clean env with no Hermes symlink — proves a Claude Code / Droid / Codex user (without Hermes installed) can install and run ultrapilot out of the box.
- `HERMES_FOOTNOTE_BEGIN` / `HERMES_FOOTNOTE_END` HTML-comment sentinels wrap the one remaining Hermes-specific install note in `SKILL.md` so the `no-hermes-paths` check can allow it without exempting the whole file.

### Reordered
- `SKILL.md` Installation section now leads with the three public marketplaces (Claude Code → Droid → Codex) before the Hermes footnote.

## [1.0.0] - 2026-06-30

First public release. This is the initial version published to all supported marketplaces (agentskills.io, Claude Code, Droid, Codex).

### What's in this release

`/ultrapilot` is a single-command engineering orchestrator that runs a full `explore → plan → build → verify → review → patch` lifecycle with multi-dimensional goal scoring. It is **model-agnostic** (works with any LLM coding tool — adapters for capability classes are in `references/adapter-prompts.md`) and **token-optimized** via lazy phase loading — a full 7-phase run costs ~2,000 tokens, down from ~22,000 if all specs were loaded up front.

The orchestrator's loop is:

1. Set a goal once: `ultrapilot_goals.py set "[task]"`
2. Loop: `ultrapilot_run.py next` → do the work → `ultrapilot_run.py report` → repeat
3. The runner enforces phase order; the agent cannot skip phases without an explicit `goto`

### Core components

- **State engine** (`scripts/ultrapilot_goals.py`): dependency-free Python, single SQLite file, no agent-specific runtime
- **State-machine runner** (`scripts/ultrapilot_run.py`): the actual control flow, with token-aware verbosity (compact / minimal)
- **Phase prompts** (`prompts/<phase>.md`): 200-500 tokens each, lazy-loaded on demand
- **Companion commands** (`commands/`): `/ultrapilot:explore`, `:plan`, `:build`, `:verify`, `:review`, `:steer`, `:goals`, `:_discipline` — each a `goto` shortcut to a phase
- **Worked examples** (`examples/01`–`08`): real task types (feature add, auth migration, bug fix, rigorous review, discipline gate, goal profiles, efficient loop, verification audit)

### Goal system (Phase 0)

Multi-dimensional success criteria with six dimensions and weights:

- Correctness (30%), Reliability (20%), Efficiency (10%), Safety (25%), UX (10%), Cost (5%)
- Six preset profiles: `default`, `perf`, `secure`, `ship-it`, `prototype`, `infra`
- Custom weights: `--weights correctness=40,safety=40`
- Per-dimension floors (safety ≥ 60%, correctness ≥ 70%) as non-negotiable minimums
- Trial-based stability: `--trials N` for non-deterministic tasks
- Three grader types: code-based, model-based, human
- Two-level evaluation: single-step (decision) + end-to-end (workflow)
- Conflict-resolution priority: safety > correctness > reliability > efficiency > UX > cost

### Discipline layer (gated, default OFF)

`/ultrapilot:_discipline` is the orchestrator's gated thinking layer. The orchestrator loads it only when the task-complexity classifier decides the task is heavy.

- **8 heuristic triggers** (file count, line count, abstractions, cross-cutting changes, etc.)
- **3 explicit triggers** (`ULTRATHINK` keyword, `--deep` flag, `--hard`/`--deep` aliases)
- **Override flags**: `--quick` and `--trivial` to force discipline OFF
- **ULTRATHINK mode** for deep-reasoning response format, toggleable mid-run (`ULTRATHINK OFF` to exit)

### Review system (v2)

Multi-perspective review with independent validation gating:

- Four parallel reviewers: convention compliance × 2, bug detection diff-only, bug detection context-aware
- Pre-flight check (short-circuits on closed/draft/auto/already-reviewed PRs)
- Project convention discovery (AGENTS.md / CLAUDE.md / equivalents) as a review input
- Validation pass for every candidate issue with confidence scoring
- High-signal filter with explicit "flag these / do not flag these" lists
- `--pr` and `--comment` flags for review command
- Inline comment posting with committable suggestion blocks (small fixes) vs description (large fixes)

### Token efficiency

| Design | Per-run prompt cost | Reduction |
|--------|---------------------|-----------|
| Naive (all specs loaded) | ~22,000 tokens | — |
| v1.0 compact (lazy phase loading) | ~2,000 tokens | 91% |
| v1.0 minimal (low-budget mode) | ~500 tokens | 98% |

### Agent support

`/ultrapilot` is **agent-agnostic** and works with any LLM coding tool that can call subprocesses and read files. The session-ID resolver detects:

- Claude Code
- Codex
- Gemini CLI
- Cursor
- Aider
- Continue
- OpenCode
- Droid (Factory)
- Hermes (out of band; not in primary marketplace list)

Detection is via environment variables only — no agent runtime APIs, no agent-specific hooks. The same `ultrapilot_goals.py` and `ultrapilot_run.py` work everywhere.

### Companion commands (stable, will not change without a major version bump)

- `/ultrapilot:explore` — read-only architecture mapping
- `/ultrapilot:plan` — scoped plan with acceptance criteria
- `/ultrapilot:build` — small-step execution with checkpoints
- `/ultrapilot:verify` — actual checks (tests, type, lint, browser)
- `/ultrapilot:review` — multi-perspective audit with validation
- `/ultrapilot:steer` — mid-flight intervention
- `/ultrapilot:goals` — multi-dimensional goal management
- `/ultrapilot:_discipline` — internal discipline module (gated, rarely invoked directly)

### Inspiration

ultrapilot synthesizes patterns that are widely used across the LLM-coding-agent space. The structured-loop-with-gates shape (spec → plan → build → verify → review → patch → audit) appears in many agent-skill repos. Specific influences:

- **Addy Osmani's [agent skills repo](https://github.com/addyosmani/agent-skills)** — the lifecycle shape (spec → plan → build → test → review → simplify → ship); specific skills from that repo are not bundled, only the lifecycle pattern is honored
- **Anthropic's [claude-code code-review plugin](https://github.com/anthropics/claude-code/blob/main/plugins/code-review/commands/code-review.md)** — multi-agent review with confidence scoring
- **[jthack/claude-goal](https://github.com/jthack/claude-goal)** — SQLite state, completion audit, anti-prompt-injection patterns
- **[Braintrust: Agent Evaluation](https://www.braintrust.dev/articles/agent-evaluation)** — multi-dimensional scoring, three grader types, two-level evaluation
- **[Brenndoerfer: Setting Goals and Success Criteria](https://mbrenndoerfer.com/writing/setting-goals-and-success-criteria-ai-agent-evaluation)** — success-criteria taxonomy
- **GStack** ([garrytan/gstack](https://github.com/garrytan/gstack)) — `/autoplan` scope modes, auto-decision principles
- **Anthropic Claude Code `/goal`** (closed-source, [docs only](https://code.claude.com/docs/en/goal)) — completion-condition pattern

The discipline layer's content (multi-lens analysis, anti-fluff response format, project-discipline) is a common pattern in prompt engineering; ultrapilot's contribution is the **gated activation** and the per-phase lazy loading, not the layer's text.

### Design audit

A self-audit of ultrapilot's deliberate design decisions and trade-offs lives in `examples/08-design-decisions.md`. It records what was chosen, what was rejected, and what would change the decision.

### Install

See [README.md](README.md) for marketplace install instructions (Claude Code, Droid, Codex, agentskills.io, or standalone).

### Notes

- First public release. API is the slash command surface plus the SKILL.md spec.
- Companion commands are stable. Breaking changes will bump major version.
- MIT license.
