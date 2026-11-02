#!/usr/bin/env python3
"""Compile/inspect isolated trial policy; never load it into a host or tablet."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'projects/firetabs-android/diagnostic-usb/policy'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_policy(output):
    subprocess.run([sys.executable, str(ROOT / 'scripts/generate_diagnostic_selinux_abi.py'), '--check'],
                   check=True, capture_output=True)
    tools = {}
    for name in ['secilc', 'checkpolicy']:
        path = shutil.which(name)
        if not path:
            raise ValueError('Install pinned Ubuntu secilc/checkpolicy3.5-1 on build host')
        version = subprocess.check_output(['dpkg-query', '-W', '-f=${Version}', name], text=True).strip()
        if version != '3.5-1':
            raise ValueError('Policy compiler package version mismatch')
        tools[name] = {'version': version, 'sha256': digest(Path(path))}
    if output.exists() or output.is_symlink():
        raise ValueError('Fresh output directory required')
    output.mkdir(mode=0o700, parents=True)
    abi = SOURCE / 'ack-abi.cil'
    policy = SOURCE / 'diagnostic.cil'

    def command(source, target):
        return ['secilc', '-m', '-c', '33', '-o', str(target), '-f', str(output / 'file_contexts'),
                str(abi), str(source)]

    binary = output / 'policy.33'
    result = subprocess.run(command(policy, binary), capture_output=True, text=True, timeout=30)
    (output / 'compile-private.log').write_text(result.stdout + result.stderr)
    if result.returncode:
        raise ValueError('Policy compile failed; inspect private output log')
    dumped = output / 'compiled.cil'
    subprocess.run(['checkpolicy', '-b', '-C', '-o', str(dumped), str(binary)],
                   capture_output=True, timeout=30, check=True)
    text = dumped.read_text()
    if re.search(r'\(typepermissive\b', text) or not re.search(r'\(handleunknown\s+deny\)', text):
        raise ValueError('Compiled policy has permissive domains or wrong unknown policy')
    controls = {}
    for name, rule in {
        'enforcement_toggle': '(allow trial_domain security_t (security (setenforce)))',
        'policy_reload': '(allow trial_domain security_t (security (load_policy)))',
        'block_read': '(allow trial_domain rootfs_t (blk_file (read)))',
        'reboot_capability': '(allow trial_domain self (capability (sys_boot)))',
    }.items():
        mutant = output / (name + '.cil')
        mutant.write_text(policy.read_text() + '\n' + rule + '\n')
        bad_binary = output / (name + '.policy')
        rejected = subprocess.run(command(mutant, bad_binary), capture_output=True, timeout=30)
        controls[name] = rejected.returncode != 0 and b'neverallow check failed' in rejected.stderr.lower()
        (output / (name + '-private.log')).write_bytes(rejected.stdout + rejected.stderr)
        if not controls[name]:
            raise ValueError('Compiler accepted forbidden privilege: ' + name)
    report = {
        'scope': 'Policy compilation and compiler-enforced negative controls only; no policy load',
        'ack_revision': 'd9318bdb4c34e8b2d997b4f67ced56b120b22b87',
        'compiler_packages': tools,
        'source_sha256': {name: digest(SOURCE / name) for name in ['ack-abi.cil', 'diagnostic.cil']},
        'policy_version': 33, 'policy_bytes': binary.stat().st_size, 'policy_sha256': digest(binary),
        'unknown_permissions': 'deny', 'permissive_domains': False,
        'forbidden_privilege_mutations_rejected': controls,
        'kernel_policy_load_tested': False, 'runtime_qualified': False,
        'tablet_security_changed': False,
    }
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'out/diagnostic-trial-policy-build')
    args = parser.parse_args()
    try:
        report = compile_policy(args.output)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(2, 'Policy build stopped: ' + str(error) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
