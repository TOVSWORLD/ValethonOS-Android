#!/usr/bin/env python3
"""Audit actual built Douglas packages; source declarations alone cannot pass."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

REQUIRED = ('webview', 'Browser2', 'LatinIME', 'Settings', 'DocumentsUI',
            'DownloadProvider', 'DownloadProviderUi', 'PackageInstaller',
            'CertInstaller', 'Launcher3QuickStep', 'Provision', 'com.android.adbd',
            'ValethonReadiness')
LIMIT = 1692925952


def audit(aosp_root, product_out, module_info, aapt2):
    root = aosp_root.resolve()
    product = product_out.resolve()
    if not product.is_relative_to(root):
        raise ValueError('Product output must be inside the Android checkout')
    modules = json.loads(module_info.read_text())
    packages = {}
    for name in REQUIRED:
        installed = modules.get(name, {}).get('installed', [])
        if not installed:
            raise ValueError('Required module has no installed output: ' + name)
        files = []
        for entry in installed:
            path = (root / entry).resolve()
            if not path.is_relative_to(product) or not path.is_file():
                raise ValueError('Missing or out-of-product installed output: ' + name)
            files.append({'path': str(path.relative_to(product)),
                          'bytes': path.stat().st_size,
                          'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        packages[name] = files
    provider_apks = [product / row['path'] for row in packages['webview']
                     if row['path'].endswith('.apk')]
    if len(provider_apks) != 1:
        raise ValueError('Expected exactly one installed WebView provider APK')
    badging = subprocess.run([str(aapt2), 'dump', 'badging', str(provider_apks[0])],
                             check=True, capture_output=True, text=True).stdout
    package = re.search(r"package: name='([^']+)'", badging)
    if not package or package.group(1) != 'com.android.webview':
        raise ValueError('Provider does not match framework com.android.webview selection')
    version = re.search(r"versionName='([^']+)'", badging)
    animation = product / 'system/media/bootanimation.zip'
    image = product / 'system.img'
    ramdisk = product / 'ramdisk.img'
    for artifact in (animation, image, ramdisk):
        if not artifact.is_file():
            raise ValueError('Missing built artifact: ' + artifact.name)
    # Sparse ext4 images must be measured by expanded blocks, not compressed length.
    with image.open('rb') as stream:
        header = stream.read(28)
    import struct
    if len(header) >= 28 and struct.unpack_from('<I', header)[0] == 0xed26ff3a:
        expanded_size = struct.unpack_from('<I', header, 12)[0] * struct.unpack_from('<I', header, 16)[0]
    else:
        expanded_size = image.stat().st_size
    if expanded_size > LIMIT:
        raise ValueError('System image exceeds existing partition')
    return {'scope': 'Actual built-output package/size audit, not tablet runtime',
            'packages': packages, 'webview_package': package.group(1),
            'webview_version': version.group(1) if version else None,
            'expanded_system_bytes': expanded_size, 'system_limit_bytes': LIMIT,
            'configured_filesystem_reserve_bytes': 16777216,
            'storage_profile': 'volatile-data', 'tablet_runtime_verified': False,
            'remaining': ['provider signature/loading/API and GLES2 runtime',
                          'SELinux/HAL/VINTF closure', 'boot-container/RAM fit',
                          'persistent storage and security release qualification']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aosp-root', type=Path, required=True)
    parser.add_argument('--product-out', type=Path, required=True)
    parser.add_argument('--module-info', type=Path, required=True)
    parser.add_argument('--aapt2', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.aosp_root, args.product_out, args.module_info, args.aapt2)
    args.report.write_text(json.dumps(result, indent=2) + '\n')
    print('Built-output package/size audit passed; tablet runtime remains unqualified.')
