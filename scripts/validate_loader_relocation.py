#!/usr/bin/env python3
"""Prove linked module's relative references and execute at modeled allocation bases."""
import argparse,hashlib,json,struct
from pathlib import Path
from validate_loader_checkpoint import elf,Machine

def relative_references(b):
 at=struct.unpack_from('<I',b,32)[0];size,count=struct.unpack_from('<HH',b,46);sections=[struct.unpack_from('<10I',b,at+i*size) for i in range(count)];counts={}
 for s in sections:
  if s[1]!=9 or not sections[s[7]][2]&2:continue
  for off in range(s[4],s[4]+s[5],s[9]):
   target,info=struct.unpack_from('<II',b,off);kind=info&255
   if kind not in [3,10,30,42]:raise ValueError('Allocated section contains non-relative reference: '+str(kind))
   counts[str(kind)]=counts.get(str(kind),0)+1

 return counts

def validate(path,objects):
 b=path.read_bytes();counts={};provenance={}
 for obj in objects:
  raw=obj.read_bytes();provenance[obj.name]=hashlib.sha256(raw).hexdigest()
  for kind,n in relative_references(raw).items():counts[kind]=counts.get(kind,0)+n
 if not counts:raise ValueError('Input object relocation evidence required')
 seg,sym=elf(path);cases=[]
 for placement in [0x43000000,0x44000000,0x4c100000]:
  f=Machine(seg,sym,relocation=placement-0x41000000);assert f.initial==0 and f.emit(1)==0
  assert f.emit(2,kind=1,size=2048,dst=0x45000000,first=8192,requested=100000*512,selected=8192*512)==0
  assert f.emit(3,entry=0x40000000,dt=0x44000000)==0
  assert f.latest()['sequence']==4 and f.hashes==1 and f.writes==9 and f.flushes==9
  assert bytes(f.image[:len(f.original)-1048576])==f.original[:len(f.original)-1048576]
  cases.append({'modeled_code_base':hex(placement),'mode_read_handoff_sequence':4,'passed':True})
 return {'scope':'PIC module in emulated allocations; no physical allocation or RAM claim','elf_sha256':hashlib.sha256(b).hexdigest(),'input_object_sha256':provenance,'allocated_input_relocation_types':counts,'cases':cases,'module_position_independent_for_tested_paths':True,'runtime_relocations_required':False,'hardware_memory_ownership_proved':False,'physical_commands':False,'device_accessed':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--object',type=Path,action='append',required=True);a=p.parse_args();r=validate(a.elf,a.object);a.output.write_text(json.dumps(r,indent=2)+'\n');print('PIC allocated-base controls passed:',len(r['cases']))
