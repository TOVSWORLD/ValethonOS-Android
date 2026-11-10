#!/usr/bin/env python3
"""Default read-only preflight; exact approval permits one temporary boot trial.
One candidate p5 write, one ordinary reboot, one exact original p5 restoration.
Leaves successful native kernel running in RAM with original boot back on flash.
No kexec jump, recovery write, failure injection or automatic reboot retry.
"""
import argparse
import gzip
import hashlib
import json
import os
import re
import secrets
import shlex
import time
from pathlib import Path
from run_pstore_warm_reboot import LabADB
from run_kexec_probe import BOOT_SHA, RELEASE
from build_kexec_probe import CONFIG_SHA as ORIGINAL_CONFIG
from verify_native_kexec_build import CONFIG_SHA as NATIVE_CONFIG

SCOPE='native-kexec-source-boot-1'
RECOVERY_SHA='3c9bafcbfc4a0b12cb1a3f372af0cfd49ffec5b3e01a0b070465b49bd8435f11'
BYTES=16777216


def sha(data):return hashlib.sha256(data).hexdigest()


def partition(device,n,size):
    data=device.shell('head -c '+str(size+1)+' /dev/block/mmcblk0p'+str(n))
    if len(data)!=size:raise ValueError('Exact partition size required')
    return sha(data)


def facts(device):
    if b'uid=0(' not in device.shell('id'):raise ValueError('Root adbd required')
    if device.shell('getprop ro.product.device').strip()!=b'douglas':raise ValueError('Wrong device identity')
    if device.shell('uname -r').strip().decode()!=RELEASE:raise ValueError('Unexpected kernel release')
    base='/dev/block/by-name/'
    for alias,node in [('boot',17),('boot_x',5),('recovery',18),('recovery_x',6)]:
        if device.shell('readlink '+base+alias).strip()!=('/dev/block/mmcblk0p'+str(node)).encode():
            raise ValueError('Partition alias differs')
    if partition(device,6,17825792)!=RECOVERY_SHA:raise ValueError('Recovery differs; never write recovery')
    boot=partition(device,5,BYTES)
    config=sha(gzip.decompress(device.shell('cat /proc/config.gz')))
    ident=device.shell('cat /proc/sys/kernel/random/boot_id').strip().decode()
    if not re.fullmatch(r'[0-9a-f-]{36}',ident):raise ValueError('Invalid boot identity')
    return {'boot':boot,'config':config,'boot_id':ident}


def ram_guard(device):
    mounts=device.shell('cat /proc/mounts').decode().splitlines()
    if not any(len(v:=l.split())>3 and v[1]=='/dev' and v[2] in ['tmpfs','devtmpfs'] and 'rw' in v[3].split(',') for l in mounts):
        raise ValueError('Writable RAM-backed /dev required')
    mem=device.shell('cat /proc/meminfo').decode()
    m=re.search(r'^MemAvailable:\s+(\d+) kB$',mem,re.M)
    if not m or int(m[1])<65536:raise ValueError('At least64MiB MemAvailable required for RAM staging')


def stage(device,lab_file,expected):
    if device.host(['sha256sum',lab_file]).stdout.split()[0].decode()!=expected:
        raise ValueError('Prepared lab asset differs')
    ram_guard(device)
    folder='/dev/kx-native-'+secrets.token_hex(12)
    device.shell('mkdir -m 700 '+folder)
    path=folder+'/boot.img'
    try:
        device.adb('push',lab_file,path);device.shell('chmod 600 '+path)
        if device.shell('sha256sum '+path).split()[0].decode()!=expected:
            raise ValueError('Device RAM asset differs')
        return folder,path
    except BaseException:
        device.shell('rm -f '+path+'; rmdir '+folder);raise


