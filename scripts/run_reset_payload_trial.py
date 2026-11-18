#!/usr/bin/env python3
"""One protected source boot/restore and one attributable reset-target jump."""
import argparse
import hashlib
import json
import os
import shlex
import subprocess
import tarfile
from pathlib import Path

from run_source_usb_trial import validate as validate_source, private
from run_pstore_warm_reboot import LabADB
from run_native_source_boot import facts, BOOT_SHA
from run_usb_console_source_boot import run as source_boot
from build_reset_payload import validate as validate_payload
from prepare_reset_jump_bundle import prepare_reset
from build_native_load_client import build
from run_reset_payload_jump import run as jump, SCOPE, geometry, sha

ROOT = Path(__file__).resolve().parents[1]
SCOPE_TWO_STAGE = 'minimal-reset-payload-two-stage-trial-1'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def validate(a):
    p = read(a.policy)
    payload = read(a.payload_report)
    validate_payload(a.image.read_bytes(), payload)
    if p.get('scope') != SCOPE_TWO_STAGE or p.get('target_kind') != 'reset-payload-v1':
        raise ValueError('Distinct reset-target two-stage policy required')
    if p.get('target_cpu_limit') is not None or p.get('source_cpu_shutdown_before_devices') is not True:
        raise ValueError('Use proven source ordering without extra target CPU experiments')
    if p.get('failure_policy') != 'pivot_after_one_failed_or_inconclusive_jump':
        raise ValueError('One-shot reset experiment must commit to the fallback')
    if digest(a.payload_report) != p['reset_payload_report_sha256']:
        raise ValueError('Exact reset-payload report required')
    validate_source(p, a.source_package, a.linked_report, a.image,
                    a.capture_report, a.helper, a.authorization)
    q = read(a.emulation_report)
    if (digest(a.emulation_report) != p['reset_emulation_report_sha256'] or
            q.get('source_sha256') != payload['source_sha256'] or
            q.get('qualified_canonical_image_sha256') != p['qualified_canonical_image_sha256'] or
            q.get('all_required_tests_passed') is not True or
            q.get('tests_skipped') != 0):
        raise ValueError('Exact, completed instruction-level qualification required')
    return p, payload


