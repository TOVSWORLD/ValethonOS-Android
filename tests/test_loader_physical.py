"""Actual guarded adapter on modeled storage; never opens a device."""
import ctypes as c,hashlib,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PART=16*1024*1024;PREFIX=15*1024*1024;SLOT=PREFIX+4096
RAWREAD=c.CFUNCTYPE(c.c_uint,c.c_void_p,c.c_ulonglong,c.c_void_p,c.c_uint,c.c_uint);RAWWRITE=c.CFUNCTYPE(c.c_uint,c.c_void_p,c.c_void_p,c.c_ulonglong,c.c_uint,c.c_uint);BLOCK=c.CFUNCTYPE(c.c_int,c.POINTER(c.c_uint),c.c_void_p,c.c_uint)
class Plan(c.Structure):_fields_=[('device',c.c_void_p),('first',c.c_ulonglong),('bytes',c.c_uint),('gpt',c.c_uint),('hw',c.c_uint),('bindings',c.c_uint),('owned',c.c_uint)]
class Ops(c.Structure):_fields_=[('read',RAWREAD),('write',RAWWRITE)]
class Hash(c.Structure):_fields_=[('compress',BLOCK),('verified',c.c_uint)]
class Fixture:
 def __init__(self,lib,short_read=0,short_write=False,hash_fail=False):
  self.lib=lib;self.image=bytearray(PART);self.first=8192;self.reads=[];self.writes=[];self.error=None;self.hash_bytes=0;self.hasher=hashlib.sha256();self.padded=False
  self.buffer=c.create_string_buffer(4096);self.ctx=c.create_string_buffer(lib.lp_context_bytes());self.plan=Plan(0x1234,self.first,PART,5,8,1,1)
  def read(dev,at,out,n,hw):
   offset=at-self.first*512;self.reads.append((dev,at,n,hw))
   if dev!=0x1234 or hw!=8 or offset<0 or offset+n>PART:self.error='read escaped target';return 0
   if len(self.reads)==short_read:return n-1
   c.memmove(out,bytes(self.image[offset:offset+n]),n);return n
  def write(dev,data,at,n,hw):
   offset=at-self.first*512;self.writes.append((dev,at,n,hw))
   if dev!=0x1234 or hw!=8 or n!=4096 or offset<SLOT or offset+n>PART-4096:self.error='write escaped slots';return 0
   self.image[offset:offset+n]=c.string_at(data,n);return n-1 if short_write else n
  def block(state,data,blocks):
   if hash_fail:return -1
   raw=c.string_at(data,blocks*64)
   if self.hash_bytes==PREFIX:
    expected=b'\x80'+bytes(55)+(PREFIX*8).to_bytes(8,'big')
    if raw!=expected:self.error='prefix padding differs';return -1
    digest=self.hasher.digest()
    for i in range(8):state[i]=int.from_bytes(digest[i*4:i*4+4],'big')
    self.padded=True
   else:self.hasher.update(raw);self.hash_bytes+=len(raw)
   return 0
  self.callbacks=(RAWREAD(read),RAWWRITE(write),BLOCK(block));self.ops=Ops(*self.callbacks[:2]);self.hash=Hash(self.callbacks[2],1)
  self.started=lib.lp_init(self.ctx,c.byref(self.plan),c.byref(self.ops),c.byref(self.hash),self.buffer,4096)
 def read(self,at,n=4096):
  out=c.create_string_buffer(max(n,1));return self.lib.lp_read(self.ctx,at,out,n),out.raw
 def write(self,at=SLOT):return self.lib.lp_write(self.ctx,at,c.create_string_buffer(b'a'*4096),4096)
 def prefix(self,digest=None):
  digest=digest or hashlib.sha256(self.image[:PREFIX]).digest();return self.lib.lp_prefix(self.ctx,c.create_string_buffer(digest))
