import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('installer', Path(__file__).resolve().parents[1] / 'scripts/install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)

class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.target = Path(self.temp.name) / 'target'
        self.target.mkdir()
        # Supply deterministic Git metadata; filesystem behavior uses real files.
        self.git = patch.object(installer.subprocess, 'check_output', side_effect=lambda args, **kw: 'a' * 40 if 'rev-parse' in args else '')
        self.git.start()
    def tearDown(self):
        self.git.stop()
        self.temp.cleanup()
    def test_complete_package_and_preserved_project_instructions(self):
        (self.target / 'CLAUDE.md').write_text('Existing instructions')
        count = installer.install(self.target)
        lock = json.loads((self.target / '.sdlc/package-lock.json').read_text())
        self.assertEqual(len(lock['files']) + 1, count)
        self.assertEqual((self.target / 'CLAUDE.md').read_text(), 'Existing instructions')
        for rel, digest in lock['files'].items():
            self.assertEqual(installer.hashlib.sha256((self.target / rel).read_bytes()).hexdigest(), digest)
    def test_collision_fails_before_any_new_files(self):
        existing = self.target / '.sdlc/VERSION'
        existing.parent.mkdir()
        existing.write_text('keep')
        with self.assertRaisesRegex(ValueError, 'overwrite'):
            installer.install(self.target)
        self.assertEqual(existing.read_text(), 'keep')
        self.assertFalse((self.target / '.claude').exists())
    def test_symlink_destination_rejected(self):
        outside = Path(self.temp.name) / 'outside'
        outside.mkdir()
        (self.target / '.sdlc').symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            installer.install(self.target)
        self.assertEqual(list(outside.iterdir()), [])
    def test_dirty_source_rejected(self):
        with patch.object(installer.subprocess, 'check_output', side_effect=['b' * 40, ' M README.md']):
            with self.assertRaisesRegex(ValueError, 'clean'):
                installer.install(self.target)
        self.assertEqual(list(self.target.iterdir()), [])

if __name__ == '__main__':
    unittest.main()
