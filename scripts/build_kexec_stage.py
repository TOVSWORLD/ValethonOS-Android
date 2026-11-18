#!/usr/bin/env python3
"""Build and version a prepare-only stage module using matched 4.9 objects."""
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from build_kexec_probe import CONFIG_SHA
from verify_kexec_probe import inspect_module, RELEASE


def build(source, kernel_build, stage, report):
    source, kernel_build, stage = [p.resolve() for p in (source, kernel_build, stage)]
    if hashlib.sha256((kernel_build / '.config').read_bytes()).hexdigest() != CONFIG_SHA:
        raise ValueError('Exact tested kernel configuration required')
    if (kernel_build / 'include/config/kernel.release').read_text().strip() != RELEASE:
        raise ValueError('Exact tested kernel release required')
    env = dict(os.environ, ARCH='arm64', CROSS_COMPILE='aarch64-linux-gnu-')
    command = ['make', '-C', str(source), 'O='+str(kernel_build), '-j4']
    log_path = report.with_suffix('.log')
    with log_path.open('w') as log:
        def make(*args):
            subprocess.run(command+list(args), stdout=log, stderr=subprocess.STDOUT, env=env, check=True)
        make('M='+str(stage), 'modules')
        imports, _, _ = inspect_module((stage / 'kxstage.ko').read_bytes())
        needed = imports | {'module_layout'}
        make('drivers/char/misc.o', 'lib/crc32.o')
        paths = [p for p in kernel_build.rglob('*.o') if p.name != 'built-in.o']
        rows = subprocess.run(['aarch64-linux-gnu-nm', '-A', '--defined-only', *map(str, paths)],
                               capture_output=True, text=True, check=True).stdout.splitlines()
        exports = {}; crcs = {}
        for row in rows:
            fields = row.split()
            if len(fields) != 3: continue
            location, kind, name = fields
            path, _, value = location.rpartition(':')
            if name.startswith('__ksymtab_'):
                exports.setdefault(path, set()).add(name[len('__ksymtab_'):])
            if kind == 'A' and name.startswith('__crc_'):
                crcs.setdefault(path, {})[name[len('__crc_'):]] = int(value, 16)
        providers = {}
        for path, values in crcs.items():
            for name in needed & values.keys() & exports.get(path, set()):
                if name in providers: raise ValueError('Duplicate symbol provider: '+name)
                providers[name] = {'crc': values[name], 'object': str(Path(path).relative_to(kernel_build)),
                                   'object_sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest()}
        missing = needed - providers.keys()
        if missing: raise ValueError('Compile these missing symbol providers: '+', '.join(sorted(missing)))
        table = ''.join(f'0x{providers[n]["crc"]:08x}\t{n}\tvmlinux\tEXPORT_SYMBOL\n' for n in sorted(providers))
        (stage / 'stage-provider.symvers').write_text(table)
        (kernel_build / 'Module.symvers').write_text(table)
        make('M='+str(stage), 'clean')
        make('M='+str(stage), 'modules')
    module = (stage / 'kxstage.ko').read_bytes()
    imports, meta, versions = inspect_module(module)
    for name in imports | {'module_layout'}:
        if versions.get(name) != providers[name]['crc']:
            raise ValueError('Missing/mismatched module CRC: '+name)
    result = {'scope':'Prepare-only generic kexec staging build, not runtime execution',
        'module_sha256':hashlib.sha256(module).hexdigest(), 'module_bytes':len(module),
        'vermagic':meta['vermagic'], 'imports':sorted(imports), 'providers':providers,
        'config_sha256':CONFIG_SHA, 'all_required_crcs_present':True,
        'kernel_handoff_implemented':False, 'loaded_on_tablet':False}
    report.write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['source','kernel-build','stage','report']:p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();print(json.dumps(build(a.source,a.kernel_build,a.stage,a.report),indent=2))
