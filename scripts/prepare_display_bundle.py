#!/usr/bin/env python3
"""Fresh display RAM bundle: reuse proven RAM derivation, no binary kernel hooks."""
import json
from pathlib import Path
import struct
import subprocess
from build_ack_combined_entry import build as build_entry
from compare_pmic_dtb import snapshot
from display_dtb_profile import preview
from display_kernel_contract import verify as verify_kernel,sha,CONTRACT
from prepare_ack_storage_bundle import prepare as prepare_ram_baseline
from prepare_ack_native_bundle import reserved_nodes,reservation_map
from prepare_native_jump_bundle import ranges_ok
KIND='ack-linux-display-mm-power-v10'


def prepare(source_dtb,iomem,kernel_package,baseline_package,initramfs_package,linked,
            out,fdtget,fdtput,trial_id=None):
    qualified=verify_kernel(kernel_package)
    config=(kernel_package/'resolved.config').read_bytes()
    init_report=json.loads((initramfs_package/'report.json').read_text())
    nonce=(initramfs_package/'trial-nonce-private.bin').read_bytes()
    if init_report.get('display_errors_profile') is not True or init_report.get('display_functional_profile') is not True or init_report.get('storage_probe_enabled') is not False:
        raise ValueError('Dedicated display-status PID1 required')
    out.mkdir(mode=0o700)
    baseline=out/'prior-storage-private'
    # The old fixed Image is used only by the established source/RAM/PSCI
    # derivation. Its transient entry/console code is never put in this bundle.
    m=prepare_ram_baseline(source_dtb,iomem,(baseline_package/'draft.dtb').read_bytes(),
        (baseline_package/'Image').read_bytes(),(baseline_package/'resolved.config').read_bytes(),
        (initramfs_package/'initramfs.cpio.gz').read_bytes(),init_report,nonce,linked,
        baseline,fdtget,fdtput,(baseline_package/'System.map').read_text(),trial_id)
    preview(baseline/'target-private.dtb',config.decode(),out/'display-preview-private',fdtget,fdtput)
    dt=out/'target-private.dtb';dt.write_bytes((out/'display-preview-private/display-preview-private.dtb').read_bytes())
    subprocess.run([str(fdtput),'-d',str(dt),'/chosen','valethon,offline-display-preview'],check=True)
    subprocess.run([str(fdtput),'-t','s',str(dt),'/chosen','valethon,native-trial',nonce.hex()],check=True)
    tree=snapshot(fdtget,dt)
    from prepare_native_jump_bundle import raw
    args=raw(tree['/chosen']['bootargs']).rstrip(b'\0').decode()+' valethon.native_trial='+nonce.hex()
    subprocess.run([str(fdtput),'-t','s',str(dt),'/chosen','bootargs',args],check=True)
    image=(kernel_package/'Image').read_bytes();extent=qualified['image_memory_bytes']
    padded=image+bytes(extent-len(image));code,deadline=build_entry(out/'entry-private',m['trial_id'],padded)
    data=dt.read_bytes()
    if len(data)>0x18000 or len(code)>0x8000:raise ValueError('Fixed metadata layout exceeded')
    metadata=bytearray(0x28000);metadata[:len(data)]=data;metadata[0x18000:0x18000+len(code)]=code
    initrd=(initramfs_package/'initramfs.cpio.gz').read_bytes()
    segments=[('image.bin',image,0x40000000,extent),('metadata.bin',bytes(metadata),0x42000000,0x28000),
              ('initrd.bin',initrd,0x69244000,(len(initrd)+4095)&~4095)]
    source_tree=snapshot(fdtget,baseline/'prior-private/base-private/source-private.dtb')
    firmware=reservation_map(source_dtb)[2]+reserved_nodes(source_tree)
    final_tree=snapshot(fdtget,dt)
    ranges_ok([(address,address+memory) for _,_,address,memory in segments],
              [tuple(r) for r in m['live_system_ram']],firmware+reserved_nodes(final_tree))
    for key in ['cinit_console','end_to_end_only','verbose_initcall_tracing']:
        m.pop(key,None)
    m.update(scope='Full unmodified display-kernel RAM candidate; unexecuted',target_kind=KIND,
             target_image_sha256=sha(image),base_target_image_sha256=sha(image),target_config_sha256=sha(config),
             target_release=qualified['target_release'],target_dtb_sha256=sha(data),image_memory_bytes=extent,
             image_padded_sha256=sha(padded),deadline=deadline,display_functional_profile=True,display_pwm_profile=True,display_mm_power_profile=True,
             storage_status_protocol=None,display_status_protocol='VDISP002',display_errors_profile=True,binary_code_hooks_added=False,
             unmodified_display_image=True,display_kernel_manifest_sha256=sha((kernel_package/'manifest.json').read_bytes()),
             display_kernel_contract_sha256=sha(CONTRACT.read_bytes()),segments=[])
    for name,content,address,memory in segments:
        path=out/name;path.write_bytes(content);path.chmod(0o600)
        m['segments'].append(dict(file=name,sha256=sha(content),bytes=len(content),address=address,memory_bytes=memory))
    (out/'report.json').write_text(json.dumps(m,indent=2)+'\n')
    return m
