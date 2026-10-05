# AI-native SDLC plugin

This repository distributes one shared workflow for Claude Code, Codex and OpenCode
in `plugins/sdlc`.
Read README.md and plugins/sdlc/references/workflow.md.

Python 3.10+, Git, standard library only.
- Validate: python3 scripts/validate.py
- Test: python3 -m unittest discover -s tests -v

## Keep the essentials

- Keep `sdlc` as the single user-facing entry point; it selects the workflow action.
- Prefer removing or simplifying before adding. Every file, command and abstraction
  must support a concrete user need.
- Give each instruction one authoritative home. Link it instead of repeating it.
- Keep artifacts proportional to the decision. Create them when needed.
- Add integrations and automation only for demonstrated needs.

Preserve project data and existing commands. Keep checks for
stale decisions, stale evidence and filesystem boundaries. Local records do not
authenticate approval; unavailable checks stay unverified.

Run the checks above after changes. Use evals/README.md for workflow evaluations and
state which native agent runtimes were exercised. Put validation results in the
PR, not another permanent report.