class LoaderPhysical(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();out=Path(cls.temp.name)/'physical.so';cc=shutil.which('clang') or shutil.which('cc')
  if not cc:raise unittest.SkipTest('C compiler unavailable')
  subprocess.run([cc,'-shared','-fPIC','-O2',*[str(ROOT/'projects/firetabs-android/loader-retained'/s) for s in ['physical.c','hash-stream.c']],'-o',str(out)],check=True,capture_output=True);cls.lib=c.CDLL(str(out));cls.lib.lp_context_bytes.restype=c.c_ulong;cls.lib.lp_init.argtypes=[c.c_void_p,c.POINTER(Plan),c.POINTER(Ops),c.POINTER(Hash),c.c_void_p,c.c_uint];cls.lib.lp_read.argtypes=[c.c_void_p,c.c_ulong,c.c_void_p,c.c_ulong];cls.lib.lp_write.argtypes=cls.lib.lp_read.argtypes;cls.lib.lp_read_absolute.argtypes=[c.c_void_p,c.c_ulonglong,c.c_void_p,c.c_uint];cls.lib.lp_prefix.argtypes=[c.c_void_p,c.c_void_p]
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def test_normalized_exact_reads_writes_and_immutable_target_copy(self):
  f=Fixture(self.lib);self.assertEqual(f.started,0);f.plan.first=9000;f.plan.hw=1;self.assertEqual(f.read(0)[0],0);self.assertEqual(f.write(),0);self.assertEqual(f.image[SLOT:SLOT+4096],b'a'*4096);self.assertEqual(f.reads[0][1],8192*512);self.assertEqual(f.writes[0][3],8);self.assertIsNone(f.error)
 def test_write_guards_fail_before_callbacks(self):
  for at in [0,PREFIX,SLOT+1,PART-4096,PART,2**64-1]:
   f=Fixture(self.lib);self.assertLess(f.write(at),0);self.assertEqual(f.writes,[]);self.assertLess(f.read(0)[0],0);self.assertEqual(f.reads,[])
 def test_short_read_and_uncertain_short_write_stop_without_retry(self):
  f=Fixture(self.lib,short_read=1);self.assertLess(f.read(0)[0],0);self.assertLess(f.read(0)[0],0);self.assertEqual(len(f.reads),1)
  f=Fixture(self.lib,short_write=True);self.assertLess(f.write(),0);self.assertLess(f.write(),0);self.assertLess(f.read(0)[0],0);self.assertEqual(len(f.writes),1);self.assertEqual(f.reads,[])
 def test_partial_payload_read_uses_owned_aligned_bounce_without_overrun(self):
  f=Fixture(self.lib);at=SLOT+4096;f.image[at:at+512]=bytes(range(256))*2;out=c.create_string_buffer(b'z'*179)
  self.assertEqual(self.lib.lp_read(f.ctx,at,c.byref(out,1),162),0);self.assertEqual(out.raw[1:163],bytes(range(162)));self.assertEqual(out.raw[163:179],b'z'*16);self.assertEqual(f.reads[0][2],512);self.assertIsNone(f.error)
 def test_absolute_blob_read_stays_in_prefix(self):
  f=Fixture(self.lib);out=c.create_string_buffer(4608);self.assertEqual(self.lib.lp_read_absolute(f.ctx,8192*512+12*1024*1024,out,4608),0)
  for at in [8192*512-1,8192*512+PREFIX,2**64-1]:
   f=Fixture(self.lib);self.assertLess(self.lib.lp_read_absolute(f.ctx,at,out,4608),0);self.assertEqual(f.reads,[])
 def test_complete_prefix_stream_has_exact_extent_and_padding(self):
  f=Fixture(self.lib);self.assertEqual(f.prefix(),0);self.assertEqual(len(f.reads),PREFIX//4096);self.assertEqual(f.hash_bytes,PREFIX);self.assertTrue(f.padded);self.assertEqual(f.writes,[]);self.assertIsNone(f.error)
 def test_prefix_read_hash_or_digest_failure_stops(self):
  f=Fixture(self.lib,short_read=2);self.assertLess(f.prefix(),0);self.assertEqual(len(f.reads),2);self.assertLess(f.write(),0)
  f=Fixture(self.lib,hash_fail=True);self.assertLess(f.prefix(),0);self.assertEqual(len(f.reads),1)
  f=Fixture(self.lib);self.assertLess(f.prefix(bytes(32)),0);self.assertLess(f.read(0)[0],0);self.assertEqual(f.writes,[])
 def test_bad_plan_or_repeat_initialization_cannot_access_storage(self):
  for field,value in [('first',0),('first',2**32-1),('first',2**64-1),('bytes',PART+4096),('gpt',6),('hw',1),('bindings',0),('owned',0)]:
   f=Fixture(self.lib);f.ctx=c.create_string_buffer(self.lib.lp_context_bytes());setattr(f.plan,field,value);self.assertLess(self.lib.lp_init(f.ctx,c.byref(f.plan),c.byref(f.ops),c.byref(f.hash),f.buffer,4096),0);self.assertLess(f.read(0)[0],0);self.assertEqual(f.reads,[])
  f=Fixture(self.lib);self.assertLess(self.lib.lp_init(f.ctx,c.byref(f.plan),c.byref(f.ops),c.byref(f.hash),f.buffer,4096),0);self.assertLess(f.write(),0);self.assertEqual(f.writes,[])
 def test_prefix_expected_digest_cannot_alias_read_buffer(self):
  f=Fixture(self.lib);self.assertLess(self.lib.lp_prefix(f.ctx,f.buffer),0);self.assertEqual(f.reads,[])
if __name__=='__main__':unittest.main()
