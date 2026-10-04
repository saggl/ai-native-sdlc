# Show progress

Resolve `<plugin-root>` as `${CLAUDE_PLUGIN_ROOT}` in Claude Code or from the
installed package in Codex/OpenCode. Read `<plugin-root>/references/workflow.md`
for the helper invocation.

Run its read-only `status` command in the target Git root. If setup is absent, explain
that the first SDLC request will initialize it; do not initialize anything for a
status-only request. For each open change show its title, current stage, missing decision
or evidence, and next action. Read the latest report for an explanation of a blocked
result. Local approval records need their referenced human evidence; do not call them
verified authorization. Completed changes are historical records, not checks of today's
code.
