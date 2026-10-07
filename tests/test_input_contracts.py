"""Regression cases for the revised helpers' external input and failure contracts."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from _load import load

parity = load('replica-diff', 'parity')
contrast = load('replica-design', 'contrast')
listing = load('replica-launch', 'listing')
reviews = load('replica-entrepreneur', 'reviews')
imgdiff = load('replica-diff', 'imgdiff')
sweep = load('replica-brand', 'sweep')


class InputContracts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def json_file(self, name, data):
        path = self.root / name
        path.write_text(json.dumps(data), encoding='utf-8')
        return str(path)

    def assert_input_error(self, main, args, message=None):
        errors = io.StringIO()
        with redirect_stdout(io.StringIO()), redirect_stderr(errors):
            self.assertEqual(main(args), 2)
        if message:
            self.assertIn(message, errors.getvalue())

    def test_visual_scores_reject_unbounded_or_nonfinite_numbers(self):
        for value in [-1, 101, float('nan'), float('inf'), True, None]:
            with self.subTest(value=value):
                path = self.json_file('visual.json', {'score': value})
                with self.assertRaises(parity.MatrixError):
                    parity.visual_scores([path])

    def test_visual_scores_reject_malformed_report_shapes(self):
        for data in [[], {'score': 80, 'files': []}]:
            path = self.json_file('visual.json', data)
            with self.assertRaises(parity.MatrixError):
                parity.visual_scores([path])

    def test_combine_does_not_mutate_a_feature_report(self):
        source = {'feature_score': 60}
        visual = [{'score': 100}]
        result = parity.combine(source, visual)
        self.assertEqual(source, {'feature_score': 60})
        self.assertEqual(result['overall'], 68)
        visual.clear()
        self.assertEqual(len(result['visual']), 1)

    def test_csv_overflow_and_duplicate_headers_are_explicit_errors(self):
        cases = [
            (parity.load, parity.MatrixError, 'feature,priority,clone\nbooking,must,yes,unexpected\n'),
            (parity.load, parity.MatrixError, 'feature,priority,clone,CLONE\nbooking,must,yes,no\n'),
            (reviews.load_reviews, reviews.FeedbackError, 'url,text\nhttps://example.com,quote,unexpected\n'),
            (reviews.load_reviews, reviews.FeedbackError, 'url,text,TEXT\nhttps://example.com,quote,quote\n'),
        ]
        for reader, error, csv in cases:
            path = self.root / 'input.csv'
            path.write_text(csv)
            with self.assertRaises(error):
                reader(str(path))

    def test_malformed_contrast_pairs_cannot_report_a_pass(self):
        for pairs in [[[]], ['text'], [['text', 'bg', 'typo']], [[1, 'bg']], 'text,bg']:
            path = self.json_file('tokens.json', {'color': {'text': '#111', 'bg': '#fff'},
                                                  'pairs': pairs})
            self.assert_input_error(contrast.main, [path])

    def test_explicit_empty_pairs_are_not_replaced_by_inference(self):
        path = self.json_file('tokens.json', {'color': {'text': '#111', 'bg': '#fff'}, 'pairs': []})
        self.assert_input_error(contrast.main, [path], 'no pairs')

    def test_nonobject_tokens_are_reported_without_a_traceback(self):
        path = self.json_file('tokens.json', [])
        self.assert_input_error(contrast.main, [path], 'JSON object')

    def test_listing_input_schema_rejects_nontext_metadata(self):
        for data in [[], {'app_store': []}, {'google_play': {'title': 123}},
                     {'avoid': 'Original App'}, {'avoid': [None]}]:
            path = self.json_file('listing.json', data)
            self.assert_input_error(listing.main, [path])

    def test_review_theme_configuration_rejects_duplicate_ids(self):
        path = self.json_file('themes.json', {'themes': [{'id': 'price'}, {'id': 'price'}]})
        with self.assertRaisesRegex(reviews.FeedbackError, 'duplicate theme'):
            reviews.load_themes(path)

    def test_review_theme_configuration_rejects_wrong_types(self):
        for data in [[], {'themes': ['price']}, {'themes': [{'id': 'price', 'patterns': 'price'}]},
                     {'request_patterns': [123]}, {'themes': [{'id': 'price', 'label': 1}]},
                     {'themes': [{'id': 'price', 'kind': 'typo'}]}]:
            path = self.json_file('themes.json', data)
            with self.assertRaises(reviews.FeedbackError):
                reviews.load_themes(path)

    def test_reproducible_review_date_is_not_silently_replaced(self):
        path = self.root / 'reviews.csv'
        path.write_text('url,text\nhttps://example.com/review,Too expensive\n')
        self.assert_input_error(reviews.main, [str(path), '--today', '2026-99-99'])
        self.assert_input_error(reviews.main, [str(path), '--months', '0'], 'positive')

    def test_review_output_failure_returns_input_error(self):
        path = self.root / 'reviews.csv'
        path.write_text('url,text\nhttps://example.com/review,Too expensive\n')
        self.assert_input_error(reviews.main, [str(path), '--out', str(self.root / 'missing/report.md')])

    def image(self):
        path = str(self.root / 'screen.png')
        imgdiff.write_png(path, 2, 2, [[(0, 0, 0)] * 2 for _ in range(2)])
        return path

    def test_image_diff_reports_output_write_failures(self):
        path = self.image()
        self.assert_input_error(imgdiff.main, [path, path, '--out', str(self.root / 'missing/diff.png')])

    def test_image_diff_validates_comparison_options(self):
        path = self.image()
        for option, value in [('--width', '0'), ('--cols', '-1'), ('--tolerance', '256')]:
            self.assert_input_error(imgdiff.main, [path, path, option, value])

    def test_invalid_release_thresholds_are_not_accepted(self):
        for value in ['nan', 'inf', '-1', '101']:
            self.assert_input_error(parity.main, ['missing.csv', '--fail-under', value], 'threshold')
            self.assert_input_error(imgdiff.main, ['a.png', 'b.png', '--fail-under', value], 'threshold')

    def test_missing_brand_scan_root_cannot_pass(self):
        self.assert_input_error(sweep.main, [str(self.root / 'missing'), '--avoid', 'Original'],
                                'not a directory')

    def test_brand_configuration_validates_lists_and_colours(self):
        for config in [[], {'avoid': 'Original'}, {'avoid': [1]}, {'colors': ['invalid']}]:
            path = self.json_file('brand.json', config)
            self.assert_input_error(sweep.main, [str(self.root), '--config', path])


if __name__ == '__main__':
    unittest.main()
