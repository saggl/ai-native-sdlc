# Spec: Full playbook coverage, still simple

## Objective

Fix the review findings and make every play in Anthropic's
[AI-native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook) map to a
concrete plugin asset, without giving up the single `sdlc` entry point, stdlib-only
Python, or "nothing installed without consent".

**"100%" means:** each of the 16 plays has an asset: a stage instruction, a template,
or an opt-in hook/CI file. Hosted products (Claude Security, Claude Tag, managed Code
Review, Claude Design) are not reimplemented. The plugin defines how their output enters
the loop (as `intent.md` or through the review gate). A coverage table proves the
mapping, and `validate.py` checks it.

**Users:** developers using Claude Code, Codex or OpenCode on their own repos; platform
engineers who opt into enforcement (hooks, CI).

**Runtimes:** the core workflow is identical everywhere. Hooks and CI templates target
Claude Code. On Codex/OpenCode the same rules are checked at the review gate, and the
coverage table states the gap.

## Part A: Review findings

| ID | Fix |
|---|---|
| A1 | Rename `templates/REVIEW.md` → `templates/review-policy.md`. Update `setup.md` and `validate.py`. `validate.py` fails on any two repo paths that differ only by case. |
| A2 | `migrate.md`: replace the removed start command with `/sdlc:run`. Remove the `migrate.md` exemption from the obsolete-command check. |
| A3 | `all_status` computes `code_snapshot` once and passes it to `status`. |
| A4 | Workflow provenance hashes only the guidance that steers the agent (`SKILL.md`, `skills/`, `agents/`, `references/`, `templates/`, `scripts/sdlc.py`), not manifests, hooks or CI templates. The version is still recorded but not compared. When only provenance differs, `status` reports `workflow_changed: true` next to the unchanged `next` action, so the agent rechecks the decision instead of treating it as never approved. |

## Part B: Playbook coverage

