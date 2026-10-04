# Tasks

Verify every task with: `python3 scripts/validate.py && python3 -m unittest discover -s tests`

## Phase 1: Review findings

- [x] A1: Rename the policy template and detect case collisions
  - Acceptance: `templates/review-policy.md` exists; `templates/REVIEW.md` is gone from
    git; `setup.md` points to the new name; validate fails on any two tracked paths that
    are equal case-insensitively.
  - Verify: test with an injected collision list → error; `git status` clean on macOS.
  - Files: plugins/sdlc/templates/review-policy.md, plugins/sdlc/references/setup.md, scripts/validate.py, tests/test_validate.py (new)
- [x] A2: Fix the stale command in migrate.md
  - Acceptance: `/sdlc:run` used; the `migrate.md` exemption is removed from the
    obsolete-command check.
  - Verify: validate passes; a planted removed start command fails.
  - Files: plugins/sdlc/references/migrate.md, scripts/validate.py
- [x] A3: Compute the code snapshot once per `all_status`
  - Acceptance: `status(root, slug, code=None)`; `all_status` passes one precomputed digest.
  - Verify: test patches `code_snapshot` and counts calls == 1 with 2 open changes.
  - Files: plugins/sdlc/scripts/sdlc.py, tests/test_workflow.py
- [x] A4: Scope provenance to guidance and report `workflow_changed`
  - Acceptance: the hash covers only the guidance paths; validity ignores the workflow
    hash; `status` returns `workflow_changed: true` with an unchanged `next`; legacy
    records still read.
  - Verify: update `test_workflow_provenance_detects_guidance_changes`; add a test that a
    manifest-only change doesn't alter the hash.
  - Files: plugins/sdlc/scripts/sdlc.py, plugins/sdlc/references/workflow.md, tests/test_workflow.py

**CP1:** suite green, collision gone.

## Phase 2: Helper additions

- [x] T5: Plan deviations section outside the approval snapshot
  - Acceptance: text after `## Implementation deviations` in plan.md doesn't change the
    snapshot; edits above it do. The template has the heading. stages.md tells the agent
    to record departures there in the same commit and to send material ones back to approval.
  - Verify: two tests (append below → still approved; edit above → approve-plan).
  - Files: sdlc.py, templates/plan.md, references/stages.md, tests/test_workflow.py
- [x] T6: `lock-tests <id> --paths …`
  - Acceptance: requires committed, existing paths; stores `locked_tests` in state;
    `record-result` refuses when any locked file differs from its hash.
  - Verify: lock → edit test → commit → record verification raises; unchanged → passes.
  - Files: sdlc.py, references/workflow.md, references/stages.md, tests/test_workflow.py
- [x] T7: `new <id> --adopt`
  - Acceptance: uses the existing `changes/<id>/intent.md`, creates state.json only, and
    refuses when state.json exists or intent is missing; the title comes from `--title`.
  - Verify: tests for adopt, missing intent and existing state.
  - Files: sdlc.py, references/workflow.md, tests/test_workflow.py

**CP2:** suite green; helper diff ≤ 50 lines.

## Phase 3: Deterministic layer (hooks)

- [x] T8: `hooks/guard.py` edit guard
  - Acceptance: PreToolUse Edit/Write/MultiEdit/NotebookEdit: exit 2 with a reason for
    a `protected_paths` glob, a path in any open change's `locked_tests`, or content
    matching secret patterns (private key header, AWS key, `ghp_`/`sk-ant-` tokens).
    Exit 0 when not configured.
  - Verify: tests/test_guard.py feeds JSON stdin through subprocess.
  - Files: plugins/sdlc/hooks/guard.py, tests/test_guard.py
- [x] T9: Guard approval gates and format-after-edit
  - Acceptance: PreToolUse Bash: the first matching `gates` entry without its
    `require_env` → `block` (exit 2) or `ask` (JSON `permissionDecision: ask`), each with
    its reason and approval route. PostToolUse Edit/Write runs `commands.format` with the
    file path as an argument when configured (list argv, no shell).
  - Verify: tests for block, ask, allow-with-env and format invoked (a stub command
    writes a marker file).
  - Files: hooks/guard.py, tests/test_guard.py
- [x] T10: `install hooks` and setup offer
  - Acceptance: copies the guard to `.claude/hooks/sdlc-guard.py`; merges PreToolUse
    and PostToolUse entries into `.claude/settings.json`, preserving other keys; running
    it again is a no-op; refuses when a differing sdlc-guard.py exists. setup.md offers
    it and installs only on a yes; guide covers managed settings for non-negotiable gates.
  - Verify: tests for fresh install, merge with existing settings, idempotence and conflict.
  - Files: sdlc.py, references/setup.md, tests/test_workflow.py

