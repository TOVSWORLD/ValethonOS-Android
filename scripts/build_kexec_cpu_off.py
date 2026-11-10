#!/usr/bin/env python3
"""Compile-review matched CPU-off objects only; never load the module wrapper."""
import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from build_kexec_probe import CONFIG_SHA
from verify_kexec_probe import RELEASE


def build(source, kernel_build, candidate, report):
    source, kernel_build, candidate = map(Path.resolve, (source, kernel_build, candidate))
    config = hashlib.sha256((kernel_build/'.config').read_bytes()).hexdigest()
    if config != CONFIG_SHA or (kernel_build/'include/config/kernel.release').read_text().strip() != RELEASE:
        raise ValueError('Exact tested kernel release/config required')
    manifest = json.loads((candidate/'source-report.json').read_text())
    for name, digest in manifest['files'].items():
        if hashlib.sha256((candidate/name).read_bytes()).hexdigest() != digest:
            raise ValueError('Candidate source differs: '+name)
    result = subprocess.run(['make', '-C', str(source), 'O='+str(kernel_build),
                             'M='+str(candidate), '-j4', 'modules'],
                            env={**os.environ, 'ARCH':'arm64', 'CROSS_COMPILE':'aarch64-linux-gnu-'},
                            capture_output=True)
    log = result.stdout + result.stderr
    report.with_suffix('.log').write_bytes(log)
    result.check_returncode()
    dis = subprocess.run(['aarch64-linux-gnu-objdump', '-dr', str(candidate/'mt_psci.o')],
                         capture_output=True, text=True, check=True).stdout
    match = re.search(r'<mt_psci_cpu_kill>:(.*?)(?=\n[0-9a-f]+ <|\Z)', dis, re.S)
    if not match or 'R_AARCH64_CALL26\tspm_mtcmos_secondary_off_bounded' not in match[1]:
        raise ValueError('Compiled kill callback does not call bounded path')
    if 'cpu_psci_ops' in match[1]:
        raise ValueError('Old PSCI wrapper still present in kill callback')
    if '<mt_kexec_secondary_off_gate>:' not in dis or 'spm_mtcmos_secondary_off_check' not in dis:
        raise ValueError('Compiled final gate missing')
    report.with_suffix('.disassembly.txt').write_text(dis)
    objects = {}
    for name in ['mtcmos.o', 'mt_psci.o', 'cpu-off-preview.o']:
        data = (candidate/name).read_bytes()
        objects[name] = {'bytes':len(data), 'sha256':hashlib.sha256(data).hexdigest()}
    warnings = [l for l in log.decode(errors='replace').splitlines() if 'WARNING:' in l]
    receipt = {
        'scope':'Matched ARM64 object compilation only; not module ABI/runtime qualification',
        'config_sha256':config, 'kernel_release':RELEASE, 'objects':objects,
        'source_report':manifest, 'compiled_kill_uses_bounded_path':True,
        'compiled_final_off_gate_present':True,
        'modpost_warnings':[re.sub(r'\[[^]]*\]', '[build-only preview]', l) for l in warnings],
        'generated_module_wrapper_must_not_be_loaded':True,
        'full_kernel_built':False, 'source_kernel_unchanged':True,
        'hardware_execution':False, 'handoff_admitted':False,
        'whole_hotplug_bound_proved':False,
    }
    report.write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['source','kernel-build','candidate','report']:
        p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(build(a.source,a.kernel_build,a.candidate,a.report),indent=2))
