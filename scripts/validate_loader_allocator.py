#!/usr/bin/env python3
"""Replay archived allocator against an explicitly modeled initialized free list."""
import argparse,hashlib,json,struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
BASE,HEAP,POOL,SIZE,COUNTER,STOP=0x4bd00000,0x4bd862fc,0x4c000000,0x100000,0x4bd74d98,0x50000000
EXPECTED='7637da8754a7494f8907d07c7b25532476959956d1cfea856ab8ea6940176056'
SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
class Model:
 def __init__(self,blob,extra_write_regions=()):
  self.extra_write_regions=list(extra_write_regions)
  self.u=u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(BASE,0x180000);u.mem_write(BASE,blob[512:]);u.mem_map(POOL,SIZE);u.mem_map(0x41fe0000,0x20000);u.mem_map(STOP,0x1000);head=HEAP+8
  u.mem_write(head,struct.pack('<II',POOL,POOL));u.mem_write(POOL,struct.pack('<III',head,head,SIZE));u.mem_write(COUNTER,bytes(4));self.irq=[];self.memory_writes=[];u.hook_add(UC_HOOK_CODE,self.hook);u.hook_add(UC_HOOK_MEM_WRITE,self.write)
 def hook(self,u,at,size,data):
  if at in [0x4bd3c75c,0x4bd3c76c]:self.irq.append(hex(at));u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def write(self,u,access,at,n,value,data):
  assert any(lo<=at and at+n<=hi for lo,hi in [(POOL,POOL+SIZE),(HEAP,HEAP+32),(COUNTER,COUNTER+4),(0x41fe0000,0x42000000)]+self.extra_write_regions),(hex(at),n)
  self.memory_writes.append((at,n))
 def alloc(self,size,alignment=16):
  u=self.u
  for i,r in enumerate(SAVED):u.reg_write(r,0xabc00000+i)
  u.reg_write(UC_ARM_REG_R0,alignment);u.reg_write(UC_ARM_REG_R1,size);u.reg_write(UC_ARM_REG_SP,0x41fff000);u.reg_write(UC_ARM_REG_LR,STOP|1);u.emu_start(0x4bd45bb9,STOP,count=100000)
  assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==0x41fff000
  assert all(u.reg_read(r)==0xabc00000+i for i,r in enumerate(SAVED))
  assert bytes(u.mem_read(COUNTER,4))==bytes(4)
  return u.reg_read(UC_ARM_REG_R0)
def validate(path):
 b=path.read_bytes();assert hashlib.sha256(b).hexdigest()==EXPECTED
 m=Model(b);regions=[]
 for name,n in [('module_capacity',8192),('integrated_module_context',8584),('private_stack_capacity',4096)]:
  at=m.alloc(n);assert at%16==0 and POOL<=at and at+n<=POOL+SIZE
  magic,raw,allocated=struct.unpack('<III',m.u.mem_read(at-12,12));assert magic==0x48454150 and POOL<=raw<=at-12 and raw+allocated>=at+n
  assert all(at+n<=r['address'] or at>=r['address']+r['bytes'] for r in regions)
  regions.append({'name':name,'address':at,'bytes':n,'allocation_header':hex(raw),'allocation_bytes':allocated})
 assert m.alloc(SIZE*2)==0;assert m.alloc(64,3)==0
 return {'scope':'Exact archived allocator with modeled initialized 1MiB free list and IRQ hooks; not actual heap state','lk_sha256':EXPECTED,'aligned_allocator_entry':'0x4bd45bb8','allocation_core':'0x4bd450dc','modeled_regions':regions,'failure_controls':['exhausted_pool_returns_null','non_power_of_two_alignment_returns_null'],'writes_confined_to_modeled_pool_metadata_counter_stack':True,'arm_callee_saved_sp_preserved':True,'irq_operations_modeled':True,'physical_heap_initialized_or_capacity_proved':False,'module_code_loaded':False,'device_accessed':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--lk',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=validate(a.lk);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Allocator module/context/stack and rejection controls passed')
