#!/usr/bin/env python3
"""Verify the exact hosted display build; keep old kernel profiles pinned separately."""
import hashlib
import json
from pathlib import Path
import struct
ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/'evidence/display-pipeline-source/pwm-kernel-build-result.json'
ACK='d9318bdb4c34e8b2d997b4f67ced56b120b22b87'
BUILD_SOURCE='616de1891cbb2af1e89fa651ec68e5feedd54616'
BUILD_RUN=44273014513


def sha(data):return hashlib.sha256(data).hexdigest()


def verify(package,contract=CONTRACT):
    if not contract.is_file():raise ValueError('Completed authenticated display build receipt required')
    lock=json.loads(contract.read_text())
    if (lock.get('workflow_passed') is not True or lock.get('source_commit')!=BUILD_SOURCE
            or lock.get('workflow_run')!=BUILD_RUN or lock.get('ack_revision')!=ACK):
        raise ValueError('Exact completed display build required')
    manifest_file=package/'manifest.json';manifest=json.loads(manifest_file.read_text())
    if (sha(manifest_file.read_bytes())!=lock['manifest_sha256'] or manifest['build_mode']!='display-provider'
            or manifest['kernel_revision']!=ACK or manifest['repository_revision']!=lock['workflow_repository_revision']):
        raise ValueError('Authenticated display manifest differs')
    for name,facts in manifest['files'].items():
        if Path(name).name!=name or (package/name).is_symlink():raise ValueError('Regular bounded artifact paths required')
        path=package/name
        if not path.is_file() or not 0<path.stat().st_size<=32*1024*1024:raise ValueError('Bounded display artifact required')
        content=path.read_bytes()
        if facts!={'bytes':len(content),'sha256':sha(content)}:raise ValueError('Display artifact differs: '+name)
    required={'Image','Image.gz','resolved.config','System.map','display-build-result.json',
              'panel-amazon-douglas-tpv.o','mtk_drm_drv.o','mtk_disp_gamma.o','mtk-mutex.o','lp855x_bl.o','pwm_bl.o'}
    # Host API linkage is independently required in System.map below.
    if not required.issubset(manifest['files']):raise ValueError('Display build artifact closure incomplete')
    report=json.loads((package/'display-build-result.json').read_text())
    if report['ack_revision']!=ACK or report['hardware_execution'] is not False or report['display_dt_enabled'] is not False:
        raise ValueError('Source-only display build scope differs')
    config=(package/'resolved.config').read_text()
    for symbol in ['DRM_MEDIATEK','DRM_PANEL_AMAZON_DOUGLAS_TPV','BACKLIGHT_PWM','PWM_MTK_DISP','I2C_MT65XX','FRAMEBUFFER_CONSOLE','DRM_FBDEV_EMULATION','VT_CONSOLE','SECURITY_SELINUX']:
        if 'CONFIG_'+symbol+'=y\n' not in config:raise ValueError('Missing built-in display dependency: '+symbol)
    if '# CONFIG_MTK_CMDQ is not set' not in config:raise ValueError('CPU-driven display profile required')
    image=(package/'Image').read_bytes()
    if len(image)<64 or image[56:60]!=b'ARMd':raise ValueError('ARM64 Image required')
    offset,extent,flags=struct.unpack_from('<QQQ',image,8)
    if offset!=0 or flags!=10 or not len(image)<=extent<0x2000000:raise ValueError('Exact native RAM layout required')
    if (lock['image_sha256']!=sha(image) or lock['config_sha256']!=sha(config.encode())
            or lock['system_map_sha256']!=sha((package/'System.map').read_bytes())):
        raise ValueError('Pinned display build differs')
    for marker in ['mt8163_mmsys_driver_data','mt8163_gamma_driver_data','mt8163_mutex_driver_data',
                   'mtk_dsi_mt8163_prepare_lanes','mtk_dsi_mt8163_unprepare_lanes','tpv_prepare','pwm_backlight_probe']:
        if marker not in (package/'System.map').read_text():raise ValueError('Missing linked display component: '+marker)
    return dict(display_kernel_verified=True,image_sha256=sha(image),config_sha256=sha(config.encode()),
                image_memory_bytes=(extent+4095)&~4095,target_release=lock['target_release'],
                source_commit=BUILD_SOURCE,workflow_run=BUILD_RUN,hardware_execution=False)
