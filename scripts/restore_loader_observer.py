#!/usr/bin/env python3
"""Restore exact original bootstrap range from a validated trial readout.

Default read-only. --restore is the separately reviewed one-shot bootstrap write;
no normal boot/recovery writes, helper, reboot, retry or trial arm.
"""
import argparse
import json
from pathlib import Path
from restore_retained_trial import expected_current
from restore_diagnostic_boot import Adb,sha
from guard_loader_observer import preflight,write_once,CANDIDATE,ORIGINAL,SIZE

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['selector-file','original-boot','rollback-manifest','candidate','candidate-report','nonce-file','readout','original-ranges','bootstrap-original']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--receipt',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    for path in [a.original_boot,a.rollback_manifest,a.candidate,a.candidate_report,a.nonce_file,a.original_ranges,a.bootstrap_original]:
        if path.is_symlink() or not path.is_file():raise ValueError('Regular exact private inputs required')
    expected=expected_current(a.original_boot.read_bytes(),json.loads(a.rollback_manifest.read_text()),a.candidate.read_bytes(),json.loads(a.candidate_report.read_text()),a.nonce_file.read_bytes(),a.readout)
    data=a.bootstrap_original.read_bytes()
    if len(data)!=SIZE or sha(data)!=ORIGINAL:raise ValueError('Exact original bootstrap sectors required')
    selector=json.loads(a.selector_file.read_text())['selector']
    if not isinstance(selector,str) or not selector or selector.startswith('-'):raise ValueError('Explicit selected recovery required')
    adb=Adb('adb',selector);ranges=json.loads(a.original_ranges.read_text())
    if a.restore:
        if a.receipt is None:raise ValueError('Fresh explicit restore receipt required')
        result=write_once(adb,data,ranges,CANDIDATE,expected,a.receipt)
    else:result=preflight(adb,ranges,CANDIDATE,expected)
    print(json.dumps(result,indent=2))
