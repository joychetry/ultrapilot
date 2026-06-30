---
name: adapter-prompts
description: "Model-specific prompt adjustments for ultrapilot. Use when the default loop produces model-quirk issues. Each adapter is isolated so the core remains model-agnostic."
type: reference
---

# Adapter Prompts

`/ultrapilot` is model-agnostic by default. The default loop works on every capable model. But some models have quirks that need small adjustments. This document collects those adjustments in one place so the main skill stays clean.

**Rule of thumb:** if a prompt adjustment is needed for one model only, it goes here, not in `SKILL.md`. The main spec stays model-agnostic.

## GLM 5.2 (Zhipu) — Zcode

**Quirk:** GLM 5.2 benefits from a discipline layer ("King Mode" in the source video). Without it, the model can over-explain or chase directions the user did not ask for.

**Adapter:** prepend this to the explore and plan phases:

```
[Discipline layer — activated]
Before responding, assess task complexity. If deep planning is needed, plan properly. If not, do the small edit and move on. Cut fluff. Commit to the implementation path. Do not over-explain.
```

**Quirk:** GLM 5.2 is text-only. For visual design references, use a vision model separately and feed GLM the design instructions as text.

**Adapter:** in the build phase for UI work, add:

```
For visual references: if a design image is provided, treat it as a description. Use a vision-capable model to convert it to text instructions if needed.
```

## Claude (Sonnet, Opus) — Claude Code

**Quirk:** Claude is strong on long-horizon tasks but can lose focus across very long sessions.

**Adapter:** use `/ultrapilot:steer` more aggressively. If the plan is sound and the model is still drifting after 3 turns, reset to the last good checkpoint.

**Quirk:** Claude sometimes produces verbose plans that bury the actionable items.

**Adapter:** in the plan phase, ask for the plan in a specific format:

```
Format the plan as: Goal (1 sentence), Acceptance Criteria (checkboxes), Files to Change (bullets), Steps (numbered, max 8), Out of Scope (bullets).
```

## GPT-Codex — Codex CLI

**Quirk:** Codex is strong on code generation but can be overconfident in self-verification.

**Adapter:** in the verify phase, never let Codex self-report test results. Force actual command output:

```
Run the following command and paste the FULL output. Do not summarize, do not infer, do not say "it should pass."
```

**Quirk:** Codex occasionally hallucinates file paths when the codebase is large.

**Adapter:** in the explore phase, require the model to use `ls` or `find` to verify file paths before listing them in the architecture map.

## Gemini (Pro) — Gemini CLI

**Quirk:** Gemini benefits from explicit reasoning chains for complex plans.

**Adapter:** in the plan phase, prepend:

```
Think through this plan step by step. For each step, state: what changes, what file, what test, what risk.
```

**Quirk:** Gemini's UI rendering is sometimes less polished than Claude's.

**Adapter:** in the build phase for UI work, explicitly load the negative design constraints from SKILL.md Appendix B. Do not skip them for "small" UI changes.

## Local models (Ollama, LM Studio, etc.)

**Quirk:** Local models have varying context windows and capability ceilings.

**Adapter:** bound the ultrapilot run tightly. Recommend:

```
/ultrapilot [task] — stop after 10 turns or when the plan is complete
```

**Quirk:** Local models often struggle with very long plans.

**Adapter:** in the plan phase, enforce a max of 5 steps. If the task needs more, break it into multiple ultrapilot runs.

## Adding a new adapter

1. Identify a specific model quirk that affects ultrapilot's loop.
2. Test that the default loop fails on the quirk.
3. Add a minimal adapter (one or two prompt adjustments).
4. Document in this file.
5. PR with a transcript showing the before/after.

If the quirk is severe (model cannot follow the loop at all), document it in the "Known Limitations" section below instead of trying to patch the loop.

## Known Limitations

These models are not currently recommended for full ultrapilot use:

- Models with < 32K context windows
- Models without reliable tool use
- Models that do not support multi-turn sessions

For these, use ultrapilot's plan and review commands as standalone prompts. Skip the orchestrator.
