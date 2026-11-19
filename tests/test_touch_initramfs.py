import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_touch_initramfs import entries, check_archive
from build_diagnostic_initramfs import archive


class TouchArchive(unittest.TestCase):
    def test_archive_contains_only_fixed_readonly_input_nodes_and_public_config(self):
        items = entries(b'ELF fixture', b'public config')
        nodes = [(n, m, d) for n, m, _, d in items if n.startswith('dev/input/event')]
        self.assertEqual(nodes, [('dev/input/event' + str(i), 0o020400, (13, 64+i)) for i in range(16)])
        self.assertIn(('lib/firmware/goodix/douglas-gt9xx.cfg', 0o100400, b'public config', (0, 0)), items)
        raw = archive(items)
        check_archive(raw, items)
        for offset in [0, 14, 22, 38, 54, 118]:
            damaged = bytearray(raw)
            damaged[offset] ^= 1
            with self.assertRaises(ValueError):
                check_archive(bytes(damaged), items)
        with self.assertRaises(ValueError):
            check_archive(raw + b'nonzero tail', items)


if __name__ == '__main__':
    unittest.main()
