#!/usr/bin/env python3
"""Independently verify unmodified display Image, fresh PID1, RAM and DT closure."""
import gzip
import json
from pathlib import Path
import re
import struct
import tempfile
from ack_storage_contract import verify_tree as verify_storage
from build_ack_combined_entry import build as build_entry
from build_diagnostic_initramfs import inspect_elf
from build_lab_log_initramfs import inspect_archive
from compare_pmic_dtb import snapshot
from display_dtb_profile import plan
from display_kernel_contract import verify as verify_kernel,sha,CONTRACT
from prepare_display_bundle import KIND
from prepare_native_jump_bundle import raw,ranges_ok
from prepare_ack_native_bundle import reserved_nodes,reservation_map
from validate_lab_policy_vm import generated_header
from verify_ack_ramfix_bundle import verify as verify_ram
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'projects/firetabs-android/diagnostic-usb'
POLICY='bb81388f3817c91e1f0590c67a208d83224c2d3a20f7cc00f4401553f8a0bacd'


def component(package,nonce):
    report=json.loads((package/'report.json').read_text())
    if (report.get('display_errors_profile') is not True or report.get('display_functional_profile') is not True or report.get('storage_probe_enabled') is not False
            or report.get('storage_readonly_profile') is not True or report['policy_sha256']!=POLICY
            or len(nonce)!=32 or sha(nonce)!=report['nonce_sha256']):
        raise ValueError('Exact enforcing display PID1 required')
    if not {'display_errors.h','display_status.h','storage_init.c','lab_policy_load.h','lab_labels.h','lab_domain.h'}.issubset(report['sources_sha256']):
        raise ValueError('Display runtime source closure missing')
    for name,digest in report['sources_sha256'].items():
        if Path(name).name!=name or sha((SOURCE/name).read_bytes())!=digest:raise ValueError('Display component source drift')
    if report['builder_sha256']!=sha((ROOT/'scripts/build_lab_log_initramfs.py').read_bytes()):raise ValueError('Display builder drift')
    elf=(package/'init').read_bytes();inspect_elf(elf)
    header=generated_header((package/'lab_inputs.h').read_bytes(),report)
    body=re.search(rb'static const unsigned char lab_policy_blob\[\]=\{\n([0-9a-fx,\n]+)\n\};\n',header)[1]
    policy=bytes(int(token,16) for token in body.replace(b'\n',b'').split(b','))
    if sha(policy)!=POLICY or elf.count(policy)!=1 or nonce not in elf or b'VDISP002' not in elf or b'VKMSG001' not in elf or b'VALETHON DISPLAY TEST' not in elf:
        raise ValueError('Display ELF policy/identity/banner differs')
    packed=(package/'initramfs.cpio.gz').read_bytes()
    for name,data in [('init',elf),('initramfs.cpio.gz',packed)]:
        if report['artifacts'][name]!={'bytes':len(data),'sha256':sha(data)}:raise ValueError('Display artifact differs')
    entries=[(n,0o040755,b'',(0,0)) for n in ['dev','proc','sys','security','config']]
    entries += [('dev/console',0o020600,b'',(5,1)),('dev/kmsg',0o020400,b'',(1,11)),
                ('dev/firetabs-boot',0o060400,b'',(179,5)),('init',0o100500,elf,(0,0))]
    inspect_archive(gzip.decompress(packed),entries,storage_readonly=True)
    return {'display_component_verified':True,'initramfs_sha256':sha(packed)}


