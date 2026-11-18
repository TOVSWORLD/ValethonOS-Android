#!/usr/bin/env python3
"""Strict functional storage status decoder; independent of kernel-log protocol."""
import hmac
import struct

MAGIC = b'VSTORE01'
PACKET_BYTES = 120
BOOT_BYTES = 16 * 1024 * 1024
BOOT_SHA256 = '08fcf3455d66943632d0fc91348d4ab7d41b80c40d88e61272000a1d697faa1e'


def decode(packet, nonce):
    if len(packet) != PACKET_BYTES or len(nonce) != 32:
        raise ValueError('Exact status packet and fresh 32-byte identity required')
    if packet[:8] != MAGIC or not hmac.compare_digest(packet[8:40], nonce):
        raise ValueError('Wrong protocol or trial identity')
    version, stage, error, flags, read, size, reserved, major, minor = struct.unpack_from('<IIiIQQQII', packet, 40)
    digest = packet[88:120]
    if version != 1 or not 1 <= stage <= 5 or error > 0 or flags & ~31 or not flags & 1:
        raise ValueError('Invalid storage status fields')
    if size != BOOT_BYTES or read > size or reserved or (major, minor) != (179, 5):
        raise ValueError('Wrong fixed boot partition contract')
    if flags not in (1, 3, 7, 15, 31):
        raise ValueError('Nonsequential storage verification flags')
    if (flags & 8 and read != size) or (flags & 16 and digest.hex() != BOOT_SHA256):
        raise ValueError('Inconsistent verification result')
    if not flags & 16 and any(digest):
        raise ValueError('Unverified digest must be empty')
    if stage != {1: 1, 3: 2, 7: 3, 15: 4, 31: 5}[flags]:
        raise ValueError('Inconsistent storage stage')
    passed = error == 0 and flags == 31 and read == size
    if not error and not passed:
        raise ValueError('Success without complete read-only verification')
    return {'protocol': 'VSTORE01', 'storage_readonly_verified': passed,
            'stage': stage, 'error': error, 'flags': flags, 'bytes_read': read,
            'boot_partition_bytes': size, 'verified_expected_sha256': digest.hex() if flags & 16 else None,
            'block_writes_requested': False, 'userdata_mounted': False,
            'kernel_log_transfer_required': False}


def receive_fd(port, raw, nonce, deadline):
    """Receive one bounded packet, durably save it, and send no protocol ACK."""
    import os
    import select
    import time
    data = bytearray()
    while len(data) < PACKET_BYTES:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError('Storage status deadline expired')
        readable, _, _ = select.select([port], [], [], remaining)
        if not readable:
            raise TimeoutError('Storage status deadline expired')
        try:
            chunk = os.read(port, PACKET_BYTES - len(data))
        except (BlockingIOError, InterruptedError):
            continue
        if not chunk:
            raise ValueError('Disconnected before complete storage status')
        offset = 0
        while offset < len(chunk):
            written = os.write(raw, chunk[offset:])
            if written <= 0:
                raise OSError('Cannot preserve storage status')
            offset += written
        data.extend(chunk)
    os.fsync(raw)
    result = decode(bytes(data), nonce)
    # A complete functional failure packet is still a complete transport result.
    # Storage acceptance is always the explicit storage_readonly_verified field.
    result.update(complete=True, device_qualified=False, status_bytes=len(data))
    return result
