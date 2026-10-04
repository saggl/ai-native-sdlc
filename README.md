# AI-native SDLC

**Describe a change. Approve the decisions. Let your coding agent do the work.**

One workflow for Claude Code, Codex and OpenCode. Decisions and evidence stay in Git,
so a fresh session can continue where you left off. Requires Git and Python 3.10+.

## Start

In Claude Code:

```text
/plugin marketplace add saggl/ai-native-sdlc
/plugin install sdlc@ai-native-sdlc
/sdlc:start Add CSV import with clear errors for invalid rows
```

Using another agent? See [Codex](docs/guide.md#codex) or [OpenCode](docs/guide.md#opencode).
If Claude commands do not appear, use `/reload-plugins` or open a new session.

## How it works

| You decide | The agent saves and does |
| --- | --- |
| Problem and outcome | `intent.md` |
| Required behavior | `spec.md` |
| Approach and checks | `plan.md`, then implementation, tests and fresh review |
| Merge and release under project policy | Delivery evidence, observed outcome and follow-up |

Reply `Intent approved`, `Spec approved` or `Plan approved` to the presented artifact.
The agent handles revision tracking, setup and stage transitions. It pauses for a
missing decision or blocker. Short artifacts and links to existing evidence are enough.

Resume with `start`; use `status` for progress and `review` in a fresh session.
In Claude Code these are `/sdlc:start`, `/sdlc:status` and `/sdlc:review <change-id>`.

## Teams

**One change, one PR.** Stage replies record decisions; GitHub **Approve** handles the
final merge review under your team's policy. See [roles and the sequence](docs/guide.md#team-workflow).

Project context lives in `.sdlc/project.json`; decisions and evidence in `changes/<id>/`.
Local records detect stale content, but do not authenticate approvals. Existing CI and
release controls still apply; unavailable required checks stay pending.

[Setup and maintenance](docs/guide.md) ·
[Anthropic's AI-native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook)
