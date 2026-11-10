#!/usr/bin/env python3
"""Build the matched query-only affinity module and exact import CRC table."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from build_kexec_probe import CONFIG_SHA
from verify_kexec_probe import inspect_module, RELEASE

PROVIDERS = ['kernel/printk/printk.o','kernel/module.o','kernel/cpu.o',
 'kernel/sched/core.o','arch/arm64/kernel/arm64ksyms.o','arch/arm64/kernel/setup.o',
 'drivers/of/base.o','arch/arm64/kernel/smp.o',
 'lib/hweight.o','init/version.o']


def build(source, kernel_build, own, policy, out):
    source,kernel_build,own,policy,out=map(Path.resolve,(source,kernel_build,own,policy,out))
    if hashlib.sha256((kernel_build/'.config').read_bytes()).hexdigest()!=CONFIG_SHA:
        raise ValueError('Matched config required')
    if (kernel_build/'include/config/kernel.release').read_text().strip()!=RELEASE:
        raise ValueError('Matched release required')
    out.mkdir()
    for n in ['Makefile','affinity.c']:shutil.copyfile(own/n,out/n)
    shutil.copyfile(policy,out/'legacy_affinity_policy.h')
    command=['make','-C',str(source),'O='+str(kernel_build),'-j4']
    env={**os.environ,'ARCH':'arm64','CROSS_COMPILE':'aarch64-linux-gnu-'}
    previous=(kernel_build/'Module.symvers').read_bytes()
    try:
        with (out/'build.log').open('w') as log:
            def make(*args):
                subprocess.run(command+list(args),env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
            make(*PROVIDERS)
            make('M='+str(out),'modules')
            imports,_,_=inspect_module((out/'kxaffinity.ko').read_bytes())
            needed=imports|{'module_layout'}
            objects=[p for p in kernel_build.rglob('*.o') if p.name!='built-in.o']
            lines=subprocess.run(['aarch64-linux-gnu-nm','-A','--defined-only',*map(str,objects)],
                                 capture_output=True,text=True,check=True).stdout.splitlines()
            symbols={}
            for line in lines:
                f=line.split()
                if len(f)!=3:continue
                path,_,value=f[0].rpartition(':')
                symbols.setdefault(path,{})[f[2]]=(f[1],value)
            providers={}
            for path,table in symbols.items():
                for name in needed:
                    if '__ksymtab_'+name in table and '__crc_'+name in table:
                        kind,crc=table['__crc_'+name]
                        if kind!='A':continue
                        if name in providers:raise ValueError('Duplicate provider: '+name)
                        providers[name]={'crc':int(crc,16),
                          'object':str(Path(path).relative_to(kernel_build)),
                          'object_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest()}
            if providers.keys()!=needed:raise ValueError('Missing providers: '+repr(needed-providers.keys()))
            text=''.join('0x%08x\t%s\tvmlinux\tEXPORT_SYMBOL\n'%(providers[n]['crc'],n) for n in sorted(needed))
            (out/'affinity-provider.symvers').write_text(text)
            (kernel_build/'Module.symvers').write_text(text)
            make('M='+str(out),'clean');make('M='+str(out),'modules')
        data=(out/'kxaffinity.ko').read_bytes()
        imports,meta,versions=inspect_module(data)
        for n in needed:
            if versions.get(n)!=providers[n]['crc']:raise ValueError('CRC mismatch: '+n)
        report={'scope':'Query-only affinity build, not runtime acceptance',
          'module_sha256':hashlib.sha256(data).hexdigest(),'module_bytes':len(data),
          'vermagic':meta['vermagic'],'config_sha256':CONFIG_SHA,'providers':providers,
          'source_sha256':hashlib.sha256((out/'affinity.c').read_bytes()).hexdigest(),
          'policy_sha256':hashlib.sha256((out/'legacy_affinity_policy.h').read_bytes()).hexdigest(),
          'firmware_query_fid':'0x84000004','maximum_query_count':4,
          'state_changing_firmware_calls':False,'loaded_on_tablet':False}
        (out/'build-result.json').write_text(json.dumps(report,indent=2)+'\n')
        return report
    finally:
        (kernel_build/'Module.symvers').write_bytes(previous)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['source','kernel-build','own','policy','out']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();print(json.dumps(build(a.source,a.kernel_build,a.own,a.policy,a.out),indent=2))
