#!/usr/bin/env python3
"""One explicitly approved prepare-only RAM self-test. No reboot or handoff."""
import argparse
import gzip
import hashlib
import json
import os
import secrets
import subprocess
import time
import zlib
from pathlib import Path
from build_kexec_probe import CONFIG_SHA
from run_kexec_probe import BOOT_SHA, RELEASE
from verify_kexec_stage import verify
SCOPE='kexec-prepare-only-1'

def digest(data):return hashlib.sha256(data).hexdigest()
def expected_crc():
 return [f'{zlib.crc32(bytes((j*17+i*71+3)&255 for j in range(n))+bytes(m-n)):08x}'
         for i,(n,m) in enumerate([(5123,8192),(1149,4096),(3999,4096)])]
def validate_client(r):
 if (type(r.get('complete')) is not bool or not r['complete'] or
     r.get('phase')!='complete' or r.get('errno')!=0 or r.get('segments')!=3 or
     r.get('requested_bytes')!=16384 or r.get('staged_bytes')!=16384 or
     not 1<=r.get('owned_pages_prepared',0)<=24592 or r.get('owned_pages_after')!=0 or
     r.get('crc32')!=expected_crc() or r.get('execute_disabled') is not True or
     r.get('handoff_attempted') is not False):
  raise ValueError('Incomplete or mismatched staging/CRC/cleanup report')

