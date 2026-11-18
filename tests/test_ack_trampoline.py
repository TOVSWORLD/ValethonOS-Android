import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_ack_trampoline import build, marker
try:
    import unicorn as uni
    from unicorn import arm64_const as reg
except ImportError:
    uni = None

ENTRY, IMAGE, FDT, CONSOLE, WDT, CAPACITY = 0x42018000, 0x40000000, 0x42000000, 0x444bf000, 0x10007000, 65524


def execute(code, *, start=0, size=0, signature=0x43474244, el=1, sctlr=0, bad_readback=None):
    u = uni.Uc(uni.UC_ARCH_ARM64, uni.UC_MODE_ARM)
    for at, n in [(ENTRY, 4096), (IMAGE, 4096), (FDT, 4096),
                  (CONSOLE - 4096, 73728), (WDT, 4096)]:
        u.mem_map(at, n)
    u.mem_write(ENTRY, code)
    u.mem_write(CONSOLE, struct.pack('<III', signature, start, size) + b'\xa5' * CAPACITY)
    before = bytes(u.mem_read(CONSOLE, 65536))
    u.mem_write(WDT, struct.pack('<I', 0x1ff))
    u.reg_write(reg.UC_ARM64_REG_PSTATE, 0x3c5)
    u.reg_write(reg.UC_ARM64_REG_CP_REG, (1, 0, 3, 0, 0, 0))
    writes, modes = [], []
    result = {'linux_entry_reached': False, 'reset_requested': False}
    mode_reads = 0

    def instruction(uc, at, n, _):
        if at == IMAGE:
            result['linux_entry_reached'] = True
            result['arguments'] = [uc.reg_read(reg.UC_ARM64_REG_X0 + i) for i in range(4)]
            uc.emu_stop()
        if el != 1 or sctlr:
            word = struct.unpack('<I', uc.mem_read(at, 4))[0]
            key = word & ~31
            if key == 0xd5384240:
                value = el << 2
            elif key in [0xd5381000, 0xd53c1000]:
                value = sctlr
            else:
                return
            uc.reg_write(reg.UC_ARM64_REG_X0 + (word & 31), value)
            uc.reg_write(reg.UC_ARM64_REG_PC, at + 4)

    def read(uc, access, at, n, value, _):
        nonlocal mode_reads
        if at == WDT:
            mode_reads += 1
            v = struct.unpack('<I', uc.mem_read(WDT, 4))[0] & 0x00ffffff
            if mode_reads == 2 and bad_readback == 'mode':
                v &= ~1
            uc.mem_write(WDT, struct.pack('<I', v))
        if at == WDT + 4:
            uc.mem_write(WDT + 4, struct.pack('<I', 0 if bad_readback == 'length' else 0xf800))

    def write(uc, access, at, n, value, _):
        writes.append((at, n, value))
        if at == WDT:
            modes.append(value)
        if at == WDT + 0x14:
            result['reset_requested'] = True
            uc.emu_stop()

    u.hook_add(uni.UC_HOOK_CODE, instruction)
    u.hook_add(uni.UC_HOOK_MEM_READ, read)
    u.hook_add(uni.UC_HOOK_MEM_WRITE, write)
    u.emu_start(ENTRY, ENTRY + 4096, count=6000)
    return u, before, writes, result


@unittest.skipIf(uni is None, 'Required qualification uses the isolated ARM64 emulator')
class EntryInstructions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.code, cls.report = build(Path(cls.tmp.name) / 'entry', 'c' * 32)
        cls.line = marker('c' * 32)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_deadline_readback_ring_wrap_and_linux_entry_arguments(self):
        for el in [1, 2]:
            for start, size in [(0, 0), (100, 100), (0, CAPACITY),
                                (CAPACITY - 1, CAPACITY), (CAPACITY - 20, CAPACITY)]:
                with self.subTest(el=el, start=start):
                    u, before, writes, result = execute(self.code, start=start, size=size, el=el)
                    self.assertTrue(result['linux_entry_reached'])
                    self.assertFalse(result['reset_requested'])
                    self.assertEqual(result['arguments'], [FDT, 0, 0, 0])
                    expected = bytearray(before)
                    for i, b in enumerate(self.line):
                        expected[12 + (start + i) % CAPACITY] = b
                    struct.pack_into('<II', expected, 4, (start + len(self.line)) % CAPACITY,
                                     min(CAPACITY, size + len(self.line)))
                    self.assertEqual(bytes(u.mem_read(CONSOLE, 65536)), expected)
                    hardware = [w for w in writes if WDT <= w[0] < WDT + 4096]
                    self.assertEqual(hardware, [(WDT, 4, 0x22000194), (WDT + 4, 4, 0xf808),
                                                (WDT + 8, 4, 0x1971), (WDT, 4, 0x22000195),
                                                (WDT + 8, 4, 0x1971)])
                    self.assertEqual(bytes(u.mem_read(CONSOLE - 4096, 4096)), bytes(4096))
                    self.assertEqual(bytes(u.mem_read(CONSOLE + 65536, 4096)), bytes(4096))

    def test_failed_hardware_readback_never_enters_linux(self):
        for field in ['mode', 'length']:
            u, before, writes, result = execute(self.code, bad_readback=field)
            self.assertFalse(result['linux_entry_reached'])
            self.assertTrue(result['reset_requested'])
            self.assertEqual(bytes(u.mem_read(CONSOLE, 65536)), before)
            self.assertEqual(writes[-1], (WDT + 0x14, 4, 0x1209))

    def test_bad_retained_header_does_not_prevent_whole_linux_attempt(self):
        for params in [dict(signature=0), dict(start=CAPACITY), dict(size=CAPACITY + 1),
                       dict(start=10, size=9)]:
            u, before, _, result = execute(self.code, **params)
            self.assertTrue(result['linux_entry_reached'])
            self.assertEqual(bytes(u.mem_read(CONSOLE, 65536)), before)

    def test_unsafe_entry_state_never_writes_hardware_or_enters_linux(self):
        for el, sctlr in [(1, 1), (1, 4), (2, 1), (2, 4), (3, 0)]:
            _, _, writes, result = execute(self.code, el=el, sctlr=sctlr)
            self.assertEqual(writes, [])
            self.assertFalse(result['linux_entry_reached'])


if __name__ == '__main__':
    unittest.main()
