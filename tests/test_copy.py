import unittest
from support import module

copy_tool = module('launch', 'copy_check')


def content(text='Ready', maximum=20, mode='codepoints', required=True):
    return {'schema_version': 1, 'fields': [{'id': 'title', 'text': text, 'max_length': maximum,
                                           'count': mode, 'required': required, 'source': 'internal specification'}]}


class Copy(unittest.TestCase):
    def test_within_limit(self):
        self.assertTrue(copy_tool.check(content())['pass'])

    def test_equal_limit_passes(self):
        self.assertTrue(copy_tool.check(content('Hello', 5))['pass'])

    def test_over_limit(self):
        result = copy_tool.check(content('Hello', 4))
        self.assertEqual(result['fields'][0]['issues'], ['over-limit'])
        self.assertFalse(result['pass'])

    def test_required_whitespace_fails(self):
        self.assertEqual(copy_tool.check(content('  '))['fields'][0]['issues'], ['required-empty'])

    def test_optional_empty_passes(self):
        self.assertTrue(copy_tool.check(content('', required=False))['pass'])

    def test_unicode_counting_modes(self):
        for mode, expected in [('codepoints', 1), ('utf16', 2), ('utf8', 4)]:
            with self.subTest(mode=mode):
                self.assertEqual(copy_tool.measure('\U0001f680', mode), expected)

    def test_invalid_fields(self):
        for field, bad in [('id', ''), ('text', 5), ('required', 1), ('max_length', True), ('max_length', 0), ('count', 'graphemes'), ('source', '')]:
            value = content()
            value['fields'][0][field] = bad
            with self.subTest(field=field, value=bad), self.assertRaises(ValueError):
                copy_tool.check(value)

    def test_duplicate_and_empty_fields(self):
        for fields in ([], content()['fields'] * 2):
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                copy_tool.check({'schema_version': 1, 'fields': fields})
