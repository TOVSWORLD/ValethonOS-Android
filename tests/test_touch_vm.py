import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_touch_vm import parse_log


class TouchVM(unittest.TestCase):
    def log(self):
        values = {'LABELS': 0, 'DOMAIN': 0, 'ENFORCE': 0, 'READ_OPEN': 3,
                  'WRITE_DENIED': -13, 'RELABEL_DENIED': -13, 'READ_IDLE': -11, 'IOCTL_DENIED': -13}
        return ''.join(f'VM_TOUCH_{k}={v:+011d}\n' for k, v in values.items()).encode() + b'VM_TOUCH_PROBE_DONE\n'

    def test_exact_virtual_evdev_policy_controls(self):
        data = self.log()
        parse_log(data)
        for bad in [data.replace(b'+0000000003', b'-0000000013'),
                    data.replace(b'-0000000013', b'+0000000000'),
                    data + b'VM_TOUCH_DOMAIN=+0000000000\n',
                    data.replace(b'VM_TOUCH_PROBE_DONE', b'incomplete'), data+b'Kernel panic']:
            with self.assertRaises(ValueError):
                parse_log(bad)
