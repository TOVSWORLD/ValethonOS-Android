#!/usr/bin/env python3
"""Integrated PIC writer/checked adapter through archived command wrapper."""
import argparse,hashlib,json,struct
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
from validate_loader_checkpoint import elf,Machine,CFG,IO,POINT
from validate_loader_relocation import relative_references
from validate_loader_flush import LK_HASH,LK_BASE
STATE,ADAPTER,CLOCK=0x41104000,0x41113000,0x50005000
class Integrated(Machine):
 def __init__(self,segments,symbols,lk,placement,failure=0):
  super().__init__(segments,symbols,relocation=placement-0x41000000);u=self.uc;u.mem_map(LK_BASE,0x80000);u.mem_write(LK_BASE,lk[512:]);self.commands=[];self.pending=False;self.failure_command=failure
  u.mem_write(ADAPTER,struct.pack('<9I',0x111,0x4bd395f5,CLOCK|1,1,1024,1,1,1,0));u.hook_add(UC_HOOK_CODE,self.command_hook);self.start=self.call('lm_start',[STATE,CFG,IO,ADAPTER])
 def command_hook(self,u,at,size,data):
  if at==CLOCK:u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  elif at==0x4bd38020:
   p=u.reg_read(UC_ARM_REG_R1);q=struct.unpack('<9I',u.mem_read(p,36));self.commands.append((q[0],q[1],q[2],q[7],q[8]));assert q[7:]==(50,0)
   assert (q[0],q[1],q[2]) in [(13,0x10000,1),(6,0x03200101,8)]
   if len(self.commands)==self.failure_command:r=9
   else:
    r=0
    if q[0]==6:self.pending=True;status=0
    else:
     status=0x900
     if self.pending:self.pending=False;self.flushes+=1;self.stable=bytes(self.image)
    u.mem_write(p+12,struct.pack('<I',status))
   u.reg_write(UC_ARM_REG_R0,r);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def emit_module(self,stage):
  self.uc.mem_write(POINT,struct.pack('<7I4x3Q',stage,0,0,0,0,0x40000000 if stage==3 else 0,0x44000000 if stage==3 else 0,0,0,0));return self.call('lm_emit',[STATE,POINT])
def validate(path,objects,lkpath):
 lk=lkpath.read_bytes();assert hashlib.sha256(lk).hexdigest()==LK_HASH
 kinds={};provenance={}
 for obj in objects:
  raw=obj.read_bytes();provenance[obj.name]=hashlib.sha256(raw).hexdigest()
  for kind,n in relative_references(raw).items():kinds[kind]=kinds.get(kind,0)+n
 assert kinds
 seg,sym=elf(path,('lc_init','lc_emit','lc_context_bytes','lm_start','lm_emit','lm_state_bytes'));cases=[]
 for placement in [0x43000000,0x44000000,0x4c100000]:
  f=Integrated(seg,sym,lk,placement);assert f.start==0 and f.emit_module(1)==0 and f.emit_module(3)==0
  assert f.latest()['sequence']==3 and f.writes==6 and f.flushes==6 and len(f.commands)==18 and f.hashes==1
  cases.append('integrated_relocated_'+hex(placement))
 for fail in range(1,10):
  f=Integrated(seg,sym,lk,0x43000000,fail);assert f.start==0 and f.emit_module(1)<0
  n=f.writes;assert len(f.commands)==fail and f.emit_module(3)<0 and f.writes==n and len(f.commands)==fail
  assert f.latest(True)['sequence']>=1;cases.append('stop_at_command_'+str(fail))
 return {'scope':'Integrated actual PIC writer/adapter plus exact archived command wrapper; storage, driver, clock modeled','elf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'lk_sha256':LK_HASH,'object_sha256':provenance,'allocated_input_relocation_types':kinds,'cases':cases,'case_count':len(cases),'state_bytes':f.call('lm_state_bytes',[]),'callee_saved_sp_preserved':True,'old_switch_not_used':True,'no_retry_after_error':True,'physical_memory_bindings_or_durability_qualified':False,'device_accessed':False,'physical_commands':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--object',type=Path,action='append',required=True);p.add_argument('--lk',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=validate(a.elf,a.object,a.lk);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Integrated PIC controls passed:',r['case_count'])
