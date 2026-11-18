#!/usr/bin/env python3
"""Protected known-source boot/restore, then one full maintained-kernel RAM boot."""
import argparse
import json
import os
import shlex
import subprocess
import tarfile
from pathlib import Path

from run_source_usb_trial import validate as validate_source, private
from run_reset_payload_trial import digest, read
from run_pstore_warm_reboot import LabADB
from run_native_source_boot import facts, BOOT_SHA
from run_usb_console_source_boot import run as source_boot
from prepare_ack_native_bundle import prepare, IMAGE_SHA, CONFIG_SHA, DRAFT_DT_SHA
from build_native_load_client import build
from run_ack_native_jump import run as jump, SCOPE, RECEIVERS
from run_reset_payload_jump import geometry, sha

ROOT = Path(__file__).resolve().parents[1]
SCOPE_TWO_STAGE = 'ack-linux-native-two-stage-1'


def validate(a):
    p = read(a.policy)
    storage = getattr(a, 'storage_readonly', False)
    ramfix = getattr(a, 'ramfix', False)
    cinit = ramfix or getattr(a, 'cinit', False)
    combined = getattr(a, 'combined', False) or cinit
    end_to_end = getattr(a, 'usb_end_to_end', False)
    if storage and (not ramfix or end_to_end):raise ValueError('Storage mode requires RAM fix and its own functional receiver')
    if end_to_end and not ramfix:raise ValueError('USB end-to-end mode requires the RAM-fixed candidate')
    required_scope = 'ack-linux-storage-readonly-two-stage-6' if storage else 'ack-linux-usb-end-to-end-two-stage-5' if end_to_end else 'ack-linux-ramfix-two-stage-4' if ramfix else 'ack-linux-cinit-two-stage-3' if cinit else 'ack-linux-combined-two-stage-2' if combined else SCOPE_TWO_STAGE
    required_kind = 'ack-linux-storage-readonly-v6' if storage else 'ack-linux-ramfix-v4' if ramfix else 'ack-linux-cinit-v3' if cinit else 'ack-linux-combined-v2' if combined else 'ack-linux-v1'
    if (p.get('scope') != required_scope or p.get('target_kind') != required_kind or
            p.get('target_hardware_deadline_seconds') != 31 or p.get('target_nr_cpus') != 1 or
            p.get('target_cpu_limit') is not None):
        raise ValueError('Exact maintained-kernel RAM-boot policy required')
    image = a.kernel_package / 'Image'
    validate_source(p, a.source_package, a.linked_report, image, a.capture_report, a.helper, a.authorization)
    files = {a.kernel_package / 'resolved.config': 'target_config_sha256',
             a.kernel_package / 'draft.dtb': 'target_base_dtb_sha256',
             a.kernel_package / 'kernel-manifest.json': 'target_kernel_manifest_sha256',
             a.kernel_package / 'valethon_mailbox.o': 'guarded_mailbox_object_sha256',
             a.initramfs_package / 'report.json': 'target_initramfs_report_sha256',
             a.initramfs_package / 'initramfs.cpio.gz': 'target_initramfs_sha256',
             a.initramfs_package / 'trial-nonce-private.bin': 'target_nonce_sha256',
             a.entry_qualification: 'entry_qualification_sha256'}
    for path, key in files.items():
        if digest(path) != p[key]:
            raise ValueError('Reviewed ACK artifact differs: ' + key)
    if (p['target_image_sha256'] != IMAGE_SHA or p['target_config_sha256'] != CONFIG_SHA or
            p['target_base_dtb_sha256'] != DRAFT_DT_SHA or
            p['guarded_mailbox_object_sha256'] != '5b1dbcea1796d3a735d0e5f4cb69f80d0b65ab05ab1be5e362a8f2e04032462a'):
        raise ValueError('Pinned full ACK draft required')
    q = read(a.entry_qualification)
    if q.get('all_tests_passed') is not True or q.get('tests_skipped') != 0:
        raise ValueError('Completed entry-stub instruction qualification required')
    if q.get('entry_source_sha256') != digest(ROOT / 'projects/firetabs-android/native-kexec/ack_trampoline.S'):
        raise ValueError('Entry assembly changed after instruction qualification')
    if combined:
        if cinit:
            if storage:
                from verify_ack_storage_bundle import verify
            elif ramfix:
                from verify_ack_ramfix_bundle import verify
            else:
                from verify_ack_cinit_bundle import verify
        else:
            from verify_ack_combined_bundle import verify
        reference = getattr(a, 'combined_reference', None)
        if reference is None or digest(reference / 'report.json') != p['combined_reference_report_sha256']:
            raise ValueError('Exact prequalified combined reference required')
        verify_options = dict(nonce=(a.initramfs_package / 'trial-nonce-private.bin').read_bytes()) if cinit else {}
        if storage:
            result = verify(reference / 'report.json', a.kernel_package, a.initramfs_package, a.fdtget, **verify_options)
        else:
            result = verify(reference / 'report.json', a.kernel_package, a.fdtget, **verify_options)
        if result['instrumented_image_sha256'] != p['combined_target_image_sha256']:
            raise ValueError('Qualified Image differs')
        qualification = read(a.combined_qualification)
        if (digest(a.combined_qualification) != p['combined_qualification_sha256'] or
                qualification.get('all_tests_passed') is not True or qualification.get('tests_skipped') != 0 or
                qualification.get('image_sha256') != p['combined_target_image_sha256'] or
                any(digest(ROOT / path) != value for path,value in qualification.get('source_sha256', {}).items())):
            raise ValueError('Completed exact combined qualification required')
    return p


