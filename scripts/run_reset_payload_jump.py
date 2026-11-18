#!/usr/bin/env python3
"""One captured native jump to an attributable reset target; no retries."""
import hashlib
import json
import os
import re
import time
from pathlib import Path

from build_reset_payload import GEOMETRY, validate
from run_native_source_boot import facts, ram_guard, BOOT_SHA, ORIGINAL_CONFIG
from source_usb_console_trial import SourceCapture

SCOPE = 'native-reset-payload-jump-1'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def geometry(device):
    values = {n: int(device.shell('cat /sys/module/ramoops/parameters/' + n).strip(), 0) for n in GEOMETRY}
    if values != GEOMETRY:
        raise ValueError('Retained-console geometry differs; no reset jump')
    if b'pstore' not in device.shell('cat /proc/consoles'):
        raise ValueError('Existing pstore console required')
    # The dummy backend uses the checked module parameters, including ECC.
    # Refuse an OF-created backend whose ECC may be configured independently.
    paths = device.shell('ls -d /sys/bus/platform/devices/ramoops*').decode().splitlines()
    if len(paths) != 1 or not re.fullmatch(r'/sys/bus/platform/devices/ramoops(?:\.[0-9]+)?', paths[0]):
        raise ValueError('Exact existing ramoops platform device required')
    if device.shell('if test -e ' + paths[0] + '/of_node; then echo yes; else echo no; fi').strip() != b'no':
        raise ValueError('OF-configured retained backend needs separate review')
    return values


def records(device, output, marker):
    output.mkdir(mode=0o700)
    names = device.shell('ls -1 /sys/fs/pstore').decode().splitlines()
    if len(names) > 256 or any(not re.fullmatch('[A-Za-z0-9_.-]+', n) for n in names):
        raise ValueError('Unreviewed retained-record listing')
    total = 0
    result = []
    for name in names:
        n = int(device.shell('wc -c < /sys/fs/pstore/' + name).strip())
        if n < 0 or n > 2 * 1024 * 1024 or total + n > 4 * 1024 * 1024:
            raise ValueError('Retained snapshot exceeds bounded readout')
        data = device.shell('cat /sys/fs/pstore/' + name)
        if len(data) != n:
            raise ValueError('Retained record changed during snapshot')
        p = output / name
        p.write_bytes(data)
        p.chmod(0o600)
        total += n
        # Only console records from this existing backend qualify attribution.
        matches = data.count(marker) if name.startswith('console-ramoops') else 0
        result.append(dict(file=name, bytes=n, sha256=sha(data), marker_matches=matches))
    return result


def classify(result, owner_used_power):
    if owner_used_power is not False:
        return 'not-qualified-pivot-required'
    required = ['target_entry_proven', 'fresh_original_android_return', 'normal_shell_restored']
    return ('reset-target-executed-and-auto-return-qualified' if
            all(result.get(k) is True for k in required) else 'not-qualified-pivot-required')


