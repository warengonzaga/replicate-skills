import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from support import ROOT, module, repository_module

installer = repository_module('install')
validator = repository_module('validate')


class Installation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='replicate project ')
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.destination = self.project / 'custom skills'

    def install(self, names=None, **options):
        with contextlib.redirect_stdout(io.StringIO()):
            installer.install(ROOT / 'skills', self.destination, names or ['replica-diff'], **options)

    def test_selected_skill_has_new_helpers_and_license(self):
        self.install()
        folder = self.destination / 'replica-diff'
        self.assertTrue((folder / 'frame_compare.py').is_file())
        self.assertTrue((folder / 'acceptance_gate.py').is_file())
        self.assertFalse((folder / 'parity.py').exists())
        self.assertEqual((folder / 'LICENSE').read_bytes(), (ROOT / 'LICENSE').read_bytes())
        self.assertEqual((folder / 'README.md').read_bytes(), (ROOT / 'README.md').read_bytes())

    def test_existing_user_changes_preserved_on_conflict(self):
        self.install()
        marker = self.destination / 'replica-diff' / 'custom.txt'
        marker.write_text('user-owned content')
        with self.assertRaises(ValueError):
            self.install()
        self.assertEqual(marker.read_text(), 'user-owned content')

    def test_replace_backs_up_user_changes(self):
        self.install()
        (self.destination / 'replica-diff' / 'custom.txt').write_text('retain me')
        self.install(replace=True)
        backups = list((self.project / '.replicate-skills-backups').glob('*/replica-diff/custom.txt'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), 'retain me')
        self.assertFalse((self.destination / 'replica-diff' / 'custom.txt').exists())

    def test_dry_run_does_not_write(self):
        self.install(dry_run=True)
        self.assertFalse(self.destination.exists())

    def test_unknown_skill_rejected(self):
        with self.assertRaises(ValueError):
            self.install(['replica-unrecognized'])

    def test_target_symlink_rejected(self):
        self.destination.mkdir()
        (self.destination / 'replica-diff').symlink_to(ROOT / 'skills' / 'replica-diff', target_is_directory=True)
        with self.assertRaises(ValueError):
            self.install(replace=True)

    def test_source_symlink_rejected(self):
        source = self.project / 'source'
        source.mkdir()
        (source / 'replica-diff').symlink_to(ROOT / 'skills' / 'replica-diff', target_is_directory=True)
        (self.project / 'LICENSE').write_text('fixture license')
        with self.assertRaises(ValueError):
            installer.install(source, self.destination, ['replica-diff'])

    def test_replacement_failure_rolls_back(self):
        self.install()
        marker = self.destination / 'replica-diff' / 'custom.txt'
        marker.write_text('recover me')
        original = Path.rename
        def fail_staged(path, target):
            if '.replicate-stage-' in str(path):
                raise OSError('simulated destination failure')
            return original(path, target)
        with patch.object(Path, 'rename', fail_staged), self.assertRaises(OSError):
            self.install(replace=True)
        self.assertEqual(marker.read_text(), 'recover me')

    def test_both_clients_receive_all_skills_with_space_paths(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/install.py'), '--runtime', 'both', '--project', str(self.project)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        for directory in ('.agents', '.claude'):
            skills = self.project / directory / 'skills'
            self.assertEqual(len(list(skills.glob('replica-*/SKILL.md'))), 11)
            for folder in skills.iterdir():
                self.assertEqual((folder / 'LICENSE').read_bytes(), (ROOT / 'LICENSE').read_bytes())

    def test_both_runtime_conflict_prevents_first_write(self):
        (self.project / '.claude/skills/replica-recon').mkdir(parents=True)
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/install.py'), '--runtime', 'both', '--project', str(self.project)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.project / '.agents').exists())


class Packaging(unittest.TestCase):
    def test_validator_accepts_pack(self):
        self.assertEqual(validator.validate(), [])

    def test_native_manifests_agree(self):
        claude = json.loads((ROOT / '.claude-plugin/plugin.json').read_text())
        codex = json.loads((ROOT / '.codex-plugin/plugin.json').read_text())
        for key in ('name', 'version', 'skills'):
            self.assertEqual(claude[key], codex[key])
        self.assertEqual(claude['skills'], './skills/')

    def test_skill_instructions_reference_existing_helpers(self):
        import re
        for path in (ROOT / 'skills').glob('*/SKILL.md'):
            for name in re.findall(r'\$SKILL_DIR/([\w_]+\.py)', path.read_text()):
                self.assertTrue((path.parent / name).is_file(), str(path))

    def test_new_tree_has_no_retired_helpers_or_templates(self):
        retired = {'contrast.py', 'listing.py', 'reviews.py', 'imgdiff.py', 'parity.py', 'sweep.py',
                   'tokens.json', 'themes.json', 'features.csv', 'recon-map.md', 'architecture.md',
                   'preflight.md', 'listing.example.json', 'test-plan.md', 'bug-report.md', 'e2e.example.spec.ts'}
        present = {path.name for path in (ROOT / 'skills').rglob('*') if path.is_file()}
        self.assertFalse(present & retired)

    def test_one_release_workflow(self):
        self.assertEqual([path.name for path in (ROOT / '.github/workflows').iterdir()], ['release.yml'])

    def test_examples_parse_as_versioned_json(self):
        for path in (ROOT / 'skills').glob('*/*.example.json'):
            self.assertEqual(json.loads(path.read_text())['schema_version'], 1)

    def test_current_license_is_owned_by_waren(self):
        text = (ROOT / 'LICENSE').read_text()
        self.assertIn('Copyright (c) 2026 Waren Gonzaga\n', text)
        self.assertNotIn('contributors', text)
        self.assertEqual(text.count('Copyright (c)'), 1)
