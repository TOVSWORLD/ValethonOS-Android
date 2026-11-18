#!/usr/bin/env python3
"""Preserve live source System RAM exclusions for the maintained-kernel allocator."""
import json,re,struct,subprocess
from pathlib import Path
from prepare_ack_cinit_bundle import prepare as cinit_prepare
from prepare_ack_combined_bundle import sha
from compare_pmic_dtb import snapshot
from prepare_native_jump_bundle import raw
KIND='ack-linux-ramfix-v4'

def ram_ranges(iomem):
 rows=[(int(a,16),int(z,16)+1) for a,z in re.findall(r'^([0-9a-f]+)-([0-9a-f]+) : System RAM$',iomem,re.M)]
 if not rows or any(a%4096 or z%4096 or a>=z for a,z in rows):raise ValueError('Page-aligned live System RAM required')
 rows.sort()
 if any(rows[i-1][1]>rows[i][0] for i in range(1,len(rows))):raise ValueError('Overlapping live RAM declarations')
 return rows

def exclusions(banks,ram):
 gaps=[]
 for lo,hi in banks:
  at=lo
  for a,z in ram:
   if z<=at or a>=hi:continue
   if at<a:gaps.append((at,min(a,hi)))
   at=max(at,min(z,hi))
  if at<hi:gaps.append((at,hi))
 return gaps

def prepare(source_dtb,iomem,draft_dtb,image,config,initramfs,init_report,nonce,linked,out,fdtget,fdtput,system_map,trial_id=None):
 m=cinit_prepare(source_dtb,iomem,draft_dtb,image,config,initramfs,init_report,nonce,linked,out,fdtget,fdtput,system_map,trial_id)
 ram=ram_ranges(iomem);gaps=exclusions(m['memory_banks'],ram)
 dt=out/'target-private.dtb';tree=snapshot(fdtget,dt);covered=[]
 for node,props in tree.items():
  if node.startswith('/reserved-memory/') and 'no-map' in props and 'reg' in props:
   covered += [(a,a+n) for a,n in struct.iter_unpack('>QQ',raw(props['reg'])) if n]
 added=[]
 for a,z in gaps:
  if any(x<=a and z<=y for x,y in covered):continue
  if any(a<s['address']+s['memory_bytes'] and s['address']<z for s in m['segments']):raise ValueError('Live exclusion overlaps a load segment')
  node='/reserved-memory/valethon-live-exclusion@'+format(a,'x')
  subprocess.run([str(fdtput),'-c',str(dt),node],check=True)
  subprocess.run([str(fdtput),'-t','x',str(dt),node,'reg',*[format(v,'x') for v in [a>>32,a&0xffffffff,(z-a)>>32,(z-a)&0xffffffff]]],check=True)
  subprocess.run([str(fdtput),str(dt),node,'no-map'],check=True)
  added.append((a,z))
 data=dt.read_bytes()
 if len(data)>0x18000:raise ValueError('Expanded DT overlaps entry')
 meta=bytearray((out/'metadata.bin').read_bytes());meta[:0x18000]=bytes(0x18000);meta[:len(data)]=data
 (out/'metadata.bin').write_bytes(meta)
 p=out/'source-iomem-private.txt';p.write_text(iomem);p.chmod(0o600)
 m.update(scope='Full ACK/PID1 candidate preserving live RAM exclusions; unexecuted',target_kind=KIND,target_dtb_sha256=sha(data),live_system_ram=ram,live_ram_exclusions=gaps,added_nomap_exclusions=added,source_iomem_sha256=sha(iomem.encode()),live_ram_exclusions_preserved=True)
 for s in m['segments']:
  if s['file']=='metadata.bin':s['sha256']=sha(meta)
 (out/'report.json').write_text(json.dumps(m,indent=2)+'\n');return m
