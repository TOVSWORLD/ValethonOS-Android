#!/usr/bin/env python3
"""Full ACK/PID1 candidate with permanent-text fixmap console and existing deadline."""
import json,subprocess
from pathlib import Path
from prepare_ack_combined_bundle import prepare as prior_prepare,sha
from build_ack_cinit_console import build as console
from build_ack_combined_entry import build as entry
from compare_pmic_dtb import snapshot
from prepare_native_jump_bundle import raw
KIND='ack-linux-cinit-v3'

def prepare(source_dtb,iomem,draft_dtb,image,config,initramfs,init_report,nonce,linked,out,fdtget,fdtput,system_map,trial_id=None):
 out.mkdir(mode=0o700)
 m=prior_prepare(source_dtb,iomem,draft_dtb,image,config,initramfs,init_report,nonce,linked,out/'prior-private',fdtget,fdtput,system_map,trial_id)
 im,c=console(image,system_map,out/'console-private',nonce.hex())
 dt=out/'target-private.dtb';dt.write_bytes((out/'prior-private/target-private.dtb').read_bytes())
 tree=snapshot(fdtget,dt);args=raw(tree['/chosen']['bootargs']).rstrip(b'\0').decode().split()
 if any(a.startswith('earlycon') or a=='keep_bootcon' or a=='initcall_debug' for a in args):raise ValueError('Unexpected prior console/debug options')
 args=[a for a in args if not a.startswith(('ramoops.','loglevel='))]
 args+=['loglevel=8','ignore_loglevel']
 args+=['earlycon=uart8250,mmio32,0x444bf000','keep_bootcon','initcall_debug']
 subprocess.run([str(fdtput),'-t','s',str(dt),'/chosen','bootargs',' '.join(args)],check=True)
 padded=im+bytes(m['image_memory_bytes']-len(im));code,e=entry(out/'entry-private',m['trial_id'],padded)
 data=dt.read_bytes()
 if len(data)>0x18000:raise ValueError('DT overlaps integrity entry')
 meta=bytearray(0x28000);meta[:len(data)]=data;meta[0x18000:0x18000+len(code)]=code
 m.pop('kernel_hooks');m.update(scope='Full maintained ACK/PID1 with retained early C-init console; unexecuted',target_kind=KIND,target_image_sha256=sha(im),target_dtb_sha256=sha(data),image_padded_sha256=sha(padded),deadline=e,cinit_console=c,legacy_entry_hooks_removed=True,ramoops_target_mapping_disabled=True,segments=[])
 for name,data,address,memory in [('image.bin',im,0x40000000,len(padded)),('metadata.bin',bytes(meta),0x42000000,0x28000),('initrd.bin',initramfs,0x69244000,(len(initramfs)+4095)&~4095)]:
  p=out/name;p.write_bytes(data);p.chmod(0o600);m['segments'].append(dict(file=name,sha256=sha(data),bytes=len(data),address=address,memory_bytes=memory))
 (out/'report.json').write_text(json.dumps(m,indent=2)+'\n');(out/'report.json').chmod(0o600);dt.chmod(0o600)
 return m
