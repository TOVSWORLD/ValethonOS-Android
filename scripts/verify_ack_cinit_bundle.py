#!/usr/bin/env python3
"""Reproduce C-init console and verify fixed-map RAM-only candidate before device I/O."""
import hashlib,json,struct,tempfile,re
from pathlib import Path
from build_ack_cinit_console import build as console, prefix
from build_ack_combined_entry import build as entry,integrity_marker
from prepare_ack_native_bundle import IMAGE_SHA,CONFIG_SHA,reservation_map,reserved_nodes
from compare_pmic_dtb import snapshot
from prepare_native_jump_bundle import raw,ranges_ok

KIND='ack-linux-cinit-v3'

def sha(b):return hashlib.sha256(b).hexdigest()

def assess(data,nonce):
 identity=prefix(nonce.hex())
 fresh=identity in data
 return dict(fresh_console_identity=fresh,console_ready_seen=fresh and b'retained_early_console_ready' in data,
             run_init_seen=fresh and b'Run /init as init process' in data,
             linux_banner_seen=fresh and b'Linux version 6.18.34-valethon-draft1+' in data,
             panic_seen=fresh and b'Kernel panic' in data,
             exception_seen=fresh and any(v in data for v in [b'Internal error:',b'Unable to handle kernel',b'SError Interrupt']),
             marker_absence_inconclusive=True)

