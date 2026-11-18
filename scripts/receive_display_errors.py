#!/usr/bin/env python3
"""Persist display status plus a bounded one-way kernel snapshot; never ACK."""
import hashlib
import hmac
import os
import select
import struct
import time
from receive_display_status import decode as decode_status

CAPACITY=256*1024
STATUS=120
HEADER=56


def status(data,nonce):
    if len(data)!=STATUS or data[:8]!=b'VDISP002' or struct.unpack_from('<I',data,40)[0]!=2:
        raise ValueError('Display error-capture status required')
    legacy=bytearray(data);legacy[:8]=b'VDISP001';struct.pack_into('<I',legacy,40,1)
    result=decode_status(bytes(legacy),nonce)
    result['protocol']='VDISP002'
    return result


def extent(header,nonce):
    if len(header)!=HEADER or header[:8]!=b'VKMSG001' or not hmac.compare_digest(header[8:40],nonce):
        raise ValueError('Fresh kernel snapshot header required')
    size,error,flags,records=struct.unpack_from('<IiII',header,40)
    if (size>CAPACITY or error>0 or not flags or flags&~31 or not flags&27
            or records>4096 or bool(size)!=bool(records)
            or bool(error)!=bool(flags&24)):
        raise ValueError('Invalid bounded kernel snapshot state')
    return size,error,flags,records


def decode(data,nonce):
    result=status(data[:STATUS],nonce)
    result.update(kernel_snapshot_received=False,kernel_snapshot_error=None)
    try:
        size,error,flags,records=extent(data[STATUS:STATUS+HEADER],nonce)
        if len(data)!=STATUS+HEADER+size:raise ValueError('Incomplete kernel snapshot payload')
    except ValueError:
        result['kernel_snapshot_error']='invalid-or-incomplete-tail'
        return result
    payload=data[STATUS+HEADER:]
    result.update(kernel_snapshot_received=True,kernel_snapshot_bytes=size,
                  kernel_snapshot_records=records,kernel_snapshot_read_error=error,
                  kernel_snapshot_flags=flags,kernel_snapshot_sha256=hashlib.sha256(payload).hexdigest(),
                  kernel_snapshot_caught_up=bool(flags&1),kernel_snapshot_truncated=bool(flags&2),
                  kernel_snapshot_ring_loss=bool(flags&4),kernel_snapshot_deadline=bool(flags&8),
                  kernel_snapshot_read_failed=bool(flags&16))
    return result


def receive_fd(port,raw,nonce,deadline):
    data=bytearray()
    def read_to(wanted):
        while len(data)<wanted:
            remaining=deadline-time.monotonic()
            if remaining<=0:raise TimeoutError('Display capture deadline expired')
            if not select.select([port],[],[],remaining)[0]:raise TimeoutError('Display capture deadline expired')
            try:chunk=os.read(port,min(4096,wanted-len(data)))
            except (BlockingIOError,InterruptedError):continue
            if not chunk:raise ValueError('Display capture disconnected')
            used=0
            while used<len(chunk):
                n=os.write(raw,chunk[used:])
                if n<=0:raise OSError('Display capture persistence failed')
                used+=n
            data.extend(chunk)
    read_to(STATUS)
    status(bytes(data),nonce)
    # Status remains useful if reset/USB loss interrupts the optional tail.
    try:
        read_to(STATUS+HEADER)
        size,_,_,_=extent(bytes(data[STATUS:]),nonce)
        read_to(STATUS+HEADER+size)
    except (TimeoutError,ValueError,OSError):
        pass
    os.fsync(raw)
    result=decode(bytes(data),nonce)
    result.update(complete=True,device_qualified=False,status_bytes=STATUS,wire_bytes=len(data))
    return result
