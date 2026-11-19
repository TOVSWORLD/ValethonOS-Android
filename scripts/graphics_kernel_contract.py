#!/usr/bin/env python3
"""Verify exact hosted graphics output against the physically observed baseline."""
import gzip, json, struct
from pathlib import Path
from touch_kernel_contract import verify as verify_touch, sha, ROOT
LOCK=ROOT/'evidence/graphics-source/kernel-build-result.json'


def verify(package, touch, display):
    previous=verify_touch(touch,display);lock=json.loads(LOCK.read_text())
    if (lock['workflow_passed'] is not True or lock['workflow_run']!=44451450892
            or lock['source_commit']!='4d534e81905130dd496e0eba2f3034aca4beca2f'
            or lock['source_tree']!='6e7182d687e49dcc491917a1a2d997c60ee2e840'):
        raise ValueError('Exact authenticated GPU build required')
    manifest=json.loads((package/'manifest.json').read_text())
    if (sha((package/'manifest.json').read_bytes())!=lock['manifest_sha256']
            or manifest['build_mode']!='graphics-provider' or manifest['run_id']!=str(lock['workflow_run'])
            or manifest['repository_revision']!=lock['workflow_repository_revision'] or manifest['kernel_revision']!=lock['ack_revision']):
        raise ValueError('Graphics manifest differs')
    for name,facts in manifest['files'].items():
        p=package/name
        if Path(name).name!=name or p.is_symlink() or not p.is_file() or not 0<p.stat().st_size<=32*1024*1024:
            raise ValueError('Bounded regular graphics artifacts required')
        b=p.read_bytes()
        if facts!={'bytes':len(b),'sha256':sha(b)}: raise ValueError('Graphics artifact differs: '+name)
    required=set(json.loads((touch/'manifest.json').read_text())['files'])|{'panfrost_drv.o','panfrost_gpu.o','panfrost_device.o'}
    if not required.issubset(manifest['files']): raise ValueError('Graphics artifact closure incomplete')
    def config(p):return {l.split('=',1)[0]:l for l in p.read_text().splitlines() if l.startswith('CONFIG_')}
    a,b=config(touch/'resolved.config'),config(package/'resolved.config')
    changes={k:[a.get(k),b.get(k)] for k in a.keys()|b.keys() if a.get(k)!=b.get(k)}
    expected={k:[k+'=m',k+'=y'] for k in ['CONFIG_DRM_PANFROST','CONFIG_DRM_SCHED','CONFIG_DRM_GEM_SHMEM_HELPER']}
    if changes!=expected or b.get('CONFIG_RD_XZ')!='CONFIG_RD_XZ=y': raise ValueError('Graphics config or XZ support differs')
    report=json.loads((package/'display-build-result.json').read_text())
    if report.get('builtin_panfrost_support') is not True or report.get('builtin_goodix_touch_support') is not True:
        raise ValueError('Built-in graphics/touch support required')
    image=(package/'Image').read_bytes()
    if sha(image)!=lock['image_sha256'] or sha((package/'resolved.config').read_bytes())!=lock['config_sha256'] or gzip.decompress((package/'Image.gz').read_bytes())!=image:
        raise ValueError('Graphics Image/config differs')
    offset,extent,flags=struct.unpack_from('<QQQ',image,8)
    if offset!=0 or flags!=10 or image[56:60]!=b'ARMd' or not len(image)<=extent<0x2000000: raise ValueError('Preserved graphics Image layout required')
    symbols=(package/'System.map').read_text()
    if sha(symbols.encode())!=lock['system_map_sha256']: raise ValueError('Graphics symbols differ')
    for name in ['panfrost_probe','goodix_ts_probe','tpv_prepare','pwm_backlight_probe','mtk_wdt_probe']:
        if name not in symbols: raise ValueError('Missing linked graphics/display/touch/watchdog: '+name)
    return {'graphics_kernel_verified':True,'image_sha256':sha(image),'config_sha256':lock['config_sha256'],
            'image_memory_bytes':(extent+4095)&~4095,'target_release':lock['target_release'],
            'observed_touch_kernel_sha256':previous['image_sha256'],'physical_graphics_verified':False}
