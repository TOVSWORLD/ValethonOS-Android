#!/usr/bin/env python3
"""Independently verify storage-only bundle, production archive and policy binding."""
import gzip
import json
import re
from pathlib import Path
from ack_storage_contract import KIND
from build_diagnostic_initramfs import inspect_elf
from build_lab_log_initramfs import inspect_archive
from prepare_ack_combined_bundle import sha
from verify_ack_ramfix_bundle import verify as ram_verify

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'projects/firetabs-android/diagnostic-usb'
POLICY_SHA='bb81388f3817c91e1f0590c67a208d83224c2d3a20f7cc00f4401553f8a0bacd'


def verify_component(component, nonce):
    report=json.loads((component/'report.json').read_text())
    if report.get('storage_readonly_profile') is not True or report.get('vm_only'):
        raise ValueError('Production storage-only component required')
    if report['policy_sha256']!=POLICY_SHA or len(nonce)!=32 or sha(nonce)!=report['nonce_sha256']:
        raise ValueError('Exact storage policy and fresh identity required')
    required={'storage_init.c','storage_readonly.h','lab_labels.h','lab_domain.h','lab_policy_load.h','acm_serial.h','acm_fs.h','memory.c'}
    if not required.issubset(report['sources_sha256']):
        raise ValueError('Runtime source bindings missing')
    for name, digest in report['sources_sha256'].items():
        if Path(name).name!=name or sha((SOURCE/name).read_bytes())!=digest:
            raise ValueError('Runtime source changed: '+name)
    if report['storage_sha_source_sha256']!=sha((ROOT/'projects/firetabs-android/native-kexec/combined_sha256.c').read_bytes()):
        raise ValueError('Storage hash implementation changed')
    if report['builder_sha256']!=sha((ROOT/'scripts/build_lab_log_initramfs.py').read_bytes()):
        raise ValueError('Component builder changed')
    elf=(component/'init').read_bytes();inspect_elf(elf)
    from validate_lab_policy_vm import generated_header
    header=generated_header((component/'lab_inputs.h').read_bytes(),report)
    body=re.search(rb'static const unsigned char lab_policy_blob\[\]=\{\n([0-9a-fx,\n]+)\n\};\n',header)[1]
    policy=bytes(int(token,16) for token in body.replace(b'\n',b'').split(b','))
    if sha(policy)!=POLICY_SHA or elf.count(policy)!=1:
        raise ValueError('Pinned policy blob missing from production ELF')
    if nonce not in elf or b'VSTORE01' not in elf or b'VM_STORAGE_' in elf or b'VM_FILESYSTEM_' in elf:
        raise ValueError('Wrong production PID1 identity/profile')
    packed=(component/'initramfs.cpio.gz').read_bytes()
    for name,content in [('init',elf),('initramfs.cpio.gz',packed)]:
        if report['artifacts'][name]!={'bytes':len(content),'sha256':sha(content)}:
            raise ValueError('Component artifact differs')
    entries=[(n,0o040755,b'',(0,0)) for n in ['dev','proc','sys','security','config']]
    entries += [('dev/console',0o020600,b'',(5,1)),('dev/kmsg',0o020400,b'',(1,11)),
                ('dev/firetabs-boot',0o060400,b'',(179,5)),('init',0o100500,elf,(0,0))]
    inspect_archive(gzip.decompress(packed),entries,storage_readonly=True)
    return dict(storage_component_verified=True,storage_policy_sha256=POLICY_SHA,
                initramfs_sha256=sha(packed),storage_status_protocol='VSTORE01')


def verify(manifest,kernel_package,component,fdtget=Path('work/dtb-tool/build/fdtget'),nonce=None):
    checked=verify_component(component,nonce)
    report=json.loads(manifest.read_text())
    if (report.get('storage_readonly_profile') is not True or report.get('internal_emmc_only') is not True
            or report.get('all_storage_controllers_disabled') is not False or report.get('storage_status_protocol')!='VSTORE01'
            or report['target_initramfs_sha256']!=checked['initramfs_sha256']
            or sha((manifest.parent/'initrd.bin').read_bytes())!=checked['initramfs_sha256']):
        raise ValueError('Storage manifest/component differs')
    result=ram_verify(manifest,kernel_package,fdtget,nonce,expected_kind=KIND)
    return dict(**result,**checked,storage_bundle_verified=True,hardware_execution=False)
