# Workflow contract

Use Python 3.10+ and Git. Select `python3`, `python`, or `py -3` by checking the local
interpreter. If unavailable, explain the missing prerequisite. Do not install it silently.
Invoke the bundled helper using its absolute path and the target Git root:

```text
python3 "<plugin-root>/scripts/sdlc.py" --root "<project-root>" status
```

`<plugin-root>` is resolved by the calling skill: `${CLAUDE_PLUGIN_ROOT}` in Claude
Code or the installed package path in Codex/OpenCode. Quote arguments safely; treat user
text as arguments, never interpolate it as executable shell code.

## Helper operations (the agent runs these)

| Operation after `--root <project-root>` | Effect |
| --- | --- |
| `setup` | Create `.sdlc/project.json` once; preserve existing content |
| `new <id> --title <title> [--kind bugfix]` | Create a unique change folder, state and intent template |
| `new <id> --title <title> --adopt [--kind bugfix]` | Register an existing committed intent from a connector, monitor, scan or Tag without overwriting it |
| `install <hooks\|monitor>` | Opt-in, only on the user’s explicit yes; install the guard or experimental monitor without overwriting files |
| `status [id]` | Infer next stage; check saved artifact and evidence fingerprints; may report `workflow_changed: true` |
| `draft <id> spec` / `draft <id> plan` | Create the next template after prior decisions |
| `require-decision <id> <intent\|spec\|plan> --reason <reason>` | Add an earlier human gate for ambiguity or significant risk; never removes gates |
| `record-approval <id> <intent\|spec\|plan> --by <human> --evidence <reference> --decision <exact-decision>` | Record a real human decision on committed artifacts |
| `record-regression <id> --file <test-path> --command-json <argv> [--expected-exit 1]` | Observe a failing committed check and protect its test files |
| `record-result <id> <verification\|review\|delivery\|learning> --outcome <passed\|blocked> --report <relative-path>` | Bind a report to the code and upstream artifacts |

Reports are named `verification.md`, `review.md`, `delivery.md`, `learning.md` in that
change's folder. Render them from the corresponding bundled template. Commit the
artifacts and records at handoffs, using explicitly scoped staging; preserve unrelated
work. A new repo can start with no commits; reviewed artifacts must be committed before
an approval is recorded. Git history, not a shared example project, holds the decisions.

## Team decisions on one PR

Follow existing project policy. For GitHub teams, use one draft PR per change when
publishing is authorized. Human defaults: product/task owner for intent, product/domain
owner for spec, implementing engineer for a routine plan, teammate for significant risk
(safety, authentication, public interfaces, migrations or architecture). A person may
hold several roles; agents cannot self-approve or impersonate owners. Ask only for the
owner needed now. Default team merge requires one teammate and passing required checks;
release follows the existing release authority. Notifications and review requests require
authorization.

New projects use `approval_stages: ["plan"]`: draft concise intent, spec and plan,
then present all three together for one `Plan approved` decision. That decision binds
all three artifacts; it does not fabricate separate intent/spec approvals. Its owner
must have authority for the outcome, behavior and approach; involve the applicable
owners when one person cannot make all those decisions.

Before drafting onward, assess ambiguity and risk. For unresolved outcomes, behavior,
scope, security, public contracts, migrations or significant architecture changes, use
`require-decision` at the affected intent/spec stage with a concrete reason, then ask
that owner. Put the concern in the artifact. Do not implement while it is unresolved.
Escalation is additive and survives resume. Plan approval remains mandatory before code.
Material departures return to the affected decision; never silently classify them as routine.

Project policy can require `approval_stages: ["intent", "spec", "plan"]` or just spec
and plan. Configurations without this key retain the original three-gate policy; do
not migrate them without an explicit project decision. The helper records gates and
snapshots, but the agent must judge risk and verify actual authority and resolution.

At each required gate:

1. Commit the artifact. Persist a presentation in the PR or durable decision record
   containing change ID, stage, path, full commit SHA and revision-pinned artifact link.
   Ask its owner for `Intent approved`, `Spec approved` or `Plan approved`.
