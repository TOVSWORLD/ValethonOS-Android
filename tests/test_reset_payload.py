"""Instruction-level tests of the assembled, nonce-bearing AArch64 payload."""
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_reset_payload import build, marker, extract, CONSOLE, CAPACITY
try:
    import unicorn as uni
    from unicorn import arm64_const as reg
except ImportError:
    uni = None

IMAGE = 0x40080000
WDT = 0x10007000


def emulate(image, *, start=0, size=0, signature=0x43474244, el=1, sctlr=0):
    u = uni.Uc(uni.UC_ARCH_ARM64, uni.UC_MODE_ARM)
    u.mem_map(IMAGE, 4096)
    u.mem_write(IMAGE, image)
    u.mem_map(CONSOLE - 4096, 73728)
    before = b'\xa5' * 65536
    u.mem_write(CONSOLE, before)
    u.mem_write(CONSOLE, struct.pack('<III', signature, start, size))
    initial = bytes(u.mem_read(CONSOLE, 65536))
    u.mem_map(WDT, 4096)
    mode = 0x1ff
    u.mem_write(WDT, struct.pack('<I', mode))
    u.reg_write(reg.UC_ARM64_REG_PSTATE, 0x3c5)
    u.reg_write(reg.UC_ARM64_REG_CP_REG, (1, 0, 3, 0, 0, 0))
    # Unicorn's PSTATE setter does not switch its CPU exception level. Inject
    # MRS results for branch controls; do not pretend a guest MMU was configured.
    if el != 1 or sctlr:
        def mrs(uc, at, n, data):
            instruction = struct.unpack('<I', uc.mem_read(at, 4))[0]
            key = instruction & ~31
            if key == 0xd5384240:  # MRS Xt, CurrentEL
                value = el << 2
            elif key in [0xd5381000, 0xd53c1000]:  # SCTLR_EL1 / EL2
                value = sctlr
            else:
                return
            uc.reg_write(reg.UC_ARM64_REG_X0 + (instruction & 31), value)
            uc.reg_write(reg.UC_ARM64_REG_PC, at + 4)
        u.hook_add(uni.UC_HOOK_CODE, mrs)
    writes = []

    def write(uc, access, at, n, value, data):
        writes.append((at, n, value))
        if at == WDT + 0x14:
            uc.emu_stop()

    u.hook_add(uni.UC_HOOK_MEM_WRITE, write)
    # Unsupported state must terminate in the bounded WFE loop without writes.
    u.emu_start(IMAGE, IMAGE + 4096, count=4000)
    return u, initial, writes


@unittest.skipIf(uni is None, 'Use the isolated reset-payload-tools environment for required ARM64 qualification')
class ResetInstructions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / 'payload'
        cls.report = build(cls.out, '0123456789abcdef0123456789abcdef')
        cls.image = (cls.out / 'Image').read_bytes()
        cls.line = marker(cls.report['nonce'])

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_append_empty_partial_full_and_wrap_at_both_exception_levels(self):
        for el in [1, 2]:
            for start, size in [(0, 0), (1, 1), (100, 100),
                                (0, CAPACITY), (CAPACITY - len(self.line), CAPACITY),
                                (CAPACITY - 1, CAPACITY), (CAPACITY - 10, CAPACITY)]:
                with self.subTest(el=el, start=start, size=size):
                    u, before, writes = emulate(self.image, start=start, size=size, el=el)
                    expected = bytearray(before)
                    for i, b in enumerate(self.line):
                        expected[12 + (start + i) % CAPACITY] = b
                    struct.pack_into('<II', expected, 4, (start + len(self.line)) % CAPACITY,
                                     min(size + len(self.line), CAPACITY))
                    self.assertEqual(bytes(u.mem_read(CONSOLE, 65536)), expected)
                    self.assertEqual(writes[-2:], [(WDT, 4, (0x1ff & ~0x49) | 0x22000010),
                                                   (WDT + 0x14, 4, 0x1209)])
                    self.assertEqual(len(writes), len(self.line) + 4)
                    for at, n, _ in writes:
                        self.assertTrue(CONSOLE + 4 <= at < CONSOLE + 12 or
                                        CONSOLE + 12 <= at < CONSOLE + 65536 or
                                        at in [WDT, WDT + 0x14])
                    self.assertEqual(bytes(u.mem_read(CONSOLE - 4096, 4096)), bytes(4096))
                    self.assertEqual(bytes(u.mem_read(CONSOLE + 65536, 4096)), bytes(4096))

    def test_invalid_ring_never_changes_retained_memory(self):
        for params in [dict(signature=0), dict(start=CAPACITY), dict(size=CAPACITY + 1),
                       dict(start=100, size=99), dict(start=0xffffffff, size=0xffffffff)]:
            with self.subTest(params=params):
                u, before, writes = emulate(self.image, **params)
                self.assertEqual(bytes(u.mem_read(CONSOLE, 65536)), before)
                self.assertEqual([at for at, _, _ in writes], [WDT, WDT + 0x14])

    def test_cache_or_translation_enabled_refuses_all_writes(self):
        for el in [1, 2]:
            for sctlr in [1, 4, 5]:
                with self.subTest(el=el, sctlr=sctlr):
                    _, _, writes = emulate(self.image, el=el, sctlr=sctlr)
                    self.assertEqual(writes, [])

    def test_unsupported_exception_level_refuses_all_writes(self):
        _, _, writes = emulate(self.image, el=3)
        self.assertEqual(writes, [])


class InputGuards(unittest.TestCase):
    def test_nonce_is_exact_and_not_a_shell_or_assembly_expression(self):
        for bad in ['', 'a' * 31, 'A' * 32, '\n' * 32, '0' * 31 + '"', None]:
            with self.assertRaises(ValueError):
                marker(bad)

    def test_arbitrary_binary_is_not_an_assembled_payload(self):
        for bad in [b'', bytes(4096), b'\x7fELF' + bytes(256)]:
            with self.assertRaises(ValueError):
                extract(bad)


if __name__ == '__main__':
    unittest.main()
