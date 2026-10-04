"""Check distributable assets and local links, not model behavior or authorization."""
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/sdlc'


def validate():
    errors = []
    if list((ROOT / '.claude/skills').glob('sdlc-*/SKILL.md')) or (ROOT / 'scripts/install.py').exists():
        errors.append('Remove obsolete copied-package entry points')
    marketplace = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
    manifest = json.loads((PLUGIN / '.claude-plugin/plugin.json').read_text())
    portable = json.loads((PLUGIN / 'plugin.json').read_text())
    codex_marketplace = json.loads((ROOT / '.agents/plugins/marketplace.json').read_text())
    if marketplace['name'] != 'ai-native-sdlc' or not marketplace.get('owner', {}).get('name'):
        errors.append('Invalid marketplace identity')
    entry, = marketplace['plugins']
    if entry['source'] != './plugins/sdlc' or entry['name'] != manifest['name']:
        errors.append('Marketplace must point to the self-contained sdlc plugin')
    if not re.fullmatch(r'\d+\.\d+\.\d+', manifest.get('version', '')):
        errors.append('Use a version for managed plugin updates')
    if portable.get('name') != manifest['name'] or portable.get('version') != manifest['version']:
        errors.append('Claude and portable plugin identities must match')
    codex_entry, = codex_marketplace['plugins']
    if (codex_marketplace['name'] != marketplace['name'] or
            codex_entry['name'] != manifest['name'] or
            codex_entry['source'] != {'source': 'local', 'path': './plugins/sdlc'}):
        errors.append('Invalid Codex marketplace entry')
    if not (PLUGIN / 'SKILL.md').read_text().startswith('---\nname: sdlc\ndescription: '):
        errors.append('Invalid OpenCode SDLC skill')
    command = ROOT / 'opencode/commands/sdlc.md'
    if not command.is_file() or 'Load the `sdlc` skill' not in command.read_text():
        errors.append('Missing OpenCode SDLC command')
    skill = PLUGIN / 'skills/run/SKILL.md'
    if not skill.is_file() or not skill.read_text().startswith('---\nname: run\ndescription: '):
        errors.append('Missing single Claude/Codex SDLC skill')
    for name in ('intent', 'spec', 'plan', 'verification', 'review', 'delivery', 'learning', 'review-policy'):
        path = PLUGIN / 'templates' / (name + '.md')
        if not path.is_file() or not path.read_text().startswith('# '):
            errors.append(f'Missing/malformed template: {name}')
    for name in ('start', 'status', 'review'):
        path = PLUGIN / 'references/workflows' / (name + '.md')
        text = path.read_text()
        if '<plugin-root>' not in text or '${CLAUDE_PLUGIN_ROOT}' not in text:
            errors.append(f'Use resolved bundled paths: {name}')
    for path in ROOT.rglob('*.md'):
        if '.git' in path.parts:
            continue
        text = path.read_text(encoding='utf-8')
        if re.search(r'/sdlc:(?:start|review|status)\b|/sdlc-(?:review|status)\b', text):
            errors.append(f'Obsolete user command in {path.relative_to(ROOT)}')
        for link in re.findall(r'\]\(([^)]+)\)', text):
            if '://' in link or link.startswith('#'):
                continue
            if not (path.parent / link.split('#')[0]).exists():
                errors.append(f'Broken link in {path.relative_to(ROOT)}: {link}')
        if path.is_relative_to(PLUGIN):
            for relative in re.findall(r'<plugin-root>/([\w./-]+)', text):
                if not (PLUGIN / relative).is_file():
                    errors.append(f'Missing bundled resource: {relative}')
            if '.sdlc/templates' in text or '.sdlc/workflow.md' in text:
                if path.name != 'migrate.md':
                    errors.append(f'Legacy runtime dependency: {path.relative_to(ROOT)}')
    errors += case_collisions(tracked_files())
    return errors


def tracked_files():
    out = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-z'], capture_output=True, check=True).stdout
    return [name for name in out.decode().split('\0') if name]


def case_collisions(paths):
    # Two names differing only by case overwrite each other on macOS and Windows checkouts.
    seen = {}
    for path in paths:
        seen.setdefault(path.lower(), []).append(path)
    return [f'Case-insensitive path collision: {", ".join(names)}'
            for names in seen.values() if len(names) > 1]


if __name__ == '__main__':
    problems = validate()
    if problems:
        raise SystemExit('\n'.join(problems))
    print('Marketplaces, plugin assets and Markdown links validated.')
