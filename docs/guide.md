# Setup and maintenance

## Adopt and update

Start with one real change. The agent discovers project commands and preserves existing
instructions. Shared workflow updates leave project decisions and configuration intact.
Records include the installed workflow version and content hash; recheck open decisions
when that guidance changes.

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

Run `codex plugin marketplace add saggl/ai-native-sdlc`, then install the `sdlc` plugin
from that source in the ChatGPT desktop Plugins Directory. Invoke its `run` skill.
Where the repository marketplace is available, enable it in `.codex/config.toml`:

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

1. The agent drafts the artifacts and presents revision-pinned links in the change PR
   at each required gate; the routine plan gate includes all three artifacts.
2. Its owner comments with approval or feedback, linking the presentation comment.
   No SHA to type.
3. Resume by invoking the same `sdlc` command. The agent checks the decision and advances.
4. After plan approval, the agent implements, tests and obtains fresh agent review.
5. Mark the same PR ready for the project's final merge review, then release normally.

New projects draft routine intent, spec and plan without intermediate approvals;
`Plan approved` covers all three revisions. Ambiguity or significant risk adds a gate
at the affected stage. Missing `approval_stages` retains the legacy sequential policy. A stage reply is not a merge approval;
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

### Opt-in hooks and monitoring

When you choose an advanced control, the agent can run
`install hooks` (copies the guard to `.claude/hooks/sdlc-guard.py` and merges entries
into `.claude/settings.json`) or `install monitor` (experimental: copies
`.github/workflows/sdlc-monitor.yml`, `.sdlc/bands.py` and `.sdlc/bands.json`; set
`metric_command` to a command that writes a JSON array of numbers). Existing files are
never overwritten. Guard rules come from `protected_paths`, `gates` and
`commands.format` in `.sdlc/project.json`. Non-negotiable gates belong in managed
settings owned by platform/IT.
Gate regexes inspect the full command, including quoted text and heredocs, so they can
also flag prose mentioning a gated command. They do not parse shell semantics or provide a sandbox.

### CI with Claude

Use Anthropic's tools directly; this plugin supplies the policy they read.

