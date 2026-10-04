# Setup and maintenance

## Adopt and update

Start with one real change. The agent discovers project commands and preserves existing
instructions. Shared workflow updates leave project decisions and configuration intact.
Existing 0.2 records need no migration; copied 0.1 packages use the
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

### Codex

Run `codex plugin marketplace add saggl/ai-native-sdlc`, then install `sdlc` from
that source in the ChatGPT desktop Plugins Directory. Where the repository marketplace
is available, enable it in `.codex/config.toml`:

```toml
[plugins."sdlc@ai-native-sdlc"]
enabled = true
```

Invoke the installed `start` skill with your change description, `status` for progress,
or `review` with a change ID in a fresh session. All load the same bundled workflow.

### OpenCode

```bash
git clone https://github.com/saggl/ai-native-sdlc.git
cd ai-native-sdlc
python3 scripts/install_opencode.py
```

Open a new session in your project and run `/sdlc-start <description>`.
Use `/sdlc-status` or `/sdlc-review <change-id>` when needed.

After `git pull`, rerun the installer. It installs the shared package in
`~/.config/opencode/skills/sdlc` and commands in `~/.config/opencode/commands/`.
It updates its managed commands, refuses conflicting edits, and leaves project files
and unrelated commands alone.

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
3. Resume `start`. The agent checks the decision and advances to the next stage.
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

Add integrations only for a demonstrated need. No hooks, credentials, background runner
or automatic merge/deploy policy are installed.

## Validate a change

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

Tests cover real Git repositories, stale evidence, data preservation and installer updates.
CI runs on Linux, Windows and macOS. For agent behavior and native installation, use the
[behavior evaluations](../evals/README.md); Python tests alone do not prove those work.
Record results and unavailable checks in the PR. Keep both plugin manifest versions aligned.

## Basis

This independent implementation follows
[Anthropic's playbook](https://claude.com/blog/the-ai-native-sdlc-playbook).
Command names, folder layout and local records are this project's choices.
