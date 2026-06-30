---
phase: explore
verbosity: compact
tokens_estimate: 200
---

# Phase: Explore

## Goal
Produce a tight architecture map of the current project. Do not edit any files.

## What to do
1. Read the project structure (`ls`, `find`, or read tools).
2. Identify: framework, language, package manager, test command, styling system, routing, database, auth layer, existing patterns.
3. Output a structured map (see Output Format below).

## Output Format

```
ARCHITECTURE_MAP
framework: <name + version>
language: <name + version>
package_manager: <name> (lockfile: <yes/no>)
test_command: <command>
test_location: <path pattern>
styling: <name>
routing: <pattern>
database: <name>
auth_layer: <name>
patterns:
  - state: <pattern>
  - data_fetching: <pattern>
  - error_handling: <pattern>
safest_extension_point: <short description>
```

## Rules
- Read-only. No file edits.
- If project is greenfield (empty / no existing code), skip this phase and return `GREENFIELD: true`.
- Be concise. The map is consumed by the next phase, not by a human.

## Next step
When done, call: `ultrapilot_run.py report --phase explore --result /tmp/explore-result.txt`
