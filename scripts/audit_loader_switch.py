#!/usr/bin/env python3
"""Replay archived LK SWITCH instructions; no device access or firmware output."""
import argparse,hashlib,json,struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
BASE=0x4bd00000
EXPECTED='7637da8754a7494f8907d07c7b25532476959956d1cfea856ab8ea6940176056'
def run(blob,status,command_error=0,status_error=0):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(BASE,0x80000);u.mem_write(BASE,blob[512:]);u.mem_map(0x41000000,0x10000);u.mem_map(0x50000000,0x1000)
 stack=0x4100f000;u.reg_write(UC_ARM_REG_SP,stack);u.mem_write(stack,struct.pack('<I',1));u.reg_write(UC_ARM_REG_LR,0x50000001)
 for r,v in [(UC_ARM_REG_R0,0x111),(UC_ARM_REG_R1,0x222),(UC_ARM_REG_R2,1),(UC_ARM_REG_R3,32)]:u.reg_write(r,v)
 seen={'polls':0,'command_argument':None,'counter_reduced_for_boundary_test':False}
 def hook(u,at,size,data):
  if at==0x4bd395f4:
   p=u.reg_read(UC_ARM_REG_R1);cmd,arg=struct.unpack('<II',u.mem_read(p,8));assert cmd==6 and arg==0x03200101
   seen['command_argument']=hex(arg);u.reg_write(UC_ARM_REG_R0,command_error);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  elif at==0x4bd39abc:
   if seen['polls']==0 and status==0:
    # Exercise exact decrement/expiry branch, without 600001 identical polls.
    u.reg_write(UC_ARM_REG_R4,2);seen['counter_reduced_for_boundary_test']=True
   seen['polls']+=1;u.mem_write(u.reg_read(UC_ARM_REG_R2),struct.pack('<I',status));u.reg_write(UC_ARM_REG_R0,status_error);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x4bd39b81,0x50000000,count=10000)
 assert u.reg_read(UC_ARM_REG_PC)==0x50000000 and u.reg_read(UC_ARM_REG_SP)==stack
 return dict(seen,return_value=u.reg_read(UC_ARM_REG_R0))
def main():
 p=argparse.ArgumentParser();p.add_argument('--lk',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();b=a.lk.read_bytes();assert hashlib.sha256(b).hexdigest()==EXPECTED
 cases={name:run(b,**kw) for name,kw in {'ready':{'status':0x900},'switch_error':{'status':0x80},'command_failure':{'status':0x900,'command_error':7},'status_failure':{'status':0x900,'status_error':9},'never_ready_timeout_boundary':{'status':0}}.items()}
 assert [cases[n]['return_value'] for n in cases]==[0,4,7,9,0]
 result={'schema':1,'baseline_sha256':EXPECTED,'routine':'0x4bd39b80','cases':cases,'finding':'Timeout expiry returns zero, indistinguishable from ready using return value alone. Direct binding is rejected.','firmware_flush_adapter_qualified':False,'device_accessed':False,'hardware_durability_proved':False,'model_limits':'Command and status callbacks modeled; timeout counter reduced only in timeout boundary case. No physical MMC command executed.'}
 a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
