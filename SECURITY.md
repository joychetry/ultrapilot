# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.0.x   | :white_check_mark: |

## Runtime Model

ultrapilot is a **skill that runs locally** in your coding agent. It is not a service, server, or hosted product.

- All state is stored in `~/.ultrapilot/goals.db` (a SQLite file on your local machine)
- All scripts (`scripts/ultrapilot_goals.py`, `scripts/ultrapilot_run.py`) run as subprocesses of your agent
- No network calls are made by ultrapilot itself
- The skill reads files in your project, the goal DB, and the agent's environment

## Threat Model

ultrapilot's threat model is:

1. **Prompt injection via the goal text** — mitigated by the `<objective>` wrapper in `commands/goals.md` and the `ultrapilot_goals.py suggest` prompt renderer. The goal text is treated as untrusted task context, not as instructions.

2. **State injection via DB tampering** — mitigated by the source-attribution field (`agent` column) and the fact that ultrapilot's own scripts are the only writers. A malicious actor with file-system access can tamper with the DB; that is the same threat as any local file.

3. **Runaway resource usage** — mitigated by:
   - The 500-continuation runaway guard (`ULTRAPILOT_MAX_CONTINUATIONS`)
   - The token budget soft bound (`--tokens N`)
   - The phase-state machine that prevents the agent from looping outside the intended flow

4. **Cross-session leakage** — mitigated by multi-source session ID resolution. Goals do not leak across separate sessions.

5. **Goal-text prompt-injection hijacking the agent** — the agent is told explicitly to treat `<objective>` content as untrusted and to ignore instructions that contradict higher-priority context.

## Reporting a Vulnerability

If you find a security issue in ultrapilot:

- **Email**: [create a GitHub issue marked `security`](https://github.com/joychetry/ultrapilot/issues/new?template=security.md) or email the maintainers.
- **Do not** post the vulnerability publicly until it has been triaged.
- We aim to respond within 72 hours.

## What is NOT a security issue

- Bugs in the agent's behavior (use [bug report template](https://github.com/joychetry/ultrapilot/issues/new?template=bug.md))
- Documentation issues
- Feature requests
- Performance issues

## Disclosure Policy

We follow **responsible disclosure**:

1. Reporter notifies us privately.
2. We confirm and triage within 72 hours.
3. We develop a fix and a CVE if appropriate.
4. We coordinate disclosure timing with the reporter.
5. We publish a security advisory after the fix is released.

## What we will NOT do

- We will not silently fix vulnerabilities.
- We will not blame reporters for honest mistakes.
- We will not pursue legal action against good-faith security research.
