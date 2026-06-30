---
name: example-goal-system
description: "Worked example — multi-dimensional goal scoring across three different task profiles (default, secure, ship-it), showing how the same code change scores differently depending on which profile is active."
type: example
---

# Example 06: Multi-Dimensional Goal System

Three scenarios showing the new v2 goal system in action. Each scenario involves the same code change — adding a sponsorship dashboard to an existing app — but with a different goal profile, the score changes dramatically.

The code change (sponsorship dashboard) involves:
- 12 new files
- ~1,800 lines of code
- Touches auth (Supabase RLS)
- No payment processing
- New UI with mobile considerations
- 13 new tests

The aggregate score depends on what matters to the user.

---

## Scenario 1: Default profile

**Invocation:**
```
/ultrapilot build a sponsorship dashboard
```

**Active profile (printed to transcript):**
```
[ultrapilot:goals] Active profile: default
[ultrapilot:goals] Weights: correctness=30, reliability=20, efficiency=10, safety=25, ux=10, cost=5
[ultrapilot:goals] Floors: safety≥60, correctness≥70
[ultrapilot:goals] Completion: aggregate≥80, no dim<50, no dim<floor
```

**Per-dimension scoring after the run:**

| Dimension | Score | How measured | Notes |
|-----------|-------|--------------|-------|
| Correctness | 95/100 | All 14 acceptance criteria met. All 13 new tests pass. Review found 0 connected issues. | 5 points off because one drive-by candidate (existing form has stale data bug) was noted but not fixed. |
| Reliability | 78/100 | Edge cases tested: empty list (✓), network failure (✓), 0 deals (✓). Did not test: concurrent edits by two users, slow network > 5s. | Could not test concurrency in the test environment. |
| Efficiency | 85/100 | Build: 4.2s. Test suite: 12.4s. Initial dashboard load: 380ms. N+1 query caught in review and fixed. | Good baseline. Not over-optimized, but no obvious waste. |
| Safety | 82/100 | RLS policies correct. Auth required. No secrets in code. Console: 0 errors. | Lost points because the existing pattern for CSRF protection on Server Actions was not explicitly verified by the review. |
| UX | 88/100 | Mobile responsive (375px, 768px, 1440px). Empty/loading/error states all present. Accessible (keyboard nav works, color contrast passes). | No animation/transition feedback. |
| Cost | 92/100 | 8 turns. ~32K tokens. | Discipline layer was not loaded (default profile, single-feature task). |

**Aggregate calculation:**
```
aggregate = (95*30 + 78*20 + 85*10 + 82*25 + 88*10 + 92*5) / 100
         = (2850 + 1560 + 850 + 2050 + 880 + 460) / 100
         = 8650 / 100
         = 86.5%
```

**Floor checks:**
- safety=82 ≥ 60 ✓
- correctness=95 ≥ 70 ✓
- All dimensions ≥ 50 ✓

**Result:** **COMPLETE** (86.5% ≥ 80% threshold, all floors satisfied)

---

## Scenario 2: Secure profile

**Invocation:**
```
/ultrapilot --profile secure build the sponsorship dashboard with payment processing
```

**Profile switch — the orchestrator detects "payment processing" and suggests:**

```
[ultrapilot:goals] Detected: payment processing keyword
[ultrapilot:goals] Recommended profile: secure (safety weight: 25% → 45%)
[ultrapilot:goals] Auto-switching to: secure
```

**Active profile (printed to transcript):**
```
[ultrapilot:goals] Active profile: secure
[ultrapilot:goals] Weights: correctness=25, reliability=15, efficiency=5, safety=45, ux=5, cost=5
[ultrapilot:goals] Floors: safety≥60, correctness≥70
[ultrapilot:goals] Completion: aggregate≥80, no dim<50, no dim<floor
```

**Per-dimension scoring after the run (same code, different weights):**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Correctness | 95/100 | Same. |
| Reliability | 78/100 | Same. |
| Efficiency | 85/100 | Same. |
| Safety | 82/100 | Same — but now weighted 45% instead of 25% |
| UX | 88/100 | Same. |
| Cost | 92/100 | Same. |

**Aggregate calculation:**
```
aggregate = (95*25 + 78*15 + 85*5 + 82*45 + 88*5 + 92*5) / 100
         = (2375 + 1170 + 425 + 3690 + 440 + 460) / 100
         = 8560 / 100
         = 85.6%
```

**Aggregate is still above 80%, but the orchestrator is now stricter about safety:**

- safety=82 still meets the floor (≥60)
- But the review would have demanded **more** safety scrutiny if it knew the profile was `secure`. In a real run with the `secure` profile active, the reviewer would have:
  - Run an explicit OWASP top-10 check
  - Verified RLS policies for every table
  - Checked the payment processing flow against PCI-DSS basics
  - Run a secret-scan on the diff
  - Tested for IDOR (insecure direct object reference) on every endpoint

**Result with realistic `secure` profile scoring:**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Correctness | 95/100 | Same. |
| Reliability | 78/100 | Same. |
| Efficiency | 85/100 | Same. |
| Safety | 95/100 | **Higher** because reviewer ran extra security checks. The dashboard passes. |
| UX | 88/100 | Same. |
| Cost | 92/100 | Same. |

