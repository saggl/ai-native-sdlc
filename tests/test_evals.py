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

    def test_accepts_initial_gate_and_added_instruction_pointer(self):
        with (self.root / 'CLAUDE.md').open('a') as stream:
            stream.write('Use the SDLC run skill.\n')
        self.assertEqual(evals.check_initial_gate(self.root, self.original), [])

    def test_rejects_implementation_and_premature_spec(self):
        (self.root / 'app.py').write_text('value = 2\n')
        (self.root / 'changes/csv-import/spec.md').write_text('# Spec\nPremature\n')
        failures = evals.check_initial_gate(self.root, self.original)
        self.assertTrue(any('app.py' in failure for failure in failures))
        self.assertTrue(any('downstream' in failure for failure in failures))

    def test_rejects_fabricated_approval_and_scaffold(self):
        folder, data = evals.sdlc.state(self.root, 'csv-import')
        data['approvals'] = [{'stage': 'intent', 'snapshot': {}}]
        evals.sdlc.save(self.root, folder, data)
        (self.root / 'extra.py').write_text('pass\n')
        failures = evals.check_initial_gate(self.root, self.original)
        self.assertTrue(any('Invented approval' in failure for failure in failures))
        self.assertTrue(any('extra.py' in failure for failure in failures))
