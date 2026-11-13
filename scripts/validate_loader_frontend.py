#!/usr/bin/env python3
"""Execute complete runtime frontend; synthetic RAM/controller/block hardware."""
import argparse,hashlib,json,struct
from pathlib import Path
from validate_loader_identity_start import Bound,IP,IR
from validate_loader_physical import DEVICE,BDEV
from validate_loader_firmware_module import STATE,CFG,POINT
from validate_loader_checkpoint import elf
from validate_loader_allocator import EXPECTED
from validate_loader_relocation import relative_references
import retained_log_mailbox as m
DESC=0x41100800
class Front(Bound):
 def __init__(self,*args,**kw):
  super().__init__(*args,**kw)
  self.u.mem_write(DESC,bytes(self.u.mem_read(CFG,104))+struct.pack('<I',0x4bcff009)+bytes(4))
  fields={(0x4bd7e038,4):DEVICE,(DEVICE+4,4):0,(DEVICE+8,4):BDEV,(DEVICE+16,4):0x4bcff009,(DEVICE+20,4):0x4bd35a89,(0x4bd7e280,4):0x4bd7edf0,(0x4bd7ee18,4):0x11230000,(0x4bd7e298,4):1,(0x4bd7e29c,4):1,(0x4bd7e38c,1):8,(0x4bd7e2ed,1):1,(0x4bd7e3c5,4):1024}
  for (at,n),v in fields.items():self.u.mem_write(at,v.to_bytes(n,'little'))
 def dispatch(self,stage=2,mode=0,kind=1,device=DEVICE):
  extra=2048 if kind==2 else 0
  self.u.mem_write(POINT,struct.pack('<7I4x3QI4x',stage,mode,kind,2048,0x44000000,0x40000000 if stage in [3,4] else 0,0x44000000 if stage in [3,4] else 0,8192,100000*512+extra,8192*512+extra,device))
  return self.call('lfo_dispatch',[STATE,DESC,POINT])
def validate(path,lkpath,objects):
 lk=lkpath.read_bytes();assert hashlib.sha256(lk).hexdigest()==EXPECTED
 kinds={}
 for obj in objects:
  for k,n in relative_references(obj.read_bytes()).items():kinds[k]=kinds.get(k,0)+n
 names=('lp_init','lp_context_bytes','lp_pinned_ops','lp_read','lp_read_absolute','lp_write','lp_prefix','lh_block','lft_start','lft_start_bound','li_memory_read','li_discover','lft_emit','lft_state_bytes','ld_pinned_services','lfo_dispatch','lfo_state_bytes');seg,sym=elf(path,names);cases=[]
 for delta in [0,0x2000000]:
  f=Front(seg,sym,lk,relocation=delta)
  assert f.dispatch()==0
  assert m.inspect(f.stable,f.nonce,f.prefix)['latest']['sequence']==3
  n=(len(f.events),len(f.writes));assert f.dispatch()==1 and n==(len(f.events),len(f.writes))
  assert f.dispatch(kind=2)==0 and f.dispatch(stage=3)==0
  assert m.inspect(f.stable,f.nonce,f.prefix)['latest']['sequence']==5 and not f.identity_reads
  cases.append('mode_two_distinct_reads_handoff_direct_metadata_'+hex(0x41000000+delta))
 for mode in [2,99]:
  f=Front(seg,sym,lk);assert f.dispatch(mode=mode)==1 and not f.events and not f.writes and not f.samples;cases.append('non_normal_no_io_'+str(mode))
 for delta in [0,0x2000000]:
  f=Front(seg,sym,lk,relocation=delta);f.cache_enabled=0;f.u.mem_write(0x4bd7e2ed,b'\0')
  assert f.dispatch()==0 and f.dispatch(kind=2)==0 and f.dispatch(stage=3)==0
  assert m.inspect(f.stable,f.nonce,f.prefix)['latest']['sequence']==5
  commands=[v&63 for off,v in f.writes if off==0x34]
  assert commands==[13]*24 and bytes(f.u.mem_read(0x4bd7e2ed,1))==b'\0'
  cases.append('cache_off_direct_metadata_records_no_switch_'+hex(0x41000000+delta))
 for at,v in [(0x4bd7e038,DEVICE+4),(DEVICE+16,0),(BDEV+4,1024),(0x4bd7e2ed,2)]:
  f=Front(seg,sym,lk);f.u.mem_write(at,v.to_bytes(1 if at==0x4bd7e2ed else 4,'little'));assert f.dispatch()<0 and not f.events and not f.writes;assert f.dispatch()<0;cases.append('first_binding_failure_latches_'+hex(at))
 for delta in [0,0x2000000]:
  f=Front(seg,sym,lk,relocation=delta);f.cache_enabled=0;f.u.mem_write(0x4bd7e2ed,b'\0')
  assert f.dispatch(stage=4)==0 and m.inspect(f.stable,f.nonce,f.prefix)['latest']['sequence']==3
  before=(len(f.events),len(f.writes));assert f.dispatch(stage=3)==1 and before==(len(f.events),len(f.writes))
  cases.append('late_pre_shutdown_cache_off_terminal_'+hex(0x41000000+delta))
 return {'scope':'Actual PIC frontend/identity/clock/writer instructions; metadata synthetic RAM, block/controller/counter and full-prefix digest modeled','cases':cases,'case_count':len(cases),'elf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'object_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in objects},'allocated_input_relocation_types':kinds,'state_bytes':f.call('lfo_state_bytes',[]),'mode_record_observation':'normal mode sampled at first redirected read, not earlier mode hook','device_accessed':False,'hardware_acceptance':False,'physical_candidate_ready':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--lk',type=Path,required=True);p.add_argument('--object',type=Path,action='append',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=validate(a.elf,a.lk,a.object);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Complete runtime frontend controls passed:',r['case_count'])
