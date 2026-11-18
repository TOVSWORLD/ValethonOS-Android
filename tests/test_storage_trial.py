import json
from pathlib import Path
import struct
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import run_ack_native_trial as trial
import run_ack_native_jump as jump
import verify_ack_storage_bundle as storage_verify
from capture_ack_native_console import validate_profile
from receive_storage_status import BOOT_SHA256, BOOT_BYTES
from validate_storage_vm import parse_log
import test_ack_native_jump as fixtures
from test_ack_native_capture import NONCE


class StorageTrial(unittest.TestCase):
    def fixture(self):
        f=fixtures.ACKJump('test_full_kernel_and_pid1_proof_with_verified_return');f.setUp();self.addCleanup(f.doCleanups)
        f.manifest.update(target_kind='ack-linux-storage-readonly-v6',internal_emmc_only=True,
                          all_storage_controllers_disabled=False,storage_readonly_profile=True)
        f.write_manifest();c=json.loads(f.c.read_text());c['target_kind']=f.manifest['target_kind'];f.c.write_text(json.dumps(c))
        f.auth.update(scope='ack-linux-native-storage-readonly-jump-6',manifest_sha256=jump.sha(f.m.read_bytes()),
                      combined_verifier_sha256=jump.sha(Path(storage_verify.__file__).read_bytes()))
        f.a.write_text(json.dumps(f.auth));f.console=b'old source console'
        f.d.wire=b'VSTORE01'+NONCE+struct.pack('<IIiIQQQII',1,5,0,31,BOOT_BYTES,BOOT_BYTES,0,179,5)+bytes.fromhex(BOOT_SHA256)
        return f

    def test_storage_success_needs_no_log_records_and_one_jump(self):
        f=self.fixture()
        with patch.object(storage_verify,'verify',return_value={'storage_bundle_verified':True}):
            result=f.invoke(combined_kernel_package=Path('fake-kernel'),storage_component=Path('fake-component'))
        self.assertTrue(result['complete']);self.assertTrue(result['storage_readonly_verified'])
        self.assertFalse(result['target_pid1_proven']) # Keep legacy log-specific metric separate.
        self.assertEqual(result['outcome'],'ack-storage-readonly-verified')
        self.assertEqual((result['load_attempts'],result['jump_requests']),(1,1))
        self.assertTrue(result['fresh_original_android_return'])

    def test_wrong_endpoint_never_qualifies_storage(self):
        f=self.fixture()
        with patch.object(storage_verify,'verify',return_value={'storage_bundle_verified':True}):
            result=f.invoke(process=fixtures.Process(endpoint=False),combined_kernel_package=Path('fake-kernel'),storage_component=Path('fake-component'))
        self.assertFalse(result['complete']);self.assertFalse(result['storage_readonly_verified'])

    def test_old_header_cannot_pass_storage(self):
        f=self.fixture();f.d.wire=b'VLOG0002'+NONCE
        with patch.object(storage_verify,'verify',return_value={'storage_bundle_verified':True}):
            with self.assertRaises(ValueError):f.invoke(combined_kernel_package=Path('fake-kernel'),storage_component=Path('fake-component'))
        self.assertFalse(f.result()['complete'])

    def test_storage_requires_explicit_component_before_device_access(self):
        f=self.fixture()
        with self.assertRaises(ValueError):f.invoke(combined_kernel_package=Path('fake-kernel'))
        self.assertEqual(f.d.calls,[])

    def test_consumed_old_scope_cannot_authorize_storage(self):
        args=SimpleNamespace(policy=Path('unused'),ramfix=True,cinit=False,combined=False,storage_readonly=True)
        with patch.object(trial,'read',return_value={'scope':'ack-linux-usb-end-to-end-two-stage-5','target_kind':'ack-linux-ramfix-v4'}):
            with self.assertRaises(ValueError):trial.validate(args)

    def test_storage_mode_requires_ramfix_and_distinct_protocol(self):
        for ramfix,logs in [(False,False),(True,True)]:
            args=SimpleNamespace(policy=Path('unused'),ramfix=ramfix,cinit=False,combined=False,storage_readonly=True,usb_end_to_end=logs)
            with patch.object(trial,'read',return_value={}):
                with self.assertRaises(ValueError):trial.validate(args)

    def test_vm_duplicate_and_missing_controls_rejected(self):
        with self.assertRaises(ValueError):parse_log(b'VM_STORAGE_PROBE_DONE\n')
        with self.assertRaises(ValueError):parse_log(b'VM_STORAGE_DOMAIN=+0000000000\n'*2)
