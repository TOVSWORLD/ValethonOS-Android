#!/usr/bin/env python3
"""Execute pinned byte wrappers with modeled block hardware and exact target guards."""
import argparse,hashlib,json,struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from validate_loader_checkpoint import elf,SAVED
from validate_loader_allocator import EXPECTED
import retained_log_mailbox as m
BASE,STOP,RAWREAD,RAWWRITE=0x4bd00000,0x50000000,0x50000100,0x50000200
CTX,PLAN,OPS,HASH,BUFFER,OUT,INPUT,DEVICE,BDEV=0x41100000,0x41100100,0x41100200,0x41100300,0x41104000,0x41106000,0x41108000,0x41110000,0x41110100
class Disk:
 def __init__(self,segments,symbols,lk,short_read=False,short_write=False,first=8192,relocation=0):
  self.u=u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);self.symbols={k:v+relocation for k,v in symbols.items()};self.short_read=short_read;self.short_write=short_write;self.events=[];self.image=bytearray(m.PARTITION);self.first=first
  for at,n in [(0x40ff0000,0x20000),(0x41100000,0x20000),(BASE,0x90000),(0x41fe0000,0x20000),(STOP,0x1000)]:u.mem_map(at,n)
  if relocation:u.mem_map(0x40ff0000+relocation,0x20000)
  for at,b in segments:u.mem_write(at+relocation,b)
  u.mem_write(BASE,lk[512:]);u.mem_write(DEVICE,struct.pack('<3I',0,0,BDEV));u.mem_write(BDEV,struct.pack('<5I',0,512,0,RAWREAD|1,RAWWRITE|1));u.mem_write(PLAN,struct.pack('<I4xQ5I4x',DEVICE,first,m.PARTITION,5,8,1,1));u.mem_write(HASH,struct.pack('<II',self.symbols['lh_block'],1));u.hook_add(UC_HOOK_CODE,self.hook);u.hook_add(UC_HOOK_MEM_WRITE,self.write)
  self.call('lp_pinned_ops',[OPS])
  self.started=self.call('lp_init',[CTX,PLAN,OPS,HASH,BUFFER,4096])
 def write(self,u,access,at,n,value,data):assert (0x41100000<=at and at+n<=0x41120000) or (0x41fe0000<=at and at+n<=0x42000000),hex(at)
 def hook(self,u,at,size,data):
  if at not in [RAWREAD,RAWWRITE]:return
  dev,lba,count,ptr=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];hw=struct.unpack('<I',u.mem_read(u.reg_read(UC_ARM_REG_SP),4))[0];offset=(lba-self.first)*512;n=count*512
  assert dev==0 and hw==8 and 0<=offset and offset+n<=m.PARTITION and n>0
  self.events.append(('read' if at==RAWREAD else 'write',offset,n,hw));result=count
  if at==RAWREAD:
   if self.short_read:result=count-1
   else:u.mem_write(ptr,bytes(self.image[offset:offset+n]))
  else:
   assert m.SLOT_BASE<=offset and offset+n<=m.GUARD
   self.image[offset:offset+n]=u.mem_read(ptr,n)
   if self.short_write:result=count-1
  u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def call(self,name,args):
  u=self.u
  for i,r in enumerate(SAVED):u.reg_write(r,0xabc00000+i)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
  sp=0x41fff000
  if len(args)>4:u.mem_write(sp,struct.pack('<'+'I'*len(args[4:]),*args[4:]))
  u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,STOP|1);u.emu_start(self.symbols[name]|1,STOP,count=getattr(self,"instruction_budget",1000000),timeout=20000000)
  assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==sp,(hex(u.reg_read(UC_ARM_REG_PC)),hex(u.reg_read(UC_ARM_REG_SP)))
  assert all(u.reg_read(r)==0xabc00000+i for i,r in enumerate(SAVED));v=u.reg_read(UC_ARM_REG_R0);return v-(1<<32) if v>>31 else v

