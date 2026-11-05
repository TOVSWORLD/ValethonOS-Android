"""Actual RAM bridge with owned allocation and modeled readonly storage/cache."""
import ctypes as c,hashlib,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Plan(c.Structure):_fields_=[('code',c.c_uint),('state',c.c_uint),('stack',c.c_uint),('start',c.c_uint),('emit',c.c_uint),('bindings',c.c_uint),('sha',c.c_ubyte*32),('first',c.c_ulonglong),('offset',c.c_ulonglong)]
READ=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_ulonglong,c.c_void_p,c.c_uint);ALLOC=c.CFUNCTYPE(c.c_void_p,c.c_uint,c.c_uint);SHA=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_void_p,c.c_uint,c.c_void_p);CACHE=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_void_p,c.c_uint)
class IO(c.Structure):_fields_=[('context',c.c_void_p),('read',READ),('allocate',ALLOC),('sha',SHA),('cache',CACHE)]
class Result(c.Structure):_fields_=[('attempted',c.c_uint),('loaded',c.c_uint),('code',c.c_void_p),('state',c.c_void_p),('stack',c.c_void_p),('start',c.c_void_p),('emit',c.c_void_p),('bytes',c.c_uint)]
class Fixture:
 def __init__(self,lib,failure=None):
  self.lib=lib;self.failure=failure;self.blob=bytes(range(256))*18;self.events=[];self.error=None;self.raw=c.create_string_buffer(32768);self.address=(c.addressof(self.raw)+31)&~15;self.plan=Plan(len(self.blob),8584,4096,1,17,1,(c.c_ubyte*32).from_buffer_copy(hashlib.sha256(self.blob).digest()),8192,12*1024*1024);self.result=Result()
  def allocate(alignment,n):
   self.events.append(('allocate',alignment,n));self.size=n
   if failure=='allocation':return 0
   if alignment!=16 or n>24576:self.error='bad allocation';return 0
   c.memset(self.address,0xa5,n)
   return self.address+1 if failure=='alignment' else self.address
  def read(_,offset,out,n):
   self.events.append(('read',offset,n))
   if failure=='read':return -1
   if offset!=self.plan.first*512+self.plan.offset or out!=self.address or n!=len(self.blob):self.error='wrong read';return -1
   c.memmove(out,self.blob,n);return 0
  def sha(_,at,n,expected):
   self.events.append(('sha',n));return -1 if failure=='sha' or hashlib.sha256(c.string_at(at,n)).digest()!=c.string_at(expected,32) else 0
  def cache(_,at,n):
   self.events.append(('cache',n));return -1 if failure=='cache' else 0
  self.callbacks=(READ(read),ALLOC(allocate),SHA(sha),CACHE(cache));self.io=IO(None,*self.callbacks)
 def load(self):return self.lib.lb_load(c.byref(self.result),c.byref(self.plan),c.byref(self.io))
class LoaderBridge(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();out=Path(cls.temp.name)/'bridge.so';cc=shutil.which('clang') or shutil.which('cc')
  if not cc:raise unittest.SkipTest('C compiler unavailable')
  subprocess.run([cc,'-shared','-fPIC','-O2',str(ROOT/'projects/firetabs-android/loader-retained/bridge.c'),'-o',str(out)],check=True,capture_output=True);cls.lib=c.CDLL(str(out));cls.lib.lb_load.argtypes=[c.POINTER(Result),c.POINTER(Plan),c.POINTER(IO)]
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def test_verified_load_publishes_owned_entries_and_zeroed_state_stack(self):
  f=Fixture(self.lib);self.assertEqual(f.load(),0);r=f.result;self.assertTrue(r.loaded);self.assertEqual(r.code,f.address);self.assertEqual(r.state,f.address+4608);self.assertEqual(r.stack,f.address+r.bytes);self.assertEqual((r.start,r.emit),(f.address+1,f.address+17));self.assertEqual(c.string_at(r.code,4608),f.blob);self.assertEqual(c.string_at(r.state,r.bytes-4608),bytes(r.bytes-4608));self.assertEqual([e[0] for e in f.events],['allocate','read','sha','cache']);self.assertIsNone(f.error)
 def test_invalid_plan_prevents_all_callbacks(self):
  for key,value in [('code',0),('code',8193),('code',513),('state',0),('state',12289),('stack',8192),('start',0),('start',8193),('emit',2),('bindings',0),('first',0),('first',2**64-1),('offset',0),('offset',12*1024*1024+1),('offset',15*1024*1024)]:
   f=Fixture(self.lib);setattr(f.plan,key,value);self.assertLess(f.load(),0);self.assertEqual(f.events,[]);self.assertFalse(f.result.loaded)
 def test_each_failure_publishes_no_entries_and_never_retries(self):
  for failure,events in [('allocation',1),('alignment',1),('read',2),('sha',3),('cache',4)]:
   f=Fixture(self.lib,failure);self.assertLess(f.load(),0);self.assertFalse(f.result.loaded);self.assertFalse(f.result.start);self.assertFalse(f.result.emit);self.assertEqual(len(f.events),events);self.assertLess(f.load(),0);self.assertEqual(len(f.events),events)
 def test_repeat_success_is_not_a_second_load(self):
  f=Fixture(self.lib);self.assertEqual(f.load(),0);n=len(f.events);self.assertLess(f.load(),0);self.assertFalse(f.result.loaded);self.assertFalse(f.result.start);self.assertEqual(len(f.events),n)
 def test_missing_callback_or_hash_is_no_operation(self):
  for field,empty in [('read',READ()),('allocate',ALLOC()),('sha',SHA()),('cache',CACHE())]:
   f=Fixture(self.lib);setattr(f.io,field,empty);self.assertLess(f.load(),0);self.assertEqual(f.events,[])
  f=Fixture(self.lib);f.plan.sha=(c.c_ubyte*32)();self.assertLess(f.load(),0);self.assertEqual(f.events,[])
if __name__=='__main__':unittest.main()
