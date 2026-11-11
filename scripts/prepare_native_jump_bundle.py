#!/usr/bin/env python3
"""Offline first-jump bundle: pinned original kernel/ramdisk, current live DT."""
import argparse,hashlib,json,re,secrets,struct,subprocess
from pathlib import Path
from inspect_boot_image import inspect
from pack_native_kexec_boot import split_kernel
from run_kexec_probe import BOOT_SHA
from prepare_kexec_entry import candidate,TEMPLATE
from compare_pmic_dtb import snapshot
PAGE=4096
IMAGE=0x40080000
META=0x42000000
ENTRY=0x42018000

def usb_bootargs(oldargs,token):
 if oldargs.startswith(b'console=ttyGS0 '):oldargs=oldargs[len(b'console=ttyGS0 '):]
 if b'g_serial.' in oldargs or b'console=ttyGS' in oldargs:raise ValueError('Unreviewed source USB console parameters')
 prefix=('console=ttyGS0 g_serial.ft_bind=1 g_serial.ft_trial='+token+' ').encode()
 if len(prefix+oldargs)>=1024:raise ValueError('Conservative kernel bootargs capacity exceeded')
 return prefix,oldargs

def sha(b):return hashlib.sha256(b).hexdigest()
def raw(s):return bytes(int(v,16) for v in s.split())
def cells(s):
 b=raw(s)
 if len(b)%8:raise ValueError('64-bit address/size cells required')
 return [int.from_bytes(b[i:i+8],'big') for i in range(0,len(b),8)]
def overlaps(a,b):return a[0]<b[1] and b[0]<a[1]
def ranges_ok(segments,ram,reserved):
 for i,(a,z) in enumerate(segments):
  if a%PAGE or z%PAGE or z<=a:raise ValueError('Page-aligned nonempty segments required')
  if not any(lo<=a and z<=hi for lo,hi in ram):raise ValueError('Segment outside current System RAM')
  if any(overlaps((a,z),r) for r in reserved):raise ValueError('Segment intersects reserved memory')
  if any(overlaps((a,z),r) for r in segments[:i]):raise ValueError('Segments overlap')
