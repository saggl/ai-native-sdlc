# Review: from starter files to a reusable workflow

Reviewed `main` at `8bd4f6a4e74e9908e83f98b9adb5e81d30d2e8a7` on 2026-10-03 against
the supplied playbook and current Anthropic plugin documentation.

The previous repository already had reusable parts: four skills, shared templates,
a collision-safe installer, provenance hashes and honest enforcement boundaries.
Its main weakness was the amount of process the adopter had to operate manually.

| Finding | Evidence in the previous revision | Effect | Change in 0.2 |
| --- | --- | --- | --- |
| Installation copied a complete package into every repo | `scripts/install.py`; README required a clean pinned clone and local installer | Every project owns another copy; no supported upgrade path | Native marketplace and self-contained versioned plugin |
| Users had to operate the workflow | Four commands and manually supplied `changes/...` paths | More to learn; stage and resumption live with the developer | `/sdlc:start` routes from persisted state |
| Getting started emphasized working in the starter | README's first section: “Start in this repository” | Looks like a demonstration to visit | README begins with installation and use in the user's existing project |
| Approval overhead was prescribed | `.sdlc/workflow.md` required a preparation PR merged before a separate implementation PR | Imposes extra handoffs on every change | Approve committed artifacts in the existing branch/PR flow; separate PRs optional |
| Lifecycle stopped at review | Skills: init, prepare, implement, review; later stages deferred in adoption guide | No reusable delivery/observation handoff | Guided delivery, observation, learning and next-intent routing |
| Validation covered package shape only | `scripts/validate.py`; four installer tests | No deterministic resume or stale-input checks | Real Git tests plus artifact/code/report fingerprints |

The plugin architecture and workflow helper are this project's design decisions.
Anthropic does not prescribe this package, command name, state format or folder layout.
The standard keeps `intent.md`, `spec.md` and `plan.md` as the playbook's shared artifacts.

## Release boundary

This is a concrete guided foundation, not a claim that installing a plugin creates a
fully autonomous engineering organization. Integration credentials, protected gates,
project tests and signals stay with each project. Move a proven transition into CI only
after its inputs, outputs, permissions and escalation path are clear.
