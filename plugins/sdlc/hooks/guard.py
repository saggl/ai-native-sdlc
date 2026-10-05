#!/usr/bin/env python3
"""Opt-in Claude Code guard: protected paths, locked tests, secrets, gates, formatter."""
import fnmatch
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

EDIT_TOOLS = {'Edit', 'Write', 'MultiEdit', 'NotebookEdit'}
SECRETS = [r'-----BEGIN [A-Z ]*PRIVATE KEY-----', r'AKIA[0-9A-Z]{16}',
           r'ghp_[A-Za-z0-9]{36}', r'sk-ant-[A-Za-z0-9_-]{20,}']
CONFIG = '.sdlc/project.json'


def load_json(path):
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def block(message):
    print(message, file=sys.stderr)
    sys.exit(2)


def new_text(tool_input):
    parts = [tool_input.get(key) for key in ('content', 'new_string', 'new_source')]
    parts += [edit.get('new_string') for edit in tool_input.get('edits') or []
              if isinstance(edit, dict)]
    return '\n'.join(part for part in parts if isinstance(part, str))


def relative(root, raw):
    path = Path(raw)
    path = path if path.is_absolute() else root / path
    try:
        return Path(os.path.normpath(path)).relative_to(os.path.normpath(root)).as_posix()
    except ValueError:
        return None


def locked_by(root, config, rel):
    for state in sorted((root / config.get('changes_dir', 'changes')).glob('*/state.json')):
        data = load_json(state)
        if not data.get('closed_at') and rel in (data.get('locked_tests') or {}):
            return state.parent.name
    return None


def check_edit(root, config, tool_input):
    raw = tool_input.get('file_path') or tool_input.get('notebook_path')
    rel = relative(root, raw) if raw else None
    if rel is not None:
        if any(fnmatch.fnmatch(rel, str(p)) for p in config.get('protected_paths') or []):
            block(f'{rel} is a protected path. Change protected_paths in {CONFIG} with its owner.')
        change = locked_by(root, config, rel)
        if change:
            block(f'{rel} is locked by change {change}; tests must not be weakened during the fix. '
                  f'Change test scope only through a revised approved plan, or close the change.')
    text = new_text(tool_input)
    if any(re.search(pattern, text) for pattern in SECRETS):
        block('Content looks like a secret or private key. Remove it and read it from the '
              'environment or a secret manager instead.')


def check_command(config, command):
    # Match the complete text: quotes, substitutions and heredocs can contain code.
    # This is a conservative regex guard, not a shell parser or a sandbox.
    for gate in config.get('gates') or []:
        env = gate.get('require_env', '')
        try:
            hit = re.search(gate.get('match', ''), command)
        except re.error:
            continue
        if hit and not os.environ.get(env):
            text = f"{gate.get('reason', 'Command is gated.')} Set {env} after approval."
            if gate.get('action') == 'ask':
                print(json.dumps({'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse', 'permissionDecision': 'ask',
                    'permissionDecisionReason': text}}))
                return
            block(text)


def run_format(root, config, tool_input):
    fmt = (config.get('commands') or {}).get('format')
    argv = shlex.split(fmt) if isinstance(fmt, str) else fmt
    raw = tool_input.get('file_path')
    rel = relative(root, raw) if raw else None
    if not argv or rel is None or not (root / rel).is_file():
        return
    try:
        done = subprocess.run([*map(str, argv), str(root / rel)], cwd=root, timeout=60,
                              capture_output=True, text=True)
        if done.returncode:
            print(f'format failed for {rel}: {done.stderr or done.stdout}', file=sys.stderr)
    except (OSError, subprocess.SubprocessError) as error:
        print(f'format failed for {rel}: {error}', file=sys.stderr)


def main():
    try:
        event = json.load(sys.stdin)
        root = Path(os.environ.get('CLAUDE_PROJECT_DIR') or event.get('cwd') or '.').resolve()
        config = load_json(root / CONFIG)
        tool, tool_input = event.get('tool_name'), event.get('tool_input') or {}
        pre = event.get('hook_event_name') == 'PreToolUse'
        if not (root / CONFIG).is_file() or not isinstance(tool_input, dict):
            return
        if pre and tool in EDIT_TOOLS:
            check_edit(root, config, tool_input)
        elif pre and tool == 'Bash':
            check_command(config, str(tool_input.get('command', '')))
        elif event.get('hook_event_name') == 'PostToolUse' and tool in EDIT_TOOLS - {'NotebookEdit'}:
            run_format(root, config, tool_input)
    except Exception as error:  # fail open, never traceback
        print(f'sdlc-guard skipped: {error}', file=sys.stderr)


if __name__ == '__main__':
    main()
