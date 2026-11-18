from pathlib import Path
import copy
import gzip
import json
import struct
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from pack_lab_log_boot import assemble


class LabBootPack(unittest.TestCase):
    def inputs(self):
        image = bytearray(4096)
        struct.pack_into('<QQQ', image, 8, 0, 0x100000, 0)
        image[56:60] = b'ARMd'
        dt = bytearray(64)
        struct.pack_into('>II', dt, 0, 0xd00dfeed, len(dt))
        return [bytes(image), gzip.compress(image, mtime=0), bytes(dt),
                gzip.compress(b'archive fixture', mtime=0),
                json.loads((ROOT / 'projects/firetabs-android/kernel/lab-log/package-contract.json').read_text()),
                json.loads((ROOT / 'evidence/independent-recovery/trial-placement-metadata.json').read_text())]

    def test_complete_image_layout_and_negative_bounds(self):
        args = self.inputs()
        full, report = assemble(*args)
        self.assertEqual(len(full), 16 * 1024 * 1024)
        self.assertEqual(full[:8], b'ANDROID!')
        self.assertEqual(struct.unpack_from('<I', full, 12)[0], 0x40000000)
        self.assertEqual(full[576:596].hex(), report['component_sha1'])
        for kind in ['reserved', 'initramfs', 'unaligned', 'capacity', 'tail']:
            bad = copy.deepcopy(args)
            if kind == 'reserved':
                bad[5]['reserved'].append({'reg': [{'address': '0x40000000', 'bytes': 1}]})
            elif kind == 'initramfs':
                bad[4]['initramfs_address'] = 0x40000000
            elif kind == 'unaligned':
                bad[4]['ram_base'] += 1
            elif kind == 'capacity':
                bad[4]['decoded_image_limit_bytes'] = 100
            else:
                bad[1] += b'junk'
            with self.assertRaises(ValueError, msg=kind):
                assemble(*bad)
