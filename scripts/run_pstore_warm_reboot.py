#!/usr/bin/env python3
"""Preflight by default; one separately approved console marker and orderly reboot.
Runs locally through the existing lab SSH/ADB connection. Never loads a module,
flashes an image, unlinks pstore records, changes policy, or injects a failure.
"""
import argparse
import gzip
import hashlib
import json
import os
import re
import secrets
import shlex
import subprocess
import time
from pathlib import Path
from build_kexec_probe import CONFIG_SHA
from run_kexec_probe import BOOT_SHA, RELEASE

SCOPE='pstore-warm-reboot-marker-1'
PREFIX='FIRETABS_RETENTION_V1'
REG=bytes.fromhex('000000004441000000000000000e0000')
RUNNER=Path(__file__)


def sha(data):return hashlib.sha256(data).hexdigest()


def framed_result(data, tag):
    before,separator,tail=data.rpartition(b'\n'+tag+b'=')
    if not separator or tail!=b'0\n':raise RuntimeError('Remote shell did not confirm successful completion')
    return before


class LabADB:
    def __init__(self, args):
        if not isinstance(args,list) or not args or any(not isinstance(a,str) for a in args):
            raise ValueError('Existing private SSH argument array required')
        self.args=args
        r=self.host(['adb','devices'])
        devices=[l.split()[0] for l in r.stdout.decode().splitlines()[1:]
                 if len(l.split())==2 and l.split()[1]=='device']
        if len(devices)!=1 or not re.fullmatch(r'[A-Za-z0-9._:-]+',devices[0]):
            raise ValueError('Exactly one existing normal ADB device required')
        self.selector=devices[0]

    def host(self, args, timeout=30, check=True):
        try:r=subprocess.run(self.args+[shlex.join(args)],capture_output=True,timeout=timeout)
        except subprocess.TimeoutExpired:raise RuntimeError('Lab command timed out; no automatic write/reboot retry') from None
        if check and r.returncode:raise RuntimeError('Lab/ADB command failed')
        return r

    def adb(self, *args, timeout=30, check=True):
        return self.host(['adb','-s',self.selector,*args],timeout,check)

    def shell(self, command, timeout=30):
        tag=('KXPS_STATUS_'+secrets.token_hex(12)).encode()
        wrapped='( '+command+' ); kxps_status=$?; printf '+shlex.quote('\n'+tag.decode()+'=%d\n')+' "$kxps_status"'
        r=self.adb('exec-out',wrapped,timeout=timeout)
        return framed_result(r.stdout,tag)


def verify_source(device):
    if device.shell('uname -r').strip().decode()!=RELEASE:raise ValueError('Wrong working kernel')
    if b'uid=0(' not in device.shell('id'):raise ValueError('Temporary root adbd required')
    config=gzip.decompress(device.shell('cat /proc/config.gz'))
    if sha(config)!=CONFIG_SHA:raise ValueError('Live configuration differs')
    boot=device.shell('head -c 16777216 /dev/block/mmcblk0p5')
    if len(boot)!=16777216 or sha(boot)!=BOOT_SHA:raise ValueError('Original full boot differs')
    base='/proc/device-tree/reserved-memory/'
    for n in ['#address-cells','#size-cells']:
        if device.shell('cat '+base+n)!=bytes.fromhex('00000002'):raise ValueError('DT cell width differs')
    if device.shell('cat '+base+'pstore-reserved-memory/reg')!=REG:raise ValueError('Existing pstore reservation differs')
    if device.shell('cat '+base+'pstore-reserved-memory/compatible')!=b'mediatek,pstore\0':
        raise ValueError('Existing pstore reservation identity differs')
    consoles=device.shell('cat /proc/consoles').decode()
    if not re.search(r'^pstore(?:-\d+)?\s+\S+\s+\(E[^)]*\)',consoles,re.M):
        raise ValueError('Enabled pstore console required')
    levels=device.shell('cat /proc/sys/kernel/printk').split()
    if not levels or int(levels[0])<=3:raise ValueError('Marker level would be filtered; loglevel changes not allowed')
    params={}
    for n in ['mem_address','mem_size','console_size']:
        params[n]=int(device.shell('cat /sys/module/ramoops/parameters/'+n).strip(),0)
    if params!={'mem_address':0x44410000,'mem_size':0xe0000,'console_size':0x10000}:
        raise ValueError('Active ramoops geometry differs')
    mounts=device.shell('cat /proc/mounts').decode().splitlines()
    if not any(len(l.split())>=3 and l.split()[1:3]==['/sys/fs/pstore','pstore'] for l in mounts):
        raise ValueError('Mounted pstore required')
    bootid=device.shell('cat /proc/sys/kernel/random/boot_id').strip().decode()
    if not re.fullmatch(r'[a-f0-9-]{36}',bootid):raise ValueError('Invalid kernel boot identity')
    return bootid


