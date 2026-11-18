#!/usr/bin/env python3
"""Execute bound identity entry; metadata read callback remains modeled."""
import argparse,hashlib,json,struct
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_PC,UC_ARM_REG_LR
from validate_loader_timed_module import Timed
from validate_loader_physical import DEVICE,BDEV
from validate_loader_firmware_module import STATE,CFG,PLAN,OPS,HASH,CARD
from validate_loader_checkpoint import elf
from validate_loader_allocator import EXPECTED
import retained_log_mailbox as m
IP,IR,READER=0x41100700,0x41100740,0x50000800
class Bound(Timed):
 def __init__(self,*args,mismatch=False,unstable=False,read_failure=False,**kw):
  super().__init__(*args,**kw);self.identity_reads=[];self.fields={(DEVICE+4,4):0,(DEVICE+8,4):BDEV,(0x41111000,4):0x41112000,(0x41112028,4):0x11230000,(0x41111018,4):2 if mismatch else 1,(0x4111101c,4):1,(0x4111110c,1):8,(0x4111106d,1):1,(0x41111145,4):1024};self.unstable=unstable;self.read_failure=read_failure
  self.u.mem_write(IP,struct.pack('<4I',DEVICE,0x41111000,0x41112000,BDEV));self.u.mem_write(IR,struct.pack('<2I',0,READER|1));self.u.hook_add(UC_HOOK_CODE,self.metadata)
 def metadata(self,u,at,size,data):
  if at!=READER:return
  address,out,n=(u.reg_read(r) for r in [UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]);key=(address,n);assert key in self.fields;self.identity_reads.append(key)
  value=self.fields[key]+int(self.unstable and len(self.identity_reads)>9 and address==0x41111018)
  if not self.read_failure:u.mem_write(out,value.to_bytes(n,'little'))
  u.reg_write(UC_ARM_REG_R0,0xffffffff if self.read_failure else 0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def bound_start(self):return self.call('lft_start_bound',[STATE,CFG,PLAN,OPS,HASH,CARD,IP,IR])
def validate(path,lkpath):
 lk=lkpath.read_bytes();assert hashlib.sha256(lk).hexdigest()==EXPECTED
 names=('lp_init','lp_context_bytes','lp_pinned_ops','lp_read','lp_read_absolute','lp_write','lp_prefix','lh_block','lft_start','lft_start_bound','li_memory_read','li_discover','lft_emit','lft_state_bytes','ld_pinned_services');seg,sym=elf(path,names);cases=[]
 for delta in [0,0x2000000]:
  f=Bound(seg,sym,lk,relocation=delta);assert f.bound_start()==0 and len(f.identity_reads)==18 and f.emit(1)==0 and f.emit(3)==0;assert m.inspect(f.stable,f.nonce,f.prefix)['latest']['sequence']==3;cases.append('bound_start_records_'+hex(0x41000000+delta))
 for condition in ['mismatch','unstable','read_failure']:
  f=Bound(seg,sym,lk,**{condition:True});assert f.bound_start()<0 and not f.events and not f.writes and not f.samples;calls=len(f.identity_reads);assert f.bound_start()<0 and len(f.identity_reads)==calls and f.start_module()<0 and f.emit(1)<0;cases.append(condition+'_stops_before_controller_storage_clock_and_no_retry')
 for delta in [0,0x2000000]:
  f=Bound(seg,sym,lk,relocation=delta)
  # Populate synthetic firmware RAM, then execute actual volatile byte reads.
  direct_plan=struct.pack('<4I',DEVICE,0x4bd7e280,0x4bd7edf0,BDEV)
  f.u.mem_write(IP,direct_plan);f.u.mem_write(IR,struct.pack('<2I',IP,f.symbols['li_memory_read']))
  fields={(0x4bd7e038,4):DEVICE,(DEVICE+4,4):0,(DEVICE+8,4):BDEV,(0x4bd7e280,4):0x4bd7edf0,(0x4bd7ee18,4):0x11230000,(0x4bd7e298,4):1,(0x4bd7e29c,4):1,(0x4bd7e38c,1):8,(0x4bd7e2ed,1):1,(0x4bd7e3c5,4):1024}
  for (address,n),value in fields.items():f.u.mem_write(address,value.to_bytes(n,'little'))
  assert f.call('li_discover',[0x41100800,DEVICE,BDEV,IR])==0
  assert f.bound_start()==0 and not f.identity_reads and f.emit(1)==0 and f.emit(3)==0
  assert m.inspect(f.stable,f.nonce,f.prefix)['latest']['sequence']==3
  before=bytes(f.u.mem_read(0x41100840,16));assert f.call('li_memory_read',[IP,0x4bd7e300,0x41100840,16])<0 and bytes(f.u.mem_read(0x41100840,16))==before
  cases.append('direct_selected_memory_discovery_start_and_forbidden_read_'+hex(0x41000000+delta))
 return {'scope':'actual Thumb identity/start/writer instructions; metadata synthetic RAM (first five controls callback-modeled), prefix digest, block/controller/counter modeled','elf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'cases':cases,'case_count':len(cases),'state_bytes':f.call('lft_state_bytes',[]),'sp_callee_saved_checked':True,'pinned_frontend_getter_provenance_proved':False,'hardware_acceptance':False,'device_accessed':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--lk',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=validate(a.elf,a.lk);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Bound identity ARM controls passed:',r['case_count'])
