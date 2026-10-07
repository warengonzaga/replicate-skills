import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from support import ROOT

COMMANDS = [
    ('design', 'palette_audit.py', 'palette.example.json', 0, []),
    ('diff', 'acceptance_gate.py', '../replica-recon/scope.example.json', 1, []),
    ('entrepreneur', 'feedback_triage.py', 'research.example.json', 0, ['--as-of', '2026-10-07']),
    ('launch', 'copy_check.py', 'content.example.json', 0, []),
]


class Commands(unittest.TestCase):
    def run_script(self, skill, name, args):
        return subprocess.run([sys.executable, str(ROOT / 'skills' / ('replica-' + skill) / name)] + list(map(str, args)), capture_output=True, text=True)

    def test_documented_examples_and_json_outputs(self):
        with tempfile.TemporaryDirectory(prefix='tool outputs ') as tmp:
            for skill, name, example, status, extra in COMMANDS:
                source = ROOT / 'skills' / ('replica-' + skill) / example
                output = Path(tmp) / (name + '.json')
                result = self.run_script(skill, name, [source, '--output', output] + extra)
                with self.subTest(tool=name):
                    self.assertEqual(result.returncode, status, result.stderr)
                    self.assertEqual(json.loads(output.read_text())['schema_version'], 1)

    def test_invalid_json_is_reported_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'bad.json'
            path.write_text('{')
            for skill, name, _, _, extra in COMMANDS:
                result = self.run_script(skill, name, [path] + extra)
                with self.subTest(tool=name):
                    self.assertEqual(result.returncode, 2)
                    self.assertNotIn('Traceback', result.stderr)

    def test_output_write_failures_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            for skill, name, example, _, extra in COMMANDS:
                source = ROOT / 'skills' / ('replica-' + skill) / example
                result = self.run_script(skill, name, [source, '--output', Path(tmp) / 'missing/out.json'] + extra)
                with self.subTest(tool=name):
                    self.assertEqual(result.returncode, 2)
                    self.assertNotIn('Traceback', result.stderr)

    def test_identity_cli_pass_and_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rules = root / 'rules.json'
            rules.write_text(json.dumps({'schema_version': 1, 'terms': ['PreviousBrand'], 'include': ['**/*.txt'], 'exclude': []}))
            surface = root / 'title.txt'
            surface.write_text('NewBrand')
            result = self.run_script('brand', 'identity_audit.py', [root, '--rules', rules])
            self.assertEqual(result.returncode, 0, result.stderr)
            surface.write_text('PreviousBrand')
            result = self.run_script('brand', 'identity_audit.py', [root, '--rules', rules])
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)['findings'][0]['path'], 'title.txt')

    def test_frame_cli_comparison_and_heatmap(self):
        with tempfile.TemporaryDirectory(prefix='screenshots ') as tmp:
            root = Path(tmp)
            left, right, heat = (root / name for name in ('left.ppm', 'right.ppm', 'heat.ppm'))
            left.write_bytes(b'P6\n1 1\n255\n\x00\x00\x00')
            right.write_bytes(b'P6\n1 1\n255\n\xff\x00\x00')
            result = self.run_script('diff', 'frame_compare.py', [left, right, '--heatmap', heat])
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(json.loads(result.stdout)['changed_percent'], 100)
            self.assertTrue(heat.exists())

    def test_feedback_rejects_invalid_analysis_date(self):
        source = ROOT / 'skills/replica-entrepreneur/research.example.json'
        result = self.run_script('entrepreneur', 'feedback_triage.py', [source, '--as-of', 'yesterday'])
        self.assertEqual(result.returncode, 2)
        self.assertNotIn('Traceback', result.stderr)

    def test_identity_and_frame_output_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'text.txt').write_text('safe')
            rules = root / 'rules.json'
            rules.write_text(json.dumps({'schema_version': 1, 'terms': ['old'], 'include': ['**/*.txt'], 'exclude': []}))
            result = self.run_script('brand', 'identity_audit.py', [root, '--rules', rules, '--output', root / 'missing/out.json'])
            self.assertEqual(result.returncode, 2)
            self.assertNotIn('Traceback', result.stderr)
            frame = root / 'frame.ppm'
            frame.write_bytes(b'P6\n1 1\n255\n\x00\x00\x00')
            result = self.run_script('diff', 'frame_compare.py', [frame, frame, '--heatmap', root / 'missing/heat.ppm'])
            self.assertEqual(result.returncode, 2)
            self.assertNotIn('Traceback', result.stderr)
