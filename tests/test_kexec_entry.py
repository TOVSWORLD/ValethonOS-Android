"""Execute compiled ARM64 entry instructions offline, plus malformed-plan cases."""
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from prepare_kexec_entry import candidate, compiled_template, TEMPLATE


def image():
    b = bytearray(4096)
    struct.pack_into('<QQQ', b, 8, 0x80000, 8192, 0)
    b[56:60] = b'ARMd'
    return bytes(b)


def dtb():
    # Minimal structurally valid v17 FDT: empty root, reserve terminator, END.
    tokens = struct.pack('>IIIII', 1, 0, 2, 9, 0)[:16]
    return struct.pack('>10I', 0xD00DFEED, 72, 56, 72, 40, 17, 16, 0, 0, 16) + bytes(16) + tokens


class EntryCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cc = shutil.which(os.environ.get('KXENTRY_CC', 'clang'))
        if not cc:
            raise unittest.SkipTest('clang needed to test actual assembled instructions')
        cls.temp = tempfile.TemporaryDirectory()
        p = Path(cls.temp.name)/'entry.o'
        flags = [] if 'aarch64-linux-gnu-gcc' in cc else ['--target=aarch64-none-elf']
        subprocess.run([cc, *flags, '-c',
                        str(ROOT/'projects/firetabs-android/kexec-stage/entry_trampoline.S'),
                        '-o', str(p)], check=True, capture_output=True)
        cls.template = compiled_template(p.read_bytes())

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def plan(self, **kwargs):
        args = dict(template=self.template, image=image(), dtb=dtb(),
                    image_address=0x40080000, dtb_address=0x48000000,
                    entry_address=0x43480000)
        args.update(kwargs)
        return candidate(**args)

    def test_compiled_literal_patch_and_no_runtime_admission(self):
        b, r = self.plan()
        self.assertEqual(len(b), 40)
        self.assertEqual(b[:24], TEMPLATE[:24])
        self.assertEqual(struct.unpack_from('<QQ', b, 24), (0x48000000, 0x40080000))
        self.assertFalse(r['device_execution_allowed'])

    def test_reject_template_mutation(self):
        b = bytearray(self.template); b[0] ^= 1
        with self.assertRaises(ValueError): self.plan(template=bytes(b))

    def test_reject_gzip_and_zero_or_short_image_extent(self):
        for offset, value in [(16, 0), (16, 1024)]:
            b = bytearray(image()); struct.pack_into('<Q', b, offset, value)
            with self.assertRaises(ValueError): self.plan(image=bytes(b))
        with self.assertRaises(ValueError): self.plan(image=b'\x1f\x8b'+bytes(100))

    def test_image_alignment_and_endianness(self):
        with self.assertRaises(ValueError): self.plan(image_address=0x40081000)
        b = bytearray(image()); struct.pack_into('<Q', b, 24, 1)
        with self.assertRaises(ValueError): self.plan(image=bytes(b))

    def test_declared_image_tail_is_reserved_even_when_not_in_file(self):
        with self.assertRaises(ValueError): self.plan(dtb_address=0x40081000)
        with self.assertRaises(ValueError): self.plan(entry_address=0x40081000)

    def test_unknown_header_flags_and_truncated_elf_are_rejected(self):
        b = bytearray(image()); struct.pack_into('<Q', b, 24, 1 << 40)
        with self.assertRaises(ValueError): self.plan(image=bytes(b))
        with self.assertRaises(ValueError): compiled_template(b'\x7fELF\x02\x01')

    def test_reject_overlapping_or_overflowing_layouts(self):
        for change in [dict(dtb_address=0x40080000), dict(entry_address=0x48000000),
                       dict(entry_address=2**64-8), dict(dtb_address=0),
                       dict(entry_address=0x43480001)]:
            with self.assertRaises(ValueError): self.plan(**change)

    def test_reject_fdt_length_and_section_bounds(self):
        for offset, value in [(0, 0), (4, 80), (8, 1000), (16, 70), (20, 18)]:
            b = bytearray(dtb()); struct.pack_into('>I', b, offset, value)
            with self.assertRaises(ValueError): self.plan(dtb=bytes(b))

    def test_actual_instructions_deliver_arguments_at_different_addresses(self):
        try:
            from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
        except ImportError:
            self.skipTest('Unicorn needed for ARM64 instruction execution')
        from unicorn.arm64_const import (UC_ARM64_REG_X0, UC_ARM64_REG_X1,
            UC_ARM64_REG_X2, UC_ARM64_REG_X3, UC_ARM64_REG_PC, UC_ARM64_REG_SP)
        regs = [UC_ARM64_REG_X0, UC_ARM64_REG_X1, UC_ARM64_REG_X2, UC_ARM64_REG_X3]
        for base in [0x43480000, 0x74000000, 0x140000000]:
            for target in [0x40080000, 0x100080000]:
                dt = base + 0x10000
                b, _ = self.plan(image_address=target, dtb_address=dt, entry_address=base)
                uc = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
                uc.mem_map(base, 4096); uc.mem_write(base, b)
                uc.mem_map(target, 4096)
                for reg in regs: uc.reg_write(reg, 0xBADCAFE)
                # SP and DTB memory deliberately unmapped: no stack or DTB access allowed.
                uc.reg_write(UC_ARM64_REG_SP, 0xDEAD0000)
                writes = []; seen = []
                uc.hook_add(UC_HOOK_MEM_WRITE, lambda *args: writes.append(args[2]))
                def step(emulator, address, size, _):
                    seen.append(address)
                    if address == target: emulator.emu_stop()
                uc.hook_add(UC_HOOK_CODE, step)
                uc.emu_start(base, target+4, count=8)
                self.assertEqual(uc.reg_read(UC_ARM64_REG_PC), target)
                self.assertEqual([uc.reg_read(r) for r in regs], [dt, 0, 0, 0])
                self.assertEqual(seen, [base+i*4 for i in range(6)]+[target])
                self.assertEqual(writes, [])
                self.assertEqual(uc.reg_read(UC_ARM64_REG_SP), 0xDEAD0000)


if __name__ == '__main__':
    unittest.main()
