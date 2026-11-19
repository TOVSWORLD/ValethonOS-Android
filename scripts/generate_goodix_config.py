#!/usr/bin/env python3
"""Reproduce the public board configuration matching this tablet's cached driver profile."""
import argparse,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'evidence/touch-input-source/working-douglas_hvt.dts'
EXPECTED='a9242d29e3f9cfcaffbe71445c3446f0adf69f3738bcfa226cad7ac7703079e7'


def configuration(text):
    groups={int(n):bytes.fromhex(s) for n,s in re.findall(r'goodix,cfg-group(\d+)\s*=\s*\[(.*?)\]',text,re.S)}
    if not all(n in groups for n in range(4)) or len({groups[n] for n in range(4)})!=1:
        raise ValueError('Known equivalent sensor groups0-3 required')
    data=groups[0]
    if (len(data)!=186 or hashlib.sha256(data).hexdigest()!=EXPECTED or
            sum(data[:-1])&255 or data[-1]!=1 or
            int.from_bytes(data[1:3],'little')!=800 or int.from_bytes(data[3:5],'little')!=1280 or
            data[5]&15!=10 or data[6]&3!=1):raise ValueError('Exact known working board configuration required')
    return data


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    data=configuration(SOURCE.read_text())
    with a.output.open('xb') as f:f.write(data)
    a.output.chmod(0o600);print(json.dumps({'bytes':len(data),'sha256':EXPECTED,'source':'public working board DTS','sensor_id_claimed':False,'hardware_written':False}))
