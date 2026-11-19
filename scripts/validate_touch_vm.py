#!/usr/bin/env python3
"""Check enforcing input-node policy on virt, without claiming physical touch."""
import argparse, gzip, hashlib, json, os, re, selectors, shutil, subprocess, time
from pathlib import Path
from build_diagnostic_initramfs import archive, inspect_elf
from build_touch_initramfs import entries, check_archive
from generate_goodix_config import configuration, SOURCE as BOARD
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'projects/firetabs-android/diagnostic-usb'
sha = lambda data: hashlib.sha256(data).hexdigest()


def parse_log(data):
    text = data.replace(b'\r\n', b'\n')
    values = {}
    for key, value in re.findall(rb'^(VM_TOUCH_[A-Z_]+)=([+-][0-9]{10})$', text, re.M):
        key = key.decode()
        if key in values: raise ValueError('Duplicate touch VM marker')
        values[key] = int(value)
    opened = values.pop('VM_TOUCH_READ_OPEN', -1)
    if (values != {'VM_TOUCH_LABELS': 0, 'VM_TOUCH_DOMAIN': 0, 'VM_TOUCH_ENFORCE': 0,
                   'VM_TOUCH_WRITE_DENIED': -13, 'VM_TOUCH_RELABEL_DENIED': -13,
                   'VM_TOUCH_READ_IDLE': -11, 'VM_TOUCH_IOCTL_DENIED': -13}
            or opened < 0 or text.count(b'VM_TOUCH_PROBE_DONE') != 1
            or any(t in text for t in [b'Kernel panic', b'Internal error: Oops'])):
        raise ValueError('Enforcing touch VM controls failed')
    return values


def run(kernel, expected_kernel, component, output, virtualization):
    if output.exists() or output.is_symlink(): raise ValueError('Fresh VM output required')
    if sha(kernel.read_bytes()) != expected_kernel: raise ValueError('Kernel identity differs')
    report = json.loads((component/'report.json').read_text())
    if report.get('touch_input_profile') is not True: raise ValueError('Touch component required')
    header = (component/'lab_inputs.h').read_bytes()
    arrays = re.findall(rb'static const unsigned char (lab_policy_blob|lab_trial_nonce)\[\]=\{\n([0-9a-fx,\n]+)\n\};\n', header)
    blobs = {n.decode(): bytes(int(v, 16) for v in b.replace(b'\n', b'').split(b',')) for n, b in arrays}
    if (len(arrays) != 2 or set(blobs) != {'lab_policy_blob', 'lab_trial_nonce'}
            or sha(blobs['lab_policy_blob']) != report['policy_sha256']
            or len(blobs['lab_trial_nonce']) != 32 or sha(blobs['lab_trial_nonce']) != report['nonce_sha256']):
        raise ValueError('Policy/nonce identity differs')
    output.mkdir(mode=0o700, parents=True)
    (output/'lab_inputs.h').write_bytes(header)
    cmd = ['clang-18', '--target=aarch64-linux-gnu', '--ld-path='+shutil.which('ld.lld-18'),
           '-nostdlib', '-static', '-Os', '-Wall', '-Wextra', '-Werror', '-ffreestanding', '-fno-builtin',
           '-fno-stack-protector', '-mgeneral-regs-only', '-Wl,--build-id=none,-e,_start', '-I', str(output),
           str(SOURCE/'touch_vm.c'), str(SOURCE/'memory.c'),
           str(ROOT/'projects/firetabs-android/native-kexec/combined_sha256.c'), '-o', str(output/'init')]
    r = subprocess.run(cmd, capture_output=True, timeout=90)
    (output/'compile-private.log').write_bytes(r.stdout+r.stderr)
    if r.returncode: raise ValueError('Touch VM compile failed')
    elf = (output/'init').read_bytes(); inspect_elf(elf)
    items = entries(elf, configuration(BOARD.read_text())); raw = archive(items); check_archive(raw, items)
    initrd = output/'vm-only-initramfs.cpio.gz'; initrd.write_bytes(gzip.compress(raw, mtime=0))
    cmd = ['qemu-system-aarch64', '-machine', 'virt,gic-version=2,virtualization='+virtualization,
           '-cpu', 'cortex-a53', '-smp', '1', '-m', '1536', '-accel', 'tcg', '-nodefaults', '-display', 'none',
           '-serial', 'stdio', '-monitor', 'none', '-nic', 'none', '-no-reboot', '-kernel', str(kernel),
           '-initrd', str(initrd), '-append', 'console=ttyAMA0,115200 rdinit=/init nr_cpus=1 maxcpus=0 loglevel=7 panic=-1']
    process = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    data = bytearray(); began = time.monotonic()
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            while time.monotonic()-began < 60 and len(data) < 2*1024*1024:
                for key, _ in selector.select(.1):
                    data.extend(os.read(key.fd, 65536))
                if b'VM_TOUCH_PROBE_DONE' in data or process.poll() is not None: break
    finally:
        if process.poll() is None: process.terminate()
        try: process.wait(timeout=5)
        except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=5)
    (output/'boot-private.log').write_bytes(data)
    passed = False; failure = None
    try: parse_log(bytes(data)); passed = True
    except ValueError as error: failure = str(error)
    final = {'scope': 'Enforcing static evdev-node VM policy only', 'passed': passed, 'failure': failure,
             'virtualization': virtualization, 'kernel_sha256': expected_kernel, 'policy_sha256': report['policy_sha256'],
             'vm_initramfs_sha256': sha(initrd.read_bytes()), 'boot_log_sha256': sha(data),
             'vm_only': True, 'physical_touch_verified': False, 'virtual_evdev_idle_read_verified': passed,
             'network_attached': False, 'tablet_commands': False, 'elapsed_seconds': round(time.monotonic()-began, 3)}
    (output/'report.json').write_text(json.dumps(final, indent=2)+'\n')
    return final


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for n in ['kernel', 'component', 'output']: p.add_argument('--'+n, type=Path, required=True)
    p.add_argument('--expected-kernel', required=True)
    p.add_argument('--virtualization', choices=['on', 'off'], required=True)
    a = p.parse_args(); r = run(a.kernel, a.expected_kernel, a.component, a.output, a.virtualization)
    print(json.dumps(r, indent=2)); raise SystemExit(0 if r['passed'] else 1)
