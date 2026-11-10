#!/usr/bin/env python3
"""Build an OFFLINE entry-argument candidate; never uploads or executes it."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_image_placement import placement

# Exact six-instruction assembled template, followed by two zero literal slots.
# Validate before patching so arbitrary binary input cannot become a candidate.
CODE = struct.pack('<6I', 0x580000C0, 0xAA1F03E1, 0xAA1F03E2,
                   0xAA1F03E3, 0x58000090, 0xD61F0200)
TEMPLATE = CODE + bytes(16)
U64 = 1 << 64


def compiled_template(obj):
    """Extract only the actual ELF64 code section; reject unresolved relocations."""
    if (len(obj) < 64 or obj[:6] != b'\x7fELF\x02\x01' or
            struct.unpack_from('<HH', obj, 16) != (1, 183)):
        raise ValueError('AArch64 ELF64 relocatable object required')
    offset = struct.unpack_from('<Q', obj, 40)[0]
    stride, count, names_index = struct.unpack_from('<HHH', obj, 58)
    if stride != 64 or not count or names_index >= count or offset + count*stride > len(obj):
        raise ValueError('Invalid ELF section table')
    headers = [struct.unpack_from('<IIQQQQIIQQ', obj, offset+i*stride) for i in range(count)]
    for h in headers:
        if h[1] != 8 and h[4]+h[5] > len(obj):
            raise ValueError('ELF section outside object')
    names_header = headers[names_index]
    names = obj[names_header[4]:names_header[4]+names_header[5]]
    found = [(i, h) for i, h in enumerate(headers)
             if names[h[0]:].split(b'\0', 1)[0] == b'.text.kxentry']
    if len(found) != 1:
        raise ValueError('Exactly one trampoline section required')
    index, section = found[0]
    if any(h[1] in (4, 9) and h[7] == index and h[5] for h in headers):
        raise ValueError('Unresolved trampoline relocation')
    binary = obj[section[4]:section[4]+section[5]]
    if binary != TEMPLATE:
        raise ValueError('Assembled instructions differ from reviewed template')
    return binary


def extent(address, size, alignment):
    if (type(address) is not int or type(size) is not int or
            address <= 0 or size <= 0 or address % alignment or
            address + size >= U64):
        raise ValueError('Invalid/alignment/overflow in candidate extent')
    return address, address + size


def candidate(template, image, dtb, image_address, dtb_address, entry_address):
    if template != TEMPLATE:
        raise ValueError('Compiled trampoline differs from reviewed template')
    if len(image) < 64 or image[56:60] != b'ARMd':
        raise ValueError('Uncompressed ARM64 Image required')
    offset, size, flags = struct.unpack_from('<QQQ', image, 8)
    if flags & 1:
        raise ValueError('Big-endian Image unsupported by this candidate')
    if flags & ~0xF:
        raise ValueError('Unknown Image flags; review protocol before use')
    if not size or size < len(image):
        raise ValueError('Image declared extent missing or smaller than file')
    layout = placement(image_address, offset, size)
    if not layout['alignment_satisfied']:
        raise ValueError('Image address minus text_offset must be 2 MiB aligned')
    if len(dtb) < 40:
        raise ValueError('Truncated FDT header')
    magic, total, off_struct, off_strings, off_reserve, version, compat, _, strings, structure = struct.unpack_from('>10I', dtb)
    if (magic != 0xD00DFEED or total != len(dtb) or total > 2*1024*1024 or
            version != 17 or compat > 17 or off_struct % 4 or off_reserve % 8 or
            off_reserve < 40 or off_reserve + 16 > total or
            off_struct < 40 or structure < 4 or off_struct + structure > total or
            off_strings < 40 or off_strings + strings > total):
        raise ValueError('Unsupported or out-of-bounds FDT header')
    ranges = [extent(image_address, size, 4), extent(dtb_address, total, 8),
              extent(entry_address, len(template), 8)]
    for i, (start, end) in enumerate(ranges):
        for other_start, other_end in ranges[:i]:
            if start < other_end and other_start < end:
                raise ValueError('Image/DTB/trampoline candidate extents overlap')
    binary = CODE + struct.pack('<QQ', dtb_address, image_address)
    report = {
        'scope': 'Offline entry-argument candidate; not a boot-ready layout',
        'image_sha256': hashlib.sha256(image).hexdigest(),
        'dtb_sha256': hashlib.sha256(dtb).hexdigest(),
        'trampoline_sha256': hashlib.sha256(binary).hexdigest(),
        'entry_address': entry_address, 'image_address': image_address,
        'dtb_address': dtb_address, 'image_placement': layout,
        'trampoline_bytes': len(binary), 'instructions': 6,
        'x0': dtb_address, 'x1_x2_x3': [0, 0, 0],
        'device_execution_allowed': False,
        'checks_limited_to': 'Template, Image placement, FDT header bounds, mutual overlap',
        'unqualified': ['FDT structure/board suitability', 'RAM/reserved-memory ownership',
                        'source allocator/relocation/control-page integration',
                        'CPU parking/EL/firmware', 'cache/MMU/DMA/device shutdown',
                        'filesystem quiescing', 'target logging/independent failure recovery'],
    }
    return binary, report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['template', 'image', 'dtb', 'out']:
        p.add_argument('--'+name, type=Path, required=True)
    for name in ['image-address', 'dtb-address', 'entry-address']:
        p.add_argument('--'+name, type=lambda s: int(s, 0), required=True)
    a = p.parse_args()
    template = a.template.read_bytes()
    if template.startswith(b'\x7fELF'):
        template = compiled_template(template)
    binary, report = candidate(template, a.image.read_bytes(),
                              a.dtb.read_bytes(), a.image_address, a.dtb_address,
                              a.entry_address)
    a.out.mkdir()
    (a.out/'entry.bin').write_bytes(binary)
    (a.out/'entry-plan.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
