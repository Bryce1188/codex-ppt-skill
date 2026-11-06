#!/usr/bin/env python3
"""Locate installed Superpowers process skills; never install or invoke them."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

NAMES = ('brainstorming', 'writing-plans', 'verification-before-completion')


def entry(path: Path, name: str):
    if not path.is_file():
        return None
    body = path.read_text(encoding='utf-8-sig')
    if not re.search(r'(?m)^name:\s*[\"\']?' + re.escape(name) + r'[\"\']?\s*$', body):
        return None
    return {'path': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def inspect(root: Path):
    router = entry(root / 'SKILL.md', 'superpowers')
    skills = {}
    for name in NAMES:
        for candidate in (root / 'skills' / name / 'SKILL.md', root / name / 'SKILL.md'):
            found = entry(candidate, name)
            if found:
                skills[name] = found
                break
    return {'router': router, 'skills': skills, 'missing': [n for n in NAMES if n not in skills]}


def resolve(skill_root: Path, explicit=None, installed_roots=None):
    if explicit is not None:
        root = Path(explicit).expanduser()
        if root.is_file():
            root = root.parent
        result = inspect(root)
        if not result['skills']:
            raise ValueError(f'No matching Superpowers process skills at {root}')
        return {**result, 'resolved_from': 'explicit', 'available': True}
    if installed_roots is None:
        installed_roots = [Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'skills',
                           Path.home() / '.agents/skills']
    candidates = [('sibling', skill_root.parent / 'superpowers')]
    for root in installed_roots:
        candidates.extend([('installed-pack', Path(root) / 'superpowers'), ('installed-split', Path(root))])
    partial = None
    for origin, root in candidates:
        result = inspect(root)
        if result['skills']:
            result.update(resolved_from=origin, available=True)
            if not result['missing']:
                return result
            if partial is None:
                partial = result
    return partial or {'available': False, 'router': None, 'skills': {}, 'missing': list(NAMES),
                       'resolved_from': 'none', 'fallback': 'docs/intake-and-superpowers.md'}


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--path', type=Path)
    args = parser.parse_args()
    try:
        result = resolve(Path(__file__).resolve().parent.parent, args.path)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'Cannot load Superpowers: {exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
