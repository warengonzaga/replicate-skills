#!/usr/bin/env python3
"""Audit explicit opaque sRGB pairs against WCAG 2 contrast thresholds."""
import argparse
import json
from pathlib import Path
import re
import sys

LIMITS = {'text': 4.5, 'large-text': 3.0, 'ui': 3.0}


def luminance(color):
    if not isinstance(color, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', color):
        raise ValueError('Colors must be six-digit opaque hex strings.')
    rgb = [int(color[offset:offset + 2], 16) / 255 for offset in (1, 3, 5)]
    linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in rgb]
    return sum(channel * weight for channel, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def audit(document):
    if not isinstance(document, dict) or type(document.get('schema_version')) is not int or document['schema_version'] != 1:
        raise ValueError('Expected schema_version 1 object.')
    pairs = document.get('pairs')
    if not isinstance(pairs, list) or not pairs:
        raise ValueError('pairs must be a nonempty array.')
    ids, rows = set(), []
    for pair in pairs:
        if not isinstance(pair, dict):
            raise ValueError('Pairs must be objects.')
        key, role = pair.get('id'), pair.get('role')
        if not isinstance(key, str) or not key.strip() or key in ids:
            raise ValueError('Pair IDs must be nonempty and unique.')
        if not isinstance(role, str) or role not in LIMITS:
            raise ValueError('Role must be text, large-text, or ui.')
        ids.add(key)
        first, second = luminance(pair.get('foreground')), luminance(pair.get('background'))
        ratio = (max(first, second) + 0.05) / (min(first, second) + 0.05)
        rows.append({'id': key, 'ratio': round(ratio, 6), 'minimum': LIMITS[role], 'pass': ratio >= LIMITS[role]})
    return {'schema_version': 1, 'pass': all(row['pass'] for row in rows), 'pairs': rows,
            'limitation': 'Declared opaque colors only; typography eligibility and full accessibility require review.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('palette', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    try:
        report = audit(json.loads(args.palette.read_text(encoding='utf-8')))
        text = json.dumps(report, indent=2) + '\n'
        if args.output:
            args.output.write_text(text, encoding='utf-8')
        else:
            print(text, end='')
        return 0 if report['pass'] else 1
    except (OSError, ValueError, TypeError) as error:
        print('Palette input/output error: %s' % error, file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
