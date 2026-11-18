import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_reset_payload_jump as runner
from build_reset_payload import build, GEOMETRY
from test_native_jump_run import Device

CFG = 'a' * 64


class Fake(Device):
    args = []

    def __init__(self, digests):
        super().__init__()
        self.digests = digests

    def adb(self, *args, **kw):
        super().adb(*args, **kw)
        return subprocess.CompletedProcess(args, 0, b'usb:1-2\n' if args[0] == 'get-devpath' else b'', b'')

    def host(self, args, **kw):
        name = args[-1].split('/')[-1]
        return subprocess.CompletedProcess(args, 0, (self.digests[name] + ' file\n').encode(), b'')

    def shell(self, cmd, **kw):
        if cmd.startswith('sha256sum '):
            self.calls.append(cmd)
            return (self.digests[cmd.split('/')[-1]] + ' file\n').encode()
        return super().shell(cmd, **kw)


class ResetJump(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tools = tempfile.TemporaryDirectory()
        p = Path(cls.tools.name) / 'payload'
        cls.payload = build(p, 'a' * 32)
        cls.image = (p / 'Image').read_bytes()

    @classmethod
    def tearDownClass(cls):
        cls.tools.cleanup()

    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.p = Path(t.name)
        files = {'image.bin': self.image, 'metadata.bin': b'metadata', 'initrd.bin': b'initrd'}
        for name, data in files.items():
            (self.p / name).write_bytes(data)
        self.m = self.p / 'manifest.json'
        self.c = self.p / 'client.json'
        self.a = self.p / 'auth.json'
        self.manifest = dict(target_kind='reset-payload-v1', trial_id='1' * 32,
                             source_config_sha256=CFG, target_image_sha256=runner.sha(self.image),
                             source_kernel_image_sha256='c' * 64, source_dtb_sha256=runner.sha(b'dtb'),
                             original_boot_sha256=runner.BOOT_SHA, reset_nonce=self.payload['nonce'],
                             reset_payload_report_sha256=runner.sha(json.dumps(self.payload, sort_keys=True).encode()),
                             entry=0x42018000, segments=[dict(file=n, sha256=runner.sha(data), bytes=len(data),
                                 memory_bytes=4096, address=addr) for (n, data), addr in
                                 zip(files.items(), [0x40080000, 0x42000000, 0x69244000])])
        self.write_manifest()
        self.linked = dict(early_cpu_shutdown_before_devices=True, native_entry_checkpoint_linked=True,
                           artifacts={'.config': {'sha256': CFG}, 'arch/arm64/boot/Image': {'sha256': 'c' * 64}})
        self.source = {'functionfs_hold': True}
        self.digests = {n: runner.sha(data) for n, data in files.items()}
        self.digests['native-load'] = 'a' * 64
        self.d = Fake(self.digests)
        self.auth = dict(scope=runner.SCOPE, runner_sha256=runner.sha(Path(runner.__file__).read_bytes()),
                         manifest_sha256=runner.sha(self.m.read_bytes()), client_sha256='a' * 64,
                         target_image_sha256=runner.sha(self.image), native_config_sha256=CFG,
                         reset_payload_report_sha256=self.manifest['reset_payload_report_sha256'],
                         source_capture_report_sha256=runner.sha(json.dumps(self.source, sort_keys=True).encode()),
                         source_capture_manager_sha256=runner.sha(Path('scripts/source_usb_console_trial.py').read_bytes()),
                         owner_approved=True, owner_available=True, maximum_loads=1, maximum_jump_requests=1,
                         boot_writes_allowed=False, automatic_reboot_commands_allowed=False,
                         bounded_read_only_return_poll_allowed=True)
        self.a.write_text(json.dumps(self.auth))

    def write_manifest(self):
        self.m.write_text(json.dumps(self.manifest))
        self.c.write_text(json.dumps(dict(manifest_sha256=runner.sha(self.m.read_bytes()),
                                          client_sha256='a' * 64, execute_implemented=False)))

    def invoke(self, execute=True, matches=1, replay=False):
        def facts(d):
            return dict(boot=runner.BOOT_SHA, config=runner.ORIGINAL_CONFIG if d.target else CFG,
                        boot_id=('22222222' if d.target else '11111111') + '-1111-1111-1111-111111111111')
        before = [{'marker_matches': 1}] if replay else []
        with patch.object(runner, 'facts', side_effect=facts), patch.object(runner, 'geometry', return_value=GEOMETRY), \
                patch.object(runner, 'records', side_effect=[before, [{'marker_matches': matches}]]), \
                patch.object(runner, 'SourceCapture') as capture:
            capture.return_value.collect.return_value = {'native_entry_seen': True}
            return runner.run(self.d, '/lab', self.m, self.c, self.linked, self.p / 'out',
                              self.payload, self.source, self.a if execute else None)

    def result(self):
        return json.loads((self.p / 'out/result.json').read_text())

    def test_exact_marker_and_fresh_original_return_still_need_owner_confirmation(self):
        r = self.invoke()
        self.assertTrue(r['target_entry_proven'])
        self.assertTrue(r['fresh_original_android_return'])
        self.assertTrue(r['normal_shell_restored'])
        self.assertFalse(r['automatic_reset_qualified'])
        self.assertEqual(runner.classify(r, False), 'reset-target-executed-and-auto-return-qualified')
        self.assertEqual((r['load_attempts'], r['jump_requests']), (1, 1))
        self.assertFalse(r['target_linux_boot_proven'])

    def test_reboot_without_marker_requires_pivot(self):
        r = self.invoke(matches=0)
        self.assertFalse(r['target_entry_proven'])
        self.assertTrue(r['pivot_required'])
        self.assertEqual(runner.classify(r, False), 'not-qualified-pivot-required')

    def test_duplicate_marker_is_not_attributable(self):
        self.assertFalse(self.invoke(matches=2)['target_entry_proven'])

    def test_owner_power_or_missing_confirmation_cannot_qualify_auto_reset(self):
        r = self.invoke()
        for used in [True, None]:
            self.assertEqual(runner.classify(r, used), 'not-qualified-pivot-required')

    def test_preflight_never_loads(self):
        r = self.invoke(execute=False)
        self.assertTrue(r['complete'])
        self.assertEqual((r['load_attempts'], r['jump_requests']), (0, 0))

    def test_existing_marker_refuses_replay_before_load(self):
        with self.assertRaises(ValueError):
            self.invoke(replay=True)
        self.assertEqual(self.result()['load_attempts'], 0)

    def test_legacy_scope_refused_before_device_access(self):
        self.auth['scope'] = 'native-early-cpu-usb-source-target-console-jump-1'
        self.a.write_text(json.dumps(self.auth))
        with self.assertRaises(ValueError):
            self.invoke()
        self.assertEqual(self.d.calls, [])

    def test_changed_code_outside_nonce_refused_before_device_access(self):
        b = bytearray(self.image); b[100] ^= 1
        (self.p / 'image.bin').write_bytes(b)
        with self.assertRaises(ValueError):
            self.invoke()
        self.assertEqual(self.d.calls, [])

    def test_offline_preview_refused_before_device_access(self):
        self.manifest['offline_preview'] = True; self.write_manifest()
        with self.assertRaises(ValueError):
            self.invoke()
        self.assertEqual(self.d.calls, [])

    def test_uncertain_load_unloaded_once_before_jump(self):
        self.d.load_error = True
        with self.assertRaises(RuntimeError):
            self.invoke()
        self.assertEqual((self.result()['unload_attempts'], self.result()['jump_requests']), (1, 0))

    def test_no_return_does_not_unload_unroot_or_retry_after_jump(self):
        with patch.object(runner.time, 'monotonic', side_effect=[0, 301]):
            r = self.invoke()
        self.assertEqual((r['jump_requests'], r['unload_attempts']), (1, 0))
        at = self.d.calls.index('setprop sys.powerctl reboot,valethon-kexec')
        self.assertEqual(self.d.calls[at + 1:], [])
        self.assertTrue(r['pivot_required'])


if __name__ == '__main__':
    unittest.main()
