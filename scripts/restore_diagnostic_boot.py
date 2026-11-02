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
import subprocess

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
            receipt['write_started'] = True
            Path(receipt_path).write_text(json.dumps(receipt, indent=2) + '\n')
            # -T disables PTY translation. No staging file or userdata mount.
            # Constant destination; image bytes are stdin, never shell source.
            adb.run(['shell', '-T', 'cat > /dev/block/mmcblk0p5'], backup)
            adb.run(['shell', 'sync'])
        if sha(adb.read(BOOT, BOOT_BYTES)) != sha(backup):
            raise ValueError('Rollback readback mismatch; leave recovery running')
        if sha(adb.read(RECOVERY, RECOVERY_BYTES)) != manifest['recovery']['sha256']:
            raise ValueError('Recovery identity changed; stop')
        receipt['verified'] = True
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
