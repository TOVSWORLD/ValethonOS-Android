#!/usr/bin/env python3
"""Stage source-controlled Douglas inputs and verified Bionic drivers into an Android checkout."""
import argparse,hashlib,json,shutil
from pathlib import Path
from package_bionic_graphics import elf_info
from build_bootanimation import build_bytes as build_bootanimation
ROOT=Path(__file__).resolve().parents[1]

def plan(aosp,graphics):
    aosp=aosp.resolve();graphics=graphics.resolve()
    if not (aosp/'build/make/core').is_dir():raise ValueError('Android checkout root required')
    record=json.loads((graphics/'artifact-manifest.json').read_text())
    if record.get('runtime_verified') is not False or record['source_build'].get('compiled') is not True:raise ValueError('Expected compiled, not runtime-qualified graphics package')
    expected={'libEGL_valethon.so','libGLESv1_CM_valethon.so','libGLESv2_valethon.so','libgallium_dri.so'}
    if set(record['libraries'])!=expected:raise ValueError('Complete four-library Bionic runtime required')
    copies={}
    for name,facts in record['libraries'].items():
        p=graphics/'arm'/name;data=p.read_bytes();info=elf_info(data)
        if hashlib.sha256(data).hexdigest()!=facts['sha256'] or info['soname']!=name:raise ValueError('Graphics ELF/hash mismatch')
        copies[aosp/'vendor/valethon/graphics/arm'/name]=data
    for name in ['Android.bp','graphics-product.mk','NOTICE','artifact-manifest.json']:
        data=(graphics/name).read_bytes()
        if name!='artifact-manifest.json' and hashlib.sha256(data).hexdigest()!=record.get('package_files',{}).get(name):raise ValueError('Generated package metadata hash mismatch')
        copies[aosp/'vendor/valethon/graphics'/name]=data
    # Keep ELF checks enabled; do not accept a package that bypasses its own admission.
    bp=copies[aosp/'vendor/valethon/graphics/Android.bp'].decode()
    if 'check_elf_files: false' in bp or bp.count('check_elf_files: true')!=4:raise ValueError('Strict Soong ELF checks required')
    device=ROOT/'projects/firetabs-android/android-integration/device'
    for p in device.rglob('*'):
        if p.is_file():copies[aosp/'device/valethon/douglas'/p.relative_to(device)]=p.read_bytes()
    copies[aosp/'device/valethon/douglas/media/bootanimation.zip']=build_bootanimation()
    for dest,data in copies.items():
        if dest.is_symlink() or not dest.resolve().is_relative_to(aosp):raise ValueError('Staging path escape')
        if dest.exists() and dest.read_bytes()!=data:raise ValueError('Refuse to overwrite different checkout inputs: '+str(dest.relative_to(aosp)))
    return copies

def stage(aosp,graphics):
    copies=plan(aosp,graphics)
    for dest,data in copies.items():dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    return {'scope':'Offline source/package staging only','files':{str(p.relative_to(aosp.resolve())):hashlib.sha256(data).hexdigest() for p,data in copies.items()},
            'lunch_target':'valethon_douglas-trunk_staging-userdebug','build_targets':['systemimage','ramdisk'],'compiled_android_image':False,'device_access':False}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--aosp-root',type=Path,required=True);p.add_argument('--graphics',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();result=stage(a.aosp_root,a.graphics);a.report.write_text(json.dumps(result,indent=2)+'\n');print('Douglas source and Bionic graphics package staged; no build or device operation.')
