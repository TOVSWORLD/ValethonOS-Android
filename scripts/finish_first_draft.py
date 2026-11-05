#!/usr/bin/env python3
"""Finish a combined draft boot artifact locally; no flash, helper or reboot."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import struct
import subprocess
import sys
import first_draft_config
import build_lab_retained_dtb
import retained_log_mailbox as mailbox
from build_douglas_dtb import inspect_header
from pack_lab_log_boot import assemble, CONTRACT, METADATA

ROOT=Path(__file__).resolve().parents[1]
ARGS='nr_cpus=1 maxcpus=0 clk_ignore_unused regulator_ignore_unused rdinit=/init initcall_debug ignore_loglevel loglevel=8 printk.time=1 panic=0'

def sha(data):return hashlib.sha256(data).hexdigest()

def finish(kernel,component,output):
    if output.exists() or output.is_symlink():raise ValueError('Fresh output required')
    manifest=json.loads((kernel/'manifest.json').read_text())
    if manifest.get('build_mode')!='first-draft':raise ValueError('Exact combined first-draft build required')
    for name,facts in manifest['files'].items():
        if Path(name).name!=name:raise ValueError('Flat manifest paths required')
        data=(kernel/name).read_bytes()
        if facts!={'bytes':len(data),'sha256':sha(data)}:raise ValueError('Kernel artifact mismatch')
    first_draft_config.diagnostic_config.check((kernel/'resolved.config').read_text(),first_draft_config.requirements())
    report=json.loads((component/'report.json').read_text());nonce=(component/'trial-nonce-private.bin').read_bytes()
    if report['nonce_sha256']!=sha(nonce):raise ValueError('Exact component nonce required')
    ramdisk=(component/'initramfs.cpio.gz').read_bytes()
    if report['artifacts']['initramfs.cpio.gz']!={'bytes':len(ramdisk),'sha256':sha(ramdisk)}:raise ValueError('Ramdisk mismatch')
    for name,expected in report['sources_sha256'].items():
        if Path(name).name!=name or sha((ROOT/'projects/firetabs-android/diagnostic-usb'/name).read_bytes())!=expected:raise ValueError('Producer source drift')
    output.mkdir(mode=0o700,parents=True)
    dt_report=build_lab_retained_dtb.build(output/'dt',nonce)
    # Change only the already-reviewed chosen boot arguments, not hardware data.
    source=output/'dt/retained.dts';text=source.read_text()
    text+='\n/ { chosen { bootargs = "'+ARGS+'"; }; };\n'
    source.write_text(text);dtb=output/'draft.dtb'
    subprocess.run([str(ROOT/'work/dtb-tool/build/dtc'),'-a','4','-I','dts','-O','dtb','-o',str(dtb),str(source)],check=True,capture_output=True)
    image=(kernel/'Image').read_bytes();compressed=(kernel/'Image.gz').read_bytes()
    releases=set(re.findall(rb'Linux version ([^\s\x00]+)',image))
    releases={x for x in releases if x.endswith(b'-valethon-draft1')}
    if len(releases)!=1:raise ValueError('Exact first-draft kernel release required')
    release=releases.pop().decode('ascii')
    full,layout=assemble(image,compressed,dtb.read_bytes(),ramdisk,json.loads(CONTRACT.read_text()),json.loads(METADATA.read_text()))
    # v0 cmdline is outside its component ID, but inside immutable prefix hash.
    full=bytearray(full);full[64:576]=bytes(512);full[64:64+len(ARGS)]=ARGS.encode();full=bytes(full)
    full,prefix=mailbox.prepare(full,nonce,b'VALETHON HOST CONTROL v1\nFirst complete draft fixture; not kernel output\n')
    path=output/'boot-full.img';path.write_bytes(full);path.chmod(0o600)
    result={'scope':'Complete first kernel draft; untested on hardware','kernel_source':manifest['kernel_revision'],
            'repository_revision':manifest['repository_revision'],'build_run':manifest['run_id'],
            'kernel_release':release,'kernel_manifest_sha256':sha((kernel/'manifest.json').read_bytes()),'component_report_sha256':sha((component/'report.json').read_bytes()),
            'partition_bytes':len(full),'partition_sha256':sha(full),'nonce_sha256':sha(nonce),
            'prefix_sha256':prefix,'dt':inspect_header(dtb.read_bytes()),'layout':layout,
            'bootargs':ARGS,'logging_backends':['USB ACM VLOG0002','kernel boot-tail VLOG0001'],
            'automatic_reboot_requested':False,'physical_execution_admitted':False,'kernel_boot_confirmed':False,'hardware_logging_confirmed':False}
    (output/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['kernel','component','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();print(json.dumps(finish(a.kernel,a.component,a.output),indent=2))
