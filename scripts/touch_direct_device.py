#!/usr/bin/env python3
"""One exact owner-approved direct touch install/rollback from original TWRP."""
import argparse, json
from pathlib import Path
from restore_diagnostic_boot import Adb, BOOT_BYTES, sha, validate_backup, preflight, restore
from display_direct_device import ORIGINAL, RECOVERY


def inputs(case):
    report = json.loads((case/'report.json').read_text())
    auth = json.loads((case/'owner-authorization-private.json').read_text())
    candidate = (case/'boot-full.img').read_bytes(); original = (case/'original-boot.img').read_bytes()
    nonce = (case/'trial-nonce-private.bin').read_bytes()
    manifest = {'boot': {'bytes': BOOT_BYTES, 'sha256': ORIGINAL},
                'recovery': {'bytes': 17825792, 'sha256': RECOVERY}}
    validate_backup(original, manifest)
    expected = {'scope': 'touch-direct-1', 'candidate_sha256': sha(candidate), 'nonce_sha256': sha(nonce),
                'runner_sha256': sha(Path(__file__).read_bytes()), 'owner_approved': True,
                'maximum_candidate_writes': 1, 'maximum_original_restore_writes': 1,
                'recovery_writes_allowed': False, 'automatic_trial_retry': False}
    if any(type(auth.get(k)) is not type(v) or auth.get(k) != v for k, v in expected.items()):
        raise ValueError('Exact fresh touch authorization required')
    if (len(nonce) != 32 or len(candidate) != BOOT_BYTES or sha(candidate) != report['partition_sha256']
            or report.get('scope') != 'Offline direct touch candidate only'
            or report.get('authorization_scope') != 'touch-direct-1' or report['nonce_sha256'] != sha(nonce)
            or report.get('native_trampoline_used') is not False
            or report.get('original_boot_restore_required') is not True
            or report.get('physical_execution_admitted') is not False
            or report.get('usb_status_is_touch_proof') is not False
            or report.get('kernel', {}).get('image_sha256') != 'd93f2ed5dad7f60abe032fef48fa05f93901bb493a02211d399c7d5b779ec27f'
            or report.get('source_sha256') != sha((Path(__file__).parent/'prepare_touch_direct_boot.py').read_bytes())):
        raise ValueError('Exact reviewed touch package required')
    return candidate, original, manifest


def run(case, adb, action):
    candidate, original, manifest = inputs(case)
    if action == 'preflight':
        preflight(adb, original, manifest, ORIGINAL); return {'preflight': 'passed', 'written': False}
    if action == 'install':
        m = {'boot': {'bytes': BOOT_BYTES, 'sha256': sha(candidate)}, 'recovery': manifest['recovery']}
        return restore(adb, candidate, m, ORIGINAL, case/'install-receipt.json', operation='approved direct touch test, one p5 write')
    installed = json.loads((case/'install-receipt.json').read_text())
    if installed.get('verified') is not True or installed.get('rollback_sha256') != sha(candidate):
        raise ValueError('Verified owned install required')
    return restore(adb, original, manifest, sha(candidate), case/'restore-receipt.json')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--case', type=Path, required=True)
    p.add_argument('--selector-file', type=Path, required=True); p.add_argument('action', choices=['preflight', 'install', 'restore'])
    a = p.parse_args(); selector = json.loads(a.selector_file.read_text())['selector']
    if not isinstance(selector, str) or not selector or selector.startswith('-'): raise ValueError('Explicit selected device required')
    print(json.dumps(run(a.case, Adb('adb', selector), a.action)))
