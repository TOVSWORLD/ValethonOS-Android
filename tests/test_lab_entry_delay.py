from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import apply_lab_entry_screen as old
import apply_lab_entry_delay as new

class EarliestEntry(unittest.TestCase):
    def test_exact_first_call_patch_revision_drift_and_reapplication(self):
        lock=new.contract()
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder);p=source/'arch/arm64/kernel/head.S';p.parent.mkdir(parents=True)
            p.write_bytes((ROOT/old.contract()['source']).read_bytes())
            old.apply(source,lock['ack_commit'])
            before=p.read_bytes()
            with self.assertRaises(ValueError):new.apply(source,'wrong')
            self.assertEqual(p.read_bytes(),before)
            new.apply(source,lock['ack_commit'])
            self.assertIn('SYM_CODE_START(primary_entry)\n\tbl\tvalethon_entry_delay\n\tbl\trecord_mmu_state',p.read_text())
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),lock['patched_sha256'])
            with self.assertRaises(ValueError):new.apply(source,lock['ack_commit'])
    def test_wait_does_not_claim_watchdog_control_or_relax_retained_security(self):
        source=(new.PORT/'entry-delay.S').read_text()
        self.assertNotIn('0x10007000',source);self.assertNotIn('wdt',source.lower())
        self.assertNotIn('msr ',source);self.assertIn('cntpct_el0',source)
        self.assertIn('mov x16, #0x80000000',source)
        self.assertIn('.quad 8',source)
        self.assertNotIn('x21,',source)
