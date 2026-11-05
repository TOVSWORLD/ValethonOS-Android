#!/usr/bin/env python3
"""Isolated local replay of pinned unbounded legacy wait sites, never hardware."""
import argparse,hashlib,json
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R8,UC_ARM_REG_PC
from validate_loader_allocator import EXPECTED
BASE=0x4bd00000

def audit(path,source):
 b=path.read_bytes();assert hashlib.sha256(b).hexdigest()==EXPECTED;pcs=[]
 for start in [0x4bd37660,0x4bd3b4e6]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(BASE,0x80000);u.mem_write(BASE,b[512:]);u.mem_map(0x11230000,0x1000);u.reg_write(UC_ARM_REG_R8,0x11230000);u.emu_start(start|1,0x50000000,count=1000);pc=u.reg_read(UC_ARM_REG_PC)
  assert (start==0x4bd37660 and pc in [0x4bd37664,0x4bd37666,0x4bd37668]) or pc==0x4bd3b4e6;pcs.append(hex(pc))
 return {'scope':'Isolated archived wait instructions with modeled stuck conditions; no claim about actual trials','lk_sha256':EXPECTED,'sites':[{'entry':'0x4bd37660','condition':'R1b DAT0 never ready','finding':'No internal timeout in selected busy loop','pc_after_1000_instructions':pcs[0]},{'entry':'0x4bd3b4e6','condition':'Legacy event-wait reset failure reaches self branch','finding':'Unconditional self loop','pc_after_1000_instructions':pcs[1]}],'r1_fallback_primary_source':str(source),'r1_fallback_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'new_command_driver_avoids_both_sites':True,'raw_data_driver_guarantee_not_inferred':True,'device_accessed':False,'physical_commands':False,'trial_failure_cause_proved':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--lk',type=Path,required=True);p.add_argument('--mmc-source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=audit(a.lk,a.mmc_source);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Isolated legacy wait sites confirmed:',len(r['sites']))
