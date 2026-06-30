---
name: example-rigorous-review
description: "Worked example — running the new multi-perspective /ultrapilot:review system with validation gating against a real diff."
type: example
---

# Example 04: Rigorous Multi-Perspective Review

**Task type:** Standalone review of an existing diff (the sponsorship dashboard from Example 01) using the v2 multi-agent review system.
**User prompt:** `/ultrapilot:review`
**Target:** Local diff of the sponsorship dashboard feature from `examples/01-add-feature.md`

This shows the v2 review system in action. The diff has been built, verified, and is ready for review. The user invokes `/ultrapilot:review` standalone (not as part of a full ultrapilot run).

---

## Step 0: Pre-flight check

```
✓ Diff present (git diff shows 12 changed files, +1,847 / -218)
✓ Not a closed or draft PR (local diff)
✓ Not already reviewed in this session
✓ Working tree has the diff but no uncommitted partial changes
```

Pre-flight passes. Proceed.

## Step 1: Project convention discovery

Reading project root and the affected directories:

```
$ ls AGENTS.md CLAUDE.md .cursorrules CONVENTIONS.md 2>/dev/null
AGENTS.md

$ cat AGENTS.md
# Project Conventions

## Code style
- No unused imports
- All exported functions must have JSDoc
- Use `cn()` utility for conditional classNames
- No `any` in TypeScript (use `unknown` and narrow)

## Components
- All forms must have empty, loading, error, and success states
- Server Components by default; mark with "use client" only when needed
- Use Server Actions for mutations

## Tests
- Test file mirrors source path: src/foo.ts → tests/foo.test.ts
- One describe block per function
- Test edge cases explicitly (empty, null, network error)
```

**Rules in scope for this diff:**
- `src/components/sponsors/*` → no-unused-imports, JSDoc on exports, server-component default, all states
- `lib/sponsors/*` → no-any, JSDoc, tests at `tests/lib/sponsors/`
- `app/(dashboard)/sponsors/*` → all states, Server Components

## Step 2: Multi-perspective parallel review

Four reviewers launched in parallel. Their raw candidate outputs:

### Reviewer 1 (Convention compliance — pass 1)

| # | File:Line | Category | Description | Reason | Confidence |
|---|-----------|----------|-------------|--------|------------|
| 1.1 | `lib/sponsors/actions.ts:12` | convention-violation | `createSponsorship` has no JSDoc | AGENTS.md requires JSDoc on exported functions | 90 |
| 1.2 | `components/sponsors/deal-form.tsx:8` | convention-violation | Unused import: `useEffect` | AGENTS.md: no unused imports | 95 |
| 1.3 | `app/(dashboard)/sponsors/new/page.tsx:1` | convention-violation | No `"use client"` directive but uses `useState` | AGENTS.md: server by default, client only when needed — but `useState` requires client | 85 |
| 1.4 | `components/sponsors/deal-card.tsx:22` | convention-violation | Missing JSDoc on `DealCard` | AGENTS.md requires JSDoc on exports | 90 |

### Reviewer 2 (Convention compliance — pass 2 — independent)

| # | File:Line | Category | Description | Reason | Confidence |
|---|-----------|----------|-------------|--------|------------|
| 2.1 | `components/sponsors/deal-form.tsx:8` | convention-violation | Unused import: `useEffect` | AGENTS.md: no unused imports | 95 |
| 2.2 | `lib/sponsors/queries.ts:34` | convention-violation | `getSponsorships` returns `any` | AGENTS.md: no `any` | 88 |
| 2.3 | `components/sponsors/deal-form.tsx:55` | convention-violation | Form has loading state but missing error state | AGENTS.md: all forms must have all four states | 80 |
| 2.4 | `lib/sponsors/validations.ts:1` | convention-violation | No test file for validations | AGENTS.md: tests mirror source | 70 |

### Reviewer 3 (Bug detection, diff-only)

| # | File:Line | Category | Description | Reason | Confidence |
|---|-----------|----------|-------------|--------|------------|
| 3.1 | `lib/sponsors/actions.ts:42` | bug | `revalidatePath` called with wrong path | Diff shows `revalidatePath('/sponsors')` but actual route is `app/(dashboard)/sponsors/page.tsx` which is at `/dashboard/sponsors` | 88 |
| 3.2 | `components/sponsors/deal-card.tsx:30` | bug | Currency formatted with `toFixed(2)` but no locale handling | Diff shows `.toFixed(2)` which produces `1234.50` not `$1,234.50` | 60 |
| 3.3 | `lib/sponsors/queries.ts:55` | bug | N+1 query in the deal list | Each deal triggers a separate `getContactById` call | 85 |

### Reviewer 4 (Bug detection, context-aware)

