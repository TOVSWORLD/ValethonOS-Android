#!/usr/bin/env python3
"""Execute SHA block-stream framing against actual archived compression."""
import argparse,hashlib,json,struct
from pathlib import Path
from unicorn.arm_const import *
from validate_loader_hash import Hash,EXPECTED,CTX,EXPECTED_AT,INPUT,STOP
from validate_loader_checkpoint import elf,SAVED
STATE=CTX+0x200
class Stream(Hash):
 def write(self,u,access,at,n,value,data):assert (0x41fe0000<=at and at+n<=0x42000000) or STATE<=at and at+n<=STATE+64,hex(at)
 def call(self,name,args):
  u=self.u
  for i,r in enumerate(SAVED):u.reg_write(r,0xabc00000+i)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
  u.reg_write(UC_ARM_REG_SP,0x41fff000);u.reg_write(UC_ARM_REG_LR,STOP|1);u.emu_start(self.symbols[name]|1,STOP,count=10000000,timeout=20000000)
  assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==0x41fff000
  assert all(u.reg_read(r)==0xabc00000+i for i,r in enumerate(SAVED));v=u.reg_read(UC_ARM_REG_R0);return v-(1<<32) if v>>31 else v
 def stream(self,payload,chunk,wrong=False):
  self.u.mem_write(EXPECTED_AT,(bytes(32) if wrong else hashlib.sha256(payload).digest()));assert self.call('lhs_init',[STATE,CTX])==0
  for at in range(0,len(payload),chunk):
   b=payload[at:at+chunk];self.u.mem_write(INPUT,b);assert self.call('lhs_add',[STATE,INPUT,len(b)])==0
  return self.call('lhs_finish',[STATE,EXPECTED_AT])
def validate(path,lk_path):
 lk=lk_path.read_bytes();assert hashlib.sha256(lk).hexdigest()==EXPECTED;seg,sym=elf(path,('lh_block','lhs_init','lhs_add','lhs_finish'));f=Stream(seg,sym,lk);cases=[]
 for n,chunk in [(0,64),(64,64),(4096,4096),(8192,8192),(8192,4096),(12288,4096),(32768,8192)]:
  assert f.stream(bytes(i%251 for i in range(n)),chunk)==0;cases.append('bytes_'+str(n)+'_chunk_'+str(chunk))
 assert f.stream(bytes(4096),4096,wrong=True)<0;cases.append('wrong_digest')
 assert f.call('lhs_init',[STATE,CTX])==0;calls=f.calls;assert f.call('lhs_add',[STATE,INPUT,63])<0 and f.call('lhs_add',[STATE,INPUT,64])<0 and f.calls==calls;cases.append('unaligned_chunk_latches')
 assert f.call('lhs_init',[STATE,CTX])==0;f.u.mem_write(STATE+32,struct.pack('<I',16*1024*1024));calls=f.calls;assert f.call('lhs_add',[STATE,INPUT,64])<0 and f.calls==calls;cases.append('total_extent_guard')
 return {'scope':'Actual block-stream C framing and generic archived ARM SHA compression, hashlib comparison','elf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'lk_sha256':EXPECTED,'cases':cases,'case_count':len(cases),'digest_computation_modeled':False,'writes_only_state_and_stack':True,'no_capability_dispatch_or_global_reads':True,'callee_saved_sp_preserved':True,'full_physical_prefix_read_executed':False,'device_accessed':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--lk',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=validate(a.elf,a.lk);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Actual stream/compression controls passed:',r['case_count'])
