"""Install the bundled skill and single command into OpenCode's global config."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins' / 'sdlc'
COMMANDS = ROOT / 'opencode' / 'commands'
NAMES = ('sdlc.md',)
LEGACY_NAMES = ('sdlc-start.md', 'sdlc-status.md', 'sdlc-review.md')
MARKER = '.ai-native-sdlc-install'


def install(config: Path):
    skill = config / 'skills' / 'sdlc'
    commands = config / 'commands'
    if skill.exists() and not (skill / MARKER).is_file():
        raise ValueError(f'Refusing to replace an existing skill: {skill}')
    # Older installs have a plain-text marker; adopt only byte-identical commands.
    previous = {}
    marker = skill / MARKER
    if marker.is_file():
        try:
            saved = json.loads(marker.read_text())
            if isinstance(saved, dict) and isinstance(saved.get('commands'), dict):
                previous = saved['commands']
        except (ValueError, UnicodeError):
            pass
    hashes = {}
    for name in NAMES:
        incoming = (COMMANDS / name).read_bytes()
        hashes[name] = hashlib.sha256(incoming).hexdigest()
        path = commands / name
        if path.exists():
            installed = path.read_bytes()
            if (installed != incoming and
                    hashlib.sha256(installed).hexdigest() != previous.get(name)):
                raise ValueError(f'Refusing to replace an existing command: {path}')

    # Build outside the live skill directory, then replace our own installation.
    skill.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.sdlc-', dir=skill.parent) as temporary:
        staging = Path(temporary) / 'sdlc'
        shutil.copytree(PLUGIN, staging, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        (staging / MARKER).write_text(json.dumps({'commands': hashes}) + '\n')
        if skill.exists():
            shutil.rmtree(skill)
        staging.rename(skill)
    commands.mkdir(parents=True, exist_ok=True)
    for name in NAMES:
        shutil.copy2(COMMANDS / name, commands / name)
    # Remove only legacy commands whose bytes still match this install's saved hashes.
    for name in LEGACY_NAMES:
        path = commands / name
        if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == previous.get(name):
            path.unlink()
    return skill


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config-dir', type=Path, default=Path.home() / '.config/opencode')
    args = parser.parse_args()
    try:
        print(f'Installed OpenCode SDLC at {install(args.config_dir.expanduser())}')
    except ValueError as error:
        parser.exit(1, f'{error}\n')
