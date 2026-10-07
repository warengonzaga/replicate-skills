import os
from pathlib import Path
import tempfile
import unittest
from support import module

identity = module('brand', 'identity_audit')
RULES = {'schema_version': 1, 'terms': ['FormerBrand'], 'include': ['**/*.txt'], 'exclude': []}


class Identity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='identity files ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def test_root_glob_and_casefold(self):
        self.write('title.txt', 'formerbrand')
        result = identity.audit(self.root, RULES)
        self.assertEqual(result['findings'], [{'path': 'title.txt', 'line': 1, 'term': 'FormerBrand'}])

    def test_reports_line_without_echoing_private_content(self):
        self.write('text.txt', 'ok\nFormerBrand secret-account-token')
        result = identity.audit(self.root, RULES)
        self.assertEqual(result['findings'][0]['line'], 2)
        self.assertNotIn('secret-account-token', str(result))

    def test_clean_selected_file_passes(self):
        self.write('safe.txt', 'New identity')
        self.assertTrue(identity.audit(self.root, RULES)['pass'])

    def test_zero_scanned_files_is_not_a_pass(self):
        self.assertFalse(identity.audit(self.root, RULES)['pass'])

    def test_agent_configs_skipped_unless_included(self):
        self.write('safe.txt', 'safe')
        self.write('.agents/skills/old.txt', 'FormerBrand')
        self.assertTrue(identity.audit(self.root, RULES)['pass'])
        self.assertFalse(identity.audit(self.root, RULES, True)['pass'])

    def test_nested_public_claude_directory_is_scanned(self):
        self.write('public/.claude/title.txt', 'FormerBrand')
        self.assertFalse(identity.audit(self.root, RULES)['pass'])

    def test_dependencies_and_git_are_skipped(self):
        self.write('safe.txt', 'safe')
        self.write('node_modules/pkg/title.txt', 'FormerBrand')
        self.write('.git/title.txt', 'FormerBrand')
        self.assertTrue(identity.audit(self.root, RULES)['pass'])

    def test_explicit_exclusion_preserves_notices(self):
        self.write('LICENSE.txt', 'FormerBrand')
        self.write('safe.txt', 'safe')
        rules = dict(RULES, exclude=['LICENSE.txt'])
        self.assertTrue(identity.audit(self.root, rules)['pass'])

    def test_binary_file_is_reported_skipped(self):
        (self.root / 'binary.txt').write_bytes(b'FormerBrand\x00')
        result = identity.audit(self.root, RULES)
        self.assertEqual(result['skipped'][0]['reason'], 'binary-or-non-utf8')

    def test_symlink_is_not_followed(self):
        self.write('safe.txt', 'safe')
        (self.root / 'linked.txt').symlink_to(self.root / 'safe.txt')
        result = identity.audit(self.root, RULES)
        self.assertEqual(result['scanned_files'], 1)
        self.assertTrue(any(row['reason'] == 'symlink' for row in result['skipped']))

    def test_non_regular_file_is_reported_without_reading(self):
        if not hasattr(os, 'mkfifo'):
            self.skipTest('Named pipes are unavailable on this platform.')
        self.write('safe.txt', 'safe')
        os.mkfifo(self.root / 'pipe.txt')
        result = identity.audit(self.root, RULES)
        self.assertEqual(result['scanned_files'], 1)
        self.assertIn({'path': 'pipe.txt', 'reason': 'non-regular-file'}, result['skipped'])

    def test_missing_root_rejected(self):
        with self.assertRaises(ValueError):
            identity.audit(self.root / 'missing', RULES)

    def test_malformed_rules_rejected(self):
        for field, value in [('terms', []), ('terms', [1]), ('include', []), ('exclude', 'glob')]:
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                identity.audit(self.root, dict(RULES, **{field: value}))
