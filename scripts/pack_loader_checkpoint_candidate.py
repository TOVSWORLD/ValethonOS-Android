#!/usr/bin/env python3
"""Offline exact loader-checkpoint candidate; no install/arm/device operations."""
import argparse,hashlib,json,struct
from pathlib import Path
from validate_loader_checkpoint import elf
from validate_loader_complete import raw_elf,BASE
from validate_loader_console_reclaim import altered,SPANS
from validate_loader_observer import bl
from validate_loader_relocation import relative_references
import retained_log_mailbox as m
ORIGINAL_PAYLOAD='e10fdf770a5be2c2adc3cce0d03b8e296eac3b31e18ebdce5b56dc5491f4e7e8'
BASE_CANDIDATE='8d3729e6869371ba80aa2da6e1c6d29dbbf1e84ba5ed6b431f1a66354141be16'
ORIGINAL_SECTORS='4c6f355c735b9302b0d421ef38f94a9974214d531fa974a41edd8132af7ac092'
def sha(b):return hashlib.sha256(b).hexdigest()
def pack(module,bootstrap,objects,execution_report,base_image,base_report,nonce_file,original_sectors,output,nonce_rebinding=None):
 _,profile_symbols=raw_elf(bootstrap)
 if 'lbo_arrival' in profile_symbols:raise ValueError('Analysis-only screen witness is not admitted to physical packaging')
 raise ValueError('Historical embedded-LK tail-hook packer disabled: hook lies outside actual bootstrap copy; use pack_loader_copy_control.py')
 if output.exists():raise ValueError('Fresh private candidate directory required')
 execution=json.loads(execution_report.read_text());assert execution['module_sha256']==sha(module.read_bytes()) and execution['bootstrap_sha256']==sha(bootstrap.read_bytes()) and execution['case_count']>=6
 for obj in objects:relative_references(obj.read_bytes())
 seg,sym=elf(module,('lfo_frame_dispatch','lfo_state_bytes'));lo=min(x for x,_ in seg);end=max(x+len(b) for x,b in seg);blob=bytearray((end-lo+511)&~511)
 for at,data in seg:blob[at-lo:at-lo+len(data)]=data
 assert lo==0x41000000 and 512<=len(blob)<=16384
 state=execution['state_bytes'];assert 0<state<=12288
 image=bytearray(base_image.read_bytes());base_hash=sha(image);assert len(image)==m.PARTITION
 proof=json.loads(nonce_rebinding.read_text()) if nonce_rebinding else None
 if base_hash!=BASE_CANDIDATE:
  assert proof and proof['parent_candidate_sha256']==BASE_CANDIDATE and proof['candidate_sha256']==base_hash and proof['init_only_named_nonexecutable_nonce_changed'] and proof['dt_only_unique_nonce_property_bytes_changed']
 page=struct.unpack_from('<I',image,36)[0];assert page==2048
 sizes=[struct.unpack_from('<I',image,off)[0] for off in [8,16,24,40]];declared=page+sum((x+page-1)//page*page for x in sizes)
 offset=12*1024*1024;assert declared<offset and image[offset:offset+len(blob)]==bytes(len(blob)) and offset+len(blob)<m.BASE
 nonce=nonce_file.read_bytes();base=json.loads(base_report.read_text());m.validate_seed(image,nonce,base['retained_mailbox']['prefix_sha256'])
 image[offset:offset+len(blob)]=blob;image[m.BASE:]=bytes(m.PARTITION-m.BASE)
 control=b'VALETHON HOST CONTROL v1\nThis is a preinstalled retention control, NOT a kernel log.\n';image,prefix=m.prepare(bytes(image),nonce,control);assert m.inspect(image,nonce,prefix)['latest']['sequence']==1
 assert image[:declared]==base_image.read_bytes()[:declared]
 sectors=bytearray(original_sectors.read_bytes());assert len(sectors)==492544 and sha(sectors)==ORIGINAL_SECTORS and sha(sectors[:492132])==ORIGINAL_PAYLOAD
 r=bytearray(altered(sectors[0xa00:0x1800]));sections,bs=raw_elf(bootstrap)
 for at,data in sections:
  if not any(BASE+a<=at and at+len(data)<=BASE+b for a,b in SPANS):raise ValueError('Linked bootstrap leaves owned spans')
  r[at-BASE:at-BASE+len(data)]=data
 entry=(sym['lfo_frame_dispatch']-lo)|1
 load=struct.pack('<6I32sQQ',len(blob),state,4096,entry,entry,1,hashlib.sha256(blob).digest(),18432,offset)
 config=struct.pack('<32s32sQQ5I4xI4x',nonce,bytes.fromhex(prefix),18432,30325760,m.PARTITION,5,8,1,1,BASE+9)
 for name,data in [('lbo_load_plan',load),('lbo_frontend',config)]:
  at=bs[name]-BASE;r[at:at+len(data)]=data
 r[0x72:0x76]=bl(BASE+0x72,bs['lbo_read']&~1);sectors[0xa00:0x1800]=r
 final=0x1a00+0x3e524;assert sectors[final:final+4]==bytes.fromhex('fff7a0fc');sectors[final:final+4]=bl(0x4bd3e524,bs['lbo_handoff']&~1)
 before=original_sectors.read_bytes();changed={i for i,(a,b) in enumerate(zip(before,sectors)) if a!=b};allowed={i for a,b in SPANS for i in range(0xa00+a,0xa00+b)}|set(range(0xa00+0x736,0xa00+0x73a))|set(range(0xa00+0x778,0xa00+0x77c))|set(range(0xa72,0xa76))|set(range(final,final+4));assert changed<=allowed
 assert sectors[0xa00+0xb84:0xa00+0xbb8]==before[0xa00+0xb84:0xa00+0xbb8]
 base.update(partition_sha256=sha(image),loader_checkpoint_blob={'offset':offset,'bytes':len(blob),'sha256':sha(blob),'source_module_sha256':sha(module.read_bytes())});base['retained_mailbox']['prefix_sha256']=prefix
 report={'scope':'Offline exact changed loader checkpoint candidate; review and physical approval pending','candidate_sha256':sha(image),'observer_sha256':sha(sectors),'base_candidate_sha256':base_hash,'kernel_source_candidate_sha256':BASE_CANDIDATE,'fresh_nonce_rebinding':proof,'original_bootstrap_sha256':ORIGINAL_SECTORS,'module_blob_sha256':sha(blob),'module_bytes':len(blob),'state_bytes':state,'stack_bytes':4096,'base_declared_bytes_preserved':True,'kernel_instructions_unchanged':True,'declared_image_bytes':declared,'module_file_padding_offset':offset,'nonce_contract':'Fresh trial nonce bound to the named non-executable PID1 constant and DT property; fresh prefix/seed, no old approval/record/receipt reused.' if proof else 'Historical exact nonce contract; not selected for new trial','prefix_sha256':prefix,'seed_sha256':sha(image[m.BASE:m.SLOT_BASE]),'nonce_sha256':sha(nonce),'target_first_sector':18432,'logical_boot_first_sector':30325760,'changed_bootstrap_bytes':len(changed),'only_owned_console_read_and_handoff_spans_changed':True,'live_globals_unchanged':True,'headers_return_bootstrap_gpt_and_security_patch_bytes_unchanged':True,'only_embedded_lk_handoff_call_changed':True,'physical_execution_admitted':False,'hardware_acceptance':False,'review_limitations':['raw data-driver termination unqualified','real allocator initialization/capacity not observed; allocation failure returns without observer retry','IRQ-disabled first read declines observation','cache/controller effects and durability not hardware-qualified','MODE records normal mode at first redirected image read, not earlier mode-hook execution','final hook records call arguments, not SMC completion or kernel entry']}
 output.mkdir(mode=0o700)
 for name,data in [('boot-full.img',image),('observer-payload-sectors-private.bin',bytes(sectors)),('module.bin',bytes(blob)),('nonce.bin',nonce),('report.json',(json.dumps(base,indent=2)+'\n').encode()),('manifest.json',(json.dumps(report,indent=2)+'\n').encode())]:
  p=output/name;p.write_bytes(data);p.chmod(0o600)
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser();
 for n in ['module','bootstrap','execution-report','base-image','base-report','nonce-file','original-sectors','output']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--object',type=Path,action='append',required=True);p.add_argument('--nonce-rebinding',type=Path);a=p.parse_args();r=pack(a.module,a.bootstrap,a.object,a.execution_report,a.base_image,a.base_report,a.nonce_file,a.original_sectors,a.output,a.nonce_rebinding);print('Offline candidate packaged:',r['candidate_sha256'],r['observer_sha256'])
