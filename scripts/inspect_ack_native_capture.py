#!/usr/bin/env python3
"""Assess complete or interrupted ACK PID1 wire evidence without raw output."""
import hashlib
import re
import struct
from kernel_log_protocol import MAGIC, MAX_RECORD, MAX_TOTAL


def inspect(raw, nonce, release):
    result = dict(identity_verified=False, complete_records=0, terminal_frame=False,
                  kernel_release_seen=False, target_cmdline_nonce_seen=False,
                  target_kernel_boot_proven=False, target_pid1_proven=False,
                  capture_sha256=hashlib.sha256(raw).hexdigest(), capture_bytes=len(raw))
    if len(nonce) != 32 or not any(nonce) or not re.fullmatch('[A-Za-z0-9._+-]{1,128}', release):
        raise ValueError('Exact PID1 nonce/release required')
    if len(raw) < 40:
        return result
    if raw[:40] != MAGIC + nonce:
        raise ValueError('PID1 wire identity differs')
    result['identity_verified'] = True
    at, total, sequence = 40, 0, 0
    previous = None
    while len(raw) - at >= 8:
        index, size = struct.unpack_from('>II', raw, at)
        if index != sequence or size > MAX_RECORD or total + size > MAX_TOTAL:
            raise ValueError('PID1 wire framing/bounds differ')
        if len(raw) - at - 8 < size:
            break
        at += 8
        if size == 0:
            if at != len(raw):
                raise ValueError('Unreviewed wire tail')
            result['terminal_frame'] = True
            break
        record = raw[at:at + size]; at += size
        m = re.match(rb'([0-9]{1,3}),([0-9]{1,20}),([0-9]{1,20}),([^;\n]{1,8});', record)
        if not m or not record.endswith(b'\n') or int(m[1]) > 191:
            raise ValueError('Invalid /dev/kmsg record')
        number, timestamp = int(m[2]), int(m[3])
        if previous and (number != previous[0] + 1 or timestamp < previous[1]):
            raise ValueError('Lost or nonmonotonic kernel records')
        previous = number, timestamp
        message = record[m.end():].split(b'\n', 1)[0]
        if int(m[1]) < 8:
            if message.startswith(b'Linux version '):
                if not message.startswith(b'Linux version ' + release.encode() + b' '):
                    raise ValueError('Actual kernel release differs')
                result['kernel_release_seen'] = True
            if (message.startswith(b'Kernel command line: ') and
                    b'valethon.native_trial=' + nonce.hex().encode() in message):
                result['target_cmdline_nonce_seen'] = True
        sequence += 1; total += size
    result.update(complete_records=sequence, payload_bytes=total)
    proven = result['kernel_release_seen'] and result['target_cmdline_nonce_seen']
    result.update(target_kernel_boot_proven=proven, target_pid1_proven=proven,
                  interrupted_tail_bytes=len(raw) - at)
    # Physical port selection remains a separate required caller-side check.
    return result
