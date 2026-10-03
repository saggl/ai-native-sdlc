# AI-native SDLC

**Intent → Spec → Plan → Code**

The smallest useful foundation for applying [Anthropic's AI-native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook) with Claude Code.

Humans approve the decisions. Claude carries the work forward.

## Install

```text
/plugin marketplace add saggl/ai-native-sdlc
/plugin install sdlc@ai-native-sdlc
```

## Use

From the repository you want to change:

```text
/sdlc:start Add CSV import with clear errors for invalid rows
```

Claude creates one folder:

```text
changes/<change>/
├── intent.md
├── spec.md
└── plan.md
```

The workflow is deliberately simple:

1. Claude drafts `intent.md`. You approve the problem and desired outcome.
2. Claude drafts `spec.md`. You approve what the solution must do.
3. Claude drafts `plan.md`. You approve how it will be implemented and verified.
4. Claude implements, verifies, and reviews the diff against the three approved artifacts.

Run `/sdlc:start` again to resume. No database, state file, workflow engine, or second command is required. The artifacts and Git history are the state.

## Why only this?

The playbook is much larger. This repository intentionally starts with its reusable core: committed artifacts that move human attention from reviewing generated code line-by-line toward approving intent, specification, and plan.

Use your repository's existing tests, CI, branch protection, PR process, security controls, and deployment flow. Add skills, hooks, evals, autonomous loops, or deployment automation only when a real need justifies them.

**Rule for this repository:** if removing something does not break the core workflow, remove it.
