---
name: review
description: Review an AI-native SDLC change against its approved artifacts and current diff. Use in a fresh session for independent verification or when a review is requested.
argument-hint: "[change ID]"
---

# Review the delivered behavior

Change selection: use the current invocation's ID, if provided.

Resolve `<plugin-root>` as `${CLAUDE_PLUGIN_ROOT}` in Claude Code or two directories
above this SKILL.md in Codex or OpenCode. Read `<plugin-root>/references/workflow.md`
and `<plugin-root>/references/stages.md`. Resolve the target Git root and identify
the requested change; with no ID, select the sole change awaiting review or ask.
Read current project instructions, REVIEW.md, the change's saved artifacts, approval
evidence, implementation diff and verification report. Do not assume a previous chat.
If this session implemented the change, label this a self-review and obtain a fresh
review before recording a passed review result. Do not edit product code as reviewer.
Write the review report and record its result only after following its Review section.
