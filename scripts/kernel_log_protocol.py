"""Bounded trial log wire protocol and durable host receiver.

Transport is caller-owned. This module never opens a device, configures USB,
changes admission, injects failure or reboots. Raw records and nonce stay private.
"""
import hashlib
import fcntl
import os
import select
import stat
import struct
import termios
import time

MAGIC = b'VLOG0001'
ACK = b'VACK0001'
MAX_RECORD = 8192
MAX_TOTAL = 256 * 1024


def receive_fd(transport_fd, raw_fd, nonce, deadline):
    """Use a caller-owned, already configured nonblocking raw duplex TTY.

    No port open/discovery, termios changes, admission override or descriptor
    close. Call only under the separately reviewed exact device trial contract.
    """
    flags = fcntl.fcntl(transport_fd, fcntl.F_GETFL)
    if not os.isatty(transport_fd) or not flags & os.O_NONBLOCK:
        raise ValueError('Caller-owned nonblocking TTY required')
    attrs = termios.tcgetattr(transport_fd)
    if (attrs[0] or attrs[1] or attrs[3]
            or attrs[2] & termios.CSIZE != termios.CS8
            or not attrs[2] & termios.CREAD or not attrs[2] & termios.CLOCAL
            or attrs[2] & (termios.HUPCL | getattr(termios, 'CRTSCTS', 0))
            or attrs[4:6] != [termios.B9600, termios.B9600]):
        raise ValueError('Previously qualified raw9600/8-bit/no-flow TTY required')

    def wait(write):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ValueError('Capture deadline exceeded')
        readable, writable, _ = select.select([] if write else [transport_fd],
                                             [transport_fd] if write else [], [], remaining)
        if not (writable if write else readable):
            raise ValueError('Capture deadline exceeded')

    def read(size):
        for _ in range(1024):
            wait(False)
            try:
                return os.read(transport_fd, size)
            except (InterruptedError, BlockingIOError):
                continue
        raise ValueError('Transport read retry budget exceeded')

    def acknowledge(data):
        view = memoryview(data)
        for _ in range(1024):
            if not view:
                return
            wait(True)
            try:
                count = os.write(transport_fd, view)
            except (InterruptedError, BlockingIOError):
                continue
            if count <= 0 or count > len(view):
                raise ValueError('Acknowledgment write failed')
            view = view[count:]
        raise ValueError('Acknowledgment write retry budget exceeded')

    return receive(read, acknowledge, raw_fd, nonce, deadline)


def receive(read, acknowledge, raw_fd, nonce, deadline, clock=time.monotonic):
    """Receive from a bounded nonblocking transport; fsync before acknowledgment.

read(n) must return at most n bytes and implement its own deadline/nonblocking
contract. This layer cannot interrupt a blocking caller. Incomplete raw evidence
is preserved; only the explicit terminal frame returns complete=True.
"""
    if len(nonce) != 32 or not any(nonce):
        raise ValueError('Fresh nonzero 32-byte trial nonce required')
    info = os.fstat(raw_fd)
    if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid()
            or stat.S_IMODE(info.st_mode) != 0o600 or info.st_nlink > 1
            or info.st_size or os.lseek(raw_fd, 0, os.SEEK_CUR)):
        raise ValueError('Fresh owned private regular output descriptor required')
    digest = hashlib.sha256()
    total = 0
    sequence = 0

    def exact(size):
        result = bytearray()
        while len(result) < size:
            if clock() >= deadline:
                raise ValueError('Capture deadline exceeded')
            chunk = read(size - len(result))
            if clock() >= deadline:
                raise ValueError('Read exceeded capture deadline')
            if not isinstance(chunk, bytes) or not chunk or len(chunk) > size - len(result):
                raise ValueError('Incomplete or invalid transport read')
            result.extend(chunk)
        return bytes(result)

    def retain(data):
        view = memoryview(data)
        attempts = 0
        while view:
            attempts += 1
            if attempts > len(data) + 16 or clock() >= deadline:
                raise ValueError('Private output write budget exceeded')
            try:
                written = os.write(raw_fd, view)
            except InterruptedError:
                continue
            if written <= 0 or written > len(view):
                raise ValueError('Private output write failed')
            digest.update(view[:written])
            view = view[written:]
        os.fsync(raw_fd)
        if clock() >= deadline:
            raise ValueError('Private output sync exceeded capture deadline')

    header = exact(40)
    if header != MAGIC + nonce:
        raise ValueError('Trial identity mismatch')
    retain(header)
    # Caller must send the entire ACK or raise. It is evidence-storage receipt,
    # never permission to panic, reboot or otherwise fail the experimental kernel.
    acknowledge(ACK + nonce)
    while True:
        frame = exact(8)
        number, length = struct.unpack('>II', frame)
        if number != sequence or length > MAX_RECORD or total + length > MAX_TOTAL:
            raise ValueError('Record sequence or capture limit violated')
        if not length:
            retain(frame)
            return {'complete': True, 'records': sequence, 'payload_bytes': total,
                    'wire_sha256': digest.hexdigest(), 'device_qualified': False}
        payload = exact(length)
        retain(frame + payload)
        total += length
        sequence += 1
