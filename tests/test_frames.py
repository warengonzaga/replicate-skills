import contextlib
import io
import os
from pathlib import Path
import tempfile
import unittest
from support import module

frames = module('diff', 'frame_compare')


def frame(values=(0, 0, 0, 255, 255, 255)):
    return frames.Frame(2, 1, bytes(values))


class Frames(unittest.TestCase):
    def test_identical_is_pass(self):
        result, heat = frames.compare(frame(), frame())
        self.assertTrue(result['pass'])
        self.assertEqual(result['changed_pixels'], 0)
        self.assertEqual(heat.rgb, b'\x00' * 6)

    def test_change_reports_percent_bounds_and_heatmap(self):
        result, heat = frames.compare(frame(), frame((0, 0, 0, 200, 255, 255)))
        self.assertFalse(result['pass'])
        self.assertEqual(result['changed_percent'], 50)
        self.assertEqual(result['changed_bounds'], [1, 0, 1, 0])
        self.assertEqual(result['maximum_channel_delta'], 55)
        self.assertEqual(heat.rgb[3:], bytes((255, 55, 0)))

    def test_tolerance_boundary_is_inclusive(self):
        self.assertTrue(frames.compare(frame(), frame((0, 0, 0, 200, 255, 255)), tolerance=55)[0]['pass'])

    def test_percent_boundary_is_inclusive(self):
        self.assertTrue(frames.compare(frame(), frame((0, 0, 0, 200, 255, 255)), max_changed_percent=50)[0]['pass'])

    def test_masks_remove_pixels_from_denominator(self):
        result, _ = frames.compare(frame(), frame((0, 0, 0, 200, 255, 255)), [[0, 0, 1, 1]])
        self.assertEqual(result['changed_percent'], 100)
        self.assertEqual(result['compared_pixels'], 1)

    def test_overlapping_masks_not_double_counted(self):
        result, _ = frames.compare(frame(), frame(), [[0, 0, 1, 1]] * 2)
        self.assertEqual(result['masked_pixels'], 1)

    def test_all_masked_rejected(self):
        with self.assertRaises(ValueError):
            frames.compare(frame(), frame(), [[0, 0, 2, 1]])

    def test_invalid_masks(self):
        for masks in ({}, [[0, 0, 3, 1]], [[-1, 0, 1, 1]], [[0, 0, 0, 1]], [[False, 0, 1, 1]], [[0, 1]]):
            with self.subTest(masks=masks), self.assertRaises(ValueError):
                frames.compare(frame(), frame(), masks)

    def test_different_dimensions_rejected(self):
        with self.assertRaises(ValueError):
            frames.compare(frame(), frames.Frame(1, 2, frame().rgb))

    def test_invalid_thresholds(self):
        for value in (float('nan'), float('inf'), -1, 101, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                frames.compare(frame(), frame(), max_changed_percent=value)
        for value in (-1, 256, True, 2.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                frames.compare(frame(), frame(), tolerance=value)

    def test_p3_with_comments(self):
        result = frames.read_ppm(b'P3\n# fixture\n2 1\n255\n0 0 0 # one\n255 255 255\n')
        self.assertEqual(result, frame())

    def test_p6_first_pixel_whitespace_is_not_discarded(self):
        self.assertEqual(frames.read_ppm(b'P6\n1 1\n255\n\x0a\x20\x23').rgb, bytes((10, 32, 35)))

    def test_p6_cr_separator_preserves_lf_first_channel(self):
        rgb = bytes((10, 32, 35))
        self.assertEqual(frames.read_ppm(b'P6\n1 1\n255\r' + rgb).rgb, rgb)

    def test_p6_crlf_separator_preserves_lf_first_channel(self):
        rgb = bytes((10, 32, 35))
        self.assertEqual(frames.read_ppm(b'P6\r\n1 1\r\n255\r\n' + rgb).rgb, rgb)

    def test_p6_crlf_header(self):
        self.assertEqual(frames.read_ppm(b'P6\r\n1 1\r\n255\r\n\x00\x00\x00').width, 1)

    def test_malformed_ppm(self):
        for raw in (b'', b'P5\n1 1\n255\n123', b'P6\n1 1\n65535\n123', b'P6\n1 1\n255\n12', b'P3\n1 1\n255\n0 0 0 4', b'P3\n1 1\n255\n-1 0 0'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                frames.read_ppm(raw)

    def test_frame_shape_validation(self):
        for args in ((0, 1, b''), (1, 1, b'12'), (True, 1, b'123'), (16000001, 1, b'')):
            with self.subTest(args=args), self.assertRaises(ValueError):
                frames.Frame(*args)

    def test_ppm_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'frame.ppm'
            frames.save_ppm(frame(), path)
            self.assertEqual(frames.load_frame(path), frame())

    def test_cli_refuses_to_overwrite_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'frame.ppm'
            frames.save_ppm(frame(), path)
            original = path.read_bytes()
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(frames.main([str(path), str(path), '--heatmap', str(path)]), 2)
            self.assertEqual(path.read_bytes(), original)

    def test_cli_refuses_hardlinked_heatmap_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            left, right, heat = (Path(tmp) / name for name in ('left.ppm', 'right.ppm', 'heat.ppm'))
            left.write_bytes(b'P6\n1 1\n255\n\x00\x00\x00')
            right.write_bytes(b'P6\n1 1\n255\n\xff\x00\x00')
            try:
                os.link(left, heat)
            except (AttributeError, OSError) as error:
                self.skipTest('Hard links are unavailable: %s' % error)
            original = left.read_bytes()
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(frames.main([str(left), str(right), '--heatmap', str(heat)]), 2)
            self.assertEqual(left.read_bytes(), original)

    def test_cli_refuses_hardlinked_output_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            left, right, report, heat = (Path(tmp) / name for name in ('left.ppm', 'right.ppm', 'report.json', 'heat.ppm'))
            left.write_bytes(b'P6\n1 1\n255\n\x00\x00\x00')
            right.write_bytes(b'P6\n1 1\n255\n\xff\x00\x00')
            report.write_text('preserve')
            try:
                os.link(report, heat)
            except (AttributeError, OSError) as error:
                self.skipTest('Hard links are unavailable: %s' % error)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(frames.main([str(left), str(right), '--output', str(report), '--heatmap', str(heat)]), 2)
            self.assertEqual(report.read_text(), 'preserve')
            self.assertEqual(heat.read_text(), 'preserve')

    def test_optional_pillow_rgb_png(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest('Optional Pillow is not installed.')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'frame.png'
            Image.new('RGB', (1, 1), (24, 48, 96)).save(str(path))
            self.assertEqual(frames.load_frame(path).rgb, bytes((24, 48, 96)))

    def test_optional_pillow_rejects_transparency(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest('Optional Pillow is not installed.')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'alpha.png'
            Image.new('RGBA', (1, 1), (0, 0, 0, 100)).save(str(path))
            with self.assertRaises(ValueError):
                frames.load_frame(path)

    def test_optional_pillow_decoder_limit_is_reported_as_input_error(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest('Optional Pillow is not installed.')
        from unittest.mock import patch
        with patch.object(Image, 'open', side_effect=Image.DecompressionBombError('too large')):
            with self.assertRaises(ValueError):
                frames.load_frame('large.png')
