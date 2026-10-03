# AI-native SDLC

**Describe the change. Approve the decisions. Let Claude carry the work forward.**

A Claude Code plugin you use inside your own projects. It saves the intent, specification,
plan and evidence in Git, guides you through the human decisions, and resumes where you
left off. Based on [Anthropic's AI-native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook).

## Install once

In Claude Code:

```text
/plugin marketplace add saggl/ai-native-sdlc
/plugin install sdlc@ai-native-sdlc
```

Use a current Claude Code with plugin support, Git and Python 3.10+. The repository is
currently private: installation requires Git access to it. Open a new session or use
`/reload-plugins` after installation if the commands are not yet visible.

## Use in your project

Open Claude Code in the repository you actually work on:

```text
/sdlc:start Add CSV import with clear errors for invalid rows
```

Claude inspects the project, sets up its context, and starts the change. You describe the
problem and review the decisions. Claude writes the documents and runs the workflow.

| You do | Claude does |
| --- | --- |
| Explain the problem | Save a concise `intent.md` |
| Approve the intent | Inspect the code and draft `spec.md` |
| Approve the required behavior | Draft `plan.md`, including checks and risks |
| Approve the approach | Implement, test, fix and obtain a fresh review |
| Make the required release decision | Work through existing PR/CI/release tools and record delivery |
| Review the observed outcome | Capture learning and route follow-up work into a new intent |

Each approval concerns the saved artifact you just reviewed. Claude records it and
continues; you do not need another command between stages. Small fixes get short
artifacts. Larger changes get the detail their decisions need.

Tomorrow, or in a fresh session:

```text
/sdlc:start
```

It resumes the open change. If several are open, it asks which one. For a quick progress
check, use `/sdlc:status`. A fresh reviewer can use `/sdlc:review <change-id>`.

## What stays in your project

- `.sdlc/project.json`: project commands, policies, owners and delivery context.
- `changes/<change-id>/`: intent, spec, plan, human decision records and observed evidence.
- Small relevant additions to project instructions, preserving your existing rules.

The shared skills, templates and helper stay in the installed plugin. Update them once
through the plugin manager; each project's decisions and custom instructions stay put.
Nothing in this repository needs to become your application's starting code.

## What this version delivers

**Version 0.2 is a guided lifecycle.** It includes automatic setup, resumable stages,
checks for changed approval/evidence inputs, a fresh reviewer, and instructions through
delivery and observation. It works with the project's available engineering tools and
verification environments, including Python and embedded projects.

The helper records evidence; it does not authenticate approvals, judge correctness or
replace repository permissions. Required target tests remain pending until run on the
target. Actual merging, releasing and observation depend on the project's tools and
authorization. Background monitoring, event-triggered agents and automatic merge policy
are project integrations, not installed features. See the [playbook coverage](docs/playbook-coverage.md).

## For teams and maintainers

- [Adopt, update or migrate](docs/adoption.md)
- [Review of the previous package and the design changes](docs/review.md)
- [Sources and implementation choices](docs/sources.md)
- [Behavior evaluation scenarios](evals/README.md)
- [Executed validation and remaining runtime checks](docs/validation.md)

Validate package structure and the real Git/file lifecycle:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

Test the unmerged plugin from a local checkout while inside a disposable project:

```bash
claude --plugin-dir /absolute/path/to/ai-native-sdlc/plugins/sdlc
```

Then use `/sdlc:start`. Package tests and agent walkthroughs do not replace a smoke test
in your actual Claude Code environment.
