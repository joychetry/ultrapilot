---
name: example-add-feature
description: "Worked example — adding a new feature (sponsorship dashboard) to an existing app using /ultrapilot."
type: example
---

# Example 01: Add a Feature

**Task type:** Add a new feature to an existing codebase.
**User prompt:** `/ultrapilot build a sponsorship dashboard inside this app — track brand deals, deliverables, deadlines, invoice status, contacts`
**Target stack:** Next.js 14 + TypeScript + Tailwind + Supabase

---

## Step 1: Explore phase

**Orchestrator dispatches:** `/ultrapilot:explore`

**Output (architecture map):**

```
Framework: Next.js 14.2.1 (App Router)
Language: TypeScript 5.4
Package manager: pnpm 9.0
Test command: pnpm test (Vitest 1.6)
Test location: tests/ + *.test.ts files alongside source
Styling: Tailwind CSS 3.4 + shadcn/ui components
Routing: App Router (app/ directory)
Database: Supabase (Postgres + Auth)
Auth layer: Supabase Auth with @supabase/ssr
State: React Server Components + useState, no Redux
Data fetching: Server Actions + revalidatePath
Error handling: error.tsx boundary per route
Styling conventions: cn() utility, cva for variants, lucide-react icons

Safest extension point: Create a new route group (app/(dashboard)/sponsors/) 
that reuses the existing layout and auth patterns. The existing user 
profile page at app/(dashboard)/profile/ is a good reference for 
the data model and form patterns.
```

## Step 2: Plan phase

**Orchestrator dispatches:** `/ultrapilot:plan`

**Output:**

```markdown
# Plan: Sponsorship Dashboard

## Goal
Build a /dashboard/sponsors route that tracks brand deals, deliverables, 
deadlines, invoice status, and contacts. Reuses the existing Supabase schema 
and Next.js App Router patterns.

## Acceptance Criteria
- [ ] User can see a list of all their sponsorship deals
- [ ] Each deal shows: brand name, value, status, deadline, deliverable count
- [ ] User can create a new deal
- [ ] User can edit an existing deal
- [ ] User can mark a deal as paid (updates invoice_status)
- [ ] Empty state: "No deals yet — add your first sponsorship"
- [ ] Loading state: skeleton rows
- [ ] Error state: "Couldn't load deals. Try again."
- [ ] Mobile responsive (cards stack, table → list)
- [ ] All tests pass, build succeeds

## Files to Create
- app/(dashboard)/sponsors/page.tsx — main list view
- app/(dashboard)/sponsors/new/page.tsx — create form
- app/(dashboard)/sponsors/[id]/page.tsx — edit form
- app/(dashboard)/sponsors/[id]/edit/page.tsx — alternative inline edit
- components/sponsors/deal-card.tsx — list item component
- components/sponsors/deal-form.tsx — create/edit form
- components/sponsors/deal-status-badge.tsx — status indicator
- lib/sponsors/actions.ts — Server Actions for CRUD
- lib/sponsors/queries.ts — Supabase queries
- lib/sponsors/types.ts — TypeScript types
- lib/sponsors/validations.ts — Zod schemas
- supabase/migrations/20260630_create_sponsorships.sql — DB schema

## Files to Change
- components/nav/sidebar.tsx — add "Sponsors" link

## Steps
1. Create the Supabase migration (sponsorships table, RLS policies)
2. Create lib/sponsors/ (types, validations, queries, actions)
3. Create the deal form component (Zod-validated, with empty/loading/error states)
4. Create the deal card component (status badge, value formatting)
5. Create the list page (server component, fetches via queries.ts)
6. Create the create page (form action)
7. Create the edit page (form action with optimistic update)
8. Add the sidebar link
9. Write tests for actions, queries, and form validation
10. Run full verification suite

## Assumptions
- Users own their sponsorship deals (RLS by user_id)
- Currency is USD (no multi-currency in v1)
- Status values: pending, active, paid, cancelled
- No file attachments in v1 (just text fields)

## Out of Scope
- Multi-currency support
- File attachments (logo, contract PDF)
- Email notifications on status change
- Bulk import from CSV
- Reporting/analytics dashboard

## Verification
- pnpm test exits 0
- pnpm build succeeds
- pnpm typecheck exits 0
- pnpm lint exits 0
- Manual: create deal → see in list → edit → refresh → data persists
- Manual: empty state shows when no deals
- Manual: mobile layout works at 375px, 768px, 1440px
```

**User feedback:** "Looks good. Proceed."

## Step 3: Build phase

**Orchestrator dispatches:** `/ultrapilot:build`

