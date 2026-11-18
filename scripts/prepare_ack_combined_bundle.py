#!/usr/bin/env python3
"""Prepare one full ACK RAM candidate with image integrity and in-kernel checkpoints."""
import hashlib,json,struct
from pathlib import Path
from prepare_ack_native_bundle import prepare as base_prepare, reserve_union, reservation_map, reserved_nodes, IMAGE_SHA
from prepare_native_jump_bundle import ranges_ok, raw
from compare_pmic_dtb import snapshot
from build_ack_kernel_hooks import build as hooks
from build_ack_combined_entry import build as entry

KIND='ack-linux-combined-v2'
METADATA_END=0x42028000

def sha(b):return hashlib.sha256(b).hexdigest()

def prepare(source_dtb,iomem,draft_dtb,image,config,initramfs,init_report,nonce,linked,out,fdtget,fdtput,system_map,trial_id=None,*,storage_readonly=False):
 out.mkdir(mode=0o700)
 base=out/'base-private'
 m=base_prepare(source_dtb,iomem,draft_dtb,image,config,initramfs,init_report,nonce,linked,base,fdtget,fdtput,trial_id=trial_id,storage_readonly=storage_readonly)
 instrumented,h=hooks(image,system_map,out/'hooks-private',m['trial_id'])
 extent=m['image_memory_bytes'];padded=instrumented+bytes(extent-len(instrumented))
 code,e=entry(out/'entry-private',m['trial_id'],padded)
 # Keep the whole metadata/table/stack region reserved while early kernel code
 # uses its page table. This is target-owned reservation, not firmware overlap.
 # Normalize only overlapping memory declarations. The working DT itself
 # carries an old 512MiB declaration overlapping the bootloader's real banks.
 # Retain adjacency boundaries and preserve the exact union, not donor size.
 t=snapshot(fdtget,base/'target-private.dtb')
 memories=[n for n,p in t.items() if n.startswith('/memory') and 'device_type' in p and raw(p['device_type'])==b'memory\0']
 if len(memories)!=1:raise ValueError('One target memory node required')
 data=raw(t[memories[0]]['reg'])
 if len(data)%16:raise ValueError('64-bit memory address/size tuples required')
 banks=sorted((a,a+n) for a,n in struct.iter_unpack('>QQ',data) if n)
 merged=[]
 for a,z in banks:
  if not a<z<1<<64:raise ValueError('Memory bank overflow')
  if merged and a<merged[-1][1]:merged[-1]=(merged[-1][0],max(z,merged[-1][1]))
  else:merged.append((a,z))
 cells=[v for a,z in merged for v in [a>>32,a&0xffffffff,(z-a)>>32,(z-a)&0xffffffff]]
 import subprocess
 subprocess.run([str(fdtput),'-t','x',str(base/'target-private.dtb'),memories[0],'reg',*[format(v,'x') for v in cells]],check=True)
 subprocess.run([str(fdtput),'-t','s',str(base/'target-private.dtb'),'/psci','status','okay'],check=True)
 dt,reserves=reserve_union((base/'target-private.dtb').read_bytes(),[(0x42000000,METADATA_END)])
 if len(dt)>0x18000:raise ValueError('Expanded DT overlaps entry')
 metadata=bytearray(METADATA_END-0x42000000);metadata[:len(dt)]=dt;metadata[0x18000:0x18000+len(code)]=code
 if any(metadata[0x20000:]):raise ValueError('Table/stack must begin zeroed')
 # Recheck the enlarged region against source firmware and all existing target
 # reserved nodes; own metadata reservation is the only intentional overlap.
 import re
 from prepare_ack_native_bundle import reserved_nodes
 ram=[(int(a,16),int(z,16)+1) for a,z in re.findall(r'^([0-9a-f]+)-([0-9a-f]+) : System RAM$',iomem,re.M)]
 firmware=reservation_map(source_dtb)[2]+reserved_nodes(snapshot(fdtget,base/'source-private.dtb'))+reserved_nodes(snapshot(fdtget,base/'target-private.dtb'))
 segments=[('image.bin',instrumented,0x40000000,extent),('metadata.bin',bytes(metadata),0x42000000,len(metadata)),('initrd.bin',initramfs,0x69244000,(len(initramfs)+4095)&~4095)]
 ranges_ok([(a,a+n) for _,_,a,n in segments],ram,firmware)
 (out/'target-private.dtb').write_bytes(dt)
 result={**m,'scope':'Combined full ACK image-integrity and actual Linux startup candidate; unexecuted',
         'target_kind':KIND,'target_image_sha256':sha(instrumented),'base_target_image_sha256':IMAGE_SHA,
         'target_dtb_sha256':sha(dt),'kernel_hooks':h,'deadline':e,'metadata_reserved':True,'psci_available':True,'overlapping_memory_declarations_normalized':True,'memory_banks':merged,
         'image_padded_sha256':sha(padded),'combined_stage_token':m['trial_id'],'segments':[]}
 for name,data,address,memory in segments:
  p=out/name;p.write_bytes(data);p.chmod(0o600)
  result['segments'].append(dict(file=name,sha256=sha(data),bytes=len(data),address=address,memory_bytes=memory))
 (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
 for p in [out/'target-private.dtb',out/'report.json']:p.chmod(0o600)
 return result
