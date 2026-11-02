#!/usr/bin/env python3
"""Prepared one-trip normal logging/return supervisor. Default preflight only.

No boot write/reboot/failure injection. A separate reviewed candidate must already
be installed. Explicit arm permits one original FACTORYM helper after the normal
boot observation guard and owner's manual shutdown/reconnection. Never StageA retry.
"""
import argparse
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
from bounded_recovery_entry import verify_sources, choose_port, scan_ports, launch_helper
from capture_lab_kernel_log import private_bytes, validate
from restore_diagnostic_boot import Adb, preflight, sha, update_receipt
from write_lab_boot_candidate import candidate_manifest


def lifecycle(present, capture, scan, launch, clock=time.monotonic, sleep=time.sleep):
    if not present():
        raise ValueError('Expected initial recovery USB identity absent')
    travel_end = clock() + 600
    while present():
        if clock() >= travel_end:
            raise TimeoutError('Owner travel/manual boot window expired')
        sleep(.1)
    boot_started = clock()
    captured = capture()  # One independently bounded process, maximum80 seconds.
    if clock() > boot_started + 85:
        raise TimeoutError('Capture supervisor exceeded entry budget')
    # Ignore initial normal-boot preloader enumeration. The owner waits90 seconds
    # before disconnecting/holding power; only their later reconnection may launch.
    while clock() < boot_started + 90:
        sleep(.1)
    deadline = clock() + 300
    while clock() < deadline:
        port = scan()
        if port is not None:
            return {'capture': captured, 'helper_returncode': launch(port, 90)}
        sleep(.05)
    raise TimeoutError('Manual shutdown/reconnection window expired')


def run_capture(plan, report, nonce, output):
    command = [sys.executable, '-E', '-s', str(Path(__file__).with_name('capture_lab_kernel_log.py')),
               '--plan', str(plan), '--candidate-report', str(report), '--nonce', str(nonce),
               '--output', str(output), '--arm']
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    try:
        stdout, stderr = proc.communicate(timeout=80)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        stdout, stderr = proc.communicate(timeout=5)
        return {'returncode': None, 'complete': False, 'timeout': True}
    # Child deliberately emits no selectors or raw records. Full output stays private.
    if len(stdout) > 4096 or len(stderr) > 4096:
        raise ValueError('Capture subprocess output budget exceeded')
    return {'returncode': proc.returncode, 'complete': proc.returncode == 0,
            'receipt_exists': (output / 'receipt.json').is_file()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['plan', 'candidate-report', 'nonce', 'output', 'modules', 'initial-usb-identity',
                 'selector-file', 'candidate', 'original-boot', 'rollback-manifest', 'receipt']:
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--arm-once', action='store_true')
    a = p.parse_args()
    result = {'armed': False, 'recovery_observed': False, 'failed_load_qualified': False,
              'device_write_performed': False, 'automatic_reboot': False}
    claimed = False
    stage = 'input_and_device_preflight'
    try:
        plan = json.loads(private_bytes(a.plan, 4096))
        report = json.loads(private_bytes(a.candidate_report, 65536))
        nonce = private_bytes(a.nonce, 32)
        validate(plan, report, nonce)
        if plan['wait_seconds'] != 45:
            raise ValueError('First-trial entry window must be45 seconds')
        identity = json.loads(private_bytes(a.initial_usb_identity, 4096))
        if (identity.get('path') != plan['physical_usb_path']
                or not re.fullmatch(r'[0-9a-f]{4}', identity.get('vendor', ''))
                or not re.fullmatch(r'[0-9a-f]{4}', identity.get('product', ''))):
            raise ValueError('Exact initial recovery USB identity required')
        verify_sources(a.modules)
        for path in [a.candidate, a.original_boot]:
            if path.is_symlink() or not path.is_file() or path.stat().st_size != 16777216:
                raise ValueError('Exact full-size regular assets required')
        candidate = a.candidate.read_bytes()
        rollback = json.loads(a.rollback_manifest.read_text())
        manifest = candidate_manifest(candidate, report, a.original_boot.read_bytes(), rollback)
        selector = json.loads(private_bytes(a.selector_file, 4096))['selector']
        if not isinstance(selector, str) or not selector or selector.startswith('-'):
            raise ValueError('Explicit selected ADB identity required')
        adb = Adb('adb', selector)
        preflight(adb, candidate, manifest, sha(candidate))
        device = Path('/sys/bus/usb/devices') / identity['path']
        def present():
            try:
                return ((device / 'idVendor').read_text().strip() == identity['vendor']
                        and (device / 'idProduct').read_text().strip() == identity['product'])
            except FileNotFoundError:
                return False
        if not present():
            raise ValueError('Initial physical USB identity differs')
        if not a.arm_once:
            print(json.dumps({**result, 'input_and_device_preflight': 'passed'}))
            return
        with a.receipt.open('x') as f:
            os.fchmod(f.fileno(), 0o600)
            result.update(armed=True, candidate_sha256=sha(candidate))
            json.dump(result, f)
            f.flush()
            os.fsync(f.fileno())
        claimed = True
        stage = 'owner_boot_capture_and_return'
        result.update(lifecycle(present,
                               lambda: run_capture(a.plan, a.candidate_report, a.nonce, a.output),
                               lambda: choose_port(scan_ports(), identity['path']),
                               lambda port, seconds: launch_helper(a.modules, port, seconds,
                                                                  a.receipt.with_suffix('.helper-private.log'))))
        stage = 'checking_helper_exit'
        if result['helper_returncode'] != 0:
            raise ValueError('One-shot return helper did not succeed')
        stage = 'waiting_for_recovery_adb'
        adb.run(['wait-for-recovery'])
        stage = 'validating_returned_recovery'
        preflight(adb, candidate, manifest, sha(candidate))
        result['recovery_observed'] = True
        result['candidate_still_installed'] = True
    except (ValueError, KeyError, OSError, TimeoutError, subprocess.SubprocessError, KeyboardInterrupt) as error:
        result['failure'] = type(error).__name__
        result['failure_stage'] = stage
        if isinstance(error, OSError):
            result['error_number'] = error.errno
    finally:
        if claimed:
            update_receipt(a.receipt, result)
    print(json.dumps(result))
    if not result['recovery_observed']:
        p.exit(2)


if __name__ == '__main__':
    main()
