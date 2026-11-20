#!/usr/bin/env python3
"""Build pinned Panfrost/EGL/GLES2/GBM userspace in an isolated lab directory.

Consumes verified public source archives. Never packages, installs or boots a
tablet image. Host compiler tools and AArch64 runtime libraries stay separate.
"""
import argparse, hashlib, json, os, subprocess
from pathlib import Path

MESA_SHA = '04294f75d22e9f61cd1e050206bc48b3d39366e788f1803a3368e3d5a872ce18'
DRM_SHA = 'fc68f9d0ba2ea63c9432a299e14fea09fad7a8a66e8039fcd7802ca59f77b4f5'
sha = lambda data: hashlib.sha256(data).hexdigest()


def run(root, jobs=2):
    root = root.resolve()
    if not root.is_dir() or root.is_symlink() or jobs not in range(1, 9):
        raise ValueError('Existing isolated source directory and bounded jobs required')
    for name, want in [('mesa-26.2.7.tar.xz', MESA_SHA), ('libdrm-2.4.133.tar.xz', DRM_SHA)]:
        p = root/name
        if p.is_symlink() or sha(p.read_bytes()) != want:
            raise ValueError('Pinned public archive differs: '+name)
    report = {'scope': 'Source compilation only; no tablet/image admission', 'steps': [],
              'mesa_source_sha256': MESA_SHA, 'libdrm_source_sha256': DRM_SHA,
              'target': 'aarch64-linux-gnu', 'physical_graphics_verified': False}
    def save():
        (root/'userspace-build-report.json').write_text(json.dumps(report, indent=2)+'\n')
    def command(name, args, env=None):
        save()
        if env is None:
            env = dict(os.environ, PATH=str(root/'tools/bin')+':/usr/lib/llvm-18/bin:'+os.environ['PATH'])
        with (root/(name+'-private.log')).open('xb') as log:
            r = subprocess.run([str(a) for a in args], stdout=log, stderr=subprocess.STDOUT, env=env, timeout=3600)
        report['steps'].append({'name': name, 'exit_code': r.returncode}); save()
        if r.returncode: raise ValueError(name+' failed; inspect isolated build log')
        print(name+' passed', flush=True)
    venv = root/'tools'
    command('tools-venv', ['python3', '-m', 'venv', '--system-site-packages', venv])
    command('tools-meson', [venv/'bin/python', '-m', 'pip', 'install', '--disable-pip-version-check', 'meson==1.4.2', 'packaging==24.2'])
    meson = venv/'bin/meson'; native = root/'native.ini'; cross = root/'aarch64.ini'
    native.write_text("[binaries]\nc = 'clang-18'\ncpp = 'clang++-18'\nllvm-config = 'llvm-config-18'\n")
    cross.write_text("[binaries]\nc = 'aarch64-linux-gnu-gcc'\ncpp = 'aarch64-linux-gnu-g++'\nar = 'aarch64-linux-gnu-ar'\nstrip = 'aarch64-linux-gnu-strip'\npkg-config = 'pkg-config'\n[properties]\nneeds_exe_wrapper = true\n[host_machine]\nsystem = 'linux'\ncpu_family = 'aarch64'\ncpu = 'cortex-a53'\nendian = 'little'\n")
    host = root/'host-build'; host_prefix = root/'host-tools'; target = root/'target'; source = root/'mesa-26.2.7'
    common = ['--buildtype=release', '-Dbuild-tests=false', '-Dplatforms=[]', '-Dvulkan-drivers=[]',
              '-Dglx=disabled', '-Dglvnd=disabled', '-Dgles1=disabled', '-Dgallium-rusticl=false',
              '-Dpanfrost-rust=false', '-Dexpat=disabled', '-Dzstd=disabled', '-Dzlib=disabled',
              '-Dshader-cache=disabled', '-Dlibunwind=disabled']
    command('host-configure', [meson, 'setup', host, source, '--native-file', native, '--prefix', host_prefix,
            *common, '-Dgallium-drivers=[]', '-Dopengl=false', '-Dgles2=disabled', '-Degl=disabled',
            '-Dgbm=disabled', '-Dtools=panfrost', '-Dmesa-clc=enabled', '-Dinstall-mesa-clc=true',
            '-Dprecomp-compiler=enabled', '-Dinstall-precomp-compiler=true'])
    command('host-compile', [meson, 'compile', '-C', host, '-j', jobs])
    command('host-install', [meson, 'install', '-C', host])
    drm = root/'drm-build'
    command('libdrm-configure', [meson, 'setup', drm, root/'libdrm-2.4.133', '--cross-file', cross,
            '--prefix', target, '--libdir=lib', '--buildtype=release', '-Dtests=false', '-Dman-pages=disabled', '-Dvalgrind=disabled'])
    command('libdrm-compile', [meson, 'compile', '-C', drm, '-j', jobs])
    command('libdrm-install', [meson, 'install', '-C', drm])
    env = dict(os.environ, PATH=str(host_prefix/'bin')+':'+str(venv/'bin')+':/usr/lib/llvm-18/bin:'+os.environ['PATH'],
               PKG_CONFIG_LIBDIR=str(target/'lib/pkgconfig'), PKG_CONFIG_PATH=str(target/'lib/pkgconfig'))
    runtime = root/'runtime-build'
    command('runtime-configure', [meson, 'setup', runtime, source, '--cross-file', cross, '--prefix', target,
            '--libdir=lib', *common, '-Dgallium-drivers=panfrost', '-Dopengl=true', '-Dgles2=enabled',
            '-Degl=enabled', '-Dgbm=enabled', '-Dllvm=disabled', '-Ddraw-use-llvm=false',
            '-Dmesa-clc=system', '-Dprecomp-compiler=system', '-Dtools=[]'], env)
    command('runtime-compile', [meson, 'compile', '-C', runtime, '-j', jobs], env)
    command('runtime-install', [meson, 'install', '-C', runtime], env)
    report['runtime_files'] = {str(p.relative_to(target)): {'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())}
                               for p in target.rglob('*') if p.is_file() and not p.is_symlink()}
    report['compiled'] = True; save()
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--root', type=Path, required=True)
    p.add_argument('--jobs', type=int, default=2); a = p.parse_args(); run(a.root, a.jobs)
