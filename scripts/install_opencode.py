"""Install the bundled skill and commands into OpenCode's global config."""

import argparse
from pathlib import Path
import shutil
import tempfile


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins' / 'sdlc'
COMMANDS = ROOT / 'opencode' / 'commands'
NAMES = ('sdlc-start.md', 'sdlc-status.md', 'sdlc-review.md')
MARKER = '.ai-native-sdlc-install'


def install(config: Path):
    skill = config / 'skills' / 'sdlc'
    commands = config / 'commands'
    if skill.exists() and not (skill / MARKER).is_file():
        raise ValueError(f'Refusing to replace an existing skill: {skill}')
    for name in NAMES:
        path = commands / name
        if path.exists() and path.read_bytes() != (COMMANDS / name).read_bytes():
            raise ValueError(f'Refusing to replace an existing command: {path}')

    # Build outside the live skill directory, then replace our own installation.
    skill.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.sdlc-', dir=skill.parent) as temporary:
        staging = Path(temporary) / 'sdlc'
        shutil.copytree(PLUGIN, staging, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        (staging / MARKER).write_text('Installed by scripts/install_opencode.py\n')
        if skill.exists():
            shutil.rmtree(skill)
        staging.rename(skill)
    commands.mkdir(parents=True, exist_ok=True)
    for name in NAMES:
        shutil.copy2(COMMANDS / name, commands / name)
    return skill


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config-dir', type=Path, default=Path.home() / '.config/opencode')
    args = parser.parse_args()
    try:
        print(f'Installed OpenCode SDLC at {install(args.config_dir.expanduser())}')
    except ValueError as error:
        parser.exit(1, f'{error}\n')
