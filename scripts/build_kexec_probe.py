#!/usr/bin/env python3
"""Build an offline no-handoff probe against the exact working 4.9 inputs."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

COMMIT = '72940eb733af8df948cc216cb977cd8be9cba5a9'
CONFIG_SHA = 'b087199622287207923f9449eedd820ee1940ee82157e77648e36b4b959f3859'
PROVIDERS = ['kernel/printk/printk.o', 'kernel/kallsyms.o', 'kernel/module.o',
             'init/version.o', 'kernel/cpu.o', 'lib/hweight.o']
NEEDED = {'printk', 'kallsyms_lookup_name', 'module_layout', 'init_uts_ns',
          '__cpu_online_mask', '__sw_hweight64'}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def options(data):
    return {l.split('=', 1)[0]: l.split('=', 1)[1] for l in data.decode().splitlines()
            if l.startswith('CONFIG_') and '=' in l}

def build(source, config, out, probe, cross='aarch64-linux-gnu-', jobs=4):
    source, config, out, probe = [p.resolve() for p in (source, config, out, probe)]
    baseline = config.read_bytes()
    if sha(baseline) != CONFIG_SHA:
        raise ValueError('Exact extracted working-kernel configuration required')
    if source.name != 'android_kernel_amazon_mt8163-' + COMMIT:
        raise ValueError('Use the pinned source archive directory')
    out.mkdir(parents=True, exist_ok=True)
    kernel = out / 'build'; module = out / 'probe'
    kernel.mkdir(exist_ok=True); module.mkdir(exist_ok=True)
    for name in ['probe.c', 'Makefile']:
        if (probe / name).resolve() != (module / name).resolve():
            shutil.copyfile(probe / name, module / name)
    (kernel / '.config').write_bytes(baseline)
    (source / '.scmversion').write_text('-g' + COMMIT[:12] + '\n')
    env = dict(os.environ, ARCH='arm64', CROSS_COMPILE=cross,
               KBUILD_BUILD_USER='nobody', KBUILD_BUILD_HOST='android-build', KBUILD_BUILD_VERSION='10')
    command = ['make', '-C', str(source), 'O=' + str(kernel), '-j' + str(jobs)]
    with (out / 'probe-build.log').open('w') as log:
        def make(*targets):
            subprocess.run(command + list(targets), env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
        make('olddefconfig')
        resolved = (kernel / '.config').read_bytes()
        if options(resolved) != options(baseline):
            raise ValueError('Resolved configuration options changed')
        make('modules_prepare')
        make(*PROVIDERS)
        crcs = {}; provider_objects = {}
        for name in PROVIDERS:
            data = (kernel / name).read_bytes(); provider_objects[name] = sha(data)
            result = subprocess.run([cross + 'nm', str(kernel / name)], capture_output=True, text=True, check=True)
            symbols = {r.split()[2]: (r.split()[0], r.split()[1]) for r in result.stdout.splitlines() if len(r.split()) == 3}
            for symbol in NEEDED:
                entry = symbols.get('__crc_' + symbol)
                if entry and entry[1] == 'A' and '__ksymtab_' + symbol in symbols:
                    if symbol in crcs:
                        raise ValueError('Duplicate CRC provider')
                    crcs[symbol] = int(entry[0], 16)
        if crcs.keys() != NEEDED:
            raise ValueError('Required exported provider CRCs missing: ' + repr(NEEDED - crcs.keys()))
        table = ''.join(f'0x{crcs[n]:08x}\t{n}\tvmlinux\tEXPORT_SYMBOL\n' for n in sorted(crcs))
        # This deliberately contains only the six source-object exports required
        # by this probe. It is not a complete kernel build's Module.symvers.
        (out / 'probe-provider.symvers').write_text(table)
        (kernel / 'Module.symvers').write_text(table)
        make('M=' + str(module), 'clean')
        make('M=' + str(module), 'modules')
    compiler = subprocess.run([cross + 'gcc', '--version'], capture_output=True, text=True, check=True).stdout.splitlines()[0]
    manifest = {'scope': 'Offline no-handoff probe build; six exact source-object CRC providers, no complete kernel image',
                'kernel_commit': COMMIT, 'baseline_config_sha256': sha(baseline),
                'resolved_config_sha256': sha(resolved), 'config_option_differences': 0,
                'compiler': compiler, 'provider_object_sha256': provider_objects,
                'provider_crc': {n: f'{v:08x}' for n, v in sorted(crcs.items())},
                'probe_source_sha256': sha((module / 'probe.c').read_bytes()),
                'module_sha256': sha((module / 'kxprobe.ko').read_bytes()),
                'loaded_on_tablet': False, 'target_runtime_abi_verified': False,
                'handoff_attempted': False, 'physical_test_admitted': False}
    (out / 'probe-build-result.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['source', 'config', 'out', 'probe']:
        p.add_argument('--' + key, type=Path, required=True)
    p.add_argument('--cross', default='aarch64-linux-gnu-')
    p.add_argument('--jobs', type=int, choices=range(1, 9), default=4)
    a = p.parse_args()
    print(json.dumps(build(a.source, a.config, a.out, a.probe, a.cross, a.jobs), indent=2))
