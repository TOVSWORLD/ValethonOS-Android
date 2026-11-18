#!/usr/bin/env python3
"""Offline integrity/boot-record assessment; never admits a physical test.

A valid byte stream alone cannot establish its physical origin. This assessor
keeps device_qualified=False even when framing and a matching kernel record pass.
No raw payload, nonce, USB identity or full kernel build banner is returned.
"""
import argparse
import hashlib
import io
import json
import os
import re
import struct
import tempfile
from pathlib import Path
from capture_lab_kernel_log import private_bytes
from kernel_log_protocol import receive, MAX_TOTAL

MAX_WIRE = 40 + 9 * MAX_TOTAL + 8


def assess(raw, nonce, receipt, release):
    if (not isinstance(raw, bytes) or not 48 <= len(raw) <= MAX_WIRE
            or not re.fullmatch(r'[A-Za-z0-9_.+\-]{1,128}', release)):
        raise ValueError('Bounded wire capture and exact expected release required')
    if (receipt.get('complete') is not True or receipt.get('failure') is not None
            or receipt.get('cleanup') != []):
        raise ValueError('Successful complete capture receipt required')
    source = io.BytesIO(raw)
    # Exercise the existing receiver, including identity, frame ordering, bounds
    # and terminal frame. ACKs are discarded locally; no transport is opened.
    with tempfile.TemporaryFile() as output:
        os.fchmod(output.fileno(), 0o600)
        result = receive(source.read, lambda data: None, output.fileno(), nonce, 1, clock=lambda: 0)
    if source.read(1):
        raise ValueError('Trailing capture bytes forbidden')
    for key in ['records', 'payload_bytes', 'wire_sha256']:
        if receipt.get(key) != result[key]:
            raise ValueError('Capture receipt and exact wire bytes differ')
    if not result['records']:
        raise ValueError('Empty terminal capture is not kernel evidence')
    # /dev/kmsg priority has facility in the upper bits. Only facility0 boot
    # records count; a userspace echo of Linux version is insufficient.
    offset = 40
    boot_records = 0
    for _ in range(result['records']):
        _, length = struct.unpack_from('>II', raw, offset)
        payload = raw[offset+8:offset+8+length]
        offset += 8 + length
        match = re.fullmatch(rb'([0-9]{1,3}),[0-9]+,[0-9]+,[^;\n]*;Linux version ([^\s\x00]+)[^\x00]*', payload)
        if match and int(match[1]) < 8:
            if match[2] != release.encode('ascii'):
                raise ValueError('Kernel boot record release differs')
            boot_records += 1
    if not boot_records:
        raise ValueError('Matching kernel-facility boot record absent')
    return {**result, 'matching_kernel_boot_record': True,
            'physical_origin_verified': False, 'test_admission': False,
            'nonce_sha256': hashlib.sha256(nonce).hexdigest(),
            'scope': 'Offline capture integrity only; physical provenance requires independent evidence'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['raw', 'nonce', 'receipt']:
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--release', required=True)
    args = parser.parse_args()
    try:
        result = assess(private_bytes(args.raw, MAX_WIRE), private_bytes(args.nonce, 32),
                        json.loads(private_bytes(args.receipt, 65536)), args.release)
    except (ValueError, OSError, KeyError):
        parser.exit(2, 'Capture not accepted as complete matching kernel evidence.\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
