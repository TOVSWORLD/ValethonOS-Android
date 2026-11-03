#!/usr/bin/env python3
"""Read-only exact recovery/p5 collector. Never write a device or read user data."""
import argparse
import hashlib
import json
from pathlib import Path
import os
from restore_diagnostic_boot import Adb, BOOT, RECOVERY, BOOT_BYTES, RECOVERY_BYTES, validate_backup
import retained_log_mailbox as mailbox


def collect(adb, original, manifest, candidate, nonce, output):
    validate_backup(original, manifest)
    if len(candidate)!=BOOT_BYTES or len(nonce)!=32 or output.exists() or output.is_symlink():
        raise ValueError('Exact candidate/nonce and fresh private output required')
    prefix=hashlib.sha256(candidate[:mailbox.BASE]).hexdigest()
    mailbox.validate_seed(candidate,nonce,prefix)
    if adb.run(['get-state']).strip()!=b'recovery':raise ValueError('Recovery required')
    for prop,want in [('ro.product.device',b'douglas'),('ro.twrp.version',b'3.3.1-0')]:
        if adb.run(['shell','getprop',prop]).strip()!=want:raise ValueError('Recovery identity differs')
    base='/dev/block/platform/mtk-msdc.0/by-name/'
    for name,node in [('boot',BOOT),('boot_x',BOOT),('recovery',RECOVERY),('recovery_x',RECOVERY)]:
        if adb.run(['shell','readlink',base+name]).strip()!=node.encode():raise ValueError('Partition alias differs')
    if hashlib.sha256(adb.read(RECOVERY,RECOVERY_BYTES)).hexdigest()!=manifest['recovery']['sha256']:
        raise ValueError('Recovery partition differs')
    image=adb.read(BOOT,BOOT_BYTES)
    # Both immutable prefix and exact per-candidate seed are required, independent
    # of whether the latest log slot was interrupted or USB ever enumerated.
    if image[mailbox.BASE:mailbox.SLOT_BASE]!=candidate[mailbox.BASE:mailbox.SLOT_BASE]:
        raise ValueError('Candidate seed differs')
    state=mailbox.inspect(image,nonce,prefix)
    output.mkdir(mode=0o700,parents=False)
    for name,data in [('boot-after-trial-private.img',image),('record-private.bin',state['latest']['payload'] if state['latest'] else b'')]:
        fd=os.open(output/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    report={'exact_candidate_prefix_and_seed_verified':True,'recovery_unchanged':True,
            'current_boot_sha256':hashlib.sha256(image).hexdigest(),
            'attributable_record':state['latest'] is not None,
            'kernel_record':bool(state['latest'] and state['latest']['sequence']>=2 and state['latest']['payload'].startswith(b'VALETHON RETAINED KERNEL LOG v1 release=')),
            'host_control_only':bool(state['latest'] and state['latest']['payload'].startswith(b'VALETHON HOST CONTROL v1\n')),
            'sequence':state['latest']['sequence'] if state['latest'] else None,
            'record_bytes':len(state['latest']['payload']) if state['latest'] else 0,
            'invalid_slots':state['invalid_slots'],'device_written':False,'rebooted':False}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');(output/'report.json').chmod(0o600)
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['selector-file','original-boot','rollback-manifest','candidate','nonce-file','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();selector=json.loads(a.selector_file.read_text())['selector']
    if not isinstance(selector,str) or not selector or selector.startswith('-'):raise ValueError('Explicit selector required')
    print(json.dumps(collect(Adb('adb',selector),a.original_boot.read_bytes(),json.loads(a.rollback_manifest.read_text()),a.candidate.read_bytes(),a.nonce_file.read_bytes(),a.output),indent=2))
