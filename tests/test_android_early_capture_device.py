import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import android_early_capture_device as d
class DiagnosticDevice(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.p=Path(self.tmp.name);(self.p/'boot-full.img').write_bytes(b'candidate')
  self.m={'files':{'boot':{'bytes':9,'sha256':d.sha(b'candidate')}},'expected_boot_before_sha256':'previous'}
  self.adb=Mock()
 def patched(self):
  for name,value in [('inputs',self.m),('authorization',{}),('preflight','previous'),('check_system',None)]:
   p=patch.object(d,name,return_value=value);p.start();self.addCleanup(p.stop)
 def test_preflight_never_writes(self):
  self.patched()
  with patch.object(d,'restore') as writer:
   self.assertEqual(d.run(self.p,self.adb,'preflight'),{'passed':True,'written':False});writer.assert_not_called();self.adb.run.assert_not_called()
 def test_boot_requires_owned_verified_install(self):
  self.patched();(self.p/'install-receipt-private.json').write_text(json.dumps({'verified':False}))
  with self.assertRaisesRegex(ValueError,'Owned verified'):d.run(self.p,self.adb,'boot')
  self.adb.run.assert_not_called()
 def test_boot_request_is_one_shot_even_after_transport_uncertainty(self):
  self.patched();(self.p/'install-receipt-private.json').write_text(json.dumps({'verified':True,'rollback_sha256':d.sha(b'candidate')}));self.adb.run.side_effect=TimeoutError
  with self.assertRaises(TimeoutError):d.run(self.p,self.adb,'boot')
  with self.assertRaises(FileExistsError):d.run(self.p,self.adb,'boot')
  self.assertEqual(self.adb.run.call_count,1)
 def test_changed_system_stops_before_boot_write(self):
  self.patched()
  with patch.object(d,'check_system',side_effect=ValueError('changed system')),patch.object(d,'restore') as writer:
   with self.assertRaisesRegex(ValueError,'changed system'):d.run(self.p,self.adb,'install')
   writer.assert_not_called()
 def test_receiver_rejects_unscoped_profile(self):
  from capture_android_early_console import capture
  with self.assertRaisesRegex(ValueError,'Exact selected'):capture({},self.p/'capture')
  self.assertFalse((self.p/'capture').exists())