2. Retrieve the actual response and verify the author's authority. Explicit acceptance
   must identify the artifact; obvious typos are fine. Generic praise, reactions, labels,
   checkboxes, commit authors, generated status or a Git merge are not approval. A reply
   with an unresolved requested change is not approval either.
3. Bind the response to its presentation through a thread or explicit reference. Never
   guess the revision from timestamps, current HEAD or unavailable chat. Ask when more
   than one presentation could match. Compare approved content and upstream policy with
   current content; stop for stale, withdrawn, inaccessible or unauthorized decisions.
4. Use `record-approval` with the human, exact quote, and both presentation and response
   references in `--evidence`; commit the state record. Policy-permitted chat decisions
   retain the quote and recoverable revision context, clearly identified as chat evidence.

On resume, recheck the sources and reuse unchanged, still-valid decisions. Implementation
commits alone do not revoke artifact approvals. GitHub's final approving review is a
separate project merge gate; stage replies and agent review do not satisfy it. Solo and
non-GitHub projects keep their existing merge/release policy. The helper neither verifies
identity nor parses comments: the agent inspects sources through available tools.

## Rules shared by every stage

- Keep artifacts short and create the next needed one; routine preparation may draft
  all three before presenting the combined decision. Link authoritative sources.
  Work on one change per worktree/session; never overwrite another session's state.
- Artifact/policy changes invalidate affected downstream records. Code, report or earlier
  result changes invalidate affected results. Preserve history; never repair fingerprints
  to hide changes. Records store revisions and hashes, not authenticated authorization.
  New decisions and results also identify the installed workflow by version and content
  hash. `workflow_changed: true` means installed guidance differs from the guidance that
  produced the latest record for a stage or result: recheck and re-record affected
  decisions/results against current guidance. It is not a missing approval.
- Plan task checkbox state in `## Implementation` is progress only: changing a tick
  preserves approval, but task wording, order and verification changes require a new
  decision. The full plan still binds verification and review evidence.
- Plan text from `## Implementation deviations` to the end is outside the plan approval
  snapshot; verification and review bind to the full plan so later deviations need fresh
  evidence. Optional `project.json` keys used by the guard: `protected_paths` (globs),
  `gates` (`[{match, require_env, action: block|ask, reason}]`), `commands.format` (argv).
  Gate regexes match the full Bash command, including quoted text and heredocs. They
  may also flag prose mentioning a gated command; they are not a shell parser or sandbox.
- Commit implementation before final verification and result recording, with scoped
  staging. Staged and tested content must agree. Evidence-only commits do not invalidate
  results. Preserve unrelated work.
- A `passed` result needs observed success of every required check for that stage.
  Record `blocked` with the missing evidence when a required check/environment is
  unavailable; agent assurance is insufficient.
- The configured changes directory is evidence-only, never product code. Ignored/generated
  outputs need CI/build or target evidence references; submodules need a project adapter.
- Completed changes are historical. New incidents start a linked intent rather than
  rewriting approved history.

Core readiness requires passed verification and independent review; the helper reports
`ready-for-merge`, not delivered or observed. New projects use `followup_stages: []`.
Projects may require `["delivery"]` or `["delivery", "learning"]` before completion.
Missing configuration preserves the original full lifecycle. Set policy during setup;
do not weaken an existing requirement to make a task appear finished. Explicitly
requested follow-up can record delivery/learning through the same entry point, using
real merge/release/observation evidence and the normal prerequisites.

Use [stage actions](stages.md) for execution. Existing branch rules, CI, protected
environments and permissions remain authoritative. Hooks and the monitor are opt-in,
installed only through `install` after the user’s explicit yes; nothing is active by default.
No credentials, auto-merge or deployment access are installed. Only `record-regression`
runs a supplied project check; the helper never calls models. An optional GitHub adapter
is distributed separately and installed only when requested.