def run(device,lab_package,report,output,authorization=None):
    candidate=report['candidate_sha256'];runner=sha(Path(__file__).read_bytes())
    if not re.fullmatch('[0-9a-f]{64}',candidate) or candidate==BOOT_SHA:raise ValueError('Distinct exact candidate required')
    if report['original_boot_sha256']!=BOOT_SHA or report['resolved_config_sha256']!=NATIVE_CONFIG:
        raise ValueError('Wrong source kernel/rollback package')
    if authorization is not None:
        a=json.loads(authorization.read_text())
        expected={'scope':SCOPE,'runner_sha256':runner,'candidate_sha256':candidate,'original_boot_sha256':BOOT_SHA,
          'owner_approved':True,'owner_available':True,'maximum_candidate_writes':1,'maximum_restore_writes':1,
          'maximum_reboots':1,'recovery_writes_allowed':False,'experimental_jump_allowed':False}
        if any(type(a.get(k)) is not type(v) or a.get(k)!=v for k,v in expected.items()):raise ValueError('Exact current source-boot approval required')
    output.mkdir(mode=0o700)
    if authorization is not None:
        fd=os.open(str(authorization)+'.consumed',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
    result={'scope':SCOPE,'runner_sha256':runner,'candidate_sha256':candidate,'original_boot_sha256':BOOT_SHA,
      'candidate_write_attempts':0,'restore_write_attempts':0,'reboot_requests':0,'complete':False,
      'original_boot_restored':False,'normal_shell_restored':False,'native_kernel_running':False,
      'recovery_written':False,'experimental_jump_executed':False,'owner_attention_required':False}
    folders=[];before=None
    def save():
        with (output/'result.json').open('w') as f:
            os.fchmod(f.fileno(),0o600);json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    def root():device.adb('root');device.adb('wait-for-device')
    def write(path,kind):
        result[kind+'_write_attempts']+=1;save()
        device.shell('dd if='+path+' of=/dev/block/mmcblk0p5 bs=4096 count=4096 conv=fsync')
        device.shell('sync')
    def restore():
        current=facts(device)
        if current['boot']==BOOT_SHA:result['original_boot_restored']=True;return
        if not result['candidate_write_attempts']:raise ValueError('Cannot restore an unowned modification')
        if result['restore_write_attempts']:raise RuntimeError('No automatic restore retry')
        folder,path=stage(device,lab_package+'/original-boot.img',BOOT_SHA);folders.append(folder)
        # Recheck identity/recovery after upload; rollback remains exact original.
        facts(device);write(path,'restore')
        if partition(device,5,BYTES)!=BOOT_SHA or partition(device,6,17825792)!=RECOVERY_SHA:
            raise RuntimeError('Original readback not verified')
        result['original_boot_restored']=True
    try:
        save();root();before=facts(device)
        if before['boot']!=BOOT_SHA or before['config']!=ORIGINAL_CONFIG:raise ValueError('Original installed kernel/boot required')
        for n,h in [('boot-full.img',candidate),('original-boot.img',BOOT_SHA)]:
            if device.host(['sha256sum',lab_package+'/'+n]).stdout.split()[0].decode()!=h:raise ValueError('Lab package differs')
        ram_guard(device)
        result['recovery_sha256']=RECOVERY_SHA
        result['preflight']='passed';result['source_boot_id_sha256']=sha(before['boot_id'].encode());save()
        if authorization is None:result['complete']=True;return result
        folder,path=stage(device,lab_package+'/boot-full.img',candidate);folders.append(folder)
        check=facts(device)
        if check!=before:raise ValueError('Source identity changed before install')
        write(path,'candidate')
        if partition(device,5,BYTES)!=candidate or partition(device,6,17825792)!=RECOVERY_SHA:
            raise RuntimeError('Candidate/recovery readback differs; do not reboot')
        result['candidate_install_verified']=True;result['reboot_requests']=1;save()
        try:device.adb('reboot',timeout=15)
        except RuntimeError:result['reboot_transport_uncertain']=True
        deadline=time.monotonic()+300;returned=False
        while time.monotonic()<deadline:
            try:
                ident=device.shell('cat /proc/sys/kernel/random/boot_id',timeout=10).strip().decode()
                if ident!=before['boot_id'] and re.fullmatch(r'[0-9a-f-]{36}',ident) and device.shell('getprop sys.boot_completed',timeout=10).strip()==b'1':
                    returned=True;break
            except RuntimeError:pass
            time.sleep(1)
        if not returned:raise RuntimeError('Native Android return not observed; stop, no reboot retry')
        root();after=facts(device)
        if after['boot']!=candidate or after['config']!=NATIVE_CONFIG:raise ValueError('Unexpected returned kernel/image')
        if device.shell('cat /sys/kernel/kexec_loaded').strip()!=b'0':raise ValueError('Unexpected preloaded kexec image')
        result['native_kernel_running']=True;result['target_boot_id_sha256']=sha(after['boot_id'].encode())
        result['native_config_sha256']=after['config']
        # Current-boot diagnostics only, filtered to this candidate's CPU gate.
        diagnostics=device.shell("dmesg | grep -E 'KXOFF|KXHANDOFF'; true").decode().splitlines()
        if any('KXOFF' not in l and 'KXHANDOFF' not in l for l in diagnostics):raise ValueError('Unexpected diagnostics')
        result['gate_diagnostics']=diagnostics
        restore();result['complete']=True;return result
    except BaseException as error:
        result['failure_kind']=type(error).__name__;raise
    finally:
        if result['candidate_write_attempts'] and not result['original_boot_restored']:
            try:root();restore()
            except BaseException:result['owner_attention_required']=True
        for folder in folders:
            try:device.shell('rm -f '+folder+'/boot.img; if [ -d '+folder+' ]; then rmdir '+folder+'; fi')
            except BaseException:result['ram_cleanup_unconfirmed']=True
        try:
            device.adb('unroot',timeout=20);device.adb('wait-for-device',timeout=30)
            result['normal_shell_restored']=b'uid=2000(' in device.shell('id',timeout=10)
        except BaseException:result['normal_shell_restored']=False
        if not result['normal_shell_restored'] or result.get('ram_cleanup_unconfirmed'):
            result['complete']=False;result['owner_attention_required']=True
        save()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['ssh-args','package-report','output']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--lab-package',required=True);p.add_argument('--authorization',type=Path);a=p.parse_args()
    try:
        r=run(LabADB(json.loads(a.ssh_args.read_text())),a.lab_package,json.loads(a.package_report.read_text()),a.output,a.authorization)
        print(json.dumps(r,indent=2));raise SystemExit(0 if r['complete'] else 1)
    except Exception as error:print(json.dumps({'error_kind':type(error).__name__,'message':str(error)}));raise SystemExit(1)
