#!/usr/bin/env python3
"""Validate real ARM32 Android ELF libraries and emit strict Soong vendor modules."""
import argparse,hashlib,json,os,re,shutil,struct,subprocess
from pathlib import Path

SYSTEM_LIBRARIES={'libc.so','libdl.so','libm.so','liblog.so','libhardware.so','libnativewindow.so','libsync.so','libz.so'}
FORBIDDEN_RUNTIME={'libhardware.so','liblog.so','libnativewindow.so','libsync.so'}

def elf_info(data):
    if len(data)<52 or data[:7]!=b'\x7fELF\x01\x01\x01':raise ValueError('Expected little-endian ELF32')
    h=struct.unpack_from('<HHIIIIIHHHHHH',data,16)
    if h[0]!=3 or h[1]!=40 or h[2]!=1:raise ValueError('Expected ARM ET_DYN library')
    if h[6]&0x400:raise ValueError('Hard-float calling convention is not Android armeabi-v7a')
    offset,entrysize,count=h[5],h[10],h[11]
    if entrysize!=40 or not 0<count<65536 or offset+entrysize*count>len(data):raise ValueError('Invalid section table')
    sections=[struct.unpack_from('<IIIIIIIIII',data,offset+i*entrysize) for i in range(count)]
    def content(section):
        start,size=section[4],section[5]
        if start+size>len(data):raise ValueError('Truncated section')
        return data[start:start+size]
    def string(raw,index):
        if index>=len(raw):raise ValueError('String outside table')
        end=raw.find(b'\0',index)
        if end<0:raise ValueError('Unterminated ELF string')
        return raw[index:end].decode('utf-8')
    soname=None;needed=[];runpaths=[];symbols=set();android_api=None
    for section in sections:
        if section[1]==6:
            raw=content(section);strings=content(sections[section[6]])
            if len(raw)%8:raise ValueError('Malformed dynamic section')
            for at in range(0,len(raw),8):
                tag,value=struct.unpack_from('<iI',raw,at)
                if tag==0:break
                if tag==1:needed.append(string(strings,value))
                elif tag==14:soname=string(strings,value)
                elif tag in [15,29]:runpaths.append(string(strings,value))
        elif section[1]==11:
            raw=content(section);strings=content(sections[section[6]])
            if section[9]!=16 or len(raw)%16:raise ValueError('Invalid dynamic symbols')
            for at in range(0,len(raw),16):
                name,value,size,info,other,index=struct.unpack_from('<IIIBBH',raw,at)
                if name and index==0:symbols.add(string(strings,name))
        elif section[1]==7:
            raw=content(section);at=0
            while at+12<=len(raw):
                namesize,descsize,kind=struct.unpack_from('<III',raw,at);at+=12
                name=raw[at:at+namesize].rstrip(b'\0');at+=(namesize+3)&~3
                desc=raw[at:at+descsize];at+=(descsize+3)&~3
                if name==b'Android' and kind==1 and len(desc)>=4:android_api=struct.unpack_from('<I',desc)[0]
    if not soname or '/' in soname or not soname.endswith('.so'):raise ValueError('Android runtime SONAME must be an unversioned .so')
    if not android_api or android_api>37:raise ValueError('Missing/unsupported Android ABI note')
    if runpaths and any('/tmp/' in x or '/home/' in x or 'android_stub' in x for x in runpaths):raise ValueError('Build-host runtime search path leaked')
    if any(x in needed for x in ['libc.so.6','libstdc++.so.6','ld-linux.so.3']):raise ValueError('glibc library cannot be packaged as Bionic')
    return {'class':'ELF32','machine':'ARM','android_api':android_api,'soname':soname,'needed':sorted(set(needed)),'runpaths':runpaths,'undefined_symbols':sorted(symbols)}

