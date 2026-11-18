import ctypes,hashlib,json,shutil,struct,subprocess,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import run_ack_native_trial as trial
from verify_ack_combined_bundle import assess
from build_ack_kernel_hooks import STAGES,line,branch,adrp
from build_ack_combined_entry import integrity_marker
from validate_ack_combined_vm import reserve
ROOT=Path(__file__).resolve().parents[1]

class CombinedWitness(unittest.TestCase):
 def setUp(self):self.token='c'*32;self.chain=integrity_marker(self.token,True)+b''.join(line(self.token,s) for s in STAGES)
 def test_full_chain_and_wrong_identity(self):
  self.assertTrue(assess(self.chain,self.token)['linux_c_entry_proven'])
  self.assertFalse(assess(self.chain,'b'*32)['linux_c_entry_proven'])
 def test_loss_reorder_duplicate_and_negative_markers_do_not_pass(self):
  for data in [self.chain.replace(line(self.token,'after_mmu'),b''),self.chain+line(self.token,'start_kernel'),b''.join(reversed(self.chain.splitlines(keepends=True))),self.chain+integrity_marker(self.token,False),self.chain+line(self.token,'map_refused')]:
   self.assertFalse(assess(data,self.token)['linux_c_entry_proven'])
 def test_relocated_branch_and_adrp_preserve_target(self):
  self.assertEqual(branch(0x4000,0x3000),0x17fffc00)
  self.assertEqual(branch(0x4000,0x5000,True),0x94000400)
  self.assertEqual(adrp(0x90000001,0x40000000,0x40001000),0xf0ffffe1)
  for at,to in [(0,2),(0,1<<27),(1<<27,0-4)]:
   with self.assertRaises(ValueError):branch(at,to)
 def test_vm_reservation_trims_capacity_and_preserves_structure(self):
  st=struct.pack('>I',1)+bytes(4)+struct.pack('>II',2,9)
  header=struct.pack('>10I',0xd00dfeed,1024*1024,56,56+len(st),40,17,16,0,0,len(st))
  original=header+bytes(16)+st;original+=bytes(1024*1024-len(original))
  changed=reserve(original);h=struct.unpack_from('>10I',changed)
  self.assertLess(len(changed),200);self.assertEqual(h[1],len(changed));self.assertEqual(changed[h[2]:h[2]+h[9]],st)
  self.assertEqual(struct.unpack_from('>QQQQQQ',changed,40),(0x42000000,0x28000,0x444bf000,65536,0,0))

class CombinedController(unittest.TestCase):
 def test_old_scope_cannot_authorize_combined_trial(self):
  a=SimpleNamespace(policy=Path('unused'),combined=True)
  with patch.object(trial,'read',return_value={'scope':trial.SCOPE_TWO_STAGE,'target_kind':'ack-linux-v1'}):
   with self.assertRaisesRegex(ValueError,'policy required'):trial.validate(a)
 def test_combined_scope_cannot_authorize_old_trial(self):
  a=SimpleNamespace(policy=Path('unused'),combined=False)
  with patch.object(trial,'read',return_value={'scope':'ack-linux-combined-two-stage-2','target_kind':'ack-linux-combined-v2'}):
   with self.assertRaisesRegex(ValueError,'policy required'):trial.validate(a)

@unittest.skipUnless(shutil.which('clang'),'C compiler required')
class FullImageSHA(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();p=Path(cls.temp.name)/'sha.so'
  subprocess.run(['clang','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror',str(ROOT/'projects/firetabs-android/native-kexec/combined_sha256.c'),'-o',str(p)],check=True)
  cls.lib=ctypes.CDLL(str(p));cls.fn=cls.lib.combined_verify;cls.fn.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p];cls.fn.restype=ctypes.c_int
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def test_vectors_padding_boundaries_and_whole_image_extent(self):
  for n in [0,1,3,55,56,63,64,65,127,128,129,4096,28049408]:
   b=(bytes(range(256))*((n+255)//256))[:n];expected=hashlib.sha256(b).digest()
   self.assertEqual(self.fn(b,n,expected),0,n)
   self.assertEqual(self.fn(b,n,bytes([expected[0]^1])+expected[1:]),1,n)
 def test_out_of_policy_length_refuses_before_read(self):self.assertEqual(self.fn(None,32*1024*1024+1,None),2)
if __name__=='__main__':unittest.main()
