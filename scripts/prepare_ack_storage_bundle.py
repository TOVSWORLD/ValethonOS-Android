#!/usr/bin/env python3
"""Storage-specific extension of the proven RAM/USB profile; never execute it."""
import json
import subprocess
from prepare_ack_usb_end_to_end import prepare as usb_prepare
from prepare_ack_combined_bundle import sha
from compare_pmic_dtb import snapshot
from ack_storage_contract import KIND, MMC0, verify_tree


def prepare(source_dtb, iomem, draft_dtb, image, config, initramfs, init_report,
            nonce, linked, out, fdtget, fdtput, system_map, trial_id=None):
    report = init_report
    if report.get('storage_readonly_profile') is not True:
        raise ValueError('Dedicated read-only storage PID1 required')
    result = usb_prepare(source_dtb, iomem, draft_dtb, image, config, initramfs,
                         init_report, nonce, linked, out, fdtget, fdtput, system_map, trial_id, storage_readonly=True)
    dt = out / 'target-private.dtb'
    subprocess.run([str(fdtput), '-t', 's', str(dt), MMC0, 'status', 'okay'], check=True)
    verify_tree(snapshot(fdtget, dt))
    data = dt.read_bytes()
    if len(data) > 0x18000:
        raise ValueError('DT overlaps entry')
    metadata = bytearray((out / 'metadata.bin').read_bytes())
    metadata[:0x18000] = bytes(0x18000)
    metadata[:len(data)] = data
    (out / 'metadata.bin').write_bytes(metadata)
    result.update(target_kind=KIND, target_dtb_sha256=sha(data),
                  all_storage_controllers_disabled=False, internal_emmc_only=True,
                  storage_readonly_profile=True, storage_status_protocol='VSTORE01',
                  scope='Internal eMMC read-only boot verification candidate; unexecuted')
    for segment in result['segments']:
        if segment['file'] == 'metadata.bin':
            segment['sha256'] = sha(metadata)
    (out / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
    return result
