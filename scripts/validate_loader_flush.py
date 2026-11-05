#!/usr/bin/env python3
"""Replay checked adapter through archived LK command wrapper with modeled driver."""
import argparse,hashlib,json,struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from validate_loader_checkpoint import elf,SAVED
LK_BASE=0x4bd00000
LK_HASH='7637da8754a7494f8907d07c7b25532476959956d1cfea856ab8ea6940176056'
CTX,CLOCK,STOP=0x41100000,0x50001000,0x50002000
class Fixture:
 def __init__(self,segments,symbols,lk,statuses,error=0,tick=0,admitted=1):
  self.u=u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);self.symbols=symbols;self.statuses=list(statuses);self.events=[];self.error=error;self.tick=tick;self.time=0
  for at,size in [(0x40ff0000,0x20000),(0x41100000,0x20000),(0x41fe0000,0x20000),(LK_BASE,0x80000),(0x50000000,0x10000)]:u.mem_map(at,size)
  for at,data in segments:u.mem_write(at,data)
  u.mem_write(LK_BASE,lk[512:]);u.mem_write(CTX,struct.pack('<9I',0x111,0x4bd395f5,CLOCK|1,1,1024,1,admitted,admitted,0));u.hook_add(UC_HOOK_CODE,self.hook)
 def hook(self,u,at,size,data):
  if at==0x4bd38020:
   assert u.reg_read(UC_ARM_REG_R0)==0x111
   ptr=u.reg_read(UC_ARM_REG_R1);q=struct.unpack('<9I',u.mem_read(ptr,36));self.events.append((q[0],q[1],q[2],q[7],q[8]));assert q[7:]==(50,0)
   status=self.statuses.pop(0) if self.statuses else 0xe00;u.mem_write(ptr+12,struct.pack('<I',status));self.time+=self.tick;u.reg_write(UC_ARM_REG_R0,9 if len(self.events)==self.error else 0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  elif at==CLOCK:u.reg_write(UC_ARM_REG_R0,self.time);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def call(self):
  u=self.u
  for i,r in enumerate(SAVED):u.reg_write(r,0xaab00000+i)
  u.reg_write(UC_ARM_REG_R0,CTX);u.reg_write(UC_ARM_REG_SP,0x41fff000);u.reg_write(UC_ARM_REG_LR,STOP|1);u.emu_start(self.symbols['lf_flush']|1,STOP,count=1000000)
  assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==0x41fff000
  assert all(u.reg_read(r)==0xaab00000+i for i,r in enumerate(SAVED));v=u.reg_read(UC_ARM_REG_R0);return v-(1<<32) if v>>31 else v

def validate(path,lk_path):
 lk=lk_path.read_bytes();assert hashlib.sha256(lk).hexdigest()==LK_HASH
 seg,sym=elf(path,('lf_flush',));passed=[]
 for name,statuses,error,tick,admitted,success,count in [
  ('fresh_ready',[0x900,0,0x900],0,0,1,True,3),
  ('busy_then_ready',[0x900,0,0xe00,0x900],0,0,1,True,4),
  ('never_ready_even_zero_returns',[0x900,0]+[0xe00]*8,0,0,1,False,1002),
  ('cmd6_transport_failure',[0x900,0],2,0,1,False,2),
  ('status_transport_failure',[0x900,0,0x900],3,0,1,False,3),
  ('switch_error',[0x900,0x80],0,0,1,False,2),
  ('status_error',[0x900,0,0x80000900],0,0,1,False,3),
  ('elapsed_even_ready',[0x900,0,0x900],0,400,1,False,3),
  ('unadmitted',[],0,0,0,False,0)]:
  f=Fixture(seg,sym,lk,statuses,error,tick,admitted);r=f.call();assert (r==0)==success and len(f.events)==count
  assert sum(x[0]==6 for x in f.events)<=1
  for op,arg,resp,timeout,retries in f.events:assert (op,arg,resp) in [(13,0x10000,1),(6,0x03200101,8)]
  if not success:n=len(f.events);assert f.call()<0 and len(f.events)==n
  passed.append(name)
 return {'scope':'Actual linked Thumb adapter through exact archived LK command wrapper; hardware driver and clock modeled','elf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'lk_sha256':LK_HASH,'cases':passed,'case_count':len(passed),'actual_wrapper':'0x4bd395f4','no_original_switch_poll_used':True,'single_cmd6_no_retry':True,'fresh_post_cmd13_required':True,'callee_saved_sp_preserved':True,'bindings_clock_placement_hardware_qualified':False,'device_accessed':False,'physical_commands':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--lk',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=validate(a.elf,a.lk);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Checked adapter ARM controls passed:',r['case_count'])