**Build summary:**

```
Step 1: Created supabase/migrations/20260630_create_sponsorships.sql
        - sponsorships table (id, user_id, brand_name, value, status, deadline, etc.)
        - RLS policy: user can only CRUD their own deals
        - Index on user_id and status
        
Step 2: Created lib/sponsors/types.ts
        - Sponsorship, SponsorshipStatus, CreateSponsorshipInput types
        
Step 3: Created lib/sponsors/validations.ts
        - Zod schema for create/edit with proper error messages
        
Step 4: Created lib/sponsors/queries.ts
        - getSponsorships, getSponsorshipById, etc. with RLS-respecting queries
        
Step 5: Created lib/sponsors/actions.ts
        - createSponsorship, updateSponsorship, markAsPaid Server Actions
        - revalidatePath('/dashboard/sponsors') after mutations
        
Step 6: Created components/sponsors/deal-status-badge.tsx
        - Variants for each status, accessible labels
        
Step 7: Created components/sponsors/deal-form.tsx
        - Reusable for create + edit
        - Optimistic updates via useOptimistic
        - Empty/loading/error states
        
Step 8: Created components/sponsors/deal-card.tsx
        - Shows brand, value, status, deadline, deliverable count
        - Click to edit
        
Step 9: Created app/(dashboard)/sponsors/page.tsx
        - Server component, fetches via queries
        - Renders list or empty state
        - Skeleton loading via loading.tsx
        
Step 10: Created app/(dashboard)/sponsors/new/page.tsx + [id]/edit/page.tsx
        
Step 11: Updated components/nav/sidebar.tsx — added Sponsors link
        
Step 12: Wrote tests in tests/lib/sponsors/ and tests/components/sponsors/
        - actions.test.ts (mocked Supabase)
        - validations.test.ts
        - deal-form.test.ts (Vitest + Testing Library)
```

## Step 4: Verify phase

**Orchestrator dispatches:** `/ultrapilot:verify`

**Output:**

```
✓ pnpm typecheck — 0 errors
✓ pnpm lint — 0 errors, 0 warnings
✓ pnpm test — 47 passed, 0 failed
  - lib/sponsors/actions.test.ts: 8 passed
  - lib/sponsors/queries.test.ts: 6 passed
  - lib/sponsors/validations.test.ts: 12 passed
  - components/sponsors/deal-form.test.ts: 15 passed
  - components/sponsors/deal-card.test.ts: 6 passed
✓ pnpm build — succeeded
✓ Manual: created a deal, appeared in list
✓ Manual: edited the deal, change persisted after refresh
✓ Manual: marked as paid, status updated, invoice_status changed
✓ Manual: deleted last deal, empty state shown
✓ Manual: mobile layout at 375px — cards stack, no overflow
✓ Manual: dev tools console — 0 errors

All acceptance criteria met.
```

## Step 5: Review phase

**Orchestrator dispatches:** `/ultrapilot:review`

**Output:**

```
Reviewing the diff against the original goal.

Issues found (connected):
1. Deal card didn't truncate long brand names — added truncate class
2. Form didn't show server-side validation errors in toast — fixed
3. Edit form pre-filled with stale data on rapid navigation — added useEffect reset

Issues found (drive-by, not fixed):
- The existing user profile form has the same stale-data bug. Note for future.
- The sidebar nav has a small icon alignment issue on iPad.

Connected issues: 3 found, 3 fixed.

Re-verification after patches:
✓ pnpm test — 47 passed, 0 failed
✓ Manual: stale data issue resolved
✓ Manual: long brand names truncate correctly

Drive-by candidates:
- Fix user profile form stale-data bug
- Fix sidebar icon alignment on iPad
```

## Step 6: Completion

```
Task: Add a sponsorship dashboard to the existing app

Status: COMPLETE
- Plan acceptance criteria: all met
- Verification: all green
- Review: 0 connected issues remaining
- Build: succeeds
- App runs: confirmed
- Drive-by candidates: 2 noted, not in scope

Ready to commit and open PR.
```

---

## What ultrapilot did for this task

1. Caught the existing data model and patterns before building (explore)
2. Surfaced the scope and trade-offs in a reviewable plan
3. Built in small, verifiable steps
4. Verified with actual test output, not "looks good"
5. Found 3 connected issues the model would have missed
6. Noted 2 drive-by issues for future work
7. Looped back to verify after the reviewer's patches

Without the loop, this task would have produced a half-working dashboard with stale data, broken mobile layout, and "fixed" console errors. With the loop, it shipped ready to merge.
