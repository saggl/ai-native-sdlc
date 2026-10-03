# Capture decisions before implementation

Read existing artifacts and their recorded evidence first. Continue from the earliest
missing or stale decision. Keep artifacts short and replace every template comment.
Use actual project constraints and policies; identify missing information explicitly.

1. **Intent:** describe the problem, affected people/systems, desired measurable outcome,
   boundaries and open questions. Ask only questions that materially change the decision.
   Show the saved intent and ask its owner to approve scope and value.
2. **Spec:** after intent approval, run `draft <id> spec`. Inspect the real codebase;
   define stable `AC-1`, `AC-2` criteria, behavior, failure cases, interfaces and concerns.
   Apply the project's skills and policies. Resolve blocking questions with their owner.
   Show the spec and ask the responsible human to approve behavior and constraints.
3. **Plan:** after spec approval, run `draft <id> plan`. Use Claude Code plan mode when
   available. List the actual files/components, ordered steps, alternatives, risks, a
   check for every AC, and delivery/rollback approach. Present it for technical approval.
   Do not implement product code while planning. If plan-mode permissions prevent
   saving/committing the artifact, show the plan and request the necessary mode change.
   Leaving plan mode alone is not approval of an unreviewed artifact.

For each gate, persist and commit the exact reviewed artifact before recording the
decision. Use existing authorization for scoped local commits. Record a real decision
with `record-approval`, then commit the state record. An explicit approval in this session
can be preserved as its exact quote and context; do not claim an externally authenticated
review. For another person's approval, retrieve the actual review/decision reference.
If content changed after approval, show that change and get the affected decision again.

Capture the plugin version (the change record does this), source task/issue and policy
references. Do not make the user transcribe the conversation. Do not ask for approval
already evidenced for these unchanged artifacts. Proceed automatically to build after
the plan decision, within permissions and the approved scope.

A spelling fix can have three tiny artifacts. A larger feature needs more evidence,
not necessarily more headings. Do not introduce a second compact workflow to learn.
