import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_usb_acm_userspace_abi import validate, file_flags

class ACMUserspace(unittest.TestCase):
    def test_pinned_abi_and_configfs_contract(self):
        self.assertFalse(validate()['runtime_qualified'])

    def test_arm64_overrides_reject_previously_accepted_generic_flags(self):
        flags = file_flags()
        self.assertEqual(flags['O_DIRECTORY'], 0o40000)
        self.assertEqual(flags['O_NOFOLLOW'], 0o100000)
        self.assertEqual(flags['O_DIRECT'], 0o200000)
        original = Path.read_text
        for old, new in [('FT_O_DIRECTORY 0040000', 'FT_O_DIRECTORY 00200000'),
                         ('FT_O_NOFOLLOW 0100000', 'FT_O_NOFOLLOW 00400000')]:
            def mutated(path, *args, **kwargs):
                text = original(path, *args, **kwargs)
                return text.replace(old, new) if path.name == 'acm_fs.h' else text
            with patch.object(Path, 'read_text', mutated), self.assertRaisesRegex(ValueError, 'File ABI mismatch'):
                validate()
        def wrong_policy(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            return text.replace('VP_NOFOLLOW 0100000', 'VP_NOFOLLOW 00400000') if path.name == 'lab_policy_load.h' else text
        with patch.object(Path, 'read_text', wrong_policy), self.assertRaisesRegex(ValueError, 'bootstrap ARM64'):
            validate()

    def test_actual_setup_and_filesystem_code_with_ram_syscalls(self):
        cc = shutil.which('cc')
        self.assertIsNotNone(cc)
        with tempfile.TemporaryDirectory() as tmp:
            for name, marker in [('setup', 'FIRETABS_ACM_SETUP_RAM_CONTROLS_PASS'),
                                 ('fs', 'FIRETABS_ACM_FS_RAM_CONTROLS_PASS')]:
                binary = Path(tmp) / name
                result = subprocess.run([cc, '-std=c11', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=address,undefined', '-I', str(ROOT / 'projects/firetabs-android/diagnostic-usb'),
                    str(ROOT / ('evidence/usb-acm-userspace/' + name + '-ram.c')), '-o', str(binary)],
                    capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                run = subprocess.run([str(binary)], capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertIn(marker, run.stdout)

if __name__ == '__main__':
    unittest.main()
