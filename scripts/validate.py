"""Validate package structure, not approval authenticity or semantic correctness."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def validate():
    errors = []
    for name in ('README', 'CLAUDE', 'REVIEW', 'intent', 'spec', 'plan', 'change', 'review-report'):
        path = ROOT / '.sdlc/templates' / (name + '.md')
        if not path.is_file() or not path.read_text().startswith('# '):
            errors.append(f'Missing or malformed template: {name}')
    for name in ('init', 'prepare', 'implement', 'review'):
        skill_name = 'sdlc-' + name
        path = ROOT / '.claude/skills' / skill_name / 'SKILL.md'
        if not path.is_file():
            errors.append(f'Missing skill: {skill_name}')
            continue
        text = path.read_text()
        if not text.startswith(f'---\nname: {skill_name}\ndescription: ') or '\n---\n' not in text[4:]:
            errors.append(f'Invalid frontmatter: {skill_name}')
        if '.sdlc/workflow.md' not in text or '.sdlc/templates' not in text:
            errors.append(f'Missing package references: {skill_name}')
    for path in ROOT.rglob('*.md'):
        for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if '://' in link or link.startswith('#'):
                continue
            dest = path.parent / link.split('#')[0]
            if not dest.exists():
                errors.append(f'Broken link in {path.relative_to(ROOT)}: {link}')
    return errors

if __name__ == '__main__':
    errors = validate()
    if errors:
        raise SystemExit('\n'.join(errors))
    print('Package structure and local Markdown links validated.')
