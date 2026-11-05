"""Full composed native writer using bounded command-only driver and clock."""
import ctypes as c,shutil,subprocess,tempfile,unittest
from pathlib import Path
import test_loader_firmware_module as base
from test_loader_checkpoint import Config,Point
from test_loader_physical import Plan as DiskPlan,Ops,Hash
from test_loader_command import Plan as CommandPlan,Driver,Fixture as Controller,WRITE,READ
ROOT=Path(__file__).resolve().parents[1]
class ServicePlan(c.Structure):_fields_=[('command',CommandPlan),('cache_size',c.c_uint),('cache_enabled',c.c_uint)]
class TimedModule(base.FirmwareModule):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();out=Path(cls.temp.name)/'timed.so';cc=shutil.which('clang') or shutil.which('cc')
  if not cc:raise unittest.SkipTest('C compiler unavailable')
  names=['checkpoint.c','mmc_flush.c','module.c','hash-stream.c','physical.c','firmware-module.c','clock.c','command.c','timed-module.c','identity.c'];subprocess.run([cc,'-shared','-fPIC','-O2',*[str(ROOT/'projects/firetabs-android/loader-retained'/s) for s in names],'-o',str(out)],check=True,capture_output=True);cls.lib=c.CDLL(str(out));cls.lib.lp_context_bytes.restype=c.c_ulong;cls.lib.lp_init.argtypes=[c.c_void_p,c.POINTER(DiskPlan),c.POINTER(Ops),c.POINTER(Hash),c.c_void_p,c.c_uint];cls.lib.lfw_state_bytes.restype=c.c_ulong;cls.lib.lft_state_bytes.restype=c.c_ulong;cls.lib.lft_start.argtypes=[c.c_void_p,c.POINTER(Config),c.POINTER(DiskPlan),c.POINTER(Ops),c.POINTER(Hash),c.POINTER(ServicePlan)];cls.lib.lft_emit.argtypes=[c.c_void_p,c.POINTER(Point)];cls.lib.ld_init.argtypes=[c.POINTER(Driver),c.POINTER(CommandPlan)]
 def fixture(self,**kw):
  f=super().fixture(**kw);f.state=c.create_string_buffer(self.lib.lft_state_bytes());f.controller=Controller(self.lib);original=f.controller.callbacks[1];original_read=f.controller.callbacks[0];f.native_opcode=0
  def record(context,off,value):
   if off==0x34:
    f.native_opcode=value&63;f.commands.append((value&63,0,0))
    if f.native_opcode==6:f.pending=True
   original(context,off,value)
  def read(context,off):
   value=original_read(context,off)
   if off==0x40 and f.native_opcode==13 and f.pending and value==0x900:f.stable=bytes(f.image);f.pending=False
   return value
  f.command_read=READ(read);f.controller.plan.read=f.command_read
  f.command_write=WRITE(record);f.original_command_write=original;f.controller.plan.write=f.command_write;f.services=ServicePlan(f.controller.plan,1024,1);return f
 def start(self,f):return self.lib.lft_start(f.state,c.byref(f.config),c.byref(f.plan),c.byref(f.ops),c.byref(f.hash),c.byref(f.services))
 def emit(self,f,stage):return self.lib.lft_emit(f.state,c.byref(Point(stage,0,0,0,0,0,0,0,0,0)))
class BoundIdentity(TimedModule):
 def test_identity_match_starts_and_mismatch_consumes_attempt_before_io(self):
  from test_loader_identity import Plan as IdentityPlan,Reader,READ as IdentityRead
  self.lib.lft_start_bound.argtypes=self.lib.lft_start.argtypes+[c.POINTER(IdentityPlan),c.POINTER(Reader)]
  for mismatch in [False,True]:
   f=self.fixture();p=IdentityPlan(0x1234,0x2000,0x3000,0x4000)
   fields={(0x1238,4):0,(0x123c,4):0x4000,(0x2000,4):0x3000,(0x3028,4):0x11230000,(0x2018,4):2 if mismatch else 1,(0x201c,4):1,(0x210c,1):8,(0x206d,1):1,(0x2145,4):1024}
   def read(_,at,out,n):
    if (at,n) not in fields:return -1
    v=fields[at,n]
    for i in range(n):out[i]=(v>>(8*i))&255
    return 0
   cb=IdentityRead(read);reader=Reader(None,cb)
   result=self.lib.lft_start_bound(f.state,c.byref(f.config),c.byref(f.plan),c.byref(f.ops),c.byref(f.hash),c.byref(f.services),c.byref(p),c.byref(reader))
   if mismatch:
    self.assertLess(result,0);self.assertEqual(f.commands,[]);self.assertLess(self.start(f),0)
   else:self.assertEqual(result,0);self.assertEqual(self.emit(f,1),0)
if __name__=='__main__':unittest.main()

