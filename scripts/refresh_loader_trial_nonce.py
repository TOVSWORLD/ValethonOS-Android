#!/usr/bin/env python3
"""Rebind only the named PID1 nonce constant and DT nonce, then repack offline."""
import argparse,gzip,hashlib,json,secrets,struct,zlib
from pathlib import Path
from pack_lab_log_boot import assemble,CONTRACT,METADATA
import retained_log_mailbox as m
PARENT='8d3729e6869371ba80aa2da6e1c6d29dbbf1e84ba5ed6b431f1a66354141be16'
def sha(b):return hashlib.sha256(b).hexdigest()
def refresh(base,report_file,old_nonce_file,init_file,output,new_nonce_file=None):
 if output.exists():raise ValueError('Fresh nonce output required')
 image=base.read_bytes();report=json.loads(report_file.read_text());old=old_nonce_file.read_bytes();init=init_file.read_bytes();assert sha(image)==PARENT and sha(old)==report['nonce_sha256']
 page=2048;k=struct.unpack_from('<I',image,8)[0];r=struct.unpack_from('<I',image,16)[0];kernel=image[page:page+k];at=page+((k+page-1)//page)*page;ramdisk=image[at:at+r];raw=gzip.decompress(ramdisk);assert raw.count(init)==1 and init.count(old)==1
 # Locate the exact named static constant in allocated, non-executable ELF data.
 shoff=struct.unpack_from('<Q',init,40)[0];es,n=struct.unpack_from('<HH',init,58);sections=[struct.unpack_from('<IIQQQQIIQQ',init,shoff+i*es) for i in range(n)];found=[]
 for sec in sections:
  if sec[1]!=2:continue
  strings_sec=sections[sec[6]];strings=init[strings_sec[4]:strings_sec[4]+strings_sec[5]]
  for pos in range(sec[4],sec[4]+sec[5],sec[9]):
   name,info,other,index,value,size=struct.unpack_from('<IBBHQQ',init,pos)
   if strings[name:].split(b'\0')[0]!=b'lab_trial_nonce':continue
   target=sections[index];assert size==32 and target[2]&2 and not target[2]&4
   off=target[4]+value-target[3];assert init[off:off+32]==old;found.append(off)
 assert len(found)==1
 new=new_nonce_file.read_bytes() if new_nonce_file else secrets.token_bytes(32);assert len(new)==32 and any(new) and new!=old;patched=init[:found[0]]+new+init[found[0]+32:];assert len(patched)==len(init)
 raw_new=raw.replace(init,patched);assert raw_new.count(new)==1 and raw_new.replace(new,old)==raw
 compressed=bytearray(gzip.compress(raw_new,mtime=0));compressed[9]=255;compressed=bytes(compressed)
 dec=zlib.decompressobj(31);decoded=dec.decompress(kernel);gzip_bytes=len(kernel)-len(dec.unused_data);dt_at=(gzip_bytes+3)&~3;dt=kernel[dt_at:];assert struct.unpack_from('>II',dt)==(0xd00dfeed,len(dt)) and dt.count(old)==1
 dt_new=dt.replace(old,new);assert len(dt_new)==len(dt) and dt_new.replace(new,old)==dt
 full,packed=assemble(decoded,kernel[:gzip_bytes],dt_new,compressed,json.loads(CONTRACT.read_text()),json.loads(METADATA.read_text()))
 full,prefix=m.prepare(full,new,b'VALETHON HOST CONTROL v1\nThis is a preinstalled retention control, NOT a kernel log.\n')
 report.update(packed);report['nonce_sha256']=sha(new);report['retained_mailbox']['prefix_sha256']=prefix
 proof={'scope':'Offline fresh nonce data rebinding; no kernel/PID1 instruction rebuild','parent_candidate_sha256':PARENT,'candidate_sha256':sha(full),'kernel_decoded_sha256':sha(decoded),'kernel_gzip_sha256':sha(kernel[:gzip_bytes]),'init_before_sha256':sha(init),'init_after_sha256':sha(patched),'init_nonce_file_offset':found[0],'init_only_named_nonexecutable_nonce_changed':True,'dt_only_unique_nonce_property_bytes_changed':True,'archive_headers_policy_and_all_other_init_bytes_unchanged':True,'nonce_sha256':sha(new),'source_compiled_again':False,'device_accessed':False}
 output.mkdir(mode=0o700)
 for name,data in [('boot-full.img',full),('nonce.bin',new),('report.json',(json.dumps(report,indent=2)+'\n').encode()),('nonce-rebinding.json',(json.dumps(proof,indent=2)+'\n').encode())]:
  p=output/name;p.write_bytes(data);p.chmod(0o600)
 print('Fresh nonce rebound in named PID1 data and DT; kernel instructions unchanged')
if __name__=='__main__':
 p=argparse.ArgumentParser();
 for n in ['base','report','old-nonce','init','output']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--new-nonce-file',type=Path);a=p.parse_args();refresh(a.base,a.report,a.old_nonce,a.init,a.output,a.new_nonce_file)
