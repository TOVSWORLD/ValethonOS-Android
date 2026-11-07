#!/usr/bin/env python3
"""Exact copy -> ROP cache -> resident installer -> bounded screen/module replay."""
import argparse,hashlib,json,struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_ARM,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from audit_loader_copy_boundary import materialize,PAYLOAD_SHA,SITE,LK
from validate_loader_complete import Complete,elf,raw_elf,REGS,BASE
from validate_loader_allocator import EXPECTED
from validate_loader_observer import bl
from validate_loader_physical import STOP
from loader_screen_record import BASE as FB,SURFACE,decode_surface
import audit_resident_loader_payload as a
import retained_log_mailbox as mailbox
PREFIX=0x4bcfe600

def cache_chain(header,payload,lk):
 prefix,ram,_=materialize(header,payload,lk)
 u=Uc(UC_ARCH_ARM,UC_MODE_ARM);u.mem_map(0x4bcf0000,0x190000);u.mem_write(PREFIX,prefix);u.mem_write(LK,bytes(ram));calls=[];lines=[]
 def hook(uc,at,n,data):
  if at==BASE:uc.emu_stop()
  if at==0x4bd3c740:calls.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
  if at in [0x4bd3c6f0,0x4bd3c704,0x4bd3c74c]:
   if at==0x4bd3c6f0:lines.append(uc.reg_read(UC_ARM_REG_R0))
   uc.reg_write(UC_ARM_REG_PC,at+4)
 u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_R3,0x4bcfef50);u.emu_start(0x4bd577f0,BASE,count=100000)
 assert u.reg_read(UC_ARM_REG_PC)==BASE and calls==[(PREFIX,0x1a00)]
 assert lines==list(range(PREFIX,LK,64))
 return len(lines)

