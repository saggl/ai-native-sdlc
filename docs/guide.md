# Team setup and maintenance

## Adopt and update

Start with one real change in an existing or empty Git repository using the README.
Claude discovers project commands and preserves existing instructions. One person can
own several decisions; team approvals use the existing review system.

For a shared project, run these in its directory:

```bash
claude plugin marketplace add saggl/ai-native-sdlc
claude plugin install sdlc@ai-native-sdlc --scope project
```

Review and commit the generated plugin settings. Collaborators need repository access
and a local install. For wider use, grant access or use an approved internal marketplace.

Update from a terminal:

```bash
claude plugin marketplace update ai-native-sdlc
claude plugin update sdlc@ai-native-sdlc
```

Use `/reload-plugins` or a new session. Updates change the shared plugin, not the
project's decisions or configuration. Teams can roll out a tested marketplace/ref.
For the old copied 0.1 package, follow the [migration instructions](../plugins/sdlc/references/migrate.md).
Existing 0.2 records need no migration.

## Team workflow

Use one branch and PR per change, from the first intent through implementation.
Agree on the owners during setup; one person can hold several roles. These are starting
defaults for teams. Preserve existing project policy and record agreed adaptations in
REVIEW.md; never silently change repository settings.

| Decision | Default owner | Record |
| --- | --- | --- |
| Intent: problem, scope and value | Product or delegated task owner | Explicit approval of the presented intent |
| Spec: behavior and constraints | Product/domain owner | Explicit approval of the presented spec |
| Plan: approach and verification | Implementing engineer; teammate for significant risk | Explicit approval of the presented plan |
| Implementation and fixes within scope | Claude, with tests and fresh agent review | Verification and review evidence; no per-edit human approval |
| Merge | One teammate, with required checks passing | GitHub approving review |
| Release | Existing release authority | Existing release decision |

The engineer driving Claude can approve a routine plan. Claude cannot approve its own
work or impersonate that engineer. Escalate significant risk such as changed safety
behavior, authentication, public interfaces, data migrations or architecture.

For example, a CSV import follows this sequence:

1. Claude saves and commits `changes/csv-import/intent.md`. With permission to push/open
   a PR, it opens a draft PR; otherwise it provides the local artifact and next action.
2. Claude saves a presentation in the PR with the change ID, stage, full commit SHA
   and revision-pinned artifact link, then asks the product owner to reply to that
   presentation with `Intent approved` or feedback. The owner need not type the SHA.
3. Resume `/sdlc:start`. Claude retrieves the response, checks its author against the
   agreed owner and binds the decision to the exact revision in the saved presentation.
   It retains both references; if the reply could refer to multiple revisions, it asks
   which one rather than guessing from the PR head or timestamps. Repeat with `Spec approved` and `Plan approved`, using their respective owners. Exact
   wording is not a parser command: obvious typos are acceptable when the approval and
   artifact are still unambiguous. Generic positive feedback, reactions or approval with
   an unresolved change request do not count. An authorized engineer's explicit chat
   approval of the saved plan is also usable when team policy allows; retain its
   quote/context and do not represent it as a GitHub review.
4. Claude implements, tests and obtains fresh agent review on the same branch. Material
   scope or behavior changes return to the relevant human decision.
5. Mark the PR ready and request a teammate's review. They review behavior, evidence,
   findings and relevant code, then choose GitHub **Approve**. Merge only when project
   requirements are met; release through the existing process.

Labels may show progress but do not count as decisions. A stage approval must explicitly
communicate approval and identify the artifact (intent, spec or plan); it does not satisfy
GitHub's required approving review.
New code alone does not invalidate unchanged artifact approvals. Changed upstream
artifacts or policy make affected records stale and require the relevant decisions again.
GitHub can separately dismiss final PR approvals when the diff changes, depending on
branch settings. See [GitHub reviews](https://docs.github.com/en/pull-requests/reference/pull-request-reviews)
and [branch protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).

The current helper records evidence and detects changed content. Claude inspects approval
sources through available tools; there is no built-in GitHub identity/role enforcement,
comment parser or background watcher. If evidence is inaccessible or the approver's role
is unclear, stop at that decision. Resume manually with `/sdlc:start` after a response.
Intent, spec and plan remain separate sequential decisions in this version.

## Extend when needed

Keep project commands and recurring mistakes in CLAUDE.md. Put reusable domain policy
in project/company skills. Link authoritative Jira, Polarion or Teamcenter records;
do not copy their contents into a second source of truth.

For embedded work, distinguish host tests, cross-build, simulation and target/HIL
evidence. A firmware delivery can be an agreed artifact handoff. Missing required
hardware evidence remains a blocker.

The helper creates files, records decisions and checks for stale inputs. Claude uses
the project's tools to build, test, review, deliver and observe. The helper never calls
a model or executes product commands. Skills and local records are not access controls:
authenticated approvals, branch rules, CI and protected environments belong to the project.
No hooks, credentials, background runner or automatic merge/deploy policy are installed.

## Validate a change

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

The tests exercise real Git repositories: setup preservation, resume, changed decisions,
stale evidence, filesystem boundaries and lifecycle completion. CI runs them on Linux,
Windows and macOS. Passing Python tests does not prove agent behavior.

Use the [behavior evaluations](../evals/README.md) for instruction changes. Test in
Claude Code from a disposable project:

```bash
claude --plugin-dir /absolute/path/to/ai-native-sdlc/plugins/sdlc
```

Run `/sdlc:start` through a small real task. Check native installation, permissions,
reviewer delegation and delivery with the intended tools. Record observed results and
unavailable checks in the PR. Bump `plugins/sdlc/.claude-plugin/plugin.json` for release.

## Basis

This independent implementation follows
[Anthropic's playbook](https://claude.com/blog/the-ai-native-sdlc-playbook):
committed decisions, human judgment, feedback loops and learning feeding the next intent.
The command names, folder layout and local records are this project's choices.

Packaging references: [plugins](https://code.claude.com/docs/en/plugins),
[marketplaces](https://code.claude.com/docs/en/plugin-marketplaces),
[skills](https://code.claude.com/docs/en/skills) and
[plugin CLI](https://code.claude.com/docs/en/plugins/cli-reference).