def run(device, lab_package, manifest, client_report, linked, output,
        payload, source_report, authorization=None):
    m = json.loads(manifest.read_text())
    c = json.loads(client_report.read_text())
    image = (manifest.parent / 'image.bin').read_bytes()
    target_marker = validate(image, payload)
    config = linked['artifacts']['.config']['sha256']
    trial = m['trial_id']
    if m.get('offline_preview') is True or m.get('target_kind') != 'reset-payload-v1':
        raise ValueError('Fresh reset-target bundle required')
    if linked.get('early_cpu_shutdown_before_devices') is not True or source_report.get('functionfs_hold') is not True:
        raise ValueError('Proven early CPU source and capture profile required')
    if not re.fullmatch('[0-9a-f]{32}', trial) or trial == payload['nonce']:
        raise ValueError('Distinct source and target-only nonces required')
    if m.get('source_config_sha256') != config or m.get('reset_nonce') != payload['nonce'] or m['target_image_sha256'] != sha(image):
        raise ValueError('Exact source/reset image binding required')
    if (m.get('original_boot_sha256') != BOOT_SHA or
            m.get('source_kernel_image_sha256') != linked['artifacts']['arch/arm64/boot/Image']['sha256']):
        raise ValueError('Bound original flash and diagnostic source Image required')
    if m.get('reset_payload_report_sha256') != sha(json.dumps(payload, sort_keys=True).encode()):
        raise ValueError('Payload metadata binding differs')
    segments = m['segments']
    if (m['entry'] != 0x42018000 or [s['file'] for s in segments] != ['image.bin', 'metadata.bin', 'initrd.bin'] or
            [s['address'] for s in segments] != [0x40080000, 0x42000000, 0x69244000] or
            (segments[0]['bytes'], segments[0]['memory_bytes']) != (4096, 4096)):
        raise ValueError('Reviewed reset layout required')
    for s in segments:
        data = (manifest.parent / s['file']).read_bytes()
        if (len(data) != s['bytes'] or sha(data) != s['sha256'] or
                not 0 < s['bytes'] <= s['memory_bytes'] <= 32 * 1024 * 1024 or
                s['memory_bytes'] % 4096):
            raise ValueError('Reset segment bytes or bounded extent differs')
    if c['manifest_sha256'] != sha(manifest.read_bytes()) or c.get('execute_implemented') is not False:
        raise ValueError('Bound load-only client required')
    here = Path(__file__).parent
    expected = dict(scope=SCOPE, runner_sha256=sha(Path(__file__).read_bytes()),
                    manifest_sha256=sha(manifest.read_bytes()), client_sha256=c['client_sha256'],
                    target_image_sha256=sha(image), native_config_sha256=config,
                    reset_payload_report_sha256=m['reset_payload_report_sha256'],
                    source_capture_report_sha256=sha(json.dumps(source_report, sort_keys=True).encode()),
                    source_capture_manager_sha256=sha((here / 'source_usb_console_trial.py').read_bytes()),
                    owner_approved=True, owner_available=True, maximum_loads=1, maximum_jump_requests=1,
                    boot_writes_allowed=False, automatic_reboot_commands_allowed=False,
                    bounded_read_only_return_poll_allowed=True)
    if authorization is not None:
        a = json.loads(authorization.read_text())
        if any(type(a.get(k)) is not type(v) or a.get(k) != v for k, v in expected.items()):
            raise ValueError('Exact reset-target authorization required')
    output.mkdir(mode=0o700)
    if authorization is not None:
        os.close(os.open(str(authorization) + '.consumed', os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600))
    r = dict(scope=SCOPE, target_kind='reset-payload-v1', complete=False,
             load_attempts=0, unload_attempts=0, jump_requests=0, boot_written=False,
             recovery_written=False, target_entry_proven=False, target_linux_boot_proven=False,
             fresh_original_android_return=False, normal_shell_restored=False,
             automatic_reset_qualified=False, owner_used_power=None, automatic_retry=False)
    folder = None
    capture = None
    returned = False

    def save():
        with (output / 'result.json').open('w') as f:
            os.fchmod(f.fileno(), 0o600)
            json.dump(r, f, indent=2)
            f.flush()
            os.fsync(f.fileno())

    def source():
        f = facts(device)
        if f['boot'] != BOOT_SHA or f['config'] != config or sha(device.shell('cat /sys/firmware/fdt')) != m['source_dtb_sha256']:
            raise ValueError('Current source kernel/DT/original flash differs')
        geometry(device)
        return f

    def loaded():
        return device.shell('cat /sys/kernel/kexec_loaded').strip()

    try:
        save()
        device.adb('root'); device.adb('wait-for-device')
        before = source()
        ram_guard(device)
        if loaded() != b'0':
            raise ValueError('Pre-existing image refused')
        physical = device.adb('get-devpath').stdout.strip().decode()
        if not re.fullmatch(r'usb:[0-9]+-[0-9]+(?:\.[0-9]+)*', physical):
            raise ValueError('Pinned physical USB port required')
        assets = [('native-load', c['client_sha256'])] + [(s['file'], s['sha256']) for s in segments]
        for name, digest in assets:
            if device.host(['sha256sum', lab_package + '/' + name]).stdout.split()[0].decode() != digest:
                raise ValueError('Staged reset asset differs')
        prior = records(device, output / 'pstore-before-private', target_marker)
        if any(p['marker_matches'] for p in prior):
            raise ValueError('Target-only nonce already present; refuse replay')
        r.update(preflight='passed', source_boot_id_sha256=sha(before['boot_id'].encode()),
                 before_records=prior, target_marker_absent_before_load=True)
        save()
        if authorization is None:
            r['complete'] = True
            return r
        capture = SourceCapture(device, lab_package, source_report, trial, physical[4:], output)
        capture.start()
        folder = '/dev/kx-reset-' + trial
        device.shell('mkdir -m 700 ' + folder)
        for name, digest in assets:
            path = folder + '/' + name
            device.adb('push', lab_package + '/' + name, path)
            device.shell('chmod ' + ('700 ' if name == 'native-load' else '600 ') + path)
            if device.shell('sha256sum ' + path).split()[0].decode() != digest:
                raise ValueError('RAM reset asset differs')
        if source() != before or loaded() != b'0':
            raise ValueError('Source changed before reset load')
        r['load_attempts'] = 1; save()
        device.shell(folder + '/native-load --load ' + folder, timeout=90)
        if loaded() != b'1' or source() != before:
            raise ValueError('Native reset load/source not verified')
        capture.intent()
        r.update(native_load_verified=True, original_boot_verified_before_jump=True,
                 recovery_verified_before_jump=True, jump_requests=1, owner_return_required=True)
        save()
        try:
            device.shell('setprop sys.powerctl reboot,valethon-kexec', timeout=15)
        except RuntimeError:
            r['request_transport_uncertain'] = True
        # Only bounded reads until a different boot has finished. No reboot,
        # root/unroot, unload, settings or console commands during this wait.
        end = time.monotonic() + 300
        while time.monotonic() < end:
            try:
                ident = device.shell('cat /proc/sys/kernel/random/boot_id', timeout=5).strip().decode()
                if (re.fullmatch('[0-9a-f-]{36}', ident) and ident != before['boot_id'] and
                        device.shell('getprop sys.boot_completed', timeout=5).strip() == b'1'):
                    returned = True
                    break
            except RuntimeError:
                pass
            time.sleep(1)
        if not returned:
            r.update(outcome='no-return-pivot-required', pivot_required=True)
            return r
        r['different_boot_completed'] = True
        device.adb('root'); device.adb('wait-for-device')
        after = facts(device)
        if after['boot_id'] == before['boot_id'] or after['boot'] != BOOT_SHA or after['config'] != ORIGINAL_CONFIG:
            raise ValueError('Returned boot is not the exact original installation')
        geometry(device)
        found = records(device, output / 'pstore-after-private', target_marker)
        matches = sum(p['marker_matches'] for p in found)
        r.update(after_records=found, retained_target_marker_matches=matches,
                 target_entry_proven=matches == 1, fresh_original_android_return=True,
                 returned_boot_id_sha256=sha(after['boot_id'].encode()), owner_return_required=False,
                 outcome='owner-confirmation-pending' if matches == 1 else 'no-attributable-marker-pivot-required',
                 pivot_required=matches != 1, owner_confirmation_required=matches == 1)
        return r
    except BaseException as e:
        r.update(failure_kind=type(e).__name__, pivot_required=bool(r['jump_requests']))
        raise
    finally:
        if capture:
            try:
                if r['jump_requests']:
                    r['source_capture'] = capture.collect()
                else:
                    capture.abort()
            except Exception as e:
                r['source_capture_collection_failure'] = type(e).__name__
        if not r['jump_requests']:
            if r['load_attempts']:
                try:
                    if loaded() == b'1':
                        r['unload_attempts'] = 1; save()
                        device.shell(folder + '/native-load --unload ' + folder)
                    if loaded() != b'0':
                        raise RuntimeError('Unload not verified')
                except Exception:
                    r['owner_return_required'] = True
            if folder:
                try:
                    device.shell('rm -f ' + ' '.join(folder + '/' + n for n, _ in assets) + '; rmdir ' + folder)
                except Exception:
                    r['ram_cleanup_unconfirmed'] = True
        if not r['jump_requests'] or returned:
            try:
                device.adb('unroot', timeout=20); device.adb('wait-for-device', timeout=30)
                r['normal_shell_restored'] = b'uid=2000(' in device.shell('id', timeout=10)
            except Exception:
                r['owner_return_required'] = True
        r['complete'] = bool(r.get('preflight') == 'passed' and not r['jump_requests'] and
                             not r['load_attempts'] and r['normal_shell_restored'])
        save()
