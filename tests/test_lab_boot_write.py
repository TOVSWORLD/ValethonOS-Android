from pathlib import Path
import json
import tempfile
import unittest
from test_restore_diagnostic_boot import FakeAdb, BACKUP, TRIAL, MANIFEST
import restore_diagnostic_boot as boot
from write_lab_boot_candidate import candidate_manifest


class CandidateWrite(unittest.TestCase):
    def report(self):
        return {'partition_sha256': boot.sha(TRIAL), 'partition_bytes': len(TRIAL),
                'scope': 'Offline first normal log-bringup candidate; review still required',
                'physical_execution_admitted': False, 'failed_load_qualified': False,
                'recovery_partition_written': False}

    def test_single_candidate_write_and_rollback_with_same_guarded_transport(self):
        adb = FakeAdb()
        adb.boot = BACKUP
        manifest = candidate_manifest(TRIAL, self.report(), BACKUP, MANIFEST)
        with tempfile.TemporaryDirectory() as d:
            installed = boot.restore(adb, TRIAL, manifest, boot.sha(BACKUP), Path(d) / 'install',
                                     operation='install reviewed first normal logging candidate')
            self.assertEqual(installed['operation'], 'install reviewed first normal logging candidate')
            self.assertTrue(installed['verified'])
            self.assertEqual(adb.writes, 1)
            restored = boot.restore(adb, BACKUP, MANIFEST, boot.sha(TRIAL), Path(d) / 'restore')
            self.assertTrue(restored['verified'])
            self.assertEqual(adb.writes, 2)
            self.assertEqual(adb.boot, BACKUP)
            self.assertFalse(any('reboot' in str(c) for c in adb.calls))
            self.assertFalse(any('of=' + boot.RECOVERY in c for c in adb.calls))

    def test_report_hash_and_acceptance_mutations_rejected(self):
        for key, value in [('partition_sha256', '0' * 64), ('partition_bytes', 1),
                           ('physical_execution_admitted', True), ('failed_load_qualified', True),
                           ('recovery_partition_written', True)]:
            with self.assertRaises(ValueError):
                candidate_manifest(TRIAL, {**self.report(), key: value}, BACKUP, MANIFEST)
