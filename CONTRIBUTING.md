# Contributing to /ultrapilot

Thanks for your interest in extending `/ultrapilot`. This document explains how to add new companion commands, refine existing phases, and ship improvements.

## Ground rules

1. **The loop is the product.** Changes that add steps, not discipline, will be rejected. If a new step doesn't have a clear gate and a clear failure mode, it doesn't belong.
2. **Model-agnostic is non-negotiable.** No prompt fragments that depend on a specific model's quirks. If it only works on Claude, document that and isolate it in `references/adapter-prompts.md`.
3. **Prompts are code.** They get tested against real tasks. If your change breaks the loop on a real task, it gets reverted.
4. **Negative space matters.** What `/ultrapilot` does *not* do is part of its value. Don't add capabilities that should be a separate skill.

## Repo structure

```
ultrapilot/
├── SKILL.md              # Main orchestrator spec
├── commands/             # Companion phase commands (one .md per phase)
├── references/           # Extended reference material
├── examples/             # Worked examples
└── assets/               # Branding, diagrams
```

Each command file in `commands/` is a self-contained slash command spec with:
- Frontmatter (name, description, parent, etc.)
- "When to Use" section
- "How to Invoke" section
- The actual prompt templates and rules
- A "Pitfalls" section
- A "Related Commands" section

## Adding a new companion command

1. Drop a new file in `commands/`.
2. Match the existing format (see `commands/explore.md` as a reference).
3. Update `SKILL.md` "Companion Commands" table.
4. Add a worked example in `examples/`.
5. Open a PR with a one-paragraph rationale and a tested transcript.

## Modifying an existing phase

1. Edit the relevant file in `commands/`.
2. Update the phase section in `SKILL.md` if the change affects the orchestrator's flow.
3. Add a CHANGELOG entry under `[Unreleased]`.
4. Test against at least two different models (a strong hosted model and one capability-class representative is a good baseline).
5. Open a PR.

## Adding a new reference doc

1. Drop a markdown file in `references/`.
2. Link it from `SKILL.md` if it's directly relevant to a phase or appendix.
3. Keep reference docs focused. One concept per file.

## Adding a worked example

1. Drop a markdown file in `examples/`.
2. Format: `NN-task-name.md` (e.g., `01-add-feature.md`).
3. Include: the user prompt, the orchestrator's plan output, the build summary, the verification report, the review report, and the final completion confirmation.
4. Real transcripts preferred over synthetic ones. If synthetic, mark it clearly.

## Versioning

We follow SemVer. Bump the major version when:
- The orchestrator's phase order changes
- A companion command is removed
- The completion condition logic changes

Bump the minor version when:
- A new companion command is added
- A new appendix is added to SKILL.md

Bump the patch version when:
- Documentation fixes
- Prompt template polish
- Example additions

## Testing your change

Before opening a PR, test against:

- [ ] A new feature add (e.g., sponsorship dashboard)
- [ ] A bug fix that touches one file
- [ ] A refactor that touches many files
- [ ] A greenfield project (no existing code)
- [ ] At least one non-default-class model if possible (local, small-context, or text-only)

## Review process

PRs are reviewed for:
- Alignment with the loop's discipline
- Model-agnosticism
- Test coverage
- Documentation completeness

Expect at least one round of feedback. Be patient, be specific, and link the test transcripts in your PR description.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
