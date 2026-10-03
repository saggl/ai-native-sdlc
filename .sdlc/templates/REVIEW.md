# Review policy
## Inputs
Approved intent, spec, plan, implementation diff and test results.
Read .sdlc/workflow.md for approval and deviation rules.
## Review areas
Behavior and acceptance criteria; logic and edge cases; security;
compatibility and project constraints; meaningful verification;
changes to tests and deviations from the approved baseline.
## Severity rules
Blocker: incorrect behavior, exploitable vulnerability, violated required constraint,
or missing evidence for a required acceptance criterion.
Advisory: maintainability or clarity improvements without demonstrated failure.
Nit: optional style issues; report at most five. Skip what deterministic CI already covers.
## Finding format
Severity, location, problem, impact and evidence. Separate suspicions from demonstrated failures.
## Review output
Use .sdlc/templates/review-report.md. Map every acceptance criterion to evidence.
State unresolved findings, deviations, unverified behavior and required human decisions.
The agent recommends; a human makes the merge decision.
