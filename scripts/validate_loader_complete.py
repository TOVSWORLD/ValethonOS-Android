#!/usr/bin/env python3
"""Full resident hook -> owned allocation/hash/cache -> PIC frontend/writer replay."""
import argparse,hashlib,json,struct
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
from validate_loader_frontend import Front
from validate_loader_physical import DEVICE,BDEV,STOP
from validate_loader_checkpoint import elf,SAVED
from validate_loader_allocator import EXPECTED,HEAP,POOL,SIZE,COUNTER
from validate_loader_console_reclaim import altered,SPANS
from validate_loader_observer import bl
import retained_log_mailbox as m
BASE=0x4bcff000
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12]
def raw_elf(path):
 b=path.read_bytes();at=struct.unpack_from('<I',b,32)[0];es,n,ni=struct.unpack_from('<HHH',b,46);ss=[struct.unpack_from('<10I',b,at+i*es) for i in range(n)];symbols={};sections=[]
 for sec in ss:
  if sec[2]&2 and sec[5] and sec[1] in [1,8]:sections.append((sec[3],bytes(sec[5]) if sec[1]==8 else b[sec[4]:sec[4]+sec[5]]))
  if sec[1]==2:
   st=ss[sec[6]];strings=b[st[4]:st[4]+st[5]]
   for pos in range(sec[4],sec[4]+sec[5],sec[9]):
    name,value,size,info,other,index=struct.unpack_from('<IIIBBH',b,pos);name=strings[name:].split(b'\0')[0].decode()
    if name:symbols[name]=value
 return sections,symbols