**CP3:** temp-repo end-to-end: the 4 block cases plus the env-approved deploy pass.

## Phase 4: Loop automation (CI)

- [x] T11: `scripts/bands.py` plus `ci/bands.json`
  - Acceptance: reads a JSON number array; baseline = all but the last `window` points;
    WE rule 1 (1 point >3σ) → propose; rule 2 (2 of 3 >2σ) → diagnose; rules 3/4 (4 of 5
    >1σ, 8 on one side) → diagnose; a single >1σ point → log; fewer than `min_points`
    → log. Prints `{"tier", "rule", "mean", "sigma", "last"}`.
  - Verify: tests/test_bands.py with spike, drift, noise and short series.
  - Files: plugins/sdlc/scripts/bands.py, plugins/sdlc/ci/bands.json, tests/test_bands.py
- [x] T12: CI templates and `install <evals|review|handoff|monitor>`
  - Acceptance:
    - evals.yml: PR paths CLAUDE.md, `.claude/**`, REVIEW.md plus nightly; runs
      `evals/*.json` through `claude -p`; fails below `EVAL_PASS_RATE`.
    - review.yml: claude-code-action review with REVIEW.md; `@claude` fix loop; failed-build triage.
    - handoff.yml: on push to main touching `changes/*/state.json` with a new intent
      approval → `claude -p` drafts spec on a branch and opens a PR.
    - monitor.yml: cron → metric_command → bands.py; diagnose runs read-only `claude -p`;
      propose writes intent.md, runs `new --adopt` and opens a PR.
    - Permissions are minimal; no production credentials.
    - install copies to `.github/workflows/sdlc-<name>.yml` (monitor also copies
      bands.py/bands.json to `.sdlc/`) and refuses to overwrite.
  - Verify: tests: install creates files, refuses a differing existing file, running it
    again is a no-op; validate checks each template has `on:`, `permissions:` and `claude`.
  - Files: plugins/sdlc/ci/*.yml, sdlc.py, scripts/validate.py, tests/test_workflow.py
- [x] T13: This repo's own agent eval CI
  - Acceptance: `.github/workflows/agent-evals.yml` runs `evals/run.py` on PRs touching
    `plugins/sdlc/**`, `evals/**`, plus a weekly run; skips with a notice when
    `ANTHROPIC_API_KEY` is absent; uploads the results JSON.
  - Verify: validate checks presence; the PR states whether it ran.
  - Files: .github/workflows/agent-evals.yml, evals/README.md

**CP4:** suite green; install idempotent; templates validated.

## Phase 5: Instructions and proof

- [x] T14: Stage instructions for the remaining plays
  - Acceptance:
    - Build: auto mode for routine work after plan approval; split independent steps
      across `claude --worktree`, starting with 2–3; verifier subagent as the final check.
    - Review: Bugs/Security/Compliance passes; a mistake flagged twice → CLAUDE.md; flag
      an outdated CLAUDE.md; `Tally:` line.
    - Deliver: tiers by environment, single rehearsed rollback, agent writes only through PRs.
    - Observe: intake rule for scans/Tag/tickets (bounded → patch PR; wide → intent via
      `new --adopt`; dismiss with a reason; fixed class → eval).
    - Spec: link the Claude Design mock for front-end work.
    - `agents/verifier.md` added; `review-policy.md` matches the playbook structure.
    - No net growth of stages.md beyond about 25 lines.
  - Verify: validate links; existing eval checks still pass.
  - Files: references/stages.md, agents/verifier.md, templates/review-policy.md, templates/review.md, templates/spec.md
- [x] T15: Coverage table, validation, release
  - Acceptance: `docs/guide.md#playbook-coverage` lists 16 plays with asset links;
    validate fails when the table has fewer than 16 rows or a link is broken; the
    "No hooks…" statements in README/guide/workflow.md are replaced with "opt-in only";
    README links the table; both manifests at 0.4.0; guide update notes mention the
    one-time `workflow_changed`.
  - Verify: full suite; planted missing asset fails validate; `wc -l` size budget checked
    against SPEC criterion 6.
  - Files: docs/guide.md, README.md, plugins/sdlc/references/workflow.md, scripts/validate.py, both plugin.json

**CP5:** all green; 16/16 coverage; PR lists native runtimes exercised (or none).
