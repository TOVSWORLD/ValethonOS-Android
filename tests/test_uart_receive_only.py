import hashlib
import importlib.util
import json
import os
from pathlib import Path
import pty
import select
import tempfile
import termios
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location('uart_capture', Path(__file__).resolve().parents[1] / 'scripts/capture_uart_receive_only.py')
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class ReceiveOnly(unittest.TestCase):
    def test_exact_binary_capture_restores_settings_and_never_writes_to_port(self):
        master, slave = pty.openpty()
        try:
            original = termios.tcgetattr(slave)
            payload = b'\x00boot\r\nLinux version TEST\xff\x13\x11\n'
            real_open, real_write = os.open, os.write
            opens, writes = [], []
            port = os.ttyname(slave)
            def opening(path, flags, *args, **kw):
                fd = real_open(path, flags, *args, **kw)
                opens.append((str(path), flags, fd))
                return fd
            def writing(fd, data):
                writes.append(fd)
                return real_write(fd, data)
            with tempfile.TemporaryDirectory() as t, mock.patch.object(m.os, 'open', side_effect=opening), mock.patch.object(m.os, 'write', side_effect=writing):
                result = m.capture(port, Path(t) / 'capture', 115200, 0.1,
                                   ready=lambda: real_write(master, payload))
                self.assertEqual((Path(t) / 'capture/uart-private.bin').read_bytes(), payload)
                self.assertEqual(result['sha256'], hashlib.sha256(payload).hexdigest())
                self.assertTrue(result['raw_fsynced'])
                self.assertFalse(result['uart_qualified'])
                self.assertFalse(result['linux_boot_proven'])
                self.assertEqual((Path(t) / 'capture/uart-private.bin').stat().st_mode & 0o777, 0o600)
            opened = [x for x in opens if x[0] == port]
            self.assertEqual(len(opened), 1)
            self.assertEqual(opened[0][1] & os.O_ACCMODE, os.O_RDONLY)
            self.assertNotIn(opened[0][2], writes)
            restored = termios.tcgetattr(slave)
            restored[3] &= ~getattr(termios, 'PENDIN', 0)
            original[3] &= ~getattr(termios, 'PENDIN', 0)
            self.assertEqual(restored, original)
            self.assertTrue(result['settings_restored'])
            self.assertFalse(select.select([master], [], [], 0)[0])
        finally:
            os.close(master)
            os.close(slave)

    def test_silence_is_inconclusive(self):
        master, slave = pty.openpty()
        try:
            with tempfile.TemporaryDirectory() as t:
                result = m.capture(os.ttyname(slave), Path(t) / 'capture', 115200, 0.02)
                self.assertEqual(result['bytes'], 0)
                self.assertTrue(result['silence_inconclusive'])
                self.assertEqual(result['reason'], 'deadline')
        finally:
            os.close(master)
            os.close(slave)

    def test_byte_limit_keeps_only_bounded_prefix(self):
        master, slave = pty.openpty()
        try:
            with tempfile.TemporaryDirectory() as t:
                result = m.capture(os.ttyname(slave), Path(t) / 'capture', 115200, 0.1, max_bytes=4,
                                   ready=lambda: os.write(master, b'12345678'))
                self.assertEqual(result['bytes'], 4)
                self.assertEqual(result['reason'], 'byte-limit')
                self.assertEqual((Path(t) / 'capture/uart-private.bin').read_bytes(), b'1234')
        finally:
            os.close(master)
            os.close(slave)

    def test_regular_file_refused_and_failure_receipt_saved(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t)
            (p / 'not-a-port').write_bytes(b'unchanged')
            with self.assertRaises(ValueError):
                m.capture(p / 'not-a-port', p / 'capture', 115200, 0.02)
            self.assertEqual((p / 'not-a-port').read_bytes(), b'unchanged')
            report = json.loads((p / 'capture/report.json').read_text())
            self.assertEqual(report['failure_kind'], 'ValueError')
            self.assertTrue(report['raw_fsynced'])

    def test_invalid_bounds_and_existing_output_refuse_before_serial_open(self):
        with tempfile.TemporaryDirectory() as t, mock.patch.object(m.os, 'open') as opening:
            for kwargs in [dict(seconds=float('nan')), dict(seconds=301), dict(seconds=0),
                           dict(max_bytes=0), dict(max_bytes=m.MAX_BYTES + 1), dict(baud=9600)]:
                with self.assertRaises(ValueError):
                    m.capture('/nonexistent', Path(t) / 'capture', baud=kwargs.pop('baud', 115200), **kwargs)
            with self.assertRaises(FileExistsError):
                m.capture('/nonexistent', Path(t), baud=115200)
            opening.assert_not_called()


if __name__ == '__main__':
    unittest.main()
