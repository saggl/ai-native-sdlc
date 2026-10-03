# AI SDLC workflow

## Start small
Pilot one repository and five real changes. Run transitions manually before automation.
Persist decisions you already make with Claude; keep documents concise.
Use changes/<id>-<slug>/{intent,spec,plan}.md per meaningful change.
For a bounded low-risk fix, change.md may combine the three sections.
Never replace historical artifacts with an unrelated feature.

## Gates and accountability
1. The originator and Claude draft intent. The product owner approves scope and value.
2. Claude inspects the repository and drafts spec. The owner approves behavior; involve the
   technical lead for material technical constraints. Resolve blocking questions.
3. Claude drafts plan. A responsible engineer approves approach and verification.
4. Claude implements and runs the verification loop within the approved scope.
5. A fresh review session challenges the diff, criteria and verification evidence.
6. A human authorizes merge under the repository's review policy. Release authorization
   remains a separate gate where required.
One person may hold multiple roles in a small project; do not invent independent review.
Use the repository's actual role assignments. No special tool or MCP interface is required.

## Practical GitHub approval
Use a preparation PR containing only the change artifacts. Review intent/spec/plan in
stages on that PR; the final decision must cover the exact resulting revision.
Merge the approved preparation before starting a separate implementation PR.
An approval record must identify the human, artifact scope, reviewed commit, timestamp
and retrievable decision evidence (PR review or explicit human decision).
A commit author, merged PR, checkbox or Status: approved text alone does not prove approval.
If decisions are made in chat, preserve the exact decision and reviewed revision in a
human-confirmed record. Do not fabricate identity or use an agent account to self-approve.
For solo projects, document an explicit owner decision; do not claim a second reviewer.

## Deviations and reapproval
Compare implementation to the approved revision, not only the current files.
Minor file/sequence adjustments that preserve agreed behavior can be recorded in plan.md
and highlighted at review. Material changes to scope, behavior, interfaces, acceptance
criteria or constraints require human reapproval before affected implementation proceeds.
Keep the original decision in Git history. Never rewrite the spec to excuse a mismatch.
Legitimate test changes are possible but require explanation; never weaken a check to
hide failure. For bug fixes, demonstrate a regression test failing before the fix and
passing after it when feasible. A passing test is evidence, not proof of all correctness.

## Verification and embedded work
Every AC needs a meaningful check and expected result. Record unrun checks honestly.
Use unit, integration, simulation, target or hardware-in-the-loop checks as appropriate.
Host tests do not establish target timing, memory bounds or physical behavior. Preserve
existing product safety/release gates; this starter does not replace domain assurance.

## Enforcement boundaries
Skills guide behavior; they do not enforce authorization. This package does not install
branch protection, CODEOWNERS, release gates, privileged hooks or automatic merging.
Configure actual GitHub rules separately: human review, stale approval dismissal where
appropriate, required checks and restricted bypass. Choose reviewers who can approve.
The included CI validates package structure only, not semantics, approvals or product code.
Protect CI and approval mechanisms from the implementation agent's ability to weaken them.

## Versioned reuse
Install the complete package together: four .claude/skills directories plus .sdlc.
The installer records the source commit and SHA-256 hashes in .sdlc/package-lock.json.
Root project instructions are generated from templates and then maintained by the project.
Upgrade shared assets in a reviewed PR, inspect the diff, rerun evaluations, and record
new hashes. The initial installer refuses to overwrite files; it is not an updater.
Do not install only SKILL.md without the shared templates and workflow.

## Pilot and evolution
Measure preparation effort, prevented rework, human review time, handover without chat,
defects and missing verification across the first five changes. Simplify unused fields.
Add hooks, CI orchestration, specialized agents and eval automation only when justified.
Run evals/README.md scenarios when changing the skills. These are manual evaluations,
not an implemented autonomous eval service.
