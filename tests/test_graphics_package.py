import copy, gzip, json, lzma, struct, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from pack_graphics_boot import assemble, INITRD_ADDRESS
from validate_graphics_vm import parse_log


class GraphicsPackage(unittest.TestCase):
    def inputs(self):
        image=bytearray(4096);struct.pack_into('<QQQ',image,8,0,0x100000,10);image[56:60]=b'ARMd'
        dt=bytearray(64);struct.pack_into('>II',dt,0,0xd00dfeed,len(dt))
        rd=lzma.compress(b'graphics fixture'*100000,check=lzma.CHECK_CRC32,preset=6)
        metadata=json.loads((ROOT/'evidence/independent-recovery/trial-placement-metadata.json').read_text())
        return [bytes(image),gzip.compress(image,mtime=0),bytes(dt),rd,metadata]

    def test_xz_graphics_placement_preserves_original_partition_size(self):
        args=self.inputs();candidate,report=assemble(*args)
        self.assertEqual(len(candidate),16*1024*1024)
        self.assertEqual(struct.unpack_from('<I',candidate,20)[0],INITRD_ADDRESS)
        self.assertGreater(report['unpacked_archive_bytes'],1024*1024)
        self.assertTrue(report['compressed_kernel_staging_included'])

    def test_ram_reservations_and_concatenated_or_wrong_check_xz_fail(self):
        for address in [INITRD_ADDRESS,0x45000000+100]:
            args=self.inputs();args[4]['reserved'].append({'reg':[{'address':hex(address),'bytes':1}]})
            with self.assertRaises(ValueError):assemble(*args)
        args=self.inputs();args[3]+=args[3]
        with self.assertRaises(ValueError):assemble(*args)
        args=self.inputs();args[3]=lzma.compress(b'fixture',check=lzma.CHECK_CRC64)
        with self.assertRaises(ValueError):assemble(*args)


class GraphicsVMResult(unittest.TestCase):
    def log(self):
        values={**{n:0 for n in ['ENFORCE','DRIVER_DLOPEN','GBM_DLOPEN','EGL_CLIENT','MEMFD','MEMORY_RW']},
                **{n:-13 for n in ['MEMORY_EXEC_DENIED','FORK_DENIED','INPUT_WRITE_DENIED','BLOCK_WRITE_DENIED']}}
        return ''.join('VM_GRAPHICS_'+n+f'={v:+011d}\n' for n,v in values.items()).encode()+b'VM_GRAPHICS_PROBE_DONE\n'

    def test_complete_controls_and_failures(self):
        data=self.log();parse_log(data)
        for bad in [data.replace(b'-0000000013',b'+0000000000'),data+b'VM_GRAPHICS_ENFORCE=+0000000000\n',
                    data.replace(b'VM_GRAPHICS_GBM_DLOPEN=+0000000000\n',b''),data+b'Kernel panic']:
            with self.assertRaises(ValueError):parse_log(bad)