**Aggregate calculation:**
```
aggregate = (95*25 + 78*15 + 85*5 + 95*45 + 88*5 + 92*5) / 100
         = (2375 + 1170 + 425 + 4275 + 440 + 460) / 100
         = 9145 / 100
         = 91.5%
```

**Result:** **COMPLETE** (91.5% ≥ 80%, all floors satisfied, with stronger safety signal)

The key insight: **the same code scores higher under `secure` because the system checks more rigorously.** Under the default profile, the safety score was 82 because the reviewer was less thorough. Under the secure profile, the same code gets a 95 because the review was more thorough — and the same code is, in fact, secure.

---

## Scenario 3: Ship-it profile

**Invocation:**
```
/ultrapilot --profile ship-it hotfix the production bug where sponsorship dashboard shows 500 error
```

**Active profile (printed to transcript):**
```
[ultrapilot:goals] Active profile: ship-it
[ultrapilot:goals] Weights: correctness=50, reliability=30, efficiency=5, safety=10, ux=5, cost=0
[ultrapilot:goals] Floors: safety≥60, correctness≥70
[ultrapilot:goals] Completion: aggregate≥80, no dim<50, no dim<floor
```

**Note:** the floor for safety stays at 60% (non-negotiable) even in `ship-it` mode. Cost is 0% (irrelevant for hotfixes). UX is reduced. The user wants the bug fixed fast.

**Per-dimension scoring after the run (focused hotfix, not full feature):**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Correctness | 100/100 | The 500 error is fixed. Targeted patch, no scope creep. |
| Reliability | 90/100 | Tested the fix path. Did not test all edge cases (skipped because ship-it). |
| Efficiency | 95/100 | Patch is minimal, no perf regression. |
| Safety | 75/100 | Floor (60%) met. The fix is safe (just a better error message + retry), but no extra security review was run. |
| UX | 80/100 | The 500 error becomes a friendly error message. No other UX work. |
| Cost | 100/100 | Hotfix completed in 3 turns. ~8K tokens. Discipline layer skipped. |

**Aggregate calculation:**
```
aggregate = (100*50 + 90*30 + 95*5 + 75*10 + 80*5 + 100*0) / 100
         = (5000 + 2700 + 475 + 750 + 400 + 0) / 100
         = 9325 / 100
         = 93.25%
```

**Result:** **COMPLETE** (93.25% ≥ 80%, all floors satisfied)

**The ship-it profile allowed the orchestrator to ship faster** because it lowered the weight on dimensions that would have required extra review (UX, Efficiency, Cost). It kept the floor on safety (60%) and correctness (70%) so the fix still has to be right and safe.

Without the profile system, the user would have had to manually decide which dimensions to deprioritize. The profile makes that decision explicit and reproducible.

---

## Comparison summary

| Scenario | Profile | Aggregate | Turns | Key trade-off |
|----------|---------|-----------|-------|---------------|
| 1. Default | default | 86.5% | 8 | Balanced. The code shipped with a 78% reliability score (some untested edge cases). |
| 2. Secure | secure | 91.5% | 12 | More review rigor. Safety score went from 82 to 95 because the review was deeper. |
| 3. Ship-it | ship-it | 93.25% | 3 | Hotfix shipped in 3 turns. UX and cost deliberately deprioritized. |

**Same code change, different profiles, different outcomes.** The profile is not changing the code — it's changing what gets measured and how strictly.

## What the orchestrator reports

After a run, the orchestrator outputs a scorecard:

```
[ultrapilot:goals] Run complete
[ultrapilot:goals] Profile: default
[ultrapilot:goals] Scorecard:
  - Correctness:  95/100  (weight 30%)  contribution: 28.5
  - Reliability:  78/100  (weight 20%)  contribution: 15.6
  - Efficiency:   85/100  (weight 10%)  contribution:  8.5
  - Safety:       82/100  (weight 25%)  contribution: 20.5
  - UX:           88/100  (weight 10%)  contribution:  8.8
  - Cost:         92/100  (weight  5%)  contribution:  4.6
  - Aggregate:    86.5%
[ultrapilot:goals] Floors: all satisfied (safety 82≥60, correctness 95≥70)
[ultrapilot:goals] Result: COMPLETE
```

The scorecard is the primary signal the user sees at the end of a run. It is more informative than "task done" or "task not done."

## What the user can do with the scorecard

- **Accept the run** if the aggregate and floors are met.
- **Reject the run** if a dimension is too low. The orchestrator logs the rejection and re-enters the patch phase targeting the weak dimension.
- **Re-run with a different profile** if the scorecard shows the wrong dimensions were weighted for this task. Example: "Re-run with `--profile secure` and add 2 more turns for the security review."
- **Re-run with `--trials 3`** if a dimension scored by LLM-as-judge (UX, edge case reliability) is borderline. Multiple trials give a more stable signal.

The goal system is the orchestrator's way of saying "we measured this run against 6 dimensions, here's the report, and here's the path forward."
