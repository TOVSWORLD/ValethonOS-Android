"""New calibration admission, return exclusivity and evidence discrimination."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import guard_known_boot_capture as guard
import known_boot_capture_device as device
import known_boot_control_return as manual
from known_boot_control_watch import private_json
from assess_known_boot_control import assess_record
import retained_log_mailbox as mailbox
import loader_checkpoint_record as record
from restore_diagnostic_boot import update_receipt


def authorization():
    return dict(scope='known-boot-capture-control-1', candidate_sha256=guard.KERNEL_CANDIDATE,
                observer_sha256=guard.CANDIDATE, owner_approved=True, owner_available=True,
                minimum_seconds=300, automatic_return=False)


class Admission(unittest.TestCase):
    def test_exact_pair_only(self):
        guard.authorize(authorization())
        for key, value in [('owner_available', False), ('owner_approved', False),
                           ('candidate_sha256', '0'*64), ('observer_sha256', '0'*64),
                           ('automatic_return', True), ('minimum_seconds', 90)]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                guard.authorize(dict(authorization(), **{key: value}))

    def test_missing_approval_stops_before_device(self):
        with tempfile.TemporaryDirectory() as folder:
            private = Path(folder)
            args = (private, b'', b'', b'', b'', {}, {}, b'', 'selected')
            for action in ('install-observer', 'install-boot'):
                with patch.object(device, 'inputs', return_value=args), patch.object(device, 'Adb') as adb:
                    with self.assertRaises(FileNotFoundError):
                        device.run(private, action)
                    adb.return_value.run.assert_not_called()
                    adb.return_value.read.assert_not_called()

    def test_repaired_original_bootstrap_is_not_written(self):
        args = (Path('/unused'), b'', b'', b'', b'original', {}, {}, b'', 'selected')
        with patch.object(device, 'inputs', return_value=args), patch.object(device, 'Adb'), \
                patch.object(device, 'returned_hash', return_value='a'*64), \
                patch.object(guard, 'range_read', return_value=b'original'), \
                patch.object(device, 'sha', return_value=guard.ORIGINAL), \
                patch.object(guard, 'preflight') as preflight, patch.object(guard, 'write_once') as write:
            result = device.run(Path('/unused'), 'restore-bootstrap')
            self.assertTrue(result['bootstrap_already_original'])
            preflight.assert_called_once(); write.assert_not_called()

    def test_unknown_bootstrap_stops_without_write(self):
        args = (Path('/unused'), b'', b'', b'', b'', {}, {}, b'', 'selected')
        with patch.object(device, 'inputs', return_value=args), patch.object(device, 'Adb'), \
                patch.object(device, 'returned_hash', return_value='a'*64), \
                patch.object(guard, 'range_read', return_value=b'unknown'), \
                patch.object(guard, 'write_once') as write:
            with self.assertRaisesRegex(ValueError, 'Unexpected bootstrap'):
                device.run(Path('/unused'), 'restore-bootstrap')
            write.assert_not_called()


class ManualReturn(unittest.TestCase):
    def test_receipt_private_even_with_loose_umask_and_exclusive(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'receipt.json'; previous = os.umask(0o022)
            try:
                private_json(path, {'helper_launches': 0})
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)
                update_receipt(path, {'helper_launches': 1})
                with self.assertRaises(FileExistsError):
                    private_json(path, {'helper_launches': 0})
                self.assertEqual(json.loads(path.read_text())['helper_launches'], 1)
            finally:
                os.umask(previous)

    def test_return_requires_desk_report_and_full_five_minutes(self):
        with tempfile.TemporaryDirectory() as folder:
            private = Path(folder)
            (private/'return-authorization.json').write_text(json.dumps({
                'owner_reported_at_desk': True, 'manual_return_requested': True,
                'candidate_sha256': device.CANDIDATE}))
            (private/'observation-receipt.json').write_text(json.dumps({
                'boot_departure_monotonic': 100, 'host_boot_id_private': 'same-boot'}))
            with patch.object(manual, 'inputs', return_value=(private,)), \
                    patch.object(manual, 'host_boot_id', return_value='same-boot'), \
                    patch.object(manual.time, 'monotonic', return_value=399), \
                    patch.object(manual, 'scan_ports') as scan, patch.object(manual, 'launch_helper') as launch:
                with self.assertRaisesRegex(ValueError, 'full observation'):
                    manual.return_once(private)
                scan.assert_not_called(); launch.assert_not_called()


class Evidence(unittest.TestCase):
    def setUp(self):
        self.nonce = bytes(range(32))
        self.image, self.prefix = mailbox.prepare(bytes(mailbox.PARTITION), self.nonce,
            b'VALETHON HOST CONTROL v1\nfixture only\n')

    def encoded(self, entry=0x40080000, dt=0x48000000, sequence=4):
        payload = record.TAG+record.BODY.pack(3,0,0,5,8,0,0,entry,dt,18432,0,0,0,
                                            bytes.fromhex(self.prefix),self.nonce)
        image = bytearray(self.image); at = mailbox.SLOT_BASE+mailbox.SLOT
        encoded = mailbox.header(sequence, self.nonce, payload)+payload
        image[at:at+len(encoded)] = encoded
        return bytes(image)

    def test_host_fixture_fails(self):
        self.assertFalse(assess_record(self.image,self.nonce,self.prefix)['loader_capture_criteria_passed'])

    def test_bound_original_handoff_passes_only_loader_criteria(self):
        result = assess_record(self.encoded(),self.nonce,self.prefix)
        self.assertTrue(result['loader_capture_criteria_passed'])
        self.assertFalse(result['kernel_logging_qualified'])
        self.assertFalse(result['kernel_entry_proved'])
        self.assertFalse(result['modern_kernel_admitted'])

    def test_wrong_entry_or_dt_or_early_sequence_fails(self):
        for values in ({'entry':0x40000000},{'dt':0x44000000},{'sequence':2}):
            with self.subTest(values=values):
                self.assertFalse(assess_record(self.encoded(**values),self.nonce,self.prefix)['loader_capture_criteria_passed'])

    def test_stale_nonce_and_changed_prefix_rejected(self):
        for nonce, prefix in ((bytes([7])*32,self.prefix),(self.nonce,'0'*64)):
            with self.assertRaises(ValueError):
                assess_record(self.encoded(),nonce,prefix)


if __name__ == '__main__':
    unittest.main()