def run(device, output, authorization=None):
    runner_sha=sha(RUNNER.read_bytes())
    if authorization is not None:
        auth=json.loads(authorization.read_text())
        expected={'scope':SCOPE,'runner_sha256':runner_sha,'target_boot_sha256':BOOT_SHA,
          'owner_approved':True,'owner_available':True,'maximum_marker_writes':1,
          'maximum_reboots':1,'boot_writes_allowed':False,'module_loading_allowed':False,
          'handoff_allowed':False}
        if any(type(auth.get(k)) is not type(v) or auth.get(k)!=v for k,v in expected.items()):
            raise ValueError('Fresh exact retention-test approval and owner availability required')
        if not re.fullmatch(r'[a-f0-9]{32}',str(auth.get('approval_id',''))):
            raise ValueError('Unique approval identity required')
    output.mkdir(mode=0o700)
    if authorization is not None:
        consumed=authorization.with_name(authorization.name+'.consumed')
        with os.fdopen(os.open(consumed,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:
            json.dump({'scope':SCOPE,'approval_id':auth['approval_id'],'runner_sha256':runner_sha},f)
    result={'scope':SCOPE,'runner_sha256':runner_sha,'complete':False,
      'marker_write_attempts':0,'reboot_requests':0,'boot_written':False,
      'module_loaded':False,'handoff_attempted':False,'pstore_records_deleted':False,
      'personal_log_contents_collected':False,'normal_shell_restored':False,
      'orderly_warm_reboot_retention_qualified':False,'failed_handoff_retention_qualified':False}
    def save():
        with (output/'result.json').open('w') as f:
            os.fchmod(f.fileno(),0o600);json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    def root():
        device.adb('root');device.adb('wait-for-device')
        if b'uid=0(' not in device.shell('id'):raise RuntimeError('Root adbd unavailable')
    try:
        save();root();before=verify_source(device)
        entries=device.shell('ls -1 /sys/fs/pstore').strip()
        if entries:raise ValueError('Pstore must start empty; no deletion or old-log collection allowed')
        result.update(preflight='passed',source_boot_id_sha256=sha(before.encode()),
          source_boot_sha256=BOOT_SHA,source_config_sha256=CONFIG_SHA,
          existing_backend={'address':0x44410000,'size':0xe0000,'console_size':0x10000})
        if authorization is None:result['complete']=True;return result
        nonce=secrets.token_hex(24)
        marker=PREFIX+' nonce='+nonce+' source_boot='+sha(before.encode())+' scope=orderly-warm-reboot'
        result['marker']=marker;result['marker_write_attempts']=1;save()
        device.shell('printf '+shlex.quote('<3>'+marker+'\n')+' > /dev/kmsg')
        line=device.shell('dmesg | grep -F '+shlex.quote(marker)).decode(errors='replace').splitlines()
        if len(line)!=1 or marker not in line[0]:raise ValueError('One attributable source marker required')
        result['source_marker_observed']=True;result['source_marker_line']=line[0]
        result['reboot_requests']=1;save()
        try:device.adb('reboot',timeout=15)
        except RuntimeError:result['reboot_transport_uncertain']=True
        deadline=time.monotonic()+240;after=None
        while time.monotonic()<deadline:
            try:
                candidate=device.shell('cat /proc/sys/kernel/random/boot_id',timeout=10).strip().decode()
                completed=device.shell('getprop sys.boot_completed',timeout=10).strip()==b'1'
                if re.fullmatch(r'[a-f0-9-]{36}',candidate) and candidate!=before and completed:
                    after=candidate;break
            except (RuntimeError,ValueError,UnicodeError):pass
            time.sleep(1)
        if after is None:raise RuntimeError('Normal Android return not observed within test window; no reboot retry')
        root();verified=verify_source(device)
        if verified!=after:raise ValueError('Boot identity changed during retrieval')
        result['target_boot_id_sha256']=sha(after.encode());result['normal_android_return_observed']=True
        # Only nonce-matching console lines leave the device. PMSG/dmesg contents,
        # account files and prior retained records are never collected or removed.
        command='for f in /sys/fs/pstore/console-ramoops*; do [ -f "$f" ] || continue; head -c 131072 "$f" | grep -F '+shlex.quote(marker)+'; done; true'
        found=device.shell(command).decode(errors='replace').splitlines()
        if any(marker not in l for l in found):raise ValueError('Unexpected retained output refused')
        result['retained_marker_matches']=len(found)
        result['retained_marker_lines']=found
        result['orderly_warm_reboot_retention_qualified']=len(found)==1
        result['outcome']='marker-retained' if len(found)==1 else 'inconclusive-marker-absent-or-nonunique'
        result['complete']=True
        return result
    except BaseException as error:
        result['failure_kind']=type(error).__name__;raise
    finally:
        try:
            device.adb('unroot',timeout=20);device.adb('wait-for-device',timeout=30)
            result['normal_shell_restored']=b'uid=2000(' in device.shell('id',timeout=10)
        except BaseException:result['normal_shell_restored']=False
        if not result['normal_shell_restored']:result['complete']=False
        save()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ssh-args',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--authorization',type=Path);a=p.parse_args()
    try:
        r=run(LabADB(json.loads(a.ssh_args.read_text())),a.output,a.authorization)
        print(json.dumps(r,indent=2));raise SystemExit(0 if r['complete'] else 1)
    except Exception as error:
        print(json.dumps({'error_kind':type(error).__name__,'message':str(error)}));raise SystemExit(1)
