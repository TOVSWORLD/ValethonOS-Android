"""Selected cached firmware metadata only; no hardware identity acceptance."""
import ctypes as c,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
READ=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint,c.POINTER(c.c_ubyte),c.c_uint)
class Reader(c.Structure):_fields_=[('context',c.c_void_p),('read',READ)]
class Plan(c.Structure):_fields_=[(n,c.c_uint) for n in ['device','card','host','block']]
class Binding(c.Structure):_fields_=[(n,c.c_uint) for n in ['device','card','host','block','rca','size','enabled']]
class Identity(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();p=Path(cls.temp.name)/'identity.so';subprocess.run(['cc','-shared','-fPIC','-O2',str(ROOT/'projects/firetabs-android/loader-retained/identity.c'),'-o',str(p)],check=True);cls.lib=c.CDLL(str(p));cls.lib.li_capture.argtypes=[c.POINTER(Binding),c.POINTER(Plan),c.POINTER(Reader)]
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def run_case(self,change=None,fail=False,unstable=False,plan=None):
  p=plan or Plan(0x1000,0x2000,0x3000,0x4000);fields={(0x1004,4):0,(0x1008,4):0x4000,(0x2000,4):0x3000,(0x3028,4):0x11230000,(0x2018,4):1,(0x201c,4):1,(0x210c,1):8,(0x206d,1):1,(0x2145,4):1024};calls=[]
  if change:fields.update(change)
  def read(_,addr,buf,n):
   calls.append((addr,n))
   if fail or (addr,n) not in fields:return -1
   v=fields[addr,n]+(1 if unstable and len(calls)>9 and addr==0x2018 else 0)
   for i in range(n):buf[i]=(v>>(i*8))&255
   return 0
  cb=READ(read);out=Binding(*([99]*7));result=self.lib.li_capture(c.byref(out),c.byref(p),c.byref(Reader(None,cb)));return result,out,calls
 def test_stable_exact_fields_and_no_identifier_reads(self):
  r,b,calls=self.run_case();self.assertEqual(r,0);self.assertEqual((b.rca,b.size,b.enabled),(1,1024,1));self.assertEqual(len(calls),18);self.assertEqual(calls[:9],calls[9:])
 def test_mismatched_device_host_card_rejected_without_output(self):
  for f,v in [((0x1004,4),1),((0x1008,4),0),((0x2000,4),0x5000),((0x3028,4),0),((0x2018,4),0),((0x2018,4),65536),((0x201c,4),0),((0x210c,1),5),((0x210c,1),9),((0x206d,1),2),((0x2145,4),0)]:
   r,b,_=self.run_case({f:v});self.assertLess(r,0);self.assertEqual(bytes(b),bytes(c.sizeof(b)))
 def test_failed_or_unstable_read_never_publishes(self):
  for kwargs in [{'fail':True},{'unstable':True}]:
   r,b,_=self.run_case(**kwargs);self.assertLess(r,0);self.assertEqual(bytes(b),bytes(c.sizeof(b)))
 def test_cache_disabled_is_reported_without_claiming_flush_admission(self):
  r,b,_=self.run_case({(0x206d,1):0});self.assertEqual(r,0);self.assertEqual(b.enabled,0)
 def test_unaligned_or_overflowing_plan(self):
  for p in [Plan(0x1001,0x2000,0x3000,0x4000),Plan(0xfffffffc,0x2000,0x3000,0x4000)]:
   r,b,_=self.run_case(plan=p);self.assertLess(r,0);self.assertEqual(bytes(b),bytes(c.sizeof(b)))
if __name__=='__main__':unittest.main()
