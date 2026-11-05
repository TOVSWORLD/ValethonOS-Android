#!/usr/bin/env python3
"""Execute actual bridge, archived allocator and loaded module in modeled RAM."""
import argparse,hashlib,json,struct
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
from validate_loader_checkpoint import elf,Machine,READ,WRITE,PREFIX
from validate_loader_allocator import Model,EXPECTED,POOL,SIZE,SAVED,STOP
from validate_loader_module import Integrated,CLOCK as MODULE_CLOCK
import retained_log_mailbox as m
PLAN,IO,OUT,CFG,PHYSICAL,ADAPTER=0x41100000,0x41100100,0x41100200,0x41101000,0x41101100,0x41101200
BREAD,SHA,CACHE,DREAD,DWRITE,DPREFIX,CLOCK=0x50000010,0x50000020,0x50000030,0x50000200,0x50000220,0x50000240,0x50000260
class Bridge(Model):
 def __init__(self,lk,segments,symbols,blob,manifest,failure=None):
  super().__init__(lk,[(0x41100000,0x41120000)]);u=self.u;self.uc=u;self.symbols=symbols;self.blob=blob;self.manifest=manifest;self.failure=failure;self.events=[];self.bridge_events=[];self.commands=[];self.pending=False;self.failure_command=0;self.writes=0;self.flushes=0;self.hashes=0;self.nonce=bytes(range(32))
  image=bytearray(m.PARTITION);image[:8]=b'ANDROID!';image,self.prefix=m.prepare(bytes(image),self.nonce,b'VALETHON HOST CONTROL v1\nThis is a preinstalled retention control, NOT a kernel log.\n');self.image=bytearray(image);self.original=image;self.stable=image
  u.mem_map(0x40ff0000,0x20000);u.mem_map(0x41100000,0x20000)
  for at,data in segments:u.mem_write(at,data)
  entries=manifest['entry_offsets'];u.mem_write(PLAN,struct.pack('<6I32sQQ',len(blob),8584,4096,entries['lm_start'],entries['lm_emit'],1,hashlib.sha256(blob).digest(),8192,12*1024*1024));u.mem_write(IO,struct.pack('<5I',0x111,BREAD|1,0x4bd45bb9,SHA|1,CACHE|1));u.hook_add(UC_HOOK_CODE,self.services)
  if failure=='allocation':u.mem_write(POOL+8,struct.pack('<I',16))
 def services(self,u,at,size,data):
  if at in [BREAD,SHA,CACHE]:
   r=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];self.bridge_events.append(hex(at));rc=0
   if at==BREAD:
    offset=r[2]|r[3]<<32;out,n=struct.unpack('<II',u.mem_read(u.reg_read(UC_ARM_REG_SP),8));assert offset==8192*512+12*1024*1024 and n==len(self.blob) and POOL<=out and out+n<=POOL+SIZE
    if self.failure=='read':rc=-1
    else:u.mem_write(out,self.blob)
   elif at==SHA:
    assert POOL<=r[1] and r[1]+r[2]<=POOL+SIZE
    rc=-1 if self.failure=='sha' or hashlib.sha256(u.mem_read(r[1],r[2])).digest()!=bytes(u.mem_read(r[3],32)) else 0
   else:
    assert POOL<=r[1] and r[1]+r[2]<=POOL+SIZE;rc=-1 if self.failure=='cache' else 0
   u.reg_write(UC_ARM_REG_R0,rc&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  elif at in [DREAD,DWRITE,DPREFIX]:Machine.hook(self,u,{DREAD:READ,DWRITE:WRITE,DPREFIX:PREFIX}[at],size,data)
  elif at in [CLOCK,0x4bd38020]:Integrated.command_hook(self,u,MODULE_CLOCK if at==CLOCK else at,size,data)
 def call_address(self,at,args,sp=0x41fff000):
  u=self.u
  for i,r in enumerate(SAVED):u.reg_write(r,0xabc00000+i)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
  u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,STOP|1);u.emu_start(at|1,STOP,count=40000000,timeout=20000000)
  assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==sp
  assert all(u.reg_read(r)==0xabc00000+i for i,r in enumerate(SAVED));r=u.reg_read(UC_ARM_REG_R0);return r-(1<<32) if r>>31 else r
 def load(self):return self.call_address(self.symbols['lb_load'],[OUT,PLAN,IO])
 def result(self):return struct.unpack('<8I',self.u.mem_read(OUT,32))
 def run_loaded_module(self):
  attempted,loaded,code,state,stack,start,emit,total=self.result();assert loaded==1 and POOL<=code<state<stack<=POOL+SIZE
  u=self.u;u.mem_write(CFG,struct.pack('<32s32sQQ5I',self.nonce,bytes.fromhex(self.prefix),8192,100000,m.PARTITION,5,8,1,1)+bytes(4));u.mem_write(PHYSICAL,struct.pack('<5I',0,DREAD|1,DWRITE|1,0,DPREFIX|1));u.mem_write(ADAPTER,struct.pack('<9I',0x111,0x4bd395f5,CLOCK|1,1,1024,1,1,1,0))
  assert self.call_address(start,[state,CFG,PHYSICAL,ADAPTER],stack)==0
  point=CFG+0x400
  for stage in [1,3]:
   u.mem_write(point,struct.pack('<7I4x3Q',stage,0,0,0,0,0x40000000 if stage==3 else 0,0x44000000 if stage==3 else 0,0,0,0));assert self.call_address(emit,[state,point],stack)==0
  assert m.inspect(bytes(self.image),self.nonce,self.prefix)['latest']['sequence']==3 and self.writes==6 and self.flushes==6 and len(self.commands)==18

def validate(bridge,lk_path,blob_path,manifest_path):
 lk=lk_path.read_bytes();assert hashlib.sha256(lk).hexdigest()==EXPECTED;seg,sym=elf(bridge,('lb_load',));blob=blob_path.read_bytes();manifest=json.loads(manifest_path.read_text());assert hashlib.sha256(blob).hexdigest()==manifest['blob_sha256'];cases=[]
 f=Bridge(lk,seg,sym,blob,manifest);assert f.load()==0;f.run_loaded_module();cases.append('allocated_verified_loaded_module_commits_on_owned_stack')
 for failure in ['allocation','read','sha','cache']:
  f=Bridge(lk,seg,sym,blob,manifest,failure);assert f.load()<0;assert f.result()[1]==0 and f.result()[5:7]==(0,0);n=len(f.bridge_events);assert f.load()<0 and len(f.bridge_events)==n;assert not f.commands;cases.append('no_publish_no_retry_'+failure)
 return {'scope':'Actual ARM bridge + archived allocator + dynamically loaded PIC module; driver/clock/storage/hash/cache/IRQ modeled','bridge_elf_sha256':hashlib.sha256(bridge.read_bytes()).hexdigest(),'module_blob_sha256':hashlib.sha256(blob).hexdigest(),'lk_sha256':EXPECTED,'cases':cases,'case_count':len(cases),'native_bridge_tests':5,'owned_allocation_and_private_stack_used_in_model':True,'loader_sequence_after_mode_handoff':3,'arm_callee_saved_sp_preserved':True,'actual_firmware_hash_cache_clock_heap_bindings_qualified':False,'device_accessed':False,'physical_commands':False,'candidate_boot_modified':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--lk',type=Path,required=True);p.add_argument('--blob',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=validate(a.elf,a.lk,a.blob,a.manifest);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Allocated bridge/module controls passed:',r['case_count'])
