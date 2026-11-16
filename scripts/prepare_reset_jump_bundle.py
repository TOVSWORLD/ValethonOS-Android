#!/usr/bin/env python3
"""Use the proven native layout for a distinct, non-Linux reset target."""
import hashlib
import json
from build_reset_payload import validate
from prepare_native_jump_bundle import prepare, IMAGE, META, ENTRY
from prepare_kexec_entry import candidate, TEMPLATE


def prepare_reset(boot, dtb, iomem, out, fdtget, fdtput, image, payload, linked):
    validate(image, payload)
    if linked.get('early_cpu_shutdown_before_devices') is not True or linked.get('native_entry_checkpoint_linked') is not True:
        raise ValueError('Hardware-tested early CPU shutdown source required')
    # The ordinary builder validates original boot, fresh FDT, reserved RAM,
    # original initrd and all three existing destination extents. The reset
    # image only reduces the first extent to one page, a validated subset.
    m = prepare(boot, dtb, iomem, out, fdtget, fdtput)
    if m['trial_id'] == payload['nonce']:
        raise ValueError('Source challenge and target-only nonce must differ')
    trampoline, _ = candidate(TEMPLATE, image, (out / 'target-private.dtb').read_bytes(), IMAGE, META, ENTRY)
    metadata = (out / 'metadata.bin').read_bytes()
    if metadata[ENTRY - META:] != trampoline:
        raise ValueError('Reset target must retain the exact DT entry trampoline')
    (out / 'image.bin').write_bytes(image)
    m['segments'][0].update(sha256=hashlib.sha256(image).hexdigest(), bytes=4096, memory_bytes=4096)
    m.update(scope='Minimal reset payload through the existing native layout; not Linux boot',
             target_kind='reset-payload-v1', target_image_sha256=hashlib.sha256(image).hexdigest(),
             source_config_sha256=linked['artifacts']['.config']['sha256'],
             source_kernel_image_sha256=linked['artifacts']['arch/arm64/boot/Image']['sha256'],
             source_cpu_shutdown_before_devices=True, reset_nonce=payload['nonce'],
             reset_payload_report_sha256=hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest(),
             target_linux_boot_proven=False,
             unqualified=['Native transition and payload execution', 'Watchdog-reset retention',
                          'Automatic return to original Android'])
    (out / 'report.json').write_text(json.dumps(m, indent=2) + '\n')
    return m
