#!/usr/bin/env python3
"""Create a standalone PIC blob; inspect candidate padding, never alter boot images."""
import argparse,hashlib,json,struct
from pathlib import Path
from validate_loader_checkpoint import elf
from validate_loader_relocation import relative_references

def pack(path,objects,module_report,candidate,output):
 b=path.read_bytes();report=json.loads(module_report.read_text())
 if report['elf_sha256']!=hashlib.sha256(b).hexdigest() or report['state_bytes']!=8584:raise ValueError('Module execution report differs')
 expected=set(report['object_sha256'].values())
 actual={hashlib.sha256(obj.read_bytes()).hexdigest() for obj in objects}
 if len(objects)!=len(expected) or actual!=expected:raise ValueError('Module input objects differ from execution report')
 for obj in objects:relative_references(obj.read_bytes())
 segments,symbols=elf(path,('lm_start','lm_emit'));base=min(a for a,data in segments);end=max(a+len(data) for a,data in segments);used=end-base;n=(used+511)&~511
 if base!=0x41000000 or not 512<=n<=8192:raise ValueError('Module extent differs')
 flat=bytearray(n)
 for at,data in segments:flat[at-base:at-base+len(data)]=data
 starts={name:(value-base) for name,value in symbols.items()}
 ph=struct.unpack_from('<I',b,28)[0];es,count=struct.unpack_from('<HH',b,42);executable=[]
 for i in range(count):
  kind,off,addr,paddr,files,total,flags,align=struct.unpack_from('<8I',b,ph+i*es)
  if kind==1 and flags&1:executable.append((addr,addr+files))
 for value in symbols.values():
  if not value&1 or not any(lo<=value-1<hi for lo,hi in executable):raise ValueError('Entry outside Thumb text')
 image=candidate.read_bytes()
 if len(image)!=16*1024*1024 or image[:8]!=b'ANDROID!':raise ValueError('Exact-size candidate Android image required')
 kernel,ramdisk,second=struct.unpack_from('<I',image,8)[0],struct.unpack_from('<I',image,16)[0],struct.unpack_from('<I',image,24)[0]
 page,dt=struct.unpack_from('<II',image,36)
 if page!=2048:raise ValueError('Unexpected header page')
 declared=page+sum((size+page-1)//page*page for size in [kernel,ramdisk,second,dt]);offset=12*1024*1024
 if declared>offset or offset+n>15*1024*1024 or image[offset:offset+n]!=bytes(n):raise ValueError('Blob file-padding interval not empty or overlaps declared image/mailbox')
 result={'scope':'Standalone source module blob and readonly file-padding proof; no candidate modification/install','elf_sha256':hashlib.sha256(b).hexdigest(),'blob_sha256':hashlib.sha256(flat).hexdigest(),'blob_bytes':n,'linked_bytes':used,'state_bytes':8584,'stack_capacity':4096,'entry_offsets':starts,'candidate_sha256':hashlib.sha256(image).hexdigest(),'candidate_declared_image_bytes':declared,'proposed_blob_offset':offset,'proposed_file_interval_zero':True,'physical_memory_or_load_admitted':False,'boot_image_modified':False,'device_accessed':False}
 output.mkdir(mode=0o700,parents=False,exist_ok=False);(output/'module.bin').write_bytes(flat);(output/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--object',type=Path,action='append',required=True);p.add_argument('--module-report',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=pack(a.elf,a.object,a.module_report,a.candidate,a.out);print('Standalone module blob bytes:',r['blob_bytes'])
