from pathlib import Path
import hashlib
import os
import sys
import tempfile
import termios
import struct
import threading
import select
from unittest.mock import patch
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import capture_lab_kernel_log as receiver
from kernel_log_protocol import MAGIC, ACK, DONE
from capture_lab_kernel_log import validate, endpoint_identity, private_bytes, raw_settings


class LabCapture(unittest.TestCase):
    def test_private_selector_contract_and_negatives(self):
        nonce = bytes(range(32))
        plan = {'purpose': 'first-normal-log-bringup', 'candidate_sha256': 'a' * 64,
                'physical_usb_path': '3-2.4', 'usb_id': '1209:0001', 'interface': '00', 'wait_seconds': 600}
        report = {'partition_sha256': 'a' * 64, 'nonce_sha256': hashlib.sha256(nonce).hexdigest()}
        validate(plan, report, nonce)
        for name, value in [('purpose', 'failure'), ('candidate_sha256', 'b' * 64),
                            ('physical_usb_path', '../../3-2.4'), ('interface', '01'), ('wait_seconds', 901)]:
            with self.assertRaises(ValueError):
                validate({**plan, name: value}, report, nonce)
        with self.assertRaises(ValueError):
            validate(plan, report, bytes(32))
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'nonce'
            p.write_bytes(nonce)
            p.chmod(0o600)
            self.assertEqual(private_bytes(p, 32), nonce)
            p.chmod(0o644)
            with self.assertRaises(ValueError):
                private_bytes(p, 32)

    def test_exact_sysfs_identity_without_opening_device(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            interface = root / 'devices/usb3/3-2.4/3-2.4:1.0'
            interface.mkdir(parents=True)
            (interface.parent / 'idVendor').write_text('1209\n')
            (interface.parent / 'idProduct').write_text('0001\n')
            (interface / 'bInterfaceNumber').write_text('00\n')
            driver = root / 'drivers/cdc_acm'
            driver.mkdir(parents=True)
            (interface / 'driver').symlink_to(driver)
            tty = root / 'class/tty/ttyACM0'
            tty.mkdir(parents=True)
            (tty / 'device').symlink_to(interface)
            (tty / 'dev').write_text('166:0\n')
            plan = {'physical_usb_path': '3-2.4', 'interface': '00'}
            self.assertEqual(endpoint_identity('ttyACM0', plan, root)['rdev'], os.makedev(166, 0))
            self.assertIsNone(endpoint_identity('ttyACM0', {**plan, 'physical_usb_path': '3-2.5'}, root))
            (interface / 'bInterfaceNumber').write_text('01\n')
            with self.assertRaises(ValueError):
                endpoint_identity('ttyACM0', plan, root)

    def test_complete_capture_uses_software_pty_and_durable_private_files(self):
        master, slave = os.openpty()
        nonce = bytes(range(32))
        record = b'6,0,0,-;fixture kernel record\n'
        wire = MAGIC + nonce + struct.pack('>II', 0, len(record)) + record + struct.pack('>II', 1, 0)
        ready = threading.Event()
        original_set = termios.tcsetattr
        acknowledgments = []
        def configure(*args):
            result = original_set(*args)
            ready.set()
            return result
        def producer():
            if not ready.wait(3):
                return
            os.write(master, wire)
            for _ in range(2):
                if select.select([master], [], [], 3)[0]:
                    acknowledgments.append(os.read(master, 80))
                if len(b''.join(acknowledgments)) == 80:
                    break
        thread = threading.Thread(target=producer)
        selected = {'endpoint': os.ttyname(slave), 'rdev': os.fstat(slave).st_rdev, 'sysfs': 'software-fixture'}
        try:
            with tempfile.TemporaryDirectory() as d:
                thread.start()
                with patch.object(receiver, 'endpoint_identity', return_value=selected), \
                     patch.object(Path, 'glob', return_value=[Path('ttyACM0')]), \
                     patch.object(receiver.termios, 'tcsetattr', side_effect=configure):
                    result = receiver.capture({'wait_seconds': 1}, nonce, Path(d) / 'new-capture')
                thread.join(4)
                self.assertFalse(thread.is_alive())
                self.assertTrue(result['complete'])
                self.assertEqual((Path(d) / 'new-capture/raw.bin').read_bytes(), wire)
                self.assertEqual(b''.join(acknowledgments), ACK + nonce + DONE + nonce)
                self.assertEqual((Path(d) / 'new-capture/raw.bin').stat().st_mode & 0o777, 0o600)
                self.assertTrue((Path(d) / 'new-capture/receipt.json').exists())
        finally:
            os.close(master)
            os.close(slave)

    def test_host_raw_settings_from_real_software_pty(self):
        master, slave = os.openpty()
        try:
            attrs = raw_settings(termios.tcgetattr(slave))
            termios.tcsetattr(slave, termios.TCSANOW, attrs)
            self.assertEqual(termios.tcgetattr(slave)[0:2], [0, 0])
        finally:
            os.close(master)
            os.close(slave)
