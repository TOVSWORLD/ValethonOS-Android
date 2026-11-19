#!/usr/bin/env python3
"""Run exact graphics loader/policy controls in a bounded networkless generic VM."""
import argparse, hashlib, json, os, re, selectors, subprocess, time
from pathlib import Path
sha=lambda b:hashlib.sha256(b).hexdigest()


def parse_log(data):
    text=data.replace(b'\r\n',b'\n');values={}
    for key,value in re.findall(rb'^(VM_GRAPHICS_[A-Z_]+)=([+-][0-9]{10})$',text,re.M):
        key=key.decode()
        if key in values: raise ValueError('Duplicate graphics VM marker')
        values[key]=int(value)
    expected={**{'VM_GRAPHICS_'+n:0 for n in ['ENFORCE','DRIVER_DLOPEN','GBM_DLOPEN','EGL_CLIENT','MEMFD','MEMORY_RW']},
              **{'VM_GRAPHICS_'+n:-13 for n in ['MEMORY_EXEC_DENIED','FORK_DENIED','INPUT_WRITE_DENIED','BLOCK_WRITE_DENIED']}}
    if values!=expected or text.count(b'VM_GRAPHICS_PROBE_DONE')!=1 or any(t in text for t in [b'Kernel panic',b'Internal error: Oops']):
        raise ValueError('Graphics loader/memory/policy VM controls failed')
    return values


def run(kernel, expected_kernel, component, output, virtualization):
    if sha(kernel.read_bytes())!=expected_kernel: raise ValueError('Exact VM kernel required')
    report=json.loads((component/'report.json').read_text());initrd=component/'vm-only-initramfs.cpio.xz';facts=report['artifacts']['vm-only-initramfs.cpio.xz']
    if report.get('graphics_render_profile') is not True or sha(initrd.read_bytes())!=facts['sha256'] or initrd.stat().st_size!=facts['bytes']:
        raise ValueError('Exact VM-only graphics archive required')
    output.mkdir(mode=0o700,parents=True)
    args=['qemu-system-aarch64','-machine','virt,gic-version=2,virtualization='+virtualization,'-cpu','cortex-a53',
          '-smp','1','-m','1536','-accel','tcg','-nodefaults','-display','none','-serial','stdio','-monitor','none',
          '-nic','none','-no-reboot','-kernel',str(kernel),'-initrd',str(initrd),
          '-append','console=ttyAMA0,115200 rdinit=/init nr_cpus=1 maxcpus=0 loglevel=7 panic=-1']
    process=subprocess.Popen(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);data=bytearray();began=time.monotonic()
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout,selectors.EVENT_READ)
            while time.monotonic()-began<90 and len(data)<2*1024*1024:
                for key,_ in selector.select(.1):data.extend(os.read(key.fd,65536))
                if b'VM_GRAPHICS_PROBE_DONE' in data or process.poll() is not None:break
    finally:
        if process.poll() is None:process.terminate()
        try:process.wait(timeout=5)
        except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
    (output/'boot-private.log').write_bytes(data);passed=False;failure=None
    try:parse_log(bytes(data));passed=True
    except ValueError as error:failure=str(error)
    result={'scope':'VM graphics loader/policy only; no physical renderer qualification','passed':passed,'failure':failure,
        'kernel_sha256':expected_kernel,'policy_sha256':report['policy_sha256'],'component_report_sha256':sha((component/'report.json').read_bytes()),
        'vm_archive_sha256':facts['sha256'],'virtualization':virtualization,'vm_only':True,'network_attached':False,
        'physical_graphics_verified':False,'boot_log_sha256':sha(data),'elapsed_seconds':round(time.monotonic()-began,3)}
    (output/'report.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['kernel','component','output']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--expected-kernel',required=True);p.add_argument('--virtualization',choices=['off','on'],required=True)
    a=p.parse_args();r=run(a.kernel,a.expected_kernel,a.component,a.output,a.virtualization);print(json.dumps(r,indent=2));raise SystemExit(0 if r['passed'] else 1)
