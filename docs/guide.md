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
