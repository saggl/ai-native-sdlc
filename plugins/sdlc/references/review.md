# Challenge the implementation against the approved decisions

For `/sdlc:start`, delegate a fresh review to the bundled `sdlc:reviewer` agent if
available. Give it only the target repository, change folder, approved baseline,
current implementation revision and the verification report. Do not seed its verdict
with the implementer's explanation. If delegation is unavailable, request a fresh
Claude Code session running `/sdlc:review <id>` and stop at this handoff.

For `/sdlc:review`, perform the fresh review yourself if you did not implement this change.
Use root REVIEW.md and project policy; inspect the complete relevant diff and surrounding
code, including untracked work. Verify the human approval evidence and current artifacts.
Check logic, security, compatibility, each AC, test strength and plan deviations.
Re-run relevant safe checks; separate observed evidence from logs supplied by the author.

Save review.md using the bundled template. Record the reviewed revision and files,
reviewer/session provenance, important findings, criterion evidence and unverified items.
Required evidence missing, material unapproved deviations or unresolved important findings
mean `blocked`. A self-review cannot satisfy the fresh review stage. The script records
your result; it cannot itself determine whether a reviewer was independent or correct.

On findings, the implementation session fixes within the approved scope, reruns relevant
verification and requests fresh review of the new revision. Recheck all applicable
findings after each fix; do not patch source while acting as reviewer. If an approved
artifact needs to change, return to that decision first.

After a passed review, record the result and continue to delivery. Agent review is
evidence for the existing merge/release gate, not permission to bypass it.
