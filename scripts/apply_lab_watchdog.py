#!/usr/bin/env python3
"""Pinned base-watchdog match for private lab-log only; no device execution."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PORT = ROOT / 'projects/firetabs-android/kernel/lab-watchdog'


def apply(source, revision):
    lock = json.loads((PORT / 'inputs.json').read_text())
    if revision != lock['ack_commit']:
        raise ValueError('Wrong watchdog ACK revision')
    patch = PORT / 'mt8163-match.patch'
    target = source / lock['target']
    for path, key in [(patch, 'patch_sha256'), (target, 'original_sha256')]:
        if hashlib.sha256(path.read_bytes()).hexdigest() != lock[key]:
            raise ValueError('Watchdog pinned input drift')
    expected = (ROOT / lock['source']).read_bytes().replace(
        b'{ .compatible = "mediatek,mt6589-wdt" },',
        b'{ .compatible = "mediatek,mt6589-wdt" },\n\t{ .compatible = "mediatek,mt8163-wdt" },')
    if hashlib.sha256(expected).hexdigest() != lock['patched_sha256']:
        raise ValueError('Unexpected watchdog output contract')
    with tempfile.TemporaryDirectory(prefix='wdt-preflight-') as folder:
        shadow = Path(folder)
        p = shadow / lock['target']
        p.parent.mkdir(parents=True)
        p.write_bytes(target.read_bytes())
        subprocess.run(['git', '-C', str(shadow), 'apply', str(patch)], check=True)
        if p.read_bytes() != expected:
            raise ValueError('Watchdog patch changes more than exact match')
    subprocess.run(['git', '-C', str(source), 'apply', '--check', str(patch)], check=True)
    subprocess.run(['git', '-C', str(source), 'apply', str(patch)], check=True)
    return {'base_watchdog_match_added': True, 'reset_controller_data_added': False,
            'runtime_qualified': False, 'source_sha256': lock['patched_sha256']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    revision = subprocess.check_output(['git', '-C', str(args.source), 'rev-parse', 'HEAD'], text=True).strip()
    print(json.dumps(apply(args.source, revision), indent=2))
