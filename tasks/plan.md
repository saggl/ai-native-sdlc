# Plan: Full playbook coverage, still simple

Source: [SPEC.md](../SPEC.md). Target version 0.4.0.

## Dependency graph

```
A1 rename+case check ─┐
A2 migrate command   ─┤
A3 status once       ─┼─► CP1 ─► T5 plan deviations ─┐
A4 provenance scope  ─┘          T6 lock-tests ──────┼─► CP2 ─► T8 guard edits ─► T9 guard bash/format ─► T10 install hooks ─► CP3
                                 T7 new --adopt ─────┘                                                          │
                                                                                     T11 bands.py ─► T12 CI templates + install ci ─► T13 repo eval CI ─► CP4
                                                                                                                                          │
                                                                                     T14 stage instructions ─► T15 coverage table, validate, 0.4.0 ─► CP5
```

- T8 depends on T6: the guard reads `locked_tests` from open change state.
- T12 depends on T7 (the monitor and handoff use `new --adopt`) and T11 (the monitor runs bands.py).
- T15 depends on everything: the coverage table links assets that must exist.
- Parallel: A1–A4 are independent. T5/T6/T7 touch separate functions of one file, so
  run them sequentially in one session. T11 can run alongside T8–T10 (separate files).

## Key design decisions

- **One helper command for opt-ins:** `install <hooks|evals|review|handoff|monitor>`
  instead of two commands. This keeps the helper within about +80 lines.
- **Guard is standalone:** `hooks/guard.py` uses stdlib only and reads `.sdlc/project.json`
  (`protected_paths`, `gates`, `commands.format`) and open `state.json` files
  (`locked_tests`) from `$CLAUDE_PROJECT_DIR`. Copied into a project, it doesn't need
  the plugin.
- **Deviation section:** the text from `## Implementation deviations` to the end of
  `plan.md` is cut before hashing. Material changes still go back to approval
  (instructions plus review), because hashing can't classify materiality.
- **Lock-tests:** `lock-tests <id> --paths …` requires committed files and stores
  `{path: sha}`. Every `record-result` checks them, not only verification, so a later
  edit can't bypass it.
- **Provenance (A4):** the hash covers `SKILL.md`, `skills/`, `agents/`, `references/`,
  `templates/`, `scripts/sdlc.py`. `approval_valid` and `result_valid` compare content
  snapshots only. `status` adds `workflow_changed` when the latest record's workflow hash
  differs. Legacy compatibility is kept.

## Risks

| Risk | Mitigation |
|---|---|
| The rename makes existing users' REVIEW.md references dangle | REVIEW.md is only copied at setup; existing projects keep their copy. Note it in the guide. |
| Hook stdin/exit contract drifts | Test against documented JSON shapes; keep the guard tolerant of missing fields (allow by default when not configured). |
| A4 weakens staleness detection | Content snapshots still invalidate. Workflow drift is surfaced, not hidden. Test both. |
| CI templates can't be executed in unit tests | Check presence and parse (a stdlib YAML subset isn't available, so check key strings). State in the PR that they weren't run natively. |
| Scope creep beyond "simple" | Size budget in SPEC success criterion 6; review before CP5. |

## Checkpoints

- **CP1** after A1–A4: validate plus all tests green; the `git status` collision is gone.
- **CP2** after T5–T7: lifecycle tests green; the helper diff is at most 50 lines so far.
- **CP3** after T8–T10: a hook installed in a temp repo blocks the 4 cases from SPEC
  success criterion 3.
- **CP4** after T11–T13: bands tiers correct; `install` is idempotent; CI files are present.
- **CP5** after T14–T15: the coverage table validates 16/16; version 0.4.0; full suite
  passes; size budget checked; PR text lists the native runtimes exercised.
