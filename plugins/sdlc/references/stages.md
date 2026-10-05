# Stage actions

Use the shared rules and helper in [workflow.md](workflow.md).
Follow the section matching the next action from `status`.

## Prepare: draft-* or approve-*

Read saved artifacts and actual approval evidence. Start at the earliest missing artifact or
required stale decision. Apply adaptive gates from workflow.md before advancing. Replace template prompts; keep each artifact as short as its decision
allows. Link existing sources and evidence instead of duplicating them.

1. **Intent:** capture problem, affected people/systems, measurable outcome, scope and
   constraints. Ask only questions that change the decision. Present it to its owner
   when outcome ambiguity or project policy requires an intent gate; otherwise draft spec.
2. **Spec:** after any required intent decision, run `draft <id> spec`. Inspect the code and policies.
   Define behavior, failure cases, interfaces and stable `AC-1`, `AC-2` criteria.
   Apply relevant available domain skills. In spec.md, retain the generation request,
   model/harness when known, and applied skill/policy paths and versions or hashes.
   Put repository policy and skill source files in `policy_files` so changes invalidate
   decisions; record external sources with immutable versions where available. State
   unavailable provenance rather than inventing it. For front-end work link the Claude
   Design mock or export in spec.md. Resolve blocking concerns with
   their owner; add a spec gate for unresolved behavior or significant risk, otherwise draft plan.
3. **Plan:** after any required spec decision, run `draft <id> plan`. Use plan mode when available.
   Name real files, a checkbox list of small independently verifiable steps, risks,
   relevant alternatives, a check and expected result for every step and AC,
   and delivery/recovery. Present intent, spec and plan together for approval of the complete approach;
   earlier required decisions still need their own evidence. Do not implement
   product code yet. If plan mode prevents saving, request the needed mode change;
   leaving plan mode is not approval of an unseen artifact. Record later departures in
   plan.md under `## Implementation deviations` in the same commit; material ones
   return to approval.

