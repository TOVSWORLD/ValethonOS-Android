#!/usr/bin/env python3
"""Fault-test source-overlay admission using temporary metadata copies, no builds."""
import argparse
import json
import shutil
import tempfile
from pathlib import Path
from prepare_kexec_source_integration import prepare


def validate(source, kernel_build, cpu_off, legacy, audit, prepared):
    manifest=json.loads((prepared/'source-manifest.json').read_text())
    results=[]
    with tempfile.TemporaryDirectory() as temp:
        p=Path(temp)
        for n in manifest['overlay_sha256']:
            dest=p/'source'/n;dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(prepared/'source'/n,dest)
        (p/'build').mkdir();shutil.copyfile(prepared/'build/.config',p/'build/.config')
        def check(out):return prepare(source,kernel_build,cpu_off,legacy,audit,out,True,manifest.get('gcc13_compat',manifest.get('gcc13_indent_fix',False)))
        check(p);results.append({'case':'matched-overlay','passed':True})
        controls=['drivers/firmware/psci.c',
          'drivers/misc/mediatek/base/power/mt8163/bounded_secondary_off.h','../build/.config']
        if manifest.get('gcc13_compat',manifest.get('gcc13_indent_fix',False)):
            controls.append('drivers/misc/mediatek/boot/mtk_boot_common.c')
        for name in controls:
            path=p/'source'/name;before=path.read_bytes();path.write_bytes(before+b'\n')
            try:
                try:check(p)
                except ValueError:results.append({'case':'reject-corrupt-'+path.name,'passed':True})
                else:raise AssertionError('Corrupt prepared input accepted: '+name)
            finally:path.write_bytes(before)
        forbidden=source/'must-not-create-kexec-overlay'
        try:check(forbidden)
        except ValueError:results.append({'case':'reject-output-inside-original-source','passed':True})
        else:raise AssertionError('Original source destination accepted')
        if forbidden.exists():raise AssertionError('Rejected source destination created')
        check(p)
    return {'scope':'Actual artifact admission fault controls; temporary metadata copies only',
      'cases':results,'kernel_compiles_started':0,'hardware_execution':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['source','kernel-build','cpu-off','legacy','audit','prepared','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();r=validate(a.source,a.kernel_build,a.cpu_off,a.legacy,a.audit,a.prepared)
    a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
