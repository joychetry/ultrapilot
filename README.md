# ultrapilot

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-blueviolet)](https://agentskills.io)
[![Pi](https://img.shields.io/badge/Pi-pi.dev-purple)](https://pi.dev)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin-orange)](https://code.claude.com/docs/en/skills)
[![Droid](https://img.shields.io/badge/Droid-plugin-blue)](https://docs.factory.ai/cli/configuration/plugins)
[![Codex](https://img.shields.io/badge/Codex-plugin-green)](https://developers.openai.com/codex/skills)

**One command. Full lifecycle. Every model. Token-optimized.**

`/ultrapilot [task]` runs a complete software engineering workflow with a single slash command. State-machine-driven. Lazy-loaded phase prompts. Multi-dimensional goal scoring. Model-agnostic.

## What it does

| Phase | Purpose | Companion command |
|-------|---------|-------------------|
| **0. Goals** | Multi-dimensional success criteria. Sets weights, floors, completion gates. | `/ultrapilot:goals` |
| **1. Explore** | Read-only architecture mapping | `/ultrapilot:explore` |
| **2. Plan** | Tight, scoped plan with verifiable acceptance criteria | `/ultrapilot:plan` |
| **3. Build** | Execute the plan in small, verifiable steps | `/ultrapilot:build` |
| **4. Verify** | Run tests, type checks, lint, browser checks | `/ultrapilot:verify` |
| **5. Review** | Multi-perspective diff audit with validation gating | `/ultrapilot:review` |
| **6. Patch** | Fix what the reviewer caught, loop back to verify | (built-in) |
| **Steer** (mid-flight) | Tighten a vague plan without restarting | `/ultrapilot:steer` |
| **Goal scoring** | Six-dimension weighted score (correctness, reliability, efficiency, safety, UX, cost) | `/ultrapilot:goals` |

> `_discipline` is also shipped (`commands/_discipline.md`) but is **internal** — the orchestrator loads it automatically when tasks warrant it. Don't invoke it directly.

The user types one command. The agent handles everything else via `scripts/ultrapilot_run.py`.

## Why

Most AI coding sessions fail the same way: the model skips the boring engineering steps, builds everything in one shot, never reads its own diff, and reports "done" when the app is broken.

`/ultrapilot` fixes this by enforcing a **structured loop with explicit gates between phases**. It treats the model as an engineer who must prove every step — not a vending machine that dispenses code on demand.

The value isn't in a clever prompt. It's in the loop.

## Token efficiency

The orchestrator is **state-machine-driven**, not doc-driven. The agent calls `ultrapilot_run.py next` to get a phase prompt (200-500 tokens), does the work, calls `ultrapilot_run.py report` to advance.

| Design | Per-run prompt cost | Reduction |
|--------|---------------------|-----------|
| Full spec (old) | ~22,000 tokens | — |
| Lazy compact (new) | ~2,000 tokens | **91%** |
| Lazy minimal (new, tight budget) | ~500 tokens | **98%** |

## Single-command loop

```bash
# Set the goal (once)
ultrapilot-goals set \
  --profile secure --tokens 250K "[task]"

# Loop until done
ultrapilot-run next     # get phase prompt
# ... do the work ...
ultrapilot-run report \
  --phase <name> --result <path> --passed
# ... repeat ...
```

> **Prereq:** the `bin/` directory from the ultrapilot install must be on your `$PATH`
> (or invoke the wrappers as `python3 <install>/bin/ultrapilot-run`, etc.). The wrappers
> auto-resolve the install location via `ULTRAPILOT_HOME` or the conventional agent
> skills directory.

Works with **Pi, Claude Code, Codex, Gemini CLI, Cursor, Aider, Continue, OpenCode, Droid (Factory), or any LLM tool** that can run subprocess commands.

## Install

### Claude Code (marketplace)

```bash
# Add this repo as a marketplace
claude plugin marketplace add https://github.com/joychetry/ultrapilot

# Install
claude plugin install ultrapilot@ultrapilot-marketplace
```

Then invoke:
```
/ultrapilot:ultrapilot build a sponsorship dashboard
```

### Droid (Factory)

```bash
# Add this repo as a marketplace
droid plugin marketplace add https://github.com/joychetry/ultrapilot

# Install
droid plugin install ultrapilot@ultrapilot
```

### Codex

```bash
# Add the marketplace
npx codex-marketplace add joychetry/ultrapilot --plugins

# Or local install
npx codex-marketplace add /path/to/ultrapilot --plugins
```

### Pi (pi.dev)

Pi has no marketplace — it scans the filesystem for Agent Skills spec–compliant
`SKILL.md` files at startup. The standalone install below is the canonical path.

```bash
# Global install (Pi-specific location)
git clone https://github.com/joychetry/ultrapilot.git ~/.pi/agent/skills/ultrapilot

# OR: the universal location (works on Pi, Claude Code, and Codex)
git clone https://github.com/joychetry/ultrapilot.git ~/.agents/skills/ultrapilot

# Add the wrappers to your $PATH (pick the path you used above)
export PATH="$HOME/.pi/agent/skills/ultrapilot/bin:$PATH"
# or: export PATH="$HOME/.agents/skills/ultrapilot/bin:$PATH"
```

Then in any Pi session:

```
/skill:ultrapilot build a sponsorship dashboard
```

> **How Pi invokes the skill.** Pi auto-discovers `SKILL.md` files in
> `~/.pi/agent/skills/`, `~/.agents/skills/`, and the project-local `.pi/skills/`
> directory, and registers them as `/skill:<name>` commands. The skill name
> `ultrapilot` is what gets shown in the system prompt and matched against your
> request — Pi loads the full `SKILL.md` only when the description matches the
> task, so token cost stays low. See [pi.dev/docs/latest/skills](https://pi.dev/docs/latest/skills)
> for the full spec.

**End-to-end loop on Pi** (the model invokes the wrappers via `bash` — same
loop that runs on Claude Code / Droid / Codex):

```bash
# 1. Set the goal once
ultrapilot-goals set --profile secure --tokens 250K "build a sponsorship dashboard"

# 2. The model's loop (the agent runs these via its bash tool)
ultrapilot-run next     # get the current phase prompt
# ... do the work ...
ultrapilot-run report --phase explore --result /tmp/explore-result.md --passed
ultrapilot-run next     # advances to plan
# ... loop until done ...
```

> The `bin/ultrapilot-run` and `bin/ultrapilot-goals` wrappers auto-resolve the
> install location via `ULTRAPILOT_HOME` first, then `~/.pi/agent/skills/`,
> `~/.agents/skills/`, and the Claude Code / Droid / Codex fallbacks. Set
> `ULTRAPILOT_HOME` to override.

**Project-local install (Pi only):** for ultrapilot available inside one
project (and not globally):

```bash
cd /path/to/your/project
git clone https://github.com/joychetry/ultrapilot.git .pi/skills/ultrapilot
```

> Project-local skills are only loaded after you run `/trust` for the project.

### Standalone (any agent)

```bash
git clone https://github.com/joychetry/ultrapilot
ln -s "$(pwd)/ultrapilot" ~/.claude/skills/ultrapilot
# or
ln -s "$(pwd)/ultrapilot" ~/.factory/skills/ultrapilot
# or
ln -s "$(pwd)/ultrapilot" ~/.codex/skills/ultrapilot
# or (Pi, pi.dev)
ln -s "$(pwd)/ultrapilot" ~/.pi/agent/skills/ultrapilot
# or (universal location — works on Pi, Claude Code, Codex)
ln -s "$(pwd)/ultrapilot" ~/.agents/skills/ultrapilot
```

The skill's runtime (`scripts/ultrapilot_goals.py` and `scripts/ultrapilot_run.py`) is dependency-free Python 3.8+ and works without any agent runtime.

## Discipline layer (gated, default OFF)

Includes a discipline module — gated by a task-complexity classifier, default OFF. Trivial tasks skip it. Heavy tasks get it. Override with `--deep` (force ON) or `--quick` (force OFF). `ULTRATHINK` in the prompt also forces it ON.

## Multi-dimensional goal system (Phase 0)

Every run starts by setting weighted success criteria across six dimensions: **Correctness** (30%), **Reliability** (20%), **Efficiency** (10%), **Safety** (25%), **UX** (10%), **Cost** (5%). Use a preset profile (`--profile secure`, `--profile ship-it`, `--profile perf`, `--profile prototype`, `--profile infra`) or pass custom weights. Completion requires aggregate score ≥ 80% with per-dimension floors (safety ≥ 60%, correctness ≥ 70%).

**Agent-agnostic state engine.** The goal state lives in `scripts/ultrapilot_goals.py` — a single dependency-free Python script with a SQLite backend. No hooks, no agent-specific runtime. The single entry point is `ultrapilot_goals.py suggest`, which returns a JSON response describing the next action.

Derived from [Braintrust's agent evaluation framework](https://www.braintrust.dev/articles/agent-evaluation), [Brenndoerfer's success-criteria taxonomy](https://mbrenndoerfer.com/writing/setting-goals-and-success-criteria-ai-agent-evaluation), and [jthack/claude-goal](https://github.com/jthack/claude-goal)'s state/audit design.

## Tools the agent must bring (required, not provided)

ultrapilot is portable. The agent's runtime provides the tools. Minimal stack:

| Tool | Used in | Why |
|------|---------|-----|
| **Web search / web reader** | Explore | Discover current API changes, package versions |
| **Documentation fetcher** (e.g. Context7) | Plan/Build | Get current framework docs without trusting model memory |
| **Browser / dev tools / Playwright** | Verify (UI) | Open app, check console, click through flows, test mobile |
| **Git worktree** (optional) | All phases | Isolated branches for parallel runs |
| **Vision model** (optional) | Build (UI) | Convert screenshots to text if the active model can't process images — see `references/adapter-prompts.md` for per-model vision support |

ultrapilot references these in the verify prompt but does not ship them. The agent's runtime must provide them.

## What's in this repo

```
ultrapilot/
├── SKILL.md                 # Main orchestrator spec (entry point)
├── README.md                # You are here
├── LICENSE                  # MIT
├── CHANGELOG.md             # Version history
├── CONTRIBUTING.md          # How to extend
├── .claude-plugin/          # Claude Code marketplace manifest
│   └── marketplace.json
├── .codex-plugin/           # Codex plugin manifest
│   └── plugin.json
├── .factory-plugin/         # Droid plugin manifest
│   ├── plugin.json
│   └── marketplace.json
├── .agents/plugins/         # Codex repo marketplace
│   └── marketplace.json
├── plugins/ultrapilot/      # Sub-plugin manifests
│   ├── .claude-plugin/plugin.json
│   ├── .codex-plugin/plugin.json
│   └── .factory-plugin/plugin.json
├── commands/                # Companion phase commands (long-form docs)
├── prompts/                 # Lazy-loaded phase prompts (200-500 tokens each)
├── scripts/                 # Executable runtime
│   ├── ultrapilot_goals.py
│   └── ultrapilot_run.py
├── references/              # Extended reference material
├── examples/                # Worked examples
└── assets/                  # Branding, diagrams
```

## Source

Built from the synthesis of:

- The **structured-loop-with-gates** pattern: spec → plan → build → verify → review → patch. This shape is widely used (Anthropic's internal workflows, Addy Osmani's agent skills repo, obra's Superpowers framework). ultrapilot's specific implementation is independent.
- **Capability-class adapters** (in [`references/adapter-prompts.md`](references/adapter-prompts.md)) for behavior patterns observed across many chat and code models — not model-specific tuning.
- **[Anthropic's claude-code `code-review` plugin](https://github.com/anthropics/claude-code/blob/main/plugins/code-review/commands/code-review.md)** — multi-perspective review with confidence scoring.
- **[jthack/claude-goal](https://github.com/jthack/claude-goal)** — persistent goal state via SQLite, completion audit.
- **[Braintrust: Agent Evaluation](https://www.braintrust.dev/articles/agent-evaluation)** — multi-dimensional scoring framework.
- **[Brenndoerfer: Setting Goals and Success Criteria](https://mbrenndoerfer.com/writing/setting-goals-and-success-criteria-ai-agent-evaluation)** — success-criteria taxonomy.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). PRs welcome.

## License

MIT — see [LICENSE](LICENSE).
