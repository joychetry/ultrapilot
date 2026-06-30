---
name: adapter-prompts
description: "Capability-class prompt adjustments for ultrapilot. Use when the default loop produces quirk-class issues. Each adapter is a behavior pattern, not a model name — ultrapilot remains model-agnostic."
type: reference
---

# Capability-Class Adapters

`/ultrapilot` is model-agnostic by default. The default loop works on every capable model. But some models exhibit behavior patterns that need small adjustments. This document groups those adjustments by **capability class** (the kind of behavior to look for) rather than by model name, so the main skill stays clean.

**Rule of thumb:** if a prompt adjustment is needed for one *capability class*, it goes here, not in `SKILL.md`. The main spec stays capability-class-free.

**How to use this doc:** run `/ultrapilot` on a representative task with the model in question. If you see a behavior pattern that matches one of the classes below and the default loop fails or underperforms on it, copy the relevant adapter into the orchestrator's prompt. The capability class is what matters — the model name does not.

## Class: text-only (no image input)

**Detection:** the model rejects messages containing image content parts (data URIs or URLs) with a 4xx error like "image content not supported" or "vision is not supported". Some models do not advertise this in their capability metadata; you have to discover it at runtime.

**Adapter:** in the build phase for UI work, add:

```
For visual references: if a design image is provided, treat it as a description.
If you cannot process the image directly, use a vision-capable model to convert
it to text instructions first, then proceed with the text.
```

## Class: over-explainer (fluff-prone)

**Detection:** the model produces long preambles, philosophical lectures, or unsolicited advice before getting to the work. Common in chat-tuned chat models. Triggered when the model's default response includes "Great question!" or "I'd be happy to help" or extensive throat-clearing.

**Adapter:** prepend to the explore and plan phases:

```
[Discipline layer — activated]
Before responding, assess task complexity. If deep planning is needed, plan
properly. If not, do the small edit and move on. Cut fluff. Commit to the
implementation path. Do not over-explain.
```

The model-agnostic form of the discipline layer lives in `commands/_discipline.md` and is gated by a task-complexity classifier so it doesn't activate on trivial edits.

## Class: long-horizon drift

**Detection:** the model loses focus or context across a very long session. The plan looks good at step 1 but by step 7 the model is implementing something different. Common in chat models with long but lossy attention.

**Adapter:** use the `/ultrapilot:steer` command more aggressively. If the plan is sound and the model is still drifting after 3 turns, reset to the last good checkpoint.

**Adapter (planning format):** in the plan phase, ask for the plan in a specific format that resists drift:

```
Format the plan as: Goal (1 sentence), Acceptance Criteria (checkboxes),
Files to Change (bullets), Steps (numbered, max 8), Out of Scope (bullets).
```

## Class: plan-buried actionable items

**Detection:** the model produces verbose plans where the actual implementation steps are buried under discussion, alternatives, and trade-off analysis. Common in models tuned for thoroughness.

**Adapter:** same as above — the "Goal / Acceptance Criteria / Files / Steps / Out of Scope" format forces the model to surface the actionable items.

## Class: self-verification overconfidence

**Detection:** the model reports that tests pass or the build succeeded without actually running the commands. Particularly common in code-tuned models. The classic symptom is "it should work" or "this should pass" instead of real command output.

**Adapter:** in the verify phase, never let the model self-report. Force actual command output:

```
Run the following command and paste the FULL output. Do not summarize, do not
infer, do not say "it should pass."
```

## Class: hallucinated file paths

**Detection:** the model lists file paths in the plan or architecture map that don't exist in the repository. Common in models with weak filesystem grounding, especially on large codebases.

**Adapter:** in the explore phase, require the model to verify file paths before listing them:

```
For every file path you cite, run `ls` or `find` to confirm it exists.
Do not list paths you have not verified.
```

## Class: needs explicit reasoning chains

**Detection:** the model produces a plan that looks plausible but skips intermediate steps; on heavy work it benefits from being told to think step-by-step. Common in models that default to fast/terse mode.

**Adapter:** in the plan phase, prepend:

```
Think through this plan step by step. For each step, state: what changes,
what file, what test, what risk.
```

## Class: weak UI polish

**Detection:** the model produces functionally correct UI but the visual quality is rough — inconsistent spacing, poor contrast, no attention to typography, generic-looking components.

**Adapter:** in the build phase for UI work, explicitly load the negative design constraints from SKILL.md Appendix B. Do not skip them for "small" UI changes.

## Class: small context / local model

**Detection:** the model has a 32K or smaller context window, or shows degraded performance past a certain conversation length. Common in local models (Ollama, LM Studio, etc.) and smaller hosted models.

**Adapter:** bound the ultrapilot run tightly:

```
/ultrapilot [task] — stop after 10 turns or when the plan is complete
```

**Adapter (plan length):** in the plan phase, enforce a max of 5 steps. If the task needs more, break it into multiple ultrapilot runs.

## Adding a new capability-class adapter

1. Identify a specific behavior pattern that affects ultrapilot's loop.
2. Test that the default loop fails on the pattern.
3. Add a minimal adapter (one or two prompt adjustments).
4. Document in this file under a new class heading.
5. PR with a transcript showing the before/after.

If the pattern is severe (model cannot follow the loop at all), document it in the "Known Limitations" section below instead of trying to patch the loop.

## Known Limitations

These capability classes are not currently recommended for full ultrapilot use:

- **Tiny context** — models with < 32K context windows
- **No reliable tool use** — models that hallucinate tool calls or ignore tool results
- **No multi-turn** — models that do not support multi-turn sessions

For these, use ultrapilot's plan and review commands as standalone prompts. Skip the orchestrator.
