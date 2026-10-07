import unittest
from support import module

palette = module('design', 'palette_audit')


def document(fg='#000000', bg='#FFFFFF', role='text'):
    return {'schema_version': 1, 'pairs': [{'id': 'content', 'foreground': fg, 'background': bg, 'role': role}]}


class Palette(unittest.TestCase):
    def test_black_white_ratio_is_21(self):
        self.assertEqual(palette.audit(document())['pairs'][0]['ratio'], 21)

    def test_order_does_not_change_ratio(self):
        self.assertEqual(palette.audit(document('#FFFFFF', '#000000'))['pairs'][0]['ratio'], 21)

    def test_same_color_fails(self):
        self.assertFalse(palette.audit(document('#123456', '#123456'))['pass'])

    def test_large_text_and_ui_use_three(self):
        for role in ('large-text', 'ui'):
            with self.subTest(role=role):
                self.assertEqual(palette.audit(document(role=role))['pairs'][0]['minimum'], 3)

    def test_normal_text_uses_four_point_five(self):
        self.assertEqual(palette.audit(document())['pairs'][0]['minimum'], 4.5)

    def test_malformed_color(self):
        for color in (None, '#fff', '#abcdef00', 'red', '#GG0000'):
            with self.subTest(color=color), self.assertRaises(ValueError):
                palette.luminance(color)

    def test_bad_role(self):
        with self.assertRaises(ValueError):
            palette.audit(document(role='caption'))

    def test_empty_and_duplicate_pairs(self):
        for pairs in ([], [document()['pairs'][0]] * 2):
            with self.subTest(pairs=pairs), self.assertRaises(ValueError):
                palette.audit({'schema_version': 1, 'pairs': pairs})

    def test_unknown_schema(self):
        value = document()
        value['schema_version'] = 2
        with self.assertRaises(ValueError):
            palette.audit(value)
