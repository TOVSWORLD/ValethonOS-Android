#!/usr/bin/env python3
"""Prepare host capture only. Never install, arm, launch recovery or reboot."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from capture_lab_kernel_log import validate

OBSERVE_SECONDS = 300


def prepare(package, physical_usb_path, output):
    if output.exists() or output.is_symlink():
        raise ValueError('Fresh private output required')
    report=json.loads((package/'report.json').read_text())
    nonce=(package/'nonce-private.bin').read_bytes()
    image=(package/'boot-full.img').read_bytes()
    if (hashlib.sha256(image).hexdigest()!=report['partition_sha256']
            or len(image)!=16777216 or len(nonce)!=32
            or hashlib.sha256(nonce).hexdigest()!=report['nonce_sha256']):
        raise ValueError('Exact complete draft package required')
    plan={'purpose':'first-normal-log-bringup','candidate_sha256':report['partition_sha256'],
          'physical_usb_path':physical_usb_path,'usb_id':'1209:0001','interface':'00',
          'wait_seconds':OBSERVE_SECONDS,'minimum_no_intervention_seconds':OBSERVE_SECONDS,
          'automatic_return_helper':False,'automatic_restore':False,'automatic_reboot':False}
    validate(plan,report,nonce)
    output.mkdir(mode=0o700,parents=False)
    for name,data in [('capture-plan-private.json',json.dumps(plan,indent=2).encode()+b'\n'),
                      ('candidate-report.json',json.dumps(report,indent=2).encode()+b'\n'),
                      ('nonce-private.bin',nonce)]:
        fd=os.open(output/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb') as stream:
            stream.write(data);stream.flush();os.fsync(stream.fileno())
    return {'prepared':True,'armed':False,'minimum_no_intervention_seconds':OBSERVE_SECONDS,
            'automatic_return_helper':False,'automatic_restore':False,'automatic_reboot':False,
            'receiver':'capture_lab_kernel_log.py only; do not use run_lab_log_trial.py'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--package',type=Path,required=True);p.add_argument('--physical-usb-path',required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    print(json.dumps(prepare(a.package,a.physical_usb_path,a.output),indent=2))
