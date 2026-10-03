# Adopt the plugin

## First real task

Install as described in the root README. In an existing repository run `/sdlc:start`
with a small real change. Claude discovers commands and policies, asks only for missing
blocking decisions and creates project context. Keep the generated artifacts in Git.

For a new project, start in an empty Git repository. Claude can capture intent before
application code exists; approve the desired behavior and approach before implementation.

No service account, hosted MCP server, API key, monitoring service or new project template
is required for guided use. Existing CLI/MCP integrations remain usable.

## Team use

Use the plugin manager's project scope when the repository should recommend the plugin
to its collaborators. From a terminal in that project:

```bash
claude plugin marketplace add saggl/ai-native-sdlc
claude plugin install sdlc@ai-native-sdlc --scope project
```

Review and commit the generated project plugin settings. Each collaborator still needs
repository access and a local install. The marketplace repository is private; distribute
access or mirror the package into an approved internal marketplace before wider rollout.
Do not change repository visibility as a side effect of installation.

| Decision | Responsible person |
| --- | --- |
| Scope/value | Product or project owner |
| Behavior and constraints | Owner with relevant domain experts |
| Approach and verification | Engineer; technical lead for material risk |
| Merge and release | Existing project authority |
| Observed outcome and follow-up | Product/service owner |

One person may hold multiple roles. Record the actual decision; do not invent independent
approval. Use protected PR reviews or the existing decision system where required.

## Updates

From a terminal:

```bash
claude plugin marketplace update ai-native-sdlc
claude plugin update sdlc@ai-native-sdlc
```

Use `/reload-plugins` or a new session to load the update. The publisher must bump
`plugins/sdlc/.claude-plugin/plugin.json` when releasing changes. Roll out a tested version
through your approved marketplace/ref for controlled team use. Project decisions and
`.sdlc/project.json` are not part of the plugin cache and are never overwritten by updates.

## Migration from 0.1

See the bundled [migration instructions](../plugins/sdlc/references/migrate.md).
Do not keep both the old copied skills and the new plugin active. Preserve existing change
artifacts and instructions. Legacy work is not retroactively marked approved by migration.

## Extend only where the project needs it

Put stable project rules in CLAUDE.md and policy files; keep reusable domain expertise in
separate project/company skills. Link authoritative Jira/Polarion/Teamcenter records from
the change artifacts rather than duplicating their complete content. A CI adapter can
use the same artifacts and evidence; it must verify actual authorization independently.

For Python, discover the actual test/environment tooling. For embedded work, distinguish
host tests, cross-compilation, simulation and target/HIL proof. An absent target leaves its
criterion unverified. A firmware release can use an artifact handoff as its delivery boundary.

Across the first five real tasks, measure time to approved intent, human review time,
rework, missing evidence and whether another session can resume correctly. Add failure
cases to the eval suite. Expand to event triggers and monitoring only once this works.
