"""Install the complete SDLC package without overwriting existing files."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

SOURCE = Path(__file__).resolve().parents[1]

def install(target):
    target = Path(target).resolve()
    if not target.is_dir():
        raise ValueError('Target must be an existing directory')
    if target == SOURCE or SOURCE in target.parents or target in SOURCE.parents:
        raise ValueError('Target and source must not overlap')
    revision = subprocess.check_output(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], text=True).strip()
    dirty = subprocess.check_output(['git', '-C', str(SOURCE), 'status', '--porcelain'], text=True)
    if dirty.strip():
        raise ValueError('Use a clean committed source checkout')
    files = sorted(p for base in (SOURCE / '.sdlc', SOURCE / '.claude/skills') for p in base.rglob('*') if p.is_file())
    outputs = {p.relative_to(SOURCE): p.read_bytes() for p in files}
    lock = {
        'version': (SOURCE / '.sdlc/VERSION').read_text().strip(),
        'source_repository': 'https://github.com/saggl/ai-native-sdlc',
        'source_commit': revision,
        'files': {str(p): hashlib.sha256(data).hexdigest() for p, data in outputs.items()},
    }
    outputs[Path('.sdlc/package-lock.json')] = (json.dumps(lock, indent=2) + '\n').encode()
    # Preflight every destination before creating anything; reject symlink escapes.
    for rel in outputs:
        dest = target / rel
        for component in (dest, *dest.parents):
            if component == target:
                break
            if component.is_symlink():
                raise ValueError(f'Symlink destination is not supported: {component}')
            if component.exists() and component != dest and not component.is_dir():
                raise ValueError(f'Parent is not a directory: {component}')
        if dest.exists():
            raise ValueError(f'Refusing to overwrite: {dest}')
    for rel, data in outputs.items():
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open('xb') as handle:
            handle.write(data)
    return len(outputs)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target')
    args = parser.parse_args()
    try:
        print(f'Installed {install(args.target)} files; run /sdlc-init in the target repository.')
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f'Installation stopped: {exc}\n')
