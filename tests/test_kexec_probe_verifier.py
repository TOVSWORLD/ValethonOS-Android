import struct
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_kexec_probe import verify, RELEASE


def module_blob(import_name='printk', crc=0x1234, versioned=True, release=RELEASE, machine=183):
    strings = b'\0' + import_name.encode() + b'\0'
    symtab = bytes(24) + struct.pack('<IBBHQQ', 1, 0x10, 0, 0, 0, 0)
    versions = b''
    if versioned:
        for name, value in [(import_name, crc), ('module_layout', 0x5678)]:
            versions += struct.pack('<Q56s', value, name.encode())
    sections = [('', b'', 0, 0, 0), ('.shstrtab', b'', 3, 0, 0),
                ('.strtab', strings, 3, 0, 0), ('.symtab', symtab, 2, 2, 24),
                ('.modinfo', ('vermagic=' + release + ' SMP preempt mod_unload modversions aarch64\0').encode(), 1, 0, 0),
                ('__versions', versions, 1, 0, 0)]
    names = b'\0'; offsets = {}
    for name, *_ in sections:
        offsets[name] = len(names); names += name.encode() + b'\0'
    sections[1] = ('.shstrtab', names, 3, 0, 0)
    data = bytearray(64); headers = []
    for name, blob, kind, link, size in sections:
        at = len(data); data += blob
        headers.append(struct.pack('<IIQQQQIIQQ', offsets[name], kind, 0, 0, at, len(blob), link, 0, 1, size))
    table = len(data); data += b''.join(headers)
    data[:16] = b'\x7fELF\x02\x01\x01' + bytes(9)
    struct.pack_into('<HHIQQQIHHHHHH', data, 16, 1, machine, 1, 0, 0, table, 0, 64, 0, 0, 64, len(headers), 1)
    return data


class ProbeGate(unittest.TestCase):
    def run_gate(self, **kwargs):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); module = root / 'probe.ko'; provider = root / 'Module.symvers'
            module.write_bytes(module_blob(**kwargs))
            provider.write_text('0x1234\tprintk\tvmlinux\tEXPORT_SYMBOL\n0x5678\tmodule_layout\tvmlinux\tEXPORT_SYMBOL\n')
            return verify(module, provider)

    def test_source_crc_match_still_does_not_admit_hardware(self):
        result = self.run_gate()
        self.assertTrue(result['all_required_crcs_match_provider'])
        self.assertFalse(result['physical_test_admitted'])
        self.assertFalse(result['target_runtime_abi_verified'])

    def test_rejects_unversioned_initial_build(self):
        with self.assertRaisesRegex(ValueError, 'Missing module CRCs'):
            self.run_gate(versioned=False)

    def test_rejects_wrong_crc(self):
        with self.assertRaisesRegex(ValueError, 'CRC mismatch'):
            self.run_gate(crc=0x9999)

    def test_rejects_handoff_import(self):
        with self.assertRaisesRegex(ValueError, 'Unexpected imports'):
            self.run_gate(import_name='kernel_kexec')

    def test_rejects_current_recovery_release(self):
        with self.assertRaisesRegex(ValueError, 'Wrong kernel release'):
            self.run_gate(release='3.18.19-g51c2c8d5bfb')

    def test_rejects_other_architecture(self):
        with self.assertRaisesRegex(ValueError, 'AArch64'):
            self.run_gate(machine=62)

if __name__ == '__main__':
    unittest.main()
