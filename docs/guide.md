# Setup and maintenance

## Adopt and update

Start with one real change. The agent discovers project commands and preserves existing
instructions. Shared workflow updates leave project decisions and configuration intact.
New records include the installed workflow version and content hash. Open decisions
are rechecked when that guidance changes; older records remain readable but lack that
provenance. Existing 0.2 records need no migration; copied 0.1 packages use the
[migration instructions](../plugins/sdlc/references/migrate.md).

### Claude Code

For a shared project, run in its directory:

```bash
claude plugin marketplace add saggl/ai-native-sdlc
claude plugin install sdlc@ai-native-sdlc --scope project
```

Review and commit the generated settings; teammates install locally. To update:

```bash
claude plugin marketplace update ai-native-sdlc
claude plugin update sdlc@ai-native-sdlc
```

Use `/reload-plugins` or a new session. Teams can roll out a tested marketplace/ref.
Start and resume work with `/sdlc:run <description-or-change-id>`. Ask for status or
an independent review in the same command, for example `/sdlc:run show status` or
`/sdlc:run review change <change-id>`.

### Codex

Run `codex plugin marketplace add saggl/ai-native-sdlc`, then install the `run` skill
from that source in the ChatGPT desktop Plugins Directory. Where the repository
marketplace is available, enable it in `.codex/config.toml`:

```toml
[plugins."sdlc@ai-native-sdlc"]
enabled = true
```

Invoke the installed `run` skill for new or resumed work. Include “show status” or
“review change <id>” when you want those focused actions. The skill reads the current
state and selects the right path.

### OpenCode

```bash
git clone https://github.com/saggl/ai-native-sdlc.git
cd ai-native-sdlc
python3 scripts/install_opencode.py
```

Open a new session in your project and run `/sdlc <description-or-change-id>`.
For example, use `/sdlc Add CSV import with clear errors for invalid rows`,
`/sdlc show status` or `/sdlc review change <change-id>`.

After `git pull`, rerun the installer. It installs the shared package in
`~/.config/opencode/skills/sdlc` and the `/sdlc` command in
`~/.config/opencode/commands/`. It updates its managed command, refuses conflicting
edits, and leaves project files and unrelated commands alone.

## Team workflow

Use one branch and draft PR from intent through implementation. Follow existing project
policy; record agreed owners and adaptations in REVIEW.md. One person may hold several roles.

| Decision | Default owner | Action |
| --- | --- | --- |
| Intent | Product or delegated task owner | Reply `Intent approved` |
| Spec | Product/domain owner | Reply `Spec approved` |
| Plan | Implementing engineer; teammate for significant risk | Reply `Plan approved` |
| Implementation within scope | Agent, with tests and fresh review | No per-edit human approval |
| Merge | Teammate, with required checks passing | GitHub **Approve** |
| Release | Existing release authority | Existing release process |

1. The agent saves an artifact and presents a revision-pinned link in the change PR.
2. Its owner replies to that presentation with approval or feedback. No SHA to type.
3. Resume by invoking the same `sdlc` command. The agent checks the decision and advances.
4. After plan approval, the agent implements, tests and obtains fresh agent review.
5. Mark the same PR ready for the project's final merge review, then release normally.

Intent, spec and plan remain sequential decisions. A stage reply is not a merge approval;
labels and generic “looks good” do not count. Changed decisions need approval again;
new code alone does not revoke unchanged artifact decisions. Solo projects and other
hosts keep their existing merge/release policy.

