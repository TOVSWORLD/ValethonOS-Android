#!/usr/bin/env python3
"""Verify the compiled no-handoff probe. This command never accesses a device."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

RELEASE = '4.9.337-g72940eb733af'
ALLOWED_IMPORTS = {'printk', 'kallsyms_lookup_name', 'init_uts_ns', '__cpu_online_mask',
                   '__stack_chk_fail', '__stack_chk_guard', '__bitmap_weight', '__sw_hweight64', 'nr_cpu_ids'}

def inspect_module(data):
    if len(data) < 64 or data[:6] != b'\x7fELF\x02\x01':
        raise ValueError('Little-endian ELF64 required')
    if struct.unpack_from('<HH', data, 16) != (1, 183):
        raise ValueError('Relocatable AArch64 module required')
    off = struct.unpack_from('<Q', data, 40)[0]
    stride, count, strings = struct.unpack_from('<HHH', data, 58)
    if stride != 64 or not count or strings >= count or off + count * stride > len(data):
        raise ValueError('Invalid section table')
    headers = [struct.unpack_from('<IIQQQQIIQQ', data, off + i * stride) for i in range(count)]
    def section(h):
        if h[1] == 8:
            return b''
        if h[4] + h[5] > len(data):
            raise ValueError('Truncated section')
        return data[h[4]:h[4]+h[5]]
    names = section(headers[strings])
    def string(blob, at):
        if at >= len(blob) or b'\0' not in blob[at:]:
            raise ValueError('Invalid string table reference')
        return blob[at:].split(b'\0', 1)[0].decode('ascii')
    sections = {string(names, h[0]): section(h) for h in headers}
    imported = set()
    for h in headers:
        if h[1] != 2:
            continue
        if h[9] != 24 or h[5] % 24 or h[6] >= count:
            raise ValueError('Invalid symbol table')
        symbols = section(h)
        symbols_names = section(headers[h[6]])
        for at in range(0, len(symbols), 24):
            name, info, _, index, _, _ = struct.unpack_from('<IBBHQQ', symbols, at)
            if index == 0 and name and info >> 4 in (1, 2):
                imported.add(string(symbols_names, name))
    meta = {}
    for item in sections.get('.modinfo', b'').split(b'\0'):
        if b'=' in item:
            key, value = item.split(b'=', 1)
            meta[key.decode()] = value.decode()
    versions = {}
    raw = sections.get('__versions', b'')
    if len(raw) % 64:
        raise ValueError('Invalid ARM64 module version table')
    for at in range(0, len(raw), 64):
        name = raw[at+8:at+64].split(b'\0', 1)[0].decode()
        if not name or name in versions:
            raise ValueError('Invalid or duplicate version symbol')
        versions[name] = struct.unpack_from('<Q', raw, at)[0]
    return imported, meta, versions


def verify(module, symvers):
    data = module.read_bytes()
    imported, meta, versions = inspect_module(data)
    if imported - ALLOWED_IMPORTS:
        raise ValueError('Unexpected imports: ' + ', '.join(sorted(imported - ALLOWED_IMPORTS)))
    magic = meta.get('vermagic', '').split()
    if not magic or magic[0] != RELEASE or not {'SMP', 'preempt', 'mod_unload', 'modversions', 'aarch64'} <= set(magic):
        raise ValueError('Wrong kernel release or module ABI flags')
    provider = {}
    for line in symvers.read_text().splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[2] == 'vmlinux':
            provider[fields[1]] = int(fields[0], 16)
    required = imported | {'module_layout'}
    if not required <= versions.keys():
        raise ValueError('Missing module CRCs: ' + ', '.join(sorted(required - versions.keys())))
    for name in required:
        if name not in provider or versions[name] != provider[name]:
            raise ValueError('Kernel symbol CRC mismatch: ' + name)
    return {'scope': 'Compiled probe import/release/source-generated CRC verification; not hardware execution',
            'module_sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
            'vermagic': meta['vermagic'], 'imports': sorted(imported),
            'versioned_symbols': sorted(required), 'all_required_crcs_match_provider': True,
            'target_release': RELEASE, 'current_twrp_compatible': False,
            'loaded_on_tablet': False, 'handoff_attempted': False,
            'target_runtime_abi_verified': False, 'physical_test_admitted': False}

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--module', type=Path, required=True)
    p.add_argument('--symvers', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    r = verify(a.module, a.symvers)
    a.output.write_text(json.dumps(r, indent=2) + '\n')
    print(json.dumps(r, indent=2))
