import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_kexec_probe as probe


class RuntimeBoundary(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name); self.module = self.base / 'probe.ko'
        self.module.write_bytes(b'compiled-probe-fixture'); self.sha = hashlib.sha256(self.module.read_bytes()).hexdigest()
        self.config = b'exact-config'; self.boot = bytes(16777216)
        self.commands = []; self.loaded = False; self.ever_loaded = False
        self.state = b'device\n'; self.bad_config = False; self.reject_load = False
        self.auth = self.base / 'approval.json'
        self.auth.write_text(json.dumps({'scope': probe.SCOPE, 'module_sha256': self.sha,
            'target_boot_sha256': probe.BOOT_SHA, 'owner_approved': True,
            'owner_available': True, 'handoff_allowed': False}))

    def execute(self, approved=True):
        def digest(data):
            if data == self.config: return probe.CONFIG_SHA
            if data == self.boot: return probe.BOOT_SHA
            return hashlib.sha256(data).hexdigest()
        with patch.object(probe, 'verify', return_value={'module_sha256': self.sha}), \
             patch.object(probe, 'digest', side_effect=digest), \
             patch.object(probe.subprocess, 'run', side_effect=self.adb):
            return probe.run('test-serial', self.module, self.base / 'symvers',
                             self.base / 'result', self.auth if approved else None)

    def adb(self, args, **kwargs):
        command = 'push ' + args[-1] if len(args) > 3 and args[3] == 'push' else args[-1]
        self.commands.append(command)
        rc = 0; err = b''
        if command == 'get-state': data = self.state
        elif command == 'uname -r': data = probe.RELEASE.encode() + b'\n'
        elif command == 'id': data = b'uid=0(root) gid=0(root)\n'
        elif command == 'cat /proc/config.gz': data = gzip.compress(b'wrong' if self.bad_config else self.config)
        elif command == 'head -c 16777216 /dev/block/mmcblk0p5': data = self.boot
        elif command == 'cat /proc/modules': data = b''
        elif command == 'dmesg':
            data = ('KXPROBE v1 release=' + probe.RELEASE + ' page_shift=12 current_el=1 online_cpus=4\n' + ''.join('KXPROBE symbol=' + n + ' present=1\n' for n in sorted(probe.SYMBOLS)) + 'KXPROBE complete handoff_attempted=0\n').encode() if self.ever_loaded else b'normal kernel log\n'
        elif command == 'cat /proc/mounts': data = b'tmpfs /dev tmpfs rw 0 0\n'
        elif command.startswith('umask 077; set -C; : > /dev/kxprobe-'): data = b''
        elif command.startswith('push /dev/kxprobe-'): data = b''
        elif command.startswith('chmod 600 /dev/kxprobe-'): data = b''
        elif command.startswith('cat /dev/kxprobe-'): data = self.module.read_bytes()
        elif command.startswith('insmod /dev/kxprobe-'):
            data = b''
            if self.reject_load: rc = 1; err = b'Invalid module format\n'
            else: self.loaded = self.ever_loaded = True
        elif command == 'rmmod kxprobe': self.loaded = False; data = b''
        elif command.startswith('rm -f /dev/kxprobe-'): data = b''
        elif command.startswith('test ! -e /dev/kxprobe-'): data = b''
        else: raise AssertionError('Unexpected operation: ' + command)
        return subprocess.CompletedProcess(args, rc, data, err)

    def test_lone_completion_marker_is_not_a_compatibility_result(self):
        with self.assertRaises(ValueError):
            probe.parse_records(['KXPROBE complete handoff_attempted=0'])

    def test_recovery_rejected_before_staging(self):
        self.state = b'recovery\n'
        with self.assertRaisesRegex(ValueError, 'normal Android'): self.execute()
        self.assertFalse(any('insmod' in c or 'cat >' in c for c in self.commands))

    def test_wrong_live_config_rejected_before_staging(self):
        self.bad_config = True
        with self.assertRaisesRegex(ValueError, 'configuration differs'): self.execute()
        self.assertFalse(any('insmod' in c or 'cat >' in c for c in self.commands))

    def test_wrong_approval_rejected_before_device_access(self):
        self.auth.write_text(json.dumps({'owner_approved': True}))
        with self.assertRaisesRegex(ValueError, 'Exact probe approval'): self.execute()
        self.assertEqual(self.commands, [])

    def test_preflight_without_approval_never_stages_or_loads(self):
        result = self.execute(approved=False)
        self.assertTrue(result['complete']); self.assertEqual(result['module_load_attempts'], 0)
        self.assertFalse(any('cat >' in c or c.startswith('insmod') for c in self.commands))

    def test_kernel_rejection_cleans_ram_and_never_force_loads(self):
        self.reject_load = True
        with self.assertRaisesRegex(RuntimeError, 'Kernel rejected'): self.execute()
        self.assertEqual(sum(c.startswith('insmod ') for c in self.commands), 1)
        self.assertFalse(any(c == 'rmmod kxprobe' or '-f ' in c and c.startswith('insmod') for c in self.commands))
        result = json.loads((self.base / 'result/result.json').read_text())
        self.assertTrue(result['ram_cleanup_verified']); self.assertFalse(result['complete'])
        self.assertTrue((self.base / 'result/dmesg-final-private.txt').exists())

    def test_success_is_one_ram_load_unload_with_no_handoff(self):
        result = self.execute()
        self.assertTrue(result['module_unloaded']); self.assertTrue(result['ram_cleanup_verified'])
        self.assertEqual(result['module_load_attempts'], 1); self.assertFalse(result['handoff_attempted'])
        self.assertFalse(any('reboot' in c or 'kexec' in c or '/data/' in c for c in self.commands))
        uploads = [c for c in self.commands if c.startswith('push ')]
        self.assertEqual(len(uploads), 1)
        self.assertTrue(uploads[0].startswith('push /dev/kxprobe-'))
        self.assertEqual((self.base / 'result/dmesg-loaded-private.txt').stat().st_mode & 0o777, 0o600)

if __name__ == '__main__': unittest.main()
