---
name: ultrapilot-explore
description: "/ultrapilot:explore — Read-only architecture mapping of the current project. Run before any edit. Standalone phase command for the ultrapilot orchestrator."
license: MIT
allowed-tools: Bash, Read, Grep, Glob
metadata:
  author: joychetry
  version: "1.0"
  category: software-development
  parent: ultrapilot
---

# /ultrapilot:explore

**Phase 1 of /ultrapilot.** Read-only codebase mapping. No edits.

## When to Use

- At the start of any task in an existing codebase
- When onboarding to a new project
- Before making architectural decisions
- When a "where do I add this?" question comes up

## How to Invoke

```
/ultrapilot:explore
```

Or with a focus:

```
/ultrapilot:explore focus on the auth and routing layers
```

## The Prompt

Use this exact structure:

```
Use explore only.
Read the project structure. Identify the framework, package manager, test commands, styling system, routing setup, and any database or auth layer. Do not edit files.
Give me a short architecture map and tell me the safest way to add a new feature.
```

For greenfield projects, replace "the safest way to add a new feature" with "the recommended structure for a new [type] project."

## Required Output

The architecture map must include:

- **Framework and language** (React, Next.js, Vue, Django, etc.)
- **Package manager** (npm, pnpm, yarn, pip, poetry) and lockfile presence
- **Test command and where tests live** (Jest, Vitest, pytest, etc.)
- **Styling system** (Tailwind, CSS modules, styled-components, etc.)
- **Routing setup** (file-based, programmatic, API routes)
- **Database and auth layer** (Prisma, Drizzle, Supabase, custom)
- **Existing patterns** for state, data fetching, error handling
- **Safest extension point** for the planned feature

## Why This Matters

The model needs a mental model of the repo before touching anything. A 2-minute read-only exploration prevents 20 minutes of "let me check how the existing code does this" thrashing during the build phase. It also surfaces constraints the model would not see otherwise (existing types, conventions, dependencies).

## Pitfalls

- **Do not skip this for "small" projects.** The smallest project still has a package.json, a test command, and conventions. Map them.
- **Do not edit during explore.** If you catch yourself wanting to "fix" something while exploring, stop. Note it and revisit later.
- **Do not summarize what you expect to see.** Read the actual files. Verify with `ls`, `cat`, or read tools.

## Related Commands

- `/ultrapilot:plan` — runs after explore
- `/ultrapilot` — full orchestrator
