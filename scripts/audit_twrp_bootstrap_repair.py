#!/usr/bin/env python3
"""Inspect pinned recovery firmware's bootstrap repair, offline; never executes it."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import struct

RECOVERY_SHA='3c9bafcbfc4a0b12cb1a3f372af0cfd49ffec5b3e01a0b070465b49bd8435f11'
MEMBERS={'fix-bootpatch.sh':'07f4353c70f2025d86f76bab8e8a112e1e133648e25e705138825a82f1202715',
         'amonet-fixup.sh':'b5a856ea642cf1f148b0e6d72eb4e175df2cf0173135fcc173c3f5097c4f30cb'}


def audit(image):
    if len(image)!=17825792 or hashlib.sha256(image).hexdigest()!=RECOVERY_SHA:
        raise ValueError('Exact unchanged recovery image required')
    if image[:8]!=b'ANDROID!':raise ValueError('Android header required')
    k,ka,rd,ra,second,sa,tags,page,version,osv=struct.unpack_from('<10I',image,8)
    if page!=2048 or version or second:raise ValueError('Recovery layout differs')
    start=page+((k+page-1)//page)*page;raw=gzip.decompress(image[start:start+rd])
    if len(raw)>64*1024*1024:raise ValueError('Recovery archive exceeds bound')
    found={};at=0;trailer=False
    while at+110<=len(raw):
        h=raw[at:at+110]
        if h[:6] not in [b'070701',b'070702']:raise ValueError('newc header differs')
        n=int(h[94:102],16);z=int(h[54:62],16)
        if not 1<=n<=4096 or at+110+n>len(raw):raise ValueError('newc name bounds')
        name=raw[at+110:at+110+n-1].decode();at=(at+110+n+3)&~3
        if at+z>len(raw):raise ValueError('newc data bounds')
        data=raw[at:at+z];at=(at+z+3)&~3
        if name=='TRAILER!!!':trailer=True;break
        if name in MEMBERS:
            if name in found or hashlib.sha256(data).hexdigest()!=MEMBERS[name]:raise ValueError('Pinned recovery member differs')
            found[name]={'bytes':z,'sha256':MEMBERS[name]}
    if not trailer or set(found)!=set(MEMBERS):raise ValueError('Incomplete repair source')
    return {'scope':'Pinned recovery firmware inspection only; no execution, device access or mutation',
            'recovery_sha256':RECOVERY_SHA,'members':found,
            'condition':'Normal bootstrap header or payload differs from recovery bootstrap',
            'effect':'Copies original recovery bootstrap header and payload into normal bootstrap',
            'payload_offset_sectors':223223,'status_file':'/tmp/restore_bootpatch.log',
            'expected_status_message':'Detected overwritten boot-exploit, restoring from recovery',
            'runtime_execution_proved_by_this_script':False,'recovery_modified':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--recovery',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.recovery.is_symlink() or not a.recovery.is_file():raise ValueError('Regular recovery file required')
    a.output.write_text(json.dumps(audit(a.recovery.read_bytes()),indent=2)+'\n');print('Pinned TWRP repair source verified offline')
