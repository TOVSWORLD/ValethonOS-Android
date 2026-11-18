#!/usr/bin/env python3
"""Offline ARM64 module compatibility inventory; never loads or executes a module."""
import argparse
import hashlib
import json
import re
from pathlib import Path

PIN = '4ba956fd60b29d2fea324515596b392afdcfa2c5'

def audit(source, symbols):
    index = json.loads((source / 'source-index.json').read_text())
    if index['commit'] != PIN:
        raise ValueError('Unexpected upstream source revision')
    for item in index['files']:
        data = (source / item['path']).read_bytes()
        if hashlib.sha256(data).hexdigest() != item['sha256']:
            raise ValueError('Source hash differs: ' + item['path'])
    rows = symbols.read_text().splitlines()
    names = {r.split()[2] for r in rows
             if len(r.split()) >= 3 and re.fullmatch('[0-9a-fA-F]{16}', r.split()[0])}
    required = set()
    for path in (source / 'kernel').rglob('*.c'):
        required.update(re.findall(r'ksym\("([^"]+)"\)', path.read_text()))
    compat = (source / 'kernel/arch/arm64/machine_kexec_compat.c').read_text()
    driver = (source / 'kernel/arch/arm64/machine_kexec_drv.c').read_text()
    cpu_mode_default_unsafe = (
        'static int detect_el2 = 1;' in driver
        and 'kallsyms_lookup_name("set_cpu_boot_mode_flag")' in compat
        and 'set_cpu_boot_mode_flag_ptr[0]' in compat
        and 'set_cpu_boot_mode_flag' not in names)
    return {
        'scope': 'Offline source/live symbol-name compatibility screen, not module ABI or runtime acceptance',
        'upstream_commit': PIN,
        'source_files_verified': len(index['files']),
        'dynamic_symbol_presence': {n: n in names for n in sorted(required)},
        'kallsyms_lookup_name_export_symbol_present': '__ksymtab_kallsyms_lookup_name' in names,
        'default_cpu_mode_probe_references_missing_symbol': cpu_mode_default_unsafe,
        'upstream_stuck_cpu_check_is_stubbed': 'return false;' in compat.split('bool cpus_are_stuck_in_kernel(void)', 1)[-1].split('}', 1)[0],
        'matching_recovery_build_configuration_established': False,
        'module_abi_qualified': False,
        'module_load_admitted': False,
        'handoff_admitted': False,
        'target_kernel_logging_qualified': False,
        'device_written': False,
        'next': 'Resolve exact recovery source/config ABI; build a non-handoff compatibility probe before porting the loader. Do not load unchanged upstream module.',
    }

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--symbols', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    result = audit(a.source, a.symbols)
    a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