The agent checks identity and revision through available tools; the helper is not an
authentication service or background watcher. See the bundled
[approval rules](../plugins/sdlc/references/workflow.md#team-decisions-on-one-pr)
for exact evidence and ambiguity handling.

## Extend when needed

Keep commands and recurring lessons in project agent instructions; reusable domain policy
belongs in skills. Link authoritative Jira, Polarion or Teamcenter records instead of
copying them. For embedded work, keep host, cross-build, simulation and target/HIL evidence
distinct. Delivery may mean a firmware artifact handoff; required hardware checks still apply.

Add integrations only for a demonstrated need. Nothing is active by default, and no
credentials or automatic merge/deploy policy are installed.

### Opt-in hooks and CI

After setup the agent offers one short question about hooks and CI templates. On your
explicit yes it runs `install <hooks|evals|review|handoff|monitor>`: `hooks` copies the
guard to `.claude/hooks/sdlc-guard.py` and merges entries into `.claude/settings.json`;
the others copy `ci/<name>.yml` to `.github/workflows/sdlc-<name>.yml` (`monitor` also
`.sdlc/bands.py` and `bands.json`). Existing files are never overwritten. Guard rules
come from `protected_paths`, `gates` and `commands.format` in `.sdlc/project.json`.
Non-negotiable gates belong in managed settings owned by platform/IT.

## Playbook coverage

Claude-first. On Codex and OpenCode, hook and CI checks fall back to the review gate.
Hosted products (Claude Security, Claude Tag, managed Code Review, Claude Design) are
integrated by intake, not reimplemented.

| Play | Asset | Notes |
| --- | --- | --- |
| Capture as intent.md | [intent template](../plugins/sdlc/templates/intent.md) | `new --adopt` registers intents from connectors, scans and Tag |
| Requirements and design | [spec stage](../plugins/sdlc/references/stages.md#prepare-draft--or-approve-), [handoff template](../plugins/sdlc/ci/handoff.yml) | Link the Claude Design mock for front-end work; `install handoff` drafts spec PRs when an intent approval merges |
| Plan mode | [plan stage](../plugins/sdlc/references/stages.md#prepare-draft--or-approve-) | Deviations go in plan.md `## Implementation deviations` |
| Auto mode | [build stage](../plugins/sdlc/references/stages.md#build-implement-and-verify) | Routine work after plan approval; artifacts reviewed afterwards |
| CLAUDE.md | [setup](../plugins/sdlc/references/setup.md) | Commands and recurring mistakes; repeated review flags land here |
| Skills as institutional knowledge | [spec stage](../plugins/sdlc/references/stages.md#prepare-draft--or-approve-) | Skill paths in `policy_files` join approval snapshots |
| Hooks as build-time guardrails | [guard](../plugins/sdlc/hooks/guard.py) | Opt-in via `install hooks`; protected paths, locked tests, format |
| Parallel sessions and subagents | [verifier](../plugins/sdlc/agents/verifier.md) | `claude --worktree` sessions; fresh-context verifier |
| Feedback loop | [build stage](../plugins/sdlc/references/stages.md#build-implement-and-verify) | Failing test first, then `lock-tests` |
| Continuous evals in CI | [evals template](../plugins/sdlc/ci/evals.yml) | Opt-in via `install evals` |
| AI in the PR review loop | [review policy](../plugins/sdlc/templates/review-policy.md) | Bugs, Security, Compliance; `Tally:` line; `install review` adds claude-code-action review, `@claude` fixes and failed-build triage, or enable managed Code Review |
| Hooks as approval gates | [guard](../plugins/sdlc/hooks/guard.py) | `gates` in project.json; managed settings for non-negotiable gates |
| CI/CD integration and deployment | [deliver stage](../plugins/sdlc/references/stages.md#deliver-deliver) | Autonomy by environment; one rehearsed rollback; PR-only writes |
| Closing the loop | [monitor template](../plugins/sdlc/ci/monitor.yml), [bands](../plugins/sdlc/scripts/bands.py) | Opt-in via `install monitor`; deterministic bands: 1σ log, 2σ read-only diagnosis, 3σ intent PR |
| Recurring codebase scans | [observe intake](../plugins/sdlc/references/stages.md#observe-observe-and-learn) | Claude Security scans; bounded fix is a patch PR, wider finding an adopted intent, dismissals need a reason |
| Claude on call with Claude Tag | [observe intake](../plugins/sdlc/references/stages.md#observe-observe-and-learn) | Tag, channel and ticket requests enter by the same intake; post-mortem in learning.md |

## Validate a change

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

Tests cover real Git repositories, stale evidence, data preservation and installer updates.
CI runs on Linux, Windows and macOS. For agent behavior and native installation, use the
[behavior evaluations](../evals/README.md); Python tests alone do not prove those work.
The opt-in `evals/run.py` runs
two initial-gate smoke cases through a supplied agent CLI; it does not replace native
installation or full lifecycle evaluations.
Version 0.4.0 changes the workflow hash scope, so open records show `workflow_changed`
once and the agent rechecks them. The policy template is now `review-policy.md`; an
existing project REVIEW.md is untouched.
Record results and unavailable checks in the PR. Keep both plugin manifest versions aligned.

## Basis

This independent implementation follows
[Anthropic's playbook](https://claude.com/blog/the-ai-native-sdlc-playbook).
Command names, folder layout and local records are this project's choices.
