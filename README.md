# ultrapilot

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-blueviolet)](https://agentskills.io)
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
python3 ~/.hermes/skills/ultrapilot/scripts/ultrapilot_goals.py set \
  --profile secure --tokens 250K "[task]"

# Loop until done
python3 ~/.hermes/skills/ultrapilot/scripts/ultrapilot_run.py next     # get phase prompt
# ... do the work ...
python3 ~/.hermes/skills/ultrapilot/scripts/ultrapilot_run.py report \
  --phase <name> --result <path> --passed
# ... repeat ...
```

Works with **Claude Code, Codex, Gemini CLI, Cursor, Aider, Continue, OpenCode, Droid (Factory), or any LLM tool** that can run subprocess commands.

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

### Standalone (any agent)

```bash
git clone https://github.com/joychetry/ultrapilot
ln -s "$(pwd)/ultrapilot" ~/.claude/skills/ultrapilot
# or
ln -s "$(pwd)/ultrapilot" ~/.factory/skills/ultrapilot
# or
ln -s "$(pwd)/ultrapilot" ~/.codex/skills/ultrapilot
```

The skill's runtime (`scripts/ultrapilot_goals.py` and `scripts/ultrapilot_run.py`) is dependency-free Python 3.8+ and works without any agent runtime.

## Discipline layer (gated, default OFF)

Includes a discipline module derived from [AICodeKing's King Mode](https://github.com/aicodeking/yt-tutorial/blob/main/gemini-king-mode.md) — but loaded only when the task complexity justifies it. Trivial tasks skip it. Heavy tasks get it. Override with `--deep` (force ON) or `--quick` (force OFF). `ULTRATHINK` in the prompt also forces it ON.

## Multi-dimensional goal system (Phase 0)

Every run starts by setting weighted success criteria across six dimensions: **Correctness** (30%), **Reliability** (20%), **Efficiency** (10%), **Safety** (25%), **UX** (10%), **Cost** (5%). Use a preset profile (`--profile secure`, `--profile ship-it`, `--profile perf`, `--profile prototype`, `--profile infra`) or pass custom weights. Completion requires aggregate score ≥ 80% with per-dimension floors (safety ≥ 60%, correctness ≥ 70%).

**Agent-agnostic state engine.** The goal state lives in `scripts/ultrapilot_goals.py` — a single dependency-free Python script with a SQLite backend. No hooks, no agent-specific runtime. The single entry point is `ultrapilot_goals.py suggest`, which returns a JSON response describing the next action.

Derived from [Braintrust's agent evaluation framework](https://www.braintrust.dev/articles/agent-evaluation), [Brenndoerfer's success-criteria taxonomy](https://mbrenndoerfer.com/writing/setting-goals-and-success-criteria-ai-agent-evaluation), and [jthack/claude-goal](https://github.com/jthack/claude-goal)'s state/audit design.

## Tools the agent must bring (required, not provided)

ultrapilot is portable. The agent's runtime provides the tools. Per AICodeKing's minimal stack:

| Tool | Used in | Why |
|------|---------|-----|
| **Web search / web reader** | Explore | Discover current API changes, package versions |
| **Documentation fetcher** (e.g. Context7) | Plan/Build | Get current framework docs without trusting model memory |
| **Browser / dev tools / Playwright** | Verify (UI) | Open app, check console, click through flows, test mobile |
| **Git worktree** (optional) | All phases | Isolated branches for parallel runs |
| **Vision model** (optional) | Build (UI) | GLM 5.2 is text-only; convert screenshots to text |

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

- **[AICodeKing's "Maximizing GLM 5.2 Performance in Zcode"](https://youtu.be/HarkkqC9hpA)** (Jun 2026) — the explore → plan → build → verify → review → patch loop. Verified against the source in [`examples/08-verification-aicodeking.md`](examples/08-verification-aicodeking.md).
- **[Addy Osmani's agent skills repo](https://github.com/addyosmani/agent-skills)** — the lifecycle: spec → plan → build → test → review → simplify → ship.
- **[obra's Superpowers framework](https://github.com/obra/superpowers)** — lifecycle shape only; specific skills not bundled.
- **[Anthropic's claude-code `code-review` plugin](https://github.com/anthropics/claude-code/blob/main/plugins/code-review/commands/code-review.md)** — multi-perspective review with confidence scoring.
- **[jthack/claude-goal](https://github.com/jthack/claude-goal)** — persistent goal state via SQLite, completion audit.
- **[Braintrust: Agent Evaluation](https://www.braintrust.dev/articles/agent-evaluation)** — multi-dimensional scoring framework.
- **[Brenndoerfer: Setting Goals and Success Criteria](https://mbrenndoerfer.com/writing/setting-goals-and-success-criteria-ai-agent-evaluation)** — success-criteria taxonomy.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). PRs welcome.

## License

MIT — see [LICENSE](LICENSE).
