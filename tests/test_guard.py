import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

GUARD = Path(__file__).resolve().parents[1] / 'plugins/sdlc/hooks/guard.py'
FORMAT = [sys.executable, '-c',
          'import sys,pathlib; pathlib.Path(sys.argv[1]+".fmt").write_text("x")']


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()

    def tearDown(self):
        self.temp.cleanup()

    def config(self, **data):
        (self.root / '.sdlc').mkdir(exist_ok=True)
        (self.root / '.sdlc/project.json').write_text(json.dumps(data))

    def run_guard(self, event, event_name='PreToolUse'):
        event = {'hook_event_name': event_name, **event}
        env = {**os.environ, 'CLAUDE_PROJECT_DIR': str(self.root)}
        env.pop('DEPLOY_OK', None)
        return subprocess.run([sys.executable, str(GUARD)], input=json.dumps(event),
                              capture_output=True, text=True, env=env)

    def write(self, path, content='x = 1\n'):
        return self.run_guard({'tool_name': 'Write',
                               'tool_input': {'file_path': str(self.root / path), 'content': content}})

    def bash(self, command):
        return self.run_guard({'tool_name': 'Bash', 'tool_input': {'command': command}})

    def lock(self, closed):
        folder = self.root / 'changes/fix'
        folder.mkdir(parents=True)
        state = {'locked_tests': {'tests/test_a.py': 'abc'}}
        if closed:
            state['closed_at'] = '2026-01-01'
        (folder / 'state.json').write_text(json.dumps(state))

    def test_unconfigured_allows(self):
        self.assertEqual(self.write('.env', 'AKIA' + 'A' * 16).returncode, 0)
        self.assertEqual(self.bash('rm -rf x').returncode, 0)

    def test_protected_path_blocked(self):
        self.config(protected_paths=['secrets/*', '*.lock'])
        result = self.write('secrets/key.txt')
        self.assertEqual(result.returncode, 2)
        self.assertIn('protected_paths', result.stderr)
        self.assertEqual(self.write('deep/a.lock').returncode, 2)
        self.assertEqual(self.write('src/a.py').returncode, 0)

    def test_locked_test_blocked_while_open_only(self):
        self.config(changes_dir='changes')
        self.lock(closed=False)
        result = self.write('tests/test_a.py')
        self.assertEqual(result.returncode, 2)
        self.assertIn('locked by change fix', result.stderr)
        (self.root / 'changes/fix/state.json').write_text(json.dumps({'locked_tests': {'tests/test_a.py': 'abc'},
                                                'closed_at': '2026-01-01'}))
        self.assertEqual(self.write('tests/test_a.py').returncode, 0)

    def test_secret_blocked(self):
        self.config()
        self.assertEqual(self.write('a.py', 'k = "ghp_' + 'a' * 36 + '"').returncode, 2)
        result = self.run_guard({'tool_name': 'MultiEdit', 'tool_input': {
            'file_path': 'a.py', 'edits': [{'new_string': '-----BEGIN RSA PRIVATE KEY-----'}]}})
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.write('a.py', 'k = 1').returncode, 0)

    def test_outside_root_ignored(self):
        self.config(protected_paths=['*'])
        self.assertEqual(self.write('../outside.txt').returncode, 0)

    def test_gates(self):
        self.config(gates=[
            {'match': r'git push', 'require_env': 'DEPLOY_OK', 'action': 'block', 'reason': 'No pushes.'},
            {'match': r'terraform apply', 'require_env': 'DEPLOY_OK', 'action': 'ask', 'reason': 'Apply?'}])
        result = self.bash('git push origin main')
        self.assertEqual(result.returncode, 2)
        self.assertIn('No pushes. Set DEPLOY_OK after approval.', result.stderr)
        result = self.bash('terraform apply')
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)['hookSpecificOutput']
        self.assertEqual(output['permissionDecision'], 'ask')
        self.assertIn('Set DEPLOY_OK', output['permissionDecisionReason'])
        self.assertEqual(self.bash('ls').returncode, 0)
        self.assertEqual(self.bash('ls').stdout, '')
        env = {**os.environ, 'CLAUDE_PROJECT_DIR': str(self.root), 'DEPLOY_OK': '1'}
        event = {'hook_event_name': 'PreToolUse', 'tool_name': 'Bash',
                 'tool_input': {'command': 'git push'}}
        done = subprocess.run([sys.executable, str(GUARD)], input=json.dumps(event),
                              capture_output=True, text=True, env=env)
        self.assertEqual(done.returncode, 0)

    def test_format_invoked_after_edit(self):
        self.config(commands={'format': FORMAT})
        target = self.root / 'a.py'
        target.write_text('x=1\n')
        result = self.run_guard({'tool_name': 'Edit', 'tool_input': {'file_path': str(target)}},
                                'PostToolUse')
        self.assertEqual(result.returncode, 0)
        self.assertTrue((self.root / 'a.py.fmt').exists())

    def test_malformed_input_fails_open(self):
        env = {**os.environ, 'CLAUDE_PROJECT_DIR': str(self.root)}
        result = subprocess.run([sys.executable, str(GUARD)], input='not json',
                                capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0)
        self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
