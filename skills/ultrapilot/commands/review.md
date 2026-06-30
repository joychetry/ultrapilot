---
name: ultrapilot-review
description: "/ultrapilot:review — Multi-perspective diff audit with validation gating. Uses parallel reviewer agents to surface bugs, CLAUDE.md/AGENTS.md violations, and code-quality issues. Each issue is independently re-validated before being reported. Model-agnostic. Phase 5 of /ultrapilot."
license: MIT
allowed-tools: Bash, Read, Grep, Glob, Edit, Write
metadata:
  author: joychetry
  version: "2.0"
  category: software-development
  parent: ultrapilot
---

# /ultrapilot:review

**Phase 5 of /ultrapilot.** The diff is the product. It must match the goal — and it must be free of high-signal bugs, project-policy violations, and the kind of issues that erode reviewer trust.

This is the rigorous version. It is structured as a multi-agent review with independent validation, inspired by Anthropic's [claude-code code-review plugin](https://github.com/anthropics/claude-code/blob/main/plugins/code-review/commands/code-review.md) and adapted to be model-agnostic, framework-neutral, and usable against any diff (local or PR).

## When to Use

- After verify passes, before declaring the task done
- Whenever the model is about to claim a task is finished
- As a final pass before opening a PR or merging
- Standalone, to review an existing diff without going through the full ultrapilot loop

## How to Invoke

```
/ultrapilot:review
```

With a goal reference:

```
/ultrapilot:review against the plan in /tmp/plan.md
```

With a target PR (if `gh` is available and the repo is on GitHub):

```
/ultrapilot:review --pr 123
```

With local diff only (no PR context):

```
/ultrapilot:review --local
```

## The Five-Step Review

The review runs five steps. Each step has a clear input, output, and failure mode. If a step fails, do not advance.

### Step 0: Pre-flight check

Before any review work, check:

- Is the diff actually present? (`git diff` produces output, or a PR exists)
- If reviewing a PR: is it open, non-draft, and not a trivial automated change?
- Has this diff already been reviewed in this session? (Avoid duplicate work)
- Is the working tree clean enough to reason about? (No half-applied changes)

If any condition blocks review, stop and report. Do not invent issues to fill the gap.

### Step 1: Discover project conventions

Read the project's instruction files (if they exist) and treat them as a contract the diff must follow:

