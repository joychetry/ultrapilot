#!/usr/bin/env python3
"""ultrapilot runner — the orchestrator's executable.

The runner is the **control flow** for ultrapilot. It:
  1. Reads the active goal from ultrapilot_goals.py state
  2. Decides which phase to run next (state machine)
  3. Loads the *current* phase prompt only (lazy loading — not all 7)
  4. Sizes the prompt based on token budget (compact / full / minimal)
  5. Records the phase result and advances

The agent's loop is now:
  1. Call `ultrapilot_run.py next` → get a phase prompt
  2. Do the work
  3. Call `ultrapilot_run.py report --phase <name> --result <path>`
  4. Repeat

No more reading the full SKILL.md. No more loading all 7 command specs.
The runner knows what to do and tells the agent.

Dependency-free, agent-agnostic, single-file.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

# Local import — same directory
sys.path.insert(0, str(Path(__file__).parent))
import ultrapilot_goals as g  # noqa: E402

# Runner state lives in the same DB as goals
STATE_DIR = Path(os.environ.get("ULTRAPILOT_HOME", Path.home() / ".ultrapilot"))
DB_PATH = Path(os.environ.get("ULTRAPILOT_DB", STATE_DIR / "goals.db"))

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# Phase state machine
PHASE_ORDER = ["explore", "plan", "build", "verify", "review", "patch", "audit"]
PHASE_TRANSITIONS = {
    "explore": "plan",       # after explore → plan
    "plan":    "build",       # after plan → build
    "build":   "verify",      # after build → verify
    "verify":  "review",      # after verify passes → review
    "review":  "patch",       # if connected issues → patch (loops back to verify)
    "patch":   "verify",      # after patch → verify again
    "audit":   None,          # terminal — goal done or rolled back
}

# Result of each phase
PHASE_RESULTS = {}  # phase_name -> {"summary": str, "result_path": str, "passed": bool, "ts": int}


# ---------------------------------------------------------------------------
# DB schema additions (run/phase tables)
# ---------------------------------------------------------------------------

def init_runner_tables(conn) -> None:
    """Idempotent: create runner-specific tables if they don't exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS phase_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id TEXT NOT NULL,
            phase TEXT NOT NULL,
            started_at INTEGER NOT NULL,
            ended_at INTEGER,
            result_path TEXT,
            passed INTEGER,
            tokens_estimate INTEGER,
            prompt_chars INTEGER,
            notes TEXT
        );
        CREATE TABLE IF NOT EXISTS phase_artifacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id TEXT NOT NULL,
            phase TEXT NOT NULL,
            kind TEXT NOT NULL,
            value TEXT NOT NULL,
            created_at INTEGER NOT NULL
        );
    """)
    conn.commit()


# ---------------------------------------------------------------------------
# Phase prompt loading + sizing
# ---------------------------------------------------------------------------

def load_phase_prompt(phase: str, goal: Any, verbosity: str = "auto") -> dict[str, Any]:
    """Load the prompt template for a phase, sized to the token budget.

    Returns: {"prompt": <text>, "tokens_estimate": <int>, "verbosity": <compact|full|minimal>}
    """
    prompt_path = PROMPTS_DIR / f"{phase}.md"
    if not prompt_path.exists():
        # Fall back to a one-line directive
        return {
            "prompt": f"# Phase: {phase}\n\nFollow ultrapilot's standard procedure for the {phase} phase. The goal is: {goal['objective']}.",
            "tokens_estimate": 50,
            "verbosity": "minimal",
        }
    text = prompt_path.read_text()
    # Strip frontmatter
    if text.startswith("---"):
        end = text.find("---", 3)
        if end > 0:
            text = text[end + 3:].lstrip()
    # Parse the metadata we want
    tokens_estimate = 300
    front = prompt_path.read_text()
    m = re.search(r"tokens_estimate:\s*(\d+)", front)
    if m:
        tokens_estimate = int(m.group(1))
    # Decide verbosity based on token budget
    if verbosity == "auto":
        budget = goal["token_budget"] if goal["token_budget"] else 250_000
        used = goal["tokens_used"] if goal["tokens_used"] else 0
        remaining = max(0, budget - used)
        if remaining < 20_000:
            verbosity = "minimal"
        elif remaining < 100_000:
            verbosity = "compact"
        else:
            verbosity = "compact"  # default — full is rarely needed
    # Substitute placeholders
    text = _substitute(text, goal)
    # Apply verbosity
    if verbosity == "minimal":
        text = _strip_to_minimal(text)
    return {
        "prompt": text,
        "tokens_estimate": tokens_estimate,
        "verbosity": verbosity,
    }


def _substitute(text: str, goal: Any) -> str:
    """Substitute the goal and prior phase results into the prompt."""
    # We can't put the full prior result inline — too big. Just the path.
    # The agent reads the file when it needs the content.
    subs = {
        "<filled in by runner>": "(see prior phase result file path below)",
        "OBJECTIVE: <filled in by runner>": f"OBJECTIVE: {goal['objective']}",
        "WEIGHTS: <filled in by runner>": f"WEIGHTS: {goal['weights_json']}",
        "PLAN_PATH: <filled in by runner>": "PLAN_PATH: ~/.ultrapilot/runs/<goal_id>/plan-result.md",
        "REVIEW_PATH: <filled in by runner>": "REVIEW_PATH: ~/.ultrapilot/runs/<goal_id>/review-result.md",
    }
    for k, v in subs.items():
        text = text.replace(k, v)
    return text


def _strip_to_minimal(text: str) -> str:
    """For very tight budgets, strip the prompt to a one-line directive."""
    # Keep only the heading and "## Goal" section
    lines = text.splitlines()
    out = []
    in_goal = False
    for line in lines:
        if line.startswith("# Phase:"):
            out.append(line)
            out.append("")
        elif line.startswith("## Goal"):
            in_goal = True
            out.append(line)
        elif line.startswith("##"):
            in_goal = False
        elif in_goal and line.strip():
            out.append(line)
    out.append("")
    out.append("Budget is tight. Be concise. Use the standard output format. Skip explanations.")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------

def next_phase(goal: Any) -> str | None:
    """Decide which phase to run next based on the goal's current state and prior results."""
    # The goal's `metadata` JSON stores which phases have been run and their results
    meta = json.loads(goal["metadata_json"] or "{}")
    phases = meta.get("phases", {})
    # If we have a saved "next phase" hint, use it
    if "next_phase" in meta:
        return meta["next_phase"]
    # Otherwise, find the first phase not in the completed list
    for p in PHASE_ORDER:
        if p not in phases:
            # Special case: skip explore if greenfield
            if p == "explore" and meta.get("greenfield"):
                continue
            # Special case: skip review if user said ship-it
            if p == "review" and goal["profile"] == "ship-it":
                continue
            return p
    return None


