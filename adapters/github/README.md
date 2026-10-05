# Optional GitHub handoff

The core plugin works without this adapter. Opt in only when you need PR comments to
resume work or a bounded review/fix cycle. The adapter runs trusted code from a pinned
plugin checkout; it never imports Python from the PR branch.

## Set up in your project

1. Initialize a change with the ordinary plugin. Keep one change per branch/PR.
2. Commit an adapted [config.example.json](config.example.json) as `.sdlc/github.json`
   on the default branch. Configure explicit GitHub logins for operators and each stage
   owner, the installed headless CLI argv (task appended last), timeout and repair limit.
   Everyone listed must have repository write permission. No command text is run through a shell.
3. Review and copy [workflow.yml](workflow.yml) to `.github/workflows/sdlc.yml` on the
   default branch. Set `SDLC_PLUGIN_SHA` to this plugin's reviewed full commit SHA.
4. Provide a disposable, isolated runner labelled `sdlc-agent` with Git, Python 3.10+
   and your selected agent installed/authenticated. Configure model tool permissions,
   network policy and cost limits there. No permission bypass flags are provided.
5. Create the `sdlc-automation` environment and configure its approval policy, model
   secrets and runner restrictions. Keep production credentials off this runner. The
   workflow has repository write permissions; enable it only for trusted internal PRs.

The adapter rejects fork PRs, bots, unlisted operators/owners, wrong branches and stale
revisions. This is not a sandbox: model processes may execute project tests/code. Merely
removing GitHub tokens from their environment does not isolate them from the host.
Use ephemeral runners with platform-enforced isolation; do not share a persistent
privileged runner with untrusted jobs. Repository rules remain the final merge authority.
`GITHUB_TOKEN` must be allowed to write the feature branch; ruleset failures remain blocked.

## Use the same PR

- An operator comments `@sdlc run <change-id>` to continue, or
  `@sdlc review <change-id>` when verification is ready for independent review.
- When a decision is missing, the adapter presents the committed artifact and a gate
  marker in a PR comment. Its configured owner replies, for example:
  `Intent approved https://github.com/owner/repo/pull/123#issuecomment-456`.
  Paste the **presentation comment's** URL. This extra link is required because GitHub
  conversation comments do not provide an unambiguous reply-to relationship.
- That reply verifies the live author, authority, presented revision and policy content,
  records the decision and advances to the next gate automatically.
- Saved GitHub decisions are re-fetched before execution and publication. Chat-only or
  inaccessible decision evidence requires a manual handoff. Editing or deleting a
  decision makes subsequent invocations fail closed; it cannot retract already-run work.
- Verification is followed by a separate fresh agent process for review. A blocked
  review can trigger at most `max_fix_attempts` repairs, each followed by fresh review.
  Unavailable evidence and new decisions stop the run. Review processes that change
  product content cannot publish.
  Implementation processes cannot write review, delivery or learning results, or change
  saved decisions; the adapter checks this boundary after every run and repair.
- To address a human GitHub **Request changes** review, an operator comments:
  `@sdlc fix <change-id> https://github.com/owner/repo/pull/123#pullrequestreview-456`.
  The adapter verifies the linked review's author, state and current head before a
  bounded repair/review cycle. The repair receives the review body and all inline
  comments with file locations; edited findings stop publication. Ordinary GitHub **Approve** does not merge or act as
  an intent/spec/plan decision. All triggers use `issue_comment`, whose workflow
  definition comes from the default branch; no privileged PR-sourced workflow is used.

The adapter publishes normal commits to the same feature branch, without force pushes.
Concurrent head changes stop publication. Policy, workflow and agent-instruction edits
require a manual handoff. It stops at delivery: merge, required CI and release follow
existing project controls. Commits made with `GITHUB_TOKEN` may not trigger downstream
workflows; use your reviewed GitHub App integration if those checks need to run automatically.
No token or repository settings are created by this plugin.

Update the pinned plugin intentionally. Its provenance hash invalidates open decisions
when guidance changes. Runs reusing the same approval may leave duplicate presentation
comments, but do not invent new human decisions. The adapter is not an always-on service.
