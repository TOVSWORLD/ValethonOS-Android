"""Integrated writer and checked persistence adapter on modeled storage."""
import ctypes as c
from pathlib import Path
import shutil,subprocess,tempfile,unittest
from test_loader_checkpoint import Fixture,Config,IO,Point
from test_loader_flush import Adapter,Command,CALL,CLOCK
ROOT=Path(__file__).resolve().parents[1]
class LoaderModule(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();out=Path(cls.temp.name)/'module.so';cc=shutil.which('clang') or shutil.which('cc')
  if not cc:raise unittest.SkipTest('C compiler unavailable')
  sources=[str(ROOT/'projects/firetabs-android/loader-retained'/s) for s in ['checkpoint.c','mmc_flush.c','module.c']]
  subprocess.run([cc,'-shared','-fPIC','-O2',*sources,'-o',str(out)],check=True,capture_output=True);cls.lib=c.CDLL(str(out));cls.lib.lc_context_bytes.restype=c.c_ulong;cls.lib.lc_init.argtypes=[c.c_void_p,c.POINTER(Config),c.POINTER(IO)];cls.lib.lc_emit.argtypes=[c.c_void_p,c.POINTER(Point)];cls.lib.lm_state_bytes.restype=c.c_ulong;cls.lib.lm_start.argtypes=[c.c_void_p,c.POINTER(Config),c.POINTER(IO),c.POINTER(Adapter)];cls.lib.lm_emit.argtypes=[c.c_void_p,c.POINTER(Point)]
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def fixture(self,fail_at=0):
  f=Fixture(self.lib);f.command_events=[];f.pending=False
  def command(_,ptr):
   q=ptr.contents;f.command_events.append((q.opcode,q.argument,q.retries))
   if len(f.command_events)==fail_at:return 9
   if q.opcode==6:f.pending=True;q.response[0]=0
   elif q.opcode==13:
    q.response[0]=0x900
    if f.pending:f.stable=bytes(f.image);f.flushes+=1;f.pending=False
   else:return 9
   return 0
  f.command=CALL(command);f.clock=CLOCK(lambda _:0);f.adapter=Adapter(None,f.command,f.clock,1,1024,1,1,1,0);f.state=c.create_string_buffer(self.lib.lm_state_bytes());f.started=self.lib.lm_start(f.state,c.byref(f.config),c.byref(f.io),c.byref(f.adapter));return f
 def emit(self,f,stage):return self.lib.lm_emit(f.state,c.byref(Point(stage,0,0,0,0,0,0,0,0,0)))
 def test_mode_and_handoff_commit_through_checked_commands(self):
  f=self.fixture();self.assertEqual(f.started,0);self.assertEqual(self.emit(f,1),0);self.assertEqual(self.emit(f,3),0);self.assertEqual(f.latest()['sequence'],3);self.assertEqual(f.flushes,6);self.assertEqual(len(f.command_events),18);self.assertTrue(all(e[2]==0 for e in f.command_events));self.assertEqual(sum(e[0]==6 for e in f.command_events),6)
 def test_every_flush_command_boundary_stops_and_keeps_previous_record(self):
  for at in range(1,10):
   f=self.fixture(at);self.assertLess(self.emit(f,1),0);self.assertEqual(len(f.command_events),at);n=f.writes;self.assertLess(self.emit(f,3),0);self.assertEqual((len(f.command_events),f.writes),(at,n));self.assertGreaterEqual(f.latest(True)['sequence'],1)
 def test_missing_adapter_admission_never_reads_or_writes(self):
  f=self.fixture();f.state=c.create_string_buffer(self.lib.lm_state_bytes());f.adapter.bindings=0;self.assertLess(self.lib.lm_start(f.state,c.byref(f.config),c.byref(f.io),c.byref(f.adapter)),0);self.assertLess(self.emit(f,1),0);self.assertEqual(f.events,[]);self.assertEqual(f.command_events,[])
 def test_second_initialization_stops_module_without_io(self):
  f=self.fixture();self.assertLess(self.lib.lm_start(f.state,c.byref(f.config),c.byref(f.io),c.byref(f.adapter)),0);self.assertLess(self.emit(f,1),0);self.assertEqual(f.events,[]);self.assertEqual(f.command_events,[])
if __name__=='__main__':unittest.main()
