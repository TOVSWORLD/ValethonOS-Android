"""Full native module/target/prefix/persistence composition on modeled hardware."""
import ctypes as c,hashlib,shutil,subprocess,tempfile,unittest
from pathlib import Path
from test_loader_physical import Fixture as Disk,Plan,Ops,Hash,PREFIX
from test_loader_checkpoint import Config,Point
from test_loader_flush import Adapter,CALL,CLOCK
import retained_log_mailbox as m
ROOT=Path(__file__).resolve().parents[1]
class FirmwareModule(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();out=Path(cls.temp.name)/'firmware-module.so';cc=shutil.which('clang') or shutil.which('cc')
  if not cc:raise unittest.SkipTest('C compiler unavailable')
  names=['checkpoint.c','mmc_flush.c','module.c','hash-stream.c','physical.c','firmware-module.c'];subprocess.run([cc,'-shared','-fPIC','-O2',*[str(ROOT/'projects/firetabs-android/loader-retained'/s) for s in names],'-o',str(out)],check=True,capture_output=True);cls.lib=c.CDLL(str(out));cls.lib.lp_context_bytes.restype=c.c_ulong;cls.lib.lp_init.argtypes=[c.c_void_p,c.POINTER(Plan),c.POINTER(Ops),c.POINTER(Hash),c.c_void_p,c.c_uint];cls.lib.lfw_state_bytes.restype=c.c_ulong;cls.lib.lfw_start.argtypes=[c.c_void_p,c.POINTER(Config),c.POINTER(Plan),c.POINTER(Ops),c.POINTER(Hash),c.POINTER(Adapter)];cls.lib.lfw_emit.argtypes=[c.c_void_p,c.POINTER(Point)]
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def fixture(self,**kw):
  f=Disk(self.lib,**kw);f.nonce=bytes(range(32));image=bytearray(m.PARTITION);image[:8]=b'ANDROID!';image,f.prefix_sha=m.prepare(bytes(image),f.nonce,b'VALETHON HOST CONTROL v1\nThis is a preinstalled retention control, NOT a kernel log.\n');f.image=bytearray(image);f.stable=image;f.commands=[];f.pending=False
  def command(_,ptr):
   q=ptr.contents;f.commands.append((q.opcode,q.argument,q.retries))
   if q.opcode==6:f.pending=True;q.response[0]=0
   elif q.opcode==13:
    q.response[0]=0x900
    if f.pending:f.stable=bytes(f.image);f.pending=False
   else:return 9
   return 0
  f.command=CALL(command);f.clock=CLOCK(lambda _:0);f.card=Adapter(None,f.command,f.clock,1,1024,1,1,1,0);f.config=Config((c.c_ubyte*32).from_buffer_copy(f.nonce),(c.c_ubyte*32).from_buffer_copy(bytes.fromhex(f.prefix_sha)),8192,100000,m.PARTITION,5,8,1,1);f.state=c.create_string_buffer(self.lib.lfw_state_bytes());return f
 def start(self,f):return self.lib.lfw_start(f.state,c.byref(f.config),c.byref(f.plan),c.byref(f.ops),c.byref(f.hash),c.byref(f.card))
 def emit(self,f,stage):return self.lib.lfw_emit(f.state,c.byref(Point(stage,0,0,0,0,0,0,0,0,0)))
 def test_mode_handoff_with_immutable_target_stream_and_checked_flush(self):
  f=self.fixture();self.assertEqual(self.start(f),0);self.assertEqual(self.emit(f,1),0);self.assertEqual(self.emit(f,3),0);self.assertEqual(m.inspect(bytes(f.stable),f.nonce,f.prefix_sha)['latest']['sequence'],3);self.assertEqual(f.hash_bytes,PREFIX);self.assertEqual(len(f.commands),18);self.assertTrue(all(e[2]==0 for e in f.commands));self.assertIsNone(f.error)
 def test_inconsistent_target_rejected_before_io(self):
  f=self.fixture();f.config.target=9000;self.assertLess(self.start(f),0);self.assertLess(self.emit(f,1),0);self.assertEqual((f.reads,f.writes,f.commands),([],[],[]))
 def test_short_read_and_uncertain_write_stop_the_whole_module(self):
  for kwargs in [{'short_read':1},{'short_write':True}]:
   f=self.fixture(**kwargs);self.assertEqual(self.start(f),0);self.assertLess(self.emit(f,1),0);counts=(len(f.reads),len(f.writes),len(f.commands));self.assertLess(self.emit(f,3),0);self.assertEqual(counts,(len(f.reads),len(f.writes),len(f.commands)));self.assertEqual(m.inspect(bytes(f.stable),f.nonce,f.prefix_sha)['latest']['sequence'],1)
 def test_uninitialized_emit_and_repeat_start_are_no_io(self):
  f=self.fixture();self.assertLess(self.emit(f,1),0);self.assertEqual(self.start(f),0);self.assertLess(self.start(f),0);self.assertLess(self.emit(f,1),0);self.assertEqual((f.reads,f.writes,f.commands),([],[],[]))
if __name__=='__main__':unittest.main()
