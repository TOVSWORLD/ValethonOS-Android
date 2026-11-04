#!/usr/bin/env python3
"""Execute pinned archived resident payload in simulated RAM, never on a device.

Requires unicorn 2.1.3. Firmware services are modeled; this is bounded behavioral
correspondence to cached source, not a reproducible-build or runtime identity proof.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zipfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7, UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11

BASE = 0x4bcff000
SHA = 'e10fdf770a5be2c2adc3cce0d03b8e296eac3b31e18ebdce5b56dc5491f4e7e8'
SOURCE_SHA = {'start.S': '0eb60174b7fc6ac66a6f78d99ca9e9f0ddee3a1fc47b5b742c4ded552d8b69dc', 'main.c': 'a98172b957fce059ffc1d05dc1da5647add14cec6a0eaf5300ad2b1b3224f30f', 'common.h': 'a74dde370000f9aa800628dddb8c6cd15d603384f9e906bfa718fe665d90f4ee', 'libc.c': '09219f68e6d5569df43a703f24fb6bc72a38fec86be4634a7beda5149c6af322', 'libc.h': '14396fdbda583ebbe4f2c9c91ba3cc39fee0f4607f5c1dfe0eb506b88d92bbe0', 'linker.x': '8676e54b20b029516275d19f22ec8a25c619b880c5ef0e038c3986540f787484', 'Makefile': 'bdb58deceecedf165f3d6a818c28133e2c3333d32eca9304041b1dc0cdbc136b'}
GLOBALS = {'g_recovery_x': 0xb88, 'g_boot': 0xb90, 'g_misc': 0xb98,
           'g_lk': 0xba0, 'g_boot_x': 0xba8, 'g_recovery': 0xbb0}
SECTORS = {'boot': 0x1000, 'boot_x': 0x2000, 'lk': 0x3000, 'MISC': 0x4000,
           'recovery': 0x5000, 'recovery_x': 0x6000}
DEVICE, READ, WRITE, STOP = 0x50000000, 0x50001000, 0x50002000, 0x50003000
REGS = [UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3]


def payload(path):
    with zipfile.ZipFile(path) as archive:
        data = archive.read('amonet/bin/boot.payload')
        lk = archive.read('amonet/bin/lk.bin')
    if hashlib.sha256(data).hexdigest() != SHA or len(data) != 492132:
        raise ValueError('Exact archived boot.payload required')
    if hashlib.sha256(lk).hexdigest() != '7637da8754a7494f8907d07c7b25532476959956d1cfea856ab8ea6940176056':
        raise ValueError('Original package LK mismatch')
    embedded = data[0x1800:]
    changes = [i for i, (x, y) in enumerate(zip(embedded, lk)) if x != y]
    assert len(embedded) == len(lk) and changes == list(range(0x5c0, 0x5c8))
    resident = data[0xa00:0x1800]
    assert resident[:8].hex() == '42d4a0e39e0000fa'
    assert resident[0xb84:] == bytes(0x27c)
    # Every BSS pointer occurs in the pinned code's literal pools; zero bytes
    # alone would miss these six live 64-bit variables after initialized data.
    for offset in GLOBALS.values():
        assert struct.pack('<I', BASE + offset) in resident[:0x830]
    return resident


def machine(resident, original_mode=0, lk_mode=0, flag=b'', missing=None):
    uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    uc.mem_map(0x4bcf0000, 0x180000)
    uc.mem_map(0x41fe0000, 0x20000)
    uc.mem_map(DEVICE, 0x10000)
    uc.mem_write(BASE, resident)
    uc.mem_write(DEVICE + 0x10, struct.pack('<II', READ | 1, WRITE | 1))
    uc.mem_write(0x4be5e20c, struct.pack('<I', original_mode))
    uc.mem_write(0x4bd7c3a0, struct.pack('<I', lk_mode))
    gpt = bytearray(0x1000)
    for i, (name, sector) in enumerate(SECTORS.items()):
        if name == missing:
            continue
        struct.pack_into('<I', gpt, i * 0x80 + 0x20, sector)
        encoded = name.encode('utf-16le') + b'\0\0'
        gpt[i*0x80+0x38:i*0x80+0x38+len(encoded)] = encoded
    state = {'reads': [], 'writes': [], 'resident_write_end': 0, 'app': False}
    def word(addr): return struct.unpack('<I', uc.mem_read(addr, 4))[0]
    def ret(value=0):
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
    def hook(u, addr, size, opaque):
        if addr in [BASE + 0x736, 0x4bd44b3c, 0x4bd3c740]:
            ret(); return
        if addr == 0x4bd35e40:
            ret(DEVICE); return
        if addr in [READ, 0x4bd358e8]:
            offset = uc.reg_read(UC_ARM_REG_R2) | (uc.reg_read(UC_ARM_REG_R3) << 32)
            sp = uc.reg_read(UC_ARM_REG_SP)
            dst, count, part = struct.unpack('<III', uc.mem_read(sp, 12))
            state['reads'].append([offset, count, part])
            if offset == 0x400 and count == 0x1000:
                uc.mem_write(dst, bytes(gpt))
            elif offset == SECTORS['MISC'] * 512 and count == 32:
                uc.mem_write(dst, flag.ljust(32, b'\0'))
            ret(count); return
        if addr == WRITE:
            sp = uc.reg_read(UC_ARM_REG_SP)
            count, part = struct.unpack('<II', uc.mem_read(sp, 8))
            state['writes'].append([uc.reg_read(UC_ARM_REG_R2), count, part])
            ret(count); return
        if addr in [0x4bd3f1a0, STOP]:
            state['app'] = addr == 0x4bd3f1a0
            uc.emu_stop()
    def written(u, access, addr, size, value, opaque):
        if BASE <= addr < BASE + 0xe00:
            state['resident_write_end'] = max(state['resident_write_end'], addr + size - BASE)
    uc.hook_add(UC_HOOK_CODE, hook)
    uc.hook_add(UC_HOOK_MEM_WRITE, written)
    return uc, state, word


def audit(resident, source):
    actual_source = {name: hashlib.sha256((source/name).read_bytes()).hexdigest() for name in SOURCE_SHA}
    if actual_source != SOURCE_SHA:
        raise ValueError("Cached source drift; correspondence review required")
    cases = []
    for label, original, mode, flag, missing, expected, writes in [
        ('normal', 0, 0, b'', None, 0, 0),
        ('recovery', 0, 2, b'', None, 2, 0),
        ('factory', 4, 0, b'', None, 99, 0),
        ('advanced_factory', 6, 0, b'', None, 2, 0),
        ('temporary_fastboot_flag', 0, 0, b'boot-amonet', None, 99, 1),
        ('permanent_fastboot_flag', 0, 0, b'FASTBOOT_PLEASE', None, 99, 0),
        ('permanent_flag_recovery', 0, 2, b'FASTBOOT_PLEASE', None, 2, 1),
        ('recovery_flag', 0, 0, b'boot-recovery', None, 2, 1),
        ('missing_boot_x', 0, 0, b'', 'boot_x', 99, 0),
    ]:
        uc, state, word = machine(resident, original, mode, flag, missing)
        uc.emu_start(BASE, STOP, timeout=2000000, count=250000)
        assert state['app'] and word(0x4bd7c3a0) == expected, label
        assert len(state['writes']) == writes, label
        assert word(DEVICE + 0x10) == BASE + 9
        assert word(0x4bd7655c) == BASE + 9
        for name, offset in GLOBALS.items():
            sector = SECTORS['MISC' if name == 'g_misc' else name[2:]]
            assert word(BASE + offset) == (0 if name[2:] == missing else sector), name
            assert word(BASE + offset + 4) == 0
        assert state['resident_write_end'] <= 0xbb8
        cases.append({'case': label, 'selected_lk_mode': expected, 'modeled_misc_writes': writes})
    redirects = []
    for name, target in [('boot', 'boot_x'), ('recovery', 'recovery_x'), ('lk', 'lk')]:
        for extra in [0, 0x800, 0x1000, 0x100000000]:
            uc, state, word = machine(resident)
            for key, off in GLOBALS.items():
                sector = SECTORS['MISC' if key == 'g_misc' else key[2:]]
                uc.mem_write(BASE + off, struct.pack('<Q', sector))
            sp = 0x41fff000
            requested = SECTORS[name] * 512 + extra
            for reg, value in zip(REGS, [DEVICE, 0xdeadbeef, requested & 0xffffffff, requested >> 32]):
                uc.reg_write(reg, value)
            saved_regs = [UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7, UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11]
            for i, reg in enumerate(saved_regs): uc.reg_write(reg, 0x12340000+i)
            uc.reg_write(UC_ARM_REG_SP, sp)
            uc.mem_write(sp, struct.pack('<III', DEVICE + 0x4000, 2048, 8))
            uc.reg_write(UC_ARM_REG_LR, STOP | 1)
            uc.emu_start(BASE + 9, STOP, timeout=2000000, count=20000)
            expected = SECTORS[target if extra in [0, 0x800] else name] * 512 + extra
            assert state['reads'] == [[expected, 2048, 8]]
            assert all(uc.reg_read(reg) == 0x12340000+i for i, reg in enumerate(saved_regs))
            assert uc.reg_read(UC_ARM_REG_SP) == sp
            assert uc.reg_read(UC_ARM_REG_R0) == 2048
            assert not state['writes']
            redirects.append({'partition': name, 'offset': extra, 'redirected': expected != requested})
    return {'scope': 'Pinned archived resident instructions in emulated RAM with modeled firmware services; no device access',
            'archive_payload_sha256': SHA, 'emulator_version': __import__('unicorn').__version__,
            'cached_source_sha256': actual_source, 'source_correspondence': 'Bounded mode/read/global behavior agrees with cached source; exact compiler/build equivalence NOT established',
            'main_cases': cases, 'read_cases': redirects, 'resident_base': hex(BASE),
            'initialized_bytes_end_exclusive': '0x4bcffb84',
            'bss_alignment_padding': ['0x4bcffb84', '0x4bcffb88'],
            'referenced_bss_globals': {k: hex(BASE+v) for k,v in GLOBALS.items()},
            'observed_bss_end_exclusive': '0x4bcffbb8',
            'remaining_zero_tail_bytes': 0xe00-0xbb8,
            'tail_is_admitted_injection_space': False,
            'embedded_lk_prefix_start': '0x4bcffe00',
            'next_baseline_decision': 'Use exact archived binary as observation-design baseline; do not claim reproducible original source build or use a rebuilt original as equivalent.',
            'exact_reproducible_build': False, 'device_written': False,
            'hardware_qualified': False, 'observer_prepared': False}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1]/'sources/reference-amonet-douglas/lk-payload')
    args = p.parse_args()
    result = audit(payload(args.archive), args.source)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print('Archived resident mode/read/global controls passed; no hardware action')
