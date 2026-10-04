# AI-native SDLC

**Describe a change. Approve the decisions. Let your coding agent do the work.**

You already use a coding agent to plan, implement, test and review changes. This plugin
connects those steps through decisions saved in your repository, so a fresh session or
teammate can continue from the agreed goal and plan.

The software development lifecycle (SDLC) takes a change from idea to delivery and
follow-up. In an AI-native workflow, agents carry work between those stages while humans
approve the decisions that guide it.

Describe what you want to change. The agent asks questions, creates and updates
`intent.md`, `spec.md` and `plan.md`, then implements and checks the code against
the approved decisions. You review and correct those files; the agent handles the
templates and bookkeeping.

Works with Claude Code, Codex and OpenCode in your existing repository, CI and release
process. Requires Git and Python 3.10+.

## Start

Install the plugin for your agent, then use its single entry point for the whole change:

| Agent | Command |
| --- | --- |
| Claude Code | `/sdlc:run Add CSV import with clear errors for invalid rows` |
| Codex | Invoke the installed `run` skill and describe the change |
| OpenCode | `/sdlc Add CSV import with clear errors for invalid rows` |

Open your project directory and start Claude Code, then run:

```text
/plugin marketplace add saggl/ai-native-sdlc
/plugin install sdlc@ai-native-sdlc
/sdlc:run Add CSV import with clear errors for invalid rows
```

Using another agent? See [Codex setup](docs/guide.md#codex) or [OpenCode setup](docs/guide.md#opencode).
If Claude commands do not appear, use `/reload-plugins` or open a new session.

## Your first change

For the CSV import example above:

1. The agent asks who needs the import and what success looks like, then presents
   `intent.md`. Give feedback or reply `Intent approved`.
2. It drafts `spec.md` with the required behavior, such as how invalid rows are handled.
   Revise it or reply `Spec approved`.
3. It drafts `plan.md` with the implementation approach and checks.
   Revise it or reply `Plan approved`. Implementation begins only after this approval.
4. The agent implements, tests and obtains an independent agent review against those decisions.
   It pauses for missing decisions or blocked checks.
5. Merge and release follow your project's policy. The agent records delivery evidence,
   the observed outcome and any follow-up.

| You decide | The agent saves and does |
| --- | --- |
| Problem and outcome | `intent.md` |
| Required behavior | `spec.md` |
| Approach and checks | `plan.md`, then implementation, tests and fresh review |
| Merge and release under project policy | Delivery evidence, observed outcome and follow-up |

For solo work, reply to the agent's presented document in chat when your project policy
allows it. The agent saves the decision and the reviewed revision. For GitHub teams,
the responsible owner replies to the document's presentation in the change PR.

## Continue with the same command

Resume with `/sdlc:run <change-id>`, ask `/sdlc:run show status`, or request
`/sdlc:run review change <change-id>`. In Codex, use the same installed `run` skill;
in OpenCode, use `/sdlc`. The agent reads the saved state and chooses the next step,
including after a teammate approves in the PR or you open a fresh session.

## Teams

**One change, one branch, one PR.** Stage replies record decisions; GitHub **Approve** handles the
final merge review under your team's policy. See [roles and the sequence](docs/guide.md#team-workflow).

Project context lives in `.sdlc/project.json`; decisions and evidence in `changes/<id>/`.
Local records detect stale content, but do not authenticate approvals. Existing CI and
release controls still apply; unavailable required checks stay pending.

This is a guided workflow, not an autonomous runner. Hooks and CI templates are opt-in
(see [playbook coverage](docs/guide.md#playbook-coverage)); nothing is active by default, and
it does not authenticate reviewers or deploy your project. Start with a small change and adapt the
decision owners to your team's existing policy.

[Setup and maintenance](docs/guide.md) ·
[Contributing](CONTRIBUTING.md) ·
[Issues and feedback](https://github.com/saggl/ai-native-sdlc/issues) ·
[Anthropic's AI-native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook)
