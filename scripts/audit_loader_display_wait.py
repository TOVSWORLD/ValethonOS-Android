#!/usr/bin/env python3
"""Replay exact archived display-delay path with modeled tick samples; no device."""
import argparse,hashlib,json
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_PC,UC_ARM_REG_SP,UC_ARM_REG_LR
from validate_loader_allocator import EXPECTED

def audit(path):
 b=path.read_bytes();assert hashlib.sha256(b).hexdigest()==EXPECTED
 body=b[512:];md=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
 def has(lo,hi,at,mnemonic,target):
  assert any(i.address==at and i.mnemonic==mnemonic and i.op_str=='#'+hex(target) for i in md.disasm(body[lo:hi],0x4bd00000+lo))
 has(0x44b3c,0x44b68,0x4bd44b56,'bl',0x4bd44b08)
 has(0x44b08,0x44b3c,0x4bd44b36,'b.w',0x4bd2266c)
 has(0x2266c,0x226ac,0x4bd226a8,'b.w',0x4bd25f8c)
 has(0x25f8c,0x25f90,0x4bd25f8c,'b.w',0x4bd25eb8)
 has(0x25eb8,0x25f08,0x4bd25f02,'beq',0x4bd25ef8)
 cases=[]
 for step in [0,13000]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x4bd00000,0x90000);u.mem_write(0x4bd00000,body)
  u.mem_map(0x41ff0000,0x10000);u.mem_map(0x50000000,0x1000)
  u.reg_write(UC_ARM_REG_R0,30);u.reg_write(UC_ARM_REG_SP,0x41fff000);u.reg_write(UC_ARM_REG_LR,0x50000001)
  ticks=[0];samples=[0]
  def tick(uc,at,size,data):
   if at==0x4bd25dfc:
    samples[0]+=1;ticks[0]+=step;uc.reg_write(UC_ARM_REG_R0,ticks[0]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,tick);u.emu_start(0x4bd25eb9,0x50000000,count=10000,timeout=1000000)
  returned=u.reg_read(UC_ARM_REG_PC)==0x50000000
  assert returned==bool(step)
  cases.append({'modeled_tick_step':step,'returned':returned,'samples':samples[0],'instruction_cap':10000})
 return {'scope':'Exact display-delay instructions and call anchors; tick helper samples modeled. No display/controller or device execution.',
 'lk_sha256':EXPECTED,'display_to_wait_path':['0x4bd44b3c','0x4bd44b08','0x4bd2266c','0x4bd25f8c','0x4bd25eb8'],
 'loop_backedge':'0x4bd25f02 -> 0x4bd25ef8','cases':cases,
 'frozen_tick_independent_iteration_limit':False,'historical_trial_cause_proved':False,
 'physical_visibility_proved':False,'device_accessed':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--lk',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=audit(a.lk);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Display wait: advancing tick returns; frozen tick remains in native wait at bounded emulator cap')
