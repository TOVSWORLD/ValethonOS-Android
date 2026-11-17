#!/usr/bin/env python3
"""Offline audit of the consumed ACK trial; never accesses a device.

Run with the isolated Unicorn environment. Source relocation is exercised with
synthetic disjoint source pages, not a recovered hardware kimage page list.
The kernel prefix uses reset-like Cortex-A53 EL1 registers, not firmware state.
"""
import argparse
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from verify_native_kexec_build import mapped_bytes
from prepare_ack_native_bundle import IMAGE_SHA, CONFIG_SHA, IMAGE, META, ENTRY


def sha(b):
    return hashlib.sha256(b).hexdigest()


def symbols(text):
    return {v[2]: int(v[0], 16) for line in text.splitlines() if len(v := line.split()) == 3}


def cpu():
    import unicorn as u
    from unicorn import arm64_const as r
    uc = u.Uc(u.UC_ARCH_ARM64, u.UC_MODE_ARM)
    uc.ctl_set_cpu_model(r.UC_CPU_ARM64_A53)
    uc.reg_write(r.UC_ARM64_REG_PSTATE, 0x3c5)
    uc.reg_write(r.UC_ARM64_REG_CP_REG, (1, 0, 3, 0, 0, 0))  # SCTLR_EL1
    return u, r, uc


def relocate(code, segments, *, corrupt_source=False):
    u, r, uc = cpu()
    for at, size in [(IMAGE, 0x4000000), (0x50000000, 0x4000000),
                     (0x69244000, 0x100000), (0x6a000000, 0x100000)]:
        uc.mem_map(at, size)
    uc.mem_write(0x6a000000, code)
    entries, src = [], 0x50000000
    for s, data in segments:
        if len(data) != s['memory_bytes'] or len(data) % 4096:
            raise ValueError('Page-aligned complete segment required')
        if corrupt_source and s['file'] == 'image.bin':
            data = bytes([data[0] ^ 1]) + data[1:]
        uc.mem_write(src, data)
        entries.append(s['address'] | 1)  # IND_DESTINATION
        entries += [(src + off) | 8 for off in range(0, len(data), 4096)]
        src += len(data)
    entries.append(4)  # IND_DONE
    pages = [entries[i:i + 511] for i in range(0, len(entries), 511)]
    for i, page in enumerate(pages):
        if i + 1 < len(pages):
            page = page + [(0x6a010000 + (i + 1) * 4096) | 2]
        uc.mem_write(0x6a010000 + i * 4096, struct.pack('<' + 'Q' * len(page), *page))
    uc.reg_write(r.UC_ARM64_REG_X0, 0x6a010000 | 2)
    uc.reg_write(r.UC_ARM64_REG_X1, ENTRY)
    result = dict(entry_reached=False, instructions=0, error=None)

    def instruction(uc, at, size, _):
        result['instructions'] += 1
        if at == ENTRY:
            result['entry_reached'] = True
            uc.emu_stop()

    uc.hook_add(u.UC_HOOK_CODE, instruction)
    try:
        uc.emu_start(0x6a000000, 0, count=20_000_000)
    except u.UcError as e:
        result['error'] = str(e)
    result.update(indirection_pages=len(pages), segments=[
        dict(file=s['file'], bytes=len(data), exact=bytes(uc.mem_read(s['address'], len(data))) == data)
        for s, data in segments])
    result['all_destination_bytes_match'] = all(s['exact'] for s in result['segments'])
    return result


def prefix(image, dtb, syms, *, corrupt_branch=False):
    u, r, uc = cpu()
    uc.mem_map(IMAGE, 0x4000000)
    if corrupt_branch:
        image = struct.pack('<I', 0x14000000) + image[4:]  # B .
    uc.mem_write(IMAGE, image)
    uc.mem_write(META, dtb)
    uc.reg_write(r.UC_ARM64_REG_X0, META)
    names = ['primary_entry', 'record_mmu_state', 'preserve_boot_args',
             '__pi_create_init_idmap', 'init_kernel_el', '__cpu_setup',
             '__primary_switch', '__enable_mmu']
    targets = {syms[s] - syms['_text'] + IMAGE: s for s in names}
    result = dict(seen=[], instructions=0, reached_mmu_enable_entry=False, error=None)

    def instruction(uc, at, size, _):
        result['instructions'] += 1
        if at in targets:
            result['seen'].append(targets[at])
            if targets[at] == '__enable_mmu':
                result['reached_mmu_enable_entry'] = True
                uc.emu_stop()

    uc.hook_add(u.UC_HOOK_CODE, instruction)
    try:
        uc.emu_start(IMAGE, 0, count=100_000)
    except u.UcError as e:
        result['error'] = str(e)
    tcr = uc.reg_read(r.UC_ARM64_REG_CP_REG, (2, 0, 3, 0, 2))
    result.update(target_cpu='Cortex-A53', entry_el=1, mmu_enable_executed=False,
                  tcr_t0sz=tcr & 63, tcr_t1sz=(tcr >> 16) & 63,
                  tcr_ips=(tcr >> 32) & 7, tcr_ds=bool(tcr & (1 << 59)))
    return result


