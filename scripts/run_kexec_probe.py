#!/usr/bin/env python3
"""One explicitly approved, RAM-only probe load/unload. Never reboots or kexecs."""
import argparse
import gzip
import hashlib
import json
import os
import re
import secrets
import subprocess
from pathlib import Path
from build_kexec_probe import CONFIG_SHA
from verify_kexec_probe import RELEASE, verify

BOOT_SHA = '08fcf3455d66943632d0fc91348d4ab7d41b80c40d88e61272000a1d697faa1e'
SCOPE = 'kexec-compatibility-probe-1'

SYMBOLS = {'machine_shutdown', 'migrate_to_reboot_cpu', 'kernel_restart_prepare',
           'cpu_hotplug_enable', 'cpu_do_switch_mm', '__flush_dcache_area',
           '__hyp_set_vectors', 'set_cpu_boot_mode_flag'}

def parse_records(lines):
    headers = [re.search(r'KXPROBE v1 release=(\S+) page_shift=(\d+) current_el=(\d+) online_cpus=(\d+)$', l) for l in lines]
    headers = [h for h in headers if h]
    if len(headers) != 1:
        raise ValueError('One fresh probe header required')
    release, page, el, cpus = headers[0].groups()
    if release != RELEASE or page != '12' or el not in ['1', '2'] or not 1 <= int(cpus) <= 4:
        raise ValueError('Unexpected probe kernel/CPU report')
    found = {}
    for line in lines:
        m = re.search(r'KXPROBE symbol=(\S+) present=([01])$', line)
        if m:
            name, present = m.groups()
            if name in found:
                raise ValueError('Duplicate probe symbol record')
            found[name] = present == '1'
    if found.keys() != SYMBOLS or sum('KXPROBE complete handoff_attempted=0' in l for l in lines) != 1 or len(lines) != 10:
        raise ValueError('Complete fresh probe record set required')
    return {'release': release, 'page_shift': int(page), 'current_el': int(el),
            'online_cpus': int(cpus), 'symbol_presence': found}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def run(selector, module, symvers, output, authorization=None):
    checked = verify(module, symvers)
    if not re.fullmatch(r'[A-Za-z0-9._:-]+', selector):
        raise ValueError('Explicit ADB selector required')
    auth = None
    if authorization is not None:
        auth = json.loads(authorization.read_text())
        expected = {'scope': SCOPE, 'module_sha256': checked['module_sha256'],
                    'target_boot_sha256': BOOT_SHA, 'owner_approved': True,
                    'owner_available': True, 'handoff_allowed': False}
        if any(type(auth.get(k)) is not type(v) or auth.get(k) != v for k, v in expected.items()):
            raise ValueError('Exact probe approval and owner availability required')
    output.mkdir(mode=0o700)
    result = {'scope': SCOPE, 'module_sha256': checked['module_sha256'],
              'module_load_attempts': 0, 'module_loaded': False, 'module_unloaded': False,
              'boot_written': False, 'handoff_attempted': False, 'rebooted': False,
              'complete': False}
    def private_file(name, data):
        path = output / name
        with path.open('wb') as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    def save():
        private_file('result.tmp', (json.dumps(result, indent=2) + '\n').encode())
        os.replace(output / 'result.tmp', output / 'result.json')
    def adb(command, data=None, check=True, timeout=40):
        r = subprocess.run(['adb', '-s', selector, 'exec-out', command], input=data,
                           capture_output=True, timeout=timeout)
        if check and r.returncode:
            raise RuntimeError('ADB command failed; stop without retry')
        return r
    path = None
    try:
        save()
        state = subprocess.run(['adb', '-s', selector, 'get-state'], capture_output=True, timeout=10)
        if state.returncode or state.stdout.strip() != b'device':
            raise ValueError('Running normal Android required; current recovery is incompatible')
        if adb('uname -r').stdout.strip().decode() != RELEASE:
            raise ValueError('Wrong running kernel; never insert into TWRP')
        identity = adb('id').stdout
        if not re.search(rb'\buid=0\b', identity):
            raise ValueError('Root ADB session required; use the installed rooted-debugging capability')
        def root(command, data=None, check=True):
            return adb(command, data, check)
        config = gzip.decompress(root('cat /proc/config.gz').stdout)
        if digest(config) != CONFIG_SHA:
            raise ValueError('Live kernel configuration differs')
        boot = root('head -c 16777216 /dev/block/mmcblk0p5').stdout
        if len(boot) != 16777216 or digest(boot) != BOOT_SHA:
            raise ValueError('Live normal boot image differs')
        if 'kxprobe ' in root('cat /proc/modules').stdout.decode():
            raise ValueError('Probe already loaded; do not retry')
        before = root('dmesg').stdout
        private_file('dmesg-before-private.txt', before)
        if b'KXPROBE' in before:
            raise ValueError('Prior probe records present; no fresh attribution available')
        mounts = root('cat /proc/mounts').stdout.decode().splitlines()
        if not any(len(r.split()) >= 3 and r.split()[1] == '/dev' and r.split()[2] in ['tmpfs', 'devtmpfs'] for r in mounts):
            raise ValueError('RAM-backed /dev required')
        result['preflight'] = 'passed'
        save()
        if auth is None:
            result['complete'] = True
            return result
        path = '/dev/kxprobe-' + secrets.token_hex(8) + '.ko'
        result['ram_path'] = path
        save()
        # Use ADB's file-transfer protocol, not an exec-out stdin stream.
        # Root adbd writes directly into the already-verified RAM filesystem.
        root('umask 077; set -C; : > ' + path)
        pushed = subprocess.run(['adb', '-s', selector, 'push', str(module), path],
                                capture_output=True, timeout=40)
        private_file('push-private.log', pushed.stdout + pushed.stderr)
        if pushed.returncode:
            raise RuntimeError('RAM module upload failed; stop before insertion')
        root('chmod 600 ' + path)
        if digest(root('cat ' + path).stdout) != checked['module_sha256']:
            raise ValueError('RAM module readback differs')
        result['module_load_attempts'] = 1
        save()
        loaded = root('insmod ' + path, check=False)
        private_file('insmod-private.log', loaded.stdout + loaded.stderr)
        result['insmod_exit_code'] = loaded.returncode
        if loaded.returncode:
            raise RuntimeError('Kernel rejected probe; never force-load or retry')
        result['module_loaded'] = True
        save()
        after = root('dmesg').stdout
        private_file('dmesg-loaded-private.txt', after)
        lines = [l for l in after.decode(errors='replace').splitlines() if 'KXPROBE ' in l]
        result['probe_records'] = lines
        result['probe'] = parse_records(lines)
        result['probe_complete_record'] = True
        result['complete'] = True
        return result
    except BaseException as error:
        result.update(failure_kind=type(error).__name__, failure=str(error))
        raise
    finally:
        if result['module_loaded']:
            try:
                unloaded = root('rmmod kxprobe', check=False)
                result['module_unloaded'] = unloaded.returncode == 0 and 'kxprobe ' not in root('cat /proc/modules').stdout.decode()
                private_file('rmmod-private.log', unloaded.stdout + unloaded.stderr)
            except BaseException as error:
                result['unload_failure_kind'] = type(error).__name__
        if path is not None:
            try:
                root('rm -f ' + path)
                result['ram_cleanup_verified'] = root('test ! -e ' + path, check=False).returncode == 0
            except BaseException as error:
                result['cleanup_failure_kind'] = type(error).__name__
        if result['module_load_attempts']:
            try:
                private_file('dmesg-final-private.txt', root('dmesg').stdout)
            except BaseException as error:
                result['final_log_failure_kind'] = type(error).__name__
        if result['module_loaded'] and not result['module_unloaded']:
            result['complete'] = False
        if path is not None and not result.get('ram_cleanup_verified'):
            result['complete'] = False
        save()

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--selector', required=True)
    for key in ['module', 'symvers', 'output']:
        p.add_argument('--' + key, type=Path, required=True)
    p.add_argument('--authorization', type=Path)
    a = p.parse_args()
    r = run(a.selector, a.module, a.symvers, a.output, a.authorization)
    print(json.dumps(r, indent=2))
    if not r['complete']:
        raise SystemExit(1)
