#!/usr/bin/env python3
"""Extract the fresh kernel snapshot into private files for display diagnosis."""
import argparse
import json
import os
from pathlib import Path
import re
from receive_display_errors import decode,STATUS,HEADER


def inspect(wire,nonce,output):
    data=wire.read_bytes();result=decode(data,nonce)
    if not result['kernel_snapshot_received']:raise ValueError('No valid kernel snapshot received')
    output.mkdir(mode=0o700)
    payload=data[STATUS+HEADER:]
    records=re.findall(rb'^(\d+),(\d+),(\d+),([^;\n]*);([^\n]*)',payload,re.M)
    relevant=[]
    for priority,sequence,timestamp,flags,message in records:
        if (int(priority)&7)<=4 or re.search(rb'drm|probe|defer|display|panel|backlight|lp855|smi|iommu|mipi|i2c|clock|regulator',message,re.I):
            relevant.append(b','.join([priority,sequence,timestamp,flags])+b';'+message)
    result.update(parsed_records=len(records),relevant_records=len(relevant))
    for name,content in [('kernel-snapshot-private.bin',payload),
                         ('display-errors-private.txt',b'\n'.join(relevant)+b'\n'),
                         ('assessment-private.json',(json.dumps(result,indent=2)+'\n').encode())]:
        fd=os.open(output/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb') as f:f.write(content);f.flush();os.fsync(f.fileno())
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--wire',type=Path,required=True);p.add_argument('--nonce',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    r=inspect(a.wire,a.nonce.read_bytes(),a.output)
    print(json.dumps({k:r[k] for k in ['kernel_snapshot_bytes','parsed_records','relevant_records']}))
