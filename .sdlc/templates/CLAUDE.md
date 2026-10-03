# Project instructions
## Project context
Purpose, architecture essentials, important boundaries.
## Commands
Verified setup, build, test and lint commands. Mark unknown commands explicitly.
## Engineering rules
Project-specific conventions, compatibility and protected interfaces.
## Change workflow
Read .sdlc/workflow.md and relevant approved change artifacts before implementing.
Use the shared templates in .sdlc/templates; do not invent decisions or approvals.
Do not implement until human approval of the relevant scope, specification and plan is evidenced.
Escalate material changes to behavior, scope, interfaces or constraints before proceeding.
Record minor implementation deviations in plan.md and the review report.
## Verification
Run the plan's checks; report exact commands, outcomes and unrun checks.
Do not weaken tests merely to make the implementation pass.
Treat hardware-dependent checks as unverified until run on the required target.
