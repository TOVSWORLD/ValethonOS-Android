import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import bounded_recovery_entry as b


class Clock:
    def __init__(self): self.t = 0
    def now(self): return self.t
    def sleep(self, seconds): self.t += seconds


class RecoveryBounds(unittest.TestCase):
    def test_absent_initial_device_never_launches(self):
        with self.assertRaises(ValueError):
            b.wait_then_launch(lambda: False, lambda: self.fail(), lambda *a: self.fail())

    def test_travel_expiry_never_scans_or_launches(self):
        c = Clock()
        with self.assertRaises(TimeoutError):
            b.wait_then_launch(lambda: True, lambda: self.fail(), lambda *a: self.fail(), c.now, c.sleep)
        self.assertGreaterEqual(c.t, 600)
        self.assertLess(c.t, 601)

    def test_reconnect_expiry_allows_manual_shutdown(self):
        c = Clock()
        initial = iter([True, False])
        with self.assertRaises(TimeoutError):
            b.wait_then_launch(lambda: next(initial), lambda: None, lambda *a: self.fail(), c.now, c.sleep)
        self.assertGreaterEqual(c.t, 300)
        self.assertLess(c.t, 301)

    def test_one_launch_with_full_handshake_deadline_after_long_shutdown(self):
        c = Clock()
        calls = []
        def present(): return c.t < 123
        def scan(): return '/dev/ttyACM0' if c.t > 234 else None
        result = b.wait_then_launch(present, scan, lambda *a: calls.append(a) or 7, c.now, c.sleep)
        self.assertEqual(result, 7)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1], 90)
        self.assertGreater(c.t, 234)

    def test_identity_and_ambiguity_rejection(self):
        row = {'vendor': '0e8d', 'product': '2000', 'usb_path': '1-2.3', 'port': '/dev/ttyACM0'}
        self.assertEqual(b.choose_port([row], '1-2.3'), '/dev/ttyACM0')
        self.assertIsNone(b.choose_port([], '1-2.3'))
        for rows in [[row, row], [dict(row, usb_path='1-9')],
                     [dict(row, product='0003')], [dict(row, port='/dev/ttyUSB0')]]:
            with self.assertRaises(ValueError): b.choose_port(rows, '1-2.3')

    def test_changed_sources_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name in b.HASHES: (root/name).write_bytes(b'changed')
            with self.assertRaises(ValueError): b.verify_sources(root)

    def test_helper_timeout_has_one_launch_and_kills_group(self):
        with tempfile.TemporaryDirectory() as d, patch.object(b, 'verify_sources'), \
                patch.object(b.subprocess, 'Popen') as popen, patch.object(b.os, 'killpg') as kill:
            p = popen.return_value
            p.pid = 1234
            p.wait.side_effect = [subprocess.TimeoutExpired('helper', 4), 0]
            with self.assertRaises(subprocess.TimeoutExpired):
                b.launch_helper(Path(d), '/dev/ttyACM2', 4, Path(d)/'private.log')
            self.assertEqual(popen.call_count, 1)
            kill.assert_called_once_with(1234, b.signal.SIGKILL)
            args = popen.call_args.args[0]
            self.assertIn('-I', args)
            self.assertEqual(args[-1], '/dev/ttyACM2')

    def test_isolated_child_executes_pinned_sources_without_local_import_path(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sources = {'logger.py': b'value=40\n', 'common.py': b'from logger import value\nvalue+=2\n',
                       'handshake2.py': b'import sys\nfrom common import value\nassert value==42\nassert sys.argv[1:]==["FACTORYM","/dev/ttyACM9"]\n'}
            for n, raw in sources.items(): (root/n).write_bytes(raw)
            hashes = {n: hashlib.sha256(raw).hexdigest() for n, raw in sources.items()}
            with patch.object(b, 'HASHES', hashes):
                self.assertEqual(b.launch_helper(root, '/dev/ttyACM9', 3, root/'test.log'), 0)


if __name__ == '__main__': unittest.main()
