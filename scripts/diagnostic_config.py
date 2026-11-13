#!/usr/bin/env python3
"""Apply/check explicit diagnostic kernel policy; never operate a device."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FRAGMENT = ROOT / 'projects/firetabs-android/kernel/diagnostic/fragment.config'


def policy():
    result = {}
    for line in FRAGMENT.read_text().splitlines():
        yes = re.fullmatch(r'CONFIG_([A-Z0-9_]+)=y', line)
        no = re.fullmatch(r'# CONFIG_([A-Z0-9_]+) is not set', line)
        if yes or no:
            name = (yes or no).group(1)
            if name in result:
                raise ValueError('Duplicate diagnostic symbol: ' + name)
            result[name] = 'y' if yes else 'n'
        elif line and not line.startswith('# '):
            raise ValueError('Unexpected fragment syntax')
    if not result:
        raise ValueError('Empty diagnostic policy')
    return result


def check(text, requirements):
    active = dict(re.findall(r'^CONFIG_([A-Z0-9_]+)=(.*)$', text, re.M))
    mismatches = []
    for name, state in requirements.items():
        # Unavailable/disabled symbols cannot compile built-in or modular code.
        actual = active.get(name, 'n')
        if actual != state:
            mismatches.append(f'CONFIG_{name} expected {state}, resolved {actual}')
    if mismatches:
        raise ValueError('; '.join(mismatches))
    return {'scope': 'Resolved kernel configuration policy only; no boot/hardware qualification',
            'fragment_sha256': hashlib.sha256(FRAGMENT.read_bytes()).hexdigest(),
            'required': requirements, 'passed': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['apply', 'check'])
    parser.add_argument('config', type=Path)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--historical-report', type=Path,
                        help='Audit retained old configuration against its recorded policy, not current readiness')
    args = parser.parse_args()
    requirements = policy()
    if args.historical_report:
        if args.mode != 'check':
            parser.error('--historical-report is check-only')
        report = json.loads(args.historical_report.read_text())
        if report.get('passed') is not True or not report.get('required'):
            raise ValueError('Invalid historical policy receipt')
        requirements = report['required']
    if args.mode == 'apply':
        if args.source is None:
            parser.error('--source required for apply')
        for name, state in requirements.items():
            subprocess.run([str(args.source / 'scripts/config'), '--file', str(args.config),
                            '--enable' if state == 'y' else '--disable', name], check=True)
    else:
        result = check(args.config.read_text(), requirements)
        if args.historical_report:
            result.update(scope='Historical resolved-policy audit only; not current build readiness',
                          fragment_sha256=report['fragment_sha256'], historical=True)
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
