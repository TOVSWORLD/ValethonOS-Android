from pathlib import Path
import hashlib
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_lab_policy_vm import parse_log, generated_header


class LabPolicyVM(unittest.TestCase):
    def log(self):
        values = {'VM_DOMAIN': 0, 'VM_LABELS': 0, 'VM_PROC': 0, 'VM_SYS': 0, 'VM_KMSG_OPEN': 3, 'VM_KMSG_READ': 64,
                  'VM_GENERIC_FLAGS_OPEN': -22, 'VM_UDC_DIR': 3, 'VM_CONFIGFS': 0, 'VM_NAMESPACE_BEFORE': 0,
                  'VM_REAL_CONFIGFS_SETUP_WITHOUT_BIND': 0, 'VM_REAL_CONFIGFS_CLEANUP': 0, 'VM_NAMESPACE_AFTER': 0}
        return b''.join((key + '=' + format(value, '+011d') + '\n').encode() for key, value in values.items()) + b'VM_FILESYSTEM_PROBE_DONE\n'

    def test_vm_success_requires_all_markers_and_old_flag_failure(self):
        data = self.log()
        self.assertEqual(parse_log(data)['VM_GENERIC_FLAGS_OPEN'], -22)
        for bad in [data.replace(b'VM_LABELS=+0000000000\n', b''),
                    data.replace(b'VM_GENERIC_FLAGS_OPEN=-0000000022', b'VM_GENERIC_FLAGS_OPEN=+0000000003'),
                    data.replace(b'VM_REAL_CONFIGFS_SETUP_WITHOUT_BIND=+0000000000', b'VM_REAL_CONFIGFS_SETUP_WITHOUT_BIND=-0000000013'),
                    data + b'VM_SYS=+0000000000\n', data + b'avc:  denied { write }\n', data + b'Kernel panic\n']:
            with self.assertRaises(ValueError):
                parse_log(bad)

    def test_generated_inputs_require_exact_data_and_no_code(self):
        policy, nonce = bytes(range(32)), bytes(range(32, 64))
        def array(name, value):
            return b'static const unsigned char ' + name + b'[]={\n' + b','.join(b'0x%02x' % x for x in value) + b'\n};\n'
        data = array(b'lab_policy_blob', policy) + array(b'lab_trial_nonce', nonce)
        report = {'policy_sha256': hashlib.sha256(policy).hexdigest(), 'nonce_sha256': hashlib.sha256(nonce).hexdigest()}
        self.assertEqual(generated_header(data, report), data)
        for bad in [data + b'#include "unexpected.h"\n', data.replace(b'0x00', b'0xff'), data.replace(b'0x00', b'0x100')]:
            with self.assertRaises(ValueError):
                generated_header(bad, report)
