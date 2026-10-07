#!/usr/bin/env python3
"""Compare aligned RGB frames with declared masks and an inspectable PPM heatmap."""
import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path
import re
import sys

MAX_PIXELS = 16000000


@dataclass(frozen=True)
class Frame:
    width: int
    height: int
    rgb: bytes

    def __post_init__(self):
        if type(self.width) is not int or type(self.height) is not int or self.width < 1 or self.height < 1 or self.width * self.height > MAX_PIXELS:
            raise ValueError('Frame dimensions must be positive and at most 16 million pixels.')
        if not isinstance(self.rgb, bytes) or len(self.rgb) != self.width * self.height * 3:
            raise ValueError('RGB bytes must match dimensions.')


def read_ppm(raw):
    cursor = 0
    def token():
        nonlocal cursor
        while cursor < len(raw):
            if raw[cursor] in b' \r\n\t\v\f':
                cursor += 1
            elif raw[cursor] == 35:
                newline = raw.find(b'\n', cursor)
                if newline < 0:
                    cursor = len(raw)
                else:
                    cursor = newline + 1
            else:
                break
        start = cursor
        while cursor < len(raw) and raw[cursor] not in b' \r\n\t\v\f#':
            cursor += 1
        if cursor == start:
            raise ValueError('Truncated PPM header or pixels.')
        return raw[start:cursor]
    magic = token()
    if magic not in (b'P3', b'P6'):
        raise ValueError('PPM must be P3 or P6.')
    width, height, maximum = int(token()), int(token()), int(token())
    if width < 1 or height < 1 or width * height > MAX_PIXELS or maximum != 255:
        raise ValueError('PPM needs positive dimensions up to 16 million pixels and maxval 255.')
    count = width * height * 3
    if magic == b'P6':
        if cursor >= len(raw) or raw[cursor] not in b' \r\n\t\v\f':
            raise ValueError('Missing PPM raster separator.')
        if raw[cursor:cursor + 2] == b'\r\n':
            cursor += 2
        else:
            cursor += 1
        rgb = raw[cursor:]
    else:
        values = [int(token()) for _ in range(count)]
        if any(value < 0 or value > 255 for value in values):
            raise ValueError('PPM channels must be between 0 and 255.')
        # Remaining comments/whitespace are allowed, extra samples are not.
        remainder = re.sub(rb'#[^\n]*', b'', raw[cursor:]).strip()
        if remainder:
            raise ValueError('PPM contains extra samples.')
        rgb = bytes(values)
    return Frame(width, height, rgb)


def load_frame(path):
    path = Path(path)
    if path.suffix.lower() in ('.ppm', '.pnm'):
        return read_ppm(path.read_bytes())
    try:
        from PIL import Image
    except ImportError as error:
        raise ValueError('PNG/JPEG support requires optional Pillow; PPM needs no dependencies.') from error
    try:
        with Image.open(str(path)) as image:
            if image.width * image.height > MAX_PIXELS:
                raise ValueError('Frame exceeds 16 million pixels.')
            rgba = image.convert('RGBA')
            if rgba.getchannel('A').getextrema() != (255, 255):
                raise ValueError('Flatten transparent screenshots to an explicit background before comparing.')
            return Frame(image.width, image.height, image.convert('RGB').tobytes())
    except Image.DecompressionBombError as error:
        raise ValueError('Image exceeds the decoder safety limit.') from error


def compare(reference, candidate, masks=None, tolerance=0, max_changed_percent=0.0):
    if (reference.width, reference.height) != (candidate.width, candidate.height):
        raise ValueError('Frames must have identical dimensions; capture again rather than resizing.')
    if type(tolerance) is not int or not 0 <= tolerance <= 255:
        raise ValueError('tolerance must be an integer from 0 to 255.')
    if isinstance(max_changed_percent, bool) or not isinstance(max_changed_percent, (int, float)) or not math.isfinite(max_changed_percent) or not 0 <= max_changed_percent <= 100:
        raise ValueError('max_changed_percent must be finite and between 0 and 100.')
    if masks is None:
        masks = []
    if not isinstance(masks, list):
        raise ValueError('Masks must be an array of [x, y, width, height] rectangles.')
    width, height = reference.width, reference.height
    excluded = bytearray(width * height)
    for rect in masks:
        if not isinstance(rect, list) or len(rect) != 4 or any(type(value) is not int for value in rect):
            raise ValueError('Mask rectangles need four integers.')
        x, y, w, h = rect
        if x < 0 or y < 0 or w < 1 or h < 1 or x + w > width or y + h > height:
            raise ValueError('Masks must fit entirely inside the frame.')
        for row in range(y, y + h):
            excluded[row * width + x:row * width + x + w] = b'\x01' * w
    compared = len(excluded) - sum(excluded)
    if not compared:
        raise ValueError('Masks exclude every pixel; no visual evidence remains.')
    heat = bytearray(width * height * 3)
    changed, total_delta, maximum_delta = 0, 0, 0
    bounds = [width, height, -1, -1]
    for pixel, masked in enumerate(excluded):
        if masked:
            continue
        offset = pixel * 3
        deltas = [abs(reference.rgb[offset + channel] - candidate.rgb[offset + channel]) for channel in range(3)]
        peak = max(deltas)
        total_delta += sum(deltas)
        maximum_delta = max(maximum_delta, peak)
        if peak > tolerance:
            changed += 1
            x, y = pixel % width, pixel // width
            bounds = [min(bounds[0], x), min(bounds[1], y), max(bounds[2], x), max(bounds[3], y)]
            heat[offset:offset + 3] = bytes((255, peak, 0))
    percent = 100 * changed / compared
    report = {'schema_version': 1, 'pass': percent <= max_changed_percent,
              'width': width, 'height': height, 'compared_pixels': compared,
              'masked_pixels': sum(excluded), 'changed_pixels': changed,
              'changed_percent': round(percent, 6), 'mean_channel_delta': round(total_delta / (compared * 3), 6),
              'maximum_channel_delta': maximum_delta,
              'changed_bounds': bounds if changed else None,
              'tolerance': tolerance, 'max_changed_percent': max_changed_percent,
              'masks': [list(rect) for rect in masks],
              'limitation': 'Aligned pixel diagnostics only; no behavioral or perceptual quality claim.'}
    return report, Frame(width, height, bytes(heat))


def save_ppm(frame, path):
    Path(path).write_bytes(('P6\n%d %d\n255\n' % (frame.width, frame.height)).encode('ascii') + frame.rgb)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reference', type=Path)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('--mask', type=Path)
    parser.add_argument('--tolerance', type=int, default=0)
    parser.add_argument('--max-changed-percent', type=float, default=0.0)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--heatmap', type=Path)
    args = parser.parse_args(argv)
    try:
        inputs = {path.resolve() for path in (args.reference, args.candidate, args.mask) if path}
        outputs = [path.resolve() for path in (args.output, args.heatmap) if path]
        if inputs.intersection(outputs) or len(outputs) != len(set(outputs)):
            raise ValueError('Outputs must be distinct and must not overwrite inputs.')
        masks = json.loads(args.mask.read_text(encoding='utf-8')) if args.mask else []
        report, heat = compare(load_frame(args.reference), load_frame(args.candidate), masks,
                               args.tolerance, args.max_changed_percent)
        if args.heatmap:
            save_ppm(heat, args.heatmap)
        text = json.dumps(report, indent=2) + '\n'
        if args.output:
            args.output.write_text(text, encoding='utf-8')
        else:
            print(text, end='')
        return 0 if report['pass'] else 1
    except (OSError, ValueError, TypeError) as error:
        print('Frame input/output error: %s' % error, file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