def record_phase(
    goal_id: str,
    phase: str,
    passed: bool,
    result_path: str | None = None,
    notes: str | None = None,
) -> None:
    """Mark a phase as completed and update the goal's next-phase hint."""
    with g.sqlite_connect() as conn:
        init_runner_tables(conn)
        # End the latest phase_run
        conn.execute(
            """
            UPDATE phase_runs SET ended_at = ?, result_path = ?, passed = ?
            WHERE goal_id = ? AND phase = ? AND ended_at IS NULL
            ORDER BY started_at DESC LIMIT 1
            """,
            (g.now(), result_path, 1 if passed else 0, goal_id, phase),
        )
        # Read the goal's metadata, update, write back
        row = conn.execute("SELECT metadata_json FROM goals WHERE id = ?", (goal_id,)).fetchone()
        if not row:
            return
        meta = json.loads(row["metadata_json"] or "{}")
        if "phases" not in meta:
            meta["phases"] = {}
        meta["phases"][phase] = {
            "passed": passed,
            "result_path": result_path,
            "ended_at": g.now(),
        }
        # Decide next phase
        if passed:
            if phase == "review":
                # Review passed → go to audit
                meta["next_phase"] = "audit"
            else:
                meta["next_phase"] = PHASE_TRANSITIONS.get(phase, "audit")
        else:
            # Phase failed → loop back appropriately
            if phase == "verify":
                meta["next_phase"] = "build"  # go fix the bugs
            elif phase == "review":
                meta["next_phase"] = "patch"
            elif phase == "patch":
                meta["next_phase"] = "verify"
            elif phase == "audit":
                # Audit failed — block on blockers, return to relevant phase
                # Default: build (the most common fix)
                meta["next_phase"] = "build"
            else:
                meta["next_phase"] = phase  # retry
        # Reset the "next phase" if the goal was abandoned
        if meta.get("abandoned"):
            meta["next_phase"] = None
        conn.execute(
            "UPDATE goals SET metadata_json = ? WHERE id = ?",
            (json.dumps(meta), goal_id),
        )
        # Audit event
        g.event(conn, "", f"phase_{phase}", f"passed={passed} next={meta.get('next_phase')}", goal_id)
        conn.commit()


