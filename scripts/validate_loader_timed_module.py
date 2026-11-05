#!/usr/bin/env python3
"""Compose writer/target adapter with actual bounded clock/command driver."""
import argparse,hashlib,json
from pathlib import Path
from unicorn import UC_HOOK_MEM_READ
from validate_loader_firmware_module import Firmware,STATE,CFG,PLAN,OPS,HASH,CARD,POINT
from validate_loader_physical import Disk
from validate_loader_command import Controller,MMC
from validate_loader_checkpoint import elf
from validate_loader_relocation import relative_references
from validate_loader_allocator import EXPECTED
import struct
import retained_log_mailbox as m
class Timed(Firmware):
 def __init__(self,segments,symbols,lk,**kw):
  super().__init__(segments,symbols,lk,**kw)
  self.busy=False;self.interrupts=0;self.dma=0;self.event=0x100;self.freeze_after=0;self.step=13000;self.ticks=0;self.samples=0;self.pending=0;self.active=False;self.op=0;self.programming=0;self.writes=[];self.reads={};self.cache_pending=False
  self.u.mem_map(0x10008000,0x1000);self.u.mem_map(MMC,0x1000);self.u.hook_add(UC_HOOK_MEM_READ,self.read)
  self.u.mem_write(CARD,struct.pack('<10I',0,0,0,0,0,1,512,1,1024,1));self.call('ld_pinned_services',[CARD])
 def services(self,u,at,size,data):
  assert at!=0x4bd38020,'Legacy unbounded command driver reached'
  super().services(u,at,size,data)
 def read(self,u,access,at,n,value,data):
  Controller.read(self,u,access,at,n,value,data)
  if at==MMC+0x40 and self.op==13 and self.cache_pending and int.from_bytes(u.mem_read(at,4),'little')==0x900:self.stable=bytes(self.image);self.cache_pending=False
 def write(self,u,access,at,n,value,data):
  if MMC<=at<MMC+0x1000:
   Controller.write(self,u,access,at,n,value,data)
   if at==MMC+0x34 and (value&63)==6:self.cache_pending=True
  else:Disk.write(self,u,access,at,n,value,data)
 def start_module(self):return self.call('lft_start',[STATE,CFG,PLAN,OPS,HASH,CARD])
 def emit(self,stage,mode=0):
  self.u.mem_write(POINT,struct.pack('<7I4x3Q',stage,mode,0,0,0,0,0,0,0,0));return self.call('lft_emit',[STATE,POINT])
def validate(path,objects,lk_path):
 lk=lk_path.read_bytes();assert hashlib.sha256(lk).hexdigest()==EXPECTED;kinds={};provenance={}
 for obj in objects:
  raw=obj.read_bytes();provenance[obj.name]=hashlib.sha256(raw).hexdigest()
  for kind,n in relative_references(raw).items():kinds[kind]=kinds.get(kind,0)+n
 names=('lp_init','lp_context_bytes','lp_pinned_ops','lp_read','lp_read_absolute','lp_write','lp_prefix','lh_block','lft_start','lft_emit','lft_state_bytes','ld_pinned_services');seg,sym=elf(path,names);cases=[]
 for delta in [0,0x2000000]:
  f=Timed(seg,sym,lk,relocation=delta);assert f.start_module()==0 and f.emit(1)==0 and f.emit(3)==0;assert m.inspect(f.stable,f.nonce,f.prefix)['latest']['sequence']==3 and f.prefix_checks==1
  assert len([v for off,v in f.writes if off==0x34])==30 and all(off in [0x0c,0x34,0x38] for off,v in f.writes);cases.append('bounded_driver_records_at_'+hex(0x41000000+delta))
 for kw in [{'short_read':True},{'short_write':True}]:
  f=Timed(seg,sym,lk,**kw);assert f.start_module()==0 and f.emit(1)<0;n=(len(f.events),len(f.writes));assert f.emit(3)<0 and (len(f.events),len(f.writes))==n;assert m.inspect(f.stable,f.nonce,f.prefix)['latest']['sequence']==1;cases.append('stop_'+next(iter(kw)))
 f=Timed(seg,sym,lk);f.u.mem_write(CFG+64,struct.pack('<Q',9000));assert f.start_module()<0 and f.emit(1)<0 and not f.events and not f.writes;cases.append('inconsistent_target_no_io')
 f=Timed(seg,sym,lk);assert f.emit(1)<0 and f.start_module()==0 and f.start_module()<0 and f.emit(1)<0 and not f.events and not f.writes;cases.append('one_initialization_only')
 f=Timed(seg,sym,lk);assert f.start_module()==0
 for mode in [2,6,99]:assert f.emit(1,mode)==1 and not f.events and not f.writes
 cases.append('non_normal_modes_no_io')
 f=Timed(seg,sym,lk);f.freeze_after=1;assert f.start_module()<0 and f.emit(1)<0 and not f.events and not f.writes;cases.append('stuck_clock_no_storage_io')
 f=Timed(seg,sym,lk);f.busy=True;assert f.start_module()==0 and f.emit(1)<0;n=(len(f.events),len(f.writes));assert f.emit(3)<0 and (len(f.events),len(f.writes))==n and not f.writes;assert m.inspect(f.stable,f.nonce,f.prefix)['latest']['sequence']==1;cases.append('controller_busy_stop_preserves_previous_record')
 return {'scope':'Actual timed PIC writer/target/clock/flush-command code and archived byte wrappers/GPT sampler; block hardware/counter/controller values and prefix digest modeled','profile':'timed','elf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'object_sha256':provenance,'allocated_input_relocation_types':kinds,'lk_sha256':EXPECTED,'cases':cases,'case_count':len(cases),'native_composition_tests':4,'state_bytes':f.call('lft_state_bytes',[]),'entry_symbols':['lft_start','lft_emit'],'prefix_digest_modeled_here':True,'full_prefix_native_and_actual_sha_stream_tested_separately':True,'legacy_unbounded_command_driver_not_reached':True,'controller_writes_only_command_arg_ack':True,'mode_handoff_sequence':3,'callee_saved_sp_preserved':True,'raw_data_driver_still_original_and_not_termination_qualified':True,'real_card_dma_clock_visibility_or_placement_qualified':False,'device_accessed':False,'physical_commands':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--object',type=Path,action='append',required=True);p.add_argument('--lk',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=validate(a.elf,a.object,a.lk);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Timed composed module controls passed:',r['case_count'])