def validate(path,lk_path):
 lk=lk_path.read_bytes();assert hashlib.sha256(lk).hexdigest()==EXPECTED
 seg,sym=elf(path,('lp_init','lp_context_bytes','lp_pinned_ops','lp_read','lp_read_absolute','lp_write','lp_prefix','lh_block'));cases=[]
 f=Disk(seg,sym,lk);assert f.started==0;f.image[:4096]=bytes(i%251 for i in range(4096));assert f.call('lp_read',[CTX,0,OUT,4096])==0 and bytes(f.u.mem_read(OUT,4096))==bytes(f.image[:4096]);cases.append('exact_aligned_read_wrapper')
 f=Disk(seg,sym,lk);offset=m.SLOT_BASE+4096;f.image[offset:offset+512]=bytes(range(256))*2;f.u.mem_write(OUT,b'z'*180);assert f.call('lp_read',[CTX,offset,OUT+1,162])==0 and bytes(f.u.mem_read(OUT+1,162))==bytes(range(162)) and bytes(f.u.mem_read(OUT+163,16))==b'z'*16;assert f.events==[('read',offset,512,8)];cases.append('partial_payload_owned_bounce')
 f=Disk(seg,sym,lk);f.u.mem_write(INPUT,b'a'*4096);assert f.call('lp_write',[CTX,m.SLOT_BASE,INPUT,4096])==0 and f.image[m.SLOT_BASE:m.SLOT_BASE+4096]==b'a'*4096;cases.append('exact_aligned_write_wrapper')
 f=Disk(seg,sym,lk);absolute=f.first*512+12*1024*1024;assert f.call('lp_read_absolute',[CTX,0,absolute,0,OUT,4608])==0 and f.events==[('read',12*1024*1024,4608,8)];cases.append('absolute_blob_read')
 for operation,kw in [('lp_read',{'short_read':True}),('lp_write',{'short_write':True})]:
  f=Disk(seg,sym,lk,**kw);args=[CTX,0 if operation=='lp_read' else m.SLOT_BASE,OUT if operation=='lp_read' else INPUT,4096];assert f.call(operation,args)<0;assert f.call(operation,args)<0 and len(f.events)==1;cases.append('short_result_no_retry_'+operation)
 f=Disk(seg,sym,lk);assert f.call('lp_write',[CTX,m.BASE,INPUT,4096])<0 and not f.events;cases.append('seed_write_rejected')
 f=Disk(seg,sym,lk);assert f.call('lp_read_absolute',[CTX,0,absolute,1,OUT,4608])<0 and not f.events;cases.append('high64_not_truncated')
 f=Disk(seg,sym,lk,first=0xffffffff);assert f.started<0 and f.call('lp_read',[CTX,0,OUT,4096])<0 and not f.events;cases.append('lba32_extent_guard')
 f=Disk(seg,sym,lk,short_read=True);assert f.call('lp_prefix',[CTX,INPUT])<0 and len(f.events)==1 and f.events[0]==('read',0,4096,8);cases.append('prefix_first_short_read_stops')
 return {'scope':'Actual guarded C adapter and exact archived byte read/write wrappers; block hardware modeled','elf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'lk_sha256':EXPECTED,'read_entry':'0x4bd358e8','write_entry':'0x4bd35a88','cases':cases,'case_count':len(cases),'native_tests':9,'physical_context_bytes':f.call('lp_context_bytes',[]),'mmc_partition':8,'gpt_partition':5,'writes_confined_to_mailbox_slots':True,'read_partial_uses_owned_aligned_bounce':True,'lba32_extent_verified':True,'callee_saved_sp_preserved':True,'hardware_driver_dma_timing_or_card_bindings_qualified':False,'device_accessed':False,'physical_commands':False,'full_prefix_native_only_with_modeled_compression':True}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--lk',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=validate(a.elf,a.lk);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Pinned byte I/O adapter controls passed:',r['case_count'])
