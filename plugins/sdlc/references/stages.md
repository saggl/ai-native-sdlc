# Stage actions

Use the shared rules and helper in [workflow.md](workflow.md).
Follow the section matching the next action from `status`.

## Prepare: draft-* or approve-*

Read saved artifacts and actual approval evidence. Start at the earliest missing or
stale decision. Replace template prompts; keep each artifact as short as its decision
allows. Link existing sources and evidence instead of duplicating them.

1. **Intent:** capture problem, affected people/systems, measurable outcome, scope and
   constraints. Ask only questions that change the decision. Present it to its owner
   using the team handoff in workflow.md when applicable.
2. **Spec:** after intent approval, run `draft <id> spec`. Inspect the code and policies.
   Define behavior, failure cases, interfaces and stable `AC-1`, `AC-2` criteria.
   Resolve blocking concerns with their owner; present behavior for human approval.
3. **Plan:** after spec approval, run `draft <id> plan`. Use plan mode when available.
   Name real files, ordered steps, risks, relevant alternatives, a check for every AC,
   and delivery/recovery. Present the approach for technical approval. Do not implement
   product code yet. If plan mode prevents saving, request the needed mode change;
   leaving plan mode is not approval of an unseen artifact.

Commit the exact reviewed artifact before `record-approval`; then commit its state
record. Preserve the actual human's decision, quote/context or retrievable review,
source task and policy references. Never infer approval from generated fields or a
commit author. Reuse evidenced approval for unchanged content; get a new decision for
changed content. After plan approval, proceed within the approved scope and permissions.

## Build: implement-and-verify

Read the current approved artifacts and verify their decision evidence.

- Implement the plan. For bugs, demonstrate a meaningful failing regression check
  before the fix when feasible.
- Run applicable checks against every AC; fix and repeat. Inspect test changes for
  weakened assertions, skips and lost coverage. Inspect rendered UI when relevant.
  Host tests cannot replace required target, timing or HIL evidence.
- Record harmless file/order deviations with reasons in verification.md. Material
  behavior, interface, scope or verification changes return to the affected decision;
  never rewrite a plan merely to make code look compliant.
- Commit the bounded implementation using explicit paths. Check staged versus working
  content; preserve unrelated work. Run final checks on that committed implementation.
- Write verification.md from its template with revision, environment, every AC,
  commands/results, log links, deviations and limits. Failed or unavailable required
  checks mean `blocked`; identify baseline failures separately.

Record the result, commit scoped evidence, and continue to fresh review after a pass.

## Review: review

For `/sdlc:start`, delegate to the bundled `sdlc:reviewer` when available. Supply only
the target repository, change folder, approved baseline, implementation revision and
verification report; do not suggest a verdict. Otherwise request a fresh session with
`/sdlc:review <id>` and stop at that handoff.

For `/sdlc:review`, review yourself only if you did not implement the change. Read project
instructions, REVIEW.md, policies, approved artifacts and actual decision evidence.
Inspect the complete relevant diff and surrounding code, including untracked work.
Check logic, security, compatibility, every AC, test strength and plan deviations.
Re-run relevant safe checks; distinguish observations from the author's claims.
Do not edit product code while reviewing.

Write review.md from its template: reviewed revision/files, fresh-session provenance,
findings, criterion evidence and limitations. Missing required evidence, material
unapproved deviations or unresolved important findings mean `blocked`. Self-review
cannot pass this stage. The caller persists a delegated reviewer's report.

The implementation session fixes within scope, repeats verification and obtains fresh
review of changed code, rechecking applicable findings. Record review and continue on
a pass. Review evidence does not authorize merge or release.

## Deliver: deliver

Use the existing host, CI and release process. Update the existing change PR (create
one only if absent), or its equivalent, linking
intent/spec/plan, decisions and evidence. Explain behavior, risks, open decisions and
rollback. For GitHub teams using the agreed teammate merge gate, obtain that teammate's
final GitHub approving review and required checks. Stage comments and an agent's review
report do not replace this decision. For solo projects or other hosts, follow the existing
merge/release policy; do not invent a teammate or GitHub requirement. A separate
preparation PR is optional.

Within existing authorization, fix actionable review/CI failures and repeat verification
and fresh review after code changes. Do not change permissions, branch rules, required
checks or merge/release policy. Unavailable tools require a concrete handoff.

Write delivery.md from observed PR/CI/release evidence. A PR opened is not a deployment.
Record `blocked` until the spec's delivery boundary has actually been reached; that
boundary may be a firmware/library artifact handoff. Record `passed` only with evidence.

## Observe: observe-and-learn

Read the agreed outcome signal through available project tools. Respect its observation
window. Write learning.md with expected versus observed outcome, time, evidence, owner
and triage. Missing access or time leaves observation pending; promise no background job.

For incidents or unmet outcomes, capture a linked next intent for its normal human
decision and add a relevant regression/eval case. Retain useful recurring lessons in
CLAUDE.md or a project skill; do not invent a lesson to fill a heading. If that changes
policy or code, repeat affected decisions, verification and review before closing.

Record learning as `passed` only after observation and triage, even if the product
outcome was below target. Completion preserves history; follow-up work gets a new intent.
