# AI-native SDLC

**Describe a change. Approve the decisions. Let Claude do the work.**

A Claude Code plugin for your own projects. It keeps intent, specification, plan and
evidence in Git, so the next session can pick up where you left off.

## Start

In Claude Code:

```text
/plugin marketplace add saggl/ai-native-sdlc
/plugin install sdlc@ai-native-sdlc
```

Then, inside the project you work on:

```text
/sdlc:start Add CSV import with clear errors for invalid rows
```

Requires Claude Code with plugin support, Git, Python 3.10+ and access to this private
repository. If commands do not appear, use `/reload-plugins` or open a new session.

## The workflow

| You approve | Claude saves and does |
| --- | --- |
| The problem and outcome | `intent.md` |
| The required behavior | `spec.md` |
| The approach and checks | `plan.md`, then implementation, tests and fresh review |
| The project's release decision | Delivery evidence, observed outcome and follow-up |

Claude handles setup and continues between stages. It pauses for a decision or a real
blocker. Each approval applies to the saved content you reviewed.

**Resume with `/sdlc:start`.** Use `/sdlc:status` for progress or
`/sdlc:review <change-id>` for review in a fresh session.

## Working as a team

Use one PR per change. Name the decision owners, record intent/spec/plan decisions in
comments identifying the artifact and commit, then use GitHub **Approve** for the final
merge review. The implementing engineer can approve a routine plan; significant risk
needs a teammate. See the [team workflow](docs/guide.md#team-workflow) for roles and an example.

## Keep it small

Use short artifacts. Create them only when needed. Link existing evidence instead of
copying it. Add a rule or integration only when a real task needs it.

Your project keeps `.sdlc/project.json` for context and `changes/<id>/` for decisions
and evidence. Shared instructions and templates stay in the plugin.

This is a guided workflow. Local records detect stale content; they do not authenticate
approvals. Existing PR, CI and release controls still apply. Required checks remain
pending until actually run. Background monitoring and automatic deployment need
project-specific integrations.

[Team setup and maintenance](docs/guide.md) ·
[Anthropic's AI-native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook)
