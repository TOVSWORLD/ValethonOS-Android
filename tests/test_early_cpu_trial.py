import json
import unittest
from pathlib import Path
import test_single_cpu_target as cpu_fixture
import test_usb_console_jump as fixture
from test_usb_console_jump import runner


class EarlyCPUTrial(unittest.TestCase):
    setUp = fixture.Tests.setUp
    write_manifest = fixture.Tests.write_manifest
    result = fixture.Tests.result
    invoke = cpu_fixture.GuardedTrial.invoke

    def setup_mode(self):
        self.linked.update(early_cpu_shutdown_before_devices=True, native_entry_checkpoint_linked=True)
        self.source = {'functionfs_hold': True, 'receiver_sha256': runner.sha(
            Path('scripts/capture_source_usb_console.py').read_bytes()), 'helper_sha256': 'f' * 64}
        self.auth.update(scope='native-early-cpu-usb-source-target-console-jump-1',
                         source_cpu_shutdown_before_devices=True,
                         source_capture_report_sha256=runner.sha(json.dumps(self.source, sort_keys=True).encode()),
                         source_capture_manager_sha256=runner.sha(Path('scripts/source_usb_console_trial.py').read_bytes()))
        self.a.write_text(json.dumps(self.auth))

    def test_new_scope_admits_one_captured_jump(self):
        self.setup_mode()
        r = self.invoke()
        self.assertTrue(r['source_cpu_shutdown_before_devices'])
        self.assertEqual((r['load_attempts'], r['jump_requests']), (1, 1))
        self.assertTrue(r['target_entry_proven'])

    def test_old_scope_refused_before_hardware(self):
        self.setup_mode()
        self.auth['scope'] = 'native-usb-source-target-console-jump-1'
        self.a.write_text(json.dumps(self.auth))
        with self.assertRaises(ValueError):
            self.invoke()
        self.assertEqual(self.device.calls, [])

    def test_capture_required(self):
        self.setup_mode()
        with self.assertRaises(ValueError):
            self.invoke(source=False)
        self.assertEqual(self.device.calls, [])

    def test_failed_cpu0_mode_cannot_be_combined(self):
        self.setup_mode()
        self.manifest['target_cpu_limit'] = 1
        self.write_manifest()
        with self.assertRaises(ValueError):
            self.invoke()
        self.assertEqual(self.device.calls, [])

    def test_preflight_does_not_load_or_jump(self):
        self.setup_mode()
        r = self.invoke(execute=False)
        self.assertEqual((r['load_attempts'], r['jump_requests']), (0, 0))


if __name__ == '__main__':
    unittest.main()
