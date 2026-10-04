# Review policy

Read approved intent/spec/plan and the complete diff. Tune this file monthly (review owner).

## Passes
1. **Bugs:** logic errors, edge cases, weakened or skipped tests.
2. **Security:** input handling, secrets, authorization, unsafe dependencies.
3. **Compliance:** behavior against spec.md and plan.md (every AC, deviations), and design principles.

## What Important means
Incorrect behavior, material unapproved deviation, a violated required constraint,
missing required verification, or a security flaw. Report location, impact and evidence;
separate demonstrated failures from suspicions.

## Cap the nits
At most five; summarize the rest as a count.

## Do not report
Generated files and anything CI already enforces (formatting, lint, types).

## Output
Record findings and AC coverage in review.md. State whether the review was fresh and which
checks you ran. End with `Tally: important=N nit=N`. Review informs the merge/release
decision; it is not that decision.