Use the [approval procedure](workflow.md#team-decisions-on-one-pr) at each required gate.
After plan approval, proceed within the approved scope and permissions.

## Build: implement-and-verify

Read the current approved artifacts and verify their decision evidence.

- Implement one coherent plan step, run its verification and fix failures before advancing.
  Mark its checkbox complete only after the expected result is observed. Keep evidence
  in verification.md; a checked box is not evidence. Commit coherent units with explicit
  paths. If the plan produces an oversized or inseparable change, split the scope before
  coding and obtain any affected decision again. Prefer several small reviewable changes
  over a large diff; do not use arbitrary line-count limits.
- After plan approval, use the harness's authorized execution mode for routine edits.
  Parallel implementation is optional and only appropriate for independent units when
  explicitly requested; preserve each unit's verification and final integrated checks.
- Classify bug fixes with `new --kind bugfix`. After plan approval,
  write a meaningful regression test, run it to confirm the intended bug, and commit
  the still-failing test before changing product code. Use `record-regression` with
  its explicit argv and protected test paths; the helper observes the expected failure.
  Preserve those files during the fix. A changed test or failure log blocks a passing
  verification/review record. Changing the regression scope requires a revised approved
  plan and fresh reproduction, not editing the lock. An exit code alone is not proof of
  the intended bug: inspect its diagnostics and explain the failure in verification.md.
  If meaningful reproduction requires unavailable hardware/environment, stay blocked.
- Run applicable deterministic tests, build, lint and behavioral checks against every AC; fix and repeat. Inspect test changes for
  weakened assertions, skips and lost coverage. Inspect rendered UI when relevant.
  Host tests cannot replace required target, timing or HIL evidence.
- Record harmless file/order deviations with reasons in plan.md
  `## Implementation deviations`. Material behavior, interface, scope or verification
  changes return to the affected decision; never rewrite a plan merely to make code
  look compliant.
- Commit the bounded implementation using explicit paths. Check staged versus working
  content; preserve unrelated work. Run final checks on that committed implementation,
  via the bundled `sdlc:verifier` subagent when available.
- Write verification.md from its template with revision, environment, every AC,
  commands/results, log links, deviations and limits. Failed or unavailable required
  checks mean `blocked`; identify baseline failures separately.

Record the result, commit scoped evidence, and continue to fresh review after a pass.

## Review: review

From the start workflow, delegate to the bundled `sdlc:reviewer` when available. Supply only
the resolved plugin root, target repository, change folder, approved baseline,
implementation revision and verification report; do not suggest a verdict. Otherwise
request a fresh session and stop at that handoff. In Claude Code, use `/sdlc:run review change <id>`; in OpenCode, use
`/sdlc review change <id>`; in Codex, invoke the installed `run` skill with
“review change <id>”.

Review only if you did not implement the change. Read project instructions, REVIEW.md when present,
policies, approved artifacts, state.json and actual decision evidence.
Inspect the complete relevant diff and surrounding code, including untracked work.
Check logic, security, compatibility, every AC, test strength and plan deviations.
Re-run relevant safe checks; distinguish observations from the author's claims.
Do not edit source, tests, policy, approval records or release configuration while
reviewing. Safe tests may create ordinary build outputs.

Run Bugs, Security and Compliance (intent/spec/plan alignment) passes; apply REVIEW.md
when present and end Findings with `Tally: Bugs <n>, Security <n>, Compliance <n>`. A repeated mistake should become a short lesson in the project agent instructions;
flag stale instructions and link deeper repository knowledge instead of expanding them.

Write review.md from its template: reviewed revision/files, fresh-session provenance,
findings, criterion evidence and limitations. Missing required evidence, material
unapproved deviations or unresolved important findings mean `blocked`. Self-review
cannot pass this stage. The caller persists a delegated reviewer's report.

The implementation session fixes within scope, repeats verification and obtains fresh
review of changed code, rechecking applicable findings. Record review and report core readiness on
a pass; continue to delivery only when requested or required by project policy. Review evidence does not authorize merge or release.

## Deliver: deliver (optional follow-up)

Use the existing host, CI and release process. Update the existing change PR (create
one only if absent), or its equivalent, linking
intent/spec/plan, decisions and evidence. Explain behavior, risks, open decisions and
rollback. Apply the [project merge gate](workflow.md#team-decisions-on-one-pr).

Within existing authorization, fix actionable review/CI failures and repeat verification
and fresh review after code changes. Do not change permissions, branch rules, required
checks or merge/release policy. Unavailable tools require a concrete handoff.

Tier autonomy by environment: dev free, staging limited, prod gated by the release
authority or a hook gate. Rollback is one rehearsed command recorded in project.json
`delivery`. The agent writes only via PR.

Write delivery.md from observed PR/CI/release evidence. A PR opened is not a deployment.
Record `blocked` until the spec's delivery boundary has actually been reached; that
boundary may be a firmware/library artifact handoff. Record `passed` only with evidence.

## Observe: observe-and-learn (optional follow-up)

Read the agreed outcome signal through available project tools. Respect its observation
window. Write learning.md with expected versus observed outcome, time, evidence, owner
and triage. Missing access or time leaves observation pending; promise no background job.

Intake: monitor findings (bands), Claude Security scan findings and Claude Tag,
channel or ticket requests. A bounded fix becomes a patch PR through the review gate;
a wider one becomes an intent.md registered with `new --adopt`. Dismissals need a
reason. A fixed class or incident gets an eval case; a post-mortem goes to learning.md
with lessons in CLAUDE.md or a skill.

For incidents or unmet outcomes, capture a linked next intent for its normal human
decision and add a relevant regression/eval case. Retain useful recurring lessons in
CLAUDE.md or a project skill; do not invent a lesson to fill a heading. If that changes
policy or code, repeat affected decisions, verification and review before closing.

Record learning as `passed` only after observation and triage, even if the product
outcome was below target. Completion preserves history; follow-up work gets a new intent.

