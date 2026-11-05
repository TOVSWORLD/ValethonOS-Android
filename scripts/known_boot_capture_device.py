#!/usr/bin/env python3
"""Exact known-stack calibration operations. No reboot, helper, or automatic return.

Each install/restore is explicit and exclusive. Default preflight is read-only.
The original diagnostic installer/logging hold is unchanged.
"""
import argparse
import json
from pathlib import Path
import guard_known_boot_capture as observer
from restore_diagnostic_boot import Adb, BOOT_BYTES, sha, validate_backup, preflight, restore
from pull_retained_mailbox import collect
import retained_log_mailbox as mailbox

CANDIDATE = observer.KERNEL_CANDIDATE
ORIGINAL = observer.ORIGINAL_BOOT


def inputs(case):
    private = case / 'private'
    candidate = (private / 'boot-full.img').read_bytes()
    original = (private / 'original-boot.img').read_bytes()
    sectors = (private / 'observer-sectors.bin').read_bytes()
    original_sectors = (private / 'original-sectors.bin').read_bytes()
    manifest = json.loads((private / 'rollback-manifest.json').read_text())
    package = json.loads((private / 'candidate-manifest.json').read_text())
    ranges = json.loads((private / 'original-ranges.json').read_text())
    nonce = (private / 'nonce.bin').read_bytes()
    validate_backup(original, manifest)
    if (sha(original) != ORIGINAL or manifest['recovery']['sha256'] != observer.RECOVERY
            or len(candidate) != BOOT_BYTES or sha(candidate) != CANDIDATE
            or len(sectors) != observer.SIZE or sha(sectors) != observer.CANDIDATE
            or len(original_sectors) != observer.SIZE or sha(original_sectors) != observer.ORIGINAL
            or len(nonce) != 32 or sha(nonce) != package['nonce_sha256']
            or package['candidate_sha256'] != CANDIDATE
            or package['observer_sha256'] != observer.CANDIDATE
            or candidate[:7796736] != original[:7796736]):
        raise ValueError('Exact reviewed known-stack control and originals required')
    mailbox.validate_seed(candidate, nonce, sha(candidate[:mailbox.BASE]))
    selector = json.loads((private / 'selector.json').read_text())['selector']
    if not isinstance(selector, str) or not selector or selector.startswith('-'):
        raise ValueError('Explicit selector required')
    return private, candidate, original, sectors, original_sectors, manifest, ranges, nonce, selector


def approval(private):
    value = json.loads((private / 'owner-authorization.json').read_text())
    observer.authorize(value)
    return value


def returned_hash(private, candidate, nonce):
    output = private / 'readout'
    image = (output / 'boot-after-trial-private.img').read_bytes()
    report = json.loads((output / 'report.json').read_text())
    if (len(image) != BOOT_BYTES
            or image[mailbox.BASE:mailbox.SLOT_BASE] != candidate[mailbox.BASE:mailbox.SLOT_BASE]
            or report.get('current_boot_sha256') != sha(image)
            or report.get('recovery_unchanged') is not True
            or report.get('exact_candidate_prefix_and_seed_verified') is not True):
        raise ValueError('Validated complete readout required')
    mailbox.inspect(image, nonce, sha(candidate[:mailbox.BASE]))
    return sha(image)


def run(case, action):
    private, candidate, original, sectors, original_sectors, manifest, ranges, nonce, selector = inputs(case)
    adb = Adb('adb', selector)
    if action == 'preflight':
        return observer.preflight(adb, ranges, observer.ORIGINAL, ORIGINAL)
    if action == 'install-observer':
        auth = approval(private)
        return observer.write_once(adb, sectors, ranges, observer.ORIGINAL, ORIGINAL,
                                   private / 'observer-install-receipt.json', auth)
    if action == 'install-boot':
        approval(private)
        receipt = json.loads((private / 'observer-install-receipt.json').read_text())
        if receipt.get('verified') is not True or receipt.get('target_sha256') != observer.CANDIDATE:
            raise ValueError('Verified exact observer installation required')
        observer.preflight(adb, ranges, observer.CANDIDATE, ORIGINAL)
        trial = {'boot': {'bytes': BOOT_BYTES, 'sha256': CANDIDATE}, 'recovery': manifest['recovery']}
        return restore(adb, candidate, trial, ORIGINAL, private / 'install-receipt.json',
                       operation='known-stack capture calibration, one full p5 write')
    if action == 'installed-preflight':
        return observer.preflight(adb, ranges, observer.CANDIDATE, CANDIDATE)
    if action == 'collect':
        return collect(adb, original, manifest, candidate, nonce, private / 'readout')
    if action == 'restore-bootstrap-before-boot':
        # Aborted preparation: p5 is still the exact original. Never reads a trial record.
        current_boot = ORIGINAL
    elif action in ('restore-bootstrap', 'restore-boot', 'restored-preflight'):
        current_boot = ORIGINAL if action == 'restored-preflight' else returned_hash(private, candidate, nonce)
    else:
        raise ValueError('Unknown action')
    if action.startswith('restore-bootstrap'):
        current = sha(observer.range_read(adb, observer.TARGET))
        if current == observer.ORIGINAL:
            # TWRP may already have repaired it. Verify; never rewrite an original range.
            observer.preflight(adb, ranges, observer.ORIGINAL, current_boot)
            return {'bootstrap_already_original': True, 'device_written': False}
        if current != observer.CANDIDATE:
            raise ValueError('Unexpected bootstrap hash; stop without write or retry')
        return observer.write_once(adb, original_sectors, ranges, current, current_boot,
                                   private / 'observer-restore-receipt.json')
    observer.preflight(adb, ranges, observer.ORIGINAL, current_boot)
    if action == 'restored-preflight':
        return {'original_boot_bootstrap_recovery_verified': True, 'device_written': False}
    archive = json.loads((private / 'archive-verified.json').read_text())
    if (archive.get('current_boot_sha256') != current_boot
            or archive.get('lab_and_controller_match') is not True):
        raise ValueError('Verified private evidence archive required before original p5 restore')
    return restore(adb, original, manifest, current_boot, private / 'restore-receipt.json')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case', type=Path, required=True)
    p.add_argument('action', choices=['preflight', 'install-observer', 'install-boot',
        'installed-preflight', 'collect', 'restore-bootstrap-before-boot',
        'restore-bootstrap', 'restore-boot', 'restored-preflight'])
    a = p.parse_args()
    print(json.dumps(run(a.case, a.action), indent=2))
