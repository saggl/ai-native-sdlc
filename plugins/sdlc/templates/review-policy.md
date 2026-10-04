# Review policy

Read approved intent/spec/plan and the complete relevant implementation diff.
Check behavior, logic, security, compatibility, project constraints, acceptance
evidence and departures from the approved baseline. Inspect changed tests for
weakened assertions; deterministic style checks belong in CI.

Block on incorrect behavior, material unapproved deviation, a violated required
constraint or missing required verification. Report location, impact and evidence;
distinguish demonstrated failures from suspicions. Cap optional nits at five.

Record review findings and criterion coverage in the change folder's review.md.
State whether this was a fresh review and which checks were personally run.
Review is evidence for the existing merge/release decision, not that decision itself.
