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
   Apply relevant available domain skills. In spec.md, retain the generation request,
   model/harness when known, and applied skill/policy paths and versions or hashes.
   Put repository policy and skill source files in `policy_files` so changes invalidate
   decisions; record external sources with immutable versions where available. State
   unavailable provenance rather than inventing it. For front-end work link the Claude
   Design mock or export in spec.md. Resolve blocking concerns with
   their owner; present behavior for human approval.
3. **Plan:** after spec approval, run `draft <id> plan`. Use plan mode when available.
   Name real files, ordered steps, risks, relevant alternatives, a check for every AC,
   and delivery/recovery. Present the approach for technical approval. Do not implement
   product code yet. If plan mode prevents saving, request the needed mode change;
   leaving plan mode is not approval of an unseen artifact. Record later departures in
   plan.md under `## Implementation deviations` in the same commit; material ones
   return to approval.

Use the [approval procedure](workflow.md#team-decisions-on-one-pr) at each handoff.
After plan approval, proceed within the approved scope and permissions.

## Build: implement-and-verify

Read the current approved artifacts and verify their decision evidence.

- Implement the plan. After plan approval, auto-accept routine work (small blast
  radius, covered by tests) and review the artifacts afterwards. Split independent plan
  steps across `claude --worktree <name>` sessions: start with 2-3 and add more only
  while review keeps up.
- For bugs, commit a meaningful failing regression test before the fix when feasible,
  then `lock-tests` it so later results refuse if it changes.
- Run applicable checks against every AC; fix and repeat. Inspect test changes for
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

Review only if you did not implement the change. Read project instructions, REVIEW.md,
policies, approved artifacts, state.json and actual decision evidence.
Inspect the complete relevant diff and surrounding code, including untracked work.
Check logic, security, compatibility, every AC, test strength and plan deviations.
Re-run relevant safe checks; distinguish observations from the author's claims.
Do not edit source, tests, policy, approval records or release configuration while
reviewing. Safe tests may create ordinary build outputs.

Run the Bugs, Security and Compliance passes from REVIEW.md and end Findings with its
`Tally:` line. A mistake flagged a second time goes into CLAUDE.md; flag when the change
makes CLAUDE.md outdated.

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

## Observe: observe-and-learn

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

