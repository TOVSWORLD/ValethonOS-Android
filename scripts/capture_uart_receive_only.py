#!/usr/bin/env python3
"""Bounded POSIX UART capture. Wire only a qualified board TX to adapter RX/GND.

No device writes, input flush, modem-line ioctl, reboot or firmware operations.
Opening/configuring an adapter can change its output pins: physically leave
adapter TX, VCC, RTS and DTR disconnected from the tablet.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import select
import stat
import termios
import time

MAX_BYTES = 16 * 1024 * 1024


def capture(port, output, baud=921600, seconds=120, max_bytes=MAX_BYTES, ready=None):
    if baud not in (115200, 921600) or not hasattr(termios, 'B' + str(baud)):
        raise ValueError('Host must provide requested native baud constant; use Linux for 921600')
    if not math.isfinite(seconds) or not 0 < seconds <= 300 or not 1 <= max_bytes <= MAX_BYTES:
        raise ValueError('Bounded duration and byte limit required')
    speed = getattr(termios, 'B' + str(baud))
    output = Path(output)
    output.mkdir(mode=0o700)
    raw_fd = os.open(output / 'uart-private.bin', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    fd = None
    previous = None
    result = dict(scope='Receive-only UART capture; interpretation requires qualified wiring and baseline',
                  baud=baud, data_bits=8, parity='none', stop_bits=1, flow_control='none',
                  seconds_limit=seconds, bytes_limit=max_bytes, bytes=0, sha256=None,
                  port_path_sha256=hashlib.sha256(os.fsencode(port)).hexdigest(),
                  serial_write_calls=0, input_flushed=False, tablet_commands=False,
                  raw_fsynced=False, settings_restored=False, reason='not-started',
                  uart_qualified=False, linux_boot_proven=False)
    digest = hashlib.sha256()
    error = None
    started = time.monotonic()
    try:
        fd = os.open(port, os.O_RDONLY | os.O_NOCTTY | os.O_NONBLOCK | getattr(os, 'O_CLOEXEC', 0))
        if not stat.S_ISCHR(os.fstat(fd).st_mode):
            raise ValueError('Character-device UART required')
        previous = termios.tcgetattr(fd)
        attrs = [*previous[:6], list(previous[6])]
        attrs[0] = termios.IGNBRK
        attrs[1] = attrs[3] = 0
        attrs[2] &= ~(termios.CSIZE | termios.PARENB | termios.CSTOPB | termios.HUPCL |
                      getattr(termios, 'PARODD', 0) | getattr(termios, 'CRTSCTS', 0))
        attrs[2] |= termios.CS8 | termios.CREAD | termios.CLOCAL
        attrs[4] = attrs[5] = speed
        attrs[6][termios.VMIN] = attrs[6][termios.VTIME] = 0
        termios.tcsetattr(fd, termios.TCSANOW, attrs)
        # Persist files/directory before asking the owner to start a normal boot.
        os.fsync(raw_fd)
        d = os.open(output, os.O_RDONLY)
        try:
            os.fsync(d)
        finally:
            os.close(d)
        started = time.monotonic()
        if ready:
            ready()
        result['reason'] = 'deadline'
        while time.monotonic() - started < seconds:
            remaining = max_bytes - result['bytes']
            if not remaining:
                result['reason'] = 'byte-limit'
                break
            readable, _, _ = select.select([fd], [], [], min(0.25, max(0, seconds - (time.monotonic() - started))))
            if not readable:
                continue
            try:
                data = os.read(fd, min(65536, remaining))
            except BlockingIOError:
                continue
            if not data:
                result['reason'] = 'port-closed'
                break
            view = memoryview(data)
            while view:
                n = os.write(raw_fd, view)
                if n <= 0:
                    raise OSError('Capture file write made no progress')
                view = view[n:]
            digest.update(data)
            result['bytes'] += len(data)
            os.fsync(raw_fd)
    except Exception as e:
        result['reason'] = 'failure'
        result['failure_kind'] = type(e).__name__
        error = e
    finally:
        if fd is not None:
            try:
                if previous is not None:
                    termios.tcsetattr(fd, termios.TCSANOW, previous)
                    restored = termios.tcgetattr(fd)
                    # PENDIN is a driver-maintained input-reprocessing flag, not
                    # a configured framing/flow/echo setting (notably on macOS).
                    restored[3] &= ~getattr(termios, 'PENDIN', 0)
                    expected = [*previous[:6], list(previous[6])]
                    expected[3] &= ~getattr(termios, 'PENDIN', 0)
                    result['settings_restored'] = restored == expected
            except (OSError, termios.error):
                result['settings_restore_unconfirmed'] = True
            finally:
                os.close(fd)
        try:
            os.fsync(raw_fd)
            result['raw_fsynced'] = True
        finally:
            os.close(raw_fd)
        result.update(sha256=digest.hexdigest(), elapsed_seconds=round(time.monotonic() - started, 3),
                      silence_inconclusive=result['bytes'] == 0)
        with (output / 'report.json').open('x') as f:
            os.chmod(f.name, 0o600)
            json.dump(result, f, indent=2)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
    if error:
        raise error
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--baud', type=int, choices=[115200, 921600], default=921600)
    p.add_argument('--seconds', type=float, default=120)
    a = p.parse_args()
    result = capture(a.port, a.output, a.baud, a.seconds,
                     ready=lambda: print('UART_CAPTURE_READY', flush=True))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
