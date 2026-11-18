#!/usr/bin/env python3
"""Actual bounded command driver + pinned GPT sampler; modeled controller/counter."""
import argparse,hashlib,json,struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from validate_loader_checkpoint import elf,SAVED
from validate_loader_allocator import EXPECTED
BASE,GPT,MMC,STOP=0x4bd00000,0x10008048,0x11230000,0x50000000
CTX,PLAN,REQUEST,CARD=0x41100000,0x41100100,0x41100200,0x41100300
class Controller:
 def __init__(self,segments,symbols,lk,busy=False,event=0x100,freeze_after=0,step=13000,stale=0,start_ticks=0,interrupts=0,dma=0):
  self.u=u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);self.symbols=symbols;self.busy=busy;self.interrupts=interrupts;self.dma=dma;self.event=event;self.freeze_after=freeze_after;self.step=step;self.ticks=start_ticks;self.samples=0;self.pending=stale;self.active=False;self.op=0;self.programming=0;self.writes=[];self.reads={}
  for at,n in [(0x40ff0000,0x20000),(0x41100000,0x10000),(BASE,0x80000),(0x41fe0000,0x20000),(STOP,0x1000),(0x10008000,0x1000),(MMC,0x1000)]:u.mem_map(at,n)
  for at,b in segments:u.mem_write(at,b)
  u.mem_write(BASE,lk[512:]);u.mem_write(PLAN,struct.pack('<8I',0,0,0,0,0,1,512,1));u.hook_add(UC_HOOK_MEM_READ,self.read);u.hook_add(UC_HOOK_MEM_WRITE,self.write)
  self.call('ld_pinned_services',[PLAN]);self.started=self.call('ld_init',[CTX,PLAN])
 def read(self,u,access,at,n,value,data):
  if at==GPT:
   self.samples+=1
   if not self.freeze_after or self.samples<=self.freeze_after:self.ticks=(self.ticks+self.step)&0xffffffff
   u.mem_write(at,struct.pack('<I',self.ticks));return
  if MMC<=at<MMC+0x1000:
   off=at-MMC;self.reads[off]=self.reads.get(off,0)+1;assert off in [0x0c,0x3c,0x40,0x10,0x98]
   if off==0x10:value=self.interrupts
   elif off==0x98:value=self.dma
   elif off==0x3c:value=3 if self.busy else 0
   elif off==0x0c:
    if self.active and not self.pending:self.pending=self.event
    value=self.pending
   else:
    if self.op==13 and self.programming:self.programming-=1;value=0xe00
    else:value=0x900 if self.op==13 else 0
   u.mem_write(at,struct.pack('<I',value))
 def write(self,u,access,at,n,value,data):
  if MMC<=at<MMC+0x1000:
   off=at-MMC;assert n==4 and off in [0x0c,0x34,0x38];self.writes.append((off,value))
   if off==0x0c:self.pending&=~value;self.active=False
   if off==0x34:
    assert value in [0x02000086,0x0200008d];self.op=value&63;self.active=True
    if self.op==6:self.programming=2
  else:assert (0x41100000<=at and at+n<=0x41110000) or (0x41fe0000<=at and at+n<=0x42000000),hex(at)
 def call(self,name,args):
  u=self.u
  for i,r in enumerate(SAVED):u.reg_write(r,0xabc00000+i)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
  u.reg_write(UC_ARM_REG_SP,0x41fff000);u.reg_write(UC_ARM_REG_LR,STOP|1);u.emu_start(self.symbols[name]|1,STOP,count=40000000,timeout=20000000)
  assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==0x41fff000
  assert all(u.reg_read(r)==0xabc00000+i for i,r in enumerate(SAVED));v=u.reg_read(UC_ARM_REG_R0);return v-(1<<32) if v>>31 else v
 def command(self,op=6,arg=0x03200101,kind=8):self.u.mem_write(REQUEST,struct.pack('<9I',op,arg,kind,0,0,0,0,50,0));return self.call('ld_command',[CTX,REQUEST])
 def flush(self):
  self.u.mem_write(CARD,struct.pack('<9I',CTX,self.symbols['ld_command'],self.symbols['lt_now'],1,1024,1,1,1,0));return self.call('lf_flush',[CARD])
def validate(path,lk_path):
 lk=lk_path.read_bytes();assert hashlib.sha256(lk).hexdigest()==EXPECTED;seg,sym=elf(path,('ld_init','ld_command','ld_context_bytes','ld_pinned_services','lt_now','lf_flush'));cases=[]
 f=Controller(seg,sym,lk);assert f.started==0 and f.command()==0 and f.writes==[(0x38,0x03200101),(0x34,0x02000086),(0x0c,0x100)];cases.append('exact_r1_cmd6_and_cmd_ack_only')
 f=Controller(seg,sym,lk);assert f.started==0 and f.flush()==0;assert [v for off,v in f.writes if off==0x34]==[0x0200008d,0x02000086,0x0200008d,0x0200008d,0x0200008d];cases.append('checked_flush_with_real_gpt_sampler_and_busy_status')
 for kwargs in [{'event':0x200},{'event':0x500},{'stale':1},{'busy':True},{'step':20*13000}]:
  f=Controller(seg,sym,lk,**kwargs);assert f.started==0 and f.command()<0;n=len(f.writes);assert f.command()<0 and len(f.writes)==n;cases.append('stops_'+str(kwargs))
 f=Controller(seg,sym,lk,busy=True,freeze_after=6);assert f.started==0 and f.command()<0 and not f.writes and f.reads[0x3c]==65536;cases.append('frozen_counter_iteration_cap')
 f=Controller(seg,sym,lk,start_ticks=0xffff0000);assert f.started==0 and f.flush()==0;cases.append('gpt_sampler_and_clock_wrap')
 f=Controller(seg,sym,lk,freeze_after=1);assert f.started<0 and not f.writes;cases.append('initial_stuck_counter_rejected')
 for kw in [{'interrupts':0x100},{'dma':1}]:
  f=Controller(seg,sym,lk,**kw);assert f.started<0 and f.command()<0 and not f.writes;cases.append('quiescence_guard_'+str(kw))
 f=Controller(seg,sym,lk);f.programming=1;assert f.command(13,0x10000,1)==0;cases.append('programming_reply_paced')
 f=Controller(seg,sym,lk,freeze_after=6);f.programming=1;assert f.command(13,0x10000,1)<0;cases.append('programming_pace_stuck_counter_stops')
 return {'scope':'Actual clock/command/flush instructions and archived three-read GPT sampler; timer/controller values modeled','elf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'lk_sha256':EXPECTED,'cases':cases,'case_count':len(cases),'native_tests':10,'context_bytes':f.call('ld_context_bytes',[]),'timer_read_address':'0x10008048','controller_base':'0x11230000','controller_writes_only':['CMD interrupt W1C0x0c','ARG0x38','CMD0x34'],'no_timer_reset_dma_or_security_register_writes':True,'r1_cmd6_with_separate_cmd13_busy_poll':True,'old_unbounded_firmware_command_path_not_used':True,'native_clock_wrap_remainder_backward_cases_passed':True,'ordinary_callee_saved_sp_preserved':True,'raw_data_driver_still_original_and_not_termination_qualified':True,'real_hardware_clock_card_or_mmio_qualified':False,'device_accessed':False,'physical_commands':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--lk',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=validate(a.elf,a.lk);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Bounded clock/command controls passed:',r['case_count'])