def run(a):
    policy, payload = validate(a)
    a.output.mkdir(mode=0o700)
    if a.authorization:
        os.close(os.open(str(a.authorization) + '.consumed', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600))
    d = LabADB(read(a.ssh_args))
    linked = read(a.linked_report)
    report = read(a.source_package / 'report.json')
    child = None
    if a.authorization:
        child = a.output / 'source-authorization-private.json'
        private(child, dict(scope='usb-console-native-source-boot-1',
                           runner_sha256=digest(ROOT / 'scripts/run_native_source_boot.py'),
                           profile_runner_sha256=digest(ROOT / 'scripts/run_usb_console_source_boot.py'),
                           native_config_sha256=policy['native_config_sha256'],
                           candidate_sha256=policy['source_boot_candidate_sha256'], original_boot_sha256=BOOT_SHA,
                           owner_approved=True, owner_available=True, maximum_candidate_writes=1,
                           maximum_restore_writes=1, maximum_reboots=1, recovery_writes_allowed=False,
                           experimental_jump_allowed=False))
    first = source_boot(d, a.lab_package, report, linked, a.output / 'source-boot', child)
    if not a.authorization:
        # Check existing backend geometry without arming or writing it.
        try:
            d.adb('root'); d.adb('wait-for-device')
            geometry(d)
        finally:
            d.adb('unroot'); d.adb('wait-for-device')
            if b'uid=2000(' not in d.shell('id'):
                raise ValueError('Normal ADB not restored')
        return dict(read_only_preflight=first, reset_geometry_verified=True)
    private(a.output / 'source-stage-summary.json', first)
    if not all(first.get(k) is True for k in ['complete', 'native_kernel_running',
                                             'original_boot_restored', 'normal_shell_restored']):
        return dict(source_boot=first, jump_executed=False)
    inputs = a.output / 'source-inputs-private'
    inputs.mkdir(mode=0o700)
    try:
        d.adb('root'); d.adb('wait-for-device')
        f = facts(d)
        if (f['boot'] != BOOT_SHA or f['config'] != policy['native_config_sha256'] or
                d.shell('cat /sys/kernel/kexec_loaded').strip() != b'0'):
            raise ValueError('Fresh source/flash/load state differs')
        geometry(d)
        for name, command in [('live.dtb', 'cat /sys/firmware/fdt'), ('iomem.txt', 'cat /proc/iomem')]:
            p = inputs / name
            p.write_bytes(d.shell(command))
            p.chmod(0o600)
    finally:
        d.adb('unroot'); d.adb('wait-for-device')
        if b'uid=2000(' not in d.shell('id'):
            raise ValueError('Normal ADB not restored')
    bundle, client = a.output / 'target-private', a.output / 'client-private'
    m = prepare_reset((a.source_package / 'original-boot.img').read_bytes(),
                      (inputs / 'live.dtb').read_bytes(), (inputs / 'iomem.txt').read_text(),
                      bundle, a.fdtget, a.fdtput, a.image.read_bytes(), payload, linked)
    c = build(ROOT / 'projects/firetabs-android/native-kexec/load_client.c', bundle / 'report.json', client)
    files = {n: bundle / n for n in ['image.bin', 'metadata.bin', 'initrd.bin']}
    files.update({'native-load': client / 'native-load', 'source-acm-hold': a.helper})
    for name in ['capture_source_usb_console.py', 'capture_live_acm_probe.py']:
        files[name] = ROOT / 'scripts' / name
    archive = a.output / 'target-package-private.tar.gz'
    with tarfile.open(archive, 'w:gz') as t:
        for name, path in files.items():
            t.add(path, arcname=name, recursive=False)
    dest = a.lab_package + '/reset-target-' + m['trial_id']
    code = ('import pathlib,tarfile,sys,json,hashlib\np=pathlib.Path(' + repr(dest) +
            ');p.mkdir(mode=0o700)\nwith tarfile.open(fileobj=sys.stdin.buffer,mode="r|gz") as t:'
            't.extractall(p,filter="data")\nprint(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() '
            'for f in p.iterdir()}))')
    with archive.open('rb') as h:
        staged = subprocess.run(d.args + ['python3 -c ' + shlex.quote(code)], stdin=h,
                                capture_output=True, timeout=120, check=True)
    if json.loads(staged.stdout) != {name: digest(path) for name, path in files.items()}:
        raise ValueError('Staged reset files differ')
    capture = read(a.capture_report)
    preflight = jump(d, dest, bundle / 'report.json', client / 'build-result.json', linked,
                     a.output / 'jump-preflight', payload, capture)
    if preflight.get('complete') is not True:
        raise ValueError('Reset-jump preflight failed')
    auth = a.output / 'jump-authorization-private.json'
    private(auth, dict(scope=SCOPE, runner_sha256=digest(ROOT / 'scripts/run_reset_payload_jump.py'),
                       manifest_sha256=digest(bundle / 'report.json'), client_sha256=c['client_sha256'],
                       target_image_sha256=policy['target_image_sha256'],
                       native_config_sha256=policy['native_config_sha256'],
                       reset_payload_report_sha256=m['reset_payload_report_sha256'],
                       source_capture_report_sha256=sha(json.dumps(capture, sort_keys=True).encode()),
                       source_capture_manager_sha256=digest(ROOT / 'scripts/source_usb_console_trial.py'),
                       owner_approved=True, owner_available=True, maximum_loads=1, maximum_jump_requests=1,
                       boot_writes_allowed=False, automatic_reboot_commands_allowed=False,
                       bounded_read_only_return_poll_allowed=True))
    return dict(source_boot=first, jump=jump(d, dest, bundle / 'report.json', client / 'build-result.json',
                                           linked, a.output / 'jump', payload, capture, auth))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['policy', 'ssh-args', 'source-package', 'linked-report', 'image', 'payload-report',
                 'emulation-report', 'capture-report', 'helper', 'output', 'fdtget', 'fdtput']:
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--lab-package', required=True)
    p.add_argument('--authorization', type=Path)
    a = p.parse_args()
    try:
        result = run(a)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps(dict(failure_kind=type(e).__name__, automatic_retry=False)))
        raise SystemExit(1)
