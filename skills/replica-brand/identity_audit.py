#!/usr/bin/env python3
"""Scan explicitly selected text surfaces for literal identity terms."""
import argparse
import fnmatch
import json
import os
from pathlib import Path
import sys

SKIP = {'.git', 'node_modules', '.venv', '__pycache__'}
AGENT_CONFIG = {'.agents', '.claude', '.codex'}


def string_array(value, field, allow_empty=False):
    if not isinstance(value, list) or (not value and not allow_empty) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(field + ' must be an array of nonempty strings.')
    return value


def selected(path, patterns):
    # Treat **/ as matching zero or more directories, including root files.
    return any(fnmatch.fnmatchcase(path, pattern) or
               (pattern.startswith('**/') and fnmatch.fnmatchcase(path, pattern[3:]))
               for pattern in patterns)


def audit(root, rules, include_agent_config=False):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('Root must be a real directory.')
    if not isinstance(rules, dict) or type(rules.get('schema_version')) is not int or rules['schema_version'] != 1:
        raise ValueError('Expected schema_version 1 object.')
    terms = string_array(rules.get('terms'), 'terms')
    include = string_array(rules.get('include'), 'include')
    exclude = string_array(rules.get('exclude'), 'exclude', allow_empty=True)
    hits, skipped, scanned = [], [], 0
    def traversal_error(error):
        raise error
    for directory, dirs, files in os.walk(str(root), followlinks=False, onerror=traversal_error):
        base = Path(directory)
        for name in sorted(dirs[:]):
            path = base / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink() or name in SKIP or (base == root and name in AGENT_CONFIG and not include_agent_config):
                dirs.remove(name)
                skipped.append({'path': relative, 'reason': 'excluded-directory-or-symlink'})
        dirs.sort()
        for name in sorted(files):
            path = base / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                skipped.append({'path': relative, 'reason': 'symlink'})
                continue
            if not selected(relative, include) or selected(relative, exclude):
                skipped.append({'path': relative, 'reason': 'outside-selected-surfaces'})
                continue
            raw = path.read_bytes()
            try:
                text = raw.decode('utf-8')
                if b'\x00' in raw:
                    raise UnicodeError('binary')
            except UnicodeError:
                skipped.append({'path': relative, 'reason': 'binary-or-non-utf8'})
                continue
            scanned += 1
            for line_number, line in enumerate(text.splitlines(), 1):
                folded = line.casefold()
                for term in terms:
                    if term.casefold() in folded:
                        # Do not echo source lines which may contain private text.
                        hits.append({'path': relative, 'line': line_number, 'term': term})
    return {'schema_version': 1, 'pass': scanned > 0 and not hits, 'scanned_files': scanned,
            'findings': hits, 'skipped': skipped,
            'limitation': 'Literal case-insensitive terms in selected UTF-8 files only; review legal notices and skipped assets manually.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--rules', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--include-agent-config', action='store_true')
    args = parser.parse_args(argv)
    try:
        report = audit(args.root, json.loads(args.rules.read_text(encoding='utf-8')), args.include_agent_config)
        text = json.dumps(report, indent=2) + '\n'
        if args.output:
            args.output.write_text(text, encoding='utf-8')
        else:
            print(text, end='')
        return 0 if report['pass'] else 1
    except (OSError, ValueError, TypeError) as error:
        print('Identity input/output error: %s' % error, file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
