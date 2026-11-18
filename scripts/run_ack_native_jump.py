#!/usr/bin/env python3
"""One full ACK Linux RAM boot with physical PID1 capture and bounded return."""
import json
import os
import re
import selectors
import shlex
import subprocess
import time
from pathlib import Path

from prepare_ack_native_bundle import IMAGE_SHA, CONFIG_SHA, RELEASE
from run_native_source_boot import facts, ram_guard, BOOT_SHA, ORIGINAL_CONFIG
from run_reset_payload_jump import geometry, records, sha
from source_usb_console_trial import SourceCapture
from inspect_ack_native_capture import inspect
from build_ack_trampoline import marker as handoff_marker

SCOPE = 'ack-linux-native-jump-1'
RECEIVERS = ['ack_capture_supervisor.py', 'capture_ack_native_console.py', 'capture_lab_kernel_log.py',
             'capture_usb_acm_status.py', 'usb_acm_frame.py', 'kernel_log_protocol.py',
             'capture_live_acm_probe.py']


def run(device, lab_package, manifest, client_report, linked, output,
        nonce, source_report, authorization=None, *, combined_kernel_package=None):
    m = json.loads(manifest.read_text()); c = json.loads(client_report.read_text())
    combined = combined_kernel_package is not None
    ramfix = combined and m.get('target_kind') == 'ack-linux-ramfix-v4'
    cinit = ramfix or combined and m.get('target_kind') == 'ack-linux-cinit-v3'
    kind = 'ack-linux-ramfix-v4' if ramfix else 'ack-linux-cinit-v3' if cinit else 'ack-linux-combined-v2' if combined else 'ack-linux-v1'
    scope = 'ack-linux-native-ramfix-jump-4' if ramfix else 'ack-linux-native-cinit-jump-3' if cinit else 'ack-linux-native-combined-jump-2' if combined else SCOPE
    image_sha = m.get('target_image_sha256') if combined else IMAGE_SHA
    if combined:
        if cinit:
            if ramfix:
                from verify_ack_ramfix_bundle import verify
            else:
                from verify_ack_cinit_bundle import verify
            verify(manifest, combined_kernel_package, nonce=nonce)
        else:
            from verify_ack_combined_bundle import verify
            verify(manifest, combined_kernel_package)
    if m.get('offline_preview') is True or m.get('target_kind') != kind:
        raise ValueError('Fresh maintained-kernel RAM bundle required')
    if (m.get('target_image_sha256') != image_sha or m.get('target_config_sha256') != CONFIG_SHA or
            m.get('target_release') != RELEASE or len(nonce) != 32 or sha(nonce) != m.get('target_nonce_sha256')):
        raise ValueError('Exact ACK kernel/config/PID1 nonce required')
    for flag in ['disk_logger_dt_opt_in_removed', 'all_storage_controllers_disabled',
                 'target_watchdog_driver_disabled', 'live_firmware_reservations_preserved',
                 'legacy_psci_contract_copied_from_live']:
        if m.get(flag) is not True:
            raise ValueError('Reviewed RAM-only DT safety profile required')
    if (m.get('entry') != 0x42018000 or m.get('image_entry') != 0x40000000 or
            m.get('deadline', {}).get('deadline_seconds') != 31 or
            linked.get('early_cpu_shutdown_before_devices') is not True or
            source_report.get('functionfs_hold') is not True):
        raise ValueError('Reviewed source and deadline entry profile required')
    config = linked['artifacts']['.config']['sha256']
    if (m.get('source_config_sha256') != config or m.get('original_boot_sha256') != BOOT_SHA or
            m.get('source_kernel_image_sha256') != linked['artifacts']['arch/arm64/boot/Image']['sha256']):
        raise ValueError('Exact source kernel and original boot binding required')
    trial = m['trial_id']
    if not re.fullmatch('[0-9a-f]{32}', trial) or trial == nonce.hex()[:32]:
        raise ValueError('Fresh independent source challenge required')
    segments = m['segments']
    if ([s['file'] for s in segments] != ['image.bin', 'metadata.bin', 'initrd.bin'] or
            [s['address'] for s in segments] != [0x40000000, 0x42000000, 0x69244000]):
        raise ValueError('Exact aligned ACK layout required')
    for s in segments:
        data = (manifest.parent / s['file']).read_bytes()
        if (len(data) != s['bytes'] or sha(data) != s['sha256'] or
                not 0 < s['bytes'] <= s['memory_bytes'] <= 32 * 1024 * 1024 or s['memory_bytes'] % 4096):
            raise ValueError('Bounded ACK segment differs')
    if c['manifest_sha256'] != sha(manifest.read_bytes()) or c.get('execute_implemented') is not False or c.get('target_kind') != kind:
        raise ValueError('ACK layout-bound load-only client required')
    here = Path(__file__).parent
    expected = dict(scope=scope, runner_sha256=sha(Path(__file__).read_bytes()),
                    manifest_sha256=sha(manifest.read_bytes()), client_sha256=c['client_sha256'],
                    target_image_sha256=image_sha, target_config_sha256=CONFIG_SHA,
                    target_nonce_sha256=sha(nonce), source_config_sha256=config,
                    source_capture_report_sha256=sha(json.dumps(source_report, sort_keys=True).encode()),
                    source_capture_manager_sha256=sha((here / 'source_usb_console_trial.py').read_bytes()),
                    receiver_sha256={name: sha((here / name).read_bytes()) for name in RECEIVERS},
                    owner_approved=True, owner_available=True, maximum_loads=1, maximum_jump_requests=1,
                    target_hardware_deadline_seconds=31, boot_writes_allowed=False,
                    post_jump_reboot_commands_allowed=False, bounded_read_only_return_poll_allowed=True)
    if combined:
        expected['combined_verifier_sha256'] = sha((here / ('verify_ack_ramfix_bundle.py' if ramfix else 'verify_ack_cinit_bundle.py' if cinit else 'verify_ack_combined_bundle.py')).read_bytes())
    if authorization is not None:
        a = json.loads(authorization.read_text())
        if any(type(a.get(k)) is not type(v) or a.get(k) != v for k, v in expected.items()):
            raise ValueError('Exact full ACK RAM-boot authorization required')
    output.mkdir(mode=0o700)
    if authorization is not None:
        os.close(os.open(str(authorization) + '.consumed', os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600))
    r = dict(scope=scope, target_release=RELEASE, target_kind=kind,
             complete=False, load_attempts=0, unload_attempts=0, jump_requests=0,
             target_kernel_boot_proven=False, target_pid1_proven=False, source_console_proven=False,
             fresh_original_android_return=False, normal_shell_restored=False,
             target_hardware_deadline_seconds=31, hardware_deadline_qualified=False,
             boot_written=False, recovery_written=False, automatic_retry=False)
    folder = None; source_capture = None; receiver = None; returned = False

    def save():
        with (output / 'result.json').open('w') as f:
            os.fchmod(f.fileno(), 0o600); json.dump(r, f, indent=2); f.flush(); os.fsync(f.fileno())

    def loaded():
        return device.shell('cat /sys/kernel/kexec_loaded').strip()

    def source():
        f = facts(device)
        if f['boot'] != BOOT_SHA or f['config'] != config or sha(device.shell('cat /sys/firmware/fdt')) != m['source_dtb_sha256']:
            raise ValueError('Current source/DT/restored flash differs')
        geometry(device)
        return f

    assets = [('native-load', c['client_sha256'])] + [(s['file'], s['sha256']) for s in segments]
    remote_capture = lab_package + '/ack-capture-' + trial
    target_token = nonce.hex().encode()
    try:
        save(); device.adb('root'); device.adb('wait-for-device')
        before = source(); ram_guard(device)
        if loaded() != b'0':
            raise ValueError('Existing loaded image refused')
        physical = device.adb('get-devpath').stdout.strip().decode()
        if not re.fullmatch(r'usb:[0-9]+-[0-9]+(?:\.[0-9]+)*', physical):
            raise ValueError('Pinned physical USB port required')
        checks = assets + [('target-nonce-private.bin', sha(nonce))] + list(expected['receiver_sha256'].items())
        for name, digest in checks:
            if device.host(['sha256sum', lab_package + '/' + name]).stdout.split()[0].decode() != digest:
                raise ValueError('Staged ACK artifact differs')
        device.host(['sudo', '-n', 'true'])
        prior = records(device, output / 'pstore-before-private', target_token)
        if any(p['marker_matches'] for p in prior):
            raise ValueError('ACK target nonce already present; refuse replay')
        if combined:
            prefix = (('FIRETABS_CINIT_V3 nonce=' + nonce.hex()) if cinit else ('FIRETABS_ACK_COMBINED_V2 nonce=' + trial)).encode()
            if any(prefix in p.read_bytes() for p in (output / 'pstore-before-private').iterdir() if p.is_file()):
                raise ValueError('Combined trial marker already present; refuse replay')
            r['combined_markers_absent_before_load'] = True
        r.update(preflight='passed', target_nonce_absent_before_load=True, before_records=prior,
                 source_boot_id_sha256=sha(before['boot_id'].encode())); save()
        if authorization is None:
            r['complete'] = True
            return r
        source_capture = SourceCapture(device, lab_package, source_report, trial, physical[4:], output)
        source_capture.start(); r['source_console_proven'] = True
        folder = '/dev/kx-ack-' + trial
        device.shell('mkdir -m 700 ' + folder)
        for name, digest in assets:
            path = folder + '/' + name
            device.adb('push', lab_package + '/' + name, path)
            device.shell('chmod ' + ('700 ' if name == 'native-load' else '600 ') + path)
            if device.shell('sha256sum ' + path).split()[0].decode() != digest:
                raise ValueError('ACK RAM asset differs')
        if source() != before or loaded() != b'0':
            raise ValueError('Source changed before ACK load')
        r['load_attempts'] = 1; save()
        device.shell(folder + '/native-load --load ' + folder, timeout=90)
        if loaded() != b'1' or source() != before:
            raise ValueError('ACK load/source state not verified')
        r['native_load_verified'] = True; save()
        # Arm only after load verification: capture covers the actual entry,
        # not the time spent staging the full Image onto source RAM.
        profile = dict(scope='ack-native-pid1-capture-1', nonce_sha256=sha(nonce),
                       physical_usb_path=physical[4:], usb_id='1209:0001', interface='00', wait_seconds=90,
                       allow_privileged_open=True)
        code = ('import sys,pathlib,json;sys.path.insert(0,' + repr(lab_package) +
                ');from capture_ack_native_console import run;print(json.dumps(run(' + repr(profile) +
                ',pathlib.Path(' + repr(lab_package + '/target-nonce-private.bin') + ').read_bytes(),' +
                repr(remote_capture) + ')))')
        receiver = subprocess.Popen(device.args + ['python3 -c ' + shlex.quote(code)],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
        with selectors.DefaultSelector() as selector:
            selector.register(receiver.stdout, selectors.EVENT_READ)
            if not selector.select(15) or receiver.stdout.readline() != b'ACK_NATIVE_RECEIVER_READY\n':
                raise RuntimeError('ACK receiver did not durably arm')
        if receiver.poll() is not None:
            raise RuntimeError('ACK receiver exited before jump')
        source_capture.intent()
        r.update(original_boot_verified_before_jump=True, recovery_verified_before_jump=True,
                 jump_requests=1, owner_return_required=True); save()
        try:
            device.shell('setprop sys.powerctl reboot,valethon-kexec', timeout=15)
        except RuntimeError:
            r['request_transport_uncertain'] = True
        end = time.monotonic() + 300
        while time.monotonic() < end:
            try:
                ident = device.shell('cat /proc/sys/kernel/random/boot_id', timeout=5).strip().decode()
                if (re.fullmatch('[0-9a-f-]{36}', ident) and ident != before['boot_id'] and
                        device.shell('getprop sys.boot_completed', timeout=5).strip() == b'1'):
                    returned = True; break
            except RuntimeError:
                pass
            time.sleep(1)
        if returned:
            r['different_boot_completed'] = True; save()
            device.adb('root'); device.adb('wait-for-device')
            after = facts(device)
            if after['boot_id'] == before['boot_id'] or after['boot'] != BOOT_SHA or after['config'] != ORIGINAL_CONFIG:
                raise ValueError('Returned installation differs from exact original')
            geometry(device)
            found = records(device, output / 'pstore-after-private', target_token)
            retained = (output / 'pstore-after-private')
            matches = []; entry_seen = False; combined_records = []
            for p in found:
                if p['file'].startswith('console-ramoops'):
                    data = (retained / p['file']).read_bytes()
                    entry_seen |= handoff_marker(trial) in data
                    if combined:
                        if cinit:
                            from verify_ack_cinit_bundle import assess
                            combined_records.append(assess(data, nonce))
                        else:
                            from verify_ack_combined_bundle import assess
                            combined_records.append(assess(data, trial))
                    matches.append(target_token in data and b'Linux version ' + RELEASE.encode() + b' ' in data)
            if combined:
                r['combined_retained_assessments'] = combined_records
                if cinit:
                    r['cinit_retained_assessments'] = combined_records
                    r['cinit_console_proven'] = any(v['fresh_console_identity'] for v in combined_records)
                    r['run_init_seen'] = any(v['run_init_seen'] for v in combined_records)
                else:
                    r['linux_c_entry_proven'] = any(v['linux_c_entry_proven'] for v in combined_records)
                    r['full_image_integrity_proven'] = any(v['full_image_integrity_proven'] for v in combined_records)
            r.update(after_records=found, retained_kernel_boot_proven=any(matches),
                     retained_handoff_marker_seen=entry_seen,
                     target_kernel_boot_proven=any(matches), fresh_original_android_return=True,
                     returned_boot_id_sha256=sha(after['boot_id'].encode()), owner_return_required=False,
                     owner_power_confirmation_pending=True); save()
        stdout, stderr = receiver.communicate(timeout=125)
        for name,data in [('receiver-stdout-private.bin',stdout),('receiver-stderr-private.bin',stderr)]:
            with (output/name).open('xb') as f:os.fchmod(f.fileno(),0o600);f.write(data)
        r['receiver_returncode'] = receiver.poll()
        lines = [line for line in stdout.splitlines() if line.startswith(b'{')]
        r['capture'] = json.loads(lines[-1]) if lines else {'receipt_missing': True}
        if r['capture'].get('receipt_missing'):
            # The worker is detached from SSH. Recover its durable outcome with
            # bounded host-only reads; never reopen a port or repeat the trial.
            code = ('import json,pathlib,time; p=pathlib.Path(' + repr(remote_capture+'.control/result.json') +
                    '); old=pathlib.Path(' + repr(remote_capture+'/receipt.json') +
                    '); control=p.parent/"inputs.json"; start=json.loads(control.read_text()).get("started_monotonic",time.monotonic()) if control.exists() else time.monotonic(); end=start+(135 if control.exists() else 35)\nwhile not p.exists() and not old.exists() and time.monotonic()<end: time.sleep(.1)\n'
                    'print((p if p.exists() else old).read_text() if p.exists() or old.exists() else "{}")')
            saved = json.loads(device.host(['python3','-c',code],timeout=145).stdout)
            if saved:
                r['capture'] = saved;r['capture_recovered_from_durable_host_file'] = True

        raw = device.host(['cat', remote_capture + '/raw.bin'], timeout=30).stdout
        if device.host(['sha256sum', remote_capture + '/raw.bin'], timeout=15).stdout.split()[0].decode() != sha(raw):
            raise ValueError('Captured wire copy differs from host digest')
        p = output / 'ack-kernel-wire-private.bin'
        with p.open('xb') as f:
            os.fchmod(f.fileno(), 0o600); f.write(raw); f.flush(); os.fsync(f.fileno())
        assessment = inspect(raw, nonce, RELEASE)
        if assessment['identity_verified'] and r['capture'].get('endpoint_selected') is not True:
            raise ValueError('Wire evidence lacks physical endpoint provenance')
        r['wire_assessment'] = assessment
        r['target_pid1_proven'] = assessment['target_pid1_proven']
        r['target_kernel_boot_proven'] |= assessment['target_kernel_boot_proven']
        r['outcome'] = ('ack-kernel-and-pid1-proven' if r['target_pid1_proven'] else
                        'ack-kernel-entry-proven' if r['target_kernel_boot_proven'] else 'ack-boot-unproven')
        return r
    except BaseException as e:
        r['failure_kind'] = type(e).__name__
        raise
    finally:
        if receiver and receiver.poll() is None:
            receiver.kill(); receiver.wait(timeout=10)
        if source_capture:
            try:
                if r['jump_requests']:
                    r['source_capture'] = source_capture.collect()
                else:
                    source_capture.abort()
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
        r['complete'] = bool((r['target_pid1_proven'] and r['fresh_original_android_return'] and r['normal_shell_restored'])
                             or (not r['jump_requests'] and not r['load_attempts'] and
                                 r.get('preflight') == 'passed' and r['normal_shell_restored']))
        save()
