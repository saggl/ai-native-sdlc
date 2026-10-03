# AI-native SDLC plugin

This repository distributes a Claude Code plugin used in other projects.
Read README.md and plugins/sdlc/references/workflow.md. Canonical runtime assets live
entirely in plugins/sdlc; the marketplace points to that self-contained directory.

Python 3.10+, Git, standard library only.
- Validate: python3 scripts/validate.py
- Test: python3 -m unittest discover -s tests -v

Keep the main user path /sdlc:start. Do not add routine manual setup steps or duplicate
lifecycle commands. Preserve existing project data on setup/updates. Test actual Git,
resume, stale evidence and filesystem boundaries when changing the helper.

Local records and skills are not authenticated approval enforcement. Report unavailable
checks honestly. Examples stay illustrative. Run relevant evals/README.md scenarios for
workflow changes and state whether a real Claude Code runtime was exercised.
