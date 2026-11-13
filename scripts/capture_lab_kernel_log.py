#!/usr/bin/env python3
"""Linux private lab receiver. Default validates inputs; explicit --arm opens one exact port."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import termios
import time
from kernel_log_protocol import receive_fd
from capture_usb_acm_status import host_raw_settings


def private_bytes(path, maximum):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        s = os.fstat(fd)
        if (not stat.S_ISREG(s.st_mode) or s.st_uid != os.geteuid()
                or stat.S_IMODE(s.st_mode) not in [0o400, 0o600] or s.st_nlink != 1
                or not 0 < s.st_size <= maximum):
            raise ValueError('Bounded owned private regular input required')
        data = os.read(fd, maximum + 1)
        if len(data) != s.st_size:
            raise ValueError('Private input changed or truncated')
        return data
    finally:
        os.close(fd)


def validate(plan, report, nonce):
    if (plan.get('purpose') != 'first-normal-log-bringup' or plan.get('candidate_sha256') != report.get('partition_sha256')
            or not re.fullmatch(r'[0-9a-f]{64}', plan.get('candidate_sha256', ''))
            or len(nonce) != 32 or not any(nonce)
            or hashlib.sha256(nonce).hexdigest() != report.get('nonce_sha256')):
        raise ValueError('Exact candidate/nonce/first-trial contract required')
    if not re.fullmatch(r'[0-9]{1,3}-[0-9]{1,3}(?:\.[0-9]{1,3}){0,6}', plan.get('physical_usb_path', '')):
        raise ValueError('Explicit Linux physical USB path required')
    if plan.get('usb_id') != '1209:0001' or plan.get('interface') != '00':
        raise ValueError('Reviewed private test descriptor/interface required')
    if not isinstance(plan.get('wait_seconds'), int) or not 1 <= plan['wait_seconds'] <= 900:
        raise ValueError('Bounded owner-trip wait required')
    return plan


def endpoint_identity(tty, plan, sysroot=Path('/sys')):
    path = sysroot / 'class/tty' / tty / 'device'
    if not re.fullmatch(r'ttyACM[0-9]{1,6}', tty) or not path.exists():
        raise ValueError('Linux ACM interface required')
    interface = path.resolve(strict=True)
    usb = next((p for p in interface.parents if p.name == plan['physical_usb_path']), None)
    if usb is None:
        return None
    if (usb / 'idVendor').read_text().strip() != '1209' or (usb / 'idProduct').read_text().strip() != '0001':
        return None
    if ((interface / 'bInterfaceNumber').read_text().strip() != plan['interface']
            or (interface / 'driver').resolve(strict=True).name != 'cdc_acm'):
        raise ValueError('Unexpected interface at selected physical device')
    major, minor = map(int, (sysroot / 'class/tty' / tty / 'dev').read_text().strip().split(':'))
    return {'sysfs': str(interface), 'rdev': os.makedev(major, minor), 'endpoint': '/dev/' + tty}


def raw_settings(attrs):
    result = [0, 0, termios.CS8 | termios.CREAD | termios.CLOCAL, 0,
              termios.B9600, termios.B9600, list(attrs[6])]
    result[6][termios.VMIN] = 1
    result[6][termios.VTIME] = 0
    host_raw_settings(result)
    return result


def capture(plan, nonce, output):
    # This action is only run after owner review/start. No device boot/write commands.
    output.mkdir(mode=0o700, parents=False, exist_ok=False)
    directory = os.open(output, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    raw = os.open('raw.bin', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                  0o600, dir_fd=directory)
    os.fchmod(raw, 0o600)
    os.fsync(directory)  # Durable directory entry before any identity ACK.
    port = None
    original = None
    result = {'complete': False, 'device_qualified': False, 'failure': None, 'cleanup': [],
              'failure_stage': None, 'endpoint_selected': False, 'port_opened': False}
    stage = 'waiting_for_port'
    try:
        end = time.monotonic() + plan['wait_seconds']
        selected = None
        while time.monotonic() < end:
            matches = [identity for tty in Path('/sys/class/tty').glob('ttyACM*')
                       if (identity := endpoint_identity(tty.name, plan)) is not None]
            if len(matches) > 1:
                raise ValueError('Ambiguous interfaces at selected physical device')
            if matches:
                selected = matches[0]
                result['endpoint_selected'] = True
                break
            time.sleep(0.1)
        if selected is None:
            raise ValueError('Bounded physical-port wait expired')
        # One open only, no retry on disconnect/failed trial.
        stage = 'opening_port'
        port = os.open(selected['endpoint'], os.O_RDWR | os.O_NONBLOCK | os.O_NOCTTY | os.O_NOFOLLOW | os.O_CLOEXEC)
        result['port_opened'] = True
        stage = 'validating_opened_identity'
        s = os.fstat(port)
        after = endpoint_identity(Path(selected['endpoint']).name, plan)
        if not stat.S_ISCHR(s.st_mode) or s.st_rdev != selected['rdev'] or after != selected:
            raise ValueError('Physical endpoint changed during open')
        stage = 'claiming_exclusive_port'
        fcntl.ioctl(port, termios.TIOCEXCL)
        stage = 'configuring_raw_tty'
        original = termios.tcgetattr(port)
        termios.tcsetattr(port, termios.TCSANOW, raw_settings(original))
        host_raw_settings(termios.tcgetattr(port))
        stage = 'receiving_wire'
        result.update(receive_fd(port, raw, nonce, time.monotonic() + 30))
    except (Exception, KeyboardInterrupt) as error:
        result['complete'] = False
        result['failure'] = type(error).__name__
        result['failure_stage'] = stage
        if isinstance(error, OSError):
            result['error_number'] = error.errno
    finally:
        if port is not None:
            if original is not None:
                try:
                    termios.tcsetattr(port, termios.TCSANOW, original)
                except OSError:
                    result['cleanup'].append('termios-restore-failed')
            try:
                os.close(port)
            except OSError:
                result['cleanup'].append('port-close-failed')
        try:
            os.fsync(raw)
        except OSError:
            result['cleanup'].append('raw-sync-failed')
        os.close(raw)
        if result['cleanup']:
            result['complete'] = False
        receipt = os.open('receipt.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                          0o600, dir_fd=directory)
        with os.fdopen(receipt, 'w') as f:
            os.fchmod(f.fileno(), 0o600)
            json.dump(result, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.fsync(directory)
        os.close(directory)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['plan', 'candidate-report', 'nonce', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--arm', action='store_true')
    a = p.parse_args()
    try:
        plan = json.loads(private_bytes(a.plan, 4096))
        report = json.loads(private_bytes(a.candidate_report, 65536))
        nonce = private_bytes(a.nonce, 32)
        validate(plan, report, nonce)
        if not a.arm:
            print(json.dumps({'input_preflight_passed': True, 'armed': False, 'port_opened': False}))
            return
        result = capture(plan, nonce, a.output)
        print(json.dumps(result))
        if not result['complete']:
            p.exit(2)
    except (OSError, ValueError, KeyError, TypeError):
        p.exit(2, 'Private lab capture stopped; inspect private receipt if created.\n')


if __name__ == '__main__':
    main()