| # | Play | Asset (new or changed) |
|---|---|---|
| 1 | Capture as intent.md | Existing intent stage. `new --adopt` registers an `intent.md` that someone else committed (a claude.ai GitHub connector, the monitor, a scan, Tag) without overwriting it. |
| 2 | Requirements and design | Existing spec stage. Front-end: spec links the Claude Design mock/export when one exists. |
| 3 | Plan mode | Existing plan stage. New: departures go in a `## Implementation deviations` section of `plan.md`, in the same commit. Text after that heading is excluded from the approval snapshot. Material departures still go back for approval. |
| 4 | Auto mode | Build stage: after plan approval, routine work (small blast radius, tests cover it) runs without per-edit prompts and is reviewed as artifacts afterwards. |
| 5 | CLAUDE.md | Existing setup pointer. Review stage adds: a mistake flagged twice goes into CLAUDE.md, and review flags when a change makes CLAUDE.md outdated. |
| 6 | Skills as institutional knowledge | Existing `policy_files`. Guide: write policy as a skill under `.claude/skills/<name>/`, test that it triggers, policy owner signs off changes. |
| 7 | Hooks as build-time guardrails | `hooks/guard.py` (opt-in). PreToolUse Edit/Write: blocks `protected_paths`, locked test files and secret patterns. PostToolUse: runs `commands.format` on the edited file when configured. |
| 8 | Parallel sessions and subagents | Build stage: split independent plan steps across `claude --worktree <name>`, starting with 2–3 sessions. New `agents/verifier.md`: fresh context, runs checks, reports only. |
| 9 | Feedback loop | Existing. New `lock-tests <id> --paths …` records hashes of the committed failing tests. `record-result verification` refuses if those files changed (deterministic). `guard.py` also blocks edits to them. |
| 10 | Continuous evals in CI | `ci/evals.yml` template: on PR changes to CLAUDE.md, `.claude/**`, REVIEW.md and policy files, plus a nightly run. Runs `evals/*.json` (`{"prompt", "check"}`) through `claude -p` and fails below the pass-rate threshold. This repo gets its own `.github/workflows/agent-evals.yml` for `plugins/sdlc/**`, which skips with a notice when there is no API key secret. |
| 11 | AI in the PR review loop | `review-policy.md` rewritten to match the playbook: Bugs/Security/Compliance passes, what counts as Important vs Nit, nit cap, do-not-report list. `review.md` template adds a `Tally: important=N nit=N` line. `ci/review.yml`: claude-code-action review with REVIEW.md, an `@claude` fix loop, and failed-build triage. Guide: managed Code Review as the alternative, monthly tuning. |
| 12 | Hooks as approval gates | `guard.py` PreToolUse Bash: `gates` in project.json, `[{"match": regex, "require_env": NAME, "action": "block"\|"ask", "reason": text}]`. A block names its reason and the route to approval. Guide: non-negotiable gates go in managed settings. |
| 13 | CI/CD integration and deployment | Deliver stage: tier autonomy by environment (dev free, staging limited, prod gated by #12); rollback is a single rehearsed command recorded in project.json `delivery`. `ci/handoff.yml`: a merged intent approval triggers a non-interactive spec draft PR. Agent writes arrive only as PRs. |
| 14 | Closing the loop | `scripts/bands.py` (stdlib): rolling mean/σ plus Western Electric rules 1–4 over a JSON series, returns tier `log`/`diagnose`/`propose`. Config in `bands.json`. `ci/monitor.yml`: cron → bands.py; diagnose runs `claude -p` with read-only tools; propose may open a PR or trigger a pre-approved runbook. Writes `intent.md` and runs `new --adopt`. |
| 15 | Recurring codebase scans | Observe stage intake rule: bounded finding → patch PR through the review gate; wider finding → `intent.md`; dismissal needs a reason; fixed class → eval. Claude Security is the scanner, not shipped. |
| 16 | Claude on call (Claude Tag) | Same intake rule for channel and ticket requests; post-mortem → `learning.md` and the lessons file. Tag itself not shipped. |

Opt-in installation goes through two helper commands. Both are explicit, idempotent and
refuse to overwrite:
- `install-hooks`: copies `guard.py` to `.claude/hooks/sdlc-guard.py` and merges entries
  into `.claude/settings.json` without touching existing keys.
- `install-ci <evals|review|handoff|monitor>`: copies the template to `.github/workflows/`
  (plus `bands.py`/`bands.json` for monitor).

Setup *offers* both and installs only on a yes. The helper still never calls models or
product commands. `guard.py` and `bands.py` run inside the user's own hooks and CI.

## Tech stack

Python 3.10+, standard library only, Git. GitHub Actions for CI templates
(`anthropics/claude-code-action`, `claude -p`). JSON config, not YAML.

## Commands

```
Validate: python3 scripts/validate.py
Test:     python3 -m unittest discover -s tests -v
Evals:    python3 evals/run.py --command '["claude","-p"]' --harness '<ver>' --model '<model>'
```

## Project structure (additions only)

```
plugins/sdlc/agents/verifier.md       fresh-context check runner (report only)
plugins/sdlc/hooks/guard.py           opt-in PreToolUse/PostToolUse guard
plugins/sdlc/scripts/bands.py         deterministic control-band detection
plugins/sdlc/ci/{evals,review,handoff,monitor}.yml
plugins/sdlc/ci/bands.json            example tier config
plugins/sdlc/templates/review-policy.md   (renamed from REVIEW.md)
.github/workflows/agent-evals.yml     this repo's own eval gate
tests/test_guard.py, tests/test_bands.py
```

The coverage table lives in `docs/guide.md#playbook-coverage` (its single home), and
`validate.py` checks it. The README links to it.

## Code style

Match `sdlc.py`: short functions, `ValueError` with an actionable message, no classes,
JSON on stdout. Hooks follow the Claude Code contract: read JSON from stdin; exit 2 plus
stderr blocks; JSON `permissionDecision: "ask"` asks.

```python
def gate(command, gates, env):
    for g in gates:
        if re.search(g['match'], command) and not env.get(g['require_env']):
            return g.get('action', 'block'), f"{g['reason']} Set {g['require_env']} after approval."
    return 'allow', ''
```

## Testing strategy

`unittest` in real temp Git repos, as today. New tests:
- case-collision detection; `all_status` hashes the code once; a provenance-only change
  reports `workflow_changed` and keeps `next`;
- plan deviations section doesn't invalidate approval, while edits above it do;
- `lock-tests` + changed test → verification refused;
- `new --adopt` keeps the existing intent and refuses an existing state.json;
- guard: protected path blocked, locked test blocked, secret blocked, gate block/ask/allow,
  format hook invoked;
- bands: each Western Electric rule maps to the right tier; a short series stays `log`;
- install-hooks/install-ci: merge preserves existing settings, refuses overwrite,
  running twice is a no-op;
- validate: every play row in the coverage table resolves to an existing asset.

Agent behavior stays in `evals/`. CI YAML is checked for presence and parse only;
running it is a native check that must be reported in the PR.

## Boundaries

- **Always:** keep `sdlc` as the single entry point; preserve existing records (old
  approvals stay readable); run validate and tests; state which runtimes were exercised.
- **Ask first:** anything that writes to `.claude/settings.json` or `.github/workflows/`
  in a user project; bumping to 0.4.0.
- **Never:** activate hooks or CI by default; add dependencies; let the helper call
  models, product commands or the network; let agents approve or merge; reimplement
  hosted Anthropic products.

## Success criteria

1. Findings A1–A4 fixed, with tests.
2. The coverage table lists all 16 plays, each linking an existing asset, and validate
   enforces it.
3. With hooks installed in a temp repo: protected-path edit, locked-test edit, secret
   write and ungated `deploy production` are blocked with a reason; with the approval
   env set, the deploy passes.
4. `bands.py` raises the right tier on synthetic spike and drift series.
5. A fresh setup without opt-ins produces the same files as today, apart from the
   renamed template.
6. Net size stays modest: the helper grows by at most about 80 lines; each new script
   is at most about 120 lines; no new top-level user commands.
7. All tests pass on Linux/macOS/Windows CI.

## Decisions

1. **Version 0.4.0.** The opt-in features and the provenance change are a minor bump
   under 0.x. Both manifests stay aligned (validate enforces this).
2. **Metric source = JSON array of numbers in a file.** `bands.json` names a
   `metric_command` that the monitor workflow runs to write the file, and bands.py only
   reads it. Detection stays deterministic and network-free, and any monitoring stack
   can feed it.
3. **A one-time `workflow_changed` after the upgrade is accepted.** Records stay
   readable, `next` doesn't regress, and the agent rechecks unchanged content without
   asking for approval again. The guide's update notes say so.
