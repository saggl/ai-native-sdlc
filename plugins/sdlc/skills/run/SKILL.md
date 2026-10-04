---
name: run
description: Continue an AI-native SDLC change from its current state, or handle a focused status or review request.
argument-hint: "[describe a change, issue URL, or existing change ID]"
---

# AI-native SDLC

Use this single skill for every SDLC action. In Claude Code, the installed plugin root
is `${CLAUDE_PLUGIN_ROOT}`; in Codex, resolve the plugin root two levels above this
file. Work in the user's project, never in the installed plugin.

Read `<plugin-root>/references/workflow.md`. For new or resumed work, follow
`<plugin-root>/references/workflows/start.md`. For an explicit status-only request,
follow `<plugin-root>/references/workflows/status.md`. For an explicit independent
review, follow `<plugin-root>/references/workflows/review.md`.

Use the user's request as the action and arguments. No separate slash command is needed
for status or review. If no action is clear, inspect saved state and continue the active
change; if several changes are open, ask which one to continue.