def verify(manifest,kernel_package,fdtget=Path('work/dtb-tool/build/fdtget'),nonce=None,*,expected_kind=KIND):
 m=json.loads(manifest.read_text());root=manifest.parent
 if nonce is None or len(nonce)!=32 or sha(nonce)!=m['target_nonce_sha256']:raise ValueError('Exact fresh PID1 identity required')
 if m.get('legacy_entry_hooks_removed') is not True or m.get('ramoops_target_mapping_disabled') is not True:raise ValueError('C-init mapping isolation required')
 if m.get('target_kind')!=expected_kind or m.get('base_target_image_sha256')!=IMAGE_SHA or m.get('target_config_sha256')!=CONFIG_SHA:
  raise ValueError('Exact combined manifest/base/config required')
 if not all(m.get(k) is True for k in ['metadata_reserved','psci_available','overlapping_memory_declarations_normalized']):
  raise ValueError('Combined boot contract flags missing')
 base=(kernel_package/'Image').read_bytes();sm=(kernel_package/'System.map').read_text()
 data={s['file']:(root/s['file']).read_bytes() for s in m['segments']}
 for s in m['segments']:
  if sha(data[s['file']])!=s['sha256'] or len(data[s['file']])!=s['bytes']:raise ValueError('Segment bytes differ')
 with tempfile.TemporaryDirectory(prefix='ft-combined-verify-') as tmp:
  p=Path(tmp);im,h=console(base,sm,p/'console',nonce.hex())
  if im!=data['image.bin'] or h!=m['cinit_console'] or sha(im)!=m['target_image_sha256']:
   raise ValueError('Actual instrumented kernel differs from exact reproducible patch')
  padded=im+bytes(m['image_memory_bytes']-len(im));code,e=entry(p/'entry',m['trial_id'],padded)
  if e!=m['deadline'] or sha(padded)!=m['image_padded_sha256']:raise ValueError('Integrity entry/report differs')
  meta=data['metadata.bin']
  if len(meta)!=0x28000 or meta[:4]!=bytes.fromhex('d00dfeed'):raise ValueError('Exact metadata extent/FDT required')
  size=struct.unpack_from('>I',meta,4)[0]
  if not 40<size<=0x18000:raise ValueError('Bounded FDT required')
  dt=meta[:size]
  expected=bytearray(0x28000);expected[:size]=dt;expected[0x18000:0x18000+len(code)]=code
  if bytes(expected)!=meta or sha(dt)!=m['target_dtb_sha256']:raise ValueError('Metadata contains unexpected code/data')
  file=p/'target.dtb';file.write_bytes(dt);tree=snapshot(fdtget,file)
  args=raw(tree['/chosen']['bootargs']).rstrip(b'\0').decode().split()
  quiet=m.get('end_to_end_only') is True
  verbosity=(m.get('verbose_initcall_tracing') is False and 'loglevel=7' in args and 'initcall_debug' not in args and 'ignore_loglevel' not in args) if quiet else ('initcall_debug' in args and 'loglevel=8' in args and 'ignore_loglevel' in args)
  if args.count('earlycon=uart8250,mmio32,0x444bf000')!=1 or 'keep_bootcon' not in args or not verbosity or any(a.startswith('ramoops.') for a in args):raise ValueError('Exact permanent console/no conflicting mapping and declared verbosity required')
  if 'valethon,trial-nonce' in tree['/chosen']:raise ValueError('Disk logger unexpectedly opted in')
  for name in ['10007000']:
   if raw(tree['/soc/watchdog@'+name]['status'])!=b'disabled\0':raise ValueError('Target watchdog driver must stay disabled')
  for name in ['11230000','11240000','11250000']:
   if raw(tree['/soc/mmc@'+name]['status'])!=b'disabled\0':raise ValueError('RAM-only target required')
  if raw(tree['/psci']['status'])!=b'okay\0' or raw(tree['/psci']['compatible'])!=b'arm,psci\0' or raw(tree['/psci']['method'])!=b'smc\0':
   raise ValueError('Explicit available legacy PSCI contract required')
  for name,value in [('cpu_suspend',0x84000001),('cpu_off',0x84000002),('cpu_on',0x84000003),('affinity_info',0x84000004)]:
   if raw(tree['/psci'][name])!=struct.pack('>I',value):raise ValueError('Firmware function ID differs')
  memory=[raw(v['reg']) for n,v in tree.items() if n.startswith('/memory') and v.get('device_type')=='6d 65 6d 6f 72 79 0']
  if len(memory)!=1 or len(memory[0])%16:raise ValueError('One normalized memory node required')
  banks=[(a,a+n) for a,n in struct.iter_unpack('>QQ',memory[0])]
  if banks!=[tuple(v) for v in m['memory_banks']] or any(a>=z for a,z in banks) or any(banks[i-1][1]>banks[i][0] for i in range(1,len(banks))):raise ValueError('Overlapping/invalid memory banks')
  # Recheck source RAM and firmware independently, rather than trust flags.
  source=root/'prior-private/base-private/source-private.dtb'
  if sha(source.read_bytes())!=m['source_dtb_sha256']:raise ValueError('Bound source DT differs')
  live=snapshot(fdtget,source)
  source_banks=sorted((a,a+n) for node,props in live.items() if node.startswith('/memory') and raw(props.get('device_type',''))==b'memory\0' for a,n in struct.iter_unpack('>QQ',raw(props['reg'])) if n)
  normalized=[]
  for a,z in source_banks:
   if normalized and a<normalized[-1][1]:normalized[-1]=(normalized[-1][0],max(z,normalized[-1][1]))
   else:normalized.append((a,z))
  if normalized!=banks:raise ValueError('Target changes working-source RAM union')
  source_reserved=reservation_map(source.read_bytes())[2]+reserved_nodes(live)
  target_reserved=reserved_nodes(tree)
  if any(not any(a<=x and y<=z for a,z in reservation_map(dt)[2]+target_reserved) for x,y in source_reserved):
   raise ValueError('Source firmware reservation lost')
  # Real source /proc/iomem was checked by the builder; source DT is independently
  # bounded here and none of the three segments may overlap firmware reserves.
  ranges_ok([(seg['address'],seg['address']+seg['memory_bytes']) for seg in m['segments']],banks,source_reserved+target_reserved)
  reserves=reservation_map(dt)[2]
  if not any(a<=0x42000000 and 0x42028000<=z for a,z in reserves):raise ValueError('Metadata/table/stack reservation absent')
 return dict(cinit_bundle_verified=True,instrumented_image_sha256=sha(data['image.bin']),metadata_sha256=sha(data['metadata.bin']),actual_kernel_patch_sites=1)
