#!/usr/bin/env python3
"""Exact full-boot rollback from existing Douglas TWRP; default is read-only.

Run on the authorized Linux lab only. Never reboot, retry, discover devices or
write recovery. --restore is a destructive boot-partition write, requiring the
separately reviewed trial procedure. Host tests do not qualify device execution.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import tempfile

BOOT = '/dev/block/mmcblk0p5'
RECOVERY = '/dev/block/mmcblk0p6'
BOOT_BYTES = 16777216
RECOVERY_BYTES = 17825792


def sha(data):
    return hashlib.sha256(data).hexdigest()


def validate_backup(data, manifest):
    if len(data) != BOOT_BYTES or not data.startswith(b'ANDROID!'):
        raise ValueError('Expected complete 16 MiB boot rollback image')
    if manifest['boot']['bytes'] != BOOT_BYTES or sha(data) != manifest['boot']['sha256']:
        raise ValueError('Rollback image identity mismatch')
    if manifest['recovery']['bytes'] != RECOVERY_BYTES:
        raise ValueError('Recovery size contract mismatch')
    for entry in (manifest['boot'], manifest['recovery']):
        digest = entry['sha256']
        if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('Invalid pinned digest')


class Adb:
    def __init__(self, executable, selector):
        self.command = [executable, '-s', selector]

    def run(self, args, data=None):
        result = subprocess.run(self.command + args, input=data,
                                capture_output=True, timeout=90)
        if result.returncode:
            # Raw adb output can include private selectors. Keep it out of reports.
            raise ValueError('Selected ADB command failed; stop without retry')
        return result.stdout

    def read(self, node, size):
        data = self.run(['exec-out', 'cat', node])
        if len(data) != size:
            raise ValueError('Partition read size mismatch; no trimming permitted')
        return data

    def push(self, data, destination):
        with tempfile.TemporaryDirectory(prefix='valethonos-rollback-') as folder:
            source = Path(folder) / 'boot.img'
            source.write_bytes(data)
            source.chmod(0o600)
            self.run(['push', str(source), destination])


def preflight(adb, backup, manifest, expected_current):
    validate_backup(backup, manifest)
    if adb.run(['get-state']).strip() != b'recovery':
        raise ValueError('Existing recovery transport required')
    for prop, value in [('ro.product.device', b'douglas'),
                        ('ro.twrp.version', b'3.3.1-0')]:
        if adb.run(['shell', 'getprop', prop]).strip() != value:
            raise ValueError('Recovery identity mismatch')
    base = '/dev/block/platform/mtk-msdc.0/by-name/'
    for alias, node in [('boot', BOOT), ('boot_x', BOOT),
                        ('recovery', RECOVERY), ('recovery_x', RECOVERY)]:
        if adb.run(['shell', 'readlink', base + alias]).strip() != node.encode():
            raise ValueError('Partition alias mismatch')
    if sha(adb.read(RECOVERY, RECOVERY_BYTES)) != manifest['recovery']['sha256']:
        raise ValueError('Independent recovery differs from rollback contract')
    current = sha(adb.read(BOOT, BOOT_BYTES))
    if current != expected_current:
        raise ValueError('Current boot differs from explicitly expected trial image')
    return current


def memory_staging(adb, backup):
    if adb.run(['exec-out', 'readlink', '-f', '/tmp']).strip() != b'/tmp':
        raise ValueError('Recovery /tmp must not redirect to storage')
    mounts = adb.run(['exec-out', 'cat', '/proc/mounts']).splitlines()
    entries = [line.split() for line in mounts]
    selected = [entry for entry in entries if len(entry) >= 4 and entry[1] == b'/tmp']
    if len(selected) != 1 or selected[0][2] != b'tmpfs' or b'rw' not in selected[0][3].split(b','):
        raise ValueError('Explicit writable tmpfs /tmp mount required')
    folder = '/tmp/valethonos-rollback-' + secrets.token_hex(16)
    # Legacy recovery lacks shell-v2 status. exec-out merges remote errors into
    # stdout, so successful mkdir must have empty output; never adopt a path.
    if adb.run(['exec-out', 'mkdir', '-m', '700', folder]):
        raise ValueError('Exclusive recovery RAM staging failed')
    destination = folder + '/boot.img'
    adb.push(backup, destination)
    if sha(adb.read(destination, BOOT_BYTES)) != sha(backup):
        raise ValueError('RAM staging readback mismatch; no block write permitted')
    return folder, destination


def restore(adb, backup, manifest, expected_current, receipt_path):
    current = preflight(adb, backup, manifest, expected_current)
    receipt = {'operation': 'full boot rollback only', 'boot_before_sha256': current,
               'rollback_sha256': sha(backup), 'write_started': False,
               'verified': False, 'rebooted': False, 'recovery_written': False}
    # Exclusive receipt prevents silently reusing a physical operation identity.
    fd = os.open(receipt_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(receipt, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        if current != sha(backup):
            folder, destination = memory_staging(adb, backup)
            receipt['private_ram_staging'] = folder
            # Recheck both partitions after the upload, before the sole write.
            preflight(adb, backup, manifest, expected_current)
            receipt['write_started'] = True
            Path(receipt_path).write_text(json.dumps(receipt, indent=2) + '\n')
            # File-to-block copy avoids unsupported shell-v2 / stdin EOF paths.
            # Full-sized regular RAM file; no short-read pipe or PTY translation.
            adb.run(['exec-out', 'dd', 'if=' + destination, 'of=' + BOOT,
                     'bs=4096', 'count=4096'])
            adb.run(['exec-out', 'sync'])
        if sha(adb.read(BOOT, BOOT_BYTES)) != sha(backup):
            raise ValueError('Rollback readback mismatch; leave recovery running')
        if sha(adb.read(RECOVERY, RECOVERY_BYTES)) != manifest['recovery']['sha256']:
            raise ValueError('Recovery identity changed; stop')
        receipt['verified'] = True
        if 'private_ram_staging' in receipt:
            adb.run(['exec-out', 'rm', destination])
            adb.run(['exec-out', 'rmdir', folder])
            # Legacy shell returns no usable remote exit status: require a marker.
            check = 'if [ -e ' + folder + ' ]; then echo LEFT; else echo RAM_CLEAN; fi'
            if adb.run(['shell', check]).strip() != b'RAM_CLEAN':
                raise ValueError('Rollback verified but private RAM cleanup unconfirmed')
            receipt['ram_staging_cleanup_verified'] = True
    finally:
        Path(receipt_path).write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adb', default='adb')
    parser.add_argument('--selector-file', type=Path, required=True)
    parser.add_argument('--image', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--expected-current-sha256', required=True)
    parser.add_argument('--restore', action='store_true')
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    try:
        selector = json.loads(args.selector_file.read_text())['selector']
        if not isinstance(selector, str) or not selector or selector.startswith('-'):
            raise ValueError('Explicit selector required')
        if not args.image.is_file() or args.image.is_symlink():
            raise ValueError('Regular private rollback image required')
        if args.image.stat().st_size != BOOT_BYTES:
            raise ValueError('Rollback image size mismatch')
        backup = args.image.read_bytes()
        manifest = json.loads(args.manifest.read_text())
        adb = Adb(args.adb, selector)
        if args.restore:
            if args.receipt is None:
                raise ValueError('Fresh private receipt path required for restore')
            result = restore(adb, backup, manifest, args.expected_current_sha256, args.receipt)
        else:
            preflight(adb, backup, manifest, args.expected_current_sha256)
            result = {'preflight': 'passed', 'write_started': False,
                      'device_rollback_execution_qualified': False}
        print(json.dumps(result, indent=2))
    except (ValueError, KeyError, OSError, subprocess.SubprocessError):
        parser.exit(2, 'Rollback stopped; no automatic retry or reboot. Inspect private receipt if created.\n')


if __name__ == '__main__':
    main()
