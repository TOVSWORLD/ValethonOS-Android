import io
import json
import subprocess
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_ack_native_jump as runner
from test_native_jump_run import Device
from test_ack_native_capture import wire, NONCE

CFG = 'a' * 64
TARGET_CONFIG = 'b' * 64


class Fake(Device):
    args = []

    def __init__(self, digests, data):
        super().__init__(); self.digests = digests; self.wire = data

    def adb(self, *args, **kw):
        super().adb(*args, **kw)
        return subprocess.CompletedProcess(args, 0, b'usb:1-2\n' if args[0] == 'get-devpath' else b'', b'')

    def shell(self, command, **kw):
        if command.startswith('sha256sum '):
            self.calls.append(command)
            return (self.digests[command.split('/')[-1]] + ' file\n').encode()
        return super().shell(command, **kw)

    def host(self, args, **kw):
        if args[0] == 'cat': data = self.wire
        elif args[0] == 'sha256sum':
            name = args[-1].split('/')[-1]
            value = runner.sha(self.wire) if name == 'raw.bin' else self.digests[name]
            data = (value + ' file\n').encode()
        else: data = b''
        return subprocess.CompletedProcess(args, 0, data, b'')


class Process:
    def __init__(self, endpoint=True, ready=True):
        self.stdout = io.BytesIO(b'ACK_NATIVE_RECEIVER_READY\n' if ready else b'wrong\n')
        self.finished = False; self.endpoint = endpoint

    def poll(self): return 0 if self.finished else None
    def communicate(self, **kw):
        self.finished = True
        return json.dumps({'endpoint_selected': self.endpoint, 'complete': True}).encode(), b''
    def kill(self): self.finished = True
    def wait(self, **kw): return 0


