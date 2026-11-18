#!/usr/bin/env python3
"""Functional framebuffer/banner status; physical visibility needs owner observation."""
import hmac
import os
import select
import struct
import time

MAGIC=b'VDISP001'
PACKET_BYTES=120


def decode(packet,nonce):
    if len(packet)!=PACKET_BYTES or len(nonce)!=32 or packet[:8]!=MAGIC or not hmac.compare_digest(packet[8:40],nonce):
        raise ValueError('Exact fresh display status required')
    version,stage,error,flags,width,height,bpp,stride,size,name_length,banner_error=struct.unpack_from('<IIiIIIIIQIi',packet,40)
    name_data=packet[88:]
    if version!=1 or flags not in [1,3,7] or stage!={1:1,3:2,7:3}[flags] or error>0 or banner_error>0:
        raise ValueError('Invalid display status state')
    if not 0<=name_length<=31 or any(name_data[name_length:]):
        raise ValueError('Invalid framebuffer name extent')
    try:name=name_data[:name_length].decode('ascii')
    except UnicodeDecodeError:raise ValueError('Invalid framebuffer name') from None
    if any(ord(c)<32 or ord(c)>126 for c in name) or size!=height*stride:
        raise ValueError('Invalid framebuffer metadata')
    ready=flags>=3
    if ready and (width,height)!=(800,1280):
        raise ValueError('Wrong TPV framebuffer dimensions')
    if ready and (bpp not in [16,24,32] or not (width*bpp+7)//8<=stride<=8192 or name!='mediatekdrmfb'):
        raise ValueError('Wrong MediaTek framebuffer contract')
    complete=flags==7 and error==0 and banner_error==0
    if not error and not complete:
        raise ValueError('Incomplete status claimed success')
    if flags==7 and (error or banner_error):
        raise ValueError('Banner-success state reports failure')
    return {'protocol':'VDISP001','framebuffer_metadata_ready':ready,
            'console_banner_written':complete,'stage':stage,'error':error,'flags':flags,
            'virtual_width':width,'virtual_height':height,'bits_per_pixel':bpp,'stride':stride,
            'buffer_extent_bytes':size,'framebuffer_name':name,'banner_error':banner_error,
            'physical_pixels_confirmed':False,'owner_visual_confirmation_required':True,
            'block_storage_probe_required':False,'kernel_log_transfer_required':False}


def receive_fd(port,raw,nonce,deadline):
    data=bytearray()
    while len(data)<PACKET_BYTES:
        remaining=deadline-time.monotonic()
        if remaining<=0:raise TimeoutError('Display status deadline expired')
        if not select.select([port],[],[],remaining)[0]:raise TimeoutError('Display status deadline expired')
        try:chunk=os.read(port,PACKET_BYTES-len(data))
        except (BlockingIOError,InterruptedError):continue
        if not chunk:raise ValueError('Disconnected before complete display status')
        used=0
        while used<len(chunk):
            n=os.write(raw,chunk[used:])
            if n<=0:raise OSError('Display status persistence failed')
            used+=n
        data.extend(chunk)
    os.fsync(raw)
    result=decode(bytes(data),nonce);result.update(complete=True,device_qualified=False,status_bytes=len(data))
    return result
