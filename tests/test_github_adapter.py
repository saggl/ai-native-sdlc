import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('github_adapter', ROOT / 'adapters/github/run.py')
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class GitHubAdapterTests(unittest.TestCase):
    def setUp(self):
        self.pr = {'state': 'open', 'merged': False,
                   'head': {'repo': {'full_name': 'owner/repo'}, 'ref': 'feature', 'sha': 'a' * 40},
                   'base': {'repo': {'full_name': 'owner/repo'}, 'ref': 'main'}}
        self.config = {'command': ['agent'], 'operators': ['alice'],
                       'owners': {s: ['alice'] for s in adapter.sdlc.STAGES},
                       'max_fix_attempts': 1, 'timeout_seconds': 30}

    def test_rejects_forks_closed_prs_and_default_branch_writes(self):
        adapter.check_pr(self.pr, 'owner/repo', 'main')
        self.pr['head']['repo']['full_name'] = 'fork/repo'
        with self.assertRaisesRegex(ValueError, 'Fork'):
            adapter.check_pr(self.pr, 'owner/repo', 'main')
        self.pr['head']['repo']['full_name'] = 'owner/repo'
        self.pr['head']['ref'] = 'main'
        with self.assertRaisesRegex(ValueError, 'separate branch'):
            adapter.check_pr(self.pr, 'owner/repo', 'main')
        self.pr['state'] = 'closed'
        with self.assertRaisesRegex(ValueError, 'open'):
            adapter.check_pr(self.pr, 'owner/repo', 'main')

    def test_rejects_bots_unlisted_actors_and_read_only_users(self):
        class API:
            def call(self, path):
                return {'permission': 'read'}
        for actor in ({'login': 'alice', 'type': 'Bot'}, {'login': 'bob', 'type': 'User'},
                      {'login': 'alice', 'type': 'User'}):
            with self.assertRaises(ValueError):
                adapter.authorize(API(), actor, ['alice'])

    def test_rejects_cross_pr_approval_links_and_unbounded_config(self):
        with self.assertRaises(ValueError):
            adapter.comment_id('https://github.com/owner/repo/pull/2#issuecomment-1', 'owner/repo', 1)
        self.config['max_fix_attempts'] = 4
        with self.assertRaisesRegex(ValueError, '0..3'):
            adapter.validate_config(self.config)

    def test_decision_accepts_pinned_content_and_rejects_stale_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            import subprocess
            subprocess.run(['git', 'init', str(root)], check=True, capture_output=True)
            adapter.sdlc.git(root, 'config', 'user.name', 'Fixture')
            adapter.sdlc.git(root, 'config', 'user.email', 'fixture@example.invalid')
            adapter.sdlc.setup(root)
            adapter.sdlc.new(root, 'change', 'Change')
            intent = root / 'changes/change/intent.md'
            intent.write_text('# Intent\nConcrete outcome.\n')
            adapter.sdlc.git(root, 'add', '.')
            adapter.sdlc.git(root, 'commit', '-m', 'Presented intent')
            revision = adapter.sdlc.git(root, 'rev-parse', 'HEAD').decode().strip()
            url = 'https://github.com/owner/repo/pull/1#issuecomment-10'
            presentation = {'issue_url': 'https://api.github.com/repos/owner/repo/issues/1',
                            'html_url': url, 'body': '<!-- sdlc:gate ' + json.dumps(
                                {'id': 'change', 'stage': 'intent', 'commit': revision,
                                 'path': 'changes/change/intent.md'}) + ' -->'}
            class API:
                repository = 'owner/repo'
                def call(self, path):
                    return {'permission': 'write'} if path.startswith('collaborators/') else presentation
            response = {'user': {'type': 'User', 'login': 'alice'}, 'body': 'Intent approved ' + url}
            self.assertEqual(adapter.decision(API(), root, 1, response, self.config)[:2], ('change', 'intent'))
            intent.write_text('# Intent\nChanged outcome.\n')
            with self.assertRaisesRegex(ValueError, 'stale'):
                adapter.decision(API(), root, 1, response, self.config)
            response['body'] = 'Intent approved ' + url + ' but change the scope'
            with self.assertRaisesRegex(ValueError, 'no extra text'):
                adapter.decision(API(), root, 1, response, self.config)

    def test_agent_does_not_forward_github_credentials(self):
        class Run:
            returncode = 0
            stdout = stderr = ''
        with patch.dict('os.environ', {'GITHUB_TOKEN': 'secret', 'GH_TOKEN': 'secret2', 'ANTHROPIC_API_KEY': 'model'}), patch.object(
                adapter.subprocess, 'run', return_value=Run()) as run, patch.object(adapter.sdlc, 'require_committed_code'):
            adapter.agent(Path('/fixture'), ['agent'], 'task', 10)
            environment = run.call_args.kwargs['env']
            self.assertNotIn('GITHUB_TOKEN', environment)
            self.assertNotIn('GH_TOKEN', environment)
            self.assertEqual(environment['ANTHROPIC_API_KEY'], 'model')

    def test_reviewer_cannot_publish_product_edits(self):
        class Run:
            returncode = 0
            stdout = stderr = ''
        with patch.object(adapter.subprocess, 'run', return_value=Run()), patch.object(
                adapter.sdlc, 'code_snapshot', side_effect=['before', 'after']):
            with self.assertRaisesRegex(ValueError, 'reviewer changed'):
                adapter.agent(Path('/fixture'), ['agent'], 'task', 10, review=True)


class AdapterLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(['git', 'init', str(self.root)], check=True, capture_output=True)
        adapter.sdlc.git(self.root, 'config', 'user.name', 'Fixture')
        adapter.sdlc.git(self.root, 'config', 'user.email', 'fixture@example.invalid')
        adapter.sdlc.git(self.root, 'config', 'core.autocrlf', 'false')
        adapter.sdlc.setup(self.root)
        adapter.sdlc.new(self.root, 'change', 'Change')
        self.folder = self.root / 'changes/change'
        (self.root / 'app.py').write_text('value = 1\n')
        for stage in adapter.sdlc.STAGES:
            (self.folder / (stage + '.md')).write_text(f'# {stage}\nConcrete reviewed scope.\n')
            self.commit()
            adapter.sdlc.record_approval(self.root, 'change', stage, 'alice', 'fixture', 'Approved.')
            self.commit()
        self.config = {'command': ['mock-agent'], 'timeout_seconds': 10, 'max_fix_attempts': 1,
                       'owners': {s: ['alice'] for s in adapter.sdlc.STAGES}}

    def commit(self):
        adapter.sdlc.git(self.root, 'add', '.')
        adapter.sdlc.git(self.root, 'commit', '--allow-empty', '-m', 'Fixture')

    def result(self, kind, outcome='passed'):
        (self.folder / (kind + '.md')).write_text(f'# {kind}\nObserved fixture evidence.\n')
        adapter.sdlc.record_result(self.root, 'change', kind, outcome,
                                   'changes/change/' + kind + '.md')
        self.commit()

    def test_cycle_uses_separate_review_process_and_stops_at_delivery(self):
        calls = []
        def invoke(*args, review=False):
            calls.append(review)
            self.result('review' if review else 'verification')
        self.assertEqual(adapter.cycle(self.root, 'change', self.config, invoke), 'deliver')
        self.assertEqual(calls, [False, True])

    def test_cycle_bounds_repairs(self):
        self.result('verification')
        calls = []
        def invoke(*args, review=False):
            calls.append(review)
            self.result('review' if review else 'verification', 'blocked' if review else 'passed')
        self.assertEqual(adapter.cycle(self.root, 'change', self.config, invoke), 'review-blocked')
        self.assertEqual(calls, [True, False, True])

    def test_implementation_cannot_supply_its_own_passing_review(self):
        def invoke(*args, review=False):
            self.result('verification')
            self.result('review')
        with self.assertRaisesRegex(ValueError, 'outside its stage'):
            adapter.cycle(self.root, 'change', self.config, invoke)

    def test_repair_cannot_supply_its_own_passing_review(self):
        self.result('verification')
        def invoke(*args, review=False):
            if review:
                self.result('review', 'blocked')
            else:
                self.result('verification')
                self.result('review')
        with self.assertRaisesRegex(ValueError, 'outside its stage'):
            adapter.cycle(self.root, 'change', self.config, invoke)

    def test_reviewer_cannot_rewrite_verification(self):
        self.result('verification')
        def invoke(*args, review=False):
            self.result('verification')
            self.result('review')
        with self.assertRaisesRegex(ValueError, 'outside its stage'):
            adapter.cycle(self.root, 'change', self.config, invoke)

    def test_reviewer_cannot_change_approved_artifacts(self):
        self.result('verification')
        def invoke(*args, review=False):
            (self.folder / 'spec.md').write_text('# Spec\nDifferent scope.\n')
            self.commit()
        with self.assertRaisesRegex(ValueError, 'changed approved artifacts'):
            adapter.cycle(self.root, 'change', self.config, invoke)

    def test_reviewer_cannot_change_plan_deviations(self):
        self.result('verification')
        def invoke(*args, review=False):
            with (self.folder / 'plan.md').open('a') as plan:
                plan.write('\n## Implementation deviations\nDifferent helper.\n')
            self.commit()
        with self.assertRaisesRegex(ValueError, 'changed approved artifacts'):
            adapter.cycle(self.root, 'change', self.config, invoke)

    def presentation(self, stage, revision):
        url = 'https://github.com/owner/repo/pull/1#issuecomment-10'
        presentation = {'issue_url': 'https://api.github.com/repos/owner/repo/issues/1',
                        'html_url': url, 'body': '<!-- sdlc:gate ' + json.dumps(
                            {'id': 'change', 'stage': stage, 'commit': revision,
                             'path': 'changes/change/' + stage + '.md'}) + ' -->'}
        class API:
            repository = 'owner/repo'
            def call(self, path):
                return {'permission': 'write'} if path.startswith('collaborators/') else presentation
        response = {'user': {'type': 'User', 'login': 'alice'}, 'body': stage.title() + ' approved ' + url}
        return API(), response

    def test_decision_handles_windows_snapshot_paths(self):
        revision = adapter.sdlc.git(self.root, 'rev-parse', 'HEAD').decode().strip()
        api, response = self.presentation('intent', revision)
        snapshot = adapter.sdlc.artifact_snapshot(self.root, self.folder, 'intent')
        windows = {path.replace('/', '\\'): value for path, value in snapshot.items()}
        with patch.object(adapter.sdlc, 'artifact_snapshot', return_value=windows):
            self.assertEqual(adapter.decision(api, self.root, 1, response, self.config)[:2], ('change', 'intent'))

    def test_decision_handles_checkout_line_ending_conversion(self):
        paths = (self.root / '.sdlc/project.json', self.folder / 'intent.md')
        # Establish LF blobs on every host, then simulate a CRLF checkout.
        for path in paths:
            path.write_bytes(path.read_bytes().replace(b'\r\n', b'\n'))
        self.commit()
        revision = adapter.sdlc.git(self.root, 'rev-parse', 'HEAD').decode().strip()
        api, response = self.presentation('intent', revision)
        adapter.sdlc.git(self.root, 'config', 'core.autocrlf', 'true')
        for path in paths:
            path.write_bytes(path.read_bytes().replace(b'\n', b'\r\n'))
        self.assertEqual(adapter.decision(api, self.root, 1, response, self.config)[:2], ('change', 'intent'))

    def test_decision_keeps_harmless_plan_deviations_outside_approval(self):
        revision = adapter.sdlc.git(self.root, 'rev-parse', 'HEAD').decode().strip()
        api, response = self.presentation('plan', revision)
        plan = self.folder / 'plan.md'
        plan.write_text(plan.read_text() + '\n## Implementation deviations\nSame behavior, different helper name.\n')
        self.commit()
        self.assertEqual(adapter.decision(api, self.root, 1, response, self.config)[:2], ('change', 'plan'))

    def test_repair_includes_inline_only_findings_and_all_pages(self):
        calls = []
        class API:
            def call(self, path):
                calls.append(path)
                if path.endswith('page=1'):
                    return [{'id': i, 'path': 'app.py', 'line': 2, 'body': f'Fix finding {i}'} for i in range(100)]
                return [{'id': 100, 'path': 'test_app.py', 'original_line': 5,
                         'body': 'Restore the lost regression assertion', 'diff_hunk': '@@ -1 +1 @@'}]
        evidence = adapter.repair_evidence(API(), 1, {'id': 42, 'body': ''})
        self.assertEqual(evidence['body'], '')
        self.assertEqual(len(evidence['comments']), 101)
        self.assertEqual(evidence['comments'][-1]['path'], 'test_app.py')
        self.assertIn('regression assertion', evidence['comments'][-1]['body'])
        self.assertEqual(calls, ['pulls/1/reviews/42/comments?per_page=100&page=1',
                                 'pulls/1/reviews/42/comments?per_page=100&page=2'])


