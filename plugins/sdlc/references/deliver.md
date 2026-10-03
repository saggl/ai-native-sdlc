# Deliver, observe and feed the next intent

## Delivery

Use the real repository host and CI; preserve its policy. Prepare a PR (or equivalent)
with links to intent/spec/plan, decisions, verification and fresh review. Lead with the
problem, resulting behavior, important risks and remaining human decisions. Include a
rollback path. Do not require a second preparation PR if the project does not need one.

When authorized to push and maintain this PR, inspect failing checks and actionable
review comments, fix within scope, rerun verification and fresh review for changed code,
and continue until the PR is ready or a decision is missing. Do not enable auto-merge,
merge or deploy without the project's existing authorization. Never alter branch rules,
permissions or required checks to finish a task. Handle unavailable host/CI tools as a
specific handoff with links and next action.

Record delivery.md from observed PR, CI and release evidence. "PR opened" is not "deployed".
Use `blocked` while required merge/release evidence is pending. For a library, firmware
or script, delivery can mean its defined artifact/release handoff rather than a live service;
the spec must identify that boundary. Record a passed delivery result only after it occurs.

## Observation and learning

Read the configured signal through available monitoring, CI, issue or engineering
integrations. Respect its observation window. Record expected versus observed outcome,
time window, evidence and the responsible owner in learning.md. If access or time is
missing, say so and leave the change awaiting observation. A passed observation step
means the observation and triage are done; the product outcome may be below target.

For an incident or failed outcome, capture a linked next intent and add the relevant
regression/eval case. Route that intent for its normal human decision; do not silently
approve a new task. Record useful repeat mistakes in CLAUDE.md or a project skill.
If those edits change policy/code, rerun the affected verification/review before closing.

Record a passed learning result only with observed evidence and completed triage. This
closes the change as a historical record. No daemon or future check is created by these
instructions. Headless event triggers need a separately configured project runner,
deterministic detection, bounded credentials and the same decision gates.
