#!/usr/bin/env python3
"""Offline persistent-log format and regular-file I/O. No device-write admission.

Proposed experimental p5 tail only. A device writer/storage contract is deliberately
not inferred from fixture success. The read CLI rejects block devices and symlinks.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import struct
import zlib

PARTITION = 16 * 1024 * 1024
BASE = 15 * 1024 * 1024
SEED = 4096
SLOT = 127 * 4096
SLOT_BASE = BASE + SEED
GUARD = SLOT_BASE + 2 * SLOT
HEADER = 4096
CAPACITY = SLOT - HEADER
MAGIC = b'VLOG0001'
FORMAT = struct.Struct('<8sIIQ32sIII')
CRC_OFFSET = FORMAT.size - 4


def prepare(image, nonce, control_record=None):
    if len(image) != PARTITION or any(image[BASE:]) or len(nonce) != 32 or not any(nonce):
        raise ValueError('Exact candidate with empty tail and fresh nonce required')
    prefix = hashlib.sha256(image[:BASE]).digest()
    seed = bytearray(SEED)
    seed[:8] = b'VSEED001'; seed[8:40] = nonce; seed[40:72] = prefix
    struct.pack_into('<I', seed, 72, zlib.crc32(seed))
    result = image[:BASE] + bytes(seed) + bytes(PARTITION-BASE-SEED)
    if control_record is not None:
        if not control_record.startswith(b'VALETHON HOST CONTROL v1\n'):
            raise ValueError('Control record must identify host producer')
        record = header(1, nonce, control_record) + control_record
        result = result[:SLOT_BASE] + record + result[SLOT_BASE+len(record):]
    return result, prefix.hex()


def validate_seed(image, nonce, prefix_sha256):
    seed = bytearray(image[BASE:SLOT_BASE])
    if len(seed) != SEED or seed[:8] != b'VSEED001' or seed[8:40] != nonce or seed[40:72].hex() != prefix_sha256:
        raise ValueError('Candidate seed binding differs')
    crc = struct.unpack_from('<I', seed, 72)[0]; struct.pack_into('<I', seed, 72, 0)
    if zlib.crc32(seed) != crc or any(seed[76:]) or any(image[GUARD:]):
        raise ValueError('Seed checksum/padding or final guard differs')


def header(sequence, nonce, payload):
    if not 0 < sequence < 2**64 or len(nonce) != 32 or not any(nonce):
        raise ValueError('Invalid sequence/nonce')
    if not payload or len(payload) > CAPACITY:
        raise ValueError('Payload outside slot bounds')
    data = bytearray(HEADER)
    FORMAT.pack_into(data, 0, MAGIC, 1, HEADER, sequence, nonce, len(payload),
                     zlib.crc32(payload), 0)
    struct.pack_into('<I', data, CRC_OFFSET, zlib.crc32(data))
    return bytes(data)


def decode(slot, nonce):
    if len(slot) != SLOT or len(nonce) != 32:
        raise ValueError('Exact slot/nonce required')
    if not any(slot):
        return None
    magic, version, hs, sequence, recorded, used, crc, hc = FORMAT.unpack_from(slot)
    if magic != MAGIC or version != 1 or hs != HEADER or not sequence or recorded != nonce:
        raise ValueError('Foreign/stale/incomplete header')
    if not 0 < used <= CAPACITY or any(slot[FORMAT.size:HEADER]):
        raise ValueError('Invalid record bounds/header padding')
    h = bytearray(slot[:HEADER]); struct.pack_into('<I', h, CRC_OFFSET, 0)
    if zlib.crc32(h) != hc:
        raise ValueError('Header checksum mismatch')
    payload = slot[HEADER:HEADER + used]
    if zlib.crc32(payload) != crc:
        raise ValueError('Payload checksum mismatch')
    return {'sequence': sequence, 'payload': payload}


def inspect(image, nonce, prefix_sha256):
    if len(image) != PARTITION or hashlib.sha256(image[:BASE]).hexdigest() != prefix_sha256:
        raise ValueError('Immutable candidate prefix differs')
    validate_seed(image, nonce, prefix_sha256)
    records, invalid = [], []
    for i in range(2):
        try:
            record = decode(image[SLOT_BASE+i*SLOT:SLOT_BASE+(i+1)*SLOT], nonce)
        except ValueError:
            invalid.append(i); continue
        if record is not None:
            records.append(dict(record, slot=i))
    if records and len({r['sequence'] for r in records}) != len(records):
        raise ValueError('Ambiguous duplicate sequence')
    return {'latest': max(records, key=lambda r:r['sequence']) if records else None,
            'invalid_slots': invalid}


def write_fixture(path, nonce, prefix_sha256, payload):
    """Exercise actual ordered disk I/O on an owned regular fixture, never a device."""
    fd = os.open(path, os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid() or st.st_size != PARTITION:
            raise ValueError('Owned exact regular fixture required; no block device')
        image = os.pread(fd, PARTITION, 0)
        state = inspect(image, nonce, prefix_sha256)
        # Never initialize unexplained/foreign contents, even with no valid record.
        if state['latest'] is None and any(image[SLOT_BASE:GUARD]):
            raise ValueError('Nonempty unrecognized tail')
        latest = state['latest']; sequence = latest['sequence']+1 if latest else 1
        index = 1-latest['slot'] if latest else 0
        encoded = header(sequence, nonce, payload)
        start = SLOT_BASE+index*SLOT
        def put(data, offset):
            if os.pwrite(fd, data, offset) != len(data):
                raise OSError('Short mailbox write; no retry')
        put(bytes(HEADER), start); os.fsync(fd)
        put(payload, start+HEADER); os.fsync(fd)
        put(encoded, start); os.fsync(fd)
        after = os.pread(fd, PARTITION, 0)
        if after[:BASE] != image[:BASE] or after[SLOT_BASE+(1-index)*SLOT:SLOT_BASE+(2-index)*SLOT] != image[SLOT_BASE+(1-index)*SLOT:SLOT_BASE+(2-index)*SLOT] or after[BASE:SLOT_BASE] != image[BASE:SLOT_BASE] or after[GUARD:] != image[GUARD:]:
            raise ValueError('Write escaped selected slot')
        result = inspect(after, nonce, prefix_sha256)['latest']
        if result is None or result['sequence'] != sequence or result['payload'] != payload:
            raise ValueError('Full fixture readback differs')
        return result
    finally:
        os.close(fd)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--image',type=Path,required=True)
    p.add_argument('--nonce-file',type=Path,required=True)
    p.add_argument('--prefix-sha256',required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    fd=os.open(a.image,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError('Regular host image only; pull exact partition separately')
        image=os.read(fd,PARTITION+1)
    finally:os.close(fd)
    state=inspect(image,a.nonce_file.read_bytes(),a.prefix_sha256)
    if state['latest'] is None:raise ValueError('No valid attributable record')
    fd=os.open(a.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as out:out.write(state['latest']['payload'])
    print(json.dumps({'sequence':state['latest']['sequence'],'bytes':len(state['latest']['payload']),
                      'invalid_slots':state['invalid_slots'],'device_written':False}))


if __name__=='__main__':main()
