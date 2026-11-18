#!/usr/bin/env python3
"""Keep the proven RAM-fixed kernel; remove verbose initcall proof for USB work."""
import json,subprocess
from prepare_ack_ramfix_bundle import prepare as ramfix_prepare
from prepare_ack_combined_bundle import sha
from compare_pmic_dtb import snapshot
from prepare_native_jump_bundle import raw

def prepare(source_dtb,iomem,draft_dtb,image,config,initramfs,init_report,nonce,linked,out,fdtget,fdtput,system_map,trial_id=None,*,storage_readonly=False):
 m=ramfix_prepare(source_dtb,iomem,draft_dtb,image,config,initramfs,init_report,nonce,linked,out,fdtget,fdtput,system_map,trial_id,storage_readonly=storage_readonly)
 dt=out/'target-private.dtb';tree=snapshot(fdtget,dt)
 values=raw(tree['/chosen']['bootargs']).rstrip(b'\0').decode().split()
 values=[a for a in values if a not in ['initcall_debug','ignore_loglevel'] and not a.startswith('loglevel=')]+['loglevel=7']
 subprocess.run([str(fdtput),'-t','s',str(dt),'/chosen','bootargs',' '.join(values)],check=True)
 data=dt.read_bytes()
 if len(data)>0x18000:raise ValueError('DT exceeds metadata capacity')
 meta=bytearray((out/'metadata.bin').read_bytes());meta[:0x18000]=bytes(0x18000);meta[:len(data)]=data;(out/'metadata.bin').write_bytes(meta)
 m.update(end_to_end_only=True,verbose_initcall_tracing=False,target_dtb_sha256=sha(data))
 for seg in m['segments']:
  if seg['file']=='metadata.bin':seg['sha256']=sha(meta)
 (out/'report.json').write_text(json.dumps(m,indent=2)+'\n');return m