- `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `CONVENTIONS.md` — or equivalents
- Any file at the project root or in directories touched by the diff
- Linter/formatter configs that are not just stylistic (`eslint.config.js` rules marked as errors, `tsconfig.json` strict mode, etc.)

Only count rules that are **scoped to the file being reviewed or its parent directories.** Do not apply root-level rules to nested files unless the file path matches the rule's scope.

Output: a list of rules the diff must respect. If no instruction files exist, this step is a no-op and the reviewer falls back to standard engineering defaults.

### Step 2: Multi-perspective parallel review

Launch four reviewers in parallel, each looking at the same diff from a different angle. Each reviewer returns a list of **candidate issues**, where each issue has:

- A clear description
- The category (`bug`, `convention-violation`, `security`, `logic-error`)
- The line(s) and file(s) affected
- A `reason` field explaining why it was flagged
- A confidence score from 0–100 (the reviewer's own estimate)

**Reviewer 1 — Convention compliance**
Audits the diff against the project instruction files discovered in Step 1. Looks for clear, unambiguous violations where the rule and the violation both exist in the file. Does not guess. Does not extrapolate rules.

**Reviewer 2 — Convention compliance (independent pass)**
Same task as Reviewer 1, but launched as a separate agent so it does not see Reviewer 1's output. Independent perspectives catch different violations and reduce the chance of both missing the same issue.

**Reviewer 3 — Bug detection (diff-only)**
Scans the diff itself for obvious bugs. Reads only the diff. Does not consult surrounding context. Flags only significant bugs — not nitpicks, not style, not "this could be cleaner." If an issue cannot be validated from the diff alone, skip it.

**Reviewer 4 — Bug detection (context-aware)**
Looks for problems that exist in the introduced code. This time it can read surrounding files for context. Looks for security issues, incorrect logic, type errors, broken control flow, missing error handling, etc. Still scoped to the changed code — not the entire codebase.

### Step 3: Independent validation

For every candidate issue from Reviewers 3 and 4 (the bug reviewers), launch a separate validation agent. Convention violations from Reviewers 1 and 2 only need a single validation pass each.

The validation agent receives:
- The PR title and description (if available)
- The original issue description and the reviewer's reason for flagging it
- Access to the relevant file(s) and surrounding context

The validation agent's job is to **confirm or reject** the issue with high confidence. Examples:

- "Variable is not defined" — does the file actually lack that variable, or is it imported?
- "Off-by-one in loop" — is the loop actually off by one, or is the boundary correct?
- "CLAUDE.md rule X violated" — does the rule apply to this file, and is the violation real?

If the validator cannot confirm the issue, the issue is rejected. **If you are not certain an issue is real, do not flag it.** False positives erode trust and waste reviewer time.

Validation rules:
- Bugs and logic issues → validate with the strongest available model
- Convention violations → validate with a fast model (the rule either applies or it doesn't)
- Each validation runs in parallel

### Step 4: High-signal filter

Take all validated issues and apply the high-signal filter. **An issue is reported only if it meets ALL of these criteria:**

1. **It is real.** The validator confirmed it.
2. **It is in the changed code.** Pre-existing issues in untouched code are out of scope.
3. **It is not a false positive.** It is not on the "do not flag" list below.
4. **It is fixable or actionable.** The reviewer can describe the fix.

**Flag these (high signal):**
- The code will fail to compile or parse (syntax errors, type errors, missing imports, unresolved references)
- The code will definitely produce wrong results regardless of inputs (clear logic errors)
- Clear, unambiguous project-instruction violations where you can quote the exact rule being broken
- Security vulnerabilities introduced by the change (auth bypass, injection, path traversal, etc.)
- Data loss or corruption risks introduced by the change

**Do NOT flag these (false positives):**
- Pre-existing issues in unchanged code
- Code that looks like a bug but is actually correct
- Pedantic nitpicks a senior engineer would not flag
- Issues a linter will catch (the linter runs in verify — do not duplicate its job here)
- General code quality concerns (lack of test coverage, naming preferences) unless explicitly required by project instructions
- Issues mentioned in project instructions but explicitly silenced in the code (e.g., via a lint ignore comment)
- Subjective style preferences

### Step 5: Report and (optionally) post

Produce the final review output. The default is to print the report to the terminal. If the `--comment` flag is passed and the review target is a PR, post inline comments to the PR.

**Default terminal output format:**

```
# Review of [target]

## High-signal issues (3)

1. **[bug]** `src/auth/session.ts:42` — `verifyToken` is called with the wrong argument
   - The `token` argument is `req.headers.authorization` (a string) but `verifyToken` expects a parsed token object.
   - Suggested fix: parse the bearer token before calling `verifyToken`.

2. **[convention-violation]** `src/views/Dashboard.tsx:18` — unused import violates the project's "no unused imports" rule in AGENTS.md
   - `import { useEffect }` is not used in this file.
   - Suggested fix: remove the import.

3. **[bug]** `lib/sponsors/queries.ts:55` — N+1 query in the deal list
   - For each deal, a separate `getContactById` call is made.
   - Suggested fix: use a join or batch fetch.

## Drive-by candidates (2)

- `src/views/Pipeline.tsx:99` — minor: header alignment off at 320px (pre-existing, not from this diff)
- `lib/auth/roles.ts:30` — minor: role check is duplicated in two places (pre-existing, not from this diff)

## Reviewer summary

- Convention compliance: 2 issues flagged, 1 validated, 1 reported
- Bug detection (diff-only): 1 issue flagged, 1 validated, 1 reported
- Bug detection (context-aware): 2 issues flagged, 1 validated, 1 reported
- Total: 5 flagged → 4 validated → 3 reported (60% pass-through)

## Re-verification status

