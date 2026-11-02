#!/usr/bin/env python3
"""Explicit loader-sized lab logging config; no runtime admission."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import diagnostic_config
import usb_acm_config

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / 'projects/firetabs-android/kernel/lab-log'


def requirements():
    lock = json.loads((PROFILE / 'profile.json').read_text())
    source = ROOT / lock['platform_source']
    if hashlib.sha256(source.read_bytes()).hexdigest() != lock['platform_sha256']:
        raise ValueError('Platform Kconfig source drift')
    result = diagnostic_config.policy()
    result.update(usb_acm_config.requirements()[0])
    # Only actual platform choices, never ARCH_HAS_* capability symbols.
    platforms = re.findall(r'^config (ARCH_[A-Z0-9_]+)$', source.read_text(), re.M)
    if 'ARCH_MEDIATEK' not in platforms or len(platforms) < 20:
        raise ValueError('Incomplete platform choices')
    result.update({name: 'n' for name in platforms})
    for line in (PROFILE / 'fragment.config').read_text().splitlines():
        active = re.fullmatch(r'CONFIG_([A-Z0-9_]+)=(y|[0-9]+)', line)
        disabled = re.fullmatch(r'# CONFIG_([A-Z0-9_]+) is not set', line)
        if active or disabled:
            result[(active or disabled)[1]] = active[2] if active else 'n'
        elif line and not line.startswith('# '):
            raise ValueError('Unsupported lab fragment syntax')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['apply', 'check'])
    p.add_argument('config', type=Path)
    p.add_argument('--source', type=Path)
    a = p.parse_args()
    expected = requirements()
    if a.mode == 'check':
        diagnostic_config.check(a.config.read_text(), expected)
        usb_acm_config.check(a.config.read_text())
        print(json.dumps({'passed': True, 'physical_execution_admitted': False,
                          'scope': 'Resolved private lab config only', 'required': expected}, indent=2))
        return
    if a.source is None:
        p.error('--source required')
    actual = a.source / 'arch/arm64/Kconfig.platforms'
    lock = json.loads((PROFILE / 'profile.json').read_text())
    if hashlib.sha256(actual.read_bytes()).hexdigest() != lock['platform_sha256']:
        raise ValueError('Build source platform choices differ')
    for name, value in expected.items():
        command = [str(a.source / 'scripts/config'), '--file', str(a.config)]
        if value.startswith('"'):
            command += ['--set-str', name, value[1:-1]]
        elif value in ['y', 'n']:
            command += ['--enable' if value == 'y' else '--disable', name]
        else:
            command += ['--set-val', name, value]
        subprocess.run(command, check=True)


if __name__ == '__main__':
    main()
