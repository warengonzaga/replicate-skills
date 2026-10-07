#!/usr/bin/env python3
"""Check launch copy using supplied channel constraints and counting rules."""
import argparse
import json
from pathlib import Path
import sys


def measure(text, mode):
    if mode == 'codepoints':
        return len(text)
    if mode == 'utf16':
        return len(text.encode('utf-16-le')) // 2
    if mode == 'utf8':
        return len(text.encode('utf-8'))
    raise ValueError('count must be codepoints, utf16, or utf8.')


def check(document):
    if not isinstance(document, dict) or type(document.get('schema_version')) is not int or document['schema_version'] != 1:
        raise ValueError('Expected schema_version 1 object.')
    fields = document.get('fields')
    if not isinstance(fields, list) or not fields:
        raise ValueError('fields must be a nonempty array.')
    ids, rows = set(), []
    for field in fields:
        if not isinstance(field, dict):
            raise ValueError('Fields must be objects.')
        key, text, required = field.get('id'), field.get('text'), field.get('required')
        maximum, mode, source = field.get('max_length'), field.get('count'), field.get('source')
        if not isinstance(key, str) or not key.strip() or key in ids:
            raise ValueError('Field IDs must be nonempty and unique.')
        ids.add(key)
        if not isinstance(text, str) or type(required) is not bool or type(maximum) is not int or maximum < 1:
            raise ValueError('Fields require text, boolean required, and positive integer max_length.')
        if not isinstance(source, str) or not source.strip():
            raise ValueError('Each constraint needs a source.')
        length = measure(text, mode)
        issues = []
        if required and not text.strip():
            issues.append('required-empty')
        if length > maximum:
            issues.append('over-limit')
        rows.append({'id': key, 'length': length, 'max_length': maximum, 'count': mode, 'issues': issues})
    return {'schema_version': 1, 'pass': all(not row['issues'] for row in rows), 'fields': rows,
            'limitation': 'Checks declared constraints; does not verify factual claims, current channel rules, or store approval.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('content', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    try:
        report = check(json.loads(args.content.read_text(encoding='utf-8')))
        text = json.dumps(report, indent=2) + '\n'
        if args.output:
            args.output.write_text(text, encoding='utf-8')
        else:
            print(text, end='')
        return 0 if report['pass'] else 1
    except (OSError, ValueError, TypeError) as error:
        print('Copy input/output error: %s' % error, file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
