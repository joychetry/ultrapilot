---
name: example-fix-bug
description: "Worked example — fixing a mobile-specific bug with /ultrapilot using mid-flight steering."
type: example
---

# Example 03: Fix a Mobile Bug

**Task type:** Targeted bug fix with a specific reproduction.
**User prompt:** `/ultrapilot fix the mobile pipeline layout — columns overflow horizontally on viewports under 768px`
**Target stack:** React + Tailwind CSS

---

## Step 1: Explore (quick — focused task)

**Architecture map (focused):**

```
The pipeline view is at src/views/Pipeline.tsx
Uses a CSS grid with 5 fixed-width columns (250px each)
No responsive breakpoints applied
Uses Tailwind 3.4, no custom CSS

The columns are: Lead, Contacted, Negotiation, Active, Closed
Each column header is in <PipelineColumn /> at src/components/PipelineColumn.tsx
Cards are <DealCard /> in src/components/DealCard.tsx
```

## Step 2: Plan

```markdown
# Plan: Fix Mobile Pipeline Overflow

## Goal
Make the pipeline view usable on viewports under 768px. No more horizontal 
overflow on the columns.

## Acceptance Criteria
- [ ] On viewports < 768px, columns do not overflow horizontally
- [ ] On viewports >= 768px, layout is unchanged (5 columns side by side)
- [ ] Each column is still scrollable independently
- [ ] Cards within each column resize appropriately
- [ ] No new console errors

## Files to Change
- src/views/Pipeline.tsx — switch from fixed grid to responsive grid
- src/components/PipelineColumn.tsx — add mobile-friendly sizing

## Files to Create
None (no new components needed)

## Files to NOT Change
- src/components/DealCard.tsx (works fine within its column)

## Steps
1. Add responsive breakpoints to Pipeline.tsx grid
2. Make columns scroll vertically on mobile, horizontally on desktop
3. Test on 375px, 768px, 1440px viewports

## Assumptions
- "Mobile" means < 768px (Tailwind md breakpoint)
- Horizontal scroll within a column is acceptable
- We don't need a card-stack layout on mobile (columns are still the structure)

## Out of Scope
- Touch gesture support (pinch to zoom, swipe between columns)
- Card-level responsive behavior
- Tablet-specific layout (768-1024px)

## Verification
- pnpm test exits 0
- pnpm typecheck exits 0
- Manual: at 375px, columns don't overflow
- Manual: at 768px, layout is unchanged
- Manual: at 1440px, layout is unchanged
- Manual: scrolling within a column works at all sizes
```

## Step 3: Build

**First attempt — orchestrator steers:**

```
Step 1: Changed grid to use grid-cols-1 md:grid-cols-5.

Orchestrator: STOP. The plan said "columns are still the structure" — 
that means we should not collapse to a single column. The issue is overflow, 
not the column structure. Re-plan.
```

**Re-planning the step:**

```
Re-plan: Keep 5 columns at all viewport sizes. Add horizontal scroll 
on the parent container when columns would overflow. Each column has 
a min-width that matches its content (no fixed 250px).
```

**Second attempt:**

```
Step 1: Changed Pipeline.tsx to use:
        - Outer container: overflow-x-auto
        - Inner grid: grid-flow-col, auto-cols-[minmax(280px,1fr)]
        - md: keeps the existing inline-scroll behavior
        
        pnpm test — 23 passed, 0 failed
        pnpm typecheck — 0 errors
        
Step 2: Adjusted PipelineColumn.tsx to remove fixed 250px width.
        pnpm test — 23 passed, 0 failed

Step 3: Manual verification.
        ✓ At 375px: outer container scrolls horizontally, no overflow of the page itself
        ✓ At 768px: layout is unchanged (5 columns visible)
        ✓ At 1440px: layout is unchanged
        ✓ Scrolling within each column works at all sizes
        ✓ Dev tools console: 0 errors
```

## Step 4: Review

```
Reviewing the diff (2 files changed, +24/-18 lines).

Issues found (connected):
1. The auto-cols-[minmax(280px,1fr)] was using 1fr at large viewports — 
   on 1440px, this stretched the columns to fill 288px each, which 
   looked wrong. Changed to fixed sizing on md+.

Issues found (drive-by):
- The header in PipelineColumn has a small alignment issue at 320px. 
  Not blocking, noted for follow-up.

Connected issues: 1 found, 1 fixed.

Re-verification:
✓ At 1440px: columns are now properly sized (not stretched)
✓ At 375px: still scrolls horizontally as expected
✓ All other viewports unchanged
```

## Step 5: Completion

```
Task: Fix mobile pipeline overflow

Status: COMPLETE
- Plan acceptance criteria: all met
- Verification: all green
- Review: 0 connected issues remaining
- Build: succeeds
- Drive-by candidates: 1 noted, not in scope

Mid-flight steering: 1 (the first attempt collapsed to single column, 
which violated the plan's "columns are still the structure" assumption).
```

---

## What ultrapilot did for this task

1. Quickly mapped the relevant files (focused explore, not full architecture map)
2. Wrote a tight plan that explicitly preserved the 5-column structure
3. **Caught a first-attempt mistake that violated the plan** — the model tried to collapse to 1 column instead of fixing the overflow. The orchestrator's steering phase caught this before it shipped.
4. Re-planned the step, completed it correctly
5. Found 1 more connected issue (column stretching on large viewports)
6. Total: 2 files, 1 steering intervention, 1 review patch, shipped correct on first merge

Without the loop, this would have shipped as "single column on mobile" which violates the user's actual need (they want to compare columns side by side even on mobile). The plan's "columns are still the structure" assumption is what caught this. Without a plan, the model would not have known to preserve the structure.