def verify(manifest,kernel,baseline,initramfs,fdtget=Path('work/dtb-tool/build/fdtget'),nonce=None):
    k=verify_kernel(kernel);c=component(initramfs,nonce);m=json.loads(manifest.read_text());root=manifest.parent
    if (m.get('target_kind')!=KIND or m.get('display_pwm_profile') is not True or m.get('display_functional_profile') is not True
            or m.get('binary_code_hooks_added') is not False or m.get('unmodified_display_image') is not True
            or m.get('display_status_protocol')!='VDISP002' or m.get('display_errors_profile') is not True or m['target_image_sha256']!=k['image_sha256']
            or m['target_config_sha256']!=k['config_sha256'] or m['target_release']!=k['target_release']
            or m['target_initramfs_sha256']!=c['initramfs_sha256'] or m['target_nonce_sha256']!=sha(nonce)
            or m['display_kernel_contract_sha256']!=sha(CONTRACT.read_bytes())):
        raise ValueError('Exact display bundle profile required')
    prior=root/'prior-storage-private'
    verify_ram(prior/'report.json',baseline,fdtget,nonce,expected_kind='ack-linux-storage-readonly-v6')
    old=json.loads((prior/'report.json').read_text())
    for field in ['source_dtb_sha256','source_config_sha256','source_kernel_image_sha256','original_boot_sha256','memory_banks',
                  'live_system_ram','live_ram_exclusions','source_iomem_sha256','trial_id']:
        if m[field]!=old[field]:raise ValueError('Proven source/RAM binding changed')
    if [v['file'] for v in m['segments']]!=['image.bin','metadata.bin','initrd.bin']:
        raise ValueError('Exact segment set required')
    data={v['file']:(root/v['file']).read_bytes() for v in m['segments']}
    if data['image.bin']!=(kernel/'Image').read_bytes() or data['initrd.bin']!=(initramfs/'initramfs.cpio.gz').read_bytes():
        raise ValueError('Unmodified Image/ramdisk differs')
    expected_layout=[(0x40000000,k['image_memory_bytes']),(0x42000000,0x28000),(0x69244000,(len(data['initrd.bin'])+4095)&~4095)]
    for segment,(address,memory) in zip(m['segments'],expected_layout):
        value=data[segment['file']]
        if (segment['address']!=address or segment['memory_bytes']!=memory or segment['bytes']!=len(value)
                or segment['sha256']!=sha(value) or not 0<len(value)<=memory):raise ValueError('Display segment differs')
    dt=(root/'target-private.dtb').read_bytes()
    if sha(dt)!=m['target_dtb_sha256']:raise ValueError('Display DT file differs')
    tree=snapshot(fdtget,root/'target-private.dtb');verify_storage(tree)
    before=snapshot(fdtget,prior/'target-private.dtb');resources,changes=plan(before,(kernel/'resolved.config').read_text())
    expected={node:dict(p) for node,p in before.items()}
    encode=lambda b:' '.join(format(v,'x') for v in b)
    for kind,node,prop,value in changes:
        if kind=='create':expected[node]={};continue
        if kind=='delete':expected[node].pop(prop,None);continue
        value=value.encode()+b'\0' if kind=='s' else struct.pack('>'+'I'*len(value),*value) if kind=='x' else bytes(value) if kind=='bytes' else b''
        expected[node][prop]=encode(value)
    expected['/chosen'].pop('valethon,offline-display-preview')
    expected['/chosen']['valethon,native-trial']=encode(nonce.hex().encode()+b'\0')
    args=raw(expected['/chosen']['bootargs']).rstrip(b'\0')+b' valethon.native_trial='+nonce.hex().encode()+b'\0'
    expected['/chosen']['bootargs']=encode(args)
    if tree!=expected:raise ValueError('Independent display DT reconstruction differs')
    if reservation_map(dt)[2]!=reservation_map((prior/'target-private.dtb').read_bytes())[2]:raise ValueError('Firmware/metadata reservation map differs')
    source_tree=snapshot(fdtget,prior/'prior-private/base-private/source-private.dtb')
    source=(prior/'prior-private/base-private/source-private.dtb').read_bytes()
    ranges_ok([(v['address'],v['address']+v['memory_bytes']) for v in m['segments']],
              [tuple(v) for v in m['live_system_ram']],reservation_map(source)[2]+reserved_nodes(source_tree)+reserved_nodes(tree))
    with tempfile.TemporaryDirectory(prefix='display-entry-verify-') as directory:
        padded=data['image.bin']+bytes(k['image_memory_bytes']-len(data['image.bin']))
        code,deadline=build_entry(Path(directory)/'entry',m['trial_id'],padded)
        metadata=bytearray(0x28000);metadata[:len(dt)]=dt;metadata[0x18000:0x18000+len(code)]=code
        if bytes(metadata)!=data['metadata.bin'] or deadline!=m['deadline'] or sha(padded)!=m['image_padded_sha256']:
            raise ValueError('Reproduced integrity/deadline metadata differs')
    return dict(display_bundle_verified=True,unmodified_image_verified=True,instrumented_image_sha256=k['image_sha256'],
                image_sha256=k['image_sha256'],display_component_verified=True,hardware_execution=False)