class AdapterIntegrationTests(unittest.TestCase):
    def test_comment_handoff_uses_default_branch_adapter_and_same_feature_branch(self):
        import os
        import subprocess
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            origin = base / 'origin.git'
            subprocess.run(['git', 'init', '--bare', str(origin)], check=True, capture_output=True)
            trusted = base / 'trusted'
            subprocess.run(['git', 'init', '-b', 'main', str(trusted)], check=True, capture_output=True)
            git = lambda *args: adapter.sdlc.git(trusted, *args)
            git('config', 'user.name', 'Fixture')
            git('config', 'user.email', 'fixture@example.invalid')
            adapter.sdlc.setup(trusted)
            config = {'command': ['unused-agent'], 'operators': ['alice'],
                      'owners': {s: ['alice'] for s in adapter.sdlc.STAGES},
                      'max_fix_attempts': 1, 'timeout_seconds': 10}
            adapter.sdlc.write_json(trusted / '.sdlc/github.json', config)
            git('add', '.')
            git('commit', '-m', 'Trusted default configuration')
            git('remote', 'add', 'origin', str(origin))
            git('push', 'origin', 'main')
            git('switch', '-c', 'feature')
            adapter.sdlc.new(trusted, 'change', 'Change')
            (trusted / 'changes/change/intent.md').write_text('# Intent\nConcrete outcome.\n')
            git('add', '.')
            git('commit', '-m', 'Feature intent')
            head = git('rev-parse', 'HEAD').decode().strip()
            git('push', 'origin', 'feature')
            git('switch', 'main')
            event_file = base / 'event.json'
            event_file.write_text(json.dumps({'action': 'created', 'issue': {'number': 1, 'pull_request': {}},
                'comment': {'id': 20}, 'repository': {'default_branch': 'main'}}))
            # GitHub's pull_request object is populated in actual issue-comment payloads.
            event = json.loads(event_file.read_text())
            event['issue']['pull_request'] = {'url': 'https://api.github.com/repos/owner/repo/pulls/1'}
            event_file.write_text(json.dumps(event))
            posts = []
            class API:
                repository = 'owner/repo'
                token = 'fixture-token'
                def call(self, path, data=None):
                    if data is not None:
                        posts.append(data['body']); return {}
                    if path.startswith('collaborators/'):
                        return {'permission': 'write'}
                    if path == 'issues/comments/20':
                        return {'id': 20, 'issue_url': 'https://api.github.com/repos/owner/repo/issues/1',
                                'body': '@sdlc run change', 'user': {'login': 'alice', 'type': 'User'}}
                    if path == 'pulls/1':
                        return {'state': 'open', 'merged': False,
                            'head': {'repo': {'full_name': 'owner/repo'}, 'ref': 'feature', 'sha': head},
                            'base': {'repo': {'full_name': 'owner/repo'}, 'ref': 'main'}}
                    raise AssertionError(path)
            environment = {'GITHUB_REPOSITORY': 'owner/repo', 'GITHUB_TOKEN': 'fixture-token',
                           'GITHUB_EVENT_NAME': 'issue_comment', 'GITHUB_EVENT_PATH': str(event_file)}
            with patch.dict(os.environ, environment), patch.object(adapter, 'GitHub', return_value=API()), patch.object(
                    adapter, 'cycle', return_value='approve-intent'), patch('sys.argv', ['run.py', '--root', str(trusted)]):
                adapter.main()
            self.assertEqual(len(posts), 1)
            self.assertIn('sdlc:gate', posts[0])
            self.assertIn(head, posts[0])
            self.assertEqual(git('rev-parse', 'HEAD').decode().strip(), git('rev-parse', 'main').decode().strip())
            self.assertEqual(git('ls-remote', 'origin', 'refs/heads/feature').decode().split()[0], head)
