"""Local workflow bookkeeping. Records evidence; never authenticates or grants approval.

Python 3.10+, standard library only. No network calls or product commands are run.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

PLUGIN = Path(__file__).resolve().parents[1]
VERSION = json.loads((PLUGIN / '.claude-plugin/plugin.json').read_text())['version']
STAGES = ('intent', 'spec', 'plan')
RESULTS = ('verification', 'review', 'delivery', 'learning')
GUIDANCE = ('SKILL.md', 'skills', 'agents', 'references', 'templates', 'scripts/sdlc.py')
DEVIATIONS = '\n## Implementation deviations'
GUARD = '"${CLAUDE_PROJECT_DIR}/.claude/hooks/sdlc-guard.py"'
# A branch without the committed guard must not lock the session: a missing file allows.
HOOK = f'[ ! -f {GUARD} ] || python3 {GUARD}'


def now():
    return datetime.now(timezone.utc).isoformat()


def git(root, *args):
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True)
    if result.returncode:
        raise ValueError(result.stderr.decode(errors='replace').strip() or 'Git command failed')
    return result.stdout


def repository(path):
    root = Path(path).resolve()
    actual = Path(git(root, 'rev-parse', '--show-toplevel').decode().strip()).resolve()
    if actual != root:
        raise ValueError(f'Use the repository root: {actual}')
    return root


def safe_path(root, relative):
    rel = Path(relative)
    if rel.is_absolute() or '..' in rel.parts or not rel.parts:
        raise ValueError('Expected a relative path inside the repository')
    current = root
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f'Symlink in workflow path: {relative}')
    return current


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path, value, exclusive=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, indent=2, ensure_ascii=False) + '\n'
    if exclusive:
        with path.open('x', encoding='utf-8') as out:
            out.write(data)
    else:
        # An adjacent temporary file prevents a partial JSON record after interruption.
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         delete=False) as out:
            out.write(data)
            temporary = out.name
        os.replace(temporary, path)


def config(root):
    path = safe_path(root, '.sdlc/project.json')
    if not path.exists():
        raise ValueError('Project is not set up; run setup first')
    data = read_json(path)
    if data.get('schema') != 1:
        raise ValueError('Unsupported project schema')
    location = data.get('changes_dir', '')
    # A single directory keeps generated artifacts unambiguous and out of code snapshots.
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]*', location):
        raise ValueError('changes_dir must be a single directory name')
    safe_path(root, location)
    return data


def setup(root):
    path = safe_path(root, '.sdlc/project.json')
    if path.exists():
        return config(root)
    legacy = safe_path(root, '.sdlc/package-lock.json')
    if legacy.exists():
        raise ValueError('Legacy copied package found. Follow the installed plugin references/migrate.md first.')
    safe_path(root, 'changes')
    data = {'schema': 1, 'created_with': VERSION, 'changes_dir': 'changes',
            'commands': {}, 'policy_files': [], 'owners': {},
            'delivery': 'Use the project release process; no automatic merge or deployment.',
            'observe': 'Choose a real signal and owner before recording delivery as observed.'}
    write_json(path, data, exclusive=True)
    return data


def change_dir(root, slug):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        raise ValueError('Change ID must contain lowercase letters, digits and single hyphens')
    return safe_path(root, Path(config(root)['changes_dir']) / slug)


def state(root, slug):
    folder = change_dir(root, slug)
    path = safe_path(root, folder.relative_to(root) / 'state.json')
    data = read_json(path)
    if data.get('schema') != 1 or data.get('id') != slug:
        raise ValueError('Invalid change record')
    return folder, data


def save(root, folder, data):
    write_json(safe_path(root, folder.relative_to(root) / 'state.json'), data)


def copy_template(root, folder, name, title):
    path = safe_path(root, folder.relative_to(root) / (name + '.md'))
    text = (PLUGIN / 'templates' / (name + '.md')).read_text(encoding='utf-8')
    with path.open('x', encoding='utf-8') as out:
        out.write(text.replace('[[SDLC_TITLE]]', title))


def new(root, slug, title, adopt=False):
    folder = change_dir(root, slug)
    if adopt:
        # Intake from a connector, monitor, scan or channel: keep its committed intent.
        if not (folder / 'intent.md').is_file():
            raise ValueError(f'No intent.md to adopt in {folder.relative_to(root)}')
        if (folder / 'state.json').exists():
            raise ValueError('This change is already tracked')
    else:
        folder.mkdir(parents=True, exist_ok=False)
    try:
        head = git(root, 'rev-parse', 'HEAD').decode().strip()
    except ValueError:
        head = None  # New repositories are supported before their first commit.
    data = {'schema': 1, 'id': slug, 'title': title, 'created_at': now(),
            'plugin_version': VERSION, 'base_commit': head, 'approvals': [], 'results': []}
    save(root, folder, data)
    if not adopt:
        copy_template(root, folder, 'intent', title)
    return data


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(root, relative, required=True):
    path = safe_path(root, relative)
    if not path.exists() and not required:
        return None
    return sha(path.read_bytes())


def decided_text(root, folder, stage):
    """Artifact text under decision; recorded plan deviations follow the decision."""
    text = safe_path(root, folder.relative_to(root) / (stage + '.md')).read_text(encoding='utf-8')
    return text.split(DEVIATIONS, 1)[0] if stage == 'plan' else text


def artifact_snapshot(root, folder, stage):
    names = STAGES[:STAGES.index(stage) + 1]
    paths = [Path('.sdlc/project.json')] + [Path(p) for p in config(root).get('policy_files', [])]
    values = {str(folder.relative_to(root) / (s + '.md')): sha(decided_text(root, folder, s).encode())
              for s in names}
    values.update({str(p): file_digest(root, p) for p in paths})
    for name in ('CLAUDE.md', 'REVIEW.md', 'AGENTS.md'):
        values[name] = file_digest(root, name, required=False)
    return values


def workflow_provenance():
    """Identify the guidance that steers the agent, including unversioned local edits."""
    paths = [PLUGIN / name for name in GUIDANCE]
    paths = [p for root in paths for p in ([root] if root.is_file() else root.rglob('*'))]
    files = {path.relative_to(PLUGIN).as_posix(): sha(path.read_bytes())
             for path in sorted(paths) if path.is_file() and path.suffix in ('.md', '.py', '.json')}
    return {'version': VERSION, 'sha256': sha(json.dumps(files, sort_keys=True).encode())}


def workflow_changed(data):
    # Legacy records predate provenance; the version alone is not compared.
    records = [r for r in data['approvals'] + data['results'] if 'workflow' in r]
    current = workflow_provenance()['sha256']
    return any(r['workflow'].get('sha256') != current for r in records)


def approval_valid(root, folder, data, stage):
    try:
        snapshot = artifact_snapshot(root, folder, stage)
    except FileNotFoundError:
        return False
    records = [r for r in data['approvals'] if r['stage'] == stage]
    return bool(records and records[-1]['snapshot'] == snapshot)


def require_approvals(root, folder, data, stages):
    for stage in stages:
        if not approval_valid(root, folder, data, stage):
            raise ValueError(f'Missing or stale recorded {stage} approval; verify the human decision')


def draft(root, slug, stage):
    folder, data = state(root, slug)
    if data.get('closed_at'):
        raise ValueError('This change is complete; create a new change for follow-up work')
    require_approvals(root, folder, data, STAGES[:STAGES.index(stage)])
    copy_template(root, folder, stage, data['title'])
    return {'created': str(folder.relative_to(root) / (stage + '.md'))}


def record_approval(root, slug, stage, by, evidence, decision):
    folder, data = state(root, slug)
    if data.get('closed_at'):
        raise ValueError('This change is complete; create a new change for follow-up work')
    if not all(value.strip() for value in (by, evidence, decision)):
        raise ValueError('Provide the human, evidence reference and exact decision')
    require_approvals(root, folder, data, STAGES[:STAGES.index(stage)])
    snapshot = artifact_snapshot(root, folder, stage)
    for name in STAGES[:STAGES.index(stage) + 1]:
        text = decided_text(root, folder, name)
        if '[[SDLC_TITLE]]' in text or '<!-- SDLC:' in text:
            raise ValueError(f'Replace template prompts before recording approval: {name}.md')
    files = [p for p, digest in snapshot.items() if digest is not None]
    # Bind the record to a committed, unchanged artifact revision, including policy.
    for path in files:
        git(root, 'ls-files', '--error-unmatch', '--', path)
    if git(root, 'diff', 'HEAD', '--', *snapshot):
        raise ValueError('Commit the reviewed artifacts and policy before recording approval')
    commit = git(root, 'rev-parse', 'HEAD').decode().strip()
    record = {'stage': stage, 'by': by, 'evidence': evidence, 'decision': decision,
              'commit': commit, 'recorded_at': now(), 'snapshot': snapshot,
              'workflow': workflow_provenance()}
    data['approvals'].append(record)
    save(root, folder, data)
    return record


def code_snapshot(root):
    """Bind working files to committed product content; ignore lifecycle-only commits."""
    exclude = config(root)['changes_dir'] + '/'
    committed = {}
    for item in git(root, 'ls-tree', '-r', '-z', 'HEAD').split(b'\0'):
        if item:
            metadata, raw_name = item.split(b'\t', 1)
            committed[os.fsdecode(raw_name)] = metadata.decode()
    indexed = git(root, 'ls-files', '--stage', '-z').split(b'\0')
    modes = {}
    for item in indexed:
        if not item:
            continue
        metadata, raw_name = item.split(b'\t', 1)
        mode, _object, index_stage = metadata.decode().split()
        if index_stage != '0':
            raise ValueError('Resolve Git conflicts before recording results')
        if mode == '160000':
            raise ValueError('Submodule verification needs a project-specific adapter')
        modes[os.fsdecode(raw_name)] = mode
    names = set(modes) | set(committed)
    names.update(os.fsdecode(p) for p in git(root, 'ls-files', '--others', '--exclude-standard', '-z').split(b'\0') if p)
    digest = hashlib.sha256()
    for name in sorted(names):
        if name.startswith(exclude) or name == '.sdlc/project.json':
            continue
        path = root / name
        # Do not follow parent symlinks into another checkout or outside the repository.
        for parent in path.parents:
            if parent == root:
                break
            if parent.is_symlink():
                raise ValueError(f'Symlink parent in source path: {name}')
        if path.is_symlink():
            content, mode = os.fsencode(os.readlink(path)), '120000'
        elif path.is_file():
            content = path.read_bytes()
            mode = modes.get(name, '100644')
            if os.name != 'nt':
                mode = '100755' if path.stat().st_mode & 0o111 else '100644'
        elif not path.exists():
            content, mode = b'', 'deleted'
        else:
            raise ValueError(f'Unsupported Git-visible file: {name}')
        digest.update(json.dumps([name, mode, sha(content), committed.get(name)], ensure_ascii=True).encode())
    return digest.hexdigest()


def require_committed_code(root):
    excluded = config(root)['changes_dir']
    paths = ['.', f':(exclude){excluded}', ':(exclude).sdlc/project.json']
    if git(root, 'diff', 'HEAD', '--', *paths):
        raise ValueError('Commit the implementation before recording evidence; staged and tested code must agree')
    if git(root, 'ls-files', '--others', '--exclude-standard', '--', *paths):
        raise ValueError('Commit untracked product files before recording evidence')
    # Comparing both sides also catches a different staged blob hidden by a restored worktree.
    if git(root, 'diff', '--cached', 'HEAD', '--', *paths):
        raise ValueError('Commit staged product changes before recording evidence')


def result_valid(root, folder, data, kind, code):
    records = [r for r in data['results'] if r['kind'] == kind]
    if not records:
        return False
    last = records[-1]
    try:
        return (last['outcome'] == 'passed' and last['code'] == code
                and last['artifacts'] == artifact_snapshot(root, folder, 'plan')
                and last['report_sha'] == file_digest(root, last['report'])
                and last['prerequisites'] == prerequisite_snapshot(data, kind))
    except FileNotFoundError:
        return False


def prerequisite_snapshot(data, kind):
    return {previous: sha(json.dumps([r for r in data['results'] if r['kind'] == previous][-1],
                                    sort_keys=True).encode())
            for previous in RESULTS[:RESULTS.index(kind)]
            if any(r['kind'] == previous for r in data['results'])}


def lock_tests(root, slug, paths):
    """Record committed regression tests so a fix cannot weaken them unnoticed."""
    folder, data = state(root, slug)
    if data.get('closed_at'):
        raise ValueError('This change is complete; create a new change for follow-up work')
    for path in paths:
        git(root, 'ls-files', '--error-unmatch', '--', path)
    if git(root, 'diff', 'HEAD', '--', *paths):
        raise ValueError('Commit the failing tests before locking them')
    data.setdefault('locked_tests', {}).update({Path(p).as_posix(): file_digest(root, p) for p in paths})
    save(root, folder, data)
    return {'locked_tests': data['locked_tests']}


def require_locked_tests(root, data):
    for path, digest in data.get('locked_tests', {}).items():
        if file_digest(root, path, required=False) != digest:
            raise ValueError(f'Locked test changed: {path}; fix the code, or ask the owner to re-lock')


def record_result(root, slug, kind, outcome, report):
    folder, data = state(root, slug)
    if data.get('closed_at'):
        raise ValueError('This change is complete; create a new change for follow-up work')
    require_approvals(root, folder, data, STAGES)
    # Reports belong to this change, so writing them does not invalidate the code digest.
    expected = folder.relative_to(root) / (kind + '.md')
    if Path(report) != expected:
        raise ValueError(f'Write this report to {expected}')
    report_sha = file_digest(root, report)
    text = safe_path(root, report).read_text(encoding='utf-8')
    if not text.strip() or '[[SDLC_TITLE]]' in text or '<!-- SDLC:' in text:
        raise ValueError('Replace report template prompts with actual evidence')
    require_committed_code(root)
    require_locked_tests(root, data)
    code = code_snapshot(root)
    for previous in RESULTS[:RESULTS.index(kind)]:
        if not result_valid(root, folder, data, previous, code):
            raise ValueError(f'Missing, blocked or stale {previous} result')
    record = {'kind': kind, 'outcome': outcome, 'report': str(expected),
              'report_sha': report_sha, 'code': code, 'recorded_at': now(),
              'commit': git(root, 'rev-parse', 'HEAD').decode().strip(),
              'artifacts': artifact_snapshot(root, folder, 'plan'),
              'workflow': workflow_provenance(),
              'prerequisites': prerequisite_snapshot(data, kind)}
    data['results'].append(record)
    if kind == 'learning' and outcome == 'passed':
        data['closed_at'] = now()
    save(root, folder, data)
    return record


def status(root, slug, snapshot=None):
    folder, data = state(root, slug)
    result = {'id': slug, 'title': data['title'], 'path': str(folder.relative_to(root)),
              'next': None, 'approval_note': 'Local records only: verify referenced human evidence.'}
    if workflow_changed(data):
        result['workflow_changed'] = True  # Recheck open decisions against current guidance.
    if data.get('closed_at'):
        result['next'] = 'complete'
        result['closed_at'] = data['closed_at']
        return result
    for stage in STAGES:
        if not safe_path(root, folder.relative_to(root) / (stage + '.md')).exists():
            result['next'] = 'draft-' + stage
            return result
        if not approval_valid(root, folder, data, stage):
            result['next'] = 'approve-' + stage
            return result
    code = (snapshot or code_snapshot)(root)
    for kind, action in zip(RESULTS, ('implement-and-verify', 'review', 'deliver', 'observe-and-learn')):
        if not result_valid(root, folder, data, kind, code):
            result['next'] = action
            return result
    result['next'] = 'complete'
    return result


def all_status(root):
    if not safe_path(root, '.sdlc/project.json').exists():
        return {'next': 'setup', 'changes': []}
    folder = safe_path(root, config(root)['changes_dir'])
    output = []
    cache = {}

    def snapshot(root):
        # One repository hash serves every change; computed only when a change needs it.
        if 'code' not in cache:
            cache['code'] = code_snapshot(root)
        return cache['code']

    if folder.exists():
        for child in sorted(folder.iterdir()):
            if child.is_symlink():
                raise ValueError(f'Symlink in changes directory: {child.name}')
            if child.is_dir() and (child / 'state.json').exists():
                output.append(status(root, child.name, snapshot))
    return {'changes': output}


def copy_new(source, target):
    """Copy once; an identical file is a no-op and a different one is never overwritten."""
    if target.exists():
        if target.read_bytes() != source.read_bytes():
            raise ValueError(f'{target.name} exists with different content. Merge it by hand, '
                             'or delete it to take the bundled version')
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    return True


def install(root, name):
    """Opt-in enforcement and monitoring, run only after the user's explicit yes."""
    config(root)
    copied = []
    if name == 'hooks':
        if copy_new(PLUGIN / 'hooks/guard.py', safe_path(root, '.claude/hooks/sdlc-guard.py')):
            copied.append('.claude/hooks/sdlc-guard.py')
        path = safe_path(root, '.claude/settings.json')
        settings = read_json(path) if path.exists() else {}
        hooks = settings.setdefault('hooks', {})
        for event, matcher in (('PreToolUse', 'Edit|Write|MultiEdit|NotebookEdit|Bash'),
                               ('PostToolUse', 'Edit|Write|MultiEdit')):
            entries = hooks.setdefault(event, [])
            if not any(h.get('command') == HOOK for e in entries for h in e.get('hooks', [])):
                entries.append({'matcher': matcher, 'hooks': [{'type': 'command', 'command': HOOK}]})
                copied.append(f'.claude/settings.json:{event}')
        write_json(path, settings)
        return {'installed': copied}
    files = {'ci/monitor.yml': '.github/workflows/sdlc-monitor.yml',
             'scripts/bands.py': '.sdlc/bands.py', 'ci/bands.json': '.sdlc/bands.json'}
    pairs = [(PLUGIN / source, safe_path(root, target)) for source, target in files.items()]
    for source, target in pairs:  # Refuse before copying anything: no half-installed monitor.
        if target.exists() and target.read_bytes() != source.read_bytes():
            raise ValueError(f'{target.name} exists with different content. Merge it by hand, '
                             'or delete it to take the bundled version')
    copied += [target.relative_to(root).as_posix() for source, target in pairs if copy_new(source, target)]
    return {'installed': copied}


