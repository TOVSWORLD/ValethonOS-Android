#!/usr/bin/env python3
"""Verify the authenticated touch kernel against the observed display baseline."""
import gzip, json, struct
from pathlib import Path
from display_kernel_contract import verify as verify_display, sha
ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT/'evidence/touch-input-source/kernel-build-result.json'


def verify(package, baseline):
    previous = verify_display(baseline)
    lock = json.loads(LOCK.read_text())
    if (lock['workflow_passed'] is not True or lock['workflow_run'] != 44438104081
            or lock['source_commit'] != '1525308e981f48a6abd4a8122093f478053382a0'
            or lock['source_tree'] != 'eb50c4dc0f637ee573f067a8d838023cc4328bf7'):
        raise ValueError('Exact authenticated touch build required')
    manifest = json.loads((package/'manifest.json').read_text())
    if (sha((package/'manifest.json').read_bytes()) != lock['manifest_sha256']
            or manifest['build_mode'] != 'touch-provider'
            or manifest['repository_revision'] != lock['workflow_repository_revision']
            or manifest['kernel_revision'] != lock['ack_revision']
            or manifest['run_id'] != str(lock['workflow_run'])):
        raise ValueError('Touch manifest differs')
    for name, facts in manifest['files'].items():
        p = package/name
        if Path(name).name != name or p.is_symlink() or not p.is_file() or not 0 < p.stat().st_size <= 32*1024*1024:
            raise ValueError('Bounded regular touch artifact required')
        data = p.read_bytes()
        if facts != {'bytes': len(data), 'sha256': sha(data)}: raise ValueError('Touch artifact differs: '+name)
    required = set(json.loads((baseline/'manifest.json').read_text())['files']) | {'goodix.o', 'mtk_wdt.o'}
    if not required.issubset(manifest['files']): raise ValueError('Touch artifact closure incomplete')
    def config(p):
        return {l.split('=', 1)[0]: l for l in p.read_text().splitlines() if l.startswith('CONFIG_')}
    a, b = config(baseline/'resolved.config'), config(package/'resolved.config')
    differences = {k: [a.get(k), b.get(k)] for k in a.keys() | b.keys() if a.get(k) != b.get(k)}
    if differences != {'CONFIG_TOUCHSCREEN_GOODIX': ['CONFIG_TOUCHSCREEN_GOODIX=m', 'CONFIG_TOUCHSCREEN_GOODIX=y']}:
        raise ValueError('Unexpected kernel configuration change')
    image = (package/'Image').read_bytes()
    if (sha(image) != lock['image_sha256'] or sha((package/'resolved.config').read_bytes()) != lock['config_sha256']
            or gzip.decompress((package/'Image.gz').read_bytes()) != image or image[56:60] != b'ARMd'
            or b'goodix,gt9xx' not in (package/'goodix.o').read_bytes()):
        raise ValueError('Touch Image/config/alias differs')
    offset, extent, flags = struct.unpack_from('<QQQ', image, 8)
    if offset != 0 or flags != 10 or not len(image) <= extent < 0x2000000: raise ValueError('Image layout differs')
    symbols = (package/'System.map').read_text()
    for marker in ['goodix_ts_probe', 'goodix_ts_driver_init', 'tpv_prepare', 'pwm_backlight_probe', 'mtk_wdt_probe']:
        if marker not in symbols: raise ValueError('Missing linked touch/display/watchdog component: '+marker)
    return {'touch_kernel_verified': True, 'image_sha256': sha(image), 'config_sha256': lock['config_sha256'],
            'image_memory_bytes': (extent+4095)&~4095, 'target_release': lock['target_release'],
            'observed_display_baseline_sha256': previous['image_sha256'], 'physical_touch_verified': False}
