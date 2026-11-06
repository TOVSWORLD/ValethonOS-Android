#!/usr/bin/env python3
"""Offline known-boot-stack capture calibration; no install/arm/device operations."""
import argparse,hashlib,json,struct
from pathlib import Path
from validate_loader_checkpoint import elf
from validate_loader_complete import raw_elf,BASE
from validate_loader_console_reclaim import altered,SPANS
from validate_loader_observer import bl
from validate_loader_relocation import relative_references
import retained_log_mailbox as m
ORIGINAL_PAYLOAD='e10fdf770a5be2c2adc3cce0d03b8e296eac3b31e18ebdce5b56dc5491f4e7e8'
BASE_CANDIDATE='08fcf3455d66943632d0fc91348d4ab7d41b80c40d88e61272000a1d697faa1e'
ORIGINAL_SECTORS='4c6f355c735b9302b0d421ef38f94a9974214d531fa974a41edd8132af7ac092'
def sha(b):return hashlib.sha256(b).hexdigest()
def pack(module,bootstrap,objects,execution_report,base_image,base_report,nonce_file,original_sectors,output,nonce_rebinding=None):
 _,profile_symbols=raw_elf(bootstrap)
 if 'lbo_arrival' in profile_symbols:raise ValueError('Analysis-only screen witness is not admitted to physical packaging')
 if output.exists():raise ValueError('Fresh private candidate directory required')
 execution=json.loads(execution_report.read_text());assert execution['module_sha256']==sha(module.read_bytes()) and execution['bootstrap_sha256']==sha(bootstrap.read_bytes()) and execution['case_count']>=6
 assert objects, 'All module objects required'
 for obj in objects:relative_references(obj.read_bytes())
 seg,sym=elf(module,('lfo_frame_dispatch','lfo_state_bytes'));lo=min(x for x,_ in seg);end=max(x+len(b) for x,b in seg);blob=bytearray((end-lo+511)&~511)
 for at,data in seg:blob[at-lo:at-lo+len(data)]=data
 assert lo==0x41000000 and 512<=len(blob)<=16384
 state=execution['state_bytes'];assert 0<state<=12288
 image=bytearray(base_image.read_bytes());base_hash=sha(image);assert len(image)==m.PARTITION
 proof=None
 assert nonce_rebinding is None and base_hash==BASE_CANDIDATE, 'Only the exact original boot image is admitted'
 page=struct.unpack_from('<I',image,36)[0];assert page==2048
 sizes=[struct.unpack_from('<I',image,off)[0] for off in [8,16,24,40]];declared=page+sum((x+page-1)//page*page for x in sizes)
 offset=12*1024*1024;assert declared<offset and image[offset:offset+len(blob)]==bytes(len(blob)) and offset+len(blob)<m.BASE
 nonce=nonce_file.read_bytes();assert len(nonce)==32;assert base_report is None
 base={'baseline':'Exact original boot stack capture calibration','retained_mailbox':{}}
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
 pre_shutdown=execution.get('snapshot_stage')=='pre_shutdown'
 site,name,expected=(0x4bd3e3e8,'lbo_pre_shutdown','dff82037') if pre_shutdown else (0x4bd3e524,'lbo_handoff','fff7a0fc')
 if pre_shutdown:assert execution['new_site']==hex(site) and execution['original_irq_mask_helper_executed']
 final=0x1a00+site-0x4bd00000;assert sectors[final:final+4]==bytes.fromhex(expected);sectors[final:final+4]=bl(site,bs[name]&~1)
 before=original_sectors.read_bytes();changed={i for i,(a,b) in enumerate(zip(before,sectors)) if a!=b};allowed={i for a,b in SPANS for i in range(0xa00+a,0xa00+b)}|set(range(0xa00+0x736,0xa00+0x73a))|set(range(0xa00+0x778,0xa00+0x77c))|set(range(0xa72,0xa76))|set(range(final,final+4));assert changed<=allowed
 assert sectors[0xa00+0xb84:0xa00+0xbb8]==before[0xa00+0xb84:0xa00+0xbb8]
 base.update(partition_sha256=sha(image),loader_checkpoint_blob={'offset':offset,'bytes':len(blob),'sha256':sha(blob),'source_module_sha256':sha(module.read_bytes())});base['retained_mailbox']['prefix_sha256']=prefix
 report={'scope':'Known-boot-stack capture calibration; review and physical approval pending','candidate_sha256':sha(image),'observer_sha256':sha(sectors),'base_candidate_sha256':base_hash,'kernel_source_candidate_sha256':BASE_CANDIDATE,'fresh_nonce_rebinding':proof,'original_bootstrap_sha256':ORIGINAL_SECTORS,'module_blob_sha256':sha(blob),'module_bytes':len(blob),'state_bytes':state,'stack_bytes':4096,'base_declared_bytes_preserved':True,'kernel_instructions_unchanged':True,'declared_image_bytes':declared,'module_file_padding_offset':offset,'nonce_contract':'Fresh loader-only nonce and mailbox seed; original header, kernel, appended DTs and ramdisk unchanged','prefix_sha256':prefix,'seed_sha256':sha(image[m.BASE:m.SLOT_BASE]),'nonce_sha256':sha(nonce),'target_first_sector':18432,'logical_boot_first_sector':30325760,'changed_bootstrap_bytes':len(changed),'only_owned_console_read_and_handoff_spans_changed':True,'live_globals_unchanged':True,'headers_return_bootstrap_gpt_and_security_patch_bytes_unchanged':True,'only_embedded_lk_handoff_call_changed':True,'physical_execution_admitted':False,'hardware_acceptance':False,'review_limitations':['raw data-driver termination unqualified','real allocator initialization/capacity not observed; allocation failure returns without observer retry','IRQ-disabled first read declines observation','cache/controller effects and durability not hardware-qualified','MODE records normal mode at first redirected image read, not earlier mode-hook execution','final hook records call arguments, not SMC completion or kernel entry']}
 if pre_shutdown:
  original_final=0x1a00+0x3e524
  report.update(snapshot_stage='pre_shutdown',checkpoint_site=hex(site),original_smc_call_unchanged=sectors[original_final:original_final+4]==before[original_final:original_final+4],only_embedded_lk_handoff_call_changed=False,only_embedded_lk_pre_shutdown_load_changed=True,only_owned_console_read_and_handoff_spans_changed=False,only_owned_console_read_and_pre_shutdown_spans_changed=True)
  report['review_limitations'][-2:]=['MODE is sampled at an eligible read or pre-shutdown initialization; not earlier mode-hook or kernel-entry proof','pre_shutdown snapshots registers before interrupt masking/later teardown; not SMC completion or kernel entry']
  assert report['original_smc_call_unchanged']
 output.mkdir(mode=0o700)
 for name,data in [('boot-full.img',image),('observer-payload-sectors-private.bin',bytes(sectors)),('module.bin',bytes(blob)),('nonce.bin',nonce),('report.json',(json.dumps(base,indent=2)+'\n').encode()),('manifest.json',(json.dumps(report,indent=2)+'\n').encode())]:
  p=output/name;p.write_bytes(data);p.chmod(0o600)
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser();
 for n in ['module','bootstrap','execution-report','base-image','nonce-file','original-sectors','output']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--object',type=Path,action='append',required=True);p.add_argument('--nonce-rebinding',type=Path);a=p.parse_args();r=pack(a.module,a.bootstrap,a.object,a.execution_report,a.base_image,None,a.nonce_file,a.original_sectors,a.output,a.nonce_rebinding);print('Offline candidate packaged:',r['candidate_sha256'],r['observer_sha256'])