def validate(module,bootstrap,old_bootstrap,header_path,lk_path,folder):
 lk=lk_path.read_bytes();assert hashlib.sha256(lk).hexdigest()==EXPECTED
 header=header_path.read_bytes();obs=(folder/'observer-payload-sectors-private.bin').read_bytes();manifest=json.loads((folder/'manifest.json').read_text());nonce=(folder/'nonce.bin').read_bytes();token=int.from_bytes(nonce[:2],'little')
 prefix,ram,extent=materialize(header,obs,lk);sections,bs=raw_elf(bootstrap);seg,_=elf(module,('lfo_frame_dispatch','lfo_state_bytes'));_,sym=raw_elf(module)
 assert all(PREFIX<=at and at+len(data)<=PREFIX+0x900 for at,data in sections)
 assert ram[SITE-LK:SITE-LK+4]==bytes.fromhex('dff82037')
 lines=cache_chain(header,obs,lk);cases=['real_copy_does_not_install_tail_hook','actual_original_rop_cleans_loaded_prefix_'+str(lines)+'_lines']
 # Full resident main uses exact copied bytes. Firmware GPT/read/cache/app
 # callbacks are modeled, never a synthetic late hook installed into RAM.
 for original,mode in [(0,0),(0,2),(6,0)]:
  u,state,word=a.machine(obs[0xa00:0x1800],original_mode=original,lk_mode=mode)
  u.mem_write(PREFIX,prefix);u.mem_write(LK,bytes(ram));u.mem_map(FB,SURFACE*3)
  u.mem_write(0x4bd7c3a0,struct.pack('<I',mode));u.mem_write(0x4be5e20c,struct.pack('<I',original))
  ordered=[]
  def order(uc,at,n,data):
   if at==(bs['lbo_install_hook']&~1):ordered.append('install')
   if at==0x4bd3c740 and state['cache_cleans'][-1][0]==LK:
    ordered.append('lk_cache');assert bytes(uc.mem_read(SITE,4))==(bl(SITE,bs['lbo_pre_shutdown']&~1) if original==0 and mode==0 else bytes.fromhex('dff82037'))
   if at==0x4bd3f1a0:ordered.append('app')
   assert at not in [0x4bd44b3c,0x4bd44b08,0x4bd2266c,0x4bd25f8c,0x4bd25eb8] or mode!=0 or original!=0
  u.hook_add(UC_HOOK_CODE,order);u.emu_start(BASE,a.STOP,count=5000000,timeout=10000000)
  assert state['app'] and ordered==['install','lk_cache'],(state,ordered,hex(u.reg_read(UC_ARM_REG_PC)))
  records=decode_surface(bytes(u.mem_read(FB,SURFACE)),token)
  assert len(records)==1 and records[0]['phase']==1 and records[0]['signed_value']==(0 if original==0 and mode==0 else -1)
  assert all(bytes(u.mem_read(FB+i*SURFACE,SURFACE))==bytes(u.mem_read(FB,SURFACE)) for i in [1,2])
  cases.append('copied_resident_installs_before_original_cache_app_'+str(original)+'_'+str(mode))
 class Fixture(Complete):
  def write(self,u,access,at,n,value,data):
   if PREFIX<=at and at+n<=PREFIX+0x900:return
   if at==SITE:
    assert n==4 and value==int.from_bytes(bl(SITE,self.bs['lbo_pre_shutdown']&~1),'little');self.install_writes+=1;return
   if FB<=at and at+n<=FB+SURFACE*3:
    off=(at-FB)%SURFACE;y,x=divmod(off,3200)
    assert n==4 and y<320 and y%40<32 and x<1024 and value in [0xffffffff,0xff000000]
    self.pixel_writes+=1;return
   super().write(u,access,at,n,value,data)
  def __init__(self,preimage=None,mode=0,badword=False):
   self.install_writes=0;self.pixel_writes=0
   super().__init__(seg,sym,lk,old_bootstrap,obs[0xa00:0x1800],packed=folder)
   self.bs=bs;self.u.mem_write(PREFIX,prefix);self.u.mem_write(LK,bytes(ram));self.u.mem_map(FB,SURFACE*3)
   if preimage is not None:self.u.mem_write(SITE,struct.pack('<I',preimage))
   self.u.mem_write(0x4bd7c3a0,struct.pack('<I',mode))
   if badword:self.u.mem_write(bs['lbo_hook_word'],bytes(4))
   # Source of this runtime branch is actual installer execution, not mem_write.
   self.u.reg_write(UC_ARM_REG_CPSR,0x13);self.u.reg_write(UC_ARM_REG_R0,0)
   self.u.reg_write(UC_ARM_REG_SP,0x41fff000);self.u.reg_write(UC_ARM_REG_LR,STOP|1)
   self.u.emu_start(bs['lbo_install_hook']|1,STOP,count=10000)
   result=self.u.reg_read(UC_ARM_REG_R0);self.install_result=result-(1<<32) if result>>31 else result
   expected=-1 if mode else -2 if preimage is not None else -3 if badword else 0
   assert self.install_result==expected and self.install_writes==int(expected==0)
   self.u.hook_add(UC_HOOK_CODE,self.forbidden)
  def forbidden(self,u,at,n,data):
   assert at not in [0x4bd44b3c,0x4bd44b08,0x4bd2266c,0x4bd25f8c,0x4bd25eb8,0x4bd38020]
  def point(self,masked=False):
   u=self.u;regs=[0xabc00000+i for i in range(13)];regs[11]=0x40080000
   for r,v in zip(REGS,regs):u.reg_write(r,v)
   sp=0x41fff000;u.mem_write(sp+8,struct.pack('<I',0x48000000));flags=0x980a00b3 if masked else 0x980a0033
   u.reg_write(UC_ARM_REG_CPSR,flags);u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,STOP|1)
   def stop(uc,at,n,data):
    if at==SITE+4:uc.emu_stop()
   h=u.hook_add(UC_HOOK_CODE,stop);u.emu_start(SITE|1,STOP,count=80000000,timeout=40000000);u.hook_del(h)
   expected=list(regs);expected[3]=struct.unpack_from('<I',lk,512+0x3eb0c)[0]
   assert u.reg_read(UC_ARM_REG_PC)==SITE+4 and [u.reg_read(r) for r in REGS]==expected and u.reg_read(UC_ARM_REG_SP)==sp
   assert u.reg_read(UC_ARM_REG_CPSR)&0xf80f00c0==flags&0xf80f00c0
   return decode_surface(bytes(u.mem_read(FB,SURFACE)),token)
 for kw in [{'preimage':0x12345678},{'mode':2},{'mode':99},{'badword':True}]:
  f=Fixture(**kw);assert not f.install_writes and not f.events and not f.writes
 cases.append('runtime_preimage_mode_and_unbound_branch_guards_stop_without_writes')
 f=Fixture();f.u.reg_write(UC_ARM_REG_SP,0x41fff000);f.u.reg_write(UC_ARM_REG_LR,STOP|1);f.u.emu_start(bs['lbo_install_hook']|1,STOP,count=10000)
 assert f.install_writes==1 and f.u.reg_read(UC_ARM_REG_R0)==0xfffffffe
 cases.append('repeated_runtime_install_does_not_rewrite')
 f=Fixture();f.step=0;r=f.point(True);assert [x['phase'] for x in r]==[2,4] and not f.events and not f.writes and not f.samples
 cases.append('masked_and_frozen_clock_still_produces_decodable_screen_without_io')
 for dev in [0,1,0xfffffff0]:
  f=Fixture();f.u.mem_write(0x4bd7e038,struct.pack('<I',dev));r=f.point();assert [x['phase'] for x in r]==[2,5] and not f.events and not f.writes
 cases.append('invalid_device_has_screen_evidence_before_io')
 f=Fixture();f.image[12*1024*1024]^=1;r=f.point();assert r[-1]['phase']==6 and r[-1]['signed_value']==-7 and not f.writes
 count=len(f.events);r=f.point();assert r[-1]['phase']==8 and len(f.events)==count
 cases.append('hash_failure_visible_and_consumed_without_retry')
 f=Fixture();f.cache_enabled=0;f.u.mem_write(0x4bd7e2ed,b'\0');r=f.point()
 assert [x['phase'] for x in r]==[2,6,7] and r[-1]['signed_value']==0
 assert mailbox.inspect(f.stable,f.nonce,f.prefix)['latest']['sequence']==3
 cases.append('correctly_installed_late_hook_records_mode_pre_shutdown')
 f=Fixture();f.u.mem_write(0x4bd7e2ed,b'\2');r=f.point();assert r[-1]['phase']==7 and r[-1]['signed_value']==-106 and not f.writes
 cases.append('identity_failure_distinct_and_no_mailbox_writes')
 return {'scope':'Exact sparse copy, original ROP/cache instructions and resident main installer, bounded pixel writer and actual module. Heap/GPT/storage/controller/ticks/IRQ/cache effects modeled; no physical visibility claim.',
 **extent,'cases':cases,'case_count':len(cases),'module_sha256':hashlib.sha256(module.read_bytes()).hexdigest(),'bootstrap_sha256':hashlib.sha256(bootstrap.read_bytes()).hexdigest(),
 'candidate_sha256':manifest['candidate_sha256'],'observer_sha256':manifest['observer_sha256'],'state_bytes':manifest['state_bytes'],
 'late_hook_installed_by_executed_resident_code':True,'no_synthetic_late_hook_installation':True,'copy_boundary_regression_reproduced':True,
 'screen_words_decoded_from_actual_emulated_pixel_writes':True,'screen_driver_timer_calls':False,
 'kernel_entry_proved':False,'physical_visibility_proved':False,'hardware_acceptance':False,'device_accessed':False}
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for key in ['module','bootstrap','old-bootstrap','header','lk','folder','output']:p.add_argument('--'+key,type=Path,required=True)
 x=p.parse_args();r=validate(x.module,x.bootstrap,x.old_bootstrap,x.header,x.lk,x.folder);x.output.write_text(json.dumps(r,indent=2)+'\n');print('Copy-corrected complete controls passed:',r['case_count'])
