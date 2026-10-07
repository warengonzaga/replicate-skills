#!/usr/bin/env python3
"""Evaluate an evidence ledger without averaging away required failures."""
import argparse
import json
from pathlib import Path
import sys

STATES = ('pass', 'fail', 'blocked', 'unknown')


def evaluate(document):
    if not isinstance(document, dict) or type(document.get('schema_version')) is not int or document['schema_version'] != 1:
        raise ValueError('Expected schema_version 1 object.')
    criteria = document.get('criteria')
    if not isinstance(criteria, list) or not criteria:
        raise ValueError('criteria must be a nonempty array.')
    ids, results = set(), []
    for item in criteria:
        if not isinstance(item, dict):
            raise ValueError('Every criterion must be an object.')
        key = item.get('id')
        if not isinstance(key, str) or not key.strip() or key in ids:
            raise ValueError('Criterion IDs must be nonempty and unique.')
        ids.add(key)
        required, state, evidence = item.get('required'), item.get('state'), item.get('evidence')
        if type(required) is not bool or state not in STATES or not isinstance(evidence, list):
            raise ValueError('Criterion %s needs boolean required, a valid state, and evidence array.' % key)
        for entry in evidence:
            if not isinstance(entry, dict) or entry.get('kind') not in ('observation', 'test') or not isinstance(entry.get('ref'), str) or not entry['ref'].strip():
                raise ValueError('Evidence needs kind observation/test and a nonempty ref.')
        verified = state == 'pass' and bool(evidence)
        results.append({'id': key, 'required': required, 'state': state,
                        'verified': verified, 'reason': 'pass without evidence' if state == 'pass' and not evidence else state})
    blockers = [row['id'] for row in results if row['required'] and not row['verified']]
    required_count = sum(row['required'] for row in results)
    # A ledger without required criteria cannot establish release readiness.
    ready = required_count > 0 and not blockers
    return {'schema_version': 1, 'ready': ready, 'required_count': required_count,
            'blockers': blockers, 'counts': {state: sum(row['state'] == state for row in results) for state in STATES},
            'criteria': results, 'limitation': 'Evidence references are declarations; this tool does not execute checks or inspect their contents.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ledger', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    try:
        report = evaluate(json.loads(args.ledger.read_text(encoding='utf-8')))
        text = json.dumps(report, indent=2) + '\n'
        if args.output:
            args.output.write_text(text, encoding='utf-8')
        else:
            print(text, end='')
        return 0 if report['ready'] else 1
    except (OSError, ValueError, TypeError) as error:
        print('Acceptance input/output error: %s' % error, file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
