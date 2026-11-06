#!/usr/bin/env python3
"""Linux-only, explicit-arm supervisor for original FACTORYM; default is preflight."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

HASHES = {
    'handshake2.py': '057db6e4051c0b241b4835d41db4f740d50c228abf9d342217746e1761a2653e',
    'common.py': '672d56ba73009b0993ff2aa3b79d2547ae7dd24ed0358eb7e84888e534bf952c',
    'logger.py': '6edcab194d402f24805538ab5f16f4331eff6de6bbc5cd760baad7f34961e69d',
}


def verify_sources(modules):
    for name, expected in HASHES.items():
        if hashlib.sha256((modules / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Original helper identity mismatch')


def usb_parent(path):
    for p in [path, *path.parents]:
        if (p / 'idVendor').is_file() and (p / 'idProduct').is_file():
            return p
    return None


def choose_port(candidates, expected_path):
    # candidates are read-only sysfs metadata; never probe/open arbitrary tty nodes.
    mtk = [c for c in candidates if c['vendor'] == '0e8d']
    if not mtk:
        return None
    if len(mtk) != 1:
        raise ValueError('Ambiguous MediaTek interfaces')
    c = mtk[0]
    if c['usb_path'] != expected_path or c['product'] != '2000':
        raise ValueError('Unexpected MediaTek USB identity')
    if not re.fullmatch(r'/dev/ttyACM[0-9]+', c['port']):
        raise ValueError('Unexpected serial node')
    return c['port']


def scan_ports(sys_tty=Path('/sys/class/tty')):
    rows = []
    for tty in sys_tty.glob('ttyACM*'):
        p = usb_parent((tty / 'device').resolve())
        if p:
            rows.append({'port': '/dev/' + tty.name, 'usb_path': p.name,
                         'vendor': (p / 'idVendor').read_text().strip(),
                         'product': (p / 'idProduct').read_text().strip()})
    return rows


def wait_then_launch(present, scan, launch, clock=time.monotonic, sleep=time.sleep):
    # Three distinct bounds: travel, manual shutdown/reconnection, then helper.
    # Manual power-off can exceed90s; do not consume handshake time before USB exists.
    if not present():
        raise ValueError('Expected connected Android USB device is absent')
    deadline = clock() + 600
    while present():
        if clock() >= deadline:
            raise TimeoutError('Travel/disconnection window expired')
        sleep(.1)
    deadline = clock() + 300
    while clock() < deadline:
        port = scan()
        if port is not None:
            return launch(port, 90)  # exactly one bounded helper call, never retry
        sleep(.05)
    raise TimeoutError('Manual shutdown/reconnection window expired')


def launch_helper(modules, port, seconds, log):
    verify_sources(modules)
    # Separate process group ensures timeout kills helper and any descendants.
    # Load pinned source bytes directly: isolated Python omits local import paths
    # and ignores user/PYTHONPATH configuration and stale local bytecode.
    bootstrap = """import sys, types, pathlib
root=pathlib.Path(sys.argv[1])
port=sys.argv[2]
for name in ('logger','common'):
    module=types.ModuleType(name)
    sys.modules[name]=module
    exec(compile((root/(name+'.py')).read_bytes(),name+'.py','exec'),module.__dict__)
sys.argv=['handshake2.py','FACTORYM',port]
exec(compile((root/'handshake2.py').read_bytes(),'handshake2.py','exec'),{'__name__':'__main__'})
"""
    fd = os.open(str(log), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as output:
        proc = subprocess.Popen([sys.executable, '-I', '-c', bootstrap,
                                 str(modules), port], cwd=modules,
                                stdout=output, stderr=subprocess.STDOUT,
                                start_new_session=True)
        try:
            return proc.wait(timeout=seconds)
        finally:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--modules', required=True, type=Path)
    parser.add_argument('--usb-identity-private', required=True, type=Path)
    parser.add_argument('--receipt-private', required=True, type=Path)
    parser.add_argument('--arm-once', action='store_true')
    args = parser.parse_args()
    modules = args.modules.resolve()
    verify_sources(modules)
    identities = json.loads(args.usb_identity_private.read_text())
    if len(identities) != 1:
        raise ValueError('Expected exactly one prior authorized USB identity')
    identity = identities[0]
    if not re.fullmatch(r'[0-9]+-[0-9]+(?:\.[0-9]+)*', identity['path']):
        raise ValueError('Invalid physical USB path')
    device = Path('/sys/bus/usb/devices') / identity['path']

    def present():
        try:
            return ((device / 'idVendor').read_text().strip() == identity['vendor'] and
                    (device / 'idProduct').read_text().strip() == identity['product'])
        except FileNotFoundError:
            return False

    if not present():
        raise ValueError('Initial Android USB identity absent or changed')
    # Preflight is safe by default: no serial open, helper or device mode change.
    if not args.arm_once:
        print('PREFLIGHT_OK; NOT_ARMED')
        return
    receipt = args.receipt_private
    # Exclusive claim prevents an automatic second invocation using this receipt.
    fd = os.open(str(receipt), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as out:
        json.dump({'status': 'armed', 'recovery_observed': False}, out)
    result = {'status': 'stopped', 'recovery_observed': False, 'failed_load_qualified': False}
    try:
        rc = wait_then_launch(present,
                              lambda: choose_port(scan_ports(), identity['path']),
                              lambda port, seconds: launch_helper(modules, port, seconds,
                                                                  receipt.with_suffix('.log')))
        result.update(status='helper_exited', helper_returncode=rc)
    except (ValueError, TimeoutError, subprocess.TimeoutExpired, OSError) as exc:
        result['error_type'] = type(exc).__name__
        result['stop_reason'] = (str(exc) if isinstance(exc, (ValueError, TimeoutError))
                                 else 'Helper deadline expired'
                                 if isinstance(exc, subprocess.TimeoutExpired)
                                 else 'Host operation failed')
    finally:
        receipt.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    if result.get('helper_returncode') != 0:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