def nonempty(value):
    if not value.strip():
        raise argparse.ArgumentTypeError('Value must not be empty')
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='.', help='Explicit target repository root')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('setup')
    command = commands.add_parser('new')
    command.add_argument('id')
    command.add_argument('--title', required=True, type=nonempty)
    command.add_argument('--adopt', action='store_true', help='Track an existing committed intent.md')
    command = commands.add_parser('status')
    command.add_argument('id', nargs='?')
    command = commands.add_parser('draft')
    command.add_argument('id')
    command.add_argument('stage', choices=STAGES)
    command = commands.add_parser('record-approval')
    command.add_argument('id')
    command.add_argument('stage', choices=STAGES)
    for flag in ('by', 'evidence', 'decision'):
        command.add_argument('--' + flag, required=True, type=nonempty)
    command = commands.add_parser('record-result')
    command.add_argument('id')
    command.add_argument('kind', choices=RESULTS)
    command.add_argument('--outcome', choices=('passed', 'blocked'), required=True)
    command.add_argument('--report', required=True)
    command = commands.add_parser('lock-tests')
    command.add_argument('id')
    command.add_argument('--paths', nargs='+', required=True)
    command = commands.add_parser('install')
    command.add_argument('name', choices=('hooks', 'monitor'))
    args = parser.parse_args()
    try:
        root = repository(args.root)
        if args.command == 'setup':
            result = setup(root)
        elif args.command == 'new':
            result = new(root, args.id, args.title, args.adopt)
        elif args.command == 'status':
            result = status(root, args.id) if args.id else all_status(root)
        elif args.command == 'draft':
            result = draft(root, args.id, args.stage)
        elif args.command == 'record-approval':
            result = record_approval(root, args.id, args.stage, args.by, args.evidence, args.decision)
        elif args.command == 'lock-tests':
            result = lock_tests(root, args.id, args.paths)
        elif args.command == 'install':
            result = install(root, args.name)
        else:
            result = record_result(root, args.id, args.kind, args.outcome, args.report)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, f'SDLC: {exc}\n')


if __name__ == '__main__':
    main()
