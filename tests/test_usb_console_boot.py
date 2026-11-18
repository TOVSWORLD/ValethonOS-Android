import hashlib,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import pack_usb_console_boot as usb
from pack_native_kexec_boot import assemble
from test_native_kexec_boot import original,image,linked
from capture_usb_kernel_console import expected_marker
class Tests(unittest.TestCase):
 def setUp(self):
  self.old=original();self.image=image(b'usb-console');self.link=linked(self.image);self.link.update(usb_console_linked=True,serial_bind_is_opt_in=True,serial_source_sha256=usb.SERIAL_SHA,usb_profile_config_changes={k:{'before':'n','after':'y'} for k in usb.ALLOWED});self.link['artifacts']['.config']['sha256']='c'*64
 def test_explicit_profile_keeps_original_header_and_reports_actual_config(self):
  def pack(o,i,r,**kw):return assemble(o,i,r,expected_original=hashlib.sha256(self.old).hexdigest(),**kw)
  with patch.object(usb,'assemble',side_effect=pack):candidate,r=usb.pack(self.old,self.image,self.link)
  self.assertEqual(r['resolved_config_sha256'],'c'*64);self.assertTrue(r['source_ramdisk_and_cmdline_unchanged']);self.assertEqual(candidate[64:576],self.old[64:576]);self.assertFalse(r['console_capture_at_boot_qualified'])
 def test_wrong_source_profile_refused_before_pack(self):
  self.link['serial_source_sha256']='a'*64
  with patch.object(usb,'assemble') as pack:
   with self.assertRaises(ValueError):usb.pack(self.old,self.image,self.link)
   pack.assert_not_called()
 def test_security_change_not_hidden_in_profile(self):
  self.link['usb_profile_config_changes']['CONFIG_SECURITY_SELINUX']={'before':'y','after':'n'}
  with self.assertRaises(ValueError):usb.pack(self.old,self.image,self.link)
 def test_console_target_marker_exact_nonce(self):
  self.assertIn(b'0'*32,expected_marker('0'*32))
  for value in ['0'*31,'0'*33,'g'*32,'0'*31+'\n']:
   with self.assertRaises(ValueError):expected_marker(value)
