"""Clock and command-only controller driver on modeled registers, no device I/O."""
import ctypes as c,shutil,subprocess,tempfile,unittest
from pathlib import Path
from test_loader_flush import Command
ROOT=Path(__file__).resolve().parents[1]
TICKS=c.CFUNCTYPE(c.c_uint,c.c_void_p);READ=c.CFUNCTYPE(c.c_uint,c.c_void_p,c.c_uint);WRITE=c.CFUNCTYPE(None,c.c_void_p,c.c_uint,c.c_uint)
class Plan(c.Structure):_fields_=[('read',READ),('write',WRITE),('io',c.c_void_p),('ticks',TICKS),('timer',c.c_void_p),('rca',c.c_uint),('block',c.c_uint),('verified',c.c_uint)]
class Clock(c.Structure):_fields_=[('ticks',TICKS),('context',c.c_void_p),('last',c.c_uint),('remainder',c.c_uint),('ms',c.c_uint),('initialized',c.c_uint),('failed',c.c_uint)]
class Driver(c.Structure):_fields_=[('clock',Clock),('plan',Plan),('initialized',c.c_uint),('stopped',c.c_uint)]
class Fixture:
 def __init__(self,lib,busy=False,event=0x100,stale=0,reply_after=0,freeze=False,step=13000,interrupts=0,dma=0,response=0x900):
  self.lib=lib;self.events=[];self.sent=False;self.pending=stale;self.tick=0;self.tick_calls=0;self.polls=0
  def ticks(_):
   self.tick_calls+=1
   if not freeze or self.tick_calls<=2:self.tick=(self.tick+step)&0xffffffff
   return self.tick
  def read(_,off):
   self.events.append(('read',off))
   if off==0x10:return interrupts
   if off==0x98:return dma
   if off==0x3c:return 3 if busy else 0
   if off==0x40:return response
   if off==0x0c:
    if self.sent and not self.pending:
     self.polls+=1
     if self.polls>reply_after:self.pending=event
    return self.pending
   return 0xffffffff
  def write(_,off,value):
   self.events.append(('write',off,value))
   if off==0x0c:
    self.pending&=~value
    if not self.pending:self.sent=False
   if off==0x34:self.sent=True
  self.callbacks=(READ(read),WRITE(write),TICKS(ticks));self.plan=Plan(self.callbacks[0],self.callbacks[1],None,self.callbacks[2],None,1,512,1);self.ctx=Driver();self.started=lib.ld_init(c.byref(self.ctx),c.byref(self.plan));self.events.clear()
 def command(self,op=6,arg=0x03200101,kind=8,retries=0,timeout=50):
  self.request=Command(op,arg,kind,(c.c_uint*4)(),timeout,retries);return self.lib.ld_command(c.byref(self.ctx),c.byref(self.request))
