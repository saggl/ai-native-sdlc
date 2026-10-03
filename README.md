# AI-native SDLC starter

A practical, versioned workflow for teams already planning, implementing, reviewing and
fixing code with Claude Code. Preserve intent and decisions, approve behavior and approach
before implementation, and review delivered evidence before merging.

This repository contains a proposed adaptation of Anthropic's playbook, not an official
Anthropic package. It starts with manual gates; human PR approval remains in place.

## Start in this repository
Open it in Claude Code and use `/sdlc-prepare <your next change>`.
The four project skills are in `.claude/skills`. Start with a real small change rather
than designing an entire future product.

## Install into another repository
Use Python 3.10+ and a clean, pinned checkout of this starter. From its root:

```bash
git rev-parse HEAD
python3 scripts/install.py /absolute/path/to/target-repository
```

The installer copies shared templates, workflow and all four skills. It refuses collisions
and does not change existing root instructions. It records the source commit and file hashes.
Commit the installed files in the target repository. Then in Claude Code:

```text
/sdlc-init
/sdlc-prepare Add the first useful capability
```

After human approval of the saved preparation revision:

```text
/sdlc-implement changes/001-first-capability
```

In a fresh Claude Code session:

```text
/sdlc-review changes/001-first-capability
```

These commands guide agents; they do not install repository permissions or approval gates.

## Contents
| Location | Purpose |
| --- | --- |
| `.sdlc/templates/` | Six core document templates, compact change and review report |
| `.claude/skills/` | Init, prepare, implement and review skills |
| [.sdlc/workflow.md](.sdlc/workflow.md) | Roles, approvals, deviations, reuse and pilot rollout |
| [docs/adoption.md](docs/adoption.md) | Practical adoption and responsibility mapping |
| [examples/001-csv-validation](examples/001-csv-validation/intent.md) | Filled illustrative intent/spec/plan |
| [evals/README.md](evals/README.md) | Manual scenarios for checking skill behavior |
| `scripts/` | Safe initial installer and structural package validation |
| `.github/` | PR template and package validation workflow |

## Validate this package
```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```
These checks validate packaging and installer behavior. They do not establish that a
model follows the skills or that a downstream product satisfies its requirements.

## Source and design decisions
See [docs/sources.md](docs/sources.md). Per-change folders, the four-skill split, compact
change option and installer are local design choices. The full source article is not
redistributed here. No corporate internal data or credentials are needed.
