# AI-native SDLC

This repository has one job: distribute the smallest useful Claude Code plugin for:

`intent.md → spec.md → plan.md → implementation`

Keep:
- one user command: `/sdlc:start`
- three artifact templates
- no runtime helper, database, project config, or duplicate workflow state

Prefer deleting complexity over documenting it. Add a new mechanism only after a real workflow need cannot be solved by the existing artifacts, Git, or the target repository's own tooling.

Smoke-test changes by installing the plugin in a disposable repository and running one change through all three approvals and implementation.
