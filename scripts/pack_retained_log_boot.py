#!/usr/bin/env python3
"""Offline seeded persistent-log candidate. Never write/boot a device."""
import argparse
import hashlib
import json
from pathlib import Path
import os
import lab_log_config
from measure_arm64_image import bounded_file, MAX_IMAGE
from pack_lab_log_boot import assemble, CONTRACT, METADATA, ROOT, sha
import retained_log_mailbox as mailbox


def pack(kernel_dir,dtb,dt_report,component_dir,output):
    if output.exists() or output.is_symlink():raise ValueError('Fresh private output required')
    manifest=json.loads((kernel_dir/'manifest.json').read_text())
    for name,info in manifest['files'].items():
        if Path(name).name!=name:raise ValueError('Invalid manifest path')
        data=bounded_file(kernel_dir/name,MAX_IMAGE)
        if len(data)!=info['bytes'] or sha(data)!=info['sha256']:raise ValueError('Kernel manifest differs')
    config=(kernel_dir/'resolved.config').read_text()
    lab_log_config.diagnostic_config.check(config,lab_log_config.requirements(True));lab_log_config.usb_acm_config.check(config)
    dt=json.loads(dt_report.read_text());blob=bounded_file(dtb,1024*1024)
    if dt['artifact']['sha256']!=sha(blob) or not dt['exact_delta_only'] or not dt['firmware_reservations_unchanged']:raise ValueError('Exact retained DT report required')
    baseline=dt['baseline']
    for name,field in [('projects/firetabs-android/kernel/lab-log/append.dts','append_sha256'),('evidence/independent-recovery/trial-placement-metadata.json','metadata_sha256')]:
        if sha((ROOT/name).read_bytes())!=baseline[field]:raise ValueError('Baseline DT inputs changed')
    component=json.loads((component_dir/'report.json').read_text());nonce=(component_dir/'trial-nonce-private.bin').read_bytes()
    if len(nonce)!=32 or sha(nonce)!=component['nonce_sha256'] or sha(nonce)!=dt['nonce_sha256']:raise ValueError('Fresh nonce binding differs')
    for field,name in [('builder_sha256','scripts/build_lab_log_initramfs.py'),('archive_builder_sha256','scripts/build_diagnostic_initramfs.py')]:
        if sha((ROOT/name).read_bytes())!=component[field]:raise ValueError('Component builder drift')
    for name,want in component['sources_sha256'].items():
        if Path(name).name!=name or sha((ROOT/'projects/firetabs-android/diagnostic-usb'/name).read_bytes())!=want:raise ValueError('Component source drift')
    ramdisk=bounded_file(component_dir/'initramfs.cpio.gz',1024*1024)
    if component['artifacts']['initramfs.cpio.gz']!={'bytes':len(ramdisk),'sha256':sha(ramdisk)}:raise ValueError('Exact initramfs required')
    full,report=assemble((kernel_dir/'Image').read_bytes(),(kernel_dir/'Image.gz').read_bytes(),blob,ramdisk,json.loads(CONTRACT.read_text()),json.loads(METADATA.read_text()))
    if report['payload_bytes']>mailbox.BASE:raise ValueError('Boot payload intrudes into retained slot')
    control=b'VALETHON HOST CONTROL v1\nThis is a preinstalled retention control, NOT a kernel log.\n'
    full,prefix=mailbox.prepare(full,nonce,control)
    mailbox.inspect(full,nonce,prefix)
    report.update(scope='Offline first normal log-bringup candidate; review still required',partition_sha256=sha(full),contract_sha256=sha(CONTRACT.read_bytes()),config_sha256=sha(config.encode()),nonce_sha256=sha(nonce),policy_sha256=component['policy_sha256'],physical_execution_admitted=False,failed_load_qualified=False,recovery_partition_written=False,original_partition_tail_replaced=True,
                  retained_mailbox={'format':'VLOG0001','seed_offset':mailbox.BASE,'slot_base':mailbox.SLOT_BASE,'slot_bytes':mailbox.SLOT,'payload_capacity':mailbox.CAPACITY,'prefix_sha256':prefix,'original_boot_write_admitted':False,'record_device_qualified':False,'host_control_sequence':1,'host_control_sha256':sha(control),'kernel_record_requires_sequence_at_least':2},kernel_manifest=manifest)
    output.mkdir(mode=0o700)
    for name,data in [('boot-full.img',full),('report.json',(json.dumps(report,indent=2)+'\n').encode())]:
        fd=os.open(output/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'wb') as out:out.write(data)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['kernel-dir','dtb','dt-report','component-dir','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();print(json.dumps(pack(a.kernel_dir,a.dtb,a.dt_report,a.component_dir,a.output),indent=2))
