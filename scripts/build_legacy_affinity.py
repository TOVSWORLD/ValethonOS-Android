#!/usr/bin/env python3
"""Compile an exact-source legacy binding object for review, never deploy."""
import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from build_kexec_probe import CONFIG_SHA
from verify_kexec_probe import RELEASE
from prepare_legacy_affinity import SHA


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def build(source, kernel_build, candidate, report):
    source,kernel_build,candidate=map(Path.resolve,(source,kernel_build,candidate))
    original=source/'drivers/firmware/psci.c'
    manifest=json.loads((candidate/'binding-report.json').read_text())
    if (digest(original)!=SHA or manifest['source_sha256']!=SHA or
        digest(candidate/'psci.c')!=manifest['patched_sha256'] or
        digest(candidate/'legacy_affinity_policy.h')!=manifest['policy_sha256']):
        raise ValueError('Pinned original/generated binding differs')
    if (digest(kernel_build/'.config')!=CONFIG_SHA or
        (kernel_build/'include/config/kernel.release').read_text().strip()!=RELEASE):
        raise ValueError('Matched kernel configuration and release required')
    (candidate/'Makefile').write_text('obj-m := legacy-affinity-preview.o\nlegacy-affinity-preview-y := psci.o\n')
    r=subprocess.run(['make','-C',str(source),'O='+str(kernel_build),'M='+str(candidate),'-j4','modules'],
      env={**os.environ,'ARCH':'arm64','CROSS_COMPILE':'aarch64-linux-gnu-'},capture_output=True)
    log=r.stdout+r.stderr;report.with_suffix('.log').write_bytes(log);r.check_returncode()
    dis=subprocess.run(['aarch64-linux-gnu-objdump','-dr',str(candidate/'psci.o')],
      capture_output=True,text=True,check=True).stdout
    if '<mt8163_legacy_affinity_info>:' not in dis:raise ValueError('Compiled callback absent')
    if digest(original)!=SHA:raise ValueError('Original source changed')
    report.with_suffix('.disassembly.txt').write_text(dis)
    result={'scope':'Matched source-kernel legacy binding object compilation only',
      'binding':manifest,'config_sha256':CONFIG_SHA,'kernel_release':RELEASE,
      'object_sha256':digest(candidate/'psci.o'),'object_bytes':(candidate/'psci.o').stat().st_size,
      'compiled_legacy_wrapper_present':True,'source_unchanged':True,
      'modpost_warnings':[re.sub(r'\[[^]]*\]','[build-only preview]',l)
        for l in log.decode(errors='replace').splitlines() if 'WARNING:' in l],
      'generated_module_wrapper_must_not_be_loaded':True,
      'full_kernel_built':False,'hardware_execution':False,'handoff_admitted':False}
    report.write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['source','kernel-build','candidate','report']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();print(json.dumps(build(a.source,a.kernel_build,a.candidate,a.report),indent=2))
