#!/usr/bin/env python3
"""Build an offline, nonce-attributed reset target; never upload or execute."""
import argparse
import hashlib
import json
import re
import secrets
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'projects/firetabs-android/native-kexec/reset_payload.S'
GEOMETRY = dict(mem_address=0x44410000, mem_size=0xe0000, record_size=4096,
                console_size=65536, ftrace_size=4096, pmsg_size=65536, ecc=0, mem_type=0)
CONSOLE = 0x444bf000
CAPACITY = 65524
PREFIX = b'FIRETABS_TARGET_RESET_V1 nonce='
QUALIFIED_NONCE = '0123456789abcdef0123456789abcdef'
QUALIFIED_IMAGE_SHA = '29f649cff58c4ace942897eaab1f906f5c5adb1f419cb288b666a3238e915aff'


def marker(nonce):
    if not isinstance(nonce, str) or not re.fullmatch('[0-9a-f]{32}', nonce):
        raise ValueError('Fresh 128-bit lowercase hexadecimal nonce required')
    return PREFIX + nonce.encode() + b'\n'


def extract(raw):
    if len(raw) < 64 or raw[:6] != b'\x7fELF\x02\x01' or struct.unpack_from('<HH', raw, 16) != (1, 183):
        raise ValueError('AArch64 ELF64 relocatable required')
    at = struct.unpack_from('<Q', raw, 40)[0]
    stride, count, names_index = struct.unpack_from('<HHH', raw, 58)
    if stride != 64 or not count or names_index >= count or at + stride * count > len(raw):
        raise ValueError('Invalid section table')
    sections = [struct.unpack_from('<IIQQQQIIQQ', raw, at + i * stride) for i in range(count)]
    for s in sections:
        if s[1] != 8 and s[4] + s[5] > len(raw):
            raise ValueError('Section outside file')
    s = sections[names_index]
    names = raw[s[4]:s[4] + s[5]]
    found = [(i, s) for i, s in enumerate(sections)
             if names[s[0]:].split(b'\0', 1)[0] == b'.text.reset_payload']
    if len(found) != 1:
        raise ValueError('Unique reset code section required')
    i, s = found[0]
    if any(s2[1] in (4, 9) and s2[7] == i and s2[5] for s2 in sections):
        raise ValueError('Unresolved reset-payload relocation')
    data = raw[s[4]:s[4] + s[5]]
    if not 64 < len(data) <= 4096 or data[:4] != struct.pack('<I', 0x14000010):
        raise ValueError('Unexpected reset Image entry')
    if struct.unpack_from('<QQQ', data, 8) != (0x80000, 4096, 10) or data[56:60] != b'ARMd':
        raise ValueError('Unexpected reset Image header')
    return data.ljust(4096, b'\0')


def validate(image, report):
    line = marker(report['nonce'])
    if len(image) != 4096 or image.count(line) != 1:
        raise ValueError('Exact one-page nonce-bearing reset Image required')
    if report['geometry'] != GEOMETRY or report['console_address'] != CONSOLE or report['console_capacity'] != CAPACITY:
        raise ValueError('Reviewed ECC-free retained-console geometry required')
    if report['image_sha256'] != hashlib.sha256(image).hexdigest() or report['source_sha256'] != hashlib.sha256(SOURCE.read_bytes()).hexdigest():
        raise ValueError('Exact reset image/source required')
    canonical = image.replace(line, marker(QUALIFIED_NONCE))
    if hashlib.sha256(canonical).hexdigest() != QUALIFIED_IMAGE_SHA:
        raise ValueError('Payload differs from instruction-qualified code outside its nonce')
    return line


def build(out, nonce=None, compiler='clang'):
    nonce = nonce or secrets.token_hex(16)
    line = marker(nonce)
    out.mkdir(mode=0o700)
    (out / 'reset_marker.inc').write_text('.ascii "' + line[:-1].decode() + '\\n"\n')
    obj = out / 'reset_payload.o'
    subprocess.run([compiler, '-target', 'aarch64-none-elf', '-c', str(SOURCE),
                    '-Wa,-I,' + str(out.resolve()), '-o', str(obj)], check=True)
    image = extract(obj.read_bytes())
    if image.count(line) != 1:
        raise ValueError('Unique exact target-only marker required')
    (out / 'Image').write_bytes(image)
    report = dict(scope='Minimal reset target; not a Linux kernel or hardware qualification',
                  nonce=nonce, marker=line.decode(), geometry=GEOMETRY,
                  console_address=CONSOLE, console_capacity=CAPACITY,
                  image_sha256=hashlib.sha256(image).hexdigest(),
                  source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  image_bytes=4096, linux_boot_proven=False, hardware_execution=False,
                  writes=['Existing retained-console data and start/size counters',
                          'WDT_MODE normal restart policy', 'WDT_SWRST normal reset key'],
                  success_requires=['Exact target-only marker recovered after jump',
                                    'Fresh boot identity', 'Automatic return without owner Power',
                                    'Original full boot/config and unchanged recovery verified'],
                  invalid_ring_policy='Reset without marker; result is inconclusive',
                  failure_policy='No automatic retry; pivot to broader boot-strategy review')
    validate(image, report)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--nonce')
    p.add_argument('--compiler', default='clang')
    a = p.parse_args()
    r = build(a.out, a.nonce, a.compiler)
    print(json.dumps({k: r[k] for k in ['scope', 'image_sha256', 'image_bytes', 'hardware_execution']}))
