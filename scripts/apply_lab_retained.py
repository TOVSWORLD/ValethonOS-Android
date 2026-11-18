#!/usr/bin/env python3
"""Private source-only retained mailbox insertion. No device operations."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
ACK='d9318bdb4c34e8b2d997b4f67ced56b120b22b87'

def apply(source, revision):
    if revision!=ACK:raise ValueError('Wrong retained-mailbox ACK revision')
    destination=source/'drivers/misc'
    files={'valethon_mailbox.c':ROOT/'projects/firetabs-android/kernel/lab-retained/mailbox.c',
           'retained_mailbox.h':ROOT/'projects/firetabs-android/diagnostic-usb/retained_mailbox.h'}
    make=destination/'Makefile';before=make.read_bytes()
    lock=json.loads((ROOT/'projects/firetabs-android/kernel/lab-retained/inputs.json').read_text())
    if revision!=lock['ack_commit'] or hashlib.sha256(before).hexdigest()!=lock['makefile_sha256']:
        raise ValueError('Retained Makefile/input revision drift')
    if b'valethon_mailbox' in before or any((destination/name).exists() for name in files):
        raise ValueError('Refuse existing mailbox source/Makefile entry')
    # Original Makefile is not modified until every source input has been read.
    data={name:path.read_bytes() for name,path in files.items()}
    for name,key in [('valethon_mailbox.c','source_sha256'),('retained_mailbox.h','codec_sha256')]:
        if hashlib.sha256(data[name]).hexdigest()!=lock[key]:raise ValueError('Retained source drift')
    for name,content in data.items():
        with (destination/name).open('xb') as out:out.write(content)
    make.write_bytes(before+b'\n# Private exact boot-tail logging experiment only\nobj-y += valethon_mailbox.o\n')
    return {'source_applied':True,'inputs_sha256':{n:hashlib.sha256(b).hexdigest() for n,b in data.items()},'device_written':False}

if __name__=='__main__':
    import json
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);a=p.parse_args()
    revision=subprocess.check_output(['git','-C',str(a.source),'rev-parse','HEAD'],text=True).strip()
    print(json.dumps(apply(a.source,revision),indent=2))
