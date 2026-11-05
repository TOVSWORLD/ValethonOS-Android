import ctypes as c
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import retained_log_mailbox as m
import loader_checkpoint_record as record
ROOT=Path(__file__).resolve().parents[1]
READ=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_ulong,c.c_void_p,c.c_ulong)
WRITE=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_ulong,c.c_void_p,c.c_ulong)
FLUSH=c.CFUNCTYPE(c.c_int,c.c_void_p)
PREFIX=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_void_p)
class IO(c.Structure):_fields_=[('context',c.c_void_p),('read',READ),('write',WRITE),('flush',FLUSH),('prefix',PREFIX)]
class Config(c.Structure):_fields_=[('nonce',c.c_ubyte*32),('prefix',c.c_ubyte*32),('target',c.c_ulonglong),('logical',c.c_ulonglong),('bytes',c.c_uint),('partition',c.c_uint),('hardware',c.c_uint),('durable',c.c_uint),('exclusive',c.c_uint)]
class Point(c.Structure):_fields_=[('stage',c.c_uint),('mode',c.c_uint),('kind',c.c_uint),('size',c.c_uint),('destination',c.c_uint),('entry',c.c_uint),('dt',c.c_uint),('selected_first',c.c_ulonglong),('requested',c.c_ulonglong),('selected',c.c_ulonglong)]


class Fixture:
 def __init__(self,lib,fail=None):
  self.lib=lib;self.nonce=bytes(range(32));b=bytearray(m.PARTITION);b[:8]=b'ANDROID!';self.image,self.prefix=m.prepare(bytes(b),self.nonce,b'VALETHON HOST CONTROL v1\nThis is a preinstalled retention control, NOT a kernel log.\n');self.original=self.image;self.image=bytearray(self.image);self.stable=bytes(self.image);self.events=[];self.writes=0;self.flushes=0;self.hashes=0;self.fail=fail;self.callback_error=None
  def read(_,at,out,n):
   self.events.append(('read',at,n))
   if self.fail=='readback_header' and self.writes==3 and self.flushes==3:return -1
   if self.fail=='readback_payload' and self.writes==3 and n==len(record.TAG)+record.BODY.size:return -1
   if at+n>len(self.image):self.callback_error='read bounds';return -1
   c.memmove(out,bytes(self.image[at:at+n]),n);return 0
  def write(_,at,data,n):
   self.writes+=1;self.events.append(('write',at,n))
   if self.fail=='write'+str(self.writes):return -1
   if at<m.SLOT_BASE or at+n>m.GUARD or n!=4096:self.callback_error='write bounds';return -1
   self.image[at:at+n]=c.string_at(data,n);return 0
  def flush(_):
   self.flushes+=1;self.events.append(('flush',))
   if self.fail=='flush'+str(self.flushes):return -1
   self.stable=bytes(self.image);return 0
  def prefix(_,expected):
   self.hashes+=1;self.events.append(('hash',));return 0 if hashlib.sha256(self.image[:m.BASE]).digest()==c.string_at(expected,32) else -1
  self.callbacks=(READ(read),WRITE(write),FLUSH(flush),PREFIX(prefix));self.io=IO(None,*self.callbacks)
  self.config=Config((c.c_ubyte*32).from_buffer_copy(self.nonce),(c.c_ubyte*32).from_buffer_copy(bytes.fromhex(self.prefix)),8192,100000,m.PARTITION,5,8,1,1)
  self.ctx=c.create_string_buffer(lib.lc_context_bytes());self.init=lib.lc_init(self.ctx,c.byref(self.config),c.byref(self.io))
 def emit(self,stage,**kw):
  p=Point(stage,0,0,0,0,0,0,0,0,0)
  for k,v in kw.items():setattr(p,k,v)
  return self.lib.lc_emit(self.ctx,c.byref(p))
 def latest(self,stable=False):return m.inspect(bytes(self.stable if stable else self.image),self.nonce,self.prefix)['latest']
 def checkpoint(self):return record.decode(self.latest()['payload'],self.nonce,self.prefix)


