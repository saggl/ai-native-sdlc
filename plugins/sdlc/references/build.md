# Implement, test and fix

Confirm all three recorded decisions and their evidence are current. Read the actual
approved artifacts and applicable instructions; do not rely on a conversation summary.

- Implement in the planned order and keep the diff bounded. For a bug, demonstrate a
  regression check failing for the intended reason before the fix when feasible.
- Run the project's applicable verification commands. Compare actual results to every
  acceptance criterion. Iterate code/test/fix until those checks pass or a real blocker
  is established. Inspect test changes for weakened assertions, skips and lost coverage.
- For UI work, inspect rendered output when appearance is part of acceptance. For
  embedded work, host tests cannot stand in for required target, timing or HIL evidence.
- Record a harmless file/sequence adjustment in verification.md with its rationale;
  do not rewrite the approved plan just to make the implementation appear compliant.
  Material behavior, interface, scope or verification changes need an updated artifact
  and a new human decision before the affected work proceeds.
- Commit the bounded implementation before final verification/evidence capture. Stage
  explicit paths and check staged versus working content; do not include unrelated work.
  Re-run the required checks on that committed implementation. A result must not refer
  to tested working files that differ from what Git will deliver.
- Render verification.md from the bundled template: current revision/diff, each AC,
  exact command and result, log location, environment, deviations and limitations.
  `blocked` covers failed or unavailable required checks; `passed` requires all of them.
- Record the verification result, commit scoped evidence, and continue
  to fresh review. Do not call an implementer's report an independent review.

Never mark an unrun command as passed. If the baseline already fails, identify that
separately and explain the impact; do not silently accept missing required evidence.
