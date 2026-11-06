#!/usr/bin/env python3
"""Exact approved complete-draft operations; no reboot/helper/automatic restore.

Separate from the held historical trial installer. Only this exact reviewed image
is accepted; each write has a fixed exclusive receipt. Default is read-only.
"""
import argparse
import json
from pathlib import Path
from restore_diagnostic_boot import Adb,BOOT_BYTES,sha,validate_backup,preflight,restore
from pull_retained_mailbox import collect
import retained_log_mailbox as mailbox

CANDIDATE='af1dc7e2e76f94a8324f42d789a32ce1a54a827bc8390d721338caab7bce6365'
ORIGINAL='08fcf3455d66943632d0fc91348d4ab7d41b80c40d88e61272000a1d697faa1e'
RECOVERY='3c9bafcbfc4a0b12cb1a3f372af0cfd49ffec5b3e01a0b070465b49bd8435f11'


def inputs(case):
    private=case/'private'
    candidate=(private/'boot-full.img').read_bytes();original=(private/'original-boot.img').read_bytes()
    manifest=json.loads((private/'rollback-manifest.json').read_text())
    report=json.loads((private/'candidate-report.json').read_text());nonce=(private/'nonce-private.bin').read_bytes()
    validate_backup(original,manifest)
    if (sha(original)!=ORIGINAL or manifest['recovery']['sha256']!=RECOVERY
            or len(candidate)!=BOOT_BYTES or sha(candidate)!=CANDIDATE
            or report['partition_sha256']!=CANDIDATE or sha(nonce)!=report['nonce_sha256']
            or report['kernel_release']!='6.18.34-valethon-draft1+'):
        raise ValueError('Exact reviewed complete draft/originals required')
    mailbox.validate_seed(candidate,nonce,sha(candidate[:mailbox.BASE]))
    approval=json.loads((private/'owner-authorization.json').read_text())
    if (approval.get('candidate_sha256')!=CANDIDATE or approval.get('owner_go') is not True
            or approval.get('two_visits') is not True or approval.get('minimum_seconds')!=300
            or approval.get('automatic_return') is not False):
        raise ValueError('Exact current owner authorization required')
    selector=json.loads((private/'selector.json').read_text())['selector']
    if not isinstance(selector,str) or not selector or selector.startswith('-'):raise ValueError('Explicit selector required')
    return candidate,original,manifest,nonce,selector


def returned_hash(case,candidate,nonce):
    output=case/'private/readout';image=(output/'boot-after-trial-private.img').read_bytes()
    report=json.loads((output/'report.json').read_text());prefix=sha(candidate[:mailbox.BASE])
    if len(image)!=BOOT_BYTES or image[mailbox.BASE:mailbox.SLOT_BASE]!=candidate[mailbox.BASE:mailbox.SLOT_BASE]:raise ValueError('Exact readout seed required')
    mailbox.inspect(image,nonce,prefix)
    if (report.get('current_boot_sha256')!=sha(image) or report.get('recovery_unchanged') is not True
            or report.get('exact_candidate_prefix_and_seed_verified') is not True):raise ValueError('Validated readout required')
    return sha(image)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',type=Path,required=True)
    p.add_argument('action',choices=['preflight','installed-preflight','install','collect','restore-preflight','restore'])
    a=p.parse_args();candidate,original,manifest,nonce,selector=inputs(a.case);adb=Adb('adb',selector)
    if a.action=='preflight':
        preflight(adb,original,manifest,ORIGINAL);result={'preflight':'passed','written':False}
    elif a.action=='installed-preflight':
        trial={'boot':{'bytes':BOOT_BYTES,'sha256':CANDIDATE},'recovery':manifest['recovery']}
        preflight(adb,candidate,trial,CANDIDATE);result={'preflight':'passed','written':False}
    elif a.action=='install':
        trial={'boot':{'bytes':BOOT_BYTES,'sha256':CANDIDATE},'recovery':manifest['recovery']}
        result=restore(adb,candidate,trial,ORIGINAL,a.case/'private/install-receipt.json',operation='approved complete first kernel draft, one p5 write')
    elif a.action=='collect':
        result=collect(adb,original,manifest,candidate,nonce,a.case/'private/readout')
    else:
        current=returned_hash(a.case,candidate,nonce)
        if a.action=='restore-preflight':
            preflight(adb,original,manifest,current);result={'preflight':'passed','written':False}
        else:
            archive=json.loads((a.case/'private/archive-verified.json').read_text())
            if archive.get('current_boot_sha256')!=current or archive.get('lab_and_controller_match') is not True:raise ValueError('Archive copy/hash verification required before restore')
            result=restore(adb,original,manifest,current,a.case/'private/restore-receipt.json')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
