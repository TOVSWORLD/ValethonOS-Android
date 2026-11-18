#!/usr/bin/env python3
"""Actual bounded writer and independent raw/photo decoder controls; no device."""
import argparse,hashlib,json,struct,zlib
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from validate_loader_complete import raw_elf
from validate_loader_allocator import EXPECTED,SAVED
from loader_screen_record import BASE,SURFACE,decode_surface,decode_words
STOP=0x50000000

def png(path,raw):
 # Standalone exact emulated pixels; no camera image is modified.
 rows=b''.join(b'\0'+b''.join(raw[(y*800+x)*4:(y*800+x)*4+3] for x in range(800)) for y in range(1280))
 def chunk(tag,b):return struct.pack('>I',len(b))+tag+b+struct.pack('>I',zlib.crc32(tag+b)&0xffffffff)
 path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',800,1280,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b''))

def validate(bootstrap,lk_path,folder,image_path):
 lk=lk_path.read_bytes();assert hashlib.sha256(lk).hexdigest()==EXPECTED
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x4bcf0000,0x190000);u.mem_write(0x4bd00000,lk[512:]);u.mem_map(0x41fe0000,0x20000);u.mem_map(STOP,4096)
 u.mem_map(BASE,SURFACE*3);u.mem_write(BASE,b'\x6d'*(SURFACE*3))
 obs=(folder/'observer-payload-sectors-private.bin').read_bytes();u.mem_write(0x4bcfe600,obs[:0x1a00]);_,bs=raw_elf(bootstrap);nonce=(folder/'nonce.bin').read_bytes();token=int.from_bytes(nonce[:2],'little')
 writes=[];cache=[];line_count=[0];instructions=[0]
 def write(uc,access,at,n,v,data):
  if BASE<=at and at+n<=BASE+SURFACE*3:
   off=(at-BASE)%SURFACE;y,x=divmod(off,3200)
   assert n==4 and y<320 and y%40<32 and x<1024 and v in [0xffffffff,0xff000000]
   writes.append(at)
  else:assert 0x41fe0000<=at and at+n<=0x42000000,hex(at)
 def code(uc,at,n,data):
  instructions[0]+=1
  assert at not in [0x4bd44b3c,0x4bd44b08,0x4bd2266c,0x4bd25dfc,0x4bd25f8c,0x4bd25eb8,0x4bd358e8,0x4bd35a88,0x4bd45bb8]
  if at==0x4bd3c740:cache.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
  if at in [0x4bd3c6f0,0x4bd3c704,0x4bd3c74c]:
   if at==0x4bd3c6f0:line_count[0]+=1
   uc.reg_write(UC_ARM_REG_PC,at+4)
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
 def call(phase,value,status):
  for i,r in enumerate(SAVED):u.reg_write(r,0xabc00000+i)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],[phase,value,status]):u.reg_write(r,v)
  u.reg_write(UC_ARM_REG_CPSR,0xb3);u.reg_write(UC_ARM_REG_SP,0x41fff000);u.reg_write(UC_ARM_REG_LR,STOP|1)
  start=instructions[0];u.emu_start(bs['lw_screen']|1,STOP,count=3000000,timeout=5000000)
  assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==0x41fff000
  assert u.reg_read(UC_ARM_REG_CPSR)&128 and all(u.reg_read(r)==0xabc00000+i for i,r in enumerate(SAVED))
  return u.reg_read(UC_ARM_REG_R0),instructions[0]-start
 costs=[]
 for phase in range(1,9):
  before=len(writes);ret,n=call(phase,(0xffffff00+phase)&0xffffffff,0x980a00b3)
  assert ret==0 and len(writes)-before==3*4*8*256;costs.append(n)
 assert len(cache)==8*24 and line_count[0]==8*6000
 for at,n in cache:assert n==16000 and BASE<=at and at+n<=BASE+SURFACE*3
 raw=bytes(u.mem_read(BASE,SURFACE));records=decode_surface(raw,token);assert len(records)==8
 for i,r in enumerate(records,1):assert r['phase']==i and r['value']==0xffffff00+i and r['irq_masked']
 assert all(bytes(u.mem_read(BASE+i*SURFACE,SURFACE))==raw for i in [1,2])
 # Every adjacent pixel and unselected row remains the initial canary.
 for y in range(1280):
  row=raw[y*3200:(y+1)*3200];start=1024 if y<320 and y%40<32 else 0
  assert row[start:]==b'\x6d'*(3200-start)
 before=len(writes);assert call(0,0,0)[0]==0xffffffff and call(9,0,0)[0]==0xffffffff and len(writes)==before
 assert not decode_surface(raw,token^1)
 bad=bytearray(raw);at=(8*800+0)*4
 # Flip one data bit cell: checksum must reject phase1, retain the other7.
 for y in range(8,16):
  for x in range(8):
   at=(y*800+x)*4;old=struct.unpack_from('<I',bad,at)[0];struct.pack_into('<I',bad,at,old^0x00ffffff)
 assert [r['phase'] for r in decode_surface(bad,token)]==list(range(2,9))
 png(image_path,raw)
 return {'scope':'Actual linked bounded pixel writer and cache loop; CP15 effects modeled. Every written framebuffer word, canary, mirrored surface and independent decoded record checked.',
 'bootstrap_sha256':hashlib.sha256(bootstrap.read_bytes()).hexdigest(),'candidate_sha256':json.loads((folder/'manifest.json').read_text())['candidate_sha256'],
 'phase_count':8,'pixel_writes_per_phase':3*4*8*256,'max_emulated_instructions_per_phase':max(costs),'cache_lines_per_phase':6000,
 'invalid_phase_zero_writes':True,'wrong_token_rejected':True,'corrupt_data_bit_checksum_rejected':True,'all_unselected_pixels_canaries_preserved':True,
 'no_timer_heap_storage_or_lcd_driver_calls':True,'irq_mask_preserved':True,'device_accessed':False,'physical_visibility_proved':False}
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for key in ['bootstrap','lk','folder','image','output']:p.add_argument('--'+key,type=Path,required=True)
 a=p.parse_args();r=validate(a.bootstrap,a.lk,a.folder,a.image);a.output.write_text(json.dumps(r,indent=2)+'\n');print('All8 bounded pixel phases, mirrors/canaries, wrong nonce and checksum controls passed')