def run(a):
    p = validate(a)
    a.output.mkdir(mode=0o700)
    if a.authorization:
        os.close(os.open(str(a.authorization) + '.consumed', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600))
    d = LabADB(read(a.ssh_args)); linked = read(a.linked_report)
    child = None
    if a.authorization:
        child = a.output / 'source-authorization-private.json'
        private(child, dict(scope='usb-console-native-source-boot-1',
                           runner_sha256=digest(ROOT / 'scripts/run_native_source_boot.py'),
                           profile_runner_sha256=digest(ROOT / 'scripts/run_usb_console_source_boot.py'),
                           native_config_sha256=p['native_config_sha256'], candidate_sha256=p['source_boot_candidate_sha256'],
                           original_boot_sha256=BOOT_SHA, owner_approved=True, owner_available=True,
                           maximum_candidate_writes=1, maximum_restore_writes=1, maximum_reboots=1,
                           recovery_writes_allowed=False, experimental_jump_allowed=False))
    first = source_boot(d, a.lab_package, read(a.source_package / 'report.json'), linked,
                        a.output / 'source-boot', child)
    if not a.authorization:
        try:
            d.adb('root'); d.adb('wait-for-device'); geometry(d)
        finally:
            d.adb('unroot'); d.adb('wait-for-device')
            if b'uid=2000(' not in d.shell('id'):
                raise ValueError('Normal ADB not restored')
        return dict(read_only_preflight=first, retained_backend_geometry_verified=True)
    private(a.output / 'source-stage-summary.json', first)
    if not all(first.get(k) is True for k in ['complete', 'native_kernel_running',
                                             'original_boot_restored', 'normal_shell_restored']):
        return dict(source_boot=first, jump_executed=False)
    inputs = a.output / 'source-inputs-private'; inputs.mkdir(mode=0o700)
    try:
        d.adb('root'); d.adb('wait-for-device'); f = facts(d)
        if f['boot'] != BOOT_SHA or f['config'] != p['native_config_sha256'] or d.shell('cat /sys/kernel/kexec_loaded').strip() != b'0':
            raise ValueError('Fresh source/flash/load state differs')
        geometry(d)
        for name, command in [('live.dtb', 'cat /sys/firmware/fdt'), ('iomem.txt', 'cat /proc/iomem')]:
            path = inputs / name; path.write_bytes(d.shell(command)); path.chmod(0o600)
    finally:
        d.adb('unroot'); d.adb('wait-for-device')
        if b'uid=2000(' not in d.shell('id'):
            raise ValueError('Normal ADB not restored')
    bundle = a.output / 'target-private'; client = a.output / 'client-private'
    k, i = a.kernel_package, a.initramfs_package
    nonce = (i / 'trial-nonce-private.bin').read_bytes()
    storage = getattr(a, 'storage_readonly', False)
    ramfix = getattr(a, 'ramfix', False)
    cinit = ramfix or getattr(a, 'cinit', False)
    combined = getattr(a, 'combined', False) or cinit
    builder = prepare
    extra = {}
    if combined:
        if cinit:
            if ramfix:
                if storage:
                    from prepare_ack_storage_bundle import prepare as builder
                elif getattr(a, 'usb_end_to_end', False):
                    from prepare_ack_usb_end_to_end import prepare as builder
                else:
                    from prepare_ack_ramfix_bundle import prepare as builder
            else:
                from prepare_ack_cinit_bundle import prepare as builder
        else:
            from prepare_ack_combined_bundle import prepare as builder
        reference = read(a.combined_reference / 'report.json')
        extra = dict(system_map=(k / 'System.map').read_text(), trial_id=reference['trial_id'])
    m = builder((inputs / 'live.dtb').read_bytes(), (inputs / 'iomem.txt').read_text(),
                (k / 'draft.dtb').read_bytes(), (k / 'Image').read_bytes(), (k / 'resolved.config').read_bytes(),
                (i / 'initramfs.cpio.gz').read_bytes(), read(i / 'report.json'), nonce, linked,
                bundle, a.fdtget, a.fdtput, **extra)
    if combined and m['target_image_sha256'] != p['combined_target_image_sha256']:
        raise ValueError('Fresh bundle differs from VM-qualified Image')
    c = build(ROOT / 'projects/firetabs-android/native-kexec/load_client.c', bundle / 'report.json', client)
    files = {n: bundle / n for n in ['image.bin', 'metadata.bin', 'initrd.bin']}
    files.update({'native-load': client / 'native-load', 'source-acm-hold': a.helper,
                  'target-nonce-private.bin': i / 'trial-nonce-private.bin'})
    for name in set(RECEIVERS + ['capture_source_usb_console.py']):
        files[name] = ROOT / 'scripts' / name
    archive = a.output / 'target-package-private.tar.gz'
    with tarfile.open(archive, 'w:gz') as t:
        for name, path in files.items():
            t.add(path, arcname=name, recursive=False)
    destination = a.lab_package + '/ack-target-' + m['trial_id']
    code = ('import pathlib,tarfile,sys,json,hashlib\np=pathlib.Path(' + repr(destination) +
            ');p.mkdir(mode=0o700)\nwith tarfile.open(fileobj=sys.stdin.buffer,mode="r|gz") as t:'
            't.extractall(p,filter="data")\nprint(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() '
            'for f in p.iterdir()}))')
    with archive.open('rb') as f:
        staged = subprocess.run(d.args + ['python3 -c ' + shlex.quote(code)], stdin=f,
                                capture_output=True, timeout=120, check=True)
    if json.loads(staged.stdout) != {name: digest(path) for name, path in files.items()}:
        raise ValueError('Staged full ACK bundle differs')
    jump_options = dict(combined_kernel_package=a.kernel_package) if combined else {}
    if storage:jump_options['storage_component'] = a.initramfs_package
    capture = read(a.capture_report)
    before = jump(d, destination, bundle / 'report.json', client / 'build-result.json', linked,
                  a.output / 'jump-preflight', nonce, capture, **jump_options)
    if before.get('complete') is not True:
        raise ValueError('ACK native preflight failed')
    auth = a.output / 'jump-authorization-private.json'
    child_scope = 'ack-linux-native-storage-readonly-jump-6' if storage else 'ack-linux-native-ramfix-jump-4' if ramfix else 'ack-linux-native-cinit-jump-3' if cinit else 'ack-linux-native-combined-jump-2' if combined else SCOPE
    child_extra = dict(combined_verifier_sha256=digest(ROOT / ('scripts/verify_ack_storage_bundle.py' if storage else 'scripts/verify_ack_ramfix_bundle.py' if ramfix else 'scripts/verify_ack_cinit_bundle.py' if cinit else 'scripts/verify_ack_combined_bundle.py'))) if combined else {}
    private(auth, dict(scope=child_scope, runner_sha256=digest(ROOT / 'scripts/run_ack_native_jump.py'),
                       manifest_sha256=digest(bundle / 'report.json'), client_sha256=c['client_sha256'],
                       target_image_sha256=m['target_image_sha256'], target_config_sha256=CONFIG_SHA,
                       target_nonce_sha256=sha(nonce), source_config_sha256=p['native_config_sha256'],
                       source_capture_report_sha256=sha(json.dumps(capture, sort_keys=True).encode()),
                       source_capture_manager_sha256=digest(ROOT / 'scripts/source_usb_console_trial.py'),
                       receiver_sha256={name: digest(ROOT / 'scripts' / name) for name in RECEIVERS},
                       owner_approved=True, owner_available=True, maximum_loads=1, maximum_jump_requests=1,
                       target_hardware_deadline_seconds=31, boot_writes_allowed=False,
                       post_jump_reboot_commands_allowed=False, bounded_read_only_return_poll_allowed=True, **child_extra))
    return dict(source_boot=first, jump=jump(d, destination, bundle / 'report.json', client / 'build-result.json',
                                           linked, a.output / 'jump', nonce, capture, auth, **jump_options))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['policy', 'ssh-args', 'source-package', 'linked-report', 'kernel-package', 'initramfs-package',
                 'entry-qualification', 'capture-report', 'helper', 'output', 'fdtget', 'fdtput']:
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--lab-package', required=True)
    parser.add_argument('--authorization', type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--combined', action='store_true')
    mode.add_argument('--cinit', action='store_true')
    mode.add_argument('--ramfix', action='store_true')
    parser.add_argument('--usb-end-to-end', action='store_true')
    parser.add_argument('--storage-readonly', action='store_true')
    parser.add_argument('--combined-reference', type=Path)
    parser.add_argument('--combined-qualification', type=Path)
    a = parser.parse_args()
    try:
        result = run(a); print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps(dict(failure_kind=type(e).__name__, automatic_retry=False)))
        raise SystemExit(1)
