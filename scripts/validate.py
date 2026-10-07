#!/usr/bin/env python3
"""Validate shared skill metadata, portable commands, and plugin packaging."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ['recon', 'architect', 'design', 'build', 'backend', 'test', 'diff',
          'entrepreneur', 'brand', 'launch', 'deploy']


def validate(root=ROOT):
    errors = []
    for suffix in SKILLS:
        name = 'replica-' + suffix
        path = root / 'skills' / name / 'SKILL.md'
        if not path.is_file():
            errors.append('Missing ' + name)
            continue
        body = path.read_text(encoding='utf-8')
        match = re.match(r'^---\n(.*?)\n---\n', body, re.S)
        if not match or not re.search(r'^name: ' + re.escape(name) + r'$', match[1], re.M):
            errors.append(name + ': invalid name/frontmatter')
        if not match or not re.search(r'^description: >-\n  \S', match[1], re.M):
            errors.append(name + ': missing folded description')
        for heading in ['## Working contract', '## Output', '## Evidence and completion']:
            if heading not in body:
                errors.append(name + ': missing ' + heading)
        if '~/.claude/' in body or 'Claude never' in body:
            errors.append(name + ': runtime-specific instruction')
        for helper in re.findall(r'\$SKILL_DIR/([a-z_]+\.py)', body):
            if not (path.parent / helper).is_file():
                errors.append(name + ': missing helper ' + helper)
        for example in path.parent.glob('*.example.json'):
            try:
                document = json.loads(example.read_text(encoding='utf-8'))
                if type(document.get('schema_version')) is not int or document['schema_version'] != 1:
                    errors.append(name + ': invalid example schema')
            except (OSError, ValueError, AttributeError, KeyError):
                errors.append(name + ': invalid JSON example')
        for command in re.findall(r'^python3 (.+)$', body, re.M):
            if not command.startswith(('"$SKILL_DIR/', '"$SKILLS_ROOT/')):
                errors.append(name + ': unresolved helper path')
    try:
        plugin = json.loads((root / '.claude-plugin/plugin.json').read_text())
        marketplace = json.loads((root / '.claude-plugin/marketplace.json').read_text())
        if plugin['name'] != 'replicate-skills' or plugin['skills'] != './skills/':
            errors.append('Invalid plugin identity or skills path')
        codex = json.loads((root / '.codex-plugin/plugin.json').read_text())
        codex_market = json.loads((root / '.agents/plugins/marketplace.json').read_text())
        for field in ['name', 'version', 'skills']:
            if codex[field] != plugin[field]:
                errors.append('Native manifest mismatch: ' + field)
        if codex_market['name'] != plugin['name'] or codex_market['plugins'][0]['source'] != {'source': 'local', 'path': './'}:
            errors.append('Invalid Codex marketplace identity or source')
        if marketplace['name'] != plugin['name'] or marketplace['plugins'][0]['name'] != plugin['name']:
            errors.append('Marketplace identity mismatch')
    except (OSError, ValueError, TypeError, KeyError, IndexError) as error:
        errors.append('Invalid plugin packaging: ' + str(error))
    workflows = sorted(path.name for path in (root / '.github/workflows').glob('*.y*ml'))
    if workflows != ['release.yml']:
        errors.append('Only the release workflow may be enabled')
    return errors


if __name__ == '__main__':
    problems = validate()
    for problem in problems:
        print(problem, file=sys.stderr)
    if not problems:
        print('Validated eleven shared skills, both native manifests, and release-only automation.')
    sys.exit(bool(problems))