def prepare(boot,dtb,iomem,out,fdtget,fdtput,token=None,target_image=None,usb_linked=None):
 if sha(boot)!=BOOT_SHA:raise ValueError('Pinned original boot required')
 token=token or secrets.token_hex(16)
 if not re.fullmatch('[0-9a-f]{32}',token):raise ValueError('Exact unique hexadecimal trial ID required')
 layout=inspect(boot,len(boot));k,rd,_=layout['components']
 image,_,_=split_kernel(boot[k['offset']:k['offset']+k['bytes']]);initrd=boot[rd['offset']:rd['offset']+rd['bytes']]
 if (target_image is None)!=(usb_linked is None):raise ValueError('USB target Image and linked profile must be supplied together')
 if target_image is not None:
  from verify_usb_console_build import ALLOWED,SERIAL_SHA
  if usb_linked.get('usb_console_linked') is not True or usb_linked.get('serial_bind_is_opt_in') is not True or usb_linked.get('serial_source_sha256')!=SERIAL_SHA:raise ValueError('Verified opt-in USB console profile required')
  if set(usb_linked.get('usb_profile_config_changes',{}))!=ALLOWED or any(v!={'before':'n','after':'y'} for v in usb_linked['usb_profile_config_changes'].values()):raise ValueError('USB console configuration drift')
  if sha(target_image)!=usb_linked['artifacts']['arch/arm64/boot/Image']['sha256']:raise ValueError('USB target Image differs from linked profile')
  image=target_image

 out.mkdir(mode=0o700);base=out/'source-private.dtb';base.write_bytes(dtb)
 before=snapshot(fdtget,base)
 if raw(before['/']['compatible']).find(b'mediatek,mt8163\0')<0:raise ValueError('Wrong board')
 if before['/'].get('#address-cells')!='0 0 0 2' or before['/reserved-memory'].get('#address-cells')!='0 0 0 2' or before['/reserved-memory'].get('#size-cells')!='0 0 0 2':raise ValueError('Unreviewed DT cells')
 chosen=before['/chosen'];key='valethon,kexec-trial'
 if key in chosen:raise ValueError('Prior trial DT cannot be reused')
 start=int.from_bytes(raw(chosen['linux,initrd-start']),'big');end=int.from_bytes(raw(chosen['linux,initrd-end']),'big')
 if start!=0x69244e00 or end-start!=len(initrd):raise ValueError('Original initrd DT extent differs')
 target=out/'target-private.dtb';target.write_bytes(dtb)
 subprocess.run([str(fdtput),'-t','s',str(target),'/chosen',key,token],check=True)
 if target_image is not None:
  oldargs=raw(chosen['bootargs'])
  if not oldargs.endswith(b'\0') or b'\0' in oldargs[:-1]:raise ValueError('Single terminated source bootargs required')
  oldargs=oldargs[:-1]
  prefix,oldargs=usb_bootargs(oldargs,token)
  subprocess.run([str(fdtput),'-t','s',str(target),'/chosen','bootargs',(prefix+oldargs).decode('ascii')],check=True)
 after=snapshot(fdtget,target);expected={n:dict(p) for n,p in before.items()};expected['/chosen'][key]=' '.join(format(v,'x') for v in token.encode()+b'\0')
 if target_image is not None:expected['/chosen']['bootargs']=' '.join(format(v,'x') for v in prefix+oldargs+b'\0')
 if after!=expected:raise ValueError('Unexpected DT property change')
 # Preserve the FDT memory reservation map byte-for-byte, including terminator.
 def reservations(b):
  offset=struct.unpack_from('>I',b,16)[0];entries=[];at=offset
  while at+16<=len(b):
   addr,size=struct.unpack_from('>QQ',b,at);at+=16
   if not size and not addr:return b[offset:at],entries
   if not size or addr+size>=1<<64:raise ValueError('Invalid FDT memory reservation')
   entries.append((addr,addr+size))
  raise ValueError('Unterminated FDT memory reservations')
 memmap,reserved=reservations(dtb)
 if reservations(target.read_bytes())[0]!=memmap:raise ValueError('FDT reservations changed')
 for node,props in before.items():
  if not node.startswith('/reserved-memory/') or 'reg' not in props:continue
  nums=cells(props['reg'])
  if len(nums)%2:raise ValueError('Invalid reserved ranges')
  reserved += [(nums[i],nums[i]+nums[i+1]) for i in range(0,len(nums),2) if nums[i+1]]
 pstore=before['/reserved-memory/pstore-reserved-memory']
 if cells(pstore['reg'])!=[0x44410000,0xe0000]:raise ValueError('Pstore geometry changed')
 ram=[(int(a,16),int(z,16)+1) for a,z in re.findall(r'^([0-9a-f]+)-([0-9a-f]+) : System RAM$',iomem,re.M)]
 trampoline,entry_report=candidate(TEMPLATE,image,target.read_bytes(),IMAGE,META,ENTRY)
 meta=target.read_bytes()
 if len(meta)>ENTRY-META:raise ValueError('DT exceeds metadata capacity')
 meta+=bytes(ENTRY-META-len(meta))+trampoline
 initrd_base=start&-PAGE;initrd_payload=bytes(start-initrd_base)+initrd
 extent=struct.unpack_from('<Q',image,16)[0]
 segments=[('image.bin',image,IMAGE,(extent+PAGE-1)&-PAGE),('metadata.bin',meta,META,(len(meta)+PAGE-1)&-PAGE),('initrd.bin',initrd_payload,initrd_base,(len(initrd_payload)+PAGE-1)&-PAGE)]
 ranges_ok([(a,a+m) for _,_,a,m in segments],ram,reserved)
 report={'scope':'First experimental native kexec jump bundle; not executed','trial_id':token,'original_boot_sha256':BOOT_SHA,'entry':ENTRY,'target_image_sha256':sha(image),'target_dtb_sha256':sha(target.read_bytes()),'source_dtb_sha256':sha(dtb),'target_ramdisk_sha256':sha(initrd),'dt_changes_only':['/chosen/valethon,kexec-trial'],'initrd_addresses_unchanged':[start,end],'pstore_preserved':True,'native_allocator_owns_source_and_relocation_pages':True,'segments':[],'experimental_jump_executed':False,'unqualified':['hardware kexec transition','device/DMA shutdown sufficiency','target entry and normal Android return','failed-jump log retrieval']}
 if target_image is not None:
  report.update(scope='USB kernel-console target bundle; not executed',target_config_sha256=usb_linked['artifacts']['.config']['sha256'],source_config_sha256=usb_linked['artifacts']['.config']['sha256'],dt_changes_only=['/chosen/valethon,kexec-trial','/chosen/bootargs'],bootargs_prefix=['console=ttyGS0','g_serial.ft_bind=1','g_serial.ft_trial='+token],original_bootargs_suffix_preserved=True,target_usb_descriptors={'vendor':'0525','product':'a4a7'})
 for name,b,addr,memsz in segments:
  q=out/name;q.write_bytes(b);q.chmod(0o600);report['segments'].append({'file':name,'sha256':sha(b),'bytes':len(b),'address':addr,'memory_bytes':memsz})
 for f in [base,target]:f.chmod(0o600)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(out/'report.json').chmod(0o600)
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['original-boot','live-dtb','iomem','out','fdtget','fdtput']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--target-image',type=Path);p.add_argument('--usb-linked-report',type=Path);a=p.parse_args();print(json.dumps(prepare(a.original_boot.read_bytes(),a.live_dtb.read_bytes(),a.iomem.read_text(),a.out,a.fdtget,a.fdtput,target_image=a.target_image.read_bytes() if a.target_image else None,usb_linked=json.loads(a.usb_linked_report.read_text()) if a.usb_linked_report else None),indent=2))
