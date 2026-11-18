#!/usr/bin/env python3
"""Reclaim console-only resident bytes in RAM; never writes a boot candidate."""
import argparse,hashlib,json,struct
from pathlib import Path
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ
import audit_resident_loader_payload as a
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_OP_IMM
# Leave return sinks at printf and puts entries. Preserve libc memory/string helpers.
SPANS=[(0x524,0x5d8),(0x618,0x736),(0x73a,0x778),(0x77c,0x794),(0x88e,0xa51),(0xbb8,0xe00)]
def altered(resident):
 r=bytearray(resident)
 for lo,hi in SPANS:r[lo:hi]=b'\xa5'*(hi-lo)
 r[0x736:0x73a]=r[0x778:0x77c]=bytes.fromhex('00207047')
 return bytes(r)
def validate(resident):
 r=altered(resident);real=a.machine;seen=[]
 def machine(*args,**kw):
  kw['suppress']=(a.BASE+0x736,);u,state,word=real(*args,**kw)
  def access(uc,access,address,size,value,data):
   if any(a.BASE+lo<=address<a.BASE+hi for lo,hi in SPANS):raise AssertionError('Reclaimed console bytes read')
  def code(uc,address,size,data):
   if any(a.BASE+lo<=address<a.BASE+hi for lo,hi in SPANS):raise AssertionError('Reclaimed console code reached')
  u.hook_add(UC_HOOK_MEM_READ,access);u.hook_add(UC_HOOK_CODE,code);seen.append(state);return u,state,word
 a.machine=machine
 try:report=a.audit(r,Path('sources/reference-amonet-douglas/lk-payload'))
 finally:a.machine=real
 # Every direct resident branch in preserved code must avoid reclaimed spans.
 md=Cs(CS_ARCH_ARM,CS_MODE_THUMB);md.detail=True;branches=[]
 # Known function/code intervals from pinned entries; literal pools excluded.
 for lo,hi in [(8,0xe0),(0x100,0x24c),(0x254,0x284),(0x284,0x4a0),(0x5d8,0x618),(0x794,0x830)]:
  for ins in md.disasm(resident[lo:hi],a.BASE+lo):
   if ins.mnemonic.startswith(('b','cb')) and ins.operands and ins.operands[-1].type==CS_OP_IMM:
    target=ins.operands[-1].imm
    if a.BASE<=target<a.BASE+0xe00:
     assert not any(a.BASE+l<=target<a.BASE+h for l,h in SPANS),(hex(ins.address),hex(target))
     branches.append([hex(ins.address),hex(target)])
 return {'scope':'poisoned console-only spans in isolated resident emulator; firmware services modeled','archive_payload_sha256':a.SHA,'reclaimed_bytes':sum(hi-lo for lo,hi in SPANS),'spans':[[hex(lo),hex(hi)] for lo,hi in SPANS],'preserved_console_sinks':['0x736..0x73a','0x778..0x77c'],'preserved_direct_branches_checked':len(branches),'main_cases':report['main_cases'],'read_cases':report['read_cases'],'globals_memory_string_flag_gpt_helpers_preserved':True,'source_attribution_retained_in_repository':True,'physical_placement_admitted':False,'device_accessed':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--payload',type=Path,required=True);p.add_argument('--output',type=Path,required=True);x=p.parse_args();b=x.payload.read_bytes();assert hashlib.sha256(b).hexdigest()==a.SHA;r=validate(b[0xa00:0x1800]);x.output.write_text(json.dumps(r,indent=2)+'\n');print('Console reclaim modeled matrix passed:',r['reclaimed_bytes'])
