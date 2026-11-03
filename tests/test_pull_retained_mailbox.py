from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import retained_log_mailbox as m
import pull_retained_mailbox as pull
import restore_diagnostic_boot as r
from test_restore_diagnostic_boot import FakeAdb,BACKUP,RECOVERY,MANIFEST

class PullMailbox(unittest.TestCase):
    def test_restore_hash_derived_only_after_prefix_seed_and_recovery_checks(self):
        nonce=bytes(range(32));candidate,sha=m.prepare(BACKUP,nonce)
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);disk=p/'fixture';disk.write_bytes(candidate)
            m.write_fixture(disk,nonce,sha,b'attributable prior kernel log\n')
            adb=FakeAdb();adb.boot=disk.read_bytes()
            report=pull.collect(adb,BACKUP,MANIFEST,candidate,nonce,p/'capture')
            self.assertTrue(report['attributable_record']);self.assertEqual(report['current_boot_sha256'],r.sha(adb.boot))
            self.assertEqual((p/'capture/record-private.bin').read_bytes(),b'attributable prior kernel log\n')
            self.assertEqual(adb.writes,0)
            self.assertFalse(any('reboot' in call for call in adb.calls))
    def test_wrong_alias_recovery_prefix_or_seed_never_produces_restore_hash(self):
        nonce=bytes(range(32));candidate,_=m.prepare(BACKUP,nonce)
        for mode in ['alias','recovery','prefix','seed']:
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as folder:
                adb=FakeAdb();adb.boot=candidate
                if mode=='alias':adb.alias=b'/dev/block/mmcblk0p6'
                if mode=='recovery':adb.recovery=b'x'*len(RECOVERY)
                if mode in ['prefix','seed']:
                    b=bytearray(candidate);b[12 if mode=='prefix' else m.BASE+10]^=1;adb.boot=bytes(b)
                output=Path(folder)/'capture'
                with self.assertRaises(ValueError):pull.collect(adb,BACKUP,MANIFEST,candidate,nonce,output)
                self.assertFalse(output.exists());self.assertEqual(adb.writes,0)

    def test_mutated_log_tail_can_restore_original_only_with_validated_readout(self):
        import restore_retained_trial as restore
        nonce=bytes(range(32));candidate,prefix=m.prepare(BACKUP,nonce,b'VALETHON HOST CONTROL v1\nfixture\n')
        candidate_report={'partition_sha256':r.sha(candidate),'partition_bytes':r.BOOT_BYTES,'scope':'Offline first normal log-bringup candidate; review still required','physical_execution_admitted':False,'failed_load_qualified':False,'recovery_partition_written':False}
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);image=p/'fixture';image.write_bytes(candidate)
            m.write_fixture(image,nonce,prefix,b'VALETHON RETAINED KERNEL LOG v1 release=test\nprintk\n')
            adb=FakeAdb();adb.boot=image.read_bytes()
            pull.collect(adb,BACKUP,MANIFEST,candidate,nonce,p/'readout')
            before=adb.boot
            result=restore.run(adb,BACKUP,MANIFEST,candidate,candidate_report,nonce,p/'readout')
            self.assertEqual(adb.writes,0);self.assertEqual(adb.boot,before);self.assertFalse(result['device_written'])
            result=restore.run(adb,BACKUP,MANIFEST,candidate,candidate_report,nonce,p/'readout',p/'restore.json',True)
            self.assertTrue(result['verified']);self.assertEqual(adb.writes,1);self.assertEqual(adb.boot,BACKUP);self.assertEqual(adb.recovery,RECOVERY)
            # Reusing the stored expected-current digest cannot rewrite restored boot.
            with self.assertRaises(ValueError):restore.run(adb,BACKUP,MANIFEST,candidate,candidate_report,nonce,p/'readout',p/'second.json',True)
            self.assertEqual(adb.writes,1)
