#!/usr/bin/env python3
"""Enforcing storage-policy VM test on synthetic read-only virtio disk only."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import shutil
import subprocess
import time
from build_diagnostic_initramfs import archive, inspect_elf

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'projects/firetabs-android/diagnostic-usb'
SIZE = 16*1024*1024
FIXTURE_SHA = hashlib.sha256(b'Z'*SIZE).hexdigest()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def parse_log(data):
    expected = {'VM_STORAGE_DOMAIN': 0, 'VM_STORAGE_ENFORCE': 1,
                'VM_STORAGE_READ_BYTES': SIZE, 'VM_STORAGE_EOF': 0,
                'VM_STORAGE_HASH': 0, 'VM_STORAGE_BAD_HASH': 1,
                'VM_STORAGE_IOCTL_DENIED': -13, 'VM_STORAGE_READ_FD_WRITE_DENIED': -9,
                'VM_STORAGE_WRITE_OPEN_DENIED': -13, 'VM_STORAGE_OTHER_READ_DENIED': -13,
                'VM_STORAGE_MKNOD_DENIED': -13}
    values = {}
    for key, value in re.findall(rb'^(VM_STORAGE_[A-Z_]+)=([+-][0-9]{10})$', data.replace(b'\r\n',b'\n'), re.M):
        key=key.decode()
        if key in values:
            raise ValueError('Duplicate storage VM marker')
        values[key]=int(value)
    opened=values.pop('VM_STORAGE_READ_OPEN', -1)
    if values!=expected or opened<0 or data.count(b'VM_STORAGE_PROBE_DONE')!=1:
        raise ValueError('Storage VM positive/negative control failed')
    if any(token in data for token in [b'Kernel panic', b'Internal error: Oops']):
        raise ValueError('Storage VM fault')
    return values


def run(kernel, expected_kernel, component, output, virtualization):
    if output.exists() or output.is_symlink():
        raise ValueError('Fresh output required')
    if sha(kernel.read_bytes())!=expected_kernel:
        raise ValueError('Exact maintained kernel required')
    report=json.loads((component/'report.json').read_text())
    if report.get('storage_readonly_profile') is not True:
        raise ValueError('Storage-only component required')
    header=(component/'lab_inputs.h').read_bytes()
    arrays=re.findall(rb'static const unsigned char (lab_policy_blob|lab_trial_nonce)\[\]=\{\n([0-9a-fx,\n]+)\n\};\n',header)
    values={name.decode():bytes(int(token,16) for token in body.replace(b'\n',b'').split(b',')) for name,body in arrays}
    if len(arrays)!=2 or set(values)!={'lab_policy_blob','lab_trial_nonce'} or sha(values['lab_policy_blob'])!=report['policy_sha256'] or len(values['lab_trial_nonce'])!=32 or sha(values['lab_trial_nonce'])!=report['nonce_sha256']:
        raise ValueError('Exact generated policy/nonce required')
    output.mkdir(mode=0o700,parents=True)
    (output/'lab_inputs.h').write_bytes((component/'lab_inputs.h').read_bytes())
    digest=bytes.fromhex(FIXTURE_SHA)
    (output/'vm_expected.h').write_text('#define VM_STORAGE_EXPECTED_HASH {'+','.join(str(x) for x in digest)+'}\n')
    command=['clang-18','--target=aarch64-linux-gnu','--ld-path='+shutil.which('ld.lld-18'),
             '-nostdlib','-static','-Os','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin',
             '-fno-stack-protector','-mgeneral-regs-only','-Wl,--build-id=none,-e,_start',
             '-I',str(SOURCE),'-I',str(output),'-include',str(output/'vm_expected.h'),
             str(SOURCE/'storage_vm.c'),str(SOURCE/'memory.c'),
             str(ROOT/'projects/firetabs-android/native-kexec/combined_sha256.c'),'-o',str(output/'init')]
    result=subprocess.run(command,capture_output=True,timeout=90)
    (output/'compile-private.log').write_bytes(result.stdout+result.stderr)
    if result.returncode:
        raise ValueError('Storage VM probe compilation failed')
    elf=(output/'init').read_bytes();inspect_elf(elf)
    entries=[(n,0o040755,b'',(0,0)) for n in ['dev','proc','sys','security','config']]
    entries += [('dev/console',0o020600,b'',(5,1)),('dev/kmsg',0o020400,b'',(1,11)),('init',0o100500,elf,(0,0))]
    initrd=output/'vm-only-initramfs.cpio.gz';initrd.write_bytes(gzip.compress(archive(entries),mtime=0))
    disk=output/'synthetic-readonly.raw';disk.write_bytes(b'Z'*SIZE);disk.chmod(0o400)
    command=['qemu-system-aarch64','-machine','virt,gic-version=2,virtualization='+virtualization,
             '-cpu','cortex-a53','-smp','1','-m','1536','-accel','tcg','-nodefaults','-display','none',
             '-serial','stdio','-monitor','none','-nic','none','-no-reboot','-kernel',str(kernel),'-initrd',str(initrd),
             '-drive','file='+str(disk)+',format=raw,if=none,id=storage,readonly=on',
             '-device','virtio-blk-device,drive=storage',
             '-append','console=ttyAMA0,115200 rdinit=/init nr_cpus=1 maxcpus=0 loglevel=7 panic=-1']
    process=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    data=bytearray();began=time.monotonic()
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout,selectors.EVENT_READ)
            while time.monotonic()-began<60 and len(data)<2*1024*1024:
                for key,_ in selector.select(.1):
                    block=os.read(key.fd,65536)
                    if block:data.extend(block)
                if b'VM_STORAGE_PROBE_DONE' in data or process.poll() is not None:
                    break
    finally:
        if process.poll() is None:process.terminate()
        try:process.wait(timeout=5)
        except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
    (output/'boot-private.log').write_bytes(data)
    passed=False;failure=None
    try:parse_log(bytes(data));passed=True
    except ValueError as error:failure=str(error)
    unchanged=sha(disk.read_bytes())==FIXTURE_SHA
    final={'scope':'Enforcing storage policy on synthetic read-only VM disk only; no tablet qualification',
           'passed':passed and unchanged,'failure':failure,'virtualization':virtualization,
           'kernel_sha256':expected_kernel,'policy_sha256':report['policy_sha256'],
           'vm_initramfs_sha256':sha(initrd.read_bytes()),'fixture_sha256':FIXTURE_SHA,
           'fixture_unchanged':unchanged,'readonly_backend':True,'vm_only':True,
           'physical_storage_verified':False,'tablet_commands':False,'network_attached':False,
           'boot_log_sha256':sha(data),'elapsed_seconds':round(time.monotonic()-began,3)}
    (output/'report.json').write_text(json.dumps(final,indent=2)+'\n')
    return final


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['kernel','component','output']:parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--expected-kernel',required=True)
    parser.add_argument('--virtualization',choices=['on','off'],required=True)
    args=parser.parse_args()
    result=run(args.kernel,args.expected_kernel,args.component,args.output,args.virtualization)
    print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed'] else 1)