| # | File:Line | Category | Description | Reason | Confidence |
|---|-----------|----------|-------------|--------|------------|
| 4.1 | `lib/sponsors/actions.ts:42` | bug | `revalidatePath('/sponsors')` is wrong — should be `/dashboard/sponsors` | Read existing pattern in `lib/profile/actions.ts:18` which uses `revalidatePath('/dashboard/profile')` | 92 |
| 4.2 | `lib/sponsors/queries.ts:55` | bug | N+1 query in the deal list | Read existing pattern in `lib/deals/queries.ts:42` which uses a join. New code doesn't follow it. | 95 |
| 4.3 | `components/sponsors/deal-form.tsx:78` | security | No CSRF protection on the form action | Read existing pattern in `components/forms/Form.tsx:34` which wraps in CSRF middleware. New form doesn't. | 75 |
| 4.4 | `components/sponsors/deal-form.tsx:55` | bug | Form submit doesn't handle server-side validation errors | Existing pattern in `components/forms/Form.tsx:55` shows a toast for server errors. New form swallows them. | 80 |

**Summary of candidates:**
- 4 from R1 (convention)
- 4 from R2 (convention)
- 3 from R3 (bug, diff-only)
- 4 from R4 (bug, context-aware)
- Total: 15 candidate issues

## Step 3: Independent validation

Launching parallel validation agents for each unique candidate.

### Convention validations

| ID | Result | Validator reasoning |
|----|--------|---------------------|
| 1.1 | ✓ Confirmed | `createSponsorship` is exported and has no JSDoc. AGENTS.md requires it. |
| 1.2 | ✓ Confirmed | `useEffect` is imported but never used. AGENTS.md prohibits unused imports. |
| 1.3 | ✓ Confirmed | File uses `useState` but lacks `"use client"`. Will fail to compile. |
| 1.4 | ✓ Confirmed | `DealCard` is exported, no JSDoc. |
| 2.1 | ✓ Confirmed (duplicate of 1.2) | Same issue. |
| 2.2 | ✓ Confirmed | `getSponsorships` returns `Promise<any>`. AGENTS.md: no `any`. |
| 2.3 | ✗ Rejected | Form does have error state — see line 58 `<FormError />`. False positive. |
| 2.4 | ✗ Rejected | `tests/lib/sponsors/validations.test.ts` exists. Validator found it. False positive. |

### Bug validations

| ID | Result | Validator reasoning |
|----|--------|---------------------|
| 3.1 | ✓ Confirmed (duplicate of 4.1) | `revalidatePath('/sponsors')` is wrong. Should be `/dashboard/sponsors`. The route is at `app/(dashboard)/sponsors/`, not `app/sponsors/`. |
| 3.2 | ✗ Rejected | `toFixed(2)` is intentional for v1. The diff adds a TODO comment for locale handling. Not a bug, a documented deferral. |
| 3.3 | ✓ Confirmed (duplicate of 4.2) | N+1 query confirmed. |
| 4.1 | ✓ Confirmed | Same as 3.1. Path mismatch. |
| 4.2 | ✓ Confirmed | N+1 query confirmed. Existing pattern uses join. |
| 4.3 | ✗ Rejected | Form is a Server Action. Server Actions have built-in CSRF protection in Next.js. False positive — the agent did not know this. |
| 4.4 | ✓ Confirmed | Form swallows server validation errors. Existing pattern handles them. |

**Validation summary:**
- 15 candidates → 10 confirmed → 5 rejected
- Pass-through rate: 67%

## Step 4: High-signal filter

Apply the high-signal criteria to the 10 confirmed issues:

| ID | Confirmed? | In changed code? | On "flag" list? | Fixable? | Report? |
|----|-----------|------------------|-----------------|----------|---------|
| 1.1 | ✓ | ✓ | Convention violation | ✓ | **Yes** |
| 1.2 | ✓ | ✓ | Convention violation | ✓ | **Yes** |
| 1.3 | ✓ | ✓ | Compile error | ✓ | **Yes** |
| 1.4 | ✓ | ✓ | Convention violation | ✓ | **Yes** |
| 2.2 | ✓ | ✓ | Convention violation | ✓ | **Yes** |
| 3.1/4.1 | ✓ | ✓ | Wrong results | ✓ | **Yes** |
| 3.3/4.2 | ✓ | ✓ | Logic error | ✓ | **Yes** |
| 4.4 | ✓ | ✓ | Logic error | ✓ | **Yes** |

All 8 unique confirmed issues pass the high-signal filter. None are on the "do not flag" list.

## Step 5: Report

**Default terminal output (no `--comment` flag):**

