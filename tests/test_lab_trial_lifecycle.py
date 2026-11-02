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
