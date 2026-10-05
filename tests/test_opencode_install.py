import hashlib
import json
import subprocess
import shutil
from unittest.mock import patch
import sys
import tempfile
import unittest
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location


ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location('opencode_install', ROOT / 'scripts/install_opencode.py')
installer = module_from_spec(spec)
spec.loader.exec_module(installer)


class OpenCodeInstallTests(unittest.TestCase):
    def test_install_and_update_keeps_helper_usable(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'opencode'
            skill = installer.install(config)
            self.assertTrue((skill / 'SKILL.md').is_file())
            self.assertTrue((skill / 'references/stages.md').is_file())
            self.assertTrue((config / 'commands/sdlc.md').is_file())
            self.assertIn('status', subprocess.check_output([
                sys.executable, str(skill / 'scripts/sdlc.py'), '--help'
            ], text=True))
            installer.install(config)
            self.assertTrue((skill / installer.MARKER).is_file())

    def test_conflicts_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'opencode'
            command = config / 'commands/sdlc.md'
            command.parent.mkdir(parents=True)
            command.write_text('my command')
            with self.assertRaises(ValueError):
                installer.install(config)
            self.assertEqual(command.read_text(), 'my command')
            self.assertFalse((config / 'skills/sdlc').exists())

            command.unlink()
            skill = config / 'skills/sdlc'
            skill.mkdir(parents=True)
            (skill / 'SKILL.md').write_text('my skill')
            with self.assertRaises(ValueError):
                installer.install(config)
            self.assertEqual((skill / 'SKILL.md').read_text(), 'my skill')

    def test_upstream_update_replaces_only_unmodified_installed_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / 'config'
            skill = installer.install(config)
            sources = root / 'commands'
            shutil.copytree(installer.COMMANDS, sources)
            incoming = sources / 'sdlc.md'
            incoming.write_text(incoming.read_text() + '\nNew upstream instructions.\n')
            with patch.object(installer, 'COMMANDS', sources):
                installer.install(config)
                installed = config / 'commands/sdlc.md'
                self.assertEqual(installed.read_bytes(), incoming.read_bytes())
                installed.write_text('local customization')
                marker = (skill / installer.MARKER).read_bytes()
                incoming.write_text(incoming.read_text() + 'Another update.\n')
                with self.assertRaises(ValueError):
                    installer.install(config)
                self.assertEqual(installed.read_text(), 'local customization')
                self.assertEqual((skill / installer.MARKER).read_bytes(), marker)
