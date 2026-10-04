---
name: status
description: Show the current AI-native SDLC changes, next steps and missing evidence in this repository without changing anything.
---

# Show progress

Resolve `<plugin-root>` as `${CLAUDE_PLUGIN_ROOT}` in Claude Code or two directories
above this SKILL.md in Codex or OpenCode. Read `<plugin-root>/references/workflow.md`
for the helper invocation.
Run its read-only `status` command in the target Git root. If setup is absent, say
"Start the sdlc start skill and describe your change." Do not initialize anything here.
For each open change show its title, current stage, missing decision or evidence,
and the next action. Read the latest report for an explanation of a blocked result.
Local approval records need their referenced human evidence; do not call them verified
authorization. Completed changes are historical records, not checks of today's code.
