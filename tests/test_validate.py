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
