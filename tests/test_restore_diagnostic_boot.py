import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import restore_diagnostic_boot as rollback

BACKUP = b'ANDROID!' + bytes(rollback.BOOT_BYTES - 8)
TRIAL = b'ANDROID!' + b'x' * (rollback.BOOT_BYTES - 8)
RECOVERY = b'ANDROID!' + bytes(rollback.RECOVERY_BYTES - 8)
MANIFEST = {'boot': {'bytes': len(BACKUP), 'sha256': rollback.sha(BACKUP)},
            'recovery': {'bytes': len(RECOVERY), 'sha256': rollback.sha(RECOVERY)}}


class FakeAdb:
    def __init__(self):
        self.boot = TRIAL
        self.recovery = RECOVERY
        self.writes = 0
        self.calls = []
        self.fail_write = False
        self.bad_write = False
        self.alias = None
        self.staged = {}
        self.bad_ram = False

    def run(self, args, data=None):
        self.calls.append(args)
        if args == ['get-state']:
            return b'recovery\n'
        if args[:2] == ['shell', 'getprop']:
            return {'ro.product.device': b'douglas', 'ro.twrp.version': b'3.3.1-0'}[args[2]]
        if args[:2] == ['shell', 'readlink']:
            if self.alias:
                return self.alias
            return (rollback.BOOT if args[2].split('/')[-1].startswith('boot') else rollback.RECOVERY).encode()
        if args[:2] == ['exec-out', 'readlink']:
            return b'/tmp\n'
        if args == ['exec-out', 'cat', '/proc/mounts']:
            return b'tmpfs /tmp tmpfs rw,seclabel 0 0\n'
        if args[:2] in [['exec-out', 'mkdir'], ['exec-out', 'rm'], ['exec-out', 'rmdir']]:
            return b''
        if args[:2] == ['exec-out', 'dd']:
            self.writes += 1
            if self.fail_write:
                raise ValueError('Interrupted write')
            if not self.bad_write:
                self.boot = self.staged[args[2][3:]]
            return b''
        if args == ['exec-out', 'sync']:
            return b''
        if args[0] == 'shell' and args[1].startswith('if [ -e /tmp/valethonos-rollback-'):
            return b'RAM_CLEAN'
        raise AssertionError(args)

    def read(self, node, size):
        if node in self.staged:
            return b'x' * size if self.bad_ram else self.staged[node]
        return self.boot if node == rollback.BOOT else self.recovery

    def push(self, data, destination):
        self.staged[destination] = data


class RollbackTests(unittest.TestCase):
    def test_preflight_is_read_only(self):
        adb = FakeAdb()
        rollback.preflight(adb, BACKUP, MANIFEST, rollback.sha(TRIAL))
        self.assertEqual(adb.writes, 0)

    def test_refusals_happen_before_write_or_receipt(self):
        for change in ['alias', 'recovery', 'current', 'backup']:
            with self.subTest(change=change), tempfile.TemporaryDirectory() as temp:
                adb = FakeAdb()
                image = BACKUP
                if change == 'alias': adb.alias = b'/dev/block/mmcblk0p16'
                if change == 'recovery': adb.recovery = b'x' * len(RECOVERY)
                if change == 'current': adb.boot = BACKUP
                if change == 'backup': image = BACKUP[:-1]
                receipt = Path(temp) / 'receipt.json'
                with self.assertRaises(ValueError):
                    rollback.restore(adb, image, MANIFEST, rollback.sha(TRIAL), receipt)
                self.assertEqual(adb.writes, 0)
                self.assertFalse(receipt.exists())

    def test_exact_restore_and_no_reboot(self):
        with tempfile.TemporaryDirectory() as temp:
            adb = FakeAdb()
            receipt = rollback.restore(adb, BACKUP, MANIFEST, rollback.sha(TRIAL), Path(temp) / 'receipt')
            self.assertTrue(receipt['verified'])
            self.assertEqual(adb.writes, 1)
            self.assertFalse(any('reboot' in str(call) for call in adb.calls))

    def test_interrupted_or_incorrect_write_stops_without_retry(self):
        for kind in ['fail_write', 'bad_write']:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                adb = FakeAdb()
                setattr(adb, kind, True)
                path = Path(temp) / 'receipt'
                with self.assertRaises(ValueError):
                    rollback.restore(adb, BACKUP, MANIFEST, rollback.sha(TRIAL), path)
                self.assertEqual(adb.writes, 1)
                receipt = json.loads(path.read_text())
                self.assertTrue(receipt['write_started'])
                self.assertFalse(receipt['verified'])

    def test_existing_receipt_refuses_before_write(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'receipt'
            path.write_text('preserve')
            adb = FakeAdb()
            with self.assertRaises(FileExistsError):
                rollback.restore(adb, BACKUP, MANIFEST, rollback.sha(TRIAL), path)
            self.assertEqual(adb.writes, 0)
            self.assertEqual(path.read_text(), 'preserve')

    def test_corrupt_ram_upload_never_writes_boot(self):
        with tempfile.TemporaryDirectory() as temp:
            adb = FakeAdb()
            adb.bad_ram = True
            with self.assertRaises(ValueError):
                rollback.restore(adb, BACKUP, MANIFEST, rollback.sha(TRIAL), Path(temp) / 'receipt')
            self.assertEqual(adb.writes, 0)

    def test_already_restored_verifies_without_write(self):
        with tempfile.TemporaryDirectory() as temp:
            adb = FakeAdb()
            adb.boot = BACKUP
            result = rollback.restore(adb, BACKUP, MANIFEST, rollback.sha(BACKUP), Path(temp) / 'receipt')
            self.assertTrue(result['verified'])
            self.assertFalse(result['write_started'])
            self.assertEqual(adb.writes, 0)


if __name__ == '__main__':
    unittest.main()
