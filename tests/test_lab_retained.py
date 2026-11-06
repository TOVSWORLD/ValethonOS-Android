import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import apply_lab_retained as apply
import lab_log_config
from select_kernel_build_scope import choose
class RetainedSource(unittest.TestCase):
    def test_source_revision_makefile_and_reapplication_guards(self):
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder);p=source/'drivers/misc/Makefile';p.parent.mkdir(parents=True);before=(ROOT/'evidence/independent-recovery/retained-log-source/Makefile').read_bytes();p.write_bytes(before)
            with self.assertRaises(ValueError):apply.apply(source,'wrong')
            p.write_bytes(before+b'changed')
            with self.assertRaises(ValueError):apply.apply(source,apply.ACK)
            p.write_bytes(before);result=apply.apply(source,apply.ACK)
            self.assertFalse(result['device_written']);self.assertTrue((p.parent/'valethon_mailbox.c').is_file())
            with self.assertRaises(ValueError):apply.apply(source,apply.ACK)
    def test_retained_explicit_scope_preserves_old_storage_denial_and_security(self):
        normal=lab_log_config.requirements();retained=lab_log_config.requirements(True)
        self.assertEqual(normal['BLOCK'],'n');self.assertEqual(retained['BLOCK'],'y')
        for n in ['MMC','MMC_BLOCK','MMC_MTK','REGULATOR_MT6323','EFI_PARTITION']:self.assertEqual(retained[n],'y')
        for n in ['SECURITY_SELINUX','SECURITY_SELINUX_BOOTPARAM','SECURITY_SELINUX_DEVELOP','LSM']:self.assertEqual(normal[n],retained[n])
        self.assertEqual(choose('workflow_dispatch',mode='lab-retained')['mode'],'lab-retained')
        with self.assertRaises(ValueError):choose('workflow_dispatch',mode='lab-retained',emulated_boot=True)