def start_phase(goal_id: str, phase: str, prompt_chars: int = 0, tokens_estimate: int = 0) -> None:
    """Open a new phase_run record."""
    with g.sqlite_connect() as conn:
        init_runner_tables(conn)
        conn.execute(
            """
            INSERT INTO phase_runs (goal_id, phase, started_at, tokens_estimate, prompt_chars)
            VALUES (?, ?, ?, ?, ?)
            """,
            (goal_id, phase, g.now(), tokens_estimate, prompt_chars),
        )
        conn.commit()


# ---------------------------------------------------------------------------
# Rendered outputs (what the agent / user sees)
# ---------------------------------------------------------------------------

def render_next(goal: Any, phase: str, prompt_data: dict[str, Any]) -> str:
    """Render the next-phase response."""
    output = [
        f"# ultrapilot — next phase: {phase}",
        "",
        f"Goal: {goal['objective']}",
        f"Profile: {goal['profile']}",
        f"Verbosity: {prompt_data['verbosity']}",
        f"Prompt tokens (estimate): {prompt_data['tokens_estimate']}",
        f"Goal budget remaining: {g.fmt_tokens(goal['token_budget'] - goal['tokens_used']) if goal['token_budget'] else 'none'}",
        "",
        "---",
        "",
        prompt_data["prompt"],
        "",
        "---",
        "",
        f"## When done, report back:",
        f"",
        f"```bash",
        f"python3 ~/.hermes/skills/ultrapilot/scripts/ultrapilot_run.py report \\",
        f"  --phase {phase} \\",
        f"  --result /tmp/{phase}-result.md \\",
        f"  --passed",
        f"```",
        "",
        f"Or with --failed if the phase did not pass. The runner will then dispatch the next phase automatically.",
    ]
    return "\n".join(output)