class Complete(Front):
 def __init__(self,segments,symbols,lk,bootstrap,resident,packed=None,**kw):
  super().__init__(segments,symbols,lk,**kw);u=self.u;self.original_symbols=dict(self.symbols);self.boot_sections,self.bs=raw_elf(bootstrap);self.cache=[];self.irq=[];self.loaded=False;self.read_entry=None;self.replay_checks=0;self.handoff=None
  u.mem_map(0x4bcf0000,0x10000);u.mem_map(POOL,SIZE);head=HEAP+8;u.mem_write(head,struct.pack('<II',POOL,POOL));u.mem_write(POOL,struct.pack('<III',head,head,SIZE));u.mem_write(COUNTER,bytes(4))
  self.logical=100000
  self.state_size=self.call('lfo_state_bytes',[])
  lo=min(at for at,data in segments);end=max(at+len(data) for at,data in segments);blob=bytearray((end-lo+511)&~511)
  for at,data in segments:blob[at-lo:at-lo+len(data)]=data
  self.blob=bytes(blob);image=bytearray(self.image);image[m.BASE:]=bytes(m.PARTITION-m.BASE);image[12*1024*1024:12*1024*1024+len(blob)]=blob
  image,self.prefix=m.prepare(bytes(image),self.nonce,b'VALETHON HOST CONTROL v1\nThis is a preinstalled retention control, NOT a kernel log.\n');self.image=bytearray(image);self.stable=image
  r=bytearray(altered(resident))
  for at,data in self.boot_sections:
   assert any(BASE+l<=at and at+len(data)<=BASE+h for l,h in SPANS),(hex(at),len(data))
   r[at-BASE:at-BASE+len(data)]=data
  r[0x72:0x76]=bl(BASE+0x72,self.bs['lbo_read']&~1)
  entry=(symbols['lfo_frame_dispatch']-0x41000000)|1
  load=struct.pack('<6I32sQQ',len(blob),self.state_size,4096,entry,entry,1,hashlib.sha256(blob).digest(),8192,12*1024*1024)
  at=self.bs['lbo_load_plan']-BASE;r[at:at+len(load)]=load
  config=struct.pack('<32s32sQQ5I4xI4x',self.nonce,bytes.fromhex(self.prefix),8192,100000,m.PARTITION,5,8,1,1,BASE+9)
  at=self.bs['lbo_frontend']-BASE;r[at:at+len(config)]=config
  for off,value in [(0xb90,100000),(0xba8,8192),(0xb98,0),(0xb88,5000),(0xbb0,6000),(0xba0,7000)]:struct.pack_into('<Q',r,off,value)
  if packed:
   folder=Path(packed);manifest=json.loads((folder/'manifest.json').read_text());self.nonce=(folder/'nonce.bin').read_bytes();self.image=bytearray((folder/'boot-full.img').read_bytes());self.stable=bytes(self.image);self.prefix=manifest['prefix_sha256'];self.first=manifest['target_first_sector'];self.logical=manifest['logical_boot_first_sector'];r=bytearray((folder/'observer-payload-sectors-private.bin').read_bytes()[0xa00:0x1800])
   for off,value in [(0xb90,self.logical),(0xba8,self.first),(0xb98,0),(0xb88,51200),(0xbb0,30551040),(0xba0,7000)]:struct.pack_into('<Q',r,off,value)
  u.mem_write(BASE,bytes(r));u.mem_write(0x4bd3e524,bl(0x4bd3e524,self.bs['lbo_handoff']&~1));u.mem_write(0x4bd7c3a0,bytes(4));u.hook_add(UC_HOOK_CODE,self.integration)
 def write(self,u,access,at,n,value,data):
  if getattr(self,'private_stack',None):
   lo,hi=self.private_stack;sp=u.reg_read(UC_ARM_REG_SP)
   if POOL<=sp<POOL+SIZE:
    assert lo<=sp<=hi,('private stack overflow',hex(sp),hex(lo))
    self.minimum_sp=min(self.minimum_sp,sp)
  if (POOL<=at and at+n<=POOL+SIZE) or (BASE<=at and at+n<=BASE+0xe00) or (HEAP<=at and at+n<=HEAP+32) or (COUNTER<=at and at+n<=COUNTER+4):return
  super().write(u,access,at,n,value,data)
 def integration(self,u,at,size,data):
  if at in [0x4bd3c75c,0x4bd3c76c]:self.irq.append(at);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
  if at in [0x4bd3c6f0,0x4bd3c704,0x4bd3c74c]:self.cache.append(at);u.reg_write(UC_ARM_REG_PC,at+4);return
  if at==(self.bs['lbo_call']&~1) and not self.loaded:
   out=struct.unpack('<8I',u.mem_read(self.bs['loaded'],32));assert out[1]==1 and POOL<=out[2]<out[3]<out[4]<=POOL+SIZE
   self.symbols={k:v-0x41000000+out[2] for k,v in self.original_symbols.items()};self.loaded=True;self.private_stack=(out[4]-4096,out[4]);self.minimum_sp=out[4]
  if at==BASE+0x72:self.read_entry=([u.reg_read(x) for x in REGS],u.reg_read(UC_ARM_REG_SP),u.reg_read(UC_ARM_REG_CPSR)&0xf80f00c0)
  if at==BASE+0x76:
   regs,sp,flags=self.read_entry;expected=list(regs);expected[0]=regs[6];expected[3]=BASE+0xb64
   assert [u.reg_read(x) for x in REGS]==expected and u.reg_read(UC_ARM_REG_SP)==sp and u.reg_read(UC_ARM_REG_CPSR)&0xf80f00c0==flags;self.replay_checks+=1
  if at==0x4bd3de68:
   self.handoff=([u.reg_read(x) for x in REGS],u.reg_read(UC_ARM_REG_SP),u.reg_read(UC_ARM_REG_CPSR)&0xf80f00c0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  if at==0x4bd3e528:u.emu_stop()
 def native_read(self,extra=0,mode=0,irq_disabled=False):
  u=self.u;u.mem_write(0x4bd7c3a0,struct.pack('<I',mode));u.reg_write(UC_ARM_REG_CPSR,0xf80f00b3 if irq_disabled else 0xf80f0033)
  for i,r in enumerate(SAVED):u.reg_write(r,0xabc00000+i)
  req=self.logical*512+extra
  for r,v in zip(REGS[:4],[DEVICE,0xdeadbeef,req&0xffffffff,req>>32]):u.reg_write(r,v)
  sp=0x41fff000;u.mem_write(sp,struct.pack('<III',0x41106000,2048,8));u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,STOP|1);u.emu_start(BASE+9,STOP,count=80000000,timeout=40000000)
  assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==sp and u.reg_read(UC_ARM_REG_R0)==2048
  assert all(u.reg_read(r)==0xabc00000+i for i,r in enumerate(SAVED))
 def final(self,irq_disabled=False,entry=0x40000000,dt=0x44000000):
  u=self.u;u.reg_write(UC_ARM_REG_CPSR,0x980a00b3 if irq_disabled else 0x980a0033);regs=[entry,dt]+[0xabcdef00+i for i in range(2,13)]
  for r,v in zip(REGS,regs):u.reg_write(r,v)
  u.reg_write(UC_ARM_REG_SP,0x41fff000);u.reg_write(UC_ARM_REG_LR,STOP|1);u.emu_start(0x4bd3e525,STOP,count=80000000,timeout=40000000)
  assert self.handoff==(regs,0x41fff000,0x980a0080 if irq_disabled else 0x980a0000)
