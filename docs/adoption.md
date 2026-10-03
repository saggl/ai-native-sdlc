# Adoption guide

## What changes
Today: plan in chat, generate code, review the diff; decisions disappear with the session.
Pilot: save and approve intent/spec/plan, build against them, review evidence and deviations.
A code review remains necessary; upstream approval cannot guarantee correct implementation.

## Responsibilities
| Decision | Accountable role |
| --- | --- |
| Value and scope | Product owner or project owner |
| Required behavior | Owner with relevant domain experts |
| Technical approach and checks | Responsible engineer; tech lead for material risk |
| Implementation and feedback loop | Engineer directing Claude |
| Merge | Authorized human reviewer under project policy |
| Release | Existing release owner/process |

The owner need not approve every routine detail. Assign roles for the actual project.

## First five changes
1. Install a pinned package and validate generated project instructions.
2. Select a bounded feature; prepare it manually and resolve questions.
3. Record staged decisions on one preparation PR, tied to the reviewed revision.
4. Implement separately; gather tests, review findings and explicit deviations.
5. Review evidence and sensitive code, then make the human merge decision.
Repeat and measure preparation effort, rework avoided, review time and escaped defects.
Use compact change.md only when the change is truly bounded and low risk.

## Ongoing maintenance
Maintain README/CLAUDE/REVIEW as current project guidance. Preserve per-change documents
as historical decisions; mark superseded decisions with links rather than deleting history.
Add domain-specific skills only for repeated institutional knowledge. Embedded constraints
belong in project rules/specs and verification environments, not in invented generic limits.
Automate transitions after the manual workflow is useful. Later additions may include
protected hooks, headless CI jobs, agent evals and incident-triggered intent creation.