def run(source_build, kernel_package, bundle, nm):
    image = (kernel_package / 'Image').read_bytes()
    if sha(image) != IMAGE_SHA or sha((kernel_package / 'resolved.config').read_bytes()) != CONFIG_SHA:
        raise ValueError('Exact consumed ACK Image/config required')
    if sha((source_build / '.config').read_bytes()) != '865d9beeb5c8c49af47aea818b341e48cbbd84f7669c0cccbc589b60d1699b31':
        raise ValueError('Exact hardware-tested source config required')
    if sha((source_build / 'arch/arm64/boot/Image').read_bytes()) != 'd556acbc3edada086df0787c1922f6513182396504092248b41ca07f98d9cac3':
        raise ValueError('Exact hardware-tested source Image required')
    elf = (source_build / 'vmlinux').read_bytes()
    src_symbols = symbols(subprocess.check_output([nm, '--defined-only', str(source_build / 'vmlinux')], text=True))
    code = mapped_bytes(elf, src_symbols['arm64_relocate_new_kernel'], 4096)
    if sha(code) != '95f5e6d0a50d88adfe125ec1b09926052b862ff3992da4583e05d12b0f16fb01':
        raise ValueError('Reviewed linked relocation instructions required')
    manifest = json.loads((bundle / 'report.json').read_text())
    if manifest['entry'] != ENTRY:
        raise ValueError('Exact native metadata entry required')
    segments = []
    for s in manifest['segments']:
        data = (bundle / s['file']).read_bytes()
        if sha(data) != s['sha256'] or len(data) != s['bytes'] or len(data) > s['memory_bytes']:
            raise ValueError('Consumed segment differs')
        segments.append((s, data + bytes(s['memory_bytes'] - len(data))))
    if len(segments) != 3 or segments[0][0]['address'] != IMAGE or segments[0][1][:len(image)] != image:
        raise ValueError('Whole pinned Image in three-segment trial required')
    syms = symbols((kernel_package / 'System.map').read_text())
    dtb = (bundle / 'target-private.dtb').read_bytes()
    normal = relocate(code, segments)
    bad_copy = relocate(code, segments, corrupt_source=True)
    early = prefix(image, dtb, syms)
    bad_branch = prefix(image, dtb, syms, corrupt_branch=True)
    controls = dict(corrupted_source_detected=bad_copy['entry_reached'] and not bad_copy['all_destination_bytes_match'],
                    broken_kernel_branch_detected=not bad_branch['reached_mmu_enable_entry'])
    passed = (normal['entry_reached'] and normal['all_destination_bytes_match'] and normal['error'] is None
              and early['reached_mmu_enable_entry'] and early['error'] is None and all(controls.values()))
    return dict(scope='Offline exact-artifact full-image relocation and pre-MMU instruction audit',
                all_controls_passed=passed, hardware_execution=False, target_kernel_boot_proven=False,
                image_sha256=IMAGE_SHA, relocation_code_sha256=sha(code), relocation=normal,
                kernel_prefix=early, negative_controls=controls,
                limitations=['Synthetic disjoint source pages; actual hardware kimage page list was not recovered',
                             'No cache, coherency, DMA, firmware or real device behavior is qualified',
                             'Reset-like emulated EL1 state; actual tablet entry state was not recovered',
                             'Stops before MMU enable; MMU transition and later startup remain unqualified'])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['source-build', 'kernel-package', 'bundle', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--nm', default='aarch64-linux-musl-nm')
    a = p.parse_args()
    result = run(a.source_build, a.kernel_package, a.bundle, a.nm)
    with a.output.open('x') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
    print(json.dumps(result, indent=2))
    return 0 if result['all_controls_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
