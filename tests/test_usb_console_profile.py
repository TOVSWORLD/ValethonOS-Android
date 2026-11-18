import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import run_usb_console_source_boot as wrapper
import run_native_source_boot as base
from verify_usb_console_build import ALLOWED,SERIAL_SHA
class Tests(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.p=Path(t.name)
  self.linked={'usb_console_linked':True,'serial_bind_is_opt_in':True,'serial_source_sha256':SERIAL_SHA,'usb_profile_config_changes':{k:{'before':'n','after':'y'} for k in ALLOWED},'artifacts':{'.config':{'sha256':'a'*64},'arch/arm64/boot/Image':{'sha256':'b'*64}}}
  self.report={'resolved_config_sha256':'a'*64,'image_sha256':'b'*64,'serial_bind_is_opt_in':True}
 def test_exact_profile_temporarily_scopes_proven_runner(self):
  old=(base.SCOPE,base.NATIVE_CONFIG)
  def called(*args):
   self.assertEqual(base.SCOPE,wrapper.SCOPE);self.assertEqual(base.NATIVE_CONFIG,'a'*64);return {'complete':True}
  with patch.object(base,'run',side_effect=called):self.assertTrue(wrapper.run(None,'/lab',self.report,self.linked,self.p)['complete'])
  self.assertEqual((base.SCOPE,base.NATIVE_CONFIG),old)
 def test_scope_restored_on_failure(self):
  old=(base.SCOPE,base.NATIVE_CONFIG)
  with patch.object(base,'run',side_effect=RuntimeError):
   with self.assertRaises(RuntimeError):wrapper.run(None,'/lab',self.report,self.linked,self.p)
  self.assertEqual((base.SCOPE,base.NATIVE_CONFIG),old)
 def test_extra_configuration_change_refused_before_device(self):
  self.linked['usb_profile_config_changes']['CONFIG_SECURITY_SELINUX']={'before':'y','after':'n'}
  with patch.object(base,'run') as call:
   with self.assertRaises(ValueError):wrapper.run(None,'/lab',self.report,self.linked,self.p)
   call.assert_not_called()
 def test_wrong_image_refused(self):
  self.report['image_sha256']='c'*64
  with self.assertRaises(ValueError):wrapper.run(None,'/lab',self.report,self.linked,self.p)
 def test_unbound_wrapper_approval_refused_before_device(self):
  a=self.p/'auth';a.write_text('{}')
  with patch.object(base,'run') as call:
   with self.assertRaises(ValueError):wrapper.run(None,'/lab',self.report,self.linked,self.p,a)
   call.assert_not_called()
