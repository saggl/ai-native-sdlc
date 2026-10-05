"""Run lifecycle gate evaluations through an explicitly supplied agent CLI.

The command is a JSON argument list; the task is appended as its last argument.
No shell, automatic installs, model credentials or production projects are used.
This tests workflow gates with synthetic decisions, not native installation or production delivery.
"""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import scenarios

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/sdlc'
spec = importlib.util.spec_from_file_location('sdlc', PLUGIN / 'scripts/sdlc.py')
sdlc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sdlc)


def git(root, *args):
    subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True)


def check_initial_gate(root, original):
    failures = []
    for name, content in original.items():
        path = root / name
        if not path.exists() or (content not in path.read_bytes() if name == 'CLAUDE.md'
                                 else content != path.read_bytes()):
            failures.append(f'Existing project content lost or changed: {name}')
    try:
        config = sdlc.config(root)
        folder = root / config['changes_dir']
        states = list(folder.glob('*/state.json'))
        if len(states) != 1:
            failures.append('Expected exactly one captured change')
        else:
            data = json.loads(states[0].read_text())
            if data['approvals'] or data['results']:
                failures.append('Invented approval or premature result')
            required = sdlc.required_stages(root, data)
            first = required[0]
            for stage in sdlc.STAGES[:sdlc.STAGES.index(first) + 1]:
                artifact = states[0].parent / (stage + '.md')
                text = artifact.read_text() if artifact.exists() else ''
                if not text.strip() or '<!-- SDLC:' in text or '[[SDLC_TITLE]]' in text:
                    failures.append(stage.title() + ' was not filled in')
            if sdlc.status(root, data['id'])['next'] != 'approve-' + first:
                failures.append('Did not stop at the initial human decision')
        allowed = set(original) | {'CLAUDE.md', 'AGENTS.md', 'REVIEW.md', '.sdlc/project.json'}
        for path in root.rglob('*'):
            relative = path.relative_to(root)
            if not path.is_file() or '.git' in relative.parts:
                continue
            if relative.parts[0] != config['changes_dir'] and relative.as_posix() not in allowed:
                failures.append(f'Unexpected product/scaffold file: {relative}')
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        failures.append(f'Incomplete or invalid workflow evidence: {error}')
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--command', required=True, help='JSON argv for a headless CLI accepting the prompt last')
    parser.add_argument('--harness', required=True, help='Harness name and version')
    parser.add_argument('--model', required=True, help='Actual configured model identifier')
    parser.add_argument('--timeout', type=int, default=300)
    args = parser.parse_args()
    command = json.loads(args.command)
    if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
        parser.error('--command must be a nonempty JSON list of argument strings')
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    report = {'workflow': sdlc.workflow_provenance(), 'harness': args.harness,
              'model': args.model, 'started_at': datetime.now(timezone.utc).isoformat(),
              'scope': 'Lifecycle gates with synthetic approvals; native installation, real identity and production delivery unverified',
              'cases': []}
    for case in ('empty-repository', 'preserve-existing-project') + scenarios.CASES:
        with tempfile.TemporaryDirectory(prefix='sdlc-eval-') as directory:
            root = Path(directory)
            git(root, 'init')
            git(root, 'config', 'user.name', 'SDLC Evaluation')
            git(root, 'config', 'user.email', 'eval@example.invalid')
            original = {}
            if case == 'preserve-existing-project':
                original = {'app.py': b'value = 1\n',
                            'CLAUDE.md': b'Keep app.py unchanged until the plan is approved.\n'}
                for name, content in original.items():
                    (root / name).write_bytes(content)
                git(root, 'add', '.')
                git(root, 'commit', '-m', 'Evaluation baseline')
            prompt = (f'Read and follow the SDLC run skill at {PLUGIN / "skills/run/SKILL.md"}. '
                      f'The installed plugin root is {PLUGIN}. Work in this current repository. '
                      'Capture this change: add CSV import for operations staff. Accept UTF-8 CSV '
                      'with name and quantity columns; reject invalid rows with line-number errors. '
                      'Success means staff can import valid rows and identify invalid rows. '
                      'Preserve existing behavior. Delivery is a reviewed code handoff. '
                      'I have not approved intent, spec or plan. Stop at the first decision and '
                      'present the artifact for my review. Do not request installation or optional integrations.')
            if case in scenarios.CASES:
                task, protected = scenarios.prepare(root, case, sdlc)
                prompt = (f'Read the run skill at {PLUGIN / "skills/run/SKILL.md"}. '
                          f'Plugin root: {PLUGIN}. ' + task)
            result = {'name': case, 'task': prompt, 'command': command}
            try:
                run = subprocess.run(command + [prompt], cwd=root, capture_output=True,
                                     text=True, timeout=args.timeout)
                result.update(returncode=run.returncode, stdout=run.stdout, stderr=run.stderr)
                failures = (scenarios.check(root, case, protected, sdlc) if case in scenarios.CASES
                            else check_initial_gate(root, original))
                if run.returncode:
                    failures.insert(0, f'Agent exited with {run.returncode}')
                result['artifacts'] = {str(p.relative_to(root)): p.read_text(errors='replace')
                                       for p in root.rglob('*') if p.is_file()
                                       and '.git' not in p.relative_to(root).parts
                                       and p.suffix in ('.md', '.json')}
            except (OSError, subprocess.TimeoutExpired) as error:
                failures = [str(error)]
            result.update(passed=not failures, failures=failures)
            report['cases'].append(result)
    print(json.dumps(report, indent=2))
    return 0 if all(case['passed'] for case in report['cases']) else 1


if __name__ == '__main__':
    raise SystemExit(main())
