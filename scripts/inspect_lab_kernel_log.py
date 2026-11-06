#!/usr/bin/env python3
"""Inspect retained private wire capture without printing kernel records or identifiers."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
from kernel_log_protocol import MAGIC, MAX_RECORD, MAX_TOTAL
from capture_lab_kernel_log import private_bytes


def inspect(data, nonce, expected_release):
    if (len(nonce) != 32 or not any(nonce) or data[:40] != MAGIC + nonce
            or not re.fullmatch(r'[A-Za-z0-9._+-]{1,128}', expected_release)):
        raise ValueError('Exact private identity/release required')
    offset = 40
    sequence = 0
    total = 0
    first = None
    previous = None
    version_seen = False
    while True:
        if len(data) - offset < 8:
            raise ValueError('Incomplete retained frame')
        number, size = struct.unpack_from('>II', data, offset)
        offset += 8
        if number != sequence or size > MAX_RECORD or total + size > MAX_TOTAL or offset + size > len(data):
            raise ValueError('Retained sequence/extent violation')
        if size == 0:
            if offset != len(data) or not sequence:
                raise ValueError('Empty capture or unreviewed tail')
            break
        record = data[offset:offset + size]
        offset += size
        total += size
        sequence += 1
        match = re.match(rb'([0-9]{1,3}),([0-9]{1,20}),([0-9]{1,20}),([^;\n]{1,8});', record)
        if not match or not record.endswith(b'\n') or int(match[1]) > 191:
            raise ValueError('Invalid Linux kmsg record')
        number, timestamp = int(match[2]), int(match[3])
        if first is None:
            first = number
        if previous and (number != previous[0] + 1 or timestamp < previous[1]):
            raise ValueError('Kernel record loss or nonmonotonic timestamp')
        previous = (number, timestamp)
        message = record[match.end():].split(b'\n', 1)[0]
        if message.startswith(b'Linux version '):
            if not message.startswith(b'Linux version ' + expected_release.encode() + b' '):
                raise ValueError('Kernel release differs from exact build')
            version_seen = True
    return {'wire_complete': True, 'records': sequence, 'payload_bytes': total,
            'wire_sha256': hashlib.sha256(data).hexdigest(), 'first_kmsg_sequence': first,
            'kernel_release_seen': version_seen,
            'initial_kernel_prefix_captured': first == 0 and version_seen,
            'failed_load_qualified': False, 'independent_return_qualified': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--raw', type=Path, required=True)
    p.add_argument('--nonce', type=Path, required=True)
    p.add_argument('--kernel-release', required=True)
    a = p.parse_args()
    try:
        result = inspect(private_bytes(a.raw, MAX_TOTAL + 8 * MAX_TOTAL + 48),
                         private_bytes(a.nonce, 32), a.kernel_release)
        print(json.dumps(result, indent=2))
    except (ValueError, OSError):
        p.exit(2, 'Private retained kernel log did not pass inspection.\n')


if __name__ == '__main__':
    main()
