#!/usr/bin/env python3
"""Offline copy-corrected known-stack control. No deployment or admission."""
import argparse,hashlib,json,struct
from pathlib import Path
from audit_loader_copy_boundary import materialize,SITE,LK
from validate_loader_complete import raw_elf,BASE
from validate_loader_checkpoint import elf
from validate_loader_observer import bl
from validate_loader_relocation import relative_references
import retained_log_mailbox as m
PREFIX=0x4bcfe600
ORIGINAL='4c6f355c735b9302b0d421ef38f94a9974214d531fa974a41edd8132af7ac092'
BOOT='08fcf3455d66943632d0fc91348d4ab7d41b80c40d88e61272000a1d697faa1e'
def sha(b):return hashlib.sha256(b).hexdigest()
def assemble(module,bootstrap,module_report,objects,header,original_sectors,original_boot,nonce_file,out):
 if out.exists():raise ValueError('Fresh output required')
 report=json.loads(module_report.read_text());assert report['elf_sha256']==sha(module.read_bytes()) and report['case_count']>=12
 state=report['state_bytes'];assert 0<state<=12288
 assert objects
 for obj in objects:relative_references(obj.read_bytes())
 seg,sym=elf(module,('lfo_frame_dispatch','lfo_state_bytes'));lo=min(a for a,_ in seg);hi=max(a+len(b) for a,b in seg)
 assert lo==0x41000000
 blob=bytearray((hi-lo+511)&~511)
 for at,data in seg:blob[at-lo:at-lo+len(data)]=data
 assert 512<=len(blob)<=16384
 boot=bytearray(original_boot.read_bytes());assert len(boot)==m.PARTITION and sha(boot)==BOOT
 page=struct.unpack_from('<I',boot,36)[0];assert page==2048
 declared=page+sum((struct.unpack_from('<I',boot,at)[0]+page-1)//page*page for at in [8,16,24,40])
 assert declared==7796736 and boot[12*1024*1024:12*1024*1024+len(blob)]==bytes(len(blob))
 nonce=nonce_file.read_bytes();assert len(nonce)==32 and any(nonce)
 boot[12*1024*1024:12*1024*1024+len(blob)]=blob;boot[m.BASE:]=bytes(m.PARTITION-m.BASE)
 control=b'VALETHON HOST CONTROL v1\nThis is a preinstalled retention control, NOT a kernel log.\n'
 boot,prefix=m.prepare(bytes(boot),nonce,control)
 before=original_sectors.read_bytes();assert len(before)==492544 and sha(before)==ORIGINAL and before[:0x900]==bytes(0x900)
 sectors=bytearray(before);sections,bs=raw_elf(bootstrap)
 assert all(k in bs for k in ['lbo_install_hook','lw_screen','lbo_arrival','lbo_hook_word','lbo_pre_shutdown']) and 'lbo_read' not in bs
 for at,data in sections:
  assert PREFIX<=at and at+len(data)<=PREFIX+0x900
  sectors[at-PREFIX:at-PREFIX+len(data)]=data
 entry=(sym['lfo_frame_dispatch']-lo)|1
 load=struct.pack('<6I32sQQ',len(blob),state,4096,entry,entry,1,hashlib.sha256(blob).digest(),18432,12*1024*1024)
 config=struct.pack('<32s32sQQ5I4xI4x',nonce,bytes.fromhex(prefix),18432,30325760,m.PARTITION,5,8,1,1,BASE+9)
 for name,data in [('lbo_load_plan',load),('lbo_frontend',config),('lbo_hook_word',bl(SITE,bs['lbo_pre_shutdown']&~1))]:
  at=bs[name]-PREFIX;sectors[at:at+len(data)]=data
 assert before[0xa00+0x386:0xa00+0x38a]==bl(BASE+0x386,BASE+0x736)
 sectors[0xa00+0x386:0xa00+0x38a]=bl(BASE+0x386,bs['lbo_arrival']&~1)
 for off in [0x736,0x778]:sectors[0xa00+off:0xa00+off+4]=bytes.fromhex('00207047')
 assert struct.unpack_from('<7I',before,0x960)==(0x4bd72a5f,BASE,0x1000,0x4bd3c740,0x4bd00151,0xdead,BASE)
 struct.pack_into('<II',sectors,0x964,PREFIX,0x1a00)
 allowed=set(range(0x900))|set(range(0x964,0x96c))|set(range(0xd86,0xd8a))|set(range(0x1136,0x113a))|set(range(0x1178,0x117c))
 changed={i for i,(a,b) in enumerate(zip(before,sectors)) if a!=b};assert changed<=allowed
 assert sectors[0x1a00:]==before[0x1a00:] and sectors[0xa72:0xa76]==before[0xa72:0xa76]
 # Sparse loading must contain every linked byte. LK tail remains native until
 # actual resident main installs the late instruction at runtime.
 count,addr=struct.unpack_from('<II',header.read_bytes(),8);assert addr+count==LK+0x3c8
 assert sha(boot[:declared])==sha(original_boot.read_bytes()[:declared])
 result={'scope':'Offline copy-corrected known-stack capture control; fresh exact review/approval required',
 'candidate_sha256':sha(boot),'observer_sha256':sha(sectors),'original_bootstrap_sha256':ORIGINAL,
 'base_candidate_sha256':BOOT,'module_sha256':sha(module.read_bytes()),'bootstrap_sha256':sha(bootstrap.read_bytes()),
 'module_blob_sha256':sha(blob),'module_bytes':len(blob),'state_bytes':state,'stack_bytes':4096,
 'module_object_sha256':{o.name:sha(o.read_bytes()) for o in objects},
 'prefix_sha256':prefix,'seed_sha256':sha(boot[m.BASE:m.SLOT_BASE]),'nonce_sha256':sha(nonce),'screen_token':f'{int.from_bytes(nonce[:2],"little"):04x}',
 'target_first_sector':18432,'logical_boot_first_sector':30325760,'declared_image_bytes':declared,
 'base_declared_bytes_preserved':True,'kernel_instructions_unchanged':True,'embedded_lk_tail_unchanged':True,
 'original_resident_read_hook_unchanged':True,'prefix_loaded_ram_span':[hex(PREFIX),hex(PREFIX+0x900)],
 'rop_cache_span':[hex(PREFIX),hex(PREFIX+0x1a00)],'runtime_hook_site':hex(SITE),
 'arrival_call_site':hex(BASE+0x386),'changed_bootstrap_bytes':len(changed),'snapshot_stage':'pre_shutdown','checkpoint_site':hex(SITE),
 'screen_allocation':[hex(0x98600000),hex(0x991b8000)],'screen_driver_timer_storage_calls':False,
 'physical_execution_admitted':False,'hardware_acceptance':False,'approval_consumed':False}
 base={'partition_sha256':sha(boot),'retained_mailbox':{'prefix_sha256':prefix},'loader_checkpoint_blob':{'offset':12*1024*1024,'bytes':len(blob),'sha256':sha(blob)}}
 out.mkdir(mode=0o700)
 for name,data in [('boot-full.img',boot),('observer-payload-sectors-private.bin',sectors),('module.bin',blob),('nonce.bin',nonce),('manifest.json',(json.dumps(result,indent=2)+'\n').encode()),('report.json',(json.dumps(base,indent=2)+'\n').encode())]:
  p=out/name;p.write_bytes(data);p.chmod(0o600)
 return result
if __name__=='__main__':
 a=argparse.ArgumentParser()
 for n in ['module','bootstrap','module-report','header','original-sectors','original-boot','nonce-file','out']:a.add_argument('--'+n,type=Path,required=True)
 a.add_argument('--object',type=Path,action='append',required=True);x=a.parse_args();r=assemble(x.module,x.bootstrap,x.module_report,x.object,x.header,x.original_sectors,x.original_boot,x.nonce_file,x.out);print('Offline exact pair:',r['candidate_sha256'],r['observer_sha256'])