def run(selector,module,provider,client,output,authorization=None,objdump='aarch64-linux-gnu-objdump'):
 checked=verify(module,provider,client,objdump)
 if authorization is not None:
  auth=json.loads(authorization.read_text())
  expected={'scope':SCOPE,'module_sha256':checked['module_sha256'],
   'client_sha256':checked['client_sha256'],'target_boot_sha256':BOOT_SHA,
   'owner_approved':True,'owner_available':True,'handoff_allowed':False,'selftest_bytes':16384}
  if any(type(auth.get(k)) is not type(v) or auth.get(k)!=v for k,v in expected.items()):
   raise ValueError('Fresh exact staging-test approval required')
 output.mkdir(mode=0o700)
 result={'scope':SCOPE,'module_sha256':checked['module_sha256'],'client_sha256':checked['client_sha256'],
  'module_load_attempts':0,'client_runs':0,'module_loaded':False,'module_unloaded':False,
  'handoff_attempted':False,'boot_written':False,'rebooted':False,'complete':False}
 paths=[]
 result['ram_paths']=paths
 def private(name,data):
  with (output/name).open('wb') as f:
   os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
 def save():
  private('result.tmp',(json.dumps(result,indent=2)+'\n').encode());os.replace(output/'result.tmp',output/'result.json')
 def adb(command,check=True,timeout=40):
  r=subprocess.run(['adb','-s',selector,'exec-out',command],capture_output=True,timeout=timeout)
  if check and r.returncode:raise RuntimeError('ADB command failed; stop without retry')
  return r
 def absent_module():return 'kxstage ' not in adb('cat /proc/modules').stdout.decode()
 try:
  save()
  state=subprocess.run(['adb','-s',selector,'get-state'],capture_output=True,timeout=10)
  if state.returncode or state.stdout.strip()!=b'device':raise ValueError('Normal Android required')
  if adb('uname -r').stdout.strip().decode()!=RELEASE:raise ValueError('Wrong running kernel')
  if b'uid=0(' not in adb('id').stdout:raise ValueError('Existing root adbd required')
  if digest(gzip.decompress(adb('cat /proc/config.gz').stdout))!=CONFIG_SHA:raise ValueError('Live config differs')
  boot=adb('head -c 16777216 /dev/block/mmcblk0p5').stdout
  if len(boot)!=16777216 or digest(boot)!=BOOT_SHA:raise ValueError('Original boot differs')
  if not absent_module() or adb('test ! -e /dev/kxstage',False).returncode:raise ValueError('Stage module/node already exists')
  before=adb('dmesg').stdout;private('dmesg-before-private.txt',before)
  if b'KXSTAGE' in before:raise ValueError('Prior stage records; no fresh attribution')
  mounts=[l.split() for l in adb('cat /proc/mounts').stdout.decode().splitlines()]
  if not any(len(r)>3 and r[1]=='/dev' and r[2] in ['tmpfs','devtmpfs'] and 'noexec' not in r[3].split(',') for r in mounts):
   raise ValueError('Executable RAM-backed /dev required')
  memory={}
  for line in adb('cat /proc/meminfo').stdout.decode().splitlines():
   fields=line.split()
   if len(fields)>=2:memory[fields[0].rstrip(':')]=int(fields[1])
  if memory.get('MemAvailable',0)<32768:raise ValueError('Insufficient available memory for staging test')
  result['mem_available_kib']=memory['MemAvailable']
  result['preflight']='passed';save()
  if authorization is None:result['complete']=True;return result
  tag=secrets.token_hex(8)
  for local,suffix,mode in [(module,'.ko','600'),(client,'-client','700')]:
   path='/dev/kxstage-'+tag+suffix;paths.append(path);save()
   adb('umask 077; set -C; : > '+path)
   r=subprocess.run(['adb','-s',selector,'push',str(local),path],capture_output=True,timeout=40)
   private('push'+suffix.replace('/','_')+'.log',r.stdout+r.stderr)
   if r.returncode:raise RuntimeError('RAM push failed')
   adb('chmod '+mode+' '+path)
   if digest(adb('cat '+path).stdout)!=digest(local.read_bytes()):raise ValueError('RAM file differs')
  result['module_load_attempts']=1;save()
  inserted=adb('insmod '+paths[0],False);private('insmod-private.log',inserted.stdout+inserted.stderr)
  result['insmod_exit_code']=inserted.returncode
  if inserted.returncode:raise RuntimeError('Kernel rejected module; no force-load or retry')
  result['module_loaded']=True;save()
  end=time.monotonic()+5
  while adb('test -c /dev/kxstage',False).returncode:
   if time.monotonic()>=end:raise RuntimeError('Stage node not created')
   time.sleep(.1)
  result['client_runs']=1;save()
  tested=adb(paths[1]+' --selftest',False,40);private('client-private.log',tested.stdout+tested.stderr)
  report=json.loads(tested.stdout)
  result['client']=report
  if tested.returncode:raise RuntimeError('Staging client failed: '+report.get('phase','unknown'))
  validate_client(report)
  result['complete']=True
  return result
 except BaseException as error:
  result.update(failure_kind=type(error).__name__,failure=str(error));raise
 finally:
  if result['module_load_attempts']:
   try:
    # Resolve an uncertain insertion outcome by observation, never by reloading.
    present=not absent_module();result['module_loaded']=result['module_loaded'] or present
    if present:
     removed=adb('rmmod kxstage',False);private('rmmod-private.log',removed.stdout+removed.stderr)
     result['module_unloaded']=removed.returncode==0 and absent_module()
     if result['module_unloaded']:
      deadline=time.monotonic()+5
      while adb('test ! -e /dev/kxstage',False).returncode and time.monotonic()<deadline:time.sleep(.1)
      result['device_node_removed']=adb('test ! -e /dev/kxstage',False).returncode==0 and adb('test ! -e /sys/class/misc/kxstage',False).returncode==0
      if not result['device_node_removed']:result['complete']=False
    final=adb('dmesg').stdout;private('dmesg-final-private.txt',final)
    if result['module_loaded'] and b'KXSTAGE unloaded owned_pages=0 execute_disabled=1' not in final:
     result['complete']=False;result['unload_accounting_log_missing']=True
   except BaseException as error:
    result['cleanup_failure_kind']=type(error).__name__;result['complete']=False
  for path in paths:
   try:
    adb('rm -f '+path)
   except BaseException as error:result['ram_cleanup_failure_kind']=type(error).__name__
  if paths:
   try:result['ram_cleanup_verified']=all(adb('test ! -e '+p,False).returncode==0 for p in paths)
   except BaseException:result['ram_cleanup_verified']=False
  if result['module_loaded'] and not result['module_unloaded']:result['complete']=False
  if paths and not result.get('ram_cleanup_verified'):result['complete']=False
  save()

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--selector',required=True)
 for key in ['module','provider','client','output']:p.add_argument('--'+key,type=Path,required=True)
 p.add_argument('--authorization',type=Path);p.add_argument('--objdump',default='aarch64-linux-gnu-objdump')
 a=p.parse_args();r=run(a.selector,a.module,a.provider,a.client,a.output,a.authorization,a.objdump)
 print(json.dumps(r,indent=2))
 if not r['complete']:raise SystemExit(1)
