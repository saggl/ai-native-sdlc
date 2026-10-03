import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PLUGIN = Path(__file__).resolve().parents[1] / 'plugins/sdlc'
SCRIPT = PLUGIN / 'scripts/sdlc.py'
spec = importlib.util.spec_from_file_location('sdlc', SCRIPT)
sdlc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sdlc)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'project with spaces'
        self.root.mkdir()
        self.git('init')
        self.git('config', 'user.name', 'Workflow Test')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'core.autocrlf', 'false')
        (self.root / 'CLAUDE.md').write_text('Keep these project rules.\n')
        (self.root / 'app.py').write_text('value = 1\n')
        (self.root / '.gitignore').write_text('__pycache__/\n*.pyc\n')
        sdlc.setup(self.root)
        sdlc.new(self.root, 'csv-import', 'CSV import')
        self.folder = self.root / 'changes/csv-import'

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], stderr=subprocess.STDOUT)

    def commit(self):
        self.git('add', '.')
        self.git('commit', '--allow-empty', '-m', 'Test fixture')

    def approve(self, stage):
        (self.folder / (stage + '.md')).write_text(f'# {stage}\nA concrete, reviewed {stage}.\n')
        self.commit()
        sdlc.record_approval(self.root, 'csv-import', stage, 'Test Owner',
                             'fixture:explicit-decision', 'I approve this fixture revision.')
        self.commit()

    def prepare(self):
        for stage in sdlc.STAGES:
            self.approve(stage)

    def result(self, kind, outcome='passed'):
        report = self.folder / (kind + '.md')
        report.write_text(f'# {kind}\nObserved test fixture evidence.\n')
        return sdlc.record_result(self.root, 'csv-import', kind, outcome,
                                  str(report.relative_to(self.root)))

    def next(self):
        return sdlc.status(self.root, 'csv-import')['next']

    def test_setup_preserves_project_files_and_custom_configuration(self):
        original = (self.root / 'CLAUDE.md').read_bytes()
        config = self.root / '.sdlc/project.json'
        data = json.loads(config.read_text())
        data['commands'] = {'test': 'python -m unittest'}
        config.write_text(json.dumps(data))
        original_config = config.read_bytes()
        sdlc.setup(self.root)
        self.assertEqual(config.read_bytes(), original_config)
        self.assertEqual((self.root / 'CLAUDE.md').read_bytes(), original)

    def test_read_only_status_before_setup(self):
        blank = Path(self.temp.name) / 'blank'
        blank.mkdir()
        self.assertEqual(sdlc.all_status(blank)['next'], 'setup')
        self.assertEqual(list(blank.iterdir()), [])

    def test_new_repository_without_initial_commit(self):
        data = json.loads((self.folder / 'state.json').read_text())
        self.assertIsNone(data['base_commit'])
        self.assertEqual(self.next(), 'approve-intent')
        self.approve('intent')
        self.assertEqual(self.next(), 'draft-spec')

    def test_collision_and_traversal_do_not_overwrite(self):
        before = (self.folder / 'state.json').read_bytes()
        with self.assertRaises(FileExistsError):
            sdlc.new(self.root, 'csv-import', 'Another task')
        with self.assertRaises(ValueError):
            sdlc.new(self.root, '../outside', 'Escape')
        self.assertEqual((self.folder / 'state.json').read_bytes(), before)

    def test_symlink_workflow_path_rejected(self):
        outside = Path(self.temp.name) / 'outside'
        outside.mkdir()
        link = self.root / 'other'
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest('Platform does not permit symlink creation')
        config = json.loads((self.root / '.sdlc/project.json').read_text())
        config['changes_dir'] = 'other'
        (self.root / '.sdlc/project.json').write_text(json.dumps(config))
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            sdlc.new(self.root, 'escape', 'Escape')
        self.assertEqual(list(outside.iterdir()), [])

    def test_legacy_package_is_detected_without_overwriting(self):
        (self.root / '.sdlc/project.json').unlink()
        (self.root / '.sdlc/package-lock.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'Legacy'):
            sdlc.setup(self.root)
        self.assertFalse((self.root / '.sdlc/project.json').exists())

    def test_cannot_skip_approval_or_overwrite_a_draft(self):
        with self.assertRaisesRegex(ValueError, 'intent'):
            sdlc.draft(self.root, 'csv-import', 'spec')
        self.approve('intent')
        sdlc.draft(self.root, 'csv-import', 'spec')
        with self.assertRaises(FileExistsError):
            sdlc.draft(self.root, 'csv-import', 'spec')

    def test_cannot_record_approval_for_template_or_uncommitted_content(self):
        with self.assertRaisesRegex(ValueError, 'template'):
            sdlc.record_approval(self.root, 'csv-import', 'intent', 'Owner', 'Evidence', 'Approved')
        self.approve('intent')
        (self.folder / 'intent.md').write_text('# Changed intent\n')
        with self.assertRaisesRegex(ValueError, 'Commit'):
            sdlc.record_approval(self.root, 'csv-import', 'intent', 'Owner', 'Evidence', 'Approved')

    def test_resume_from_saved_approvals_and_detect_upstream_changes(self):
        self.prepare()
        self.assertEqual(self.next(), 'implement-and-verify')
        process = subprocess.run([sys.executable, str(SCRIPT), '--root', str(self.root),
                                  'status', 'csv-import'], capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads(process.stdout)['next'], 'implement-and-verify')
        (self.folder / 'spec.md').write_text('# Different behavior\n')
        self.assertEqual(self.next(), 'approve-spec')

    def test_policy_change_invalidates_decisions(self):
        self.prepare()
        (self.root / 'CLAUDE.md').write_text('A new constraint\n')
        self.assertEqual(self.next(), 'approve-intent')

    def test_full_lifecycle_and_historical_completion(self):
        self.prepare()
        expected = ('review', 'deliver', 'observe-and-learn', 'complete')
        for kind, next_stage in zip(sdlc.RESULTS, expected):
            self.result(kind)
            self.commit()
            self.assertEqual(self.next(), next_stage)
        (self.root / 'app.py').write_text('value = 2\n')
        self.assertEqual(self.next(), 'complete')
        sdlc.new(self.root, 'next-change', 'Next')
        self.assertEqual(len(sdlc.all_status(self.root)['changes']), 2)
        with self.assertRaisesRegex(ValueError, 'complete'):
            self.result('verification')

    def test_blocked_or_unrun_verification_cannot_advance(self):
        self.prepare()
        self.result('verification', 'blocked')
        self.assertEqual(self.next(), 'implement-and-verify')
        with self.assertRaisesRegex(ValueError, 'verification'):
            self.result('review')

    def test_code_changes_deleted_and_untracked_files_invalidate_results(self):
        self.prepare()
        for action in ('modify', 'delete', 'untracked'):
            with self.subTest(action=action):
                (self.root / 'app.py').write_text('value = 1\n')
                extra = self.root / 'extra.py'
                if extra.exists():
                    extra.unlink()
                self.result('verification')
                self.result('review')
                if action == 'modify':
                    (self.root / 'app.py').write_text('value = 2\n')
                elif action == 'delete':
                    (self.root / 'app.py').unlink()
                else:
                    extra.write_text('value = 3\n')
                self.assertEqual(self.next(), 'implement-and-verify')

    def test_edited_report_and_new_verification_invalidate_review(self):
        self.prepare()
        self.result('verification')
        self.result('review')
        (self.folder / 'review.md').write_text('Tampered report\n')
        self.assertEqual(self.next(), 'review')
        self.result('review')
        self.result('verification')
        self.assertEqual(self.next(), 'review')

    def test_result_report_cannot_escape_change_directory(self):
        self.prepare()
        with self.assertRaisesRegex(ValueError, 'Write this report'):
            sdlc.record_result(self.root, 'csv-import', 'verification', 'passed', '../outside.md')

    def test_helper_survives_plugin_distribution_copy(self):
        import shutil
        copy = Path(self.temp.name) / 'installed-plugin'
        shutil.copytree(PLUGIN, copy, ignore=shutil.ignore_patterns('__pycache__'))
        result = subprocess.run([sys.executable, str(copy / 'scripts/sdlc.py'), '--root',
                                 str(self.root), 'status'], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['changes'][0]['id'], 'csv-import')

    def test_unknown_schema_and_nested_root_fail_clearly(self):
        config = self.root / '.sdlc/project.json'
        config.write_text('{"schema": 99}')
        with self.assertRaisesRegex(ValueError, 'schema'):
            sdlc.config(self.root)
        nested = self.root / 'nested'
        nested.mkdir()
        with self.assertRaisesRegex(ValueError, 'repository root'):
            sdlc.repository(nested)

    def test_committed_deletion_survives_evidence_commit(self):
        self.prepare()
        (self.root / 'app.py').unlink()
        with self.assertRaisesRegex(ValueError, 'Commit'):
            self.result('verification')
        self.commit()
        self.result('verification')
        self.commit()
        self.assertEqual(self.next(), 'review')

    def test_different_staged_and_tested_code_cannot_be_recorded(self):
        self.prepare()
        app = self.root / 'app.py'
        app.write_text('value = 999\n')
        self.git('add', 'app.py')
        app.write_text('value = 2\n')
        with self.assertRaisesRegex(ValueError, 'Commit'):
            self.result('verification')

    def test_changed_commit_invalidates_results_even_with_same_working_bytes(self):
        self.prepare()
        self.result('verification')
        self.result('review')
        app = self.root / 'app.py'
        app.write_text('value = 999\n')
        self.git('add', 'app.py')
        app.write_text('value = 1\n')
        self.git('commit', '-m', 'Different staged code')
        self.assertEqual(self.next(), 'implement-and-verify')
        with self.assertRaisesRegex(ValueError, 'Commit'):
            self.result('delivery')

    def test_deleted_optional_policy_must_be_committed_for_approval(self):
        self.approve('intent')
        (self.root / 'CLAUDE.md').unlink()
        with self.assertRaisesRegex(ValueError, 'Commit'):
            sdlc.record_approval(self.root, 'csv-import', 'intent', 'Owner', 'Evidence', 'Approved')
        self.commit()
        record = sdlc.record_approval(self.root, 'csv-import', 'intent', 'Owner', 'Evidence', 'Approved')
        self.assertIsNone(record['snapshot']['CLAUDE.md'])

    def test_real_template_syntax_is_allowed_in_spec_and_evidence(self):
        self.approve('intent')
        (self.folder / 'spec.md').write_text('# Spec\nAC-1: Render {{title}} and <!-- literal markup -->.\n')
        self.commit()
        sdlc.record_approval(self.root, 'csv-import', 'spec', 'Owner', 'Evidence', 'Approved')
        self.approve('plan')
        report = self.folder / 'verification.md'
        report.write_text('# Evidence\nRendered {{title}} and <!-- literal markup --> as expected.\n')
        sdlc.record_result(self.root, 'csv-import', 'verification', 'passed',
                           str(report.relative_to(self.root)))
        self.assertEqual(self.next(), 'review')

    def test_unfilled_report_cannot_be_recorded(self):
        self.prepare()
        report = self.folder / 'verification.md'
        report.write_text((PLUGIN / 'templates/verification.md').read_text())
        with self.assertRaisesRegex(ValueError, 'template prompts'):
            sdlc.record_result(self.root, 'csv-import', 'verification', 'passed',
                               str(report.relative_to(self.root)))


if __name__ == '__main__':
    unittest.main()