```
# Review of sponsorship dashboard diff

## High-signal issues (8)

1. **[compile-error]** `app/(dashboard)/sponsors/new/page.tsx:1` — Missing "use client" directive
   - File uses `useState` but is missing the required directive. Will fail to compile.
   - Suggested fix: Add `"use client"` at the top of the file.

2. **[bug]** `lib/sponsors/actions.ts:42` — `revalidatePath` called with wrong path
   - Currently `revalidatePath('/sponsors')`. The actual route is at `app/(dashboard)/sponsors/` which resolves to `/dashboard/sponsors`.
   - Existing pattern: see `lib/profile/actions.ts:18`.
   - Suggested fix: change to `revalidatePath('/dashboard/sponsors')`.

3. **[bug]** `lib/sponsors/queries.ts:55` — N+1 query in deal list
   - Each deal triggers a separate `getContactById` call.
   - Existing pattern uses a join — see `lib/deals/queries.ts:42`.
   - Suggested fix: use a Supabase join in the `getSponsorships` query, or batch fetch contacts.

4. **[bug]** `components/sponsors/deal-form.tsx:78` — Form swallows server validation errors
   - When the server returns validation errors, the form does not display them to the user.
   - Existing pattern: see `components/forms/Form.tsx:55` (toast on server error).
   - Suggested fix: add an error display path that consumes the action's error result.

5. **[convention-violation]** `lib/sponsors/queries.ts:34` — `getSponsorships` returns `any`
   - AGENTS.md prohibits `any`. Use `unknown` and narrow.
   - Suggested fix: type the return as `Promise<Sponsorship[]>`.

6. **[convention-violation]** `components/sponsors/deal-form.tsx:8` — Unused import: `useEffect`
   - AGENTS.md prohibits unused imports.
   - Suggested fix: remove the import.

7. **[convention-violation]** `lib/sponsors/actions.ts:12` — `createSponsorship` lacks JSDoc
   - AGENTS.md requires JSDoc on exported functions.
   - Suggested fix: add JSDoc with @param and @returns.

8. **[convention-violation]** `components/sponsors/deal-card.tsx:22` — `DealCard` lacks JSDoc
   - AGENTS.md requires JSDoc on exported components.
   - Suggested fix: add JSDoc describing the component's purpose and props.

## Drive-by candidates (2)

- `lib/sponsors/actions.ts:88` — `deleteSponsorship` lacks JSDoc too (AGENTS.md violation, but pre-existing pattern across the codebase)
- `components/sponsors/deal-card.tsx:55` — Long brand name truncation works but is missing `aria-label` (pre-existing pattern, accessibility nit)

## Reviewer summary

| Reviewer | Flagged | Confirmed | Reported | Pass-through |
|----------|---------|-----------|----------|--------------|
| Convention (R1) | 4 | 4 | 4 | 100% |
| Convention (R2) | 4 | 2 (2 dup) | 2 | 50% (75% unique) |
| Bug diff-only (R3) | 3 | 2 (1 rejected) | 2 | 67% |
| Bug context-aware (R4) | 4 | 3 (1 rejected) | 3 | 75% |
| **Total** | **15** | **8 unique** | **8** | **53%** |

Validation rejected 5 of 15 candidates (33%): 2 false-positive convention violations, 1 deferred-feature (not a bug), 1 false-positive security (Server Actions have built-in CSRF), 1 duplicate of an existing test file.

## Re-verification status

[Waiting for ultrapilot:patch → ultrapilot:verify → ultrapilot:review loop]
```

---

## What the v2 review did differently than v1

**v1 (single-prompt self-review)** would have produced something like:

> "I see a few things to clean up: missing JSDoc, unused import, the revalidate path looks wrong, and the form could be improved."

That output is untrustworthy. The model is reviewing its own work. Confirmation bias is high. No false-positive filtering. The user has no way to know which issues are real.

**v2 (multi-agent with validation)** produced:

- 8 issues with line numbers, categories, and confidence scores
- 2 false positives caught and rejected at the validation step
- 1 rejected as a deferred feature (not a bug, has a TODO)
- 1 rejected as a false positive (Server Actions have CSRF built-in)
- Duplicate detection (issues 1.2/2.1, 3.1/4.1, 3.3/4.2) so they appear once in the report
- Drive-by candidates separated from blockers

**The cost:** about 4× more LLM calls than v1. The benefit: the user can trust the report. The 33% rejection rate at validation means the user is not chasing 5 false positives for every 8 real ones.

For a developer-time-saving tradeoff, v2 wins by a large margin. The whole point of review is to surface high-signal issues. Surfacing noise is not review — it is a tax on the reader.

---

## What happens next

The orchestrator picks up this report and dispatches:

1. `/ultrapilot:build` — patch the 8 confirmed issues
2. `/ultrapilot:verify` — re-run the test suite and manual flows
3. `/ultrapilot:review` — re-review the patched code (small, focused diff this time)

After the second review pass comes back clean, the task is complete.
