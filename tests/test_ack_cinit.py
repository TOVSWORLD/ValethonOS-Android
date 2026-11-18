import sys,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_ack_cinit_console import prefix
from verify_ack_cinit_bundle import assess
import run_ack_native_trial as trial

class CinitIdentity(unittest.TestCase):
 def setUp(self):self.nonce=bytes(range(32))
 def test_fresh_last_records_attribute_progress_and_errors(self):
  data=prefix(self.nonce.hex())+b'Run /init as init process\nKernel panic: test\n'
  r=assess(data,self.nonce)
  self.assertTrue(r['fresh_console_identity']);self.assertTrue(r['run_init_seen']);self.assertTrue(r['panic_seen'])
  self.assertFalse(r['linux_banner_seen'])
  self.assertFalse(assess(data,bytes(32))['run_init_seen'])
 def test_unattributed_errors_are_not_current_boot_evidence(self):
  r=assess(b'Run /init as init process\nKernel panic\nInternal error:',self.nonce)
  for key in ['fresh_console_identity','run_init_seen','panic_seen','exception_seen']:self.assertFalse(r[key])
 def test_only_exact_full_identity_admitted(self):
  for value in ['a'*32,'A'*64,'z'*64,'a'*63+'\n']:
   with self.assertRaises(ValueError):prefix(value)
 def test_consumed_combined_scope_cannot_authorize_cinit(self):
  a=SimpleNamespace(policy=Path('unused'),cinit=True,combined=False)
  with patch.object(trial,'read',return_value={'scope':'ack-linux-combined-two-stage-2','target_kind':'ack-linux-combined-v2'}):
   with self.assertRaisesRegex(ValueError,'policy required'):trial.validate(a)
 def test_cinit_scope_cannot_authorize_combined(self):
  a=SimpleNamespace(policy=Path('unused'),cinit=False,combined=True)
  with patch.object(trial,'read',return_value={'scope':'ack-linux-cinit-two-stage-3','target_kind':'ack-linux-cinit-v3'}):
   with self.assertRaisesRegex(ValueError,'policy required'):trial.validate(a)
if __name__=='__main__':unittest.main()