def package(prefix,destination,patchelf):
    prefix=prefix.resolve();destination=destination.resolve()
    if destination.exists():raise ValueError('Package destination must be fresh')
    report=json.loads((prefix.parent/'bionic-build-report.json').read_text())
    if report.get('compiled') is not True or report.get('mesa_archive_sha256')!='04294f75d22e9f61cd1e050206bc48b3d39366e788f1803a3368e3d5a872ce18':raise ValueError('Qualified source-build report required')
    candidates=[p for p in prefix.rglob('*.so*') if p.is_file() and not p.is_symlink()]
    if any(p.name in FORBIDDEN_RUNTIME for p in candidates):raise ValueError('Link-only Android ABI library must not be shipped')
    # All installed runtimes must have been hashed by the completed build, not added afterward.
    for p in candidates:
        row=report['runtime_files'].get(str(p.relative_to(prefix)))
        if not row or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Compiled library hash mismatch')
    destination.mkdir(parents=True);arm=destination/'arm';arm.mkdir()
    infos={}
    try:
        for source in candidates:
            # Mesa's Unix version suffix is normalized on copied artifacts only.
            name=source.name.split('.so',1)[0]+'.so'
            name={'libGLESv1_CM.so':'libGLESv1_CM_valethon.so','libGLESv2.so':'libGLESv2_valethon.so'}.get(name,name)
            if not (name.startswith(('libEGL_valethon','libGLESv1_CM_valethon','libGLESv2_valethon')) or name=='libgallium_dri.so'):raise ValueError('Unexpected installed runtime: '+name)
            target=arm/name;shutil.copyfile(source,target)
            subprocess.run([patchelf,'--set-soname',name,str(target)],check=True,capture_output=True)
            info=elf_info(target.read_bytes())
            if name in infos:raise ValueError('Duplicate packaged SONAME')
            infos[name]=dict(info,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),bytes=target.stat().st_size)
        required={'libEGL_valethon.so','libGLESv1_CM_valethon.so','libGLESv2_valethon.so','libgallium_dri.so'}
        if set(infos)!=required:raise ValueError('Incomplete Android graphics runtime')
        for name,info in infos.items():
            unknown=set(info['needed'])-set(infos)-SYSTEM_LIBRARIES
            if unknown:raise ValueError('Unresolved or versioned runtime dependencies: '+','.join(sorted(unknown)))
        notices=[]
        for label,path in [('Mesa MIT',prefix.parent/'mesa-26.2.7/licenses/MIT'),('Android NDK notices',prefix.parent/'android-ndk-r30/NOTICE'),('Android NDK toolchain/runtime notices',prefix.parent/'android-ndk-r30/NOTICE.toolchain')]:
            if not path.is_file():raise ValueError('Required source notice missing: '+label)
            notices.append(label+'\n'+path.read_text())
        drm=prefix.parent/'libdrm-2.4.133'
        license_count=0
        for source in sorted(drm.rglob('*')):
            if source.is_file() and source.suffix in ['.c','.h']:
                text=source.read_text(errors='replace')
                match=re.match(r'(?:\s*/\*.*?\*/|\s*//[^\n]*)+',text,re.S)
                if match:
                    notices.append('libdrm source notice: '+str(source.relative_to(drm))+'\n'+match.group(0));license_count+=1
        if not license_count:raise ValueError('libdrm per-file source notices missing')
        (destination/'NOTICE').write_text('\n\n'.join(notices))
        bp=['// Generated from hash-verified Bionic build outputs; do not disable ELF checks.',
            'package { default_applicable_licenses: ["valethon_bionic_graphics_license"], }',
            'license { name: "valethon_bionic_graphics_license", license_kinds: ["SPDX-license-identifier-MIT", "SPDX-license-identifier-Apache-2.0"], license_text: ["NOTICE"], }',
            'soong_namespace {}','']
        for name,info in sorted(infos.items()):
            module=name.removesuffix('.so');dependencies=[x.removesuffix('.so') for x in info['needed']]
            bp+=['cc_prebuilt_library_shared {',f'    name: "{module}",','    vendor: true,','    compile_multilib: "32",',f'    srcs: ["arm/{name}"],',('    relative_install_path: "egl",' if name!='libgallium_dri.so' else '    // Gallium dependency uses the standard vendor library search path.'),'    strip: { none: true },',f'    shared_libs: {json.dumps(dependencies)},','    check_elf_files: true,','}', '']
        (destination/'Android.bp').write_text('\n'.join(bp))
        packages=sorted(x.removesuffix('.so') for x in infos)
        (destination/'graphics-product.mk').write_text('# ARM32 graphics runtime built from pinned Mesa sources.\nPRODUCT_SOONG_NAMESPACES += vendor/valethon/graphics\nPRODUCT_PACKAGES += '+ ' \\\n    '.join(packages+['gralloc.minigbm','mapper.minigbm','android.hardware.graphics.allocator-service.minigbm','android.hardware.composer.hwc3-service.drm'])+'\nPRODUCT_VENDOR_PROPERTIES += ro.hardware.egl=valethon ro.hardware.gralloc=minigbm\n')
        result={'scope':'ELF/package validation only; no Android image or runtime qualification','source_build':report,'libraries':infos,'runtime_verified':False,'package_files':{name:hashlib.sha256((destination/name).read_bytes()).hexdigest() for name in ['Android.bp','graphics-product.mk','NOTICE']},'release_license_audit_complete':False}
        (destination/'artifact-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
        return result
    except Exception:
        shutil.rmtree(destination);raise
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prefix',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--patchelf',default='patchelf');a=p.parse_args();result=package(a.prefix,a.output,a.patchelf);print(json.dumps({'libraries':list(result['libraries']),'runtime_verified':False}))
