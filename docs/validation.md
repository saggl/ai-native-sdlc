# Validation of the plugin refactor

Performed 2026-10-03 in a Linux execution environment with Python and Git.

## Executed checks

- Package validation: marketplace/manifest agreement, bundled paths, canonical templates,
  skill frontmatter, local Markdown links and removal of obsolete entry points.
- 23 tests using real disposable Git repositories, including empty initial history,
  fresh-process resume, setup preservation, collisions, symlink rejection, stale decisions,
  uncommitted policy removal, staged/working/committed code divergence, deleted/untracked
  files, report edits, blocked results, lifecycle completion and standalone plugin copying.
- Git whitespace/diff validation.
- A fresh agent used the start skill on an existing Python contact utility. It discovered
  and ran the actual test command, preserved the original CLAUDE.md rules, added project
  context/review policy, committed the intent and stopped for scope approval. It neither
  changed product code nor fabricated approval. Evidence: the disposable project commit
  `432b646df6634d895a0a0803e623d66120605d15` and its transcript in the development session.
  This was a Codex agent interpreting the skill, not a Claude Code runtime session.
- Independent helper review reproduced four issues: staged code could differ from tested
  code; recording an unstaged deletion caused evidence to go stale on staging; an optional
  policy deletion could be omitted from committed-approval checks; legitimate template
  syntax was rejected. Each was fixed and covered by regression tests.

## Remaining runtime check

The Claude Code executable is not available in this environment. Native plugin validation,
marketplace installation, Claude permission/mode behavior, reviewer delegation, and a full
real-project run through delivery/observation have not been exercised here. Run the local
`--plugin-dir` pilot described in README before calling this production-ready.

The GitHub workflow runs the deterministic package/tests on Linux, Windows and macOS.
Its configuration is not itself evidence those remote jobs passed; inspect the PR checks.