- **PR review:** enable managed Code Review, or run
  [claude-code-action](https://github.com/anthropics/claude-code-action) with a prompt
  such as "Review this PR against REVIEW.md, spec.md and plan.md; end with the Tally
  line." `@claude` comments on a PR then address review findings.
- **Failed-build triage:** a step with `if: failure()` that runs
  `claude -p "Read the build log, say whether the failure is flaky or real, summarize in
  three lines"` and posts the result to the PR.
- **Evals on configuration changes:** run your eval cases through `claude -p` on pull
  requests touching `CLAUDE.md`, `.claude/**` or `REVIEW.md`, plus a nightly run, and
  fail below an agreed pass rate. Start from 20–50 real tasks; add one per incident.
- **Intent → spec handoff:** after an intent approval merges, a job may run
  `claude -p "/sdlc:run <id>"` to draft spec.md on a branch and open a PR. The spec
  still needs its human decision.

## Playbook coverage

Claude-first. On Codex and OpenCode, hook and CI checks fall back to the review gate.
Hosted products (Claude Security, Claude Tag, managed Code Review, Claude Design) are
integrated by intake, not reimplemented.

| Play | Asset | Notes |
| --- | --- | --- |
| Capture as intent.md | [intent template](../plugins/sdlc/templates/intent.md) | `new --adopt` registers intents from connectors, scans and Tag |
| Requirements and design | [spec stage](../plugins/sdlc/references/stages.md#prepare-draft--or-approve-), [CI handoff](#ci-with-claude) | Link the Claude Design mock for front-end work; a merged intent approval can trigger a spec draft PR |
| Plan mode | [plan stage](../plugins/sdlc/references/stages.md#prepare-draft--or-approve-) | Deviations go in plan.md `## Implementation deviations` |
| Auto mode | [build stage](../plugins/sdlc/references/stages.md#build-implement-and-verify) | Routine work after plan approval; artifacts reviewed afterwards |
| CLAUDE.md | [setup](../plugins/sdlc/references/setup.md) | Commands and recurring mistakes; repeated review flags land here |
| Skills as institutional knowledge | [spec stage](../plugins/sdlc/references/stages.md#prepare-draft--or-approve-) | Skill paths in `policy_files` join approval snapshots |
| Hooks as build-time guardrails | [guard](../plugins/sdlc/hooks/guard.py) | Opt-in via `install hooks`; protected paths, locked tests, format |
| Parallel sessions and subagents | [verifier](../plugins/sdlc/agents/verifier.md) | `claude --worktree` sessions; fresh-context verifier |
| Feedback loop | [build stage](../plugins/sdlc/references/stages.md#build-implement-and-verify) | Failing test first, then `record-regression` |
| Continuous evals in CI | [CI evals](#ci-with-claude), [eval runner](../evals/run.py) | Run on configuration changes and nightly; gate on pass rate |
| AI in the PR review loop | [review policy](../plugins/sdlc/templates/review-policy.md), [CI review](#ci-with-claude) | Bugs, Security, Compliance; `Tally:` line; managed Code Review or claude-code-action reads it |
| Hooks as approval gates | [guard](../plugins/sdlc/hooks/guard.py) | `gates` in project.json; managed settings for non-negotiable gates |
| CI/CD integration and deployment | [deliver stage](../plugins/sdlc/references/stages.md#deliver-deliver) | Autonomy by environment; one rehearsed rollback; PR-only writes |
| Closing the loop | [bands](../plugins/sdlc/scripts/bands.py), [monitor template](../plugins/sdlc/ci/monitor.yml) | Experimental, `install monitor`; deterministic bands: 1σ log, 2σ read-only diagnosis, 3σ intent PR |
| Recurring codebase scans | [observe intake](../plugins/sdlc/references/stages.md#observe-observe-and-learn) | Claude Security scans; bounded fix is a patch PR, wider finding an adopted intent, dismissals need a reason |
| Claude on call with Claude Tag | [observe intake](../plugins/sdlc/references/stages.md#observe-observe-and-learn) | Tag, channel and ticket requests enter by the same intake; post-mortem in learning.md |

## Protected bug fixes

For a bug fix, the agent creates the change with `--kind bugfix`, obtains the usual
intent/spec/plan decisions, commits a meaningful failing regression test, then runs:

```text
python3 <plugin-root>/scripts/sdlc.py --root <project-root> record-regression <id> --file tests/test_bug.py --command-json '["python3", "-m", "pytest", "tests/test_bug.py"]'
```

The supplied command runs without a shell and must return the expected nonzero exit
(default 1; use `--expected-exit` for your test runner). The agent must inspect why it
failed. Protected test content and the failure log are bound to the approved plan.
A passed result cannot be recorded after those files change. Reproduce again only
following a revised approved plan. Hardware-dependent reproduction remains blocked
without actual target evidence. This is result-time enforcement, not a per-edit hook or an
authorization service; fresh review must still check test strength and surrounding code.

## Optional GitHub automation

See the [GitHub adapter](../adapters/github/README.md) for explicit owner approvals,
revision-pinned comment handoffs, fresh review processes and bounded repair cycles.
It is installed separately in the consuming project and stops before merge/release.
The standard plugin stays guided and keeps the same single command.

## Validate a change

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

Tests cover real Git repositories, stale evidence, data preservation and installer updates.
CI runs on Linux, Windows and macOS. For agent behavior and native installation, use the
[behavior evaluations](../evals/README.md); Python tests alone do not prove those work.
The opt-in `evals/run.py` runs
lifecycle gate cases through a supplied agent CLI; synthetic decisions do not replace
native installation, real identity checks or production delivery verification.
Record results and unavailable checks in the PR. Keep both plugin manifest versions aligned.

## Basis

This independent implementation follows
[Anthropic's playbook](https://claude.com/blog/the-ai-native-sdlc-playbook).
Command names, folder layout and local records are this project's choices.
