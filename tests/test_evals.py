import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('agent_evals', Path(__file__).resolve().parents[1] / 'evals/run.py')
evals = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evals)


class EvalChecksTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        evals.git(self.root, 'init')
        self.original = {'app.py': b'value = 1\n', 'CLAUDE.md': b'Preserve this rule.\n'}
        for name, content in self.original.items():
            (self.root / name).write_bytes(content)
        evals.sdlc.setup(self.root)
        evals.sdlc.new(self.root, 'csv-import', 'CSV import')
        (self.root / 'changes/csv-import/intent.md').write_text('# Intent\nImport CSV with line-number errors.\n')

    def tearDown(self):
        self.temp.cleanup()

    def fill_preparation(self):
        for stage in ('spec', 'plan'):
            (self.root / ('changes/csv-import/' + stage + '.md')).write_text('# Concrete ' + stage + '\n')

    def test_accepts_initial_gate_and_added_instruction_pointer(self):
        self.fill_preparation()
        with (self.root / 'CLAUDE.md').open('a') as stream:
            stream.write('Use the SDLC run skill.\n')
        self.assertEqual(evals.check_initial_gate(self.root, self.original), [])

    def test_rejects_implementation_and_incomplete_preparation(self):
        (self.root / 'app.py').write_text('value = 2\n')
        (self.root / 'changes/csv-import/spec.md').write_text('# Spec\nPremature\n')
        failures = evals.check_initial_gate(self.root, self.original)
        self.assertTrue(any('app.py' in failure for failure in failures))
        self.assertTrue(any('Plan was not filled' in failure for failure in failures))

    def test_rejects_fabricated_approval_and_scaffold(self):
        folder, data = evals.sdlc.state(self.root, 'csv-import')
        data['approvals'] = [{'stage': 'intent', 'snapshot': {}}]
        evals.sdlc.save(self.root, folder, data)
        (self.root / 'extra.py').write_text('pass\n')
        failures = evals.check_initial_gate(self.root, self.original)
        self.assertTrue(any('Invented approval' in failure for failure in failures))
        self.assertTrue(any('extra.py' in failure for failure in failures))


class LifecycleFixtureTests(unittest.TestCase):
    def test_lifecycle_fixtures_are_valid_and_do_not_pass_unexecuted_stages(self):
        for case in evals.scenarios.CASES:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                evals.git(root, 'init')
                evals.git(root, 'config', 'user.name', 'Fixture')
                evals.git(root, 'config', 'user.email', 'fixture@example.invalid')
                task, protected = evals.scenarios.prepare(root, case, evals.sdlc)
                self.assertIn('Synthetic', task.title())
                failures = evals.scenarios.check(root, case, protected, evals.sdlc)
                if case == 'stale-spec':
                    # Correct behavior here is preserving the already-blocked state.
                    self.assertEqual(failures, [])
                else:
                    self.assertTrue(failures, 'An unexecuted lifecycle stage must not pass')

    def test_observation_checker_rejects_false_success_before_window(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evals.git(root, 'init')
            evals.git(root, 'config', 'user.name', 'Fixture')
            evals.git(root, 'config', 'user.email', 'fixture@example.invalid')
            _, protected = evals.scenarios.prepare(root, 'observation-pending', evals.sdlc)
            (root / 'changes/fixture/learning.md').write_text('# Learning\nPretended window elapsed.\n')
            evals.sdlc.record_result(root, 'fixture', 'learning', 'passed', 'changes/fixture/learning.md')
            self.assertTrue(evals.scenarios.check(root, 'observation-pending', protected, evals.sdlc))
