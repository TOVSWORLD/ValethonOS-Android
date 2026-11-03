from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from run_lab_log_trial import lifecycle


class TrialLifecycle(unittest.TestCase):
    def test_no_helper_during_normal_entry_and_one_later_launch(self):
        now = [0]
        calls = []
        def sleep(seconds):
            now[0] += seconds
        def scan():
            calls.append(('scan', now[0]))
            return '/dev/ttyACM-fixture' if now[0] >= 145 else None
        def launch(port, seconds):
            calls.append(('launch', now[0], port, seconds))
            return 0
        def capture():
            now[0] += 45
            return {'complete': False}
        result = lifecycle(lambda: now[0] < 10, capture, scan, launch, lambda: now[0], sleep)
        self.assertEqual(result['helper_returncode'], 0)
        self.assertFalse(result['capture']['complete'])
        self.assertTrue(all(c[1] >= 100 for c in calls))
        self.assertEqual(sum(c[0] == 'launch' for c in calls), 1)

    def test_travel_timeout_or_capture_overrun_never_launches(self):
        for overrun in [False, True]:
            now = [0]
            def sleep(seconds):
                now[0] += seconds
            def capture():
                now[0] += 86
            def forbidden(*args):
                self.fail('Helper/scanner must not run')
            with self.assertRaises(TimeoutError):
                lifecycle(lambda: True if not overrun else now[0] < 1, capture, forbidden, forbidden,
                          lambda: now[0], sleep)

class RecoveryReadiness(unittest.TestCase):
    def test_metadata_only_then_stable_identity_and_no_partition_io(self):
        from run_lab_log_trial import wait_recovery_identity
        from types import SimpleNamespace
        now = [0.0]; calls = []
        def run(command, capture_output, timeout):
            self.assertTrue(capture_output); self.assertLessEqual(timeout, 2)
            calls.append(command)
            if command[-1] == 'get-state': data = b'recovery'
            elif command[-1] == 'ro.product.device': data = b'douglas' if now[0] >= .5 else b''
            else: data = b'3.3.1-0'
            return SimpleNamespace(returncode=0, stdout=data)
        wait_recovery_identity(SimpleNamespace(command=['adb', '-s', 'private-fixture']),
                               clock=lambda: now[0], sleep=lambda n: now.__setitem__(0, now[0]+n), run=run)
        self.assertGreaterEqual(now[0], .75)
        self.assertTrue(all('getprop' in c or c[-1] == 'get-state' for c in calls))
        self.assertFalse(any('exec-out' in c or 'wait-for-recovery' in c for c in calls))

    def test_mismatch_and_hung_probe_exhaust_only_metadata_budget(self):
        from run_lab_log_trial import wait_recovery_identity
        from types import SimpleNamespace
        import subprocess
        for hang in [False, True]:
            now = [0.0]; calls = []
            def run(command, capture_output, timeout):
                calls.append(command)
                if hang:
                    now[0] += timeout
                    raise subprocess.TimeoutExpired(command, timeout)
                return SimpleNamespace(returncode=1, stdout=b'wrong')
            with self.assertRaises(TimeoutError):
                wait_recovery_identity(SimpleNamespace(command=['adb', '-s', 'private-fixture']),
                                       clock=lambda: now[0], sleep=lambda n: now.__setitem__(0, now[0]+n), run=run)
            self.assertEqual(now[0], 30)
            self.assertLessEqual(len(calls), 120)
