# Workflow contract

Use Python 3.10+ and Git. Select `python3`, `python`, or `py -3` by checking the local
interpreter. If unavailable, explain the missing prerequisite. Do not install it silently.
Invoke the bundled helper using its absolute path and the target Git root:

```text
python3 "<plugin-root>/scripts/sdlc.py" --root "<project-root>" status
```

`<plugin-root>` is resolved by the calling skill: `${CLAUDE_PLUGIN_ROOT}` in Claude
Code or the installed package path in Codex/OpenCode. Quote arguments safely; treat user
text as arguments, never interpolate it as executable shell code.

## Helper operations (the agent runs these)

| Operation after `--root <project-root>` | Effect |
| --- | --- |
| `setup` | Create `.sdlc/project.json` once; preserve existing content |
| `new <id> --title <title>` | Create a unique change folder, state and intent template |
| `status [id]` | Infer next stage; check saved artifact and evidence fingerprints |
| `draft <id> spec` / `draft <id> plan` | Create the next template after prior decisions |
| `record-approval <id> <intent\|spec\|plan> --by <human> --evidence <reference> --decision <exact-decision>` | Record a real human decision on committed artifacts |
| `record-result <id> <verification\|review\|delivery\|learning> --outcome <passed\|blocked> --report <relative-path>` | Bind a report to the code and upstream artifacts |

Reports are named `verification.md`, `review.md`, `delivery.md`, `learning.md` in that
change's folder. Render them from the corresponding bundled template. Commit the
artifacts and records at handoffs, using explicitly scoped staging; preserve unrelated
work. A new repo can start with no commits; reviewed artifacts must be committed before
an approval is recorded. Git history, not a shared example project, holds the decisions.

## Team decisions on one PR

For GitHub teams, use one draft PR from intent onward when authorized to publish.
Use the owners and policy established during setup. At a stage gate, present the committed
artifact revision, identify the decision owner and ask for the concise stage response
`Intent approved`, `Spec approved` or `Plan approved`. Provide a handoff for that
owner; request a review or send a notification only when authorized to do so.

Persist the presentation in the existing PR or other durable decision record: include the
change ID, stage, artifact path, full commit SHA and a revision-pinned artifact link.
Link the owner's reply to that presentation (a thread reply or an explicit reference).
The owner need not type the SHA. Save both presentation and response references in the
approval evidence so a fresh session can recover what was reviewed. Do not infer the
revision from the current PR head, comment timing or an unavailable previous chat. If
multiple presentations could match a reply, ask which one before recording approval.

A human response counts when it explicitly communicates approval or acceptance and
identifies the artifact being approved (intent, spec or plan). Exact wording is not
required; accept obvious spelling mistakes when the meaning remains unambiguous. Do not
infer approval from generic positive feedback, reactions, labels, or a response that also
requests an unresolved change. Retrieve the actual comment/review and verify its author
against the agreed owner. Bind the decision to the exact committed artifact revision that
was presented, then compare that artifact and upstream policy with current content before
recording. Save the source URL and exact decision using `record-approval`; do not invent
evidence. If the source is inaccessible, role unclear, decision withdrawn or content
stale, resolve that gate. For chat decisions allowed by project policy, retain the exact
human quote and context.

On resume, recheck referenced decisions; continue without asking for unchanged, still
valid approvals again. New implementation commits alone do not revoke artifact decisions.
GitHub's final approving review is a separate merge gate; stage comments and fresh agent
review do not satisfy it. No built-in identity/role enforcement, comment parser or watcher
is installed: use available tools to inspect evidence and the agent's start entry point to resume manually.

## Rules shared by every stage

- Humans own intent, behavior, approach and release judgment. One person can hold
  several roles. Ask only the responsible person for the decision needed now.
- Use the existing repository workflow. A single change branch/PR can contain the
  artifact commits followed by implementation; separate preparation PRs are optional.
- Approval records store the person's decision, evidence reference, time, commit and
  SHA-256 of artifacts/policies. They detect stale content; they do not authenticate
  identity. For team gates use retrievable PR reviews or the team's approval system.
  For a solo project use the actual explicit chat decision and identify it as such.
- No agent self-approval. An authorized human driving the agent may approve a routine
  plan; this is distinct from a teammate's final merge review. No checkbox, label,
  commit author, generated status or Git merge alone is
  evidence of a human's intended decision. Resolve inaccessible evidence before proceeding.
- Changing an upstream artifact or policy invalidates downstream records. Keep history
  and obtain the changed decision. A result also becomes stale when Git-visible code,
  its report, or earlier result records change. Never silently repair fingerprints.
- Commit implementation before final verification/result recording; the helper rejects
  uncommitted or untracked product files and binds results to the committed code as well
  as working files. Evidence-only commits do not invalidate results.
- Results record observed evidence, not guarantees. A `passed` result requires that
  stage's required checks, independent review or observed delivery actually passed.
- Stop when a required environment/check is unavailable. Record `blocked` with the
  specific missing evidence; no green status based only on an agent's assurance.
- Workflow data lives in the configured changes directory; product code must not live
  there. Git-ignored/generated outputs are not fingerprinted: reference CI/build IDs
  and target evidence where needed. Submodule result capture requires a project adapter.
- Work on one change per worktree/session. Never overwrite another session's state.
- After learning closes a change, it is a historical record. New incidents start a
  linked new intent; they do not rewrite the previous change's approved history.

Skills and local files are guidance, not a security boundary. Server-side branch rules,
required checks, protected environments and permissions remain authoritative. This
plugin installs no hooks, background jobs, model keys, auto-merge or deployment access.

