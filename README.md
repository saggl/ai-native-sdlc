# AI-native SDLC

**Describe a change. Approve the decisions. Let your coding agent do the work.**

One workflow for Claude Code, Codex and OpenCode. Decisions and evidence stay in Git,
so a fresh session can continue where you left off. Requires Git and Python 3.10+.

When an agent can write code faster than a team can review it, the hard part is keeping
the problem, expected behavior and chosen approach visible. This plugin guides one
change through those decisions, implementation, independent review and observed
delivery. It uses your existing repository, CI and release process.

## Start

Install the plugin for your agent, then use the same entry point for the whole change:

| Agent | Command |
| --- | --- |
| Claude Code | `/sdlc:sdlc Add CSV import with clear errors for invalid rows` |
| Codex | Invoke the installed `sdlc` skill and describe the change |
| OpenCode | `/sdlc Add CSV import with clear errors for invalid rows` |

For Claude Code:

```text
/plugin marketplace add saggl/ai-native-sdlc
/plugin install sdlc@ai-native-sdlc
/sdlc:sdlc Add CSV import with clear errors for invalid rows
```

Using Codex or OpenCode? See [setup and use](docs/guide.md#setup-and-use).
If Claude commands do not appear, use `/reload-plugins` or open a new session.

## How to use it

Describe new work, resume with the change ID, or ask for a focused action such as
“show status” or “review change <id>.” The agent reads the saved state and chooses the
right next step. You do not switch between start, status and review commands.

The agent pauses when a human decision or external dependency is needed. Reply to the
presented intent, spec or plan with `Intent approved`, `Spec approved` or
`Plan approved`; otherwise give feedback. To resume, invoke the same command again.

| You decide | The agent saves and does |
| --- | --- |
| Problem and outcome | `intent.md` |
| Required behavior | `spec.md` |
| Approach and checks | `plan.md`, then implementation, tests and fresh review |
| Merge and release under project policy | Delivery evidence, observed outcome and follow-up |

## Teams

**One change, one PR.** Stage replies record decisions; GitHub **Approve** handles the
final merge review under your team's policy. See [roles and the sequence](docs/guide.md#team-workflow).

Project context lives in `.sdlc/project.json`; decisions and evidence in `changes/<id>/`.
Local records detect stale content, but do not authenticate approvals. Existing CI and
release controls still apply; unavailable required checks stay pending.

This is a guided workflow, not an autonomous runner. It does not install CI gates,
authenticate reviewers or deploy your project. Start with a small change and adapt the
decision owners to your team's existing policy.

[Setup and maintenance](docs/guide.md) ·
[Contributing](CONTRIBUTING.md) ·
[Issues and feedback](https://github.com/saggl/ai-native-sdlc/issues) ·
[Anthropic's AI-native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook)
