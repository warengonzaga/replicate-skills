import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from _load import load, ROOT

installer = load('scripts', 'install')


class Installer(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='skills with spaces ')
        self.addCleanup(self.tmp.cleanup)
        self.destination = Path(self.tmp.name) / 'skills'

    def install(self, **options):
        with contextlib.redirect_stdout(io.StringIO()):
            installer.install(Path(ROOT) / "skills", self.destination, ['replica-diff'], **options)

    def test_helpers_and_templates_preserved(self):
        self.install()
        for name in ['SKILL.md', 'imgdiff.py', 'parity.py']:
            self.assertEqual((self.destination / 'replica-diff' / name).read_bytes(),
                             (Path(ROOT) / 'skills' / 'replica-diff' / name).read_bytes())

    def test_install_preserves_required_license(self):
        self.install()
        self.assertEqual((self.destination / 'replica-diff/LICENSE').read_bytes(),
                         (Path(ROOT) / 'LICENSE').read_bytes())

    def test_conflict_preserves_user_files(self):
        self.install()
        marker = self.destination / 'replica-diff/custom.txt'
        marker.write_text('user edit')
        with self.assertRaises(ValueError):
            self.install()
        self.assertEqual(marker.read_text(), 'user edit')

    def test_dry_run_has_no_filesystem_side_effects(self):
        self.install(dry_run=True)
        self.assertFalse(self.destination.exists())

    def test_replace_keeps_dated_backup(self):
        self.install()
        (self.destination / 'replica-diff/custom.txt').write_text('preserve me')
        self.install(replace=True)
        backups = list((self.destination.parent / '.replicate-skills-backups').glob('*/replica-diff/custom.txt'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), 'preserve me')
        self.assertFalse((self.destination / 'replica-diff/custom.txt').exists())

    def test_failure_restores_replaced_skill(self):
        self.install()
        (self.destination / 'replica-diff/custom.txt').write_text('preserve me')
        rename = Path.rename

        def fail_staged(path, target):
            if path.parent.name.startswith('.replicate-stage-'):
                raise OSError('simulated disk error')
            return rename(path, target)

        with patch.object(Path, 'rename', fail_staged):
            with self.assertRaises(OSError):
                self.install(replace=True)
        self.assertEqual((self.destination / 'replica-diff/custom.txt').read_text(), 'preserve me')

    def test_rejects_symlink_target_and_unknown_skill(self):
        external = self.destination.parent / 'external'
        external.mkdir()
        self.destination.mkdir()
        (self.destination / 'replica-diff').symlink_to(external, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.install(replace=True)
        with self.assertRaises(ValueError):
            installer.install(Path(ROOT) / "skills", self.destination, ['../outside'])

    def test_cli_both_destinations_and_preflight(self):
        command = [sys.executable, str(Path(ROOT) / 'scripts/install.py'), '--runtime', 'both',
                   '--project', self.tmp.name, '--skill', 'replica-design']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        for folder in ['.agents', '.claude']:
            helper = Path(self.tmp.name) / folder / 'skills/replica-design/contrast.py'
            self.assertTrue(helper.is_file())
        # A conflict in the second runtime must block mutation of the first.
        import shutil
        shutil.rmtree(str(Path(self.tmp.name) / '.agents/skills/replica-design'))
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((Path(self.tmp.name) / '.agents/skills/replica-design').exists())


if __name__ == '__main__':
    unittest.main()
