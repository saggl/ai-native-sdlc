# Migrate the copied 0.1 package

Read `.sdlc/package-lock.json` and compare its listed hashes with installed files.
Identify modifications before removing anything; preserve custom content as project
instructions/policies. Present the concrete migration diff in a normal project branch.

Remove only unmodified old shared assets recorded by that lock: the four
`.claude/skills/sdlc-*` directories, `.sdlc/templates`, `.sdlc/workflow.md` and `.sdlc/VERSION`.
Update their links in CLAUDE.md/REVIEW.md to the plugin workflow. After preserving its
provenance in Git, remove the old package lock. Do not remove the complete `.sdlc` or
`.claude` directory; they may contain unrelated project data.

Run plugin setup and preserve all existing `changes/` artifacts. Old changes do not have
state.json: continue an in-flight legacy change with its old version, or explicitly adopt
it by creating a new uniquely named tracked change, copying the actual artifacts and
linking their original approval evidence. Review the current content before recording
any decisions. Never convert old descriptive "approved" fields into human approval.

Use `/sdlc:run` for the next task. Keep only one active implementation of the workflow.
