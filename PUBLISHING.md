# Publishing ultrapilot to marketplaces

This document explains how to publish ultrapilot to each major agent marketplace. The skill is designed for one-repo-many-marketplace distribution: a single GitHub repo serves as the source for all of them.

## 0. Pre-publish checklist

Before publishing to any marketplace, ensure:

- [ ] The repo is at a stable Git URL (e.g. `https://github.com/joychetry/ultrapilot`)
- [ ] The default branch is `main`
- [ ] `LICENSE` is present (MIT)
- [ ] `README.md` has badges and install instructions
- [ ] `SECURITY.md` is present
- [ ] `CHANGELOG.md` is up to date
- [ ] All JSON manifests are valid
- [ ] CI is passing on the latest commit
- [ ] The smoke test passes:
  ```bash
  python3 scripts/ultrapilot_goals.py set --profile secure "test"
  python3 scripts/ultrapilot_goals.py status
  python3 scripts/ultrapilot_run.py next
  ```

## 0a. One-time: create the GitHub repo and push

If you have not pushed to GitHub yet, the fastest path is the `gh` CLI:

```bash
cd /Users/joysmacbook/Documents/GitHub/ultrapilot

# Initialize (skip if already a git repo)
git init
git add .
git commit -m "Initial release v1.0.0"

# Create the public GitHub repo and push in one shot
gh repo create joychetry/ultrapilot --public \
  --source=. --push \
  --description "Single-command engineering orchestrator with state-machine-driven explore → plan → build → verify → review → patch loop. Model-agnostic, token-optimized."

# Verify the push landed
gh repo view joychetry/ultrapilot --web
```

If you prefer a manual flow:

```bash
# On GitHub, create a public repo at https://github.com/new named "ultrapilot"
# Then locally:
git remote add origin https://github.com/joychetry/ultrapilot.git
git branch -M main
git push -u origin main
```

After the first push, tag the release and let `release-drafter` build the notes:

```bash
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
gh release create v1.0.0 --generate-notes
```

## 1. Publish to the open Agent Skills spec (agentskills.io)

