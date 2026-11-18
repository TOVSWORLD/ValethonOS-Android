#!/usr/bin/env python3
"""Apply source-locked MT8163 display pipeline after the existing DSI port."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]
PORT=ROOT/'projects/firetabs-android/kernel/display-port'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def apply(source, revision):
    lock=json.loads((PORT/'inputs.json').read_text())
    if revision!=lock['ack_commit']:
        raise ValueError('Exact ACK revision required')
    patch=PORT/lock['patch']
    if sha(patch)!=lock['patch_sha256']:
        raise ValueError('Display patch changed')
    for part in lock['files']:
        for path in [ROOT/part['source'],source/part['target']]:
            if path.is_symlink() or sha(path)!=part['original_sha256']:
                raise ValueError('Display input drift: '+part['target'])
    targets=[part['target'] for part in lock['files']]
    stat=subprocess.check_output(['git','-C',str(source),'apply','--numstat',str(patch)],text=True)
    if sorted(line.split('\t')[2] for line in stat.splitlines())!=sorted(targets):
        raise ValueError('Display patch target set changed')
    with tempfile.TemporaryDirectory(prefix='display-preflight-') as directory:
        shadow=Path(directory)
        for part in lock['files']:
            dest=shadow/part['target'];dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source/part['target'],dest)
        subprocess.run(['git','-C',str(shadow),'apply',str(patch)],check=True,capture_output=True)
        for part in lock['files']:
            if sha(shadow/part['target'])!=part['patched_sha256']:
                raise ValueError('Display output drift before writes')
    subprocess.run(['git','-C',str(source),'apply','--check',str(patch)],check=True,capture_output=True)
    subprocess.run(['git','-C',str(source),'apply',str(patch)],check=True,capture_output=True)
    return {'scope':'MT8163 display pipeline source only; no DT enablement or hardware action',
            'targets':targets,'all_outputs_preflighted':True,'hardware_execution':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',type=Path);args=parser.parse_args()
    revision=subprocess.check_output(['git','-C',str(args.source),'rev-parse','HEAD'],text=True).strip()
    print(json.dumps(apply(args.source,revision),indent=2))