class LoaderCheckpoint(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();output=Path(cls.temp.name)/'checkpoint.so';cc=shutil.which('clang') or shutil.which('cc')
  if not cc:raise unittest.SkipTest('C compiler unavailable')
  subprocess.run([cc,'-shared','-fPIC','-O2',str(ROOT/'projects/firetabs-android/loader-retained/checkpoint.c'),'-o',str(output)],check=True,capture_output=True)
  cls.lib=c.CDLL(str(output));cls.lib.lc_context_bytes.restype=c.c_ulong;cls.lib.lc_init.argtypes=[c.c_void_p,c.POINTER(Config),c.POINTER(IO)];cls.lib.lc_emit.argtypes=[c.c_void_p,c.POINTER(Point)]
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def test_mode_reads_and_handoff_are_distinct_loader_records(self):
  f=Fixture(self.lib);self.assertEqual(f.init,0);self.assertEqual(f.emit(1),0)
  self.assertEqual(f.checkpoint()['stage'],'mode')
  for kind,extra in [(1,0),(2,2048)]:
   self.assertEqual(f.emit(2,kind=kind,size=4096,destination=0x45000000,selected_first=9000,requested=100000*512+extra,selected=9000*512+extra),0)
   r=f.checkpoint();self.assertEqual(r['selected_partition_first_sector'],9000);self.assertEqual(r['selected_read_offset'],9000*512+extra);self.assertEqual(r['record_storage_first_sector'],8192)
  self.assertEqual(f.emit(3,entry=0x12345678,dt=0x44000000),0)
  r=f.checkpoint();self.assertEqual(r['kernel_entry'],0x12345678);self.assertFalse(r['kernel_record']);self.assertFalse(r['kernel_entry_proved']);self.assertEqual(f.latest()['sequence'],5)
  self.assertEqual(f.hashes,1);self.assertEqual(f.flushes,12);self.assertEqual(f.writes,12);self.assertIsNone(f.callback_error)
  self.assertEqual(bytes(f.image[:m.SLOT_BASE]),f.original[:m.SLOT_BASE]);self.assertEqual(bytes(f.image[m.GUARD:]),f.original[m.GUARD:])
  events=len(f.events);self.assertEqual(f.emit(3),1);self.assertEqual(len(f.events),events)
 def test_recovery_fastboot_and_unrelated_reads_make_no_io(self):
  f=Fixture(self.lib)
  for mode in [2,6,99]:self.assertEqual(f.emit(1,mode=mode),1)
  self.assertEqual(f.emit(2,kind=1,requested=7),1);self.assertEqual(f.events,[])
 def test_missing_target_or_durability_admission_stops_before_io(self):
  for field,value in [('durable',0),('exclusive',0),('bytes',17*1024*1024),('partition',6),('hardware',1),('target',0),('target',2**64-1)]:
   with self.subTest(field=field,value=value):
    f=Fixture(self.lib);setattr(f.config,field,value);self.assertLess(self.lib.lc_init(f.ctx,c.byref(f.config),c.byref(f.io)),0);self.assertLess(f.emit(1),0);self.assertEqual(f.events,[])
 def test_seed_prefix_guard_and_foreign_tail_prevent_writes(self):
  for label,at in [('seed',m.BASE+12),('prefix',20),('guard',m.GUARD),('foreign_tail',m.SLOT_BASE+m.SLOT+8192),('host_control',m.SLOT_BASE+4096)]:
   with self.subTest(label=label):
    f=Fixture(self.lib);f.image[at]^=1;self.assertLess(f.emit(1),0);self.assertEqual(f.writes,0);events=len(f.events);self.assertLess(f.emit(3),0);self.assertEqual(len(f.events),events)
 def test_each_failed_io_stops_without_retry_and_preserves_previous_record(self):
  for failure in ['write1','write2','write3','flush1','flush2','flush3','readback_header','readback_payload']:
   with self.subTest(failure=failure):
    f=Fixture(self.lib,failure);self.assertLess(f.emit(1),0);events=len(f.events);self.assertLess(f.emit(3),0);self.assertEqual(len(f.events),events)
    self.assertGreaterEqual(f.latest(True)['sequence'],1)
    self.assertEqual(bytes(f.image[:m.SLOT_BASE]),f.original[:m.SLOT_BASE]);self.assertEqual(bytes(f.image[m.GUARD:]),f.original[m.GUARD:]);self.assertEqual(bytes(f.image[m.SLOT_BASE:m.SLOT_BASE+m.SLOT]),f.original[m.SLOT_BASE:m.SLOT_BASE+m.SLOT])
 def test_foreign_concurrent_record_and_commit_cap_stop_further_writes(self):
  f=Fixture(self.lib);self.assertEqual(f.emit(1),0)
  foreign=b'VALETHON RETAINED KERNEL LOG v1 release=fixture\n';at=m.SLOT_BASE
  f.image[at:at+m.HEADER]=m.header(3,f.nonce,foreign);f.image[at+m.HEADER:at+m.HEADER+len(foreign)]=foreign
  writes=f.writes;self.assertLess(f.emit(3),0);self.assertEqual(f.writes,writes)
  f=Fixture(self.lib);self.assertEqual(f.emit(1),0)
  for _ in range(7):self.assertEqual(f.emit(2,kind=1,requested=100000*512),0)
  writes=f.writes;self.assertLess(f.emit(3),0);self.assertEqual(f.writes,writes)
 def test_existing_regular_file_writer_continues_after_loader_records(self):
  f=Fixture(self.lib);self.assertEqual(f.emit(1),0);self.assertEqual(f.emit(3,entry=0x40000000,dt=0x44000000),0)
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'fixture.img';p.write_bytes(f.image);p.chmod(0o600)
   payload=b'VALETHON RETAINED KERNEL LOG v1 release=fixture\n'
   r=m.write_fixture(p,f.nonce,f.prefix,payload);self.assertEqual(r['sequence'],4);self.assertEqual(r['payload'],payload);self.assertIsNone(record.decode(payload,f.nonce,f.prefix))
 def test_decoder_rejects_wrong_attribution_and_fields(self):
  f=Fixture(self.lib);self.assertEqual(f.emit(1),0);payload=f.latest()['payload']
  with self.assertRaises(ValueError):record.decode(payload,f.nonce[::-1],f.prefix)
  with self.assertRaises(ValueError):record.decode(payload[:-1],f.nonce,f.prefix)
  bad=bytearray(payload);bad[len(record.TAG)+4]=2
  with self.assertRaises(ValueError):record.decode(bytes(bad),f.nonce,f.prefix)
 def test_null_flush_callback_never_initializes(self):
  f=Fixture(self.lib);f.io.flush=FLUSH()
  self.assertLess(self.lib.lc_init(f.ctx,c.byref(f.config),c.byref(f.io)),0)
  self.assertLess(f.emit(1),0);self.assertEqual(f.events,[])
 def test_c_writer_commits_to_owned_regular_file_with_real_fsync(self):
  import os,stat
  f=Fixture(self.lib);events=[]
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'disk.img';fd=os.open(p,os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
   try:
    self.assertTrue(stat.S_ISREG(os.fstat(fd).st_mode));self.assertEqual(os.pwrite(fd,f.original,0),m.PARTITION)
    def read(_,at,out,n):
     data=os.pread(fd,n,at)
     if len(data)!=n:return -1
     c.memmove(out,data,n);return 0
    def write(_,at,buf,n):
     if at<m.SLOT_BASE or at+n>m.GUARD or n!=4096:return -1
     events.append(('write',at));return 0 if os.pwrite(fd,c.string_at(buf,n),at)==n else -1
    def flush(_):events.append(('flush',));os.fsync(fd);return 0
    def prefix(_,expected):return 0 if hashlib.sha256(os.pread(fd,m.BASE,0)).digest()==c.string_at(expected,32) else -1
    callbacks=(READ(read),WRITE(write),FLUSH(flush),PREFIX(prefix));io=IO(None,*callbacks)
    self.assertEqual(self.lib.lc_init(f.ctx,c.byref(f.config),c.byref(io)),0)
    self.assertEqual(f.emit(1),0);self.assertEqual(f.emit(3,entry=0x40000000,dt=0x44000000),0)
    image=os.pread(fd,m.PARTITION,0);latest=m.inspect(image,f.nonce,f.prefix)['latest']
    self.assertEqual(latest['sequence'],3);self.assertEqual(record.decode(latest['payload'],f.nonce,f.prefix)['stage'],'pre_handoff')
    self.assertEqual([e[0] for e in events],['write','flush']*6)
    self.assertEqual(image[:m.SLOT_BASE],f.original[:m.SLOT_BASE]);self.assertEqual(image[m.GUARD:],f.original[m.GUARD:])
   finally:os.close(fd)
