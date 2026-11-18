#!/usr/bin/env python3
"""Build the separate private logging PID1 component; never pack/load firmware."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import secrets
import shutil
import subprocess
from build_diagnostic_initramfs import archive, inspect_elf

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'projects/firetabs-android/diagnostic-usb'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inspect_archive(raw, entries, *, storage_readonly=False):
    allowed = {'dev': (0o040755, (0, 0)), 'proc': (0o040755, (0, 0)),
               'sys': (0o040755, (0, 0)), 'security': (0o040755, (0, 0)),
               'config': (0o040755, (0, 0)), 'dev/console': (0o020600, (5, 1)),
               'dev/kmsg': (0o020400, (1, 11)), 'init': (0o100500, (0, 0))}
    if storage_readonly:
        allowed = dict(list(allowed.items())[:-1] + [('dev/firetabs-boot', (0o060400, (179, 5))), ('init', allowed['init'])])
    if [entry[0] for entry in entries] != list(allowed):
        raise ValueError('Unreviewed archive path/order')
    for name, mode, payload, device in entries:
        if (mode, device) != allowed[name] or (name != 'init' and payload):
            raise ValueError('Unreviewed archive node, permission or payload')
    offset = 0
    expected = entries + [('TRAILER!!!', 0, b'', (0, 0))]
    for index, (name, mode, payload, device) in enumerate(expected, 1):
        if raw[offset:offset + 6] != b'070701':
            raise ValueError('Invalid newc header')
        fields = [int(raw[offset + 6 + i * 8:offset + 14 + i * 8], 16) for i in range(13)]
        start = offset + 110
        encoded = name.encode('ascii') + b'\0'
        wanted = [index, mode, 0, 0, 1, 0, len(payload), 0, 0, *device, len(encoded), 0]
        if fields != wanted or raw[start:start + fields[11]] != encoded:
            raise ValueError('Archive ownership, node, extent or name differs')
        name_end = start + fields[11]
        start = (name_end + 3) & ~3
        if any(raw[name_end:start]):
            raise ValueError('Nonzero name padding')
        if raw[start:start + fields[6]] != payload:
            raise ValueError('Archive payload differs')
        payload_end = start + fields[6]
        offset = (payload_end + 3) & ~3
        if any(raw[payload_end:offset]):
            raise ValueError('Nonzero payload padding')
    if any(raw[offset:]):
        raise ValueError('Unreviewed archive tail')
    return [entry[0] for entry in entries]


def build(policy_file, policy_report, output, compiler='clang-18', linker='ld.lld-18', compiler_kind='clang', *, storage_readonly=False, display_functional=False):
    if display_functional and not storage_readonly:
        raise ValueError('Display variant requires the enforcing read-only policy')
    if output.exists() or output.is_symlink():
        raise ValueError('Fresh private output directory required')
    policy = policy_file.read_bytes()
    report = json.loads(policy_report.read_text())
    required_controls = {'enforcement_toggle', 'policy_reload', 'block_read', 'reboot_capability', 'pid1_fork', 'pid1_domain_escape'}
    if storage_readonly:
        required_controls |= {'block_write', 'block_ioctl', 'block_create', 'block_relabel', 'other_block_open'}
    if report.get('storage_readonly_profile', False) != storage_readonly:
        raise ValueError('Policy/profile mismatch')
    if (len(policy) > 65536 or len(policy) != report['policy_bytes']
            or sha(policy) != report['policy_sha256'] or report['policy_version'] != 33
            or report['permissive_domains'] is not False or report['unknown_permissions'] != 'deny'
            or set(report['forbidden_privilege_mutations_rejected']) != required_controls
            or not all(report['forbidden_privilege_mutations_rejected'].values())):
        raise ValueError('Exact enforcing policy/negative-control report required')
    for name, expected in report['source_sha256'].items():
        if name not in ['ack-abi.cil', 'storage-readonly.cil' if storage_readonly else 'diagnostic.cil'] or sha((SOURCE / 'policy' / name).read_bytes()) != expected:
            raise ValueError('Policy source changed after compilation')
    if compiler_kind not in ['clang', 'gcc']:
        raise ValueError('Explicit clang or AArch64 GCC compiler kind required')
    tool = shutil.which(linker) if compiler_kind == 'clang' else shutil.which(compiler)
    if not tool:
        raise ValueError('Explicit LLVM18 linker required')
    if compiler_kind == 'gcc' and not subprocess.check_output([compiler, '-dumpmachine'], text=True).strip().startswith('aarch64-'):
        raise ValueError('AArch64 cross GCC required')
    output.mkdir(mode=0o700, parents=True)
    nonce = secrets.token_bytes(32)
    (output / 'trial-nonce-private.bin').write_bytes(nonce)
    (output / 'trial-nonce-private.bin').chmod(0o400)

    def array(name, raw):
        rows = [','.join('0x%02x' % byte for byte in raw[i:i + 16]) for i in range(0, len(raw), 16)]
        return 'static const unsigned char ' + name + '[]={\n' + ',\n'.join(rows) + '\n};\n'

    header = output / 'lab_inputs.h'
    header.write_text(array('lab_policy_blob', policy) + array('lab_trial_nonce', nonce))
    header.chmod(0o400)
    elf = output / 'init'
    command = [compiler]
    if compiler_kind == 'clang':
        command += ['--target=aarch64-linux-gnu', '--ld-path=' + tool]
    command += ['-nostdlib', '-static',
               '-Os', '-Wall', '-Wextra', '-Werror', '-ffreestanding', '-fno-builtin',
               '-fno-stack-protector', '-mgeneral-regs-only', '-Wl,--build-id=none,-e,_start',
               '-I', str(output), '-o', str(elf), str(SOURCE / ('storage_init.c' if storage_readonly else 'lab_init.c')), str(SOURCE / 'memory.c')]
    if display_functional:
        command += ['-DVALETHON_DISPLAY_TEST=1']
    if storage_readonly:
        command += [str(ROOT / 'projects/firetabs-android/native-kexec/combined_sha256.c')]
    result = subprocess.run(command, capture_output=True, text=True, timeout=90)
    (output / 'compile-private.log').write_text(result.stdout + result.stderr)
    if result.returncode:
        raise ValueError('Lab PID1 compilation failed; inspect private output log')
    data = elf.read_bytes()
    inspection = inspect_elf(data)
    entries = [(name, 0o040755, b'', (0, 0)) for name in ['dev', 'proc', 'sys', 'security', 'config']]
    entries += [('dev/console', 0o020600, b'', (5, 1)), ('dev/kmsg', 0o020400, b'', (1, 11)),
                ('init', 0o100500, data, (0, 0))]
    if storage_readonly:
        entries.insert(-1, ('dev/firetabs-boot', 0o060400, b'', (179, 5)))
    raw = archive(entries)
    names = inspect_archive(raw, entries, storage_readonly=storage_readonly)
    packed = bytearray(gzip.compress(raw, mtime=0))
    packed[9] = 255
    packed = bytes(packed)
    if gzip.decompress(packed) != raw:
        raise ValueError('Compressed archive roundtrip failed')
    (output / 'initramfs.cpio.gz').write_bytes(packed)
    for path in output.iterdir():
        if path.is_file():
            path.chmod(0o400 if path.name in ['trial-nonce-private.bin', 'lab_inputs.h'] else 0o600)
    final = {
        'scope': 'Separate private ' + ('functional display' if display_functional else 'read-only storage' if storage_readonly else 'log-bringup') + ' component build only; not a boot image or device test',
        'storage_readonly_profile': storage_readonly,
        'display_functional_profile': display_functional,
        'storage_probe_enabled': storage_readonly and not display_functional,
        'storage_sha_source_sha256': sha((ROOT / 'projects/firetabs-android/native-kexec/combined_sha256.c').read_bytes()) if storage_readonly else None,
        'elf': inspection, 'archive_entries': names,
        'policy_sha256': sha(policy), 'nonce_sha256': sha(nonce),
        'policy_report_sha256': sha(policy_report.read_bytes()),
        'builder_sha256': sha(Path(__file__).read_bytes()),
        'archive_builder_sha256': sha((ROOT / 'scripts/build_diagnostic_initramfs.py').read_bytes()),
        'artifacts': {name: {'bytes': len(content), 'sha256': sha(content)}
                      for name, content in [('init', data), ('initramfs.cpio.gz', packed)]},
        'sources_sha256': {p.name: sha(p.read_bytes()) for p in sorted(SOURCE.glob('*')) if p.suffix in ['.h', '.c']},
        'compiler': subprocess.check_output([compiler, '--version'], text=True).splitlines()[0],
        'linker': subprocess.check_output([tool, '--version'], text=True).splitlines()[0],
        'compiler_kind': compiler_kind,
        'private_test_usb_id': '1209:0001', 'usb_id_globally_unique': False,
        'redistribution_allowed': False, 'physical_execution_admitted': False,
        'policy_load_device_tested': False, 'log_transport_device_tested': False,
        'failure_injection_implemented': False, 'reboot_interface': False,
    }
    (output / 'report.json').write_text(json.dumps(final, indent=2) + '\n')
    (output / 'report.json').chmod(0o600)
    return final


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy', type=Path, required=True)
    parser.add_argument('--policy-report', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--compiler', default='clang-18')
    parser.add_argument('--linker', default='ld.lld-18')
    parser.add_argument('--compiler-kind', choices=['clang','gcc'], default='clang')
    parser.add_argument('--storage-readonly', action='store_true')
    parser.add_argument('--display-functional', action='store_true')
    args = parser.parse_args()
    try:
        report = build(args.policy, args.policy_report, args.output, args.compiler, args.linker, args.compiler_kind, storage_readonly=args.storage_readonly, display_functional=args.display_functional)
    except (ValueError, KeyError, OSError, subprocess.SubprocessError):
        parser.exit(2, 'Lab component build stopped; inspect private output if created.\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