def render_status(goal: Any) -> str:
    """Render the current run state — which phases are done, what's next."""
    meta = json.loads(goal["metadata_json"] or "{}")
    phases = meta.get("phases", {})
    next_p = meta.get("next_phase") or "complete"
    lines = [
        f"# ultrapilot run status",
        "",
        f"Goal: {goal['objective']}",
        f"Profile: {goal['profile']}",
        f"Status: {goal['status']}",
        "",
        f"## Phase progress",
        "",
    ]
    for p in PHASE_ORDER:
        if p in phases:
            r = phases[p]
            mark = "✅" if r["passed"] else "❌"
            lines.append(f"- {mark} {p} — passed={r['passed']}, result={r.get('result_path', 'n/a')}")
        elif p == next_p:
            lines.append(f"- ⏳ {p} — NEXT")
        else:
            lines.append(f"- ⏸ {p} — pending")
    lines.append("")
    lines.append(f"Next phase: {next_p}")
    lines.append(f"Tokens used: {g.fmt_tokens(goal['tokens_used'])} / {g.fmt_tokens(goal['token_budget']) if goal['token_budget'] else 'none'}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="ultrapilot runner — single-command orchestrator. Use `next` to get the current phase prompt, then `report` to advance."
    )
    sub = parser.add_subparsers(dest="cmd")

    # `next` — the main entry point
    p_next = sub.add_parser("next", help="Get the current phase prompt. This is the only command you call repeatedly.")
    p_next.add_argument("--verbosity", default="auto", choices=["auto", "compact", "full", "minimal"])
    p_next.add_argument("--phase", default=None, help="Override the auto-selected phase")
    p_next.add_argument("--greenfield", action="store_true", help="Mark as greenfield (skip explore)")

    # `report` — the agent calls this when a phase is done
    p_report = sub.add_parser("report", help="Record a phase result and advance to the next phase")
    p_report.add_argument("--phase", required=True, choices=PHASE_ORDER)
    p_report.add_argument("--result", required=True, help="Path to the result file the agent produced")
    p_report.add_argument("--passed", action="store_true")
    p_report.add_argument("--failed", dest="passed", action="store_false")
    p_report.set_defaults(passed=True)
    p_report.add_argument("--notes", default=None)

    # `status` — show the current run state
    sub.add_parser("status", help="Show current run state and which phases are done")

    # `goto` — jump to a specific phase (used by companion commands)
    p_goto = sub.add_parser("goto", help="Set the next phase (overrides the state machine)")
    p_goto.add_argument("phase", choices=PHASE_ORDER)

    # `reset` — clear all phase progress (start over)
    sub.add_parser("reset", help="Clear all phase progress for the current goal")

    # `compact` — get the compact version of a specific phase prompt (for debugging)
    p_compact = sub.add_parser("compact", help="Render a phase prompt in compact form")
    p_compact.add_argument("phase", choices=PHASE_ORDER)

    args = parser.parse_args(argv)

    try:
        if args.cmd == "next":
            with g.sqlite_connect() as conn:
                init_runner_tables(conn)
                goal = g.find_goal(conn, g.candidate_session_ids())
                if not goal:
                    print("No goal is set. Use `ultrapilot_goals.py set [task]` first.")
                    return 1
                # Optionally mark as greenfield before selecting phase
                if args.greenfield:
                    meta = json.loads(goal["metadata_json"] or "{}")
                    meta["greenfield"] = True
                    if "next_phase" not in meta:
                        meta["next_phase"] = "plan"
                    conn.execute(
                        "UPDATE goals SET metadata_json = ? WHERE id = ?",
                        (json.dumps(meta), goal["id"]),
                    )
                    conn.commit()
                    goal = g.find_goal(conn, g.candidate_session_ids())  # re-read
                phase = args.phase or next_phase(goal)
                if not phase:
                    print("# ultrapilot run complete\n\nAll phases done. Run `complete` to mark the goal done.")
                    return 0
                prompt_data = load_phase_prompt(phase, goal, args.verbosity)
                start_phase(goal["id"], phase, len(prompt_data["prompt"]), prompt_data["tokens_estimate"])
                print(render_next(goal, phase, prompt_data))
        elif args.cmd == "report":
            if not os.path.exists(args.result):
                print(f"Result file not found: {args.result}", file=sys.stderr)
                return 1
            with g.sqlite_connect() as conn:
                init_runner_tables(conn)
                goal = g.find_goal(conn, g.candidate_session_ids())
                if not goal:
                    print("No goal is set.", file=sys.stderr)
                    return 1
                record_phase(goal["id"], args.phase, args.passed, args.result, args.notes)
                # Re-read goal to get the updated next_phase
                goal = g.find_goal(conn, g.candidate_session_ids())
                # Also record this as a run (for token tracking)
                tokens = 0  # agent should pass this via --tokens; we don't have it here
                conn.execute(
                    """
                    INSERT INTO runs (goal_id, session_id, started_at, ended_at, tokens_used, turns_used, artifacts_json, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (goal["id"], g.session_id(), g.now(), g.now(), 0, 1, json.dumps([args.result]), f"phase={args.phase} passed={args.passed}"),
                )
                conn.commit()
                meta = json.loads(goal["metadata_json"] or "{}")
                next_p = meta.get("next_phase", "complete")
                print(f"Phase {args.phase} recorded: passed={args.passed}")
                print(f"Next phase: {next_p}")
                if next_p == "audit":
                    print()
                    print("Run the completion audit before marking the goal done:")
                    print("  ultrapilot_run.py next")
        elif args.cmd == "status":
            with g.sqlite_connect() as conn:
                init_runner_tables(conn)
                goal = g.find_goal(conn, g.candidate_session_ids())
                if not goal:
                    print("No goal is set.")
                    return 1
                print(render_status(goal))
        elif args.cmd == "goto":
            with g.sqlite_connect() as conn:
                init_runner_tables(conn)
                goal = g.find_goal(conn, g.candidate_session_ids())
                if not goal:
                    print("No goal is set.", file=sys.stderr)
                    return 1
                meta = json.loads(goal["metadata_json"] or "{}")
                meta["next_phase"] = args.phase
                conn.execute(
                    "UPDATE goals SET metadata_json = ? WHERE id = ?",
                    (json.dumps(meta), goal["id"]),
                )
                conn.commit()
                print(f"Next phase set to: {args.phase}")
        elif args.cmd == "reset":
            with g.sqlite_connect() as conn:
                init_runner_tables(conn)
                goal = g.find_goal(conn, g.candidate_session_ids())
                if not goal:
                    print("No goal is set.", file=sys.stderr)
                    return 1
                meta = json.loads(goal["metadata_json"] or "{}")
                meta["phases"] = {}
                meta.pop("next_phase", None)
                conn.execute(
                    "UPDATE goals SET metadata_json = ? WHERE id = ?",
                    (json.dumps(meta), goal["id"]),
                )
                conn.commit()
                print("Phase progress reset. Next call to `next` will return the first phase.")
        elif args.cmd == "compact":
            with g.sqlite_connect() as conn:
                init_runner_tables(conn)
                goal = g.find_goal(conn, g.candidate_session_ids())
                if not goal:
                    print("No goal is set.", file=sys.stderr)
                    return 1
                prompt_data = load_phase_prompt(args.phase, goal, "compact")
                print(prompt_data["prompt"])
        else:
            parser.print_help()
            return 2
    except Exception as exc:
        print(f"ultrapilot:run error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
