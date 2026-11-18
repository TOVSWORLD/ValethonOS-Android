#!/usr/bin/env python3
"""Compose guarded module with exact byte/command wrappers; model block hardware."""
import argparse,hashlib,json,struct
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
from validate_loader_physical import Disk,PLAN,OPS,HASH,INPUT
from validate_loader_checkpoint import elf
from validate_loader_allocator import EXPECTED
from validate_loader_relocation import relative_references
import retained_log_mailbox as m
STATE,CFG,CARD,POINT,CLOCK=0x41101000,0x41100400,0x41100500,0x41100600,0x50000400
class Firmware(Disk):
 instruction_budget=40000000
 def __init__(self,segments,symbols,lk,**kw):
  super().__init__(segments,symbols,lk,**kw);self.commands=[];self.pending=False;self.prefix_checks=0;self.nonce=bytes(range(32));image=bytearray(m.PARTITION);image[:8]=b'ANDROID!';image,self.prefix=m.prepare(bytes(image),self.nonce,b'VALETHON HOST CONTROL v1\nThis is a preinstalled retention control, NOT a kernel log.\n');self.image=bytearray(image);self.stable=image
  u=self.u;u.mem_write(CFG,struct.pack('<32s32sQQ5I',self.nonce,bytes.fromhex(self.prefix),8192,100000,m.PARTITION,5,8,1,1)+bytes(4));u.mem_write(CARD,struct.pack('<9I',0x111,0x4bd395f5,CLOCK|1,1,1024,1,1,1,0));u.hook_add(UC_HOOK_CODE,self.services)
 def services(self,u,at,size,data):
  if at==(self.symbols['lp_prefix']&~1):
   self.prefix_checks+=1;expected=bytes(u.mem_read(u.reg_read(UC_ARM_REG_R1),32));assert expected==hashlib.sha256(self.image[:m.BASE]).digest();u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  elif at==CLOCK:u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  elif at==0x4bd38020:
   p=u.reg_read(UC_ARM_REG_R1);q=struct.unpack('<9I',u.mem_read(p,36));self.commands.append((q[0],q[1],q[2],q[7],q[8]));assert (q[0],q[1],q[2],q[7],q[8]) in [(13,0x10000,1,50,0),(6,0x03200101,8,50,0)]
   if q[0]==6:self.pending=True;status=0
   else:
    status=0x900
    if self.pending:self.stable=bytes(self.image);self.pending=False
   u.mem_write(p+12,struct.pack('<I',status));u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def start_module(self):return self.call('lfw_start',[STATE,CFG,PLAN,OPS,HASH,CARD])
 def emit(self,stage,mode=0):
  self.u.mem_write(POINT,struct.pack('<7I4x3Q',stage,mode,0,0,0,0,0,0,0,0));return self.call('lfw_emit',[STATE,POINT])
def validate(path,objects,lk_path):
 lk=lk_path.read_bytes();assert hashlib.sha256(lk).hexdigest()==EXPECTED;kinds={};provenance={}
 for obj in objects:
  raw=obj.read_bytes();provenance[obj.name]=hashlib.sha256(raw).hexdigest()
  for kind,n in relative_references(raw).items():kinds[kind]=kinds.get(kind,0)+n
 names=('lp_init','lp_context_bytes','lp_pinned_ops','lp_read','lp_read_absolute','lp_write','lp_prefix','lh_block','lfw_start','lfw_emit','lfw_state_bytes');seg,sym=elf(path,names);cases=[]
 for delta in [0,0x2000000]:
  f=Firmware(seg,sym,lk,relocation=delta);assert f.start_module()==0 and f.emit(1)==0 and f.emit(3)==0;assert m.inspect(f.stable,f.nonce,f.prefix)['latest']['sequence']==3 and len(f.commands)==18 and f.prefix_checks==1;cases.append('complete_module_wrappers_at_'+hex(0x41000000+delta))
 for kw in [{'short_read':True},{'short_write':True}]:
  f=Firmware(seg,sym,lk,**kw);assert f.start_module()==0 and f.emit(1)<0;n=(len(f.events),len(f.commands));assert f.emit(3)<0 and (len(f.events),len(f.commands))==n;assert m.inspect(f.stable,f.nonce,f.prefix)['latest']['sequence']==1;cases.append('whole_module_stop_'+next(iter(kw)))
 f=Firmware(seg,sym,lk);f.u.mem_write(CFG+64,struct.pack('<Q',9000));assert f.start_module()<0 and f.emit(1)<0 and not f.events and not f.commands;cases.append('inconsistent_target_no_io')
 f=Firmware(seg,sym,lk);assert f.emit(1)<0 and f.start_module()==0 and f.start_module()<0 and f.emit(1)<0 and not f.events;cases.append('uninitialized_and_repeat_start_no_io')
 f=Firmware(seg,sym,lk);assert f.start_module()==0
 for mode in [2,6,99]:assert f.emit(1,mode)==1 and not f.events and not f.commands
 cases.append('non_normal_modes_no_io')
 return {'scope':'Actual composed PIC module and archived byte/command wrappers; hardware, clock and prefix digest modeled in this ARM composition','profile':'firmware','elf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'object_sha256':provenance,'allocated_input_relocation_types':kinds,'lk_sha256':EXPECTED,'cases':cases,'case_count':len(cases),'native_composition_tests':4,'state_bytes':f.call('lfw_state_bytes',[]),'entry_symbols':['lfw_start','lfw_emit'],'prefix_digest_modeled_here':True,'full_prefix_native_c_stream_tested_separately':True,'actual_sha_stream_vectors_tested_separately':True,'writes_confined_to_slots':True,'mode_handoff_sequence':3,'callee_saved_sp_preserved':True,'physical_timing_card_dma_or_placement_qualified':False,'device_accessed':False,'physical_commands':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--object',type=Path,action='append',required=True);p.add_argument('--lk',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=validate(a.elf,a.object,a.lk);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Firmware-target module controls passed:',r['case_count'])
