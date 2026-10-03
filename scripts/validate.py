"""Check distributable assets and local links, not model behavior or authorization."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/sdlc'


def validate():
    errors = []
    if list((ROOT / '.claude/skills').glob('sdlc-*/SKILL.md')) or (ROOT / 'scripts/install.py').exists():
        errors.append('Remove obsolete copied-package entry points')
    marketplace = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
    manifest = json.loads((PLUGIN / '.claude-plugin/plugin.json').read_text())
    if marketplace['name'] != 'ai-native-sdlc' or not marketplace.get('owner', {}).get('name'):
        errors.append('Invalid marketplace identity')
    entry, = marketplace['plugins']
    if entry['source'] != './plugins/sdlc' or entry['name'] != manifest['name']:
        errors.append('Marketplace must point to the self-contained sdlc plugin')
    if not re.fullmatch(r'\d+\.\d+\.\d+', manifest.get('version', '')):
        errors.append('Use a version for managed plugin updates')
    for name in ('intent', 'spec', 'plan', 'verification', 'review', 'delivery', 'learning', 'REVIEW'):
        path = PLUGIN / 'templates' / (name + '.md')
        if not path.is_file() or not path.read_text().startswith('# '):
            errors.append(f'Missing/malformed template: {name}')
    for name in ('start', 'status', 'review'):
        path = PLUGIN / 'skills' / name / 'SKILL.md'
        text = path.read_text()
        if not text.startswith(f'---\nname: {name}\ndescription: ') or '\n---\n' not in text[4:]:
            errors.append(f'Invalid skill frontmatter: {name}')
        if '${CLAUDE_PLUGIN_ROOT}' not in text:
            errors.append(f'Use portable bundled paths: {name}')
    for path in ROOT.rglob('*.md'):
        if '.git' in path.parts:
            continue
        text = path.read_text(encoding='utf-8')
        for link in re.findall(r'\]\(([^)]+)\)', text):
            if '://' in link or link.startswith('#'):
                continue
            if not (path.parent / link.split('#')[0]).exists():
                errors.append(f'Broken link in {path.relative_to(ROOT)}: {link}')
        if path.is_relative_to(PLUGIN):
            for relative in re.findall(r'\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+)', text):
                if not (PLUGIN / relative).is_file():
                    errors.append(f'Missing bundled resource: {relative}')
            if '.sdlc/templates' in text or '.sdlc/workflow.md' in text:
                if path.name != 'migrate.md':
                    errors.append(f'Legacy runtime dependency: {path.relative_to(ROOT)}')
    return errors


if __name__ == '__main__':
    problems = validate()
    if problems:
        raise SystemExit('\n'.join(problems))
    print('Marketplace, plugin assets and Markdown links validated.')
