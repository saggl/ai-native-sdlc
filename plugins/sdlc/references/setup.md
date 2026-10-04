# Set up this project while starting the first task

Inspect instructions, manifests, build/test targets, CI and relevant code. Run `setup`
to create `.sdlc/project.json`. If a legacy copied package is detected, read the bundled
`references/migrate.md`; preserve historical changes and local customizations.

Fill the project config from evidence, preserving existing values on later runs:

- `commands`: verified build, test and lint commands, with expected success conditions.
  Leave unavailable commands absent and explain what needs to be supplied.
- `policy_files`: repository-relative paths for applicable security, architecture,
  product or review policies and applied domain skill source files. These files join
  approval snapshots. Keep this concise.
- `owners`: discover actual owners and retrievable identities from project policy; ask
  only for the missing owner needed now. Use [workflow defaults](workflow.md#team-decisions-on-one-pr)
  where no policy exists. Record agreed adaptations in REVIEW.md. Comment access alone
  does not establish authority; do not change repository settings during setup.
- `delivery`: existing release command or process, authorization and rollback route.
- `observe`: the signal of success, where to read it, observation window and owner.
- `changes_dir`: default `changes`; use another unused evidence-only directory if that
  name already holds unrelated/product code. Do not move existing project content.

For Python tooling, discover the actual environment and test command. For embedded
work, identify host tests, cross-build, simulation and target/HIL evidence separately;
record hardware availability and timing/memory constraints. Do not invent support.

Preserve existing CLAUDE.md, AGENTS.md, README and REVIEW.md. Add only a small relevant
pointer to the project's active agent instructions (such as CLAUDE.md or AGENTS.md),
using that agent's start entry point from the installed skill. Mention .sdlc/project.json
and the configured changes directory. Add verified commands and recurring mistakes if
missing; keep instructions short. Never replace project rules.
Use the bundled REVIEW.md template only if no review policy exists; adapt it to the
actual product. Resolve conflicting policy with its owner.

Show a brief setup summary and any decision that blocks the task, then capture its
intent. Do not ask the user to complete a questionnaire or configure optional integrations
before the first task. Setup is local and repeatable; plugin updates do not rewrite it.

