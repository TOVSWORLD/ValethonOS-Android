#!/usr/bin/env python3
"""One exactly approved four-query affinity test. No CPU state changes/handoff."""
import argparse
import gzip
import hashlib
import json
import os
import re
import secrets
import subprocess
from pathlib import Path
from build_kexec_probe import CONFIG_SHA
from run_kexec_probe import BOOT_SHA, RELEASE
from verify_kexec_affinity import verify

SCOPE='kexec-affinity-query-1'


def parse_report(lines):
    heads=[re.search(r'KXAFF v1 fid=84000004 conduit=smc queries=4 current_cpu=(\d+) online_mask=([0-9a-f]+)$',l) for l in lines]
    heads=[h for h in heads if h]
    if len(lines)!=6 or len(heads)!=1:raise ValueError('One fresh complete query report required')
    current,online=int(heads[0][1]),int(heads[0][2],16)
    if current not in range(4) or not 1<=online<=15 or not online&(1<<current):
        raise ValueError('Invalid CPU report')
    states={}
    for line in lines:
        m=re.search(r'KXAFF cpu=(\d+) target=([0-9a-f]+) result=(-?\d+)$',line)
        if m:
            cpu,target,value=int(m[1]),int(m[2],16),int(m[3])
            if cpu not in range(4) or target!=cpu or cpu in states:
                raise ValueError('Invalid/duplicate CPU query')
            states[cpu]=value
    if set(states)!=set(range(4)):raise ValueError('Missing query result')
    end=[re.search(r'KXAFF complete supported=(\d+) current_on=([01]) state_changes=0 handoff=0$',l) for l in lines]
    end=[e for e in end if e]
    supported=sum(0<=n<=2 for n in states.values())
    current_on=states[current]==0
    if len(end)!=1 or int(end[0][1])!=supported or bool(int(end[0][2]))!=current_on:
        raise ValueError('Summary differs from actual query records')
    return {'current_cpu':current,'online_mask':online,
            'results':{str(k):v for k,v in states.items()},
            'firmware_affinity_qualified':supported==4 and current_on,
            'query_scope':'Affinity query responses only; no CPU shutdown acceptance'}


def run(selector,module,provider,output,authorization=None,objdump='aarch64-linux-gnu-objdump'):
    checked=verify(module,provider,objdump)
    if not re.fullmatch(r'[A-Za-z0-9._:-]+',selector):raise ValueError('Explicit device selector required')
    if authorization is not None:
        auth=json.loads(authorization.read_text())
        expected={'scope':SCOPE,'module_sha256':checked['module_sha256'],
          'target_boot_sha256':BOOT_SHA,'owner_approved':True,'owner_available':True,
          'query_fid':'0x84000004','maximum_queries':4,'cpu_state_changes_allowed':False,
          'handoff_allowed':False}
        if any(type(auth.get(k)) is not type(v) or auth.get(k)!=v for k,v in expected.items()):
            raise ValueError('Fresh exact query-test approval and owner availability required')
    output.mkdir(mode=0o700)
    result={'scope':SCOPE,'module_sha256':checked['module_sha256'],'module_load_attempts':0,
      'module_loaded':False,'module_unloaded':False,'complete':False,
      'rebooted':False,'boot_written':False,'handoff_attempted':False,
      'cpu_hotplug_performed':False,'firmware_affinity_qualified':False}
    path=None
    def private(name,data):
        with (output/name).open('wb') as f:
            os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
    def save():private('result.json',(json.dumps(result,indent=2)+'\n').encode())
    def adb(command,check=True,timeout=30):
        r=subprocess.run(['adb','-s',selector,'exec-out',command],capture_output=True,timeout=timeout)
        if check and r.returncode:raise RuntimeError('ADB failed; no automatic retry')
        return r
    def absent():return 'kxaffinity ' not in adb('cat /proc/modules').stdout.decode()
    try:
        save()
        if adb('uname -r').stdout.strip().decode()!=RELEASE:raise ValueError('Wrong source kernel')
        if b'uid=0(' not in adb('id').stdout:raise ValueError('Existing root adbd required')
        if hashlib.sha256(gzip.decompress(adb('cat /proc/config.gz').stdout)).hexdigest()!=CONFIG_SHA:
            raise ValueError('Live config differs')
        boot=adb('head -c 16777216 /dev/block/mmcblk0p5').stdout
        if len(boot)!=16777216 or hashlib.sha256(boot).hexdigest()!=BOOT_SHA:
            raise ValueError('Original full boot differs')
        mounts=[l.split() for l in adb('cat /proc/mounts').stdout.decode().splitlines()]
        if not any(len(r)>3 and r[1]=='/dev' and r[2] in ['tmpfs','devtmpfs'] for r in mounts):
            raise ValueError('RAM-backed /dev required')
        if not absent():raise ValueError('Query module already present')
        before=adb('dmesg').stdout;private('dmesg-before-private.txt',before)
        if b'KXAFF' in before:raise ValueError('Prior query records; fresh attribution refused')
        result['preflight']='passed';save()
        if authorization is None:result['complete']=True;return result
        path='/dev/kxaffinity-'+secrets.token_hex(8)+'.ko'
        adb('umask 077; set -C; : > '+path)
        r=subprocess.run(['adb','-s',selector,'push',str(module),path],capture_output=True,timeout=30)
        private('push-private.log',r.stdout+r.stderr)
        if r.returncode:raise RuntimeError('RAM upload failed')
        adb('chmod 600 '+path)
        if hashlib.sha256(adb('cat '+path).stdout).hexdigest()!=checked['module_sha256']:
            raise ValueError('RAM module differs')
        result['module_load_attempts']=1;save()
        r=adb('insmod '+path,False,30);private('insmod-private.log',r.stdout+r.stderr)
        result['insmod_exit_code']=r.returncode
        if r.returncode:raise RuntimeError('Insertion rejected; no force-load/retry')
        result['module_loaded']=True;save()
        after=adb('dmesg').stdout;private('dmesg-after-private.txt',after)
        lines=[l for l in after.decode(errors='replace').splitlines() if 'KXAFF' in l]
        report=parse_report(lines);result.update(report);result['complete']=True
        return result
    except BaseException as error:
        result['failure_kind']=type(error).__name__
        raise
    finally:
        if result['module_load_attempts']:
            try:
                if not absent():
                    result['module_loaded']=True
                    r=adb('rmmod kxaffinity',False);private('rmmod-private.log',r.stdout+r.stderr)
                    result['module_unloaded']=r.returncode==0 and absent()
                final=adb('dmesg').stdout;private('dmesg-final-private.txt',final)
                if result['module_loaded'] and (not result['module_unloaded'] or
                     b'KXAFF unloaded state_changes=0 handoff=0' not in final):
                    result['complete']=False
            except BaseException as error:
                result['cleanup_failure_kind']=type(error).__name__;result['complete']=False
        if path:
            try:
                adb('rm -f '+path)
                result['ram_cleanup_verified']=adb('test ! -e '+path,False).returncode==0
                if not result['ram_cleanup_verified']:result['complete']=False
            except BaseException:
                result['complete']=False;result['ram_cleanup_verified']=False
        save()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--selector',required=True)
    for n in ['module','provider','output']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--authorization',type=Path)
    a=p.parse_args();r=run(a.selector,a.module,a.provider,a.output,a.authorization)
    print(json.dumps(r,indent=2));raise SystemExit(0 if r['complete'] else 1)
