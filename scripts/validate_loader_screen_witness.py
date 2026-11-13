#!/usr/bin/env python3
"""Analysis-only screen-witness execution; never packages/exports a candidate."""
import argparse,hashlib,json,struct
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
from validate_loader_complete import Complete,raw_elf,elf,BASE,REGS
from validate_loader_observer import bl
from validate_loader_allocator import EXPECTED,POOL
from validate_loader_physical import STOP
import audit_resident_loader_payload as resident_audit
import retained_log_mailbox as mailbox

SITE=0x4bd3e3e8

def validate(module,bootstrap,lkpath,payload):
 lk=lkpath.read_bytes();assert hashlib.sha256(lk).hexdigest()==EXPECTED
 full=payload.read_bytes()[:492132];assert hashlib.sha256(full).hexdigest()==resident_audit.SHA
 resident=full[0xa00:0x1800];sections,bs=raw_elf(bootstrap)
 assert 'lbo_read' not in bs and 'lbo_arrival' in bs
 seg,_=elf(module,('lfo_frame_dispatch','lfo_state_bytes'));_,sym=raw_elf(module)
 cases=[]
 # Execute exact resident main, not merely a synthetic direct observer call.
 for original,mode in [(0,0),(0,2),(6,0)]:
  u,state,word=resident_audit.machine(resident,original_mode=original,lk_mode=mode)
  for at,data in sections:u.mem_write(at,data)
  assert resident[0x386:0x38a]==bl(BASE+0x386,BASE+0x736)
  u.mem_write(BASE+0x386,bl(BASE+0x386,bs['lbo_arrival']&~1))
  reached=[]
  def arrival(uc,at,size,data):
   if at==(bs['lbo_arrival']&~1):reached.append(word(0x4bd7c3a0))
  u.hook_add(UC_HOOK_CODE,arrival)
  u.emu_start(BASE,resident_audit.STOP,count=1000000,timeout=5000000)
  assert state['app'] and reached==[2 if original==6 else mode]
  assert word(resident_audit.DEVICE+16)==BASE+9
  assert state['cache_cleans']==[[0x4bd00000,0x100000]]
  cases.append('resident_main_reaches_arrival_then_original_cache_clean_app_'+str(original)+'_'+str(mode))
 def fixture():
  f=Complete(seg,sym,lk,bootstrap,resident);f.messages=[];f.formatter_calls=0
  # Execute original video_printf and its formatter. Only the final display
  # puts is modeled, so this proves real variadic formatting, not pixels.
  def screen(u,at,size,data):
   if at==0x4bd44b3c:f.formatter_calls+=1
   if at==0x4bd44b08:
    p=u.reg_read(UC_ARM_REG_R0);b=bytes(u.mem_read(p,96)).split(b'\0')[0]
    assert len(b)<96
    f.messages.append(b.decode('ascii'));u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  f.u.hook_add(UC_HOOK_CODE,screen)
  return f
 def point(f,mode=0,masked=False):
  u=f.u;u.mem_write(0x4bd7c3a0,struct.pack('<I',mode))
  regs=[0xabc00000+i for i in range(13)];regs[11]=0x40080000
  for r,v in zip(REGS,regs):u.reg_write(r,v)
  sp=0x41fff000;u.mem_write(sp+8,struct.pack('<I',0x48000000))
  flags=0x980a00b3 if masked else 0x980a0033
  u.reg_write(UC_ARM_REG_CPSR,flags);u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,STOP|1)
  def stop(uc,at,size,data):
   if at==SITE+4:uc.emu_stop()
  hook=u.hook_add(UC_HOOK_CODE,stop);u.emu_start(SITE|1,STOP,count=80000000,timeout=40000000);u.hook_del(hook)
  expected=list(regs);expected[3]=struct.unpack_from('<I',lk,512+0x3eb0c)[0]
  assert u.reg_read(UC_ARM_REG_PC)==SITE+4
  assert [u.reg_read(r) for r in REGS]==expected and u.reg_read(UC_ARM_REG_SP)==sp
  assert u.reg_read(UC_ARM_REG_CPSR)&0xf80f00c0==flags&0xf80f00c0
  assert f.formatter_calls==len(f.messages)
  return [int(s.split()[1]) for s in f.messages]
 f=fixture();assert point(f,masked=True)==[2,4] and not f.events and not f.writes
 assert int(f.messages[-1].split()[2],16)&0x80
 cases.append('actual_formatter_masked_rejection_visible_before_no_storage')
 f=fixture();assert point(f,mode=2)==[2,3] and not f.events and not f.writes
 cases.append('actual_formatter_non_normal_rejection_visible_before_no_storage')
 for dev in [0,1,0xfffffff0]:
  f=fixture();f.u.mem_write(0x4bd7e038,struct.pack('<I',dev));assert point(f)==[2,5] and not f.events and not f.writes
 cases.append('actual_formatter_invalid_device_visible_before_no_storage')
 f=fixture();f.u.mem_write(POOL+8,struct.pack('<I',16));assert point(f)==[2,6]
 assert 'fffffffc' in f.messages[-1] and not f.events and not f.writes
 cases.append('actual_formatter_allocation_failure_minus4_visible')
 f=fixture();f.image[12*1024*1024]^=1;assert point(f)==[2,6]
 assert 'fffffff9' in f.messages[-1] and not f.writes
 n=len(f.events);assert point(f)==[2,6,2,8] and len(f.events)==n
 cases.append('actual_formatter_hash_failure_minus7_visible_no_retry')
 f=fixture();f.native_read();assert not f.loaded and not f.messages and not f.writes
 assert len(f.events)==1
 f.cache_enabled=0;f.u.mem_write(0x4bd7e2ed,b'\0');assert point(f)==[2,6,7]
 assert '00000000' in f.messages[-1]
 assert mailbox.inspect(f.stable,f.nonce,f.prefix)['latest']['sequence']==3
 cases.append('actual_formatter_success_with_mode_pre_shutdown_records')
 f=fixture();f.u.mem_write(0x4bd7e2ed,b'\2');assert point(f)==[2,6,7] and not f.writes
 assert f.messages[-1].split()[2]=='ffffff96'
 cases.append('actual_formatter_identity_minus106_distinct_from_bridge_success')
 for at,value,expected in [(0x41110010,0,-102),(0x41110104,1024,-103)]:
  f=fixture();f.u.mem_write(at,struct.pack('<I',value));assert point(f)==[2,6,7] and not f.writes
  assert int(f.messages[-1].split()[2],16)==(expected&0xffffffff)
 cases.append('actual_formatter_device_minus102_block_minus103_distinct')
 return {'scope':'Exact resident main arrival plus linked late hook/bridge/module and original LK variadic formatter; final display sink, heap initialization, storage/controller/clock/IRQ/cache effects and prefix digest modeled',
 'case_count':len(cases),'cases':cases,'bootstrap_sha256':hashlib.sha256(bootstrap.read_bytes()).hexdigest(),
 'lk_sha256':EXPECTED,'module_sha256':hashlib.sha256(module.read_bytes()).hexdigest(),
 'arrival_call_site':hex(BASE+0x386),'pre_shutdown_site':hex(SITE),
 'display_printf':hex(0x4bd44b3c),'display_sink_modeled':hex(0x4bd44b08),
 'gate_evidence_independent_of_mailbox':True,'physical_visibility_proved':False,
 'display_driver_termination_stack_or_irq_contract_proved':False,'runtime_cause_proved':False,
 'device_accessed':False,'candidate_packaged':False,'physical_execution_admitted':False}
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for key in ['module','bootstrap','lk','payload','output']:p.add_argument('--'+key,type=Path,required=True)
 a=p.parse_args();r=validate(a.module,a.bootstrap,a.lk,a.payload);a.output.write_text(json.dumps(r,indent=2)+'\n');print('New screen-witness controls passed:',r['case_count'])
