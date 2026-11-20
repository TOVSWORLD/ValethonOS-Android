#!/usr/bin/env python3
"""Boot the actual Android first/second stage and system read-only in a networkless VM."""
import argparse,gzip,hashlib,json,os,re,selectors,struct,subprocess,time
from pathlib import Path
from prepare_android_direct_boot import ramdisk

def sha_file(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def vm_ramdisk(data):
 raw,report=ramdisk(data);at=0;out=bytearray();changes=0
 while True:
  header=bytearray(raw[at:at+110]);fields=[int(header[6+i*8:14+i*8],16) for i in range(13)]
  name=raw[at+110:at+110+fields[11]];begin=(at+110+fields[11]+3)&~3;payload=raw[begin:begin+fields[6]];at=(begin+fields[6]+3)&~3
  if name==b'fstab.douglas\0':
   old=b'/dev/block/mmcblk0p14'
   if payload.count(old)!=1:raise ValueError('Exact tablet system-only fstab required')
   payload=payload.replace(old,b'/dev/block/vda');header[54:62]=f'{len(payload):08x}'.encode();changes+=1
  out+=header+name;out+=bytes(-len(out)%4);out+=payload;out+=bytes(-len(out)%4)
  if name==b'TRAILER!!!\0':break
 if changes!=1:raise ValueError('Exactly one VM storage-path replacement required')
 out+=bytes(-len(out)%512)
 return gzip.compress(out,mtime=0),{'changed_entry':'fstab.douglas','change':'mmcblk0p14 -> vda','original_android_init_sha256':report['entries']['init']['sha256'],'original_android_init_unchanged':True}

def assess(data):
 first=b'init first stage started!' in data;second=b'init second stage started!' in data
 apex=bool(re.search(rb"Service 'apexd-bootstrap'.*exited with status 0",data))
 failed=any(s in data for s in [b'Kernel panic',b'bootstrap-apexd-failed',b'Failed to setup cpuset cgroup'])
 return {'first_stage_started':first,'second_stage_started':second,'system_mounted':b'target=/system,type=ext4)=0: Success' in data,'selinux_policy_load_reached':b'Loading SELinux policy' in data,'legacy_cpuset_setup_failed':b'Failed to setup cpuset cgroup' in data,'apex_bootstrap_exited_zero':apex,'bootstrap_failure_reboot':b'bootstrap-apexd-failed' in data,'kernel_panic':b'Kernel panic' in data,'critical_service_abort':b'critical process' in data,'init_fatal_reboot':b'InitFatalReboot' in data,'post_fs_data_reached':b'processing action (post-fs-data)' in data,'passed':first and second and apex and not failed}

def run(kernel,kernel_sha,android_ramdisk,ramdisk_sha,system,system_sha,output,virtualization='on'):
 for path,digest in [(kernel,kernel_sha),(android_ramdisk,ramdisk_sha),(system,system_sha)]:
  if not re.fullmatch('[a-f0-9]{64}',digest) or sha_file(path)!=digest:raise ValueError('Exact built input digest required')
 if virtualization not in ['on','off']:raise ValueError('Explicit bounded VM mode required')
 if system.stat().st_size!=1692925952:raise ValueError('Exact expanded system geometry required')
 output.mkdir(mode=0o700);rd,delta=vm_ramdisk(android_ramdisk.read_bytes());initrd=output/'VM-ONLY-ramdisk.cpio.gz';initrd.write_bytes(rd)
 args=['qemu-system-aarch64','-machine','virt,gic-version=2,virtualization='+virtualization,'-cpu','cortex-a53','-smp','1','-m','1536','-accel','tcg','-nodefaults','-display','none','-serial','stdio','-monitor','none','-nic','none','-no-reboot','-kernel',str(kernel),'-initrd',str(initrd),'-drive','file='+str(system)+',format=raw,if=none,id=system,readonly=on','-device','virtio-blk-device,drive=system','-append','console=ttyAMA0,115200 rdinit=/init nr_cpus=1 maxcpus=0 androidboot.hardware=douglas androidboot.selinux=enforcing androidboot.console=ttyAMA0 loglevel=8 ignore_loglevel printk.devkmsg=on panic=-1']
 p=subprocess.Popen(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);data=bytearray();began=time.monotonic()
 try:
  with selectors.DefaultSelector() as s:
   s.register(p.stdout,selectors.EVENT_READ)
   while time.monotonic()-began<120 and len(data)<8*1024*1024:
    for key,_ in s.select(.1):data.extend(os.read(key.fd,65536))
    if b'Kernel panic' in data or p.poll() is not None:break
 finally:
  if p.poll() is None:p.terminate()
  try:p.wait(timeout=5)
  except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)
 (output/'boot-private.log').write_bytes(data)
 result={'scope':'Actual compiled Android init/system VM bootstrap; not tablet Linux/Android qualification',**assess(data),'kernel_sha256':kernel_sha,'android_ramdisk_sha256':ramdisk_sha,'system_sha256':system_sha,'vm_ramdisk_sha256':hashlib.sha256(rd).hexdigest(),'vm_only_modification':delta,'system_read_only':True,'selinux_enforcing_requested':True,'network_attached':False,'virtualization':virtualization,'elapsed_seconds':round(time.monotonic()-began,3),'log_sha256':hashlib.sha256(data).hexdigest()}
 (output/'result.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['kernel','android-ramdisk','system','output']:p.add_argument('--'+n,type=Path,required=True)
 for n in ['kernel-sha','ramdisk-sha','system-sha']:p.add_argument('--'+n,required=True)
 p.add_argument('--virtualization',choices=['on','off'],default='on');a=p.parse_args();r=run(a.kernel,a.kernel_sha,a.android_ramdisk,a.ramdisk_sha,a.system,a.system_sha,a.output,a.virtualization);print(json.dumps(r));raise SystemExit(0 if r['passed'] else 1)