def validate(module,bootstrap,lkpath,payload,packed=None):
 lk=lkpath.read_bytes();assert hashlib.sha256(lk).hexdigest()==EXPECTED
 names=('lp_init','lp_context_bytes','lp_pinned_ops','lp_read','lp_read_absolute','lp_write','lp_prefix','lh_block','lft_start','lft_start_bound','li_memory_read','li_discover','lft_emit','lft_state_bytes','ld_pinned_services','lfo_dispatch','lfo_frame_dispatch','lfo_state_bytes');seg,sym=elf(module,names)
 full=payload.read_bytes();assert hashlib.sha256(full).hexdigest()=='e10fdf770a5be2c2adc3cce0d03b8e296eac3b31e18ebdce5b56dc5491f4e7e8';resident=full[0xa00:0x1800];cases=[]
 f=Complete(seg,sym,lk,bootstrap,resident,packed=packed);f.native_read();assert f.loaded and m.inspect(f.stable,f.nonce,f.prefix)['latest']['sequence']==3;f.native_read(2048);f.final();assert m.inspect(f.stable,f.nonce,f.prefix)['latest']['sequence']==5 and f.replay_checks==2;cases.append('native_redirect_load_verified_blob_owned_stack_mode_reads_handoff')
 for mode in [2,99]:
  g=Complete(seg,sym,lk,bootstrap,resident,packed=packed);g.native_read(mode=mode);assert not g.loaded and not g.writes and len(g.events)==1;cases.append('non_normal_no_observer_'+str(mode))
 for failure in ['blob_hash','allocation','irq_disabled']:
  g=Complete(seg,sym,lk,bootstrap,resident,packed=packed)
  if failure=='blob_hash':g.image[12*1024*1024]^=1
  if failure=='allocation':g.u.mem_write(POOL+8,struct.pack('<I',16))
  g.native_read(irq_disabled=failure=='irq_disabled');assert not g.loaded and not g.writes
  assert m.inspect(g.stable,g.nonce,g.prefix)['latest']['sequence']==1
  n=len(g.events);g.native_read();assert len(g.events)==n+1 and not g.loaded and not g.writes
  cases.append(failure+'_original_read_preserved_observer_stops_no_retry')
 g=Complete(seg,sym,lk,bootstrap,resident,packed=packed);g.native_read();before=(len(g.events),len(g.writes),g.samples);g.final(irq_disabled=True);assert before==(len(g.events),len(g.writes),g.samples) and m.inspect(g.stable,g.nonce,g.prefix)['latest']['sequence']==3;cases.append('loaded_observer_masked_handoff_preserves_arguments_and_skips_storage')
 return {'scope':'Complete original resident read/handoff hooks, actual archived allocator, blob SHA and cache instructions, PIC frontend/writer; synthetic metadata/heap, IRQ/cache effects/controller/block hardware and prefix digest modeled','cases':cases,'case_count':len(cases),'bootstrap_sha256':hashlib.sha256(bootstrap.read_bytes()).hexdigest(),'module_sha256':hashlib.sha256(module.read_bytes()).hexdigest(),'blob_sha256':hashlib.sha256(f.blob).hexdigest(),'blob_bytes':len(f.blob),'state_bytes':f.state_size,'integer_sp_apsr_and_original_instruction_replay':True,'latest_loader_sequence':5,'private_stack_capacity':4096,'modeled_path_stack_bytes_used':f.private_stack[1]-f.minimum_sp,'hardware_driver_worst_case_stack_bound_proved':False,'no_device_access':True,'hardware_acceptance':False,'physical_candidate_ready':False,'packed_candidate_tested':str(packed) if packed else None}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--module',type=Path,required=True);p.add_argument('--bootstrap',type=Path,required=True);p.add_argument('--lk',type=Path,required=True);p.add_argument('--payload',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--packed',type=Path);a=p.parse_args();r=validate(a.module,a.bootstrap,a.lk,a.payload,a.packed);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Complete linked load/hook controls passed:',r['case_count'])
