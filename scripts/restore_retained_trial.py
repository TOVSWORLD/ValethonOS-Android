#!/usr/bin/env python3
"""Guarded original rollback after an independently collected persistent trial.

Default read-only device preflight. Explicit --restore performs exactly one existing
rollback transport operation; no reboot, retry, recovery write or user-data reads.
"""
import argparse
import json
from pathlib import Path
from restore_diagnostic_boot import Adb, preflight, restore, sha, validate_backup, BOOT_BYTES
from write_lab_boot_candidate import candidate_manifest
import retained_log_mailbox as mailbox


def expected_current(original,manifest,candidate,candidate_report,nonce,readout):
    candidate_manifest(candidate,candidate_report,original,manifest)
    image_path=readout/'boot-after-trial-private.img';report_path=readout/'report.json'
    if image_path.is_symlink() or not image_path.is_file() or image_path.stat().st_size!=BOOT_BYTES or report_path.is_symlink():
        raise ValueError('Exact regular private readout required')
    image=image_path.read_bytes();report=json.loads(report_path.read_text())
    prefix=sha(candidate[:mailbox.BASE])
    mailbox.validate_seed(candidate,nonce,prefix)
    if image[mailbox.BASE:mailbox.SLOT_BASE]!=candidate[mailbox.BASE:mailbox.SLOT_BASE]:raise ValueError('Readout seed differs')
    mailbox.inspect(image,nonce,prefix)
    if not report.get('exact_candidate_prefix_and_seed_verified') or not report.get('recovery_unchanged') or report.get('current_boot_sha256')!=sha(image):
        raise ValueError('Collector receipt/image differs')
    return sha(image)


def run(adb,original,manifest,candidate,candidate_report,nonce,readout,receipt=None,write=False):
    expected=expected_current(original,manifest,candidate,candidate_report,nonce,readout)
    if write:
        if receipt is None:raise ValueError('Fresh explicit rollback receipt required')
        return restore(adb,original,manifest,expected,receipt)
    preflight(adb,original,manifest,expected)
    return {'preflight':'passed','expected_current_boot_sha256':expected,'device_written':False,'rebooted':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['selector-file','original-boot','rollback-manifest','candidate','candidate-report','nonce-file','readout']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--receipt',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    selector=json.loads(a.selector_file.read_text())['selector']
    if not isinstance(selector,str) or not selector or selector.startswith('-'):raise ValueError('Explicit selected device required')
    for path in [a.original_boot,a.candidate,a.nonce_file,a.candidate_report,a.rollback_manifest]:
        if path.is_symlink() or not path.is_file():raise ValueError('Regular exact input files required')
    print(json.dumps(run(Adb('adb',selector),a.original_boot.read_bytes(),json.loads(a.rollback_manifest.read_text()),a.candidate.read_bytes(),json.loads(a.candidate_report.read_text()),a.nonce_file.read_bytes(),a.readout,a.receipt,a.restore),indent=2))