The open spec at [agentskills.io](https://agentskills.io) is the cross-platform standard. Any tool that supports it (Claude Code, Codex, Droid, Cursor, Aider, Continue, OpenCode) can install the skill from this single submission.

**Repository layout required:**

```
ultrapilot/
├── SKILL.md         # With name + description + license + compatibility in frontmatter
├── scripts/
├── prompts/
├── commands/
├── references/
└── LICENSE
```

The root-level `SKILL.md` is the canonical entry point. All other files are optional.

**To publish:**

1. Push the repo to GitHub (public).
2. Submit a PR to the [agentskills/agentskills](https://github.com/agentskills/agentskills) showcase repo, OR publish on your own and link from your README.
3. Validate with:
   ```bash
   npx skills-ref validate ./
   ```
   (The `skills-ref` tool is the official validator.)

**What the spec validates:**

- `name` field: 1-64 chars, lowercase letters/numbers/hyphens, no leading/trailing hyphen
- `description`: 1-1024 chars, describes what + when
- `license`: optional, name or bundled file
- `compatibility`: optional, environment requirements

ultrapilot passes all of these.

**What the spec does NOT require:**

- Marketplace manifests (those are marketplace-specific)
- A `plugin.json` (that's the plugin system, not the skill spec)
- Hooks or commands (those are optional additions)

## 2. Publish to Claude Code marketplace

Claude Code has its own plugin marketplace system, layered on top of the agent skills spec.

**Repository layout required (in addition to the open spec):**

```
ultrapilot/
├── .claude-plugin/
│   └── marketplace.json   # Lists the plugins in this marketplace
├── plugins/
│   └── ultrapilot/
│       ├── .claude-plugin/
│       │   └── plugin.json   # Plugin manifest
│       └── SKILL.md          # Plugin's entry point (or skills/<name>/SKILL.md)
└── ...
```

**Files already in this repo:**

- `.claude-plugin/marketplace.json` — declares the `ultrapilot-marketplace` marketplace and the `ultrapilot` plugin
- `plugins/ultrapilot/.claude-plugin/plugin.json` — plugin manifest with name, version, description, author, license
- `plugins/ultrapilot/skills/ultrapilot/SKILL.md` — the skill itself (subdir matches Claude Code's convention)

**To publish:**

1. Push the repo to GitHub.
2. Have users add the marketplace and install:
   ```bash
   claude plugin marketplace add https://github.com/joychetry/ultrapilot
   claude plugin install ultrapilot@ultrapilot-marketplace
   ```
3. (Optional) Submit the marketplace to Anthropic's curated marketplaces. See [code.claude.com/docs/en/plugin-marketplaces](https://code.claude.com/docs/en/plugin-marketplaces). Anthropic maintains `claude-code-plugins`, `anthropic-marketplace`, and others. To submit:
   - Open a PR to the relevant marketplace repo adding your marketplace source
   - Include a clear description, use case, and category
4. Validate locally with:
   ```bash
   claude plugin validate ./
   ```

**Reserved marketplace names** (do not use these — they conflict with Anthropic's official marketplaces):
- `claude-code-marketplace`
- `claude-code-plugins`
- `claude-plugins-official`
- `claude-plugins-community`
- `claude-community`
- `anthropic-marketplace`
- `anthropic-plugins`
- `agent-skills`
- `anthropic-agent-skills`
- `knowledge-work-plugins`
- `life-sciences`
- `claude-for-legal`
- `claude-for-financial-services`
- `financial-services-plugins`
- `official-claude-plugins`
- `anthropic-tools-v2`

## 3. Publish to Droid (Factory) marketplace

Droid's plugin format is **interoperable with Claude Code's** (per [Factory docs](https://docs.factory.ai/cli/configuration/plugins#claude-code-compatibility)). The same repo works for both.

**Additional files required for Droid:**

```
ultrapilot/
├── .factory-plugin/
│   ├── plugin.json       # Plugin manifest
│   └── marketplace.json  # Marketplace listing
└── plugins/ultrapilot/
    └── .factory-plugin/
        └── plugin.json   # Sub-plugin manifest
```

**Files already in this repo:**

- `.factory-plugin/plugin.json` and `.factory-plugin/marketplace.json` at the root
- `plugins/ultrapilot/.factory-plugin/plugin.json` for sub-plugin format

**To publish:**

1. Push the repo to GitHub.
2. Have users add the marketplace and install:
   ```bash
   droid plugin marketplace add https://github.com/joychetry/ultrapilot
   droid plugin install ultrapilot@ultrapilot
   ```
3. (Optional) Submit to [Factory-AI/factory-plugins](https://github.com/Factory-AI/factory-plugins) for inclusion in the official `factory-plugins` marketplace. Open a PR with the marketplace URL.

**Note:** Droid uses `.factory-plugin/` not `.claude-plugin/`. Both are present in this repo. The user can install from either path; the `.factory-plugin/` is the canonical Droid entry.

## 4. Publish to Codex

Codex uses the open agent skills spec. Skills install from the spec directly, no plugin wrapper required.

**To publish (local install):**

```bash
# As a standalone skill
$skill-installer install https://github.com/joychetry/ultrapilot

# Or via the Codex plugin system (Codex also supports plugins)
npx codex-marketplace add joychetry/ultrapilot --plugins
```

**Additional files for Codex plugin format:**

```
ultrapilot/
├── .codex-plugin/
│   └── plugin.json        # Plugin manifest
├── .agents/plugins/
│   └── marketplace.json   # Repo marketplace
└── plugins/ultrapilot/
    └── .codex-plugin/
        └── plugin.json    # Sub-plugin manifest
```

**Files already in this repo.**

**To publish to the official Codex plugin registry** (if/when one exists for community plugins), open a PR to the registry repo. As of late 2026, the main path is via `$skill-installer` or `npx codex-marketplace add`.

## 5. Publish to claudeskills.info (curated marketplace)

[claudeskills.info](https://claudeskills.info/skills) is a community-curated directory of 658+ skills.

**To publish:**

1. Push the repo to GitHub.
2. Open an issue or PR on the [claudeskills.info](https://github.com/claudeskills/info) repo with:
   - Repo URL
   - One-paragraph description
   - Category (suggest: `development` or `workflow-automation`)
3. The site uses the open SKILL.md standard, so no additional packaging is needed.

## 6. Publish as a downloadable release

For users on agents that don't have a marketplace:

1. Create a GitHub release with a semver tag (e.g. `v1.0.0`).
2. Attach a tarball:
   ```bash
   git archive --format=tar.gz --prefix=ultrapilot/ v1.0.0 > ultrapilot-1.0.0.tar.gz
   ```
3. Users can install manually:
   ```bash
   # Claude Code (default)
   tar -xzf ultrapilot-1.0.0.tar.gz -C ~/.claude/skills/
   # Droid
   tar -xzf ultrapilot-1.0.0.tar.gz -C ~/.factory/skills/
   # Codex
   tar -xzf ultrapilot-1.0.0.tar.gz -C ~/.codex/skills/
   # Other agents (Hermes, etc.) — substitute the relevant skills directory
   ```

## 7. Update the marketplaces after a release

When you cut a new release:

```bash
# 1. Tag the release
git tag -a v1.1.0 -m "Release 1.1.0"
git push origin v1.1.0

# 2. Update the version field in EVERY plugin.json / marketplace.json
#    (or rely on the git-SHA-based version fallback)

# 3. Users update via:
claude plugin update ultrapilot@ultrapilot-marketplace
droid plugin update ultrapilot@ultrapilot
```

Version resolution depends on the marketplace:
- **Claude Code**: pins to the git SHA unless `version` is set in `plugin.json` or `marketplace.json`
- **Droid**: tracks the marketplace's default branch
- **Codex**: tracks the repo's latest commit

For deterministic releases, set `version` explicitly in each `plugin.json`.

## Marketplace submission order (suggested)

1. **Open spec (agentskills.io)** — single submission, works everywhere
2. **claudeskills.info** — easy PR, high visibility
3. **Claude Code marketplace** — bigger user base, gated
4. **Droid marketplace** — same as Claude Code (interoperable)
5. **Codex** — via `npx codex-marketplace`
6. **GitHub release** — fallback for users without a marketplace

## What NOT to do

- **Don't submit to multiple Claude Code marketplaces with the same name.** Each user can only register one marketplace per name; duplicates will replace the existing one.
- **Don't use Anthropic's reserved marketplace names** (see list above).
- **Don't publish without a working smoke test.** A broken skill wastes reviewer time and erodes trust.
- **Don't use `master` as the default branch.** Use `main`.
- **Don't bake an agent-specific hard dependency** (no Claude-Code-only hooks, no Codex-only `app.json`). ultrapilot is model-agnostic by design.

## Support

For questions about publishing, open an issue on the repo or contact the maintainers.
