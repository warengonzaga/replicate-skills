from datetime import date
import unittest
from support import module

feedback = module('entrepreneur', 'feedback_triage')
AS_OF = date(2026, 10, 7)


def research(text='Please RETRY the upload.'):
    return {'schema_version': 1, 'topics': [{'id': 'retry', 'terms': ['retry']}],
            'records': [{'id': 'person-1', 'date': '2026-10-01', 'text': text, 'source': 'interview-1'}]}


class Feedback(unittest.TestCase):
    def test_casefold_matches_and_preserves_evidence_ids(self):
        result = feedback.triage(research(), AS_OF)
        self.assertEqual(result['topics'][0]['record_ids'], ['person-1'])
        self.assertEqual(result['sample_size'], 1)
        self.assertEqual(result['as_of'], '2026-10-07')

    def test_unmatched_record_stays_visible(self):
        self.assertEqual(feedback.triage(research('Needs keyboard access.'), AS_OF)['unmatched'], ['person-1'])

    def test_multiple_topic_matches_are_ambiguous(self):
        value = research()
        value['topics'].append({'id': 'upload', 'terms': ['upload']})
        self.assertEqual(feedback.triage(value, AS_OF)['ambiguous'], ['person-1'])

    def test_duplicate_respondent_rejected(self):
        value = research()
        value['records'] *= 2
        with self.assertRaises(ValueError):
            feedback.triage(value, AS_OF)

    def test_future_and_invalid_dates_rejected(self):
        for captured in ('2026-10-08', '2026-02-30', 'today'):
            value = research()
            value['records'][0]['date'] = captured
            with self.subTest(date=captured), self.assertRaises(ValueError):
                feedback.triage(value, AS_OF)

    def test_date_range_records_actual_sample(self):
        value = research()
        value['records'].append({'id': 'person-2', 'date': '2026-10-07', 'text': 'retry', 'source': 'review-2'})
        self.assertEqual(feedback.triage(value, AS_OF)['date_range'], ['2026-10-01', '2026-10-07'])

    def test_invalid_topics(self):
        for topics in ([], [{'id': 'x', 'terms': []}], [{'id': 'x', 'terms': [False]}], [{'id': 'x', 'terms': ['a']}] * 2):
            value = research()
            value['topics'] = topics
            with self.subTest(topics=topics), self.assertRaises(ValueError):
                feedback.triage(value, AS_OF)

    def test_missing_source_is_rejected(self):
        value = research()
        del value['records'][0]['source']
        with self.assertRaises(ValueError):
            feedback.triage(value, AS_OF)

    def test_empty_sample_rejected(self):
        value = research()
        value['records'] = []
        with self.assertRaises(ValueError):
            feedback.triage(value, AS_OF)
