#!/usr/bin/env python3
"""Build the reviewed, deadline-bounded maintained-kernel entry stub offline."""
import hashlib
import re
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'projects/firetabs-android/native-kexec/ack_trampoline.S'


def marker(token):
    if not isinstance(token, str) or not re.fullmatch('[0-9a-f]{32}', token):
        raise ValueError('Fresh lowercase 128-bit handoff token required')
    return b'FIRETABS_ACK_HANDOFF_V1 nonce=' + token.encode() + b'\n'


def extract(raw):
    if len(raw) < 64 or raw[:6] != b'\x7fELF\x02\x01' or struct.unpack_from('<HH', raw, 16) != (1, 183):
        raise ValueError('AArch64 relocatable required')
    at = struct.unpack_from('<Q', raw, 40)[0]
    stride, count, names_index = struct.unpack_from('<HHH', raw, 58)
    if stride != 64 or not count or names_index >= count or at + count * stride > len(raw):
        raise ValueError('Invalid section table')
    sections = [struct.unpack_from('<IIQQQQIIQQ', raw, at + i * stride) for i in range(count)]
    for s in sections:
        if s[1] != 8 and s[4] + s[5] > len(raw):
            raise ValueError('Section outside object')
    s = sections[names_index]; names = raw[s[4]:s[4] + s[5]]
    found = [(i, s) for i, s in enumerate(sections)
             if names[s[0]:].split(b'\0', 1)[0] == b'.text.ack_trampoline']
    if len(found) != 1:
        raise ValueError('Unique ACK entry section required')
    i, s = found[0]
    if any(r[1] in (4, 9) and r[7] == i and r[5] for r in sections):
        raise ValueError('Unresolved entry relocation')
    data = raw[s[4]:s[4] + s[5]]
    if not 128 < len(data) < 4096:
        raise ValueError('One-page entry stub required')
    return data


def build(out, token, compiler='clang'):
    line = marker(token)
    out.mkdir(mode=0o700)
    (out / 'ack_marker.inc').write_text('.ascii "' + line[:-1].decode() + '\\n"\n')
    obj = out / 'ack_trampoline.o'
    subprocess.run([compiler, '-target', 'aarch64-none-elf', '-c', str(SOURCE),
                    '-Wa,-I,' + str(out.resolve()), '-o', str(obj)], check=True)
    data = extract(obj.read_bytes())
    if data.count(line) != 1:
        raise ValueError('Unique handoff marker required')
    (out / 'trampoline.bin').write_bytes(data)
    return data, dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                      source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                      deadline_seconds=31, image_entry=0x40000000, fdt=0x42000000,
                      marker_proves='Entry stub and deadline readback only; not Linux boot',
                      hardware_deadline_qualified=False)
