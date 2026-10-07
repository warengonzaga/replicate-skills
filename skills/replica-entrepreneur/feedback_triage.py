#!/usr/bin/env python3
"""Group dated feedback by explicit literal terms, preserving respondent IDs."""
import argparse
from datetime import date
import json
from pathlib import Path
import sys


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + ' must be nonempty text.')
    return value


def triage(document, as_of):
    if not isinstance(as_of, date):
        raise ValueError('as_of must be a date.')
    if not isinstance(document, dict) or type(document.get('schema_version')) is not int or document['schema_version'] != 1:
        raise ValueError('Expected schema_version 1 object.')
    topics, records = document.get('topics'), document.get('records')
    if not isinstance(topics, list) or not topics or not isinstance(records, list) or not records:
        raise ValueError('topics and records must be nonempty arrays.')
    terms, groups, seen, unmatched, ambiguous = {}, {}, set(), [], []
    for topic in topics:
        if not isinstance(topic, dict):
            raise ValueError('Topics must be objects.')
        key = nonempty(topic.get('id'), 'Topic ID')
        values = topic.get('terms')
        if key in terms or not isinstance(values, list) or not values:
            raise ValueError('Topic IDs must be unique and terms nonempty arrays.')
        terms[key] = [nonempty(term, 'Term').casefold() for term in values]
        groups[key] = []
    dates = []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError('Records must be objects.')
        key = nonempty(record.get('id'), 'Respondent ID')
        if key in seen:
            raise ValueError('Duplicate respondent ID: ' + key)
        seen.add(key)
        captured = date.fromisoformat(nonempty(record.get('date'), 'Record date'))
        if captured > as_of:
            raise ValueError('Record is after the analysis date: ' + key)
        dates.append(captured)
        text = nonempty(record.get('text'), 'Feedback text').casefold()
        nonempty(record.get('source'), 'Source')
        matches = [topic for topic, words in terms.items() if any(word in text for word in words)]
        for topic in matches:
            groups[topic].append(key)
        if not matches:
            unmatched.append(key)
        if len(matches) > 1:
            ambiguous.append(key)
    return {'schema_version': 1, 'as_of': as_of.isoformat(), 'sample_size': len(records),
            'date_range': [min(dates).isoformat(), max(dates).isoformat()],
            'topics': [{'id': key, 'count': len(ids), 'record_ids': ids} for key, ids in groups.items()],
            'unmatched': unmatched, 'ambiguous': ambiguous,
            'limitation': 'Literal substring triage; manual review is required for negation, sentiment, duplicates with different IDs, and representativeness.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('research', type=Path)
    parser.add_argument('--as-of', required=True, type=date.fromisoformat)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    try:
        report = triage(json.loads(args.research.read_text(encoding='utf-8')), args.as_of)
        text = json.dumps(report, indent=2) + '\n'
        if args.output:
            args.output.write_text(text, encoding='utf-8')
        else:
            print(text, end='')
        return 0
    except (OSError, ValueError, TypeError) as error:
        print('Feedback input/output error: %s' % error, file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
