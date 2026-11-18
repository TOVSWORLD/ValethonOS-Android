#!/usr/bin/env python3
"""Independently require every live non-System-RAM gap to stay unallocatable."""
import json,struct
from pathlib import Path
from verify_ack_cinit_bundle import verify as cinit_verify
from prepare_ack_ramfix_bundle import KIND,ram_ranges,exclusions
from prepare_ack_combined_bundle import sha
from compare_pmic_dtb import snapshot
from prepare_native_jump_bundle import raw,ranges_ok

def verify(manifest,kernel_package,fdtget=Path('work/dtb-tool/build/fdtget'),nonce=None,*,expected_kind=KIND):
 result=cinit_verify(manifest,kernel_package,fdtget,nonce=nonce,expected_kind=expected_kind)
 m=json.loads(manifest.read_text());root=manifest.parent;source=(root/'source-iomem-private.txt').read_bytes()
 if sha(source)!=m['source_iomem_sha256'] or m.get('live_ram_exclusions_preserved') is not True:raise ValueError('Exact live iomem binding required')
 ram=ram_ranges(source.decode());gaps=exclusions(m['memory_banks'],ram)
 if ram!=[tuple(v) for v in m['live_system_ram']] or gaps!=[tuple(v) for v in m['live_ram_exclusions']]:raise ValueError('Live RAM exclusion computation differs')
 dt=(root/'target-private.dtb').read_bytes()
 if sha(dt)!=m['target_dtb_sha256']:raise ValueError('Verified DT file differs')
 tree=snapshot(fdtget,root/'target-private.dtb');nomap=[]
 for n,p in tree.items():
  if n.startswith('/reserved-memory/') and 'no-map' in p and 'reg' in p:nomap += [(a,a+z) for a,z in struct.iter_unpack('>QQ',raw(p['reg'])) if z]
 if any(not any(a<=x and y<=z for a,z in nomap) for x,y in gaps):raise ValueError('Live non-System-RAM remains allocatable')
 ranges_ok([(s['address'],s['address']+s['memory_bytes']) for s in m['segments']],ram,[])
 return dict(**result,live_ram_exclusions_verified=True)
