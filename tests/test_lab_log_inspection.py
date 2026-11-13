from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from inspect_lab_kernel_log import inspect
from kernel_log_protocol import MAGIC
NONCE = bytes(range(32))


def wire(records):
    result = MAGIC + NONCE
    for i, record in enumerate(records):
        result += struct.pack('>II', i, len(record)) + record
    return result + struct.pack('>II', len(records), 0)


class LogInspection(unittest.TestCase):
    def test_attributable_initial_prefix_and_negative_captures(self):
        records = [b'6,0,0,-;Booting Linux\n', b'5,1,1,-;Linux version 6.12-lab builder\n']
        result = inspect(wire(records), NONCE, '6.12-lab')
        self.assertTrue(result['initial_kernel_prefix_captured'])
        self.assertFalse(result['failed_load_qualified'])
        for bad in [wire([]), wire(records)[:-1], wire(records) + b'x',
                    wire([records[0], records[1].replace(b',1,1,', b',2,1,')]),
                    wire([records[0], records[1].replace(b'6.12-lab', b'3.18-stock')])]:
            with self.assertRaises(ValueError):
                inspect(bad, NONCE, '6.12-lab')
        late = inspect(wire([b'5,9,5,-;late log\n']), NONCE, '6.12-lab')
        self.assertFalse(late['initial_kernel_prefix_captured'])