[Waiting for ultrapilot:patch → ultrapilot:verify loop]
```

**If `--comment` is passed and no issues were found:**

```
## Code review
No issues found. Checked for bugs and project-convention compliance.
```

**If `--comment` is passed and issues were found:**

Post one inline comment per issue. For each:
- Provide a brief description
- For small, self-contained fixes (≤5 lines, single file), include a committable suggestion block in a fenced code block
- For larger fixes, describe the issue and suggested approach without a suggestion block
- **Never post a committable suggestion UNLESS applying it fixes the issue entirely.** If follow-up steps are required, describe instead.

**CRITICAL: only post ONE comment per unique issue.** Do not duplicate.

## What the Reviewer Looks For (reference)

| Category | Examples |
|----------|----------|
| Compile/parse | Syntax error, type error, missing import, unresolved reference |
| Wrong results | Off-by-one, wrong operator, inverted condition, wrong variable used |
| Convention violation | Unused import (if rule says so), wrong file location, missing required test |
| Security | Auth bypass, missing permission check, injection, path traversal, secret leak |
| Logic error | Async/await mismatch, missing return, swallowed error, wrong default value |
| State management | Stale closure, race condition, missing cleanup, state update after unmount |
| Resource leak | Unclosed connection, missing cleanup, unbounded growth |
| Data integrity | Migration without rollback, destructive operation without backup, missing transaction |

## Scoped Patching

The reviewer should be **ruthless but scoped.** It is not refactoring unrelated code. It is closing the gap between "works on the happy path" and "works."

If the reviewer finds an unrelated issue (something that was wrong before this task), note it in the drive-by candidates list but do not fix it. The user can decide whether to address it now or later.

## Required Output

The review pass must produce:

1. **Pre-flight check result** — was review even possible?
2. **Convention rules discovered** — what the diff must respect
3. **Candidate issues from each reviewer** (raw, before validation)
4. **Validation result per candidate** (confirmed / rejected)
5. **Final high-signal report** (the only output the user sees by default)
6. **Drive-by candidates list** (noted but not blocking)
7. **Re-verification status** (pending until the patch loop completes)

If the reviewer finds nothing actionable, that is the green light for `/ultrapilot` to declare the task done.

## Multi-Model Strategy

`/ultrapilot:review` is model-agnostic but benefits from a model mix if available:

| Reviewer | Best model | Acceptable model |
|----------|-----------|------------------|
| Convention compliance (×2) | Fast, deterministic | Any |
| Bug detection (diff-only) | Strong reasoning, careful | Strong reasoning |
| Bug detection (context-aware) | Strong reasoning, large context | Strong reasoning |
| Bug validation | Strongest available | Strong reasoning |
| Convention validation | Fast, deterministic | Any |

If only one model is available, use it for everything. The discipline still applies; only the speed varies.

## Pitfalls

- **Do not let the reviewer rewrite the whole codebase.** Scope is critical.
- **Do not skip the validation pass.** A single reviewer over-confidently flagging an issue is how you ship 10 false positives per real one.
- **Do not post issue lists to the user before validation.** Raw reviewer output is noisy. The user only sees the validated, filtered set.
- **Do not flag pre-existing issues as new bugs.** They are drive-by candidates, not blockers.
- **Do not duplicate the linter's job.** If the linter would catch it, the linter is running in verify.
- **Do not skip the drive-by list.** Those are real bugs. They just are not this task's bugs.
- **Do not re-review without re-verifying.** After patches, the verification suite must run again, then the new code should be re-reviewed.

## Related Commands

- `/ultrapilot:verify` — runs before review
- `/ultrapilot:build` — loops back to this if review found issues that need a code change
- `/ultrapilot` — full orchestrator
- `/ultrapilot:steer` — for mid-flight intervention when the reviewer disagrees with the model

## Source

This review design is adapted from:
- [Anthropic's claude-code code-review plugin](https://github.com/anthropics/claude-code/blob/main/plugins/code-review/commands/code-review.md) — multi-agent review with confidence scoring
- obra's Superpowers — review-before-ship discipline
- Addy Osmani's agent skills repo — the `review` phase of the lifecycle
