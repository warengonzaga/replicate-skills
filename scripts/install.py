#!/usr/bin/env python3
"""Install shared skills for Codex or Claude Code without silent overwrites."""
import argparse
import datetime
from pathlib import Path
import shutil
import sys
import tempfile

SOURCE = Path(__file__).resolve().parent.parent / "skills"


def available(source=SOURCE):
    return sorted(p.name for p in source.glob('replica-*') if (p / 'SKILL.md').is_file())


def install(source, destination, names, replace=False, dry_run=False):
    source, destination = Path(source), Path(destination).expanduser().absolute()
    names = list(dict.fromkeys(names))
    if not names or any(name not in available(source) for name in names):
        raise ValueError('Choose at least one existing replica-* skill.')
    if destination.is_symlink() or (destination.exists() and not destination.is_dir()):
        raise ValueError('Destination must be a directory, not a symlink or file.')
    targets = [destination / name for name in names]
    if any(target.is_symlink() for target in targets):
        raise ValueError('Refusing to replace a symlinked skill.')
    conflicts = [target for target in targets if target.exists()]
    if conflicts and not replace:
        raise ValueError('Existing skills: %s. Use --replace to back them up first.' %
                         ', '.join(p.name for p in conflicts))
    license_path = source.parent / 'LICENSE'
    notice_path = source.parent / 'NOTICE.md'
    if not license_path.is_file():
        raise ValueError('Source pack must include its LICENSE.')
    for name in names:
        if (source / name).is_symlink():
            raise ValueError('Source skills must not contain symlinks.')
        for path in (source / name).rglob('*'):
            if path.is_symlink():
                raise ValueError('Source skills must not contain symlinks.')
    print('%s %d skills into %s' % ('Would install' if dry_run else 'Installing',
                                  len(names), destination))
    if dry_run:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    backup = None
    moved, installed = [], []
    with tempfile.TemporaryDirectory(prefix='.replicate-stage-', dir=str(destination.parent)) as tmp:
        staging = Path(tmp)
        # Copy everything successfully before moving any existing installation.
        for name in names:
            shutil.copytree(str(source / name), str(staging / name),
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            shutil.copy2(str(license_path), str(staging / name / 'LICENSE'))
            if notice_path.is_file():
                shutil.copy2(str(notice_path), str(staging / name / 'NOTICE.md'))
        destination.mkdir(exist_ok=True)
        try:
            for target in targets:
                if target.is_symlink():
                    raise ValueError('Skill became a symlink during installation: ' + target.name)
                if target.exists():
                    if not replace:
                        raise ValueError('Skill appeared during installation: ' + target.name)
                    if backup is None:
                        backup_root = destination.parent / '.replicate-skills-backups'
                        backup_root.mkdir(exist_ok=True)
                        backup = Path(tempfile.mkdtemp(
                            prefix=datetime.datetime.now().strftime('%Y%m%d-%H%M%S-'),
                            dir=str(backup_root)))
                    target.rename(backup / target.name)
                    moved.append(target)
                (staging / target.name).rename(target)
                installed.append(target)
        except (OSError, ValueError):
            for target in reversed(installed):
                shutil.rmtree(str(target))
            for target in reversed(moved):
                (backup / target.name).rename(target)
            raise
    if backup:
        print('Previous installation saved in %s' % backup)
    print('Start a new agent session and verify skill discovery.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', required=True, choices=['codex', 'claude', 'both'])
    parser.add_argument('--scope', choices=['project', 'user'], default='project')
    parser.add_argument('--project', type=Path, default=Path.cwd(), help='Project root for project scope')
    parser.add_argument('--destination', type=Path, help='Explicit skills directory for one runtime')
    parser.add_argument('--skill', action='append', choices=available(), help='Install selected skills only')
    parser.add_argument('--replace', action='store_true', help='Back up and replace existing selected skills')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.destination and args.runtime == 'both':
        parser.error('--destination requires a single runtime')
    root = Path.home() if args.scope == 'user' else args.project.expanduser().absolute()
    runtimes = ['codex', 'claude'] if args.runtime == 'both' else [args.runtime]
    destinations = [args.destination or root / ('.agents' if runtime == 'codex' else '.claude') / 'skills'
                    for runtime in runtimes]
    try:
        # Preflight every runtime before performing either installation.
        for destination in destinations:
            install(SOURCE, destination, args.skill or available(), args.replace, dry_run=True)
        if not args.dry_run:
            for destination in destinations:
                install(SOURCE, destination, args.skill or available(), args.replace)
    except (OSError, ValueError) as error:
        print('Installation failed: %s' % error, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
