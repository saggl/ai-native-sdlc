# AI-native SDLC

**Describe a change. Approve the decisions. Let your coding agent do the work.**

A workflow for Claude Code, Codex and OpenCode. It keeps intent, specification, plan and
evidence in Git, so the next session can pick up where you left off.

## Start

Use Git, Python 3.10+ and access to this private repository. Choose your agent:

**Claude Code** (plugin marketplace):

```text
/plugin marketplace add saggl/ai-native-sdlc
/plugin install sdlc@ai-native-sdlc
```

Then, inside the project you work on:

```text
/sdlc:start Add CSV import with clear errors for invalid rows
```

If commands do not appear, use `/reload-plugins` or open a new session.

**Codex** (plugin marketplace): run `codex plugin marketplace add
saggl/ai-native-sdlc`, then install `sdlc` from that source in the ChatGPT desktop
Plugins Directory. Invoke its `start` skill with your change description; use
`status` or `review` when needed. The same package includes the helper and templates.
See [team setup](docs/guide.md#adopt-and-update).

**OpenCode** (global skill and commands): clone this repository, then run:

```bash
python3 scripts/install_opencode.py
```

In any project, run `/sdlc-start Add CSV import with clear errors for invalid rows`.
Use `/sdlc-status` and `/sdlc-review <change-id>` for progress and review. Run the
installer again after pulling an update. It only replaces its own installed skill and
commands; it refuses to overwrite a conflicting command. Open a new OpenCode session
after installation.

## The workflow

| You approve | The agent saves and does |
| --- | --- |
| The problem and outcome | `intent.md` |
| The required behavior | `spec.md` |
| The approach and checks | `plan.md`, then implementation, tests and fresh review |
| The project's release decision | Delivery evidence, observed outcome and follow-up |

The agent handles setup and continues between stages. It pauses for a decision or a real
blocker. Each approval applies to the saved content you reviewed.

Resume with your agent's start entry point. Use its status and review entry points;
run review in a fresh session.

## Working as a team

Use one PR per change. Name the decision owners and use explicit stage replies such as
`Intent approved`, `Spec approved` and `Plan approved`; The agent binds each decision to
the committed artifact revision it presented. Use GitHub **Approve** for the final merge
review. The implementing engineer can approve a routine plan; significant risk needs a
teammate. See the [team workflow](docs/guide.md#team-workflow) for roles and an example.

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