class LoaderCommand(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();out=Path(cls.temp.name)/'command.so';cc=shutil.which('clang') or shutil.which('cc')
  if not cc:raise unittest.SkipTest('C compiler unavailable')
  subprocess.run([cc,'-shared','-fPIC','-O2',*[str(ROOT/'projects/firetabs-android/loader-retained'/s) for s in ['clock.c','command.c']],'-o',str(out)],check=True,capture_output=True);cls.lib=c.CDLL(str(out));cls.lib.ld_init.argtypes=[c.POINTER(Driver),c.POINTER(Plan)];cls.lib.ld_command.argtypes=[c.c_void_p,c.POINTER(Command)];cls.lib.lt_init.argtypes=[c.POINTER(Clock),TICKS,c.c_void_p,c.c_uint];cls.lib.lt_now.argtypes=[c.c_void_p];cls.lib.lt_now.restype=c.c_uint
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def test_exact_cmd6_r1_and_cmd13_without_unbounded_firmware_wait(self):
  for op,arg,kind in [(6,0x03200101,8),(13,0x10000,1)]:
   f=Fixture(self.lib);self.assertEqual(f.started,0);self.assertEqual(f.command(op,arg,kind),0);self.assertEqual([e for e in f.events if e[0]=='write'],[('write',0x38,arg),('write',0x34,0x02000080|op),('write',0x0c,0x100)]);self.assertEqual(f.request.response[0],0x900)
 def test_frozen_clock_busy_loop_has_hard_iteration_bound_and_no_writes(self):
  f=Fixture(self.lib,busy=True,freeze=True);self.assertEqual(f.started,0);self.assertLess(f.command(),0);self.assertEqual(sum(e==('read',0x3c) for e in f.events),65536);self.assertFalse(any(e[0]=='write' for e in f.events));n=len(f.events);self.assertLess(f.command(),0);self.assertEqual(len(f.events),n)
 def test_event_timeout_late_ready_or_error_latches(self):
  for kw in [{'reply_after':1000},{'event':0x200},{'event':0x500},{'step':20*13000}]:
   f=Fixture(self.lib,**kw);self.assertLess(f.command(),0);n=len(f.events);self.assertLess(f.command(),0);self.assertEqual(len(f.events),n);self.assertFalse(any(e[0]=='write' and e[1] not in [0x0c,0x34,0x38] for e in f.events))
 def test_unrelated_or_stale_error_is_not_acknowledged_or_issued(self):
  for stale in [1,0x200,0x400,0x10001]:
   f=Fixture(self.lib,stale=stale);self.assertLess(f.command(),0);self.assertFalse(any(e[0]=='write' for e in f.events))
  f=Fixture(self.lib,stale=0x100);self.assertEqual(f.command(),0);self.assertEqual([e for e in f.events if e[0]=='write'][0],('write',0x0c,0x100))
 def test_only_exact_flush_status_commands_and_single_attempt_are_allowed(self):
  for kw in [{'op':0},{'arg':0},{'kind':1},{'retries':1},{'timeout':51},{'timeout':0},{'op':13,'arg':0x20000,'kind':1}]:
   f=Fixture(self.lib);self.assertLess(f.command(**kw),0);self.assertEqual(f.events,[])
 def test_clock_wrap_remainder_and_backwards_jump(self):
  for sequence,want,failed in [([0xffffff00,0xfffffff0,0x32b8],1,0),([1,2,6502,13002],1,0),([1000,1001,900],0,1)]:
   values=iter(sequence);callback=TICKS(lambda _:next(values));clock=Clock();self.assertEqual(self.lib.lt_init(c.byref(clock),callback,None,1),0)
   for _ in range(len(sequence)-2):result=self.lib.lt_now(c.byref(clock))
   self.assertEqual((result,clock.failed),(want,failed))
 def test_clock_stuck_at_initialization_and_missing_admission_are_no_command(self):
  calls=[];callback=TICKS(lambda _:(calls.append(1) or 7));clock=Clock();self.assertLess(self.lib.lt_init(c.byref(clock),callback,None,1),0);self.assertEqual(len(calls),33)
  f=Fixture(self.lib);f.ctx=Driver();f.plan.verified=0;self.assertLess(self.lib.ld_init(c.byref(f.ctx),c.byref(f.plan)),0);self.assertLess(f.command(),0);self.assertEqual(f.events,[])
 def test_uninitialized_command_has_no_callbacks(self):
  f=Fixture(self.lib);f.ctx=Driver();self.assertLess(f.command(),0);self.assertEqual(f.events,[])
 def test_interrupt_consumer_or_active_dma_rejects_admission(self):
  for kw in [{'interrupts':0x100},{'dma':1}]:
   f=Fixture(self.lib,**kw);self.assertLess(f.started,0);self.assertLess(f.command(),0);self.assertFalse(any(e[0]=='write' for e in f.events))
 def test_programming_status_is_paced_and_frozen_counter_fails(self):
  f=Fixture(self.lib,response=0xe00);self.assertEqual(f.command(13,0x10000,1),0);self.assertEqual(f.request.response[0],0xe00)
  f=Fixture(self.lib,response=0xe00,freeze=True);self.assertLess(f.command(13,0x10000,1),0);n=len(f.events);self.assertLess(f.command(13,0x10000,1),0);self.assertEqual(len(f.events),n)
if __name__=='__main__':unittest.main()
