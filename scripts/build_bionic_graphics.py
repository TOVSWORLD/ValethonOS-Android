#!/usr/bin/env python3
"""Build ARM32 Bionic Panfrost/EGL from pinned sources; no image install or device access."""
import argparse,hashlib,json,os,shutil,stat,subprocess,tarfile,urllib.request,zipfile
from pathlib import Path

MESA_SHA='04294f75d22e9f61cd1e050206bc48b3d39366e788f1803a3368e3d5a872ce18'
DRM_SHA='fc68f9d0ba2ea63c9432a299e14fea09fad7a8a66e8039fcd7802ca59f77b4f5'
NDK_URL='https://dl.google.com/android/repository/android-ndk-r30-linux.zip'
NDK_SHA1='5107f898313790e449e87eee2183d9a20602dee9'
NDK_BYTES=738633529

def digest(path,algorithm='sha256'):
    h=hashlib.new(algorithm)
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def build(root,prior,jobs=2):
    root=root.resolve();prior=prior.resolve()
    if jobs not in (1,2) or not prior.is_dir() or root==prior:raise ValueError('Isolated target and one/two jobs required')
    root.mkdir(parents=True,exist_ok=True)
    report={'scope':'ARM32 Bionic graphics source build only','target':'armv7a-linux-androideabi34','mesa_archive_sha256':MESA_SHA,
        'libdrm_archive_sha256':DRM_SHA,'ndk_url':NDK_URL,'ndk_archive_sha1':NDK_SHA1,'steps':[],
        'compiled':False,'android_image_built':False,'device_access_performed':False,'runtime_verified':False}
    def save():(root/'bionic-build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    def command(name,args,env=None,timeout=7200):
        log=root/(name+'.log')
        if log.exists():raise ValueError('Do not overwrite earlier build step: '+name)
        with log.open('xb') as output:r=subprocess.run([str(a) for a in args],env=env,stdout=output,stderr=subprocess.STDOUT,timeout=timeout)
        report['steps'].append({'name':name,'exit_code':r.returncode});save();print(name,'exit',r.returncode,flush=True)
        if r.returncode:raise RuntimeError(name+' failed; inspect isolated log')
    for name,want in [('mesa-26.2.7.tar.xz',MESA_SHA),('libdrm-2.4.133.tar.xz',DRM_SHA)]:
        source=prior/name
        if not source.is_file() or digest(source)!=want:raise ValueError('Source archive mismatch: '+name)
        target=root/name
        if not target.exists():shutil.copy2(source,target)
        if digest(target)!=want:raise ValueError('Staged source archive mismatch')
        directory=root/name.removesuffix('.tar.xz')
        if not directory.exists():
            with tarfile.open(target) as archive:archive.extractall(root,filter='data')
    archive=root/'android-ndk-r30-linux.zip'
    if not archive.exists():
        if shutil.disk_usage(root).free<8*2**30:raise ValueError('Need 8 GiB free for bounded graphics build')
        partial=archive.with_suffix('.partial')
        with urllib.request.urlopen(NDK_URL,timeout=60) as response,partial.open('wb') as output:
            shutil.copyfileobj(response,output,1024*1024)
        if partial.stat().st_size!=NDK_BYTES or digest(partial,'sha1')!=NDK_SHA1:raise ValueError('NDK download integrity mismatch')
        partial.rename(archive)
    if archive.stat().st_size!=NDK_BYTES or digest(archive,'sha1')!=NDK_SHA1:raise ValueError('NDK integrity mismatch')
    report['ndk_archive_sha256']=digest(archive);save();print('NDK verified',flush=True)
    ndk=root/'android-ndk-r30'
    if not (ndk/'.firetabs-extraction-complete').exists():
        links=[]
        with zipfile.ZipFile(archive) as bundle:
            for item in bundle.infolist():
                path=root/item.filename
                if not path.resolve().is_relative_to(root) or item.filename.startswith('/'):raise ValueError('Unsafe NDK archive path')
                mode=item.external_attr>>16
                if stat.S_ISLNK(mode):
                    links.append((path,bundle.read(item).decode()))
                    continue
                bundle.extract(item,root)
                permissions=mode&0o777
                if permissions:path.chmod(permissions)
        for path,target in links:
            if target.startswith('/') or not (path.parent/target).resolve().is_relative_to(root):raise ValueError('Unsafe NDK symlink')
            if path.exists() or path.is_symlink():path.unlink()
            path.symlink_to(target)
        (ndk/'.firetabs-extraction-complete').write_text(NDK_SHA1+'\n')
    if '30.0.16248370' not in (ndk/'source.properties').read_text():raise ValueError('Unexpected NDK revision')
    toolchain=ndk/'toolchains/llvm/prebuilt/linux-x86_64';bin=toolchain/'bin'
    cross=root/'android-armv7.ini'
    cross.write_text("[binaries]\n"+f"c = '{bin}/armv7a-linux-androideabi34-clang'\ncpp = ['{bin}/armv7a-linux-androideabi34-clang++', '-fno-exceptions', '-static-libstdc++']\nar = '{bin}/llvm-ar'\nstrip = '{bin}/llvm-strip'\npkg-config = '/usr/bin/pkg-config'\n[properties]\nneeds_exe_wrapper = true\n[host_machine]\nsystem = 'android'\ncpu_family = 'arm'\ncpu = 'armv7-a'\nendian = 'little'\n")
    meson=prior/'tools/bin/meson';host=prior/'host-tools/bin';prefix=root/'target'
    env=dict(os.environ,PATH=str(host)+':'+str(prior/'tools/bin')+':'+os.environ['PATH'],PKG_CONFIG_LIBDIR=str(prefix/'lib/pkgconfig'),PKG_CONFIG_PATH='')
    command('drm-configure',[meson,'setup',root/'drm-build',root/'libdrm-2.4.133','--cross-file',cross,'--prefix',prefix,'--libdir=lib',
        '--buildtype=release','-Ddefault_library=static','-Db_staticpic=true','-Dtests=false','-Dman-pages=disabled','-Dvalgrind=disabled',
        '-Dintel=disabled','-Dradeon=disabled','-Damdgpu=disabled','-Dnouveau=disabled','-Dvmwgfx=disabled','-Dfreedreno=disabled','-Dtegra=disabled','-Dvc4=disabled','-Detnaviv=disabled'],env)
    command('drm-compile',[meson,'compile','-C',root/'drm-build','-j',jobs],env)
    command('drm-install',[meson,'install','-C',root/'drm-build'],env)
    command('mesa-configure',[meson,'setup',root/'mesa-build',root/'mesa-26.2.7','--cross-file',cross,'--prefix',prefix,'--libdir=lib',
        '--buildtype=release','-Dplatforms=android','-Dplatform-sdk-version=34','-Dandroid-stub=true','-Dandroid-libbacktrace=disabled',
        '-Dprefer_static=true','-Degl-lib-suffix=_valethon','-Degl=enabled','-Dgles1=enabled','-Dgles2=enabled','-Dopengl=true',
        '-Dgallium-drivers=panfrost','-Dvulkan-drivers=[]','-Dpanfrost-rust=false','-Dgallium-rusticl=false','-Dgbm=disabled',
        '-Dglx=disabled','-Dglvnd=disabled','-Dllvm=disabled','-Ddraw-use-llvm=false','-Dbuild-tests=false',
        '-Dexpat=disabled','-Dzstd=disabled','-Dzlib=disabled','-Dshader-cache=disabled','-Dlibunwind=disabled',
        '-Dmesa-clc=system','-Dprecomp-compiler=system','-Dtools=[]'],env)
    command('mesa-compile',[meson,'compile','-C',root/'mesa-build','-j',jobs],env)
    command('mesa-install',[meson,'install','-C',root/'mesa-build'],env)
    report['runtime_files']={str(p.relative_to(prefix)):{'sha256':digest(p),'bytes':p.stat().st_size} for p in prefix.rglob('*.so*') if p.is_file() and not p.is_symlink()}
    # Link-only Android ABI stand-ins must NEVER be shipped as runtime implementations.
    forbidden={'libhardware.so','liblog.so','libnativewindow.so','libsync.so'}
    if any(p.name in forbidden for p in prefix.rglob('*.so*')):raise ValueError('Link-only Android library unexpectedly installed')
    report['compiled']=True;save();return report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--prior',type=Path,required=True);p.add_argument('--jobs',type=int,default=2);a=p.parse_args();os.nice(10);build(a.root,a.prior,a.jobs)
