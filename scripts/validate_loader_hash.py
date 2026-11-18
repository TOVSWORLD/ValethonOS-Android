#!/usr/bin/env python3
"""Hash known vectors using actual pinned generic ARM compression, no modeled hash."""
import argparse,hashlib,json,struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from validate_loader_checkpoint import elf,SAVED
BASE=0x4bd00000
EXPECTED='7637da8754a7494f8907d07c7b25532476959956d1cfea856ab8ea6940176056'
CTX,EXPECTED_AT,INPUT,STOP=0x41100000,0x41100100,0x43000000,0x50000000
class Hash:
 def __init__(self,segments,symbols,lk):
  self.u=u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);self.symbols=symbols;self.calls=0;self.data_reads=0
  for at,n in [(0x40ff0000,0x20000),(0x41100000,0x10000),(INPUT,0x10000),(0x41fe0000,0x20000),(BASE,0x80000),(STOP,0x1000)]:u.mem_map(at,n)
  for at,b in segments:u.mem_write(at,b)
  u.mem_write(BASE,lk[512:]);u.mem_write(CTX,struct.pack('<II',symbols['lh_block'],1));u.hook_add(UC_HOOK_CODE,self.code);u.hook_add(UC_HOOK_MEM_READ,self.read);u.hook_add(UC_HOOK_MEM_WRITE,self.write)
 def code(self,u,at,size,data):
  if at==0x4bd15620:self.calls+=1
  # Generic entry must never run the original capability dispatch or other
  # hardware-specific compression paths.
  if BASE<=at<BASE+0x80000:assert 0x4bd15620<=at<0x4bd16400,hex(at)
 def read(self,u,access,at,n,value,data):
  if BASE<=at<BASE+0x80000:assert 0x4bd154e0<=at and at+n<=0x4bd155e0,hex(at)
  self.data_reads+=1
 def write(self,u,access,at,n,value,data):
  assert 0x41fe0000<=at and at+n<=0x42000000,hex(at)
 def run(self,payload,digest=None,verified=1,n_override=None):
  u=self.u;u.mem_write(INPUT,payload or b'\0');u.mem_write(EXPECTED_AT,digest if digest is not None else hashlib.sha256(payload).digest());u.mem_write(CTX,struct.pack('<II',self.symbols['lh_block'],verified));calls=self.calls
  for i,r in enumerate(SAVED):u.reg_write(r,0xabc00000+i)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[CTX,INPUT,len(payload) if n_override is None else n_override,EXPECTED_AT]):u.reg_write(r,v)
  u.reg_write(UC_ARM_REG_SP,0x41fff000);u.reg_write(UC_ARM_REG_LR,STOP|1);u.emu_start(self.symbols['lh_equal']|1,STOP,count=10000000,timeout=20000000)
  assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==0x41fff000
  assert all(u.reg_read(r)==0xabc00000+i for i,r in enumerate(SAVED));v=u.reg_read(UC_ARM_REG_R0);return (v-(1<<32) if v>>31 else v),self.calls-calls

def validate(path,lk_path):
 lk=lk_path.read_bytes();assert hashlib.sha256(lk).hexdigest()==EXPECTED
 seg,sym=elf(path,('lh_equal','lh_block'));f=Hash(seg,sym,lk);cases=[]
 for name,payload in [('empty',b''),('abc',b'abc'),*[(str(n)+'_bytes',bytes(i%251 for i in range(n))) for n in [55,56,63,64,65,128,4608]]]:
  rc,calls=f.run(payload);assert rc==0 and calls==(1 if len(payload)<64 else 2);cases.append(name)
 payload=bytes(i%251 for i in range(4608));wrong=bytearray(hashlib.sha256(payload).digest());wrong[0]^=1;assert f.run(payload,bytes(wrong))[0]<0;cases.append('wrong_digest_rejected')
 assert f.run(payload,verified=0)==(-1,0);cases.append('unverified_binding_no_compression')
 assert f.run(payload,n_override=16*1024*1024+1)==(-1,0);cases.append('oversize_no_compression')
 return {'scope':'Actual SHA framing, Thumb thunk and pinned generic ARM compression instructions; hashlib known-vector comparison only','lk_sha256':EXPECTED,'elf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'generic_entry':'0x4bd15620','cases':cases,'case_count':len(cases),'digest_computation_modeled':False,'no_capability_dispatch_or_global_reads':True,'firmware_reads_only_round_constants':True,'writes_only_private_stack':True,'callee_saved_sp_preserved':True,'runtime_code_placement_and_service_admission_qualified':False,'device_accessed':False,'physical_commands':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--lk',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=validate(a.elf,a.lk);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Actual firmware generic SHA controls passed:',r['case_count'])
