---
name: sdlc
description: Continue an AI-native SDLC change from its current state, or handle a focused status or review request.
---

# AI-native SDLC entry point

This skill is installed as the single user-facing `sdlc` entry point. The folder
containing this file is `<plugin-root>`. Work in the user's project, never in this
folder.

Read `<plugin-root>/references/workflow.md` and inspect the user's request:

- For new or resumed work, follow `<plugin-root>/references/workflows/start.md`.
- For an explicit progress/status request, follow
  `<plugin-root>/references/workflows/status.md`.
- For an explicit independent review, follow
  `<plugin-root>/references/workflows/review.md`.

Use the current request as the arguments to that path. If a request combines actions,
finish the requested focused action and then continue only when the next step is clear.
Do not require users to remember separate start, status or review commands.
