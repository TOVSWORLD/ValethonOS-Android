#!/usr/bin/env python3
"""Pinned private entry-display checkpoint; source changes only, no device access."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
ROOT = Path(__file__).resolve().parents[1]
PORT = ROOT / 'projects/firetabs-android/kernel/lab-entry-screen'


def contract():
    lock = json.loads((PORT / 'inputs.json').read_text())
    path = ROOT / lock['metadata_source']
    if hashlib.sha256(path.read_bytes()).hexdigest() != lock['metadata_sha256']:
        raise ValueError('Framebuffer metadata drift')
    metadata = json.loads(path.read_text())
    fb, tag = metadata['recovery_framebuffer_get'], metadata['firmware_handoff_tag']
    if (int(fb['smem_start'], 16) != lock['framebuffer_start']
            or fb['smem_len'] != lock['framebuffer_bytes']
            or int(tag['fb_base'], 16) != lock['framebuffer_start']
            or tag['vram_bytes'] != lock['firmware_reservation_bytes']
            or tag['panel_found'] != 1 or metadata['pixels_read']
            or metadata['framebuffer_written'] or not metadata['device_tmpfs_helper_cleaned']
            or fb['smem_len'] > tag['vram_bytes']):
        raise ValueError('Framebuffer ownership/bounds contract differs')
    return lock


def apply(source, revision):
    lock = contract()
    if revision != lock['ack_commit']:
        raise ValueError('Wrong entry-marker ACK revision')
    patch, overlay = PORT/'head-entry.patch', PORT/lock['overlay']
    target, new = source/lock['target'], source/lock['overlay_target']
    for path, key in [(patch, 'patch_sha256'), (overlay, 'overlay_sha256'), (target, 'original_sha256')]:
        if hashlib.sha256(path.read_bytes()).hexdigest() != lock[key]:
            raise ValueError('Entry-marker input drift')
    if new.exists() or new.is_symlink():
        raise ValueError('Refusing existing marker overlay')
    with tempfile.TemporaryDirectory(prefix='entry-preflight-') as folder:
        shadow = Path(folder); p = shadow/lock['target'];p.parent.mkdir(parents=True);p.write_bytes(target.read_bytes())
        subprocess.run(['git','-C',str(shadow),'apply',str(patch)],check=True)
        if hashlib.sha256(p.read_bytes()).hexdigest() != lock['patched_sha256']:
            raise ValueError('Entry patch output differs')
    subprocess.run(['git','-C',str(source),'apply','--check',str(patch)],check=True)
    subprocess.run(['git','-C',str(source),'apply',str(patch)],check=True)
    with new.open('xb') as f:f.write(overlay.read_bytes())
    return {'source_applied':True,'framebuffer_bytes':lock['framebuffer_bytes'],
            'runtime_qualified':False,'device_written':False}


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);a=p.parse_args()
    revision=subprocess.check_output(['git','-C',str(a.source),'rev-parse','HEAD'],text=True).strip()
    print(json.dumps(apply(a.source,revision),indent=2))