class ACKJump(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup); self.p = Path(tmp.name)
        files = {'image.bin': b'controlled fake Image for supervisor tests', 'metadata.bin': b'dtb', 'initrd.bin': b'initrd'}
        self.image_sha = runner.sha(files['image.bin'])
        for name, data in files.items(): (self.p / name).write_bytes(data)
        self.m = self.p / 'manifest'; self.c = self.p / 'client'; self.a = self.p / 'auth'
        self.manifest = dict(target_kind='ack-linux-v1', target_release=runner.RELEASE,
            target_image_sha256=self.image_sha, target_config_sha256=TARGET_CONFIG,
            source_config_sha256=CFG, source_kernel_image_sha256='c' * 64,
            source_dtb_sha256=runner.sha(b'dtb'), original_boot_sha256=runner.BOOT_SHA,
            target_nonce_sha256=runner.sha(NONCE), trial_id='1' * 32,
            entry=0x42018000, image_entry=0x40000000, deadline={'deadline_seconds': 31},
            disk_logger_dt_opt_in_removed=True, all_storage_controllers_disabled=True,
            target_watchdog_driver_disabled=True, live_firmware_reservations_preserved=True,
            legacy_psci_contract_copied_from_live=True,
            segments=[dict(file=n, sha256=runner.sha(b), bytes=len(b), memory_bytes=4096, address=at)
                      for (n, b), at in zip(files.items(), [0x40000000, 0x42000000, 0x69244000])])
        self.write_manifest()
        self.source = {'functionfs_hold': True}
        self.linked = dict(early_cpu_shutdown_before_devices=True,
            artifacts={'.config': {'sha256': CFG}, 'arch/arm64/boot/Image': {'sha256': 'c' * 64}})
        self.digests = {n: runner.sha(b) for n, b in files.items()}
        self.digests.update({'native-load': 'a' * 64, 'target-nonce-private.bin': runner.sha(NONCE)})
        self.digests.update({n: runner.sha((Path('scripts') / n).read_bytes()) for n in runner.RECEIVERS})
        self.auth = dict(scope=runner.SCOPE, runner_sha256=runner.sha(Path(runner.__file__).read_bytes()),
            manifest_sha256=runner.sha(self.m.read_bytes()), client_sha256='a' * 64,
            target_image_sha256=self.image_sha, target_config_sha256=TARGET_CONFIG,
            target_nonce_sha256=runner.sha(NONCE), source_config_sha256=CFG,
            source_capture_report_sha256=runner.sha(json.dumps(self.source, sort_keys=True).encode()),
            source_capture_manager_sha256=runner.sha(Path('scripts/source_usb_console_trial.py').read_bytes()),
            receiver_sha256={n: self.digests[n] for n in runner.RECEIVERS},
            owner_approved=True, owner_available=True, maximum_loads=1, maximum_jump_requests=1,
            target_hardware_deadline_seconds=31, boot_writes_allowed=False,
            post_jump_reboot_commands_allowed=False, bounded_read_only_return_poll_allowed=True)
        self.a.write_text(json.dumps(self.auth)); self.d = Fake(self.digests, wire())
        self.console = b'Linux version ' + runner.RELEASE.encode() + b' build\nKernel command line: valethon.native_trial=' + NONCE.hex().encode()

    def write_manifest(self):
        self.m.write_text(json.dumps(self.manifest))
        self.c.write_text(json.dumps(dict(manifest_sha256=runner.sha(self.m.read_bytes()),
            client_sha256='a' * 64, execute_implemented=False, target_kind='ack-linux-v1')))

    def invoke(self, execute=True, process=None, **options):
        def facts(d):
            return dict(boot=runner.BOOT_SHA, config=runner.ORIGINAL_CONFIG if d.target else CFG,
                boot_id=('22222222' if d.target else '11111111') + '-1111-1111-1111-111111111111')
        def records(d, out, marker):
            out.mkdir(); data = self.console if d.target else b'old console'
            (out / 'console-ramoops').write_bytes(data)
            return [{'file': 'console-ramoops', 'marker_matches': data.count(marker)}]
        with patch.object(runner, 'IMAGE_SHA', self.image_sha), patch.object(runner, 'CONFIG_SHA', TARGET_CONFIG), \
             patch.object(runner, 'facts', side_effect=facts), patch.object(runner, 'geometry'), \
             patch.object(runner, 'records', side_effect=records), patch.object(runner, 'SourceCapture') as capture, \
             patch.object(runner.subprocess, 'Popen', return_value=process or Process()), \
             patch.object(runner.selectors, 'DefaultSelector') as selector:
            capture.return_value.collect.return_value = {'native_entry_seen': True}
            selector.return_value.select.return_value = [True]
            return runner.run(self.d, '/lab', self.m, self.c, self.linked, self.p / 'out', NONCE,
                              self.source, self.a if execute else None, **options)

    def result(self): return json.loads((self.p / 'out/result.json').read_text())

    def test_full_kernel_and_pid1_proof_with_verified_return(self):
        r = self.invoke()
        self.assertTrue(r['target_kernel_boot_proven']); self.assertTrue(r['target_pid1_proven'])
        self.assertTrue(r['fresh_original_android_return']); self.assertTrue(r['complete'])
        self.assertEqual((r['load_attempts'], r['jump_requests']), (1, 1))
        self.assertFalse(r['hardware_deadline_qualified'])

    def test_display_banner_status_does_not_claim_visible_pixels(self):
        self.manifest.update(target_kind='ack-linux-display-v7', internal_emmc_only=True)
        self.write_manifest()
        client = json.loads(self.c.read_text())
        client['target_kind'] = 'ack-linux-display-v7'
        self.c.write_text(json.dumps(client))
        self.auth.update(scope='ack-linux-native-display-functional-jump-7',
                         manifest_sha256=runner.sha(self.m.read_bytes()),
                         combined_verifier_sha256=runner.sha(Path('scripts/verify_display_bundle.py').read_bytes()))
        self.a.write_text(json.dumps(self.auth))
        self.d.wire = (b'VDISP001' + NONCE +
                       struct.pack('<IIiIIIIIQIi',1,3,0,7,800,1280,32,3200,4096000,13,0) +
                       b'mediatekdrmfb' + bytes(19))
        self.console = b'old record; no kernel log required'
        with patch('display_kernel_contract.verify', return_value={
                'config_sha256': TARGET_CONFIG, 'target_release': runner.RELEASE}), \
                patch('verify_display_bundle.verify') as verify:
            result = self.invoke(combined_kernel_package=self.p, display_component=self.p,
                                 baseline_kernel_package=self.p)
            verify.assert_called_once_with(self.m,self.p,self.p,self.p,nonce=NONCE)
        self.assertTrue(result['display_banner_status_verified'])
        self.assertTrue(result['complete'])
        self.assertFalse(result['physical_pixels_confirmed'])
        self.assertTrue(result['owner_visual_confirmation_pending'])
        self.assertEqual((result['load_attempts'],result['jump_requests']),(1,1))

    def display_error_result(self,kind,scope):
        self.manifest.update(target_kind=kind, internal_emmc_only=True)
        self.write_manifest()
        client=json.loads(self.c.read_text());client['target_kind']=self.manifest['target_kind']
        self.c.write_text(json.dumps(client))
        self.auth.update(scope=scope,
                         manifest_sha256=runner.sha(self.m.read_bytes()),
                         combined_verifier_sha256=runner.sha(Path('scripts/verify_display_bundle.py').read_bytes()))
        self.a.write_text(json.dumps(self.auth))
        payload=b'3,1,100,-;mediatek-drm probe failed -517\n'
        self.d.wire=(b'VDISP002'+NONCE+
                     struct.pack('<IIiIIIIIQIi',2,1,-110,1,0,0,0,0,0,0,0)+bytes(32)+
                     b'VKMSG001'+NONCE+struct.pack('<IiII',len(payload),0,1,1)+payload)
        self.console=b'old record'
        with patch('display_kernel_contract.verify',return_value={
                'config_sha256':TARGET_CONFIG,'target_release':runner.RELEASE}), \
                patch('verify_display_bundle.verify'):
            old=dict(self.auth,scope='ack-linux-native-display-mm-power-jump-10' if kind.endswith('v11') else 'ack-linux-native-display-pwm-jump-9' if kind.endswith('v10') else 'ack-linux-native-display-errors-jump-8' if kind.endswith('v9') else 'ack-linux-native-display-functional-jump-7')
            self.a.write_text(json.dumps(old))
            with self.assertRaises(ValueError):
                self.invoke(combined_kernel_package=self.p,display_component=self.p,
                            baseline_kernel_package=self.p)
            self.assertEqual(self.d.calls,[])
            self.a.write_text(json.dumps(self.auth))
            result=self.invoke(combined_kernel_package=self.p,display_component=self.p,
                               baseline_kernel_package=self.p)
        self.assertTrue(result['display_status']['kernel_snapshot_received'])
        self.assertFalse(result['display_banner_status_verified'])
        self.assertFalse(result['complete'])
        self.assertTrue(result['fresh_original_android_return'])
        self.assertTrue(result['pid1_usb_identity_proven'])
        self.assertEqual((result['load_attempts'],result['jump_requests']),(1,1))

    def test_display_failure_receives_kernel_errors_without_requiring_banner(self):
        self.display_error_result('ack-linux-display-errors-v8','ack-linux-native-display-errors-jump-8')

    def test_pwm_display_uses_fresh_scope_and_keeps_error_capture(self):
        self.display_error_result('ack-linux-display-pwm-v9','ack-linux-native-display-pwm-jump-9')

    def test_mm_power_fix_requires_new_scope(self):
        self.display_error_result('ack-linux-display-mm-power-v10','ack-linux-native-display-mm-power-jump-10')

    def test_pinconf_fix_requires_new_scope(self):
        self.display_error_result('ack-linux-display-pinconf-v11','ack-linux-native-display-pinconf-jump-11')

    def test_fresh_pid1_usb_identity_is_a_milestone_without_log_payload(self):
        self.d.wire = b'VLOG0002' + NONCE
        self.console = b'old source record'
        r = self.invoke()
        self.assertTrue(r['pid1_usb_identity_proven'])
        self.assertFalse(r['target_pid1_proven']); self.assertFalse(r['complete'])
        self.assertEqual(r['outcome'],'ack-pid1-usb-identity-proven-stream-incomplete')

    def test_lost_ssh_stdout_recovers_durable_result_without_reopening(self):
        class LostSSH(Process):
            def communicate(self, **kw):
                self.finished = True
                return b'', b'fixture SSH connection lost'
            def poll(self): return 255 if self.finished else None
        original = self.d.host
        def host(args, **kw):
            if args[0] == 'python3':
                return subprocess.CompletedProcess(args,0,json.dumps({'complete':True,'endpoint_selected':True}).encode(),b'')
            return original(args,**kw)
        self.d.host = host
        r = self.invoke(process=LostSSH())
        self.assertTrue(r['capture_recovered_from_durable_host_file'])
        self.assertTrue(r['target_pid1_proven']); self.assertTrue(r['complete'])
        self.assertEqual(r['receiver_returncode'],255)
        self.assertEqual((r['load_attempts'],r['jump_requests']),(1,1))
        self.assertEqual((self.p/'out/receiver-stderr-private.bin').read_bytes(),b'fixture SSH connection lost')

    def test_retained_kernel_record_without_usb_does_not_prove_pid1(self):
        self.d.wire = b''
        r = self.invoke(process=Process(endpoint=False))
        self.assertTrue(r['target_kernel_boot_proven']); self.assertFalse(r['target_pid1_proven'])
        self.assertFalse(r['complete'])

    def test_return_without_target_evidence_is_not_linux_success(self):
        self.d.wire = b''; self.console = b'old source record'
        r = self.invoke(process=Process(endpoint=False))
        self.assertFalse(r['target_kernel_boot_proven']); self.assertFalse(r['complete'])

    def test_retained_handoff_marker_is_not_linux_boot_proof(self):
        self.d.wire = b''; self.console = runner.handoff_marker(self.manifest['trial_id'])
        r = self.invoke(process=Process(endpoint=False))
        self.assertTrue(r['retained_handoff_marker_seen'])
        self.assertFalse(r['target_kernel_boot_proven']); self.assertFalse(r['complete'])

    def test_wrong_physical_endpoint_cannot_qualify_wire(self):
        with self.assertRaises(ValueError): self.invoke(process=Process(endpoint=False))
        self.assertFalse(self.result()['target_pid1_proven'])

    def test_legacy_scope_cannot_authorize_maintained_kernel(self):
        self.auth['scope'] = 'native-reset-payload-jump-1'; self.a.write_text(json.dumps(self.auth))
        with self.assertRaises(ValueError): self.invoke()
        self.assertEqual(self.d.calls, [])

    def test_deadline_and_legacy_firmware_profile_are_required(self):
        self.manifest['legacy_psci_contract_copied_from_live'] = False; self.write_manifest()
        with self.assertRaises(ValueError): self.invoke()
        self.assertEqual(self.d.calls, [])

    def test_source_disk_must_stay_restored_before_load(self):
        self.d.postload_dt = True
        with self.assertRaises(ValueError): self.invoke()
        self.assertEqual((self.result()['unload_attempts'], self.result()['jump_requests']), (1, 0))

    def test_missing_receiver_ready_aborts_without_jump(self):
        with self.assertRaises(RuntimeError): self.invoke(process=Process(ready=False))
        self.assertEqual((self.result()['unload_attempts'], self.result()['jump_requests']), (1, 0))

    def test_preflight_does_not_load(self):
        r = self.invoke(execute=False)
        self.assertTrue(r['complete']); self.assertEqual(r['load_attempts'], 0)

    def test_no_post_jump_unload_root_or_reboot_when_tablet_does_not_return(self):
        self.d.wire = b''
        with patch.object(runner.time, 'monotonic', side_effect=[0, 301]):
            r = self.invoke(process=Process(endpoint=False))
        at = self.d.calls.index('setprop sys.powerctl reboot,valethon-kexec')
        self.assertEqual(self.d.calls[at + 1:], [])
        self.assertEqual((r['jump_requests'], r['unload_attempts']), (1, 0))


if __name__ == '__main__': unittest.main()
