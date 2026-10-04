# Contributing

Try the plugin on a small change in a disposable Git repository first. Reports from
real Claude Code, Codex and OpenCode sessions are especially useful: tell us which
client and version you used, what you asked it to do, what happened, and what you
expected. Remove secrets and private project content before sharing logs.

Open an [issue](https://github.com/saggl/ai-native-sdlc/issues) for bugs or focused
improvements. For larger changes, discuss the user problem before writing code. Keep
the solution small and preserve existing change records and project files. A useful
first contribution is a reproducible first-run failure or a shorter instruction that
retains the same safety checks.

For a pull request:

1. Explain the problem and resulting behavior. Link an issue if there is one.
2. Run `python3 scripts/validate.py` and
   `python3 -m unittest discover -s tests -q` (Python 3.10+).
3. State which native clients you actually tried. If none, say so; Python tests do not
   establish agent behavior. See [behavior evaluations](evals/README.md).
4. Describe any compatibility, migration or approval-evidence impact.

The review standard is in [REVIEW.md](REVIEW.md). Small documentation fixes need only
the checks relevant to them. The plugin's intent/spec/plan workflow is a tool you can
use for contributions, not a requirement for every outside pull request.
