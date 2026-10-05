# AI-native SDLC

Early preview · version `0.0.1`

**Describe a change. Approve the approach. Let your coding agent implement, verify and review it.**

A small reusable workflow for Claude Code, Codex and OpenCode in your existing repository.
It connects the coding work you already do through durable decisions that a fresh session
or teammate can read:

**Intent → Spec → Plan → Implement → Verify → Independent review**

Humans make decisions that require judgment. Agents carry out the work. Your existing
CI and merge/release policy enforce the project's rules. Requires Git and Python 3.10+.

## Start

Install for your agent, then use its single entry point for new work, resumption or review:

| Agent | Entry point |
| --- | --- |
| Claude Code | `/sdlc:run Add CSV import with clear errors for invalid rows` |
| Codex | Invoke the installed `run` skill and describe the change |
| OpenCode | `/sdlc Add CSV import with clear errors for invalid rows` |

In Claude Code, open your project directory and run:

```text
/plugin marketplace add saggl/ai-native-sdlc
/plugin install sdlc@ai-native-sdlc
/sdlc:run Add CSV import with clear errors for invalid rows
```

See [Codex setup](docs/guide.md#codex) or [OpenCode setup](docs/guide.md#opencode).
If Claude commands do not appear, use `/reload-plugins` or open a new session.

## Your first change

1. Describe the outcome. The agent asks questions that affect the decision and drafts:

   | Artifact | Decision |
   | --- | --- |
   | `intent.md` | Why the change matters, its outcome, constraints and scope |
   | `spec.md` | Required behavior, acceptance criteria and relevant edge cases |
   | `plan.md` | Approach, risks and small implementation steps with checks |

2. For a clear, routine change, review all three together and reply `Plan approved`.
   This approves their presented revisions before implementation. Ambiguity or significant
   risk adds an earlier intent or spec decision. Existing project policy takes precedence;
   legacy configurations keep their three-stage gates.
3. The agent implements one coherent step at a time, checks it and fixes failures.
   After final verification, a fresh reviewer checks the decisions, diff and evidence.
4. With required checks passing and important findings resolved, the change is **ready
   for your project's merge process**. Merge approval and release follow that process.

The agent handles templates and evidence. You do not manage separate stage commands.
Missing required checks remain blocked; delivery and outcome observation are optional
follow-up unless your project requires them.

## Continue and collaborate

Use `/sdlc:run <change-id>`, `/sdlc:run show status` or
`/sdlc:run review change <change-id>`. In Codex, use the same `run` skill; in OpenCode,
use `/sdlc`. The agent reads the saved decisions and evidence to choose the next step.

**One change, one branch, one PR.** For GitHub teams, the authorized owner reviews the
revision-pinned links and replies in the same PR:

```text
Plan approved <presentation-comment-url>
```

The routine plan presentation includes intent, spec and plan. Use `Intent approved` or
`Spec approved` when an earlier gate is required. The owner must have authority for
the decisions covered. Final GitHub **Approve** remains a separate merge decision.
Solo projects can use explicit chat decisions when their policy permits it.
See [team decisions](docs/guide.md#team-workflow).

## Six essentials

- Establish intent before implementation.
- Make the approach inspectable before significant code.
- Work in small, independently verifiable increments.
- Verify with observed results; writing code alone is not completion.
- Review from fresh context against intent, spec, plan and evidence.
- Keep deterministic rules in tests, linters, hooks and CI.

Project configuration lives in `.sdlc/project.json`; the three planning artifacts,
machine state and verification/review evidence live in `changes/<id>/`. Local records
detect stale content; they do not authenticate approval or grant permissions.

Add integrations only when needed. The [optional GitHub adapter](adapters/github/README.md)
can resume after owner decisions and run bounded review/fix cycles. Hooks, monitoring,
agent evals and delivery/observation are extensions; installation enables no deployment
access or background automation.

[Setup and extensions](docs/guide.md) · [Contributing](CONTRIBUTING.md) ·
[Issues](https://github.com/saggl/ai-native-sdlc/issues) ·
[Anthropic's playbook](https://claude.com/blog/the-ai-native-sdlc-playbook)
