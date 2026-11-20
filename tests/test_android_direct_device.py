import hashlib,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import android_direct_device as d
class AndroidInstallSafety(unittest.TestCase):
 def test_chunk_plan_covers_exact_partition_without_overrun(self):
  plan=d.chunks(d.SYSTEM_BYTES)
  self.assertEqual(sum(n for _,n in plan),d.SYSTEM_BYTES)
  self.assertEqual(plan[0][0],0);self.assertEqual(plan[-1][0]+plan[-1][1],d.SYSTEM_BYTES)
  self.assertTrue(all(at%4096==0 and n%4096==0 and 0<n<=d.CHUNK for at,n in plan))
  with self.assertRaises(ValueError):d.chunks(d.SYSTEM_BYTES+4096)
 def test_unapproved_install_stops_before_device_calls(self):
  with tempfile.TemporaryDirectory() as folder:
   case=Path(folder);(case/'owner-authorization-private.json').write_text('{}');(case/'case-manifest-private.json').write_text('{}')
   m={'files':{'boot':{'sha256':'a'*64},'system':{'sha256':'b'*64},'original_system':{'sha256':'c'*64}},'nonce_sha256':'d'*64}
   adb=unittest.mock.Mock()
   with patch.object(d,'inputs',return_value=m),self.assertRaisesRegex(ValueError,'authorization'):d.run(case,adb,'install')
   adb.assert_not_called();self.assertEqual(adb.mock_calls,[])
 def test_failed_system_verification_never_writes_boot(self):
  with tempfile.TemporaryDirectory() as folder:
   case=Path(folder);m={'expected_boot_before_sha256':'a'*64,'files':{'original_system':{'sha256':'b'*64},'boot':{'sha256':'c'*64},'system':{'sha256':'d'*64}}}
   with patch.object(d,'inputs',return_value=m),patch.object(d,'authorization'),patch.object(d,'preflight'),patch.object(d,'write_system',side_effect=ValueError('readback mismatch')),patch.object(d,'restore') as boot:
    with self.assertRaisesRegex(ValueError,'readback'):d.run(case,unittest.mock.Mock(),'install')
    boot.assert_not_called()
 def test_bad_ram_chunk_digest_prevents_partition_write(self):
  class Adb:
   def __init__(self):self.calls=[]
   def run(self,args):
    self.calls.append(args)
    if args==['exec-out','cat','/proc/mounts']:return b'tmpfs /tmp tmpfs rw 0 0\n'
    if args==['exec-out','readlink','-f','/tmp']:return b'/tmp\n'
    return b''
   def push(self,*args):pass
   def digest(self,*args):return '0'*64
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);image=root/'image';image.write_bytes(b'x'*4096);p=root/'receipt';log={};d.receipt(p,log);adb=Adb()
   with patch.object(d,'chunks',return_value=[(0,4096)]),self.assertRaisesRegex(ValueError,'RAM chunk'):d.write_system(adb,image,'a'*64,log,p)
   self.assertFalse(any('dd' in args for args in adb.calls))

 def test_cli_selector_must_be_the_case_bound_file(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);case=root/'case';case.mkdir();selected=case/'selector-private.json';selected.write_text(json.dumps({'selector':'test-only-selector'}))
   self.assertEqual(d.load_selector(case,selected),'test-only-selector')
   other=root/'other.json';other.write_text(selected.read_text())
   with self.assertRaisesRegex(ValueError,'case-bound'):d.load_selector(case,other)
   selected.unlink();selected.symlink_to(other)
   with self.assertRaisesRegex(ValueError,'case-bound'):d.load_selector(case,selected)
