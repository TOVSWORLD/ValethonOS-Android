#!/usr/bin/env python3
"""Execute cache binding/firmware loop; record modeled CP15 maintenance order."""
import argparse,hashlib,json
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from validate_loader_checkpoint import elf,SAVED
from validate_loader_allocator import EXPECTED
BASE,STOP=0x4bd00000,0x50000000
class Cache:
 def __init__(self,segments,symbols,lk):
  self.u=u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);self.symbols=symbols;self.events=[];self.barriers={}
  for at,n in [(0x40ff0000,0x20000),(BASE,0x80000),(0x41fe0000,0x20000),(STOP,0x1000)]:u.mem_map(at,n)
  for at,b in segments:
   u.mem_write(at,b)
   for i in Cs(CS_ARCH_ARM,CS_MODE_THUMB).disasm(b,at):
    if i.mnemonic in ['dsb','isb']:self.barriers[i.address]=i.mnemonic
  u.mem_write(BASE,lk[512:]);u.hook_add(UC_HOOK_CODE,self.hook);u.hook_add(UC_HOOK_MEM_WRITE,self.write)
 def write(self,u,access,at,n,value,data):assert 0x41fe0000<=at and at+n<=0x42000000,hex(at)
 def hook(self,u,at,size,data):
  if at in [0x4bd3c6f0,0x4bd3c704,0x4bd3c74c]:
   self.events.append(({0x4bd3c6f0:'clean_line',0x4bd3c704:'drain_writes',0x4bd3c74c:'invalidate_icache'}[at],u.reg_read(UC_ARM_REG_R0)));u.reg_write(UC_ARM_REG_PC,at+4)
  elif at in self.barriers:self.events.append((self.barriers[at],0))
 def run(self,address,n):
  u=self.u;self.events=[]
  for i,r in enumerate(SAVED):u.reg_write(r,0xabc00000+i)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],[0x111,address,n]):u.reg_write(r,v)
  u.reg_write(UC_ARM_REG_SP,0x41fff000);u.reg_write(UC_ARM_REG_LR,STOP|1);u.emu_start(self.symbols['lb_cache_sync']|1,STOP,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==0x41fff000
  assert all(u.reg_read(r)==0xabc00000+i for i,r in enumerate(SAVED));v=u.reg_read(UC_ARM_REG_R0);return v-(1<<32) if v>>31 else v

def validate(path,lk_path):
 lk=lk_path.read_bytes();assert hashlib.sha256(lk).hexdigest()==EXPECTED;seg,sym=elf(path,('lb_cache_sync',));f=Cache(seg,sym,lk);cases=[]
 for n in [512,4608,8192]:
  address=0x43000010;assert f.run(address,n)==0;lines=list(range(address&~63,address+n,64));assert f.events==[('clean_line',a) for a in lines]+[('drain_writes',0),('invalidate_icache',0),('dsb',0),('isb',0)];cases.append('clean_drain_invalidate_dsb_isb_'+str(n))
 for address,n in [(0,512),(0x43000010,0),(0x43000010,8193),(0xfffffff0,512)]:assert f.run(address,n)<0 and not f.events;cases.append('invalid_'+hex(address)+'_'+str(n))
 return {'scope':'Actual binding and archived cache loop; CP15 maintenance effects modeled/recorded','elf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'lk_sha256':EXPECTED,'firmware_cache_entry':'0x4bd3c740','cases':cases,'case_count':len(cases),'cache_order':'all covered64B lines clean, drain writes, invalidate I-cache, DSB, ISB','callee_saved_sp_preserved':True,'ordinary_memory_writes_only_stack':True,'cache_visibility_on_hardware_proved':False,'device_accessed':False,'physical_cache_operations':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--lk',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=validate(a.elf,a.lk);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Cache binding/loop controls passed:',r['case_count'])
