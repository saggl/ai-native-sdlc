import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('validate', Path(__file__).resolve().parents[1] / 'scripts/validate.py')
validate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate)


class ValidateTests(unittest.TestCase):
    def test_repository_is_valid(self):
        self.assertEqual(validate.validate(), [])

    def test_case_only_path_difference_is_rejected(self):
        errors = validate.case_collisions(['a/REVIEW.md', 'a/review.md', 'b.md'])
        self.assertEqual(len(errors), 1)
        self.assertIn('a/REVIEW.md', errors[0])

    def test_coverage_requires_every_play_with_an_asset(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            guide = Path(temp) / 'guide.md'
            rows = ''.join(f'| Step {i} | [a](a.md) | n |\n' for i in range(15))
            guide.write_text('## Playbook coverage\n| Play | Asset | Notes |\n| --- | --- | --- |\n' + rows)
            self.assertEqual(validate.coverage(guide), ['Playbook coverage needs 16 plays'])
            guide.write_text(guide.read_text() + '| Missing | none | n |\n## Next\n')
            self.assertEqual(validate.coverage(guide), ['Play without a linked asset: Missing'])
