#!/usr/bin/env python3
"""Read-only exact recovery/p5 collector. Never write a device or read user data."""
import argparse
import hashlib
import json
from pathlib import Path
import os
import subprocess
from restore_diagnostic_boot import Adb, BOOT, RECOVERY, BOOT_BYTES, RECOVERY_BYTES, validate_backup
import retained_log_mailbox as mailbox


class CollectionError(ValueError):
    """Allowlisted validation stage only; never includes transport output/identity."""
    def __init__(self, stage, kind, reason):
        self.stage = stage
        self.kind = kind
        self.reason = reason
        super().__init__('Retained collection stopped at ' + stage)


def collect(adb, original, manifest, candidate, nonce, output):
    stage = ['rollback_input']
    def mark(name):
        stage[0] = name
    try:
        return _collect(adb, original, manifest, candidate, nonce, output, mark)
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        reasons = {
            'Selected ADB command failed; stop without retry': 'adb_command_failed',
            'Partition read size mismatch; no trimming permitted': 'partition_read_size_mismatch',
            'Recovery required': 'recovery_state_mismatch',
            'Recovery identity differs': 'recovery_identity_mismatch',
            'Partition alias differs': 'partition_alias_mismatch',
            'Recovery partition differs': 'recovery_hash_mismatch',
            'Candidate seed differs': 'candidate_seed_mismatch',
            'Exact candidate/nonce and fresh private output required': 'candidate_nonce_or_output_invalid',
        }
        reason = ('transport_timeout' if isinstance(error, subprocess.TimeoutExpired)
                  else reasons.get(str(error), 'validation_or_io_failure'))
        raise CollectionError(stage[0], type(error).__name__, reason) from error


def _collect(adb, original, manifest, candidate, nonce, output, mark):
    validate_backup(original, manifest)
    mark('candidate_nonce_output')
    if len(candidate)!=BOOT_BYTES or len(nonce)!=32 or output.exists() or output.is_symlink():
        raise ValueError('Exact candidate/nonce and fresh private output required')
    prefix=hashlib.sha256(candidate[:mailbox.BASE]).hexdigest()
    mark('candidate_seed')
    mailbox.validate_seed(candidate,nonce,prefix)
    mark('recovery_state')
    if adb.run(['get-state']).strip()!=b'recovery':raise ValueError('Recovery required')
    for prop,want in [('ro.product.device',b'douglas'),('ro.twrp.version',b'3.3.1-0')]:
        mark('recovery_identity_' + prop.split('.')[-1])
        if adb.run(['shell','getprop',prop]).strip()!=want:raise ValueError('Recovery identity differs')
    base='/dev/block/platform/mtk-msdc.0/by-name/'
    for name,node in [('boot',BOOT),('boot_x',BOOT),('recovery',RECOVERY),('recovery_x',RECOVERY)]:
        mark('alias_' + name)
        if adb.run(['shell','readlink',base+name]).strip()!=node.encode():raise ValueError('Partition alias differs')
    mark('full_recovery_read_and_hash')
    if hashlib.sha256(adb.read(RECOVERY,RECOVERY_BYTES)).hexdigest()!=manifest['recovery']['sha256']:
        raise ValueError('Recovery partition differs')
    mark('full_boot_read')
    image=adb.read(BOOT,BOOT_BYTES)
    # Both immutable prefix and exact per-candidate seed are required, independent
    # of whether the latest log slot was interrupted or USB ever enumerated.
    mark('returned_candidate_seed')
    if image[mailbox.BASE:mailbox.SLOT_BASE]!=candidate[mailbox.BASE:mailbox.SLOT_BASE]:
        raise ValueError('Candidate seed differs')
    mark('returned_prefix_and_records')
    state=mailbox.inspect(image,nonce,prefix)
    mark('private_readout_output')
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
