"""Actual C adapter with modeled command completion; no hardware bindings."""
import ctypes as c
from pathlib import Path
import shutil,subprocess,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
class Command(c.Structure):_fields_=[('opcode',c.c_uint),('argument',c.c_uint),('response_type',c.c_uint),('response',c.c_uint*4),('timeout',c.c_uint),('retries',c.c_uint)]
CALL=c.CFUNCTYPE(c.c_int,c.c_void_p,c.POINTER(Command));CLOCK=c.CFUNCTYPE(c.c_uint,c.c_void_p)
class Adapter(c.Structure):_fields_=[('context',c.c_void_p),('command',CALL),('clock',CLOCK),('rca',c.c_uint),('cache_size',c.c_uint),('cache_enabled',c.c_uint),('bindings',c.c_uint),('clock_verified',c.c_uint),('stopped',c.c_uint)]
class Fixture:
 def __init__(self,lib,statuses=(0x900,0,0x900),error_at=0,time_after=0,start=0):
  self.events=[];self.t=start;self.n=0;self.lib=lib;self.statuses=list(statuses);self.failure=None
  def command(_,ptr):
   q=ptr.contents;self.n+=1;self.events.append((q.opcode,q.argument,q.response_type,q.timeout,q.retries));self.t=(self.t+time_after)&0xffffffff
   q.response[0]=self.statuses.pop(0) if self.statuses else 0xe00
   return 9 if self.n==error_at else 0
  self.call=CALL(command);self.clock=CLOCK(lambda _:self.t);self.a=Adapter(None,self.call,self.clock,1,1024,1,1,1,0)
 def flush(self):return self.lib.lf_flush(c.byref(self.a))
class LoaderFlush(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();out=Path(cls.temp.name)/'flush.so';cc=shutil.which('clang') or shutil.which('cc')
  if not cc:raise unittest.SkipTest('C compiler unavailable')
  subprocess.run([cc,'-shared','-fPIC','-O2',str(ROOT/'projects/firetabs-android/loader-retained/mmc_flush.c'),'-o',str(out)],check=True,capture_output=True)
  cls.lib=c.CDLL(str(out));cls.lib.lf_flush.argtypes=[c.c_void_p]
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def test_command_layout_and_fresh_status_after_exact_single_flush(self):
  self.assertEqual(c.sizeof(Command),36);self.assertEqual(Command.response.offset,12);self.assertEqual(Command.timeout.offset,28);self.assertEqual(Command.retries.offset,32)
  f=Fixture(self.lib);self.assertEqual(f.flush(),0);self.assertEqual(f.events,[(13,0x10000,1,50,0),(6,0x03200101,8,50,0),(13,0x10000,1,50,0)])
 def test_busy_then_ready_requires_fresh_post_command_status(self):
  f=Fixture(self.lib,[0x900,0,0xe00,0xe00,0x900]);self.assertEqual(f.flush(),0);self.assertEqual(len(f.events),5)
 def test_zero_firmware_returns_never_hide_poll_exhaustion(self):
  f=Fixture(self.lib,[0x900,0]+[0xe00]*9);self.assertLess(f.flush(),0);self.assertEqual(len(f.events),1002);self.assertEqual(sum(e[0]==6 for e in f.events),1);n=len(f.events);self.assertLess(f.flush(),0);self.assertEqual(len(f.events),n)
 def test_command_and_status_transport_failures_latch_without_retry(self):
  for at in [1,2,3]:
   f=Fixture(self.lib,error_at=at);self.assertLess(f.flush(),0);self.assertEqual(len(f.events),at);self.assertLess(f.flush(),0);self.assertEqual(len(f.events),at)
 def test_each_r1_error_fails_even_when_ready(self):
  for bit in [31,30,29,28,27,26,25,24,23,22,21,20,19,18,17,16,15,14,13,7,6]:
   for at in [0,1,2]:
    s=[0x900,0,0x900];s[at]|=1<<bit;f=Fixture(self.lib,s);self.assertLess(f.flush(),0);self.assertEqual(len(f.events),at+1)
 def test_busy_or_unexpected_initial_state_prevents_switch(self):
  for status in [0,0xe00,0x100,0xb00,0xd00]:
   f=Fixture(self.lib,[status]);self.assertLess(f.flush(),0);self.assertEqual([e[0] for e in f.events],[13])
 def test_unexpected_post_state_stops(self):
  for status in [0,0x100,0xb00,0xd00]:
   f=Fixture(self.lib,[0x900,0,status]);self.assertLess(f.flush(),0);self.assertEqual(len(f.events),3)
 def test_elapsed_budget_rejects_even_ready_and_wrapping_clock_works(self):
  f=Fixture(self.lib,time_after=500);self.assertLess(f.flush(),0);self.assertEqual(len(f.events),2)
  f=Fixture(self.lib,time_after=400);self.assertLess(f.flush(),0);self.assertEqual(len(f.events),3)
  f=Fixture(self.lib,time_after=1,start=0xfffffffe);self.assertEqual(f.flush(),0)
 def test_missing_admission_or_bindings_stops_before_commands(self):
  for field,value in [('rca',0),('rca',0x10000),('cache_size',0),('cache_enabled',2),('bindings',0),('clock_verified',0)]:
   f=Fixture(self.lib);setattr(f.a,field,value);self.assertLess(f.flush(),0);self.assertEqual(f.events,[])
  for field,callback in [('command',CALL()),('clock',CLOCK())]:
   f=Fixture(self.lib);setattr(f.a,field,callback);self.assertLess(f.flush(),0);self.assertEqual(f.events,[])
 def test_cache_off_still_requires_two_fresh_statuses_and_never_switches(self):
  f=Fixture(self.lib,[0x900,0x900]);f.a.cache_enabled=0
  self.assertEqual(f.flush(),0);self.assertEqual(f.events,[(13,0x10000,1,50,0)]*2)
  self.assertEqual(f.a.cache_enabled,0)
 def test_cache_off_busy_post_status_is_bounded_without_any_switch(self):
  f=Fixture(self.lib,[0x900]+[0xe00]*1000);f.a.cache_enabled=0
  self.assertLess(f.flush(),0);self.assertEqual(len(f.events),1001)
  self.assertTrue(all(e[0]==13 for e in f.events));n=len(f.events)
  self.assertLess(f.flush(),0);self.assertEqual(len(f.events),n)
 def test_cache_off_errors_latch_at_either_status_without_retry(self):
  for at in [1,2]:
   f=Fixture(self.lib,[0x900,0x900],error_at=at);f.a.cache_enabled=0
   self.assertLess(f.flush(),0);self.assertEqual(len(f.events),at)
   self.assertLess(f.flush(),0);self.assertEqual(len(f.events),at)
  for at in [0,1]:
   s=[0x900,0x900];s[at]|=0x80;f=Fixture(self.lib,s);f.a.cache_enabled=0
   self.assertLess(f.flush(),0);self.assertEqual(len(f.events),at+1)
 def test_cache_off_deadline_rejects_even_ready(self):
  f=Fixture(self.lib,[0x900,0x900],time_after=500);f.a.cache_enabled=0
  self.assertLess(f.flush(),0);self.assertEqual(len(f.events),2)
if __name__=='__main__':unittest.main()
