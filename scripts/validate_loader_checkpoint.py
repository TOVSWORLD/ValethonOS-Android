#!/usr/bin/env python3
"""Execute linked ARM checkpoint core against modeled RAM/storage only."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
import retained_log_mailbox as m
from loader_checkpoint_record import decode,TAG,BODY

REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
CTX,CFG,IO,POINT=0x41100000,0x41110000,0x41111000,0x41112000
READ,WRITE,FLUSH,PREFIX,STOP=0x50000000,0x50001000,0x50002000,0x50003000,0x50004000


def elf(path,wanted=('lc_init','lc_emit','lc_context_bytes')):
 b=path.read_bytes()
 if b[:7]!=b'\x7fELF\x01\x01\x01' or struct.unpack_from('<HH',b,16)!=(2,40):raise ValueError('ARM32 analysis ELF required')
 shoff=struct.unpack_from('<I',b,32)[0];ents,count=struct.unpack_from('<HH',b,46)
 sections=[struct.unpack_from('<10I',b,shoff+i*ents) for i in range(count)];symbols={}
 for s in sections:
  if s[1]!=2:continue
  names=sections[s[6]];names=b[names[4]:names[4]+names[5]]
  for at in range(s[4],s[4]+s[5],s[9]):
   n,value,size,info,other,index=struct.unpack_from('<IIIBBH',b,at);name=names[n:].split(b'\0')[0].decode()
   if name in wanted:symbols[name]=value
 if len(symbols)!=len(wanted):raise ValueError('Core symbols missing')
 phoff=struct.unpack_from('<I',b,28)[0];ents,count=struct.unpack_from('<HH',b,42);segments=[]
 for i in range(count):
  kind,off,vaddr,paddr,used,total,flags,align=struct.unpack_from('<8I',b,phoff+i*ents)
  if kind==1:
   if vaddr<0x40ff0000 or vaddr+total>0x41010000:raise ValueError('ELF outside analysis map')
   segments.append((vaddr,b[off:off+used]))
 return segments,symbols


class Machine:
 def __init__(self,segments,symbols,failure=None,durable=1,exclusive=1):
  self.uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);self.symbols=symbols;self.failure=failure
  for start,size in [(0x40ff0000,0x20000),(0x41100000,0x20000),(0x41fe0000,0x20000),(0x50000000,0x10000)]:self.uc.mem_map(start,size)
  for address,data in segments:self.uc.mem_write(address,data)
  self.nonce=bytes(range(32));image=bytearray(m.PARTITION);image[:8]=b'ANDROID!';image,self.prefix=m.prepare(bytes(image),self.nonce,b'VALETHON HOST CONTROL v1\nThis is a preinstalled retention control, NOT a kernel log.\n');self.original=image;self.image=bytearray(image);self.stable=image;self.events=[];self.writes=0;self.flushes=0;self.hashes=0
  self.uc.mem_write(CFG,struct.pack('<32s32sQQ5I',self.nonce,bytes.fromhex(self.prefix),8192,100000,m.PARTITION,5,8,durable,exclusive)+bytes(4))
  self.uc.mem_write(IO,struct.pack('<5I',0,READ|1,WRITE|1,FLUSH|1,PREFIX|1));self.uc.hook_add(UC_HOOK_CODE,self.hook)
  self.initial=self.call('lc_init',[CTX,CFG,IO])
 def hook(self,u,at,size,data):
  if at not in [READ,WRITE,FLUSH,PREFIX]:return
  r=[u.reg_read(x) for x in REGS];result=0
  if at==READ:
   offset,out,n=r[1:];self.events.append(('read',offset,n))
   if offset+n>len(self.image):raise ValueError('Read escaped fixture')
   if self.failure=='readback' and self.writes==3 and n==len(TAG)+BODY.size:result=-1
   else:u.mem_write(out,bytes(self.image[offset:offset+n]))
  elif at==WRITE:
   offset,source,n=r[1:];self.writes+=1;self.events.append(('write',offset,n))
   if offset<m.SLOT_BASE or offset+n>m.GUARD or n!=4096:raise ValueError('Write escaped slots')
   if self.failure=='write'+str(self.writes):result=-1
   else:self.image[offset:offset+n]=u.mem_read(source,n)
  elif at==FLUSH:
   self.flushes+=1;self.events.append(('flush',))
   if self.failure=='flush'+str(self.flushes):result=-1
   else:self.stable=bytes(self.image)
  else:
   self.hashes+=1;self.events.append(('prefix',));result=0 if hashlib.sha256(self.image[:m.BASE]).digest()==bytes(u.mem_read(r[1],32)) else -1
  u.reg_write(UC_ARM_REG_R0,result&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def call(self,name,args):
  u=self.uc
  for reg,v in zip(REGS,args):u.reg_write(reg,v)
  for i,reg in enumerate(SAVED):u.reg_write(reg,0xaaa00000+i)
  u.reg_write(UC_ARM_REG_SP,0x41fff000);u.reg_write(UC_ARM_REG_LR,STOP|1)
  u.emu_start(self.symbols[name]|1,STOP,count=40000000,timeout=20000000)
  if u.reg_read(UC_ARM_REG_PC)!=STOP:raise ValueError('Core exceeded execution budget')
  if u.reg_read(UC_ARM_REG_SP)!=0x41fff000 or any(u.reg_read(reg)!=0xaaa00000+i for i,reg in enumerate(SAVED)):raise ValueError('ARM ABI preservation differs')
  result=u.reg_read(UC_ARM_REG_R0);return result-(1<<32) if result&(1<<31) else result
 def emit(self,stage,mode=0,kind=0,size=0,dst=0,entry=0,dt=0,first=0,requested=0,selected=0):
  self.uc.mem_write(POINT,struct.pack('<7I4x3Q',stage,mode,kind,size,dst,entry,dt,first,requested,selected));return self.call('lc_emit',[CTX,POINT])
 def latest(self):return m.inspect(bytes(self.image),self.nonce,self.prefix)['latest']


def validate(path):
 segments,symbols=elf(path);passed=[]
 f=Machine(segments,symbols);assert f.initial==0 and f.emit(1)==0
 assert f.emit(2,kind=1,size=2048,dst=0x45000000,first=9000,requested=100000*512,selected=9000*512)==0
 read=decode(f.latest()['payload'],f.nonce,f.prefix);assert read['record_storage_first_sector']==8192 and read['selected_partition_first_sector']==9000 and read['selected_read_offset']==9000*512
 assert f.emit(2,kind=2,size=7252168,dst=0x45000000,first=8192,requested=100000*512+2048,selected=8192*512+2048)==0
 assert f.emit(3,entry=0x40000000,dt=0x44000000)==0
 latest=f.latest();decoded=decode(latest['payload'],f.nonce,f.prefix)
 assert latest['sequence']==5 and decoded['stage']=='pre_handoff' and decoded['kernel_entry']==0x40000000 and decoded['dt_address']==0x44000000 and not decoded['kernel_record'] and f.hashes==1 and f.writes==12 and f.flushes==12
 assert bytes(f.image[:m.SLOT_BASE])==f.original[:m.SLOT_BASE] and bytes(f.image[m.GUARD:])==f.original[m.GUARD:]
 passed.append('mode_header_body_handoff_with_actual_selected_offset')
 for mode in [2,6,99]:
  f=Machine(segments,symbols);assert f.emit(1,mode=mode)==1 and not f.events;passed.append('mode_'+str(mode)+'_no_io')
 for durable,exclusive in [(0,1),(1,0)]:
  f=Machine(segments,symbols,durable=durable,exclusive=exclusive);assert f.initial<0 and f.emit(1)<0 and not f.events;passed.append('unadmitted_adapter_'+str(durable)+str(exclusive))
 for failure in ['write1','write2','write3','flush1','flush2','flush3','readback']:
  f=Machine(segments,symbols,failure=failure);assert f.emit(1)<0;events=len(f.events);assert f.emit(3)<0 and len(f.events)==events
  assert m.inspect(f.stable,f.nonce,f.prefix)['latest']['sequence']>=1
  assert bytes(f.image[:m.SLOT_BASE+m.SLOT])==f.original[:m.SLOT_BASE+m.SLOT] and bytes(f.image[m.GUARD:])==f.original[m.GUARD:]
  passed.append('no_retry_'+failure)
 return {'scope':'Linked ARM32 checkpoint core in simulated RAM/storage with modeled exclusive flush-capable callbacks only',
         'elf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'context_bytes':f.call('lc_context_bytes',[]),'cases':passed,'case_count':len(passed),
         'arm_callee_saved_and_sp_preserved':True,'mailbox_format':'VLOG0001','loader_payload_bytes':len(TAG)+BODY.size,
         'prefix_hashed_once_per_exclusive_context':True,'normal_partition_slots_only':True,
         'modeled_header_last_flush_order_verified':True,'existing_python_reader_decodes_actual_arm_records':True,
         'physical_memory_placement_qualified':False,'firmware_adapter_or_flush_qualified':False,
         'device_accessed':False,'device_written':False,'hardware_durability_qualified':False}

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--elf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=validate(a.elf);a.output.write_text(json.dumps(r,indent=2)+'\n');print('ARM checkpoint core controls passed:',r['case_count'])
